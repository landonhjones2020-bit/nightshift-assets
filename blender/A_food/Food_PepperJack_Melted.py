"""Food_PepperJack_Melted — melted (toasted) pepper jack (A_food batch).

One gooey sheet over the roll with pepper flecks; plateau bottom at Z 0, edges and drips sag over
the layer below (pivot = contract origin). Parts: Cheese, PepperRed, PepperGreen.
Run:  bpyenv/bin/python blender/A_food/Food_PepperJack_Melted.py   (NS_EXPORT=1 export)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from Food_PepperJack import CH, GREEN, RED, SIZE  # noqa: E402


def build():
    m = C.melted_sheet("Cheese", CH["melt"], N=32, lobes=C.MELT_LOBES, drips=C.MELT_DRIPS, seed=7)
    C.flecks_on("PepperRed", [m], RED, CH["red"], "SmoothPlastic", size=SIZE, verts=4, seed=1, sink=0.3)
    C.flecks_on("PepperGreen", [m], GREEN, CH["green"], "SmoothPlastic", size=SIZE, verts=4, seed=2, sink=0.3)
    C.check_bounds("Food_PepperJack_Melted", [m])


if __name__ == "__main__":
    C.run(build, "Food_PepperJack_Melted", C.meta("pepper_jack", 0.04, melted=True))
