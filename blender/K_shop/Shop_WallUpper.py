"""Shop_WallUpper — 8 x 8 x 1 upper wall band that sits ON TOP of a 12-tall wall module.

Used where the 20-stud dining room is taller than the next room: above the counter line and
the restroom walls. Pivot = bottom of the wall centre line, i.e. y = 12 in the map, right on
the lower module's top. Front (-Y, the dining room): upper wall skin (role wall_upper) from
the lower module's crown up to the crown moulding at the top (7.45 .. 8 -> 19.45 .. 20 in
the map, the same crown as the tall modules). Back (+Y): plain Core (role wall_back), which
the back presets recolour (it is a facade above the kitchen / restroom roofs).
Collision: Core.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
X0, X1 = -C.WALL_W / 2, C.WALL_W / 2
H = C.UPPER_H
CROWN0 = H - (C.TALL_H - C.TALL_CROWN_Z)   # 7.45


def build():
    core = ns.box((C.WALL_W, C.WALL_T, H), loc=(0, 0, H / 2), bevel=0.0)
    ns.tag(core, "Core", C.CREAM_SHADE, "SmoothPlastic", recolor="wall_back", can_collide=True)
    d = {"upper": [C.skin(X0, X1, 0.0, CROWN0 + 0.05)], "crown": [C.crown_tall(X0, X1, z0=CROWN0, z1=H)]}
    C.tag_wall_set(d)


META = dict(C.wall_presets_meta(), module="wall_upper", grid=8, size=[8, 8, 1], collider="Core", height=8,
            mount_height=12,
            placement="sits ON TOP of a 12-tall wall module: pivot on the wall centre line at the lower module's "
                      "top (y = 12); room side (front, crown) = LookVector")

if __name__ == "__main__":
    C.run(build, "Shop_WallUpper", pivot=(0, 0, 0), meta=META)
