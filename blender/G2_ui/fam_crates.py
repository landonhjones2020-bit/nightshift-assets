"""fam_crates — the five supply-crate glyphs (group "hud"): HUD_Crate_<Type>.

Each is the game's one Kitchen_Crate mesh (blender/gate/Kitchen_Crate.py, built by its own
build()), recoloured with that type's runtime body/trim colours, with a hint of its contents
peeking over the rim (modelled here; sauce bottles reuse A_food's squeeze_bottle). Shared
"crates" camera = the crate's natural 3/4.
"""
from __future__ import annotations

import math
import random

import _common as G
from _common import ns, Vector

FAM = "crates"
TYPES = {
    "Meat": ("#B33A3A", "#7E2525"),
    "Cheese": ("#F2C53D", "#B89220"),
    "Veg": ("#4FA04A", "#3B7D37"),
    "Bread": ("#C69C6D", "#8E6A44"),
    "Sauce": ("#E26A2C", "#A84A1C"),
}
TOP = 1.0          # crate rim height (Kitchen_Crate H)


def crate(kind):
    body, trim = TYPES[kind]
    _, objs = G.build_foreign("gate", "Kitchen_Crate")
    for o in objs:
        role = o.get("ns_role")
        col = {"crate_body": body, "crate_trim": trim}.get(role)
        if col:
            o["ns_color"] = col
            o.data.materials.clear()
            o.data.materials.append(ns.material(col, "SmoothPlastic"))
    # dark interior floor so the contents read as "inside"
    G.T(G.box((1.78, 1.18, 0.02), loc=(0, 0, 0.11), bevel=0.0), G.INK_SOFT, name="Shadow")
    return objs


def crate_icon(kind, contents):
    def build():
        crate(kind)
        contents()
        G.xform(G.tagged(), G.R(rz=4))
    G.icon(f"HUD_Crate_{kind}", "hud", FAM)(build)


# ---- contents ---------------------------------------------------------------------------------

def salami(p0, p1, r=0.17):
    s = G.tube([p0, (Vector(p0) + Vector(p1)) / 2, p1], [r * 0.9, r, r * 0.9], sides=16, res=4)
    G.T(s, "#8E2430", name="Salami")
    ends = []
    for p, q in ((p0, p1), (p1, p0)):
        d = (Vector(q) - Vector(p)).normalized()
        e = G.sphere(r * 0.9, loc=Vector(p), segs=16, rings=8)
        ends.append(e)
    G.T(ends, "#8E2430", name="Salami")
    ties = []
    for t in (0.2, 0.8):
        c = Vector(p0).lerp(Vector(p1), t)
        d = (Vector(p1) - Vector(p0)).normalized()
        tor = G.torus(r * 0.95, 0.025, segs=20, rsegs=6)
        tor.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        tor.location = c
        ties.append(tor)
    G.T(ties, G.CREAM, name="Twine")


def steak(loc, rot):
    meat = G.puffy(G.smooth_path([(-0.5, 0.05), (-0.42, 0.32), (-0.1, 0.42), (0.3, 0.36), (0.52, 0.12), (0.46, -0.2),
                                  (0.1, -0.34), (-0.3, -0.3)], 4, closed=True), 0.18, puff=0.4)
    fat = G.puffy(G.smooth_path([(-0.56, 0.05), (-0.47, 0.37), (-0.1, 0.48), (0.33, 0.42), (0.58, 0.13), (0.52, -0.24),
                                 (0.1, -0.4), (-0.34, -0.36)], 4, closed=True), 0.14, puff=0.4, y=0.01)
    bone = G.puffy_holes(G.circle(0.12, 20, 0.12, 0.04), [G.circle(0.05, 12, 0.12, 0.04)], 0.2, puff=0.3)
    G.T(meat, "#D9455A", name="Steak")
    G.T(fat, "#F6E7DA", name="Fat")
    G.T(bone, "#F3EEE2", name="Bone")
    G.xform([meat, fat, bone], G.Tm(*loc) @ G.R(*rot))


def meat_contents():
    salami((-0.7, 0.25, 0.95), (0.55, 0.42, 1.25))
    salami((-0.45, -0.05, 0.85), (0.75, 0.15, 1.05), r=0.15)
    steak((0.05, -0.32, 1.12), (78, 0, 14))


def cheese_contents():
    wheel = G.cyl(0.5, 0.36, loc=(-0.32, 0.18, 1.0), rot=(70, 0, 20), verts=40, bevel=0.06)
    G.T(wheel, "#F59A2A", name="Wheel")
    rind = G.torus(0.5, 0.05, loc=(-0.32, 0.18, 1.0), rot=(70, 0, 20), segs=40, rsegs=8)
    G.T(rind, "#D97A1A", name="Rind")
    wedge = G.slab_holes([(-0.5, -0.26), (0.5, -0.26), (0.5, 0.22)], [G.circle(0.07, 14, 0.28, -0.08), G.circle(0.05, 12, 0.05, -0.14)],
                         0.42, bevel=0.04, segs=2)
    G.T(wedge, "#FFE27A", name="Swiss")
    G.xform(wedge, G.Tm(0.38, -0.2, 1.05) @ G.R(rx=8, rz=-20))


def veg_contents():
    rnd = random.Random(3)
    head = G.sphere(0.46, loc=(-0.38, 0.12, 0.98), scale=(1.0, 1.0, 0.85), segs=24, rings=14)
    G.T(head, "#8FD15A", name="Lettuce")
    leaves = []
    for k in range(7):
        a = 2 * math.pi * k / 7 + 0.3
        lf = G.sphere(0.3, loc=(-0.38 + 0.33 * math.cos(a), 0.12 + 0.33 * math.sin(a), 0.94), scale=(1.0, 0.45, 0.9), segs=16, rings=10,
                      rot=(0, 0, math.degrees(a) + 90))
        leaves.append(lf)
    G.T(leaves, "#5FBF45", name="Leaf")
    toms = []
    stems = []
    for x, y, z, r in ((0.38, -0.2, 1.0, 0.27), (0.62, 0.22, 1.0, 0.25), (0.18, 0.28, 1.06, 0.24)):
        toms.append(G.sphere(r, loc=(x, y, z), scale=(1, 1, 0.85), segs=20, rings=12))
        stems.append(G.slab_xy(G.fillet([(math.cos(a) * r * (0.55 if i % 2 == 0 else 0.18), math.sin(a) * r * (0.55 if i % 2 == 0 else 0.18))
                                         for i, a in enumerate([2 * math.pi * j / 10 for j in range(10)])], 0.01, 1),
                               0.03, bevel=0.01, z=z + r * 0.83))
        G.xform(stems[-1], G.Tm(x, y, 0))
    G.T(toms, "#E8423A", name="Tomato")
    G.T(stems, "#3B8F33", name="Stem")


def roll(p0, p1, r=0.2):
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0)
    o = G.lathe([(0.0, 0.0), (r * 0.6, 0.02), (r * 0.92, 0.12), (r, 0.3), (r, d.length - 0.3), (r * 0.92, d.length - 0.12),
                 (r * 0.6, d.length - 0.02), (0.0, d.length)], verts=20)
    G._bevel(o, 0.0, 1)
    o.location = p0
    o.rotation_euler = d.normalized().to_track_quat("Z", "Y").to_euler()
    G.T(o, "#E2A24E", name="Roll")
    return o


def bread_contents():
    for p0, p1 in (((-0.7, 0.3, 0.3), (-0.25, 0.25, 1.75)), ((-0.15, 0.32, 0.3), (0.3, 0.1, 1.85)), ((0.35, 0.2, 0.3), (0.85, 0.0, 1.55))):
        o = roll(p0, p1)
        p0v, p1v = Vector(p0), Vector(p1)
        d = (p1v - p0v).normalized()
        side = Vector((0, -1, 0.2))
        side = (side - d * side.dot(d)).normalized()
        slashes = []
        for t in (0.55, 0.7, 0.85):
            c = p0v.lerp(p1v, t) + side * 0.19
            s = G.rod(c - d * 0.07 + side.cross(d) * 0.09, c + d * 0.07 - side.cross(d) * 0.09, 0.03, verts=8)
            slashes.append(s)
        G.T(slashes, "#F6D497", name="Score")
    bun = G.sphere(0.3, loc=(0.4, -0.28, 1.0), scale=(1.0, 1.0, 0.7), segs=20, rings=12)
    G.T(bun, "#D8913F", name="Bun")


def sauce_contents():
    FC = G.batch_common("A_food")
    specs = [(-0.5, 0.15, "#D92B2B", "#F3EEE2", 8), (0.05, 0.22, "#F7C21A", "#E8502A", -4), (0.55, 0.05, "#FFF3D2", "#3E7FD6", 10)]
    for x, y, body, cap, tilt in specs:
        before = set(G.tagged())
        FC.squeeze_bottle(body, cap, label_col=G.PAPER, suffix=f"_{x}")
        objs = [o for o in G.tagged() if o not in before]
        G.xform(objs, G.Tm(x, y, 0.1) @ G.R(rx=-6, ry=tilt) @ G.S(1.3))


crate_icon("Meat", meat_contents)
crate_icon("Cheese", cheese_contents)
crate_icon("Veg", veg_contents)
crate_icon("Bread", bread_contents)
crate_icon("Sauce", sauce_contents)
