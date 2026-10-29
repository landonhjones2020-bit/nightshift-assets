"""Cosmetic_Hat_Lampshade — the Cursed lampshade: an old pleated fabric shade sitting slightly
tilted on the head, with trimmed rims, a fringe of little tassels, the wire spider resting on
the head top and a small glowing bulb in its socket inside.

Worn on HatAttachment (pivot = origin = top centre of the head; head below, front -Y). The
spider washer rests on the head top; the shade (r 0.84 at the bottom rim, 0.48 at the top)
hangs around the head with >= 0.2 clearance, tilted 10 deg to the wearer's left and 5 deg
back.
Roles: Shade = cos_body; Trim (rims, tassels, spider, socket) = cos_trim; Bulb (glass) =
cos_beam (a glow part, Neon) — see the batch report: the catalogue trim colour is a dark brown,
so the glowing glass is the beam role rather than trim.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

from mathutils import Matrix  # noqa: E402

ns = C.ns
PLEATS = 24
V = PLEATS * 2
BOT_R, BOT_Z = 0.84, -0.40
TOP_R, TOP_Z = 0.48, 0.50
BULB = "#FFE9A8"


def shade_ring(r, z, amp):
    out = []
    for i in range(V):
        a = 2 * math.pi * i / V
        rr = r + (amp if i % 2 == 0 else -amp)
        out.append((rr * math.cos(a), rr * math.sin(a), z))
    return out


def rim_band(r, z, w=0.055, t=0.03, n=16):
    rings = []
    for dr, dz in ((-0.006, -w / 2), (t, -w / 2), (t, w / 2), (-0.006, w / 2)):
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / n
            ring.append(((r + dr) * math.cos(a), (r + dr) * math.sin(a), z + dz))
        rings.append(ring)
    rings.append(rings[0])
    return C.loft("Rim", rings, None, None)


def build():
    dc = C.default_colours("Hat_Lampshade")
    amp = 0.03
    outer = [shade_ring(BOT_R, BOT_Z, amp), shade_ring(TOP_R, TOP_Z, amp * 0.7)]
    inner = [shade_ring(TOP_R - 0.018, TOP_Z, amp * 0.7), shade_ring(BOT_R - 0.018, BOT_Z, amp)]
    shade = C.loft("Shade", outer + inner + [outer[0]], None, None)

    trims = [rim_band(BOT_R + amp, BOT_Z + 0.01), rim_band(TOP_R + amp * 0.7, TOP_Z - 0.01, w=0.045)]
    # tassel fringe under the bottom rim
    for i in range(12):
        a = 2 * math.pi * (i + 0.5) / 12
        x, y = (BOT_R + 0.03) * math.cos(a), (BOT_R + 0.03) * math.sin(a)
        trims.append(ns.cyl(0.032, 0.12, loc=(x, y, BOT_Z - 0.075), verts=5, bevel=0.0, radius_top=0.009))
    # wire spider: washer on the head top, three arms up to the top rim
    trims.append(ns.ring(0.075, 0.11, 0.02, loc=(0, 0, 0.11), verts=10))
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        trims.append(C.rod((0.1 * math.cos(a), 0.1 * math.sin(a), 0.11),
                           ((TOP_R - 0.01) * math.cos(a), (TOP_R - 0.01) * math.sin(a), TOP_Z - 0.01), 0.012, verts=4))
    # bulb socket standing on the head top
    trims.append(ns.lathe([(0.0, 0.0), (0.075, 0.0), (0.08, 0.03), (0.07, 0.15), (0.055, 0.17), (0.0, 0.17)], verts=10))
    bulb = ns.lathe([(0.0, 0.165), (0.05, 0.165), (0.05, 0.2), (0.1, 0.27), (0.112, 0.33), (0.09, 0.39), (0.05, 0.425),
                     (0.0, 0.435)], verts=10, name="Bulb")

    objs = {"Shade": [shade], "Trim": trims, "Bulb": [bulb]}
    # lift 0.02 so the tilted socket base stays on top of the head, then tilt
    tilt = Matrix.Rotation(math.radians(-5), 4, "X") @ Matrix.Rotation(math.radians(10), 4, "Y") @ \
        Matrix.Translation((0, 0, 0.02))
    for lst in objs.values():
        for o in lst:
            ns.apply_all(o)
            o.matrix_world = tilt @ o.matrix_world
    C.part(objs["Shade"], "Shade", dc["body"], "SmoothPlastic", recolor="cos_body",
           smooth_angle=30)
    C.part(objs["Trim"], "Trim", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=50)
    C.part(objs["Bulb"], "Bulb", BULB, "Neon", recolor="cos_beam", cast_shadow=False, smooth_angle=60)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Hat_Lampshade", "Hat")
