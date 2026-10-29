"""fam_hud — HUD and rail glyphs (group "hud"): one chunky object each, read at 28-56 px.

Family look: soft-plastic toy glyphs, 2-3 flat-ish colours + one bright accent from the game
palette, the shared "hud" camera (yaw -28, pitch 20) with flat emblems turned toward it so
only a sliver of their thickness shows. HUD_Right is HUD_Left's render mirrored pixel for
pixel (a true mirror, light included).
"""
from __future__ import annotations

import math
import os
import random

import _common as G
from _common import ns, Vector

FAM = "hud"


def hud(name, **opts):
    return G.icon(name, "hud", FAM, **opts)


# ---------------------------------------------------------------------------------------------
# simple emblem glyphs
# ---------------------------------------------------------------------------------------------

@hud("HUD_Check")
def check():
    pts = G.stroke([(-0.86, 0.02), (-0.3, -0.56), (0.92, 0.78)], 0.56)
    G.T(G.puffy(G.fillet(pts, 0.05, 2), 0.5), G.GREEN, name="Check")
    G.face_cam(reveal=14, tilt=6)


@hud("HUD_Warn")
def warn():
    tri = G.fillet([(0.0, 1.0), (-1.12, -0.92), (1.12, -0.92)], 0.26, 5)
    G.T(G.puffy(tri, 0.5), G.AMBER, name="Tri")
    bar = G.puffy(G.stroke([(0.0, 0.42), (0.0, -0.22)], 0.27), 0.16, y=-0.27)
    dot = G.puffy(G.circle(0.155, 24, 0, -0.56), 0.16, y=-0.27)
    G.T([bar, dot], G.INK_SOFT, name="Bang")
    G.face_cam(reveal=14, tilt=6)


@hud("HUD_Featured")
def featured():
    burst = G.fillet(G.star(12, 1.0, 0.8, a0=90), 0.035, 2)
    G.T(G.puffy(burst, 0.42), G.AMBER, name="Burst")
    st = G.fillet(G.star(5, 0.66, 0.29, a0=90, cz=-0.02), 0.045, 2)
    G.T(G.puffy(st, 0.2, y=-0.24), G.PAPER, name="Star")
    G.face_cam(reveal=14, tilt=6)


def gear_outline(n=8, r_tip=1.0, r_root=0.76, tip_frac=0.32, root_frac=0.42, steps=4):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        w = 2 * math.pi / n
        # tooth: root -> flank -> tip -> flank -> root
        segs = [(-0.5 * root_frac, r_root), (-0.5 * tip_frac, r_tip), (0.5 * tip_frac, r_tip), (0.5 * root_frac, r_root)]
        for k, (f, r) in enumerate(segs):
            pts.append((r * math.cos(a + f * w), r * math.sin(a + f * w)))
        # valley arc
        for s in range(1, steps):
            aa = a + (0.5 * root_frac + (1 - root_frac) * s / steps) * w
            pts.append((r_root * math.cos(aa), r_root * math.sin(aa)))
    return G.fillet(pts, 0.05, 2)


@hud("HUD_Settings")
def settings():
    g = G.puffy_holes(gear_outline(), [G.circle(0.34, 32)], 0.46, puff=0.32)
    G.T(g, G.STEEL, name="Gear")
    hub = G.puffy_holes(G.circle(0.55, 40), [G.circle(0.34, 32)], 0.2, y=-0.22, puff=0.4)
    G.T(hub, G.CYAN, name="Hub")
    G.face_cam(reveal=16, tilt=8)


def chevron():
    pts = G.stroke([(0.42, 0.9), (-0.46, 0.0), (0.42, -0.9)], 0.58)
    G.T(G.puffy(G.fillet(pts, 0.1, 3), 0.5), G.PAPER, name="Chevron")
    G.face_cam(reveal=10, tilt=4)


def _mirror_png(path):
    from PIL import Image, ImageOps
    im = Image.open(path)
    ImageOps.mirror(im).save(path)


hud("HUD_Left")(chevron)
hud("HUD_Right", post=_mirror_png)(chevron)


@hud("HUD_Stamina")
def stamina():
    bolt = [(0.04, 1.06), (0.64, 1.06), (0.2, 0.24), (0.66, 0.24), (-0.34, -1.12), (-0.08, -0.16), (-0.6, -0.16)]
    G.T(G.puffy(G.fillet(bolt, 0.07, 3), 0.48), G.GOLD, name="Bolt")
    G.face_cam(reveal=14, tilt=6)


@hud("HUD_Revive")
def revive():
    G.T(G.puffy(G.heart(1.05, 72), 0.62, puff=0.45), "#FF2E4D", name="Heart")
    plus = [G.puffy(G.rrect(0.26, 0.86, 0.1, cz=0.1), 0.16, y=-0.31), G.puffy(G.rrect(0.86, 0.26, 0.1, cz=0.1), 0.16, y=-0.31)]
    G.T(plus, G.PAPER, name="Plus")
    G.face_cam(reveal=14, tilt=6)


@hud("HUD_Info")
def info():
    G.T(G.puffy(G.circle(1.0, 64), 0.5), G.BLUE, name="Bubble")
    tail = G.fillet([(-0.42, -0.62), (-1.0, -1.22), (0.02, -0.9)], 0.06, 2)
    G.T(G.puffy(tail, 0.5), G.BLUE, name="Tail")
    dot = G.puffy(G.circle(0.16, 24, 0, 0.5), 0.16, y=-0.25)
    stem = G.puffy(G.rrect(0.32, 0.78, 0.1, cz=-0.2), 0.16, y=-0.25)
    G.T([dot, stem], G.PAPER, name="Eye")
    G.face_cam(reveal=14, tilt=6)


# ---------------------------------------------------------------------------------------------
# objects
# ---------------------------------------------------------------------------------------------

@hud("HUD_Book")
def book():
    W, D, H = 1.46, 0.66, 1.95
    cover = G.box((W, D, H), loc=(0, 0, 0), bevel=0.0)
    G.boolean(cover, G.box((W, D - 0.2, H - 0.18), loc=(0.11, 0, 0), bevel=0.0))
    G._bevel(cover, 0.045, 3)
    G.T(cover, G.VINYL_RED, name="Cover")
    spine = G.cyl(D / 2, H, loc=(-W / 2, 0, 0), verts=32, bevel=0.045)
    G.T(spine, G.VINYL_RED, name="Spine")
    pages = G.box((W - 0.12, D - 0.2, H - 0.2), loc=(0.05, 0, 0), bevel=0.03, segs=2)
    G.T(pages, G.CREAM, name="Pages")
    # gold spine bands + corner caps
    bands = [G.torus(D / 2 + 0.005, 0.035, loc=(-W / 2, 0, z), segs=40, rsegs=8) for z in (0.62, 0.48, -0.55, -0.69)]
    caps = []
    for sz in (1, -1):
        tri = [(W / 2 + 0.03, sz * (H / 2 + 0.03)), (W / 2 + 0.03 - 0.36, sz * (H / 2 + 0.03)), (W / 2 + 0.03, sz * (H / 2 + 0.03 - 0.36))]
        caps.append(G.slab(G.fillet(tri, 0.04, 2), 0.06, bevel=0.015, y=-D / 2 - 0.01))
    G.T(bands + caps, G.GOLD, name="Brass")
    # emblem: cream medallion with a stacked sandwich
    yf = -D / 2 - 0.01
    G.T(G.puffy(G.circle(0.5, 48, 0.0, 0.18), 0.1, y=yf), G.PAPER, name="Medal")
    bun = G.puffy(G.arc(0.36, 0, 180, 16, 0.0, 0.2) + [(-0.36, 0.2)], 0.1, y=yf - 0.05)
    base = G.puffy(G.rrect(0.72, 0.15, 0.07, cz=-0.05), 0.1, y=yf - 0.05)
    G.T([bun, base], G.AMBER, name="Bun")
    wave = [(-0.42 + 0.84 * i / 16, 0.11 + 0.035 * math.sin(i * 1.4)) for i in range(17)]
    lettuce = G.puffy(G.stroke(wave, 0.09), 0.1, y=yf - 0.06)
    G.T(lettuce, "#4FC04A", name="Lettuce")
    G.T(G.puffy(G.rrect(0.66, 0.08, 0.04, cz=0.04), 0.1, y=yf - 0.055), "#E8423A", name="Tomato")
    # ribbon bookmark out of the bottom
    rib = G.slab([(0.25, -H / 2 + 0.1), (0.41, -H / 2 + 0.1), (0.41, -H / 2 - 0.42), (0.33, -H / 2 - 0.32), (0.25, -H / 2 - 0.42)],
                 0.03, bevel=0.008, y=-0.05)
    G.T(rib, G.PINK, name="Ribbon")
    G.xform(G.tagged(), G.R(ry=-6) @ G.R(rz=12))


@hud("HUD_Clues")
def clues():
    note = G.slab(G.rrect(1.3, 1.55, 0.06), 0.06, bevel=0.015, y=0.3)
    G.T(note, G.PAPER, name="Note")
    lines = [G.slab(G.rrect(w, 0.08, 0.04, cx=-0.08 + (w - 0.9) / 2, cz=z), 0.03, y=0.27) for w, z in ((0.9, 0.45), (0.75, 0.22), (0.85, -0.01), (0.6, -0.24))]
    G.T(lines, "#9C978C", name="Lines")
    pin = [G.sphere(0.12, loc=(0.0, 0.18, 0.72)), G.cyl(0.03, 0.2, loc=(0.0, 0.28, 0.72), rot=(90, 0, 0), verts=8, bevel=0)]
    G.T(pin, G.RED, name="Pin")
    G.xform(G.tagged(), G.R(ry=-9))
    cx, cz, Rr = -0.22, 0.12, 0.6
    ring = G.torus(Rr, 0.115, loc=(cx, -0.12, cz), rot=(90, 0, 0), segs=48, rsegs=14)
    G.T(ring, G.AMBER, name="Ring")
    lens = G.cyl(Rr - 0.02, 0.06, loc=(cx, -0.1, cz), rot=(90, 0, 0), verts=48, bevel=0.02)
    G.T(lens, "#CFF3FF", name="Lens")
    x = [G.puffy(G.stroke([(cx - 0.26, cz + 0.26), (cx + 0.26, cz - 0.26)], 0.13), 0.04, y=-0.15),
         G.puffy(G.stroke([(cx - 0.26, cz - 0.26), (cx + 0.26, cz + 0.26)], 0.13), 0.04, y=-0.15)]
    G.T(x, G.RED, name="Mark")
    glint = G.puffy(G.stroke(G.arc(Rr - 0.13, 110, 160, 8, cx, cz), 0.07), 0.03, y=-0.16)
    G.T(glint, "#FFFFFF", name="Glint")
    a = math.radians(-50)
    d = Vector((math.cos(a), 0, math.sin(a)))
    p0 = Vector((cx, -0.12, cz)) + d * (Rr + 0.08)
    ferrule = G.rod(p0, p0 + d * 0.22, 0.12, verts=20)
    G.T(ferrule, G.AMBER_D, name="Ferrule")
    handle = G.rod(p0 + d * 0.2, p0 + d * 0.95, 0.13, verts=20, r_top=0.15)
    G._bevel(handle, 0.05, 3)
    G.T(handle, VINYL_DARK, name="Handle")
    G.face_cam(reveal=16, tilt=6)


VINYL_DARK = "#7A1E2A"


@hud("HUD_Shop")
def shop_bag():
    W, D, H = 1.36, 0.82, 1.5
    body = G.box((W, D, H), loc=(0, 0, H / 2), bevel=0.04, segs=2)
    G.T(body, G.PAPER, name="Bag")
    stripes = []
    for x in (-0.45, 0.0, 0.45):
        stripes.append(G.box((0.2, 0.03, H - 0.32), loc=(x, -D / 2 - 0.006, (H - 0.32) / 2 + 0.02), bevel=0.01, segs=1))
    for y in (-0.2, 0.2):
        stripes.append(G.box((0.03, 0.2, H - 0.32), loc=(-W / 2 - 0.006, y, (H - 0.32) / 2 + 0.02), bevel=0.01, segs=1))
    G.T(stripes, "#E23B3F", name="Stripe")
    cuff = G.box((W + 0.05, D + 0.05, 0.3), loc=(0, 0, H - 0.15), bevel=0.04, segs=2)
    G.T(cuff, "#E23B3F", name="Cuff")
    handles = []
    for y in (-D / 2 + 0.06, D / 2 - 0.06):
        pts = [(-0.34, y, H - 0.08), (-0.3, y, H + 0.3), (0.0, y, H + 0.5), (0.3, y, H + 0.3), (0.34, y, H - 0.08)]
        handles.append(G.tube(pts, 0.055, sides=10))
    G.T(handles, VINYL_DARK, name="Handle")
    st = G.cyl(0.29, 0.05, loc=(0, -D / 2 - 0.03, 0.62), rot=(90, 0, 0), verts=40, bevel=0.015)
    G.T(st, G.AMBER, name="Sticker")
    s_ = G.text("S", 0.42, 0.04, loc=(0, -D / 2 - 0.06, 0.62))
    G.T(s_, G.PAPER, name="StickerS")
    G.xform(G.tagged(), G.R(rz=-8))


def shirt_outline(body_w=0.64, sleeve=1.05, hem=-0.98, neck_drop=0.34):
    right = [(0.0, 0.72 - neck_drop), (0.2, 0.72), (0.56, 0.64), (sleeve, 0.28), (sleeve - 0.2, 0.0),
             (0.6, 0.16), (body_w, hem + 0.04), (body_w - 0.06, hem), (0.0, hem)]
    left = [(-x, z) for x, z in reversed(right[1:-1])]
    return G.fillet(right + left, 0.05, 2)


def hanger_hook(z_top=0.72, col=None):
    neck = G.box((0.34, 0.16, 0.12), loc=(0, 0.04, z_top + 0.0), bevel=0.04)
    G.T(neck, G.WOOD, name="HangerWood")
    hook = G.tube([(0, 0.04, z_top), (0, 0.04, z_top + 0.25), (0.04, 0.04, z_top + 0.42), (0.2, 0.04, z_top + 0.5),
                   (0.33, 0.04, z_top + 0.4), (0.3, 0.04, z_top + 0.27)], 0.04, sides=10)
    G.T(hook, col or G.CHROME, "Metal", name="Hook", gloss=0.3)


@hud("HUD_Uniforms")
def uniforms():
    SH = "#3E98E6"
    G.T(G.puffy(shirt_outline(), 0.34, puff=0.4), SH, name="Shirt")
    yf = -0.17
    collar = []
    for s in (1, -1):
        collar.append(G.puffy([(0.0, 0.36), (s * 0.24, 0.73), (s * 0.34, 0.5), (s * 0.06, 0.24)][::s], 0.07, y=yf - 0.03))
    G.T(collar, G.PAPER, name="Collar")
    cuffs = []
    for s in (1, -1):
        a, b = Vector((s * 1.05, 0.28)), Vector((s * 0.85, 0.0))
        d = Vector((-s * 0.45, 0.32)).normalized() * 0.18
        quad = [tuple(a), tuple(b), tuple(b + d), tuple(a + d)]
        if s < 0:
            quad = quad[::-1]
        cuffs.append(G.puffy(quad, 0.36, puff=0.3))
    G.T(cuffs, G.PAPER, name="Cuff")
    plack = G.puffy(G.rrect(0.1, 1.12, 0.04, cz=-0.4), 0.05, y=yf)
    G.T(plack, "#2F7FC8", name="Placket")
    buttons = [G.cyl(0.05, 0.05, loc=(0, yf - 0.03, z), rot=(90, 0, 0), verts=16, bevel=0.015) for z in (0.06, -0.3, -0.66)]
    G.T(buttons, G.PAPER, name="Button")
    pocket = G.puffy(G.rrect(0.32, 0.3, 0.05, cx=-0.34, cz=-0.12), 0.05, y=yf)
    G.T(pocket, "#2F7FC8", name="Pocket")
    tag = G.puffy(G.rrect(0.3, 0.13, 0.04, cx=0.34, cz=-0.06), 0.06, y=yf - 0.01)
    G.T(tag, G.RED, name="NameTag")
    hanger_hook()
    G.face_cam(reveal=14, tilt=6)


@hud("HUD_Quests")
def quests():
    G.T(G.slab(G.rrect(1.5, 1.95, 0.14), 0.12, bevel=0.04), G.WOOD, name="Board")
    G.T(G.slab(G.rrect(1.24, 1.56, 0.05, cz=-0.1), 0.04, bevel=0.01, y=-0.07), G.PAPER, name="Paper")
    clip = [G.puffy(G.rrect(0.78, 0.34, 0.1, cz=0.86), 0.16, y=-0.1),
            G.puffy_holes(G.rrect(0.44, 0.34, 0.12, cz=1.02), [G.rrect(0.22, 0.14, 0.06, cz=1.04)], 0.08, y=-0.1)]
    G.T(clip, G.STEEL, "Metal", name="Clip", gloss=0.35)
    for i, z in enumerate((0.38, -0.12, -0.62)):
        tick = G.puffy(G.stroke([(-0.5, z + 0.02), (-0.38, z - 0.1), (-0.14, z + 0.16)], 0.12), 0.1, y=-0.12)
        G.T(tick, G.GREEN_D if False else "#2FCB5A", name="Tick")
        line = G.slab(G.rrect(0.56, 0.1, 0.05, cx=0.24, cz=z), 0.03, y=-0.095)
        G.T(line, "#A39E92", name="Line")
    G.face_cam(reveal=14, tilt=8)


@hud("HUD_Daily")
def daily():
    page = [(-0.75, 0.55), (0.75, 0.55), (0.75, -0.42), (0.37, -0.8), (-0.75, -0.8)]
    G.T(G.slab(G.fillet(page, 0.1, 3), 0.22, bevel=0.035, segs=3), G.PAPER, name="Page")
    G.T(G.slab(G.rrect(1.5, 0.46, 0.12, cz=0.72), 0.3, bevel=0.06, segs=3), "#F0453A", name="Header")
    rings = [G.torus(0.13, 0.04, loc=(x, 0, 0.98), rot=(0, 90, 0), segs=20, rsegs=8) for x in (-0.4, 0.4)]
    G.T(rings, G.STEEL, "Metal", name="Binder", gloss=0.35)
    num = G.text("7", 0.95, 0.08, loc=(-0.06, -0.12, -0.1))
    G.T(num, G.INK_SOFT, name="Number")
    curl = G.slab(G.fillet([(0.37, -0.8), (0.75, -0.42), (0.3, -0.36)], 0.04, 2), 0.04, bevel=0.012, y=-0.13)
    G.T(curl, G.PAPER_D, name="Curl")
    G.face_cam(reveal=14, tilt=8)


def apron_outline(top=0.86, bib=0.36, waist=0.66, hem=-1.06, hem_w=0.7):
    right = [(0.0, top), (bib, top), (bib + 0.03, 0.6), (bib + 0.09, 0.4), (0.52, 0.24), (waist, 0.16),
             (hem_w, hem + 0.12), (hem_w - 0.1, hem), (0.0, hem - 0.02)]
    left = [(-x, z) for x, z in reversed(right[1:-1])]
    return G.fillet(right + left, 0.05, 2)


@hud("HUD_Cosmetics")
def cosmetics():
    G.T(G.puffy(apron_outline(), 0.24, puff=0.4), G.PINK, name="Apron")
    pocket = G.puffy(G.rrect(0.96, 0.4, 0.08, cz=-0.4), 0.06, y=-0.12)
    G.T(pocket, G.PINK_L, name="Pocket")
    seam = G.slab(G.rrect(0.05, 0.38, 0.02, cz=-0.4), 0.02, y=-0.155)
    trim = G.puffy(G.rrect(0.62, 0.09, 0.04, cz=0.74), 0.05, y=-0.12)
    G.T([seam, trim], G.PAPER, name="Trim")
    strap = G.tube([(-0.3, 0.0, 0.84), (-0.2, 0.0, 1.16), (0.0, -0.04, 1.33), (0.2, 0.0, 1.16), (0.3, 0.0, 0.84)], 0.05, sides=10)
    ties = [G.tube([(s * 0.64, 0.0, 0.16), (s * 0.8, -0.02, 0.0), (s * 0.78, -0.03, -0.3), (s * 0.88, -0.03, -0.55)], 0.045, sides=10)
            for s in (1, -1)]
    G.T([strap] + ties, G.PAPER, name="Strap")
    plate = G.slab(G.rrect(0.3, 0.42, 0.1, cz=1.42), 0.06, bevel=0.02, y=0.12)
    hook = G.tube([(0, 0.1, 1.33), (0, -0.06, 1.33), (0, -0.12, 1.4), (0, -0.13, 1.52)], 0.045, sides=10)
    knob = G.sphere(0.07, loc=(0, -0.13, 1.54))
    G.T([plate, hook, knob], G.CHROME, "Metal", name="WallHook", gloss=0.3)
    G.xform(G.tagged(), G.R(ry=4))
    G.face_cam(reveal=14, tilt=6)


@hud("HUD_Passes")
def passes():
    G.T(G.slab(G.rrect(1.36, 1.78, 0.16), 0.1, bevel=0.03), "#CFE6EE", name="Laminate", gloss=0.25)
    G.T(G.slab(G.rrect(1.2, 1.5, 0.1, cz=-0.06), 0.06, bevel=0.015, y=-0.04), G.PAPER, name="Card")
    G.T(G.slab(G.rrect(1.2, 0.5, 0.1, cz=0.44), 0.07, bevel=0.015, y=-0.045), G.VIOLET, name="Header")
    vip = G.text("VIP", 0.46, 0.06, loc=(0, -0.09, 0.44))
    G.fit_width(vip, 0.86)
    G.T(vip, G.AMBER, name="VIP")
    G.T(G.slab(G.rrect(0.42, 0.48, 0.05, cx=-0.32, cz=-0.32), 0.03, y=-0.075), G.BLUE, name="Photo")
    head = G.slab(G.circle(0.1, 20, -0.32, -0.22), 0.03, y=-0.09)
    sh = G.slab(G.arc(0.17, 0, 180, 10, -0.32, -0.56), 0.03, y=-0.09)
    G.T([head, sh], G.PAPER, name="Person")
    lines = [G.slab(G.rrect(w, 0.08, 0.04, cx=0.06 + w / 2, cz=z), 0.03, y=-0.075) for w, z in ((0.4, -0.2), (0.32, -0.36), (0.38, -0.52))]
    G.T(lines, "#A39E92", name="Lines")
    slot = G.slab(G.rrect(0.42, 0.1, 0.05, cz=0.78), 0.12, y=0.0)
    G.T(slot, G.INK_SOFT, name="Slot")
    clip = [G.box((0.22, 0.14, 0.24), loc=(0, 0, 1.0), bevel=0.05), G.torus(0.09, 0.03, loc=(0, 0, 1.17), rot=(0, 90, 0), segs=16, rsegs=6)]
    G.T(clip, G.STEEL, "Metal", name="Clip", gloss=0.35)
    straps = []
    for s in (1, -1):
        p0, p1 = Vector((s * 0.04, 0.0, 1.2)), Vector((s * 0.5, 0.06, 1.95))
        d = (p1 - p0)
        st = G.box((0.2, 0.04, d.length + 0.1), loc=(p0 + p1) / 2, bevel=0.015, segs=1)
        st.rotation_euler = (0, math.atan2(d.x, d.z), 0)
        straps.append(st)
    G.T(straps, G.VIOLET_D, name="Lanyard")
    G.xform(G.tagged(), G.R(ry=-7))
    G.face_cam(reveal=14, tilt=6)


@hud("HUD_Deals")
def deals():
    tag = [(-0.5, 0.62), (0.98, 0.62), (0.98, -0.62), (-0.5, -0.62), (-1.06, 0.0)]
    body = G.puffy_holes(G.fillet(tag, 0.14, 3), [G.circle(0.13, 20, -0.66, 0.0)], 0.24, puff=0.38)
    G.T(body, "#FFD877", name="Tag")
    eyelet = G.puffy_holes(G.circle(0.2, 24, -0.66, 0.0), [G.circle(0.13, 20, -0.66, 0.0)], 0.06, y=-0.12)
    G.T(eyelet, G.GOLD, name="Eyelet")
    pct = G.text("%", 1.25, 0.1, loc=(0.24, -0.13, 0.0))
    G.T(pct, "#E8323A", name="Percent")
    string = G.tube([(-0.66, 0.0, 0.0), (-0.95, 0.02, 0.18), (-1.3, 0.0, 0.5), (-1.42, -0.02, 0.85)], 0.04, sides=10)
    G.T(string, "#E8323A", name="String")
    G.xform(G.tagged(), G.R(ry=22))
    G.face_cam(reveal=14, tilt=6)


def _aim(objs, src=Vector((0, -1, 0)), dst=Vector((0, -1, 0)), about=(0, 0, 0)):
    q = Vector(src).rotation_difference(Vector(dst).normalized())
    M = G.Tm(*about) @ q.to_matrix().to_4x4() @ G.Tm(*(-Vector(about)))
    G.xform(objs, M)


@hud("HUD_Flashlight")
def flashlight():
    _, objs = G.build_foreign("A_kitchen", "Kitchen_Flashlight")
    for o in objs:
        if o.get("ns_role") == "lens":
            G.neon(o, "#FFF4C8", 6.0, name="Lens")
    halo = G.glow_mat(G.cyl(0.36, 0.01, loc=(0, -0.69, 0), rot=(90, 0, 0), verts=32, bevel=0), "#FFE89A", 2.5, 0.35)
    halo["g2_noframe"] = True
    allo = objs + [halo]
    _aim(allo, Vector((0, -1, 0)), Vector((0.62, -0.55, 0.45)))
    G.xform(allo, G.R(rz=-10))


def glove(fingers=((-0.33, 0.72, 4), (-0.11, 0.84, 1), (0.11, 0.8, -2), (0.33, 0.66, -6)), col=None, depth=0.36):
    col = col or G.PAPER
    parts = [G.puffy(G.rrect(0.96, 0.96, 0.36, cz=-0.22), depth, puff=0.42)]
    for x, L, ang in fingers:
        a = math.radians(90 + ang)
        p0 = (x, 0.1)
        p1 = (x + L * math.cos(a), 0.1 + L * math.sin(a))
        parts.append(G.puffy(G.stroke([p0, p1], 0.25), depth * 0.85, puff=0.45))
    parts.append(G.puffy(G.stroke([(-0.32, -0.3), (-0.62, -0.06), (-0.8, 0.2)], 0.27), depth * 0.85, puff=0.45))
    G.T(parts, col, name="Glove")
    return parts


@hud("HUD_Interact")
def interact():
    glove()
    cuff = G.puffy(G.rrect(1.06, 0.34, 0.14, cz=-0.82), 0.46, puff=0.4)
    G.T(cuff, G.CYAN, name="Cuff")
    lines = [G.slab(G.rrect(0.05, 0.36, 0.025, cx=x, cz=-0.24), 0.02, y=-0.19) for x in (-0.18, 0.0, 0.18)]
    G.T(lines, G.PAPER_D, name="Stitch")
    G.face_cam(reveal=14, tilt=6)


def sneaker(upper_col, accent, sole=None, w=0.56):
    """Chunky sneaker in side profile (toe to +X), built facing -Y; returns its parts."""
    sole = sole or G.PAPER
    up = [(-0.82, 0.14), (-0.88, 0.45), (-0.8, 0.82), (-0.56, 0.74), (-0.36, 0.68), (-0.18, 0.95), (0.02, 0.88),
          (0.4, 0.6), (0.72, 0.43), (0.9, 0.27), (0.88, 0.14)]
    parts = []
    u = G.puffy(G.fillet(up, 0.08, 3), w, puff=0.34)
    G.T(u, upper_col, name="Upper")
    parts.append(u)
    so = [(-0.86, 0.0), (0.82, 0.0), (0.94, 0.08), (0.92, 0.22), (0.8, 0.2), (-0.86, 0.2)]
    s = G.puffy(G.fillet(so, 0.06, 3), w + 0.06, puff=0.3)
    G.T(s, sole, name="Sole")
    toe = G.puffy(G.fillet([(0.44, 0.2), (0.86, 0.2), (0.82, 0.38), (0.6, 0.48)], 0.08, 3), w + 0.02, puff=0.4)
    G.T(toe, sole, name="Toecap")
    swoosh = G.puffy(G.stroke(G.smooth_path([(-0.6, 0.3), (-0.2, 0.36), (0.25, 0.52)], 4), 0.13), 0.05, y=-w / 2 + 0.005)
    G.T(swoosh, accent, name="Swoosh")
    laces = [G.puffy(G.stroke([(x - 0.07, z - 0.05), (x + 0.07, z + 0.05)], 0.07), w * 0.75, puff=0.4)
             for x, z in ((0.02, 0.84), (0.18, 0.74), (0.34, 0.64))]
    G.T(laces, sole, name="Lace")
    collar = G.puffy(G.stroke([(-0.8, 0.8), (-0.56, 0.72), (-0.36, 0.66)], 0.09), w + 0.02, puff=0.4)
    G.T(collar, accent, name="Collar")
    return [u, s, toe, swoosh, collar] + laces


@hud("HUD_Crouch")
def crouch():
    tip = Vector((0.92, 0, 0.04))
    front = sneaker(G.VIOLET, G.CYAN)
    G.xform(front, G.R(ry=38, about=tip))
    back = sneaker(G.VIOLET_D, G.CYAN)
    G.xform(back, G.R(ry=34, about=tip))
    G.xform(back, G.Tm(-1.0, 0.55, 0.0))
    # the floor strip both toes rest on (heels clearly off the ground)
    floor = G.box((2.3, 1.45, 0.07), loc=(0.15, 0.28, -0.035), bevel=0.03, segs=2)
    G.T(floor, "#2A8FA6", name="Ground")
    G.face_cam(reveal=12, tilt=0)


@hud("HUD_Sprint")
def sprint():
    s = sneaker(G.BRAND, G.AMBER)
    G.xform(s, G.R(ry=-12, about=(0, 0, 0)))
    streaks = [G.puffy(G.stroke([(-1.0 - L, z), (-1.0, z)], 0.13), 0.12) for L, z in ((0.55, 0.55), (0.8, 0.32), (0.45, 0.1))]
    G.T(streaks, G.CYAN, name="Streak")
    G.face_cam(reveal=24, tilt=6)


@hud("HUD_Ping")
def ping():
    c, r = (0.0, 0.32), 0.74
    a0 = math.degrees(math.asin(0.0)) - 38
    outline = G.arc(r, -38, 218, 40, c[0], c[1]) + [(-0.12, -1.0), (0.0, -1.16), (0.12, -1.0)]
    G.T(G.puffy(G.fillet(outline, 0.04, 2), 0.56, puff=0.45), G.CYAN, name="Pin")
    G.T(G.puffy(G.circle(0.3, 32, c[0], c[1]), 0.12, y=-0.28), G.PAPER, name="Dot")
    ring = G.torus(0.46, 0.06, loc=(0, 0, -1.16), segs=40, rsegs=8, scale=(1, 1, 1))
    G.T(ring, "#1BA9C2", name="Ground")
    G.face_cam(reveal=14, tilt=6)


@hud("HUD_Rattle")
def rattle():
    d = Vector((math.cos(math.radians(-55)), 0, math.sin(math.radians(-55))))
    start = Vector((-0.55, 0, 0.9))
    links = []
    for i in range(4):
        c = start + d * 0.8 * i
        L = G.torus(0.3, 0.1, segs=36, rsegs=12)
        L.scale = (1.55, 1.0, 1.0)
        G.apply(L)
        # long axis along d; alternate links turned 90 deg about it
        ang = math.atan2(d.z, d.x)
        M = G.Tm(*c) @ G.R(ry=-math.degrees(ang)) @ G.R(rx=90 if i % 2 == 0 else 0)
        G.xform(L, M)
        links.append(L)
    G.T(links, "#C9D0D8", "Metal", name="Link", gloss=0.32)
    shackle = G.torus(0.26, 0.09, loc=start - d * 0.62, rot=(90, 0, 0), segs=32, rsegs=10)
    G.T(shackle, "#C9D0D8", "Metal", name="Link", gloss=0.32)
    arcs = []
    for s, cx, cz in ((1, 0.55, 0.55), (-1, -0.75, -0.25)):
        for k, rr in enumerate((0.32, 0.52)):
            a0, a1 = (-30, 50) if s > 0 else (150, 230)
            arcs.append(G.puffy(G.stroke(G.arc(rr, a0, a1, 10, cx, cz), 0.085), 0.08))
    G.T(arcs, G.CYAN, name="Rattle")
    G.face_cam(reveal=14, tilt=6)


def ghost_outline(w=0.86, top=0.3, bottom=-0.86, waves=3, arms=True):
    pts = G.arc(w, 0, 180, 24, 0, top)
    pts += [(-w - 0.02, top - 0.4)]
    if arms:
        pts += [(-w - 0.26, -0.12), (-w - 0.3, -0.26), (-w - 0.02, -0.3)]
    pts += [(-w, bottom + 0.12)]
    span = 2 * w
    n = waves * 2
    for i in range(1, n + 1):
        x = -w + span * i / n
        z = bottom + (0.0 if i % 2 == 1 else 0.14)
        pts += [(x - span / n / 2, bottom - 0.02 + (0.12 if i % 2 == 0 else 0.0)), (x, z)]
    pts += [(w, bottom + 0.12)]
    if arms:
        pts += [(w + 0.02, -0.3), (w + 0.3, -0.18), (w + 0.26, -0.02)]
    pts += [(w + 0.02, top - 0.4)]
    return G.smooth_path(pts, 3, closed=True)


@hud("HUD_Spook")
def spook():
    G.T(G.puffy(ghost_outline(), 0.6, puff=0.46), "#EEF5FF", name="Ghost")
    eyes = [G.puffy(G.circle(0.13, 24, x, 0.36, rz=0.19), 0.1, y=-0.3) for x in (-0.3, 0.3)]
    mouth = G.puffy(G.circle(0.13, 24, 0.0, -0.1, rz=0.16), 0.1, y=-0.3)
    G.T(eyes + [mouth], G.INK_SOFT, name="Face")
    cheeks = [G.puffy(G.circle(0.09, 16, x, 0.08, rz=0.06), 0.06, y=-0.3) for x in (-0.52, 0.52)]
    G.T(cheeks, G.PINK_L, name="Blush")
    G.xform(G.tagged(), G.R(ry=-8))
    G.face_cam(reveal=14, tilt=6)


def toast_slice(w=0.92, h=0.98, depth=0.16, crust="#B8722F", crumb="#F4D59C"):
    """Bread slice outline (two-lobed top) facing -Y, centred, bottom at z = -h/2."""
    out = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2 - 0.3)]
    out += G.arc(0.27, -20, 160, 10, w / 2 - 0.22, h / 2 - 0.28)
    out += G.arc(0.27, 20, 200, 10, -w / 2 + 0.22, h / 2 - 0.28)
    out = G.fillet(out, 0.06, 2)
    c = G.puffy(out, depth, puff=0.35)
    G.T(c, crust, name="Crust")
    inner = [(x * 0.8, z * 0.8 - 0.02) for x, z in out]
    m = [G.slab(inner, depth + 0.02, bevel=0.01)]
    G.T(m, crumb, name="Crumb")
    return [c] + m


@hud("HUD_Toaster")
def toaster():
    W, D, H = 1.6, 0.92, 1.0
    body = G.box((W, D, H), loc=(0, 0, H / 2 + 0.12), bevel=0.0)
    G._bevel(body, 0.32, 6, angle=30)
    for y in (-0.18, 0.18):
        G.boolean(body, G.box((1.1, 0.13, 0.6), loc=(0, y, H + 0.12), bevel=0.0))
    G._bevel(body, 0.02, 2)
    G.T(body, "#DCE2E7", "Metal", name="Chrome", gloss=0.28)
    base = G.box((W + 0.1, D + 0.1, 0.2), loc=(0, 0, 0.1), bevel=0.08, segs=3)
    G.T(base, G.VINYL_RED, name="Base")
    slotin = [G.box((1.08, 0.11, 0.06), loc=(0, y, H + 0.06), bevel=0.0) for y in (-0.18, 0.18)]
    G.T(slotin, G.INK_SOFT, name="SlotDark")
    lever = [G.box((0.08, 0.1, 0.42), loc=(-W / 2 - 0.02, 0.0, 0.62), bevel=0.03), G.box((0.2, 0.26, 0.14), loc=(-W / 2 - 0.1, 0.0, 0.72), bevel=0.05)]
    G.T(lever, G.INK_SOFT, name="Lever")
    knob = G.cyl(0.11, 0.08, loc=(-W / 2 - 0.02, 0.0, 0.32), rot=(0, 90, 0), verts=20, bevel=0.03)
    G.T(knob, G.VINYL_RED, name="Knob")
    s1 = toast_slice()
    G.xform(s1, G.Tm(-0.12, -0.18, H + 0.62) @ G.R(ry=-10))
    s2 = toast_slice()
    G.xform(s2, G.Tm(0.08, 0.18, H + 0.2) @ G.R(ry=4))
    G.xform(G.tagged(), G.R(rz=-6))


@hud("HUD_Wrapped")
def wrapped():
    _, objs = G.build_foreign("A_food", "Food_WrappedSandwich")
    G.xform(objs, G.R(rz=8) @ G.R(ry=-8))


@hud("HUD_Gift")
def gift():
    Bw, Bh = 1.3, 1.08
    G.T(G.box((Bw, Bw, Bh), loc=(0, 0, Bh / 2), bevel=0.06), G.VIOLET, name="Box")
    G.T(G.box((Bw + 0.12, Bw + 0.12, 0.3), loc=(0, 0, Bh + 0.1), bevel=0.07), "#AE7BFF", name="Lid")
    rib = [G.box((0.28, Bw + 0.04, Bh), loc=(0, 0, Bh / 2), bevel=0.02, segs=1),
           G.box((Bw + 0.04, 0.28, Bh), loc=(0, 0, Bh / 2), bevel=0.02, segs=1),
           G.box((0.3, Bw + 0.16, 0.34), loc=(0, 0, Bh + 0.1), bevel=0.03, segs=1),
           G.box((Bw + 0.16, 0.3, 0.34), loc=(0, 0, Bh + 0.1), bevel=0.03, segs=1)]
    G.T(rib, G.AMBER, name="Ribbon")
    top = Bh + 0.27
    loops = []
    for s in (1, -1):
        L = G.torus(0.28, 0.09, segs=32, rsegs=10)
        L.scale = (1.35, 1.0, 0.75)
        G.apply(L)
        G.xform(L, G.Tm(s * 0.34, 0, top + 0.2) @ G.R(ry=-s * 28) @ G.R(rx=90))
        loops.append(L)
    knot = G.sphere(0.16, loc=(0, -0.02, top + 0.1), scale=(1.1, 1.0, 0.9))
    tails = [G.puffy([(0.0, 0.0), (s * 0.22, -0.36), (s * 0.1, -0.3), (s * 0.02, -0.44), (-s * 0.08, -0.06)][::s], 0.06)
             for s in (1, -1)]
    G.xform(tails, G.Tm(0, -Bw / 2 - 0.1, top))
    G.T(loops + [knot] + tails, G.AMBER, name="Bow")
    G.xform(G.tagged(), G.R(rz=8))


def key_shape(L=1.05, head_r=0.27, teeth=((0.62, 0.12), (0.76, 0.2), (0.9, 0.1)), col=None, head_col=None, depth=0.13):
    """One key (head ring at the origin, blade along -Z), facing -Y."""
    parts = []
    head = G.puffy_holes(G.circle(head_r, 36), [G.circle(0.09, 20, 0, 0.08)], depth, puff=0.35)
    G.T(head, head_col or col, name="KeyHead")
    blade = G.puffy(G.rrect(0.16, L, 0.05, cz=-head_r - L / 2 + 0.06), depth * 0.85, puff=0.3)
    tooth = []
    for z, w in teeth:
        tooth.append(G.puffy(G.rrect(w + 0.08, 0.11, 0.03, cx=0.08 + w / 2 - 0.04, cz=-head_r - z + 0.06), depth * 0.85, puff=0.3))
    G.T([blade] + tooth, col, name="KeyBlade")
    return [head, blade] + tooth


@hud("HUD_Keys")
def keys():
    keyring(((G.GOLD, None, -28), (G.STEEL, None, 4), ("#E8B23A", G.VINYL_RED, 34)))
    G.face_cam(reveal=16, tilt=6)


def keyring(spec, ring_r=0.44, tilt=62):
    ring = G.torus(ring_r, 0.06, segs=48, rsegs=10)
    M = G.Tm(0, 0, 0.75) @ G.R(rx=90 - tilt)
    G.xform(ring, M @ G.R(rx=90))
    G.T(ring, G.CHROME, "Metal", name="KeyRing", gloss=0.3)
    out = []
    for i, (col, head_col, ang) in enumerate(spec):
        a = math.radians(-90 + ang * 0.9)
        p = M @ Vector((ring_r * math.cos(a), 0, ring_r * math.sin(a)))
        k = key_shape(col=col, head_col=head_col)
        G.xform(k, G.Tm(*p) @ G.R(ry=-ang) @ G.Tm(0, 0, -0.08) @ G.R(rz=8 * (i - 1)))
        out += k
    return out


@hud("HUD_Level")
def level():
    pts = [(-0.88, 0.92), (-0.3, 1.02), (0.0, 1.1), (0.3, 1.02), (0.88, 0.92), (0.86, 0.1), (0.62, -0.5), (0.0, -1.1),
           (-0.62, -0.5), (-0.86, 0.1)]
    outline = G.smooth_path(pts, 4, closed=True)
    G.T(G.puffy(outline, 0.42, puff=0.4), G.GOLD, name="Shield")
    inner = [(x * 0.8, z * 0.8 + 0.01) for x, z in outline]
    G.T(G.puffy(inner, 0.1, y=-0.2), G.BLUE, name="Field")
    G.T(G.puffy(G.fillet(G.star(5, 0.56, 0.25, cz=0.0), 0.04, 2), 0.16, y=-0.26), G.GOLD, name="Star")
    G.face_cam(reveal=14, tilt=6)


def wrench_head(cx, cz, r=0.44, axis_deg=45.0, slot_w=0.17, slot_d=0.42):
    phi = math.degrees(math.asin(slot_w / r))
    pts = G.arc(r, axis_deg + phi, axis_deg + 360 - phi, 40, cx, cz)
    d = Vector((math.cos(math.radians(axis_deg)), math.sin(math.radians(axis_deg))))
    pp = Vector((-d.y, d.x))
    c = Vector((cx, cz))
    base = c + d * (r - slot_d)
    pts += [tuple(base - pp * slot_w), tuple(base - d * 0.06), tuple(base + pp * slot_w)]
    return G.fillet(pts, 0.03, 2)


@hud("HUD_Dev")
def dev():
    head = G.puffy(wrench_head(0.62, 0.62), 0.24, puff=0.35)
    ring = G.puffy_holes(G.circle(0.33, 36, -0.78, -0.78), [G.circle(0.15, 24, -0.78, -0.78)], 0.22, puff=0.35)
    shaft = G.puffy(G.stroke([(-0.7, -0.7), (0.5, 0.5)], 0.3), 0.2, puff=0.35)
    G.T([head, ring, shaft], "#C9D0D8", "Metal", name="Wrench", gloss=0.32)
    grip = G.puffy(G.stroke([(-0.42, -0.42), (0.12, 0.12)], 0.38), 0.27, puff=0.45)
    G.T(grip, G.CYAN, name="Grip")
    G.face_cam(reveal=16, tilt=6)
