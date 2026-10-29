"""Shop_RulesBoard — the handwritten rules sheet on a big clipboard hung from a nail.

Hardboard clipboard with a chunky chrome clip, a blank Sheet (role sign_panel: the rules
text is a SurfaceGui in Permanent Marker), two older dog-eared sheets peeking out
underneath, and a pencil on a string. 2.8 x 3.9.
Wall-mounted: pivot = bottom-centre of the back face (+Y, touches the wall).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
BW, BH, BT = 2.8, 3.9, 0.1
HARDBOARD = "#8B5E3C"


def build():
    zc = BH / 2
    board = C.prism(C.rrect(BW, BH, 0.22, 3, 0, zc), "y", -BT, 0.0)
    ns.bevel(board, width=0.025, segments=1)
    ns.tag(board, "Board", HARDBOARD, "Wood", smooth_angle=40)
    # older sheets underneath, slightly rotated and offset
    old = []
    for ang, dx, dz in ((-4.0, -0.08, -0.12), (3.0, 0.1, -0.06)):
        s = ns.box((2.4, 0.012, 3.1), loc=(dx, -BT - 0.008, zc - 0.22 + dz), rot=(0, ang, 0), bevel=0.0)
        old.append(s)
    C.part(old, "OldSheets", "#E3D9C0")
    sheet = ns.box((2.4, 0.012, 3.15), loc=(0, -BT - 0.022, zc - 0.2), bevel=0.0)
    ns.tag(sheet, "Sheet", C.PAPER, recolor="sign_panel")
    # chrome clip
    clip = [ns.box((1.3, 0.1, 0.42), loc=(0, -BT - 0.06, BH - 0.36), bevel=0.05, segments=2),
            C.pipe([(-0.45, -BT - 0.12, BH - 0.2), (-0.45, -BT - 0.22, BH - 0.05), (0.45, -BT - 0.22, BH - 0.05),
                    (0.45, -BT - 0.12, BH - 0.2)], 0.04, sides=6, corner=0.06, corner_segs=2),
            ns.cyl(0.07, 0.6, loc=(0, -BT - 0.12, BH - 0.12), rot=(0, 90, 0), verts=8, bevel=0.0)]
    # nail head the board hangs on
    clip.append(ns.cyl(0.08, 0.08, loc=(0, -BT - 0.02, BH - 0.05), rot=(90, 0, 0), verts=8, bevel=0.0))
    C.part(clip, "Clip", C.CHROME, "Metal", smooth_angle=50)
    # pencil on a string, hanging at the right edge
    px = BW / 2 + 0.12
    pencil = ns.cyl(0.045, 0.85, loc=(px, -BT - 0.05, 1.05), verts=6, bevel=0.0)
    tip = ns.cyl(0.045, 0.14, loc=(px, -BT - 0.05, 0.56), verts=6, radius_top=0.0, bevel=0.0)
    tip.rotation_euler = (3.14159, 0, 0)
    ns.tag(C.merge([pencil], "Pencil"), "Pencil", C.MUSTARD, smooth_angle=20)
    ns.tag(C.merge([tip], "PencilTip"), "PencilTip", "#E8CFA4", smooth_angle=20)
    string = C.pipe([(BW / 2 - 0.25, -BT - 0.03, BH - 0.4), (px + 0.05, -BT - 0.06, BH - 1.4), (px, -BT - 0.05, 1.48)],
                    0.014, sides=4)
    ns.tag(string, "String", "#D8D2C4", smooth_angle=60)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)",
        "surfaces": [{"part": "Sheet", "face": "Front"}], "sheet_size": [2.4, 3.15], "font_hint": "PermanentMarker"}

if __name__ == "__main__":
    C.run(build, "Shop_RulesBoard", pivot=(0, 0, 0), meta=META, sockets={"Read": ((0, -2.5, 0), 180.0)})
