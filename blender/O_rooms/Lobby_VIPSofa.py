"""Lobby_VIPSofa — gently curved tufted red-velvet VIP sofa (9 W x 3 H x 3.5 D).

The sofa follows a shallow arc (centre of curvature in front of it, ends ~1 stud forward of the
middle) so it wraps the people sitting on it. A red velvet base and three plump seat cushions,
a deep backrest leaning back with a rolled top, diamond-tufted with gold buttons, and rolled
scroll arms at both ends traced in gold piping. Gold piping also runs along the top roll and the
base, and the sofa stands on six gold tapered feet. A hot-pink and a gold satin throw pillow lean
in the outer seats.

Front (open, concave side) = -Y, pivot = bottom-centre. Collides (base, cushions, back, arms).
Sockets Seat1..Seat3 = seat-top points left to right as seen from the front, each facing the
centre of curvature (yaw).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
R4 = 11.0                     # back outer radius
R3 = 9.95                     # backrest front face (at the seat)
R1 = 8.5                      # seat front
TH = 20.8                     # half-angle of the seat / back (degrees)
CY = -(R4 - 1.72)             # centre of curvature (0, CY): the back middle lands at y = +1.72
SEAT = 1.45                   # cushion top
BASE_Z = (0.28, 0.95)
SEG = 20
ARM_W = 0.55
VEL = C.VELVET


def P(r, a, z=0.0):
    a = math.radians(a)
    return Vector((r * math.cos(a), CY + r * math.sin(a), z))


def arc(r, z, a0, a1, n=SEG):
    return [tuple(P(r, a0 + (a1 - a0) * i / n, z)) for i in range(n + 1)]


def back_r(z):
    """Radius of the leaning backrest front face at height z."""
    return R3 + (z - SEAT) / (2.66 - SEAT) * 0.3


def arm(side):
    """Rolled scroll arm at one end. side +1 = right (Blender +X), -1 = left. Returns (arm, trim)."""
    a = 90.0 - side * TH
    u = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0))
    t = Vector((math.sin(math.radians(a)), -math.cos(math.radians(a)), 0.0)) * side    # outward tangent
    prof = C.fillet([(0.0, BASE_Z[0]), (ARM_W, BASE_Z[0]), (ARM_W, 1.9), (ARM_W + 0.1, 2.08), (ARM_W + 0.06, 2.24),
                     (ARM_W - 0.12, 2.34), (0.2, 2.32), (0.02, 2.18), (0.0, 2.0)],
                    [0.04, 0.04, 0.06, 0.08, 0.1, 0.1, 0.08, 0.06, 0.04], 2)
    y0, y1 = R1 - 0.12, R4 - 0.02
    body = C.prism(prof, "y", y0, y1)
    ns.bevel(body, width=0.06, segments=1)
    trim = C.pipe([(x, y0 - 0.025, z) for x, z in C.fillet([(0.04, 0.5), (ARM_W - 0.02, 0.5), (ARM_W - 0.02, 1.9),
                                                            (ARM_W + 0.06, 2.07), (ARM_W + 0.03, 2.2), (ARM_W - 0.13, 2.29),
                                                            (0.2, 2.27), (0.06, 2.16), (0.04, 2.0)], 0.06, 1)],
                  0.045, sides=4, closed=True)
    O = Vector((0.0, CY, 0.0))
    for ob in (body, trim):
        ns.apply_all(ob)
        for v in ob.data.vertices:
            x, y, z = v.co
            v.co = O + t * x + u * y + Vector((0, 0, z))
        if side < 0:
            ob.data.flip_normals()     # the tangent frame is mirrored on the left
    return body, trim


def build():
    velvet = []
    base = C.arc_profile_sweep([(R1 + 0.12, BASE_Z[0]), (R4 - 0.05, BASE_Z[0]), (R4 - 0.05, BASE_Z[1]), (R1 + 0.12, BASE_Z[1])],
                               90 - TH, 90 + TH, segs=SEG, cy=CY)
    ns.bevel(base, width=0.05, segments=1)
    back = C.arc_profile_sweep([(R3 - 0.05, BASE_Z[1] - 0.02), (R4, BASE_Z[1] - 0.02), (R4, 2.68), (R4 - 0.1, 2.85),
                                (R4 - 0.35, 2.945), (R3 + 0.6, 2.925), (R3 + 0.42, 2.83), (R3 + 0.3, 2.66), (R3, SEAT)],
                               90 - TH, 90 + TH, segs=SEG, cy=CY)
    velvet += [base, back]
    # three plump seat cushions with small gaps
    span = 2 * TH
    for k in range(3):
        a0 = 90 - TH + span * k / 3 + 0.35
        a1 = 90 - TH + span * (k + 1) / 3 - 0.35
        cu = C.arc_solid(R1, R3 + 0.12, a0, a1, BASE_Z[1] - 0.03, SEAT, segs=6, cy=CY)
        ns.bevel(cu, width=0.13, segments=1, angle=50)
        velvet.append(cu)
    trims = []
    for side in (-1, 1):
        body, trim = arm(side)
        velvet.append(body)
        trims.append(trim)
    C.part(velvet, "Velvet", VEL, "Fabric", can_collide=True, smooth_angle=50)

    # gold: top-roll piping, base piping, arm scroll trims, feet, tufting buttons
    gold = trims
    gold.append(C.pipe(arc(R4 - 0.3, 2.945, 90 - TH + 0.5, 90 + TH - 0.5, n=16), 0.055, sides=4))
    gold.append(C.pipe(arc(R1 + 0.09, BASE_Z[0] + 0.04, 90 - TH + 0.3, 90 + TH - 0.3, n=16), 0.05, sides=4))
    for a in (90 - TH + 1.6, 90.0, 90 + TH - 1.6):
        for r in (R1 + 0.4, R4 - 0.35):
            p = P(r, a)
            gold.append(ns.cyl(0.13, 0.3, loc=(p.x, p.y, 0.15), verts=8, radius_top=0.17, bevel=0.0))
    # diamond tufting: three staggered rows of buttons on the leaning back face
    pts, axes = [], []
    n_cols = 12
    da = (2 * TH - 3.0) / n_cols
    nrm_rz = Vector((-(2.66 - SEAT), 0.3)).normalized()      # back-face normal in (r, z)
    for row, z in enumerate((1.8, 2.16, 2.52)):
        cols = n_cols if row % 2 == 0 else n_cols - 1
        off = 0.5 if row % 2 == 0 else 1.0
        for k in range(cols):
            a = 90 - TH + 1.5 + da * (k + off)
            u = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0))
            pts.append(tuple(P(back_r(z) - 0.01, a, z)))
            axes.append(tuple(u * nrm_rz.x + Vector((0, 0, nrm_rz.y))))
    gold.append(C.domes(pts, 0.075, axis=axes, segs=5, rings=2))
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=50)

    # accent throw pillows leaning on the back in the outer seats (hot pink left, gold satin right)
    for a, col, roll in ((90 + TH - 6.5, C.PINK, 8.0), (90 - TH + 6.5, C.GOLD, -8.0)):
        pil = ns.box((0.95, 0.3, 0.95), loc=(0, 0, 0), bevel=0.14, segments=1)
        ns.apply_all(pil)
        for v in pil.data.vertices:          # puff the middle, pinch the corners
            r = min(1.0, (abs(v.co.x) + abs(v.co.z)) / 0.95)
            v.co.y *= 1.0 + 0.6 * (1.0 - r)
        pos = P(back_r(1.9) - 0.32, a, 1.95)
        yaw = a - 90.0
        C.place([pil], loc=tuple(pos), yaw=yaw, pitch=-14)
        C.part([pil], "PillowPink" if col == C.PINK else "PillowGold", col, "Fabric", smooth_angle=55)


def sockets():
    s = {}
    for k in range(3):
        a = 90 + TH - 2 * TH * (k + 0.5) / 3       # left -> right as seen from the front
        p = P((R1 + R3) / 2, a, SEAT)
        s[f"Seat{k + 1}"] = (tuple(p), round(C.facing_yaw(p, (0.0, CY, 0.0)), 2))
    return s


META = {"seat_height": SEAT, "curve": {"radius_back": R4, "centre_y_blender": CY, "span_deg": 2 * TH},
        "seat_order": "Seat1..Seat3 left to right as seen from the front; each faces the curve centre"}

if __name__ == "__main__":
    C.run(build, "Lobby_VIPSofa", sockets=sockets(), budget=3000, meta=META, backdrop="#3A2440")
