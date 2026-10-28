"""Food_Tomato — one tomato slice (pipeline-gate asset #1).

Parts: Flesh (red pericarp, walls and centre), Core (the lighter seed chambers), Seeds.
The sandwich renderer lays 3 slices along a sub roll for the Tomato layer.
Run:  bpyenv/bin/python blender/gate/Food_Tomato.py      (NS_EXPORT=1 to export)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import nslib as ns  # noqa: E402

R = 0.42          # slice radius (studs)
H = 0.10          # slice thickness
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
        # superellipse in (radial, tangential) space -> rounded "bean" that follows the arc
        c, s = math.cos(phi), math.sin(phi)
        r = rc + rh * math.copysign(abs(c) ** 0.7, c)
        a = math.radians(ac) + math.radians(half) * math.copysign(abs(s) ** 0.8, s) * (0.75 + 0.25 * (r - rc + rh) / (2 * rh))
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def build():
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
            # flat lens-shaped seeds lying on the cut face (the side the sandwich shows)
            seeds.append(ns.sphere(1.0, loc=(r * math.cos(a), r * math.sin(a), H + EPS),
                                   rot=(0, 0, math.degrees(a)), scale=(0.03, 0.052, 0.012),
                                   segs=5, rings=3))
    seed = ns.join_applied(seeds, "Seeds")
    ns.tag(seed, "Seeds", SEED, "SmoothPlastic", smooth_angle=80)


if __name__ == "__main__":
    ns.run_main(build, "Food_Tomato", "gate", "Food",
                meta={"ingredient": "tomato", "layer_count": 3, "layer_spacing": 0.62})

    # Pipeline-gate experiment: the same slice as ONE mesh with per-vertex colours,
    # to test whether vertex colours survive publishing (CONVERSION_CONSTANTS records the result).
    if os.environ.get("NS_EXPORT") == "1":
        doc = ns.export_asset("Test_TomatoVertexColor", "gate", group="Food", vertex_colors=True,
                              merge_parts="Merged", fbx=False, meta={"test": "vertex_colors"})
        print(f"[Test_TomatoVertexColor] exported: {doc['tris']} tris")

    # Icon (pipeline gate): shared icon rig, 3/4 view, transparent background, 512 px
    if os.environ.get("NS_ICON") == "1":
        ns.reset()
        build()
        print("[Food_Tomato] icon:", ns.render_icon("Food_Tomato", "food", pitch=38.0))
