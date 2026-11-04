"""Lobby_WaterCooler — office water cooler (1.4 W x 4.5 H x 1.4 D).

A cream cabinet with rounded corners on a charcoal base, a brushed-steel dispensing alcove on
the front with a red (hot) and a blue (cold) lever tap over a slotted steel drip tray, a blue
water-drop badge, and a steel collar on top holding an upside-down blue water jug (Glass,
ribbed). A paper-cup dispenser tube is clipped to the right-hand side with a cup peeking out
of its bottom.

Front = -Y, pivot = bottom-centre. Decor (no collision). Socket Tap = between the two tap
spouts (a running-water / drip effect), yaw 0.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
CW = 1.16                     # cabinet width / depth
CAB_Z = (0.12, 2.95)
FY = -CW / 2
JUG_Z0 = 2.98
JUG = "#4E9FE6"
HOT = "#D9472B"
COLD = "#3C7FD8"
BASE = "#3A3D42"
ALC_Z = (1.72, 2.62)          # alcove bottom / top


def build():
    cab = C.prism(C.rrect(CW, CW, 0.2, 2), "z", CAB_Z[0], CAB_Z[1])
    ns.bevel(cab, width=0.05, segments=1)
    C.part([cab], "Cabinet", C.CREAM, smooth_angle=40)
    base = C.prism(C.rrect(CW - 0.06, CW - 0.06, 0.18, 2), "z", 0.0, CAB_Z[0] + 0.01)
    C.part([base], "Base", BASE, smooth_angle=40)

    # dispensing alcove: steel frame, dark recess panel, drip tray with slots, taps
    steel = []
    az0, az1 = ALC_Z
    steel.append(C.ring_slab(C.rrect(0.86, az1 - az0 + 0.1, 0.12, 2, 0, (az0 + az1) / 2),
                             C.rrect(0.66, az1 - az0 - 0.1, 0.08, 2, 0, (az0 + az1) / 2), "y", FY - 0.05, FY + 0.01))
    recess = ns.box((0.68, 0.02, az1 - az0 - 0.08), loc=(0, FY - 0.0, (az0 + az1) / 2), bevel=0.0)
    C.part([recess], "Recess", "#2B3036", smooth_angle=None)
    tray = ns.box((0.7, 0.24, 0.06), loc=(0, FY - 0.08, az0 + 0.06), bevel=0.02, segments=1)
    steel.append(tray)
    grille = []
    for k in range(5):
        x = -0.26 + 0.13 * k
        grille.append(C.flat_poly_3d([(x - 0.035, FY - 0.18, az0 + 0.1), (x + 0.035, FY - 0.18, az0 + 0.1),
                                      (x + 0.035, FY - 0.0, az0 + 0.1), (x - 0.035, FY - 0.0, az0 + 0.1)], up=True))
    C.part(grille, "TraySlots", "#2B3036", smooth_angle=None)
    taps = {HOT: [], COLD: []}
    for sx, col in ((-1, HOT), (1, COLD)):
        x = sx * 0.17
        steel.append(ns.cyl(0.05, 0.16, loc=(x, FY - 0.06, az1 - 0.17), rot=(90, 0, 0), verts=6, bevel=0.0))
        steel.append(ns.cyl(0.035, 0.12, loc=(x, FY - 0.13, az1 - 0.25), verts=6, bevel=0.0))
        taps[col].append(C.prism(C.rrect(0.11, 0.22, 0.04, 1, x, az1 - 0.06), "y", FY - 0.19, FY - 0.09))
    for col, objs in taps.items():
        C.part(objs, "TapHot" if col == HOT else "TapCold", col, smooth_angle=40)
    # top collar where the jug seats
    steel.append(ns.cyl(0.36, 0.1, loc=(0, 0, CAB_Z[1] + 0.03), verts=14, bevel=0.03, segments=1))
    # cup dispenser tube on the right-hand side (+X), with a bracket and a paper cup peeking out
    tx = CW / 2 + 0.11
    steel.append(ns.cyl(0.1, 1.05, loc=(tx, 0.05, 1.95), verts=10, bevel=0.0))
    steel.append(ns.cyl(0.13, 0.08, loc=(tx, 0.05, 2.5), verts=10, bevel=0.02, segments=1))
    steel.append(ns.box((0.1, 0.14, 0.34), loc=(CW / 2 + 0.03, 0.05, 2.1), bevel=0.0))
    C.part(steel, "Steel", C.STEEL, "Metal", smooth_angle=45)
    cup = ns.lathe([(0.0, 0.0), (0.075, 0.0), (0.105, 0.22), (0.0, 0.22)], verts=10, loc=(tx, 0.05, 1.21))
    C.part([cup], "Cup", "#FBF8F0", smooth_angle=50)

    # water-drop badge under the alcove
    drop = []
    for i in range(12):
        a = 2 * math.pi * i / 12
        r = 0.14
        x, z = r * math.cos(a), r * math.sin(a)
        if z > 0:                       # pull the top into a point
            x *= 1.0 - z / r * 0.75
            z *= 1.6
        drop.append((x, z + 1.28))
    C.part([C.face_dir(C.flat_poly(drop, FY - 0.006), "-Y")], "DropBadge", COLD, smooth_angle=None)

    # the jug: upside-down 5-gallon bottle, neck down in the collar, two ribs, domed base on top
    prof = [(0.0, 0.0), (0.12, 0.0), (0.12, 0.16), (0.3, 0.26), (0.52, 0.42), (0.6, 0.6), (0.6, 0.78), (0.57, 0.83),
            (0.6, 0.88), (0.6, 1.08), (0.57, 1.13), (0.6, 1.18), (0.6, 1.36), (0.48, 1.49), (0.0, 1.52)]
    jug = ns.lathe(prof, verts=16, loc=(0, 0, JUG_Z0))
    ns.tag(jug, "Jug", JUG, "Glass", transparency=0.3, cast_shadow=False, smooth_angle=50)


SOCKETS = {"Tap": ((0, FY - 0.13, ALC_Z[1] - 0.32), 0.0)}
META = {"decor": True, "collide": False, "jug": "Jug (Glass, transparency 0.3)"}

if __name__ == "__main__":
    C.run(build, "Lobby_WaterCooler", sockets=SOCKETS, budget=2000, meta=META)
