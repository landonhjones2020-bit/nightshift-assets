"""Prop_OrderSlip — a torn order-pad page / guest check, held in a player's RIGHT HAND.

Cream paper slip (0.9 x 1.25 x 0.03) with a torn zig-zag top edge, a red header band
(STACKHOUSE red-orange, matches Prop_Notepad) with little printed marks, printed ruled
lines, a red price-column rule, and a pencil scribble of handwriting marks (thin dark
strips) on four lines plus a circled total. Printing is on the front face (-Y).
PIVOT = GRIP POINT: the bottom-centre edge (the slip stands up out of the fist, face -Y).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 0.9, 1.25, 0.03
FY = -T / 2
LINE = "#A9B9C9"
PENCIL = "#3A3E48"


def build():
    rnd = random.Random(42)
    # outline with a torn top edge (right to left), extruded through the thickness
    top = []
    n = 13
    for k in range(n + 1):
        x = W / 2 - W * k / n + (rnd.uniform(-0.02, 0.02) if 0 < k < n else 0.0)
        z = H - rnd.choice((0.0, 0.015, 0.03, 0.05, 0.065)) - rnd.uniform(0.0, 0.015)
        top.append((x, z))
    outline = [(-W / 2, 0.0), (W / 2, 0.0)] + top
    slip = C.prism(outline, "y", FY, -FY)
    C.part([slip], "Paper", C.PAPER, smooth_angle=None)

    y1, y2 = FY - 0.004, FY - 0.008
    header = [C.quad_xz(-W / 2 + 0.05, W / 2 - 0.05, H - 0.27, H - 0.12, y1)]
    marks = [C.quad_xz(-0.34, 0.02, H - 0.21, H - 0.18, y2), C.quad_xz(0.12, 0.2, H - 0.225, H - 0.165, y2),
             C.quad_xz(0.26, 0.34, H - 0.225, H - 0.165, y2)]
    lines = [C.quad_xz(-W / 2 + 0.05, W / 2 - 0.05, z - 0.006, z + 0.006, y1) for z in (0.22, 0.36, 0.5, 0.64, 0.78)]
    rule = [C.quad_xz(0.2, 0.212, 0.12, H - 0.32, y1)]
    # handwriting: a few short slanted strokes per line (left of the price rule) + prices + total
    ink = []
    for z, n_strokes in ((0.43, 4), (0.57, 3), (0.71, 5), (0.29, 2)):
        x = -0.36
        for s in range(n_strokes):
            ln = rnd.uniform(0.06, 0.11)
            ink.append(C.strip_xz((x, z - 0.015), (x + ln, z + 0.02 + rnd.uniform(-0.01, 0.01)), 0.016, y2))
            x += ln + 0.03
        ink.append(C.strip_xz((0.26, z - 0.01), (0.36, z + 0.015), 0.016, y2))
    # circled total at the bottom right
    import math
    ring = []
    for k in range(8):
        a0, a1 = 2 * math.pi * k / 8, 2 * math.pi * (k + 1) / 8
        ring.append(C.strip_xz((0.3 + 0.08 * math.cos(a0), 0.13 + 0.05 * math.sin(a0)),
                               (0.3 + 0.08 * math.cos(a1), 0.13 + 0.05 * math.sin(a1)), 0.014, y2))
    C.part(header, "Header", C.BRAND, smooth_angle=None)
    C.part(marks, "HeaderPrint", "#F6EEDC", smooth_angle=None)
    C.part(lines, "Lines", LINE, smooth_angle=None)
    C.part(rule, "Rule", "#D9534A", smooth_angle=None)
    C.part(ink + ring, "Pencil", PENCIL, smooth_angle=None)


META = {"held": "RightHand", "pivot": "grip point = bottom-centre edge; slip stands up out of the fist, printed face -Y",
        "size": [W, H, T]}

if __name__ == "__main__":
    C.run(build, "Prop_OrderSlip", views=C.VIEWS_SMALL, pivot=(0, 0, 0), budget=300, meta=META)
