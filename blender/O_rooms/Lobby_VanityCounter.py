"""Lobby_VanityCounter — locker-room vanity (10 W x 8 H x 2.4 D) with a Hollywood bulb mirror.

A cream cabinet on a black toe-kick with mustard doors and drawers (chrome bar pulls): a double
door under each sink and a three-drawer stack between them. A brushed-steel counter top (top at
3.2) carries two white porcelain vessel sinks with chrome gooseneck taps and lever handles, a
soap pump and a folded towel stack. Behind it a red-orange mirror board rises to 8: a long
mirror (Glass, role "mirror") in a steel bezel, framed on the top and both sides by round warm
white vanity bulbs (Bulbs, Neon, role "lamp").

The back (+Y) stands against the wall, front = -Y, pivot = bottom-centre. Collides (cabinet,
counter, mirror board). Sockets: Mirror (glass face centre, yaw 0), Tap1 / Tap2 (spout tips,
left / right as seen from the front, for running-water effects), Light (in front of the top
bulb row, for a warm PointLight).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 10.0, 8.0, 2.4
TOP = 3.2                       # counter top surface
TOP_T = 0.2
CAB_Y = (-0.98, 1.1)            # cabinet front .. back
BOARD_Y = (0.96, D / 2)         # mirror board front .. back (wall)
GLASS = (-4.0, 4.0, 4.15, 7.25)  # mirror x0, x1, z0, z1
SINK_X = (-3.1, 3.1)
SINK_Y = -0.12
BOWL_R, BOWL_H = 0.74, 0.42
BULB_R = 0.2


def bulb_points():
    fy = BOARD_Y[0]
    pts = [(-4.5 + 0.9 * i, fy, 7.66) for i in range(11)]
    for sx in (-1, 1):
        pts += [(sx * 4.5, fy, 4.4 + 0.815 * k) for k in range(4)]   # sides (the top row has the corners)
    return pts


def tap(x):
    """Chrome gooseneck tap behind a vessel sink. Returns (objs, spout tip)."""
    by = SINK_Y + BOWL_R + 0.22
    base = ns.cyl(0.11, 0.14, loc=(x, by, TOP + 0.07), verts=8, bevel=0.0)
    tip = (x, SINK_Y + 0.12, TOP + 0.9)
    neck = C.pipe([(x, by, TOP + 0.1), (x, by, TOP + 1.12), (x, SINK_Y + 0.12, TOP + 1.12), tip], 0.065, sides=5,
                  corner=0.22, corner_segs=2)
    levers = []
    for sx in (-1, 1):
        hx = x + sx * 0.36
        levers.append(ns.cyl(0.07, 0.16, loc=(hx, by, TOP + 0.08), verts=6, bevel=0.0))
        levers.append(C.rod((hx, by, TOP + 0.15), (hx + sx * 0.05, by - 0.26, TOP + 0.24), 0.035, verts=4))
    return [base, neck] + levers, tip


def build():
    # cabinet + toe kick + counter top
    cab = ns.box((W - 0.2, CAB_Y[1] - CAB_Y[0], TOP - TOP_T - 0.28), loc=(0, sum(CAB_Y) / 2, 0.28 + (TOP - TOP_T - 0.28) / 2),
                 bevel=0.04, segments=1)
    C.part([cab], "Cabinet", C.CREAM, can_collide=True, smooth_angle=40)
    kick = ns.box((W - 0.4, CAB_Y[1] - CAB_Y[0] - 0.24, 0.3), loc=(0, sum(CAB_Y) / 2 + 0.1, 0.15), bevel=0.02, segments=1)
    C.part([kick], "Kick", C.BLACK, can_collide=True, smooth_angle=40)
    top = ns.box((W, D, TOP_T), loc=(0, 0, TOP - TOP_T / 2), bevel=0.05, segments=1)
    board = C.prism(C.rrect(W, H - TOP + 0.02, 0.18, 2, 0, (TOP - 0.02 + H) / 2), "y", BOARD_Y[0], BOARD_Y[1])
    ns.bevel(board, width=0.04, segments=1)
    C.part([top], "Counter", C.STEEL, "Metal", can_collide=True, smooth_angle=40)
    C.part([board], "MirrorBoard", C.LOCKER_RED, can_collide=True, smooth_angle=40)

    # doors / drawers (mustard) + chrome bar pulls
    fy = CAB_Y[0]
    panels, pulls = [], []
    z0, z1 = 0.45, TOP - TOP_T - 0.14
    for sx in (-1, 1):
        for k in range(2):   # double doors under each sink
            xa = sx * (1.55 + 1.65 * k)
            xb = sx * (1.55 + 1.65 * (k + 1))
            xa, xb = sorted((xa, xb))
            xa, xb = xa + 0.05, xb - 0.05
            panels.append(C.prism(C.rrect(xb - xa, z1 - z0, 0.08, 1, (xa + xb) / 2, (z0 + z1) / 2), "y", fy - 0.065,
                                  fy + 0.005))
            # pulls next to the meeting edge of each pair
            px = (xb - 0.2) if (k == 0) == (sx > 0) else (xa + 0.2)
            pulls.append(ns.box((0.1, 0.1, 0.62), loc=(px, fy - 0.1, 2.1), bevel=0.0))
    dh = (z1 - z0) / 3
    for k in range(3):     # drawer stack in the middle
        za, zb = z0 + k * dh + 0.04, z0 + (k + 1) * dh - 0.04
        panels.append(C.prism(C.rrect(3.0, zb - za, 0.08, 1, 0, (za + zb) / 2), "y", fy - 0.065, fy + 0.005))
        pulls.append(ns.box((0.9, 0.1, 0.1), loc=(0, fy - 0.1, (za + zb) / 2 + 0.12), bevel=0.0))
    C.part(panels, "Doors", C.MUSTARD, smooth_angle=40)

    # mirror: steel bezel + glass
    x0, x1, gz0, gz1 = GLASS
    gcx, gcz = (x0 + x1) / 2, (gz0 + gz1) / 2
    bezel = C.ring_slab(C.rrect(x1 - x0 + 0.3, gz1 - gz0 + 0.3, 0.2, 1, gcx, gcz), C.rrect(x1 - x0, gz1 - gz0, 0.08, 1, gcx, gcz),
                        "y", BOARD_Y[0] - 0.08, BOARD_Y[0] + 0.02)
    glass = C.prism(C.rrect(x1 - x0 + 0.04, gz1 - gz0 + 0.04, 0.09, 1, gcx, gcz), "y", BOARD_Y[0] - 0.04, BOARD_Y[0] + 0.01)
    ns.tag(glass, "Mirror", C.MIRROR, "Glass", recolor="mirror", cast_shadow=False, smooth_angle=None)

    # bulbs (domes on the board face)
    bulbs = C.domes(bulb_points(), BULB_R, axis=(0, -1, 0), segs=8, rings=2)
    ns.tag(bulbs, "Bulbs", C.WARM_WHITE, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)

    # vessel sinks (porcelain bowls with a real hollow), drains, taps
    porcelain, chrome = [], pulls + [bezel]
    for x in SINK_X:
        r, h = BOWL_R, BOWL_H
        bowl = ns.lathe([(0.0, 0.0), (r * 0.5, 0.0), (r * 0.8, h * 0.3), (r * 0.98, h * 0.82), (r, h),
                         (r - 0.07, h), (r - 0.09, h * 0.8), (r * 0.66, h * 0.3), (r * 0.3, h * 0.22), (0.0, h * 0.2)],
                        verts=10, loc=(x, SINK_Y, TOP))
        porcelain.append(bowl)
        drain = C.disc(0.1, loc=(x, SINK_Y, TOP + h * 0.2 + 0.012), verts=8)
        chrome.append(drain)
        objs, _tip = tap(x)
        chrome += objs
    # soap pump (between the left sink and the drawers) and a folded towel stack
    sx_ = -1.1
    porcelain.append(ns.lathe([(0.0, 0.0), (0.17, 0.0), (0.18, 0.32), (0.12, 0.42), (0.06, 0.45), (0.0, 0.45)], verts=8,
                              loc=(sx_, 0.35, TOP)))
    chrome.append(ns.cyl(0.035, 0.16, loc=(sx_, 0.35, TOP + 0.52), verts=6, bevel=0.0))
    chrome.append(C.rod((sx_, 0.35, TOP + 0.6), (sx_, 0.17, TOP + 0.6), 0.035, verts=5))
    C.part(porcelain, "Porcelain", C.PORCELAIN, smooth_angle=50)
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=50)
    towels = [ns.box((0.95, 0.75, 0.2), loc=(1.15, 0.25, TOP + 0.1), rot=(0, 0, 6), bevel=0.07, segments=1),
              ns.box((0.9, 0.72, 0.19), loc=(1.13, 0.27, TOP + 0.295), rot=(0, 0, -4), bevel=0.07, segments=1)]
    C.part(towels[:1], "TowelA", C.TOWEL, "Fabric", smooth_angle=50)
    C.part(towels[1:], "TowelB", C.BRAND, "Fabric", smooth_angle=50)


GZC = (GLASS[2] + GLASS[3]) / 2
SOCKETS = {"Mirror": ((0, BOARD_Y[0] - 0.04, GZC), 0.0),
           "Tap1": ((SINK_X[0], SINK_Y + 0.12, TOP + 0.84), 0.0),
           "Tap2": ((SINK_X[1], SINK_Y + 0.12, TOP + 0.84), 0.0),
           "Light": ((0, BOARD_Y[0] - 0.8, 7.66), 0.0)}
META = {"counter_height": TOP, "mount": "floor, back (+Y) against the wall",
        "glass_size": [GLASS[1] - GLASS[0], GLASS[3] - GLASS[2]],
        "surfaces": [C.screen_meta("Mirror", GLASS[1] - GLASS[0], GLASS[3] - GLASS[2])],
        "roles": {"mirror": "Mirror", "lamp": "Bulbs (19 vanity bulbs)"},
        "light_hint": {"type": "PointLight", "at": "Socket_Light", "color": C.WARM_WHITE, "range": 12, "brightness": 1.2}}

if __name__ == "__main__":
    C.run(build, "Lobby_VanityCounter", sockets=SOCKETS, budget=2000, meta=META)
