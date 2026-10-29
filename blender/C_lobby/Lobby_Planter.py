"""Lobby_Planter — square brick planter (3.4 x 3.4 x 1.6) with a rounded shrub.

Red brick box with modelled mortar rings and a cream concrete cap, dark soil, a clumpy
two-tone shrub and a scatter of mustard and pink flowers. The brick box collides.
Front = -Y (reads the same from every side), pivot = bottom-centre.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
S = 3.4
HB = 1.35                     # brick top / cap bottom
SOIL = "#4A3528"
FLOWER_PINK = "#F27BAE"


def build():
    box = ns.box((S, S, HB), loc=(0, 0, HB / 2), bevel=0.03, segments=1)
    C.part([box], "Brick", C.BRICK, can_collide=True, smooth_angle=30)
    rings = [ns.box((S + 0.05, S + 0.05, 0.06), loc=(0, 0, z), bevel=0.0) for z in (0.45, 0.9)]
    # staggered head joints, two per course per face
    for row, (za, zb) in enumerate(((0.06, 0.45), (0.45, 0.9), (0.9, HB))):
        zc, h = (za + zb) / 2, zb - za - 0.06
        for u in ((-0.85, 0.85) if row % 2 == 0 else (-0.05, 1.55)):
            for ang in range(4):
                p = C.yaw_point((u, -S / 2 - 0.02, zc), 90 * ang)
                rings.append(ns.box((0.06 if ang % 2 == 0 else 0.05, 0.05 if ang % 2 == 0 else 0.06, h), loc=p,
                                    bevel=0.0))
    C.part(rings, "Mortar", C.MORTAR, smooth_angle=30)
    outer = C.rrect(S + 0.3, S + 0.3, 0.12, 2)
    inner = C.rrect(S - 0.5, S - 0.5, 0.08, 2)
    cap = C.ring_slab(outer, inner, "z", HB, HB + 0.22)
    ns.bevel(cap, width=0.04, segments=1, angle=50)
    C.part([cap], "Cap", C.CREAM, "Concrete", can_collide=True, smooth_angle=40)
    soil = ns.box((S - 0.5, S - 0.5, 0.1), loc=(0, 0, HB + 0.1), bevel=0.0)
    C.part([soil], "Soil", SOIL, "Fabric", smooth_angle=None)

    dark, light = [], []
    blobs = [((0, 0, HB + 0.85), 1.05, dark), ((0.55, -0.35, HB + 0.75), 0.8, light), ((-0.6, -0.3, HB + 0.7), 0.75, light),
             ((-0.35, 0.55, HB + 0.8), 0.8, dark), ((0.45, 0.5, HB + 1.15), 0.7, light)]
    for i, (p, r, lst) in enumerate(blobs):
        o = ns.sphere(r, loc=p, scale=(1, 1, 0.9), segs=10, rings=6)
        ns.jitter(o, amount=0.07, seed=3 + i)
        lst.append(o)
    C.part(dark, "ShrubDark", C.SHRUB_DARK, smooth_angle=60)
    C.part(light, "ShrubLight", C.SHRUB, smooth_angle=60)
    must, pink = [], []
    c0 = Vector((0, 0, HB + 0.85))
    for k in range(10):
        a, e = k * 2.39, math.radians(10 + 55 * ((k * 0.37) % 1.0))
        d = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        t_out = 0.0
        for p, r, _ in blobs:   # farthest exit point of the ray through all shrub blobs
            ci = Vector(p) - c0
            b = d.dot(ci)
            disc = b * b - (ci.length_squared - (r * 0.93) ** 2)
            if disc > 0:
                t_out = max(t_out, b + math.sqrt(disc))
        (must if k % 2 else pink).append(ns.sphere(0.12, loc=c0 + d * (t_out + 0.02), segs=6, rings=4))
    C.part(must, "FlowersMustard", C.MUSTARD, smooth_angle=60)
    C.part(pink, "FlowersPink", FLOWER_PINK, smooth_angle=60)


if __name__ == "__main__":
    C.run(build, "Lobby_Planter", meta={"size": [S + 0.3, S + 0.3, 3.4]})
