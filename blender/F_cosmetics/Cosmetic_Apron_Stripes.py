"""Cosmetic_Apron_Stripes — the butcher's apron: bold vertical stripes (cos_trim) running the
full length of the cos_body cloth, clipped to the cut inside the binding.

Worn on BodyFrontAttachment (pivot = origin, body behind it along +Y). Same cut, straps,
ties, bow, pockets and pencil as Cosmetic_Apron.
Roles: Apron = cos_body; Trim (stripes, binding, straps, ties, bow, pockets) = cos_trim.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

PITCH = 0.27
WIDTH = 0.095


def zs():
    top, bot = C.APRON_TOP - C.BIND, C.APRON_HEM + C.BIND
    pts = [top, 0.62, 0.30]
    pts += [0.30 - 0.8 * k / 10 for k in range(1, 11)]          # armhole curve, finely
    pts += [-0.64, -0.85, -1.05, -1.28, -1.50, -1.72, bot]
    return pts


def build():
    cols = []
    max_hw = C.apron_hw(C.APRON_HEM) - C.BIND
    for k in range(-4, 4):
        xc = (k + 0.5) * PITCH                    # no stripe on the centre line: symmetric pairs
        if abs(xc) + WIDTH / 2 > max_hw - 0.06:     # never a sliver against the binding
            continue
        col = []
        for z in zs():
            hw = C.apron_hw(z) - C.BIND
            lx, rx = max(xc - WIDTH / 2, -hw), min(xc + WIDTH / 2, hw)
            if rx - lx > 0.004:
                col.append((lx, rx, z))
            elif col:
                break
        if len(col) >= 2:
            cols.append(col)
    stripes = C.strip_quads("Stripes", cols, lift=0.007)
    C.apron_base("Apron_Stripes", extra_trim=[stripes])


if __name__ == "__main__":
    C.run(build, "Cosmetic_Apron_Stripes", "Apron")
