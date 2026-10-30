"""World_TreeRound — stylized deciduous tree (~12 wide x 16 tall).

A chunky flared bark trunk that splits into three stubby branches, under a canopy of
five lumpy faceted blobs. The canopy is two greens: upward-facing facets lighter (a
baked moonlight gradient that still reads at night), the rest darker. Canopy faces
buried inside neighbouring blobs are removed, so the merged canopy stays cheap.
Exports as 2 MeshParts: Canopy (SmoothPlastic, vertex colours, no collision) and
Trunk (Wood, collides). Pivot = trunk base (origin).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

BLOBS = [  # (radius, centre, scale, seed)
    (4.1, (0.2, 0.3, 12.2), (1.12, 1.05, 0.88), 3),
    (3.1, (-3.1, -0.6, 9.8), (1.05, 1.0, 0.9), 5),
    (3.2, (3.0, 0.7, 10.2), (1.0, 1.05, 0.9), 7),
    (2.9, (0.6, 2.9, 9.5), (1.05, 1.0, 0.88), 9),
    (2.7, (-0.5, -2.8, 9.2), (1.1, 1.0, 0.85), 13),
]


def build():
    trunk = C.lathe([(1.35, 0.0), (0.98, 0.5), (0.8, 2.6), (0.62, 6.4)], verts=8, phase=11)
    branches = [
        C.rod((0.0, 0.0, 4.4), (-2.8, -0.5, 9.0), 0.5, verts=6, r_top=0.24),
        C.rod((0.0, 0.0, 4.8), (2.7, 0.6, 9.4), 0.5, verts=6, r_top=0.24),
        C.rod((0.0, 0.1, 5.6), (0.4, 2.5, 9.2), 0.42, verts=6, r_top=0.2),
    ]
    C.part([trunk] + branches, "Trunk", C.BARK, "Wood", can_collide=True, smooth_angle=None)

    blobs = [C.ico_blob(r, loc=c, scale=s, subdiv=2, seed=sd, jitter=0.13) for r, c, s, sd in BLOBS]
    C.cull_hidden(blobs)
    light, dark = C.two_tone(blobs, up=0.42, name="Canopy")
    C.part(light, "CanopyLight", "#4A7F3A", "SmoothPlastic", smooth_angle=None)
    C.part(dark, "CanopyDark", C.GREEN_DARK, "SmoothPlastic", smooth_angle=None)


META = {"kind": "tree", "pivot": "trunk base", "trunk_collides": True}

if __name__ == "__main__":
    C.run(build, "World_TreeRound", meta=META)
