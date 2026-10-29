"""Lobby_DailyBoard — "daily specials" chalkboard on an A-frame easel (dailies + quests).

A wood-framed chalkboard stands upright between two splayed A-frame leg pairs. Chalk
"DAILY" lettering and stars across the top, a cork strip pinned with seven calendar
day tabs (cream pages with red-orange headers; today's tab is mustard), and below it the
screen (Screen, role "screen", Front face) where the game draws the 7-day rewards
calendar and the three daily quests, outlined in chalk. A chalk tray with chalk sticks and
an eraser sits under the board; brand bunting hangs along the top rail.
The screen is vertical (not tilted) so the yaw-only socket describes it exactly.

Front = -Y, pivot = bottom-centre. Sockets: Screen (screen face centre), Prompt (in front
of the board at chest height).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
BW, BH = 5.4, 6.4               # board outer size
BZ0 = 1.3                       # board bottom
ZC = BZ0 + BH / 2
SCR_W, SCR_H = 4.3, 2.9
SCR_Z = 3.6
CHALK_FACE = -0.06              # chalk surface plane (front)
CHALK_WHITE = "#ECE8DC"
CHALK_PINK = "#F29BC4"
FELT = "#3A3A40"


def beam(p0, p1, w=0.22, d=0.22, name="Beam"):
    p0, p1 = Vector(p0), Vector(p1)
    v = p1 - p0
    b = ns.box((w, d, v.length), loc=(0, 0, 0), bevel=0.04, segments=1, name=name)
    b.rotation_euler = v.to_track_quat("Z", "Y").to_euler()
    b.location = (p0 + p1) / 2
    return b


def star(r_out, r_in, cx, cz, n=5):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(90 + 180.0 * i / n)
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def build():
    # board: wood frame ring + chalk panel
    frame = C.ring_slab(C.rrect(BW, BH, 0.25, 2, 0, ZC), C.rrect(BW - 0.5, BH - 0.5, 0.12, 2, 0, ZC), "y", -0.16, 0.16)
    chalk = ns.box((BW - 0.46, 0.14, BH - 0.46), loc=(0, CHALK_FACE + 0.07, ZC), bevel=0.0)
    C.part([chalk], "Chalkboard", C.CHALK, "Slate", can_collide=True, smooth_angle=30)
    # A-frame legs (both sides) + cross braces + top rail with knob pins
    wood = [frame]
    for sx in (-1, 1):
        x = sx * (BW / 2 + 0.17)
        top = (x, 0.0, BZ0 + BH - 0.5)
        wood.append(beam(top, (x, -1.35, 0.0)))
        wood.append(beam(top, (x, 1.35, 0.0)))
        wood.append(beam((x, -1.0, 1.0), (x, 1.0, 1.0), w=0.16, d=0.16))
    wood.append(ns.box((BW + 0.7, 0.36, 0.26), loc=(0, 0.0, BZ0 + BH + 0.05), bevel=0.06, segments=1))
    # chalk tray
    wood.append(ns.box((BW - 0.2, 0.55, 0.12), loc=(0, -0.3, BZ0 + 0.18), bevel=0.03, segments=1))
    wood.append(ns.box((BW - 0.2, 0.06, 0.16), loc=(0, -0.56, BZ0 + 0.28), bevel=0.02, segments=1))
    C.part(wood, "Wood", C.WOOD, "Wood", can_collide=True, smooth_angle=40)
    knobs = [ns.cyl(0.16, 0.12, loc=(sx * (BW / 2 + 0.3), 0, BZ0 + BH - 0.5), rot=(0, 90, 0), verts=8, bevel=0.0)
             for sx in (-1, 1)]

    # chalk drawing: DAILY letters, stars, outline round the screen, a dashed underline
    fy = CHALK_FACE - 0.012
    letters = C.text("DAILY", 0.75, 0.04, (0, fy, BZ0 + BH - 0.82), width=2.8, res=1, spacing=1.12, flat=True)
    stars = [C.prism(star(0.3, 0.13, sx * 1.95, BZ0 + BH - 0.82), "y", fy - 0.02, fy + 0.02) for sx in (-1, 1)]
    outline = C.ring_slab(C.rrect(SCR_W + 0.42, SCR_H + 0.42, 0.18, 2, 0, SCR_Z), C.rrect(SCR_W + 0.3, SCR_H + 0.3, 0.14, 2, 0, SCR_Z),
                          "y", fy - 0.02, fy + 0.02)
    dashes = [ns.box((0.42, 0.04, 0.06), loc=(-1.4 + i * 0.7, fy, BZ0 + BH - 1.3), bevel=0.0) for i in range(5)]
    C.part([letters, outline] + dashes, "ChalkLines", CHALK_WHITE, smooth_angle=None)
    C.part(stars, "ChalkStars", C.MUSTARD, smooth_angle=None)

    # cork strip with 7 calendar day tabs
    cz = SCR_Z + SCR_H / 2 + 0.77
    cork = ns.box((4.6, 0.05, 0.92), loc=(0, CHALK_FACE - 0.02, cz), bevel=0.0)
    C.part([cork], "Cork", C.CORK, "Fabric", smooth_angle=None)
    pages, heads, today, pins = [], [], [], []
    for i in range(7):
        x = -1.92 + i * 0.64
        rot = (0, (-4, 3, -2, 0, 4, -3, 2)[i], 0)
        pg = ns.box((0.52, 0.03, 0.6), loc=(x, CHALK_FACE - 0.065, cz - 0.04), rot=rot, bevel=0.0)
        hd = ns.box((0.52, 0.035, 0.16), loc=(x, CHALK_FACE - 0.075, cz + 0.2), rot=rot, bevel=0.0)
        (today if i == 3 else pages).append(pg)
        heads.append(hd)
        pins.append(ns.sphere(0.06, loc=(x, CHALK_FACE - 0.12, cz + 0.2), segs=6, rings=4))
    C.part(pages, "DayPages", C.PAPER, smooth_angle=None)
    C.part(today, "Today", C.MUSTARD, smooth_angle=None)
    C.part(heads, "DayHeads", C.BRAND, smooth_angle=None)
    C.part(pins + knobs, "Brass", C.BRASS, "Metal", smooth_angle=50)

    # screen
    scr = C.prism(C.rrect(SCR_W, SCR_H, 0.1, 2, 0, SCR_Z), "y", CHALK_FACE - 0.05, CHALK_FACE + 0.02)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)

    # chalk sticks + eraser in the tray
    sticks = []
    for i, (x, col) in enumerate(((-1.6, CHALK_WHITE), (-1.2, CHALK_PINK), (-0.9, C.MUSTARD))):
        sticks.append((C.rod((x - 0.2, -0.3, BZ0 + 0.29), (x + 0.15, -0.36, BZ0 + 0.29), 0.05, verts=6), col))
    for k, (o, col) in enumerate(sticks):
        C.part([o], f"Chalk{k + 1}", col, smooth_angle=50)
    er = ns.box((0.8, 0.3, 0.22), loc=(1.4, -0.3, BZ0 + 0.35), rot=(0, 0, 8), bevel=0.05, segments=1)
    C.part([er], "Eraser", C.WOOD_LIGHT, "Wood", smooth_angle=40)
    felt = ns.box((0.78, 0.28, 0.06), loc=(1.4, -0.3, BZ0 + 0.22), rot=(0, 0, 8), bevel=0.0)
    C.part([felt], "Felt", FELT, "Fabric", smooth_angle=40)

    # bunting along the top rail
    zt = BZ0 + BH + 0.05
    string_pts = C.catenary((-BW / 2 - 0.3, -0.22, zt + 0.17), (BW / 2 + 0.3, -0.22, zt + 0.17), 0.18, n=8)
    string = C.pipe(string_pts, 0.025, sides=4)
    C.part([string], "String", C.CREAM_SHADE, smooth_angle=60)
    flags = {C.BRAND: [], C.MUSTARD: [], C.CYAN: []}
    cols = list(flags)
    for i in range(1, 8):
        p = Vector(string_pts[i])
        flags[cols[i % 3]].append(C.prism([(p.x - 0.26, p.z), (p.x + 0.26, p.z), (p.x, p.z - 0.42)], "y", p.y - 0.02,
                                          p.y + 0.02))
    for col, objs in flags.items():
        C.part(objs, "Flag" + {C.BRAND: "Red", C.MUSTARD: "Mustard", C.CYAN: "Cyan"}[col], col, "Fabric", smooth_angle=None)


def sockets():
    return {"Screen": ((0, CHALK_FACE - 0.05, SCR_Z), 0.0), "Prompt": ((0, -1.8, 3.2), 0.0)}


META = {"screen_size": [SCR_W, SCR_H], "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
        "calendar_tabs": 7, "today_tab": 4, "roles": {"screen": "Screen"}}

if __name__ == "__main__":
    C.run(build, "Lobby_DailyBoard", sockets=sockets(), meta=META)
