"""Lobby_PottedPalm — tall kentia-style palm in a gold urn (3 W x 7 H x 3 D).

A gold urn planter (foot ring, swelling body with a black-lacquer band, rolled rim) holds dark
soil and a slightly leaning ringed palm trunk (stacked flared segments). From its crown ten
pinnate fronds rise and arch over, plus two young upright spears, two greens alternating: each is a
rachis tube with saw-tooth leaflets on both sides, double-sided because Roblox draws one side
only. The fronds stay inside the 3 x 3 footprint.

Pivot = bottom-centre (floor prop). Only the pot collides (Pot part, can_collide).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
POT_H = 1.55
SOIL_Z = POT_H - 0.1
LEAF_A = "#4E9A3E"
LEAF_B = "#3E7D34"
RACHIS = "#6E8F3A"
BARK = "#7A5A3A"
BARK_DARK = "#5A3926"
SOIL = "#3F2F25"
CROWN = Vector((0.04, 0.02, 3.7))
# fronds: (yaw, start elevation, end elevation, length) - the rachis bends over as it grows, tips stay
# within ~1.45 of the axis; the last two are young upright spears
FRONDS = [(0, 85, 36, 2.8), (36, 82, 30, 2.6), (72, 86, 38, 2.85), (108, 81, 28, 2.55), (144, 85, 34, 2.75),
          (180, 82, 30, 2.65), (216, 86, 37, 2.85), (252, 80, 27, 2.5), (288, 84, 33, 2.7), (324, 82, 30, 2.6),
          (20, 89, 70, 3.32), (200, 89, 68, 3.2)]


def frond(base, yaw, e0, e1, L, n=12):
    """Rachis points + a double-sided saw-tooth leaflet sheet for one arching frond (the elevation
    angle falls linearly from e0 at the base to e1 at the tip)."""
    a = math.radians(yaw)
    hdir = Vector((math.cos(a), math.sin(a), 0.0))
    side = Vector((-math.sin(a), math.cos(a), 0.0))
    pts = [base.copy()]
    ds = L / n
    for i in range(n):
        th = math.radians(e0 + (e1 - e0) * (i + 0.5) / n)
        pts.append(pts[-1] + hdir * (ds * math.cos(th)) + Vector((0, 0, ds * math.sin(th))))
    bm = C.bmesh.new()
    for i in range(3, n + 1):                 # bare stem at the base (the crown centre stays uncluttered)
        t = (i - 0.5) / n
        w = 0.36 * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.6 + 0.03
        p0, p1 = pts[i - 1], pts[i]
        fwd = (p1 - p0).normalized()
        for sgn in (-1, 1):
            # leaflets droop (V-section) and sweep toward the tip
            d = (side * sgn * math.cos(math.radians(30)) + Vector((0, 0, -math.sin(math.radians(30))))).normalized()
            tip = (p0 + p1) / 2 + d * w + fwd * 0.1
            tri = [p0 + d * 0.03, tip, p1 + d * 0.03]          # leaflet starts at the rachis tube surface
            nrm = (tri[1] - tri[0]).cross(tri[2] - tri[0]).normalized()
            if nrm.z < 0:
                tri = tri[::-1]
                nrm = -nrm
            bm.faces.new([bm.verts.new(v) for v in tri])
            bm.faces.new([bm.verts.new(v - nrm * 0.01) for v in reversed(tri)])
    return pts, ns.from_bmesh(bm, "Frond")


def build():
    rnd = random.Random(4)
    pot = ns.lathe([(0.0, 0.0), (0.66, 0.0), (0.66, 0.1), (0.56, 0.18), (0.62, 0.32), (0.86, 0.7), (0.95, 1.05), (0.92, 1.3),
                    (0.98, 1.38), (1.02, 1.48), (0.98, POT_H), (0.88, POT_H), (0.86, SOIL_Z - 0.02), (0.0, SOIL_Z - 0.02)],
                   verts=16)
    C.part([pot], "Pot", C.GOLD, "Metal", can_collide=True, smooth_angle=45)
    band = C.lathe_ring([(0.88, 0.62), (0.955, 0.8), (0.975, 1.0), (0.955, 1.12), (0.9, 1.0), (0.85, 0.78)], verts=16)
    C.part([band], "PotBand", C.LACQUER, smooth_angle=45)
    soil = C.disc(0.87, loc=(0, 0, SOIL_Z - 0.01), verts=16)
    C.part([soil], "Soil", SOIL, "Fabric", smooth_angle=None)

    # ringed trunk: stacked flared segments (one bark colour; the flared lips cast the rings)
    trunk = []
    n_seg = 7
    z0 = SOIL_Z - 0.06
    for k in range(n_seg):
        t0, t1 = k / n_seg, (k + 1) / n_seg
        za, zb = z0 + (CROWN.z - z0) * t0, z0 + (CROWN.z - z0) * t1
        ca = Vector((CROWN.x * t0 ** 1.5, CROWN.y * t0 ** 1.5, za))
        cb = Vector((CROWN.x * t1 ** 1.5, CROWN.y * t1 ** 1.5, zb))
        ra, rb = 0.3 - 0.11 * t0, 0.3 - 0.11 * t1
        trunk.append(C.rod(ca, cb, ra * 0.84, verts=8, r_top=rb * 1.14))
    C.part(trunk, "Trunk", BARK, "Wood", smooth_angle=40)
    # fibrous dark collar where the fronds leave the trunk
    C.part([ns.cyl(0.25, 0.42, loc=tuple(CROWN + Vector((0, 0, 0.04))), verts=8, radius_top=0.13, bevel=0.0)], "Crown",
           BARK_DARK, "Wood", smooth_angle=40)

    leaves = {LEAF_A: [], LEAF_B: []}
    rachis = []
    for i, (yaw, e0, e1, L) in enumerate(FRONDS):
        base = CROWN + Vector((math.cos(math.radians(yaw)) * 0.11, math.sin(math.radians(yaw)) * 0.11, rnd.uniform(0.0, 0.12)))
        pts, sheet = frond(base, yaw + rnd.uniform(-5, 5), e0, e1, L)
        leaves[LEAF_A if i % 2 == 0 else LEAF_B].append(sheet)
        rachis.append(C.pipe([tuple(p) for p in pts[1::2]], 0.035, sides=3))
    C.part(leaves[LEAF_A], "FrondsLight", LEAF_A, smooth_angle=35)
    C.part(leaves[LEAF_B], "FrondsDark", LEAF_B, smooth_angle=35)
    C.part(rachis, "Rachis", RACHIS, smooth_angle=60)


META = {"collider": "Pot (only the pot collides)", "mount": "floor"}

if __name__ == "__main__":
    C.run(build, "Lobby_PottedPalm", budget=2000, meta=META, backdrop="#3A2440")
