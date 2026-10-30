"""Review render (not an asset): a corner of the new double-height dining room built from the
K_shop pieces at their intended heights, Dining preset, with a 4.1-stud avatar block for
scale: tall windows + picture window along the front, the counter wall (B:Shop_Wall +
Shop_WallUpper) carrying Shop_BigNeonSign at ~12.75, the clock and posters, the ceiling fan
and tall pendants hanging from 20, plant / specials board / wait sign / gumball machine on
the floor and the dessert case on a counter-height block.
Output: /home/claude/previews/K_shop/_room_test.png (each render <= 512 px).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402

import _tiling_test as T  # noqa: E402
import Shop_WallTall, Shop_WallWindowTall, Shop_WallWindowWide, Shop_WallUpper, Shop_WallCornerTall  # noqa: E402,E401
import Shop_BigNeonSign, Shop_WallClock, Shop_PosterA, Shop_PosterB, Shop_PosterC  # noqa: E402,E401
import Shop_CeilingFan, Shop_TallPendant, Shop_PottedPlant, Shop_SpecialsBoard  # noqa: E402,E401
import Shop_WaitSign, Shop_GumballMachine, Shop_DessertCase  # noqa: E402,E401

ns = C.ns


def put(build, x, y, z=0.0, yaw=0.0):
    before = set(bpy.context.scene.objects)
    build()
    m = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
    for o in set(bpy.context.scene.objects) - before:
        o.matrix_world = m @ o.matrix_world


def main():
    B_Wall = T.load_bshop("Shop_Wall")
    ns.reset()
    # Blender frame for this test: room interior y > 0; front wall on y = 0 (room side = +Y, so modules
    # turn 180 deg); counter wall on y = 24 facing -Y (toward the front wall)
    put(Shop_WallCornerTall.build, -16, 0)
    put(Shop_WallWindowTall.build, -12, 0, yaw=180)
    put(Shop_WallWindowTall.build, -4, 0, yaw=180)
    put(Shop_WallWindowWide.build, 8, 0, yaw=180)
    put(Shop_WallTall.build, -16, 4, yaw=90)
    put(Shop_WallTall.build, -16, 12, yaw=90)
    put(Shop_WallTall.build, -16, 20, yaw=90)
    put(Shop_WallCornerTall.build, -16, 24)
    for x in (-12, -4, 4, 12):
        put(B_Wall.build, x, 24)
        put(Shop_WallUpper.build, x, 24, z=12.0)
    T.dress("Dining", "Interior")
    put(Shop_BigNeonSign.build, 0, 24 - 0.5, z=12.75)
    put(Shop_WallClock.build, -15.5, 12, z=13.0, yaw=90)
    put(Shop_PosterA.build, -15.5, 7, z=4.6, yaw=90)
    put(Shop_PosterB.build, -15.5, 17, z=4.6, yaw=90)
    put(Shop_PosterC.build, -8, 24 - 0.5, z=5.0)
    put(Shop_CeilingFan.build, 0, 12, z=20.0)
    for x in (-8, 8):
        put(Shop_TallPendant.build, x, 4.5, z=20.0)
    put(Shop_PottedPlant.build, -13.5, 2.2)
    put(Shop_SpecialsBoard.build, -6.5, 8, yaw=-20)
    put(Shop_WaitSign.build, -10, 9)
    put(Shop_GumballMachine.build, -13.8, 21.5)
    counter = ns.box((16, 2.5, 3.0), loc=(0, 22.25, 1.5), bevel=0.05)
    ns.tag(counter, "CounterBlock", "#E9E2D3")
    put(Shop_DessertCase.build, 4, 22.25, z=3.0)
    avatar = ns.box((1.6, 0.8, 4.1), loc=(-9, 5, 2.05), bevel=0.2)
    ns.tag(avatar, "AvatarBlock", "#E8502A")
    pdir = C.PREVIEWS
    a = os.path.join(pdir, "_room_a.png")
    b = os.path.join(pdir, "_room_b.png")
    C.render_views(a, [((12, 3, 6.0), (-5, 20, 10.5), 17)], res=(512, 384), samples=16, world=0.6, light_scale=0.35)
    for o in list(bpy.data.objects):
        if o.name.startswith("Floor"):
            bpy.data.objects.remove(o, do_unlink=True)
    C.render_views(b, [((7, 19, 6.0), (-15, 7, 8.5), 17)], res=(512, 384), samples=16, world=0.6, light_scale=0.35)
    from PIL import Image
    ia, ib = Image.open(a), Image.open(b)
    combo = Image.new("RGB", (ia.width + ib.width, ia.height))
    combo.paste(ia, (0, 0))
    combo.paste(ib, (ia.width, 0))
    out = os.path.join(pdir, "_room_test.png")
    combo.save(out)
    os.remove(a)
    os.remove(b)
    print("room test:", os.path.abspath(out))


if __name__ == "__main__":
    main()
