"""Food_Crumbs — three toasted bread crumbs (M_food batch), the tutorial's crumb trail.

Landon, 2026-11-05: the tutorial's route is a trail of crumbs ("follow the crumbs to a van"),
then "make actual crumbs not just boxes". Controllers.Tutorial clones these from
ReplicatedStorage.Assets.Food.Food_Crumbs and floats them at hip height along the route.

Each crumb is a lumpy, torn-off piece of soft bread: a low-poly ball knocked out of round by
two layers of noise, broken flat on one or two sides where it came away from the slice, with
the toasted crust as a patch over its outside. Two colours, so it reads as bread even as a
speck on a phone. Three shapes side by side along X (the client takes each Crumb<i>/Crust<i>
pair apart and scales it to Config.Tutorial guide.crumbSize):
  1  a chunky piece from the middle of a slice (crust over the top)
  2  a long edge piece (crust over the top and down one long side)
  3  a small round-ish nub (a crust cap)
Parts: Crumb1, Crust1, Crumb2, Crust2, Crumb3, Crust3 (crusts recolor="toast").
Run:  python3 blender/M_food/Food_Crumbs.py   (NS_EXPORT=1 export)
"""
from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import nslib as ns  # noqa: E402  (imports bpy first: bmesh and mathutils need it)
import bmesh  # noqa: E402
from mathutils import Vector, noise  # noqa: E402

CRUMB = "#F1D49C"  # the soft inside of the bread
CRUST = "#B5622A"  # toasted
GAP = 1.4  # studs between the three crumbs in the asset (they are taken apart in game)

# (scale xyz, crust direction, crust coverage, torn sides [(axis, sign, cut)], seed)
SHAPES = [
    ((0.9, 0.78, 0.66), (0.15, -0.2, 1.0), 0.42, [(1, 1, 0.3), (0, -1, 0.36)], 4),
    ((1.08, 0.6, 0.5), (0.0, -0.75, 0.7), 0.3, [(1, 1, 0.24), (0, 1, 0.46)], 9),
    ((0.64, 0.6, 0.56), (0.25, 0.1, 1.0), 0.48, [(1, -1, 0.24)], 17),
]


def lumpy(scale, tears, seed) -> bmesh.types.BMesh:
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.5)
    rnd = random.Random(seed)
    off = Vector((rnd.uniform(0, 50), rnd.uniform(0, 50), rnd.uniform(0, 50)))
    for v in bm.verts:
        n = v.co.normalized()
        r = 0.5 + 0.16 * noise.noise(n * 1.7 + off) + 0.06 * noise.noise(n * 3.9 - off)
        v.co = Vector((n.x * r * scale[0], n.y * r * scale[1], n.z * r * scale[2]))
    # where it broke off the slice: squashed nearly flat past a plane, a little uneven
    for axis, sign, cut in tears:
        for v in bm.verts:
            d = sign * v.co[axis] - cut
            if d > 0:
                v.co[axis] = sign * (cut + d * 0.12) + rnd.uniform(-0.012, 0.012)
    # rest on z = 0
    lo = min(v.co.z for v in bm.verts)
    for v in bm.verts:
        v.co.z -= lo
    bm.normal_update()
    return bm


def split(bm: bmesh.types.BMesh, keep) -> bmesh.types.BMesh:
    """A copy of bm with only the faces `keep(face)` says yes to."""
    out = bm.copy()
    out.faces.ensure_lookup_table()
    gone = [f for f in out.faces if not keep(f)]
    bmesh.ops.delete(out, geom=gone, context="FACES")
    return out


def crumb(i: int, x: float):
    scale, cdir, cover, tears, seed = SHAPES[i - 1]
    bm = lumpy(scale, tears, seed)
    d = Vector(cdir).normalized()

    def is_crust(f) -> bool:
        return f.normal.dot(d) > cover

    body = ns.from_bmesh(split(bm, lambda f: not is_crust(f)), f"Crumb{i}", loc=(x, 0, 0))
    ns.tag(body, f"Crumb{i}", CRUMB, "SmoothPlastic", smooth_angle=75.0)
    # the crust stands a hair proud of the crumb, so its edge catches the light
    cb = split(bm, is_crust)
    edge = {v for e in cb.edges if e.is_boundary for v in e.verts}
    for v in cb.verts:
        if v not in edge:
            v.co += v.normal * 0.018
    crust = ns.from_bmesh(cb, f"Crust{i}", loc=(x, 0, 0))
    ns.tag(crust, f"Crust{i}", CRUST, "SmoothPlastic", smooth_angle=75.0, recolor="toast")
    bm.free()


def build():
    for i, x in ((1, -GAP), (2, 0.0), (3, GAP)):
        crumb(i, x)
    return {}


if __name__ == "__main__":
    # merge=None: the client takes the crumbs apart, so every part ships on its own
    ns.run_main(build, "Food_Crumbs", "M_food", "Food", merge=None)
