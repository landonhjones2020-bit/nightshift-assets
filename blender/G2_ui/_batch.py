"""_batch — render G2_ui icons in one Blender session (one icon after another, never parallel).

Usage:  bpyenv/bin/python blender/G2_ui/_batch.py hud                 # a whole family, finals
        bpyenv/bin/python blender/G2_ui/_batch.py HUD_Book HUD_Gift --draft
        bpyenv/bin/python blender/G2_ui/_batch.py --list
Families: hud, crates, tags, shop, meta, portraits, art, fx. Finals write icons/<group>/<name>.png
+ .nsz and register them in manifests/icons.json (nslib.export_icon); --draft writes 128 px
drafts to the scratch dir only.
"""
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as G  # noqa: E402

FAMILY_MODULES = ("fam_hud", "fam_crates", "fam_tags", "fam_shop", "fam_meta", "fam_portraits", "fam_keyart", "fam_fx")
for _m in FAMILY_MODULES:
    __import__(_m)


def names_for(args):
    out = []
    for a in args:
        if a in G.ORDER:
            out += G.ORDER[a]
        elif a in G.REG:
            out.append(a)
        else:
            raise SystemExit(f"unknown icon or family: {a}")
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if "--list" in flags:
        for fam, ns_ in G.ORDER.items():
            print(fam, len(ns_), " ".join(ns_))
        sys.exit(0)
    failed = []
    for n in names_for(args):
        t0 = time.time()
        try:
            G.run(n, draft="--draft" in flags)
        except Exception:
            traceback.print_exc()
            failed.append(n)
        print(f"   ({time.time() - t0:.1f} s)", flush=True)
    if failed:
        print("FAILED:", " ".join(failed))
        sys.exit(1)
