"""Shop_Radio — retro 1950s tabletop diner radio (sits on a worktop / shelf).

Ivory "loaf" body with big rounded top corners and soft bevels, a cherry-red front plate
following the body curve, a speaker grille of chrome bars over dark cloth on the left with
a little gold badge, a big round tuning dial on the right (chrome bezel, cream face, tick
ring, red needle), two cream knobs and rubber feet.
Socket Speaker = centre of the grille (yaw 0 = sound faces front, -Y).
Front faces -Y, pivot = bottom-centre. ~2.0 x 1.3 x 0.9.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, BH, D = 2.0, 1.2, 0.86
FOOT = 0.06
IVORY = "#F3E3C3"
CHERRY = "#C23038"
FY = -D / 2                      # front face
GRILLE = (-0.8, 0.06, 0.34, 0.98)  # x0, x1, z0, z1 (absolute z)
DIAL = (0.5, 0.7, 0.27)          # x, z, radius


def build():
    z0 = FOOT
    prof = C.fillet([(-W / 2, z0), (W / 2, z0), (W / 2, z0 + BH), (-W / 2, z0 + BH)], [0.12, 0.12, 0.5, 0.5], 3)
    body = C.prism(prof, "y", FY, D / 2)
    ns.bevel(body, width=0.07, segments=2, angle=50)
    C.part([body], "Body", IVORY, smooth_angle=45)

    # red front plate following the body outline (inset 0.09)
    pin = C.fillet([(-W / 2 + 0.09, z0 + 0.09), (W / 2 - 0.09, z0 + 0.09), (W / 2 - 0.09, z0 + BH - 0.09),
                    (-W / 2 + 0.09, z0 + BH - 0.09)], [0.06, 0.06, 0.42, 0.42], 3)
    plate = C.prism(pin, "y", FY - 0.025, FY + 0.01)
    C.part([plate], "Plate", CHERRY, smooth_angle=40)
    py = FY - 0.025            # plate front

    # grille: dark cloth + chrome bars + gold badge
    gx0, gx1, gz0, gz1 = GRILLE
    cloth = C.quad_xz(gx0, gx1, gz0, gz1, py - 0.004)
    C.part([cloth], "Cloth", "#2B2522", "Fabric", smooth_angle=None)
    bars = []
    n = 6
    for k in range(n):
        z = gz0 + 0.06 + (gz1 - gz0 - 0.12) * k / (n - 1)
        bars.append(ns.cyl(0.032, gx1 - gx0 + 0.04, loc=((gx0 + gx1) / 2, py - 0.035, z), rot=(0, 90, 0), verts=6,
                           bevel=0.0))
    for x in (gx0 - 0.01, gx1 + 0.01):
        bars.append(ns.box((0.05, 0.05, gz1 - gz0 + 0.06), loc=(x, py - 0.02, (gz0 + gz1) / 2), bevel=0.0))
    C.part(bars, "Grille", C.CHROME, "Metal", smooth_angle=50)
    badge = ns.cyl(0.075, 0.04, loc=((gx0 + gx1) / 2, py - 0.07, (gz0 + gz1) / 2), rot=(90, 0, 0), verts=8, bevel=0.0)
    C.part([badge], "Badge", "#D9A93E", "Metal", smooth_angle=40)

    # dial
    dx, dz, dr = DIAL
    bezel = ns.cyl(dr + 0.04, 0.06, loc=(dx, py - 0.02, dz), rot=(90, 0, 0), verts=16, bevel=0.0)
    C.part([bezel], "Bezel", C.CHROME, "Metal", smooth_angle=40)
    face = C.disc(dr, verts=16)
    face.rotation_euler = (math.radians(90), 0, 0)
    face.location = (dx, py - 0.058, dz)
    ns.apply_all(face)
    C.part([C.face_dir(face, "-Y")], "DialFace", "#F4EAD2", smooth_angle=None)
    ticks = []
    for k in range(11):
        a = math.radians(-125 + 25 * k)
        r0 = dr * (0.72 if k % 2 == 0 else 0.8)
        ticks.append(C.strip_xz((dx + r0 * math.sin(a), dz + r0 * math.cos(a)),
                                (dx + dr * 0.9 * math.sin(a), dz + dr * 0.9 * math.cos(a)), 0.022, py - 0.066))
    C.part(ticks, "Ticks", C.INK, smooth_angle=None)
    a = math.radians(38)
    needle = [C.strip_xz((dx - 0.04 * math.sin(a), dz - 0.04 * math.cos(a)), (dx + dr * 0.86 * math.sin(a), dz + dr * 0.86 * math.cos(a)),
                         0.03, py - 0.074)]
    hub = ns.cyl(0.04, 0.03, loc=(dx, py - 0.078, dz), rot=(90, 0, 0), verts=8, bevel=0.0)
    C.part(needle + [hub], "Needle", "#D9342B", smooth_angle=None)

    # knobs (cream) under the dial
    knobs = [ns.cyl(0.085, 0.09, loc=(x, py - 0.045, z0 + 0.24), rot=(90, 0, 0), verts=10, bevel=0.0)
             for x in (0.3, 0.7)]
    C.part(knobs, "Knobs", "#F6EEDC", smooth_angle=40)
    feet = [ns.box((0.26, 0.2, FOOT + 0.01), loc=(sx * (W / 2 - 0.3), sy * (D / 2 - 0.2), (FOOT + 0.01) / 2), bevel=0.0)
            for sx in (-1, 1) for sy in (-1, 1)]
    C.part(feet, "Feet", C.RUBBER, smooth_angle=30)


SOCKETS = {"Speaker": (((GRILLE[0] + GRILLE[1]) / 2, FY - 0.06, (GRILLE[2] + GRILLE[3]) / 2), 0.0)}
META = {"speaker": "socket Speaker = grille centre, facing front"}

if __name__ == "__main__":
    C.run(build, "Shop_Radio", sockets=SOCKETS, budget=700, meta=META)
