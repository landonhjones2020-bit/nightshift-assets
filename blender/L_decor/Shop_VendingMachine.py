"""Shop_VendingMachine — Break Room snack vending machine.

Red-orange cabinet with a big glass front (part Glass, role "glass", transparent) over a
dark-lined cavity holding five shelves of colourful snacks — candy bars, chip bags with
label bands, cookie packs, big bags — with price-tag strips, a lit fluorescent tube (part InteriorLight, role "lamp") and three sold-out slots
showing their chrome spiral coils. Right-hand control column: a small display with lit
digits, a 3 x 4 keypad, a chrome coin slot plate, a bill slot with a green light and a coin
return cup. Below the window: the push-flap pickup bin. On top: a lit header panel (part
Lamp, role "lamp", Neon) with SNACKS letters. Collides (cabinet).
Sockets: Prompt = keypad front (yaw 0, faces -Y); Dispense = inside the pickup bin.
Front faces -Y, pivot = bottom-centre. 3.4 x 6.4 x 2.6.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 3.4, 6.4, 2.6
PLINTH = 0.22
FY = -D / 2                       # front face
CAV_Y = -0.35                     # cavity back wall
WIN = (-1.5, 0.62, 1.9, 5.82)     # window x0, x1, z0, z1
SHELF_Z = (2.02, 2.78, 3.54, 4.3, 5.06)
COLS_X = [WIN[0] + 0.21 + 0.42 * i for i in range(5)]
LINER = "#24262B"
SOLD_OUT = {(1, 3), (3, 1), (4, 4)}     # (row, col) slots showing a bare coil


def build():
    rnd = random.Random(5)
    x0, x1, z0, z1 = WIN
    body = [ns.box((W, D - (CAV_Y - FY), H - PLINTH), loc=(0, (CAV_Y + D / 2) / 2, PLINTH + (H - PLINTH) / 2), bevel=0.12,
                   segments=1),                                                                       # cabinet back
            ns.box((W / 2 + x0, CAV_Y - FY, H - PLINTH), loc=((-W / 2 + x0) / 2, (FY + CAV_Y) / 2, PLINTH + (H - PLINTH) / 2),
                   bevel=0.1, segments=1),                                                            # left stile
            ns.box((W / 2 - x1, CAV_Y - FY, H - PLINTH), loc=((x1 + W / 2) / 2, (FY + CAV_Y) / 2, PLINTH + (H - PLINTH) / 2),
                   bevel=0.1, segments=1),                                                            # control column
            ns.box((x1 - x0 + 0.02, CAV_Y - FY, z0 - PLINTH), loc=((x0 + x1) / 2, (FY + CAV_Y) / 2, (PLINTH + z0) / 2),
                   bevel=0.06, segments=1),                                                           # bottom section
            ns.box((x1 - x0 + 0.02, CAV_Y - FY, H - z1), loc=((x0 + x1) / 2, (FY + CAV_Y) / 2, (z1 + H) / 2), bevel=0.06,
                   segments=1)]                                                                       # top header
    C.part(body, "Cabinet", C.BRAND, can_collide=True, smooth_angle=35)
    plinth = ns.box((W - 0.3, D - 0.3, PLINTH + 0.02), loc=(0, 0.05, (PLINTH + 0.02) / 2), bevel=0.0)
    C.part([plinth], "Plinth", C.BASE_DARK, can_collide=True, smooth_angle=30)

    # cavity liner (dark): back wall, side walls, ceiling, floor — just inside the opening
    e = 0.004
    back_wall = C.quad_xz(x0, x1, z0, z1, CAV_Y - e)
    liner = [ns.box((0.01, CAV_Y - FY, z1 - z0), loc=(x0 + e + 0.005, (FY + CAV_Y) / 2, (z0 + z1) / 2), bevel=0.0),
             ns.box((0.01, CAV_Y - FY, z1 - z0), loc=(x1 - e - 0.005, (FY + CAV_Y) / 2, (z0 + z1) / 2), bevel=0.0),
             ns.box((x1 - x0, CAV_Y - FY, 0.01), loc=((x0 + x1) / 2, (FY + CAV_Y) / 2, z1 - e - 0.005), bevel=0.0)]
    C.part(liner, "Liner", LINER, smooth_angle=None)
    C.part([back_wall], "LinerBack", "#767C86", smooth_angle=None)
    # fluorescent tube along the top of the cavity, behind the header (role lamp: dims in blackouts)
    tube = ns.box((x1 - x0 - 0.1, 0.05, 0.05), loc=((x0 + x1) / 2, FY + 0.16, z1 - 0.07), bevel=0.0)
    C.part([tube], "InteriorLight", "#FFF4D6", "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)

    # shelves + price-tag strips + white tags
    shelves, strips, tags = [], [], []
    for z in SHELF_Z:
        shelves.append(ns.box((x1 - x0 - 0.02, CAV_Y - FY - 0.12, 0.05), loc=((x0 + x1) / 2, (FY + CAV_Y) / 2 + 0.04, z - 0.025),
                              bevel=0.0))
        strips.append(C.quad_xz(x0 + 0.01, x1 - 0.01, z - 0.13, z - 0.02, FY + 0.094))
        for x in COLS_X:
            tags.append(C.quad_xz(x - 0.1, x + 0.1, z - 0.115, z - 0.035, FY + 0.088))
    C.part(shelves, "Shelves", "#5A5E66", "Metal", smooth_angle=None)
    C.part(strips, "TagStrips", "#2E3138", smooth_angle=None)
    C.part(tags, "Tags", C.PAPER, smooth_angle=None)

    # snacks: one product type per shelf (bottom -> top)
    rows = [  # (w, d, h, colours, label band colour or None, bevel)
        (0.36, 0.24, 0.62, ("#E23B2E", "#2F74C0", "#F2C230", "#3FA34D", "#7E4BB5"), "#FBF6EA", 0.07),   # big bags
        (0.36, 0.14, 0.42, ("#B5793E", "#E9D7B0", "#B5793E", "#8A5530", "#E9D7B0"), "#C8323A", 0.04),   # cookie packs
        (0.34, 0.2, 0.56, ("#F07F2C", "#21A39A", "#E23B2E", "#F2C230", "#2F74C0"), "#FBF6EA", 0.07),    # chip bags
        (0.36, 0.2, 0.56, ("#3FA34D", "#F2C230", "#7E4BB5", "#E23B2E", "#F07F2C"), "#FBF6EA", 0.07),    # chip bags
        (0.34, 0.1, 0.5, ("#5B3A29", "#C8323A", "#E8A33A", "#2E5EAA", "#5B3A29"), "#F2C230", 0.03),     # candy bars
    ]
    snacks, bands, coils = {}, {}, []
    for r, (z, (w, d, h, cols, band, bev)) in enumerate(zip(SHELF_Z, rows)):
        for c, x in enumerate(COLS_X):
            if (r, c) in SOLD_OUT:
                # bare spiral coil lying front-to-back on the shelf
                pts = []
                turns, n = 2.5, 14
                for k in range(n + 1):
                    t = k / n
                    a = 2 * math.pi * turns * t
                    pts.append((x + 0.13 * math.cos(a), FY + 0.2 + 0.62 * t, z + 0.15 + 0.13 * math.sin(a)))
                coils.append(C.pipe(pts, 0.018, sides=3))
                continue
            yy = FY + 0.24 + d / 2 + rnd.uniform(0.0, 0.05)
            yaw = rnd.uniform(-6, 6)
            b = ns.box((w, d, h), loc=(x, yy, z + h / 2), rot=(rnd.uniform(-4, 2), 0, yaw), bevel=bev, segments=1)
            snacks.setdefault(cols[c], []).append(b)
            if band:
                # label band on the packet front, turned with the packet
                q = C.quad_xz(-w * 0.36, w * 0.36, h * 0.38, h * 0.62, -d / 2 - 0.006)
                C.place([q], loc=(x, yy, z), yaw=yaw)
                bands.setdefault(band, []).append(q)
    for i, (col, objs) in enumerate(snacks.items()):
        C.part(objs, f"Snack{i}", col, smooth_angle=40)
    for i, (col, objs) in enumerate(bands.items()):
        C.part(objs, f"SnackLabel{i}", col, smooth_angle=None)
    C.part(coils, "Coils", C.CHROME, "Metal", smooth_angle=60)

    # glass front (slightly behind the frame face so the stiles overlap its edges)
    glass = ns.box((x1 - x0 + 0.06, 0.03, z1 - z0 + 0.06), loc=((x0 + x1) / 2, FY + 0.06, (z0 + z1) / 2), bevel=0.0)
    C.part([glass], "Glass", "#A7C7D2", "Glass", transparency=0.78, recolor="glass", cast_shadow=False, smooth_angle=None)

    # control column
    cx = (x1 + W / 2) / 2 - 0.02
    panel = ns.box((0.86, 0.06, 3.3), loc=(cx, FY - 0.03, 3.85), bevel=0.03, segments=1)
    C.part([panel], "ControlPanel", "#2E3138", smooth_angle=35)
    py = FY - 0.06
    disp = ns.box((0.62, 0.03, 0.34), loc=(cx, py - 0.015, 5.1), bevel=0.0)
    C.part([disp], "Display", "#121A16", smooth_angle=None)
    digits = [C.quad_xz(cx - 0.24 + 0.13 * k, cx - 0.14 + 0.13 * k, 5.03, 5.17, py - 0.033) for k in range(4)]
    C.part(digits, "Digits", "#7CFF8A", "Neon", cast_shadow=False, smooth_angle=None)
    keys = []
    for rr in range(4):
        for cc in range(3):
            keys.append(ns.box((0.16, 0.05, 0.13), loc=(cx - 0.21 + 0.21 * cc, py - 0.025, 4.62 - 0.19 * rr), bevel=0.0))
    C.part(keys, "Buttons", "#D9DCE0", smooth_angle=None)
    chrome = [ns.box((0.34, 0.05, 0.46), loc=(cx - 0.18, py - 0.025, 3.52), bevel=0.02, segments=1),    # coin plate
              ns.box((0.3, 0.12, 0.2), loc=(cx, py - 0.06, 2.42), bevel=0.02, segments=1)]           # coin return
    slots = [C.quad_xz(cx - 0.2, cx - 0.16, 3.4, 3.66, py - 0.052),                                   # coin slot
             C.quad_xz(cx + 0.06, cx + 0.36, 3.2, 3.26, py - 0.004),                                  # bill slot
             C.quad_xz(cx - 0.11, cx + 0.11, 2.36, 2.44, py - 0.121)]                                 # return cup opening
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=40)
    C.part(slots, "Slots", "#0E0F12", smooth_angle=None)
    light = ns.box((0.07, 0.03, 0.07), loc=(cx + 0.21, py - 0.015, 3.42), bevel=0.0)
    C.part([light], "BillLight", "#5CD67F", "Neon", cast_shadow=False, smooth_angle=None)

    # pickup bin: dark recess + chrome push flap
    bz0, bz1 = 0.62, 1.42
    recess = C.quad_xz(x0 + 0.18, x1 - 0.18, bz0, bz1, FY - 0.004)
    flap = ns.box((x1 - x0 - 0.5, 0.05, (bz1 - bz0) * 0.55), loc=((x0 + x1) / 2, FY - 0.03, bz1 - (bz1 - bz0) * 0.3),
                  rot=(-12, 0, 0), bevel=0.02, segments=1)
    C.part([recess], "BinRecess", "#0E0F12", smooth_angle=None)
    C.part([flap], "BinFlap", "#3B3F46", smooth_angle=40)

    # lit header panel with SNACKS letters
    lamp = ns.box((W - 0.5, 0.05, 0.42), loc=(0, FY - 0.025, H - 0.32), bevel=0.0)
    C.part([lamp], "Lamp", "#FFF1C8", "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)
    letters = C.text("SNACKS", 0.3, 0.01, (0, FY - 0.05 - 0.008 + 0.005, H - 0.32), width=1.8, res=1, spacing=1.1, flat=True)
    C.part([letters], "LampLetters", C.BRAND_DARK, smooth_angle=None)


SOCKETS = {"Prompt": (((0.62 + W / 2) / 2 - 0.02, FY - 0.4, 4.3), 0.0),
           "Dispense": (((WIN[0] + WIN[1]) / 2, FY + 0.25, 0.75), 0.0)}
META = {"glass": "part Glass (role glass, transparency 0.78)",
        "lamp": "parts Lamp (lit SNACKS header) and InteriorLight (tube inside the cavity), both role lamp, Neon",
        "light_hint": {"type": "SurfaceLight", "part": "Lamp", "face": "Front", "color": "#FFF1C8", "range": 8}}

if __name__ == "__main__":
    C.run(build, "Shop_VendingMachine", sockets=SOCKETS, budget=2500, meta=META)
