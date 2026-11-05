"""Lobby_FencePost — the brick gate post that ends a run of Lobby_IronFence and turns its corners
(2.0 x 8.9 x 2.0), with an iron lantern on top.

A 1.6-square brick post (a stone band at railing height), a stone cap and a black iron lantern
with warm glass (role "lamp") under a little pyramid roof and a gold finial. Pivot = bottom-centre.
Socket: Light (the lantern's centre). No collision (the map's fence walls cover it).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

IRON = "#1C1D22"
PW = 1.6
LAMP_Z = (6.95, 8.05)


def build():
    brick, stone, iron, gold, glass = [], [], [], [], []
    brick.append(ns.box((PW, PW, 6.4), loc=(0, 0, 3.2), bevel=0.04, segments=1))
    stone.append(ns.box((PW + 0.12, PW + 0.12, 0.2), loc=(0, 0, 1.9), bevel=0.03, segments=1))
    stone.append(ns.box((PW + 0.4, PW + 0.4, 0.35), loc=(0, 0, 6.575), bevel=0.06, segments=1))
    iron.append(ns.box((0.9, 0.9, 0.18), loc=(0, 0, 6.84), bevel=0.03, segments=1))
    z0, z1 = LAMP_Z
    glass.append(ns.box((0.62, 0.62, z1 - z0 - 0.06), loc=(0, 0, (z0 + z1) / 2), bevel=0.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            iron.append(ns.box((0.08, 0.08, z1 - z0), loc=(sx * 0.33, sy * 0.33, (z0 + z1) / 2), bevel=0.0))
    roof = C.loft([(z1, 0.95, 0.95, 0.02), (z1 + 0.45, 0.2, 0.2, 0.02)], segs=1)
    iron.append(roof)
    gold.append(ns.sphere(0.13, loc=(0, 0, z1 + 0.58), segs=6, rings=4))
    C.part(brick, "Brick", C.BRICK, "Brick", smooth_angle=None)
    C.part(stone, "Stone", C.STONE, "Concrete", smooth_angle=40)
    C.part(iron, "Iron", IRON, "Metal", smooth_angle=50)
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=50)
    ns.tag(C.merge(glass, "Lantern"), "Lantern", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)


def sockets():
    return {"Light": ((0.0, 0.0, (LAMP_Z[0] + LAMP_Z[1]) / 2), 0.0)}


META = {"post": PW, "light_hint": {"type": "PointLight", "at": "Light", "color": C.LAMP_WARM, "range": 12, "brightness": 0.8}}

if __name__ == "__main__":
    C.run(build, "Lobby_FencePost", sockets=sockets(), meta=META, budget=600)
