"""_view — close-up review renders for P_plaza generators (dev tool, exports nothing).

    bpyenv/bin/python nightshift-assets/blender/P_plaza/_view.py <Asset> "cx,cy,cz,dist,yaw,pitch[,lens]" ...

Builds the asset with its generator's build(), then renders each view (camera `dist` studs
from the look-at point, yaw 0 = from the front (-Y), pitch up from horizontal, lens mm default
50) side by side into previews/P_plaza/_checks/<Asset>_views.png. NS_DUSK=1 uses the J_lobby
dusk lighting (Neon glowing, purple sky) instead of the studio preview lights.
"""
import importlib.util
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns


def main():
    asset = sys.argv[1]
    specs = [tuple(float(x) for x in s.split(",")) for s in sys.argv[2:]]
    spec = importlib.util.spec_from_file_location("gen", os.path.join(os.path.dirname(os.path.abspath(__file__)), asset + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ns.reset()
    mod.build()
    from PIL import Image
    views = []
    for s in specs:
        cx, cy, cz, dist, yaw, pitch = s[:6]
        lens = s[6] if len(s) > 6 else 50.0
        y, p = math.radians(yaw), math.radians(pitch)
        off = Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p))) * dist
        views.append((tuple(Vector((cx, cy, cz)) + off), (cx, cy, cz), lens))
    out_dir = os.path.join(C.PREVIEWS, "_checks")
    os.makedirs(out_dir, exist_ok=True)
    if os.environ.get("NS_DUSK") == "1":
        out = C.J.render_dusk(asset, views, res=(448, 448), samples=12, tag="view")
        print(f"[{asset}] views: {os.path.normpath(out)}")
        return
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    bpy.ops.mesh.primitive_plane_add(size=max((hi - lo).length * 8, 40), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z - 0.002))
    fl = bpy.context.active_object
    fl.name = "Floor"
    fl.data.materials.append(ns.material("#3A3B42"))
    ns._setup_render(448, 12)
    paths = []
    for i, (cl, at, lens) in enumerate(views):
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cd = bpy.data.cameras.new("PreviewCam")
        cd.lens = lens
        cd.clip_start = 0.01
        cam = bpy.data.objects.new("PreviewCam", cd)
        bpy.context.scene.collection.objects.link(cam)
        cam.location = Vector(cl)
        cam.rotation_euler = (Vector(at) - Vector(cl)).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.camera = cam
        d = (Vector(at) - Vector(cl)).length
        c = Vector(at)
        k = math.atan2(cl[0] - at[0], -(cl[1] - at[1]))
        ns._light("Key", "AREA", c + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * d, 60 * d ** 2 / 9, size=d * 0.6, target=c)
        ns._light("Fill", "AREA", c + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3)) * d, 22 * d ** 2 / 9, size=d * 0.8, target=c)
        ns._light("Rim", "AREA", c + Vector((-math.sin(k), math.cos(k), 0.8)) * d, 30 * d ** 2 / 9, size=d * 0.4, target=c)
        p = os.path.join(out_dir, f"{asset}_v{i}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    ims = [Image.open(p).convert("RGB") for p in paths]
    combo = Image.new("RGB", (sum(im.width for im in ims), max(im.height for im in ims)))
    x = 0
    for im in ims:
        combo.paste(im, (x, 0))
        x += im.width
    out = os.path.join(out_dir, f"{asset}_views.png")
    combo.save(out)
    for p in paths:
        os.remove(p)
    print(f"[{asset}] views: {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
