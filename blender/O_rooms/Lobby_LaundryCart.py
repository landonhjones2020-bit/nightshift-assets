"""Lobby_LaundryCart — canvas laundry cart on casters, heaped with towels (3 W x 3 H x 2 D).

A brushed-steel tube frame (base ring, four corner posts) on four black swivel casters holds a
mustard canvas bin that bulges a little, with a red-orange canvas cuff folded over the top rim.
A lumpy heap of cream towels fills the opening, topped by folded and rolled towels (cream,
white, slate blue, mustard, red-orange) and a red-orange towel draped over the right-hand side.

Front = -Y, pivot = bottom-centre. Decor (no collision). No sockets.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 3.0, 3.0, 2.0
PX, PY = 1.36, 0.93          # corner posts
BASE_Z, RIM_Z = 0.42, 2.4
CANVAS = C.MUSTARD
CUFF = C.BRAND
WHITE = "#FAF8F2"


def build():
    rnd = random.Random(5)
    steel = []
    ring = [(x, y, BASE_Z) for x, y in C.rrect(2 * PX, 2 * PY, 0.22, 2)]
    steel.append(C.pipe(ring, 0.06, sides=6, closed=True))
    for sx in (-1, 1):
        for sy in (-1, 1):
            steel.append(C.rod((sx * PX * 0.985, sy * PY * 0.975, BASE_Z), (sx * PX * 0.985, sy * PY * 0.975, RIM_Z), 0.055,
                               verts=6))
    C.part(steel, "Frame", C.STEEL, "Metal", smooth_angle=45)
    forks, wheels = [], []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (PX - 0.1), sy * (PY - 0.12)
            forks.append(ns.box((0.1, 0.24, 0.16), loc=(x, y, 0.3), bevel=0.0))
            forks.append(ns.cyl(0.07, 0.06, loc=(x, y, BASE_Z - 0.06), verts=6, bevel=0.0))
            wheels.append(ns.cyl(0.17, 0.12, loc=(x, y, 0.17), rot=(0, 90, 0), verts=8, bevel=0.0))
    C.part(forks, "Forks", C.CHROME, "Metal", smooth_angle=45)
    C.part(wheels, "Casters", C.RUBBER, smooth_angle=40)

    # canvas bin: bulging loft, closed (the towel heap covers its top)
    bag = C.loft([(0.55, 2.3, 1.46, 0.4), (1.0, 2.58, 1.72, 0.36), (1.7, 2.7, 1.83, 0.32), (2.28, 2.64, 1.77, 0.3)],
                 segs=2)
    C.part([bag], "Canvas", CANVAS, "Fabric", smooth_angle=50)
    cuff = C.ring_slab(C.rrect(2.86, 2.0, 0.34, 2), C.rrect(2.56, 1.7, 0.26, 2), "z", 2.2, 2.5)
    ns.bevel(cuff, width=0.05, segments=1)
    C.part([cuff], "Cuff", CUFF, "Fabric", smooth_angle=45)

    # towel heap: a low lumpy mound filling the opening, then a jumble of folded / rolled towels
    heap = C.loft([(2.3, 2.62, 1.76, 0.3), (2.46, 2.5, 1.62, 0.42), (2.58, 1.9, 1.18, 0.45), (2.62, 1.2, 0.65, 0.28)], segs=2)
    ns.jitter(heap, amount=0.04, seed=3)
    towels = {C.TOWEL: [heap], WHITE: [], C.BRAND: [], C.MUSTARD: [], C.SLATE: []}
    folded = ((-0.75, 0.3, 2.62, 18, (8, -6), WHITE, (0.86, 0.6, 0.18)),
              (0.55, 0.32, 2.6, -24, (-5, 9), C.SLATE, (0.9, 0.58, 0.18)),
              (-0.2, -0.32, 2.58, 8, (10, 4), C.TOWEL, (0.92, 0.6, 0.18)),
              (0.05, 0.12, 2.8, 52, (-7, -8), C.MUSTARD, (0.8, 0.52, 0.17)),
              (-0.6, -0.12, 2.78, -12, (12, 6), C.TOWEL, (0.78, 0.5, 0.16)),
              (0.72, -0.3, 2.74, 30, (6, -10), WHITE, (0.7, 0.5, 0.16)))
    for x, y, z, rz, (rx, ry), col, size in folded:
        C.add(towels, col, ns.box(size, loc=(x, y, z), rot=(rx, ry, rz), bevel=0.07, segments=1))
    # red-orange stripe across the first white towel
    C.add(towels, C.BRAND, ns.box((0.14, 0.64, 0.2), loc=(-0.55, 0.36, 2.64), rot=(8, -6, 18), bevel=0.04, segments=1))
    # rolled towels (spa rolls)
    for x, y, z, rz, col in ((0.3, 0.05, 2.97 - 0.15, 75, WHITE), (-0.25, 0.4, 2.86, 100, C.BRAND)):
        C.add(towels, col, ns.cyl(0.15, 0.6, loc=(x, y, z), rot=(90, 0, rz), verts=8, bevel=0.05, segments=1))
    # towel draped over the right-hand side of the cuff: a flap on the heap + a tail down the outside
    drape = [ns.box((0.62, 0.66, 0.06), loc=(1.12, 0.05, 2.56), rot=(0, 12, 0), bevel=0.03, segments=1),
             ns.box((0.06, 0.66, 0.85), loc=(1.45, 0.05, 2.12), rot=(0, -4, 0), bevel=0.03, segments=1)]
    C.add(towels, C.BRAND, drape)
    C.parts_by_colour(towels, "Towels", "Fabric", smooth_angle=50)


META = {"decor": True, "collide": False}

if __name__ == "__main__":
    C.run(build, "Lobby_LaundryCart", budget=2000, meta=META)
