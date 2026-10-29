"""fam_tags — ingredient flavour tags (group "hud"): Tag_<Tag>, shown at ~20 px on Cook View cards.

One coherent family: a single chunky soft-plastic glyph per tag, one main colour (+ at most
one detail colour), same depth and puff, the shared "tags" camera nearly face-on (reveal 10).
"""
from __future__ import annotations

import math

import _common as G
from _common import Vector

FAM = "tags"
DEPTH = 0.46


def tag(name):
    def deco(fn):
        def build():
            fn()
            G.face_cam(reveal=10, tilt=4)
        G.icon(f"Tag_{name}", "hud", FAM)(build)
        return fn
    return deco


def front(d=DEPTH):
    return -d / 2


def teardrop(r=0.78, cz=-0.28, tip=1.16):
    L = tip - cz
    al = math.degrees(math.acos(r / L))
    pts = G.arc(r, 90 + al, 90 - al + 360, 40, 0, cz)
    pts.append((0.0, tip))
    return G.fillet(pts, 0.05, 3)


def crescent(rA=1.0, b=(0.5, 0.32), rB=0.86, n=72):
    a = Vector((0, 0))
    bv = Vector(b)
    d = (bv - a).length
    u = (bv - a) / d
    x = (d * d - rB * rB + rA * rA) / (2 * d)
    h = math.sqrt(max(rA * rA - x * x, 0))
    perp = Vector((-u.y, u.x))
    P1, P2 = a + u * x + perp * h, a + u * x - perp * h
    tA1, tA2 = math.atan2(P1.y, P1.x), math.atan2(P2.y, P2.x)
    # outer arc of A: from P1 CCW to P2, the long way round (away from B)
    while tA2 < tA1:
        tA2 += 2 * math.pi
    pts = [(rA * math.cos(tA1 + (tA2 - tA1) * i / n), rA * math.sin(tA1 + (tA2 - tA1) * i / n)) for i in range(n + 1)]
    tB2, tB1 = math.atan2(P2.y - bv.y, P2.x - bv.x), math.atan2(P1.y - bv.y, P1.x - bv.x)
    while tB1 > tB2:
        tB1 -= 2 * math.pi
    # inner arc of B from P2 back to P1 (clockwise, the side inside A)
    m = n // 2
    for i in range(1, m):
        t = tB2 - (tB2 - tB1) * i / m
        pts.append((bv.x + rB * math.cos(t), bv.y + rB * math.sin(t)))
    return G.fillet(pts, 0.04, 2)


# ---- tags -------------------------------------------------------------------------------------

@tag("Bloody")
def bloody():
    G.T(G.puffy(teardrop(), 0.6, puff=0.46), "#E01E37", name="Drop")
    hl = G.puffy(G.stroke(G.arc(0.5, 140, 200, 8, 0, -0.28), 0.12), 0.06, y=-0.3)
    G.T(hl, "#FF8A95", name="Shine")


@tag("Cheesy")
def cheesy():
    tri = G.fillet([(-1.0, -0.62), (1.0, -0.62), (1.0, 0.62)], 0.08, 3)
    holes = [G.circle(0.16, 20, 0.52, -0.2), G.circle(0.1, 16, 0.1, -0.36), G.circle(0.09, 16, 0.72, 0.22)]
    G.T(G.slab_holes(tri, holes, 0.8, bevel=0.1, segs=3), "#FFB52E", name="Wedge")


@tag("Creamy")
def creamy():
    prof = [(0.0, 0.0), (0.92, 0.0), (1.0, 0.12), (0.96, 0.28), (0.8, 0.38), (0.66, 0.4), (0.76, 0.5), (0.76, 0.66),
            (0.6, 0.76), (0.46, 0.78), (0.54, 0.9), (0.5, 1.04), (0.34, 1.13), (0.2, 1.18), (0.18, 1.3), (0.06, 1.46), (0.0, 1.5)]
    d = G.lathe(prof, verts=36)
    G.T(d, "#FFF1D6", name="Cream", smooth=70)
    G.xform(d, G.R(rx=-14))


@tag("Crunchy")
def crunchy():
    shards = [
        ([(-0.18, -0.9), (0.3, -0.85), (0.42, 0.25), (0.1, 1.05), (-0.3, 0.3)], (0, 0, 0)),
        ([(-0.3, -0.5), (0.25, -0.62), (0.3, 0.15), (-0.1, 0.62)], (0, 0, 0)),
        ([(-0.25, -0.55), (0.3, -0.45), (0.18, 0.5), (-0.28, 0.2)], (0, 0, 0)),
    ]
    out = []
    for (pts, _), (x, z, a, col) in zip(shards, ((0.0, 0.0, 0, "#E9A93A"), (-0.78, -0.25, 28, "#D9922E"), (0.76, -0.3, -32, "#F2BC55"))):
        o = G.slab(G.fillet(pts, 0.04, 1), 0.36, bevel=0.06, segs=2)
        G.xform(o, G.Tm(x, 0, z) @ G.R(ry=a))
        G.T(o, col, name="Shard", smooth=20)
        out.append(o)
    crumbs = [G.box((s, s, s), loc=(x, -0.05, z), rot=(20, 30, 40), bevel=0.02, segs=1) for x, z, s in ((-0.4, -0.95, 0.14), (0.42, -0.98, 0.12))]
    G.T(crumbs, "#D9922E", name="Crumb", smooth=20)


@tag("Crusty")
def crusty():
    loaf = G.sphere(1.0, scale=(1.2, 0.66, 0.66), segs=32, rings=18)
    G.T(loaf, "#C7782F", name="Loaf", smooth=70)
    base = G.box((2.06, 1.06, 0.22), loc=(0, 0, -0.42), bevel=0.09)
    G.T(base, "#A9611F", name="Base")
    cuts = []
    for x in (-0.62, 0.0, 0.62):
        pts = []
        for i in range(9):
            t = i / 8 - 0.5
            px, py = x + t * 0.5, t * 0.86
            q = 1 - (px / 1.2) ** 2 - (py / 0.66) ** 2
            pts.append((px, py, 0.66 * math.sqrt(max(q, 0.0)) - 0.01))
        cuts.append(G.tube(pts, [0.03, 0.06, 0.08, 0.085, 0.085, 0.085, 0.08, 0.06, 0.03], sides=10, res=2))
    G.T(cuts, "#F6CF8A", name="Score")
    G.xform(G.tagged(), G.R(rx=30))


@tag("Cursed")
def cursed():
    skull = G.puffy(G.smooth_path([(-0.88, 0.25), (-0.8, 0.75), (-0.4, 1.08), (0.4, 1.08), (0.8, 0.75), (0.88, 0.25),
                                   (0.62, -0.18), (0.55, -0.55), (0.3, -0.72), (-0.3, -0.72), (-0.55, -0.55), (-0.62, -0.18)], 4,
                                  closed=True), 0.6, puff=0.42)
    G.T(skull, "#EFE8DA", name="Skull")
    eyes = [G.puffy(G.circle(0.24, 24, x, 0.22, rz=0.27), 0.1, y=-0.29) for x in (-0.36, 0.36)]
    G.T(eyes, "#2A1418", name="Socket")
    glow = [G.puffy(G.circle(0.1, 16, x, 0.2), 0.08, y=-0.33) for x in (-0.36, 0.36)]
    G.neon(glow, G.RED, 5.0, name="EyeGlow")
    nose = G.puffy(G.fillet([(0, -0.08), (-0.11, -0.28), (0.11, -0.28)], 0.03, 2), 0.08, y=-0.29)
    teeth = [G.puffy(G.rrect(0.06, 0.2, 0.03, cx=x, cz=-0.52), 0.08, y=-0.29) for x in (-0.2, 0.0, 0.2)]
    G.T([nose] + teeth, "#2A1418", name="Teeth")


@tag("Dark")
def dark():
    G.T(G.puffy(crescent(), 0.52, puff=0.44), G.VIOLET, name="Moon")
    G.xform(G.tagged(), G.R(ry=-18))


@tag("Earthy")
def earthy():
    mound = G.puffy(G.arc(1.0, 0, 180, 24, 0, -0.62) + [(-1.0, -0.72), (1.0, -0.72)], DEPTH * 1.6, puff=0.4)
    G.T(mound, "#8A5A3B", name="Soil")
    stem = G.puffy(G.stroke(G.smooth_path([(0.0, 0.2), (0.05, 0.6), (-0.02, 0.9)], 4), 0.13), 0.14)
    leaves = [G.puffy(G.smooth_path([(0.0, 0.0), (0.25, 0.22), (0.62, 0.22), (0.78, 0.02), (0.5, -0.08), (0.2, -0.06)], 4, closed=True), 0.16)
              for _ in range(2)]
    G.xform(leaves[0], G.Tm(0.0, 0, 0.86) @ G.R(ry=-18))
    G.xform(leaves[1], G.Tm(0.0, 0, 0.8) @ G.S((-1, 1, 1)) @ G.R(ry=-12))
    G.T([stem] + leaves, "#57C84A", name="Sprout")
    pebbles = [G.sphere(0.09, loc=(x, -0.5, z), scale=(1.3, 1, 0.9)) for x, z in ((-0.45, -0.25), (0.42, -0.4), (0.1, -0.5))]
    G.T(pebbles, "#B98A5E", name="Pebble")


@tag("Fresh")
def fresh():
    leaf = G.smooth_path([(-0.95, -0.85), (-0.85, 0.05), (-0.35, 0.72), (0.4, 1.0), (0.95, 0.95), (0.85, 0.3), (0.35, -0.45),
                          (-0.35, -0.85)], 4, closed=True)
    G.T(G.puffy(leaf, 0.36, puff=0.42), "#3FCB55", name="Leaf")
    rib = G.puffy(G.stroke(G.smooth_path([(-0.88, -0.8), (-0.1, 0.0), (0.82, 0.88)], 6), 0.08), 0.06, y=-0.17)
    veins = [G.puffy(G.stroke([(x, z), (x + dx, z + dz)], 0.06), 0.05, y=-0.17)
             for x, z, dx, dz in ((-0.4, -0.3, -0.28, 0.32), (0.05, 0.12, -0.26, 0.36), (0.4, 0.45, -0.18, 0.3), (-0.3, -0.2, 0.36, -0.2), (0.1, 0.2, 0.34, -0.2))]
    G.T([rib] + veins, "#A6F28F", name="Vein")
    drop = G.puffy(teardrop(0.22, -0.08, 0.3), 0.2, y=-0.22)
    G.xform(drop, G.Tm(0.38, 0, -0.5))
    G.T(drop, "#8FEFFF", name="Dew")


@tag("Glowing")
def glowing():
    orb = G.sphere(0.9, segs=32, rings=18)
    G.T(orb, "#38E83A", "Neon", name="Orb", emit=1.6)
    hi = G.sphere(0.2, loc=(-0.32, -0.74, 0.36), scale=(1.0, 0.5, 0.8), segs=16, rings=10)
    G.neon(hi, "#F2FFE8", 4.0, name="Spec")
    G.glow_mat(G.sphere(1.25, segs=32, rings=18), "#5CFF4A", 1.8, 0.6, falloff=1.6)


@tag("Hearty")
def hearty():
    G.T(G.puffy(G.heart(1.0, 72), 0.62, puff=0.46), "#FF5A45", name="Heart")
    hl = G.puffy(G.stroke(G.arc(0.36, 110, 170, 8, -0.45, 0.25), 0.12), 0.05, y=-0.31)
    G.T(hl, "#FFB1A3", name="Shine")


@tag("Holey")
def holey():
    sq = G.fillet([(-0.95, -0.9), (0.95, -0.9), (0.95, 0.9), (-0.95, 0.9)], 0.14, 3)
    holes = [G.circle(0.26, 24, -0.38, 0.36), G.circle(0.18, 20, 0.45, 0.48), G.circle(0.22, 22, 0.32, -0.36),
             G.circle(0.13, 16, -0.45, -0.42), G.circle(0.1, 14, 0.0, 0.02)]
    G.T(G.slab_holes(sq, holes, 0.3, bevel=0.08, segs=3), "#FFE9A6", name="Swiss")
    G.xform(G.tagged(), G.R(ry=-8))


@tag("Meaty")
def meaty():
    meat = G.puffy(G.smooth_path([(-0.95, 0.6), (-0.6, 1.0), (-0.05, 0.95), (0.35, 0.55), (0.32, 0.12), (-0.1, -0.12),
                                  (-0.6, -0.05), (-0.95, 0.2)], 4, closed=True), 0.7, puff=0.45)
    G.T(meat, "#B8622E", name="Meat")
    bone = G.puffy(G.stroke([(0.15, 0.25), (0.72, -0.48)], 0.24), 0.26, puff=0.4)
    knobs = [G.puffy(G.circle(0.17, 20, 0.62 + dx, -0.6 + dz), 0.3, puff=0.45) for dx, dz in ((0.2, 0.06), (-0.04, -0.18))]
    G.T([bone] + knobs, "#F3EEE2", name="Bone")
    sheen = G.puffy(G.stroke(G.smooth_path([(-0.7, 0.55), (-0.45, 0.8), (-0.1, 0.8)], 4), 0.1), 0.05, y=-0.35)
    G.T(sheen, "#E08A4F", name="Sheen")


@tag("Salty")
def salty():
    for (x, z, s, r) in ((-0.42, -0.25, 0.8, (12, 20, 35)), (0.5, -0.32, 0.64, (-20, 10, -25)), (0.08, 0.5, 0.56, (30, -25, 15))):
        c = G.box((s, s, s), loc=(x, 0, z), rot=r, bevel=0.06, segs=2)
        G.T(c, "#F2F6FA", name="Crystal", smooth=20)
    G.T(G.box((0.2, 0.2, 0.2), loc=(-0.85, -0.2, 0.4), rot=(40, 20, 10), bevel=0.03, segs=1), "#DCE8F2", name="Grain", smooth=20)


@tag("Sharp")
def sharp():
    blade = [(-0.72, -0.5), (-0.36, -0.9), (0.42, -0.12), (1.0, 1.0), (-0.22, 0.32)]
    o = G.slab(G.fillet(blade, 0.04, 2), 0.2, bevel=0.06, segs=2)
    G.T(o, "#D6DCE2", "Metal", name="Blade", gloss=0.3, smooth=25)
    edge = G.slab([(-0.36, -0.9), (0.42, -0.12), (1.0, 1.0), (0.28, -0.2), (-0.44, -0.8)], 0.21, bevel=0.0)
    G.T(edge, "#F4F7FA", "Metal", name="Edge", gloss=0.25, smooth=25)
    handle = G.puffy(G.stroke([(-0.62, -0.78), (-0.98, -1.12)], 0.42), 0.36, puff=0.4)
    G.T(handle, "#5A3624", name="Handle")
    spark = G.puffy(G.fillet(G.star(4, 0.36, 0.09, a0=90, cx=0.84, cz=0.5), 0.02, 1), 0.08, y=-0.15)
    G.T(spark, "#FFFFFF", name="Glint")


@tag("Smoky")
def smoky():
    puffs = [(-0.34, -0.62, 0.5, "#868C97"), (0.28, -0.3, 0.42, "#969CA6"), (-0.08, 0.24, 0.35, "#A8AEB7"),
             (0.3, 0.7, 0.26, "#BBC0C8"), (0.04, 1.04, 0.16, "#CED2D8")]
    for i, (x, z, r, col) in enumerate(puffs):
        o = G.puffy(G.circle(r, 36, x, z), 0.5 * r + 0.12, puff=0.46, y=0.02 * i)
        G.T(o, col, name="Puff")


@tag("Soft")
def soft():
    cloud = [(-1.0, -0.42), (1.0, -0.42)]
    cloud += G.arc(0.42, -60, 100, 10, 0.62, -0.05)
    cloud += G.arc(0.58, 20, 160, 12, 0.02, 0.22)
    cloud += G.arc(0.4, 80, 240, 10, -0.6, 0.0)
    G.T(G.puffy(G.fillet(cloud, 0.08, 3), 0.7, puff=0.47), "#F4F2FA", name="Cloud")


@tag("Spicy")
def spicy():
    path = [(-0.8, 0.55, 0), (-0.25, 0.35, 0), (0.25, -0.05, 0), (0.55, -0.55, 0), (0.62, -1.0, 0)]
    body = G.tube([(x, y, z) for x, z, y in path], [0.36, 0.34, 0.28, 0.17, 0.04], sides=16, res=6)
    G.T(body, "#E8302A", name="Chili", smooth=70)
    cap = G.sphere(0.3, loc=(-0.86, 0, 0.58), scale=(0.7, 1.0, 1.0), segs=20, rings=10)
    stem = G.tube([(-0.95, 0, 0.62), (-1.15, 0, 0.78), (-1.12, 0, 1.0)], [0.08, 0.07, 0.06], sides=10)
    G.T([cap, stem], "#3FA83A", name="Stem")
    hl = G.tube([(-0.55, -0.3, 0.62), (-0.1, -0.29, 0.42), (0.2, -0.22, 0.12)], [0.05, 0.06, 0.03], sides=8)
    G.T(hl, "#FF8C80", name="Shine")


@tag("Tangy")
def tangy():
    rind = G.arc(1.0, 180, 360, 32, 0, 0.3)
    G.T(G.slab(rind, 0.5, bevel=0.1, segs=3), "#FFD43A", name="Rind")
    pith = G.slab(G.arc(0.86, 180, 360, 30, 0, 0.3), 0.08, y=-0.26)
    G.T(pith, "#FFF8E6", name="Pith")
    segs = []
    for i in range(4):
        a0, a1 = 180 + 45 * i + 5, 180 + 45 * (i + 1) - 5
        pts = [(0.06 * math.cos(math.radians((a0 + a1) / 2)), 0.3 + 0.06 * math.sin(math.radians((a0 + a1) / 2)))]
        pts += G.arc(0.74, a0, a1, 8, 0, 0.3)
        segs.append(G.puffy(G.fillet(pts, 0.04, 2), 0.1, y=-0.3))
    G.T(segs, "#FFE873", name="Flesh")
    G.xform(G.tagged(), G.R(ry=-14))
