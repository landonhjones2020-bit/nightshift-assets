--!nocheck
-- NSZ — base64 + zlib(DEFLATE) decoder for Night Shift icon payloads.
-- Source of truth for the decoder: build.py inlines it into NightShiftImporter.lua.
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


local NSZ = {}
--- Returns (pixels: buffer RGBA, width, height) for an NSZ1 base64 payload.
function NSZ.decode(text: string): (buffer, number, number)
	local raw = base64Decode(text)
	assert(buffer.readstring(raw, 0, 4) == "NSZ1", "not an NSZ1 image")
	local w = buffer.readu16(raw, 4)
	local h = buffer.readu16(raw, 6)
	return inflate(raw, 8, w * h * 4), w, h
end
NSZ.inflate = inflate
NSZ.base64Decode = base64Decode
return NSZ
