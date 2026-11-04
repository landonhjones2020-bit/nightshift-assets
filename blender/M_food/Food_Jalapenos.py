"""Food_Jalapenos — sliced jalapeno rings (M_food batch).

Eight thick, slightly lobed pepper rings in two staggered rows along the roll, each tipped a few
degrees. Every ring has a green skin wall that rolls over into a thin dark-green line on top, a
pale green flesh face and inner wall, and a lumpy cream seed core in the hollow.
Parts: Skin, Flesh, Seeds.
Run:  bpyenv/bin/python blender/M_food/Food_Jalapenos.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SKIN, FLESH, SEED = "#2F8F2E", "#BFE08A", "#F1EBC5"
H = 0.065                     # ring thickness
R_OUT, R_IN = 0.165, 0.085    # outer radius, hollow radius
PITCH = 0.262
ROWS = 0.172                  # row offset from the roll's centre-line
SPOTS = [(-3.5 * PITCH + k * PITCH, ROWS if k % 2 else -ROWS) for k in range(8)]


def pepper_ring(name, rnd, r_out=R_OUT, r_in=R_IN, h=H, N=10, skin_w=0.026, e=0.022):
    """One ring at the origin: (skin, flesh, seeds) objects."""
    from mathutils import Vector
    ph = rnd.uniform(0, 6.28)
    lobes = rnd.choice((3, 4))

    def w_out(t):
        return 1 + 0.07 * math.sin(lobes * t + ph) + 0.025 * math.sin(7 * t + 2 * ph)

    def w_in(t):
        return 1 + 0.11 * math.sin(lobes * t + ph + 0.3) + 0.03 * math.sin(5 * t + ph)

    V = []

    def add(x, y, z):
        V.append((x, y, z))
        return len(V) - 1
    ob, ot, sh, fi, ib = [], [], [], [], []
    for i in range(N):
        t = 2 * math.pi * i / N
        c, s = math.cos(t), math.sin(t)
        ro, ri = r_out * w_out(t), r_in * w_in(t)
        ob.append(add(ro * c, ro * s, 0.0))
        ot.append(add((ro + 0.004) * c, (ro + 0.004) * s, h - e))
        sh.append(add((ro - skin_w) * c, (ro - skin_w) * s, h))
        fi.append(add(ri * c, ri * s, h - 0.006))
        ib.append(add(ri * 0.94 * c, ri * 0.94 * s, 0.012))
    skin_f, flesh_f = [], []
    for i in range(N):
        j = (i + 1) % N
        skin_f += [(ob[i], ob[j], ot[j], ot[i]), (ot[i], ot[j], sh[j], sh[i])]
        flesh_f += [(sh[i], sh[j], fi[j], fi[i]), (fi[i], fi[j], ib[j], ib[i])]

    def outward(c):
        return Vector((c.x, c.y, 0.0)).normalized() + Vector((0, 0, 0.6 if c.z > h - e else 0.0))

    def flesh_dir(c):
        r = math.hypot(c.x, c.y)
        return Vector((0, 0, 1)) if c.z > h - 0.01 and r > r_in * 0.9 else -Vector((c.x, c.y, 0.0)).normalized()
    skin = C.faces_obj(name + "S", V, skin_f, outward)
    flesh = C.faces_obj(name + "F", V, flesh_f, flesh_dir)

    # seed core: a lumpy cream mound filling the hollow below the flesh face, two seeds standing proud
    S = []
    cz = h * 0.66
    S.append((0.0, 0.0, cz))
    M = 7
    for i in range(M):
        t = 2 * math.pi * (i + 0.5) / M
        ri = r_in * w_in(t) * 0.93
        S.append((ri * math.cos(t), ri * math.sin(t), h * (0.56 if i % 2 else 0.44)))
    faces = [(0, 1 + i, 1 + (i + 1) % M) for i in range(M)]
    for k in range(2):
        a = ph + k * math.pi + rnd.uniform(-0.4, 0.4)
        d = r_in * 0.42
        x, y = d * math.cos(a), d * math.sin(a)
        base = len(S)
        sw, sl = 0.03, 0.042
        ca, sa = math.cos(a + 1.3), math.sin(a + 1.3)
        S += [(x + ca * sl, y + sa * sl, cz - 0.012), (x - ca * sl, y - sa * sl, cz - 0.012),
              (x - sa * sw, y + ca * sw, cz - 0.01), (x + 0.0, y + 0.0, cz + 0.016)]
        faces += [(base, base + 2, base + 3), (base + 2, base + 1, base + 3), (base + 1, base, base + 3)]
    seeds = C.faces_obj(name + "D", S, faces, lambda c: Vector((c.x, c.y, 0.0)) * 0.3 + Vector((0, 0, 1)))
    return skin, flesh, seeds


def rings(spots, seed=6, r_scale=1.0, N=10):
    rnd = random.Random(seed)
    SK, FL, SD = [], [], []
    for k, (x, y) in enumerate(spots):
        s, f, d = pepper_ring(f"J{k}", rnd, r_out=R_OUT * r_scale * rnd.uniform(0.95, 1.04),
                              r_in=R_IN * r_scale * rnd.uniform(0.94, 1.05), N=N)
        rot = (rnd.uniform(-6, 6), rnd.uniform(-6, 6), rnd.uniform(0, 360))
        for o in (s, f, d):
            o.rotation_euler = tuple(math.radians(a) for a in rot)
            o.location = (x, y, 0.012 + 0.008 * (k % 2))
            ns.apply_all(o)
        SK.append(s)
        FL.append(f)
        SD.append(d)
    sk = ns.join(SK, "Skin")
    ns.tag(sk, "Skin", SKIN, "SmoothPlastic", smooth_angle=70)
    fl = ns.join(FL, "Flesh")
    ns.tag(fl, "Flesh", FLESH, "SmoothPlastic", smooth_angle=70)
    sd = ns.join(SD, "Seeds")
    ns.tag(sd, "Seeds", SEED, "SmoothPlastic", smooth_angle=60)
    return sk, fl, sd


def build():
    parts = rings(SPOTS)
    C.check_bounds("Food_Jalapenos", list(parts))


def icon():
    rings([(-0.2, 0.1), (0.19, -0.09), (0.04, 0.34)], seed=3, r_scale=1.25, N=14)


if __name__ == "__main__":
    C.run(build, "Food_Jalapenos", C.meta("jalapenos", 0.08),
          icon=("Ingredient_jalapenos", icon, {"pitch": 45.0}))
