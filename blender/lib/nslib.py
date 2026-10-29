"""
nslib — Night Shift at STACKHOUSE shared Blender library.

Every asset generator script imports this module. It provides:
  * scene reset and colour/material helpers (hex sRGB -> Blender linear)
  * chunky, soft-bevelled primitive builders (box, cylinder, sphere, ...)
  * part tagging (which Roblox part a Blender object becomes, its colour/material)
  * the Roblox exporter (mesh JSON in Roblox axes + studs, FBX, manifest entry)
  * preview renders (two angles + 1-stud reference) and icon renders

Conventions (locked by the Phase 1 pipeline gate; see CONVERSION_CONSTANTS):
  * 1 Blender unit = 1 stud.
  * Model the FRONT of every asset facing Blender -Y (what Blender's "Front" view shows).
  * Z is up in Blender.
  * Roblox axes: x_r = -x_b, y_r = z_b, z_r = y_b  (a proper rotation; the front ends up
    facing Roblox -Z, which is CFrame.LookVector).
  * The asset pivot is bottom-centre of the combined bounding box unless the script passes
    an explicit pivot (doors and lids use their hinge).
"""
from __future__ import annotations

import bpy
import bmesh
import hashlib
import json
import math
import os
from mathutils import Matrix, Vector

REPO = os.environ.get("NS_REPO", "/home/claude/nightshift-assets")
RAW_BASE = "https://raw.githubusercontent.com/landonhjones2020-bit/nightshift-assets/main"

# --------------------------------------------------------------------------------------
# Scene / colour helpers
# --------------------------------------------------------------------------------------

def reset() -> None:
    """Start every generator from an empty scene so scripts are re-runnable."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


_MATS: dict[str, bpy.types.Material] = {}

# Rough approximation of how each Roblox material reads, for previews only.
_ROUGHNESS = {
    "SmoothPlastic": 0.45, "Plastic": 0.55, "Metal": 0.3, "DiamondPlate": 0.35,
    "Glass": 0.05, "Neon": 0.5, "Wood": 0.7, "WoodPlanks": 0.75, "Fabric": 0.95,
    "Concrete": 0.9, "Brick": 0.9, "Slate": 0.85, "Foil": 0.25, "Ice": 0.1,
    "Granite": 0.8, "Marble": 0.3, "Pebble": 0.85, "Cobblestone": 0.9, "Asphalt": 0.95,
    "Leather": 0.6, "Rubber": 0.8, "Cardboard": 0.9, "Paper": 0.9, "Ceramic": 0.25,
}


def material(hexcolor: str, roblox_material: str = "SmoothPlastic", transparency: float = 0.0) -> bpy.types.Material:
    key = f"{hexcolor}|{roblox_material}|{transparency}"
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name=f"M_{hexcolor.lstrip('#')}_{roblox_material}")
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    r, g, b = (srgb_to_linear(c) for c in hex_rgb(hexcolor))
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Roughness"].default_value = _ROUGHNESS.get(roblox_material, 0.5)
    if roblox_material in ("Metal", "DiamondPlate", "Foil"):
        bsdf.inputs["Metallic"].default_value = 0.85
    if roblox_material == "Neon":
        bsdf.inputs["Emission Color"].default_value = (r, g, b, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 4.0
    if transparency > 0:
        bsdf.inputs["Alpha"].default_value = max(0.05, 1.0 - transparency)
    m.diffuse_color = (r, g, b, 1.0)
    _MATS[key] = m
    return m


def tag(obj: bpy.types.Object, part: str, color: str, mat: str = "SmoothPlastic", *,
        transparency: float = 0.0, cast_shadow: bool = True, can_collide: bool = False,
        smooth_angle: float | None = 35.0, recolor: str | None = None) -> bpy.types.Object:
    """Mark a Blender object as one Roblox part.

    part          Part name inside the asset (unique per asset, no spaces).
    color         Hex sRGB colour applied as MeshPart.Color in Studio.
    mat           Roblox Enum.Material name.
    smooth_angle  Edges sharper than this angle stay hard; softer ones shade smooth.
                  None = fully faceted (flat) shading.
    recolor       Optional runtime role (e.g. "toast", "tell_flannel") so code can find it.
    """
    obj.name = part
    obj["ns_part"] = part
    obj["ns_color"] = color.upper() if color.startswith("#") else "#" + color.upper()
    obj["ns_material"] = mat
    obj["ns_transparency"] = float(transparency)
    obj["ns_cast_shadow"] = bool(cast_shadow)
    obj["ns_can_collide"] = bool(can_collide)
    obj["ns_smooth_angle"] = -1.0 if smooth_angle is None else float(smooth_angle)
    if recolor:
        obj["ns_role"] = recolor
    obj.data.materials.clear()
    obj.data.materials.append(material(obj["ns_color"], mat, transparency))
    # Same smoothing rule the exporter uses, so previews match what Studio shows.
    _set_sharp_by_angle(obj.data, obj["ns_smooth_angle"])
    return obj


def join(objs: list[bpy.types.Object], name: str) -> bpy.types.Object:
    """Join several meshes into one object (they share a part and colour)."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    obj = bpy.context.active_object
    obj.name = name
    return obj


def apply_all(obj: bpy.types.Object) -> None:
    """Apply modifiers and transforms (used before booleans/joins)."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    for mod in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


# --------------------------------------------------------------------------------------
# Primitive builders — everything gets soft bevels so nothing reads as a default primitive
# --------------------------------------------------------------------------------------

def _finish(obj: bpy.types.Object, loc, rot, bevel: float, bevel_segments: int, bevel_angle: float = 40.0):
    obj.location = Vector(loc)
    obj.rotation_euler = tuple(math.radians(a) for a in rot)
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = bevel_segments
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(bevel_angle)
        mod.profile = 0.5
        mod.use_clamp_overlap = True
    return obj


def box(size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.08, segments=2, name="Box"):
    """Axis-aligned box centred at loc. size = (x, y, z) in studs."""
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = Vector(size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(obj, loc, rot, bevel, segments)


def cyl(radius, depth, loc=(0, 0, 0), rot=(0, 0, 0), verts=16, bevel=0.05, segments=2,
        radius_top=None, name="Cyl"):
    """Cylinder (or cone/frustum with radius_top) along Blender Z, centred at loc."""
    if radius_top is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=radius, radius2=radius_top, depth=depth)
    obj = bpy.context.active_object
    obj.name = name
    return _finish(obj, loc, rot, bevel, segments)


def sphere(radius, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), segs=16, rings=10, name="Sphere"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings, radius=radius)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = Vector(scale)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(obj, loc, rot, 0, 0)


def torus(major, minor, loc=(0, 0, 0), rot=(0, 0, 0), major_segs=20, minor_segs=8, name="Torus"):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                     major_segments=major_segs, minor_segments=minor_segs)
    obj = bpy.context.active_object
    obj.name = name
    return _finish(obj, loc, rot, 0, 0)


def from_bmesh(bm: bmesh.types.BMesh, name: str, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0, segments=2):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return _finish(obj, loc, rot, bevel, segments)


def profile_slab(points2d, thickness, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.04, segments=2, name="Slab"):
    """Extrude a closed 2D outline (x, y in Blender XY plane) upward by `thickness` along Z."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0)) for x, y in points2d]
    face = bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=[face])
    if face.normal.z < 0:
        face.normal_flip()
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, thickness))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return from_bmesh(bm, name, loc, rot, bevel, segments)


def lathe(profile, verts=20, loc=(0, 0, 0), rot=(0, 0, 0), name="Lathe"):
    """Revolve a profile [(radius, z), ...] (bottom to top) around Blender Z."""
    bm = bmesh.new()
    rings = []
    for i in range(verts):
        a = 2 * math.pi * i / verts
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
    for i in range(verts):
        r0, r1 = rings[i], rings[(i + 1) % verts]
        for j in range(len(profile) - 1):
            quad = [r0[j], r1[j], r1[j + 1], r0[j + 1]]
            if len({v.co.to_tuple(5) for v in quad}) >= 3:
                try:
                    bm.faces.new(quad)
                except ValueError:
                    pass
    # cap bottom/top if radius > 0
    if profile[0][0] > 1e-4:
        bm.faces.new([rings[i][0] for i in reversed(range(verts))])
    if profile[-1][0] > 1e-4:
        bm.faces.new([rings[i][-1] for i in range(verts)])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return from_bmesh(bm, name, loc, rot)


def jitter(obj, amount=0.02, seed=1, axes=(1, 1, 1)):
    """Small deterministic vertex noise for organic shapes (lettuce, bread crust)."""
    import random
    rnd = random.Random(seed)
    apply_all(obj)
    for v in obj.data.vertices:
        v.co.x += rnd.uniform(-amount, amount) * axes[0]
        v.co.y += rnd.uniform(-amount, amount) * axes[1]
        v.co.z += rnd.uniform(-amount, amount) * axes[2]
    return obj


def subsurf(obj, levels=1):
    mod = obj.modifiers.new("Subsurf", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels
    return obj


# --------------------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------------------

UV_STUDS_PER_TILE = 4.0

# Blender -> Roblox axis change as a matrix (symmetric and its own inverse).
M_B2R = Matrix(((-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0)))


def to_roblox(v: Vector) -> tuple[float, float, float]:
    """Blender (x, y, z) -> Roblox (x, y, z). See module docstring."""
    return (-v.x, v.z, v.y)


def _tagged_objects() -> list[bpy.types.Object]:
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and "ns_part" in o]


def _set_sharp_by_angle(me: bpy.types.Mesh, angle_deg: float) -> None:
    bm = bmesh.new()
    bm.from_mesh(me)
    if angle_deg < 0:
        for f in bm.faces:
            f.smooth = False
    else:
        lim = math.radians(angle_deg)
        for f in bm.faces:
            f.smooth = True
        for e in bm.edges:
            if not e.is_manifold:
                continue
            if e.calc_face_angle(0.0) > lim:
                e.smooth = False
    bm.to_mesh(me)
    bm.free()


def _evaluated_mesh(obj: bpy.types.Object) -> bpy.types.Mesh:
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
    me.transform(obj.matrix_world)
    if obj.matrix_world.determinant() < 0:
        me.flip_normals()
    _set_sharp_by_angle(me, obj.get("ns_smooth_angle", 35.0))
    return me


def _r3(x: float) -> float:
    v = round(x, 3)
    return 0.0 if v == 0 else v


def bbox_world(objs) -> tuple[Vector, Vector]:
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    dg = bpy.context.evaluated_depsgraph_get()
    for o in objs:
        ev = o.evaluated_get(dg)
        for c in ev.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def export_asset(asset: str, batch: str, *, group: str, pivot: tuple | None = None,
                 objects=None, fbx: bool = True, meta: dict | None = None,
                 rig: "bpy.types.Object | None" = None, vertex_colors: bool = False,
                 merge_parts: str | None = None, sockets: dict | None = None,
                 merge: str | None = "material") -> dict:
    """Export every tagged object in the scene as one Roblox asset.

    asset   e.g. "Food_Tomato" (Category_Name). Used for file names and the Studio Model name.
    batch   folder under meshes/ and fbx/, e.g. "gate", "A_food".
    group   ReplicatedStorage.Assets.<group> the model is stored under in Studio.
    pivot   Blender-space world point used as the asset pivot. Default: bottom-centre of bbox.
    rig     Armature object for rigid-part rigs: parts are exported in the REST pose and a
            "rig" section (bone names, parents, joint positions) is added.
    vertex_colors  Also write per-vertex colours ("c") — used by the pipeline-gate test.
    merge_parts    If set, merge every tagged object into ONE part with this name
                   (only meaningful with vertex_colors=True).
    merge          "material" (default): parts that share material, transparency, shadow,
                   collision and bone, and have no runtime role, are merged into ONE
                   vertex-coloured mesh per group (fewer MeshParts; colours survive publishing
                   and the MeshPart colour is white). Parts with a `recolor` role always stay
                   separate so code can find them. None = one MeshPart per tagged object.
    sockets        Named gameplay points, {name: (x, y, z)} or {name: ((x, y, z), yaw_deg)} in
                   Blender world space (yaw about Blender Z, which equals Roblox yaw about Y).
                   Exported relative to the pivot; Studio stores each as a CFrame attribute
                   "Socket_<name>" on the Model (world = model:GetPivot() * socket).
    """
    if rig is not None:
        rig.data.pose_position = "REST"
        bpy.context.view_layer.update()
    objs = objects or _tagged_objects()
    assert objs, f"{asset}: no tagged objects"
    names = [o["ns_part"] for o in objs]
    assert len(names) == len(set(names)), f"{asset}: duplicate part names {names}"

    lo, hi = bbox_world(objs)
    if pivot is None:
        pv = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    else:
        pv = Vector(pivot)

    parts = []
    total_tris = 0
    if merge_parts:
        groups = [objs]
    elif merge == "material":
        keyed: dict[tuple, list] = {}
        order: list[tuple] = []
        for o in objs:
            if o.get("ns_role"):
                k = ("__solo__", o["ns_part"])
            else:
                k = (o["ns_material"], round(o["ns_transparency"], 3), o["ns_cast_shadow"],
                     o["ns_can_collide"], o.get("ns_bone"))
            if k not in keyed:
                keyed[k] = []
                order.append(k)
            keyed[k].append(o)
        groups = [keyed[k] for k in order]
    else:
        groups = [[o] for o in objs]
    for grp in groups:
        o = grp[0]
        merged = bool(merge_parts) or len(grp) > 1
        me = _merged_evaluated(grp) if merged else _evaluated_mesh(o)
        use_vc = vertex_colors or merged
        colmap = None
        if use_vc:
            colmap = me.attributes.get("ns_col")
        me.calc_loop_triangles()
        cn = me.corner_normals  # per-corner normals honouring sharp edges / flat faces
        # Unique (vertex, normal) pairs -> output vertex
        key_to_idx: dict[tuple, int] = {}
        pos: list[tuple] = []
        nor: list[tuple] = []
        cols: list[tuple] = []
        tris: list[int] = []
        for lt in me.loop_triangles:
            idx3 = []
            for li, vi in zip(lt.loops, lt.vertices):
                p = to_roblox(me.vertices[vi].co - pv)
                n = to_roblox(cn[li].vector)
                col = tuple(colmap.data[vi].color[:3]) if colmap is not None else None
                k = (vi, round(n[0], 3), round(n[1], 3), round(n[2], 3))
                if k not in key_to_idx:
                    key_to_idx[k] = len(pos)
                    pos.append(p)
                    nl = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
                    nor.append((n[0] / nl, n[1] / nl, n[2] / nl))
                    cols.append(col)
                idx3.append(key_to_idx[k])
            tris.extend(idx3)
        bpy.data.meshes.remove(me)
        if not tris:
            continue
        # Part-local coordinates: centred on the part's own bounding box (MeshParts are
        # always centred on their bounds in Roblox), with `offset` placing it in the asset.
        mn = [min(p[i] for p in pos) for i in range(3)]
        mx = [max(p[i] for p in pos) for i in range(3)]
        ctr = [(mn[i] + mx[i]) / 2 for i in range(3)]
        size = [mx[i] - mn[i] for i in range(3)]
        v_flat = []
        for p in pos:
            v_flat.extend((_r3(p[0] - ctr[0]), _r3(p[1] - ctr[1]), _r3(p[2] - ctr[2])))
        n_flat = []
        for n in nor:
            n_flat.extend((_r3(n[0]), _r3(n[1]), _r3(n[2])))
        uv_flat = []
        for p, n in zip(pos, nor):
            ax = max(range(3), key=lambda i: abs(n[i]))
            a, b = {0: (2, 1), 1: (0, 2), 2: (0, 1)}[ax]
            uv_flat.extend((_r3(p[a] / UV_STUDS_PER_TILE), _r3(-p[b] / UV_STUDS_PER_TILE)))
        c_flat = None
        if use_vc and colmap is not None:
            c_flat = []
            for c in cols:
                c_flat.extend((_r3(c[0]), _r3(c[1]), _r3(c[2])))
        geo_hash = hashlib.sha1(json.dumps([v_flat, n_flat, tris, uv_flat, c_flat]).encode()).hexdigest()[:16]
        if merge_parts:
            pname = merge_parts
        elif merged:
            bone = o.get("ns_bone")
            taken = {p["name"] for p in parts} | {x["ns_part"] for x in objs if x not in grp}
            if bone and bone not in taken:
                pname = bone  # rigs: the bone's main part must carry the bone's name
            else:
                pname = (bone + "_" if bone else "") + o["ns_material"]
            while pname in taken:
                pname += "_"
        else:
            pname = o["ns_part"]
        part = {
            "name": pname,
            "color": "#FFFFFF" if c_flat is not None else o["ns_color"],
            "material": o["ns_material"],
            "transparency": o["ns_transparency"],
            "castShadow": o["ns_cast_shadow"],
            "canCollide": o["ns_can_collide"],
            "role": o.get("ns_role"),
            "bone": o.get("ns_bone"),
            "offset": [_r3(c) for c in ctr],
            "size": [_r3(s) for s in size],
            "hash": geo_hash,
            "tris": len(tris) // 3,
            "v": v_flat,
            "n": n_flat,
            "t": tris,
            "uv": uv_flat,
        }
        if c_flat is not None:
            part["c"] = c_flat
        total_tris += len(tris) // 3
        parts.append(part)

    rig_info = None
    if rig is not None:
        rig_info = _rig_info(rig, pv)
        rig.data.pose_position = "POSE"
        bpy.context.view_layer.update()

    rlo = to_roblox(lo - pv)
    rhi = to_roblox(hi - pv)
    asset_size = [_r3(abs(rhi[i] - rlo[i])) for i in range(3)]
    doc = {
        "asset": asset,
        "group": group,
        "batch": batch,
        "format": 1,
        "size": asset_size,
        "tris": total_tris,
        "meta": meta or {},
        "parts": parts,
    }
    if rig_info is not None:
        doc["rig"] = rig_info
    if sockets:
        out = {}
        for sname, spec in sockets.items():
            if len(spec) == 2 and not isinstance(spec[0], (int, float)):
                loc, yaw = spec
            else:
                loc, yaw = spec, 0.0
            out[sname] = {"p": [_r3(c) for c in to_roblox(Vector(loc) - pv)], "yaw": _r3(float(yaw))}
        doc["sockets"] = dict(sorted(out.items()))
    mdir = os.path.join(REPO, "meshes", batch)
    os.makedirs(mdir, exist_ok=True)
    with open(os.path.join(mdir, f"{asset}.json"), "w") as f:
        json.dump(doc, f, separators=(",", ":"))

    if fbx:
        fdir = os.path.join(REPO, "fbx", batch)
        os.makedirs(fdir, exist_ok=True)
        _export_fbx(objs, os.path.join(fdir, f"{asset}.fbx"), pv)

    _update_manifest(batch, doc)
    return doc


def _export_fbx(objs, path, pv: Vector) -> None:
    # Temporarily move everything so the pivot sits at the world origin.
    for o in objs:
        o.location -= pv
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_unit_scale=True,
                             global_scale=1.0, axis_forward="-Z", axis_up="Y",
                             use_mesh_modifiers=True, mesh_smooth_type="FACE",
                             add_leaf_bones=False, bake_anim=False)
    for o in objs:
        o.location += pv


def _update_manifest(batch: str, doc: dict) -> None:
    path = os.path.join(REPO, "manifests", f"{batch}.json")
    man = {}
    if os.path.exists(path):
        with open(path) as f:
            man = json.load(f)
    man[doc["asset"]] = {
        "group": doc["group"],
        "size": doc["size"],
        "tris": doc["tris"],
        "meta": doc["meta"],
        "url": f"{RAW_BASE}/meshes/{batch}/{doc['asset']}.json",
        "parts": [{k: p[k] for k in ("name", "color", "material", "transparency", "castShadow",
                                      "canCollide", "role", "bone", "offset", "size", "hash", "tris")}
                  for p in doc["parts"]],
    }
    if "rig" in doc:
        man[doc["asset"]]["rig"] = doc["rig"]
    if "sockets" in doc:
        man[doc["asset"]]["sockets"] = doc["sockets"]
    with open(path, "w") as f:
        json.dump(dict(sorted(man.items())), f, indent=1)


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------

def _setup_render(res=512, samples=24, transparent=False):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.render.film_transparent = transparent
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.32, 0.33, 0.36, 1)
    bg.inputs[1].default_value = 0.9


def _light(name, kind, loc, energy, size=2.0, target=(0, 0, 0)):
    ld = bpy.data.lights.new(name, type=kind)
    ld.energy = energy
    if kind == "AREA":
        ld.size = size
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = Vector(loc)
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return ob


def _camera_fit(lo: Vector, hi: Vector, yaw_deg: float, pitch_deg: float, fov_deg=30.0, margin=1.15):
    ctr = (lo + hi) / 2
    radius = max((hi - lo).length / 2, 0.05)
    dist = radius * margin / math.sin(math.radians(fov_deg) / 2)
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    # yaw 0 = looking at the front (camera on -Y side)
    off = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch))) * dist
    cd = bpy.data.cameras.new("PreviewCam")
    cd.angle = math.radians(fov_deg)
    cd.clip_start = 0.01
    cd.clip_end = dist * 10
    cam = bpy.data.objects.new("PreviewCam", cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = ctr + off
    cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam, ctr, dist


def _clear_rig():
    for o in list(bpy.context.scene.objects):
        if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim", "RefCube", "Floor")):
            bpy.data.objects.remove(o, do_unlink=True)


def render_preview(asset: str, out_dir: str | None = None, res=512, samples=24) -> str:
    """Two-panel preview: (1) close 3/4 view of the asset, (2) rear 3/4 view with a
    1-stud reference cube beside it. Returns the combined PNG path."""
    from PIL import Image
    out_dir = out_dir or os.path.join(REPO, "..", "previews")
    os.makedirs(out_dir, exist_ok=True)
    objs = _tagged_objects()
    lo, hi = bbox_world(objs)
    span = max(hi.x - lo.x, hi.y - lo.y, 0.5)
    bpy.ops.mesh.primitive_plane_add(size=max(span * 8, 8), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z - 0.001))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor.data.materials.append(material("#3A3B42"))
    _setup_render(res, samples, transparent=False)
    paths = []
    for i, (yaw, pitch, with_ref) in enumerate(((-35, 28, False), (150, 22, True))):
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim", "RefCube")):
                bpy.data.objects.remove(o, do_unlink=True)
        fit = list(objs)
        if with_ref:
            ref = box((1, 1, 1), loc=(lo.x - 0.7, (lo.y + hi.y) / 2, lo.z + 0.5), bevel=0.0, name="RefCube")
            ref.data.materials.append(material("#9A9AA6"))
            fit.append(ref)
        flo, fhi = bbox_world(fit)
        cam, ctr, dist = _camera_fit(flo, fhi, yaw, pitch)
        k = math.radians(yaw)
        _light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * dist, 60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        _light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3)) * dist, 20 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        _light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.8)) * dist, 35 * dist ** 2 / 9, size=dist * 0.4, target=ctr)
        p = os.path.join(out_dir, f"{asset}_{i}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    _clear_rig()  # also removes the reference cube and floor
    ims = [Image.open(p) for p in paths]
    combo = Image.new("RGB", (res * len(ims), res))
    for i, im in enumerate(ims):
        combo.paste(im.convert("RGB"), (i * res, 0))
    out = os.path.join(out_dir, f"{asset}_preview.png")
    combo.save(out)
    for p in paths:
        os.remove(p)
    return out


def render_icon(name: str, group: str, yaw=-35.0, pitch=28.0, res=512, samples=48, fov=24.0,
                margin=1.02, objects=None) -> str:
    """Consistent 3/4 icon render, transparent background, three-point light."""
    objs = objects or _tagged_objects()
    lo, hi = bbox_world(objs)
    _setup_render(res, samples, transparent=True)
    bg = bpy.context.scene.world.node_tree.nodes.get("Background")
    bg.inputs[1].default_value = 0.45
    # Icons: soft, low-specular materials so colours read saturated (no grey sky reflections)
    saved = []
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
        if b:
            saved.append((b, b.inputs["Roughness"].default_value, b.inputs["Specular IOR Level"].default_value))
            b.inputs["Roughness"].default_value = max(0.62, b.inputs["Roughness"].default_value)
            b.inputs["Specular IOR Level"].default_value = 0.25
    cam, ctr, dist = _camera_fit(lo, hi, yaw, pitch, fov_deg=fov, margin=margin)
    k = math.radians(yaw)
    _light("Key", "AREA", ctr + Vector((math.sin(k - 0.7), -math.cos(k - 0.7), 1.0)) * dist, 62 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
    _light("Fill", "AREA", ctr + Vector((math.sin(k + 1.3), -math.cos(k + 1.3), 0.2)) * dist, 18 * dist ** 2 / 9, size=dist * 0.9, target=ctr)
    _light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.9)) * dist, 50 * dist ** 2 / 9, size=dist * 0.4, target=ctr)
    out_dir = os.path.join(REPO, "icons", group)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{name}.png")
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    _clear_rig()
    for b, r, sp in saved:
        b.inputs["Roughness"].default_value = r
        b.inputs["Specular IOR Level"].default_value = sp
    export_icon(out, name, group)
    return out


def write_nsz(png_path: str, nsz_path: str | None = None, size: int | None = None) -> tuple[str, str, int, int]:
    """Encode a PNG as NSZ1 (base64 of "NSZ1" + u16le w + u16le h + zlib(RGBA)).

    This is the payload the Studio importer plugin decodes into an EditableImage and
    publishes with CreateAssetAsync. Returns (path, sha1-of-pixels, width, height).
    """
    import base64
    import struct
    import zlib
    from PIL import Image

    im = Image.open(png_path).convert("RGBA")
    if size and im.size != (size, size):
        im = im.resize((size, size), Image.LANCZOS)
    w, h = im.size
    pixels = im.tobytes()
    raw = b"NSZ1" + struct.pack("<HH", w, h) + zlib.compress(pixels, 9)
    nsz_path = nsz_path or os.path.splitext(png_path)[0] + ".nsz"
    with open(nsz_path, "w") as f:
        f.write(base64.b64encode(raw).decode("ascii"))
    return nsz_path, hashlib.sha1(pixels).hexdigest()[:16], w, h


def export_icon(png_path: str, name: str, group: str) -> dict:
    """Write the .nsz payload next to an icon PNG and register it in manifests/icons.json."""
    nsz, digest, w, h = write_nsz(png_path)
    rel = os.path.relpath(nsz, REPO).replace(os.sep, "/")
    entry = {"group": group, "size": [w, h], "hash": digest, "url": f"{RAW_BASE}/{rel}"}
    path = os.path.join(REPO, "manifests", "icons.json")
    man = {}
    if os.path.exists(path):
        with open(path) as f:
            man = json.load(f)
    man[name] = entry
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(dict(sorted(man.items())), f, indent=1)
    return entry


# --------------------------------------------------------------------------------------
# Merged / vertex-colour export (pipeline-gate experiment)
# --------------------------------------------------------------------------------------

def _merged_evaluated(objs) -> bpy.types.Mesh:
    """Evaluate several tagged objects, bake each one's colour into a point attribute
    `ns_col`, and return them as one world-space mesh."""
    bm = bmesh.new()
    col_layer = bm.verts.layers.float_color.new("ns_col")
    for o in objs:
        me = _evaluated_mesh(o)
        rgb = hex_rgb(o["ns_color"])
        tmp = bmesh.new()
        tmp.from_mesh(me)
        offset = len(bm.verts)
        vmap = []
        for v in tmp.verts:
            nv = bm.verts.new(v.co)
            nv[col_layer] = (rgb[0], rgb[1], rgb[2], 1.0)
            vmap.append(nv)
        bm.verts.index_update()
        for f in tmp.faces:
            try:
                nf = bm.faces.new([vmap[v.index] for v in f.verts])
                nf.smooth = f.smooth
            except ValueError:
                pass
        # keep each part's own hard edges (its smooth_angle), not one global angle
        for e in tmp.edges:
            if not e.smooth:
                ne = bm.edges.get([vmap[e.verts[0].index], vmap[e.verts[1].index]])
                if ne is not None:
                    ne.smooth = False
        tmp.free()
        bpy.data.meshes.remove(me)
    out = bpy.data.meshes.new("Merged")
    bm.to_mesh(out)
    bm.free()
    return out


# --------------------------------------------------------------------------------------
# Rigid-part rigs
# --------------------------------------------------------------------------------------

def make_armature(name: str, bones: list[tuple]) -> bpy.types.Object:
    """Create an armature. bones = [(name, parent_or_None, head_xyz, tail_xyz), ...]."""
    arm_data = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones
    for bname, parent, head, tail in bones:
        b = eb.new(bname)
        b.head = Vector(head)
        b.tail = Vector(tail)
        b.roll = 0.0
        if parent:
            b.parent = eb[parent]
            b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return arm


def bind(obj: bpy.types.Object, arm: bpy.types.Object, bone: str) -> bpy.types.Object:
    """Rigidly attach a tagged part to a bone (no skinning), keeping its world transform."""
    obj["ns_bone"] = bone
    bpy.context.view_layer.update()  # matrix_world is stale right after creation/transform
    mw = obj.matrix_world.copy()
    obj.parent = arm
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    bpy.context.view_layer.update()
    obj.matrix_world = mw
    return obj


def _rig_info(arm: bpy.types.Object, pv: Vector) -> dict:
    bones = []
    for b in arm.data.bones:  # hierarchy order: parents before children
        head_w = arm.matrix_world @ b.head_local
        bones.append({
            "name": b.name,
            "parent": b.parent.name if b.parent else None,
            "joint": [_r3(c) for c in to_roblox(head_w - pv)],
        })
    order = []
    seen = set()

    def visit(n):
        if n["name"] in seen:
            return
        if n["parent"]:
            visit(next(x for x in bones if x["name"] == n["parent"]))
        seen.add(n["name"])
        order.append(n)

    for n in bones:
        visit(n)
    return {"bones": order}


# --------------------------------------------------------------------------------------
# Animation export -> anim/<Rig>.lua  (played in game by BlenderAnimator)
# --------------------------------------------------------------------------------------

_EASE_NAMES = {"SINE": "sine", "QUAD": "quad", "CUBIC": "cubic", "QUART": "quart", "QUINT": "quint",
               "EXPO": "expo", "CIRC": "circ", "BACK": "back", "BOUNCE": "bounce", "ELASTIC": "elastic",
               "LINEAR": "linear", "CONSTANT": "constant", "BEZIER": "sine"}
_EASE_DIR = {"EASE_IN": "In", "EASE_OUT": "Out", "EASE_IN_OUT": "InOut", "AUTO": "InOut"}


def key(arm, bone: str, frame: int, rot=(0, 0, 0), loc=None, ease="SINE", direction="EASE_IN_OUT"):
    """Key one bone at a frame. rot = Euler degrees (XYZ) in the bone's local rest frame,
    loc = local offset in studs (bone frame) or None. ease applies to the segment that
    starts at this key."""
    from mathutils import Euler
    pb = arm.pose.bones[bone]
    pb.rotation_quaternion = Euler(tuple(math.radians(a) for a in rot), "XYZ").to_quaternion()
    pb.keyframe_insert("rotation_quaternion", frame=frame)
    if loc is not None:
        pb.location = Vector(loc)
        pb.keyframe_insert("location", frame=frame)
    act = arm.animation_data.action
    for fc in _action_fcurves(act):
        if fc.data_path.startswith(f'pose.bones["{bone}"]'):
            for kp in fc.keyframe_points:
                if int(round(kp.co.x)) == frame:
                    kp.interpolation = ease
                    kp.easing = direction


def _action_fcurves(act):
    """F-curves of an action (Blender 4.4+ layered actions and the legacy API)."""
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])) > 0:
        return list(act.fcurves)
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                out.extend(bag.fcurves)
    return out


def new_action(arm, name: str, start: int, end: int, loop: bool = True, fps: int = 30):
    act = bpy.data.actions.new(name)
    act["ns_loop"] = loop
    act["ns_start"] = start
    act["ns_end"] = end
    act["ns_fps"] = fps
    act.use_fake_user = True
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and arm.animation_data.action_slot is None:
        try:
            slot = act.slots.new(id_type="OBJECT", name=arm.name)
            arm.animation_data.action_slot = slot
        except Exception:
            pass
    # start every action from rest
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    return act


def _euler_for_roblox(R) -> tuple[float, float, float]:
    """Return (rx, ry, rz) so that CFrame.Angles(rx, ry, rz) == R (R = Rx·Ry·Rz)."""
    e = R.to_euler("ZYX")
    return (e.x, e.y, e.z)


def export_animations(arm, rig_name: str, actions: list, pivot=None) -> str:
    """Write anim/<rig_name>.lua with every action's keys in Roblox axes, relative to rest."""
    scene = bpy.context.scene
    bones = [b.name for b in arm.data.bones]
    out_clips = {}
    for act in actions:
        arm.animation_data.action = act
        if hasattr(arm.animation_data, "action_slot") and len(getattr(act, "slots", [])) > 0:
            arm.animation_data.action_slot = act.slots[0]
        fps = act.get("ns_fps", 30)
        start, end = act["ns_start"], act["ns_end"]
        fcs = _action_fcurves(act)
        per_bone = {}
        for bname in bones:
            path = f'pose.bones["{bname}"]'
            bfcs = [fc for fc in fcs if fc.data_path.startswith(path)]
            if not bfcs:
                continue
            has_loc = any(fc.data_path.endswith("location") for fc in bfcs)
            frames = sorted({int(round(kp.co.x)) for fc in bfcs for kp in fc.keyframe_points})
            ease_at = {}
            for fc in bfcs:
                for kp in fc.keyframe_points:
                    f = int(round(kp.co.x))
                    if fc.data_path.endswith("rotation_quaternion") or f not in ease_at:
                        nm = _EASE_NAMES.get(kp.interpolation, "sine")
                        if nm not in ("linear", "constant"):
                            nm += _EASE_DIR.get(kp.easing, "InOut")
                        ease_at[f] = nm
            bone = arm.data.bones[bname]
            B = bone.matrix_local.copy()
            h = B.translation.copy()
            keys = []
            for f in frames:
                scene.frame_set(f)
                L = arm.pose.bones[bname].matrix_basis.copy()
                D = B @ L @ B.inverted()
                T = Matrix.Translation(-h) @ D @ Matrix.Translation(h)
                R = M_B2R @ T.to_3x3() @ M_B2R
                rx, ry, rz = _euler_for_roblox(R)
                k = [_r3((f - start) / fps), _r3(rx), _r3(ry), _r3(rz)]
                if has_loc:
                    t = M_B2R @ T.translation
                    k += [_r3(t.x), _r3(t.y), _r3(t.z)]
                k.append(ease_at.get(f, "sineInOut"))
                keys.append(k)
            per_bone[bname] = keys
        out_clips[act.name] = {"length": _r3((end - start) / fps), "loop": bool(act.get("ns_loop", True)),
                               "keys": per_bone}
    scene.frame_set(0)
    lua = _to_lua({"rig": rig_name, "bones": bones, "clips": out_clips})
    header = (f"-- AnimData for rig '{rig_name}' — generated by blender/lib/nslib.py; do not edit by hand.\n"
              "-- keys per bone: { t, rx, ry, rz, [px, py, pz,] ease }  (radians, studs, Roblox axes,\n"
              "-- relative to the rest pose; rotation = CFrame.Angles(rx, ry, rz))\n")
    path = os.path.join(REPO, "anim", f"{rig_name}.lua")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(header + "return " + lua + "\n")
    return path


def _to_lua(v, indent=0) -> str:
    pad = "\t" * indent
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        r = round(float(v), 3)
        return str(int(r)) if r == int(r) else repr(r)
    if isinstance(v, str):
        return json.dumps(v)
    if v is None:
        return "nil"
    if isinstance(v, list):
        if all(not isinstance(x, (list, dict)) for x in v):
            return "{" + ", ".join(_to_lua(x) for x in v) + "}"
        return "{\n" + ",\n".join(pad + "\t" + _to_lua(x, indent + 1) for x in v) + ",\n" + pad + "}"
    if isinstance(v, dict):
        items = []
        for k, x in v.items():
            kk = k if (isinstance(k, str) and k.isidentifier()) else f"[{json.dumps(k)}]"
            items.append(f"{pad}\t{kk} = {_to_lua(x, indent + 1)}")
        return "{\n" + ",\n".join(items) + ",\n" + pad + "}"
    raise TypeError(type(v))


def render_pose_strip(arm, action, frames: list[int], name: str, out_dir: str, res=320) -> str:
    """Render the rig at several frames side by side (animation review)."""
    from PIL import Image
    arm.animation_data.action = action
    if hasattr(arm.animation_data, "action_slot") and len(getattr(action, "slots", [])) > 0:
        arm.animation_data.action_slot = action.slots[0]
    objs = _tagged_objects()
    bpy.context.scene.frame_set(frames[0])
    lo, hi = bbox_world(objs)
    pad = Vector((0.15, 0.15, 0.1)) * max((hi - lo).length, 1)
    lo, hi = lo - pad, hi + pad
    bpy.ops.mesh.primitive_plane_add(size=max((hi - lo).length * 4, 4), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor.data.materials.append(material("#3A3B42"))
    _setup_render(res, 16, transparent=False)
    cam, ctr, dist = _camera_fit(lo, hi, -60, 15)
    _light("Key", "AREA", ctr + Vector((-0.5, -1, 1.2)) * dist, 60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
    _light("Fill", "AREA", ctr + Vector((1, -0.6, 0.4)) * dist, 25 * dist ** 2 / 9, size=dist, target=ctr)
    paths = []
    for f in frames:
        bpy.context.scene.frame_set(f)
        p = os.path.join(out_dir, f"{name}_f{f}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    _clear_rig()
    ims = [Image.open(p).convert("RGB") for p in paths]
    combo = Image.new("RGB", (res * len(ims), res))
    for i, im in enumerate(ims):
        combo.paste(im, (i * res, 0))
    out = os.path.join(out_dir, f"{name}_strip.png")
    combo.save(out)
    for p in paths:
        os.remove(p)
    bpy.context.scene.frame_set(0)
    return out


def ring(r_in: float, r_out: float, depth: float, loc=(0, 0, 0), verts=24, name="Ring"):
    """Flat annulus (washer) of given radii and thickness, centred at loc."""
    bm = bmesh.new()
    rows = []
    for z in (-depth / 2, depth / 2):
        rows.append([bm.verts.new((r * math.cos(2 * math.pi * i / verts), r * math.sin(2 * math.pi * i / verts), z))
                     for r in (r_in, r_out) for i in range(verts)])
    (bi, bo), (ti, to) = [(row[:verts], row[verts:]) for row in rows]
    for i in range(verts):
        j = (i + 1) % verts
        bm.faces.new([bo[i], bo[j], to[j], to[i]])        # outer wall
        bm.faces.new([bi[j], bi[i], ti[i], ti[j]])        # inner wall
        bm.faces.new([to[i], to[j], ti[j], ti[i]])        # top
        bm.faces.new([bo[j], bo[i], bi[i], bi[j]])        # bottom
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return from_bmesh(bm, name, loc)


def join_applied(objs, name):
    for o in objs:
        apply_all(o)
    return join(objs, name)


def boolean(target, cutter, op="DIFFERENCE"):
    mod = target.modifiers.new("Bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def bevel(obj, width=0.03, segments=2, angle=40.0):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle)
    mod.use_clamp_overlap = True
    mod.harden_normals = False
    return obj


def tri_count(objs=None) -> int:
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for o in objs or _tagged_objects():
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        total += len(me.loop_triangles)
        o.evaluated_get(dg).to_mesh_clear()
    return total


def run_main(build, asset: str, batch: str, group: str, **export_kw):
    """Standard generator entry: build -> preview -> (export when NS_EXPORT=1)."""
    reset()
    extra = build() or {}
    print(f"[{asset}] triangles: {tri_count()}")
    prev = render_preview(asset, out_dir=os.path.join(REPO, "..", "previews", batch))
    print(f"[{asset}] preview: {prev}")
    if os.environ.get("NS_EXPORT") == "1":
        kw = dict(export_kw)
        kw.update(extra.get("export", {}))
        doc = export_asset(asset, batch, group=group, **kw)
        print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']}")
    return extra


def tube(points, radii, sides=8, resolution=4, name="Tube"):
    """Smooth tapered tube through `points` (Blender xyz) with per-point radius."""
    cd = bpy.data.curves.new(name, "CURVE")
    cd.dimensions = "3D"
    cd.resolution_u = resolution
    cd.bevel_depth = 1.0
    cd.bevel_resolution = max(1, sides // 4 - 1)
    cd.use_fill_caps = True
    sp = cd.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for bp, p, r in zip(sp.bezier_points, points, radii):
        bp.co = Vector(p)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
        bp.radius = r
    ob = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.ops.object.convert(target="MESH")
    return bpy.context.active_object


def contact_sheet(batch: str, cols: int = 3, thumb: int = 360) -> str:
    """Tile every <asset>_preview.png of a batch into one labelled review sheet."""
    from PIL import Image, ImageDraw

    pdir = os.path.join(REPO, "..", "previews", batch)
    files = sorted(f for f in os.listdir(pdir) if f.endswith("_preview.png"))
    assert files, f"no previews in {pdir}"
    tw, th = thumb * 2, thumb + 28
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, th * rows), (24, 26, 30))
    draw = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(os.path.join(pdir, f)).convert("RGB")
        im = im.resize((tw, int(im.height * tw / im.width)))
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(im, (x, y + 28))
        draw.text((x + 8, y + 6), f.replace("_preview.png", ""), fill=(235, 235, 235))
    out = os.path.join(pdir, "_contact.png")
    sheet.save(out)
    return out
