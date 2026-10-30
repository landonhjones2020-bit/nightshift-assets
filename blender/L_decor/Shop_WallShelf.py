"""Shop_WallShelf — two-tier stainless kitchen wall shelf, stocked.

Two stainless shelf boards on four open-gusset brackets. Lower shelf: a stack of white
plates, three tomato cans with red labels, a pickle jar and a pepper jar (gold lids, cream
label bands) and a blue salt canister. Upper shelf: a row of six spice tins with coloured
lids and label bands, two tall flour / sugar canisters, an oil bottle and a cracker box; two bowls at the lower right. Labels are
simple coloured bands. Wall-mounted: pivot = bottom-centre of the back face (+Y, touches
the wall). ~4 x 2.4 x 1.2.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D = 4.0, 1.2
SHELVES = (0.55, 1.55)        # board bottoms
BT = 0.08                     # board thickness
BR_X = (-1.5, 1.5)
FRONT = -D                    # board front edge y


def bracket(x, top):
    """Open right-triangle gusset in the YZ plane under a board (wall at y = 0)."""
    a, b = 0.88, 0.55
    o = [(0.0, top), (-a, top), (0.0, top - b)]
    c = math.hypot(a, b)
    r = (a + b - c) / 2
    ic = (-r, top - r)
    f = (r - 0.075) / r
    i = [(ic[0] + f * (y - ic[0]), ic[1] + f * (z - ic[1])) for y, z in o]
    return C.ring_slab(o, i, "x", x - 0.035, x + 0.035)


def build():
    steel = []
    for z in SHELVES:
        steel.append(ns.box((W, D, BT), loc=(0, -D / 2, z + BT / 2), bevel=0.03, segments=1))
        for x in BR_X:
            steel.append(bracket(x, z))
    C.part(steel, "Steel", C.STAINLESS, "Metal", smooth_angle=35)

    z1 = SHELVES[0] + BT          # lower shelf top
    z2 = SHELVES[1] + BT          # upper shelf top
    plates, cans, can_lbl, metal, jars, lids, lbl_cream, salt, salt_lbl = [], [], [], [], [], [], [], [], []
    tins, tin_lbl, tin_lids, canisters, can_tops, oil = [], [], {}, [], [], []

    # lower: plate stack
    for k in range(5):
        plates.append(ns.cyl(0.33, 0.055, loc=(-1.45, -0.55, z1 + 0.03 + k * 0.058), verts=10, radius_top=0.38, bevel=0.0))
    # tomato cans
    for k, x in enumerate((-0.78, -0.42, -0.6)):
        zc = z1 + (0.0 if k < 2 else 0.42)
        yc = -0.62 if k < 2 else -0.6
        metal.append(ns.cyl(0.16, 0.42, loc=(x, yc, zc + 0.21), verts=8, bevel=0.0))
        can_lbl.append(C.band(0.168, 0.26, loc=(x, yc, zc + 0.21), verts=8))
    # pickle jar + pepper jar
    for x, col in ((0.18, "#6E9A35"), (0.72, "#C9432F")):
        j = ns.lathe([(0.0, 0.0), (0.24, 0.0), (0.26, 0.04), (0.26, 0.5), (0.2, 0.58), (0.0, 0.58)], verts=8,
                     loc=(x, -0.55, z1))
        jars.append((j, col))
        lids.append(ns.cyl(0.21, 0.09, loc=(x, -0.55, z1 + 0.62), verts=8, bevel=0.0))
        lbl_cream.append(C.band(0.268, 0.2, loc=(x, -0.55, z1 + 0.27), verts=8))
    # salt canister
    salt.append(ns.cyl(0.17, 0.42, loc=(1.15, -0.6, z1 + 0.21), verts=8, bevel=0.0))
    salt_lbl.append(C.band(0.177, 0.14, loc=(1.15, -0.6, z1 + 0.24), verts=8))

    # upper: six spice tins with coloured lids + label bands
    lid_cols = ("#C9432F", "#E3B23C", "#4E8F3A", "#D9782E", "#7A4B2A", "#C9432F")
    for k, col in enumerate(lid_cols):
        x = -1.62 + k * 0.26
        tins.append(ns.cyl(0.105, 0.26, loc=(x, -0.5, z2 + 0.13), verts=6, bevel=0.0))
        tin_lbl.append(C.band(0.11, 0.1, loc=(x, -0.5, z2 + 0.12), verts=6))
        tin_lids.setdefault(col, []).append(ns.cyl(0.11, 0.06, loc=(x, -0.5, z2 + 0.29), verts=6, bevel=0.0))
    # flour + sugar canisters (cream with red / blue bands)
    for x, band_col in ((0.0, "#C9432F"), (0.52, "#3C6FB0")):
        canisters.append(ns.cyl(0.22, 0.62, loc=(x, -0.52, z2 + 0.31), verts=8, bevel=0.0))
        tin_lids.setdefault(band_col, []).append(C.band(0.226, 0.12, loc=(x, -0.52, z2 + 0.36), verts=8))
        can_tops.append(ns.cyl(0.18, 0.1, loc=(x, -0.52, z2 + 0.67), verts=8, bevel=0.0))
    # oil bottle
    oil.append(ns.lathe([(0.0, 0.0), (0.14, 0.0), (0.15, 0.36), (0.06, 0.52), (0.05, 0.64), (0.0, 0.64)], verts=8,
                        loc=(1.15, -0.5, z2)))
    oil_cap = ns.cyl(0.055, 0.07, loc=(1.15, -0.5, z2 + 0.67), verts=6, bevel=0.0)
    # cracker box (upper right) + two stacked bowls (lower right, clear of the bracket above)
    box = ns.box((0.38, 0.26, 0.6), loc=(1.65, -0.45, z2 + 0.3), rot=(0, 0, -8), bevel=0.02, segments=1)
    box_band = C.quad_xz(-0.15, 0.15, 0.24, 0.4, -0.136)
    C.place([box_band], loc=(1.65, -0.45, z2), yaw=-8)
    bowls = [ns.cyl(0.2, 0.13, loc=(1.68, -0.6, z1 + 0.065 + k * 0.1), verts=8, radius_top=0.27, bevel=0.0) for k in range(2)]

    C.part(plates, "Plates", "#F4F2EC", smooth_angle=40)
    C.part(metal + [oil_cap], "Tin", C.STAINLESS, "Metal", smooth_angle=50)
    C.part(can_lbl, "CanLabels", "#C8352B", smooth_angle=50)
    for i, (j, col) in enumerate(jars):
        C.part([j], f"Jar{i}", col, smooth_angle=60)
    C.part(lids + can_tops, "Lids", "#D8B24A", "Metal", smooth_angle=50)
    C.part(lbl_cream, "JarLabels", "#F1E8D2", smooth_angle=50)
    C.part(salt + canisters, "Canisters", "#F1E8D2", smooth_angle=50)
    C.part(salt_lbl, "SaltLabel", "#3C6FB0", smooth_angle=50)
    C.part(tins, "Tins", "#C9CED3", "Metal", smooth_angle=50)
    C.part(tin_lbl, "TinLabels", "#F1E8D2", smooth_angle=50)
    for i, (col, objs) in enumerate(tin_lids.items()):
        C.part(objs, f"Colour{i}", col, smooth_angle=50)
    C.part(oil, "Oil", "#D8A93A", smooth_angle=60)
    C.part([box], "CrackerBox", "#E0582F", smooth_angle=30)
    C.part([box_band], "CrackerLabel", "#F6E7C8", smooth_angle=None)
    C.part(bowls, "Bowls", "#9CC7DA", smooth_angle=40)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)",
        "shelf_tops": [round(SHELVES[0] + BT, 3), round(SHELVES[1] + BT, 3)]}

if __name__ == "__main__":
    C.run(build, "Shop_WallShelf", mount="wall", budget=1500, meta=META)
