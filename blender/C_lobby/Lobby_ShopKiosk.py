"""Lobby_ShopKiosk — freestanding retro shop kiosk (~6.6 wide x 4.5 deep x 11.5 tall).

Red-orange counter cabinet with a cream inset front carrying a big cyan gem emblem (the
premium-currency vibe; a classic brilliant-cut shape, not any real logo), chrome kick plate
and counter edge, a cream laminate counter with a coin stack, a gem and a gift box on it.
Behind the counter a navy back tower holds the screen (Screen, role "screen", Front face)
in a chrome bezel; chrome corner posts carry a roof with a cream / red-orange striped
awning and scalloped valance, a navy fascia with mustard "SHOP" letters and warm marquee
bulbs (Bulbs, Neon, role "lamp"), and a giant gold star coin on top (Coin, role
"coin_spin": code may spin it about its vertical axis).

Front = -Y, pivot = bottom-centre. Sockets: Screen (screen face centre, facing front),
Prompt (in front of the counter, counter height), Coin (coin centre, its spin axis is Z).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D = 5.6, 3.4                # cabinet footprint (x, y); front at y = -D/2
TOP = 3.1                      # counter top
ROOF = 7.9
SCR_W, SCR_H = 4.0, 2.3
SCR_Z = 5.45
SCR_Y = 0.55                   # screen face plane (front of the back tower)
COIN_Z = 10.35
GEM = "#38D5F0"
GEM_LIGHT = "#A8F2FF"
GIFT = "#E8502A"


def star(r_out, r_in, n=5, cx=0.0, cz=0.0, rot=90.0):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + 180.0 * i / n)
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def gem_outline(s, cx, cz):
    return [(cx - 0.9 * s, cz + 0.3 * s), (cx - 0.5 * s, cz + 0.72 * s), (cx + 0.5 * s, cz + 0.72 * s),
            (cx + 0.9 * s, cz + 0.3 * s), (cx, cz - 0.85 * s)]


def build():
    fy = -D / 2
    # --- cabinet + counter -------------------------------------------------------------
    cab = ns.box((W, D, TOP - 0.35), loc=(0, 0, 0.35 + (TOP - 0.35) / 2 - 0.1), bevel=0.1, segments=1)
    tower = ns.box((W, D / 2 - SCR_Y + 0.0, ROOF - TOP), loc=(0, (SCR_Y + D / 2) / 2, (TOP + ROOF) / 2), bevel=0.08,
                   segments=1)
    C.part([cab], "Cabinet", C.BRAND, can_collide=True, smooth_angle=40)
    C.part([tower], "Tower", C.NAVY, can_collide=True, smooth_angle=40)
    # red-orange belt + mustard pinstripe wrapped round the tower's sides and back
    belt, pin = [], []
    for (z0, z1), lst in (((6.1, 6.6), belt), ((6.75, 6.87), pin)):
        zc, h = (z0 + z1) / 2, z1 - z0
        lst.append(ns.box((W - 0.12, 0.04, h), loc=(0, D / 2 + 0.01, zc), bevel=0.0))
        for sx in (-1, 1):
            lst.append(ns.box((0.04, D / 2 - SCR_Y - 0.12, h), loc=(sx * (W / 2 + 0.01), (SCR_Y + D / 2) / 2, zc), bevel=0.0))
    panel = C.prism(C.rrect(W - 1.0, TOP - 1.05, 0.25, 3, 0, 0.45 + (TOP - 1.05) / 2 + 0.05), "y", fy - 0.04, fy + 0.02)
    top = C.prism(C.rrect(W + 0.4, D + 0.3, 0.2, 2, 0, -0.1), "z", TOP - 0.14, TOP + 0.06)
    ns.bevel(top, width=0.04, segments=1)
    C.part([panel, top], "Cream", C.CREAM, smooth_angle=40)

    chrome = [ns.box((W + 0.06, D + 0.06, 0.35), loc=(0, 0, 0.175), bevel=0.05, segments=1),
              C.pipe([(x, fy - 0.32, TOP - 0.17) for x in (-W / 2 - 0.12, W / 2 + 0.12)], 0.07, sides=6)]
    # corner posts (front) and screen bezel
    for sx in (-1, 1):
        chrome.append(ns.cyl(0.11, ROOF - TOP, loc=(sx * (W / 2 - 0.15), fy + 0.15, (TOP + ROOF) / 2), verts=8, bevel=0.0))
        chrome.append(ns.cyl(0.2, 0.12, loc=(sx * (W / 2 - 0.15), fy + 0.15, TOP + 0.12), verts=8, bevel=0.0))
    chrome.append(C.ring_slab(C.rrect(SCR_W + 0.32, SCR_H + 0.32, 0.18, 1, 0, SCR_Z), C.rrect(SCR_W, SCR_H, 0.08, 1, 0, SCR_Z),
                              "y", SCR_Y - 0.08, SCR_Y + 0.03))
    chrome.append(ns.cyl(0.14, COIN_Z - ROOF - 1.0, loc=(0, 0.2, (ROOF + COIN_Z - 1.0) / 2 + 0.2), verts=8, bevel=0.0))
    scr = C.prism(C.rrect(SCR_W, SCR_H, 0.08, 1, 0, SCR_Z), "y", SCR_Y - 0.04, SCR_Y + 0.02)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)

    # --- gem emblem on the cabinet front + counter props ---------------------------------
    gz = 1.75
    gem = C.prism(gem_outline(0.95, 0, gz), "y", fy - 0.14, fy - 0.02)
    gem_top = C.prism([(-0.5 * 0.95, gz + 0.72 * 0.95), (0.5 * 0.95, gz + 0.72 * 0.95), (0.3, gz + 0.3 * 0.95),
                       (-0.3, gz + 0.3 * 0.95)], "y", fy - 0.17, fy - 0.1)
    small = C.prism(gem_outline(0.3, 0.0, 0.0), "y", -0.1, 0.1)
    ns.bevel(small, width=0.03, segments=1)
    C.place(small, (0.45, -1.15, TOP + 0.06 + 0.255), yaw=-20)
    C.part([gem, small], "Gem", GEM, smooth_angle=None)
    C.part([gem_top], "GemShine", GEM_LIGHT, smooth_angle=None)
    gold = []
    for i in range(4):
        gold.append(ns.cyl(0.32, 0.1, loc=(-1.6 + (0.03 if i % 2 else -0.02), -0.7, TOP + 0.11 + i * 0.11), verts=10,
                           bevel=0.0))
    gold.append(ns.cyl(0.32, 0.1, loc=(-1.05, -0.85, TOP + 0.11), verts=10, bevel=0.0))
    # gift box with mustard ribbon
    gift = ns.box((0.75, 0.75, 0.6), loc=(1.65, -0.35, TOP + 0.06 + 0.3), rot=(0, 0, 18), bevel=0.04, segments=1)
    rib = [ns.box((0.79, 0.16, 0.64), loc=(1.65, -0.35, TOP + 0.06 + 0.3), rot=(0, 0, 18), bevel=0.0),
           ns.box((0.16, 0.79, 0.64), loc=(1.65, -0.35, TOP + 0.06 + 0.3), rot=(0, 0, 18), bevel=0.0),
           ns.sphere(0.14, loc=(1.65, -0.35, TOP + 0.06 + 0.66), scale=(1.4, 0.7, 0.8), segs=8, rings=4)]
    C.part([gift], "Gift", GIFT, smooth_angle=40)

    # --- roof, fascia, awning ------------------------------------------------------------
    roof = ns.box((W + 0.6, D + 0.5, 0.3), loc=(0, 0.05, ROOF + 0.15), bevel=0.08, segments=1)
    fascia = C.prism(C.rrect(W + 0.2, 1.1, 0.2, 2, 0, ROOF + 0.3 + 0.55), "y", fy - 0.2, fy + 0.1)
    ns.bevel(fascia, width=0.04, segments=1)
    C.part([roof, fascia], "Roof", C.NAVY_DEEP, smooth_angle=40)
    letters = C.text("SHOP", 0.8, 0.04, (0, fy - 0.21, ROOF + 0.85), width=2.6, res=1, spacing=1.1, flat=True)
    gold_trim = [letters] + rib
    # awning: 8 stripes from the roof edge sloping down/out to the front + scalloped valance
    ax0, ax1 = -W / 2 - 0.3, W / 2 + 0.3
    n = 8
    sw = (ax1 - ax0) / n
    # back edge starts inside the fascia (at fy - 0.25 the whole awning hung 0.05 in front of it, unattached)
    y_back, z_back, y_front, z_front = fy - 0.15, ROOF + 0.05, fy - 1.45, ROOF - 0.85
    stripes = {C.CREAM: [], C.BRAND: []}
    t = 0.07
    for i in range(n):
        col = C.BRAND if i % 2 == 0 else C.CREAM
        x0, x1 = ax0 + i * sw, ax0 + (i + 1) * sw
        prof = [(y_back, z_back), (y_front, z_front), (y_front, z_front - t), (y_back, z_back - t)]
        stripes[col].append(C.prism(prof, "x", x0, x1))
        tab = [(x0, z_front), (x1, z_front), (x1, z_front - 0.28)]
        for k in range(1, 4):
            a = math.pi * k / 4
            tab.append(((x0 + x1) / 2 + (sw / 2) * math.cos(a), z_front - 0.28 - (sw / 2) * math.sin(a)))
        tab.append((x0, z_front - 0.28))
        stripes[col].append(C.prism(tab, "y", y_front - t / 2, y_front + t / 2))
    for sx in (-1, 1):   # side cheeks
        x = sx * (ax1 - 0.02)
        a0, a1 = sorted((x - 0.035, x + 0.035))
        # cheek top 0.012 above the canvas (coplanar before: red / cream z-fighting along the +X edge)
        stripes[C.BRAND].append(C.prism([(y_back, z_back + 0.012), (y_front, z_front + 0.012), (y_front, z_front - 0.28),
                                         (y_back, z_front - 0.1)], "x", a0, a1))
    C.part(stripes[C.BRAND], "AwningRed", C.BRAND, smooth_angle=None)
    C.part(stripes[C.CREAM], "AwningCream", C.PAPER, smooth_angle=None)

    # marquee bulbs along the fascia top
    bulbs = [ns.sphere(0.14, loc=(-W / 2 + 0.3 + (W - 0.6) * i / 6, fy - 0.2, ROOF + 1.47), segs=6, rings=4)
             for i in range(7)]
    ns.tag(C.merge(bulbs, "Bulbs"), "Bulbs", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)

    # --- giant gold star coin on top -----------------------------------------------------
    coin = ns.cyl(1.05, 0.36, loc=(0, 0, 0), verts=18, bevel=0.1, segments=2)
    stars = [C.prism(star(0.66, 0.29), "y", -0.27, -0.12), C.prism(star(0.66, 0.29), "y", 0.12, 0.27)]
    coin.rotation_euler = (math.radians(90), 0, 0)
    C.place([coin] + stars, (0, 0.2, COIN_Z))
    ns.tag(C.merge([coin] + stars, "Coin"), "Coin", C.GOLD, "Metal", recolor="coin_spin", smooth_angle=40)
    C.part(gold, "GoldCoins", C.GOLD, "Metal", smooth_angle=40)
    C.part(gold_trim + pin, "Mustard", C.MUSTARD, smooth_angle=40)
    C.part(belt, "Belt", C.BRAND, smooth_angle=30)
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=45)


def sockets():
    return {"Screen": ((0, SCR_Y - 0.04, SCR_Z), 0.0),
            "Prompt": ((0, -D / 2 - 0.9, TOP), 0.0),
            "Coin": ((0, 0.2, COIN_Z), 0.0)}


META = {"screen_size": [SCR_W, SCR_H], "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
        "counter_height": TOP, "roles": {"screen": "Screen", "lamp": "Bulbs", "coin_spin": "Coin (spin about Y)"},
        "light_hint": {"type": "PointLight", "color": C.LAMP_WARM, "range": 12, "brightness": 1}}

if __name__ == "__main__":
    C.run(build, "Lobby_ShopKiosk", sockets=sockets(), meta=META)
