"""Food_Swiss — Swiss cheese slices (A_food batch).

Three pale square slices with real through-holes (the layer below shows through), overlapping
along the roll with sagging corners. Part: Cheese.
Food_Swiss_Melted is the toasted variant.
Run:  bpyenv/bin/python blender/A_food/Food_Swiss.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

CH = C.CHEESES["swiss"]


def build():
    parts = C.cheese_slices(CH["col"], CH["edge"], holes=C.SWISS_HOLES, zstep=0.006)
    C.check_bounds("Food_Swiss", parts)


def icon():
    C.cheese_slices(CH["col"], CH["edge"], holes=C.SWISS_HOLES[:2], xs=(-0.22, 0.22), yaws=(-14, 22),
                    tilt=(-6, 6), zstep=0.04, droop=False)


if __name__ == "__main__":
    C.run(build, "Food_Swiss", C.meta("swiss", 0.06),
          icon=("Ingredient_swiss", icon, {"pitch": 42.0}))
