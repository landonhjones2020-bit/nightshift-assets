"""World_Rock — faceted grey-brown boulder (~5 wide x 3 tall).

Convex hull of noisy points on an ellipsoid: a few big chunky facets, flat-ish base sat
on the ground. Upward-facing facets a step lighter (weathered top), sides darker.
Exports as 1 MeshPart (Slate, vertex colours, no collision). Pivot = bottom-centre.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns


def build():
    rock = C.hull_rock(40, 2.65, 2.0, 2.05, seed=17, noise=0.18, base_cut=0.5,
                       cuts=[((0.3, -0.25, 1.0), 0.66), ((1.0, 0.2, 0.25), 0.7), ((-0.4, -1.0, 0.2), 0.68),
                             ((-1.0, 0.55, 0.4), 0.72), ((0.2, 1.0, 0.6), 0.74)])
    light, dark = C.two_tone([rock], up=0.55, name="Rock")
    C.part(light, "RockTop", C.ROCK_LIGHT, "Slate", smooth_angle=None)
    C.part(dark, "RockSide", C.ROCK, "Slate", smooth_angle=None)


META = {"kind": "rock"}

if __name__ == "__main__":
    C.run(build, "World_Rock", meta=META)
