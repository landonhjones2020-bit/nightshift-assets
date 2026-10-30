"""Prop_OrderSlip — the order ticket the player carries after writing it (RIGHT HAND).

Cream paper (0.55 x 0.9 x 0.02) with a torn zig-zag bottom edge, a STACKHOUSE red-orange
header band across the top (printed through the paper, so it shows from behind too) with a
cream ORDER mark, four printed blue lines and three pencil scrawls on the top lines.

Held like the Cosmetic_Spatula skins (blender/F_cosmetics): the game does
model:PivotTo(RightGripAttachment.WorldCFrame), so the PIVOT (0, 0, 0) is the grip point and
the model axes are the attachment's (see L_decor/_common.py, "Hand props"):
  * grip point = the middle of the bottom (torn) edge, at the zig-zag's mid-line, mid-thickness;
  * the slip extends along Blender +Z = Roblox +Y = the hand's front (thumb side): it stands up
    out of the fist with the arm held forward, and points forward with the arm down;
  * the printed face looks back up the forearm, toward the player, turned 45 deg toward the
    body's midline and tipped 15 deg toward the hand's front about the grip - the same turn
    as Prop_Notepad (C.HOLD_YAW / HOLD_TILT), so it faces the player's eyes.
NS_HOLD=1 renders it in hand on the R15 reference rig (previews/L_decor/_checks/).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import Prop_Notepad as NP  # noqa: E402  (ribbon / scrawl handwriting + shared colours)

ns = C.ns

# front frame (built facing -Y, up +Z); C.to_grip() turns it onto the grip at the end
W, H, T = 0.55, 0.9, 0.02
HEAD_Z = 0.745                 # header band: HEAD_Z .. H
TEETH, TOOTH = 8, 0.04         # torn zig-zag bottom: 8 teeth, 0.04 deep
LINES_Z = (0.32, 0.43, 0.54, 0.65)
GRIP = (0.0, 0.0, TOOTH / 2)   # middle of the torn bottom edge, mid-thickness


def torn_outline(rnd):
    """Body outline (x, z): right side, zig-zag bottom (right to left), left side."""
    pts = [(W / 2, HEAD_Z)]
    n = TEETH * 2
    for k in range(n + 1):
        x = W / 2 - W * k / n
        notch = k % 2 == 0
        z = TOOTH + rnd.uniform(-0.008, 0.006) if notch else rnd.uniform(0.0, 0.012)
        if 0 < k < n:
            x += rnd.uniform(-0.006, 0.006)
        pts.append((x, z))
    pts.append((-W / 2, HEAD_Z))
    return pts


def build():
    rnd = random.Random(11)
    body = C.prism(torn_outline(rnd), "y", -T / 2, T / 2)
    C.part(body, "Paper", C.CREAM, smooth_angle=None)
    head = C.prism([(-W / 2, HEAD_Z), (W / 2, HEAD_Z), (W / 2, H), (-W / 2, H)], "y", -T / 2, T / 2)
    C.part(head, "Header", C.BRAND, smooth_angle=None)
    mark = C.text("ORDER", 0.075, 0.002, (0.0, -T / 2 - 0.0005, (HEAD_Z + H) / 2), width=0.25, res=1, spacing=1.1,
                  flat=True)
    C.part(mark, "HeaderPrint", NP.LETTER, smooth_angle=None)

    fy = -T / 2 - 0.0015
    lines = [C.quad_xz(-W / 2 + 0.04, W / 2 - 0.04, z - 0.005, z + 0.005, fy) for z in LINES_Z]
    C.part(lines, "Rules", NP.RULE, smooth_angle=None)
    ink = []
    for z, words in ((LINES_Z[3], (3, 3)), (LINES_Z[2], (4,)), (LINES_Z[1], (2, 3))):
        ink += NP.scrawl(-W / 2 + 0.05, words, z + 0.007, rnd, h=0.032, y=fy - 0.0015)
    C.part(ink, "Writing", NP.INK, smooth_angle=None)

    C.to_grip(GRIP)


META = {"attach": "RightGripAttachment",
        "grip": "pivot = grip point: middle of the torn bottom edge, mid-thickness "
                "(model:PivotTo(RightGripAttachment.WorldCFrame), as Cosmetic_Spatula)",
        "face": "printed face looks back up the forearm toward the player (Roblox model axes: +Z), turned 45 deg toward the "
                "body midline (model -X) and tipped 15 deg toward the hand's front (model +Y); the slip "
                "extends along model +Y (the hand's front / thumb side) from the grip"}
VIEWS = ((155, 16, False), (110, 8, True))      # the face looks toward +X+Y (yaw 135)

if __name__ == "__main__":
    C.run(build, "Prop_OrderSlip", views=VIEWS, pivot=(0.0, 0.0, 0.0), budget=250, meta=META)
