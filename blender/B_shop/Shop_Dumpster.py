"""Shop_Dumpster — big front-load alley dumpster (Mr. Usual "alley dumpster" clue spot).

Dark green painted steel body with a slanted front, rolled top lip, vertical ribs, fork
pockets on both ends and casters; two black plastic lids — LidL closed, LidR flipped open
and resting back (both role "dumpster_lid") — with black trash bags bulging out and one bag
dumped on the ground. Front = -Y. Pivot = bottom-centre.
Socket Clue = inside the open half, on top of the bags.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L = 7.0
GREEN = "#2F5B40"
LID = "#1C1D20"
BAG = "#151619"
YB, YF, YT = 1.9, -1.55, -2.05      # back y, front-bottom y, front-top y
ZB, ZT = 0.6, 4.2


def build():
    prof = C.fillet([(YF, ZB), (YB, ZB), (YB, ZT), (YT, ZT)], [0.15, 0.15, 0.05, 0.05], 2)
    body = C.prism(prof, "x", -L / 2, L / 2)
    ns.bevel(body, width=0.08, segments=1)
    paint = [body]
    lip = C.ring_slab(C.rrect(L + 0.2, YB - YT + 0.24, 0.12, 1, 0, (YB + YT) / 2),
                      C.rrect(L - 0.2, YB - YT - 0.16, 0.08, 1, 0, (YB + YT) / 2), "z", ZT - 0.25, ZT)
    paint.append(lip)
    for x in (-2.2, 0.0, 2.2):        # vertical ribs on the slanted front
        rib = C.prism([(YF - 0.12, ZB + 0.2), (YF, ZB + 0.2), (YT, ZT - 0.3), (YT - 0.12, ZT - 0.3)], "x", x - 0.12, x + 0.12)
        paint.append(rib)
    for sx in (-1, 1):                # fork pockets on the ends
        pk = C.ring_slab(C.rrect(1.0, 0.7, 0.08, 1, 0.2, 2.6), C.rrect(0.75, 0.45, 0.05, 1, 0.2, 2.6), "x",
                         *sorted((sx * L / 2, sx * (L / 2 + 0.25))))
        paint.append(pk)
    ns.tag(C.merge(paint, "Body"), "Body", GREEN, "Metal", recolor="dumpster_paint", can_collide=True, smooth_angle=40)

    # lids (hinged along the back top edge)
    hw = L / 2 - 0.1
    lidL = ns.box((hw, YB - YT + 0.1, 0.18), loc=(-L / 4, (YB + YT) / 2, ZT + 0.09), rot=(-2, 0, 0), bevel=0.06,
                  segments=1)
    ns.tag(lidL, "LidL", LID, recolor="dumpster_lid", smooth_angle=40)
    lidR = ns.box((hw, YB - YT + 0.1, 0.18), loc=(0, -(YB - YT + 0.1) / 2, 0.09), bevel=0.06, segments=1)
    ns.apply_all(lidR)
    lidR.rotation_euler = (math.radians(-118), 0, 0)
    lidR.location = (L / 4, YB + 0.05, ZT + 0.12)
    ns.apply_all(lidR)
    ns.tag(lidR, "LidR", LID, recolor="dumpster_lid", smooth_angle=40)

    bags = []
    for (x, y, z, s) in ((1.2, -0.3, ZT - 0.05, 1.0), (2.4, 0.5, ZT + 0.05, 0.9), (1.7, 1.1, ZT - 0.1, 0.8),
                         (-2.0, -3.0, 0.62, 1.0)):
        b = ns.sphere(1.0, loc=(x, y, z), scale=(0.85 * s, 0.75 * s, 0.62 * s), segs=10, rings=6)
        knot = ns.cyl(0.12 * s, 0.3 * s, loc=(x + 0.1, y, z + 0.6 * s), verts=6, radius_top=0.03, bevel=0.0)
        bags += [b, knot]
    C.part(bags, "Bags", BAG, "Plastic", smooth_angle=70)

    wheels = []
    for sx in (-1, 1):
        for y in (YF + 0.4, YB - 0.4):
            wheels.append(ns.cyl(0.28, 0.22, loc=(sx * (L / 2 - 0.6), y, 0.28), rot=(0, 90, 0), verts=10, bevel=0.03,
                                 segments=1))
            wheels.append(ns.box((0.4, 0.4, 0.12), loc=(sx * (L / 2 - 0.6), y, 0.56), bevel=0.02, segments=1))
    # hinge knuckles along the back top edge (two per lid): the open lid's hinge edge sat 0.12 above the lip
    # with nothing joining them (floating lid); the knuckles span lip top -> lid hinge edge
    for cxl in (-L / 4, L / 4):
        for dx in (-1.1, 1.1):
            wheels.append(ns.cyl(0.1, 0.4, loc=(cxl + dx, YB + 0.06, ZT + 0.1), rot=(0, 90, 0), verts=8, bevel=0.02,
                                 segments=1))
    C.part(wheels, "Casters", "#2A2B2F", smooth_angle=50)


META = {"size": [L + 0.5, 6.0, 4.4], "clue_spot": True, "lids": ["LidL", "LidR"],
        "variants": {"Blue": {"dumpster_paint": "#2C4A6E"}}}

if __name__ == "__main__":
    C.run(build, "Shop_Dumpster", meta=META, sockets={"Clue": ((1.8, 0.2, ZT + 0.5), 0.0)})
