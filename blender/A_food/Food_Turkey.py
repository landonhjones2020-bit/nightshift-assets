"""Food_Turkey — sliced turkey layer (A_food batch).

Three round deli slices gathered into soft folds, overlapping along the roll; ruffled edges hang
just past the long sides (<= 0.08 overhang). Parts: Meat (pale roast turkey), MeatEdge (the
golden roasted rim band, which also outlines overlapping slices).
Run:  bpyenv/bin/python blender/A_food/Food_Turkey.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

MEAT, EDGE = "#F0D5A8", "#CF9C5E"
KW = dict(seed=3, amp=0.04, wavelength=0.44)


def build():
    m = C.polar_slices(MEAT, EDGE, **KW)
    C.check_bounds("Food_Turkey", m)


def icon():
    C.polar_slices(MEAT, EDGE, xs=(-0.3, 0.3), yaws=(-14, 18), tilt=(-6, 8), droop=False, seed=3, amp=0.04,
                   wavelength=0.44, zstep=0.03)


if __name__ == "__main__":
    C.run(build, "Food_Turkey", C.meta("turkey", 0.07),
          icon=("Ingredient_turkey", icon, {"pitch": 40.0}))
