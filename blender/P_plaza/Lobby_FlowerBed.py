"""Lobby_FlowerBed — long raised brick flower bed (8 x 1.8 x 3).

A rounded-corner brick bed (Brick) with a cast-stone coping and dark soil, planted with bushy
leaf clumps in dappled greens, drifts of chunky tulips (red-orange, pink, mustard) and daisies
(white, violet) - two rows, so it reads from both long sides. The brick bed and coping collide.

Front = -Y (reads the same from both long sides), pivot = bottom-centre.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix  # noqa: E402

ns = C.ns

W, D = 8.0, 3.0              # coping footprint
WALL_H = 0.94
COP = (0.9, 1.1)             # coping bottom / top
SOIL_Z = 1.0
TOP = 1.8                    # tallest flower head
TULIP_COLS = (C.BRAND, C.PETAL_PINK, C.MUSTARD)
DAISY_COLS = (C.PETAL_WHITE, C.PETAL_VIOLET)


def build():
    wall = C.ring_slab(C.rrect(W - 0.16, D - 0.16, 0.3, 2), C.rrect(W - 0.86, D - 0.86, 0.12, 2), "z", 0.0, WALL_H)
    plinth = C.ring_slab(C.rrect(W - 0.06, D - 0.06, 0.32, 2), C.rrect(W - 0.6, D - 0.6, 0.14, 2), "z", 0.0, 0.16)
    cop = C.ring_slab(C.rrect(W, D, 0.34, 2), C.rrect(W - 0.98, D - 0.98, 0.12, 2), "z", COP[0], COP[1])
    ns.bevel(cop, width=0.05, segments=1)
    soil = ns.box((W - 0.9, D - 0.9, 0.1), loc=(0, 0, SOIL_Z - 0.05), bevel=0.0)
    C.part([wall], "Bed", C.BRICK, "Brick", can_collide=True, smooth_angle=40)
    C.part([plinth], "Plinth", C.BRICK_DARK, "Brick", can_collide=True, smooth_angle=40)
    C.part([cop], "Coping", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part([soil], "Soil", C.SOIL, "Pebble", smooth_angle=None)

    rnd = random.Random(21)
    # one full leafy mound filling the bed, crowned in the middle, dropping into the soil at the edges
    mound = C.grid_box((W - 1.04, D - 1.04, 0.34), (22, 6, 1), loc=(0, 0, SOIL_Z + 0.17 - 0.1), bottom=False)
    C.round_box(mound, (0, 0, SOIL_Z + 0.07), ((W - 1.04) / 2, (D - 1.04) / 2, 0.17), 0.16, r_bottom=0.02)
    # leafy clumps: rounded bumps in two staggered rows (+ the ends), then a little noise
    bumps = []
    for i in range(9):
        x = -3.15 + 6.3 * i / 8
        bumps.append((x + rnd.uniform(-0.1, 0.1), (-0.42 if i % 2 else 0.42) + rnd.uniform(-0.08, 0.08),
                      rnd.uniform(0.62, 0.78), rnd.uniform(0.15, 0.2)))
        if i % 2 == 0 and 0 < i < 8:
            bumps.append((x + 0.4, -0.45, 0.55, 0.12))
        elif 0 < i < 8:
            bumps.append((x - 0.4, 0.45, 0.55, 0.12))
    for v in mound.data.vertices:
        if v.co.z > SOIL_Z:
            h = 0.0
            for bx, by, br, bh in bumps:
                d = math.hypot(v.co.x - bx, (v.co.y - by) * 1.15) / br
                if d < 1.0:
                    h = max(h, bh * (1 - d * d) ** 0.7)
            edge = min(1.0, (min((W - 1.04) / 2 - abs(v.co.x), (D - 1.04) / 2 - abs(v.co.y)) + 0.05) / 0.3)
            v.co.z += h * max(0.25, edge)
    mound.data.update()
    C.noise_displace(mound, amp=0.07, freq=3.4, seed=8, jitter=0.02, keep=lambda co: co.z < SOIL_Z - 0.05)
    dapple = C.noise_field(freq=2.6, seed=4)
    tones = C.split_faces(mound, lambda c, n, i: "L" if (n.z > 0.75 and dapple(c) > -0.1) else
                          ("D" if (dapple(c) < -0.3 or n.z < 0.2) else "M"), name="Mound")
    looks = {"L": ("LeavesLight", C.LEAF_LIGHT), "M": ("LeavesMid", C.FOLIAGE), "D": ("LeavesDark", C.FOLIAGE_DARK)}
    for key, ob in tones.items():
        C.part([ob], looks[key][0], looks[key][1], "Plastic", smooth_angle=None)
    def surface_z(x, y):
        """Height of the mound top at (x, y) (ray cast down onto the leaf parts)."""
        from mathutils import Vector
        best = SOIL_Z
        for ob in tones.values():
            ok, loc, nrm, _ = ob.ray_cast(Vector((x, y, 4.0)), Vector((0, 0, -1)))
            if ok:
                best = max(best, loc.z)
        return best

    # tulip drifts (3 per drift, same colour), both rows, heads standing clear of the leaves
    groups = {}
    drifts = [(-3.0, -0.42), (-1.85, 0.45), (-0.65, -0.45), (0.6, 0.45), (1.85, -0.42), (3.0, 0.42)]
    for k, (x, y) in enumerate(drifts):
        col = TULIP_COLS[k % 3]
        for j in range(3):
            a = 2.1 * j + k
            px, py = x + 0.3 * math.cos(a), y + 0.2 * math.sin(a)
            z0 = surface_z(px, py) - 0.1
            h = TOP - 0.5 - z0 - rnd.uniform(0.0, 0.12)
            tilt = (rnd.uniform(-8, 8) - 8 * (1 if y < 0 else -1), rnd.uniform(-10, 10))
            C.merge_into(groups, C.tulip(px, py, z0, h, col, r=0.19, tilt=tilt, seed=k * 5 + j))
        # two strap leaves per drift, leaning out
        for j, a in enumerate((k * 1.7, k * 1.7 + 2.6)):
            cx, cy = x + 0.12 * math.cos(a), y + 0.1 * math.sin(a)
            z0 = surface_z(cx, cy) - 0.06
            d = (math.cos(a + 0.4), math.sin(a + 0.4))
            blade = C.prism([(-0.08, 0.0), (0.08, 0.0), (0.02, 0.5)], "y", -0.02, 0.02)
            ns.apply_all(blade)
            M = (Matrix.Translation((cx, cy, z0)) @ Matrix.Rotation(math.atan2(d[1], d[0]) + math.pi / 2, 4, "Z") @
                 Matrix.Rotation(math.radians(25 + 10 * j), 4, "X"))
            blade.data.transform(M)
            blade.data.update()
            groups.setdefault(C.FOLIAGE, []).append(blade)
    # small daisies dotted over the leaves, facing out and up
    heads = {C.PETAL_WHITE: [], C.PETAL_VIOLET: []}
    eyes = []
    for k in range(12):
        x = -3.2 + 6.4 * (k + 0.5) / 12 + rnd.uniform(-0.15, 0.15)
        y = (0.62 if k % 2 else -0.62) * rnd.uniform(0.75, 1.05)
        z = surface_z(x, y)
        pt, eye = C.blossom((x, y, z + 0.015), (0, 0.7 if y > 0 else -0.7, 0.75), rnd.uniform(0.2, 0.25), up_tilt=0.0,
                            spin=rnd.uniform(0, 1.2))
        heads[DAISY_COLS[k % 2]].append(pt)
        eyes.append(eye)
    names = {C.BRAND: "TulipsRed", C.PETAL_PINK: "TulipsPink", C.MUSTARD: "TulipsGold", C.FOLIAGE_DARK: "Stems",
             C.FOLIAGE: "TulipLeaves"}
    for col, objs in groups.items():
        C.part(objs, names[col], col, smooth_angle=60 if col == C.FOLIAGE_DARK else None)
    C.part(heads[C.PETAL_WHITE], "DaisiesWhite", C.PETAL_WHITE, smooth_angle=None)
    C.part(heads[C.PETAL_VIOLET], "DaisiesViolet", C.PETAL_VIOLET, smooth_angle=None)
    C.part(eyes, "DaisyEyes", C.MUSTARD_SAUCE, smooth_angle=None)
    return {}


META = {"planting": "tulips (red-orange, pink, mustard) and daisies (white, violet) on leaf clumps",
        "bed_height": COP[1]}

if __name__ == "__main__":
    C.run(build, "Lobby_FlowerBed", meta=META, budget=2000, pivot=(0.0, 0.0, 0.0))
