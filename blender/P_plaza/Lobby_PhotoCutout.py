"""Lobby_PhotoCutout — "Stacky" face-in-hole photo board (5 x 7 x 0.6).

A die-cut board of the STACKHOUSE mascot Stacky: a smiling cartoon sub sandwich (long top roll
with score slashes, big eyes, rosy cheeks and a wide open smile; lettuce, tomato and cheese
peeking out; bottom bun) with navy noodle arms and white gloves holding up a sign at face height.
The sign (red-orange border, cream panel, mustard starburst) has a round FACE HOLE: players stand
behind the board and look through it. Navy noodle legs and red-orange sneakers stand on a navy
base; two wooden posts (hidden behind the legs) brace the board from behind. Layers are raised a little off each other
(cartoon foam-board look) on a cream die-cut backing. Board, base and posts collide.

Front = -Y, pivot = bottom-centre. Sockets: Face = centre of the face hole in the board plane;
Stand = ground point 0.75 behind the board (+Y) where a player stands to look through the hole.
Both yaw 0: the player faces the front (-Y), toward whoever takes the photo.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

HOLE = (0.0, 3.55, 0.6)                 # face hole centre x, z and radius
SIGN = (3.3, 2.05, 3.48)                # sign width, height, centre z
SEAM = 5.48                             # top bun bottom
BOARD = (-0.06, 0.06)                   # backing slab y range
WHITE = "#F8F4EA"
CHEEK = "#FF8FB5"
SEED = "#FBEFD2"
MOUTH = "#2A1A1F"


def paint(points, y_front, depth=0.04, name="Paint"):
    """Raised paint layer: prism from y_front back `depth`, back cap dropped (it lies on the board)."""
    o = C.prism(points, "y", y_front, y_front + depth, name=name)
    return C.drop_faces(o, lambda c, n: n.y > 0.9)


def top_bun_outline(n=16, w=2.3, h=1.32):
    pts = []
    for i in range(n + 1):
        t = math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        pts.append((w * math.copysign(abs(c) ** 0.7, c), SEAM + h * abs(s) ** 0.5))
    return pts


def build():
    sw, sh, sz = SIGN
    hx, hz, hr = HOLE
    # --- cream die-cut backing: sandwich silhouette + sign plate ---------------------------
    sub_sil = C.inset_poly(top_bun_outline() + [(-2.36, SEAM - 0.2), (-2.3, 4.75), (-1.95, 4.48), (1.95, 4.48), (2.3, 4.75),
                                                (2.36, SEAM - 0.2)], -0.12)
    def hole():
        return C.prism(C.circle_pts(hr, 20, hx, hz), "y", -1.0, 1.0)

    back_sub = C.prism(sub_sil, "y", *BOARD)
    back_sign = C.prism(C.rrect(sw + 0.24, sh + 0.24, 0.26, 2, 0, sz), "y", *BOARD)
    ns.boolean(back_sign, hole())

    # --- sandwich -----------------------------------------------------------------------------
    top = paint(top_bun_outline(), -0.1, 0.05)
    bot = paint(C.rrect(4.5, 0.8, 0.38, 3, 0, 4.9), -0.09, 0.04)
    lettuce_pts = [(2.36, SEAM + 0.06), (-2.36, SEAM + 0.06)] + [(-2.36 + 4.72 * i / 14, SEAM - 0.16 + (0.07 if i % 2 else -0.06))
                                                                   for i in range(15)]
    let = paint(lettuce_pts, -0.115, 0.05)
    tom = paint(C.rrect(4.44, 0.2, 0.08, 1, 0, SEAM - 0.2), -0.1, 0.03)
    cheese_pts = [(2.2, SEAM - 0.27), (-2.2, SEAM - 0.27), (-2.2, SEAM - 0.4), (-1.3, SEAM - 0.4), (-1.1, SEAM - 0.66),
                  (-0.9, SEAM - 0.4), (0.7, SEAM - 0.4), (0.95, SEAM - 0.72), (1.2, SEAM - 0.4), (2.2, SEAM - 0.4)]
    chz = paint(cheese_pts, -0.11, 0.04)
    seeds = []                                   # sub-roll score slashes across the top
    for x, z in ((-1.62, 6.48), (-0.58, 6.62), (0.58, 6.62), (1.62, 6.48)):
        r = math.radians(-28)
        pts = [(x + px * math.cos(r) - pz * math.sin(r), z + px * math.sin(r) + pz * math.cos(r))
               for px, pz in C.rrect(0.62, 0.11, 0.05, 1)]
        seeds.append(paint(pts, -0.115, 0.03))
    # face: eyes, pupils, glints, brows, cheeks, smile
    whites, pupils, glints, dark, cheeks, tongue = [], [], [], [], [], []
    for s in (-1, 1):
        whites.append(paint(C.ellipse_pts(0.32, 0.38, 14, s * 0.58, 6.02), -0.14, 0.04))
        pupils.append(paint(C.ellipse_pts(0.17, 0.21, 10, s * 0.53, 5.92), -0.16, 0.02))
        glints.append(paint(C.circle_pts(0.065, 6, s * 0.47 + 0.07, 6.01), -0.17, 0.01))
        brow = C.pipe([(s * 0.86, -0.14, 6.52), (s * 0.58, -0.14, 6.63), (s * 0.32, -0.14, 6.55)], 0.05, sides=4)
        dark.append(brow)
        cheeks.append(paint(C.ellipse_pts(0.24, 0.15, 10, s * 1.22, 5.72), -0.125, 0.025))
    mouth_pts = [(0.58, 5.74)] + [(0.58 * math.cos(math.pi * i / 10), 5.74 - 0.36 * math.sin(math.pi * i / 10))
                                  for i in range(1, 10)] + [(-0.58, 5.74)]
    dark.append(paint(mouth_pts, -0.135, 0.03))
    tongue.append(paint(C.ellipse_pts(0.27, 0.11, 10, 0.0, 5.47), -0.145, 0.015))
    teeth = paint(C.rrect(0.84, 0.11, 0.04, 1, 0, 5.67), -0.145, 0.015)

    # --- sign with the face hole ----------------------------------------------------------------
    border = C.prism(C.rrect(sw, sh, 0.2, 2, 0, sz), "y", -0.09, -0.05)
    panel = C.prism(C.rrect(sw - 0.3, sh - 0.3, 0.12, 2, 0, sz), "y", -0.11, -0.08)
    for o in (border, panel):
        ns.boolean(o, hole())
        C.drop_faces(o, lambda c, n: n.y > 0.9)
    star = C.ring_slab(C.star_pts(hr + 0.42, hr + 0.24, hx, hz, n=10), C.circle_pts(hr + 0.05, 20, hx, hz, math.radians(90)),
                       "y", -0.135, -0.105)
    C.drop_faces(star, lambda c, n: n.y > 0.9)
    small = [paint(C.star_pts(0.2, 0.09, x, z), -0.125, 0.02) for x, z in ((-1.25, 2.88), (1.25, 2.88))]

    # --- arms, gloves, legs, shoes, stand -------------------------------------------------------
    navy = []
    for s in (-1, 1):
        navy.append(C.pipe([(s * 2.08, -0.17, 5.02), (s * 2.38, -0.17, 4.72), (s * 2.2, -0.19, 4.3), (s * 1.78, -0.2, 4.36)],
                           0.1, sides=5, corner=0.2, corner_segs=2))
        navy.append(C.pipe([(s * 0.55, -0.02, sz - sh / 2 + 0.05), (s * 0.6, -0.06, 1.4), (s * 0.62, -0.06, 0.5)], 0.12,
                           sides=5, corner=0.3, corner_segs=2))
    gloves, cuffs = [], []
    for s in (-1, 1):
        g = paint(C.ellipse_pts(0.36, 0.3, 12, s * 1.48, 4.38), -0.24, 0.1)
        th = paint(C.ellipse_pts(0.12, 0.18, 8, s * 1.18, 4.55), -0.25, 0.06)
        gloves += [g, th]
        cuffs.append(paint(C.rrect(0.16, 0.5, 0.06, 1, s * 1.86, 4.37), -0.23, 0.08))
    shoes, soles = [], []
    for s in (-1, 1):
        shoe = C.fillet([(s * 0.3, 0.3), (s * 1.12, 0.3), (s * 1.18, 0.5), (s * 0.95, 0.66), (s * 0.4, 0.7)], 0.12, 2)
        if s < 0:
            shoe = list(reversed(shoe))
        o = C.prism(shoe, "y", -0.24, 0.08)
        shoes.append(o)
        soles.append(C.prism(C.rrect(0.9, 0.09, 0.04, 1, s * 0.74, 0.265), "y", -0.25, 0.09))
    base = C.prism(C.rrect(3.4, 0.6, 0.22, 2), "z", 0.0, 0.22)
    ns.bevel(base, width=0.04, segments=1)
    posts = [ns.box((0.16, 0.14, 6.1), loc=(s * 0.6, 0.13, 0.2 + 3.05), bevel=0.03, segments=1) for s in (-1, 1)]

    C.part([back_sub, back_sign], "Board", C.CREAM, can_collide=True, smooth_angle=40)
    C.part([top, bot], "Bun", C.BUN, smooth_angle=40)
    C.part([let], "Lettuce", C.LETTUCE, smooth_angle=None)
    C.part([tom] + tongue, "Tomato", C.TOMATO, smooth_angle=None)
    C.part([chz], "Cheese", C.CHEESE, smooth_angle=None)
    C.part(seeds, "Scores", SEED, smooth_angle=None)
    C.part(whites + glints + [teeth] + gloves, "White", WHITE, smooth_angle=50)
    C.part(pupils + dark, "Ink", MOUTH, smooth_angle=50)
    C.part(cheeks, "Cheeks", CHEEK, smooth_angle=None)
    C.part([border] + cuffs + shoes, "Red", C.BRAND, smooth_angle=40)
    C.part([panel], "SignPanel", C.PAPER, smooth_angle=40)
    C.part([star] + small, "Starburst", C.MUSTARD, smooth_angle=None)
    C.part(navy, "Limbs", C.NAVY, smooth_angle=60)
    C.part(soles, "Soles", C.CREAM_SHADE, smooth_angle=40)
    C.part([base], "Base", C.NAVY_DEEP, can_collide=True, smooth_angle=40)
    C.part(posts, "Posts", C.WOOD_LIGHT, "Wood", can_collide=True, smooth_angle=40)
    return {}


SOCKETS = {"Face": ((HOLE[0], 0.0, HOLE[1]), 0.0), "Stand": ((HOLE[0], 0.75, 0.0), 0.0)}
META = {"face_hole": {"centre_height": HOLE[1], "radius": HOLE[2], "player_scale": "about 4 studs tall"},
        "mascot": "Stacky (smiling sub sandwich) holding the sign with the face hole"}

if __name__ == "__main__":
    C.run(build, "Lobby_PhotoCutout", sockets=SOCKETS, meta=META, budget=2000, pivot=(0.0, 0.0, 0.0))
