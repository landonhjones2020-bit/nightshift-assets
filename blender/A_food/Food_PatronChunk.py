"""Food_PatronChunk — one giant sandwich chunk for the Night 5 Patron (A_food batch).

A ~6-stud sub built from the same ingredient builders as the regular layers (sourdough-ish roll,
ham, melted cheddar, tomato, lettuce) at 2.7x scale with the fillings exaggerated (thicker, more
overhang) and a giant frilled toothpick through the top, so it reads as an absurdly huge sandwich.
Parts: CrustBottom / CrustTop (recolor "toast"), CrumbBottom / CrumbTop, Ham, HamEdge, Cheese,
Tomato, TomatoCore, LeafDark, Pick, PickFrill.
Run:  bpyenv/bin/python blender/A_food/Food_PatronChunk.py   (NS_EXPORT=1 export)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix  # noqa: E402

ns = C.ns
S = 6.0 / C.ROLL_L          # 2.73x the regular sub
FILL_Z = 1.45               # fillings exaggerated in thickness
FILL_XY = 1.06              # ...and in overhang
BREAD = C.BREADS["white_sub"]


def layer(fn, z, suffix="", xy=1.0, zs=1.0):
    """Build one layer at sub scale, rename its parts, then place/scale it into the chunk."""
    before = set(ns._tagged_objects())
    fn()
    new = [o for o in ns._tagged_objects() if o not in before]
    M = Matrix.Scale(S, 4) @ Matrix.Translation((0, 0, z)) @ Matrix.Diagonal((xy, xy, zs, 1.0))
    for o in new:
        if suffix:
            o["ns_part"] = o["ns_part"] + suffix
            o.name = o["ns_part"]
        o.matrix_world = M @ o.matrix_world
        ns.apply_all(o)
    return new


def tomatoes():
    flesh, core = [], []
    for k, x in enumerate((-0.68, 0.0, 0.68)):
        f = ns.cyl(0.36, 0.09, loc=(x, 0.02 * (k - 1), 0.045), rot=(0, 4 * (k - 1), 0), verts=14, bevel=0)
        c = C.flat_ring(f"TC{k}", 0.09, 0.27, 0.0, N=10)
        c.rotation_euler = (0, math.radians(4 * (k - 1)), 0)
        c.location = (x, 0.02 * (k - 1), 0.093)
        ns.apply_all(f)
        ns.apply_all(c)
        flesh.append(f)
        core.append(c)
    ns.tag(ns.join(flesh, "Tomato"), "Tomato", "#D92E24", "SmoothPlastic", smooth_angle=50)
    ns.tag(ns.join(core, "TomatoCore"), "TomatoCore", "#FF8A63", "SmoothPlastic", smooth_angle=50)


def lettuce():
    leaf = C.frilly_leaf("LeafDark", 1.08, 0.47, N=30, frills=14, amp_z=0.04, amp_xy=0.08, seed=9)
    ns.tag(leaf, "LeafDark", "#4BB23A", "SmoothPlastic", smooth_angle=80)


def pick(z_top):
    stick = ns.cyl(0.06, 1.5, verts=6, bevel=0, name="Pick")
    stick.location = (0.25 * S, -0.05 * S, z_top + 0.25)
    stick.rotation_euler = (math.radians(4), math.radians(6), 0)
    ns.apply_all(stick)
    ns.tag(stick, "Pick", "#D9B27A", "Wood", smooth_angle=40)
    frill = ns.cyl(0.3, 0.5, verts=10, bevel=0, radius_top=0.07, name="PickFrill")
    frill.location = (0.25 * S + 0.1, -0.05 * S - 0.07, z_top + 0.95)
    frill.rotation_euler = (math.radians(4 + 180), math.radians(6), 0)
    ns.apply_all(frill)
    for i, v in enumerate(frill.data.vertices):   # crinkled cellophane frill
        if v.co.z > z_top + 1.1:
            v.co.x += 0.07 * math.cos(i * 2.1)
            v.co.y += 0.07 * math.sin(i * 2.1)
            v.co.z += 0.05 * math.sin(i * 1.7)
    ns.tag(frill, "PickFrill", "#E8502A", "SmoothPlastic", smooth_angle=None)


def build():
    z = 0.0
    layer(lambda: C.build_bread_bottom(BREAD["crust"], BREAD["crumb"], N=20, lump=C.roll_lump(3, 0.008)),
          z, "Bottom")
    z += C.BOTTOM_H
    layer(lambda: C.polar_slices("#F58EA3", "#D9637D", xs=(-0.45, 0.45), a=0.62, b=0.48, N=18, inner=(0.5,),
                                 amp=0.035, wavelength=0.5, names=("Ham", "HamEdge"), yaws=(-4, 5), tilt=(-3, 3)),
          z, xy=1.12, zs=1.9)
    z += 0.08 * 1.9
    layer(lambda: C.melted_sheet("Cheese", C.CHEESES["cheddar"]["melt"], N=22, inner=(0.6, 0.88, 0.96),
                                 lobes=C.MELT_LOBES, drips=C.MELT_DRIPS),
          z, xy=FILL_XY, zs=FILL_Z)
    z += 0.04 * FILL_Z
    layer(tomatoes, z, xy=FILL_XY, zs=FILL_Z)
    z += 0.095 * FILL_Z
    layer(lettuce, z, xy=FILL_XY, zs=FILL_Z)
    z += 0.07 * FILL_Z
    top = layer(lambda: C.build_bread_top(BREAD["crust"], BREAD["crumb"], N=20, lump=C.roll_lump(4, 0.012),
                                          height=0.5, steps=(0, 22, 44, 66, 86)), z, "Top")
    lo, hi = ns.bbox_world(top)
    pick(hi.z)
    print(C.part_tris())


if __name__ == "__main__":
    C.run(build, "Food_PatronChunk", meta_={"patron_chunk": True, "scale": round(S, 3)}, pivot=None)
