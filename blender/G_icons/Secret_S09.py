"""Secret_S09 — Secret Book icon for Secret Sandwich S09 (G_icons batch).

The assembled sandwich from the recipe in Bible §5.8 (read at run time from the git-ignored
_local/ bible, so no recipe text lives in this repo), built from the A_food ingredient models and
rendered with nslib's shared icon rig to icons/secrets/Secret_S09.png (+ .nsz, manifests/icons.json).
Run:  bpyenv/bin/python blender/G_icons/Secret_S09.py   (NS_DRAFT=1: low-res draft to the scratch dir only)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as G  # noqa: E402

if __name__ == "__main__":
    G.main("S09")
