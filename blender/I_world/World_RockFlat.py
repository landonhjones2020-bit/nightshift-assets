"""World_RockFlat — flat faceted grey-brown slab rock (~7 wide x 1.6 tall).

The flatter variant of World_Rock: a low, wide convex-hull boulder with a flat base,
upward-facing facets a step lighter. Exports as 1 MeshPart (Slate, vertex colours,
no collision). Pivot = bottom-centre.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns


def build():
    rock = C.hull_rock(40, 3.85, 2.8, 1.3, seed=29, noise=0.16, base_cut=0.3,
                       cuts=[((-0.15, 0.12, 1.0), 0.6), ((0.9, -0.6, 0.45), 0.72), ((-0.8, 0.9, 0.55), 0.74),
                             ((-0.7, -0.9, 0.5), 0.8)])
    light, dark = C.two_tone([rock], up=0.6, name="Slab")
    C.part(light, "RockTop", C.ROCK_LIGHT, "Slate", smooth_angle=None)
    C.part(dark, "RockSide", C.ROCK, "Slate", smooth_angle=None)


META = {"kind": "rock"}

if __name__ == "__main__":
    C.run(build, "World_RockFlat", meta=META)
