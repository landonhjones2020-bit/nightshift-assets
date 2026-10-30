"""_common — shared helpers for the K_shop batch (double-height dining room modules + decor).

Import from an asset script in this folder with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Builds on blender/lib/nslib.py and re-uses the B_shop batch (palette, WALL_PRESETS,
BACK_PRESETS, wainscot constants and trim builders, loaded as `S`) and the C_lobby shape
helpers (rod, catenary, text, sandwich_icon, place, screen_meta ..., loaded as `L`), so
the new pieces share the shop's family look and the tall wall modules tile with the
existing 12-tall Shop_Wall / Shop_WallWindow / Shop_WallDoorway.

Conventions used by every K_shop asset
  * 1 stud = 1 Blender unit, Z up, the room-facing / user-facing side looks at Blender -Y.
  * Wall modules: pivot on the wall centre line, bottom; same part roles (wall_back,
    wall_upper, wall_tile, wall_grout, wall_base, wall_stripe, wall_back_base,
    wall_back_band, glass) and meta keys as the B_shop modules. The lower 12 studs are
    built with the very same B_shop helpers; the crown moves to the top of the module.
  * Wall-mounted props pivot at the bottom-centre of their BACK face (+Y, touches the wall).
  * Ceiling-hung fittings pivot at the TOP of their canopy (z = 0, everything hangs below).
  * nslib merges role-less parts per material at export (vertex colours); only parts code
    must find carry a `recolor` role. Part names must not start with
    Key/Fill/Rim/Floor/RefCube/PreviewCam (nslib's preview deletes those) - part() asserts.
  * Env: NS_QUICK=1 fast low-res preview (to previews/K_shop/_quick), NS_SOCKETS=1 socket
    check render (previews/K_shop/_checks), NS_PARTS=1 prints the parts, NS_EXPORT=1 exports.
"""
from __future__ import annotations

import importlib.util
import math
import os
import sys

import bpy  # noqa: F401  (must load before bmesh in the bpy module build)
import bmesh  # noqa: F401
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "lib"))
import nslib as ns  # noqa: E402

# PIL (previews / contact sheet) is installed in the system interpreter, not in bpyenv:
# append that site dir at the END of sys.path so bpyenv's own packages keep precedence.
try:
    import PIL  # noqa: F401
except ImportError:
    for _site in ("/usr/local/lib/python3.13/site-packages",):
        if os.path.isdir(_site) and _site not in sys.path:
            sys.path.append(_site)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(_HERE, "..", rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# B_shop helpers + C_lobby helpers, loaded under their own module names (every batch calls
# its helper module `_common`)
S = _load("shop_common", os.path.join("B_shop", "_common.py"))
L = _load("lobby_common", os.path.join("C_lobby", "_common.py"))

fillet, rrect, circle_pts, ellipse_pts = S.fillet, S.rrect, S.circle_pts, S.ellipse_pts
prism, slab, pipe, round_path, ring_slab = S.prism, S.slab, S.pipe, S.round_path, S.ring_slab
text_mesh, fit_text_width, bbox_of, merge = S.text_mesh, S.fit_text_width, S.bbox_of, S.merge
tiles, skin, square_ring, band = S.tiles, S.skin, S.square_ring, S.band
rod, catenary, text, sandwich_icon, place = L.rod, L.catenary, L.text, L.sandwich_icon, L.place
screen_meta, annulus, disc, yaw_point = L.screen_meta, L.annulus, L.disc, L.yaw_point
arc_solid, arc_profile_sweep = L.arc_solid, L.arc_profile_sweep
FONT_BOLD, FONT_BOLD_ITALIC = S.FONT_BOLD, S.FONT_BOLD_ITALIC
FONT_REGULAR = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"

BATCH = "K_shop"
GROUP = "Shop"
PREVIEWS = os.path.join(ns.REPO, "..", "previews", BATCH)
FORBIDDEN = ("PreviewCam", "Key", "Fill", "Rim", "RefCube", "Floor")

# ---------------------------------------------------------------------------------------
# Palette (STYLE.md §1 + the B_shop / C_lobby derived shades)
# ---------------------------------------------------------------------------------------
CREAM, CREAM_SHADE = S.CREAM, S.CREAM_SHADE
STAINLESS, CHROME = S.STAINLESS, S.CHROME
NAVY, NAVY_DEEP = S.NAVY, S.NAVY_DEEP
PINK, CYAN, MUSTARD, BRAND = S.PINK, S.CYAN, S.MUSTARD, S.BRAND
BRAND_DARK = L.BRAND_DARK
CHARCOAL, RUBBER, BASE_DARK = S.CHARCOAL, S.RUBBER, S.BASE_DARK
LAMINATE, PAPER, CORK = S.LAMINATE, S.PAPER, S.CORK
WOOD, WOOD_LIGHT, WOOD_DARK = S.WOOD, S.WOOD_LIGHT, S.WOOD_DARK
GLASS, SCREEN = S.GLASS, L.SCREEN
GOLD, BRASS = L.GOLD, L.BRASS
CHALK = L.CHALK
LAMP_WARM = L.LAMP_WARM
LETTUCE, TOMATO, CHEESE, BUN, BUN_DARK = L.LETTUCE, L.TOMATO, L.CHEESE, L.BUN, L.BUN_DARK
VINYL_RED, VINYL_TEAL = S.VINYL_RED, S.VINYL_TEAL
BLACK = L.BLACK
DARK_VOID = S.DARK_VOID
CHECK_DARK, CHECK_LIGHT = S.CHECK_DARK, S.CHECK_LIGHT
TEAL_TILE = S.TEAL_TILE

# ---------------------------------------------------------------------------------------
# Wall-module layout (front face of a module; B_shop heights + the tall zone)
# ---------------------------------------------------------------------------------------
WALL_W, WALL_H, WALL_T = S.WALL_W, S.WALL_H, S.WALL_T   # 8 x 12 x 1 (existing modules)
FACE_Y = S.FACE_Y
BASE_TOP, TILE_TOP, CHECK_TOP = S.BASE_TOP, S.TILE_TOP, S.CHECK_TOP
RAIL_H, RAIL_Z, SILL_Z = S.RAIL_H, S.RAIL_Z, S.SILL_Z
STRIPE_Z = S.STRIPE_Z          # brand pinstripes 9.62 / 9.86 (same line as the 12-tall modules)
WALL_PRESETS, BACK_PRESETS = S.WALL_PRESETS, S.BACK_PRESETS

TALL_H = 20.0                  # double-height dining room: ceiling underside at 20
TALL_CROWN_Z = 19.45           # crown bottom on the tall modules (top = 20)
UPPER_H = 8.0                  # Shop_WallUpper band (sits on a 12-tall module: 12 .. 20)
FRIEZE_Z = 12.0                # frieze rail centre on the tall modules: the 12-stud line where the
                               # old crown / the kitchen ceiling sits, level with the window transoms


def wall_presets_meta():
    return S.wall_presets_meta()


def crown_tall(x0, x1, z0=TALL_CROWN_Z, z1=TALL_H, face_y=FACE_Y):
    """The B_shop crown moulding profile, at the top of a tall module."""
    return prism(S.crown_profile(face_y - 0.03, z0, z1), "x", x0, x1)


def frieze_rail(x0, x1, z=FRIEZE_Z, face_y=FACE_Y):
    """Slim bullnose rail (the chair-rail profile) marking the 12-stud line on tall walls.
    0.1 proud of the skin (front at y -0.63), so its ends bury inside window/door casings."""
    return prism(S.chair_rail_profile(face_y - 0.03, z, h=0.24, proud=0.1), "x", x0, x1)


def back_band(x0, x1, z=FRIEZE_Z, face_y=-FACE_Y):
    """Flat band on the back (+Y) face at the 12-stud line (the back_trim band profile; tagged
    into BackBand / role wall_back_band by tag_wall_set)."""
    pts = [(face_y, z - 0.12), (face_y + 0.08, z - 0.12), (face_y + 0.08, z + 0.12), (face_y, z + 0.12)]
    b = prism(fillet(pts, [0, 0.03, 0.03, 0], 1), "x", x0, x1)
    b["ns_back_band"] = True
    return b


def stripes(x0, x1, face_y=FACE_Y, zs=STRIPE_Z):
    """Brand pinstripes (the B_shop pair: 0.13 + 0.07 tall) at heights zs."""
    out = []
    for zc, h in ((zs[0], 0.13), (zs[1], 0.07)):
        pts = fillet([(face_y - 0.03, zc - h / 2), (face_y - 0.07, zc - h / 2), (face_y - 0.07, zc + h / 2),
                      (face_y - 0.03, zc + h / 2)], [0, 0.02, 0.02, 0], 1)
        out.append(prism(pts, "x", x0, x1))
    return out


def tag_wall_set(d, collide=False):
    return S.tag_wall_set(d, collide=collide)


# ---------------------------------------------------------------------------------------
# Small builders
# ---------------------------------------------------------------------------------------

def part(objs, name, color, mat="SmoothPlastic", **kw):
    """Apply + join + tag in one call (objs: object or list, nested lists / None ok)."""
    assert not name.startswith(FORBIDDEN), name
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    return ns.tag(merge(list(objs), name), name, color, mat, **kw)


def star(r_out, r_in, cx, cz, n=5, a0=90.0):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(a0 + 180.0 * i / n)
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def burst(r_out, r_in, cx, cz, n=12, a0=90.0):
    """Starburst outline (n points) in the XZ plane, for retro ad posters."""
    return star(r_out, r_in, cx, cz, n=n, a0=a0)


def flip_y(obj, y0=0.0):
    """Mirror an object's mesh through the plane y = y0 (keeps normals outward)."""
    ns.apply_all(obj)
    for v in obj.data.vertices:
        v.co.y = 2 * y0 - v.co.y
    obj.data.flip_normals()
    return obj


def lathe_ring(profile, verts=20, loc=(0, 0, 0), name="LatheRing"):
    """Revolve a CLOSED (r, z) profile about Z with no end caps (rims, bezels, rings)."""
    bm = bmesh.new()
    rings = []
    for i in range(verts):
        a = 2 * math.pi * i / verts
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
    n = len(profile)
    for i in range(verts):
        r0, r1 = rings[i], rings[(i + 1) % verts]
        for j in range(n):
            jj = (j + 1) % n
            bm.faces.new([r0[j], r1[j], r1[jj], r0[jj]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name, loc=loc)


def lathe_open(profile, verts=20, loc=(0, 0, 0), name="LatheOpen", outward=True):
    """Revolve an OPEN (r, z) profile about Z with no caps (domes, shades, bowls). A profile
    point with r = 0 closes to a single pole vertex. Normals point away from the axis
    (outward=True) or toward it."""
    bm = bmesh.new()
    rings = []
    for i in range(verts):
        a = 2 * math.pi * i / verts
        rings.append([(r * math.cos(a), r * math.sin(a), z) for r, z in profile])
    vid = {}

    def V(i, j):
        r, z = profile[j]
        key = ("pole", j) if r < 1e-6 else (i, j)
        if key not in vid:
            vid[key] = bm.verts.new(rings[i][j] if r >= 1e-6 else (0.0, 0.0, z))
        return vid[key]
    for i in range(verts):
        ii = (i + 1) % verts
        for j in range(len(profile) - 1):
            q = [V(i, j), V(ii, j), V(ii, j + 1), V(i, j + 1)]
            uniq = []
            for v in q:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                bm.faces.new(uniq)
    bm.normal_update()
    # orient: face normals away from the axis (or toward it)
    for f in bm.faces:
        c = f.calc_center_median()
        radial = Vector((c.x, c.y, 0.0))
        if radial.length < 1e-6:
            continue
        if (f.normal.dot(radial) < 0) == outward:
            f.normal_flip()
    return ns.from_bmesh(bm, name, loc=loc)


def contact_sheet(cols=3, thumb=340):
    """Labelled grid of every final <asset>_preview.png in previews/K_shop -> _contact.png
    (label = asset name + exported size / tris from manifests/K_shop.json)."""
    import json
    from PIL import Image, ImageDraw, ImageFont
    files = sorted(f for f in os.listdir(PREVIEWS) if f.endswith("_preview.png"))
    man = {}
    mpath = os.path.join(ns.REPO, "manifests", f"{BATCH}.json")
    if os.path.exists(mpath):
        with open(mpath) as f:
            man = json.load(f)
    try:
        font = ImageFont.truetype(FONT_REGULAR, 20)
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


def poster_frame(w, h, depth=0.15, border=0.16, radius=0.1, paper=PAPER, frame=CHROME, frame_mat="Metal",
                 paper_inset=0.07):
    """Framed poster shell for wall props: a frame ring (outer w x h, `border` wide, back face on
    y = 0, front at y = -depth, bottom at z = 0) and the paper panel recessed `paper_inset`
    behind the frame front. Returns (frame_obj, paper_obj, paper_front_y, (cx, cz), (pw, ph))
    with pw x ph the visible paper size. Objects are untagged."""
    zc = h / 2
    outer = rrect(w, h, radius, 2, 0, zc)
    inner = rrect(w - 2 * border, h - 2 * border, max(0.02, radius * 0.4), 2, 0, zc)
    fr = ring_slab(outer, inner, "y", -depth, 0.0)
    ns.bevel(fr, width=min(0.03, border * 0.2), segments=1, angle=50)
    pf = -depth + paper_inset
    pw, ph = w - 2 * border, h - 2 * border
    pa = ns.box((pw + 0.04, 0.02, ph + 0.04), loc=(0, pf + 0.01, zc), bevel=0.0)
    return fr, pa, pf, (0.0, zc), (pw, ph)


def screw_heads(points, y, r=0.05, verts=6):
    out = []
    for x, z in points:
        s = ns.cyl(r, 0.04, loc=(0, 0, 0), verts=verts, bevel=0.0)
        place(s, (x, y, z), pitch=90)
        out.append(s)
    return out


# ---------------------------------------------------------------------------------------
# Run wrappers (quick previews, socket check render, part listing) — all output goes to
# previews/K_shop only.
# ---------------------------------------------------------------------------------------

def _print_parts(asset):
    dg = bpy.context.evaluated_depsgraph_get()
    tot = 0
    for o in sorted(ns._tagged_objects(), key=lambda o: o.name):
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        n = len(me.loop_triangles)
        tot += n
        print(f"  [{asset}] {o.name:20s} {n:5d} tris  {o['ns_material']:13s} role={o.get('ns_role')}")
        o.evaluated_get(dg).to_mesh_clear()
    lo, hi = ns.bbox_world(ns._tagged_objects())
    print(f"  [{asset}] bbox lo {tuple(round(c, 3) for c in lo)} hi {tuple(round(c, 3) for c in hi)} total {tot}")


def _arrow(loc, yaw, size=0.6):
    a = math.radians(yaw)
    d = Vector((math.sin(a), -math.cos(a), 0))
    p = Vector(loc)
    shaft = rod(p, p + d * size, size * 0.08, verts=6)
    head = rod(p + d * size, p + d * size * 1.5, size * 0.22, verts=8, r_top=0.0)
    ball = ns.sphere(size * 0.16, loc=p, segs=8, rings=5)
    m = ns.material("#FF00FF", "Neon")
    for o in (shaft, head, ball):
        o.data.materials.append(m)
        o.name = "SockMarker"
    return [shaft, head, ball]


def socket_check(asset, sockets, views=((-35, 28),), res=448, samples=8, size=0.6):
    """Render the asset with arrow markers at every socket (one image per view)."""
    from PIL import Image
    markers = []
    for name, spec in sockets.items():
        if len(spec) == 2 and not isinstance(spec[0], (int, float)):
            loc, yaw = spec
        else:
            loc, yaw = spec, 0.0
        markers += _arrow(loc, yaw, size)
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


def render_views(path, views, res=(512, 512), samples=16, floor=True, world=0.9, light_scale=1.0):
    """Render the current scene from explicit cameras (each image <= 512 px).
    views = [(cam_loc, look_at, lens_mm)]; images are tiled horizontally into `path`."""
    from PIL import Image
    sc = bpy.context.scene
    assert max(res) <= 512, res
    ns._setup_render(res[0], samples, transparent=False)
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.world.node_tree.nodes.get("Background").inputs[1].default_value = world
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=400, location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z - 0.001))
        fl = bpy.context.active_object
        fl.name = "Floor"
        fl.data.materials.append(ns.material("#3A3B42"))
    ctr = (lo + hi) / 2
    d = (hi - lo).length
    paths = []
    for i, (cl, at, lens) in enumerate(views):
        for o in list(sc.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cd = bpy.data.cameras.new("PreviewCam")
        cd.lens = lens
        cd.clip_start = 0.05
        cd.clip_end = 2000
        cam = bpy.data.objects.new("PreviewCam", cd)
        sc.collection.objects.link(cam)
        cam.location = Vector(cl)
        cam.rotation_euler = (Vector(at) - Vector(cl)).to_track_quat("-Z", "Y").to_euler()
        sc.camera = cam
        ns._light("Key", "AREA", Vector(cl) + Vector((-d * 0.4, -d * 0.2, d * 0.5)), light_scale * 60 * d ** 2 / 9,
                  size=d * 0.6, target=ctr)
        ns._light("Fill", "AREA", Vector(cl) + Vector((d * 0.5, 0, d * 0.1)), light_scale * 18 * d ** 2 / 9,
                  size=d * 0.8, target=ctr)
        p = path.replace(".png", f"_{i}.png")
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    ims = [Image.open(p).convert("RGB") for p in paths]
    combo = Image.new("RGB", (sum(im.width for im in ims), max(im.height for im in ims)))
    x = 0
    for im in ims:
        combo.paste(im, (x, 0))
        x += im.width
    combo.save(path)
    for p in paths:
        os.remove(p)
    return path


def run(build, asset, sockets=None, socket_views=((-35, 28),), preview=None, **export_kw):
    """Standard K_shop entry: build -> preview (quick with NS_QUICK=1) -> optional socket
    check render -> export when NS_EXPORT=1. `preview(asset, out_dir, res, spp)` may replace
    the standard two-angle preview (it must write <out_dir>/<asset>_preview.png)."""
    ns.reset()
    extra = build() or {}
    print(f"[{asset}] triangles: {ns.tri_count()}")
    if os.environ.get("NS_PARTS") == "1":
        _print_parts(asset)
    if os.environ.get("NS_NORENDER") != "1":
        quick = os.environ.get("NS_QUICK") == "1"
        res, spp = (320, 8) if quick else (512, 16)
        out_dir = os.path.join(PREVIEWS, "_quick") if quick else PREVIEWS
        os.makedirs(out_dir, exist_ok=True)
        if preview is not None:
            prev = preview(asset, out_dir, res, spp)
        else:
            prev = ns.render_preview(asset, out_dir=out_dir, res=res, samples=spp)
        print(f"[{asset}] preview: {os.path.abspath(prev)}")
    if sockets and os.environ.get("NS_SOCKETS") == "1":
        print(f"[{asset}] sockets: {socket_check(asset, sockets, views=socket_views)}")
    if os.environ.get("NS_EXPORT") == "1":
        kw = dict(export_kw)
        kw.update(extra.get("export", {}))
        doc = ns.export_asset(asset, BATCH, group=GROUP, sockets=sockets, **kw)
        print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']}")
        for p in doc["parts"]:
            print(f"    part {p['name']:18s} {p['material']:13s} role={p['role']} tris={p['tris']}")
        if doc.get("sockets"):
            print(f"    sockets {doc['sockets']}")
    return extra


def dir_preview(asset, out_dir, res, spp, dirs, lens=50, margin=1.1, world=0.9):
    """Tightly framed views from explicit directions (camera at ctr + dir * dist), no floor."""
    from PIL import Image
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    ctr = (lo + hi) / 2
    ns._setup_render(res, spp, transparent=False)
    bpy.context.scene.world.node_tree.nodes.get("Background").inputs[1].default_value = world
    paths = []
    for i, dv in enumerate(dirs):
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cd = bpy.data.cameras.new("PreviewCam")
        cd.lens = lens
        cd.clip_start = 0.02
        cd.clip_end = 1000
        cam = bpy.data.objects.new("PreviewCam", cd)
        bpy.context.scene.collection.objects.link(cam)
        dvec = Vector(dv).normalized()
        cam.location = ctr + dvec * max((hi - lo).length, 1.0) * 2
        cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.camera = cam
        dist = tight_fit(cam, lo, hi, ctr, margin=margin)
        side = dvec.cross(Vector((0, 0, 1)))
        if side.length < 1e-3:
            side = Vector((1, 0, 0))
        side.normalize()
        ns._light("Key", "AREA", ctr + (dvec - side * 0.8 + Vector((0, 0, 0.6))).normalized() * dist,
                  60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + (dvec + side * 1.0).normalized() * dist, 22 * dist ** 2 / 9,
                  size=dist * 0.8, target=ctr)
        p = os.path.join(out_dir, f"{asset}_{i}.png")
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


def hanging_preview(asset, out_dir, res, spp):
    """Two tightly framed views from BELOW / the side (ceiling-hung fittings show their lit
    side), no floor."""
    return dir_preview(asset, out_dir, res, spp, [(-0.45, -1.0, -0.55), (1.0, -0.9, 0.12)])


def _mesh_points(max_pts=4000):
    """World-space vertices of every tagged part (evaluated, subsampled)."""
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in ns._tagged_objects():
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        pts += [o.matrix_world @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    step = max(1, len(pts) // max_pts)
    return pts[::step]


def tight_fit(cam, lo, hi, ctr, margin=1.1, iters=4):
    """Move a camera along its view axis until the asset's vertices fill the frame (x or y)."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    corners = _mesh_points()
    for _ in range(iters):
        bpy.context.view_layer.update()
        ext = 0.0
        for c in corners:
            u, v, _w = world_to_camera_view(sc, cam, c)
            ext = max(ext, abs(u - 0.5) * 2, abs(v - 0.5) * 2)
        d = cam.location - ctr
        cam.location = ctr + d * (ext * margin)
    bpy.context.view_layer.update()
    return (cam.location - ctr).length


def front_preview(asset, out_dir, res, spp, side_yaw=-38, pitch=10, backdrop=None):
    """Wall props: straight front view + 3/4 view (both from the room side), tightly framed.
    backdrop = hex colour of a wall plane just behind y = 0 (shows how it sits on a wall)."""
    from PIL import Image
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    ns._setup_render(res, spp, transparent=False)
    wall = None
    if backdrop:
        span = max(hi.x - lo.x, hi.z - lo.z) * 3
        bpy.ops.mesh.primitive_plane_add(size=span, location=((lo.x + hi.x) / 2, hi.y + 0.002, (lo.z + hi.z) / 2),
                                         rotation=(math.radians(90), 0, 0))
        wall = bpy.context.active_object
        wall.name = "Floor_Backdrop"
        wall.data.materials.append(ns.material(backdrop))
    paths = []
    for i, (yaw, pt) in enumerate(((0, 4), (side_yaw, pitch))):
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cam, ctr, dist = ns._camera_fit(lo, hi, yaw, pt, margin=1.08)
        dist = tight_fit(cam, lo, hi, ctr, margin=1.12)
        k = math.radians(yaw)
        ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * dist,
                  60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3)) * dist,
                  22 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        p = os.path.join(out_dir, f"{asset}_{i}.png")
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
