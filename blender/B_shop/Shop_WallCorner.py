"""Shop_WallCorner — 1.5 x 1.5 x 12 corner column for the wall grid nodes.

Placed on every 8-stud grid node where wall modules meet (outside/inside corners, T-joins,
free wall ends). It overlaps the module ends by 0.75 and stands 0.25 proud of the wall
faces, so it hides the seams. The wall dressing (baseboard, tiles, checker band, chrome
rail, cream upper, pinstripe, crown) wraps all four faces with the same recolour roles.
Collision: Core.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
HW = 0.75  # half width


def face_set():
    """Flat dressing for the -Y face (tiles, checker, skins). Skins run 0.08 past the +X end
    so each corner is covered by exactly one face once the set is rotated four times."""
    d = C.wainscot([(-HW, HW)], face_y=-HW, with_base=False)
    d.pop("rail")
    d["grout"] = [ns.box((2 * HW + 0.03, 0.03, C.CHECK_TOP - C.BASE_TOP),
                         loc=(0.015, -HW - 0.015, (C.BASE_TOP + C.CHECK_TOP) / 2), bevel=0.0)]
    d["check_light"] = [ns.box((2 * HW + 0.08, 0.05, C.CHECK_TOP - C.TILE_TOP),
                               loc=(0.04, -HW - 0.055, (C.TILE_TOP + C.CHECK_TOP) / 2), bevel=0.0)]
    d["upper"] = [ns.box((2 * HW + 0.03, 0.03, C.CROWN_Z + 0.05 - C.CHECK_TOP),
                         loc=(0.015, -HW - 0.015, (C.CHECK_TOP + C.CROWN_Z + 0.05) / 2), bevel=0.0)]
    return d


def rings():
    """Mitred trims that wrap the column."""
    out = {"base": [C.square_ring(C.baseboard_profile(-HW, proud=0.13), HW)],
           "rail": [C.square_ring(C.chair_rail_profile(-HW - 0.03, C.RAIL_Z), HW)],
           "crown": [C.square_ring(C.crown_profile(-HW - 0.03, C.CROWN_Z), HW)],
           "stripe": []}
    for zc, h in ((C.STRIPE_Z[0], 0.13), (C.STRIPE_Z[1], 0.07)):
        pts = C.fillet([(-HW - 0.03, zc - h / 2), (-HW - 0.07, zc - h / 2), (-HW - 0.07, zc + h / 2),
                        (-HW - 0.03, zc + h / 2)], [0, 0.02, 0.02, 0], 1)
        out["stripe"].append(C.square_ring(pts, HW))
    return out


def build():
    core = ns.box((2 * HW, 2 * HW, C.WALL_H), loc=(0, 0, C.WALL_H / 2), bevel=0.0)
    ns.tag(core, "Core", C.CREAM_SHADE, recolor="wall_back", can_collide=True)
    merged = {}
    import math
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
    # stainless corner guards on the four vertical edges (kitchen-proofing), up to the rail
    guards = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            pts = [(0, 0), (0.3, 0), (0.3, 0.05), (0.05, 0.05), (0.05, 0.3), (0, 0.3)]
            pts = [(sx * (HW + 0.085) - sx * x, sy * (HW + 0.085) - sy * y) for x, y in C.fillet(pts, [0, 0.02, 0.02, 0.02, 0.02, 0.02], 1)]
            g = C.prism(pts, "z", 0.5, C.CHECK_TOP)
            guards.append(g)
    C.part(guards, "CornerGuard", C.STAINLESS, "Metal", recolor="wall_trim", smooth_angle=40)


META = dict(C.wall_presets_meta(), module="wall_corner", grid=8, size=[1.5, 12, 1.5], collider="Core",
            placement="pivot on an 8-stud grid node (wall line intersection), bottom")

if __name__ == "__main__":
    C.run(build, "Shop_WallCorner", pivot=(0, 0, 0), meta=META)
