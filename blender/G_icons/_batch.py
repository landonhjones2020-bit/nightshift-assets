"""_batch — render several sandwich icons in one Blender session (G_icons batch).

Usage:  bpyenv/bin/python blender/G_icons/_batch.py all            # all 38 final icons, in order
        bpyenv/bin/python blender/G_icons/_batch.py M1 S05 --draft # low-res drafts to the scratch dir
        bpyenv/bin/python blender/G_icons/_batch.py --list         # print every parsed recipe stack
Renders run one after another (never in parallel).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as G  # noqa: E402

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    ids = G.ALL_IDS if (not args or args == ["all"]) else args
    if "--list" in flags:
        for rid in ids:
            r = G.RECIPES[rid]
            print(f"{r['icon']:11s} {r['rarity']:9s} {r['bread']:11s} {r['toast']:8s} {' > '.join(G.stack_of(rid))}")
        sys.exit(0)
    for rid in ids:
        G.render(rid, draft="--draft" in flags)
