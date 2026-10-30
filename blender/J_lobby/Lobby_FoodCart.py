"""Lobby_FoodCart — STACKHOUSE snack cart (~7 wide x ~8 tall x ~4 deep).

Red-orange cart body with a cream front panel and a STACKHOUSE logo badge, cream counter top with a
chrome edge, two big spoked wheels at the left end and two legs at the right end, a chrome push
handle, a red-orange / cream striped umbrella with a scalloped edge on a chrome pole, a navy menu
panel on the pole ("MENU" + three item lines), a napkin box and ketchup / mustard squeeze bottles
on the counter.

Front = -Y, pivot = bottom-centre. Socket Prompt (in front of the counter, y 3). No runtime roles.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

BW, BD = 4.8, 2.4             # body width (x) and depth (y)
BZ0, BZ1 = 1.05, 3.0          # body bottom / top
TOP = 3.18                    # counter top surface
WHEEL_R = 0.95
WHEEL_X = -1.55
POLE = (0.55, 0.45)           # umbrella pole x, y
UMB_Z = 6.9                   # canopy rim height
UMB_R = 3.3


def bottle(x, y, z0, col, cap_col, h=0.95, r=0.22):
    body = ns.cyl(r, h, loc=(x, y, z0 + h / 2), verts=8, bevel=0.0)
    cap = ns.cyl(r * 0.85, 0.16, loc=(x, y, z0 + h + 0.08), verts=8, bevel=0.0)
    tip = C.rod((x, y, z0 + h + 0.15), (x, y, z0 + h + 0.48), r * 0.55, verts=6, r_top=0.03)
    return [body], [cap, tip]


def build():
    red, cream, chrome, dark, navy = [], [], [], [], []
    # body + panels
    body = ns.box((BW, BD, BZ1 - BZ0), loc=(0, 0, (BZ0 + BZ1) / 2), bevel=0.1, segments=1)
    red.append(body)
    cream.append(C.prism(C.rrect(BW - 0.7, BZ1 - BZ0 - 0.55, 0.15, 2, 0, (BZ0 + BZ1) / 2), "y", -BD / 2 - 0.05, -BD / 2 + 0.02))
    cream.append(C.prism(C.rrect(BW + 0.35, BD + 0.3, 0.15, 2), "z", BZ1 - 0.02, TOP))
    chrome.append(C.pipe([(-BW / 2 - 0.12, -BD / 2 - 0.2, TOP - 0.09), (BW / 2 + 0.12, -BD / 2 - 0.2, TOP - 0.09)], 0.07, sides=6))
    chrome.append(ns.box((BW + 0.04, BD + 0.04, 0.22), loc=(0, 0, BZ0 + 0.11), bevel=0.0))   # kick band
    badge = C.mini_logo((0.0, -BD / 2 - 0.049, (BZ0 + BZ1) / 2), r=0.66, disc=C.CREAM_SHADE)
    # wheels (front and back side at the left end), axle, legs + feet (right end), push handle
    for sy in (-1, 1):
        y = sy * (BD / 2 + 0.18)
        # tyre ring, hub and spokes (open wheel, so the spokes show)
        dark.append(C.ring_slab(C.circle_pts(WHEEL_R, 12, WHEEL_X, WHEEL_R), C.circle_pts(WHEEL_R - 0.24, 12, WHEEL_X, WHEEL_R),
                                "y", y - 0.11, y + 0.11))
        chrome.append(ns.cyl(0.2, 0.26, loc=(WHEEL_X, y, WHEEL_R), rot=(90, 0, 0), verts=6, bevel=0.0))
        for k in range(3):   # spokes
            a = math.radians(60 * k + 15)
            d = Vector((math.cos(a), 0, math.sin(a))) * (WHEEL_R - 0.2)
            c = Vector((WHEEL_X, y, WHEEL_R))
            chrome.append(C.rod(c - d, c + d, 0.04, verts=4))
        x = BW / 2 - 0.45
        chrome.append(C.rod((x, sy * (BD / 2 - 0.25), BZ0 + 0.05), (x, sy * (BD / 2 - 0.25), 0.18), 0.09, verts=6))
        dark.append(ns.cyl(0.2, 0.18, loc=(x, sy * (BD / 2 - 0.25), 0.09), verts=6, bevel=0.0))
    chrome.append(C.rod((WHEEL_X, -BD / 2 - 0.3, WHEEL_R), (WHEEL_X, BD / 2 + 0.3, WHEEL_R), 0.07, verts=6))
    chrome.append(C.pipe([(BW / 2 - 0.05, -0.9, TOP - 0.35), (BW / 2 + 0.75, -0.9, TOP - 0.1), (BW / 2 + 0.75, 0.9, TOP - 0.1),
                          (BW / 2 - 0.05, 0.9, TOP - 0.35)], 0.07, sides=4, corner=0.18, corner_segs=2))
    # umbrella: pole, 8 striped panels with scalloped tabs, finial
    px, py = POLE
    chrome.append(C.rod((px, py, TOP), (px, py, UMB_Z + 1.05), 0.08, verts=6))
    panels = {C.BRAND: [], C.PAPER: []}
    n = 8
    apex = Vector((px, py, UMB_Z + 1.0))
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = Vector((px + UMB_R * math.cos(a0), py + UMB_R * math.sin(a0), UMB_Z))
        p1 = Vector((px + UMB_R * math.cos(a1), py + UMB_R * math.sin(a1), UMB_Z))
        mid = (p0 + p1) / 2
        # slightly domed panel: apex, rim corners, and a bulged mid point between them
        bulge = apex.lerp(mid, 0.55) + Vector((0, 0, 0.18))
        col = C.BRAND if i % 2 == 0 else C.PAPER
        panels[col].append(C.flat_poly_3d([apex, p0, bulge], up=True))
        panels[col].append(C.flat_poly_3d([bulge, p0, p1], up=True))
        panels[col].append(C.flat_poly_3d([apex, bulge, p1], up=True))
        # under side (seen from below)
        panels[col].append(C.flat_poly_3d([apex, p1, p0], up=False))
        # scalloped tab hanging from the rim
        tab = []
        for k in range(5):
            t = k / 4
            q = p0.lerp(p1, t)
            tab.append(q - Vector((0, 0, 0.32 * math.sin(math.pi * t) + 0.02)))
        out_dir = Vector((mid.x - px, mid.y - py, 0))
        panels[col].append(C.flat_poly_3d([p0] + tab[1:-1] + [p1], up=None, facing_out=out_dir))
        panels[col].append(C.flat_poly_3d([p0] + tab[1:-1] + [p1], up=None, facing_out=-out_dir))
    finial = ns.sphere(0.16, loc=(px, py, UMB_Z + 1.12), segs=6, rings=3)
    # menu panel on the pole, facing front
    mz = 4.85
    navy.append(ns.box((1.7, 0.1, 1.45), loc=(px, py - 0.13, mz), bevel=0.04, segments=1))
    mw = C.Word("MENU", px, cap=0.26, spacing=1.12, base=mz + 0.36)
    menu_txt = mw.solid(py - 0.21, 0.03, front_only=True, name="MenuText")
    lines = [ns.box((1.15 - 0.15 * k, 0.03, 0.07), loc=(px - 0.075 * k, py - 0.205, mz + 0.08 - 0.25 * k), bevel=0.0) for k in range(3)]
    chrome.append(C.ring_slab(C.rrect(1.84, 1.59, 0.1, 1, px, mz), C.rrect(1.66, 1.41, 0.06, 1, px, mz), "y", py - 0.22, py - 0.09))
    # napkin box + napkins, bottles
    chrome.append(ns.box((0.7, 0.45, 0.42), loc=(1.45, -0.55, TOP + 0.21), bevel=0.05, segments=1))
    napkins = [ns.box((0.5, 0.3, 0.18), loc=(1.45, -0.55, TOP + 0.48), rot=(0, 0, 4), bevel=0.04, segments=1)]
    kb, kc = bottle(-1.25, -0.6, TOP, C.KETCHUP, C.KETCHUP)
    mb, mc = bottle(-0.72, -0.5, TOP, C.MUSTARD_SAUCE, C.MUSTARD_SAUCE)

    C.part(red, "CartBody", C.BRAND, can_collide=True, smooth_angle=40)
    C.part(cream + [menu_txt] + lines + napkins, "Cream", C.CREAM, smooth_angle=40)
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    C.part(dark, "Rubber", C.RUBBER, "Plastic", smooth_angle=40)
    C.part(navy, "MenuBoard", C.NAVY, smooth_angle=40)
    C.part(panels[C.BRAND], "UmbrellaRed", C.BRAND, "Fabric", smooth_angle=None)
    C.part(panels[C.PAPER], "UmbrellaCream", C.PAPER, "Fabric", smooth_angle=None)
    C.part([finial], "Finial", C.MUSTARD, smooth_angle=60)
    C.part(kb + kc, "Ketchup", C.KETCHUP, smooth_angle=45)
    C.part(mb + mc, "Mustard", C.MUSTARD_SAUCE, smooth_angle=45)
    C.add_parts(badge, "Badge", smooth_angle=40)


SOCKETS = {"Prompt": ((0.0, -BD / 2 - 1.6, 3.0), 0.0)}
META = {"counter_height": TOP, "menu": "modelled MENU panel on the umbrella pole (not a screen)"}

if __name__ == "__main__":
    # pivot = bottom-centre of the cart body (the umbrella overhangs to one side)
    C.run(build, "Lobby_FoodCart", sockets=SOCKETS, meta=META, budget=1500, pivot=(0.0, 0.0, 0.0))
