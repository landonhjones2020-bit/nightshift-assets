"""Basement_CageLight — caged work lamp screwed to the wall by the breaker box.

A dull-green cast junction box on the wall (four screw heads), a short pipe neck out to a
green cast housing with a domed cap, and a bare bulb (part Bulb, Neon, role "lamp") hanging
inside a mustard safety cage: a guard ring, six curved wires, a middle ring and a bottom
cap.
Wall-mounted, modelled with the box's back face on the wall plane y = 0, front -Y.
PIVOT = CENTRE OF THE BACK FACE (on the wall). Socket Light = bulb centre. No collision.
~0.6 x 1 x 0.75.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
BOX = 0.6                  # junction box width / height
BOX_D = 0.16
HY = -0.45                 # housing / cage axis (y)
RING_Z = -0.12             # guard ring (cage top)
CAGE_BOT = -0.68
BULB_Z = -0.38


def cage_r(z):
    """Cage profile radius at height z (straight upper part, rounding into the bottom cap)."""
    t = (RING_Z - z) / (RING_Z - CAGE_BOT)
    return 0.27 * math.sqrt(max(0.0, 1.0 - max(0.0, (t - 0.35) / 0.65) ** 2)) + 0.03 * (t > 0.95)


def build():
    box = ns.box((BOX, BOX_D, BOX), loc=(0, -BOX_D / 2, 0), bevel=0.06, segments=2)
    neck = C.rod((0, -BOX_D + 0.02, 0.02), (0, HY - 0.1, 0.02), 0.075, verts=8)
    housing = ns.lathe([(0.0, RING_Z - 0.02), (0.2, RING_Z - 0.02), (0.2, 0.08), (0.15, 0.15), (0.0, 0.17)], verts=10,
                       loc=(0, HY, 0))
    C.part([box, neck, housing], "Housing", C.GREEN, "Metal", smooth_angle=45)
    screws = [C.rivet((sx * 0.21, -BOX_D, sz * 0.21), (0, -1, 0), r=0.035, h=0.02) for sx in (-1, 1) for sz in (-1, 1)]
    C.part(screws, "Screws", C.STEEL, "Metal", smooth_angle=60)

    # safety cage: guard ring, middle ring, six curved wires, bottom cap
    wires = [ns.torus(0.27, 0.03, loc=(0, HY, RING_Z), major_segs=12, minor_segs=4),
             ns.torus(0.27, 0.022, loc=(0, HY, -0.36), major_segs=12, minor_segs=3)]
    zs = [RING_Z - 0.01 - (RING_Z - CAGE_BOT + 0.02) * i / 6 for i in range(7)]
    for k in range(6):
        a = math.radians(30 + 60 * k)
        pts = []
        for z in zs:
            r = max(cage_r(z), 0.05)
            pts.append((r * math.sin(a), HY - r * math.cos(a), z))
        wires.append(C.pipe(pts, 0.02, sides=4))
    wires.append(ns.cyl(0.07, 0.05, loc=(0, HY, CAGE_BOT), verts=8, bevel=0.0))
    C.part(wires, "Cage", C.MUSTARD, smooth_angle=50)

    bulb = ns.lathe([(0.0, RING_Z - 0.0), (0.09, RING_Z - 0.0), (0.095, RING_Z - 0.08), (0.15, BULB_Z + 0.07),
                     (0.18, BULB_Z), (0.165, BULB_Z - 0.09), (0.11, BULB_Z - 0.16), (0.0, BULB_Z - 0.19)], verts=10,
                    loc=(0, HY, 0))
    C.part([bulb], "Bulb", C.BULB, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)


SOCKETS = {"Light": ((0.0, HY, BULB_Z), 0.0)}
META = {"mount": "wall", "pivot": "centre of the back face, on the wall plane", "lamp_part": "Bulb",
        "light_hint": {"type": "PointLight", "socket": "Light", "color": C.BULB, "range": 10, "brightness": 0.8}}

if __name__ == "__main__":
    C.run(build, "Basement_CageLight", mount="wall", pivot=(0.0, 0.0, 0.0), sockets=SOCKETS, budget=2000, meta=META,
          socket_views=((-35, 18),))
