"""Menu_M2 — sandwich icon for Menu sandwich M2 (G_icons batch).

The assembled sandwich from the recipe in Bible §5.7 (read at run time from the git-ignored
_local/ bible, so no recipe text lives in this repo), built from the A_food ingredient models and
rendered with nslib's shared icon rig to icons/menu/Menu_M2.png (+ .nsz, manifests/icons.json).
Run:  bpyenv/bin/python blender/G_icons/Menu_M2.py   (NS_DRAFT=1: low-res draft to the scratch dir only)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as G  # noqa: E402

if __name__ == "__main__":
    G.main("M2")
