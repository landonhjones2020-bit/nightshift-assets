"""Lobby_PicnicTable — wooden picnic table with attached benches and a striped umbrella (6 x 8 x 6).

A plank table (four warm-wood planks, top at 2.8) with an attached plank bench on each long side
(seat at 1.6), carried by two darker-wood A-frames (cleats, splayed legs, chrome bolt heads).
A chrome umbrella pole stands in a navy base under the table and rises through the slot between
the middle planks to a domed red-orange / cream striped umbrella (eight panels, scalloped
valance, chrome ribs and stretchers underneath, mustard finial). Table, benches and A-frames
collide; the umbrella does not.

Front = -Y, pivot = bottom-centre. Sockets Seat1..Seat4 = seat surface centres: Seat1/Seat2 on
the front (-Y) bench facing the table (yaw 180), Seat3/Seat4 on the back bench (yaw 0).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

TOP_Z = 2.8
SEAT_Z = 1.6
LEN = 4.8                       # table / bench length (x)
PLANK_T = 0.16
TOP_PLANKS = [(-1.23, -0.71), (-0.65, -0.13), (0.13, 0.65), (0.71, 1.23)]       # y ranges (centre slot for the pole)
BENCH_Y = 2.0
BENCH_PLANKS = [(-0.445, -0.025), (0.025, 0.445)]                               # relative to BENCH_Y
FRAME_X = 1.75
UMB_R = 3.0
RIM_Z = 6.42
APEX_Z = 7.5
PLANK_WOOD = "#C08A57"
POLE_R = 0.085


def canopy():
    """Domed 8-panel umbrella: {colour: [objs]} with top + under faces and scalloped valance tabs."""
    rings = [(0.14, APEX_Z), (1.05, APEX_Z - 0.2), (2.05, APEX_Z - 0.55), (UMB_R, RIM_Z)]
    out = {C.BRAND: [], C.PAPER: []}
    n = 8
    for i in range(n):
        col = C.BRAND if i % 2 == 0 else C.PAPER
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        am = (a0 + a1) / 2
        cols3 = []
        for a, sag in ((a0, 0.0), (am, 1.0), (a1, 0.0)):
            col_pts = []
            for k, (r, z) in enumerate(rings):
                f = k / (len(rings) - 1)
                rr = r * (1 - 0.045 * sag * f)            # fabric pulls in between the ribs
                zz = z - 0.06 * sag * f
                col_pts.append(Vector((rr * math.cos(a), rr * math.sin(a), zz)))
            cols3.append(col_pts)
        for s in range(2):
            A, B = cols3[s], cols3[s + 1]
            for k in range(len(rings) - 1):
                quad = [A[k], A[k + 1], B[k + 1], B[k]]
                out[col].append(C.flat_poly_3d(quad, up=True))
                out[col].append(C.flat_poly_3d(list(reversed(quad)), up=False))
        # scalloped valance tab hanging from the rim edge
        rim = [cols3[0][-1], cols3[1][-1], cols3[2][-1]]
        tab = [rim[0]]
        for k in range(1, 6):
            t = k / 6
            q = rim[0].lerp(rim[1], t * 2) if t <= 0.5 else rim[1].lerp(rim[2], (t - 0.5) * 2)
            tab.append(q - Vector((0, 0, 0.36 * math.sin(math.pi * t) + 0.04)))
        tab.append(rim[2])
        outline = tab + [rim[1]]
        out_dir = Vector((math.cos(am), math.sin(am), 0))
        out[col].append(C.flat_poly_3d(outline, up=None, facing_out=out_dir))
        out[col].append(C.flat_poly_3d(list(reversed(outline)), up=None, facing_out=-out_dir))
    return out


def build():
    planks = []
    for y0, y1 in TOP_PLANKS:
        planks.append(ns.box((LEN, y1 - y0, PLANK_T), loc=(0, (y0 + y1) / 2, TOP_Z - PLANK_T / 2), bevel=0.05, segments=1))
    for sy in (-1, 1):
        for y0, y1 in BENCH_PLANKS:
            planks.append(ns.box((LEN - 0.2, y1 - y0, PLANK_T), loc=(0, sy * BENCH_Y + (y0 + y1) / 2, SEAT_Z - PLANK_T / 2),
                                 bevel=0.05, segments=1))
    frame, bolts = [], []
    for sx in (-1, 1):
        x = sx * FRAME_X
        frame.append(ns.box((0.24, 2.3, 0.2), loc=(x, 0, TOP_Z - PLANK_T - 0.1), bevel=0.04, segments=1))
        frame.append(ns.box((0.24, 2 * BENCH_Y + 1.0, 0.2), loc=(x, 0, SEAT_Z - PLANK_T - 0.1), bevel=0.04, segments=1))
        for sy in (-1, 1):
            frame.append(C.W.beam((x, sy * 0.72, TOP_Z - PLANK_T - 0.02), (x, sy * 1.92, 0.1), 0.24, 0.3, bevel=0.04))
            # carriage-bolt heads where the legs cross the cleats (outer face)
            for yb, zb in ((sy * 0.85, TOP_Z - PLANK_T - 0.1), (sy * 1.37, SEAT_Z - PLANK_T - 0.1)):
                b = ns.cyl(0.07, 0.05, verts=6, bevel=0.0)
                C.place(b, (x + sx * 0.14, yb, zb), yaw=90 * sx, pitch=90)
                bolts.append(b)
        # foot pads under the legs
        for sy in (-1, 1):
            frame.append(ns.box((0.3, 0.42, 0.06), loc=(x, sy * 1.92, 0.03), bevel=0.02, segments=1))

    # umbrella: base, pole through the slot, hub, runner, ribs, stretchers, canopy, finial
    base = ns.lathe([(0.0, 0.0), (0.55, 0.0), (0.55, 0.08), (0.42, 0.16), (0.14, 0.2), (0.0, 0.2)], verts=12)
    pole = C.rod((0, 0, 0.15), (0, 0, APEX_Z + 0.08), POLE_R, verts=8)
    collar = ns.cyl(0.13, 0.12, loc=(0, 0, TOP_Z + 0.07), verts=8, bevel=0.0)
    hub = ns.cyl(0.16, 0.2, loc=(0, 0, APEX_Z - 0.12), verts=8, bevel=0.0)
    runner = ns.cyl(0.13, 0.26, loc=(0, 0, 5.55), verts=8, bevel=0.0)
    ribs = []
    under = [(0.14, APEX_Z - 0.06), (1.05, APEX_Z - 0.27), (2.05, APEX_Z - 0.62), (UMB_R - 0.05, RIM_Z - 0.06)]
    for i in range(8):
        a = 2 * math.pi * i / 8
        pts = [(r * math.cos(a), r * math.sin(a), z) for r, z in under]
        ribs.append(C.pipe(pts, 0.035, sides=4))
        mid = Vector((1.55 * math.cos(a), 1.55 * math.sin(a), APEX_Z - 0.48))
        ribs.append(C.rod((0.1 * math.cos(a), 0.1 * math.sin(a), 5.6), mid, 0.03, verts=4))
    fin = [ns.sphere(0.17, loc=(0, 0, APEX_Z + 0.25), segs=8, rings=5),
           ns.cyl(0.2, 0.08, loc=(0, 0, APEX_Z + 0.04), verts=8, bevel=0.0)]
    panels = canopy()

    C.part(planks, "Planks", PLANK_WOOD, "Wood", can_collide=True, smooth_angle=40)
    C.part(frame, "Frame", C.WOOD, "Wood", can_collide=True, smooth_angle=40)
    C.part(bolts + [pole, collar, hub, runner] + ribs, "Chrome", C.CHROME, "Metal", smooth_angle=50)
    C.part([base], "UmbrellaBase", C.STEEL_NAVY, "Metal", smooth_angle=45)
    C.part(panels[C.BRAND], "CanopyRed", C.BRAND, "Fabric", smooth_angle=None)
    C.part(panels[C.PAPER], "CanopyCream", C.PAPER, "Fabric", smooth_angle=None)
    C.part(fin, "Finial", C.MUSTARD, smooth_angle=60)
    return {}


SOCKETS = {"Seat1": ((-1.1, -BENCH_Y, SEAT_Z), 180.0), "Seat2": ((1.1, -BENCH_Y, SEAT_Z), 180.0),
           "Seat3": ((-1.1, BENCH_Y, SEAT_Z), 0.0), "Seat4": ((1.1, BENCH_Y, SEAT_Z), 0.0)}
META = {"table_height": TOP_Z, "seat_height": SEAT_Z, "seats": 4,
        "seat_order": "1-2 front (-Y) bench facing the table, 3-4 back bench facing the table"}

if __name__ == "__main__":
    C.run(build, "Lobby_PicnicTable", sockets=SOCKETS, meta=META, budget=2000, pivot=(0.0, 0.0, 0.0))
