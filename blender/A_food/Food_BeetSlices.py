"""Food_BeetSlices — one beet slice (A_food batch).

Deep magenta round with lighter concentric growth rings and a dark skin rim; juicy domed face.
The KitchenRenderer lays layer_count = 3 copies along X at layer_spacing = 0.74 (no overlap).
Parts: Flesh, Rings (lighter magenta), Skin (dark rim band).
Run:  bpyenv/bin/python blender/A_food/Food_BeetSlices.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
FLESH, RINGS, SKIN = "#B0145E", "#E8509A", "#5C0B33"
R, H = 0.355, 0.07


def beet_slice(suffix=""):
    wob = (lambda t: 0.03 * math.sin(2 * t + 0.5) + 0.015 * math.sin(5 * t))
    out = C.circle(R, 26, wobble=wob)
    f, e = C.sheet("Flesh" + suffix, out, H, center=(0, 0), inner=(0.45, 0.8), edge=0.5, bulge=0.012,
                   split_edge=True)
    ns.tag(f, "Flesh" + suffix, FLESH, "SmoothPlastic", smooth_angle=70)
    ns.tag(e, "Skin" + suffix, SKIN, "SmoothPlastic", smooth_angle=70)
    tree = C.bvh(f)
    rings = []
    for k, (r0, r1) in enumerate(((0.262, 0.277), (0.17, 0.184), (0.075, 0.088))):
        ring = C.flat_ring(f"BR{k}", r0, r1, 0.0, N=22, wob=wob)
        for v in ring.data.vertices:
            loc, nor = C.hit(tree, v.co.x, v.co.y)
            v.co.z = (loc.z if loc else H) + 0.003
        rings.append(ring)
    r = ns.join(rings, "Rings" + suffix)
    ns.tag(r, "Rings" + suffix, RINGS, "SmoothPlastic", smooth_angle=70)
    return f, e, r


def build():
    beet_slice()
    C.check_bounds("Food_BeetSlices", layer=False)


def icon():
    a = beet_slice("Back")
    for o in a:
        o.location = (-0.27, 0.22, 0)
    b = beet_slice()
    for o in b:
        o.rotation_euler = (math.radians(8), math.radians(-10), 0)
        o.location = (0.22, -0.18, 0.05)


if __name__ == "__main__":
    C.run(build, "Food_BeetSlices", C.meta("beet_slices", 0.08, 3, 0.74),
          icon=("Ingredient_beet_slices", icon, {"pitch": 58.0}))
