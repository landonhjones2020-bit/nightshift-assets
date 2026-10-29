"""Cosmetic_Apron_Checkered — the bib apron in a diner gingham: alternate checks are cos_trim
tiles laid flush on the cos_body cloth (clipped to the outline, inside the binding).

Worn on BodyFrontAttachment (pivot = origin, body behind it along +Y). Same cut, straps,
ties, bow, pockets and pencil as Cosmetic_Apron.
Roles: Apron = cos_body; Trim (checks, binding, straps, ties, bow, pockets) = cos_trim.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

T = 0.25          # check size (studs)


def covered(x0, x1, z0, z1, rect):
    cx, cz, w, h = rect
    return x0 >= cx - w / 2 and x1 <= cx + w / 2 and z0 >= cz - h / 2 and z1 <= cz + h / 2


def build():
    polys = []
    z_top = C.APRON_TOP - C.BIND
    z_bot = C.APRON_HEM + C.BIND
    rows = math.ceil((z_top - z_bot) / T)
    for j in range(rows):
        z1 = z_top - j * T
        z0 = max(z1 - T, z_bot)
        for i in range(-5, 6):
            if (i + j) % 2:
                continue
            x0 = -T / 2 + i * T
            x1 = x0 + T
            if covered(x0, x1, z0, z1, C.BIB_POCKET) or covered(x0, x1, z0, z1, C.HIP_POCKET):
                continue
            poly = C.clip_band_x(x0, x1, z0, z1, C.apron_hw, inset=C.BIND, steps=2)
            if poly:
                polys.append(poly)
    checks = C.flat_patches("Checks", polys, lift=0.007)
    C.apron_base("Apron_Checkered", extra_trim=[checks])


if __name__ == "__main__":
    C.run(build, "Cosmetic_Apron_Checkered", "Apron")
