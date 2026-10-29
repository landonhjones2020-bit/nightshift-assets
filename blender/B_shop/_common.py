"""_common — shared helpers for the B_shop batch (STACKHOUSE shop building + furniture).

Everything here builds on blender/lib/nslib.py. Import from an asset script with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Conventions used by every B_shop asset
  * 1 stud = 1 Blender unit, Z up, the room-facing / user-facing side looks at Blender -Y.
  * Building modules sit on an 8-stud grid: walls are 8 wide x 12 tall x 1 thick, centred on
    the wall line (pivot = bottom of the wall centre line). Ends land on grid nodes, where
    Shop_WallCorner columns go.
  * Collision is designed for CollisionFidelity = Box: every part that collides has a
    bounding box that is itself a sensible collider (openings, knee spaces and hiding spots
    are never inside the bounding box of any part).
  * Wall-mounted props (signs, boards, mirror) pivot at the bottom-centre of their BACK
    face (the face that touches the wall, +Y), so they place flush on a wall face.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import nslib as ns  # noqa: E402,F401
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

BATCH = "B_shop"
GROUP = "Shop"
FONT_BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_BOLD_ITALIC = "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf"

# ---------------------------------------------------------------------------------------
# Palette (STYLE.md §1; derived shades are a step greyer than the food)
# ---------------------------------------------------------------------------------------
CREAM = "#EFE6D2"          # kitchen warm cream
CREAM_SHADE = "#DCD0B8"    # back faces / grout
STAINLESS = "#B9C0C6"
CHROME = "#D3D8DC"
NAVY = "#1E2A44"           # dining room
NAVY_DEEP = "#141C2E"
PINK = "#FF4FA3"
CYAN = "#38E1FF"
ICE = "#9FD3E8"
CHARCOAL = "#3A3D42"       # basement
BRAND = "#E8502A"          # STACKHOUSE red-orange
MUSTARD = "#F2B33D"
TEAL_TILE = "#6E9E97"      # diner seafoam wainscot tile
CHECK_DARK = "#26282E"
CHECK_LIGHT = "#ECE6D8"
BASE_DARK = "#2B2D33"      # baseboards, kick plates, rubber
RUBBER = "#1D1E22"
VINYL_RED = "#B8323C"
VINYL_RED_DARK = "#8E2530"
VINYL_TEAL = "#2F8A88"
LAMINATE = "#E9E2D3"       # table / counter tops
WOOD = "#8A5A3B"
WOOD_LIGHT = "#A8774E"
WOOD_DARK = "#5A3926"
PAPER = "#F3EEE2"
CARDBOARD = "#B48A5C"
CORK = "#B9895A"
GLASS = "#A9D3E0"
SCREEN_OFF = "#1C2B26"     # CRT glass, off
PORCELAIN = "#F1F0EA"
DARK_VOID = "#121317"      # interiors of openings / cubbies

# Recolour presets for the wall modules (roles -> colour). Exported in meta so the map
# builder can dress the same modules for each zone.
WALL_PRESETS = {
    "Kitchen": {"wall_upper": CREAM, "wall_tile": TEAL_TILE, "wall_grout": CREAM_SHADE,
                "wall_base": BASE_DARK, "wall_back": CREAM_SHADE},
    "Dining": {"wall_upper": NAVY, "wall_tile": "#2C5560", "wall_grout": NAVY_DEEP,
               "wall_base": "#101521", "wall_back": CREAM_SHADE},
    "Freezer": {"wall_upper": "#CFE7F0", "wall_tile": ICE, "wall_grout": "#B4CBD4",
                "wall_base": "#5B6E78", "wall_back": CREAM_SHADE},
    "Basement": {"wall_upper": CHARCOAL, "wall_tile": "#4A4E55", "wall_grout": "#2A2C30",
                 "wall_base": "#1E1F22", "wall_back": "#2F3236"},
    "Restroom": {"wall_upper": "#D8E2DA", "wall_tile": "#9DB8A8", "wall_grout": "#C2CCC4",
                 "wall_base": BASE_DARK, "wall_back": CREAM_SHADE},
}

# Wall layout (front face of a wall module, heights in studs)
WALL_W, WALL_H, WALL_T = 8.0, 12.0, 1.0
FACE_Y = -WALL_T / 2          # front face plane
BASE_TOP = 0.5                # baseboard top
TILE_TOP = 2.72               # tile field top (5 rows of 0.444, 0.5 wide)
CHECK_TOP = 3.22              # checker band top (2 rows of 0.25 squares, 32 per module)
RAIL_H = 0.28                 # chrome chair rail: 3.22 .. 3.5, top flush with the window sill
RAIL_Z = CHECK_TOP + RAIL_H / 2
SILL_Z = 3.5
CROWN_Z = 11.45               # crown moulding bottom


def run(build, asset, **kw):
    """Standard B_shop entry point."""
    return ns.run_main(build, asset, BATCH, GROUP, **kw)


# ---------------------------------------------------------------------------------------
# 2D profile helpers
# ---------------------------------------------------------------------------------------

def fillet(pts, r, segs=3):
    """Round the corners of a closed 2D polygon. r = radius (float) or a list per corner."""
    out = []
    n = len(pts)
    for i in range(n):
        ri = r[i] if isinstance(r, (list, tuple)) else r
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        if ri <= 0 or segs < 1:
            out.append((p1.x, p1.y))
            continue
        d0 = (p0 - p1)
        d1 = (p2 - p1)
        if d0.length < 1e-6 or d1.length < 1e-6:
            out.append((p1.x, p1.y))
            continue
        d0.normalize()
        d1.normalize()
        ang = d0.angle(d1)
        if ang > math.pi - 1e-3:
            out.append((p1.x, p1.y))
            continue
        t = ri / math.tan(ang / 2)
        t = min(t, (Vector(pts[i - 1]) - p1).length * 0.5, (Vector(pts[(i + 1) % n]) - p1).length * 0.5)
        a = p1 + d0 * t
        b = p1 + d1 * t
        for k in range(segs + 1):
            s = k / segs
            q = (1 - s) ** 2 * a + 2 * (1 - s) * s * p1 + s * s * b
            out.append((q.x, q.y))
    return out


def rrect(w, h, r, segs=3, cx=0.0, cy=0.0):
    """Rounded rectangle outline (CCW), centred at (cx, cy)."""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    return fillet([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], r, segs)


def circle_pts(r, n=16, cx=0.0, cy=0.0, a0=0.0):
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cy + r * math.sin(a0 + 2 * math.pi * i / n))
            for i in range(n)]


def ellipse_pts(rx, ry, n=20, cx=0.0, cy=0.0):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ---------------------------------------------------------------------------------------
# 3D builders
# ---------------------------------------------------------------------------------------

def _to3(axis, u, v, a):
    if axis == "x":
        return (a, u, v)
    if axis == "y":
        return (u, a, v)
    return (u, v, a)


def prism(profile, axis, a0, a1, name="Prism", loc=(0, 0, 0), bevel=0.0, segments=2):
    """Extrude a closed 2D profile along an axis between a0 and a1 (flat end caps, no bevel
    by default, so trim pieces butt seamlessly against the next module).
    axis "x": profile = (y, z) points; "y": (x, z); "z": (x, y)."""
    bm = bmesh.new()
    r0 = [bm.verts.new(_to3(axis, u, v, a0)) for u, v in profile]
    r1 = [bm.verts.new(_to3(axis, u, v, a1)) for u, v in profile]
    n = len(profile)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
    bm.faces.new(list(reversed(r0)))
    bm.faces.new(r1)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name, loc=loc, bevel=bevel, segments=segments)


def slab(points2d, thickness, axis="y", at=0.0, name="Slab", bevel=0.03, segments=2):
    """Flat plate from a 2D outline: axis 'y' = plate in the XZ plane (wall-mounted things),
    spanning from `at` to `at + thickness` along the axis."""
    return prism(points2d, axis, at, at + thickness, name=name, bevel=bevel, segments=segments)


def tiles(cells, face_y, depth, chamfer, name="Tiles"):
    """Raised square tiles on a plane facing -Y (no back faces). cells = [(x0, x1, z0, z1)].
    Each tile is a chamfered frustum: 1 front quad + 4 slanted sides."""
    bm = bmesh.new()
    for x0, x1, z0, z1 in cells:
        c = chamfer
        b = [bm.verts.new((x0, face_y, z0)), bm.verts.new((x1, face_y, z0)),
             bm.verts.new((x1, face_y, z1)), bm.verts.new((x0, face_y, z1))]
        yf = face_y - depth
        f = [bm.verts.new((x0 + c, yf, z0 + c)), bm.verts.new((x1 - c, yf, z0 + c)),
             bm.verts.new((x1 - c, yf, z1 - c)), bm.verts.new((x0 + c, yf, z1 - c))]
        bm.faces.new(f)
        for i in range(4):
            j = (i + 1) % 4
            bm.faces.new([b[i], b[j], f[j], f[i]])
    return ns.from_bmesh(bm, name)


def round_path(points, r, segs=3):
    """Insert rounded corners into an open 3D polyline."""
    pts = [Vector(p) for p in points]
    if len(pts) < 3 or r <= 0:
        return [tuple(p) for p in pts]
    out = [tuple(pts[0])]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        d0 = (p0 - p1)
        d1 = (p2 - p1)
        t = min(r, d0.length * 0.5, d1.length * 0.5)
        d0.normalize()
        d1.normalize()
        if abs(d0.dot(d1)) > 0.999:
            out.append(tuple(p1))
            continue
        a = p1 + d0 * t
        b = p1 + d1 * t
        for k in range(segs + 1):
            s = k / segs
            q = (1 - s) ** 2 * a + 2 * (1 - s) * s * p1 + s * s * b
            out.append(tuple(q))
    out.append(tuple(pts[-1]))
    return out


def pipe(points, radius, sides=8, closed=False, cap=True, corner=0.0, corner_segs=3, name="Pipe"):
    """Tube swept along a 3D polyline (parallel-transport frames). corner > 0 rounds bends."""
    if corner > 0 and not closed:
        points = round_path(points, corner, corner_segs)
    pts = [Vector(p) for p in points]
    n = len(pts)
    bm = bmesh.new()
    rings = []
    nrm = None
    for i in range(n):
        if closed:
            d_prev = (pts[i] - pts[i - 1]).normalized()
            d_next = (pts[(i + 1) % n] - pts[i]).normalized()
        else:
            d_prev = (pts[i] - pts[i - 1]).normalized() if i > 0 else (pts[1] - pts[0]).normalized()
            d_next = (pts[i + 1] - pts[i]).normalized() if i < n - 1 else (pts[-1] - pts[-2]).normalized()
        t = (d_prev + d_next)
        t = t.normalized() if t.length > 1e-6 else d_next
        if nrm is None:
            up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            nrm = t.cross(up).normalized()
        nrm = (nrm - t * nrm.dot(t)).normalized()
        bi = t.cross(nrm)
        miter = 1.0 / max(0.5, d_prev.dot(t))
        ring = []
        for k in range(sides):
            a = 2 * math.pi * (k + 0.5) / sides
            off = nrm * math.cos(a) + bi * math.sin(a)
            # stretch along the bend direction only (keeps the tube round in the miter plane)
            bend = (d_next - d_prev)
            if bend.length > 1e-6:
                bn = bend.normalized()
                off = off + bn * off.dot(bn) * (miter - 1.0)
            ring.append(bm.verts.new(pts[i] + off * radius))
        rings.append(ring)
    segs = n if closed else n - 1
    for i in range(segs):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for k in range(sides):
            kk = (k + 1) % sides
            bm.faces.new([r0[k], r0[kk], r1[kk], r1[k]])
    if cap and not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def text_mesh(text, size, depth, font=FONT_BOLD, bevel=0.0, resolution=2, spacing=1.0,
              align="CENTER", name="Text", loc=(0, 0, 0), facing="-Y"):
    """Modelled text (font -> mesh). The letters stand up in the XZ plane facing -Y, centred
    on loc, `depth` thick (back face at loc.y + depth/2)."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = text
    if font and os.path.exists(font):
        cu.font = bpy.data.fonts.load(font, check_existing=True)
    cu.size = size
    cu.extrude = depth / 2
    cu.bevel_depth = bevel
    cu.bevel_resolution = 1
    cu.resolution_u = resolution
    cu.space_character = spacing
    cu.align_x = align
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:])
    bm.to_mesh(ob.data)
    bm.free()
    if facing == "-Y":
        ob.rotation_euler = (math.radians(90), 0, 0)
    elif facing == "+Z":
        pass
    ob.location = Vector(loc)
    ns.apply_all(ob)
    # recentre in X/Z on the requested location (font metrics can offset the block)
    lo = Vector((min(v.co.x for v in ob.data.vertices), min(v.co.y for v in ob.data.vertices),
                 min(v.co.z for v in ob.data.vertices)))
    hi = Vector((max(v.co.x for v in ob.data.vertices), max(v.co.y for v in ob.data.vertices),
                 max(v.co.z for v in ob.data.vertices)))
    shift = Vector(loc) - (lo + hi) / 2
    if facing == "+Z":
        shift.z = 0
    else:
        shift.y = 0
    for v in ob.data.vertices:
        v.co += shift
    ob.name = name
    return ob


def bbox_of(obj):
    vs = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs)))
    hi = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    return lo, hi


def fit_text_width(obj, width):
    """Uniformly scale an applied text mesh (about its bbox centre) to an exact width."""
    lo, hi = bbox_of(obj)
    s = width / (hi.x - lo.x)
    c = (lo + hi) / 2
    for v in obj.data.vertices:
        v.co = c + (v.co - c) * s
    return obj


def merge(objs, name):
    """Apply + join a list of objects into one (flattens nested lists, skips None)."""
    flat = []
    for o in objs:
        if o is None:
            continue
        if isinstance(o, (list, tuple)):
            flat.extend(x for x in o if x is not None)
        else:
            flat.append(o)
    if len(flat) == 1:
        ns.apply_all(flat[0])
        flat[0].name = name
        return flat[0]
    return ns.join_applied(flat, name)


def part(objs, name, color, mat="SmoothPlastic", **kw):
    """merge + tag in one call."""
    return ns.tag(merge(objs if isinstance(objs, (list, tuple)) else [objs], name), name, color, mat, **kw)


def mirror_x(obj_fn, xs=(-1, 1)):
    return [obj_fn(s) for s in xs]


def socket_meta(sockets_doc: dict) -> dict:
    return sockets_doc


# ---------------------------------------------------------------------------------------
# Wall-module building blocks (front face at y = -0.5, room side = -Y)
# ---------------------------------------------------------------------------------------

def baseboard_profile(y_face, proud=0.13, h=BASE_TOP):
    """Baseboard cross-section (y, z) for a face at y_face, protruding toward the room.
    `sign` handled by the caller through y_face/proud sign."""
    s = -1 if proud > 0 else 1
    p = abs(proud)
    pts = [(y_face, 0.0), (y_face + s * p, 0.0), (y_face + s * p, h - 0.09),
           (y_face + s * (p - 0.05), h - 0.02), (y_face + s * 0.03, h), (y_face, h)]
    if s > 0:
        pts = list(reversed(pts))
    return fillet(pts, [0, 0, 0.05, 0.04, 0.02, 0], 2)


def chair_rail_profile(y_face, z, h=RAIL_H, proud=0.2):
    """Chrome bullnose rail centred at height z."""
    pts = [(y_face, z - h / 2), (y_face - proud * 0.7, z - h / 2), (y_face - proud, z),
           (y_face - proud * 0.7, z + h / 2), (y_face, z + h / 2)]
    return fillet(pts, [0, 0.05, 0.08, 0.05, 0], 3)


def crown_profile(y_face, z0, z1=WALL_H, proud=0.32):
    """Stepped cove crown moulding from z0 up to the ceiling."""
    h = z1 - z0
    pts = [(y_face, z0), (y_face - 0.06, z0), (y_face - 0.08, z0 + h * 0.18),
           (y_face - proud * 0.55, z0 + h * 0.42), (y_face - proud * 0.62, z0 + h * 0.6),
           (y_face - proud, z0 + h * 0.66), (y_face - proud, z1), (y_face, z1)]
    return fillet(pts, [0, 0.02, 0.06, 0.08, 0.05, 0.02, 0, 0], 2)


def checker_cells(x0, x1, z0, z1, n_rows, size, phase=0):
    """Cells of a two-colour checker band: returns (dark_cells, light_cells)."""
    dark, light = [], []
    nx = int(round((x1 - x0) / size))
    rh = (z1 - z0) / n_rows
    for r in range(n_rows):
        for i in range(nx):
            c = (x0 + i * size, x0 + (i + 1) * size, z0 + r * rh, z0 + (r + 1) * rh)
            ((dark if (i + r + phase) % 2 == 0 else light)).append(c)
    return dark, light


def wainscot(x_ranges, face_y=FACE_Y, with_base=True, z_top_limit=None):
    """Front-face wainscot for the given x ranges [(x0, x1), ...]:
    grout backing, raised tiles (0.5 grid), checker band and baseboard.
    Returns dict of lists of objects keyed by part kind."""
    out = {"grout": [], "tile": [], "check_dark": [], "check_light": [], "base": [], "rail": []}
    for x0, x1 in x_ranges:
        # grout backing panel (thin skin on the wall face)
        out["grout"].append(ns.box((x1 - x0, 0.03, CHECK_TOP - BASE_TOP),
                                   loc=((x0 + x1) / 2, face_y - 0.015, (BASE_TOP + CHECK_TOP) / 2), bevel=0.0))
        cells = []
        nx = int(round((x1 - x0) / 0.5))
        rows = 5
        rh = (TILE_TOP - BASE_TOP) / rows
        for r in range(rows):
            for i in range(nx):
                g = 0.025
                cells.append((x0 + i * 0.5 + g, x0 + (i + 1) * 0.5 - g, BASE_TOP + r * rh + g,
                              BASE_TOP + (r + 1) * rh - g))
        out["tile"].append(tiles(cells, face_y - 0.03, 0.05, 0.025))
        # checker band: light strip + raised dark squares (absolute-x phase so modules tile)
        out["check_light"].append(ns.box((x1 - x0, 0.05, CHECK_TOP - TILE_TOP),
                                         loc=((x0 + x1) / 2, face_y - 0.03 - 0.025, (TILE_TOP + CHECK_TOP) / 2),
                                         bevel=0.0))
        sz = 0.25
        dark = []
        nxc = int(round((x1 - x0) / sz))
        for r in range(2):
            for i in range(nxc):
                xa = x0 + i * sz
                gi = int(round((xa + 64) / sz))
                if (gi + r) % 2 == 0:
                    dark.append((xa, min(xa + sz, x1), TILE_TOP + r * sz, TILE_TOP + (r + 1) * sz))
        out["check_dark"].append(tiles(dark, face_y - 0.08, 0.015, 0.006))
        if with_base:
            out["base"].append(prism(baseboard_profile(face_y), "x", x0, x1))
        out["rail"].append(prism(chair_rail_profile(face_y - 0.03, RAIL_Z), "x", x0, x1))
    return out


def back_trim(x_ranges, face_y=-FACE_Y, rail=True):
    """Simple baseboard (+ flat chair rail) on the back (+Y) face."""
    objs = []
    for x0, x1 in x_ranges:
        pts = [(face_y, 0), (face_y + 0.1, 0), (face_y + 0.1, 0.42), (face_y + 0.04, 0.5), (face_y, 0.5)]
        objs.append(prism(fillet(pts, [0, 0, 0.04, 0.02, 0], 2), "x", x0, x1))
        if rail:
            pts = [(face_y, RAIL_Z - 0.12), (face_y + 0.08, RAIL_Z - 0.12), (face_y + 0.08, RAIL_Z + 0.12),
                   (face_y, RAIL_Z + 0.12)]
            objs.append(prism(fillet(pts, [0, 0.03, 0.03, 0], 1), "x", x0, x1))
    return objs


def wall_presets_meta():
    return {"recolor_presets": WALL_PRESETS, "default_preset": "Kitchen"}


# ---------------------------------------------------------------------------------------
# Custom review renders (tiling test etc.)
# ---------------------------------------------------------------------------------------

def render_views(path, views, res=(1024, 512), samples=24, floor=True, world=0.9):
    """Render the current scene from explicit cameras.
    views = [(cam_loc, look_at, lens_mm)]; images are tiled horizontally into `path`."""
    from PIL import Image
    sc = bpy.context.scene
    ns._setup_render(res[0], samples, transparent=False)
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.world.node_tree.nodes.get("Background").inputs[1].default_value = world
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=200, location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z - 0.001))
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
        cd.clip_end = 1000
        cam = bpy.data.objects.new("PreviewCam", cd)
        sc.collection.objects.link(cam)
        cam.location = Vector(cl)
        cam.rotation_euler = (Vector(at) - Vector(cl)).to_track_quat("-Z", "Y").to_euler()
        sc.camera = cam
        ns._light("Key", "AREA", Vector(cl) + Vector((-d * 0.4, -d * 0.2, d * 0.5)), 60 * d ** 2 / 9, size=d * 0.6, target=ctr)
        ns._light("Fill", "AREA", Vector(cl) + Vector((d * 0.5, 0, d * 0.1)), 18 * d ** 2 / 9, size=d * 0.8, target=ctr)
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


STRIPE_Z = (9.62, 9.86)      # brand pinstripe band (two thin stripes) above window heads


def crown(x0, x1, face_y=FACE_Y):
    return prism(crown_profile(face_y - 0.03, CROWN_Z), "x", x0, x1)


def stripes(x0, x1, face_y=FACE_Y):
    out = []
    for zc, h in ((STRIPE_Z[0], 0.13), (STRIPE_Z[1], 0.07)):
        pts = fillet([(face_y - 0.03, zc - h / 2), (face_y - 0.07, zc - h / 2), (face_y - 0.07, zc + h / 2),
                      (face_y - 0.03, zc + h / 2)], [0, 0.02, 0.02, 0], 1)
        out.append(prism(pts, "x", x0, x1))
    return out


def skin(x0, x1, z0, z1, face_y=FACE_Y, t=0.03):
    """Thin colour skin on the front face (no bevel; neighbours butt seamlessly)."""
    return ns.box((x1 - x0, t, z1 - z0), loc=((x0 + x1) / 2, face_y - t / 2, (z0 + z1) / 2), bevel=0.0)


def tag_wall_set(d, suffix="", collide=False):
    """Tag the dict returned by wainscot() (+ optional extra lists) as the standard wall parts."""
    out = []
    spec = [("grout", "Grout", "wall_grout", CREAM_SHADE, "SmoothPlastic"),
            ("tile", "Tiles", "wall_tile", TEAL_TILE, "SmoothPlastic"),
            ("check_light", "CheckerLight", "wall_check_light", CHECK_LIGHT, "SmoothPlastic"),
            ("check_dark", "CheckerDark", "wall_check_dark", CHECK_DARK, "SmoothPlastic"),
            ("base", "Baseboard", "wall_base", BASE_DARK, "SmoothPlastic"),
            ("rail", "ChairRail", "wall_trim", CHROME, "Metal"),
            ("upper", "Upper", "wall_upper", CREAM, "SmoothPlastic"),
            ("crown", "Crown", "wall_upper", CREAM, "SmoothPlastic"),
            ("stripe", "Stripe", "wall_stripe", BRAND, "SmoothPlastic"),
            ("back", "BackTrim", "wall_back_trim", BASE_DARK, "SmoothPlastic")]
    for key, name, role, col, mat in spec:
        objs = [o for o in d.get(key, []) if o is not None]
        if not objs:
            continue
        out.append(part(objs, name + suffix, col, mat, recolor=role, can_collide=collide, smooth_angle=40))
    return out


def square_ring(profile_yz, hw, name="Ring"):
    """Sweep a trim profile (given as (y, z) against a face at y = -hw, like the wall-face
    profiles) around a square column of half-width hw, with clean mitred corners."""
    bm = bmesh.new()
    corners = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    rings = []
    for y, z in profile_yz:
        d = -y - hw
        rings.append([bm.verts.new((sx * (hw + d), sy * (hw + d), z)) for sx, sy in corners])
    n = len(rings)
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for k in range(4):
            kk = (k + 1) % 4
            bm.faces.new([a[k], a[kk], b[kk], b[k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)
