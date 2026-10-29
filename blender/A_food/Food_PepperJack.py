"""Food_PepperJack — pepper jack slices (A_food batch).

Three creamy-white square slices flecked with red and green pepper bits. Parts: Cheese,
CheeseEdge (rim band / outline), PepperRed, PepperGreen (fleck parts).
Food_PepperJack_Melted is the toasted variant.
Run:  bpyenv/bin/python blender/A_food/Food_PepperJack.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

CH = C.CHEESES["pepper_jack"]
RED = [(-0.95, 0.2), (-0.7, -0.22), (-0.42, 0.12), (-0.12, -0.2), (0.15, 0.24), (0.4, -0.08), (0.72, 0.18),
       (0.97, -0.17)]
GREEN = [(-0.88, -0.05), (-0.6, 0.26), (-0.3, -0.04), (-0.02, 0.1), (0.25, -0.26), (0.55, 0.3), (0.8, -0.05),
         (0.62, -0.28)]
SIZE = (0.062, 0.04, 0.012)


def build():
    parts = C.cheese_slices(CH["col"], CH["edge"], zstep=0.006, side_pts=2, seed=6)
    C.flecks_on("PepperRed", parts[:1], RED, CH["red"], "SmoothPlastic", size=SIZE, verts=4, seed=1, sink=0.3)
    C.flecks_on("PepperGreen", parts[:1], GREEN, CH["green"], "SmoothPlastic", size=SIZE, verts=4, seed=2, sink=0.3)
    C.check_bounds("Food_PepperJack", parts)


def icon():
    parts = C.cheese_slices(CH["col"], CH["edge"], xs=(-0.22, 0.22), yaws=(-14, 22), tilt=(-6, 6), zstep=0.04,
                            droop=False, side_pts=2, seed=6)
    C.flecks_on("PepperRed", parts[:1], [(-0.4, 0.1), (-0.15, -0.2), (0.1, 0.25), (0.35, -0.05), (0.5, 0.3),
                                         (0.45, -0.3)], CH["red"], "SmoothPlastic", size=(0.04, 0.026, 0.01), verts=4)
    C.flecks_on("PepperGreen", parts[:1], [(-0.3, -0.12), (-0.45, 0.3), (0.2, 0.0), (0.3, 0.3), (0.55, -0.15)],
                CH["green"], "SmoothPlastic", size=(0.04, 0.026, 0.01), verts=4)


if __name__ == "__main__":
    C.run(build, "Food_PepperJack", C.meta("pepper_jack", 0.06),
          icon=("Ingredient_pepper_jack", icon, {"pitch": 42.0}))
