"""Shop_CoffeeMachine — commercial twin drip coffee brewer for a worktop (Break Room / kitchen).

Stainless base with two black warmer plates, a back tower and an overhanging brew hood
(control strip: a red-orange label plate and two lit rocker switches), two black brew
funnels with handles. On the warmers stand two glass decanters (part Glass, role "glass",
transparent) with coffee inside — the left one nearly full, the right one half full — with
a black "regular" collar and an orange "decaf" collar, each with a handle.
Front faces -Y, pivot = bottom-centre. ~2.4 x 2.0 x 1.4.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H = 2.4, 2.0
BASE_H = 0.16
POTS = ((-0.6, 0.47, "#26272B"), (0.6, 0.27, "#E5782E"))     # (x, coffee level, collar colour)
PY = -0.16                                                     # pot axis y
BLACK = "#1E1F22"
COFFEE = "#6A3816"


def pot_profile():
    """Decanter glass outline (r, z) from the bottom up to the neck."""
    return [(0.0, 0.0), (0.2, 0.0), (0.31, 0.1), (0.34, 0.27), (0.29, 0.46), (0.19, 0.58), (0.17, 0.64)]


def build():
    steel = [ns.box((W, 1.36, BASE_H), loc=(0, -0.02, BASE_H / 2), bevel=0.04, segments=1),
             ns.box((W - 0.02, 0.44, H - BASE_H - 0.03), loc=(0, 0.44, BASE_H + (H - BASE_H - 0.03) / 2), bevel=0.0),
             ns.box((W, 1.0, 0.4), loc=(0, 0.0, H - 0.2), bevel=0.05, segments=1)]
    C.part(steel, "Steel", C.STAINLESS, "Metal", smooth_angle=35)

    black, glass, coffee, collars = [], [], [], {}
    for x, level, col in POTS:
        black.append(ns.cyl(0.36, 0.03, loc=(x, PY, BASE_H + 0.015), verts=10, bevel=0.0))           # warmer plate
        # brew funnel under the hood + handle
        black.append(ns.lathe([(0.2, 0.0), (0.34, 0.2), (0.38, 0.3), (0.0, 0.3)], verts=10, loc=(x, PY + 0.02, H - 0.72)))
        black.append(ns.box((0.1, 0.42, 0.08), loc=(x, PY - 0.5, H - 0.48), bevel=0.0))
        # decanter: glass bulb, coffee inside, collar + handle
        z0 = BASE_H + 0.03
        g = ns.lathe(pot_profile(), verts=10, loc=(x, PY, z0))
        glass.append(g)
        cprof = []
        for r, z in pot_profile():
            if z <= level:
                cprof.append((max(0.0, r - 0.025), z + 0.02 if z == 0 else z))
        # close the coffee at its surface: radius at `level` by interpolation
        prof = pot_profile()
        for (r0, z0p), (r1, z1p) in zip(prof[:-1], prof[1:]):
            if z0p <= level <= z1p:
                rl = r0 + (r1 - r0) * (level - z0p) / max(1e-6, z1p - z0p)
                cprof.append((rl - 0.025, level))
                break
        cprof.append((0.0, level))
        coffee.append(ns.lathe(cprof, verts=10, loc=(x, PY, z0)))
        collar_z = z0 + 0.6
        collars.setdefault(col, []).append(ns.cyl(0.205, 0.16, loc=(x, PY, collar_z + 0.08), verts=10, radius_top=0.22,
                                                  bevel=0.0))
        collars[col].append(C.pipe([(x + 0.2, PY, collar_z + 0.1), (x + 0.42, PY, collar_z + 0.04),
                                    (x + 0.42, PY, z0 + 0.3), (x + 0.3, PY, z0 + 0.22)], 0.04, sides=5))
    C.part(black, "Black", BLACK, smooth_angle=40)
    C.part(glass, "Glass", "#8FB0BC", "Glass", transparency=0.8, recolor="glass", smooth_angle=60)
    C.part(coffee, "Coffee", COFFEE, smooth_angle=60)
    for i, (col, objs) in enumerate(collars.items()):
        C.part(objs, ("CollarRegular", "CollarDecaf")[i], col, smooth_angle=45)

    # hood front control strip
    fy = -0.5
    label = ns.box((0.9, 0.02, 0.2), loc=(0, fy - 0.01, H - 0.2), bevel=0.0)
    C.part([label], "Label", C.BRAND, smooth_angle=None)
    lights = [ns.box((0.1, 0.05, 0.12), loc=(x, fy - 0.02, H - 0.2), bevel=0.0) for x in (-0.75, 0.75)]
    C.part(lights[:1], "SwitchRed", "#FF5A3C", smooth_angle=None)
    C.part(lights[1:], "SwitchGreen", "#5CD67F", smooth_angle=None)


META = {"pots": {"left": "nearly full, black regular collar", "right": "half full, orange decaf collar"}}

if __name__ == "__main__":
    C.run(build, "Shop_CoffeeMachine", budget=900, meta=META)
