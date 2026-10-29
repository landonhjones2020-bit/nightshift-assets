"""_sheet — review sheet of all 38 sandwich icons (G_icons batch).

Every icon at full size with a 64 px copy beside it, labelled, plus a 64 px-only companion sheet;
written to the scratch dir (not the repo).
Usage:  bpyenv/bin/python blender/G_icons/_sheet.py            # the published icons
        bpyenv/bin/python blender/G_icons/_sheet.py --drafts   # the low-res drafts
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as G  # noqa: E402

if __name__ == "__main__":
    if "--drafts" in sys.argv:
        print(G.icon_sheet(os.path.join(G.SCRATCH, "_drafts_sheet.png"), src=G.DRAFT_DIR))
    else:
        print(G.icon_sheet())
