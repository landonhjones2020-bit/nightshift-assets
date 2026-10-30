"""Prop_Notepad — a waiter's order pad, held in the player's RIGHT HAND while writing an order.

Cream pages on a chipboard back, a STACKHOUSE red-orange (#E8502A) binding band wrapped over
the top edge with a cream STACKHOUSE wordmark, five thin blue ruled lines, three dark
handwriting scrawls on the top lines, and a short yellow pencil tucked under the band along
the right side (ferrule + pink eraser poking out above the band). ~0.76 x 1.06 x 0.08.

Held like the Cosmetic_Spatula skins (blender/F_cosmetics): the game does
model:PivotTo(RightGripAttachment.WorldCFrame), so the PIVOT (0, 0, 0) is the grip point and
the model axes are the attachment's (see L_decor/_common.py, "Hand props"):
  * grip point = bottom-centre of the page block, 0.06 above the pad's bottom edge, at
    mid-thickness - the bottom of the pad sits in the fist;
  * the pad extends along Blender +Z = Roblox +Y = the hand's front (thumb side): it stands up
    out of the fist with the arm held forward, and points forward with the arm down;
  * the writing face looks back up the forearm, toward the player (Blender +Y = Roblox +Z),
    turned about the grip 45 deg toward the body's midline (Blender +X = Roblox -X) and tipped
    15 deg toward the hand's front (C.HOLD_YAW / HOLD_TILT), so it faces the player's eyes:
    within 22 / 6 / 28 deg with the arm down / held forward / elbow bent on the 0.8-scale R15
    (28 / 50 / 73 deg square to the hand). The attachment's LookVector side is the back.
Built facing -Y (readable from the front) and turned onto the grip by C.to_grip(), so the
wordmark reads correctly for the player holding it. NS_HOLD=1 renders it in hand on the R15
reference rig (previews/L_decor/_checks/Prop_Notepad_hold.png).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
bmesh = C.bmesh
Vector = C.Vector

# front frame (built facing -Y, up +Z); C.to_grip() turns it onto the grip at the end
PW, PH = 0.66, 1.0             # page block width, pad (board) height
BOARD_W = 0.68
BOARD_Y = (0.018, 0.04)        # chipboard back
PAGE_Y = (-0.034, 0.018)       # page block; the top page's face is at y = -0.034
BAND_X = (-0.345, 0.415)       # band also covers the pencil (tucked under it)
BAND_Y = (-0.042, 0.042)
BAND_Z = (0.845, 1.005)
PX, PR = 0.38, 0.034           # pencil axis x (right side), radius (hex)
LINES_Z = (0.30, 0.41, 0.52, 0.63, 0.74)
GRIP = (0.0, 0.0, 0.06)        # bottom-centre of the page block, mid-thickness

BOARD = "#8B7D6B"
RULE = "#7FA2CC"               # ruled-line blue
INK = "#2E3240"
WOOD = "#E8CFA4"
GRAPHITE = "#2B2D31"
ERASER = "#F28CA0"
LETTER = "#F6EEDC"


def ribbon(pts, w, y, name="Ribbon"):
    """Single-sided ribbon of width w through 2D points (x, z) at depth y, facing -Y
    (mitred joints, clamped), for pencil handwriting."""
    P = [Vector(p) for p in pts]
    n = len(P)
    sides = []
    for i in range(n):
        d0 = (P[max(i, 1)] - P[max(i, 1) - 1]).normalized()
        d1 = (P[min(i + 1, n - 1)] - P[min(i + 1, n - 1) - 1]).normalized()
        n0, n1 = Vector((-d0.y, d0.x)), Vector((-d1.y, d1.x))
        m = n0 + n1
        m = m.normalized() if m.length > 1e-6 else n0
        k = (w / 2) / max(0.4, m.dot(n0))
        sides.append((P[i] + m * k, P[i] - m * k))
    bm = bmesh.new()
    a = [bm.verts.new((p.x, y, p.y)) for p, _ in sides]
    b = [bm.verts.new((q.x, y, q.y)) for _, q in sides]
    for i in range(n - 1):
        bm.faces.new([b[i], b[i + 1], a[i + 1], a[i]])
    return C.face_dir(ns.from_bmesh(bm, name), "-Y")


def scrawl(x0, words, z, rnd, h=0.036, y=None, step=(0.03, 0.038)):
    """Pencil handwriting on a ruled line: one word per entry of `words` (= its up-strokes),
    quick up/down strokes, small gaps between words."""
    out = []
    x = x0
    for n_up in words:
        pts = []
        for k in range(n_up * 2 + 1):
            if k % 2:     # up-stroke: varied height, the odd tall ascender, slanted forward
                pts.append((x + 0.007, z + h * (1.3 if rnd.random() < 0.2 else rnd.uniform(0.45, 1.0))))
            else:
                pts.append((x, z + rnd.uniform(-0.004, 0.004)))
            x += rnd.uniform(*step) / 2
        out.append(ribbon(pts, 0.014, y))
        x += rnd.uniform(0.04, 0.055)
    return out


def build():
    rnd = random.Random(7)
    # pad: chipboard back + cream page block (crisp paper edges, no bevel)
    board = ns.box((BOARD_W, BOARD_Y[1] - BOARD_Y[0], PH), loc=(0, sum(BOARD_Y) / 2, PH / 2), bevel=0.0)
    pages = ns.box((PW, PAGE_Y[1] - PAGE_Y[0], 0.973), loc=(0, sum(PAGE_Y) / 2, 0.012 + 0.973 / 2), bevel=0.0)
    C.part(board, "Back", BOARD, smooth_angle=None)
    C.part(pages, "Pages", C.CREAM, smooth_angle=None)

    # binding band wrapped over the top edge (and over the tucked pencil), cream wordmark
    band = ns.box((BAND_X[1] - BAND_X[0], BAND_Y[1] - BAND_Y[0], BAND_Z[1] - BAND_Z[0]),
                  loc=(sum(BAND_X) / 2, 0, sum(BAND_Z) / 2), bevel=0.008, segments=1)
    C.part(band, "Band", C.BRAND, smooth_angle=30)
    word = C.text("STACKHOUSE", 0.07, 0.003, (0.02, BAND_Y[0] - 0.0005, sum(BAND_Z) / 2), width=0.53, res=1,
                  spacing=1.05, flat=True)
    C.part(word, "Wordmark", LETTER, smooth_angle=None)

    # five thin blue ruled lines, three lines of pencil handwriting on the top ones
    fy = PAGE_Y[0] - 0.0015
    lines = [C.quad_xz(-PW / 2 + 0.035, PW / 2 - 0.035, z - 0.0055, z + 0.0055, fy) for z in LINES_Z]
    C.part(lines, "Rules", RULE, smooth_angle=None)
    ink = []
    for z, words in ((LINES_Z[4], (4, 3)), (LINES_Z[3], (5,)), (LINES_Z[2], (3, 3))):
        ink += scrawl(-PW / 2 + 0.05, words, z + 0.008, rnd, y=fy - 0.0015)
    C.part(ink, "Writing", INK, smooth_angle=None)

    # short yellow pencil tucked under the band along the right side, point down: open lofted
    # tubes (the joints and both ends hide inside each other / the band, so no hidden caps)
    def ring(r, z, n=6):
        return [(PX + r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), z) for k in range(n)]

    z_tip, z_wood, z_body, z_ferr, z_top, z_end = 0.34, 0.37, 0.45, 0.99, 1.03, 1.065
    C.part(C.loft([ring(0.0, z_tip), ring(0.012, z_wood)], False, False), "PencilLead", GRAPHITE,
           smooth_angle=None)
    C.part(C.loft([ring(0.012, z_wood), ring(PR, z_body)], False, False), "PencilWood", WOOD, smooth_angle=None)
    C.part(C.loft([ring(PR, z_body), ring(PR, z_ferr)], False, False), "PencilBody", C.MUSTARD, smooth_angle=None)
    C.part(C.loft([ring(PR * 1.08, z_ferr, 8), ring(PR * 1.08, z_top, 8)], False, False), "Ferrule", C.CHROME,
           "Metal", smooth_angle=50)
    C.part(C.loft([ring(PR, z_top, 8), ring(PR, z_end, 8)], False, True), "Eraser", ERASER, smooth_angle=50)

    C.to_grip(GRIP)


META = {"attach": "RightGripAttachment",
        "grip": "pivot = grip point: bottom-centre of the pad 0.06 above its bottom edge, mid-thickness "
                "(model:PivotTo(RightGripAttachment.WorldCFrame), as Cosmetic_Spatula)",
        "face": "writing face looks back up the forearm toward the player (Roblox model axes: +Z), turned 45 deg toward the "
                "body midline (model -X) and tipped 15 deg toward the hand's front (model +Y); the pad "
                "extends along model +Y (the hand's front / thumb side) from the grip"}
VIEWS = ((155, 16, False), (110, 8, True))      # the face looks toward +X+Y (yaw 135)

if __name__ == "__main__":
    C.run(build, "Prop_Notepad", views=VIEWS, pivot=(0.0, 0.0, 0.0), budget=400, meta=META)
