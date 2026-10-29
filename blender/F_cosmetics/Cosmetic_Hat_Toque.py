"""Cosmetic_Hat_Toque — the tall chef's toque: a smooth headband, a pleated column that flares
slightly as it rises, and a big soft puff folding over the top of the pleats.

Worn on HatAttachment (pivot = origin = top centre of the head; head below, front -Y). The
band hugs the head from z -0.32 to 0 (r 0.62 vs head r 0.58); the column and puff stand
1.47 above the head top, the puff billowing out past the column. The puff carries on the pleats softly so it reads as gathered cloth.
Roles: every part is cos_body (single-colour item).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

PLEATS = 18
V = PLEATS * 2


def pleat(i, amp):
    """Zig-zag radius offset: ridge on even vertices, valley on odd ones."""
    return amp if i % 2 == 0 else -amp


def ring(r, z, amp=0.0, twist=0.0):
    out = []
    for i in range(V):
        a = 2 * math.pi * i / V + twist
        rr = r + pleat(i, amp)
        out.append((rr * math.cos(a), rr * math.sin(a), z))
    return out


def build():
    dc = C.default_colours("Hat_Toque")
    # headband: a soft rolled band with an inner face
    band = C.loft("Band", [ring(0.598, -0.32), ring(0.628, -0.31), ring(0.638, -0.16), ring(0.63, 0.005),
                           ring(0.60, 0.02), ring(0.598, -0.32)], None, None)
    # pleated column flaring to the puff, then the puff closing over the top
    body = [ring(0.60, -0.02, 0.0),
            ring(0.612, 0.06, 0.042),
            ring(0.645, 0.48, 0.048),
            ring(0.685, 0.88, 0.048),
            ring(0.70, 0.99, 0.04, twist=0.02),
            ring(0.84, 1.07, 0.036, twist=0.05),
            ring(0.885, 1.20, 0.028, twist=0.07),
            ring(0.81, 1.34, 0.018, twist=0.09),
            ring(0.56, 1.43, 0.01, twist=0.1),
            ring(0.24, 1.465, 0.0)]
    column = C.loft("Column", body, None, "fan")
    C.part([band], "Band", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=50)
    C.part([column], "Puff", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=50)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Hat_Toque", "Hat")
