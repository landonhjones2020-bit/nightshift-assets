"""Cosmetic_Flashlight_Lantern — the Graveyard Lantern flashlight skin: a small square iron
cage lantern held by its bail handle, with a spired roof, gothic pointed-arch bars over warm
glass panes, a stepped base and a candle flame inside.

Held in the left hand: pivot = grip point = the top of the bail handle (the bail's top bar
runs along Y, like the flashlight body, so the hand wraps it the same way); the lantern hangs
below it (-Z). Total 0.95 tall x 0.46 wide.
Roles: Cage (posts, frames, arches, bail) = cos_body; Trim (roof, finial, base) = cos_trim;
Glass and Flame = cos_beam (glass is translucent, flame Neon). The candle keeps a fixed colour.
Sockets: Beam = the flame, yaw 0 (pointing -Y; attach the light here).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

from mathutils import Matrix  # noqa: E402

ns = C.ns
H = 0.17                     # half width of the cage (post centres)
TOP_Z, BOT_Z = -0.37, -0.80  # cage frame top / bottom
FLAME_Z = -0.585


def bail():
    pts = []
    for i in range(9):
        a = math.radians(180 * i / 8)
        pts.append((0.0, 0.16 * math.cos(a), -0.175 + 0.155 * math.sin(a)))
    pts = [(0, 0.16, -0.25)] + pts[::-1][::-1] + [(0, -0.16, -0.25)]
    return C.cord("Bail", pts, 0.022, sides=6, per_seg=1)


def face_arches():
    """Pointed gothic arch + centre bar on each of the four faces."""
    out = []
    for k in range(4):
        a = math.pi / 2 * k
        c, s = math.cos(a), math.sin(a)

        def P(u, z, d=H + 0.012):
            # u across the face, d outward
            return (c * d - s * u, s * d + c * u, z)
        apex = TOP_Z - 0.04
        spring = TOP_Z - 0.17
        out.append(C.rod(P(-H + 0.02, spring), P(0, apex), 0.014, verts=4))
        out.append(C.rod(P(H - 0.02, spring), P(0, apex), 0.014, verts=4))
        out.append(C.rod(P(0, apex), P(0, BOT_Z + 0.02), 0.013, verts=4))
    return out


def build():
    dc = C.default_colours("Flashlight_Lantern")
    cage = [bail()]
    for sx in (-1, 1):
        for sy in (-1, 1):
            cage.append(ns.box((0.045, 0.045, TOP_Z - BOT_Z + 0.02), loc=(sx * H, sy * H, (TOP_Z + BOT_Z) / 2),
                               bevel=0.0))
    for z in (TOP_Z, BOT_Z):
        for k in range(4):
            a = math.pi / 2 * k
            cage.append(ns.box((2 * H + 0.045, 0.04, 0.04), loc=(math.cos(a) * H, math.sin(a) * H, z),
                               rot=(0, 0, math.degrees(a) + 90), bevel=0.0))
    cage += face_arches()
    C.part(cage, "Cage", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=40)

    trim = []
    # roof: flared eave plate + four-sided spire + finial ring
    trim.append(ns.box((0.47, 0.47, 0.035), loc=(0, 0, TOP_Z + 0.035), bevel=0.012, segments=1))
    trim.append(ns.cyl(0.29, 0.15, loc=(0, 0, TOP_Z + 0.125), verts=4, bevel=0.0, radius_top=0.035,
                       rot=(0, 0, 45)))
    trim.append(ns.sphere(0.045, loc=(0, 0, TOP_Z + 0.215), segs=8, rings=4))
    trim.append(ns.torus(0.045, 0.014, loc=(0, 0, TOP_Z + 0.275), rot=(0, 90, 0), major_segs=10, minor_segs=4))
    # stepped base with four little ball feet
    trim.append(ns.box((0.47, 0.47, 0.05), loc=(0, 0, BOT_Z - 0.04), bevel=0.012, segments=1))
    trim.append(ns.box((0.38, 0.38, 0.04), loc=(0, 0, BOT_Z - 0.085), bevel=0.01, segments=1))
    for sx in (-1, 1):
        for sy in (-1, 1):
            trim.append(ns.sphere(0.035, loc=(sx * 0.15, sy * 0.15, BOT_Z - 0.115), segs=6, rings=3))
    C.part(trim, "Trim", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=40)

    glass = [ns.box((2 * H - 0.02, 0.012, TOP_Z - BOT_Z - 0.03), loc=(math.cos(a) * (H - 0.005), math.sin(a) * (H - 0.005),
                                                                    (TOP_Z + BOT_Z) / 2),
                    rot=(0, 0, math.degrees(a) - 90), bevel=0.0) for a in (0, math.pi / 2, math.pi, 1.5 * math.pi)]
    C.part(glass, "Glass", dc["beam"], "Glass", recolor="cos_beam", transparency=0.5, cast_shadow=False,
           smooth_angle=None)
    candle = ns.cyl(0.055, 0.15, loc=(0, 0, BOT_Z - 0.015 + 0.075), verts=8, bevel=0.012, segments=1)
    C.part(candle, "Candle", "#F3E9D2", "SmoothPlastic", smooth_angle=50)
    flame = ns.lathe([(0.0, FLAME_Z - 0.06), (0.045, FLAME_Z - 0.04), (0.056, FLAME_Z), (0.036, FLAME_Z + 0.055),
                      (0.0, FLAME_Z + 0.115)], verts=8, name="Flame")
    C.part(flame, "Flame", dc["beam"], "Neon", recolor="cos_beam", cast_shadow=False, smooth_angle=60)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Flashlight_Lantern", "Flashlight", sockets={"Beam": ((0, 0, FLAME_Z), 0)},
          icon_kw={"pose": Matrix.Rotation(math.radians(-12), 4, "Y") @ Matrix.Rotation(math.radians(8), 4, "Z"),
                   "pitch": 18.0})
