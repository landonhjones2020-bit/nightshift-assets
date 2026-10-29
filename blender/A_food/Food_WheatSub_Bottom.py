"""Food_WheatSub_Bottom — bottom half of the wheat_sub sub roll (A_food batch).

Contract (STYLE.md section 4): roll 2.2 long (X) x 0.85 wide, bottom 0.30 tall / top 0.42 tall,
bottom at Z=0. Parts: Crust (recolor "toast"; the client darkens it with doneness), Crumb, Pores.
Bread look and colours live in _common.BREADS / build_bread.
Run:  bpyenv/bin/python blender/A_food/Food_WheatSub_Bottom.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

KIND, HALF = "wheat_sub", "bottom"


def build():
    C.build_bread(KIND, HALF)


def icon():
    """Ingredient card: the empty roll, top half hinged open to show the crumb."""
    C.build_open_roll(KIND, open_deg=40)


if __name__ == "__main__":
    C.run(build, "Food_WheatSub_Bottom", C.bread_meta(KIND, HALF),
          icon=("Ingredient_wheat_sub", icon, {"yaw": -58.0, "pitch": 30.0}))
