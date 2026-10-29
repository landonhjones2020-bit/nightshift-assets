"""Food_Cheddar_Melted — melted (toasted) cheddar (A_food batch).

One gooey sheet over the whole roll; the bottom of the plateau is at Z 0 and the edges sag over
the layer below (lobes and drips reach about -0.18), so the pivot is the contract origin, not the
bounding-box bottom. Part: Cheese (glossy orange).
Run:  bpyenv/bin/python blender/A_food/Food_Cheddar_Melted.py   (NS_EXPORT=1 export)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

CH = C.CHEESES["cheddar"]


def build():
    m = C.melted_sheet("Cheese", CH["melt"], lobes=C.MELT_LOBES, drips=C.MELT_DRIPS)
    C.check_bounds("Food_Cheddar_Melted", [m])


if __name__ == "__main__":
    C.run(build, "Food_Cheddar_Melted", C.meta("cheddar", 0.04, melted=True))
