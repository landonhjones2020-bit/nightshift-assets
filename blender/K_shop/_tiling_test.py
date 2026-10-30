"""Review render (not an asset): the K_shop tall modules on the 8-stud grid next to the
existing B_shop modules, dressed with the "Dining" preset (front) / "Exterior" (back):

  WallCornerTall | WallTall | WindowTall | DoorwayTall (+ B:Shop_DoorFront) | WindowWide (16) |
  WindowTall | B:Shop_Wall + WallUpper stacked | WallCornerTall

Panels: front overview, seam close-up at the 12-stud line, stacked-wall junction close-up,
and the back (exterior) overview. Output: /home/claude/previews/K_shop/_tiling_test.png
(every single render <= 512 px).
"""
import importlib.util
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402

import Shop_WallTall  # noqa: E402
import Shop_WallWindowTall  # noqa: E402
import Shop_WallWindowWide  # noqa: E402
import Shop_WallDoorwayTall  # noqa: E402
import Shop_WallUpper  # noqa: E402
import Shop_WallCornerTall  # noqa: E402

ns = C.ns
_B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "B_shop")


def load_bshop(name):
    """Import a B_shop generator with ITS _common (both batches call theirs `_common`)."""
    saved = sys.modules.get("_common")
    sys.modules["_common"] = C.S
    try:
        spec = importlib.util.spec_from_file_location("bshop_" + name, os.path.join(_B, name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        if saved is not None:
            sys.modules["_common"] = saved
    return mod


def place(build, x, yaw=0.0, local=(0, 0, 0), z=0.0):
    before = set(bpy.context.scene.objects)
    build()
    m = Matrix.Translation((x, 0, z)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Translation(local)
    for o in set(bpy.context.scene.objects) - before:
        o.matrix_world = m @ o.matrix_world


def dress(front="Dining", back="Interior"):
    for o in ns._tagged_objects():
        role = o.get("ns_role")
        col = C.WALL_PRESETS[front].get(role) or C.BACK_PRESETS[back].get(role)
        if col:
            o.data.materials.clear()
            o.data.materials.append(ns.material(col, o["ns_material"], o["ns_transparency"]))


def main():
    B_Wall, B_Corner, B_Door = load_bshop("Shop_Wall"), load_bshop("Shop_WallCorner"), load_bshop("Shop_DoorFront")
    ns.reset()
    place(Shop_WallCornerTall.build, -24)
    place(Shop_WallTall.build, -20)
    place(Shop_WallWindowTall.build, -12)
    place(Shop_WallDoorwayTall.build, -4)
    place(B_Door.build, -4 - 2.5, yaw=-70)
    place(Shop_WallWindowWide.build, 8)
    place(Shop_WallWindowTall.build, 20)
    place(B_Wall.build, 28)
    place(Shop_WallUpper.build, 28, z=12.0)
    place(Shop_WallCornerTall.build, 32)
    dress("Dining", "Interior")
    pdir = C.PREVIEWS
    os.makedirs(pdir, exist_ok=True)
    front = os.path.join(pdir, "_tiling_front.png")
    close = os.path.join(pdir, "_tiling_close.png")
    back = os.path.join(pdir, "_tiling_back.png")
    C.render_views(front, [((-1, -62, 11.0), (4, 0, 9.5), 30)], res=(512, 320), samples=16)
    for o in list(bpy.data.objects):
        if o.name.startswith("Floor"):
            bpy.data.objects.remove(o, do_unlink=True)
    C.render_views(close, [((-10.5, -10.5, 9.0), (-8, 0, 10.6), 30), ((29.0, -13, 13.5), (31.5, 0, 12.0), 30),
                           ((-3.0, -16, 6.5), (-4, 0, 9.5), 30), ((-19.5, -11, 8.0), (-23.5, 0, 10.5), 26)],
                   res=(256, 320), samples=16)
    for o in list(bpy.data.objects):
        if o.name.startswith("Floor"):
            bpy.data.objects.remove(o, do_unlink=True)
    dress("Dining", "Exterior")
    C.render_views(back, [((9, 62, 11.0), (4, 0, 9.5), 30)], res=(512, 320), samples=16)
    from PIL import Image
    a, b, c = Image.open(front), Image.open(close), Image.open(back)
    combo = Image.new("RGB", (max(a.width + c.width, b.width), a.height + b.height), (20, 20, 24))
    combo.paste(a, (0, 0))
    combo.paste(c, (a.width, 0))
    combo.paste(b, (0, a.height))
    out = os.path.join(pdir, "_tiling_test.png")
    combo.save(out)
    for p in (front, close, back):
        os.remove(p)
    print("tiling test:", os.path.abspath(out))


if __name__ == "__main__":
    main()
