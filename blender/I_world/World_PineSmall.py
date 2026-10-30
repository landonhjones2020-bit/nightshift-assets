"""World_PineSmall — small stylized low-poly pine (~5 wide x 11 tall), same family as
World_PineTall / World_PineMid.

Three jagged tiers (two alternating dark greens, lighter branch-tip bands, darker
underside), a slight lean and a short flared trunk. Exports as 2 MeshParts: foliage
(SmoothPlastic, vertex colours, no collision) and Trunk (Wood, collides).
Pivot = trunk base (origin).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

TIERS = [  # (R, H, z0) bottom -> top
    (2.5, 4.6, 1.5),
    (1.95, 4.1, 3.9),
    (1.35, 4.7, 6.3),
]


def build():
    C.pine(TIERS, trunk_r=0.32, trunk_top=4.0, seed=37, n=6, lean=(-0.3, 0.25))


META = {"kind": "tree", "pivot": "trunk base", "trunk_collides": True}

if __name__ == "__main__":
    C.run(build, "World_PineSmall", meta=META)
