"""Lobby_BarStool — VIP shake-bar stool (1.6 dia x 3 H) for Lobby_ShakeBar (bar top 2.6).

A domed gold base, a gold pole with a gold foot ring on two spokes, a gold seat collar, a plump
round red-velvet seat (top 1.95) with a gold band and a centre button, and a low curved velvet
backrest on two gold posts, gold-piped along its top and tufted with three gold buttons.

Front = -Y (the backrest is at +Y), pivot = bottom-centre. Collides (base, pole, seat, back).
Socket Seat = seat-top centre, facing front (yaw 0).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
SEAT = 1.95
SEAT_R = 0.72
BACK_A = (38.0, 142.0)         # backrest arc (degrees from +X; +Y is the back)
BACK_Z = (SEAT + 0.12, 3.0)
BR = (0.56, 0.72)              # backrest inner / outer radius


def build():
    gold, gold_c = [], []
    gold_c.append(ns.lathe([(0.0, 0.0), (0.8, 0.0), (0.8, 0.05), (0.63, 0.12), (0.18, 0.19), (0.0, 0.2)], verts=16))
    gold_c.append(ns.cyl(0.085, SEAT - 0.5, loc=(0, 0, 0.15 + (SEAT - 0.5) / 2), verts=8, bevel=0.0))
    gold_c.append(ns.cyl(0.42, 0.14, loc=(0, 0, SEAT - 0.37), verts=16, radius_top=0.6, bevel=0.0))   # seat collar
    ring = ns.torus(0.46, 0.04, major_segs=16, minor_segs=4)
    C.place(ring, (0, 0, 0.82))
    gold.append(ring)
    gold.append(C.rod((-0.46, 0, 0.82), (0.46, 0, 0.82), 0.03, verts=4))
    C.part(gold_c, "Pole", C.GOLD, "Metal", can_collide=True, smooth_angle=50)

    # seat: plump velvet cushion, gold band, centre button
    cush = ns.lathe([(0.0, SEAT - 0.3), (SEAT_R - 0.04, SEAT - 0.3), (SEAT_R, SEAT - 0.22), (SEAT_R, SEAT - 0.1),
                     (SEAT_R - 0.08, SEAT - 0.02), (0.4, SEAT + 0.01), (0.0, SEAT - 0.02)], verts=16)
    gold.append(C.lathe_ring([(SEAT_R - 0.02, SEAT - 0.31), (SEAT_R + 0.03, SEAT - 0.3), (SEAT_R + 0.03, SEAT - 0.2),
                              (SEAT_R - 0.02, SEAT - 0.2)], verts=16))
    gold.append(C.domes([(0, 0, SEAT - 0.025)], 0.07, axis=(0, 0, 1), segs=6, rings=2))
    # backrest: curved velvet band on two gold posts, gold piping on top, three buttons
    back = C.arc_solid(BR[0], BR[1], BACK_A[0], BACK_A[1], BACK_Z[0] + 0.12, BACK_Z[1] - 0.06, segs=8)
    ns.bevel(back, width=0.07, segments=1)
    C.part([cush, back], "Velvet", C.VELVET, "Fabric", can_collide=True, smooth_angle=50)
    rm = (BR[0] + BR[1]) / 2
    top = [(rm * math.cos(math.radians(a)), rm * math.sin(math.radians(a)), BACK_Z[1] - 0.04)
           for a in [BACK_A[0] + (BACK_A[1] - BACK_A[0]) * k / 8 for k in range(9)]]
    gold.append(C.pipe(top, 0.045, sides=4))
    for a in (60.0, 120.0):
        p = Vector((rm * math.cos(math.radians(a)), rm * math.sin(math.radians(a)), 0))
        gold.append(C.rod((p.x, p.y, SEAT - 0.08), (p.x, p.y, BACK_Z[0] + 0.2), 0.04, verts=6))
    pts, axes = [], []
    for a, z in ((70.0, 2.5), (90.0, 2.62), (110.0, 2.5)):
        u = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0))
        pts.append(tuple(u * (BR[0] - 0.005) + Vector((0, 0, z))))
        axes.append(tuple(-u))
    gold.append(C.domes(pts, 0.06, axis=axes, segs=6, rings=2))
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=50)


SOCKETS = {"Seat": ((0, 0, SEAT), 0.0)}
META = {"seat_height": SEAT, "bar_top": 2.6, "matches": "Lobby_ShakeBar"}

if __name__ == "__main__":
    C.run(build, "Lobby_BarStool", sockets=SOCKETS, budget=2000, meta=META, backdrop="#3A2440")
