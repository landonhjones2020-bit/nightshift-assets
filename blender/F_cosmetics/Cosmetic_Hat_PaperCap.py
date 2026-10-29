"""Cosmetic_Hat_PaperCap — the folded paper diner cap (garrison style): two paper side panels
folded together into a crisp top crease that overhangs the rim in pointed front/back peaks,
a folded cuff around the bottom and a cos_trim stripe along the cuff.

Worn on HatAttachment (pivot = origin = top centre of the head; head below, front -Y). The
rim hugs the head at z -0.30 (r 0.625 x 0.665 vs head r 0.58); above it the plan blends from
that ellipse into a pointed lens, so the walls stand clear of the head's rounded top edge
and the crease rides 0.2 above the flat head top.
Roles: Cap (shell + cuff) = cos_body; Stripe = cos_trim.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

N = 36
RIM_Z = -0.30
SH_Z = -0.02
T = 0.022          # paper thickness


def rim(c, s, d=0.0):
    return (0.625 + d) * c, (0.665 + d) * s


def shoulder(c, s, d=0.0):
    """Lens-shaped plan: pointed at the front/back folds."""
    return (0.60 + d) * math.copysign(abs(c) ** 1.6, c), (0.775 + d) * s


def crease_z(s2):
    return 0.20 + 0.12 * s2


def angles():
    for i in range(N):
        ph = 2 * math.pi * i / N
        yield math.cos(ph), math.sin(ph)


def wall(z, d):
    """Ring on the lower wall at height z (blend ellipse -> lens), pushed d outward."""
    t = (z - RIM_Z) / (SH_Z - RIM_Z)
    ring = []
    for c, s in angles():
        x0, y0 = rim(c, s, d)
        x1, y1 = shoulder(c, s, d)
        ring.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z))
    return ring


def band(z0, z1, out0, out1, name):
    rings = [wall(z0 - 0.004, out0), wall(z0, out1), wall(z1, out1), wall(z1 + 0.004, out0)]
    rings.append(rings[0])
    return C.loft(name, rings, None, None)


def build():
    dc = C.default_colours("Hat_PaperCap")
    outer = [[(*rim(c, s), RIM_Z) for c, s in angles()],
             [(*shoulder(c, s), SH_Z + 0.03 * s * s) for c, s in angles()],
             [(0.035 * c, 0.875 * s, crease_z(s * s)) for c, s in angles()]]
    inner = [[(0.008 * c, 0.85 * s, crease_z(s * s) - 0.035) for c, s in angles()],
             [(*shoulder(c, s, -T), SH_Z + 0.03 * s * s - 0.012) for c, s in angles()],
             [(*rim(c, s, -T), RIM_Z) for c, s in angles()]]
    shell = C.loft("Shell", outer + inner + [outer[0]], None, None)
    cuff = band(RIM_Z + 0.002, -0.13, 0.002, 0.02, "Cuff")
    C.part([shell, cuff], "Cap", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=32)
    stripe = band(-0.245, -0.185, 0.016, 0.03, "Stripe")
    C.part(stripe, "Stripe", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=35)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Hat_PaperCap", "Hat")
