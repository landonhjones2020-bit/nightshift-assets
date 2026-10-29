"""Food_Pickles — crinkle-cut pickle chips (A_food batch).

Seven ridged chips scattered over the roll in two staggered rows. Parts: Flesh (yellow-green
ridged faces), Skin (dark green rim), Seeds (pale seed ring).
Run:  bpyenv/bin/python blender/A_food/Food_Pickles.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
FLESH, SKIN, SEED = "#B9CC4A", "#3D7A22", "#ECEFB4"
SPOTS = [(-0.86, -0.17), (-0.29, -0.2), (0.28, -0.16), (0.86, -0.19), (-0.58, 0.19), (0.0, 0.17), (0.58, 0.2)]


def chips(spots, R=0.165, seed=4):
    rnd = random.Random(seed)
    F, S = [], []
    for k, (x, y) in enumerate(spots):
        f, s = C.ridged_chip(f"Chip{k}", R * rnd.uniform(0.93, 1.05), 0.035)
        for o in (f, s):
            o.rotation_euler = (math.radians(rnd.uniform(-6, 6)), math.radians(rnd.uniform(-6, 6)),
                                math.radians(rnd.uniform(0, 180)))
            o.location = (x, y, 0.012 + 0.01 * (k % 3))
            ns.apply_all(o)
        F.append(f)
        S.append(s)
    fl = ns.join(F, "Flesh")
    ns.tag(fl, "Flesh", FLESH, "SmoothPlastic", smooth_angle=70)
    sk = ns.join(S, "Skin")
    ns.tag(sk, "Skin", SKIN, "SmoothPlastic", smooth_angle=70)
    seeds = []
    for k, (x, y) in enumerate(spots):
        a0 = rnd.uniform(0, 6.28)
        for j in range(4):
            a = a0 + j * math.pi / 2
            seeds.append((x + R * 0.36 * math.cos(a), y + R * 0.36 * math.sin(a)))
    sd = C.flecks_on("Seeds", [fl], seeds, SEED, "SmoothPlastic", size=(0.024, 0.015, 0.007), verts=4, seed=seed,
                     sink=0.3, smooth_angle=60)
    return fl, sk, sd


def build():
    parts = chips(SPOTS)
    C.check_bounds("Food_Pickles", list(parts))


def icon():
    chips([(-0.17, 0.1), (0.17, -0.06), (0.02, 0.28)], R=0.2, seed=7)


if __name__ == "__main__":
    C.run(build, "Food_Pickles", C.meta("pickles", 0.07),
          icon=("Ingredient_pickles", icon, {"pitch": 45.0}))
