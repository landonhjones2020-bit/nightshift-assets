"""Shop_Wall — plain 8 x 12 x 1 interior wall module (warm cream over a seafoam tile wainscot).

Front (-Y) = room side: dark baseboard, tile field, black/white checker band, chrome chair
rail at 3.5 (same line as the window sill), cream upper wall, brand pinstripe and a crown.
Back (+Y): plain shade with a baseboard. Every trim runs edge to edge with flat ends so
modules butt seamlessly on the 8-stud grid; Shop_WallCorner columns cover grid nodes.
Collision: the Core slab only (Box fidelity = the whole module).
Recolour roles (wall_upper, wall_tile, ...) + meta.recolor_presets dress the same module
for the kitchen, dining room, freezer, basement and restroom.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
X0, X1 = -C.WALL_W / 2, C.WALL_W / 2


def build(xoff=0.0):
    core = ns.box((C.WALL_W, C.WALL_T, C.WALL_H), loc=(0, 0, C.WALL_H / 2), bevel=0.0)
    ns.tag(core, "Core", C.CREAM_SHADE, "SmoothPlastic", recolor="wall_back", can_collide=True)
    d = C.wainscot([(X0, X1)])
    d["upper"] = [C.skin(X0, X1, C.CHECK_TOP, C.CROWN_Z + 0.05)]
    d["crown"] = [C.crown(X0, X1)]
    d["stripe"] = C.stripes(X0, X1)
    d["back"] = C.back_trim([(X0, X1)])
    C.tag_wall_set(d)


META = dict(C.wall_presets_meta(), module="wall", grid=8,
            size=[8, 12, 1], collider="Core",
            placement="pivot on the wall centre line, bottom; ends on 8-stud grid nodes; room side = LookVector")

if __name__ == "__main__":
    C.run(build, "Shop_Wall", pivot=(0, 0, 0), meta=META)
