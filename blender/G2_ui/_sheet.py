"""_sheet — G2_ui review sheets: every icon of a family at full size beside 56 / 32 px copies
(+ 20 px for tags, a 160 px rarity-gradient card for shop/meta) on the #1b1b26 HUD panel.

Usage:  bpyenv/bin/python blender/G2_ui/_sheet.py <family...|all> [--draft]
Writes <scratch>/_sheet_<family>.png (finals, from icons/<group>/) or _draft_<family>.png.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _batch  # noqa: E402,F401  (registers every family)
import _common as G  # noqa: E402

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    draft = "--draft" in sys.argv
    fams = list(G.ORDER) if (not args or args == ["all"]) else args
    for fam in fams:
        names = G.ORDER[fam]
        out = os.path.join(G.SCRATCH, f"_{'draft' if draft else 'sheet'}_{fam}.png")
        print(G.sheet(fam, names, src=G.DRAFT_DIR if draft else None, out=out))
