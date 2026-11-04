"""Lobby_VIPArmchair — wingback red-velvet armchair matching Lobby_VIPSofa (3 W x 4 H x 3 D).

A red velvet base with a plump seat cushion, rolled scroll arms traced in gold piping, a tall
camel-topped backrest leaning back, diamond-tufted with gold buttons, and curved wings at its
sides. Gold piping follows the back's top and the wings' front edges; four gold tapered legs.

Front = -Y, pivot = bottom-centre. Collides (base, cushion, arms, back, wings). Socket Seat =
seat-top centre, facing front (yaw 0).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns
W, H, D = 3.0, 4.0, 3.0
SEAT = 1.45
BASE_Z = (0.32, 0.95)
ARM_W = 0.46
AX0 = W / 2 - ARM_W - 0.1           # arm inner face x (abs)
FRONT = -D / 2 + 0.04
BACK_Y = (0.56, 1.08)                # back panel front .. back (before the tilt)
TILT = 8.0                           # backrest lean (degrees)
VEL = C.VELVET


def tilt(objs, pivot=(0, BACK_Y[0], BASE_Z[1])):
    """Lean objects back by TILT degrees about the X axis through `pivot`."""
    R = Matrix.Rotation(math.radians(-TILT), 3, "X")
    pv = Vector(pivot)
    for o in objs:
        ns.apply_all(o)
        for v in o.data.vertices:
            v.co = pv + R @ (v.co - pv)
    return objs


def back_outline(inset=0.0):
    """Camel-topped back silhouette (x, z) between the wings."""
    hw = W / 2 - 0.3 - inset
    pts = [(-hw, BASE_Z[1] - 0.05), (hw, BASE_Z[1] - 0.05), (hw, 3.66 - inset)]
    for k in range(1, 8):
        t = k / 8
        x = hw - 2 * hw * t
        pts.append((x, 3.66 - inset + 0.38 * math.sin(math.pi * t) ** 1.5))
    pts.append((-hw, 3.66 - inset))
    return pts


def build():
    velvet, gold = [], []
    by0, by1 = FRONT + 0.12, BACK_Y[1] - 0.04
    velvet.append(ns.box((W - 0.5, by1 - by0, BASE_Z[1] - BASE_Z[0]), loc=(0, (by0 + by1) / 2, sum(BASE_Z) / 2), bevel=0.06,
                         segments=1))
    cush = ns.box((2 * AX0 - 0.04, BACK_Y[0] - FRONT + 0.1, SEAT - BASE_Z[1] + 0.03), loc=(0, (FRONT + BACK_Y[0] + 0.1) / 2,
                                                                                         (BASE_Z[1] - 0.03 + SEAT) / 2),
                  bevel=0.14, segments=1)
    velvet.append(cush)
    # rolled scroll arms (front profile extruded front -> back)
    prof = C.fillet([(0.0, BASE_Z[0] - 0.02), (ARM_W, BASE_Z[0] - 0.02), (ARM_W, 1.9), (ARM_W + 0.08, 2.06), (ARM_W + 0.04, 2.2),
                     (ARM_W - 0.12, 2.29), (0.18, 2.27), (0.02, 2.14), (0.0, 1.98)],
                    [0.04, 0.04, 0.06, 0.08, 0.1, 0.1, 0.08, 0.06, 0.04], 2)
    for sx in (-1, 1):
        pts = [(sx * (AX0 + x), z) for x, z in prof]
        armb = C.prism(pts, "y", FRONT, BACK_Y[1] - 0.1)
        ns.bevel(armb, width=0.05, segments=1)
        velvet.append(armb)
        trim = C.fillet([(0.04, 0.5), (ARM_W - 0.02, 0.5), (ARM_W - 0.02, 1.9), (ARM_W + 0.05, 2.05), (ARM_W + 0.02, 2.17),
                         (ARM_W - 0.13, 2.24), (0.18, 2.22), (0.06, 2.12), (0.04, 1.98)], 0.06, 1)
        gold.append(C.pipe([(sx * (AX0 + x), FRONT - 0.025, z) for x, z in trim], 0.04, sides=4, closed=True))
    # backrest (leaning) + its gold top piping
    back = C.prism(back_outline(), "y", BACK_Y[0], BACK_Y[1])
    ns.bevel(back, width=0.1, segments=1)
    top = [(x, BACK_Y[0] - 0.02, z) for x, z in back_outline(0.06)[2:-1]]
    pipe = C.pipe(top, 0.05, sides=4)
    tilt([back, pipe])
    velvet.append(back)
    gold.append(pipe)
    # wings: curved side panels from the back forward over the arms
    wing = [(BACK_Y[1] - 0.05, 2.0), (-0.05, 2.0), (-0.22, 2.25), (-0.2, 2.75), (-0.02, 3.25), (0.28, 3.6), (0.62, 3.8),
            (BACK_Y[1] - 0.05, 3.84)]
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (W / 2 - 0.32), sx * (W / 2 - 0.06)))
        wg = C.prism(C.fillet(wing, [0.0, 0.08, 0.15, 0.2, 0.2, 0.15, 0.1, 0.0], 2), "x", x0, x1)
        ns.bevel(wg, width=0.05, segments=1)
        xe = sx * (W / 2 - 0.06 + 0.02)
        edge = C.pipe(C.round_path([(xe, y - 0.02, z) for y, z in wing[1:-1]], 0.18, 2), 0.04, sides=4)
        tilt([wg, edge])
        velvet.append(wg)
        gold.append(edge)
    C.part(velvet, "Velvet", VEL, "Fabric", can_collide=True, smooth_angle=50)

    # tufting buttons on the back face (3 staggered rows), leaning with the back
    pts = []
    for row, z in enumerate((1.95, 2.45, 2.95)):
        xs = (-0.55, 0.0, 0.55) if row % 2 == 0 else (-0.28, 0.28)
        for x in xs:
            pts.append((x, BACK_Y[0] - 0.005, z))
    btn = C.domes(pts, 0.08, axis=(0, -1, 0), segs=6, rings=2)
    tilt([btn])
    gold.append(btn)
    # gold piping along the base front and gold tapered legs
    gold.append(C.pipe([(-AX0, FRONT + 0.11, BASE_Z[0] + 0.05), (AX0, FRONT + 0.11, BASE_Z[0] + 0.05)], 0.045, sides=4))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ly = (FRONT + 0.42) if sy < 0 else (BACK_Y[1] - 0.3)
            gold.append(ns.cyl(0.11, 0.34, loc=(sx * (W / 2 - 0.42), ly, 0.17), verts=8, radius_top=0.15, bevel=0.0))
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=50)


SOCKETS = {"Seat": ((0, (FRONT + BACK_Y[0]) / 2, SEAT), 0.0)}
META = {"seat_height": SEAT, "matches": "Lobby_VIPSofa"}

if __name__ == "__main__":
    C.run(build, "Lobby_VIPArmchair", sockets=SOCKETS, budget=2000, meta=META, backdrop="#3A2440")
