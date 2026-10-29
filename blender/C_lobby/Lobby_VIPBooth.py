"""Lobby_VIPBooth — luxurious curved VIP booth (seats 4) around a round marble table.

A 240-degree C-shaped booth open to the front (-Y): deep plum lacquer shell, purple velvet
seat cushion and ten channel-tufted velvet back rolls, gold piping along the backrest top,
the seat edge and the kick base, gold end caps. In the middle a round cream marble table
with a gold edge band and gold pedestal, and a little gold table lamp with a warm shade
(Shade, Neon, role "lamp").

Front (open side) = -Y, pivot = bottom-centre of the table. Collides (shell, cushion,
table). Sockets Seat1..Seat4 = seat surface points along the arc from left to right as
seen from the front, each facing the table centre; Table = table top centre.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
A0, A1 = -30.0, 210.0          # arc span (deg from +X, CCW); the gap faces -Y
SEAT_Z, TABLE_Z = 1.6, 2.8
R_SEAT_IN, R_SEAT_OUT = 2.45, 3.75
R_BACK_IN, R_BACK_OUT = 3.95, 4.35
BACK_TOP = 4.5
SEG = 16
PLUM = "#3B2244"
MARBLE = "#EDE6DA"
SEAT_ANGLES = (198.0, 132.0, 48.0, -18.0)   # left -> right as seen from the front
SEAT_R = 3.1


def arc_pts(r, z, a0=A0, a1=A1, n=SEG):
    return [(r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), r * math.sin(math.radians(a0 + (a1 - a0) * i / n)), z)
            for i in range(n + 1)]


def build():
    base = C.arc_solid(R_SEAT_IN + 0.05, R_BACK_OUT, A0, A1, 0.0, 1.17, segs=SEG)
    back = C.arc_solid(R_BACK_IN, R_BACK_OUT, A0, A1, 1.1, BACK_TOP, segs=SEG)
    ns.bevel(base, width=0.06, segments=1)
    ns.bevel(back, width=0.08, segments=1)
    C.part([base, back], "Shell", PLUM, can_collide=True, smooth_angle=40)
    cushion = C.arc_solid(R_SEAT_IN, R_SEAT_OUT + 0.25, A0 + 1.5, A1 - 1.5, 1.15, SEAT_Z, segs=SEG)
    ns.bevel(cushion, width=0.14, segments=1)
    rolls = []
    n = 10
    for i in range(n):
        a = A0 + 3 + (A1 - A0 - 6) * (i + 0.5) / n
        x, y = 3.78 * math.cos(math.radians(a)), 3.78 * math.sin(math.radians(a))
        w = 2 * math.pi * 3.78 * (A1 - A0 - 6) / 360 / n - 0.05
        r = ns.box((0.42, w, BACK_TOP - SEAT_Z - 0.35), loc=(0, 0, 0), bevel=0.17, segments=1)
        r.rotation_euler = (0, math.radians(7), math.radians(a))
        r.location = (x, y, SEAT_Z + (BACK_TOP - SEAT_Z - 0.35) / 2 + 0.02)
        rolls.append(r)
    C.part([cushion] + rolls, "Velvet", C.VELVET, "Fabric", can_collide=True, smooth_angle=50)

    gold = [C.pipe(arc_pts((R_BACK_IN + R_BACK_OUT) / 2, BACK_TOP + 0.02), 0.09, sides=6),
            C.pipe(arc_pts(R_SEAT_IN + 0.06, 1.15, A0 + 2, A1 - 2), 0.06, sides=5),
            C.pipe(arc_pts(R_BACK_OUT + 0.01, 2.2, A0 + 1, A1 - 1), 0.06, sides=4)]
    for a, da in ((A0, -0.9), (A1, 0.9)):   # gold piping round each end profile of the shell
        c, sn = math.cos(math.radians(a + da)), math.sin(math.radians(a + da))
        prof = [(R_SEAT_IN + 0.08, 0.08), (R_SEAT_IN + 0.08, 1.17), (R_BACK_IN - 0.02, 1.17), (R_BACK_IN - 0.02, BACK_TOP),
                (R_BACK_OUT - 0.03, BACK_TOP), (R_BACK_OUT - 0.03, 0.08)]
        gold.append(C.pipe([(r * c, r * sn, z) for r, z in prof], 0.07, sides=5, corner=0.12, corner_segs=1))
    # table: marble top, gold band, pedestal, foot + lamp
    top = ns.cyl(1.4, 0.16, loc=(0, 0, TABLE_Z - 0.08), verts=24, bevel=0.04, segments=1)
    C.part([top], "TableTop", MARBLE, "Marble", can_collide=True, smooth_angle=40)
    band = ns.cyl(1.45, 0.1, loc=(0, 0, TABLE_Z - 0.2), verts=24, bevel=0.0)
    post = ns.cyl(0.18, TABLE_Z - 0.4, loc=(0, 0, (TABLE_Z - 0.4) / 2 + 0.12), verts=10, bevel=0.0)
    foot = ns.cyl(0.85, 0.14, loc=(0, 0, 0.07), verts=16, radius_top=0.7, bevel=0.0)
    lamp_base = ns.lathe([(0.0, 0.0), (0.22, 0.0), (0.2, 0.06), (0.06, 0.12), (0.05, 0.62), (0.0, 0.66)], verts=8,
                         loc=(0.35, 0.25, TABLE_Z))
    gold += [band, post, foot, lamp_base]
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=45)
    shade = ns.cyl(0.32, 0.36, loc=(0.35, 0.25, TABLE_Z + 0.76), verts=10, radius_top=0.18, bevel=0.0)
    ns.tag(shade, "Shade", "#FFC56B", "Neon", recolor="lamp", cast_shadow=False, smooth_angle=50)


def sockets():
    s = {}
    for i, a in enumerate(SEAT_ANGLES):
        p = (SEAT_R * math.cos(math.radians(a)), SEAT_R * math.sin(math.radians(a)), SEAT_Z)
        s[f"Seat{i + 1}"] = (p, round(C.facing_yaw(p, (0, 0, 0)), 2))
    s["Table"] = ((0, 0, TABLE_Z), 0.0)
    return s


META = {"seat_height": SEAT_Z, "table_height": TABLE_Z, "open_side": "front (-Y)",
        "seat_order": "Seat1..Seat4 left to right as seen from the front; each faces the table",
        "roles": {"lamp": "Shade"}, "vip_only": True,
        "light_hint": {"type": "PointLight", "at": "Socket_Table", "color": "#FFC56B", "range": 9, "brightness": 1}}

if __name__ == "__main__":
    C.run(build, "Lobby_VIPBooth", sockets=sockets(), pivot=(0, 0, 0), meta=META, socket_views=((0, 60),))
