"""Food_WhiteSub_Top — top half of the white_sub sub roll (A_food batch).

Contract (STYLE.md section 4): roll 2.2 long (X) x 0.85 wide, bottom 0.30 tall / top 0.42 tall,
bottom at Z=0. Parts: Crust (recolor "toast"; the client darkens it with doneness), Crumb, Split.
Bread look and colours live in _common.BREADS / build_bread.
Run:  bpyenv/bin/python blender/A_food/Food_WhiteSub_Top.py   (NS_EXPORT=1 export)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

KIND, HALF = "white_sub", "top"


def build():
    C.build_bread(KIND, HALF)


if __name__ == "__main__":
    C.run(build, "Food_WhiteSub_Top", C.bread_meta(KIND, HALF))
