"""Shop_CeilingFan — diner ceiling fan for the 20-stud dining room ceiling (6 x 2.5 x 6).

Chrome ceiling canopy and down-rod, a chrome motor housing with a navy band, four pitched
wooden paddle blades on wooden irons, a switch cup and a warm glowing light bowl with a
chrome finial underneath.
Parts code must find: Blades (role fan_blades: all four blades + their irons, ONE part, spun
about the vertical axis through Socket_Spin) and Bowl (role lamp, Neon: dim / kill it).
PIVOT = TOP of the canopy (z = 0, flush on the ceiling); everything hangs below.
Sockets: Spin (blade hub centre on the rotation axis, yaw 0), Light (just under the bowl).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
BLADE_Z = -1.62          # blade plane (mid thickness)
R0, R1 = 0.78, 2.98      # blade root / tip radius
PITCH = 11.0             # blade pitch about its long axis (deg)
BOWL_LAMP = "#FFE3A8"


def blade(k):
    """One paddle blade + its iron, built along +X then turned to slot k (90 deg steps)."""
    out = C.fillet([(R0, -0.2), (R1 - 0.3, -0.3), (R1, -0.24), (R1, 0.24), (R1 - 0.3, 0.3), (R0, 0.2)],
                   [0.04, 0.0, 0.12, 0.12, 0.0, 0.04], 2)
    b = C.prism(out, "z", -0.04, 0.04)
    iron = ns.box((R0 + 0.32 - 0.42, 0.2, 0.07), loc=((0.42 + R0 + 0.32) / 2, 0, 0.075), bevel=0.0)
    parts = [b, iron]
    for o in parts:
        ns.apply_all(o)
        o.rotation_euler = (math.radians(PITCH), 0, math.radians(90 * k))
        o.location = (0, 0, BLADE_Z)
        ns.apply_all(o)
    return parts


def build():
    canopy = ns.lathe([(0.0, 0.0), (0.46, 0.0), (0.44, -0.08), (0.3, -0.28), (0.12, -0.34), (0.0, -0.34)], verts=12)
    rod = ns.cyl(0.06, 0.9, loc=(0, 0, -0.34 - 0.45), verts=6, bevel=0.0)
    coupling = ns.cyl(0.11, 0.14, loc=(0, 0, -1.22), verts=8, bevel=0.0)
    housing = ns.lathe([(0.0, -1.27), (0.32, -1.27), (0.52, -1.36), (0.6, -1.5), (0.6, -1.7), (0.5, -1.78), (0.0, -1.78)],
                       verts=12)
    cup = ns.lathe([(0.0, -1.78), (0.4, -1.78), (0.42, -1.86), (0.36, -1.96), (0.0, -1.96)], verts=12)
    finial = ns.sphere(0.07, loc=(0, 0, -2.42), segs=6, rings=4)
    C.part([canopy, rod, coupling, housing, cup, finial], "Chrome", C.CHROME, "Metal", smooth_angle=45)
    band = C.lathe_ring([(0.6, -1.53), (0.625, -1.55), (0.625, -1.65), (0.6, -1.67)], verts=12)
    C.part([band], "Band", C.NAVY, smooth_angle=45)

    bl = []
    for k in range(4):
        bl += blade(k)
    ns.tag(C.merge(bl, "Blades"), "Blades", C.WOOD, "Wood", recolor="fan_blades", smooth_angle=40)

    bowl = C.lathe_open([(0.38, -1.95), (0.37, -2.08), (0.3, -2.24), (0.17, -2.33), (0.0, -2.36)], verts=12)
    ns.tag(bowl, "Bowl", BOWL_LAMP, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=60)


SOCKETS = {"Spin": ((0, 0, BLADE_Z), 0.0), "Light": ((0, 0, -2.6), 0.0)}
META = {"pivot": "top of the ceiling canopy (hangs below)", "drop": 2.5, "spin_part": "Blades",
        "spin": "about the vertical axis (Y) through Socket_Spin",
        "light_hint": {"type": "PointLight", "color": "#FFD9A0", "range": 16, "brightness": 0.6}}

if __name__ == "__main__":
    C.run(build, "Shop_CeilingFan", sockets=SOCKETS, pivot=(0, 0, 0), meta=META, preview=C.hanging_preview)
