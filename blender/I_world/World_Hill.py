"""World_Hill — low-poly rolling ridge / berm (~180 long (X) x 26 tall x 70 deep).

Rings the maps beyond the treeline. A jittered heightfield with three rolling summits
along an irregular crest (crest sits a little toward the back, +Y, so the front slope
facing the playfield (-Y) is the long gentle one). The footprint narrows toward the X
ends and the height tapers to nothing there, so hills overlap / chain without seams.
Flat-shaded facets in dark grass green with a scatter of slightly lighter facets.

Ground contract: Z = 0 is the ground plane and the PIVOT (bottom-centre at ground level,
passed explicitly). The outer footprint edge sinks to Z = -0.5 and the underside is one
flat cap at Z = -0.5, so on flat ground there is never a visible gap or edge.
Exports as 1 MeshPart (SmoothPlastic, vertex colours, no collision).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
LX, DY, H = 180.0, 70.0, 26.0


def build():
    hill = C.hill_mesh(LX, DY, H, nu=25, nv=11, seed=7, crest=0.16,
                       humps=((-0.5, 0.8), (0.08, 1.0), (0.58, 0.72)), sink=0.5, end_w=0.2, taper=0.6)
    rnd = random.Random(41)
    pick = {}
    for poly in hill.data.polygons:
        pick[poly.index] = "L" if (poly.normal.z > 0.2 and rnd.random() < 0.32) else "D"
    parts = C.split_faces(hill, lambda c, n, i: pick[i], name="Hill")
    C.part([parts["D"]], "Grass", C.HILL, "SmoothPlastic", smooth_angle=None)
    C.part([parts["L"]], "GrassLight", C.HILL_LIGHT, "SmoothPlastic", smooth_angle=None)


META = {"kind": "hill", "pivot": "bottom-centre at ground level (Z=0)", "ground_z": 0.0, "skirt_z": -0.5,
        "chain": "overlap neighbours ~25 studs along X; ends taper to the ground"}

if __name__ == "__main__":
    C.run(build, "World_Hill", meta=META, far_kw={"yaw": -20.0})
