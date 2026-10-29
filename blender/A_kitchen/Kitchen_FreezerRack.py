"""Kitchen_FreezerRack — chrome wire shelving for the walk-in freezer, with frosty stock.

4 wide x 1.8 deep x 5.6 tall (a head taller than an avatar). Four round posts, four wire
shelves (rims + cross wires), a few kraft boxes and white tubs with icy frost caps, and
icicles hanging from the shelf rims (Ice). Decor only (gameplay stock lives in
Kitchen_Crate). Shelves and posts collide. Front faces -Y.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D, H = 4.0, 1.8, 5.6
SHELVES = (0.45, 2.0, 3.55, 5.1)
CHROME = "#C4CBD1"
KRAFT = "#A98D6E"
TUB = "#E6EAEC"


def shelf(z):
    objs = []
    for y in (-D / 2 + 0.04, D / 2 - 0.04):           # front/back rims (chunky)
        objs.append(ns.box((W - 0.06, 0.06, 0.1), loc=(0, y, z), bevel=0.0))
    for x in (-W / 2 + 0.04, W / 2 - 0.04):           # side rims
        objs.append(ns.box((0.06, D - 0.06, 0.08), loc=(x, 0, z), bevel=0.0))
    n = 9
    for k in range(1, n):                               # cross wires front-to-back
        x = -W / 2 + W * k / n
        objs.append(ns.box((0.035, D - 0.08, 0.035), loc=(x, 0, z + 0.02), bevel=0.0))
    return objs


def build():
    wire = []
    for z in SHELVES:
        wire += shelf(z)
    posts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = (sx * (W / 2 - 0.02), sy * (D / 2 - 0.02))
            posts.append(C.rod((p[0], p[1], 0.06), (p[0], p[1], H), 0.075, verts=8))
            posts.append(ns.cyl(0.11, 0.08, loc=(p[0], p[1], 0.04), verts=8, bevel=0.0, radius_top=0.08))
    C.part(wire + posts, "Wire", CHROME, "Metal", can_collide=True, smooth_angle=50)

    # ---- frosty stock -------------------------------------------------------------
    # (x, shelf index, w, d, h, rot, kind)
    stock = [(-1.15, 0, 1.3, 1.2, 0.9, 4, "box"), (0.45, 0, 1.1, 1.1, 0.75, -6, "box"),
             (1.35, 0, 0.8, 0.8, 0.55, 2, "tub"),
             (-0.9, 1, 1.5, 1.2, 0.7, -3, "box"), (0.95, 1, 0.9, 0.9, 1.0, 5, "box"),
             (-1.2, 2, 0.8, 0.8, 0.6, 0, "tub"), (-0.2, 2, 0.8, 0.8, 0.6, 8, "tub"), (1.0, 2, 1.2, 1.1, 0.85, -4, "box"),
             (0.1, 3, 1.6, 1.25, 0.6, 3, "box")]
    boxes, tubs, lids, frost = [], [], [], []
    for x, si, w, d, h, rot, kind in stock:
        z0 = SHELVES[si] + 0.04
        if kind == "box":
            boxes.append(ns.box((w, d, h), loc=(x, 0.0, z0 + h / 2), rot=(0, 0, rot), bevel=0.04, segments=1))
            # frost cap: a soft icy slab a little wider than the box
            cap = ns.box((w + 0.04, d + 0.04, 0.08), loc=(x, 0.0, z0 + h + 0.02), rot=(0, 0, rot), bevel=0.035, segments=1)
            frost.append(cap)
        else:
            tubs.append(ns.cyl(w / 2, h, loc=(x, 0.0, z0 + h / 2), verts=10, bevel=0.0, radius_top=w / 2 + 0.05))
            lids.append(ns.cyl(w / 2 + 0.08, 0.08, loc=(x, 0.0, z0 + h + 0.03), verts=10, bevel=0.03, segments=1))
    C.part(boxes, "Boxes", KRAFT, "SmoothPlastic", smooth_angle=40)
    C.part(tubs, "Tubs", TUB, "SmoothPlastic", smooth_angle=50)
    C.part(lids, "Lids", C.ICY, "SmoothPlastic", smooth_angle=50)
    C.part(frost, "Frost", C.FROST, "SmoothPlastic", smooth_angle=50)

    # ---- icicles hanging from the front rims ------------------------------------------
    ice = []
    for z, xs in ((2.0, (-1.6, -1.35, 0.3, 1.55)), (3.55, (-0.6, 0.85, 1.05)), (5.1, (-1.4, -1.2, 0.5))):
        for i, x in enumerate(xs):
            L = 0.3 + 0.14 * ((i * 7 + int(z * 3)) % 3)
            ice.append(ns.cyl(0.075, L, loc=(x, -D / 2 + 0.04, z - 0.05 - L / 2), verts=6, bevel=0.0, radius_top=0.0,
                              rot=(180, 0, 0)))
    C.part(ice, "Icicles", "#CFEFFB", "Ice", smooth_angle=60)
    return {"export": {"meta": {"decor": True}}}


if __name__ == "__main__":
    C.run(build, "Kitchen_FreezerRack")
