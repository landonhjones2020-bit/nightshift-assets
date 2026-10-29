"""Shop_PantryShelf — tall wooden pantry shelving (6 wide x 2 deep x 8 tall) stocked with
cardboard boxes, cans, pickle jars, flour sacks and squeeze bottles.
Ladder-style side frames with cross braces, four stocked shelves + a top shelf.
Back (+Y) goes against the wall. Pivot = bottom-centre. Socket Clue = an empty slot on the
middle shelf (for a clue note / item spawn).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D, H = 6.0, 2.0, 8.0
SHELVES = (0.45, 2.3, 4.15, 6.0, 7.75)
CAN_COLS = {"CansRed": "#C8352B", "CansGreen": "#4E8F3A", "CansYellow": "#E3B23C", "CansBlue": "#3C6FB0"}


def build():
    rnd = random.Random(7)
    wood = []
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.1)
        for sy in (-1, 1):
            wood.append(ns.box((0.2, 0.2, H), loc=(x, sy * (D / 2 - 0.1), H / 2), bevel=0.04, segments=1))
        for z in (0.2, H - 0.15):
            wood.append(ns.box((0.16, D - 0.2, 0.16), loc=(x, 0, z), bevel=0.0))
    for z in SHELVES:
        wood.append(ns.box((W - 0.05, D, 0.14), loc=(0, 0, z), bevel=0.04, segments=1))
    # diagonal braces on the back
    wood.append(C.pipe([(-W / 2 + 0.2, D / 2 - 0.05, 0.4), (W / 2 - 0.2, D / 2 - 0.05, H - 0.4)], 0.05, sides=4))
    wood.append(C.pipe([(W / 2 - 0.2, D / 2 - 0.05, 0.4), (-W / 2 + 0.2, D / 2 - 0.05, H - 0.4)], 0.05, sides=4))
    C.part(wood, "Wood", C.WOOD, "Wood", can_collide=True, smooth_angle=40)

    boxes, labels, jars, lids, sacks, bottles, tops = [], [], [], [], [], [], []
    cans = {k: [] for k in CAN_COLS}
    zt = [z + 0.07 for z in SHELVES]

    def box(cx, w, d, h, z, rz=0.0, label=True):
        boxes.append(ns.box((w, d, h), loc=(cx, -0.05, z + h / 2), rot=(0, 0, rz), bevel=0.03 if label else 0.0,
                            segments=1))
        if label:
            labels.append(ns.box((w * 0.7, 0.02, h * 0.28), loc=(cx, -0.05 - d / 2 - 0.01, z + h * 0.58), bevel=0.0))

    def can_row(x0, n, col, z, stack=1):
        for i in range(n):
            for k in range(stack):
                cx, cz = x0 + i * 0.46, z + 0.25 + k * 0.5
                cans[col].append(C.band(0.2, 0.36, loc=(cx, -0.45, cz), verts=8))
                tops.append(ns.cyl(0.185, 0.48, loc=(cx, -0.45, cz), verts=8, bevel=0.0))

    def jar(cx, z):
        jars.append(ns.lathe([(0.27, 0.0), (0.28, 0.55), (0.2, 0.68), (0.0, 0.68)], verts=8, loc=(cx, -0.3, z)))
        lids.append(ns.cyl(0.21, 0.1, loc=(cx, -0.3, z + 0.72), verts=8, bevel=0.0))

    def bottle(cx, z):
        bottles.append(ns.lathe([(0.14, 0.0), (0.15, 0.5), (0.06, 0.66), (0.02, 0.82), (0.0, 0.82)], verts=8,
                                loc=(cx, -0.4, z)))

    # bottom: flour sacks + a big box
    for cx in (-2.1, -0.8):
        sacks.append(ns.box((1.2, 1.1, 1.35), loc=(cx, 0.0, zt[0] + 0.62), rot=(0, 0, rnd.uniform(-8, 8)),
                            bevel=0.22, segments=1))
    box(1.35, 1.5, 1.4, 1.3, zt[0], 3)
    # shelf 1: stacked cans, a box, two pickle jars
    can_row(-2.55, 3, "CansRed", zt[1], stack=2)
    box(-0.3, 1.2, 1.3, 1.1, zt[1], -4)
    jar(0.8, zt[1])
    jar(1.45, zt[1])
    can_row(2.25, 2, "CansGreen", zt[1])
    # shelf 2: two boxes | empty clue slot | squeeze bottles
    box(-2.3, 1.1, 1.3, 1.25, zt[2], 2)
    box(-1.2, 0.9, 1.2, 0.9, zt[2], -3)
    for cx in (1.05, 1.4, 1.75):
        bottle(cx, zt[2])
    can_row(2.3, 2, "CansYellow", zt[2])
    # shelf 3: cans, box, jar
    can_row(-2.55, 3, "CansBlue", zt[3])
    box(0.0, 1.4, 1.4, 1.0, zt[3], 2)
    jar(1.4, zt[3])
    box(2.25, 1.0, 1.2, 0.7, zt[3], -2, label=False)
    # top: flat boxes
    box(-1.6, 1.6, 1.5, 0.45, zt[4], 4, label=False)
    box(1.7, 1.4, 1.4, 0.6, zt[4], -3)
    C.part(boxes, "Boxes", C.CARDBOARD, smooth_angle=40)
    C.part(labels, "Labels", C.BRAND)
    for k, objs in cans.items():
        if objs:
            C.part(objs, k, CAN_COLS[k], smooth_angle=50)
    C.part(tops, "CanMetal", C.STAINLESS, "Metal", smooth_angle=50)
    if jars:
        C.part(jars, "Jars", "#7FA83A", smooth_angle=60)
        C.part(lids, "Lids", "#D8C25A", "Metal")
    if sacks:
        C.part(sacks, "Sacks", "#E9E1CF", "Fabric", smooth_angle=50)
    if bottles:
        C.part(bottles, "Bottles", C.MUSTARD, smooth_angle=60)


META = {"size": [W, H, D], "back": "+Y against the wall"}

if __name__ == "__main__":
    C.run(build, "Shop_PantryShelf", meta=META, sockets={"Clue": ((0, -0.3, SHELVES[2] + 0.07), 0.0)})
