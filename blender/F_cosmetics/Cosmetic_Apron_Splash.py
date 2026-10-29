"""Cosmetic_Apron_Splash — "Ketchup Splash": the bib apron with glossy ketchup splats, drips
and droplets (all cos_trim) on the cos_body cloth.

Worn on BodyFrontAttachment (pivot = origin, body behind it along +Y). Same cut, straps,
ties, bow and bib pocket as Cosmetic_Apron (no hip pocket: the splats own the skirt).
The big splats and drips are raised blobs; the droplets lie flat.
Roles: Apron = cos_body; Trim (splats, binding, straps, ties, bow, pocket) = cos_trim.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402


FLUNG = []      # droplets flung off the ray tips (collected while building splats)


def splat(cx, cz, R, seed, N=30, rays=6, ray_len=(0.3, 0.8), fling=True):
    """Irregular blob with uneven splash rays; droplets land beyond some ray tips."""
    rnd = random.Random(seed)
    a1, a2 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    picks = rnd.sample(range(N), rays)
    ray = {i: (R * rnd.uniform(*ray_len), rnd.choice((1, 1, 2))) for i in picks}
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N
        r = R * (1 + 0.13 * math.sin(2 * t + a1) + 0.09 * math.sin(3 * t + a2) + rnd.uniform(-0.04, 0.04))
        for j, (L, wdt) in ray.items():
            d = min(abs(i - j), N - abs(i - j))
            if d == 0:
                r += L
            elif d == 1 and wdt == 2:
                r += L * 0.45
        pts.append((cx + r * math.cos(t), cz + r * math.sin(t)))
    if fling:
        for j, (L, _) in ray.items():
            if rnd.random() < 0.6:
                t = 2 * math.pi * j / N
                rr = R * 1.1 + L + rnd.uniform(0.05, 0.11)
                FLUNG.append(C.circle2(rnd.uniform(0.022, 0.036), N=7, cx=cx + rr * math.cos(t),
                                       cy=cz + rr * math.sin(t), phase=rnd.uniform(0, 1)))
    return pts


def drip(x, z_top, length, w, bulb=1.35):
    """Run of ketchup from z_top down, ending in a round drop."""
    r = w / 2 * bulb
    zb = z_top - length
    pts = [(x - w / 2, z_top), (x - w / 2 * 0.9, zb + r * 1.2)]
    for i in range(7):
        a = math.radians(200 + 140 * i / 6)
        pts.append((x + r * math.cos(a), zb + r * math.sin(a)))
    pts += [(x + w / 2 * 0.9, zb + r * 1.2), (x + w / 2, z_top)]
    return pts


def build():
    FLUNG.clear()
    raised = [
        splat(-0.40, -0.80, 0.21, 3, rays=7),
        splat(0.48, -1.40, 0.19, 5, rays=6),
        splat(-0.14, 0.66, 0.12, 11, N=24, rays=5),
        drip(-0.45, -0.90, 0.44, 0.075),
        drip(-0.27, -0.92, 0.24, 0.06),
        drip(0.55, -1.47, 0.30, 0.065),
    ]
    flat = [splat(0.22, -0.30, 0.07, 8, N=14, rays=3, fling=False),
            splat(-0.60, -1.66, 0.06, 13, N=14, rays=3, fling=False)]
    flat += [p for p in FLUNG if all(abs(x) < C.apron_hw(z) - C.BIND - 0.01 and z > C.APRON_HEM + C.BIND + 0.01
                                     and z < C.APRON_TOP - C.BIND - 0.01 for x, z in p)]
    rnd = random.Random(21)
    for cx, cz, r in [(0.08, -0.95, 0.04), (-0.78, -1.15, 0.03), (0.72, -1.0, 0.035), (0.10, -1.72, 0.03)]:
        flat.append(C.circle2(r * rnd.uniform(0.9, 1.15), N=7, cx=cx, cy=cz, phase=rnd.uniform(0, 1)))
    blobs = C.flat_patches("Splats", raised, lift=0.016, walls=True)
    drops = C.flat_patches("Drops", flat, lift=0.009)
    C.apron_base("Apron_Splash", hips=False, extra_trim=[blobs, drops])


if __name__ == "__main__":
    C.run(build, "Cosmetic_Apron_Splash", "Apron")
