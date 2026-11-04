"""Basement_PaintCans — a cluster of five old paint cans with dried drips.

Steel gallon cans with rolled rims and dried paint running down from their lips (each in
its own colour, ending in little blobs): a green one with a paper label, an open mustard
one (its lid on the floor beside it) showing the dried paint inside, a red-orange one with
a smaller cream can stacked on it (bail handle up), and a cream one tipped on its side
with a dried puddle spreading from its mouth. No collision.
Front faces -Y, pivot = bottom-centre. ~1.5 x 1 x 1.5.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns
V = 10


def drips(cx, cy, r, z_top, n, seed, lo=0.12, hi=0.32):
    """Dried drips down a vertical can side: streak + a small blob at the end."""
    rnd = random.Random(seed)
    out = []
    a0 = rnd.uniform(-180, 180)
    for k in range(n):   # spread round the can (never two drips on one spot)
        a = a0 + k * 360.0 / n + rnd.uniform(-20, 20)
        ln = rnd.uniform(lo, hi)
        out.append(C.streak_cyl(cx, cy, r, a, z_top, ln, rnd.uniform(0.06, 0.09), seed=seed * 10 + k, segs=3,
                                sway=0.01))
        ar = math.radians(a)
        d = Vector((math.sin(ar), -math.cos(ar), 0.0))
        out.append(C.rivet((cx + d.x * r, cy + d.y * r, z_top - ln + 0.012), d, r=0.03, h=0.018))
    return out


def can(cx, cy, z0, r, h, open_top=False):
    """Steel can standing at (cx, cy, z0). Returns (steel_objs, inside_cap_z)."""
    objs = []
    if open_top:
        body = ns.lathe([(r, 0.0), (r, h), (r - 0.03, h), (r - 0.03, h - 0.07)], verts=V, loc=(cx, cy, z0))
    else:
        body = ns.cyl(r, h, loc=(cx, cy, z0 + h / 2), verts=V, bevel=0.0)
    objs.append(body)
    for z in (z0 + 0.03, z0 + h - 0.03):            # rolled beads, 0.01 in from the ends (no shared cap planes)
        if open_top and z > z0 + h / 2:             # the open can's lip bead is a ring (a disc would close the can)
            o = C.ring_slab(C.circle_pts(r + 0.018, V), C.circle_pts(r - 0.012, V), "z", z - 0.02, z + 0.02)
            o.location = (cx, cy, 0)
            objs.append(o)
        else:
            objs.append(ns.cyl(r + 0.018, 0.04, loc=(cx, cy, z), verts=V, bevel=0.0))
    return objs


def build():
    steel, paint = [], {}

    def add(col, *objs):
        paint.setdefault(col, []).extend(objs)

    R, H = 0.29, 0.44
    # A: green, closed, paper label
    ax, ay = -0.42, -0.36
    steel += can(ax, ay, 0.0, R, H)
    steel.append(ns.cyl(R - 0.01, 0.03, loc=(ax, ay, H + 0.01), verts=V, bevel=0.0))       # lid
    label = ns.cyl(R + 0.008, 0.24, loc=(ax, ay, 0.21), verts=V, bevel=0.0)
    add(C.CREAM, label)
    add(C.GREEN, C.patch_cyl(ax, ay, R + 0.008, -10, 0.34, 0.15, 0.27, segs=3, proud=0.008))
    add(C.GREEN, *drips(ax, ay, R, H - 0.055, 3, 1, lo=0.08, hi=0.12))
    add(C.GREEN, C.annulus(R - 0.12, R - 0.02, loc=(ax, ay, H + 0.035), verts=V))     # dried crust on the lid
    # B: mustard, open, dried paint inside, its lid on the floor in front
    bx, by = 0.25, -0.4
    steel += can(bx, by, 0.0, R, H, open_top=True)
    add(C.MUSTARD, ns.cyl(R - 0.03, 0.03, loc=(bx, by, H - 0.07 + 0.01), verts=V, bevel=0.0))
    add(C.MUSTARD, *drips(bx, by, R, H - 0.055, 4, 2))
    # its lid leans against its right side, standing on its edge, crusty face out
    lid = ns.cyl(R + 0.01, 0.03, loc=(0, 0, 0), verts=V, bevel=0.0)
    crust = C.annulus(R - 0.1, R - 0.02, loc=(0, 0, 0.023), verts=V)
    lean = Matrix.Translation((bx + R + 0.075, by, (R + 0.01) * math.cos(math.radians(12)) + 0.012)) @ \
        Matrix.Rotation(math.radians(-12), 4, "Y") @ Matrix.Rotation(math.radians(90), 4, "Y")
    for o in (lid, crust):
        ns.apply_all(o)
        o.data.transform(lean)
        o.data.update()
    steel.append(lid)
    add(C.MUSTARD, crust)
    # C: red-orange, closed; E: smaller cream can stacked on it, bail handle up
    cx_, cy_ = -0.38, 0.34
    steel += can(cx_, cy_, 0.0, R, H)
    steel.append(ns.cyl(R - 0.01, 0.03, loc=(cx_, cy_, H + 0.01), verts=V, bevel=0.0))
    add(C.BRAND, *drips(cx_, cy_, R, H - 0.055, 4, 3))
    r2, h2 = 0.22, 0.34
    ez = H + 0.025
    steel += can(cx_ + 0.03, cy_ - 0.02, ez, r2, h2)
    steel.append(ns.cyl(r2 - 0.01, 0.03, loc=(cx_ + 0.03, cy_ - 0.02, ez + h2 + 0.01), verts=V, bevel=0.0))
    add(C.CREAM, *drips(cx_ + 0.03, cy_ - 0.02, r2, ez + h2 - 0.055, 3, 4, lo=0.08, hi=0.2))
    hx0, hx1 = cx_ + 0.03 - r2 - 0.02, cx_ + 0.03 + r2 + 0.02
    hy = cy_ - 0.02
    bail = C.pipe([(hx0, hy, ez + h2 - 0.08)] + [((hx0 + hx1) / 2 - (hx1 - hx0) / 2 * math.cos(t),
                                                   hy, ez + h2 + 0.04 + 0.16 * math.sin(t))
                                                  for t in (math.radians(a) for a in (20, 55, 90, 125, 160))] +
                  [(hx1, hy, ez + h2 - 0.08)], 0.012, sides=4)
    steel.append(bail)
    # D: cream, tipped over on its side (mouth toward +X), dried puddle spreading out of it
    dx, dy, ln = 0.24, 0.38, 0.44
    dcan = can(0.0, 0.0, -ln / 2, R, ln, open_top=True)
    M = Matrix.Translation((dx, dy, R + 0.018)) @ Matrix.Rotation(math.radians(90), 4, "Y")
    for o in dcan:
        ns.apply_all(o)
        o.data.transform(M)
        o.data.update()
    steel += dcan
    inner = ns.cyl(R - 0.03, 0.03, loc=(0, 0, ln / 2 - 0.07 + 0.01), verts=V, bevel=0.0)
    ns.apply_all(inner)
    inner.data.transform(M)
    add(C.CREAM, inner)
    puddle = C.blob(0, 0, 0.22, 0, seed=7, n=8)
    C.place([puddle], loc=(0, 0, 0), pitch=-90)
    C.face_dir(puddle, "+Z")
    for v in puddle.data.vertices:
        v.co.x, v.co.y, v.co.z = v.co.x * 1.2 + dx + ln / 2 + 0.06, v.co.y + dy - 0.02, 0.006
    add(C.CREAM, puddle)

    C.part(steel, "Steel", C.STEEL, "Metal", smooth_angle=60)
    names = {C.GREEN: "PaintGreen", C.MUSTARD: "PaintMustard", C.BRAND: "PaintRed", C.CREAM: "PaintCream"}
    for col, objs in paint.items():
        C.part(objs, names[col], col, smooth_angle=None)


META = {"collide": "none", "cans": 5}

if __name__ == "__main__":
    C.run(build, "Basement_PaintCans", budget=2000, meta=META, views=((-35, 30, False), (40, 22, True)))
