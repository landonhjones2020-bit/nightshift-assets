"""Lobby_ShoeCubby — open 3 x 3 shoe cubby shelf (4 W x 4 H x 1.5 D) with sneakers and boots.

A maple cubby shelf (Lobby_Bench maple) on a black toe-kick, lined slate blue inside, and a
cream name card on the lip under every cubby. Seven cubbies hold a pair each, toes out: five
pairs of sneakers (white rubber soles, contrasting laces) in red-orange, cream, navy,
mustard and slate, brown work boots and black kitchen rubber boots; one cubby holds a rolled
towel, one is empty.

Front = -Y, pivot = bottom-centre. Collides (the shelf).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 4.0, 4.0, 1.5
KICK = 0.2
SIDE = 0.14
SHELF = 0.1
TOP_Z = 3.85
FY = -D / 2
X_IN = W / 2 - SIDE                        # inner half width
COL_W = (2 * X_IN - 2 * SHELF) / 3
Z_IN0 = KICK + 0.14                        # bottom shelf top
ROW_H = (TOP_Z - Z_IN0 - 2 * SHELF) / 3
BACK_IN = 0.68                             # slate liner front face (cubby back)
WHITE = "#F6F4EE"
BROWN = "#7A4B2C"
BROWN_SOLE = "#3A2A1E"
DARK = "#2A2A2E"
# cubby contents, (row 0 = bottom, col 0 = left as seen from the front)
CONTENTS = {(2, 0): ("sneaker", C.BRAND, C.CREAM), (2, 1): ("boot", BROWN, BROWN_SOLE), (2, 2): ("sneaker", C.CREAM, C.BRAND),
            (1, 0): ("sneaker", C.NAVY, C.MUSTARD), (1, 1): ("towel", None, None), (1, 2): ("sneaker", C.MUSTARD, C.NAVY),
            (0, 0): ("boot", "#26262A", C.MUSTARD), (0, 1): ("sneaker", C.SLATE, C.CREAM)}


def cell(r, c):
    """Cubby (x centre, z floor) for row r, column c."""
    x = -X_IN + COL_W / 2 + c * (COL_W + SHELF)
    z = Z_IN0 + r * (ROW_H + SHELF)
    return x, z


def footprint(L, hw, n=8):
    """Shoe sole outline (x, y), toe toward -y, the heel end narrower."""
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        y = (L / 2) * math.sin(a)
        x = hw * math.cos(a) * (1.0 - 0.2 * max(0.0, math.sin(a)))
        out.append((x, y))
    return out


def upper(L, hw, levels, n=8):
    """Lofted shoe upper: levels = [(z, toe_recede, width_scale)], the heel stays at +L/2."""
    fp = footprint(L, hw, n)
    rings = []
    for z, rec, ws in levels:
        y0 = -L / 2 + rec
        rings.append([(x * ws, y0 + (y + L / 2) * (L / 2 - y0) / L, z) for x, y in fp])
    bm = C.bmesh.new()
    vr = [[bm.verts.new(p) for p in r] for r in rings]
    for a, b in zip(vr[:-1], vr[1:]):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([a[k], a[j], b[j], b[k]])
    bm.faces.new(list(reversed(vr[0])))
    bm.faces.new(vr[-1])
    C.bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, "Upper"), rings


def shoe(kind, col, accent, g):
    """One shoe built at the origin (toe toward -Y). Adds to g[colour]."""
    if kind == "sneaker":
        L, hw = 0.78, 0.17
        C.add(g, WHITE, C.prism(footprint(L + 0.04, hw + 0.02), "z", 0.0, 0.09))
        up, rings = upper(L, hw, [(0.08, 0.02, 0.98), (0.22, 0.08, 0.95), (0.4, 0.44, 0.78)])
        C.add(g, col, up)
        top = rings[-1]
        cx = sum(p[0] for p in top) / len(top)
        cy = sum(p[1] for p in top) / len(top)
        C.add(g, DARK, C.flat_poly_3d([(cx + (p[0] - cx) * 0.72, cy + (p[1] - cy) * 0.66, 0.414) for p in top], up=True))
        # laces: quads lying on the vamp slope (front point of ring 2 -> front point of ring 3)
        a = C.Vector((0.0, rings[1][6][1], 0.22))
        b = C.Vector((0.0, rings[2][6][1], 0.4))
        sdir = (b - a).normalized()
        nrm = C.Vector((0.0, -sdir.z, sdir.y))
        for t in (0.28, 0.5, 0.72):
            c = a.lerp(b, t) + nrm * 0.014
            hx, hs = C.Vector((0.085, 0, 0)), sdir * 0.016
            C.add(g, accent, C.flat_poly_3d([c - hx - hs, c + hx - hs, c + hx + hs, c - hx + hs], up=None,
                                            facing_out=tuple(nrm)))
    else:   # boot: sole, foot, tall shaft, collar band, dark opening
        L, hw = 0.8, 0.18
        C.add(g, accent if accent != C.MUSTARD else "#141416", C.prism(footprint(L + 0.04, hw + 0.02), "z", 0.0, 0.11))
        up, _rings = upper(L, hw, [(0.1, 0.02, 0.98), (0.22, 0.06, 0.96), (0.32, 0.24, 0.9)])
        C.add(g, col, up)
        C.add(g, col, C.loft([(0.25, 0.3, 0.36, 0.13), (0.74, 0.32, 0.36, 0.14)], segs=1, cy=0.18))
        C.add(g, accent if accent == C.MUSTARD else C.CREAM,
              C.loft([(0.6, 0.3143 * 1.12, 0.36 * 1.12, 0.1371 * 1.12), (0.7, 0.3184 * 1.12, 0.36 * 1.12, 0.1392 * 1.12)],
                     segs=1, cy=0.18))
        C.add(g, DARK, C.flat_poly_3d([(x, 0.18 + y, 0.748) for x, y in C.rrect(0.22, 0.27, 0.09, 1)], up=True))


def build():
    rnd = random.Random(12)
    wood = []
    for sx in (-1, 1):
        wood.append(ns.box((SIDE, D, TOP_Z - KICK), loc=(sx * (W / 2 - SIDE / 2), 0, (KICK + TOP_Z) / 2), bevel=0.03, segments=1))
    wood.append(ns.box((W, D + 0.04, 0.15), loc=(0, -0.02, TOP_Z + 0.075), bevel=0.04, segments=1))
    wood.append(ns.box((2 * X_IN + 0.02, BACK_IN - FY, 0.14), loc=(0, (FY + BACK_IN) / 2, KICK + 0.07), bevel=0.03, segments=1))
    for r in (1, 2):
        z = Z_IN0 + r * ROW_H + (r - 0.5) * SHELF
        wood.append(ns.box((2 * X_IN + 0.02, BACK_IN - FY - 0.03, SHELF), loc=(0, (FY + 0.03 + BACK_IN) / 2, z), bevel=0.025,
                           segments=1))
    for c in (1, 2):
        x = -X_IN + c * COL_W + (c - 0.5) * SHELF
        wood.append(ns.box((SHELF, BACK_IN - FY - 0.07, TOP_Z - Z_IN0 + 0.02), loc=(x, (FY + 0.06 + BACK_IN - 0.01) / 2, (Z_IN0 + TOP_Z) / 2),
                           bevel=0.025, segments=1))
    wood.append(ns.box((2 * X_IN + 0.02, D / 2 - BACK_IN - 0.02, TOP_Z - KICK), loc=(0, (BACK_IN + 0.02 + D / 2) / 2,
                                                                                    (KICK + TOP_Z) / 2), bevel=0.0))
    C.part(wood, "Shelf", C.MAPLE, "Wood", can_collide=True, smooth_angle=40)
    liner = ns.box((2 * X_IN, 0.02, TOP_Z - Z_IN0), loc=(0, BACK_IN + 0.01, (Z_IN0 + TOP_Z) / 2), bevel=0.0)
    C.part([liner], "BackLiner", C.SLATE, smooth_angle=None)
    kick = ns.box((W - 0.2, D - 0.3, KICK), loc=(0, 0.1, KICK / 2), bevel=0.02, segments=1)
    C.part([kick], "Kick", C.BLACK, can_collide=True, smooth_angle=40)

    # name cards on the lip under every cubby
    cards, ink = [], []
    for r in range(3):
        for c in range(3):
            x, z = cell(r, c)
            zc = z - (0.07 if r == 0 else SHELF / 2)
            cards.append(C.quad_xz(x - 0.2, x + 0.2, zc - 0.035, zc + 0.035, FY - 0.012))
            ln = 0.12 + 0.05 * ((r * 3 + c) % 3)
            ink.append(C.quad_xz(x - ln, x + ln, zc - 0.008, zc + 0.008, FY - 0.02))
    C.part(cards, "Cards", C.CREAM, smooth_angle=None)
    C.part(ink, "Names", C.NAVY, smooth_angle=None)

    g = {}
    for (r, c), (kind, col, accent) in CONTENTS.items():
        x, z = cell(r, c)
        if kind == "towel":
            C.add(g, C.TOWEL, ns.cyl(0.24, 0.85, loc=(x, -0.05, z + 0.24), rot=(0, 90, 4), verts=10, bevel=0.06, segments=1))
            ax = (math.cos(math.radians(4)), math.sin(math.radians(4)))
            C.add(g, C.BRAND, ns.cyl(0.258, 0.12, loc=(x + 0.25 * ax[0], -0.05 + 0.25 * ax[1], z + 0.24), rot=(0, 90, 4),
                                     verts=10, bevel=0.0))
            continue
        for sx in (-1, 1):
            local = {}
            shoe(kind, col, accent, local)
            yaw = rnd.uniform(-8, 8) + sx * 4
            jy = rnd.uniform(-0.04, 0.04)          # one offset per shoe (all its colour parts move together)
            for colr, objs in local.items():
                C.place(objs, (x + sx * 0.22, -0.18 + jy, z), yaw=yaw)
                C.add(g, colr, objs)
    C.parts_by_colour(g, "Shoes", smooth_angle=40)


META = {"cubbies": "3 x 3", "contents": "row by row from the top, left->right (front view): red-orange sneakers, brown "
                    "work boots, cream sneakers / navy sneakers, rolled towel, mustard sneakers / black rubber boots, "
                    "slate sneakers, empty"}

if __name__ == "__main__":
    C.run(build, "Lobby_ShoeCubby", budget=2000, meta=META)
