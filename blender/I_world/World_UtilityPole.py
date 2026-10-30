"""World_UtilityPole — weathered wooden power pole (~2.5 wide x 26 tall).

Tapered grey-brown wood pole with a crossarm on top (a T silhouette) carrying three
green-glass insulators, two steel brace straps, a pole-mounted transformer can on the +X
side and staggered step bolts from 7 to 22 studs up.

Orientation: the crossarm runs front-to-back (Blender Y = Roblox Z), so the wires leave
the insulators along +/-X: place poles in a row along their local X axis (yaw 0 = a
road running along X) and string Beams Wire1->Wire1, Wire2->Wire2, Wire3->Wire3.
Sockets Wire1/Wire2/Wire3 = insulator tips (front, centre, back).
Exports as 3 MeshParts (Wood, Metal, Glass), no collision. Pivot = pole base (origin).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
TOP = 25.0                  # pole top (inside the crossarm)
ARM_Z = 25.15               # crossarm centre
ARM_H = 0.45
ARM_L = 6.0
INS_Y = (-2.55, 0.0, 2.55)  # insulator positions along the crossarm
INS_BASE = ARM_Z + ARM_H / 2
INS_H = 0.62
WOOD = "#6B5B4B"            # weathered grey-brown
WOOD_DARK = "#5A4B3E"
HARDWARE = "#474C52"
CAN = "#7E868C"
INSULATOR = "#5FB0A0"


def build():
    pole = C.lathe([(0.62, 0.0), (0.55, 3.0), (0.42, TOP)], verts=8, phase=22.5)
    arm = C.box((0.46, ARM_L, ARM_H), loc=(0, 0, ARM_Z), bevel=0.05)
    C.part([pole], "Pole", WOOD, "Wood", smooth_angle=None)
    C.part([arm], "Crossarm", WOOD_DARK, "Wood", smooth_angle=None)

    hw = []
    # diagonal brace straps: pole -> crossarm underside
    for sy in (-1, 1):
        hw.append(C.beam((0.0, sy * 0.3, TOP - 1.7), (0.0, sy * 1.75, ARM_Z - ARM_H / 2 + 0.02), 0.12, 0.05))
    # staggered step bolts (triangular stubs) from 7 to 22 studs
    for k in range(9):
        z = 7.0 + k * 1.85
        sy = -1 if k % 2 == 0 else 1
        r = 0.55 - 0.13 * (z / TOP)
        hw.append(C.rod((0.0, sy * (r - 0.1), z), (0.0, sy * (r + 0.42), z), 0.06, verts=3))
    # transformer can on the +X side, with a mounting bracket and a top bushing
    cx = 1.3
    can = C.lathe([(0.6, 0.0), (0.62, 0.12), (0.62, 1.55), (0.67, 1.62), (0.42, 1.82), (0.0, 1.86)],
                  verts=7, loc=(cx, 0.0, 19.2))
    bracket = C.box((0.9, 0.5, 1.1), loc=(0.66, 0.0, 20.1))
    bushing = C.rod((cx + 0.15, 0.0, 20.9), (cx + 0.15, 0.0, 21.45), 0.1, verts=4)
    C.part([can, bushing], "Transformer", CAN, "Metal", smooth_angle=50)
    C.part(hw + [bracket], "Hardware", HARDWARE, "Metal", smooth_angle=None)

    ins = []
    for y in INS_Y:
        ins.append(C.lathe([(0.21, 0.0), (0.26, 0.16), (0.11, 0.48), (0.0, INS_H)], verts=6,
                           loc=(0.0, y, INS_BASE - 0.02), phase=30))
    C.part(ins, "Insulators", INSULATOR, "Glass", smooth_angle=50)


SOCKETS = {f"Wire{i + 1}": ((0.0, y, INS_BASE - 0.02 + INS_H), 0.0) for i, y in enumerate(INS_Y)}
META = {"kind": "utility_pole", "pivot": "pole base",
        "wires": "Beams run along local X between neighbouring poles: Wire1 = front (-Z in Roblox), "
                 "Wire2 = centre, Wire3 = back"}

if __name__ == "__main__":
    C.run(build, "World_UtilityPole", sockets=SOCKETS, meta=META)
