"""Review render (not an asset): Shop_WallCorner | Shop_Wall | Shop_WallWindow | Shop_WallDoorway
(+ Shop_DoorInterior, ajar) | Shop_WallCorner side by side on the 8-stud grid, to check the
modules tile seamlessly. Panels: front 3/4, seam close-up, and the back face (the exterior
side on outside runs) dressed with the "Exterior" back preset.
Output: /home/claude/previews/B_shop/_tiling_test.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402

import Shop_Wall  # noqa: E402
import Shop_WallWindow  # noqa: E402
import Shop_WallDoorway  # noqa: E402
import Shop_WallCorner  # noqa: E402
import Shop_DoorInterior  # noqa: E402

ns = C.ns


def place(build, x, yaw=0.0, local=(0, 0, 0)):
    before = set(bpy.context.scene.objects)
    build()
    m = Matrix.Translation((x, 0, 0)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Translation(local)
    for o in set(bpy.context.scene.objects) - before:
        o.matrix_world = m @ o.matrix_world


def main():
    ns.reset()
    place(Shop_WallCorner.build, -12)
    place(Shop_Wall.build, -8)
    place(Shop_WallWindow.build, 0)
    place(Shop_WallDoorway.build, 8)
    place(Shop_DoorInterior.build, 8 - 2.5, yaw=-65)
    place(Shop_WallCorner.build, 12)
    pdir = os.path.join(C.ns.REPO, "..", "previews", C.BATCH)
    front = os.path.join(pdir, "_tiling_front.png")
    back = os.path.join(pdir, "_tiling_back.png")
    C.render_views(front, [((-9, -27, 7.5), (0.5, 0, 5.2), 30),
                           ((-2.2, -5.5, 3.0), (-4.2, 0, 2.2), 28)], res=(1024, 640), samples=24)
    # back face = exterior on outside runs: show it with the "Exterior" back preset
    for o in ns._tagged_objects():
        col = C.BACK_PRESETS["Exterior"].get(o.get("ns_role"))
        if col:
            o.data.materials.clear()
            o.data.materials.append(ns.material(col, o["ns_material"]))
    for o in list(bpy.data.objects):
        if o.name.startswith("Floor"):
            bpy.data.objects.remove(o, do_unlink=True)
    C.render_views(back, [((10, 26, 7.5), (0.5, 0, 5.2), 30)], res=(1024, 640), samples=24)
    from PIL import Image
    a, b = Image.open(front), Image.open(back)
    combo = Image.new("RGB", (a.width + b.width, a.height))
    combo.paste(a, (0, 0))
    combo.paste(b, (a.width, 0))
    out = os.path.join(pdir, "_tiling_test.png")
    combo.save(out)
    os.remove(front)
    os.remove(back)
    print("tiling test:", os.path.abspath(out))


if __name__ == "__main__":
    main()
