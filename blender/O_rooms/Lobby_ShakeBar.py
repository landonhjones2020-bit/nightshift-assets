"""Lobby_ShakeBar — VIP milkshake bar counter (12 W x 3.5 H x 3 D).

A black-lacquer bar with bullnose ends on a recessed kick: gold art-deco pinstripes and a gold
band on the front fascia, a dark glossy label screen in a gold bezel in the middle of the fascia
(Screen, role "screen", Front face: the game writes SHAKE BAR there), a cyan neon underglow strip
along the foot of the fascia (Underglow, Neon, role "neon") and a gold foot rail on brackets. The
lacquer top (surface at 2.6) has a gold edge band and a gold drink rail along its customer edge.
On it three chrome spindle milkshake mixers (pink, cyan and gold name bands) and three tall
soda-fountain shakes (strawberry, mint, chocolate).

Front (customer side) = -Y, pivot = bottom-centre. Collides (body, top, kick). Sockets: Screen
(label face centre, yaw 0), Underglow (front foot of the bar, for a cyan SurfaceLight/PointLight),
Mixer1..Mixer3 (mixer cup tops, left to right as seen from the front).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
W, H, D = 12.0, 3.5, 3.0
TOP = 2.6                       # bar top surface
TOP_T = 0.16
BODY = (11.4, 2.3, 0.95, 0.12)  # body plan: width, depth, end radius, centre y
TOPP = (12.0, 3.0, 1.25, -0.05)  # top plan
FY = BODY[3] - BODY[1] / 2      # fascia front plane -1.03
SCR_W, SCR_H, SCR_Z = 4.2, 0.95, 1.62
MIXERS = ((-3.9, C.PINK), (0.0, C.CYAN), (3.9, C.GOLD))
SHAKES = ((-1.95, 0.05, C.SHAKE_PINK, C.CYAN), (1.95, 0.0, C.SHAKE_MINT, C.PINK), (5.15, -0.1, C.SHAKE_CHOC, C.GOLD))


def front_path(w, d, r, cy, z, inset=0.0, segs=4):
    """Customer-side (-Y) half of the same rounded-rect outline the prisms use (C.rrect), offset
    outward by `inset`: right side midpoint -> front-right corner -> front edge -> front-left
    corner -> left side midpoint, at height z."""
    pts = C.rrect(w + 2 * inset, d + 2 * inset, r + inset, segs, 0, cy)
    n = segs + 1
    bl, br = pts[:n], pts[n:2 * n]          # rrect lists the corners BL, BR, TR, TL (front = low y)
    path = [(w / 2 + inset, cy)] + list(reversed(br)) + list(reversed(bl)) + [(-(w / 2 + inset), cy)]
    return [(x, y, z) for x, y in path]


def mixer(x, accent, g):
    """Chrome spindle milkshake mixer on the bar top at x (faces -Y). Returns the cup-top point."""
    z0, y = TOP, 0.35
    chrome = g.setdefault("chrome", [])
    chrome.append(C.prism(C.rrect(0.58, 0.66, 0.22, 2, x, y), "z", z0 - 0.01, z0 + 0.11))
    col = C.prism(C.rrect(0.24, 0.22, 0.08, 1, x, y + 0.2), "z", z0 + 0.1, z0 + 0.7)
    chrome.append(col)
    head = ns.cyl(0.14, 0.56, loc=(x, y + 0.04, z0 + 0.74), rot=(90, 0, 0), verts=10, bevel=0.06, segments=1)
    chrome.append(head)
    C.add(g, accent, ns.cyl(0.148, 0.12, loc=(x, y + 0.08, z0 + 0.74), rot=(90, 0, 0), verts=10, bevel=0.0))
    chrome.append(C.rod((x, y - 0.18, z0 + 0.62), (x, y - 0.18, z0 + 0.3), 0.025, verts=4))      # spindle
    chrome.append(ns.box((0.08, 0.2, 0.06), loc=(x, y + 0.04, z0 + 0.55), bevel=0.0))            # cup holder arm
    cup = ns.lathe([(0.0, 0.0), (0.13, 0.0), (0.17, 0.42), (0.155, 0.42), (0.115, 0.03), (0.0, 0.03)], verts=10,
                   loc=(x, y - 0.18, z0 + 0.13))
    C.add(g, C.STEEL, cup)
    C.add(g, C.BLACK, C.spheres([(x + 0.16, y + 0.12, z0 + 0.78)], 0.05, segs=6, rings=4))      # switch knob
    return (x, y - 0.18, z0 + 0.55)


def build():
    # body (lacquer), kick (lacquer, recessed), top slab
    bw, bd, br, bcy = BODY
    body = C.prism(C.rrect(bw, bd, br, 3, 0, bcy), "z", 0.3, TOP - TOP_T + 0.01)
    ns.bevel(body, width=0.04, segments=1)
    kick = C.prism(C.rrect(bw - 0.5, bd - 0.5, br - 0.25, 3, 0, bcy + 0.05), "z", 0.0, 0.32)
    tw, td, tr, tcy = TOPP
    top = C.prism(C.rrect(tw - 0.16, td - 0.16, tr - 0.08, 3, 0, tcy), "z", TOP - TOP_T, TOP)
    C.part([body, kick, top], "Lacquer", C.LACQUER, can_collide=True, smooth_angle=40)

    gold = []
    # gold edge band round the top slab + gold drink rail along the customer edge
    gold.append(C.ring_slab(C.rrect(tw, td, tr, 3, 0, tcy), C.rrect(tw - 0.16, td - 0.16, tr - 0.08, 3, 0, tcy), "z",
                            TOP - TOP_T - 0.03, TOP + 0.01))
    gold.append(C.pipe(front_path(tw - 0.34, td - 0.34, tr - 0.17, tcy, TOP + 0.07, segs=3), 0.075, sides=5))
    # fascia: gold band under the top, gold pinstripes either side of the screen, foot rail on brackets
    gold.append(C.pipe(front_path(bw, bd, br, bcy, TOP - TOP_T - 0.12, inset=0.02, segs=3), 0.035, sides=4))
    for x in (-4.6, -3.7, -2.8, 2.8, 3.7, 4.6):
        gold.append(ns.box((0.07, 0.04, 1.62), loc=(x, FY - 0.01, 1.42), bevel=0.0))
    gold.append(C.pipe(front_path(bw + 0.5, bd + 0.5, br + 0.25, bcy, 0.62, segs=3)[1:-1], 0.06, sides=5))
    for x in (-4.2, -1.4, 1.4, 4.2):
        gold.append(C.rod((x, FY - 0.25, 0.62), (x, FY + 0.02, 0.62), 0.045, verts=4))
    # label screen + bezel
    scr = ns.box((SCR_W, 0.04, SCR_H), loc=(0, FY - 0.06, SCR_Z), bevel=0.0)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=None)
    gold.append(C.ring_slab(C.rrect(SCR_W + 0.26, SCR_H + 0.26, 0.16, 2, 0, SCR_Z), C.rrect(SCR_W, SCR_H, 0.04, 2, 0, SCR_Z),
                            "y", FY - 0.1, FY + 0.02))
    # cyan neon underglow along the foot of the fascia
    glow = C.pipe(front_path(bw, bd, br, bcy, 0.36, inset=0.03, segs=3), 0.05, sides=5)
    ns.tag(glow, "Underglow", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # mixers + tall shakes
    g = {}
    for x, accent in MIXERS:
        mixer(x, accent, g)
    gold += g.pop(C.GOLD, [])
    C.part(g.pop("chrome"), "Mixers", C.CHROME, "Metal", smooth_angle=50)
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=50)
    glass = []
    for x, y, shake, straw in SHAKES:
        d = C.milkshake((x, y, TOP), h=0.6, r=0.155, shake=shake, straw=straw, straw_yaw=60.0, verts=7)
        glass += d.pop("glass")
        for col, objs in d.items():
            C.add(g, col, objs)
    ns.tag(C.merge(glass, "Glasses"), "Glasses", C.GLASS_TINT, "Glass", transparency=0.55, cast_shadow=False, smooth_angle=50)
    C.parts_by_colour(g, "Bits", smooth_angle=50)


def sockets():
    s = {"Screen": ((0, FY - 0.08, SCR_Z), 0.0), "Underglow": ((0, FY - 0.3, 0.2), 0.0)}
    for i, (x, _a) in enumerate(MIXERS):
        s[f"Mixer{i + 1}"] = ((x, 0.17, TOP + 0.55), 0.0)
    return s


META = {"counter_height": TOP, "screen_size": [SCR_W, SCR_H], "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
        "screen_hint": "dark glossy label panel: draw SHAKE BAR in neon-style text",
        "roles": {"screen": "Screen (front fascia label)", "neon": "Underglow (cyan)"},
        "light_hint": {"type": "SurfaceLight / PointLight", "at": "Socket_Underglow", "color": C.CYAN, "range": 8,
                       "brightness": 1.5}}

if __name__ == "__main__":
    C.run(build, "Lobby_ShakeBar", sockets=sockets(), budget=3000, meta=META, backdrop="#3A2440")
