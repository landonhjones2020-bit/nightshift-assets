"""Food_MysteryMeat — the night shift's purple mystery meat (A_food batch).

Three thick, slightly cupped luncheon-meat rounds in a dark casing, studded with a few glowing
flecks. Parts: Meat (purple), Casing (dark purple rim), Flecks (Neon green — they glow).
Run:  bpyenv/bin/python blender/A_food/Food_MysteryMeat.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

MEAT, CASING, GLOW = "#8E46BE", "#4E1F72", "#7DFF4F"
KW = dict(seed=13, amp=0.012, wavelength=0.6, thick=0.06, N=20, inner=(0.4, 0.86), rim_on_top=True,
          a=0.43, b=0.43, wob_amp=0.03, wob_k=3, cup=0.022, yaws=(0, 0, 0), tilt=(-3, 1, 3),
          xs=(-0.7, 0.0, 0.7), zstep=0.01, names=("Meat", "Casing"), smooth_angle=60.0)
SPOTS = [(-0.82, -0.12), (-0.62, 0.18), (-0.55, -0.2), (-0.1, 0.12), (0.12, -0.16), (0.05, 0.25),
         (0.6, 0.1), (0.82, -0.14), (0.7, 0.25)]


def build():
    m, c = C.polar_slices(MEAT, CASING, **KW)
    C.flecks_on("Flecks", [m], SPOTS, GLOW, "Neon", size=(0.044, 0.03, 0.014))
    C.check_bounds("Food_MysteryMeat", [m, c])


def icon():
    kw = dict(KW)
    kw.update(xs=(-0.28, 0.32), tilt=(-8, 10), droop=False, zstep=0.05)
    m, c = C.polar_slices(MEAT, CASING, **kw)
    C.flecks_on("Flecks", [m], [(-0.4, 0.1), (-0.2, -0.15), (-0.38, -0.2), (0.3, 0.15), (0.45, -0.1),
                                (0.2, -0.05)], GLOW, "Neon", size=(0.05, 0.034, 0.016))


if __name__ == "__main__":
    C.run(build, "Food_MysteryMeat", C.meta("mystery_meat", 0.10),
          icon=("Ingredient_mystery_meat", icon, {"pitch": 40.0}))
