"""_common — shared helpers for the C_lobby batch (STACKHOUSE HQ lobby props).

Import from an asset script in this folder with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Builds on blender/lib/nslib.py and re-uses the B_shop shape helpers (text_mesh, prism,
pipe, fillet, rrect, ring_slab, ...) so the lobby props share the shop's family look.

Conventions used by every C_lobby asset
  * 1 stud = 1 Blender unit, Z up, the user-facing side looks at Blender -Y.
  * nslib merges role-less parts per material at export (vertex colours); only parts code
    must find (screens, number plates, neon, lamps, photos, mirror glass, seats' recolours)
    carry a `recolor` role.
  * Screens for SurfaceGuis: a flat part with role "screen" (dark glossy Glass), a socket at
    the CENTRE of the screen face (yaw = the way the face looks; 0 = front, -Y) and
    meta `screen_size: [w, h]` in studs. `surfaces` meta also names the part and its
    Roblox NormalId face.
  * Part names must not start with Key/Fill/Rim/Floor/RefCube/PreviewCam (nslib's preview
    deletes objects with those prefixes) - `part()` asserts this.
  * Env: NS_QUICK=1 renders a fast low-res preview (iteration), NS_SOCKETS=1 also renders a
    socket check view with arrows (to previews/C_lobby/_checks/), NS_PARTS=1 prints parts.
"""
from __future__ import annotations

import importlib.util
import math
import os
import sys

import bpy  # noqa: F401  (must load before bmesh in the bpy module build)
import bmesh
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "lib"))
import nslib as ns  # noqa: E402

# B_shop helpers, loaded under their own module name (both batches call theirs `_common`)
_spec = importlib.util.spec_from_file_location("shop_common", os.path.join(_HERE, "..", "B_shop", "_common.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

fillet, rrect, circle_pts, ellipse_pts = S.fillet, S.rrect, S.circle_pts, S.ellipse_pts
prism, slab, pipe, round_path, ring_slab = S.prism, S.slab, S.pipe, S.round_path, S.ring_slab
text_mesh, fit_text_width, bbox_of, merge = S.text_mesh, S.fit_text_width, S.bbox_of, S.merge
FONT_BOLD, FONT_BOLD_ITALIC = S.FONT_BOLD, S.FONT_BOLD_ITALIC

BATCH = "C_lobby"
GROUP = "Lobby"
PREVIEWS = os.path.join(ns.REPO, "..", "previews", BATCH)

# ---------------------------------------------------------------------------------------
# Palette (STYLE.md §1 + lobby accents)
# ---------------------------------------------------------------------------------------
CREAM = "#EFE6D2"
CREAM_SHADE = "#DCD0B8"
VAN_WHITE = "#F3EEE2"      # van body (cream-white)
BRAND = "#E8502A"          # STACKHOUSE red-orange
BRAND_DARK = "#B83D22"
MUSTARD = "#F2B33D"
NAVY = "#1E2A44"
NAVY_DEEP = "#141C2E"
PINK = "#FF4FA3"
CYAN = "#38E1FF"
CHROME = "#D3D8DC"
STEEL = "#3B4046"
CHARCOAL = "#3A3D42"
RUBBER = "#1D1E22"
GLASS_DARK = "#1E262E"
GLASS = "#A9D3E0"
SCREEN = "#121823"         # dark glossy screen panel (game draws the content)
GOLD = "#D9A93E"           # gilding / brass (Metal)
BRASS = "#C79A45"
VELVET = "#5B2A6E"         # VIP purple velvet (Fabric)
VELVET_DARK = "#43204F"
WOOD = "#8A5A3B"
WOOD_LIGHT = "#A8774E"
WOOD_DARK = "#5A3926"
PAPER = "#F3EEE2"
BRICK = "#8A3E30"
BRICK_DARK = "#6A2E25"
MORTAR = "#B3A797"
CONCRETE = "#8E8C86"
CHALK = "#2B3A33"          # chalkboard green-black
CORK = "#B9895A"
LAMP_WARM = "#FFD99A"      # warm bulbs (Neon)
LETTUCE = "#7DBE4B"
TOMATO = "#D9472F"
CHEESE = "#F6C343"
BUN = "#E3A253"
BUN_DARK = "#C9853B"
SHRUB = "#4E8A3A"
SHRUB_DARK = "#3C6E2E"
BLACK = "#16171A"

FORBIDDEN = ("PreviewCam", "Key", "Fill", "Rim", "RefCube", "Floor")

# Shift van / van bay shared layout (Blender coords, van pivot = bottom-centre at origin,
# van front = -Y, sliding door on the -X side = the van's right / curb side).
VAN_HW = 3.5                 # body half width
VAN_HL = 8.0                 # body half length (bumpers stick out ~0.25 more)
VAN_FLOOR = 1.6              # cargo floor top
VAN_DOOR_Y = (-3.0, 2.0)     # sliding-door opening along Y
VAN_DOOR_Z = (1.6, 6.25)
VAN_DOOR_YC = sum(VAN_DOOR_Y) / 2
VAN_PAD = (-VAN_HW - 2.4, VAN_DOOR_YC)   # join pad centre on the ground outside the door


# ---------------------------------------------------------------------------------------
# Small builders
# ---------------------------------------------------------------------------------------

def part(objs, name, color, mat="SmoothPlastic", **kw):
    """Apply + join + tag in one call (objs: object or list, nested lists / None ok)."""
    assert not name.startswith(FORBIDDEN), name
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    return ns.tag(merge(list(objs), name), name, color, mat, **kw)


def rod(p0, p1, r, verts=8, bevel=0.0, segments=1, name="Rod", r_top=None):
    """Straight cylinder (or taper with r_top) from point p0 to p1."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = ns.cyl(r, d.length, loc=(p0 + p1) / 2, verts=verts, bevel=bevel, segments=segments,
               radius_top=r_top, name=name)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def yaw_point(p, yaw_deg, about=(0, 0, 0)):
    """Rotate a point about the Z axis through `about` by yaw degrees (CCW from above)."""
    a = math.radians(yaw_deg)
    x, y = p[0] - about[0], p[1] - about[1]
    return (about[0] + x * math.cos(a) - y * math.sin(a), about[1] + x * math.sin(a) + y * math.cos(a), p[2])


def facing_yaw(frm, to):
    """Socket yaw (degrees) for something at `frm` facing toward `to` (yaw 0 = facing -Y)."""
    dx, dy = to[0] - frm[0], to[1] - frm[1]
    return math.degrees(math.atan2(dx, -dy))


def arc_solid(r_in, r_out, a0, a1, z0, z1, segs=16, cx=0.0, cy=0.0, name="Arc"):
    """Annular-sector solid (a curved bench / rail) around a vertical axis at (cx, cy).
    Angles in degrees, measured from +X counter-clockwise."""
    bm = bmesh.new()
    rings = []
    for i in range(segs + 1):
        a = math.radians(a0 + (a1 - a0) * i / segs)
        c, s = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((cx + r * c, cy + r * s, z)) for r, z in
                      ((r_in, z0), (r_out, z0), (r_out, z1), (r_in, z1))])
    for i in range(segs):
        a, b = rings[i], rings[i + 1]
        for k in range(4):
            kk = (k + 1) % 4
            bm.faces.new([a[k], a[kk], b[kk], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def arc_profile_sweep(profile_rz, a0, a1, segs=16, cx=0.0, cy=0.0, name="Sweep"):
    """Sweep a closed (r, z) cross-section around a vertical axis between angles a0..a1
    (degrees), with flat end caps. Used for curved booth backs and trims."""
    bm = bmesh.new()
    rings = []
    for i in range(segs + 1):
        a = math.radians(a0 + (a1 - a0) * i / segs)
        c, s = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((cx + r * c, cy + r * s, z)) for r, z in profile_rz])
    n = len(profile_rz)
    for i in range(segs):
        a, b = rings[i], rings[i + 1]
        for k in range(n):
            kk = (k + 1) % n
            bm.faces.new([a[k], a[kk], b[kk], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def arch(w, h, z0, n=8, cx=0.0):
    """Arch-topped outline (x, z): straight sides from z0, semicircular top, total height h."""
    r = w / 2
    zs = z0 + h - r
    pts = [(cx - r, z0), (cx + r, z0)]
    for k in range(n + 1):
        a = math.pi * k / n
        pts.append((cx + r * math.cos(a), zs + r * math.sin(a)))
    return pts


def arch_path(w, h, z0, n=8, cx=0.0):
    """Open path up the left side, over the arch and down the right side (for tubes)."""
    r = w / 2
    zs = z0 + h - r
    pts = [(cx - r, z0)]
    for k in range(n + 1):
        a = math.pi - math.pi * k / n
        pts.append((cx + r * math.cos(a), zs + r * math.sin(a)))
    pts.append((cx + r, z0))
    return pts


def annulus(r_in, r_out, loc=(0, 0, 0), verts=16, name="Annulus"):
    """Single-sided flat ring facing +Z (decals like whitewalls / painted rings: one quad
    strip, no hidden faces). Rotate it to face elsewhere."""
    bm = bmesh.new()
    vi = [bm.verts.new((r_in * math.cos(2 * math.pi * i / verts), r_in * math.sin(2 * math.pi * i / verts), 0))
          for i in range(verts)]
    vo = [bm.verts.new((r_out * math.cos(2 * math.pi * i / verts), r_out * math.sin(2 * math.pi * i / verts), 0))
          for i in range(verts)]
    for i in range(verts):
        j = (i + 1) % verts
        bm.faces.new([vi[i], vo[i], vo[j], vi[j]])
    return ns.from_bmesh(bm, name, loc)


def disc(r, loc=(0, 0, 0), verts=16, name="Disc"):
    """Single-sided flat disc facing +Z."""
    bm = bmesh.new()
    vs = [bm.verts.new((r * math.cos(2 * math.pi * i / verts), r * math.sin(2 * math.pi * i / verts), 0))
          for i in range(verts)]
    bm.faces.new(vs)
    return ns.from_bmesh(bm, name, loc)


def catenary(p0, p1, sag, n=12):
    """Points of a hanging cable from p0 to p1 sagging `sag` below the chord at mid-span."""
    p0, p1 = Vector(p0), Vector(p1)
    a = 2.0  # shape factor (cosh); normalised so the mid point sags exactly `sag`
    pts = []
    for i in range(n + 1):
        t = i / n
        u = (t - 0.5) * 2
        drop = sag * (math.cosh(a) - math.cosh(a * u)) / (math.cosh(a) - 1)
        p = p0.lerp(p1, t)
        pts.append((p.x, p.y, p.z - drop))
    return pts


def text(txt, height, depth, loc, width=None, font=None, res=1, spacing=1.0, facing="-Y", name="Text",
         back=True, flat=False):
    """Modelled text, letters standing in the XZ plane facing -Y (facing '+Y' turns it to
    read from behind). width fits the block to an exact width. back=False drops the back
    caps (for letters mounted flat on a board: they are never seen, ~1/3 of the tris).
    flat=True keeps only the front caps: single-sided letter decals standing depth/2 in
    front of loc (place loc so that sits just proud of the board) - ~1/4 of the tris."""
    ob = text_mesh(txt, height, depth, font=font or FONT_BOLD, resolution=res, spacing=spacing, loc=loc,
                   name=name)
    if width:
        fit_text_width(ob, width)
    if not back or flat:
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.normal_update()
        drop = [f for f in bm.faces if (f.normal.y > -0.95 if flat else f.normal.y > 0.95)]
        bmesh.ops.delete(bm, geom=drop, context="FACES")
        bm.to_mesh(ob.data)
        bm.free()
    if facing == "+Y":
        c = Vector(loc)
        for v in ob.data.vertices:
            v.co.x = 2 * c.x - v.co.x
            v.co.y = 2 * c.y - v.co.y
    return ob


def sandwich_icon(s=1.0, depth=0.12):
    """Stacked-sandwich logo built at the origin in the XZ plane: back face on y = 0, the
    layers stand out toward -Y (front). ~2.2 * s wide, ~1.6 * s tall, centred on z = 0.
    Returns {colour: [objs]}: domed top bun, lettuce wave, tomato bar, cheese drip, bottom
    bun. Use place() to move / turn the pieces."""
    out = {BUN: [], LETTUCE: [], TOMATO: [], CHEESE: []}

    def P(u, v):
        return (u * s, v * s)

    dome = ([P(1.0, 0.36)] + [P(math.cos(t * math.pi / 9), 0.42 + 0.6 * math.sin(t * math.pi / 9))
                              for t in range(10)] + [P(-1.0, 0.36)])
    out[BUN].append(prism(dome, "y", -depth, 0.0))
    wave_top = [P(-1.1 + 2.2 * i / 8, 0.29 + 0.07 * (1 if i % 2 else -1)) for i in range(9)]
    wave_bot = [P(1.06, 0.14), P(-1.06, 0.14)]
    out[LETTUCE].append(prism(wave_top + wave_bot, "y", -depth * 0.85, 0.0))
    out[TOMATO].append(prism(rrect(2.04 * s, 0.17 * s, 0.07 * s, 2, 0, 0.03 * s), "y", -depth * 0.8, 0.0))
    chz = [P(-1.04, -0.07), P(1.04, -0.07), P(1.04, -0.16), P(0.56, -0.16), P(0.43, -0.34), P(0.3, -0.16),
           P(-1.04, -0.16)]
    out[CHEESE].append(prism(chz, "y", -depth * 0.9, 0.0))
    out[BUN].append(prism(rrect(2.0 * s, 0.36 * s, 0.15 * s, 2, 0, -0.37 * s), "y", -depth, 0.0))
    return out


def place(objs, loc=(0, 0, 0), yaw=0.0, pitch=0.0):
    """Rotate objects built around the origin (pitch about X first, then yaw about Z) and
    move them to loc. Works on lists / dicts of lists; transforms are applied on merge."""
    if isinstance(objs, dict):
        for v in objs.values():
            place(v, loc, yaw, pitch)
        return objs
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    for o in objs:
        ns.apply_all(o)
        o.rotation_euler = (math.radians(pitch), 0.0, math.radians(yaw))
        o.location = Vector(loc)
        ns.apply_all(o)
    return objs


def screen_meta(part_name, w, h, face="Front"):
    return {"part": part_name, "face": face, "screen_size": [round(w, 3), round(h, 3)]}


# ---------------------------------------------------------------------------------------
# Run wrapper (quick previews, socket check render, part listing)
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
    print(f"  [{asset}] bbox lo {tuple(round(c, 2) for c in lo)} hi {tuple(round(c, 2) for c in hi)} total {tot}")


def _arrow(loc, yaw, size=0.6):
    """Untagged magenta arrow marker (cone pointing the socket's facing direction)."""
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


def socket_check(asset, sockets, views=((-35, 28),), res=448, samples=8):
    """Render the asset with arrow markers at every socket (one image per view)."""
    from PIL import Image
    markers = []
    for name, spec in sockets.items():
        if len(spec) == 2 and not isinstance(spec[0], (int, float)):
            loc, yaw = spec
        else:
            loc, yaw = spec, 0.0
        markers += _arrow(loc, yaw)
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    span = max(hi.x - lo.x, hi.y - lo.y, 0.5)
    bpy.ops.mesh.primitive_plane_add(size=max(span * 8, 8), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0 - 0.001))
    fl = bpy.context.active_object
    fl.name = "Floor"
    fl.data.materials.append(ns.material("#3A3B42"))
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


def run(build, asset, sockets=None, socket_views=((-35, 28),), **export_kw):
    """Standard C_lobby entry: build -> preview (quick with NS_QUICK=1) -> optional socket
    check render -> export when NS_EXPORT=1."""
    ns.reset()
    extra = build() or {}
    print(f"[{asset}] triangles: {ns.tri_count()}")
    if os.environ.get("NS_PARTS") == "1":
        _print_parts(asset)
    if os.environ.get("NS_NORENDER") != "1":
        quick = os.environ.get("NS_QUICK") == "1"
        res, spp = (384, 8) if quick else (512, 16)
        out_dir = os.path.join(PREVIEWS, "_quick") if quick else PREVIEWS
        prev = ns.render_preview(asset, out_dir=out_dir, res=res, samples=spp)
        print(f"[{asset}] preview: {prev}")
    if sockets and os.environ.get("NS_SOCKETS") == "1":
        print(f"[{asset}] sockets: {socket_check(asset, sockets, views=socket_views)}")
    if os.environ.get("NS_EXPORT") == "1":
        kw = dict(export_kw)
        kw.update(extra.get("export", {}))
        doc = ns.export_asset(asset, BATCH, group=GROUP, sockets=sockets, **kw)
        print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']}")
        for p in doc["parts"]:
            print(f"    part {p['name']:18s} {p['material']:13s} role={p['role']} tris={p['tris']}")
    return extra


# ---------------------------------------------------------------------------------------
# STACKHOUSE HQ facade kit (Lobby_StoreFrontBay / Lobby_StoreWall share these so the
# modules line up: same plinth, brick courses, header line, parapet and coping).
# Wall centre line on y = 0, exterior face -Y, pivot bottom-centre of the centre line.
# ---------------------------------------------------------------------------------------
HQ_T = 1.5                    # wall thickness
HQ_H = 14.0
HQ_PLINTH = 0.6
HQ_HEADER = (10.4, 11.4)      # red-orange header band / steel beam
HQ_COPING = 13.45             # coping bottom (top = HQ_H)
HQ_COURSE = 0.5


def hq_courses(z0, z1):
    """Mortar-line heights between z0 and z1 (absolute grid so modules line up)."""
    out = []
    k = math.ceil((z0 + 1e-3 - HQ_PLINTH) / HQ_COURSE)
    while True:
        z = HQ_PLINTH + k * HQ_COURSE
        if z >= z1 - 1e-3:
            break
        if z > z0 + 1e-3:
            out.append(z)
        k += 1
    return out


def hq_mortar_face(x0, x1, z0, z1, sy, heads=True, head_every=2.0, lines=True):
    """Raised mortar lines (+ staggered head joints) on a flat brick face between x0..x1,
    z0..z1. sy = -1 exterior (front) face, +1 interior face. Head joints sit on an absolute
    1-stud brick grid so neighbouring modules continue the bond."""
    fy = sy * HQ_T / 2
    objs = []
    for z in (hq_courses(z0, z1) if lines else []):
        objs.append(ns.box((x1 - x0, 0.05, 0.06), loc=((x0 + x1) / 2, fy + sy * 0.025, z), bevel=0.0))
    if heads:
        zs = [z0] + hq_courses(z0, z1) + [z1]
        for za, zb in zip(zs[:-1], zs[1:]):
            if zb - za < HQ_COURSE - 0.05:
                continue
            zc = (za + zb) / 2
            row = int(round((za - HQ_PLINTH) / HQ_COURSE))
            off = 0.5 if row % 2 else 0.0
            n = math.floor(x0 - off)
            while n + off < x1:
                x = n + off
                if x0 + 0.08 < x < x1 - 0.08 and (n + row) % int(head_every) == 0:
                    objs.append(ns.box((0.06, 0.05, HQ_COURSE - 0.06), loc=(x, fy + sy * 0.025, zc), bevel=0.0))
                n += 1
    return objs


def hq_pier_rings(x0, x1, z0, z1, grow=(0.02, 0.02)):
    """Mortar rings wrapped round a brick pier (front, back and the exposed side faces).
    grow = how far the ring sticks out past x0 / x1 (use a small negative value on a side
    that butts the next module, so neighbouring rings never overlap coplanar)."""
    a0, a1 = x0 - grow[0], x1 + grow[1]
    return [ns.box((a1 - a0, HQ_T + 0.05, 0.06), loc=((a0 + a1) / 2, 0, z), bevel=0.0) for z in hq_courses(z0, z1)]


def hq_plinth(x0, x1):
    prof = fillet([(-HQ_T / 2 - 0.12, 0), (HQ_T / 2 + 0.12, 0), (HQ_T / 2 + 0.12, HQ_PLINTH - 0.08),
                   (HQ_T / 2 + 0.02, HQ_PLINTH), (-HQ_T / 2 - 0.02, HQ_PLINTH), (-HQ_T / 2 - 0.12, HQ_PLINTH - 0.08)],
                  [0, 0, 0.04, 0.02, 0.02, 0.04], 1)
    return prism(prof, "x", x0, x1)


def hq_coping(x0, x1):
    prof = fillet([(-HQ_T / 2 - 0.22, HQ_COPING), (HQ_T / 2 + 0.22, HQ_COPING), (HQ_T / 2 + 0.22, HQ_COPING + 0.16),
                   (HQ_T / 2 + 0.05, HQ_H), (-HQ_T / 2 - 0.05, HQ_H), (-HQ_T / 2 - 0.22, HQ_COPING + 0.16)],
                  [0, 0, 0.04, 0.03, 0.03, 0.04], 1)
    return prism(prof, "x", x0, x1)


def hq_header_band(x0, x1, proud=0.06):
    """Red-orange header band (flat ends so modules butt seamlessly)."""
    z0, z1 = HQ_HEADER
    prof = fillet([(-HQ_T / 2 - proud, z0), (HQ_T / 2 + proud, z0), (HQ_T / 2 + proud, z1), (-HQ_T / 2 - proud, z1)],
                  [0.03, 0.03, 0.03, 0.03], 1)
    return prism(prof, "x", x0, x1)


def hq_pinstripes(x0, x1):
    """Mustard pinstripes: under the header band and under the coping, both faces."""
    out = []
    for z in (HQ_HEADER[0] - 0.14, HQ_COPING - 0.16):
        for sy in (-1, 1):
            out.append(ns.box((x1 - x0, 0.06, 0.09), loc=((x0 + x1) / 2, sy * (HQ_T / 2 + 0.03), z), bevel=0.0))
    return out
