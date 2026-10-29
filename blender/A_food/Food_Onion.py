"""Food_Onion — one red onion slice: three nested rings (A_food batch).

The KitchenRenderer lays layer_count = 3 copies along X at layer_spacing = 0.72 (no overlap).
Parts: Skin (magenta rings, which show as thin purple lines at each ring's edges), Flesh (pale
lavender-white cut faces).
Run:  bpyenv/bin/python blender/A_food/Food_Onion.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SKIN, FLESH = "#9C2C7C", "#F5E2EF"
H = 0.05
RINGS = ((0.33, 0.058, 0.0, 0.0, 22), (0.245, 0.055, 0.012, -0.008, 18), (0.16, 0.052, -0.01, 0.014, 14))


def onion_slice(suffix="", wob_seed=0.0):
    skins, flesh = [], []
    for k, (ro, w, dx, dy, N) in enumerate(RINGS):
        wob = (lambda t, k=k: 0.025 * math.sin(3 * t + k * 1.7 + wob_seed) + 0.012 * math.sin(5 * t + k))
        a = C.annulus(f"R{k}", ro - w, ro, H - 0.004 * k, N=N, wob=wob)
        a.location = (dx, dy, 0.0)
        ns.apply_all(a)
        f = C.flat_ring(f"F{k}", ro - w + 0.011, ro - 0.013, H - 0.004 * k + 0.002, N=N, wob=wob)
        f.location = (dx, dy, 0.0)
        ns.apply_all(f)
        skins.append(a)
        flesh.append(f)
    s = ns.join(skins, "Skin" + suffix)
    ns.tag(s, "Skin" + suffix, SKIN, "SmoothPlastic", smooth_angle=70)
    f = ns.join(flesh, "Flesh" + suffix)
    ns.tag(f, "Flesh" + suffix, FLESH, "SmoothPlastic", smooth_angle=70)
    return s, f


def build():
    onion_slice()
    C.check_bounds("Food_Onion", layer=False)


def icon():
    a = onion_slice("Back", 1.0)
    for o in a:
        o.location = (-0.24, 0.2, 0)
    b = onion_slice()
    for o in b:
        o.rotation_euler = (math.radians(7), math.radians(-9), 0.4)
        o.location = (0.2, -0.16, 0.045)


if __name__ == "__main__":
    C.run(build, "Food_Onion", C.meta("onion", 0.06, 3, 0.72),
          icon=("Ingredient_onion", icon, {"pitch": 58.0}))
