"""Shop_MenuBoard — wall-mounted backlit diner menu board.

Brand red-orange header with modelled mustard "MENU" letters, a row of marquee bulbs (Neon, role
"neon"), a chrome-framed lightbox and one big blank backlit-cream Panel (role sign_panel, front face)
that Studio fills with a SurfaceGui menu. 9 wide x 5.4 tall.
Wall-mounted: pivot = bottom-centre of the back face (+Y, touches the wall).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W = 9.0
PH = 3.6               # panel height
HH = 1.25              # header height
D = 0.45               # box depth
Z0 = 0.0


def build():
    zc_p = Z0 + 0.2 + PH / 2
    zc_h = Z0 + 0.2 + PH + 0.12 + HH / 2
    total_h = PH + HH + 0.52
    # lightbox body (dark) + chrome frame
    body = C.prism(C.rrect(W, total_h, 0.25, 3, 0, Z0 + total_h / 2), "y", -D, 0.0)
    ns.bevel(body, width=0.04, segments=1)
    ns.tag(body, "Body", "#1A1E28", smooth_angle=40)
    fr = []
    # frame ring around the panel and around the header (front face)
    for zc, h in ((zc_p, PH), (zc_h, HH)):
        outer = C.rrect(W - 0.1, h + 0.3, 0.12, 2, 0, zc)
        o = C.prism(outer, "y", -D - 0.1, -D + 0.02)
        ns.boolean(o, ns.box((W - 0.5, 1, h), loc=(0, -D, zc), bevel=0.0))
        ns.bevel(o, width=0.03, segments=1)
        fr.append(o)
    C.part(fr, "Frame", C.CHROME, "Metal", smooth_angle=40)

    panel = ns.box((W - 0.5, 0.04, PH), loc=(0, -D - 0.02, zc_p), bevel=0.0)
    ns.tag(panel, "Panel", "#EFE3C4", recolor="sign_panel")

    header = ns.box((W - 0.5, 0.05, HH), loc=(0, -D - 0.025, zc_h), bevel=0.0)
    ns.tag(header, "Header", C.BRAND)
    letters = C.text_mesh("MENU", 1.0, 0.12, font=C.FONT_BOLD, resolution=2, spacing=1.2, loc=(0, -D - 0.11, zc_h))
    C.fit_text_width(letters, 3.4)
    ns.tag(letters, "Letters", C.MUSTARD, smooth_angle=30)
    # marquee bulbs along the top edge
    bulbs = []
    n = 13
    for i in range(n):
        x = -W / 2 + 0.45 + (W - 0.9) * i / (n - 1)
        bulbs.append(ns.sphere(0.1, loc=(x, -D - 0.09, Z0 + total_h - 0.12), segs=8, rings=5))
    ns.tag(C.merge(bulbs, "Bulbs"), "Bulbs", "#FFE7A8", "Neon", recolor="neon", cast_shadow=False, smooth_angle=80)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)",
        "surfaces": [{"part": "Panel", "face": "Front"}], "panel_size": [W - 0.5, PH]}

if __name__ == "__main__":
    C.run(build, "Shop_MenuBoard", pivot=(0, 0, 0), meta=META)
