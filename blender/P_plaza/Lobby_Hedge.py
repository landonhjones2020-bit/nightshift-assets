"""Lobby_Hedge — boxy trimmed hedge with a little flower trim (8 x 3 x 2).

A clipped box hedge on a low dark mulch strip: rounded top edges, a slight batter (narrower at
the top), a lumpy faceted leaf surface in three greens (sunlit top, mid sides, shaded foot), and
a trim of small five-petal flowers (pink, white, mustard) along the foot of both long sides and
round the ends, with a few more dotted along the top edge. The hedge collides.

Front = -Y (reads the same from both long sides), pivot = bottom-centre.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

L, D, H = 7.7, 1.62, 2.86        # hedge body (x, y, z) before the batter
BATTER = 0.14                    # top is 14 % narrower in y
MULCH = (8.0, 2.0, 0.08)
FLOWER_COLS = (C.PETAL_PINK, C.PETAL_WHITE, C.MUSTARD)


def build():
    body = C.grid_box((L, D, H), (20, 5, 7), loc=(0, 0, H / 2), bottom=False)
    C.round_box(body, (0, 0, H / 2), (L / 2, D / 2, H / 2), 0.5, r_bottom=0.03)
    for v in body.data.vertices:                      # batter: narrower toward the top
        v.co.y *= 1.0 - BATTER * max(0.0, v.co.z) / H
    body.data.update()
    C.noise_displace(body, amp=0.13, freq=2.6, seed=5, jitter=0.0, keep=lambda co: co.z < 0.02)
    rnd = random.Random(3)
    for v in body.data.vertices:                      # leafy lumps, stronger toward the top
        if v.co.z > 0.02:
            v.co += v.normal * rnd.uniform(-0.035, 0.055) * (0.6 + 0.8 * v.co.z / H)
        v.co.z = max(0.0, v.co.z)
    body.data.update()
    dapple = C.noise_field(freq=3.1, seed=9)

    def tone(c, n, i):
        if n.z > 0.62:
            return "T2" if dapple(c) > 0.3 else "T"
        if c.z < 0.5:
            return "B"
        d = dapple(c)
        return "S2" if d > 0.28 else ("S3" if d < -0.32 else "S")
    tones = C.split_faces(body, tone, name="Hedge")
    looks = {"T": ("LeavesTop", C.LEAF_LIGHT), "T2": ("LeavesTopBright", "#82B955"), "S": ("LeavesSide", C.FOLIAGE),
             "S2": ("LeavesSideLight", "#5C9A45"), "S3": ("LeavesSideDark", "#447A37"), "B": ("LeavesFoot", C.FOLIAGE_DARK)}
    for key, obj in tones.items():
        nm, col = looks[key]
        C.part([obj], nm, col, "Plastic", can_collide=True, smooth_angle=None)

    mulch = C.prism(C.rrect(MULCH[0], MULCH[1], 0.3, 2), "z", 0.0, MULCH[2])
    C.part([mulch], "Mulch", C.SOIL, "Pebble", smooth_angle=None)

    # flower trim: foot of both long sides + the ends, a few along the top edges
    rnd = random.Random(11)
    heads = {c: [] for c in FLOWER_COLS}
    centres = []
    k = 0
    for sy in (-1, 1):
        n = 12
        for i in range(n):
            x = -L / 2 + 0.5 + (L - 1.0) * i / (n - 1) + rnd.uniform(-0.12, 0.12)
            z = rnd.uniform(0.32, 0.62)
            y = sy * (D / 2 * (1 - BATTER * z / H) + 0.06)
            p, c = C.blossom((x, y, z), (0, sy, 0), rnd.uniform(0.19, 0.24), spin=rnd.uniform(0, 1.3))
            heads[FLOWER_COLS[k % 3]].append(p)
            centres.append(c)
            k += 1
    for sx in (-1, 1):
        for i, (y, z) in enumerate(((-0.42, 0.45), (0.05, 0.62), (0.45, 0.4))):
            p, c = C.blossom((sx * (L / 2 + 0.06), y, z), (sx, 0, 0), rnd.uniform(0.17, 0.21), spin=rnd.uniform(0, 1.3))
            heads[FLOWER_COLS[k % 3]].append(p)
            centres.append(c)
            k += 1
    for sy in (-1, 1):
        for i in range(5):
            x = -L / 2 + 1.0 + (L - 2.0) * i / 4 + rnd.uniform(-0.25, 0.25)
            z = H - 0.18
            y = sy * (D / 2 * (1 - BATTER) - 0.02)
            p, c = C.blossom((x, y, z), (0, sy * 0.6, 0.8), rnd.uniform(0.16, 0.2), up_tilt=0.0, spin=rnd.uniform(0, 1.3))
            heads[FLOWER_COLS[(k + 1) % 3]].append(p)
            centres.append(c)
            k += 1
    C.part(heads[C.PETAL_PINK], "FlowersPink", C.PETAL_PINK, smooth_angle=None)
    C.part(heads[C.PETAL_WHITE], "FlowersWhite", C.PETAL_WHITE, smooth_angle=None)
    C.part(heads[C.MUSTARD], "FlowersGold", C.MUSTARD, smooth_angle=None)
    C.part(centres, "FlowerEyes", C.BRAND_DARK, smooth_angle=None)
    return {}


META = {"hedge": "clipped box hedge on a mulch strip, flower trim on both long sides"}

if __name__ == "__main__":
    C.run(build, "Lobby_Hedge", meta=META, budget=2000, pivot=(0.0, 0.0, 0.0))
