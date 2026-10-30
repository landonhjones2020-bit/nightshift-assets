"""Shop_SidewalkPlanter — long concrete planter trough with low shrubs (outdoors, night).

A slightly tapered concrete trough on a recessed darker foot, with a chunky lip around the
top and a groove line, dark soil, and three clumps of rounded low shrubs in desaturated
night greens. No collision (street furniture; the map adds its own collision boxes).
Front faces -Y (reads the same from both long sides), pivot = bottom-centre. ~6 x 2.6 x 2.2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D = 6.0, 2.2
FOOT = 0.14
LIP_Z = (1.16, 1.32)
SOIL_Z = 1.2
CONC_DARK = "#6E6C68"


def build():
    def ring(w, d, z, r=0.12):
        return C.ring3(C.rrect(w, d, r, 1), z)

    # trough: tapered body -> lip (outer) -> rim top -> inner wall down to the soil
    rings = [ring(W - 0.5, D - 0.5, FOOT - 0.01, 0.1), ring(W - 0.32, D - 0.32, LIP_Z[0], 0.12),
             ring(W, D, LIP_Z[0], 0.16), ring(W, D, LIP_Z[1], 0.16), ring(W - 0.36, D - 0.36, LIP_Z[1], 0.1),
             ring(W - 0.36, D - 0.36, SOIL_Z - 0.04, 0.1)]
    trough = C.loft(rings, cap0=True, cap1=True)
    C.part([trough], "Trough", C.CONCRETE, "Concrete", smooth_angle=30)
    groove = C.loft([ring(W - 0.37, D - 0.37, 0.62, 0.11), ring(W - 0.36, D - 0.36, 0.66, 0.11)], cap0=False, cap1=False)
    foot = ns.box((W - 0.7, D - 0.7, FOOT + 0.02), loc=(0, 0, (FOOT + 0.02) / 2), bevel=0.0)
    C.part([foot, groove], "Foot", CONC_DARK, "Concrete", smooth_angle=30)
    soil = ns.box((W - 0.4, D - 0.4, 0.04), loc=(0, 0, SOIL_Z - 0.02), bevel=0.0)
    C.part([soil], "Soil", C.SOIL, "Fabric", smooth_angle=None)

    greens = {C.FOLIAGE[0]: [], C.FOLIAGE[1]: [], C.FOLIAGE[2]: []}
    # (x, y, radius, z-squash, colour index): four big clumps + three small fill-ins, faceted
    clumps = [(-2.15, 0.08, 0.78, 0.78, 0), (-0.75, -0.06, 0.86, 0.82, 1), (0.7, 0.1, 0.82, 0.8, 0), (2.15, -0.04, 0.76, 0.76, 1),
              (-1.45, -0.42, 0.46, 0.8, 2), (0.0, 0.48, 0.5, 0.85, 2), (1.45, -0.4, 0.46, 0.8, 2)]
    for i, (x, y, r, sq, ci) in enumerate(clumps):
        o = ns.sphere(r, loc=(x, y, SOIL_Z + r * 0.38), scale=(1.0, 0.92, sq), segs=7, rings=5)
        ns.jitter(o, amount=0.09 * r, seed=10 + i)
        greens[C.FOLIAGE[ci]].append(o)
    for i, (col, objs) in enumerate(greens.items()):
        if objs:
            C.part(objs, f"Shrubs{i}", col, smooth_angle=None)


META = {"night": "desaturated foliage greens (shared brief palette)"}

if __name__ == "__main__":
    C.run(build, "Shop_SidewalkPlanter", budget=700, meta=META)
