"""Shop_BrickWall — EXTERIOR brick wall module, 8 wide x 12 tall x 1 thick (outside = front, -Y).

Dark red brick body with sparse modelled mortar: a raised mortar line on every course and
a staggered scatter of head joints (repeating every 8 studs, so modules tile), a darker
soldier-course band at the window-head line and above the plinth, a concrete plinth and a
concrete coping with drip edges on both faces. The back (+Y) gets the same treatment so the
module also works as the free-standing back-alley wall.
Pivot = bottom of the wall centre line (same grid contract as Shop_Wall: ends on 8-stud nodes).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 8.0, 12.0, 1.0
BRICK = "#7A3A2F"
BRICK_DARK = "#5C2A24"
MORTAR = "#A79C8F"
CONCRETE = "#8E8C86"
COURSE = 0.5                 # brick course height (studs)
PLINTH = 1.0
BAND_Z = (8.6, 9.6)          # soldier-course band
COPING = 11.6


def face_detail(sy, rnd):
    """Mortar lines + head joints + band skins for one face (sy = -1 front, +1 back)."""
    fy = sy * T / 2
    mortar, band = [], []
    z = PLINTH
    while z < COPING - 0.05:
        if not (BAND_Z[0] - 0.01 < z < BAND_Z[1] + 0.01):
            mortar.append(ns.box((W, 0.04, 0.06), loc=(0, fy + sy * 0.02, z), bevel=0.0))
        z += COURSE
    # head joints: staggered every other course, only ~40% drawn (sparse), deterministic
    row = 0
    z = PLINTH
    while z + COURSE < COPING:
        zc = z + COURSE / 2
        if not (BAND_Z[0] - 0.3 < zc < BAND_Z[1] + 0.3):
            off = 0.5 if row % 2 else 0.0
            for i in range(8):
                x = -W / 2 + off + i * 1.0
                if -W / 2 + 0.05 < x < W / 2 - 0.05 and rnd.random() < 0.4:
                    mortar.append(ns.box((0.06, 0.04, COURSE - 0.06), loc=(x, fy + sy * 0.02, zc), bevel=0.0))
        z += COURSE
        row += 1
    # soldier course band (vertical bricks) + a thin band above the plinth
    band.append(ns.box((W, 0.08, BAND_Z[1] - BAND_Z[0]), loc=(0, fy + sy * 0.04, sum(BAND_Z) / 2), bevel=0.0))
    for i in range(16):
        x = -W / 2 + 0.5 * i
        mortar.append(ns.box((0.05, 0.1, BAND_Z[1] - BAND_Z[0]), loc=(x + 0.25, fy + sy * 0.05, sum(BAND_Z) / 2),
                             bevel=0.0) if i % 1 == 0 else None)
    for zz in (BAND_Z[0], BAND_Z[1]):
        mortar.append(ns.box((W, 0.1, 0.06), loc=(0, fy + sy * 0.05, zz), bevel=0.0))
    band.append(ns.box((W, 0.05, 0.5), loc=(0, fy + sy * 0.025, PLINTH + 0.25), bevel=0.0))
    return [m for m in mortar if m is not None], band


def build():
    rnd = random.Random(11)
    core = ns.box((W, T, H), loc=(0, 0, H / 2), bevel=0.0)
    ns.tag(core, "Brick", BRICK, recolor="brick", can_collide=True)
    mortar, band = [], []
    for sy in (-1, 1):
        m, b = face_detail(sy, rnd)
        mortar += m
        band += b
    C.part(mortar, "Mortar", MORTAR, smooth_angle=30)
    C.part(band, "BrickBand", BRICK_DARK, recolor="brick_band", smooth_angle=30)
    # concrete plinth and coping (flat ends so modules butt seamlessly)
    plinth = C.prism(C.fillet([(-T / 2 - 0.12, 0), (T / 2 + 0.12, 0), (T / 2 + 0.12, PLINTH - 0.08),
                               (T / 2 + 0.02, PLINTH), (-T / 2 - 0.02, PLINTH), (-T / 2 - 0.12, PLINTH - 0.08)],
                              [0, 0, 0.04, 0.02, 0.02, 0.04], 1), "x", -W / 2, W / 2)
    coping = C.prism(C.fillet([(-T / 2 - 0.2, COPING), (T / 2 + 0.2, COPING), (T / 2 + 0.2, COPING + 0.12),
                               (0.0, H), (-T / 2 - 0.2, COPING + 0.12)], [0, 0, 0.03, 0.05, 0.03], 1),
                     "x", -W / 2, W / 2)
    C.part([plinth, coping], "Concrete", CONCRETE, "Concrete", smooth_angle=35)


META = {"module": "wall_exterior", "grid": 8, "size": [8, 12, 1], "outside": "front (-Y / LookVector)",
        "placement": "pivot on the wall centre line, bottom; ends on 8-stud grid nodes",
        "recolor_presets": {"Brick": {"brick": BRICK, "brick_band": BRICK_DARK},
                            "Painted": {"brick": "#4A5568", "brick_band": "#2F3646"}}}

if __name__ == "__main__":
    C.run(build, "Shop_BrickWall", pivot=(0, 0, 0), meta=META)
