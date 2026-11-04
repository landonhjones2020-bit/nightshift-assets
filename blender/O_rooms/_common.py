"""_common — shared helpers for the O_rooms batch (STACKHOUSE HQ Locker Room + VIP Lounge decor).

Import from an asset script in this folder with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Re-uses blender/J_lobby/_common.py the way J_lobby re-uses C_lobby: the giant-lettering kit
(Word, contour_tubes, stroke_paths), domes / spheres / loft / flat_poly, star_pts, mini_logo ...,
and through it C_lobby (part, rod, text, place, screen_meta, arc_solid, arc_profile_sweep,
catenary, facing_yaw ...) and B_shop (prism, pipe, fillet, rrect, ring_slab, text_mesh ...).
Also K_shop's lathe_ring / lathe_open (open shells) and L_decor's single-sided decal helpers
(poly, quad_xz, strip_xz, face_dir, turn_y).

New here:
  * milkshake()   soda-fountain tulip glass (Glass) with a shake, whipped cream, cherry, straw
                  (shared by Lobby_GoldCoffeeTable and Lobby_ShakeBar).
  * qa_check()    mesh QA from I_world/_qa.py: faces pointing into their own closed shell (they
                  vanish in Roblox, which draws one side) and same-plane same-facing overlaps
                  between faces (z-fighting). Printed on NS_QA=1 and on every export.
  * run()         build -> preview -> QA -> socket check -> export, with three mounts:
                    "floor"  pivot bottom-centre (nslib default)
                    "wall"   pivot bottom-centre of the BACK face (+Y, touches the wall), front -Y;
                             previews in front of a wall backdrop
                    "hang"   pivot TOP-centre (ceiling mount, everything hangs below z = 0);
                             previews from below with a ceiling plane
  * contact_sheet() labelled review grid of every final preview + manifest size / tris.

Conventions (as C_lobby / J_lobby): 1 stud = 1 Blender unit, Z up, front faces Blender -Y.
Role-less parts merge per material at export (vertex colours); only parts code must find carry
a `recolor` role (screen, lamp, neon, mirror, plaque ...). Part names never start with
Key/Fill/Rim/Floor/RefCube/PreviewCam (nslib's preview deletes those) - part() asserts this.
Screens for SurfaceGuis: a flat part with role "screen", a socket at the CENTRE of its face
(yaw = the way the face looks, 0 = front / -Y) and meta screen_size + surfaces (part, face).

Env: NS_QUICK=1 fast preview into previews/O_rooms/_quick, NS_PARTS=1 part list, NS_QA=1 mesh
QA without exporting, NS_SOCKETS=1 socket check render (previews/O_rooms/_checks),
NS_NORENDER=1 no preview, NS_EXPORT=1 export.
"""
from __future__ import annotations

import importlib.util
import math
import os
import sys

sys.dont_write_bytecode = True   # don't drop .pyc caches into the other batches' folders

import bpy  # noqa: F401  (must load before bmesh in the bpy module build)
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "lib"))
import nslib as ns  # noqa: E402

_SYS_SITE = "/usr/local/lib/python3.13/site-packages"   # Pillow lives in the system Python
if os.path.isdir(_SYS_SITE) and _SYS_SITE not in sys.path:
    sys.path.append(_SYS_SITE)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, "..", rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# every batch calls its helper module `_common`: load them under their own names
J = _load("jlobby_common", os.path.join("J_lobby", "_common.py"))
K = _load("kshop_common", os.path.join("K_shop", "_common.py"))
D = _load("ldecor_common", os.path.join("L_decor", "_common.py"))
L, S = J.L, J.S

fillet, rrect, circle_pts, ellipse_pts = S.fillet, S.rrect, S.circle_pts, S.ellipse_pts
prism, slab, pipe, round_path, ring_slab = S.prism, S.slab, S.pipe, S.round_path, S.ring_slab
text_mesh, fit_text_width, bbox_of, merge, band = S.text_mesh, S.fit_text_width, S.bbox_of, S.merge, S.band
FONT_BOLD, FONT_BOLD_ITALIC = S.FONT_BOLD, S.FONT_BOLD_ITALIC
rod, yaw_point, facing_yaw = L.rod, L.yaw_point, L.facing_yaw
arc_solid, arc_profile_sweep, arch, arch_path = L.arc_solid, L.arc_profile_sweep, L.arch, L.arch_path
annulus, disc, catenary, text, place, screen_meta = L.annulus, L.disc, L.catenary, L.text, L.place, L.screen_meta
star_pts, domes, spheres, loft, flat_poly, flat_poly_3d = J.star_pts, J.domes, J.spheres, J.loft, J.flat_poly, J.flat_poly_3d
Word, contour_tubes, stroke_paths, resample, path_points = J.Word, J.contour_tubes, J.stroke_paths, J.resample, J.path_points
mini_logo, add_parts, merge_into, clip_rect, clip_band = J.mini_logo, J.add_parts, J.merge_into, J.clip_rect, J.clip_band
obj_from_bm = J.obj_from_bm
lathe_ring, lathe_open, tight_fit = K.lathe_ring, K.lathe_open, K.tight_fit
poly, quad_xz, strip_xz, face_dir, turn_y = D.poly, D.quad_xz, D.strip_xz, D.face_dir, D.turn_y

BATCH = "O_rooms"
GROUP = "Lobby"
PREVIEWS = os.path.join(ns.REPO, "..", "previews", BATCH)
FORBIDDEN = ("PreviewCam", "Key", "Fill", "Rim", "RefCube", "Floor")

# ---------------------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------------------
# shared brand / environment colours (STYLE.md section 1, C_lobby)
BRAND = "#E8502A"            # STACKHOUSE red-orange
MUSTARD = "#F2B33D"
CREAM = "#EFE6D2"
CREAM_SHADE = "#DCD0B8"
PAPER = "#F3EEE2"
NAVY = "#1E2A44"
PINK = "#FF4FA3"
CYAN = "#38E1FF"
CHROME = "#D3D8DC"
RUBBER = "#1D1E22"
BLACK = "#16171A"
SCREEN = L.SCREEN            # dark glossy screen panel (the game draws the content)
INK = "#24262B"

# Locker Room: staff back-room
LOCKER_RED = "#D9472B"       # locker doors (Lobby_LockerBank)
LOCKER_DARK = "#9E3524"      # locker carcass (Lobby_LockerBank)
STEEL = "#B9C0C6"            # brushed steel (Metal)
MAPLE = "#C8955F"            # bench slats (Lobby_Bench)
SLATE = "#4F6475"            # slate-blue (the room's floor tile family)
WARM_WHITE = "#FFE6B5"       # vanity bulbs (Neon, role "lamp")
TOWEL = "#F1EBDD"            # towels (Lobby_Bench)
VENT = "#2B1A17"             # locker louvres (Lobby_LockerBank)
PORCELAIN = "#F1F0EA"
MIRROR = "#C6D3D8"           # mirror glass (Lobby_Mirror)
CORK = "#B9895A"
WOOD_LIGHT = "#A8774E"

# VIP Lounge: plush and premium
VIP_PURPLE = "#4A2350"       # carpet
GOLD = "#E8B84A"             # gilding (Metal)
VELVET = "#8E1E2E"           # red velvet (Fabric)
VELVET_DARK = "#6E1623"
LACQUER = "#16121C"          # black lacquer
CRYSTAL = "#E4F3FF"          # chandelier drops (Glass)
LAMP_WARM = "#FFD99A"        # warm candle bulbs (Neon, role "lamp"; C_lobby LAMP_WARM)
CHERRY = "#C8102E"
WHIP = "#FBF6EC"
SHAKE_PINK = "#F483B3"       # strawberry
SHAKE_MINT = "#8EE0CC"       # mint
SHAKE_CHOC = "#7A4A30"       # chocolate
SHAKE_VANILLA = "#F6E7C1"
GLASS_TINT = "#DDEFF5"       # glassware (Glass, transparent)


# ---------------------------------------------------------------------------------------
# Small builders
# ---------------------------------------------------------------------------------------

def part(objs, name, color, mat="SmoothPlastic", **kw):
    """Apply + join + tag in one call (objs: object or list, nested lists / None ok)."""
    assert not name.startswith(FORBIDDEN), name
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    return ns.tag(merge(list(objs), name), name, color, mat, **kw)


def parts_by_colour(groups, prefix, mat="SmoothPlastic", **kw):
    """Tag a {colour: [objs]} dict as one part per colour (names prefix1, prefix2, ...)."""
    out = []
    k = 0
    for col, objs in groups.items():
        objs = [o for o in objs if o is not None]
        if objs:
            k += 1
            out.append(part(objs, f"{prefix}{k}", col, mat, **kw))
    return out


def add(groups, col, *objs):
    """groups[col] += objs (flattening lists)."""
    lst = groups.setdefault(col, [])
    for o in objs:
        if isinstance(o, (list, tuple)):
            lst.extend(x for x in o if x is not None)
        elif o is not None:
            lst.append(o)
    return groups


def rbox(size, loc, bevel=0.04, segments=1, rot=(0, 0, 0)):
    """Box with a soft one-segment bevel (the batch's default chunky block)."""
    return ns.box(size, loc=loc, rot=rot, bevel=bevel, segments=segments)


def xform(objs, fn):
    """Apply fn(Vector) -> Vector to every vertex of the (applied) objects."""
    for o in (objs if isinstance(objs, (list, tuple)) else [objs]):
        ns.apply_all(o)
        for v in o.data.vertices:
            v.co = Vector(fn(v.co.copy()))
    return objs


def milkshake(loc, h=0.6, r=0.2, shake=SHAKE_PINK, straw=CYAN, verts=8, tilt=12.0, straw_yaw=35.0):
    """Soda-fountain tulip glass standing on loc (bottom centre), filled with a shake that
    rises into a whipped-cream swirl topped by a cherry, with a bendy straw.
    Returns {"glass": [obj], shake: [...], WHIP: [...], CHERRY: [...], straw: [...]} - the glass
    goes into a transparent Glass part, the rest are opaque colour groups."""
    x, y, z = loc
    # tulip glass: foot, stem, knop, bowl flaring to the rim (closed solid; Roblox shows the
    # shake through it when transparent)
    g = ns.lathe([(0.0, 0.0), (r * 0.75, 0.0), (r * 0.72, 0.03), (r * 0.18, 0.06), (r * 0.16, h * 0.2),
                  (r * 0.42, h * 0.27), (r * 0.62, h * 0.45), (r * 0.86, h * 0.75), (r, h), (0.0, h)],
                 verts=verts, loc=(x, y, z))
    # the shake fills the bowl to just under the rim (a lathe slightly inside the glass)
    s = ns.lathe([(0.0, h * 0.27), (r * 0.36, h * 0.3), (r * 0.56, h * 0.46), (r * 0.8, h * 0.75),
                  (r * 0.93, h * 0.985), (0.0, h * 0.985)], verts=verts, loc=(x, y, z))
    # whipped cream: a ribbed cone swirl rising out of the rim
    cz = z + h * 0.985
    cream = ns.lathe([(0.0, 0.0), (r * 0.98, 0.0), (r * 0.9, r * 0.35), (r * 0.62, r * 0.55), (r * 0.66, r * 0.72),
                      (r * 0.32, r * 0.95), (r * 0.12, r * 1.25), (0.0, r * 1.3)], verts=verts, loc=(x, y, cz))
    ch = spheres([(x + r * 0.05, y - r * 0.05, cz + r * 1.32)], r * 0.3, segs=6, rings=4)
    stem = pipe([(x + r * 0.07, y - r * 0.05, cz + r * 1.52), (x + r * 0.17, y - r * 0.02, cz + r * 1.68)],
                r * 0.04, sides=3)
    # bendy straw: up through the cream, kinks over at the top
    a = math.radians(straw_yaw)
    d = Vector((math.cos(a), math.sin(a), 0.0))
    p0 = Vector((x, y, z + h * 0.45)) + d * r * 0.25
    p1 = p0 + Vector((0, 0, h * 0.55 + r * 1.2)) + d * r * 0.35
    p2 = p1 + d * r * 0.55 + Vector((0, 0, r * 0.35))
    stw = pipe([tuple(p0), tuple(p1), tuple(p2)], r * 0.09, sides=5)
    return {"glass": [g], shake: [s], WHIP: [cream], CHERRY: [ch, stem], straw: [stw]}


# ---------------------------------------------------------------------------------------
# Mesh QA (from I_world/_qa.py)
# ---------------------------------------------------------------------------------------

def qa_check():
    """(inward, zfight) for the tagged objects in the scene. inward = faces whose normal ray
    hits the back of a face of the same connected shell first (they point into their own
    closed mesh and vanish in Roblox). zfight = faces whose centre lies inside another face
    in (nearly) the same plane (< 0.006 studs) with the same facing."""
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


def _print_qa(asset):
    from collections import Counter
    inward, zf = qa_check()
    print(f"[{asset}] QA: inward faces {len(inward)}, z-fight faces {len(zf)}")
    for x in inward[:8]:
        print("    inward", x)
    pairs = Counter(tuple(sorted((a, b))) for a, b, _c, _d in zf)
    for (a, b), n in pairs.most_common(12):
        ex = next(c for x, y, c, _d in zf if tuple(sorted((x, y))) == (a, b))
        print(f"    zfight {a} / {b}: {n} faces, e.g. at {ex}")
    return inward, zf


# ---------------------------------------------------------------------------------------
# Previews
# ---------------------------------------------------------------------------------------
VIEWS = {"floor": ((-35, 28, False), (150, 22, True)),
         "wall": ((-28, 12, False), (34, 8, True)),
         "hang": ((-35, -16, False), (40, -7, True))}


def preview(asset, out_dir, res=512, samples=16, views=None, mount="floor", backdrop="#D6CCB6"):
    """Two-panel preview like nslib.render_preview with per-mount views: floor props on a
    floor; wall props in front of a wall plane (colour `backdrop`) on their back face;
    hanging props seen from below under a ceiling plane."""
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True)
    views = views or VIEWS[mount]
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    span = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z, 0.5)
    if mount != "hang":
        bpy.ops.mesh.primitive_plane_add(size=max(span * 8, 8), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z - 0.001))
        fl = bpy.context.active_object
        fl.name = "Floor"
        fl.data.materials.append(ns.material("#3A3B42"))
    if mount == "wall":
        bpy.ops.mesh.primitive_plane_add(size=max(span * 6, 8), location=((lo.x + hi.x) / 2, hi.y + 0.003, lo.z))
        w = bpy.context.active_object
        w.rotation_euler = (math.radians(90), 0, 0)
        w.name = "FloorWall"
        w.data.materials.append(ns.material(backdrop))
    elif mount == "hang":
        bpy.ops.mesh.primitive_plane_add(size=max(span * 6, 8), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z + 0.003))
        c = bpy.context.active_object
        c.name = "FloorCeiling"
        c.data.materials.append(ns.material(backdrop))
    ns._setup_render(res, samples, transparent=False)
    for m in bpy.data.materials:   # Roblox Glass reflects far less than a roughness-0.05 BSDF
        if m.name.endswith("_Glass") and m.use_nodes and m.node_tree.nodes.get("Principled BSDF"):
            b = m.node_tree.nodes["Principled BSDF"]
            b.inputs["Roughness"].default_value = 0.08
            b.inputs["Specular IOR Level"].default_value = 0.1
    paths = []
    for i, (yaw, pitch, with_ref) in enumerate(views):
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim", "RefCube")):
                bpy.data.objects.remove(o, do_unlink=True)
        fit = list(objs)
        if with_ref:
            rz = (hi.z - 1.0) if mount == "hang" else lo.z
            ry = hi.y - 0.5 if mount == "wall" else (lo.y + hi.y) / 2
            ref = ns.box((1, 1, 1), loc=(lo.x - 0.7, ry, rz + 0.5), bevel=0.0, name="RefCube")
            ref.data.materials.append(ns.material("#9A9AA6"))
            fit.append(ref)
        flo, fhi = ns.bbox_world(fit)
        cam, ctr, dist = ns._camera_fit(flo, fhi, yaw, pitch)
        k = math.radians(yaw)
        up = 0.9 if pitch >= 0 else -0.6
        ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), up)) * dist,
                  60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3 if pitch >= 0 else -0.3)) * dist,
                  20 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        ns._light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.8 if pitch >= 0 else -0.2)) * dist,
                  35 * dist ** 2 / 9, size=dist * 0.4, target=ctr)
        p = os.path.join(out_dir, f"{asset}_{i}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    ns._clear_rig()   # also removes the floor / wall / ceiling planes (names start with "Floor")
    ims = [Image.open(p).convert("RGB") for p in paths]
    combo = Image.new("RGB", (res * len(ims), res))
    for i, im in enumerate(ims):
        combo.paste(im, (i * res, 0))
    out = os.path.join(out_dir, f"{asset}_preview.png")
    combo.save(out)
    for p in paths:
        os.remove(p)
    return out


def _print_parts(asset):
    dg = bpy.context.evaluated_depsgraph_get()
    tot = 0
    for o in sorted(ns._tagged_objects(), key=lambda o: o.name):
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        n = len(me.loop_triangles)
        tot += n
        print(f"  [{asset}] {o.name:22s} {n:5d} tris  {o['ns_material']:13s} {o['ns_color']} role={o.get('ns_role')}"
              f" collide={o['ns_can_collide']}")
        o.evaluated_get(dg).to_mesh_clear()
    lo, hi = ns.bbox_world(ns._tagged_objects())
    print(f"  [{asset}] bbox lo {tuple(round(c, 3) for c in lo)} hi {tuple(round(c, 3) for c in hi)} total {tot}")


def socket_check(asset, sockets, views=((-35, 28),), res=448, samples=8, size=0.6):
    """Render the asset with magenta arrow markers at every socket (one image per view)."""
    from PIL import Image
    markers = []
    for name, spec in sockets.items():
        if len(spec) == 2 and not isinstance(spec[0], (int, float)):
            loc, yaw = spec
        else:
            loc, yaw = spec, 0.0
        markers += L._arrow(loc, yaw, size=size)
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    ns._setup_render(res, samples)
    out_dir = os.path.join(PREVIEWS, "_checks")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, (yaw, pitch) in enumerate(views):
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cam, ctr, dist = ns._camera_fit(lo, hi, yaw, pitch)
        k = math.radians(yaw)
        ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * dist,
                  60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3)) * dist,
                  25 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        p = os.path.join(out_dir, f"{asset}_sock{i}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    ns._clear_rig()
    for o in markers:
        bpy.data.objects.remove(o, do_unlink=True)
    ims = [Image.open(p).convert("RGB") for p in paths]
    combo = Image.new("RGB", (res * len(ims), res))
    for i, im in enumerate(ims):
        combo.paste(im, (i * res, 0))
    out = os.path.join(out_dir, f"{asset}_sockets.png")
    combo.save(out)
    for p in paths:
        os.remove(p)
    return out


def run(build, asset, sockets=None, mount="floor", budget=2000, views=None, backdrop=None,
        socket_views=((-35, 28),), **export_kw):
    """Standard O_rooms entry: build -> preview (NS_QUICK=1 fast, to _quick/) -> mesh QA
    (NS_QA=1, and on export) -> socket check (NS_SOCKETS=1) -> export (NS_EXPORT=1).
    mount "wall" / "hang" set the pivot (bottom-centre of the back face / top-centre) unless
    `pivot` is passed. Socket positions are Blender world points (exported relative to the pivot)."""
    ns.reset()
    extra = build() or {}
    tris = ns.tri_count()
    flag = "" if budget is None or tris <= budget else f"   *** OVER BUDGET ({budget}) ***"
    print(f"[{asset}] triangles: {tris}" + (f" / {budget}" if budget else "") + flag)
    if os.environ.get("NS_PARTS") == "1":
        _print_parts(asset)
    exporting = os.environ.get("NS_EXPORT") == "1"
    if os.environ.get("NS_QA") == "1" or exporting:
        _print_qa(asset)
    if os.environ.get("NS_NORENDER") != "1":
        quick = os.environ.get("NS_QUICK") == "1"
        res, spp = (384, 8) if quick else (512, 16)
        out_dir = os.path.join(PREVIEWS, "_quick") if quick else PREVIEWS
        bd = backdrop or ("#D6CCB6" if mount == "wall" else "#CFC6B4")
        prev = preview(asset, out_dir, res=res, samples=spp, views=views, mount=mount, backdrop=bd)
        print(f"[{asset}] preview: {os.path.abspath(prev)}")
    if sockets and os.environ.get("NS_SOCKETS") == "1":
        print(f"[{asset}] sockets: {socket_check(asset, sockets, views=socket_views)}")
    if exporting:
        kw = dict(export_kw)
        kw.update(extra.get("export", {}))
        if mount in ("wall", "hang") and "pivot" not in kw:
            lo, hi = ns.bbox_world(ns._tagged_objects())
            if mount == "wall":
                kw["pivot"] = ((lo.x + hi.x) / 2, hi.y, lo.z)
            else:
                kw["pivot"] = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z)
            print(f"[{asset}] pivot ({mount}): {tuple(round(c, 3) for c in kw['pivot'])}")
        doc = ns.export_asset(asset, BATCH, group=GROUP, sockets=sockets, **kw)
        print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']} "
              f"(Roblox x,y,z = W,H,D)")
        for p in doc["parts"]:
            print(f"    part {p['name']:20s} {p['material']:13s} role={p['role']} collide={p['canCollide']} "
                  f"tris={p['tris']}")
        if doc.get("sockets"):
            print(f"    sockets {doc['sockets']}")
    return extra


def contact_sheet(cols=3, thumb=340):
    """Labelled grid of every final <asset>_preview.png in previews/O_rooms -> _contact.png
    (label = asset name + exported size / tris from manifests/O_rooms.json)."""
    import json
    from PIL import Image, ImageDraw, ImageFont
    files = sorted(f for f in os.listdir(PREVIEWS) if f.endswith("_preview.png"))
    man = {}
    mpath = os.path.join(ns.REPO, "manifests", f"{BATCH}.json")
    if os.path.exists(mpath):
        with open(mpath) as f:
            man = json.load(f)
    try:
        font = ImageFont.truetype(K.FONT_REGULAR, 20)
    except OSError:
        font = ImageFont.load_default()
    tw, lab = thumb * 2, 32
    th = thumb + lab
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, th * rows), (24, 26, 30))
    draw = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        name = f.replace("_preview.png", "")
        im = Image.open(os.path.join(PREVIEWS, f)).convert("RGB")
        im = im.resize((tw, int(im.height * tw / im.width)))
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(im, (x, y + lab))
        e = man.get(name)
        info = f"   {e['size'][0]:g} x {e['size'][1]:g} x {e['size'][2]:g}  |  {e['tris']} tris" if e else ""
        draw.text((x + 10, y + 5), name + info, fill=(235, 235, 235), font=font)
    out = os.path.join(PREVIEWS, "_contact.png")
    sheet.save(out)
    return out


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "contact":
    print(contact_sheet())
