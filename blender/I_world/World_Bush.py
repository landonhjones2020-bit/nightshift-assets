"""World_Bush — lumpy faceted shrub clump (~4.5 wide x 2.6 tall).

Three overlapping faceted blobs with a flat base on the ground; upward-facing facets in a
lighter green, the rest darker (baked moonlight gradient). Faces buried inside the other
blobs are removed. Exports as 1 MeshPart (SmoothPlastic, vertex colours, no collision).
Pivot = bottom-centre (origin).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

BLOBS = [  # (radius, centre, scale, seed)
    (1.45, (0.15, 0.1, 1.02), (1.15, 1.0, 1.08), 4),
    (1.08, (-1.2, 0.28, 0.62), (1.05, 1.0, 1.05), 6),
    (1.02, (1.25, -0.22, 0.58), (1.05, 1.0, 1.02), 8),
]


def build():
    blobs = []
    for k, (r, c, s, sd) in enumerate(BLOBS):
        b = C.ico_blob(r, loc=c, scale=s, subdiv=2, seed=sd, jitter=0.12)
        C.flatten_below(b, -0.01 * k)      # staggered bases: the overlapping caps are never coplanar
        blobs.append(b)
    C.cull_hidden(blobs)
    light, dark = C.two_tone(blobs, up=0.45, name="Bush")
    C.part(light, "LeavesLight", "#4A7F3A", "SmoothPlastic", smooth_angle=None)
    C.part(dark, "LeavesDark", C.GREEN_DARK, "SmoothPlastic", smooth_angle=None)


META = {"kind": "shrub"}

if __name__ == "__main__":
    C.run(build, "World_Bush", meta=META)
