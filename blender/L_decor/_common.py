"""_common — shared helpers for the L_decor batch (diner back-of-house + outdoor decor).

Import from an asset script in this folder with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Builds on blender/lib/nslib.py and re-uses the B_shop shape helpers (fillet, rrect, prism,
pipe, ring_slab, text_mesh, ...) plus C_lobby's small builders (rod, text, catenary, place,
disc, annulus, ...), loaded under their own module names the way C_lobby loads B_shop's.

Conventions used by every L_decor asset
  * 1 stud = 1 Blender unit, Z up, the user-facing side looks at Blender -Y.
  * Floor props: pivot bottom-centre. Wall props: pivot = bottom-centre of the BACK face
    (+Y side, touches the wall), modelled with the back face on y = 0. Hanging props (pot
    rack, heat lamp): pivot = TOP (z = 0, everything hangs below).
  * nslib merges role-less parts per material at export (vertex colours); only parts code
    must find (glass, lamps, speaker grille, vinyl recolour) carry a `recolor` role.
  * can_collide only on big furniture (vending machine, fridge, couch, filing cabinet,
    box stacks).
  * Part names must not start with Key/Fill/Rim/Floor/RefCube/PreviewCam (nslib's preview
    deletes objects with those prefixes) - `part()` asserts this.
  * Env: NS_QUICK=1 fast low-res preview into previews/L_decor/_quick, NS_SOCKETS=1 socket
    check render (previews/L_decor/_checks), NS_PARTS=1 prints the part list,
    NS_NORENDER=1 skips the preview, NS_EXPORT=1 exports.
"""
from __future__ import annotations

import importlib.util
import math
import os
import sys

sys.dont_write_bytecode = True   # don't drop .pyc caches into other batches' folders

import bpy  # noqa: F401  (must load before bmesh in the bpy module build)
import bmesh
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "lib"))
import nslib as ns  # noqa: E402

try:  # previews / contact sheet need Pillow; the bpy venv may not ship it
    import PIL  # noqa: F401
except ImportError:  # borrow the system interpreter's copy (same CPython minor), appended last
    import glob
    _v = f"python{sys.version_info.major}.{sys.version_info.minor}"
    for _sp in glob.glob(f"/usr/local/lib/{_v}/site-packages") + glob.glob(f"/usr/lib/{_v}/site-packages"):
        if os.path.isdir(os.path.join(_sp, "PIL")) and _sp not in sys.path:
            sys.path.append(_sp)
            break


def _load(modname, rel):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(_HERE, "..", rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# B_shop helpers and C_lobby builders under their own module names (all batches call theirs `_common`)
S = _load("shop_common", os.path.join("B_shop", "_common.py"))
L = _load("lobby_common", os.path.join("C_lobby", "_common.py"))

fillet, rrect, circle_pts, ellipse_pts = S.fillet, S.rrect, S.circle_pts, S.ellipse_pts
prism, slab, pipe, round_path, ring_slab = S.prism, S.slab, S.pipe, S.round_path, S.ring_slab
text_mesh, fit_text_width, bbox_of, merge, band = S.text_mesh, S.fit_text_width, S.bbox_of, S.merge, S.band
rod, text, catenary, place, yaw_point = L.rod, L.text, L.catenary, L.place, L.yaw_point
disc, annulus, arc_solid, arc_profile_sweep = L.disc, L.annulus, L.arc_solid, L.arc_profile_sweep
FONT_BOLD, FONT_BOLD_ITALIC = S.FONT_BOLD, S.FONT_BOLD_ITALIC

BATCH = "L_decor"
GROUP = "Shop"
PREVIEWS = os.path.join(ns.REPO, "..", "previews", BATCH)

# ---------------------------------------------------------------------------------------
# Palette (STYLE.md section 1 + shared brief extras; environment a step greyer than food)
# ---------------------------------------------------------------------------------------
CREAM = "#EFE6D2"
CREAM_SHADE = "#DCD0B8"
STAINLESS = "#B9C0C6"
CHROME = "#D3D8DC"
NAVY = "#1E2A44"
NAVY_DEEP = "#141C2E"
PINK = "#FF4FA3"
CYAN = "#38E1FF"
BRAND = "#E8502A"          # STACKHOUSE red-orange
BRAND_DARK = "#B83D22"
MUSTARD = "#F2B33D"
BRICK = "#8A3E30"
CHARCOAL = "#3A3D42"
LAMP_WARM = "#FFD99A"      # warm bulbs (Neon)
FOLIAGE = ("#3E6B35", "#4E8A3A", "#2F5229")
BARK = "#5A3926"
BASE_DARK = "#2B2D33"
RUBBER = "#1D1E22"
VINYL_RED = "#B8323C"
WOOD = "#8A5A3B"
WOOD_LIGHT = "#A8774E"
WOOD_DARK = "#5A3926"
PAPER = "#F3EEE2"
CARDBOARD = "#B48A5C"
CARDBOARD_DARK = "#8E6A44"
TAPE = "#D9B77E"
CORK = "#B9895A"
GLASS = "#A9D3E0"
CONCRETE = "#8E8C86"
SOIL = "#3F2F25"
DARK_VOID = "#121317"
INK = "#24262B"            # printed / marker lines
STICKY = "#F4D85A"
SAFETY_YELLOW = "#F6C823"  # caution yellow (wet-floor sign, mop bucket)
EXT_RED = "#C8302C"        # fire-safety red

FORBIDDEN = ("PreviewCam", "Key", "Fill", "Rim", "RefCube", "Floor")


# ---------------------------------------------------------------------------------------
# Small builders
# ---------------------------------------------------------------------------------------

def part(objs, name, color, mat="SmoothPlastic", **kw):
    """Apply + join + tag in one call (objs: object or list, nested lists / None ok)."""
    assert not name.startswith(FORBIDDEN), name
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    return ns.tag(merge(list(objs), name), name, color, mat, **kw)


def loft(rings, cap0=True, cap1=True, name="Loft"):
    """Skin closed rings [(x, y, z), ...] (same point count, bottom to top) into one mesh,
    optionally capping the first / last ring. Coincident rings collapse cleanly."""
    bm = bmesh.new()
    vr = [[bm.verts.new(p) for p in r] for r in rings]
    n = len(rings[0])
    for a, b in zip(vr[:-1], vr[1:]):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([a[k], a[j], b[j], b[k]])
    if cap0:
        bm.faces.new(list(reversed(vr[0])))
    if cap1:
        bm.faces.new(vr[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def lathe_open(profile, verts=12, loc=(0, 0, 0), normals="out", name="LatheOpen"):
    """Revolve [(r, z), ...] around Z WITHOUT end caps (lamp shades, bowls). normals "out"
    points the faces away from the axis, "in" toward it (single-sided surfaces in Roblox)."""
    bm = bmesh.new()
    rings = []
    for i in range(verts):
        a = 2 * math.pi * i / verts
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
    for i in range(verts):
        r0, r1 = rings[i], rings[(i + 1) % verts]
        for j in range(len(profile) - 1):
            bm.faces.new([r0[j], r1[j], r1[j + 1], r0[j + 1]])
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        radial = Vector((c.x, c.y, 0.0))
        d = f.normal.dot(radial)
        if (normals == "out" and d < 0) or (normals == "in" and d > 0):
            f.normal_flip()
    return ns.from_bmesh(bm, name, loc)


def ring3(pts2d, z, dx=0.0, dy=0.0):
    """2D outline (x, y) -> 3D ring at height z."""
    return [(x + dx, y + dy, z) for x, y in pts2d]


def poly(pts3d, name="Poly"):
    """One single-sided polygon (decals: lines, scribbles, pictograms). Winding decides the
    facing; use quad_xz()/strip_xz() for decals on a -Y face."""
    bm = bmesh.new()
    bm.faces.new([bm.verts.new(p) for p in pts3d])
    return ns.from_bmesh(bm, name)


def quad_xz(x0, x1, z0, z1, y, name="Quad"):
    """Single-sided rectangle in the XZ plane at depth y, facing -Y."""
    return poly([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], name)


def strip_xz(p0, p1, w, y, name="Strip"):
    """Single-sided straight stroke from p0 to p1 (x, z) of width w at depth y, facing -Y."""
    a, b = Vector((p0[0], p0[1])), Vector((p1[0], p1[1]))
    d = (b - a).normalized()
    n = Vector((-d.y, d.x)) * (w / 2)
    pts = [a - n, b - n, b + n, a + n]
    return poly([(p.x, y, p.y) for p in pts], name)


def face_dir(obj, axis="-Y"):
    """Make every face of a single-sided decal point along `axis` ('-Y', '+Y', '+Z', '-X', '+X')."""
    sign = -1 if axis[0] == "-" else 1
    idx = "XYZ".index(axis[1])
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    for f in bm.faces:
        if f.normal[idx] * sign < 0:
            f.normal_flip()
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def turn_y(objs, deg, cx, cz):
    """Rotate objects about a Y-parallel axis through (cx, *, cz) — tilts papers pinned on a
    wall face (positive = counter-clockwise as seen from the front, -Y)."""
    a = math.radians(-deg)
    c, s = math.cos(a), math.sin(a)
    for o in (objs if isinstance(objs, (list, tuple)) else [objs]):
        ns.apply_all(o)
        for v in o.data.vertices:
            x, z = v.co.x - cx, v.co.z - cz
            v.co.x, v.co.z = cx + x * c + z * s, cz - x * s + z * c
    return objs


def jbox(size, loc, rot=(0, 0, 0), bevel=0.03, segments=1):
    """Box shorthand with a small bevel."""
    return ns.box(size, loc=loc, rot=rot, bevel=bevel, segments=segments)


def carton(w, d, h, loc=(0, 0, 0), yaw=0.0, open_top=False, flap_angle=118.0, tape=True, bevel=0.03):
    """Cardboard box standing on loc (bottom-centre), turned by yaw degrees.
    Closed: body + a tape strip over the top seam that runs down the front and back faces.
    Open: a shorter solid body + a thin wall ring + dark inside plate + four flaps folded
    outward by flap_angle (90 = flat out). Returns {"body", "tape", "inside", "flaps"} lists
    (flaps share the body colour)."""
    out = {"body": [], "tape": [], "inside": [], "flaps": []}
    if not open_top:
        out["body"].append(ns.box((w, d, h), loc=(0, 0, h / 2), bevel=bevel, segments=1))
        if tape:
            tw, t = min(0.3, w * 0.22), 0.012
            drop = min(0.38, h * 0.3)
            out["tape"].append(ns.box((tw, d + 2 * t, t), loc=(0, 0, h + t / 2 - 0.002), bevel=0.0))
            for sy in (-1, 1):
                out["tape"].append(ns.box((tw, t, drop), loc=(0, sy * (d / 2 + t / 2 - 0.002), h - drop / 2 + 0.004),
                                          bevel=0.0))
    else:
        wall_h, wt = min(0.3, h * 0.35), 0.045
        out["body"].append(ns.box((w, d, h - wall_h), loc=(0, 0, (h - wall_h) / 2), bevel=bevel, segments=1))
        outer = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
        inner = [(-w / 2 + wt, -d / 2 + wt), (w / 2 - wt, -d / 2 + wt), (w / 2 - wt, d / 2 - wt), (-w / 2 + wt, d / 2 - wt)]
        out["body"].append(ring_slab(outer, inner, "z", h - wall_h - 0.01, h))
        out["inside"].append(ns.box((w - 2 * wt + 0.01, d - 2 * wt + 0.01, 0.02), loc=(0, 0, h - wall_h + 0.005),
                                    bevel=0.0))
        ft = 0.035
        reach = d * 0.48
        b = math.radians(flap_angle)   # measured from straight up: 90 = flat out, >90 droops
        for axis, sgn in (("y", -1), ("y", 1), ("x", -1), ("x", 1)):
            # built standing up from its hinge line (the top outer edge), turned outward about it
            if axis == "y":
                fl = ns.box((w - 0.05, ft, reach), loc=(0, 0, reach / 2), bevel=0.0)
                ns.apply_all(fl)
                fl.rotation_euler = (-sgn * b, 0, 0)
                fl.location = (0, sgn * (d / 2 - ft / 2), h)
            else:
                fl = ns.box((ft, d - 0.05, reach), loc=(0, 0, reach / 2), bevel=0.0)
                ns.apply_all(fl)
                fl.rotation_euler = (0, sgn * b, 0)
                fl.location = (sgn * (w / 2 - ft / 2), 0, h)
            ns.apply_all(fl)
            out["flaps"].append(fl)
    for lst in out.values():
        place(lst, loc=loc, yaw=yaw)
    return out


def screen_meta(part_name, w, h, face="Front"):
    return {"part": part_name, "face": face, "screen_size": [round(w, 3), round(h, 3)]}


# ---------------------------------------------------------------------------------------
# Previews (configurable views; wall backdrop for wall props, ceiling + low views for
# hanging props)
# ---------------------------------------------------------------------------------------
VIEWS_FLOOR = ((-35, 28, False), (150, 22, True))
VIEWS_WALL = ((-35, 18, False), (32, 10, True))
VIEWS_HANG = ((-35, -14, False), (40, -6, True))
VIEWS_SMALL = ((-35, 24, False), (35, 12, True))


def preview(asset, out_dir, res=512, samples=16, views=VIEWS_FLOOR, backdrop=None, floor=True):
    """Two-panel preview like nslib.render_preview but with configurable (yaw, pitch, ref)
    views. backdrop: None | "wall" (cream wall plane on the back face, y = bbox max) |
    "ceiling" (plane on z = bbox max, for hanging props)."""
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True)
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    span = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z, 0.5)
    extras = []
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=max(span * 8, 8),
                                         location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z - 0.001))
        fl = bpy.context.active_object
        fl.name = "Floor"
        fl.data.materials.append(ns.material("#3A3B42"))
    if backdrop == "wall":
        bpy.ops.mesh.primitive_plane_add(size=max(span * 6, 8), location=((lo.x + hi.x) / 2, hi.y + 0.002, lo.z))
        w = bpy.context.active_object
        w.rotation_euler = (math.radians(90), 0, 0)
        w.name = "FloorWall"
        w.data.materials.append(ns.material("#D6CCB6"))
        extras.append(w)
    elif backdrop == "ceiling":
        bpy.ops.mesh.primitive_plane_add(size=max(span * 6, 8), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2,
                                                                          hi.z + 0.002))
        c = bpy.context.active_object
        c.name = "FloorCeiling"
        c.data.materials.append(ns.material("#D6CCB6"))
        extras.append(c)
    ns._setup_render(res, samples, transparent=False)
    # preview only: Roblox Glass reflects far less than a roughness-0.05 Principled surface,
    # which would hide everything behind a transparent pane in these renders
    for m in bpy.data.materials:
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
            ref = ns.box((1, 1, 1), loc=(lo.x - 0.7, (lo.y + hi.y) / 2 if backdrop != "wall" else hi.y - 0.5,
                                         lo.z + 0.5), bevel=0.0, name="RefCube")
            ref.data.materials.append(ns.material("#9A9AA6"))
            fit.append(ref)
        flo, fhi = ns.bbox_world(fit)
        cam, ctr, dist = ns._camera_fit(flo, fhi, yaw, pitch)
        k = math.radians(yaw)
        up = 0.9 if pitch >= 0 else -0.5
        ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), up)) * dist,
                  60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3 if pitch >= 0 else -0.3)) * dist,
                  20 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        ns._light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.8)) * dist, 35 * dist ** 2 / 9,
                  size=dist * 0.4, target=ctr)
        p = os.path.join(out_dir, f"{asset}_{i}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    ns._clear_rig()   # also removes the floor and the backdrop planes (names start with "Floor")
    ims = [Image.open(p) for p in paths]
    combo = Image.new("RGB", (res * len(ims), res))
    for i, im in enumerate(ims):
        combo.paste(im.convert("RGB"), (i * res, 0))
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
        print(f"  [{asset}] {o.name:20s} {n:5d} tris  {o['ns_material']:13s} role={o.get('ns_role')} "
              f"collide={o['ns_can_collide']}")
        o.evaluated_get(dg).to_mesh_clear()
    lo, hi = ns.bbox_world(ns._tagged_objects())
    print(f"  [{asset}] bbox lo {tuple(round(c, 3) for c in lo)} hi {tuple(round(c, 3) for c in hi)} total {tot}")


def socket_check(asset, sockets, views=((-35, 28),), res=448, samples=8):
    """Render the asset with magenta arrow markers at every socket (previews/L_decor/_checks)."""
    from PIL import Image
    markers = []
    for name, spec in sockets.items():
        if len(spec) == 2 and not isinstance(spec[0], (int, float)):
            loc, yaw = spec
        else:
            loc, yaw = spec, 0.0
        markers += L._arrow(loc, yaw, size=0.4)
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


def run(build, asset, sockets=None, views=None, backdrop=None, socket_views=((-35, 28),),
        budget=None, mount="floor", **export_kw):
    """Standard L_decor entry: build -> preview (quick with NS_QUICK=1) -> optional socket
    check render -> export when NS_EXPORT=1. `budget` = triangle budget (warns if over).
    mount: "floor" (pivot bottom-centre, nslib default), "wall" (pivot = bottom-centre of the
    back face, +Y; wall views + backdrop) or "hang" (pivot = top-centre; views from below).
    Socket positions are Blender world points (exported relative to the pivot)."""
    if views is None:
        views = {"wall": VIEWS_WALL, "hang": VIEWS_HANG}.get(mount, VIEWS_FLOOR)
    if backdrop is None:
        backdrop = {"wall": "wall", "hang": "ceiling"}.get(mount)
    ns.reset()
    extra = build() or {}
    tris = ns.tri_count()
    flag = "" if budget is None or tris <= budget else f"   *** OVER BUDGET ({budget}) ***"
    print(f"[{asset}] triangles: {tris}" + (f" / {budget}" if budget else "") + flag)
    if os.environ.get("NS_PARTS") == "1":
        _print_parts(asset)
    if os.environ.get("NS_NORENDER") != "1":
        quick = os.environ.get("NS_QUICK") == "1"
        res, spp = (384, 8) if quick else (512, 16)
        out_dir = os.path.join(PREVIEWS, "_quick") if quick else PREVIEWS
        prev = preview(asset, out_dir, res=res, samples=spp, views=views, backdrop=backdrop,
                       floor=(mount != "hang"))
        print(f"[{asset}] preview: {prev}")
    if sockets and os.environ.get("NS_SOCKETS") == "1":
        print(f"[{asset}] sockets: {socket_check(asset, sockets, views=socket_views)}")
    if os.environ.get("NS_EXPORT") == "1":
        kw = dict(export_kw)
        kw.update(extra.get("export", {}))
        if mount in ("wall", "hang") and "pivot" not in kw:
            lo, hi = ns.bbox_world(ns._tagged_objects())
            if mount == "wall":   # bottom-centre of the back face (+Y)
                kw["pivot"] = ((lo.x + hi.x) / 2, hi.y, lo.z)
            else:                 # top-centre (hangs from the ceiling / header)
                kw["pivot"] = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z)
            print(f"[{asset}] pivot ({mount}): {tuple(round(c, 3) for c in kw['pivot'])}")
        doc = ns.export_asset(asset, BATCH, group=GROUP, sockets=sockets, **kw)
        print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']} "
              f"(Roblox x,y,z = W,H,D)")
        for p in doc["parts"]:
            print(f"    part {p['name']:18s} {p['material']:13s} role={p['role']} collide={p['canCollide']} "
                  f"tris={p['tris']}")
        if doc.get("sockets"):
            print(f"    sockets {doc['sockets']}")
    return extra
