"""Food_RoastBeef — shaved roast beef layer (A_food batch).

Thin slices folded tightly (shaved-deli look) with a pink centre and a brown roasted rim, which
shows both on top and on the folded edges. Parts: Meat (pink centre), MeatEdge (brown rim).
Run:  bpyenv/bin/python blender/A_food/Food_RoastBeef.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

MEAT, EDGE = "#D9506A", "#8A4634"
KW = dict(seed=8, amp=0.045, wavelength=0.48, pleat=0.6, cup=0.008, thick=0.035, N=22, inner=(0.3, 0.6, 0.84), rim_on_top=True,
          a=0.47, b=0.455, wob_amp=0.042, wob_k=7)


def build():
    m = C.polar_slices(MEAT, EDGE, **KW)
    C.check_bounds("Food_RoastBeef", m)


def icon():
    kw = dict(KW)
    kw.update(xs=(-0.3, 0.3), yaws=(-12, 15), tilt=(-6, 8), droop=False, zstep=0.035)
    C.polar_slices(MEAT, EDGE, **kw)


if __name__ == "__main__":
    C.run(build, "Food_RoastBeef", C.meta("roast_beef", 0.09),
          icon=("Ingredient_roast_beef", icon, {"pitch": 40.0}))
