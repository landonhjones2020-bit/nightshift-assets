"""_common — shared helpers for the M_food batch (Night Shift at STACKHOUSE).

M_food adds six sandwich ingredients (salami, provolone + its melted variant, jalapenos, avocado,
bbq_sauce, ranch) with their Ingredient_* icons, the 6-bottle sauce rail and three counter /
dining-room props (hanging sign, now-serving board, pickup shelf).

Import from an asset script in this folder with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Re-uses the A_food batch helpers: A_food/_common.py is loaded under the private module name
`a_food_common` (the name G_icons uses for it too) and every public name is re-exported here, so
the M_food food scripts read exactly like the A_food ones (C.sheet, C.polar_slices,
C.melted_sheet, C.flecks_on, C.squeeze_bottle, C.check_bounds, C.meta ...). The two new sauces
are added to A_food's SAUCES table in memory (SAUCES below is that same dict), so
C.sauce_ribbon / C.sauce_icon / C.squeeze_bottle work for them unchanged.
The prop scripts add the B_shop shape helpers (C.shop(): fillet, rrect, prism, pipe, ring_slab,
part, palette) and the A_kitchen helpers (C.kitchen(): rod, part, kitchen palette), loaded on
first use so G_icons, which imports the food scripts to assemble sandwich icons, never pays
for them.

Sandwich contract (STYLE.md section 4): a filling lies along Blender X on the 2.2 x 0.85 sub roll,
bottom at Z = 0, overhang <= 0.08 (|x| <= 1.18, |y| <= 0.505); meta from C.meta(ingredient,
layer_height, layer_count, layer_spacing). Pivot = the contract origin (0, 0, 0).
Groups: Food_* -> "Food" (default), Kitchen_* -> "Kitchen", Shop_* -> "Shop" (run(group=...)).
Env: NS_EXPORT=1 export, NS_ICON=1 icon (icons/ingredients + manifests/icons.json),
     NS_DRAFT=1 low-res draft into NS_DRAFT_DIR only, NS_ICON_DRAFT=1 icon framing draft there,
     NS_ONLY_ICON=1 icon only, NS_PARTS=1 prints the part list.
"""
from __future__ import annotations

import importlib.util
import math
import os
import random
import sys

sys.dont_write_bytecode = True   # never drop .pyc caches into other batches' folders

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(BLENDER, "lib"))
import nslib as ns  # noqa: E402

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402


def _load(modname: str, rel: str):
    """Load another batch's helper module (every batch calls its own `_common`) under a private
    name, once per process."""
    if modname in sys.modules:
        return sys.modules[modname]
    spec = importlib.util.spec_from_file_location(modname, os.path.join(BLENDER, rel))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


F = _load("a_food_common", os.path.join("A_food", "_common.py"))

_KEEP_LOCAL = {"BATCH", "GROUP", "PREVIEW_DIR", "DRAFT_DIR", "HERE", "run", "draft", "draft_icon"}
for _k, _v in list(vars(F).items()):
    if not _k.startswith("_") and _k not in _KEEP_LOCAL and _k != "annotations":
        globals()[_k] = _v

BATCH = "M_food"
GROUP = "Food"
PREVIEW_DIR = os.path.join(ns.REPO, "..", "previews", BATCH)
DRAFT_DIR = os.environ.get("NS_DRAFT_DIR", "/tmp/ns_drafts/M_food")

# --------------------------------------------------------------------------------------
# sauces: the two new ones join A_food's table (ribbon colour, material, bottle body, cap, label)
# --------------------------------------------------------------------------------------
NEW_SAUCES = {
    "bbq_sauce": dict(col="#5B2614", mat="SmoothPlastic", body="#6A2B16", cap="#F2B33D"),
    "ranch": dict(col="#F3EFE2", mat="SmoothPlastic", body="#F3EFE2", cap="#4F9A3A", label="#4F9A3A",
                  herb="#5E8C3A"),
}
F.SAUCES.update(NEW_SAUCES)
SAUCES = F.SAUCES


def herb_flecks(name: str, target, path, col: str, every: int = 2, side: float = 0.026, seed: int = 3,
                size=(0.029, 0.019, 0.008), verts: int = 3):
    """Tiny herb chips on top of a sauce bead: sampled along its centre-line `path`, alternating a
    little to either side of the crest (ray-cast onto `target`)."""
    rnd = random.Random(seed)
    spots = []
    for i in range(2, len(path) - 2, every):
        x, y, _ = path[i]
        xa, ya, _ = path[i - 1]
        xb, yb, _ = path[i + 1]
        tx, ty = xb - xa, yb - ya
        L = math.hypot(tx, ty) or 1.0
        s = side * (1 if (i // every) % 2 else -1) * rnd.uniform(0.3, 1.0)
        spots.append((x - ty / L * s, y + tx / L * s))
    return F.flecks_on(name, [target], spots, col, "SmoothPlastic", size=size, verts=verts, seed=seed, sink=0.35,
                       smooth_angle=None)


def surface_decals(name: str, targets, polys, lift: float = 0.0025, max_step: float = 0.012):
    """Flat single-sided flecks laid on the top surface of `targets` (each vertex ray-cast straight
    down, then lifted `lift`). polys = [[(x, y), ...], ...]. A poly is dropped if any corner misses
    the surface or lands on a different layer (height spread > max_step), so decals never bend over
    a slice edge. Returns the joined object (untagged) or None."""
    tree = F.bvh_multi(targets)
    verts, faces = [], []
    for poly in polys:
        hits = []
        for x, y in poly:
            loc, _ = F.hit(tree, x, y)
            if loc is None:
                break
            hits.append(loc)
        if len(hits) != len(poly):
            continue
        zs = [h.z for h in hits]
        if max(zs) - min(zs) > max_step:
            continue
        base = len(verts)
        for h in hits:
            verts.append((h.x, h.y, h.z + lift))
        faces.append(tuple(range(base, base + len(poly))))
    if not faces:
        return None
    o = F.mesh_obj(name, verts, faces, recalc=False)
    for p in o.data.polygons:
        if p.normal.z < 0:
            p.flip()
    o.data.update()
    return o


def faces_obj(name: str, verts, faces, want):
    """Mesh object built from only the vertices its faces use (no loose verts). Repeated indices
    in a face are dropped (a quad that touches a pointed tip becomes a triangle). Every face is
    flipped to point along `want`: a callable want(face_centre) -> Vector, or a list with one
    direction per face (same order as `faces`)."""
    clean, dirs = [], []
    for k, f in enumerate(faces):
        out = []
        for i in f:
            if i not in out:
                out.append(i)
        if len(out) >= 3:
            clean.append(out)
            dirs.append(None if callable(want) else Vector(want[k]))
    used = sorted({i for f in clean for i in f})
    remap = {old: new for new, old in enumerate(used)}
    # mesh_obj welds coincident verts, which can merge faces away: build the mesh directly instead
    me = bpy.data.meshes.new(name)
    me.from_pydata([verts[i] for i in used], [], [tuple(remap[i] for i in f) for f in clean])
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    for p, d in zip(o.data.polygons, dirs):
        w = want(p.center) if d is None else d
        if p.normal.dot(w) < 0:
            p.flip()
    o.data.update()
    return o


def blob(r: float, n: int, cx: float, cy: float, rnd: random.Random, squash: float = 0.8, jag: float = 0.18):
    """Irregular little polygon (fat fleck, seed) centred at (cx, cy)."""
    a0 = rnd.uniform(0, 6.28)
    sq = rnd.uniform(squash, 1.0)
    pts = []
    for i in range(n):
        t = a0 + 2 * math.pi * i / n
        rr = r * rnd.uniform(1 - jag, 1 + jag)
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t) * sq))
    return pts


def melted_sheet_rind(name: str, col: str, rind_name: str, rind_col: str, *, N: int = 36, thick: float = 0.035,
                      lobes=None, drips=None, seed: int = 1, half=(1.12, 0.455), smooth_angle: float = 80.0,
                      base_hang: float = 0.03, inner=(0.55, 0.86, 0.955)):
    """A_food melted_sheet (same outline, plateau, lobes, drape and drips) with the curled-over rim
    band split into its own part: the smoked rind of melted provolone. The outermost ring of top
    quads joins the rim, so a thin rind line also shows from above. Drips stay cheese-coloured."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    lobes = lobes or []
    drips = drips or []
    A, B = half
    s_hang = inner[-2]
    smooth, spow = F.smooth, F.spow

    def lobe(t):
        d = 0.0
        for ang, drop, wid in lobes:
            da = math.degrees(math.atan2(math.sin(t - math.radians(ang)), math.cos(t - math.radians(ang))))
            d = max(d, drop * smooth(1 - abs(da) / wid))
        return d

    ts = [2 * math.pi * i / N for i in range(N)]
    outline = []
    for t in ts:
        w = 1 + 0.02 * math.sin(5 * t + ph[0]) + 0.012 * math.sin(11 * t + ph[1]) + 0.25 * lobe(t)
        outline.append((A * w * spow(math.cos(t), 2 / 3.2), B * min(w, 1.03) * spow(math.sin(t), 2 / 3.2)))

    def zfn(x, y, s, i):
        u = smooth((s - s_hang) / (1 - s_hang)) if s > s_hang else 0.0
        seams = sum(0.011 * math.exp(-((x - sx - 0.06 * math.sin(7 * y + sx)) / 0.07) ** 2) for sx in (-0.36, 0.36))
        return (0.006 * (1 - s) + 0.005 * math.sin(3.2 * x + ph[2]) + seams * (1 - u)
                - (base_hang + lobe(ts[i])) * u)

    sheet_, rim = F.sheet(name, outline, thick, zfn=zfn, center=(0, 0), inner=inner, edge=0.6, split_edge=True,
                          rim_on_top=True)
    parts = [sheet_]
    for k, (ang, length) in enumerate(drips):
        t = math.radians(ang)
        i = min(range(N), key=lambda j: abs(math.atan2(math.sin(ts[j] - t), math.cos(ts[j] - t))))
        x, y = outline[i]
        z = zfn(x, y, 1.0, i) + 0.055
        d = F.teardrop(f"Drip{k}", length + 0.045, 0.048 + 0.008 * (k % 2), flat=0.5)
        d.location = (x * 1.004, y * 1.004, z)
        d.rotation_euler = (0, 0, math.atan2(y, x) - math.pi / 2)
        ns.apply_all(d)
        parts.append(d)
    out = ns.join(parts, name) if len(parts) > 1 else sheet_
    ns.tag(out, name, col, "SmoothPlastic", smooth_angle=smooth_angle)
    rim.name = rind_name
    ns.tag(rim, rind_name, rind_col, "SmoothPlastic", smooth_angle=smooth_angle)
    return out, rim


# --------------------------------------------------------------------------------------
# other batches' helpers for the props (loaded on first use)
# --------------------------------------------------------------------------------------

def shop():
    """B_shop helpers: fillet, rrect, prism, slab, pipe, ring_slab, merge, part + the shop palette."""
    return _load("shop_common", os.path.join("B_shop", "_common.py"))


def kitchen():
    """A_kitchen helpers: rod, rrect, extrude, plate, part, screws + the kitchen palette."""
    return _load("a_kitchen_common", os.path.join("A_kitchen", "_common.py"))


# --------------------------------------------------------------------------------------
# run / review helpers
# --------------------------------------------------------------------------------------

def print_parts(asset: str):
    dg = bpy.context.evaluated_depsgraph_get()
    tot = 0
    for o in sorted(ns._tagged_objects(), key=lambda o: o.name):
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        n = len(me.loop_triangles)
        tot += n
        print(f"  [{asset}] {o.name:18s} {n:5d} tris  {o['ns_color']} {o['ns_material']:13s} role={o.get('ns_role')}")
        o.evaluated_get(dg).to_mesh_clear()
    lo, hi = ns.bbox_world(ns._tagged_objects())
    print(f"  [{asset}] bbox lo {tuple(round(c, 3) for c in lo)} hi {tuple(round(c, 3) for c in hi)} total {tot}")


def run(build, asset: str, meta_: dict | None = None, icon=None, pivot=(0.0, 0.0, 0.0), group: str = GROUP,
        preview=None, **export_kw):
    """Standard M_food entry (the A_food run() with this batch's folder): preview to
    previews/M_food (+ export with NS_EXPORT=1, + icon with NS_ICON=1).

    pivot    defaults to the contract origin (0, 0, 0); pass None for nslib's bbox bottom-centre or
             an explicit Blender point (hung / wall props).
    icon     (icon_name, icon_build_fn, render_icon_kwargs) or None; rendered into icons/ingredients.
    group    "Food" (default), "Kitchen" or "Shop".
    preview  optional preview(asset, out_dir, res, samples) -> png path replacing nslib's standard
             two-angle preview (e.g. angles_preview for ceiling-hung props).
    build() may return {"export": {...}} (sockets, meta) like every nslib generator.
    """
    kw = dict(export_kw)
    if meta_ is not None:
        kw["meta"] = meta_
    if pivot is not None:
        kw["pivot"] = pivot
    if os.environ.get("NS_PARTS") == "1":
        inner = build

        def build():
            out = inner()
            print_parts(asset)
            return out
    if os.environ.get("NS_DRAFT") == "1":
        draft(build, asset, preview=preview)
        return
    if os.environ.get("NS_ICON_DRAFT") == "1":
        if icon:
            name, fn, rkw = icon
            draft_icon(fn, name, **(rkw or {}))
        return
    if os.environ.get("NS_ONLY_ICON") != "1":
        # nslib.run_main's steps, with an optional custom preview
        ns.reset()
        extra = build() or {}
        print(f"[{asset}] triangles: {ns.tri_count()}")
        if preview is None:
            prev = ns.render_preview(asset, out_dir=PREVIEW_DIR)
        else:
            prev = preview(asset, PREVIEW_DIR, 512, 24)
        print(f"[{asset}] preview: {os.path.abspath(prev)}")
        if os.environ.get("NS_EXPORT") == "1":
            kw.update(extra.get("export", {}))
            doc = ns.export_asset(asset, BATCH, group=group, **kw)
            print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']}")
            for p in doc["parts"]:
                print(f"    part {p['name']:16s} {p['material']:13s} role={p['role']} tris={p['tris']}")
            if doc.get("sockets"):
                print(f"    sockets {doc['sockets']}")
    if icon and os.environ.get("NS_ICON") == "1":
        name, fn, rkw = icon
        ns.reset()
        fn()
        print(f"[{asset}] icon triangles: {ns.tri_count()}")
        print(f"[{asset}] icon:", ns.render_icon(name, "ingredients", **(rkw or {})))


def angles_preview(asset: str, out_dir: str, res: int = 512, samples: int = 24,
                   angles=((-35.0, -20.0), (145.0, 12.0)), floor: bool = False, margin: float = 1.1):
    """Two-angle preview from explicit (yaw, pitch) cameras (negative pitch = from below), no floor
    by default: ceiling-hung props show their face and underside the way players see them."""
    from PIL import Image
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=max((hi - lo).length * 6, 8),
                                         location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z - 0.001))
        fl = bpy.context.active_object
        fl.name = "Floor"
        fl.data.materials.append(ns.material("#3A3B42"))
    ns._setup_render(res, samples, transparent=False)
    paths = []
    for i, (yaw, pitch) in enumerate(angles):
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cam, ctr, dist = ns._camera_fit(lo, hi, yaw, pitch, margin=margin)
        k = math.radians(yaw)
        ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.6)) * dist,
                  60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), -0.3)) * dist,
                  22 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        ns._light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.8)) * dist,
                  30 * dist ** 2 / 9, size=dist * 0.4, target=ctr)
        p = os.path.join(out_dir, f"{asset}_{i}.png")
        os.makedirs(out_dir, exist_ok=True)
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    ns._clear_rig()
    ims = [Image.open(p).convert("RGB") for p in paths]
    combo = Image.new("RGB", (res * len(ims), res))
    for i, im in enumerate(ims):
        combo.paste(im, (i * res, 0))
    out = os.path.join(out_dir, f"{asset}_preview.png")
    combo.save(out)
    for p in paths:
        os.remove(p)
    return out


def screen_meta(part_name: str, w: float, h: float, face: str = "Front") -> dict:
    """SurfaceGui target description (the C_lobby / K_shop convention)."""
    return {"part": part_name, "face": face, "screen_size": [round(w, 3), round(h, 3)]}


def draft(build, name: str, res: int = 384, samples: int = 12, preview=None):
    """Quick low-res review render into DRAFT_DIR (never the repo)."""
    ns.reset()
    build()
    print(f"[{name}] triangles: {ns.tri_count()}")
    if preview is None:
        out = ns.render_preview(name, out_dir=DRAFT_DIR, res=res, samples=samples)
    else:
        out = preview(name, DRAFT_DIR, res, samples)
    print(out)
    return out


def draft_icon(fn, name: str, yaw=-35.0, pitch=28.0, fov=24.0, margin=1.02, res=256, samples=12, **_):
    """Low-sample stand-in for ns.render_icon (same camera, lights and material tweak) writing
    only to DRAFT_DIR — framing checks before the real icon render."""
    ns.reset()
    fn()
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    ns._setup_render(res, samples, transparent=True)
    bpy.context.scene.world.node_tree.nodes.get("Background").inputs[1].default_value = 0.45
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
        if b:
            b.inputs["Roughness"].default_value = max(0.62, b.inputs["Roughness"].default_value)
            b.inputs["Specular IOR Level"].default_value = 0.25
    cam, ctr, dist = ns._camera_fit(lo, hi, yaw, pitch, fov_deg=fov, margin=margin)
    k = math.radians(yaw)
    ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.7), -math.cos(k - 0.7), 1.0)) * dist, 62 * dist ** 2 / 9,
              size=dist * 0.6, target=ctr)
    ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.3), -math.cos(k + 1.3), 0.2)) * dist, 18 * dist ** 2 / 9,
              size=dist * 0.9, target=ctr)
    ns._light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.9)) * dist, 50 * dist ** 2 / 9,
              size=dist * 0.4, target=ctr)
    os.makedirs(DRAFT_DIR, exist_ok=True)
    out = os.path.join(DRAFT_DIR, f"{name}_icon.png")
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print(out)
    return out


def under_bread(kind: str = "white_sub"):
    """Draft helper: a bottom roll under the layer (context only; its parts are renamed Ctx* and
    removed again by strip_context() before export)."""
    F.under_bread(kind)


def strip_context():
    """Delete the Ctx* context parts added by under_bread()."""
    for o in list(ns._tagged_objects()):
        if o["ns_part"].startswith("Ctx"):
            bpy.data.objects.remove(o, do_unlink=True)
