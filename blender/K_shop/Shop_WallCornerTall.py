"""Shop_WallCornerTall — 1.5 x 1.5 x 20 corner column for the 20-tall dining room grid nodes.

(Extra to brief S1: the 12-tall Shop_WallCorner stops at 12, leaving the corner seams and a
0.5 x 0.5 shaft open from 12 to 20 where tall modules meet.) Same idea as Shop_WallCorner:
placed on an 8-stud grid node where tall modules meet (outside / inside corners, T-joins,
free ends, or where a tall module meets a 12-tall module + Shop_WallUpper), overlapping
the module ends by 0.75 and standing 0.25 proud of the wall faces. The dressing wraps all
four faces with the same roles: baseboard, tiles, checker band, chrome chair rail, upper
wall, pinstripes (9.62 / 9.86), the chrome frieze ring at 12 and the crown at the top
(19.45 .. 20). Stainless corner guards up to the checker band. Collision: Core.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
S = C.S
HW = 0.75  # half width
H = C.TALL_H


def face_set():
    """Flat dressing for the -Y face. Skins run past the +X end so each corner is covered by
    exactly one face once the set is rotated four times (as in Shop_WallCorner)."""
    d = S.wainscot([(-HW, HW)], face_y=-HW, with_base=False)
    d.pop("rail")
    d["grout"] = [ns.box((2 * HW + 0.03, 0.03, C.CHECK_TOP - C.BASE_TOP),
                         loc=(0.015, -HW - 0.015, (C.BASE_TOP + C.CHECK_TOP) / 2), bevel=0.0)]
    d["check_light"] = [ns.box((2 * HW + 0.08, 0.05, C.CHECK_TOP - C.TILE_TOP),
                               loc=(0.04, -HW - 0.055, (C.TILE_TOP + C.CHECK_TOP) / 2), bevel=0.0)]
    top = C.TALL_CROWN_Z + 0.05
    d["upper"] = [ns.box((2 * HW + 0.03, 0.03, top - C.CHECK_TOP),
                         loc=(0.015, -HW - 0.015, (C.CHECK_TOP + top) / 2), bevel=0.0)]
    return d


def rings():
    """Mitred trims that wrap the column."""
    out = {"base": [S.square_ring(S.baseboard_profile(-HW, proud=0.13), HW)],
           "rail": [S.square_ring(S.chair_rail_profile(-HW - 0.03, C.RAIL_Z), HW),
                    S.square_ring(S.chair_rail_profile(-HW - 0.03, C.FRIEZE_Z, h=0.24, proud=0.1), HW)],
           "crown": [S.square_ring(S.crown_profile(-HW - 0.03, C.TALL_CROWN_Z, H), HW)],
           "stripe": []}
    for zc, h in ((C.STRIPE_Z[0], 0.13), (C.STRIPE_Z[1], 0.07)):
        pts = C.fillet([(-HW - 0.03, zc - h / 2), (-HW - 0.07, zc - h / 2), (-HW - 0.07, zc + h / 2),
                        (-HW - 0.03, zc + h / 2)], [0, 0.02, 0.02, 0], 1)
        out["stripe"].append(S.square_ring(pts, HW))
    return out


def build():
    core = ns.box((2 * HW, 2 * HW, H), loc=(0, 0, H / 2), bevel=0.0)
    ns.tag(core, "Core", C.CREAM_SHADE, recolor="wall_back", can_collide=True)
    merged = {}
    for k in range(4):
        d = face_set()
        for key, objs in d.items():
            for o in objs:
                ns.apply_all(o)
                o.rotation_euler = (0, 0, math.radians(90 * k))
                ns.apply_all(o)
                merged.setdefault(key, []).append(o)
    for key, objs in rings().items():
        merged.setdefault(key, []).extend(objs)
    C.tag_wall_set(merged)
    guards = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            pts = [(0, 0), (0.3, 0), (0.3, 0.05), (0.05, 0.05), (0.05, 0.3), (0, 0.3)]
            pts = [(sx * (HW + 0.085) - sx * x, sy * (HW + 0.085) - sy * y)
                   for x, y in C.fillet(pts, [0, 0.02, 0.02, 0.02, 0.02, 0.02], 1)]
            guards.append(C.prism(pts, "z", 0.5, C.CHECK_TOP))
    C.part(guards, "CornerGuard", C.STAINLESS, "Metal", smooth_angle=40)


META = dict(C.wall_presets_meta(), module="wall_corner", grid=8, size=[1.5, 20, 1.5], collider="Core", height=20,
            placement="pivot on an 8-stud grid node (wall line intersection), bottom")

if __name__ == "__main__":
    C.run(build, "Shop_WallCornerTall", pivot=(0, 0, 0), meta=META)
