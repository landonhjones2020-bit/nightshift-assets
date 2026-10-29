"""fam_meta — meta progression cards (group "meta"): Supply Locker items, Break Room run upgrades,
the six Uniforms and the two uniform Abilities. Shown at 120-200 px on dark cards.

Family look: the "meta" camera (yaw -30, pitch 24); every uniform hangs on the same wooden
hanger with a chrome hook so the six read as one set; supplies and upgrades are chunky props
in the diner palette (the fuse box reuses A_kitchen's breaker panel, the turbo toaster the HUD
toaster).
"""
from __future__ import annotations

import math
import random

import _common as G
from _common import Vector
import fam_hud
import fam_shop

FAM = "meta"


def meta(name, **opts):
    return G.icon(name, "meta", FAM, **opts)


def fc(reveal=14, tilt=6):
    G.face_cam(family=FAM, reveal=reveal, tilt=tilt)


# ---------------------------------------------------------------------------------------------
# supplies
# ---------------------------------------------------------------------------------------------

def battery(loc=(0, 0, 0), rot=(0, 0, 0), s=1.0):
    r, L = 0.34, 1.7
    low = G.lathe([(0.0, 0.0), (r - 0.04, 0.0), (r, 0.04), (r, L * 0.6), (0.0, L * 0.6)], verts=36)
    G.T(low, "#3B4048", name="BattBody", smooth=40)
    top = G.lathe([(0.0, L * 0.6), (r, L * 0.6), (r, L - 0.04), (r - 0.04, L), (0.0, L)], verts=36)
    G.T(top, G.AMBER, name="BattTop", smooth=40)
    nub = G.cyl(0.12, 0.1, loc=(0, 0, L + 0.04), verts=24, bevel=0.03)
    G.T(nub, G.CHROME, "Metal", name="Nub", gloss=0.3)
    plus = [G.puffy(G.rrect(0.07, 0.24, 0.03), 0.04), G.puffy(G.rrect(0.24, 0.07, 0.03), 0.04)]
    G.xform(plus, G.Tm(0, -r - 0.01, L * 0.8))
    bolt = G.puffy(G.fillet([(0.02, 0.18), (0.12, 0.18), (0.04, 0.04), (0.12, 0.04), (-0.06, -0.18), (-0.01, -0.03), (-0.1, -0.03)], 0.01, 1), 0.04)
    G.xform(bolt, G.Tm(0, -r - 0.01, L * 0.3))
    G.T(plus, G.INK_SOFT, name="PlusMark")
    G.T(bolt, G.AMBER, name="BattBolt")
    objs = [low, top, nub, bolt] + plus
    G.xform(objs, G.Tm(*loc) @ G.R(*rot) @ G.S(s))
    return objs


@meta("Supply_spare_batteries")
def spare_batteries():
    battery(loc=(-0.42, 0.0, 0.0), rot=(0, 0, 0))
    battery(loc=(0.42, -0.15, 0.0), rot=(0, 14, 0))
    G.xform(G.tagged(), G.R(rz=-14))


@meta("Supply_energy_drink")
def energy_drink():
    prof = [(0.0, 0.0), (0.5, 0.0), (0.58, 0.08), (0.62, 0.2), (0.62, 1.78), (0.56, 1.95), (0.46, 2.04), (0.0, 2.04)]
    can = G.lathe(prof, verts=48)
    G.T(can, G.GREEN, name="Can", smooth=45)
    top = G.lathe([(0.0, 2.02), (0.44, 2.02), (0.47, 2.08), (0.43, 2.1), (0.0, 2.06)], verts=48)
    bot = G.lathe([(0.0, -0.01), (0.5, -0.01), (0.58, 0.08), (0.5, 0.06), (0.0, 0.03)], verts=48)
    tab = G.slab_xy(G.fillet([(-0.1, -0.22), (0.1, -0.22), (0.12, 0.1), (-0.12, 0.1)], 0.05, 3), 0.025, bevel=0.01, z=2.08)
    G.xform(tab, G.Tm(0.0, -0.05, 0))
    G.T([top, bot, tab], G.CHROME, "Metal", name="CanTop", gloss=0.3)
    band = G.lathe([(0.625, 1.25), (0.635, 1.25), (0.635, 1.6), (0.625, 1.6)], verts=48)
    G.T(band, G.INK_SOFT, name="Band")
    bolt = G.puffy(G.fillet([(0.04, 0.55), (0.34, 0.55), (0.1, 0.12), (0.34, 0.12), (-0.18, -0.55), (-0.04, -0.06), (-0.3, -0.06)], 0.03, 2), 0.12)
    G.xform(bolt, G.Tm(0.0, -0.6, 0.72))
    G.T(bolt, G.INK_SOFT, name="CanBolt")
    stripe = G.lathe([(0.626, 0.32), (0.636, 0.32), (0.636, 0.4), (0.626, 0.4)], verts=48)
    G.T(stripe, G.INK_SOFT, name="Stripe")
    G.xform(G.tagged(), G.R(rz=-8) @ G.R(ry=-6))


def napkin(col=G.PAPER):
    out = []
    n = 6
    for side in range(4):
        a0 = [(-1, -1), (1, -1), (1, 1), (-1, 1)][side]
        a1 = [(-1, -1), (1, -1), (1, 1), (-1, 1)][(side + 1) % 4]
        for i in range(n):
            t = i / n
            x = a0[0] + (a1[0] - a0[0]) * t
            z = a0[1] + (a1[1] - a0[1]) * t
            # gentle scallops along every edge
            if i % 2 == 1:
                dx, dz = (a1[1] - a0[1]) * 0.03, -(a1[0] - a0[0]) * 0.03
                x, z = x + dx, z + dz
            out.append((x, z))
    pts = [(x * 0.95, z * 0.95) for x, z in out]
    nap = G.slab(pts, 0.06, bevel=0.02)
    G.T(nap, col, name="Napkin")
    emb = G.slab(G.rrect(1.56, 1.56, 0.1), 0.02, y=-0.035)
    G.boolean(emb, G.slab(G.rrect(1.48, 1.48, 0.08), 0.2, y=-0.035))
    G.T(emb, "#E2DAC8", name="Emboss")
    fold = G.slab([(0.95, -0.95), (0.95, -0.35), (0.35, -0.95)], 0.04, bevel=0.01, y=-0.06)
    G.T(fold, "#E2DAC8", name="Fold")
    return [nap, emb, fold]


@meta("Supply_lucky_clue")
def lucky_clue():
    napkin()
    # "X marks the spot": a dashed trail from the corner to a loose hand-drawn ring around an X
    loop = [(0.18 + 0.6 * math.cos(math.radians(a)) * (1 + 0.04 * math.sin(math.radians(3 * a))),
             0.22 + 0.5 * math.sin(math.radians(a))) for a in range(100, 480, 10)]
    ring = G.puffy(G.stroke(loop, 0.065), 0.05, y=-0.06)
    xs = [G.puffy(G.stroke([(0.0, 0.02), (0.36, 0.42)], 0.15), 0.06, y=-0.065),
          G.puffy(G.stroke([(0.0, 0.42), (0.36, 0.02)], 0.15), 0.06, y=-0.065)]
    dashes = []
    trail = G.smooth_path([(-0.78, -0.75), (-0.62, -0.25), (-0.35, -0.38), (-0.22, -0.08)], 6)
    for i in range(0, len(trail) - 1, 3):
        dashes.append(G.puffy(G.stroke([trail[i], trail[min(i + 1, len(trail) - 1)]], 0.07), 0.04, y=-0.06))
    G.T([ring] + xs + dashes, G.RED, name="Ink")
    G.xform(G.tagged(), G.R(ry=-10))
    fc(16, 30)


@meta("Supply_recipe_card")
def recipe_card():
    card = G.slab(G.rrect(2.2, 1.4, 0.06), 0.05, bevel=0.015)
    G.T(card, G.PAPER, name="Card")
    top = G.slab(G.rrect(2.1, 0.04, 0.02, cz=0.42), 0.02, y=-0.03)
    G.T(top, "#E8423A", name="TopLine")
    lines = [G.slab(G.rrect(2.1, 0.025, 0.01, cz=z), 0.02, y=-0.03) for z in (0.2, 0.0, -0.2, -0.4)]
    G.T(lines, "#7FB8E8", name="Rule")
    # sandwich doodle on the right, title scribble on the left
    yd = -0.045
    bun = G.puffy(G.arc(0.36, 0, 180, 14, 0.52, 0.05) + [(0.16, 0.05)], 0.03, y=yd)
    G.T(bun, "#E09A3A", name="DoodleBun")
    let = G.puffy(G.stroke([(0.1 + 0.84 * i / 12, -0.04 + 0.04 * math.sin(i * 1.5)) for i in range(13)], 0.07), 0.03, y=yd)
    G.T(let, "#4FC04A", name="DoodleLettuce")
    tom = G.puffy(G.rrect(0.74, 0.07, 0.03, cx=0.52, cz=-0.14), 0.03, y=yd)
    G.T(tom, "#E8423A", name="DoodleTomato")
    base = G.puffy(G.rrect(0.76, 0.12, 0.05, cx=0.52, cz=-0.27), 0.03, y=yd)
    G.T(base, "#E09A3A", name="DoodleBun")
    title = [G.puffy(G.stroke([(-0.95, z), (-0.95 + w, z)], 0.06), 0.03, y=yd) for z, w in ((0.3, 0.9), (0.1, 0.62), (-0.1, 0.78), (-0.3, 0.5))]
    G.T(title, "#3A3F4A", name="Writing")
    G.xform(G.tagged(), G.R(ry=-8))
    fc(14, 26)


@meta("Supply_second_shift_ticket")
def second_shift_ticket():
    holes = [G.circle(0.07, 14, 0.42, z) for z in (0.35, -0.05)]
    card = G.slab_holes(G.rrect(1.15, 2.1, 0.08), holes, 0.05, bevel=0.015)
    G.T(card, "#F2DFA8", name="Ticket")
    head = G.slab(G.rrect(1.15, 0.5, 0.08, cz=0.8), 0.06, bevel=0.015)
    G.T(head, "#E8423A", name="Header")
    t = G.text("2ND", 0.3, 0.04, loc=(0, -0.04, 0.8))
    G.T(t, G.PAPER, name="HeaderText")
    rows = [G.slab(G.rrect(0.62, 0.05, 0.02, cx=-0.14, cz=z), 0.02, y=-0.03) for z in (0.35, 0.15, -0.05, -0.25)]
    G.T(rows, "#9C8A5E", name="Row")
    stamp = G.puffy(G.heart(0.26, 40, cx=0.0, cz=-0.68), 0.04, y=-0.035)
    G.T(stamp, G.PINK, name="Stamp")
    ring = G.puffy_holes(G.circle(0.38, 32, 0.0, -0.66), [G.circle(0.32, 32, 0.0, -0.66)], 0.04, y=-0.035)
    G.T(ring, G.PINK, name="StampRing")
    G.xform(G.tagged(), G.R(ry=-10))
    fc(14, 8)


# ---------------------------------------------------------------------------------------------
# run upgrades (Break Room)
# ---------------------------------------------------------------------------------------------

def flame(h=1.0, w=0.5):
    pts = G.smooth_path([(0.0, h), (w * 0.35, h * 0.55), (w * 0.62, h * 0.2), (w * 0.5, 0.0), (0.0, -0.08 * h), (-w * 0.5, 0.0),
                         (-w * 0.62, h * 0.22), (-w * 0.2, h * 0.5), (-w * 0.05, h * 0.62)], 4, closed=True)
    return pts


@meta("Upgrade_toaster_turbo")
def toaster_turbo():
    fam_hud.toaster()
    fl = []
    for x, h, w, col, y in ((-0.45, 1.0, 0.55, "#FF6A1E", 0.42), (0.15, 1.25, 0.62, "#FF6A1E", 0.42), (0.68, 0.9, 0.5, "#FF6A1E", 0.42),
                            (-0.45, 0.62, 0.32, "#FFD23A", 0.34), (0.15, 0.8, 0.36, "#FFD23A", 0.34), (0.68, 0.55, 0.3, "#FFD23A", 0.34)):
        o = G.puffy(flame(h, w), 0.16, puff=0.42)
        G.xform(o, G.Tm(x, y, 1.0))
        G.neon(o, col, 1.6 if col == "#FF6A1E" else 2.5, name="Flame")
        fl.append(o)
    streaks = [G.puffy(G.stroke([(-1.0 - L, z), (-0.95, z)], 0.1), 0.1) for L, z in ((0.55, 0.85), (0.8, 0.55), (0.45, 0.25))]
    G.xform(streaks, G.Tm(0, -0.2, 0.0))
    G.T(streaks, G.CYAN, name="Streak")
    G.xform(fl + streaks, G.R(rz=-6))


def mini_crate(col, trim, loc, s=0.42):
    b = G.box((2.0, 1.4, 1.0), bevel=0.0)
    G.boolean(b, G.box((1.8, 1.2, 1.0), loc=(0, 0, 0.1), bevel=0.0))
    G.boolean(b, G.box((2.4, 0.55, 0.2), loc=(0, 0, 0.25), bevel=0.0))
    G._bevel(b, 0.03, 2)
    G.T(b, col, name="Crate")
    rim = G.box((2.06, 1.46, 0.12), loc=(0, 0, 0.47), bevel=0.04)
    G.boolean(rim, G.box((1.8, 1.2, 0.5), loc=(0, 0, 0.47), bevel=0.0))
    G.T(rim, trim, name="CrateRim")
    label = G.box((0.95, 0.03, 0.26), loc=(0, -0.71, 0.2), bevel=0.01, segs=1)
    G.T(label, G.PAPER, name="CrateLabel")
    objs = [b, rim, label]
    G.xform(objs, G.Tm(*loc) @ G.S(s) @ G.Tm(0, 0, 0.5))
    return objs


@meta("Upgrade_stock_shelf")
def stock_shelf():
    W, D = 2.4, 0.8
    posts = [G.box((0.1, 0.1, 2.3), loc=(sx * (W / 2 - 0.05), sy * (D / 2 - 0.05), 1.15), bevel=0.03) for sx in (-1, 1) for sy in (-1, 1)]
    shelves = [G.box((W, D, 0.08), loc=(0, 0, z), bevel=0.03) for z in (0.25, 1.2, 2.18)]
    lips = [G.box((W, 0.05, 0.14), loc=(0, -D / 2, z + 0.05), bevel=0.02, segs=1) for z in (0.25, 1.2, 2.18)]
    G.T(posts + shelves + lips, G.STEEL, "Metal", name="Shelf", gloss=0.4)
    for col, trim, x in (("#B33A3A", "#7E2525", -0.62), ("#F2C53D", "#B89220", 0.4)):
        mini_crate(col, trim, (x, 0.0, 1.24), s=0.44)
    mini_crate("#4FA04A", "#3B7D37", (-0.55, 0.0, 0.29), s=0.44)
    # jars and cans on the bottom shelf
    jars = []
    for k, (x, col) in enumerate(((0.3, "#E26A2C"), (0.68, "#C69C6D"), (1.0, "#E8423A"))):
        j = G.cyl(0.16, 0.42, loc=(x, -0.05, 0.5), verts=24, bevel=0.04)
        jars.append(j)
        G.T(j, col, name="Jar")
        lid = G.cyl(0.165, 0.08, loc=(x, -0.05, 0.75), verts=24, bevel=0.025)
        G.T(lid, G.CHROME, "Metal", name="JarLid", gloss=0.3)
    # bottles on the top shelf
    FC = G.batch_common("A_food")
    for x, body, cap in ((-0.7, "#F7C21A", "#E8502A"), (-0.35, "#D92B2B", "#F3EEE2")):
        before = set(G.tagged())
        FC.squeeze_bottle(body, cap, label_col=G.PAPER, suffix=f"_{x}")
        new = [o for o in G.tagged() if o not in before]
        G.xform(new, G.Tm(x, 0.0, 2.22) @ G.S(0.62))
    box_ = G.box((0.7, 0.5, 0.42), loc=(0.55, 0.0, 2.43), bevel=0.04)
    G.T(box_, G.KRAFT, name="Box")
    G.xform(G.tagged(), G.R(rz=4))


@meta("Upgrade_batteries")
def batteries_pack():
    body = G.box((2.0, 0.9, 1.3), loc=(0, 0, 0.65), bevel=0.16, segs=4)
    G.T(body, "#3B4048", name="Pack")
    top = G.box((2.04, 0.94, 0.3), loc=(0, 0, 1.18), bevel=0.12, segs=3)
    G.T(top, G.AMBER, name="PackTop")
    terms = [G.cyl(0.13, 0.18, loc=(x, 0.0, 1.38), verts=20, bevel=0.04) for x in (-0.55, 0.55)]
    G.T(terms, G.CHROME, "Metal", name="Terminal", gloss=0.3)
    marks = [G.puffy(G.rrect(0.07, 0.22, 0.03), 0.04), G.puffy(G.rrect(0.22, 0.07, 0.03), 0.04), G.puffy(G.rrect(0.22, 0.07, 0.03), 0.04)]
    G.xform(marks[:2], G.Tm(-0.55, -0.48, 1.18))
    G.xform(marks[2:], G.Tm(0.55, -0.48, 1.18))
    G.T(marks, G.INK_SOFT, name="Sign")
    win = G.slab(G.rrect(1.6, 0.56, 0.1), 0.06, bevel=0.02, y=-0.45)
    G.xform(win, G.Tm(0, 0, 0.5))
    G.T(win, "#15171C", name="Meter")
    bars = []
    for k in range(4):
        b = G.slab(G.rrect(0.32, 0.38, 0.06, cx=-0.57 + 0.38 * k, cz=0.5), 0.06, bevel=0.015, y=-0.48)
        bars.append(b)
        if k < 3:
            G.neon(b, G.GREEN, 2.2, name="Charge")
        else:
            G.T(b, "#2C3038", name="Empty")
    bolt = G.puffy(G.fillet([(0.04, 0.5), (0.3, 0.5), (0.1, 0.12), (0.3, 0.12), (-0.16, -0.5), (-0.04, -0.08), (-0.26, -0.08)], 0.03, 2), 0.18)
    G.xform(bolt, G.Tm(0.95, -0.55, 1.45) @ G.R(ry=10))
    G.T(bolt, G.GOLD, name="Bolt")
    G.xform(G.tagged(), G.R(rz=-10))


@meta("Upgrade_space_heater")
def space_heater():
    dish = G.lathe([(0.0, 0.0), (0.4, 0.02), (0.75, 0.12), (1.0, 0.32), (1.08, 0.45), (1.0, 0.45), (0.92, 0.36), (0.68, 0.18), (0.36, 0.08), (0.0, 0.06)], verts=48)
    G.T(dish, "#DCE2E7", "Metal", name="Dish", gloss=0.25)
    # glowing coil element (a spiral) at the centre of the reflector
    pts = []
    for i in range(90):
        t = i / 89
        a = t * 2 * math.pi * 6
        pts.append((0.12 * math.cos(a), 0.12 * math.sin(a), 0.12 + t * 0.55))
    coil = G.tube(pts, 0.035, sides=6, res=1)
    G.neon(coil, "#FF7A1E", 4.5, name="Coil")
    core = G.cyl(0.07, 0.6, loc=(0, 0, 0.4), verts=12, bevel=0.0)
    G.T(core, "#F4E2C8", name="Core")
    glow = G.glow_mat(G.sphere(0.6, loc=(0, 0, 0.35), segs=24, rings=12), "#FF8A2A", 2.5, 0.55, falloff=1.5)
    guards = [G.torus(r, 0.022, loc=(0, 0, 0.5 + 0.06 * (1.05 - r)), segs=48, rsegs=6) for r in (0.35, 0.7, 1.04)]
    spokes = []
    for k in range(6):
        a = 2 * math.pi * k / 6
        spokes.append(G.tube([(0.0, 0.0, 0.85), (0.5 * math.cos(a), 0.5 * math.sin(a), 0.72), (1.04 * math.cos(a), 1.04 * math.sin(a), 0.48)], 0.02, sides=6, res=2))
    hub = G.sphere(0.07, loc=(0, 0, 0.86))
    G.T(guards + spokes + [hub], G.CHROME, "Metal", name="Guard", gloss=0.3)
    objs = [dish, coil, core, glow] + guards + spokes + [hub]
    G.xform(objs, G.Tm(0, 0, 1.55) @ G.R(rx=78))
    yoke = G.tube([(-1.1, 0.12, 1.55), (-1.15, 0.2, 1.0), (0.0, 0.25, 0.75), (1.15, 0.2, 1.0), (1.1, 0.12, 1.55)], 0.06, sides=10, res=4)
    stem = G.rod((0, 0.25, 0.75), (0, 0.25, 0.2), 0.08, verts=14)
    base = G.cyl(0.75, 0.2, loc=(0, 0.25, 0.1), verts=40, bevel=0.07, r_top=0.6)
    G.T([yoke, stem], G.CHROME, "Metal", name="Stand", gloss=0.3)
    G.T(base, G.VINYL_RED, name="Base")
    knob = G.cyl(0.12, 0.08, loc=(0.0, -0.4, 0.14), rot=(90, 0, 0), verts=16, bevel=0.03)
    G.T(knob, G.PAPER, name="Knob")
    G.xform(G.tagged(), G.R(rz=-6))


@meta("Upgrade_fuse_box")
def fuse_box():
    _, objs = G.build_foreign("A_kitchen", "Kitchen_BreakerBox")
    # mirrored so the big red main lever is on the camera's side, turned toward the camera
    G.xform(objs, G.R(rz=-24) @ G.S((-1, 1, 1)))


@meta("Upgrade_second_station")
def second_station():
    board = G.slab_xy(G.fillet([(-1.25, -0.75), (1.0, -0.75), (1.0, -0.25), (1.45, -0.18), (1.45, 0.18), (1.0, 0.25), (1.0, 0.75), (-1.25, 0.75)], 0.12, 4),
                      0.16, bevel=0.05, segs=3)
    G.boolean(board, G.cyl(0.09, 1.0, loc=(1.3, 0.0, 0.0), verts=16, bevel=0))
    G._bevel(board, 0.02, 2)
    G.T(board, G.WOOD, name="Board")
    grain = [G.box((1.9, 0.02, 0.01), loc=(-0.15, y, 0.165), bevel=0.0) for y in (-0.45, -0.1, 0.32)]
    G.T(grain, G.WOOD_D, name="Grain")
    blade = G.slab_xy(G.fillet([(-0.9, -0.12), (0.25, -0.12), (0.25, 0.14), (-0.55, 0.12), (-0.95, -0.02)], 0.03, 2), 0.04, bevel=0.012, z=0.17)
    G.T(blade, "#D6DCE2", "Metal", name="Knife", gloss=0.3)
    handle = G.box((0.62, 0.2, 0.14), loc=(0.6, 0.01, 0.25), bevel=0.06, segs=3)
    G.T(handle, G.INK_SOFT, name="KnifeHandle")
    rivets = [G.cyl(0.03, 0.15, loc=(x, 0.01, 0.25), verts=10, bevel=0.0) for x in (0.45, 0.72)]
    G.T(rivets, G.CHROME, "Metal", name="Rivet", gloss=0.3)
    knife = [blade, handle] + rivets
    G.xform(knife, G.Tm(-0.05, 0.25, 0.0) @ G.R(rz=-18))
    for k, (x, y) in enumerate(((-0.75, -0.35), (-0.38, -0.42), (-0.02, -0.38))):
        t = G.cyl(0.24, 0.07, loc=(x, y, 0.2 + 0.01 * k), verts=28, bevel=0.02)
        G.T(t, "#E8423A", name="Tomato")
        inner = G.cyl(0.18, 0.02, loc=(x, y, 0.24 + 0.01 * k), verts=24, bevel=0.0)
        G.T(inner, "#FF7B6E", name="TomatoFlesh")
    G.xform(G.tagged(), G.R(rx=30) @ G.R(rz=-4))
    b = fam_shop.badge("2", col=G.AMBER, loc=(0, 0, 0), r=0.42, size=0.6)
    G.xform(b, G.Tm(1.2, -0.75, 0.55) @ G.R(rz=-26) @ G.R(rx=-10))


@meta("Upgrade_radio_tuner")
def radio_tuner():
    body = G.box((2.2, 0.9, 1.35), loc=(0, 0, 0.68), bevel=0.32, segs=6)
    G.T(body, G.CREAM, name="Radio")
    front = G.slab(G.rrect(1.95, 1.08, 0.24), 0.06, bevel=0.02, y=-0.45)
    G.xform(front, G.Tm(0, 0, 0.68))
    G.T(front, G.VINYL_RED, name="Front")
    grille = G.slab(G.circle(0.42, 40, -0.42, 0.66), 0.05, bevel=0.015, y=-0.49)
    G.T(grille, "#F3D9A4", name="Grille")
    slots = [G.slab(G.rrect(0.62, 0.05, 0.025, cx=-0.42, cz=0.66 + dz), 0.02, y=-0.52) for dz in (-0.24, -0.12, 0.0, 0.12, 0.24)]
    G.T(slots, "#7A5233", name="Slot")
    dial = G.slab(G.rrect(0.7, 0.34, 0.08, cx=0.48, cz=0.86), 0.05, bevel=0.015, y=-0.5)
    G.neon(dial, "#FFC24A", 1.8, name="Dial")
    ticks = [G.slab(G.rrect(0.02, 0.1, 0.01, cx=0.2 + 0.08 * k, cz=0.9), 0.02, y=-0.53) for k in range(8)]
    needle = G.slab(G.rrect(0.03, 0.26, 0.01, cx=0.55, cz=0.86), 0.02, y=-0.535)
    G.T(ticks, "#7A5233", name="Tick")
    G.T(needle, G.RED, name="Needle")
    knobs = [G.cyl(0.16, 0.14, loc=(x, -0.52, 0.42), rot=(90, 0, 0), verts=24, bevel=0.04) for x in (0.28, 0.7)]
    G.T(knobs, G.CREAM, name="Knob")
    feet = [G.box((0.3, 0.6, 0.1), loc=(x, 0, 0.0), bevel=0.04) for x in (-0.7, 0.7)]
    G.T(feet, G.INK_SOFT, name="Feet")
    ant = G.rod((0.75, 0.15, 1.3), (1.45, 0.25, 2.55), 0.035, verts=10)
    ant2 = G.rod((0.75, 0.15, 1.3), (1.0, 0.2, 1.75), 0.055, verts=10)
    tip = G.sphere(0.07, loc=(1.45, 0.25, 2.57))
    G.T([ant, ant2, tip], G.CHROME, "Metal", name="Antenna", gloss=0.3)
    waves = [G.puffy(G.stroke(G.arc(r, 20, 100, 10, 1.45, 2.57), 0.07), 0.06) for r in (0.25, 0.45)]
    G.T(waves, G.CYAN, name="Wave")
    G.xform(G.tagged(), G.R(rz=-8))


def clover(cx=0.0, cz=0.0, s=1.0):
    leaves = []
    veins = []
    for k in range(4):
        a = 45 + 90 * k
        h = G.puffy(G.heart(0.3 * s, 40), 0.09, puff=0.4)
        M = G.Tm(cx, 0, cz) @ G.R(ry=90 - a) @ G.Tm(0, 0, 0.34 * s)
        G.xform(h, M)
        leaves.append(h)
        v = G.puffy(G.stroke([(0.0, 0.2 * s), (0.0, -0.12 * s)], 0.04 * s), 0.03, y=-0.05)
        G.xform(v, M)
        veins.append(v)
    G.T(leaves, "#4CD964", name="Clover")
    G.T(veins, "#A6F0B4", name="CloverVein")
    stem = G.puffy(G.stroke(G.smooth_path([(cx, cz), (cx + 0.12 * s, cz - 0.42 * s), (cx + 0.32 * s, cz - 0.72 * s)], 4), 0.08 * s), 0.07)
    G.T(stem, "#2F9A3A", name="CloverStem")
    return leaves + veins + [stem]


@meta("Upgrade_lucky_napkin")
def lucky_napkin():
    napkin()
    cl = clover(0.0, 0.16, 1.15)
    G.xform(cl, G.Tm(0, -0.06, 0))
    G.xform(G.tagged(), G.R(ry=-10))
    fc(16, 30)


# ---------------------------------------------------------------------------------------------
# uniforms: one shirt/jacket per role on the shared hanger
# ---------------------------------------------------------------------------------------------

def shirt(body, collar=None, cuffs=None, collar_kind="point", depth=0.34, placket=True, buttons=G.PAPER, sleeve=1.05):
    s = G.puffy(fam_hud.shirt_outline(sleeve=sleeve), depth, puff=0.4)
    G.T(s, body, name="Shirt")
    yf = -depth / 2
    if collar_kind == "point":
        col = [G.puffy([(0.0, 0.36), (k * 0.24, 0.73), (k * 0.34, 0.5), (k * 0.06, 0.24)][::k], 0.07, y=yf - 0.03) for k in (1, -1)]
        G.T(col, collar or body, name="Collar")
    elif collar_kind == "band":
        col = G.puffy(G.stroke(G.arc(0.26, 200, 340, 12, 0.0, 0.72), 0.12), depth * 0.9, puff=0.4)
        G.T(col, collar or body, name="Collar")
    if cuffs:
        cs = []
        for k in (1, -1):
            a, b = Vector((k * sleeve, 0.28)), Vector((k * (sleeve - 0.2), 0.0))
            d = Vector((-k * 0.45, 0.32)).normalized() * 0.18
            quad = [tuple(a), tuple(b), tuple(b + d), tuple(a + d)]
            cs.append(G.puffy(quad if k > 0 else quad[::-1], depth + 0.02, puff=0.3))
        G.T(cs, cuffs, name="Cuff")
    if placket and buttons:
        bs = [G.cyl(0.05, 0.05, loc=(0, yf - 0.03, z), rot=(90, 0, 0), verts=16, bevel=0.015) for z in (0.06, -0.3, -0.66)]
        G.T(bs, buttons, name="Button")
    fam_hud.hanger_hook()
    return s


def uniform(name):
    return meta(f"Uniform_{name}")


@uniform("trainee")
def u_trainee():
    shirt("#C9D3DE", collar="#E9EEF3", cuffs=None, buttons="#F4F6F8")
    pin = G.puffy(G.rrect(0.52, 0.2, 0.06, cx=-0.3, cz=0.0), 0.08, y=-0.2)
    G.T(pin, G.AMBER, name="Pin")
    t = G.text("TRAINEE", 0.1, 0.03, loc=(-0.3, -0.25, 0.0))
    G.fit_width(t, 0.42)
    G.T(t, G.INK_SOFT, name="PinText")
    fc()


@uniform("line_cook")
def u_line_cook():
    shirt(G.PAPER, collar=G.PAPER, cuffs=G.INK_SOFT, collar_kind="band", buttons=None)
    piping = G.puffy(G.stroke([(0.1, 0.5), (0.18, -0.95)], 0.05), 0.04, y=-0.18)
    G.T(piping, G.INK_SOFT, name="Piping")
    bs = [G.cyl(0.05, 0.05, loc=(0.28, -0.2, z), rot=(90, 0, 0), verts=16, bevel=0.015) for z in (0.3, -0.05, -0.4, -0.75)]
    G.T(bs, G.INK_SOFT, name="Button")
    # red bandana knotted at the collar
    band = G.puffy(G.stroke(G.arc(0.3, 200, 340, 12, 0.0, 0.78), 0.12), 0.42, puff=0.4)
    tri = G.puffy(G.fillet([(-0.42, 0.62), (0.42, 0.62), (0.04, 0.02)], 0.06, 2), 0.12, y=-0.22)
    knot = G.sphere(0.11, loc=(0.3, -0.27, 0.6))
    tails = [G.puffy(G.fillet([(0.3, 0.6), (0.62, 0.38), (0.5, 0.3)], 0.03, 1), 0.07, y=-0.27),
             G.puffy(G.fillet([(0.3, 0.6), (0.5, 0.2), (0.36, 0.2)], 0.03, 1), 0.07, y=-0.28)]
    G.T([band, tri, knot] + tails, G.RED, name="Bandana")
    dots = [G.sphere(0.035, loc=(x, -0.3, z)) for x, z in ((-0.18, 0.5), (0.12, 0.48), (0.0, 0.3), (-0.06, 0.54), (0.04, 0.16))]
    G.T(dots, G.PAPER, name="BandanaDot")
    fc()


@uniform("stock_runner")
def u_stock_runner():
    shirt("#4A4F56", collar=None, collar_kind=None, buttons=None)
    vest = [(0.0, 0.1), (0.2, 0.7), (0.5, 0.64), (0.56, 0.12), (0.62, -0.92), (0.06, -0.96)]
    for k in (1, -1):
        v = G.puffy([(k * x, z) for x, z in (vest if k > 0 else vest[::-1])], 0.42, puff=0.35)
        G.T(v, "#D8FF2E", name="Vest")
    bands = []
    for z in (-0.32, -0.62):
        for k in (1, -1):
            pts = [(k * 0.08, z - 0.06), (k * 0.62, z - 0.06), (k * 0.62, z + 0.06), (k * 0.08, z + 0.06)]
            bands.append(G.puffy(pts if k > 0 else pts[::-1], 0.46, puff=0.3))
    for k in (1, -1):
        pts = [(k * 0.28, 0.6), (k * 0.4, 0.6), (k * 0.4, -0.25), (k * 0.28, -0.25)]
        bands.append(G.puffy(pts if k < 0 else pts[::-1], 0.45, puff=0.3))
    G.T(bands, "#E6EBEF", name="Reflective")
    zipper = G.puffy(G.rrect(0.05, 1.0, 0.02, cz=-0.4), 0.43)
    G.T(zipper, G.INK_SOFT, name="Zip")
    fc()


@uniform("security_guard")
def u_security():
    NAVY = "#2E4482"
    shirt(NAVY, collar="#24376B", cuffs="#24376B", buttons="#C9D0D8")
    eps = [G.puffy(G.fillet([(k * 0.22, 0.74), (k * 0.6, 0.64), (k * 0.62, 0.54), (k * 0.24, 0.62)][::k], 0.03, 1), 0.38, puff=0.3) for k in (1, -1)]
    G.T(eps, "#1E2C55", name="Epaulette")
    eb = [G.sphere(0.04, loc=(k * 0.5, -0.2, 0.62)) for k in (1, -1)]
    G.T(eb, G.GOLD, name="EpButton")
    pockets = [G.puffy(G.rrect(0.34, 0.12, 0.04, cx=k * 0.33, cz=0.05), 0.06, y=-0.18) for k in (1, -1)]
    G.T(pockets, "#24376B", name="Flap")
    shield = G.puffy(G.smooth_path([(-0.18, 0.2), (0.0, 0.26), (0.18, 0.2), (0.17, 0.0), (0.0, -0.2), (-0.17, 0.0)], 3, closed=True), 0.08, y=-0.21)
    G.xform(shield, G.Tm(0.33, 0, 0.26))
    G.T(shield, G.GOLD, "Metal", name="Badge", gloss=0.3)
    st = G.puffy(G.fillet(G.star(5, 0.08, 0.035, cx=0.33, cz=0.28), 0.005, 1), 0.04, y=-0.25)
    G.T(st, "#B58A1E", name="BadgeStar")
    # flashlight loop at the hem with a mini work flashlight in it
    loop = G.puffy(G.rrect(0.14, 0.34, 0.05, cx=-0.42, cz=-0.82), 0.06, y=-0.2)
    G.T(loop, G.INK_SOFT, name="Loop")
    fl = G.lathe([(0.0, -0.32), (0.07, -0.32), (0.07, 0.12), (0.11, 0.2), (0.11, 0.3), (0.0, 0.3)], verts=20)
    G.xform(fl, G.Tm(-0.42, -0.27, -0.85) @ G.R(ry=8))
    G.T(fl, G.MUSTARD, name="MiniLight")
    lens = G.cyl(0.09, 0.02, loc=(-0.42, -0.27, -0.55), verts=16, bevel=0)
    G.xform(lens, G.R(ry=8, about=(-0.42, -0.27, -0.85)))
    G.neon(lens, "#FFF1C4", 3.0, name="MiniLens")
    fc()


@uniform("night_manager")
def u_night_manager():
    shirt("#CFE4F7", collar=G.PAPER, cuffs=None, buttons=None)
    tie = G.puffy(G.fillet([(0.0, 0.42), (0.14, 0.3), (0.1, 0.22), (0.2, -0.55), (0.0, -0.75), (-0.2, -0.55), (-0.1, 0.22), (-0.14, 0.3)], 0.03, 2),
                  0.1, y=-0.21)
    knot = G.puffy(G.fillet([(-0.12, 0.5), (0.12, 0.5), (0.08, 0.32), (-0.08, 0.32)], 0.03, 2), 0.13, y=-0.22)
    G.T([tie, knot], G.VINYL_RED, name="Tie")
    stripes = [G.puffy(G.stroke([(-0.15, z), (0.15, z + 0.12)], 0.035), 0.03, y=-0.27) for z in (0.0, -0.22, -0.44)]
    G.T(stripes, "#E8B23A", name="TieStripe")
    tag = G.puffy(G.rrect(0.42, 0.18, 0.05, cx=-0.36, cz=0.08), 0.07, y=-0.2)
    G.T(tag, G.GOLD, "Metal", name="Badge", gloss=0.3)
    st = G.puffy(G.fillet(G.star(5, 0.06, 0.025, cx=-0.5, cz=0.08), 0.005, 1), 0.04, y=-0.24)
    line = G.puffy(G.rrect(0.18, 0.03, 0.01, cx=-0.31, cz=0.08), 0.03, y=-0.24)
    G.T([st, line], G.INK_SOFT, name="BadgeMark")
    pen = G.rod((0.36, -0.2, 0.2), (0.36, -0.2, -0.05), 0.03, verts=8)
    G.T(pen, G.BLUE, name="Pen")
    pocket = G.puffy(G.rrect(0.3, 0.28, 0.04, cx=0.36, cz=-0.06), 0.04, y=-0.18)
    G.T(pocket, "#B9D3EC", name="Pocket")
    fc()


def toque(loc=(0, 0, 0), s=1.0):
    band = G.cyl(0.4, 0.34, loc=(0, 0, 0.17), verts=40, bevel=0.06)
    G.T(band, G.PAPER, name="ToqueBand")
    body = G.lathe([(0.0, 0.3), (0.4, 0.3), (0.44, 0.8), (0.5, 1.22), (0.56, 1.38), (0.52, 1.56), (0.36, 1.68), (0.0, 1.7)], verts=48)
    for v in body.data.vertices:
        a = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.07 * math.cos(12 * a) * min(1.0, max(0.0, (v.co.z - 0.35) / 0.4))
        v.co.x *= k
        v.co.y *= k
    G.T(body, "#F7F4EC", name="ToquePuff", smooth=70)
    objs = [band, body]
    G.xform(objs, G.Tm(*loc) @ G.S(s))
    return objs


@uniform("head_chef")
def u_head_chef():
    shirt(G.PAPER, collar=G.PAPER, cuffs=G.PAPER, collar_kind="band", buttons=None)
    flap = G.puffy(G.fillet([(-0.5, 0.5), (0.0, 0.62), (0.52, 0.48), (0.56, -0.96), (-0.1, -0.98)], 0.06, 2), 0.06, y=-0.19)
    G.T(flap, "#F7F4EC", name="Breast")
    bs = [G.cyl(0.055, 0.05, loc=(x, -0.24, z), rot=(90, 0, 0), verts=16, bevel=0.015) for x in (-0.22, 0.3) for z in (0.3, -0.05, -0.4, -0.75)]
    G.T(bs, G.INK_SOFT, name="Button")
    trim = G.puffy(G.stroke(G.arc(0.26, 200, 340, 12, 0.0, 0.72), 0.04), 0.4)
    G.xform(trim, G.Tm(0, -0.02, -0.03))
    G.T(trim, G.RED, name="CollarTrim")
    toque(loc=(1.12, 0.1, -0.98), s=0.82)
    fc()


# ---------------------------------------------------------------------------------------------
# abilities
# ---------------------------------------------------------------------------------------------

@meta("Ability_ClosingTime")
def closing_time():
    rim = G.cyl(1.0, 0.3, rot=(90, 0, 0), verts=64, bevel=0.1, segs=3)
    G.T(rim, G.VINYL_RED, name="ClockRim")
    face = G.cyl(0.84, 0.05, loc=(0, -0.16, 0), rot=(90, 0, 0), verts=64, bevel=0.015)
    G.T(face, G.PAPER, name="Face")
    chrome = G.torus(0.88, 0.05, loc=(0, -0.16, 0), rot=(90, 0, 0), segs=64, rsegs=8)
    G.T(chrome, G.CHROME, "Metal", name="Bezel", gloss=0.3)
    ticks = []
    for k in range(12):
        a = math.radians(90 - 30 * k)
        L = 0.16 if k % 3 == 0 else 0.08
        ticks.append(G.rod((0.72 * math.cos(a), -0.19, 0.72 * math.sin(a)), ((0.72 - L) * math.cos(a), -0.19, (0.72 - L) * math.sin(a)), 0.035, verts=8))
    G.T(ticks, G.INK_SOFT, name="Tick")
    hands = [G.puffy(G.stroke([(0, 0), (-0.04, 0.6)], 0.07), 0.05, y=-0.22), G.puffy(G.stroke([(0, 0), (-0.12, 0.42)], 0.09), 0.05, y=-0.24)]
    hub = G.cyl(0.08, 0.06, loc=(0, -0.26, 0), rot=(90, 0, 0), verts=16, bevel=0.02)
    G.T(hands + [hub], G.INK_SOFT, name="Hand")
    nail = G.sphere(0.07, loc=(0, -0.1, 1.08))
    G.T(nail, G.CHROME, "Metal", name="Nail", gloss=0.3)
    sign = G.puffy(G.rrect(1.7, 0.6, 0.12), 0.12, puff=0.35)
    G.T(sign, G.RED, name="Sign")
    border = G.puffy_holes(G.rrect(1.6, 0.5, 0.08), [G.rrect(1.5, 0.4, 0.06)], 0.04, y=-0.06)
    G.T(border, G.PAPER, name="SignBorder")
    t = G.text("CLOSED", 0.3, 0.05, loc=(0, -0.07, -0.01))
    G.fit_width(t, 1.28)
    G.T(t, G.PAPER, name="SignText")
    hooks = [G.torus(0.05, 0.015, loc=(x, 0, 0.32), rot=(0, 90, 0), segs=12, rsegs=4) for x in (-0.6, 0.6)]
    G.T(hooks, G.CHROME, "Metal", name="SignHook", gloss=0.3)
    sg = [sign, border, t] + hooks
    G.xform(sg, G.Tm(0.15, -0.35, -1.25) @ G.R(ry=-7))
    strings = [G.tube([(x0, -0.3, -0.92), (0.0, -0.3, -0.6)], 0.018, sides=6, res=1) for x0 in (-0.45, 0.75)]
    G.T(strings, "#C9B48A", name="String")
    fc(14, 6)


@meta("Ability_ChefsKiss")
def chefs_kiss():
    # glove (same style as HUD_Interact): four fingers and the thumb pinched to one point
    tip = (0.16, 1.12)
    palm = G.puffy(G.rrect(0.95, 0.88, 0.36, cz=-0.25), 0.42, puff=0.42)
    fingers = []
    for k, x in enumerate((-0.33, -0.11, 0.11, 0.33)):
        mid = (x * 1.05 + 0.04, 0.55 + 0.06 * (1.5 - abs(k - 1.5)))
        path = G.smooth_path([(x, 0.05), mid, (tip[0] + (k - 1.5) * 0.05, tip[1] - 0.04 * abs(k - 1.5))], 4)
        fingers.append(G.puffy(G.stroke(path, 0.17), 0.26, puff=0.45, y=0.06 - 0.03 * k))
    G.T([palm] + fingers, G.PAPER, name="Glove")
    thumb = G.puffy(G.stroke(G.smooth_path([(-0.44, -0.36), (-0.56, 0.2), (-0.26, 0.74), (tip[0] - 0.08, tip[1] - 0.14)], 4), 0.2), 0.3, puff=0.45, y=-0.12)
    G.T(thumb, "#E9E1D0", name="Thumb")
    lines = [G.puffy(G.stroke([(x, -0.12), (x, -0.42)], 0.035), 0.02, y=-0.21) for x in (-0.16, 0.04, 0.24)]
    G.T(lines, G.PAPER_D, name="Stitch")
    cuff = G.puffy(G.rrect(1.04, 0.34, 0.14, cz=-0.82), 0.48, puff=0.4)
    G.T(cuff, G.CYAN, name="Cuff")
    sp = [G.puffy(G.fillet(G.star(4, r, r * 0.26, cx=x, cz=z), 0.015, 1), 0.12, puff=0.4) for x, z, r in ((0.66, 1.42, 0.36), (1.02, 0.92, 0.2), (0.28, 1.76, 0.16))]
    G.T(sp, G.AMBER, name="Sparkle")
    h = G.puffy(G.heart(0.22, 40, cx=-0.52, cz=1.32), 0.14, puff=0.45)
    G.T(h, G.PINK, name="Kiss")
    G.xform(G.tagged(), G.R(ry=12))
    fc(14, 6)
