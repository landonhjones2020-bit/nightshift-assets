"""Food_Cheddar — cheddar slices (A_food batch).

Three square deli slices overlapping along the roll, corners just overhanging and sagging.
Parts: Cheese (orange), CheeseEdge (deeper orange rim band that outlines the slices).
Food_Cheddar_Melted is the toasted variant.
Run:  bpyenv/bin/python blender/A_food/Food_Cheddar.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

CH = C.CHEESES["cheddar"]


def build():
    parts = C.cheese_slices(CH["col"], CH["edge"], zstep=0.006)
    C.check_bounds("Food_Cheddar", parts)


def icon():
    C.cheese_slices(CH["col"], CH["edge"], xs=(-0.22, 0.22), yaws=(-14, 22), tilt=(-6, 6), zstep=0.04, droop=False)


if __name__ == "__main__":
    C.run(build, "Food_Cheddar", C.meta("cheddar", 0.06),
          icon=("Ingredient_cheddar", icon, {"pitch": 42.0}))
