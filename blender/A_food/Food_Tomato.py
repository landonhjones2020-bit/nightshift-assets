"""Food_Tomato — one tomato slice, ported from the pipeline-gate asset (blender/gate/Food_Tomato.py).

Parts: Flesh (red pericarp, walls and centre), Core (the lighter seed chambers), Seeds.
The KitchenRenderer lays layer_count = 3 copies along X at layer_spacing = 0.62 (the slices
overlap by ~0.22). Change from the gate version: the slice is tipped 3 deg about the roll's cross
axis (its -X edge touches Z 0, its +X edge is lifted), so overlapping copies shingle instead of
z-fighting. Geometry is otherwise identical to the gate slice.
Run:  bpyenv/bin/python blender/A_food/Food_Tomato.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix  # noqa: E402

ns = C.ns
R = 0.42          # slice radius (studs)
H = 0.10          # slice thickness
TIP = 3.0         # shingle tip (degrees)
FLESH = "#D92E24"
CORE = "#FF8A63"
SEED = "#FFE27A"
EPS = 0.004       # chambers/seeds sit a hair proud of the flesh faces (no z-fighting)

# (centre angle deg, angular half-width deg, radial centre, radial half-depth)
CHAMBERS = ((40, 39, 0.205, 0.112), (130, 36, 0.2, 0.106), (220, 38, 0.208, 0.11), (308, 37, 0.2, 0.108))


def chamber_outline(ac, half, rc, rh, n=18):
    pts = []
    for i in range(n):
        phi = 2 * math.pi * i / n
        c, s = math.cos(phi), math.sin(phi)
        r = rc + rh * math.copysign(abs(c) ** 0.7, c)
        a = math.radians(ac) + math.radians(half) * math.copysign(abs(s) ** 0.8, s) * (0.75 + 0.25 * (r - rc + rh) / (2 * rh))
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def slice_(tip=TIP):
    flesh = ns.cyl(R, H, loc=(0, 0, H / 2), verts=24, bevel=0.035, segments=2)
    ns.tag(flesh, "Flesh", FLESH, "SmoothPlastic")

    chambers = [ns.profile_slab(chamber_outline(*c), H + 2 * EPS, loc=(0, 0, -EPS), bevel=0.0, name=f"Ch{i}")
                for i, c in enumerate(CHAMBERS)]
    core = ns.join_applied(chambers, "Core")
    ns.tag(core, "Core", CORE, "SmoothPlastic", smooth_angle=50)

    seeds = []
    for ac, half, rc, _ in CHAMBERS:
        for da, dr in ((-0.45, 0.015), (0.0, -0.035), (0.45, 0.012)):
            a = math.radians(ac + half * da)
            r = rc + dr
            seeds.append(ns.sphere(1.0, loc=(r * math.cos(a), r * math.sin(a), H + EPS),
                                   rot=(0, 0, math.degrees(a)), scale=(0.03, 0.052, 0.012),
                                   segs=5, rings=3))
    seed = ns.join_applied(seeds, "Seeds")
    ns.tag(seed, "Seeds", SEED, "SmoothPlastic", smooth_angle=80)
    parts = [flesh, core, seed]
    if tip:
        hinge = Matrix.Translation((-R, 0, 0))
        M = hinge @ Matrix.Rotation(math.radians(-tip), 4, "Y") @ hinge.inverted()
        for o in parts:
            ns.apply_all(o)
            o.data.transform(M)
            o.data.update()
    return parts


def build():
    slice_()
    C.check_bounds("Food_Tomato", layer=False)


def icon():
    """Two overlapping slices, the front one leaning on the back one."""
    back = slice_(tip=0)
    for o in back:
        o["ns_part"] = o["ns_part"] + "Back"
        o.name = o["ns_part"]
        o.location = (-0.3, 0.22, 0.0)
    front = slice_(tip=0)
    for o in front:
        o.rotation_euler = (math.radians(8), math.radians(-10), 0)
        o.location = (0.25, -0.18, 0.05)


if __name__ == "__main__":
    C.run(build, "Food_Tomato", C.meta("tomato", 0.12, 3, 0.62),
          icon=("Ingredient_tomato", icon, {"pitch": 58.0}))
