"""Basement_MascotHead — "Stacky", the shop's old sub-sandwich mascot costume head.

A giant plush sub roll (Fabric) with round ends: a soft bottom half, a meat layer with a
wavy lettuce frill, drooping cheese and tomato slices at the sides, and a long domed top
with three baked score cuts.
The sandwich's gap is Stacky's grin: a dark mouth with six big buck teeth (one chipped).
Two big round plastic eyes stand up on top of the roll, mascot-style, with black pupils
and a shine dot; the left one (viewer's right) half-closed under a drooping eyelid. The head sits a little crooked on a wooden mannequin
stand (round base, pole, collar). Creepy-cute and dusty, never gory. No collision.
Front faces -Y, pivot = bottom-centre. ~3 x 4.5 x 2.5.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

ns = C.ns
HZ = 2.5                       # head bottom (top of the stand)
B0, B1 = HZ, 2.98              # bottom half of the roll
F1 = 3.4                       # filling top = top half bottom
TOPZ = 4.2                     # roll crown (the eyes stand up above it)
TILT = 5.0                     # head leans this many degrees (about the front-back axis)
BUN = "#C99A62"                # faded bun
BUN_TOP = "#BE8A52"
LETTUCE = "#7E9A4C"
TOMATO = "#B24A3A"
MEAT = "#A8695C"
TEETH = "#E6DFCC"
MOUTH = "#3A1C1E"
EYE = "#EDE8DA"
CRUMB = "#E2C590"              # pale crumb showing in the score cuts
EYE_X, EYE_Z, EYE_R = 0.62, 4.1, 0.4
EYE_Y = -0.5


def ring(w, d, r, z):
    return C.ring3(C.rrect(w, d, r, 3), z)


def build():
    head = {}

    def add(key, *objs):
        head.setdefault(key, []).extend(objs)

    # ---- buns ----------------------------------------------------------------------------
    # a long sub roll: capsule footprint (round ends), low wide dome on top
    bottom = C.loft([ring(2.5, 1.4, 0.68, B0), ring(2.85, 1.75, 0.86, B0 + 0.12), ring(2.92, 1.82, 0.88, B1 - 0.1),
                     ring(2.82, 1.72, 0.84, B1)], cap0=True, cap1=True)
    top = C.loft([ring(2.85, 1.7, 0.82, F1), ring(3.0, 1.85, 0.9, F1 + 0.12), ring(2.88, 1.75, 0.86, F1 + 0.45),
                  ring(2.5, 1.35, 0.66, F1 + 0.68), ring(1.8, 0.7, 0.34, TOPZ)], cap0=True, cap1=True)
    add("bun", bottom)
    add("buntop", top)

    # three baked score cuts slashed across the top, hugging the dome (ray cast)
    ns.apply_all(top)
    bvh = BVHTree.FromObject(top, bpy.context.evaluated_depsgraph_get())

    def on_top(x, y):
        hit = bvh.ray_cast(Vector((x, y, TOPZ + 1)), Vector((0, 0, -1)))
        return hit[0] + hit[1] * 0.025
    for cx in (-0.95, 0.0, 0.95):
        a0, a1 = Vector((cx - 0.18, 0.0)), Vector((cx + 0.18, 0.44))
        dv = (a1 - a0).normalized()
        side = Vector((-dv.y, dv.x)) * 0.07
        rows = []
        for i in range(5):
            q = a0.lerp(a1, i / 4)
            w = 1.0 - abs(i - 2) / 3.0
            rows.append((on_top(*(q - side * w)), on_top(*(q + side * w))))
        bm = bmesh.new()
        vs = [(bm.verts.new(l), bm.verts.new(r)) for l, r in rows]
        for i in range(4):
            bm.faces.new([vs[i][0], vs[i + 1][0], vs[i + 1][1], vs[i][1]])
        add("score", C.face_dir(ns.from_bmesh(bm, "Score"), "+Z"))

    # ---- filling: meat layer notched for the mouth, lettuce frill, cheese, tomato ---------------
    # meat layer recessed 0.12 behind the buns; the dark mouth box sits in front of it
    meat = C.prism(C.rrect(2.66, 1.5, 0.74, 3), "z", B1 - 0.02, F1 + 0.02)
    add("meat", meat)
    add("mouth", ns.box((1.9, 0.3, F1 - B1 + 0.02), loc=(0, -0.63, (B1 + F1) / 2), bevel=0.0))
    frill = []
    # capsule outline resampled to even spacing (rrect's round ends nearly meet: near-duplicate points kink a tube)
    outline = [Vector(p) for p in C.rrect(2.98, 1.86, 0.86, 4)]
    n = len(outline)
    seg = [(outline[(i + 1) % n] - outline[i]).length for i in range(n)]
    total, m = sum(seg), 34
    pts, i, acc = [], 0, 0.0
    for k in range(m):
        t = total * k / m
        while acc + seg[i] < t:
            acc += seg[i]
            i += 1
        pts.append(outline[i].lerp(outline[(i + 1) % n], (t - acc) / seg[i]))
    wav = [(q.x, q.y, B1 + 0.05 + 0.06 * math.sin(i * 2.2)) for i, q in enumerate(pts)]
    frill.append(C.pipe(wav, 0.075, sides=4, closed=True))
    add("lettuce", *frill)
    for sx in (-1, 1):   # cheese corners drooping over the sides
        flap = C.prism([(-0.5, F1 - 0.06), (0.25, F1 - 0.06), (-0.02, B1 - 0.36), (-0.2, B1 - 0.3)], "x",
                       sx * 1.44, sx * 1.44 + sx * 0.06)
        add("cheese", flap)
        add("tomato", ns.cyl(0.3, 0.12, loc=(sx * 1.32, 0.34, (B1 + F1) / 2 + 0.04), verts=10, bevel=0.0))

    # ---- teeth (one chipped) ------------------------------------------------------------------
    tw, th = 0.27, 0.27
    for k in range(6):
        x = -0.75 + k * 0.3
        if k == 3:   # chipped: the lower outer corner broken off on a slant
            outline_t = [(x - tw / 2, F1 + 0.02), (x + tw / 2, F1 + 0.02), (x + tw / 2, F1 - th + 0.12),
                         (x + 0.02, F1 - th + 0.02), (x - tw / 2, F1 - th + 0.02)]
            add("teeth", C.prism(C.fillet(outline_t, [0, 0, 0.02, 0.02, 0.04], 1), "y", -0.87, -0.72))
        else:
            add("teeth", ns.box((tw, 0.15, th), loc=(x, -0.795, F1 - th / 2 + 0.02), bevel=0.035, segments=1))

    # ---- eyes, pupils, shine, the drooping lid ------------------------------------------------
    for sx in (-1, 1):
        ex = sx * EYE_X
        add("eye", ns.sphere(EYE_R, loc=(ex, EYE_Y, EYE_Z), segs=12, rings=8))
        px, pz = ex - sx * 0.07, EYE_Z - (0.06 if sx < 0 else 0.13)   # the droopy eye looks a bit lower
        py = EYE_Y - math.sqrt(EYE_R ** 2 - (px - ex) ** 2 - (pz - EYE_Z) ** 2) + 0.04
        add("pupil", ns.sphere(0.21, loc=(px, py, pz), segs=10, rings=6, scale=(1.0, 0.36, 1.0)))
        if sx < 0:   # shine dot (the open eye only)
            d = C.disc(0.055, loc=(0, 0, 0), verts=6)
            d.rotation_euler = (math.radians(90), 0, 0)
            d.location = (px + 0.07, py - 0.21 * 0.36 + 0.004, pz + 0.07)
            ns.apply_all(d)
            add("shine", C.face_dir(d, "-Y"))
    # eyelid: a dome slightly bigger than the eye, cut a bit below the eye centre, tipped 20 degrees
    rl = EYE_R + 0.07
    lid = ns.lathe([(rl * math.cos(math.radians(a)), rl * math.sin(math.radians(a))) for a in (0, 22.5, 45, 67.5, 90)],
                   verts=14)
    lid.location = (0, 0, -0.04)
    ns.apply_all(lid)
    lid.rotation_euler = (math.radians(-12), math.radians(-20), 0)
    lid.location = (EYE_X, EYE_Y, EYE_Z)
    ns.apply_all(lid)
    add("lid", lid)

    # ---- tilt the whole head a little on its stand ------------------------------------------
    R = Matrix.Translation((0, 0, HZ)) @ Matrix.Rotation(math.radians(TILT), 4, "Y") @ Matrix.Translation((0, 0, -HZ))
    for objs in head.values():
        for o in objs:
            ns.apply_all(o)
            o.data.transform(R)
            o.data.update()

    fab = dict(smooth_angle=45)
    C.part(head["bun"], "BunBottom", BUN, "Fabric", **fab)
    C.part(head["buntop"] + head["lid"], "BunTop", BUN_TOP, "Fabric", **fab)
    C.part(head["score"], "ScoreCuts", CRUMB, "Fabric", smooth_angle=None)
    C.part(head["meat"], "MeatLayer", MEAT, "Fabric", **fab)
    C.part(head["mouth"], "Mouth", MOUTH, "Fabric", smooth_angle=None)
    C.part(head["lettuce"], "Lettuce", LETTUCE, "Fabric", smooth_angle=60)
    C.part(head["cheese"], "Cheese", C.MUSTARD, "Fabric", smooth_angle=40)
    C.part(head["tomato"], "Tomato", TOMATO, "Fabric", smooth_angle=50)
    C.part(head["teeth"], "Teeth", TEETH, smooth_angle=40)
    C.part(head["eye"], "Eyes", EYE, smooth_angle=70)
    C.part(head["pupil"], "Pupils", C.INK, smooth_angle=70)
    C.part(head["shine"], "Shine", "#FFFFFF", smooth_angle=None)

    # ---- wooden mannequin stand -----------------------------------------------------------------
    base = ns.cyl(0.75, 0.16, loc=(0, 0, 0.08), verts=14, radius_top=0.68, bevel=0.03, segments=1)
    pole = ns.cyl(0.085, HZ + 0.2, loc=(0, 0, (HZ + 0.2) / 2 + 0.1), verts=8, bevel=0.0)
    collar = ns.cyl(0.36, 0.18, loc=(0, 0, HZ - 0.04), verts=12, radius_top=0.3, bevel=0.0)
    C.part([base, pole, collar], "Stand", C.WOOD_DARK, "Wood", smooth_angle=45)


META = {"character": "Stacky, the STACKHOUSE sub-sandwich mascot (old costume head)", "collide": "none",
        "tilt_deg": TILT}

if __name__ == "__main__":
    C.run(build, "Basement_MascotHead", budget=2000, meta=META, views=((-25, 12, False), (35, 8, True)))
