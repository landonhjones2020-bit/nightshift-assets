--[[
	Night Shift Asset Importer — local Roblox Studio plugin
	Night Shift at STACKHOUSE · v1.0

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
	  Url     string   https://raw.githubusercontent.com/landonhjones2020-bit/nightshift-assets/<ref>/meshes/...json
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

local VERSION = "1.0"
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
