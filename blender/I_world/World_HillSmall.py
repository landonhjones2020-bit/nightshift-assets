"""World_HillSmall — smaller low-poly rolling berm (~90 long (X) x 14 tall x 40 deep).

Same construction and ground contract as World_Hill: jittered heightfield, two rolling
summits, crest a little toward the back (+Y), ends taper to the ground, flat-shaded dark
grass green with a scatter of slightly lighter facets. Z = 0 = ground = PIVOT; the outer
footprint edge and the flat underside sit at Z = -0.5 so there is never a gap on flat
ground. Exports as 1 MeshPart (SmoothPlastic, vertex colours, no collision).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
LX, DY, H = 90.0, 40.0, 14.0


def build():
    hill = C.hill_mesh(LX, DY, H, nu=17, nv=9, seed=19, crest=0.14,
                       humps=((-0.32, 0.88), (0.36, 1.0)), sink=0.5, end_w=0.22, taper=0.58)
    rnd = random.Random(43)
    pick = {}
    for poly in hill.data.polygons:
        pick[poly.index] = "L" if (poly.normal.z > 0.2 and rnd.random() < 0.32) else "D"
    parts = C.split_faces(hill, lambda c, n, i: pick[i], name="Hill")
    C.part([parts["D"]], "Grass", C.HILL, "SmoothPlastic", smooth_angle=None)
    C.part([parts["L"]], "GrassLight", C.HILL_LIGHT, "SmoothPlastic", smooth_angle=None)


META = {"kind": "hill", "pivot": "bottom-centre at ground level (Z=0)", "ground_z": 0.0, "skirt_z": -0.5,
        "chain": "overlap neighbours ~12 studs along X; ends taper to the ground"}

if __name__ == "__main__":
    C.run(build, "World_HillSmall", meta=META, far_kw={"yaw": -20.0})
