"""fam_meta2 — the 2026-11-06 additions to the meta family (group "meta"), same camera, cards and
look as fam_meta:

  * Break Room upgrades for the expanded night-by-night list (Config.RunUpgrades): Tip Jar,
    Comfy Stools, Labeled Breakers, Glow Paint, Rat Traps, Coffee Pot, ID Scanner, Riddle
    Dictionary, Emergency Lights, Backup Generator, Big Plate (the tier IIs reuse their base
    upgrade's icon).
  * the six new classes' uniforms on the shared hanger (fam_meta.shirt): Exterminator, Cashier,
    Food Critic, Detective, Bouncer, Mascot - each in its Config.Uniforms look.shirt colour.
  * the two new class abilities: Shove! (Bouncer) and Hype Up! (Mascot).
"""
from __future__ import annotations

import math
import random

import _common as G
from _common import Vector
import currency_kit as CK
import fam_hud
import fam_meta
from fam_meta import meta, fc, shirt, uniform

FAM = "meta"


# ---------------------------------------------------------------------------------------------
# run upgrades
# ---------------------------------------------------------------------------------------------

@meta("Upgrade_tip_jar", env="studio", world=1.0)
def tip_jar():
    R_, H_ = 0.85, 1.75
    glass = G.lathe([(0.0, 0.0), (R_ - 0.1, 0.0), (R_, 0.1), (R_, H_ - 0.3), (R_ - 0.18, H_ - 0.12), (R_ - 0.18, H_)], verts=48)
    G.glass_mat(glass)
    lip = G.torus(R_ - 0.16, 0.06, loc=(0, 0, H_), segs=48, rsegs=8)
    G.glass_mat(lip, centre=0.4, edge=0.9)
    # coins and folded bills inside, a few bills sticking out of the top
    rnd = random.Random(61)
    for i in range(34):
        z = 0.1 + (H_ - 0.55) * (i / 34) ** 0.9
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.0, 0.5)
        p = CK.coin(detail=(i % 3 == 0), scale=0.24)
        G.xform(p, G.Tm(rr * math.cos(a), rr * math.sin(a), z) @ G.R(rz=rnd.uniform(0, 360)) @ G.R(rx=rnd.uniform(-60, 60), ry=rnd.uniform(-60, 60)))
    bills = []
    for x, tilt, yaw in ((-0.2, -14, 8), (0.18, 12, -18), (0.0, 3, 40)):
        b = G.box((0.62, 0.03, 0.9), loc=(x, 0.0, H_ + 0.05), bevel=0.01, segs=1)
        G.xform(b, G.R(ry=tilt, rz=yaw, about=(x, 0.0, H_ - 0.3)))
        bills.append(b)
    G.T(bills, "#5DBB63", name="Bill")
    label = G.lathe([(R_ + 0.005, 0.55), (R_ + 0.02, 0.55), (R_ + 0.02, 1.0), (R_ + 0.005, 1.0)], verts=48)
    G.T(label, G.PAPER, name="Label")
    t = G.text("TIPS", 0.3, 0.05, loc=(0, -R_ - 0.04, 0.77))
    G.fit_width(t, 0.86)
    G.T(t, G.VINYL_RED, name="LabelText")
    h = G.puffy(G.heart(0.2, 40), 0.12, puff=0.45)
    G.xform(h, G.Tm(0.82, -0.6, H_ + 0.55) @ G.R(ry=-12))
    G.T(h, G.PINK, name="Heart")
    G.xform(G.tagged(), G.R(rz=-8))


@meta("Upgrade_comfy_stools", env="studio", world=0.8)
def comfy_stools():
    base = G.cyl(0.72, 0.12, loc=(0, 0, 0.06), verts=48, bevel=0.05, r_top=0.6)
    pole = G.cyl(0.09, 1.55, loc=(0, 0, 0.85), verts=24, bevel=0.0)
    ring = G.torus(0.52, 0.045, loc=(0, 0, 0.72), segs=48, rsegs=8)
    spokes = [G.rod((0, 0, 0.72), (0.52 * math.cos(a), 0.52 * math.sin(a), 0.72), 0.03, verts=8) for a in (0.4, 2.5, 4.6)]
    band = G.torus(0.84, 0.06, loc=(0, 0, 1.6), segs=56, rsegs=8)
    G.T([base, pole, ring, band] + spokes, G.CHROME, "Metal", name="Chrome", gloss=0.18)
    seat = G.cyl(0.85, 0.36, loc=(0, 0, 1.78), verts=56, bevel=0.15, segs=4)
    G.T(seat, G.VINYL_RED, name="Vinyl", gloss=0.35)
    tufts = [G.sphere(0.05, loc=(0.45 * math.cos(a), 0.45 * math.sin(a), 1.97), scale=(1, 1, 0.6)) for a in [k * math.pi / 3 for k in range(6)]]
    tufts.append(G.sphere(0.05, loc=(0, 0, 1.98), scale=(1, 1, 0.6)))
    G.T(tufts, G.VINYL_RED_D, name="Tuft")
    # a plump extra cushion on top
    cushion = G.box((1.15, 1.15, 0.36), loc=(0.05, -0.05, 2.18), bevel=0.17, segs=5)
    G.xform(cushion, G.R(rz=24, rx=-6, about=(0.05, -0.05, 2.18)))
    G.T(cushion, "#FFE0B8", name="Cushion", smooth=70)
    zs = []
    for i, (x, z, s) in enumerate(((0.75, 2.75, 0.32), (1.05, 3.08, 0.24))):
        o = G.text("z", s, 0.06, loc=(x, -0.3, z))
        zs.append(o)
    G.T(zs, G.CYAN, name="Zzz")
    G.xform(G.tagged(), G.R(rz=-10))


@meta("Upgrade_breaker_labels")
def breaker_labels():
    panel = G.box((2.5, 0.3, 1.5), loc=(0, 0, 0.75), bevel=0.08, segs=3)
    G.T(panel, "#5A6068", "Metal", name="Panel", gloss=0.45)
    inset = G.box((2.26, 0.06, 1.26), loc=(0, -0.15, 0.75), bevel=0.03)
    G.T(inset, "#2C3038", name="Inset")
    tapes = [("#E8423A", 0.0), ("#2E9BFF", 0.0), ("#4CD964", 0.0), ("#FFB020", 0.0)]
    for k, (col, _) in enumerate(tapes):
        x = -0.84 + 0.56 * k
        body = G.box((0.36, 0.16, 0.56), loc=(x, -0.2, 0.98), bevel=0.04)
        G.T(body, "#1C1E23", name="Breaker")
        up = k != 2
        lever = G.box((0.14, 0.2, 0.22), loc=(x, -0.3, 1.06 if up else 0.9), bevel=0.04)
        G.xform(lever, G.R(rx=-18 if up else 18, about=(x, -0.3, 0.98)))
        G.T(lever, G.PAPER if up else G.RED, name="Lever")
        tape = G.box((0.46, 0.03, 0.26), loc=(x, -0.2, 0.42), bevel=0.012, segs=1)
        G.xform(tape, G.R(ry=(-4, 3, -2, 5)[k], about=(x, -0.2, 0.42)))
        G.T(tape, G.PAPER, name="Tape")
        line = G.box((0.3, 0.02, 0.06), loc=(x - 0.02, -0.225, 0.44), bevel=0.008, segs=1)
        G.xform(line, G.R(ry=(-4, 3, -2, 5)[k], about=(x, -0.2, 0.42)))
        G.T(line, col, name="Scribble")
        dot = G.cyl(0.04, 0.02, loc=(x + 0.17, -0.225, 0.42), rot=(90, 0, 0), verts=12, bevel=0.0)
        G.T(dot, col, name="ScribbleDot")
    # the marker that wrote them
    pen = G.rod((-0.9, -0.75, 0.12), (0.4, -0.95, 0.12), 0.09, verts=20)
    G._bevel(pen, 0.03, 2)
    G.T(pen, G.INK_SOFT, name="Marker")
    cap = G.rod((0.38, -0.95, 0.12), (0.72, -1.0, 0.12), 0.1, verts=20)
    G._bevel(cap, 0.04, 2)
    G.T(cap, G.RED, name="MarkerCap")
    stripe = G.torus(0.092, 0.02, loc=(-0.3, -0.85, 0.12), rot=(0, 90, 0), segs=20, rsegs=4)
    G.xform(stripe, G.R(rz=-8.7, about=(-0.3, -0.85, 0.12)))
    G.T(stripe, G.PAPER, name="MarkerBand")
    G.xform(G.tagged(), G.R(rz=-6))


@meta("Upgrade_glow_notes")
def glow_notes():
    # Mr. Usual's sticky note, painted with glow paint
    note = G.slab(G.fillet([(-0.7, -0.7), (0.7, -0.7), (0.7, 0.42), (0.42, 0.7), (-0.7, 0.7)], 0.03, 2), 0.05, bevel=0.012, y=0.0)
    G.neon(note, "#E4FF57", 1.3, name="Note")
    curl = G.slab(G.fillet([(0.42, 0.7), (0.7, 0.42), (0.47, 0.47)], 0.02, 1), 0.05, bevel=0.01, y=-0.03)
    G.T(curl, "#B8D23A", name="Curl")
    lines = [G.slab(G.rrect(w, 0.07, 0.035, cx=-0.08 + (w - 0.95) / 2, cz=z), 0.03, y=-0.035) for w, z in ((0.95, 0.38), (0.8, 0.16), (0.9, -0.06), (0.55, -0.28))]
    G.T(lines, "#5E7A12", name="Scrawl")
    halo = G.glow_mat(G.sphere(1.05, loc=(0, 0.15, 0), scale=(1.0, 0.3, 1.0), segs=32, rings=16), "#E8FF5A", 1.6, 0.5, falloff=1.4)
    halo["g2_noframe"] = True
    G.xform(G.tagged(), G.R(ry=-8) @ G.Tm(-0.25, 0, 0.35))
    # the glow-paint tin and its brush
    tin = G.cyl(0.42, 0.62, loc=(0.95, -0.55, -0.55), verts=40, bevel=0.03)
    G.T(tin, G.CHROME, "Metal", name="Tin", gloss=0.3)
    lab = G.lathe([(0.425, -0.75), (0.435, -0.75), (0.435, -0.38), (0.425, -0.38)], verts=40)
    G.xform(lab, G.Tm(0.95, -0.55, 0))
    G.T(lab, "#2F3B1A", name="TinLabel")
    paint = G.cyl(0.36, 0.04, loc=(0.95, -0.55, -0.23), verts=40, bevel=0.0)
    G.neon(paint, "#D8FF3A", 2.2, name="Paint")
    drip = G.slab(G.fillet([(-0.08, 0.0), (0.08, 0.0), (0.06, -0.22), (0.0, -0.3), (-0.06, -0.22)], 0.02, 2), 0.04, y=0.0)
    G.xform(drip, G.Tm(0.62, -0.88, -0.3) @ G.R(rz=-30))
    G.neon(drip, "#D8FF3A", 2.2, name="Drip")
    brush = G.rod((0.75, -0.2, 0.55), (1.15, -0.75, -0.05), 0.05, verts=12)
    G.T(brush, G.WOOD, name="BrushHandle")
    ferrule = G.rod((1.15, -0.75, -0.05), (1.22, -0.85, -0.16), 0.08, verts=16)
    G.T(ferrule, G.CHROME, "Metal", name="Ferrule", gloss=0.3)
    tip = G.rod((1.22, -0.85, -0.16), (1.3, -0.96, -0.32), 0.09, verts=16, r_top=0.03)
    G.neon(tip, "#D8FF3A", 2.0, name="Bristles")
    G.xform(G.tagged(), G.R(rz=-4))


@meta("Upgrade_rat_traps")
def rat_traps():
    board = G.box((2.2, 1.0, 0.16), loc=(0, 0, 0.08), bevel=0.04)
    G.T(board, "#C8925A", name="Board")
    grain = [G.box((2.0, 0.015, 0.01), loc=(0, y, 0.163), bevel=0.0) for y in (-0.3, 0.05, 0.32)]
    G.T(grain, "#A6703D", name="Grain")
    # the bar (snapped up, ready), the springs and the bait plate
    bar = G.tube([(-0.2, -0.4, 0.2), (-0.2, -0.4, 0.95), (-0.2, 0.4, 0.95), (-0.2, 0.4, 0.2)], 0.045, sides=10, res=1)
    G.xform(bar, G.R(ry=-62, about=(-0.2, 0, 0.2)))
    hold = G.rod((-0.2, 0.0, 0.2), (0.62, 0.0, 0.2), 0.03, verts=8)
    G.T([bar, hold], G.CHROME, "Metal", name="Wire", gloss=0.25)
    springs = []
    for y in (-0.28, 0.28):
        pts = []
        for i in range(60):
            t = i / 59
            a = t * 2 * math.pi * 5
            pts.append((-0.2 + 0.09 * math.cos(a), y + (t - 0.5) * 0.3, 0.27 + 0.09 * math.sin(a)))
        springs.append(G.tube(pts, 0.022, sides=6, res=1))
    G.T(springs, G.CHROME, "Metal", name="Spring", gloss=0.25)
    staple = [G.tube([(x, -0.42, 0.16), (x, -0.42, 0.26), (x, 0.42, 0.26), (x, 0.42, 0.16)], 0.03, sides=8, res=1) for x in (-0.55,)]
    G.T(staple, G.STEEL_D, "Metal", name="Staple", gloss=0.35)
    plate = G.box((0.42, 0.42, 0.05), loc=(0.62, 0, 0.2), bevel=0.02)
    G.T(plate, "#C9CDD2", "Metal", name="Plate", gloss=0.35)
    # a wedge of cheese as bait
    wedge = G.slab([(-0.36, 0.0), (0.36, 0.0), (-0.36, 0.42)], 0.42, bevel=0.03, y=0.0)
    G.xform(wedge, G.Tm(0.66, 0.0, 0.23) @ G.R(rz=-30))
    G.T(wedge, "#FFD23A", name="Cheese")
    holes = []
    for x, z, r in ((-0.15, 0.12, 0.06), (0.05, 0.06, 0.045), (-0.25, 0.28, 0.04)):
        h = G.cyl(r, 0.02, loc=(x, -0.215, z), rot=(90, 0, 0), verts=16, bevel=0.0)
        holes.append(h)
    G.xform(holes, G.Tm(0.66, 0.0, 0.23) @ G.R(rz=-30))
    G.T(holes, "#E0A81E", name="CheeseHole")
    G.xform(G.tagged(), G.R(rz=-14))


@meta("Upgrade_coffee_pot", env="studio", world=0.8)
def coffee_pot():
    prof = [(0.0, 0.0), (0.62, 0.0), (0.72, 0.08), (0.86, 0.45), (0.86, 0.75), (0.62, 1.22), (0.52, 1.42), (0.52, 1.6)]
    glass = G.lathe(prof, verts=48)
    G.glass_mat(glass)
    coffee = G.lathe([(0.0, 0.03), (0.6, 0.03), (0.68, 0.1), (0.8, 0.45), (0.8, 0.72), (0.0, 0.72)], verts=48)
    G.T(coffee, "#4A2A18", name="Coffee", gloss=0.2)
    collar = G.lathe([(0.5, 1.4), (0.6, 1.42), (0.62, 1.75), (0.56, 1.8), (0.0, 1.8)], verts=40)
    G.T(collar, G.INK_SOFT, name="Collar", gloss=0.35)
    knob = G.sphere(0.12, loc=(0, 0, 1.86))
    G.T(knob, G.INK_SOFT, name="Knob", gloss=0.35)
    band = G.torus(0.6, 0.05, loc=(0, 0, 1.52), segs=40, rsegs=8)
    G.T(band, "#E8502A", name="Band")
    handle = G.tube([(0.55, 0, 1.55), (1.05, 0, 1.45), (1.12, 0, 0.95), (0.86, 0, 0.6)], 0.09, sides=12)
    G.T(handle, G.INK_SOFT, name="Handle", gloss=0.35)
    spout = G.slab(G.fillet([(-0.62, 1.42), (-0.88, 1.72), (-0.72, 1.74), (-0.48, 1.48)], 0.04, 2), 0.3, bevel=0.06, y=0.0)
    G.T(spout, G.INK_SOFT, name="Spout", gloss=0.35)
    # steam
    steam = []
    for k, (x, h) in enumerate(((-0.2, 0.9), (0.15, 1.15), (0.45, 0.8))):
        pts = [(x + 0.12 * math.sin(i * 1.3 + k), -0.1, 2.0 + h * i / 8) for i in range(9)]
        s = G.tube(pts, 0.07, sides=10, res=3)
        steam.append(G.glow_mat(s, "#FFFFFF", 1.2, 0.55))
    bolt = G.puffy(G.fillet([(0.04, 0.5), (0.3, 0.5), (0.1, 0.12), (0.3, 0.12), (-0.16, -0.5), (-0.04, -0.08), (-0.26, -0.08)], 0.03, 2), 0.16)
    G.xform(bolt, G.Tm(1.25, -0.4, 2.15) @ G.R(ry=12) @ G.S(0.85))
    G.T(bolt, G.GOLD, name="Bolt")
    G.xform(G.tagged(), G.R(rz=-6))


@meta("Upgrade_id_scanner")
def id_scanner():
    # the ID card being scanned
    card = G.slab(G.rrect(1.5, 0.95, 0.1), 0.05, bevel=0.015, y=0.0)
    G.T(card, G.PAPER, name="Card")
    head = G.slab(G.rrect(1.5, 0.24, 0.08, cz=0.355), 0.06, bevel=0.01, y=-0.01)
    G.T(head, G.BLUE, name="CardBand")
    photo = G.slab(G.rrect(0.42, 0.46, 0.05, cx=-0.45, cz=-0.08), 0.06, bevel=0.01, y=-0.012)
    G.T(photo, "#9AA4B0", name="Photo")
    face = G.puffy(G.circle(0.1, 20, -0.45, 0.0), 0.04, y=-0.04)
    sh = G.puffy(G.rrect(0.3, 0.14, 0.07, cx=-0.45, cz=-0.24), 0.04, y=-0.04)
    G.T([face, sh], "#5F6A78", name="Silhouette")
    bars = []
    for k in range(13):
        w = (0.02, 0.04, 0.03)[k % 3]
        bars.append(G.slab(G.rrect(w, 0.32, 0.005, cx=0.05 + 0.055 * k, cz=-0.12), 0.06, y=-0.012))
    G.T(bars, G.INK_SOFT, name="Barcode")
    laser = G.slab(G.rrect(0.95, 0.035, 0.017, cx=0.38, cz=-0.12), 0.02, y=-0.05)
    G.neon(laser, "#FF3B47", 3.5, name="Laser")
    G.xform(G.tagged(), G.Tm(-0.25, 0.4, -0.25) @ G.R(rx=-30) @ G.R(rz=-8))
    # the scanner gun and its red laser line across the card
    gun_head = G.box((0.9, 0.5, 0.42), loc=(0.6, -0.65, 0.65), bevel=0.14, segs=4)
    grip = G.box((0.36, 0.42, 0.85), loc=(0.85, -0.6, 0.2), bevel=0.14, segs=4)
    G.xform(grip, G.R(ry=-18, about=(0.85, -0.6, 0.6)))
    G.T([gun_head, grip], "#2C3038", name="Scanner", gloss=0.4)
    trig = G.box((0.12, 0.2, 0.26), loc=(0.6, -0.62, 0.32), bevel=0.05)
    G.T(trig, G.AMBER, name="Trigger")
    stripe = G.box((0.92, 0.52, 0.08), loc=(0.6, -0.65, 0.58), bevel=0.03)
    G.T(stripe, G.AMBER, name="Stripe")
    window = G.box((0.06, 0.38, 0.3), loc=(0.15, -0.65, 0.65), bevel=0.04)
    G.neon(window, "#FF2E3A", 2.5, name="Window")
    beam = G.slab([(0.0, 0.0), (-0.95, 0.38), (-0.95, -0.46)], 0.02, y=0.0)
    G.xform(beam, G.Tm(0.13, -0.65, 0.65) @ G.R(rx=-24))
    G.glow_mat(beam, "#FF3B47", 2.2, 0.35)
    G.xform(G.tagged(), G.R(rz=-6))


@meta("Upgrade_riddle_dictionary")
def riddle_dictionary():
    W, D, H = 1.5, 0.95, 1.95
    PURPLE = "#4B2E86"
    cover = G.box((W, D, H), loc=(0, 0, 0), bevel=0.0)
    G.boolean(cover, G.box((W, D - 0.2, H - 0.18), loc=(0.11, 0, 0), bevel=0.0))
    G._bevel(cover, 0.045, 3)
    G.T(cover, PURPLE, name="Cover")
    spine = G.cyl(D / 2, H, loc=(-W / 2, 0, 0), verts=32, bevel=0.045)
    G.T(spine, PURPLE, name="Spine")
    pages = G.box((W - 0.12, D - 0.2, H - 0.2), loc=(0.05, 0, 0), bevel=0.03, segs=2)
    G.T(pages, G.CREAM, name="Pages")
    # thumb-index tabs along the page edge
    tabs = []
    for k, z in enumerate((0.62, 0.3, -0.02, -0.34, -0.66)):
        tabs.append(G.cyl(0.09, 0.2, loc=(W / 2 + 0.005, -0.18 + 0.09 * (k % 2), z), rot=(0, 90, 0), verts=16, bevel=0.0))
    G.T(tabs, "#2B1E4A", name="Thumb")
    bands = [G.torus(D / 2 + 0.005, 0.035, loc=(-W / 2, 0, z), segs=40, rsegs=8) for z in (0.66, 0.52, -0.58, -0.72)]
    G.T(bands, G.GOLD, "Metal", name="Brass", gloss=0.3)
    yf = -D / 2 - 0.01
    plate = G.puffy(G.rrect(0.95, 1.2, 0.12, cx=0.1, cz=0.08), 0.06, y=yf)
    G.T(plate, "#3A2369", name="Plate")
    frame = G.puffy_holes(G.rrect(1.02, 1.27, 0.14, cx=0.1, cz=0.08), [G.rrect(0.9, 1.15, 0.1, cx=0.1, cz=0.08)], 0.05, y=yf - 0.02)
    G.T(frame, G.GOLD, "Metal", name="Frame", gloss=0.3)
    q = G.text("?", 1.0, 0.12, loc=(0.1, yf - 0.06, 0.1))
    G.T(q, G.GOLD, "Metal", name="Question", gloss=0.3)
    rib = G.slab([(0.3, -H / 2 + 0.1), (0.46, -H / 2 + 0.1), (0.46, -H / 2 - 0.42), (0.38, -H / 2 - 0.32), (0.3, -H / 2 - 0.42)], 0.03, bevel=0.008, y=-0.1)
    G.T(rib, G.RED, name="Ribbon")
    G.xform(G.tagged(), G.R(ry=-6) @ G.R(rz=12))


@meta("Upgrade_emergency_lights")
def emergency_lights():
    box_ = G.box((2.0, 0.66, 0.9), loc=(0, 0, 0.45), bevel=0.14, segs=4)
    G.T(box_, G.PAPER, name="Unit")
    grille = [G.box((0.9, 0.04, 0.05), loc=(-0.3, -0.34, z), bevel=0.015, segs=1) for z in (0.3, 0.42, 0.54)]
    G.T(grille, "#B8B2A4", name="Grille")
    led = G.sphere(0.06, loc=(0.55, -0.34, 0.42))
    G.neon(led, G.RED, 3.5, name="LED")
    btn = G.cyl(0.08, 0.06, loc=(0.75, -0.34, 0.42), rot=(90, 0, 0), verts=16, bevel=0.02)
    G.T(btn, G.INK_SOFT, name="Test")
    sign = G.slab(G.rrect(0.5, 0.18, 0.04, cx=0.65, cz=0.68), 0.03, y=-0.335)
    G.T(sign, "#2EA84A", name="Sign")
    for s in (-1, 1):
        x = s * 0.62
        joint = G.sphere(0.13, loc=(x, 0.0, 0.98))
        G.T(joint, G.STEEL_D, "Metal", name="Joint", gloss=0.35)
        can = G.lathe([(0.0, 0.0), (0.2, 0.0), (0.3, 0.12), (0.34, 0.42), (0.36, 0.48), (0.0, 0.48)], verts=36)
        lens = G.cyl(0.3, 0.04, loc=(0, 0, 0.49), verts=36, bevel=0.0)
        beam = G.lathe([(0.0, 0.5), (0.3, 0.5), (0.7, 1.4), (0.0, 1.4)], verts=36)
        parts = [can, lens, beam]
        G.xform(parts, G.Tm(x, 0.0, 1.0) @ G.R(rz=s * 32) @ G.R(rx=78, ry=s * 18))
        G.T(can, G.PAPER, name="Head")
        G.neon(lens, "#FFF1C4", 4.0, name="Lens")
        G.glow_mat(beam, "#FFE9A8", 1.4, 0.22, falloff=0.6)
        beam["g2_noframe"] = True
    G.xform(G.tagged(), G.R(rz=-4))


@meta("Upgrade_backup_generator")
def backup_generator():
    YEL = "#FFC23A"
    frame_pts = [(-1.1, 0.0), (-1.1, 1.35), (1.1, 1.35), (1.1, 0.0)]
    rails = []
    for y in (-0.6, 0.6):
        rails.append(G.tube([(x, y, z) for x, z in frame_pts], 0.06, sides=10, res=1))
    for x in (-1.1, 1.1):
        rails.append(G.rod((x, -0.6, 1.35), (x, 0.6, 1.35), 0.06, verts=10))
    G.T(rails, G.INK_SOFT, name="Frame", gloss=0.4)
    body = G.box((1.75, 1.05, 0.95), loc=(0, 0, 0.6), bevel=0.12, segs=3)
    G.T(body, "#E2E5E9", "Metal", name="Engine", gloss=0.4)
    tank = G.box((1.5, 0.95, 0.42), loc=(0.05, 0, 1.28), bevel=0.18, segs=4)
    G.T(tank, YEL, name="Tank")
    cap = G.cyl(0.13, 0.12, loc=(0.45, 0.0, 1.52), verts=20, bevel=0.03)
    G.T(cap, G.INK_SOFT, name="Cap")
    panel = G.box((0.9, 0.06, 0.6), loc=(0.25, -0.55, 0.62), bevel=0.04)
    G.T(panel, YEL, name="Panel")
    for x in (0.02, 0.48):
        sock = G.cyl(0.13, 0.05, loc=(x, -0.6, 0.66), rot=(90, 0, 0), verts=20, bevel=0.015)
        G.T(sock, G.PAPER, name="Socket")
        for dx in (-0.04, 0.04):
            slot = G.box((0.02, 0.03, 0.08), loc=(x + dx, -0.63, 0.68), bevel=0.0)
            G.T(slot, G.INK_SOFT, name="Slot")
    pull = G.tube([(-0.55, -0.6, 0.85), (-0.6, -0.72, 0.85), (-0.85, -0.72, 0.85)], 0.04, sides=8, res=2)
    G.T(pull, G.INK_SOFT, name="Pull")
    exhaust = G.cyl(0.14, 0.42, loc=(-0.75, 0.2, 0.55), rot=(0, 90, 0), verts=20, bevel=0.03)
    G.T(exhaust, G.STEEL_D, "Metal", name="Muffler", gloss=0.35)
    bolt = G.puffy(G.fillet([(0.04, 0.5), (0.3, 0.5), (0.1, 0.12), (0.3, 0.12), (-0.16, -0.5), (-0.04, -0.08), (-0.26, -0.08)], 0.03, 2), 0.14)
    G.xform(bolt, G.Tm(0.25, -0.62, 0.35) @ G.S(0.55))
    G.T(bolt, G.INK_SOFT, name="BoltMark")
    big = G.puffy(G.fillet([(0.04, 0.5), (0.3, 0.5), (0.1, 0.12), (0.3, 0.12), (-0.16, -0.5), (-0.04, -0.08), (-0.26, -0.08)], 0.03, 2), 0.2)
    G.xform(big, G.Tm(1.15, -0.85, 1.95) @ G.R(ry=14) @ G.S(1.1))
    G.T(big, G.GOLD, name="Bolt")
    G.xform(G.tagged(), G.R(rz=-12))


@meta("Upgrade_big_plate")
def big_plate():
    plate = G.lathe([(0.0, 0.0), (0.9, 0.0), (1.05, 0.06), (1.5, 0.2), (1.62, 0.26), (1.6, 0.3), (1.45, 0.26), (1.0, 0.13), (0.0, 0.11)], verts=64)
    G.T(plate, G.PAPER, name="Plate", gloss=0.25)
    rim = G.lathe([(1.36, 0.215), (1.4, 0.225), (1.48, 0.25), (1.44, 0.25)], verts=64)
    G.T(rim, "#2E7BD1", name="RimStripe")
    # a tall sandwich on it
    z = 0.12
    layers = []
    for h, col, r, wav in ((0.22, "#E7B46A", 0.82, 0.0), (0.08, "#5CC24B", 0.92, 0.05), (0.08, "#E8423A", 0.8, 0.0),
                            (0.07, "#FFD23A", 0.86, 0.03), (0.16, "#8A4A2A", 0.8, 0.0), (0.08, "#5CC24B", 0.9, 0.05), (0.28, "#E9A955", 0.8, 0.0)):
        o = G.cyl(r, h, loc=(0, 0, z + h / 2), verts=40, bevel=min(0.06, h * 0.45), segs=3)
        if wav:
            for v in o.data.vertices:
                a = math.atan2(v.co.y, v.co.x)
                k = 1 + wav * math.sin(9 * a)
                v.co.x *= k
                v.co.y *= k
        G.T(o, col, name="Layer")
        layers.append(o)
        z += h
    seeds = [G.sphere(0.04, loc=(0.4 * math.cos(a), 0.4 * math.sin(a), z - 0.01), scale=(1.4, 0.8, 0.5)) for a in (0.3, 1.6, 2.9, 4.3, 5.4)]
    G.T(seeds, G.PAPER, name="Seed")
    pick = G.rod((0.0, 0.0, z - 0.6), (0.0, 0.0, z + 0.45), 0.025, verts=8)
    G.T(pick, G.WOOD, name="Pick")
    flag = G.slab([(0.0, 0.0), (0.42, 0.06), (0.0, 0.22)], 0.02, y=0.0)
    G.xform(flag, G.Tm(0.0, -0.01, z + 0.22))
    G.T(flag, G.RED, name="Flag")
    G.xform(G.tagged(), G.R(rz=-10))


# ---------------------------------------------------------------------------------------------
# uniforms (Config.Uniforms look.shirt colours)
# ---------------------------------------------------------------------------------------------

def rat_mark(cx, cz, s=1.0, y=-0.22, col="#5A5F68"):
    body = G.puffy(G.circle(0.16 * s, 24, cx - 0.02 * s, cz, rz=0.1 * s), 0.04, y=y)
    head = G.puffy(G.circle(0.08 * s, 16, cx + 0.15 * s, cz + 0.02 * s, rz=0.07 * s), 0.04, y=y)
    ear = G.puffy(G.circle(0.045 * s, 12, cx + 0.12 * s, cz + 0.1 * s), 0.04, y=y)
    tail = G.puffy(G.stroke(G.smooth_path([(cx - 0.17 * s, cz - 0.02 * s), (cx - 0.3 * s, cz + 0.08 * s), (cx - 0.36 * s, cz - 0.04 * s)], 3), 0.025 * s), 0.03, y=y)
    G.T([body, head, ear, tail], col, name="Rat")


@uniform("exterminator")
def u_exterminator():
    OLIVE, OLIVE_D = "#6F7F3A", "#56652C"
    shirt(OLIVE, collar=OLIVE_D, cuffs=OLIVE_D, buttons=None)
    zip_ = G.puffy(G.rrect(0.06, 1.3, 0.02, cz=-0.32), 0.05, y=-0.2)
    G.T(zip_, G.CHROME, "Metal", name="Zip", gloss=0.3)
    pull = G.puffy(G.rrect(0.07, 0.14, 0.03, cz=0.3), 0.05, y=-0.22)
    G.T(pull, G.CHROME, "Metal", name="ZipPull", gloss=0.3)
    belt = G.puffy(G.rrect(1.26, 0.16, 0.04, cz=-0.62), 0.36, puff=0.3)
    G.T(belt, G.INK_SOFT, name="Belt")
    buckle = G.puffy(G.rrect(0.2, 0.2, 0.04, cz=-0.62), 0.06, y=-0.2)
    G.T(buckle, G.GOLD, "Metal", name="Buckle", gloss=0.3)
    # the NO RATS patch on the chest
    patch = G.puffy(G.circle(0.26, 36, 0.33, 0.12), 0.06, y=-0.19)
    G.T(patch, G.PAPER, name="Patch")
    rat_mark(0.33, 0.1, 0.9, y=-0.225)
    ring = G.puffy_holes(G.circle(0.24, 36, 0.33, 0.12), [G.circle(0.19, 36, 0.33, 0.12)], 0.05, y=-0.235)
    slash = G.puffy(G.stroke([(0.18, 0.27), (0.48, -0.03)], 0.05), 0.05, y=-0.24)
    G.T([ring, slash], G.RED, name="NoMark")
    fc()


@uniform("cashier")
def u_cashier():
    RED, RED_D = "#D94B4B", "#B23838"
    shirt(RED, collar=G.PAPER, cuffs=G.PAPER, buttons=G.PAPER)
    pocket = G.puffy(G.rrect(0.32, 0.3, 0.05, cx=-0.34, cz=-0.1), 0.05, y=-0.18)
    G.T(pocket, RED_D, name="Pocket")
    pencil = G.rod((-0.42, -0.21, -0.05), (-0.36, -0.21, 0.28), 0.04, verts=6)
    G.T(pencil, "#FFC93C", name="Pencil")
    tipp = G.rod((-0.36, -0.21, 0.28), (-0.35, -0.21, 0.36), 0.04, verts=6, r_top=0.01)
    G.T(tipp, G.KRAFT, name="PencilTip")
    eraser = G.rod((-0.42, -0.21, -0.05), (-0.425, -0.21, -0.1), 0.04, verts=6)
    G.T(eraser, G.PINK, name="Eraser")
    tag = G.puffy(G.rrect(0.42, 0.22, 0.05, cx=0.34, cz=-0.04), 0.06, y=-0.2)
    G.T(tag, G.PAPER, name="NameTag")
    hi = G.text("HI!", 0.15, 0.03, loc=(0.34, -0.24, -0.04))
    G.fit_width(hi, 0.3)
    G.T(hi, RED, name="NameTagText")
    stripe = [G.puffy(G.stroke([(k * 0.62, -0.95), (k * 0.66, 0.12)], 0.05), 0.36, puff=0.3) for k in (1, -1)]
    G.T(stripe, G.PAPER, name="Piping")
    fc()


@uniform("food_critic")
def u_food_critic():
    PURPLE, PURPLE_D = "#5B3A8C", "#43296A"
    shirt(PURPLE, collar=None, cuffs=PURPLE_D, collar_kind=None, buttons=None)
    lapels = []
    for k in (1, -1):
        pts = [(0.0, 0.3), (k * 0.2, 0.72), (k * 0.36, 0.56), (k * 0.26, 0.36), (k * 0.34, 0.2), (k * 0.08, -0.36)]
        lapels.append(G.puffy(pts if k > 0 else pts[::-1], 0.07, y=-0.2))
    G.T(lapels, PURPLE_D, name="Lapel")
    # a silk ascot at the throat
    ascot = G.puffy(G.fillet([(-0.14, 0.56), (0.14, 0.56), (0.18, 0.32), (0.0, 0.12), (-0.18, 0.32)], 0.05, 2), 0.12, y=-0.24)
    G.T(ascot, "#E8B23A", name="Ascot")
    dots = [G.sphere(0.025, loc=(x, -0.31, z)) for x, z in ((-0.06, 0.45), (0.07, 0.4), (0.0, 0.28), (-0.08, 0.3))]
    G.T(dots, "#B5452F", name="AscotDot")
    sq = G.puffy(G.fillet([(0.24, 0.02), (0.46, 0.02), (0.42, 0.14), (0.35, 0.08), (0.3, 0.16)], 0.02, 1), 0.06, y=-0.21)
    G.T(sq, G.PAPER, name="PocketSquare")
    btns = [G.cyl(0.05, 0.05, loc=(0.08, -0.22, z), rot=(90, 0, 0), verts=16, bevel=0.015) for z in (-0.48, -0.72)]
    G.T(btns, G.GOLD, "Metal", name="Button", gloss=0.3)
    # the monocle on its chain
    mono = G.torus(0.12, 0.022, loc=(-0.42, -0.24, -0.38), rot=(90, 0, 0), segs=28, rsegs=6)
    glass = G.cyl(0.11, 0.01, loc=(-0.42, -0.24, -0.38), rot=(90, 0, 0), verts=28, bevel=0.0)
    chain = G.tube([(-0.32, -0.22, 0.02), (-0.36, -0.24, -0.15), (-0.42, -0.25, -0.26)], 0.012, sides=6)
    G.T([mono, chain], G.GOLD, "Metal", name="Monocle", gloss=0.3)
    G.T(glass, "#DDF6FF", name="MonocleGlass", gloss=0.1)
    fc()


@uniform("detective")
def u_detective():
    TAN, TAN_D = "#8A6A44", "#6E5233"
    shirt(TAN, collar=TAN_D, cuffs=TAN_D, collar_kind="point", buttons=None, sleeve=1.08)
    lapels = []
    for k in (1, -1):
        pts = [(k * 0.04, 0.3), (k * 0.22, 0.7), (k * 0.5, 0.5), (k * 0.36, 0.36), (k * 0.5, 0.18), (k * 0.12, -0.2)]
        lapels.append(G.puffy(pts if k > 0 else pts[::-1], 0.07, y=-0.2))
    G.T(lapels, TAN_D, name="Lapel")
    btns = [G.cyl(0.055, 0.05, loc=(x, -0.22, z), rot=(90, 0, 0), verts=16, bevel=0.015) for x in (-0.18, 0.22) for z in (-0.25, -0.75)]
    G.T(btns, "#3B2A1A", name="Button")
    belt = G.puffy(G.rrect(1.3, 0.16, 0.05, cz=-0.5), 0.38, puff=0.3)
    G.T(belt, TAN_D, name="Belt")
    buckle = G.puffy_holes(G.rrect(0.24, 0.22, 0.04, cz=-0.5), [G.rrect(0.14, 0.12, 0.02, cz=-0.5)], 0.06, y=-0.21)
    G.T(buckle, "#3B2A1A", name="Buckle")
    eps = [G.puffy(G.fillet([(k * 0.24, 0.72), (k * 0.6, 0.62), (k * 0.62, 0.52), (k * 0.26, 0.6)][::k], 0.03, 1), 0.38, puff=0.3) for k in (1, -1)]
    G.T(eps, TAN_D, name="Epaulette")
    # a magnifying glass in the pocket
    ring = G.torus(0.17, 0.035, loc=(0.42, -0.26, 0.22), rot=(90, 0, 0), segs=32, rsegs=8)
    lens = G.cyl(0.15, 0.02, loc=(0.42, -0.26, 0.22), rot=(90, 0, 0), verts=32, bevel=0.0)
    handle = G.rod((0.42, -0.26, 0.05), (0.42, -0.26, -0.2), 0.04, verts=12)
    G.T(ring, G.GOLD, "Metal", name="LensRing", gloss=0.3)
    G.T(lens, "#CFF3FF", name="Lens", gloss=0.1)
    G.T(handle, "#3B2A1A", name="LensHandle")
    pocket = G.puffy(G.rrect(0.36, 0.3, 0.05, cx=0.42, cz=-0.1), 0.05, y=-0.22)
    G.T(pocket, TAN_D, name="Pocket")
    fc()


@uniform("bouncer")
def u_bouncer():
    BLACK = "#2B2B30"
    shirt(BLACK, collar="#1E1E22", cuffs=None, collar_kind="band", buttons=None, sleeve=0.86)
    t = G.text("STAFF", 0.26, 0.04, loc=(0.0, -0.2, 0.0))
    G.fit_width(t, 0.86)
    G.T(t, G.PAPER, name="Print")
    # earpiece: a curly clear wire up from the collar
    pts = []
    for i in range(70):
        u = i / 69
        a = u * 2 * math.pi * 8
        pts.append((0.3 + 0.04 * math.cos(a), -0.24 + 0.03 * math.sin(a), 0.62 - 0.85 * u))
    wire = G.tube(pts, 0.012, sides=6, res=1)
    G.T(wire, "#D9E6EE", name="Wire", gloss=0.15)
    bud = G.sphere(0.07, loc=(0.32, -0.24, 0.68))
    G.T(bud, "#1E1E22", name="Earpiece", gloss=0.3)
    arms = [G.puffy(G.stroke([(k * 0.84, 0.26), (k * 0.66, 0.02)], 0.06), 0.36, puff=0.3) for k in (1, -1)]
    G.T(arms, "#3A3A42", name="SleeveBand")
    fc()


@uniform("mascot")
def u_mascot():
    MUSTARD = "#E8A93A"
    shirt(MUSTARD, collar=G.RED, cuffs=G.RED, collar_kind="band", buttons=None)
    # the STACKHOUSE burger on the chest
    st = CK.stamp_parts(0.07)
    cols = {"bun": "#C97A2C", "seed": G.PAPER, "leaf": "#4FC04A", "patty": "#6B3A1E"}
    objs = []
    for o, role in st:
        G.T(o, cols[role], name=f"Crest_{role}")
        objs.append(o)
    G.xform(objs, G.Tm(0.0, -0.25, -0.05) @ G.S(0.62))
    stripes = [G.puffy(G.stroke([(k * 0.98, 0.22), (k * 0.84, 0.02)], 0.06), 0.36, puff=0.3) for k in (1, -1)]
    G.T(stripes, G.RED, name="SleeveStripe")
    num = G.text("1", 0.24, 0.04, loc=(-0.44, -0.2, -0.62))
    G.T(num, G.RED, name="Number")
    # a foam finger beside the jersey
    hand = G.puffy(G.rrect(0.5, 0.42, 0.16, cz=0.0), 0.3, puff=0.45)
    finger = G.puffy(G.stroke([(0.08, 0.15), (0.08, 0.68)], 0.18), 0.26, puff=0.45)
    thumb = G.puffy(G.stroke([(-0.22, 0.05), (-0.34, 0.24)], 0.13), 0.24, puff=0.45)
    cuffp = G.puffy(G.rrect(0.42, 0.24, 0.06, cz=-0.32), 0.3, puff=0.3)
    foam = [hand, finger, thumb]
    G.T(foam, G.PINK, name="Foam")
    G.T(cuffp, G.PAPER, name="FoamCuff")
    one = G.text("#1", 0.16, 0.03, loc=(-0.02, -0.17, -0.02))
    G.T(one, G.PAPER, name="FoamText")
    G.xform(foam + [cuffp, one], G.Tm(1.15, 0.05, -0.62) @ G.R(ry=-14) @ G.S(0.9))
    fc()


# ---------------------------------------------------------------------------------------------
# abilities
# ---------------------------------------------------------------------------------------------

@meta("Ability_Shove")
def shove():
    # an impact burst behind, the open palm shoving forward, speed lines trailing
    burst = G.puffy(G.fillet(G.star(10, 1.25, 0.82, a0=8), 0.03, 1), 0.12, puff=0.35, y=0.35)
    G.T(burst, G.AMBER, name="Burst")
    inner = G.puffy(G.fillet(G.star(10, 0.92, 0.62, a0=26), 0.03, 1), 0.12, puff=0.35, y=0.25)
    G.T(inner, "#FFE27A", name="BurstCore")
    palm = fam_hud.glove(fingers=((-0.33, 0.66, 8), (-0.11, 0.78, 3), (0.11, 0.76, -2), (0.33, 0.62, -8)), col=G.PAPER)
    cuff = G.puffy(G.rrect(1.06, 0.34, 0.14, cz=-0.82), 0.46, puff=0.4)
    G.T(cuff, G.INK_SOFT, name="Cuff")
    lines = [G.slab(G.rrect(0.05, 0.36, 0.025, cx=x, cz=-0.24), 0.02, y=-0.19) for x in (-0.18, 0.0, 0.18)]
    G.T(lines, G.PAPER_D, name="Stitch")
    hand = palm + [cuff] + lines
    G.xform(hand, G.Tm(0.1, -0.3, 0.05) @ G.R(ry=-14) @ G.S(0.9))
    speed = [G.puffy(G.stroke([(-1.75, z), (-1.05, z)], 0.09), 0.06, y=-0.3) for z in (0.55, 0.15, -0.25)]
    G.T(speed, G.CYAN, name="Speed")
    G.xform(G.tagged(), G.R(ry=4))
    fc(14, 6)


@meta("Ability_HypeUp")
def hype_up():
    # a megaphone blaring up and to the right, sound arcs and sparkles
    cone = G.lathe([(0.12, 0.0), (0.2, 0.05), (0.62, 1.1), (0.66, 1.18), (0.58, 1.18), (0.0, 1.18)], verts=40)
    G.T(cone, G.RED, name="Horn")
    bell = G.torus(0.62, 0.06, loc=(0, 0, 1.17), segs=40, rsegs=8)
    G.T(bell, G.PAPER, name="Bell")
    stripe = G.lathe([(0.34, 0.52), (0.36, 0.52), (0.42, 0.68), (0.4, 0.68)], verts=40)
    G.T(stripe, G.PAPER, name="Stripe")
    back = G.cyl(0.2, 0.36, loc=(0, 0, -0.15), verts=24, bevel=0.06)
    G.T(back, G.INK_SOFT, name="Back")
    grip = G.box((0.55, 0.2, 0.16), loc=(0.32, 0.0, 0.22), bevel=0.06)
    G.T(grip, G.INK_SOFT, name="Grip")
    horn = [cone, bell, stripe, back, grip]
    G.xform(horn, G.Tm(-0.35, 0.0, -0.3) @ G.R(ry=52) @ G.R(rx=-90 + 75))
    arcs = [G.puffy(G.stroke(G.arc(r, -30, 50, 12, 0.55, 0.42), 0.09), 0.08, y=-0.1) for r in (0.45, 0.75, 1.05)]
    G.T(arcs, G.CYAN, name="Sound")
    sp = [G.puffy(G.fillet(G.star(4, r, r * 0.28, cx=x, cz=z), 0.015, 1), 0.1, puff=0.4, y=-0.2) for x, z, r in ((-0.85, 1.05, 0.28), (1.25, -0.55, 0.22), (-1.1, 0.35, 0.16))]
    G.T(sp, G.AMBER, name="Sparkle")
    chev = []
    for k in range(2):
        chev.append(G.puffy(G.stroke([(-1.2 + 0.25 * k, -0.25), (-1.0 + 0.25 * k, -0.45), (-1.2 + 0.25 * k, -0.65)], 0.09), 0.08, y=-0.15))
    G.T(chev, G.PINK, name="Speed")
    fc(14, 6)
