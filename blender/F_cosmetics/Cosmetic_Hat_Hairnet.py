"""Cosmetic_Hat_Hairnet — the kitchen hairnet: a soft, puffy net dome over the hair with a
diamond lattice of raised strands and a gathered elastic band around the head.

Worn on HatAttachment (pivot = origin = top centre of the head; head below, front -Y). The
band hugs the head at z -0.36 (r 0.612 vs head r 0.58); the dome puffs 0.27 above the head
top as if there were hair inside. The dome is slightly see-through (net) so a player's hair
shows through in game; the strands and band are opaque.
Roles: every part is cos_body (single-colour item).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

V = 18
# dome profile (r, z) from the band up to the crown
PROFILE = [(0.613, -0.34), (0.632, -0.24), (0.648, -0.11), (0.638, 0.02), (0.585, 0.13), (0.48, 0.215),
           (0.32, 0.262), (0.15, 0.28), (0.0, 0.284)]


def dome_r(z):
    """Outer dome radius at height z (linear in the profile)."""
    for (r0, z0), (r1, z1) in zip(PROFILE, PROFILE[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return 0.0


def dome_point(phi, s, lift=0.0):
    """Point on the dome at azimuth phi and arc parameter s (0 band .. 1 crown)."""
    # walk the profile by cumulative length
    segs = [(PROFILE[i], PROFILE[i + 1]) for i in range(len(PROFILE) - 1)]
    lens = [math.dist(a, b) for a, b in segs]
    L = sum(lens) * s
    for (a, b), l in zip(segs, lens):
        if L <= l or (a, b) == segs[-1]:
            t = min(L / l, 1.0)
            r = a[0] + (b[0] - a[0]) * t
            z = a[1] + (b[1] - a[1]) * t
            # outward normal of the profile segment
            nx, nz = (b[1] - a[1]), -(b[0] - a[0])
            nl = math.hypot(nx, nz) or 1.0
            r += lift * nx / nl
            z += lift * nz / nl
            return (r * math.cos(phi), r * math.sin(phi), z)
        L -= l
    return (0, 0, PROFILE[-1][1] + lift)


def build():
    dc = C.default_colours("Hat_Hairnet")
    # net dome: single surface, see-through
    rings = C.lathe_pts(PROFILE[:-1], verts=V)
    dome = C.loft("Dome", rings, None, "fan")
    C.part(dome, "Net", dc["body"], "SmoothPlastic", recolor="cos_body", transparency=0.3, smooth_angle=60)

    # diamond lattice: strands spiralling both ways from the band to the crown
    strands = []
    K = 8
    for k in range(K):
        for d in (1, -1):
            ph0 = 2 * math.pi * k / K
            path = [dome_point(ph0 + d * 1.25 * s, s * 0.93, lift=0.014) for s in (0.04, 0.2, 0.36, 0.52, 0.68, 0.82, 0.93)]
            strands.append(C.cord("Strand", path, 0.0125, sides=3, per_seg=1, cap=False))
    # crown knot where the strands gather
    strands.append(C.ns.sphere(0.045, loc=(0, 0, 0.292), scale=(1, 1, 0.55), segs=8, rings=4, name="Knot"))
    C.part(strands, "Strands", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=70)

    # gathered elastic band: a fat rolled ring with little ruffles
    band_rings = []
    for j, (dr, dz) in enumerate(((-0.012, -0.035), (0.024, -0.04), (0.024, 0.04), (-0.012, 0.035))):
        ring = []
        for i in range(36):
            ph = 2 * math.pi * i / 36
            ruff = 0.012 * (1 if i % 2 else -1) * (1 if j in (1, 2) else 0.3)
            r = 0.613 + dr + ruff
            ring.append((r * math.cos(ph), r * math.sin(ph), -0.345 + dz))
        band_rings.append(ring)
    band_rings.append(band_rings[0])
    band = C.loft("Band", band_rings, None, None)
    C.part(band, "Band", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=60)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Hat_Hairnet", "Hat")
