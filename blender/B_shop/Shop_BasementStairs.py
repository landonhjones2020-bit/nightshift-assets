"""Shop_BasementStairs — straight run down to the basement: drops 12 studs (floor to floor),
5 studs clear width, 16 risers of 0.75 and 15 open wooden treads 1.0 deep (open risers:
nothing between the steps but darkness), charcoal steel stringers, safety-mustard pipe
handrails on both sides and hazard strips on the top and bottom nosings.

PIVOT = the TOP LANDING EDGE: centre of the width, on the upper floor level (z = 0), at
the line where the upper floor ends and the first riser drops. The stairs descend toward
+Y (away from the front/LookVector): tread k (1..15) top is at z = -0.75k over
y = k-1 .. k; the basement floor starts at y = 15, z = -12. The stairwell opening in the
upper floor must be at least 5.6 wide x 15 long (y = 0 .. 15) plus head room.
Sockets: Top (on the landing, facing down the run), Bottom (basement floor at the foot,
facing away from the stairs), LightsOutSpawn (foot of the stairs, facing up the run; 7.6).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
N_RISE, RISE, RUN = 16, 0.75, 1.0
HW = 2.5                  # half clear width
DROP = N_RISE * RISE      # 12
RAIL_H = 3.0
RAIL = "#C9962F"


def build():
    treads = []
    for k in range(1, N_RISE):
        z = -RISE * k
        treads.append(ns.box((2 * HW, RUN + 0.1, 0.2), loc=(0, k - 0.5 + 0.05, z - 0.1), bevel=0.04, segments=1))
    C.part(treads, "Treads", C.WOOD, "WoodPlanks", can_collide=True, smooth_angle=40)

    hazard = [ns.box((2 * HW, 0.25, 0.04), loc=(0, 0.125, 0.0), bevel=0.0),
              ns.box((2 * HW, 0.22, 0.03), loc=(0, N_RISE - 1 - 0.0 + 0.04, -RISE * (N_RISE - 1) + 0.015),
                     bevel=0.0)]
    ns.tag(C.merge(hazard, "Hazard"), "Hazard", C.MUSTARD)

    # stringers: sloped steel channels either side, cut vertical at the top, flat on the floor
    s = RISE / RUN
    y_lo_end = (DROP - 1.1) / s
    y_hi_end = (DROP + 0.4) / s
    poly = [(-0.2, 0.4 + 0.15), (y_hi_end, -DROP), (y_lo_end, -DROP), (-0.2, -1.1 + 0.15)]
    steel = []
    for sx in (-1, 1):
        x0, x1 = sorted((sx * HW, sx * (HW + 0.32)))
        st = C.prism(poly, "x", x0, x1)
        ns.bevel(st, width=0.04, segments=1)
        steel.append(st)
    # mid-run support columns and a cross tie under the stringers
    ym = 9.0
    for sx in (-1, 1):
        steel.append(ns.box((0.3, 0.3, DROP - (s * ym + 1.1)), loc=(sx * (HW + 0.16), ym, -DROP + (DROP - (s * ym + 1.1)) / 2),
                            bevel=0.03, segments=1))
    steel.append(ns.box((2 * HW + 0.6, 0.25, 0.3), loc=(0, ym, -s * ym - 1.2), bevel=0.03, segments=1))
    C.part(steel, "Stringers", C.CHARCOAL, "Metal", can_collide=True, smooth_angle=40)

    # handrails: pipe rail 3.0 above the nosing line with level extensions top and bottom
    rail = []
    for sx in (-1, 1):
        x = sx * (HW + 0.16)
        path = [(x, -1.2, RAIL_H), (x, 0.0, RAIL_H), (x, DROP / s + 0.0, -DROP + RAIL_H), (x, DROP / s + 1.3, -DROP + RAIL_H)]
        rail.append(C.pipe(path, 0.1, sides=8, corner=0.4, corner_segs=2))
        for py in (-1.0, 2.5, 6.0, 9.5, 13.0, 16.2):
            top = -s * max(0.0, min(py, DROP / s)) + RAIL_H
            base = (-s * py + 0.55) if py <= y_hi_end else -DROP
            if py < 0:
                base = 0.0
            if py > DROP / s:
                base = -DROP
            rail.append(ns.cyl(0.07, top - base, loc=(x, py, (top + base) / 2), verts=8, bevel=0.0))
            rail.append(ns.cyl(0.16, 0.08, loc=(x, py, base + 0.04), verts=8, bevel=0.02, segments=1))
    C.part(rail, "Handrail", RAIL, "Metal", smooth_angle=55)


META = {"pivot": "top landing edge: width centre, upper floor level, where the first riser drops",
        "descends": "+Y (away from LookVector)", "drop": DROP, "risers": N_RISE, "rise": RISE, "run": RUN,
        "treads": N_RISE - 1, "clear_width": 2 * HW, "footprint": {"x": [-2.98, 2.98], "y": [-1.3, 17.4]},
        "floor_opening": {"x": [-2.9, 2.9], "y": [0, 15]}, "bottom_floor": {"y_from": 15.0, "z": -DROP}}

if __name__ == "__main__":
    C.run(build, "Shop_BasementStairs", pivot=(0, 0, 0), meta=META,
          sockets={"Top": ((0, -0.5, 0), 180.0), "Bottom": ((0, 15.8, -DROP), 180.0),
                   "LightsOutSpawn": ((0, 16.5, -DROP), 0.0)})
