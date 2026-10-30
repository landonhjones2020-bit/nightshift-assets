"""Lobby_BannerPole — tall decorative lamp pole with two STACKHOUSE banners (~3 x 22 x 1.1).

A stepped navy base, a tapered navy pole with mustard collars, two horizontal bracket arms each side
carrying vertical swallow-tail banners — red-orange on the left, mustard on the right as seen from the
front — each with a STACKHOUSE sandwich mark, and a lantern head on top (LanternGlass, Neon warm,
role "lamp").

Front = -Y, pivot = bottom-centre. Socket Light (just under the lantern head, for the light).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

POLE_TOP = 19.9
BAN = (0.3, 1.38, 10.9, 16.36)     # banner inner x, outer x, bottom, top (top sleeved on the arm)
ARM_Z = (16.35, 11.05)
LANT_Z0 = 20.1                     # lantern glass bottom
GLASS_H = 1.05


def banner(side):
    x0, x1, z0, z1 = BAN
    xs = sorted((side * x0, side * x1))
    xm = (xs[0] + xs[1]) / 2
    outline = [(xs[0], z1), (xs[0], z0), (xm, z0 + 0.55), (xs[1], z0), (xs[1], z1)]
    return C.prism(outline, "y", -0.03, 0.03)


def build():
    navy, mustard, chrome = [], [], []
    navy.append(ns.box((1.1, 1.1, 0.45), loc=(0, 0, 0.225), bevel=0.06, segments=1))
    navy.append(ns.box((0.78, 0.78, 0.55), loc=(0, 0, 0.72), bevel=0.06, segments=1))
    navy.append(C.rod((0, 0, 0.95), (0, 0, POLE_TOP), 0.21, verts=8, r_top=0.15))
    for z, r in ((1.35, 0.27), (9.6, 0.24), (POLE_TOP - 0.15, 0.22)):
        mustard.append(ns.cyl(r, 0.22, loc=(0, 0, z), verts=8, bevel=0.0))
    for z in ARM_Z:
        chrome.append(C.rod((-BAN[1] - 0.12, 0, z), (BAN[1] + 0.12, 0, z), 0.05, verts=4))
        for s in (-1, 1):
            chrome.append(ns.sphere(0.09, loc=(s * (BAN[1] + 0.14), 0, z), segs=4, rings=3))
    red_banner = banner(-1)
    gold_banner = banner(1)
    # sandwich marks on the banner fronts
    zc = (BAN[2] + BAN[3]) / 2 + 0.6
    logo_l = C.mini_logo((-(BAN[0] + BAN[1]) / 2, -0.029, zc), r=0.44, depth=0.05, disc=C.CREAM, n=10)
    logo_r = C.mini_logo(((BAN[0] + BAN[1]) / 2, -0.029, zc), r=0.44, depth=0.05, disc=C.NAVY, n=10)
    # lantern: base cup, glass, corner posts, pyramid roof, finial
    navy.append(C.rod((0, 0, POLE_TOP - 0.05), (0, 0, LANT_Z0 + 0.02), 0.2, verts=8, r_top=0.44))
    glass = ns.box((0.62, 0.62, GLASS_H), loc=(0, 0, LANT_Z0 + GLASS_H / 2), bevel=0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            navy.append(ns.box((0.1, 0.1, GLASS_H + 0.06), loc=(sx * 0.33, sy * 0.33, LANT_Z0 + GLASS_H / 2), bevel=0.0))
    roof = C.rod((0, 0, LANT_Z0 + GLASS_H), (0, 0, LANT_Z0 + GLASS_H + 0.62), 0.6, verts=4, r_top=0.05)
    roof.rotation_euler.z += math.radians(45)
    navy.append(roof)
    mustard.append(ns.sphere(0.12, loc=(0, 0, LANT_Z0 + GLASS_H + 0.7), segs=6, rings=3))

    C.part(navy, "Pole", C.STEEL_NAVY, "Metal", can_collide=True, smooth_angle=45)
    C.part(mustard + logo_r.pop(C.CHEESE, []), "Collars", C.MUSTARD, "Metal", smooth_angle=45)
    C.part(chrome, "Brackets", C.CHROME, "Metal", smooth_angle=45)
    C.part([red_banner], "BannerRed", C.BRAND, "Fabric", smooth_angle=None)
    C.part([gold_banner], "BannerGold", C.MUSTARD, "Fabric", smooth_angle=None)
    logos = {}
    C.merge_into(logos, logo_l)
    C.merge_into(logos, logo_r)
    names = {C.CREAM: "LogoDiscCream", C.NAVY: "LogoDiscNavy", C.BUN: "LogoBun", C.LETTUCE: "LogoLettuce"}
    for col, objs in logos.items():
        C.part(objs, names.get(col, "Logo" + col.lstrip("#")), col, smooth_angle=None)
    ns.tag(glass, "LanternGlass", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=30)


SOCKETS = {"Light": ((0.0, 0.0, LANT_Z0 - 0.15), 0.0)}
META = {"banners": "left red-orange, right mustard (as seen from the front), STACKHOUSE sandwich mark on the front",
        "roles": {"lamp": "LanternGlass"},
        "light_hint": {"type": "PointLight", "at": "Socket_Light", "color": C.LAMP_WARM, "range": 16, "brightness": 1}}

if __name__ == "__main__":
    C.run(build, "Lobby_BannerPole", sockets=SOCKETS, meta=META, budget=700)
