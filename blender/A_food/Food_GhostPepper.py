"""Food_GhostPepper — sliced ghost pepper (A_food batch).

Five pale, wrinkled pepper rings scattered over the roll, a little warped; the inside wall of each
ring is hot red-orange membrane, with a seed lump clinging to it. Parts: Flesh (ghost white with a cold green tint), Membrane.
Run:  bpyenv/bin/python blender/A_food/Food_GhostPepper.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
FLESH, MEMBRANE = "#E2ECE2", "#E2492F"
SPOTS = [(-0.84, 0.13), (-0.44, -0.15), (0.0, 0.16), (0.44, -0.12), (0.84, 0.14)]


def pepper_ring(name, R, seed):
    """One wrinkled ring: lumpy outline, thin wall around a big hollow, a seed-membrane lump
    clinging to one side of the inner wall."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(4)]
    lobes = rnd.choice((3, 4))

    def wob_out(t):
        return 0.12 * math.sin(lobes * t + ph[0]) + 0.05 * math.sin(9 * t + ph[1]) + 0.03 * math.sin(13 * t + ph[2])

    def wob_in(t):
        return 0.13 * math.sin(lobes * t + ph[0]) + 0.05 * math.sin(7 * t + ph[3])
    out = C.circle(R, 16, wobble=wob_out)
    hole = C.circle(R * 0.66, 10, wobble=wob_in)
    zfn = (lambda x, y: 0.018 * math.sin(6 * x + ph[2]) * math.cos(5 * y + ph[1]))
    body, walls = C.holed_slab(name, out, [hole], 0.05, zfn=zfn, round_out=0.5, split_holes=True)
    a = rnd.uniform(0, 6.28)
    rr = R * 0.66 * (1 + wob_in(a)) - 0.03
    lump = ns.sphere(1.0, loc=(rr * math.cos(a), rr * math.sin(a), 0.03), rot=(0, 0, math.degrees(a)),
                     scale=(0.045, 0.06, 0.028), segs=5, rings=3, name=name + "Lump")
    ns.apply_all(lump)
    return body, ns.join([walls, lump], name + "M")


def peppers(spots, R=0.18, seed=1):
    rnd = random.Random(seed)
    B, W = [], []
    for k, (x, y) in enumerate(spots):
        b, w = pepper_ring(f"Pep{k}", R * rnd.uniform(0.9, 1.08), seed + k * 7)
        # one tilt/spin per ring for BOTH meshes (each used to draw its own, so the red inner wall sat rotated
        # away from the hole: see-through gaps and membrane poking through the flesh); both draws are kept so
        # the random stream is unchanged
        rots = [(rnd.uniform(-6, 6), rnd.uniform(-6, 6), rnd.uniform(0, 360)) for _ in (b, w)]
        for o in (b, w):
            o.rotation_euler = tuple(math.radians(a) for a in rots[0])
            o.location = (x, y, 0.014 + 0.008 * (k % 2))
            ns.apply_all(o)
        B.append(b)
        W.append(w)
    b = ns.join(B, "Flesh")
    ns.tag(b, "Flesh", FLESH, "SmoothPlastic", smooth_angle=75)
    w = ns.join(W, "Membrane")
    ns.tag(w, "Membrane", MEMBRANE, "SmoothPlastic", smooth_angle=60)
    return b, w


def build():
    parts = peppers(SPOTS)
    C.check_bounds("Food_GhostPepper", list(parts))


def icon():
    peppers([(-0.17, 0.1), (0.19, -0.08), (0.05, 0.32)], R=0.21, seed=3)


if __name__ == "__main__":
    C.run(build, "Food_GhostPepper", C.meta("ghost_pepper", 0.08),
          icon=("Ingredient_ghost_pepper", icon, {"pitch": 45.0}))
