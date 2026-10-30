"""World_PineMid — medium stylized low-poly pine (~7 wide x 19 tall), same family as
World_PineTall.

Four jagged tiers (two alternating dark greens, lighter branch-tip bands, darker
underside) with a lean baked in: the tiers drift ~1.9 studs toward +X / slightly +Y as
they rise, and the trunk follows, so a row of these never looks copy-pasted. Exports as
2 MeshParts: foliage (SmoothPlastic, vertex colours, no collision) and Trunk (Wood,
collides). Pivot = trunk base (origin), not the bbox centre.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

TIERS = [  # (R, H, z0) bottom -> top
    (3.5, 6.4, 2.5),
    (2.9, 5.8, 5.9),
    (2.25, 5.3, 9.1),
    (1.6, 6.8, 12.2),
]


def build():
    C.pine(TIERS, trunk_r=0.48, trunk_top=6.5, seed=23, n=7, lean=(1.9, 0.6))


META = {"kind": "tree", "pivot": "trunk base", "trunk_collides": True, "lean": "baked ~1.9 studs toward +X (Blender) at the top"}

if __name__ == "__main__":
    C.run(build, "World_PineMid", meta=META)
