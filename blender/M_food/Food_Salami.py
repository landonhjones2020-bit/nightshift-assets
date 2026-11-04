"""Food_Salami — sliced salami layer (M_food batch).

Five round slices (r ~0.3) overlapping along the roll, laid low-high-low-high-low so each raised
slice rests on its neighbours' edges, with a slight wave. Deep red faces dotted with pale fat
flecks, and a thin darker casing rim that outlines every slice. Parts: Meat, Casing (the dark rim), Fat.
Run:  bpyenv/bin/python blender/M_food/Food_Salami.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
MEAT, FAT, RIM = "#B8342E", "#F2D6C9", "#7E1F1C"
R = 0.31
THICK = 0.045
LIFT = 0.054                     # base height of the raised slices (rest on the low ones' edges)
# (x, y, raised) — low-high-low-high-low along the roll, a small zig-zag across it
SLICES = [(-0.82, 0.03, False), (-0.41, -0.035, True), (0.0, 0.03, False), (0.41, -0.035, True), (0.82, 0.03, False)]


def slices(spec, R=R, seed=11, N=14, fat_per=8):
    rnd = random.Random(seed)
    F_, E_, info = [], [], []
    for k, (x0, y0, up) in enumerate(spec):
        ph = rnd.uniform(0, 6.28)
        r = R * rnd.uniform(0.97, 1.03)
        outline = C.circle(r, N, phase=ph, wobble=lambda t, ph=ph: 0.022 * math.sin(3 * t + ph))

        def zfn(x, y, s, i, ph=ph, up=up, r=r):
            wave = 0.005 * math.sin(2 * math.pi * x / 0.42 + ph) * s
            # raised slices sag a touch over the gap between the low ones
            return wave + ((-0.01 * (1 - s * s)) if up else 0.0)
        f, e = C.sheet(f"Sl{k}", outline, THICK, zfn=zfn, center=(0, 0), inner=(0.84,), edge=0.5,
                       split_edge=True, rim_on_top=True)
        spin = rnd.uniform(0, 360)
        tx, ty = rnd.uniform(-2.5, 2.5), rnd.uniform(-2.5, 2.5)
        for o in (f, e):
            o.rotation_euler = (math.radians(tx), math.radians(ty), math.radians(spin))
            o.location = (x0, y0, 0.004 + (LIFT if up else 0.0))
            ns.apply_all(o)
        F_.append(f)
        E_.append(e)
        info.append((x0, y0, r, up))
    meat = ns.join(F_, "Meat")
    ns.tag(meat, "Meat", MEAT, "SmoothPlastic", smooth_angle=70)
    rim = ns.join(E_, "Casing")
    ns.tag(rim, "Casing", RIM, "SmoothPlastic", smooth_angle=70)

    # fat flecks: pale little blobs on every slice, dropped where a raised slice hides them
    polys = []
    for x0, y0, r, up in info:
        for j in range(fat_per):
            a = 2 * math.pi * (j + rnd.uniform(0.15, 0.85)) / fat_per
            d = r * (0.12 + 0.62 * math.sqrt(rnd.uniform(0.02, 1.0)))
            cx, cy = x0 + d * math.cos(a), y0 + d * math.sin(a)
            if not up and any(u and math.hypot(cx - xx, cy - yy) < rr + 0.04 for xx, yy, rr, u in info):
                continue
            polys.append(C.blob(rnd.uniform(0.018, 0.034), 5, cx, cy, rnd))
    fat = C.surface_decals("Fat", [meat, rim], polys, lift=0.003)
    ns.tag(fat, "Fat", FAT, "SmoothPlastic", smooth_angle=None)
    return meat, rim, fat


def build():
    parts = slices(SLICES)
    C.check_bounds("Food_Salami", list(parts))


def icon():
    slices([(-0.3, 0.06, False), (0.0, -0.09, True), (0.3, 0.07, False)], seed=4, fat_per=7, N=22)


if __name__ == "__main__":
    C.run(build, "Food_Salami", C.meta("salami", 0.10),
          icon=("Ingredient_salami", icon, {"pitch": 40.0}))
