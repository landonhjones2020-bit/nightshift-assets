"""Shop_Couch — worn three-seat Break Room couch in olive vinyl.

Dark olive frame with rolled arms and a back, three slightly sagging seat cushions and
three back cushions (each a little askew), short tapered wooden legs. Wear: the middle
seat cushion is patched with a duct-tape X, a back cushion carries a stitched brown vinyl
patch, a small split on the right seat cushion, and a mustard knit throw pillow is jammed
in the left corner. Collides (frame and cushions).
Sockets Seat1..Seat3 = seat-top centres left to right (yaw 0 = sitter faces front, -Y).
Front faces -Y, pivot = bottom-centre. ~6.5 x 3.0 x 2.8.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402

ns = C.ns
W, D, H = 6.5, 2.8, 3.0
LEG = 0.3
BASE_TOP = 0.95
SEAT_TOP = 1.5
ARM_W = 0.62
OLIVE_DARK = "#5A5530"
OLIVE = "#6E6A3A"
SEAT_X = (-1.75, 0.0, 1.75)


def build():
    rnd = random.Random(11)
    frame = [ns.box((W - 2 * ARM_W + 0.1, D - 0.1, BASE_TOP - LEG), loc=(0, 0.02, (LEG + BASE_TOP) / 2), bevel=0.0),
             ns.box((W - 2 * ARM_W + 0.1, 0.55, H - 0.25 - LEG), loc=(0, D / 2 - 0.3, LEG + (H - 0.25 - LEG) / 2), bevel=0.12,
                    segments=1)]
    prof = C.fillet([(-D / 2, LEG), (D / 2, LEG), (D / 2, 2.15), (-D / 2, 2.15)], [0.05, 0.05, 0.3, 0.32], 2)
    for x0, x1 in ((-W / 2, -W / 2 + ARM_W), (W / 2 - ARM_W, W / 2)):     # rolled arms
        arm = C.prism(prof, "x", x0, x1)
        ns.bevel(arm, width=0.1, segments=1, angle=50)
        frame.append(arm)
    C.part(frame, "Frame", OLIVE_DARK, can_collide=True, smooth_angle=40)

    cushions, back_rot = [], {}
    for i, x in enumerate(SEAT_X):
        sag = (0.0, -0.05, -0.02)[i]
        c = ns.box((1.72, D - 0.55, SEAT_TOP - BASE_TOP + sag), loc=(x + rnd.uniform(-0.03, 0.03), -0.22, (BASE_TOP + SEAT_TOP + sag) / 2),
                   rot=(rnd.uniform(-2, 1), rnd.uniform(-1.5, 1.5), rnd.uniform(-2.5, 2.5)), bevel=0.17, segments=2)
        cushions.append(c)
        ctr = Vector((x + rnd.uniform(-0.04, 0.04), D / 2 - 0.78, SEAT_TOP + 0.62))
        rot = (-11 + rnd.uniform(-2, 2), rnd.uniform(-2.5, 2.5), rnd.uniform(-2, 2))
        cushions.append(ns.box((1.72, 0.55, 1.32), loc=ctr, rot=rot, bevel=0.2, segments=2))
        back_rot[i] = (ctr, rot)
    C.part(cushions, "Cushions", OLIVE, can_collide=True, smooth_angle=50)

    legs = [ns.cyl(0.09, LEG + 0.02, loc=(sx * (W / 2 - 0.35), sy * (D / 2 - 0.3), (LEG + 0.02) / 2), verts=4, radius_top=0.12,
                   bevel=0.0) for sx in (-1, 1) for sy in (-1, 1)]
    C.part(legs, "Legs", C.WOOD_DARK, "Wood", smooth_angle=40)

    # duct-tape X on the middle seat cushion (top face ~ SEAT_TOP - 0.05)
    tz = SEAT_TOP - 0.05 + 0.012
    tape = [ns.box((0.95, 0.2, 0.02), loc=(0.05, -0.32, tz), rot=(0, 0, a), bevel=0.0) for a in (32, -38)]
    C.part(tape, "DuctTape", "#A6ABB0", smooth_angle=None)
    # stitched brown patch on the right back cushion's front face (moved with that cushion)
    ctr, rot = back_rot[2]
    R = Euler(tuple(math.radians(a) for a in rot), "XYZ").to_matrix()
    off = Vector((0.28, -0.275 - 0.012, 0.16))
    patch = ns.box((0.5, 0.03, 0.42), loc=ctr + R @ off, rot=rot, bevel=0.0)
    stitches = []
    for k in range(3):
        for sz in (-1, 1):
            o2 = Vector((0.28 - 0.16 + 0.16 * k, -0.275 - 0.03, 0.16 + sz * 0.21))
            stitches.append(ns.box((0.05, 0.012, 0.11), loc=ctr + R @ o2, rot=rot, bevel=0.0))
    C.part([patch], "Patch", "#7A5232", smooth_angle=None)
    C.part(stitches, "Stitches", "#D8CBAA", smooth_angle=None)
    # split in the right seat cushion (dark slit with stuffing showing)
    slit = ns.box((0.42, 0.06, 0.02), loc=(SEAT_X[2] - 0.2, -0.75, SEAT_TOP - 0.02 + 0.008), rot=(0, 0, 18), bevel=0.0)
    C.part([slit], "Split", "#2A2616", smooth_angle=None)
    fluff = ns.sphere(0.07, loc=(SEAT_X[2] - 0.2, -0.75, SEAT_TOP + 0.0), scale=(2.2, 0.8, 0.6), segs=6, rings=4)
    C.part([fluff], "Stuffing", "#EDE4CF", smooth_angle=60)

    # mustard throw pillow jammed into the left corner, leaning on the arm and back
    pil = ns.box((0.86, 0.3, 0.86), loc=(0, 0, 0), bevel=0.14, segments=1)
    ns.apply_all(pil)
    for v in pil.data.vertices:      # puff the middle, pinch the corners
        r = min(1.0, (abs(v.co.x) + abs(v.co.z)) / 0.86)
        v.co.y *= 1.0 + 0.5 * (1.0 - r)
    ns.jitter(pil, amount=0.015, seed=4)
    C.place([pil], loc=(-W / 2 + ARM_W + 0.5, 0.05, SEAT_TOP + 0.44), yaw=24, pitch=-20)
    C.part([pil], "Pillow", "#D99A34", "Fabric", smooth_angle=55)


SOCKETS = {f"Seat{i + 1}": ((x, -0.3, SEAT_TOP), 0.0) for i, x in enumerate(SEAT_X)}
META = {"seat_height": SEAT_TOP, "front": "-Y (sit facing LookVector)"}

if __name__ == "__main__":
    C.run(build, "Shop_Couch", sockets=SOCKETS, budget=1200, meta=META)
