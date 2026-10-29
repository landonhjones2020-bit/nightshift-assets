"""Shop_OpenSign — small hanging "OPEN" neon window sign.

Red-pink neon letters inside a cyan oval tube, mounted on a slim black rod frame that
hangs from two chains (top hook = socket Hang). Lit parts have role "neon"
(Letters, Oval) so the sign can flicker or switch to "CLOSED" logic in code.
Pivot = bottom-centre; hang it in a window with Socket_Hang at the window head.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H = 3.0, 1.5
ZC = 0.9
RED_NEON = "#FF3B4E"


def build():
    letters = C.text_mesh("OPEN", 0.95, 0.1, font=C.FONT_BOLD_ITALIC, resolution=2, spacing=1.08, loc=(0, -0.02, ZC))
    C.fit_text_width(letters, 2.0)
    ns.tag(letters, "Letters", RED_NEON, "Neon", recolor="neon", cast_shadow=False, smooth_angle=30)
    oval = C.pipe([(x, -0.02, z) for x, z in C.ellipse_pts(1.38, 0.66, 28, 0, ZC)], 0.05, sides=6, closed=True)
    ns.tag(oval, "Oval", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # black rod frame behind the tubes + tube clips + transformer box
    frame = []
    for z in (ZC - 0.45, ZC + 0.45):
        frame.append(C.pipe([(-1.45, 0.08, z), (1.45, 0.08, z)], 0.035, sides=6))
    for x in (-1.45, 1.45):
        frame.append(C.pipe([(x, 0.08, ZC - 0.5), (x, 0.08, ZC + 0.5)], 0.035, sides=6))
    for x in (-0.95, 0.0, 0.95):
        frame.append(ns.box((0.08, 0.14, 0.12), loc=(x, 0.03, ZC - 0.45), bevel=0.02, segments=1))
    frame.append(ns.box((0.7, 0.2, 0.22), loc=(0, 0.12, ZC - 0.62), bevel=0.04, segments=1))
    C.part(frame, "Frame", "#18191D", smooth_angle=60)

    # hanging wires up to the top bar (with crimp beads)
    links = []
    for sx in (-1, 1):
        links.append(C.pipe([(sx * 1.25, 0.08, ZC + 0.47), (sx * 1.25, 0.08, ZC + 1.6)], 0.022, sides=5))
        for z in (ZC + 0.55, ZC + 1.52):
            links.append(ns.cyl(0.05, 0.1, loc=(sx * 1.25, 0.08, z), verts=6, bevel=0.0))
    links.append(C.pipe([(-1.4, 0.08, ZC + 1.6), (1.4, 0.08, ZC + 1.6)], 0.035, sides=6))
    C.part(links, "Wire", C.CHROME, "Metal", smooth_angle=60)


META = {"size": [3.0, 2.6, 0.3], "neon_parts": ["Letters", "Oval"], "hang": "Socket_Hang (top bar)",
        "light_hint": {"color": RED_NEON, "range": 8, "brightness": 1.5}}

if __name__ == "__main__":
    C.run(build, "Shop_OpenSign", meta=META, sockets={"Hang": ((0, 0.08, ZC + 1.63), 0.0)})
