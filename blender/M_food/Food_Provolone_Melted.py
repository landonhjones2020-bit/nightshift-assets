"""Food_Provolone_Melted — melted (toasted) provolone (M_food batch).

One gooey sheet over the roll, built exactly like Food_Swiss_Melted (A_food melted_sheet: plateau
bottom at Z 0, the edge curls over the layer below, lobes flow down the sides, teardrop drips hang
from the deepest ones; pivot = contract origin), with the curled-over rim kept as the tan smoked
rind so it still reads as provolone, not Swiss or pepper jack. Parts: Cheese, Rind.
Run:  bpyenv/bin/python blender/M_food/Food_Provolone_Melted.py   (NS_EXPORT=1 export)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from Food_Provolone import MELT, RIND  # noqa: E402


def build():
    m, r = C.melted_sheet_rind("Cheese", MELT, "Rind", RIND, N=36, lobes=C.MELT_LOBES, drips=C.MELT_DRIPS[:2],
                               seed=9)
    C.check_bounds("Food_Provolone_Melted", [m, r])


if __name__ == "__main__":
    C.run(build, "Food_Provolone_Melted", C.meta("provolone", 0.04, melted=True))
