"""Lobby_IronFence — one 8-stud module of the lobby's perimeter fence (8 x 6.95 x 1.4 + pillar).

2026-11-04 (Landon: "the gate not going around all the way"): the lobby is now fenced on every
side with this module (MapKit wall letter "I"): a brick dwarf wall with a stone coping, black
iron railings (15 bars with gold spear tips, three rails) and one brick pillar with a stone cap
and a gold ball finial standing on the module's left edge (x = -4, as seen from the front), so
a run of modules alternates pillar / railing; Lobby_FencePost closes the far end of a run and
turns the corners.

Front = -Y (the plaza side), pivot = bottom-centre of the 8-stud run (the pillar overhangs to
x = -4.7). No collision (the map adds an invisible 12-tall wall per module).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

IRON = "#1C1D22"
PILLAR_X = -4.0
PW = 1.4                # pillar width
WALL_H = 1.3
COPE = 0.15
RAIL_Z = (1.62, 4.55, 4.95)
BAR_TOP = 5.35


def build():
    brick, stone, iron, gold = [], [], [], []
    half = PW / 2
    # pillar + cap + pyramid + ball
    brick.append(ns.box((PW, PW, 6.0), loc=(PILLAR_X, 0, 3.0), bevel=0.04, segments=1))
    stone.append(ns.box((PW + 0.3, PW + 0.3, 0.3), loc=(PILLAR_X, 0, 6.15), bevel=0.05, segments=1))
    stone.append(ns.box((PW + 0.1, PW + 0.1, 0.18), loc=(PILLAR_X, 0, 1.9), bevel=0.03, segments=1))
    pyr = C.loft([(6.3, PW, PW, 0.02), (6.62, 0.5, 0.5, 0.02), (6.66, 0.36, 0.36, 0.02)], segs=1, cx=PILLAR_X, cy=0.0)
    stone.append(pyr)
    gold.append(ns.sphere(0.2, loc=(PILLAR_X, 0, 6.85), segs=8, rings=5))
    # dwarf wall + coping
    x0, x1 = PILLAR_X + half, -PILLAR_X - half
    brick.append(ns.box((x1 - x0, 0.8, WALL_H), loc=((x0 + x1) / 2, 0, WALL_H / 2), bevel=0.0))
    stone.append(ns.box((x1 - x0, 1.0, COPE), loc=((x0 + x1) / 2, 0, WALL_H + COPE / 2), bevel=0.03, segments=1))
    # railings: three rails, 15 bars, spear tips
    for z in RAIL_Z:
        iron.append(ns.box((x1 - x0, 0.1, 0.12), loc=((x0 + x1) / 2, 0, z), bevel=0.0))
    n = 15
    for i in range(n):
        x = x0 + 0.22 + i * (x1 - x0 - 0.44) / (n - 1)
        iron.append(ns.cyl(0.045, BAR_TOP - (WALL_H + COPE), loc=(x, 0, (WALL_H + COPE + BAR_TOP) / 2), verts=5, bevel=0.0))
        gold.append(ns.cyl(0.1, 0.32, loc=(x, 0, BAR_TOP + 0.14), verts=4, bevel=0.0, radius_top=0.0))
        if i % 2 == 0 and i < n - 1:   # small rings between the two top rails
            r = C.ns.torus(0.13, 0.025, major_segs=8, minor_segs=3)
            r.rotation_euler = (1.5708, 0, 0)
            r.location = (x + (x1 - x0 - 0.44) / (n - 1) / 2, 0, (RAIL_Z[1] + RAIL_Z[2]) / 2)
            iron.append(r)
    C.part(brick, "Brick", C.BRICK, "Brick", smooth_angle=None)
    C.part(stone, "Stone", C.STONE, "Concrete", smooth_angle=40)
    C.part(iron, "Iron", IRON, "Metal", smooth_angle=50)
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=50)


META = {"module": 8, "pillar": "left edge (x = -4 as seen from the front), 1.4 wide; Lobby_FencePost closes a run"}

if __name__ == "__main__":
    C.run(build, "Lobby_IronFence", meta=META, budget=1600)
