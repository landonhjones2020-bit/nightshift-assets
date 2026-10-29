"""Cosmetic_Spatula_Wooden — the Wooden Spatula skin: a one-piece wooden flipper with a rounded
handle, a hang hole with a leather loop, a flared neck and a thin slanted blade with two
slots, its tip toasted dark from the flat-top.

Held in the right hand: pivot = grip point (middle of the handle) at the origin, the blade
points along Blender -Y, blade face up (+Z). Same reach as the kitchen spatula (~1.85).
Roles: Wood (the whole one-piece flipper) = cos_body; leather loop and scorch marks keep fixed
colours (the toasted tip band is a fixed darker wood).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
# stations along the flipper: (y, width, thickness)
STATIONS = [(0.45, 0.10, 0.06), (0.43, 0.135, 0.075), (0.30, 0.14, 0.08), (0.0, 0.13, 0.08), (-0.28, 0.115, 0.07),
            (-0.42, 0.16, 0.055), (-0.56, 0.36, 0.045), (-0.66, 0.43, 0.04), (-1.05, 0.44, 0.034),
            (-1.30, 0.44, 0.024), (-1.33, 0.40, 0.016)]
TIP_SLANT = 0.08          # the tip edge is cut on a slant


def section(y, w, t, slant=0.0):
    e = min(w * 0.25, t * 0.45)
    pts = [(-w / 2, 0.0), (-w / 2 + e, t / 2), (w / 2 - e, t / 2), (w / 2, 0.0), (w / 2 - e, -t / 2),
           (-w / 2 + e, -t / 2)]
    return [(x, y - slant * x / 0.22, z) for x, z in pts]


def build():
    dc = C.default_colours("Spatula_Wooden")
    rings = []
    for k, (y, w, t) in enumerate(STATIONS):
        sl = TIP_SLANT if k >= len(STATIONS) - 2 else 0.0
        rings.append(section(y, w, t, sl))
    wood = C.loft("Wood", rings, "ngon", "ngon")
    ns.apply_all(wood)
    ns.boolean(wood, ns.cyl(0.032, 0.3, loc=(0, 0.36, 0), verts=10, bevel=0.0))
    for x in (-0.08, 0.08):
        ns.boolean(wood, ns.box((0.05, 0.36, 0.3), loc=(x, -0.93, 0), bevel=0.0))
    ns.bevel(wood, width=0.008, segments=1, angle=50)
    C.part(wood, "Wood", dc["body"], "Wood", recolor="cos_body", smooth_angle=45)

    loop = ns.torus(0.075, 0.013, loc=(0, 0.405, -0.01), rot=(0, 90, 0), major_segs=10, minor_segs=4)
    C.part(loop, "Loop", "#6B4A35", "SmoothPlastic", smooth_angle=60)

    def top(x, y):
        # top surface height of the blade near the tip (thickness tapers linearly)
        for (y0, _, t0), (y1, _, t1) in zip(STATIONS, STATIONS[1:]):
            if y1 <= y <= y0:
                return (t0 + (t1 - t0) * (y0 - y) / (y0 - y1)) / 2
        return STATIONS[-1][2] / 2
    # one toasted band along the slanted tip edge
    band = []
    for i in range(9):
        x = -0.2 + 0.4 * i / 8
        band.append((x, -1.31 - TIP_SLANT * x / 0.22 + 0.02 + 0.012 * math.sin(i * 1.7)))
    for i in range(8, -1, -1):
        x = -0.2 + 0.4 * i / 8
        band.append((x, -1.20 - TIP_SLANT * x / 0.22 + 0.025 * math.sin(i * 2.3 + 1)))
    verts = [(x, y, top(x, y) + 0.003) for x, y in band]
    sc = C.mesh_obj("Scorch", verts, [tuple(range(len(verts)))], recalc=False, dedupe=0)
    sc.data.update()
    if sc.data.polygons[0].normal.z < 0:
        sc.data.polygons[0].flip()
    scorch = [sc]
    C.part(scorch, "Scorch", "#6A4326", "Wood", smooth_angle=None)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Spatula_Wooden", "Spatula")
