"""Basement_OldSign — the diner's first STACKHOUSE neon sign, dead and leaning on a wall.

A faded navy board with a dull steel rim, its neon long dead: "STACK" over "HOUSE" in bent
single-stroke tubes of dull grey glass (part Tubes, role "neon", so the game could make it
flicker back to life), a border tube with one run snapped off near the top-right corner,
and the U of HOUSE cracked through at the bottom (jagged ends). A few glass shards lie on
the floor in front. No collision.
It stands on the floor leaning back 6 degrees; its top back edge touches the wall.
PIVOT = on the wall line at the floor: bottom-centre of the bbox's back (+Y) face, like a
wall prop. Front faces -Y. ~6 x 3 x 0.6.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns
W, H = 6.0, 2.95
BT = 0.14                    # board thickness (back on y = 0 before the lean)
LEAN = 6.0
TUBE_R = 0.05
TY = -BT - TUBE_R + 0.008    # tube centre plane (tubes rest on the board face)
BOARD = "#2B3346"
GW, GH = 0.55, 1.0           # glyph cell


def ell(cx, cy, rx, ry, a0, a1, n):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


# single-stroke neon glyphs on a 0.62 x 1 cell (scaled to GW x GH), each a list of strokes
GLYPHS = {
    "S": [[(0.58, 0.84), (0.44, 0.98), (0.2, 0.98), (0.05, 0.82), (0.1, 0.62), (0.5, 0.42), (0.6, 0.22), (0.47, 0.03),
           (0.2, 0.02), (0.03, 0.15)]],
    "T": [[(0.0, 1.0), (0.62, 1.0)], [(0.31, 1.0), (0.31, 0.0)]],
    "A": [[(0.02, 0.0), (0.25, 1.0), (0.37, 1.0), (0.6, 0.0)], [(0.12, 0.36), (0.5, 0.36)]],   # flat apex: no fold
    "C": [ell(0.33, 0.5, 0.3, 0.5, 40, 320, 8)],
    "K": [[(0.06, 0.0), (0.06, 1.0)], [(0.58, 1.0), (0.08, 0.42), (0.6, 0.0)]],
    "H": [[(0.06, 0.0), (0.06, 1.0)], [(0.56, 0.0), (0.56, 1.0)], [(0.06, 0.52), (0.56, 0.52)]],
    "O": [ell(0.31, 0.5, 0.29, 0.5, 90, 450, 12)],
    "U": [[(0.05, 1.0), (0.05, 0.3), (0.12, 0.08), (0.31, 0.0), (0.5, 0.08), (0.57, 0.3), (0.57, 1.0)]],
    "E": [[(0.57, 1.0), (0.05, 1.0), (0.05, 0.0), (0.57, 0.0)], [(0.05, 0.52), (0.45, 0.52)]],
}


def word(txt, cx, z0, gap=0.13):
    """Tube strokes for a word centred on x = cx, baseline z0. Returns [(stroke_pts_3d, letter)]."""
    total = len(txt) * GW + (len(txt) - 1) * gap
    x = cx - total / 2
    out = []
    for ch in txt:
        for st in GLYPHS[ch]:
            out.append(([(x + u / 0.62 * GW, TY, z0 + v * GH) for u, v in st], ch))
        x += GW + gap
    return out


def jag(p, d, r):
    """Jagged broken tube end: a short cone pointing along d from p."""
    o = C.rod(p, Vector(p) + Vector(d).normalized() * 0.09, r, verts=5, r_top=r * 0.25)
    return o


def build():
    board = C.prism(C.rrect(W - 0.1, H - 0.1, 0.25, 3, 0, H / 2), "y", -BT, 0.0)
    C.part([board], "Board", BOARD, smooth_angle=40)
    rim = C.ring_slab(C.rrect(W, H, 0.3, 3, 0, H / 2), C.rrect(W - 0.24, H - 0.24, 0.2, 3, 0, H / 2), "y", -BT - 0.05,
                      -0.012)   # back face inside the board, not on its back plane
    C.part([rim], "SignFrame", C.CONCRETE, "Metal", smooth_angle=40)

    tubes, shards, jags = [], [], []
    strokes = word("STACK", 0.0, 1.62) + word("HOUSE", 0.0, 0.36)
    for pts, ch in strokes:
        if ch == "U":   # cracked through at the bottom: two pieces with jagged ends
            # the bottom curve (pts[2] .. pts[4]) is gone; jagged stubs point into the gap
            tubes.append(C.pipe(pts[:3], TUBE_R, sides=5))
            tubes.append(C.pipe(pts[4:], TUBE_R, sides=5))
            jags.append(jag(pts[2], Vector(pts[3]) - Vector(pts[2]), TUBE_R))
            jags.append(jag(pts[4], Vector(pts[3]) - Vector(pts[4]), TUBE_R))
            continue
        closed = ch == "O"
        tubes.append(C.pipe(pts[:-1] if closed else pts, TUBE_R, sides=5, closed=closed))   # mitred joints
    # border tube with a snapped run near the top-right corner
    border = [(x, TY, z) for x, z in C.rrect(W - 0.5, H - 0.5, 0.22, 2, 0, H / 2)]
    n = len(border)
    top_right = max(range(n), key=lambda i: border[i][0] * 0.6 + border[i][2])
    k0 = (top_right - 3) % n
    run = [border[(k0 + 4 + i) % n] for i in range(n - 3)]
    tubes.append(C.pipe(run, 0.045, sides=5))
    jags.append(jag(run[0], Vector(run[0]) - Vector(run[1]), 0.045))
    jags.append(jag(run[-1], Vector(run[-1]) - Vector(run[-2]), 0.045))

    # lean back about the bottom back edge (y = 0, z = 0)
    R = Matrix.Rotation(math.radians(-LEAN), 4, "X")
    for o in [board, rim] + tubes + jags:
        ns.apply_all(o)
        o.data.transform(R)
        o.data.update()
    C.part(tubes, "Tubes", C.GLASS_DULL, "Glass", recolor="neon", cast_shadow=False, smooth_angle=60)
    C.part(jags, "Broken", C.GLASS_DULL, "Glass", cast_shadow=False, smooth_angle=None)

    # shards on the floor in front
    for k, (x, y, s, a) in enumerate(((0.9, -0.42, 0.12, 20), (1.15, -0.55, 0.08, 75), (0.7, -0.6, 0.06, 140))):
        tri = C.poly([(x + s * math.cos(math.radians(a + d)), y + s * 0.7 * math.sin(math.radians(a + d)), 0.006)
                      for d in (0, 130, 245)])
        shards.append(C.face_dir(tri, "+Z"))
    C.part(shards, "Shards", "#B4BBBE", smooth_angle=None)

    lo, hi = ns.bbox_world(ns._tagged_objects())
    pivot = ((lo.x + hi.x) / 2, hi.y, 0.0)
    meta = {"mount": "lean on a wall", "pivot": "floor, on the wall line (bottom-centre of the bbox back face)",
            "lean_deg": LEAN, "neon_part": "Tubes (dead: dull glass; role neon for a flicker scare)",
            "collide": "none"}
    return {"export": {"pivot": pivot, "meta": meta}}


if __name__ == "__main__":
    C.run(build, "Basement_OldSign", budget=2000, views=((-30, 14, False), (28, 8, True)), backdrop="wall")
