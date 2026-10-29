"""Cosmetic_Spatula_RollingPin — the Rolling Pin spatula skin: a classic baker's rolling pin
held by one handle, the barrel pointing forward, with steel washers between the barrel and
the turned handles.

Held in the right hand: pivot = grip point (middle of the near handle) at the origin, the
barrel points along Blender -Y. 2.0 long, barrel r 0.19.
Roles: Pin (barrel + both handles) = cos_body; washers keep a fixed steel colour.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
R = 0.19
B0, B1 = -0.22, -1.17          # barrel ends (y)


def along_y(profile, verts, name):
    """Lathe [(r, y)] around the Y axis (profile y grows toward +Y)."""
    o = ns.lathe([(r, -y) for r, y in profile], verts=verts, name=name)
    o.rotation_euler = (math.radians(90), 0, 0)      # +Z -> -Y, so -(-y) ends up at y
    ns.apply_all(o)
    return o


def handle(y_far, y_near, name):
    """Turned handle from the barrel side (y_near) out to the knob end (y_far)."""
    s = 1 if y_far > y_near else -1
    L = abs(y_far - y_near)

    def at(f):
        return y_near + s * L * f
    prof = [(0.0, at(1.0)), (0.05, at(1.0)), (0.075, at(0.95)), (0.08, at(0.86)), (0.06, at(0.74)),
            (0.058, at(0.35)), (0.066, at(0.12)), (0.05, at(0.02)), (0.0, at(0.0))]
    if s < 0:
        prof = list(reversed(prof))
    return along_y(prof, 10, name)


def build():
    dc = C.default_colours("Spatula_RollingPin")
    barrel = along_y([(0.0, B1), (R - 0.05, B1), (R - 0.01, B1 + 0.015), (R, B1 + 0.05), (R, B0 - 0.05),
                      (R - 0.01, B0 - 0.015), (R - 0.05, B0), (0.0, B0)], 18, "Barrel")
    near = handle(0.30, B0 - 0.03, "Near")
    far = handle(B1 - 0.52, B1 + 0.03, "Far")
    C.part([barrel, near, far], "Pin", dc["body"], "Wood", recolor="cos_body", smooth_angle=50)

    washers = [along_y([(0.0, y - 0.012), (0.085, y - 0.012), (0.085, y + 0.012), (0.0, y + 0.012)], 10, "Washer")
               for y in (B0 - 0.025, B1 + 0.025)]
    C.part(washers, "Washers", C.STEEL, "Metal", smooth_angle=50)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Spatula_RollingPin", "Spatula")
