"""Scale/style comparison of the creature set (review aid, exports nothing).

Builds every creature rig of batch E (plus the gate Nibbler, read-only) in one scene, in a
row, each with a 5-stud reference figure (R15 height) beside it, and renders an
orthographic front-3/4 line-up to previews/E_creatures/_scale_compare.png. Creatures are
shown in their rest pose at their real heights: the Shiver hangs from a 12-stud ceiling
beam; the Patron's pivot is on the ground with its face pressed to a 12-stud wall line
(the ground hides its lower face, as in game).
"""
import importlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gate"))
import _common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

LINEUP = [  # (module, x position, y offset of the rig, label)
    ("Creature_Nibbler", 0.0, 0.0, "Nibbler"),
    ("Creature_Paperface", 5.0, 0.0, "Paperface"),
    ("Creature_MrUsual", 11.5, 0.0, "MrUsual"),
    ("Creature_LightsOut", 19.0, 0.0, "LightsOut"),
    ("Creature_Shiver", 26.0, 0.0, "Shiver"),
    ("Creature_Patron", 52.0, 10.6, "Patron"),
]


def main():
    ns.reset()
    built = []
    for mod_name, x, y, label in LINEUP:
        before = set(bpy.data.objects)
        mod = importlib.import_module(mod_name)
        out = mod.build()
        arm = out["arm"]
        arm.data.pose_position = "REST"
        arm.location = (x, y, 0.0)
        built.append((label, x, set(bpy.data.objects) - before))
        ref_x = x + {"Nibbler": 1.6, "Paperface": 1.8, "MrUsual": 2.4, "LightsOut": 2.2, "Shiver": 2.3,
                     "Patron": -19.5}[label]
        r = C._ref_capsule((ref_x, 0.0, 0.0), name=f"Ref5_{label}")
        r.data.materials.clear()
        r.data.materials.append(ns.material("#9A9AA6"))
    bpy.context.view_layer.update()
    # ceiling beam for the Shiver, wall line for the Patron
    beam = ns.box((3.0, 1.0, 0.3), loc=(26.0, 0.0, 12.15), bevel=0.0, name="Beam")
    beam.data.materials.append(ns.material("#5A6670"))
    wall = ns.box((40.0, 0.4, 12.0), loc=(52.0, -0.2, 6.0), bevel=0.0, name="Wall")
    wall.data.materials.append(ns.material("#2A3448", transparency=0.75))
    bpy.ops.mesh.primitive_plane_add(size=200, location=(30, 0, 0))
    fl = bpy.context.active_object
    fl.data.materials.append(ns.material("#3A3B42"))

    sc = bpy.context.scene
    ns._setup_render(512, 24, transparent=False)
    sc.render.resolution_x, sc.render.resolution_y = 2400, 760
    cd = bpy.data.cameras.new("Cmp")
    cd.type = "ORTHO"
    cd.ortho_scale = 76.0
    cam = bpy.data.objects.new("Cmp", cd)
    sc.collection.objects.link(cam)
    yaw, pitch = math.radians(-12), math.radians(6)
    ctr = Vector((30.0, 0.0, 9.0))
    cam.location = ctr + Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch))) * 120
    cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.clip_end = 400
    sc.camera = cam
    ns._light("Key", "SUN", (0, -50, 60), 3.5, target=(30, 0, 0))
    ns._light("Fill", "SUN", (60, -40, 20), 1.2, target=(30, 0, 0))
    out = os.path.join(C.PREV_DIR, "_scale_compare.png")
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    # label strip
    from PIL import Image, ImageDraw
    im = Image.open(out).convert("RGB")
    d = ImageDraw.Draw(im)
    W = im.width
    for label, x, _ in built:
        # ortho: screen x ~ (world x - ctr.x) * cos(yaw) / scale
        sx = W / 2 + (x - ctr.x) * math.cos(yaw) / cd.ortho_scale * W
        d.text((sx - 24, 8), label, fill=(240, 240, 240))
    d.text((8, im.height - 18), "grey capsules = 5-stud R15 reference; Shiver hangs from a 12-stud ceiling beam; "
                                "Patron face pressed to the window wall (translucent), ground hides its lower face",
           fill=(220, 220, 220))
    im.save(out)
    print("scale compare:", out)


if __name__ == "__main__":
    main()
