"""Shop_WallTall — plain 8 x 20 x 1 wall module for the double-height dining room.

The lower 12 studs are the Shop_Wall dressing, built with the same B_shop helpers (dark
baseboard, seafoam tile field, black/white checker band, chrome chair rail at 3.5, upper
wall, brand pinstripes at 9.62 / 9.86). A slim chrome frieze rail marks the 12-stud line
(level with the tall windows' transom bars and the old crown / kitchen ceiling height),
the upper wall continues to the ceiling and the crown moulding sits at the top
(19.45 .. 20). Back (+Y): plain shade with the standard baseboard + band.
Every trim runs edge to edge with flat ends, so modules butt seamlessly on the 8-stud grid.
Same roles (wall_back, wall_upper, wall_tile, wall_grout, wall_base, wall_stripe,
wall_back_base, wall_back_band) and recolour/back presets as Shop_Wall.
Collision: the Core slab only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
X0, X1 = -C.WALL_W / 2, C.WALL_W / 2
H = C.TALL_H


def build():
    core = ns.box((C.WALL_W, C.WALL_T, H), loc=(0, 0, H / 2), bevel=0.0)
    ns.tag(core, "Core", C.CREAM_SHADE, "SmoothPlastic", recolor="wall_back", can_collide=True)
    d = C.S.wainscot([(X0, X1)])
    d["upper"] = [C.skin(X0, X1, C.CHECK_TOP, C.TALL_CROWN_Z + 0.05)]
    d["crown"] = [C.crown_tall(X0, X1)]
    d["stripe"] = C.stripes(X0, X1)
    d["rail"].append(C.frieze_rail(X0, X1))
    d["back"] = C.S.back_trim([(X0, X1)]) + [C.back_band(X0, X1)]
    C.tag_wall_set(d)


META = dict(C.wall_presets_meta(), module="wall", grid=8, size=[8, 20, 1], collider="Core", height=20,
            placement="pivot on the wall centre line, bottom; ends on 8-stud grid nodes; room side = LookVector")

if __name__ == "__main__":
    C.run(build, "Shop_WallTall", pivot=(0, 0, 0), meta=META)
