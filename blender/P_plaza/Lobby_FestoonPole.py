"""Lobby_FestoonPole — wooden market-light pole with a cross-arm (1 x 14 x 1).

A cast-stone footing, a navy steel post shoe with bolt heads, a round tapered wooden pole with a
red-orange guard band and a mustard ring, a short wooden cross-arm near the top on two navy
knee braces, a navy cap, and a chrome eye bolt on top where a light string hooks on.
Footing, shoe and pole collide.

Front = -Y, pivot = bottom-centre. Socket Hook = centre of the eye bolt ring on top (where
Lobby_FestoonSpan / Lobby_Bunting start or end).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

FOOT_H = 0.3
SHOE_H = 1.05
POLE_TOP = 13.45
ARM_Z = 12.75
EYE_Z = 13.84               # eye ring centre
EYE_R = 0.12


def build():
    stone = C.prism(C.rrect(1.0, 1.0, 0.16, 2), "z", 0.0, FOOT_H)
    ns.bevel(stone, width=0.06, segments=1)
    shoe = [C.prism(C.rrect(0.74, 0.74, 0.1, 1), "z", FOOT_H - 0.02, FOOT_H + SHOE_H),
            C.prism(C.rrect(0.9, 0.9, 0.12, 1), "z", FOOT_H - 0.02, FOOT_H + 0.1)]
    ns.bevel(shoe[0], width=0.04, segments=1)
    bolts = []
    for k in range(4):
        p = C.yaw_point((0.0, -0.375, FOOT_H + 0.72), 90 * k)
        b = ns.cyl(0.06, 0.06, verts=6, bevel=0.0)
        C.place(b, p, yaw=90 * k, pitch=90)
        bolts.append(b)
        q = C.yaw_point((0.34, -0.34, FOOT_H + 0.1), 90 * k)
        bolts.append(ns.cyl(0.07, 0.05, loc=(q[0], q[1], q[2] + 0.025), verts=6, bevel=0.0))
    pole = C.rod((0, 0, FOOT_H + 0.4), (0, 0, POLE_TOP), 0.29, verts=10, r_top=0.23)
    guard = ns.lathe([(0.0, 2.25), (0.3, 2.25), (0.31, 2.32), (0.31, 3.12), (0.3, 3.2), (0.0, 3.2)], verts=10)
    ring = ns.cyl(0.29, 0.12, loc=(0, 0, 3.32), verts=10, bevel=0.0)
    # cross-arm (bolted through the pole) + knee braces
    arm = ns.box((1.0, 0.28, 0.3), loc=(0, 0, ARM_Z), bevel=0.07, segments=1)
    braces = []
    for s in (-1, 1):
        braces.append(C.rod((s * 0.42, 0.0, ARM_Z - 0.12), (s * 0.2, 0.0, ARM_Z - 0.85), 0.04, verts=4))
        braces.append(ns.cyl(0.055, 0.07, loc=(s * 0.38, -0.15, ARM_Z), rot=(90, 0, 0), verts=6, bevel=0.0))
    braces.append(ns.box((0.08, 0.56, 0.08), loc=(0, 0, ARM_Z - 0.85), bevel=0.0))
    cap = ns.lathe([(0.0, POLE_TOP - 0.06), (0.25, POLE_TOP - 0.06), (0.27, POLE_TOP + 0.02), (0.17, POLE_TOP + 0.16),
                    (0.0, POLE_TOP + 0.2)], verts=10)
    eye = ns.torus(EYE_R, 0.035, major_segs=10, minor_segs=4)
    C.place(eye, (0, 0, EYE_Z), pitch=90)
    shank = C.rod((0, 0, POLE_TOP + 0.12), (0, 0, EYE_Z - EYE_R + 0.01), 0.035, verts=5)

    C.part([stone], "Footing", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(shoe, "Shoe", C.STEEL_NAVY, "Metal", can_collide=True, smooth_angle=40)
    C.part([pole], "Pole", C.WOOD_LIGHT, "Wood", can_collide=True, smooth_angle=50)
    C.part([arm], "CrossArm", C.WOOD, "Wood", smooth_angle=40)
    C.part(braces + [cap], "Braces", C.STEEL_NAVY, "Metal", smooth_angle=45)
    C.part([guard], "Guard", C.BRAND, smooth_angle=45)
    C.part([ring], "Ring", C.MUSTARD, "Metal", smooth_angle=45)
    C.part([eye, shank] + bolts, "EyeBolt", C.CHROME, "Metal", smooth_angle=50)


SOCKETS = {"Hook": ((0.0, 0.0, EYE_Z), 0.0)}
META = {"hook_height": EYE_Z, "pairs_with": "Lobby_FestoonSpan / Lobby_Bunting (pivot at their start hook)"}

if __name__ == "__main__":
    C.run(build, "Lobby_FestoonPole", sockets=SOCKETS, meta=META, budget=2000, pivot=(0.0, 0.0, 0.0))
