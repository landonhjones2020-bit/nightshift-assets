"""Prop_Notepad — a waitress's order notepad, held in a player's RIGHT HAND.

Grey-brown card back, a stack of cream pages, a chrome spiral binding along the top (six
wire loops over the top edge), a red STACKHOUSE header band (cream letters) on the top
page with ruled lines below, and a short yellow pencil clipped on the right side.
PIVOT = GRIP POINT: the middle of the LEFT edge as seen from the front (Blender -X /
Roblox +X), at mid thickness. Front (top page) faces -Y. ~1.0 x 1.4.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H = 1.0, 1.4
PAGE_FRONT = -0.03
BACK = (0.02, 0.05)


def build():
    back = ns.box((W, BACK[1] - BACK[0], H), loc=(0, (BACK[0] + BACK[1]) / 2, H / 2), bevel=0.0)
    pages = ns.box((W - 0.04, BACK[0] - PAGE_FRONT, H - 0.1), loc=(0, (PAGE_FRONT + BACK[0]) / 2, (H - 0.1) / 2), bevel=0.0)
    C.part([back], "Back", "#8B7D6B", smooth_angle=None)
    C.part([pages], "Pages", C.PAPER, smooth_angle=None)

    fy = PAGE_FRONT - 0.004
    zt = H - 0.1                 # page top
    header = C.quad_xz(-W / 2 + 0.06, W / 2 - 0.06, zt - 0.3, zt - 0.08, fy)
    letters = C.text("STACKHOUSE", 0.12, 0.01, (0, fy - 0.004 + 0.005, zt - 0.19), width=0.78, res=1, spacing=1.05,
                     flat=True)
    lines = [C.quad_xz(-W / 2 + 0.08, W / 2 - 0.08, z - 0.006, z + 0.006, fy) for z in (0.36, 0.62, 0.88)]
    C.part([header], "Header", C.BRAND, smooth_angle=None)
    C.part([letters], "HeaderText", "#F6EEDC", smooth_angle=None)
    C.part(lines, "Lines", "#A9B9C9", smooth_angle=None)

    # spiral binding: wire loops over the top edge (edge-on bars)
    loops = [ns.box((0.035, 0.13, 0.14), loc=(-0.38 + 0.152 * k, 0.0, zt + 0.03), bevel=0.0) for k in range(6)]
    C.part(loops, "Spiral", C.CHROME, "Metal", smooth_angle=None)

    # short pencil clipped on the right side (hex body + sharpened tip + clip)
    px = W / 2 + 0.06
    body = ns.cyl(0.045, 0.62, loc=(px, -0.01, 0.62), verts=6, bevel=0.0)
    tip = ns.cyl(0.045, 0.13, loc=(px, -0.01, 0.245), rot=(180, 0, 0), verts=6, radius_top=0.0, bevel=0.0)
    clip = ns.box((0.12, 0.1, 0.1), loc=(px - 0.04, 0.0, 0.8), bevel=0.0)
    C.part([body], "PencilBody", C.MUSTARD, smooth_angle=None)
    C.part([tip], "PencilTip", "#E8CFA4", smooth_angle=None)
    C.part([clip], "Clip", C.CHROME, "Metal", smooth_angle=None)


GRIP = (-W / 2, 0.0, H / 2)
META = {"held": "RightHand",
        "pivot": "grip point = middle of the left edge as seen from the front (Blender -X / Roblox +X), mid thickness",
        "front": "-Y (top page)"}

if __name__ == "__main__":
    C.run(build, "Prop_Notepad", views=C.VIEWS_SMALL, pivot=GRIP, budget=300, meta=META)
