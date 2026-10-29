"""Food_Swiss_Melted — melted (toasted) Swiss (A_food batch).

One gooey sheet over the roll with stretched holes; plateau bottom at Z 0, edges and drips sag
over the layer below (pivot = contract origin). Part: Cheese.
Run:  bpyenv/bin/python blender/A_food/Food_Swiss_Melted.py   (NS_EXPORT=1 export)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

CH = C.CHEESES["swiss"]
HOLES = [(-0.66, 0.06, 0.13, 0.1), (-0.24, -0.15, 0.1, 0.08), (0.13, 0.13, 0.115, 0.09), (0.6, -0.1, 0.11, 0.085)]


def build():
    m = C.melted_sheet("Cheese", CH["melt"], N=36, lobes=C.MELT_LOBES, drips=C.MELT_DRIPS[:2], holes=HOLES, seed=4)
    C.check_bounds("Food_Swiss_Melted", [m])


if __name__ == "__main__":
    C.run(build, "Food_Swiss_Melted", C.meta("swiss", 0.04, melted=True))
