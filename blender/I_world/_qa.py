"""_qa — mesh QA for the I_world batch (review tool, exports nothing).

For each asset generator: build it, then
  * inward faces: cast a ray from every face along its normal; hitting the BACK of a face
    of the same object first means the face points into its own closed mesh (it would
    vanish in Roblox, which draws single-sided).
  * z-fighting: a face whose centre projects inside another face lying in (nearly) the
    same plane (< 0.006 studs) with the same facing.
  * a back-face-culled render (back faces transparent, as Roblox draws them) from four
    angles -> previews/I_world/_qa/<asset>_qa.png
Usage: bpyenv/bin/python blender/I_world/_qa.py [Asset ...]   (default: every World_*.py)
"""
import importlib.util
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

ns = C.ns
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(C.PREVIEWS, "_qa")


def check(asset):
    """Return (inward, zfight) lists for the tagged objects currently in the scene."""
    objs = ns._tagged_objects()
    bm = bmesh.new()
    lay = bm.faces.layers.int.new("own")
    isl = bm.faces.layers.int.new("isl")
    dg = bpy.context.evaluated_depsgraph_get()
    names = []
    next_island = 0
    for k, o in enumerate(objs):
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), depsgraph=dg)
        me.transform(o.matrix_world)
        tmp = bmesh.new()
        tmp.from_mesh(me)
        bmesh.ops.remove_doubles(tmp, verts=tmp.verts[:], dist=1e-5)
        bmesh.ops.triangulate(tmp, faces=tmp.faces[:])
        tmp.faces.ensure_lookup_table()
        tmp.verts.index_update()
        # connected shells (faces sharing vertices)
        comp = {}
        for f0 in tmp.faces:
            if f0.index in comp:
                continue
            stack = [f0]
            comp[f0.index] = next_island
            while stack:
                f = stack.pop()
                for v in f.verts:
                    for g in v.link_faces:
                        if g.index not in comp:
                            comp[g.index] = next_island
                            stack.append(g)
            next_island += 1
        vmap = [bm.verts.new(v.co) for v in tmp.verts]
        for f in tmp.faces:
            try:
                nf = bm.faces.new([vmap[v.index] for v in f.verts])
                nf[lay] = k
                nf[isl] = comp[f.index]
            except ValueError:
                pass
        tmp.free()
        bpy.data.meshes.remove(me)
        names.append(o.name)
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    tree = BVHTree.FromBMesh(bm)
    inward, zfight = [], []
    faces = bm.faces
    for f in faces:
        n = f.normal
        if n.length < 0.5 or f.calc_area() < 1e-6:
            continue
        c = f.calc_center_median()
        hit = tree.ray_cast(c + n * 1e-3, n, 50.0)
        if hit[0] is not None:
            hf = faces[hit[2]]
            if hf[isl] == f[isl] and hit[1].dot(n) > 0.2 and hit[3] < 50.0:
                inward.append((names[f[lay]], tuple(round(x, 2) for x in c), round(hit[3], 3)))
        for loc, nrm, idx, dist in tree.find_nearest_range(c, 0.006):
            if idx == f.index:
                continue
            g = faces[idx]
            if g.normal.dot(n) < 0.99:
                continue
            pd = abs((c - g.verts[0].co).dot(g.normal))
            if pd < 0.006 and abs(dist - pd) < 1e-4:
                if set(v.index for v in g.verts) & set(v.index for v in f.verts) and pd < 1e-5:
                    continue
                zfight.append((names[f[lay]], names[g[lay]], tuple(round(x, 2) for x in c), round(pd, 4)))
                break
    bm.free()
    return inward, zfight


def culled_render(asset, res=256, samples=6):
    from PIL import Image
    undo = []
    for m in bpy.data.materials:
        if not m.use_nodes or m.node_tree is None:
            continue
        nt = m.node_tree
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out is None or not out.inputs["Surface"].links:
            continue
        src = out.inputs["Surface"].links[0].from_socket
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(geo.outputs["Backfacing"], mix.inputs[0])
        nt.links.new(src, mix.inputs[1])
        nt.links.new(tr.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        undo.append((nt, out, src, [geo, tr, mix]))
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    ns._setup_render(res, samples)
    bpy.context.scene.world.node_tree.nodes.get("Background").inputs[0].default_value = (0.9, 0.1, 0.6, 1)  # magenta
    paths = []
    for i, (yaw, pitch) in enumerate(((-35, 25), (145, 20), (60, 4), (-120, -12))):
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cam, ctr, dist = ns._camera_fit(lo, hi, yaw, pitch)
        k = math.radians(yaw)
        ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * dist,
                  60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), -0.3)) * dist,
                  30 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        p = os.path.join(OUT, f"{asset}_qa{i}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    ns._clear_rig()
    for nt, out, src, nodes in undo:
        for n in nodes:
            nt.nodes.remove(n)
        nt.links.new(src, out.inputs["Surface"])
    ims = [Image.open(p).convert("RGB") for p in paths]
    combo = Image.new("RGB", (res * len(ims), res))
    for i, im in enumerate(ims):
        combo.paste(im, (i * res, 0))
    path = os.path.join(OUT, f"{asset}_qa.png")
    combo.save(path)
    for p in paths:
        os.remove(p)
    return path


def main(assets):
    os.makedirs(OUT, exist_ok=True)
    for asset in assets:
        spec = importlib.util.spec_from_file_location(asset, os.path.join(HERE, f"{asset}.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ns.reset()
        mod.build()
        inward, zf = check(asset)
        print(f"[QA {asset}] inward faces: {len(inward)}  z-fight faces: {len(zf)}")
        for x in inward[:8]:
            print("    inward", x)
        for x in zf[:8]:
            print("    zfight", x)
        if os.environ.get("QA_RENDER", "1") == "1":
            print(f"[QA {asset}] render: {culled_render(asset)}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        args = sorted(f[:-3] for f in os.listdir(HERE) if f.startswith("World_") and f.endswith(".py"))
    main(args)
