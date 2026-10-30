"""World_PineTall — tall stylized low-poly pine (~9 wide x 28 tall).

Five stacked, slightly irregular tiers with jagged branch-tip skirts, alternating two
dark greens, a subtle lighter band at each tier's branch tips and a darker recessed
underside (so the tiers separate when seen from below). Short flared bark trunk visible
under the bottom tier. Exports as 2 MeshParts: foliage (SmoothPlastic, vertex colours,
no collision) and Trunk (Wood, collides). Pivot = trunk base (origin).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

TIERS = [  # (R, H, z0) bottom -> top
    (4.5, 8.4, 3.3),
    (3.85, 7.7, 7.6),
    (3.15, 7.1, 11.7),
    (2.45, 6.6, 15.6),
    (1.8, 8.4, 19.6),
]


def build():
    C.pine(TIERS, trunk_r=0.62, trunk_top=9.0, seed=11, n=7)


META = {"kind": "tree", "pivot": "trunk base", "trunk_collides": True}

if __name__ == "__main__":
    C.run(build, "World_PineTall", meta=META)
