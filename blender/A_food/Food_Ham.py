"""Food_Ham — sliced ham layer (A_food batch).

Three round pink deli slices in soft folds, overlapping along the roll, edges hanging just past
the long sides. Parts: Meat (ham pink), MeatEdge (deeper pink rim band / outline).
Run:  bpyenv/bin/python blender/A_food/Food_Ham.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

MEAT, EDGE = "#F58EA3", "#D9637D"
KW = dict(seed=5, amp=0.034, wavelength=0.52, wob_amp=0.025, yaws=(5, -3, -8))


def build():
    m = C.polar_slices(MEAT, EDGE, **KW)
    C.check_bounds("Food_Ham", m)


def icon():
    C.polar_slices(MEAT, EDGE, xs=(-0.3, 0.3), yaws=(10, -16), tilt=(-6, 8), droop=False, seed=5, amp=0.034,
                   wavelength=0.52, wob_amp=0.025, zstep=0.03)


if __name__ == "__main__":
    C.run(build, "Food_Ham", C.meta("ham", 0.07),
          icon=("Ingredient_ham", icon, {"pitch": 40.0}))
