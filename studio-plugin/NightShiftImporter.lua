--[[
	Night Shift Asset Importer — local Roblox Studio plugin
	Night Shift at STACKHOUSE · v1.1

	WHY THIS EXISTS
	Roblox only lets *locally installed plugins* publish mesh assets
	(AssetService:CreateAssetAsync). Claude models everything in Blender, pushes the
	mesh data to the public GitHub repo `landonhjones2020-bit/nightshift-assets`, and
	this plugin turns that data into mesh assets on the logged-in Studio account.

	WHAT IT DOES (and nothing else)
	  * Watches ServerStorage.NS_Pipeline.Jobs for Configuration objects with
	    Status = "pending".
	  * Downloads the job's mesh JSON (only from the nightshift-assets repo).
	  * Builds one EditableMesh per part and publishes it as a Mesh asset.
	  * Writes the resulting mesh asset IDs back onto the job (Result attribute)
	    and into a shared cache keyed by geometry hash, so nothing uploads twice.
	Building MeshParts, colouring and assembling models happens in the place itself,
	not here, so this plugin rarely needs updating.

	JOB FORMAT  (ServerStorage.NS_Pipeline.Jobs.<any name> : Configuration)
	  Kind    string   "mesh" (default) or "image"
	  Url     string   https://raw.githubusercontent.com/landonhjones2020-bit/nightshift-assets/<ref>/meshes/...json
	                   (images: .../icons/...nsz — base64 of "NSZ1", width u16, height u16, zlib(RGBA))
	  Status  string   "pending" -> "working" -> "done" | "error"
	  Result  string   JSON { [partName] = meshAssetId }        (set by this plugin)
	  Error   string   failure reason                            (set by this plugin)
	  Log     string   per-part upload notes                      (set by this plugin)

	Toolbar: "Night Shift" -> "Asset Importer" toggles processing on/off.
]]

local AssetService = game:GetService("AssetService")
local ChangeHistoryService = game:GetService("ChangeHistoryService")
local HttpService = game:GetService("HttpService")
local RunService = game:GetService("RunService")
local ServerStorage = game:GetService("ServerStorage")

-- Only run in the edit DataModel (plugins are also loaded into play-test DataModels).
if not RunService:IsEdit() then
	return
end

local VERSION = "1.1"
local ALLOWED_PREFIX = "https://raw.githubusercontent.com/landonhjones2020-bit/nightshift-assets/"
local POLL_SECONDS = 0.5
local MAX_ATTEMPTS = 4

local toolbar = plugin:CreateToolbar("Night Shift")
local toggleButton = toolbar:CreateButton(
	"Asset Importer",
	"Upload Blender meshes queued in ServerStorage.NS_Pipeline (click to pause/resume)",
	""
)
toggleButton.ClickableWhenViewportHidden = true

local active = true
toggleButton:SetActive(active)
toggleButton.Click:Connect(function()
	active = not active
	toggleButton:SetActive(active)
	print(("[NightShiftImporter] %s"):format(active and "resumed" or "paused"))
end)

-- ----------------------------------------------------------------------------------
-- Pipeline folders
-- ----------------------------------------------------------------------------------

local function record(name: string, fn: () -> ())
	local id = ChangeHistoryService:TryBeginRecording(name)
	local ok, err = pcall(fn)
	if id then
		ChangeHistoryService:FinishRecording(id, Enum.FinishRecordingOperation.Commit)
	end
	if not ok then
		warn("[NightShiftImporter] " .. tostring(err))
	end
end

local function ensurePipeline(): (Folder, Folder, Configuration)
	local root = ServerStorage:FindFirstChild("NS_Pipeline")
	local jobs = root and root:FindFirstChild("Jobs")
	local cache = root and root:FindFirstChild("MeshCache")
	if not (root and jobs and cache) then
		record("NightShift: create pipeline folders", function()
			if not root then
				root = Instance.new("Folder")
				root.Name = "NS_Pipeline"
				root.Parent = ServerStorage
			end
			if not jobs then
				jobs = Instance.new("Folder")
				jobs.Name = "Jobs"
				jobs.Parent = root
			end
			if not cache then
				cache = Instance.new("Configuration")
				cache.Name = "MeshCache"
				cache.Parent = root
			end
		end)
	end
	return root :: Folder, jobs :: Folder, cache :: Configuration
end

-- ----------------------------------------------------------------------------------
-- Mesh building
-- ----------------------------------------------------------------------------------

type PartData = {
	name: string,
	hash: string,
	v: { number }, -- flat x,y,z  (Roblox axes, studs, part-local)
	n: { number }, -- flat nx,ny,nz per vertex
	t: { number }, -- flat triangle indices, 0-based
	uv: { number }?, -- optional flat u,v per vertex
	c: { number }?, -- optional flat r,g,b per vertex (0..1) — vertex-colour test only
}

local function buildEditableMesh(part: PartData): EditableMesh
	local em = AssetService:CreateEditableMesh()
	local v, n, t, uv, c = part.v, part.n, part.t, part.uv, part.c
	local count = #v // 3
	local vids = table.create(count)
	local nids = table.create(count)
	local uids = uv and table.create(count) or nil
	local cids = c and table.create(count) or nil

	for i = 0, count - 1 do
		local k = i * 3
		vids[i + 1] = em:AddVertex(Vector3.new(v[k + 1], v[k + 2], v[k + 3]))
		nids[i + 1] = em:AddNormal(Vector3.new(n[k + 1], n[k + 2], n[k + 3]))
		if uids and uv then
			uids[i + 1] = em:AddUV(Vector2.new(uv[i * 2 + 1], uv[i * 2 + 2]))
		end
		if cids and c then
			cids[i + 1] = em:AddColor(Color3.new(c[k + 1], c[k + 2], c[k + 3]), 1)
		end
	end

	for i = 1, #t, 3 do
		local a, b, d = t[i] + 1, t[i + 1] + 1, t[i + 2] + 1
		local face = em:AddTriangle(vids[a], vids[b], vids[d])
		em:SetFaceNormals(face, { nids[a], nids[b], nids[d] })
		if uids then
			em:SetFaceUVs(face, { uids[a], uids[b], uids[d] })
		end
		if cids then
			em:SetFaceColors(face, { cids[a], cids[b], cids[d] })
		end
	end
	return em
end

local function uploadMesh(em: EditableMesh, assetName: string, description: string): (boolean, string)
	local lastErr = "unknown error"
	for attempt = 1, MAX_ATTEMPTS do
		local ok, result, idOrErr = pcall(function()
			return AssetService:CreateAssetAsync(em, Enum.AssetType.Mesh, {
				Name = assetName,
				Description = description,
			})
		end)
		if ok and result == Enum.CreateAssetResult.Success then
			return true, tostring(idOrErr)
		end
		lastErr = ok and (tostring(result) .. " " .. tostring(idOrErr)) or tostring(result)
		if attempt < MAX_ATTEMPTS then
			task.wait(2 ^ attempt) -- 2, 4, 8 s backoff
		end
	end
	return false, lastErr
end

-- ----------------------------------------------------------------------------------
-- Images: base64 -> "NSZ1" header -> zlib inflate -> RGBA -> EditableImage -> asset
-- ----------------------------------------------------------------------------------

local B64 = {}
do
	local alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
	for i = 1, #alphabet do
		B64[string.byte(alphabet, i)] = i - 1
	end
end

local function base64Decode(text: string): buffer
	text = string.gsub(text, "[^%w%+/=]", "")
	local len = #text
	local pad = 0
	if string.sub(text, -2) == "==" then
		pad = 2
	elseif string.sub(text, -1) == "=" then
		pad = 1
	end
	local outLen = (len // 4) * 3 - pad
	local out = buffer.create(outLen)
	local o = 0
	for i = 1, len, 4 do
		local a = B64[string.byte(text, i)] or 0
		local b = B64[string.byte(text, i + 1)] or 0
		local c = B64[string.byte(text, i + 2)] or 0
		local d = B64[string.byte(text, i + 3)] or 0
		local n = a * 262144 + b * 4096 + c * 64 + d
		if o < outLen then buffer.writeu8(out, o, bit32.rshift(n, 16)); o += 1 end
		if o < outLen then buffer.writeu8(out, o, bit32.band(bit32.rshift(n, 8), 255)); o += 1 end
		if o < outLen then buffer.writeu8(out, o, bit32.band(n, 255)); o += 1 end
	end
	return out
end

local LBASE = { 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258 }
local LEXT = { 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0 }
local DBASE = { 1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577 }
local DEXT = { 0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13 }
local CLORDER = { 16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15 }

type Huff = { counts: { number }, symbols: { number } }

local function buildHuff(lengths: { number }, n: number): Huff
	local counts = table.create(16, 0)
	for i = 0, n - 1 do
		local l = lengths[i] or 0
		counts[l + 1] += 1
	end
	counts[1] = 0
	local offs = table.create(16, 0)
	for len = 1, 15 do
		offs[len + 1] = offs[len] + counts[len + 1]
	end
	local symbols = table.create(n, 0)
	for i = 0, n - 1 do
		local l = lengths[i] or 0
		if l ~= 0 then
			symbols[offs[l] + 1] = i
			offs[l] += 1
		end
	end
	return { counts = counts, symbols = symbols }
end

--- Minimal zlib/DEFLATE decoder (stored, fixed and dynamic Huffman blocks).
local function inflate(src: buffer, start: number, outSize: number): buffer
	local out = buffer.create(outSize)
	local outPos = 0
	local pos = start + 2 -- skip zlib header
	local bitBuf, bitCnt = 0, 0
	local srcLen = buffer.len(src)

	local function bits(n: number): number
		while bitCnt < n do
			local byte = if pos < srcLen then buffer.readu8(src, pos) else 0
			bitBuf = bit32.bor(bitBuf, bit32.lshift(byte, bitCnt))
			pos += 1
			bitCnt += 8
		end
		local v = bit32.band(bitBuf, bit32.lshift(1, n) - 1)
		bitBuf = bit32.rshift(bitBuf, n)
		bitCnt -= n
		return v
	end

	local function decode(h: Huff): number
		local code, first, index = 0, 0, 0
		local counts, symbols = h.counts, h.symbols
		for len = 1, 15 do
			code = bit32.bor(code, bits(1))
			local count = counts[len + 1]
			if code - count < first then
				return symbols[index + (code - first) + 1]
			end
			index += count
			first += count
			first *= 2
			code *= 2
		end
		error("inflate: bad Huffman code")
	end

	local fixedLit, fixedDist
	local done = false
	while not done do
		done = bits(1) == 1
		local btype = bits(2)
		if btype == 0 then
			bitBuf, bitCnt = 0, 0
			local len = buffer.readu16(src, pos)
			pos += 4
			buffer.copy(out, outPos, src, pos, len)
			pos += len
			outPos += len
		else
			local lit: Huff, dist: Huff
			if btype == 1 then
				if not fixedLit then
					local l = {}
					for i = 0, 143 do l[i] = 8 end
					for i = 144, 255 do l[i] = 9 end
					for i = 256, 279 do l[i] = 7 end
					for i = 280, 287 do l[i] = 8 end
					fixedLit = buildHuff(l, 288)
					local d = {}
					for i = 0, 29 do d[i] = 5 end
					fixedDist = buildHuff(d, 30)
				end
				lit, dist = fixedLit, fixedDist
			elseif btype == 2 then
				local nlen = bits(5) + 257
				local ndist = bits(5) + 1
				local ncode = bits(4) + 4
				local cl = {}
				for i = 0, 18 do cl[i] = 0 end
				for i = 1, ncode do
					cl[CLORDER[i]] = bits(3)
				end
				local clh = buildHuff(cl, 19)
				local lengths = {}
				local idx = 0
				while idx < nlen + ndist do
					local sym = decode(clh)
					if sym < 16 then
						lengths[idx] = sym
						idx += 1
					else
						local rep, val = 0, 0
						if sym == 16 then
							val = lengths[idx - 1]
							rep = 3 + bits(2)
						elseif sym == 17 then
							rep = 3 + bits(3)
						else
							rep = 11 + bits(7)
						end
						for _ = 1, rep do
							lengths[idx] = val
							idx += 1
						end
					end
				end
				local litL, distL = {}, {}
				for i = 0, nlen - 1 do litL[i] = lengths[i] end
				for i = 0, ndist - 1 do distL[i] = lengths[nlen + i] end
				lit = buildHuff(litL, nlen)
				dist = buildHuff(distL, ndist)
			else
				error("inflate: bad block type")
			end
			while true do
				local sym = decode(lit)
				if sym < 256 then
					buffer.writeu8(out, outPos, sym)
					outPos += 1
				elseif sym == 256 then
					break
				else
					local li = sym - 256
					local length = LBASE[li] + bits(LEXT[li])
					local ds = decode(dist) + 1
					local distance = DBASE[ds] + bits(DEXT[ds])
					local from = outPos - distance
					if distance >= length then
						buffer.copy(out, outPos, out, from, length)
						outPos += length
					else
						for _ = 1, length do
							buffer.writeu8(out, outPos, buffer.readu8(out, from))
							outPos += 1
							from += 1
						end
					end
				end
			end
		end
	end
	return out
end

local function decodeImage(text: string): (EditableImage, number, number)
	local raw = base64Decode(text)
	assert(buffer.readstring(raw, 0, 4) == "NSZ1", "not an NSZ1 image")
	local w = buffer.readu16(raw, 4)
	local h = buffer.readu16(raw, 6)
	local pixels = inflate(raw, 8, w * h * 4)
	local img = AssetService:CreateEditableImage({ Size = Vector2.new(w, h) })
	img:WritePixelsBuffer(Vector2.zero, Vector2.new(w, h), pixels)
	return img, w, h
end

local function processImageJob(job: Configuration, cache: Configuration, body: string)
	local key = "img_" .. tostring(job:GetAttribute("Hash") or "")
	if job:GetAttribute("Hash") then
		local cached = cache:GetAttribute(key)
		if typeof(cached) == "string" and cached ~= "" then
			job:SetAttribute("Result", HttpService:JSONEncode({ image = cached }))
			job:SetAttribute("Status", "done")
			return
		end
	end
	local img = decodeImage(body)
	local name = (job:GetAttribute("AssetName") :: string?) or "NS_Image"
	local lastErr = "unknown"
	for attempt = 1, MAX_ATTEMPTS do
		local ok, result, idOrErr = pcall(function()
			return AssetService:CreateAssetAsync(img, Enum.AssetType.Image, { Name = name, Description = "Night Shift at STACKHOUSE — " .. name .. " (Blender render)" })
		end)
		if ok and result == Enum.CreateAssetResult.Success then
			img:Destroy()
			if job:GetAttribute("Hash") then
				cache:SetAttribute(key, tostring(idOrErr))
			end
			job:SetAttribute("Result", HttpService:JSONEncode({ image = tostring(idOrErr) }))
			job:SetAttribute("Status", "done")
			return
		end
		lastErr = ok and (tostring(result) .. " " .. tostring(idOrErr)) or tostring(result)
		task.wait(2 ^ attempt)
	end
	img:Destroy()
	job:SetAttribute("Status", "error")
	job:SetAttribute("Error", "Image upload failed: " .. lastErr)
end

-- ----------------------------------------------------------------------------------
-- Job processing
-- ----------------------------------------------------------------------------------

local function processJob(job: Configuration, cache: Configuration)
	local url = job:GetAttribute("Url")
	if typeof(url) ~= "string" or url:sub(1, #ALLOWED_PREFIX) ~= ALLOWED_PREFIX then
		job:SetAttribute("Status", "error")
		job:SetAttribute("Error", "Url must start with " .. ALLOWED_PREFIX)
		return
	end
	job:SetAttribute("Status", "working")

	local okGet, body = pcall(function()
		return HttpService:GetAsync(url, true)
	end)
	if not okGet then
		job:SetAttribute("Status", "error")
		job:SetAttribute("Error", "Download failed: " .. tostring(body))
		return
	end
	if job:GetAttribute("Kind") == "image" then
		processImageJob(job, cache, body)
		return
	end
	local okJson, doc = pcall(function()
		return HttpService:JSONDecode(body)
	end)
	if not okJson or typeof(doc) ~= "table" or typeof(doc.parts) ~= "table" then
		job:SetAttribute("Status", "error")
		job:SetAttribute("Error", "Not a Night Shift mesh file")
		return
	end

	local results = {}
	local log = {}
	for _, part in ipairs(doc.parts) do
		local cacheKey = "h_" .. tostring(part.hash)
		local cached = cache:GetAttribute(cacheKey)
		if typeof(cached) == "string" and cached ~= "" then
			results[part.name] = cached
			table.insert(log, part.name .. ": cached " .. cached)
		else
			local em = buildEditableMesh(part)
			local assetName = ("NS_%s_%s"):format(tostring(doc.asset), tostring(part.name))
			local okUp, idOrErr = uploadMesh(
				em,
				assetName,
				("Night Shift at STACKHOUSE — %s / %s (Blender export)"):format(tostring(doc.asset), tostring(part.name))
			)
			em:Destroy()
			if not okUp then
				job:SetAttribute("Status", "error")
				job:SetAttribute("Error", ("Upload failed for %s: %s"):format(tostring(part.name), idOrErr))
				job:SetAttribute("Log", table.concat(log, "\n"))
				return
			end
			cache:SetAttribute(cacheKey, idOrErr)
			results[part.name] = idOrErr
			table.insert(log, part.name .. ": uploaded " .. idOrErr)
		end
		task.wait() -- keep Studio responsive between parts
	end

	job:SetAttribute("Result", HttpService:JSONEncode(results))
	job:SetAttribute("Log", table.concat(log, "\n"))
	job:SetAttribute("Error", "")
	job:SetAttribute("Status", "done")
end

local root, jobs, cache = ensurePipeline()
record("NightShift: importer version", function()
	root:SetAttribute("ImporterVersion", VERSION)
end)
print(("[NightShiftImporter] v%s ready — watching ServerStorage.NS_Pipeline.Jobs"):format(VERSION))

local running = true
plugin.Unloading:Connect(function()
	running = false
end)

task.spawn(function()
	while running do
		if active then
			root, jobs, cache = ensurePipeline()
			for _, job in ipairs(jobs:GetChildren()) do
				if not running or not active then
					break
				end
				if job:IsA("Configuration") and job:GetAttribute("Status") == "pending" then
					-- Not wrapped in a ChangeHistory recording: a job spans long network
					-- yields and must not swallow unrelated edits made meanwhile.
					local ok, err = pcall(processJob, job, cache)
					if not ok then
						job:SetAttribute("Status", "error")
						job:SetAttribute("Error", "Importer error: " .. tostring(err))
					end
				end
			end
		end
		task.wait(POLL_SECONDS)
	end
end)
