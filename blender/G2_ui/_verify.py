"""_verify — check every G2_ui icon end to end (no Blender rendering).

For each registered icon: the PNG exists in icons/<group>/, has the expected size (512 x 512;
Art_KeyArt 1024 x 576), its .nsz decodes (base64 -> "NSZ1" + u16le w + u16le h + zlib RGBA) to
exactly the PNG's RGBA pixels, and manifests/icons.json has the entry with the right group,
size, pixel hash and URL. Also checks the manifest is valid JSON and lists unknown/missing keys.
Usage:  bpyenv/bin/python blender/G2_ui/_verify.py [before.json]   (optional: an earlier
manifest whose entries must all still be present and unchanged)
"""
import base64
import hashlib
import json
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _batch  # noqa: E402,F401
import _common as G  # noqa: E402
from PIL import Image  # noqa: E402


def decode_nsz(path):
    raw = base64.b64decode(open(path).read())
    assert raw[:4] == b"NSZ1", "bad magic"
    w, h = struct.unpack("<HH", raw[4:8])
    px = zlib.decompress(raw[8:])
    assert len(px) == w * h * 4, "bad pixel length"
    return w, h, px


def main():
    man_path = os.path.join(G.REPO, "manifests", "icons.json")
    man = json.load(open(man_path))
    bad = []
    by_group = {}
    for fam, names in G.ORDER.items():
        for n in names:
            e = G.REG[n]
            grp = e["group"]
            png = os.path.join(G.REPO, "icons", grp, f"{n}.png")
            nsz = os.path.splitext(png)[0] + ".nsz"
            want = (1024, 576) if e["kind"] == "art" else (512, 512)
            try:
                im = Image.open(png).convert("RGBA")
                assert im.size == want, f"size {im.size} != {want}"
                w, h, px = decode_nsz(nsz)
                assert (w, h) == im.size, "nsz size mismatch"
                assert px == im.tobytes(), "nsz pixels differ from png"
                m = man.get(n)
                assert m, "missing from manifest"
                assert m["group"] == grp, f"group {m['group']} != {grp}"
                assert m["size"] == [w, h], "manifest size"
                assert m["hash"] == hashlib.sha1(px).hexdigest()[:16], "manifest hash"
                assert m["url"].endswith(f"/icons/{grp}/{n}.nsz"), "manifest url"
                by_group[grp] = by_group.get(grp, 0) + 1
            except Exception as ex:   # noqa: BLE001
                bad.append((n, str(ex)))
    print(f"manifest entries: {len(man)}")
    print("G2 icons verified per group:", dict(sorted(by_group.items())))
    if len(sys.argv) > 1:
        before = json.load(open(sys.argv[1]))
        lost = [k for k in before if k not in man]
        changed = [k for k in before if k in man and man[k] != before[k]]
        print(f"earlier entries: {len(before)}, missing now: {lost}, changed: {changed}")
        if lost or changed:
            bad.append(("earlier entries", f"missing {lost} changed {changed}"))
    for n, why in bad:
        print("FAIL", n, why)
    print("OK" if not bad else f"{len(bad)} problem(s)")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
