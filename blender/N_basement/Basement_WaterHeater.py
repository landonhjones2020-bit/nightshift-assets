"""Basement_WaterHeater — tall old gas water heater in dingy cream with rust streaks.

A cream enamel jacket (2.2 across) on a dark base ring, gently domed top. On top: a steel
draft hood on little legs with the vent pipe elbowing back toward the wall, and two copper
water pipes (cold left with a red hand-wheel valve, hot right) that rise and bend back to
the wall. Right side: a brass T&P relief valve whose copper discharge pipe runs down to the
floor. Front: the black gas-control box with a red-orange knob and its gas pipe, the
burner access panel below it, and a mustard rating plate. Rust streaks run down from the
top seam and the relief valve. Jacket and base collide.
Front faces -Y, pivot = bottom-centre. 2.4 x 6 x 2.4.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
R = 1.1
TOP = 5.28            # jacket crown
CTRL = "#2B2D31"


def build():
    jacket = ns.lathe([(R - 0.02, 0.28), (R, 0.36), (R, 4.95), (R - 0.07, 5.13), (R - 0.32, 5.24), (0.0, TOP)], verts=16)
    C.part([jacket], "Jacket", C.CREAM, can_collide=True, smooth_angle=50)
    base = ns.cyl(R + 0.03, 0.32, loc=(0, 0, 0.16), verts=16, bevel=0.0)
    C.part([base], "BaseRing", C.CONCRETE_DARK, "Metal", can_collide=True, smooth_angle=50)

    # ---- draft hood + vent elbow back to the wall ------------------------------------
    hx, hy = 0.0, 0.12
    hood = ns.cyl(0.46, 0.26, loc=(hx, hy, 5.47), verts=10, radius_top=0.3, bevel=0.0)
    legs = [C.rod((hx + 0.38 * dx, hy + 0.38 * dy, TOP - 0.06), (hx + 0.38 * dx, hy + 0.38 * dy, 5.36), 0.035, verts=4)
            for dx, dy in ((1, 0), (-0.5, 0.87), (-0.5, -0.87))]
    vent = C.pipe([(hx, hy, 5.15), (hx, hy, 5.72), (hx, R + 0.1, 5.72)], 0.24, sides=8, corner=0.3)   # bend r > pipe r
    C.part([hood, vent] + legs, "Vent", C.STEEL, "Metal", smooth_angle=45)

    # ---- copper water pipes (cold left with the red valve, hot right) -----------------
    copper = []
    for x in (-0.62, 0.62):
        copper.append(C.pipe([(x, 0.18, 5.05), (x, 0.18, 5.62), (x, R + 0.1, 5.62)], 0.085, sides=6, corner=0.16))
        copper.append(ns.cyl(0.13, 0.16, loc=(x, 0.18, 5.2), verts=6, bevel=0.0))      # union nut
    copper.append(ns.cyl(0.14, 0.26, loc=(-0.62, 0.18, 5.42), verts=6, bevel=0.0))      # valve body
    copper.append(C.rod((-0.62, 0.05, 5.42), (-0.62, -0.18, 5.42), 0.035, verts=4))     # valve stem
    # T&P relief valve on the right, copper discharge pipe down to the floor
    tp = [C.rod((R - 0.04, -0.1, 4.55), (R + 0.2, -0.1, 4.55), 0.09, verts=6),
          ns.cyl(0.1, 0.16, loc=(R + 0.17, -0.1, 4.67), verts=6, bevel=0.0)]
    lever = [C.rod((R + 0.17, -0.1, 4.75), (R + 0.02, -0.1, 4.82), 0.025, verts=4)]
    copper.append(C.pipe([(R + 0.17, -0.1, 4.5), (R + 0.17, -0.1, 0.04)], 0.06, sides=6))
    C.part(copper, "Copper", C.COPPER, "Metal", smooth_angle=45)
    C.part(tp + lever, "Brass", C.BRASS, "Metal", smooth_angle=45)
    wheel = C.handwheel((-0.62, -0.2, 5.42), (0, -1, 0), r=0.2, verts=8)
    C.part(wheel, "Valve", C.VALVE_RED, smooth_angle=45)

    # ---- gas control box, knob, gas pipe, burner panel, rating plate ------------------
    box = ns.box((0.56, 0.36, 0.5), loc=(0, -R + 0.06, 1.2), bevel=0.05, segments=1)
    gas = C.pipe([(0.2, -R - 0.02, 1.08), (0.52, -R - 0.06, 1.08), (0.52, -R - 0.06, 0.04)], 0.055, sides=6,
                 corner=0.12)
    C.part([box, gas], "Control", CTRL, "Metal", smooth_angle=40)
    knob = ns.cyl(0.13, 0.1, loc=(0, -R - 0.15, 1.26), rot=(90, 0, 0), verts=8, bevel=0.02, segments=1)
    C.part([knob], "Knob", C.BRAND, smooth_angle=40)
    panel = C.patch_cyl(0, 0, R, 0, 0.7, 0.44, 0.84, segs=3)
    C.part([panel], "BurnerPanel", "#8F8878", smooth_angle=None)
    plate = C.patch_cyl(0, 0, R, -38, 0.56, 3.1, 3.85, segs=3)
    C.part([plate], "Plate", C.MUSTARD, smooth_angle=None)
    ink = [C.patch_cyl(0, 0, R, -38 + da, w, z, z + 0.05, segs=2, proud=0.018)
           for da, w, z in ((-2, 0.4, 3.66), (2, 0.32, 3.52), (-1, 0.38, 3.38), (3, 0.26, 3.24))]
    C.part(ink, "PlateInk", C.INK, smooth_angle=None)

    # ---- rust streaks ------------------------------------------------------------------
    # rust bleeding out of the top seam (a band) and running down in streaks
    streaks = [C.band(R + 0.012, 0.09, loc=(0, 0, 4.93), verts=16)]     # spans z 4.885 .. 4.975
    streaks += [C.streak_cyl(0, 0, R, a, 4.89, ln, w, seed=k, sway=0.05) for k, (a, ln, w) in
                enumerate(((-62, 1.6, 0.3), (-8, 0.7, 0.2), (18, 1.1, 0.24), (44, 1.9, 0.3), (100, 0.8, 0.22),
                           (135, 1.4, 0.26), (-150, 1.7, 0.28), (-105, 0.9, 0.22)))]
    streaks.append(C.streak_cyl(0, 0, R, 84, 4.5, 1.5, 0.2, seed=9))     # under the relief valve
    C.part(streaks, "Rust", C.RUST, smooth_angle=None)


META = {"collide": "jacket + base ring", "valve_part": "Valve (red hand wheel on the cold pipe)"}

if __name__ == "__main__":
    C.run(build, "Basement_WaterHeater", budget=2000, meta=META)
