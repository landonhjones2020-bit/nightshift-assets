"""Lobby_LeaderboardBoard — freestanding big leaderboard (13.4 wide x 14 tall).

A navy cabinet holding one 10 x 7 screen (Screen, role "screen", Front face) in a chrome
bezel, carried between two navy steel posts on concrete footings. On top, a red-orange
header cap with a mustard trim band and a dark title panel (TitlePanel, role "title",
Front face: code writes "Nights Survived" / "Secrets Discovered" / "Perfect Runs"), gold
trophies on both ends, and three gooseneck spot lamps leaning over the screen (Lenses,
Neon, role "lamp"). The back carries a red-orange belt stripe.

Front = -Y, pivot = bottom-centre. Sockets: Screen (screen face centre), Title (title panel
face centre), Lamp1..Lamp3 (lens centres; aim SpotLights at the screen).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
SCR_W, SCR_H = 10.0, 7.0
SCR_Z = 6.6                     # screen centre height (bottom 3.1)
CW, CH, CD = 10.86, 7.9, 0.7    # cabinet
PX = 5.8                        # post centre x
HDR_Z = (10.65, 12.45)
TTL_W, TTL_H = 8.2, 1.1
FY = -CD / 2                    # cabinet front plane
LAMP_X = (-3.4, 0.0, 3.4)


def lamp_geo(x):
    """Gooseneck arm from the header top + shade + lens, aimed at the screen centre."""
    base = Vector((x, 0.05, HDR_Z[1]))
    head = Vector((x, -1.75, 13.35))
    arm = C.pipe([tuple(base), (x, 0.0, 13.25), (x, -0.9, 13.6), tuple(head)], 0.07, sides=6, corner=0.35,
                 corner_segs=2)
    target = Vector((x * 0.6, FY, SCR_Z + 1.2))
    d = (target - head).normalized()
    shade = C.rod(head - d * 0.15, head + d * 0.7, 0.2, verts=10, r_top=0.48)
    lens_c = head + d * 0.71
    lens = C.rod(lens_c - d * 0.03, lens_c + d * 0.03, 0.42, verts=10)
    return arm, shade, lens, lens_c


def trophy(x, z, k=1.35):
    cup = ns.lathe([(0.0, 0.0), (0.34 * k, 0.0), (0.34 * k, 0.12 * k), (0.12 * k, 0.18 * k), (0.09 * k, 0.42 * k),
                    (0.36 * k, 0.55 * k), (0.44 * k, 1.0 * k), (0.0, 1.0 * k)], verts=10, loc=(x, 0, z))
    out = [cup]
    for sx in (-1, 1):
        h = ns.torus(0.17 * k, 0.05 * k, major_segs=8, minor_segs=3)
        C.place(h, (x + sx * 0.44 * k, 0, z + 0.72 * k), pitch=90)
        out.append(h)
    out.append(C.prism(C.rrect(0.85, 0.85, 0.08, 1), "z", z - 0.18, z + 0.0))
    out[-1].location = (x, 0, 0)
    return out


def build():
    # posts + footings
    posts, foot = [], []
    for sx in (-1, 1):
        posts.append(ns.box((0.7, 0.7, HDR_Z[0] + 0.05), loc=(sx * PX, 0, (HDR_Z[0] + 0.05) / 2), bevel=0.08, segments=1))
        foot.append(ns.box((1.2, 1.3, 0.45), loc=(sx * PX, 0, 0.225), bevel=0.07, segments=1))
    zc = SCR_Z
    cab = C.prism(C.rrect(CW, CH, 0.35, 3, 0, zc), "y", FY, -FY)
    ns.bevel(cab, width=0.06, segments=1)
    C.part(posts + [cab], "Frame", C.NAVY, "Metal", can_collide=True, smooth_angle=40)
    C.part(foot, "Footings", C.CONCRETE, "Concrete", can_collide=True, smooth_angle=40)

    bezel = C.ring_slab(C.rrect(SCR_W + 0.36, SCR_H + 0.36, 0.25, 2, 0, zc), C.rrect(SCR_W, SCR_H, 0.1, 2, 0, zc), "y",
                        FY - 0.1, FY + 0.04)
    scr = C.prism(C.rrect(SCR_W, SCR_H, 0.1, 2, 0, zc), "y", FY - 0.05, FY + 0.03)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)

    # header cap
    hz = sum(HDR_Z) / 2
    hdr = C.prism(C.rrect(2 * PX + 0.9, HDR_Z[1] - HDR_Z[0], 0.45, 3, 0, hz), "y", FY - 0.15, -FY + 0.1)
    ns.bevel(hdr, width=0.06, segments=1)
    C.part([hdr], "Header", C.BRAND, smooth_angle=40)
    band = ns.box((2 * PX + 0.4, CD + 0.36, 0.2), loc=(0, 0.0, HDR_Z[0] - 0.02), bevel=0.04, segments=1)
    ttl_ring = C.ring_slab(C.rrect(TTL_W + 0.24, TTL_H + 0.24, 0.2, 1, 0, hz), C.rrect(TTL_W, TTL_H, 0.12, 1, 0, hz), "y",
                           FY - 0.24, FY - 0.1)
    ttl = C.prism(C.rrect(TTL_W, TTL_H, 0.12, 1, 0, hz), "y", FY - 0.2, FY - 0.12)
    ns.tag(ttl, "TitlePanel", C.NAVY_DEEP, recolor="title", cast_shadow=False, smooth_angle=30)
    # back: red-orange belt + mustard pinstripe on the cabinet back
    back = [ns.box((CW - 0.6, 0.05, 0.5), loc=(0, -FY + 0.02, 8.4), bevel=0.0)]
    back_pin = [ns.box((CW - 0.6, 0.05, 0.12), loc=(0, -FY + 0.02, 8.86), bevel=0.0)]
    C.part(back, "BackBelt", C.BRAND, smooth_angle=30)

    # trophies + lamps
    gold = []
    for sx in (-1, 1):
        gold += trophy(sx * (PX - 0.15), HDR_Z[1] + 0.18)
    C.part(gold, "Trophies", C.GOLD, "Metal", smooth_angle=45)
    arms, shades, lenses = [], [], []
    for x in LAMP_X:
        a, s, l, _ = lamp_geo(x)
        arms.append(a)
        shades.append(s)
        lenses.append(l)
    C.part([band, ttl_ring] + back_pin, "Trim", C.MUSTARD, smooth_angle=40)
    C.part([bezel] + arms, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    C.part(shades, "Shades", C.CHARCOAL, "Metal", smooth_angle=45)
    ns.tag(C.merge(lenses, "Lenses"), "Lenses", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=50)


def sockets():
    s = {"Screen": ((0, FY - 0.05, SCR_Z), 0.0), "Title": ((0, FY - 0.2, sum(HDR_Z) / 2), 0.0)}
    for i, x in enumerate(LAMP_X):
        s[f"Lamp{i + 1}"] = (tuple(lamp_geo_point(x)), 0.0)
    return s


def lamp_geo_point(x):
    head = Vector((x, -1.75, 13.35))
    target = Vector((x * 0.6, FY, SCR_Z + 1.2))
    return head + (target - head).normalized() * 0.71


META = {"screen_size": [SCR_W, SCR_H], "title_size": [TTL_W, TTL_H],
        "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H), C.screen_meta("TitlePanel", TTL_W, TTL_H)],
        "boards": ["Nights Survived", "Secrets Discovered", "Perfect Runs"],
        "roles": {"screen": "Screen", "title": "TitlePanel", "lamp": "Lenses"},
        "light_hint": {"type": "SpotLight", "at": "Socket_Lamp1..3", "aim": "Socket_Screen", "color": "#FFE2B0",
                       "range": 16, "angle": 70, "brightness": 1.5}}

if __name__ == "__main__":
    C.run(build, "Lobby_LeaderboardBoard", sockets=sockets(), meta=META)
