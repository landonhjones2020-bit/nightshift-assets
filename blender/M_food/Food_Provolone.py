"""Food_Provolone — provolone slices (M_food batch).

Two large round slices (r ~0.48) overlapping along the roll: the second one's near edge rides up
over the first, and both sag a little where they hang past the long sides. Pale cream faces
ringed by a thin tan smoked rind that shows on top and around the crisp cut edge.
Parts: Cheese, Rind.
Food_Provolone_Melted is the toasted variant.
Run:  bpyenv/bin/python blender/M_food/Food_Provolone.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
FACE, RIND = "#F2E2B0", "#C9944E"
MELT = "#F5E1A4"            # melted provolone (a touch warmer and glossier than the slice face)
R = 0.48
THICK = 0.03


def provolone(xs=(-0.41, 0.41), ys=(0.012, -0.012), R=R, seed=2, N=26, droop=True, ride=0.034, yaws=(0, 0),
              tilt=(0, 0)):
    """Round slices along X; every slice after the first rides up over the previous one where they
    overlap (`ride` = lift at the overlap)."""
    rnd = random.Random(seed)
    F_, E_ = [], []
    for k, (x0, y0) in enumerate(zip(xs, ys)):
        ph = rnd.uniform(0, 6.28)
        r = R * rnd.uniform(0.985, 1.015)
        outline = C.circle(r, N, phase=ph, wobble=lambda t, ph=ph: 0.012 * math.sin(3 * t + ph)
                           + 0.006 * math.sin(7 * t + 2 * ph))
        prev = xs[k - 1] + R if k > 0 else None      # previous slice's far (+X) edge, world x

        def zfn(x, y, s, i, ph=ph, x0=x0, prev=prev):
            z = 0.004 * math.sin(4.0 * x + ph) * s
            if prev is not None:
                # ride over the previous slice: full lift over the overlap, easing out past it
                wx = x0 + x
                z += ride * (1 - C.smooth((wx - (prev - 0.02)) / 0.16))
            return z
        f, e = C.sheet(f"Pv{k}", outline, THICK, zfn=zfn, center=(0, 0), inner=(0.5, 0.955), edge=0.3,
                       split_edge=True, rim_on_top=True)
        for o in (f, e):
            o.rotation_euler = (math.radians(tilt[k % len(tilt)] * 0.5), math.radians(tilt[k % len(tilt)]),
                                math.radians(yaws[k % len(yaws)]))
            o.location = (x0, y0, 0.003 + 0.004 * k)
            C.drape(o, C.overhang_droop(k=0.6, kx=0.4)) if droop else ns.apply_all(o)
        F_.append(f)
        E_.append(e)
    m = ns.join(F_, "Cheese")
    ns.tag(m, "Cheese", FACE, "SmoothPlastic", smooth_angle=70)
    d = ns.join(E_, "Rind")
    ns.tag(d, "Rind", RIND, "SmoothPlastic", smooth_angle=70)
    return [m, d]


def build():
    parts = provolone()
    C.check_bounds("Food_Provolone", parts)


def icon():
    provolone(xs=(-0.26, 0.26), ys=(0.08, -0.08), R=0.4, N=36, droop=False, ride=0.05, yaws=(0, 0), tilt=(-4, 4))


if __name__ == "__main__":
    C.run(build, "Food_Provolone", C.meta("provolone", 0.06),
          icon=("Ingredient_provolone", icon, {"pitch": 42.0}))
