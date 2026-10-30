"""_common — shared helpers for the I_world batch (group "World": the border / surroundings kit).

Import from an asset script in this folder with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Builds on blender/lib/nslib.py and re-uses the B_shop shape helpers (prism, pipe, fillet,
rrect, ring_slab, text_mesh ...) and the C_lobby helpers (rod, text, catenary, place ...),
loaded the way C_lobby/_common.py loads B_shop's.

Conventions used by every I_world asset
  * 1 stud = 1 Blender unit, Z up, the side that faces the playfield looks at Blender -Y.
  * These props are placed by the hundreds 40-600 studs from the player, at dusk / night,
    through fog: strong silhouettes, low triangle counts, colours that read in dim light.
  * Role-less parts are merged per material by nslib at export (vertex colours), so most
    assets export as 1-3 MeshParts. Only parts code must find carry a `recolor` role
    (lamp, neon, screen).
  * can_collide=False everywhere except tree trunks.
  * Pivots are passed explicitly (trunk base / ground point under the asset, Z = 0 = ground).
  * Env: NS_QUICK=1 fast low-res preview (to previews/I_world/_quick/), NS_PARTS=1 prints the
    parts, NS_NORENDER=1 skips renders, NS_EXPORT=1 exports. Every preview gets a third
    panel: the asset seen from ~4x its size away, at eye height, 70 deg FOV, dusk light and
    linear distance fog ("game distance" review).
"""
from __future__ import annotations

import importlib.util
import math
import os
import random
import sys

# Pillow lives in the system site-packages (same CPython 3.13 build); nslib's preview needs it.
# Appended last so the venv's own packages (numpy, bpy) always win.
_SYS_SITE = "/usr/local/lib/python3.13/site-packages"
try:
    import PIL  # noqa: F401
except ImportError:
    if os.path.isdir(os.path.join(_SYS_SITE, "PIL")) and _SYS_SITE not in sys.path:
        sys.path.append(_SYS_SITE)

import bpy  # noqa: E402,F401  (must load before bmesh in the bpy module build)
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "lib"))
import nslib as ns  # noqa: E402


def _load(modname, folder):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(_HERE, "..", folder, "_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _load("shop_common", "B_shop")      # B_shop shape helpers
L = _load("lobby_common", "C_lobby")    # C_lobby helpers

fillet, rrect, circle_pts, ellipse_pts = S.fillet, S.rrect, S.circle_pts, S.ellipse_pts
prism, slab, pipe, round_path, ring_slab = S.prism, S.slab, S.pipe, S.round_path, S.ring_slab
text_mesh, fit_text_width, bbox_of, merge = S.text_mesh, S.fit_text_width, S.bbox_of, S.merge
FONT_BOLD, FONT_BOLD_ITALIC = S.FONT_BOLD, S.FONT_BOLD_ITALIC
rod, catenary, text, place, yaw_point = L.rod, L.catenary, L.text, L.place, L.yaw_point
screen_meta, disc, annulus, arc_solid = L.screen_meta, L.disc, L.annulus, L.arc_solid
part = L.part   # apply + join + tag (asserts the name is not a preview-rig prefix)

BATCH = "I_world"
GROUP = "World"
PREVIEWS = os.path.join(ns.REPO, "..", "previews", BATCH)

# ---------------------------------------------------------------------------------------
# Palette (SHARED.md palette + world extras). Night scene: greens a little desaturated and
# dark, never black; sky reads purple-pink.
# ---------------------------------------------------------------------------------------
CREAM = "#EFE6D2"
STAINLESS = "#B9C0C6"
CHROME = "#D3D8DC"
NAVY = "#1E2A44"
NAVY_DEEP = "#141C2E"
PINK = "#FF4FA3"
CYAN = "#38E1FF"
BRAND = "#E8502A"
BRAND_DARK = "#B83D22"
MUSTARD = "#F2B33D"
BRICK = "#8A3E30"
CHARCOAL = "#3A3D42"
WARM_BULB = "#FFD99A"
STEEL = "#3B4046"
CONCRETE = "#8E8C86"
SCREEN = "#121823"          # dark glossy screen panel (the game draws the content)

GREEN_DARK = "#2F5229"
GREEN_MID = "#3E6B35"
GREEN_LIGHT = "#4E8A3A"
BARK = "#5A3926"
BARK_DARK = "#47301F"
HILL = "#2F4A2A"
HILL_LIGHT = "#37552F"
ROCK = "#675F56"
ROCK_LIGHT = "#8A8175"
ROCK_DARK = "#5A534B"
CITY = ("#2A3142", "#2F3647", "#343B4C", "#3A4152")   # distant building blue-greys
CITY_ROOF = "#242A38"
AIRCRAFT_RED = "#FF3B30"

FORBIDDEN = ("PreviewCam", "Key", "Fill", "Rim", "RefCube", "Floor", "Sun", "Moon")


# ---------------------------------------------------------------------------------------
# Generic mesh helpers
# ---------------------------------------------------------------------------------------

def mesh_obj(verts, faces, name="Mesh"):
    """Object from raw verts / faces (faces wound counter-clockwise seen from outside)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate(clean_customdata=False)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def split_faces(obj, key, name="Split"):
    """Split an applied mesh object into several objects by a per-face key function
    key(center: Vector, normal: Vector, index: int) -> hashable. Returns {key: object}.
    Used to give facets two colours (each colour = its own tagged part; nslib merges them
    back into one vertex-coloured MeshPart at export)."""
    ns.apply_all(obj)
    me = obj.data
    groups: dict = {}
    for poly in me.polygons:
        groups.setdefault(key(Vector(poly.center), Vector(poly.normal), poly.index), []).append(poly.index)
    out = {}
    for k, idxs in groups.items():
        keep = set(idxs)
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        nm = bpy.data.meshes.new(f"{name}_{k}")
        bm.to_mesh(nm)
        bm.free()
        ob = bpy.data.objects.new(f"{name}_{k}", nm)
        bpy.context.scene.collection.objects.link(ob)
        out[k] = ob
    bpy.data.objects.remove(obj, do_unlink=True)
    return out


def drop_faces(obj, pred):
    """Delete the faces of an applied object for which pred(center, normal) is true
    (e.g. the hidden underside of something that sits on the ground)."""
    ns.apply_all(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    dead = [f for f in bm.faces if pred(f.calc_center_median(), f.normal)]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def cull_hidden(objs, margin=0.05):
    """Delete the faces of each closed blob that lie entirely inside another blob of the
    list (hidden overlap). The union's outer surface is untouched: a face is only removed
    when all its vertices are deeper than `margin` inside some other blob."""
    from mathutils.bvhtree import BVHTree
    for o in objs:
        ns.apply_all(o)
    trees = []
    for o in objs:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.normal_update()
        trees.append(BVHTree.FromBMesh(bm))
        bm.free()
    removed = 0
    for i, o in enumerate(objs):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        inside = set()
        for v in bm.verts:
            for j, t in enumerate(trees):
                if j == i:
                    continue
                hit = t.find_nearest(v.co)
                if hit[0] is not None and (v.co - hit[0]).dot(hit[1]) < -margin:
                    inside.add(v.index)
                    break
        dead = [f for f in bm.faces if all(v.index in inside for v in f.verts)]
        removed += len(dead)
        bmesh.ops.delete(bm, geom=dead, context="FACES")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        bm.to_mesh(o.data)
        bm.free()
    return removed


def two_tone(objs, up=0.35, name="Two"):
    """Split blobs into upward-facing facets ('L') and the rest ('D'): a baked moonlight
    gradient that still reads when the engine lighting is dim. Returns (light, dark) lists."""
    light, dark = [], []
    for k, o in enumerate(objs):
        d = split_faces(o, lambda c, n, i: "L" if n.z > up else "D", name=f"{name}{k}")
        if "L" in d:
            light.append(d["L"])
        if "D" in d:
            dark.append(d["D"])
    return light, dark


def flatten_below(obj, z=0.0, cap=True):
    """Clamp every vertex below z up to z (flat base for things that sit on the ground).
    cap=True dissolves the flattened faces into one flat n-gon (fewer triangles)."""
    ns.apply_all(obj)
    for v in obj.data.vertices:
        if v.co.z < z:
            v.co.z = z
    obj.data.update()
    if cap:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        flat = [f for f in bm.faces if all(abs(v.co.z - z) < 1e-5 for v in f.verts)]
        if len(flat) > 1:
            bmesh.ops.dissolve_faces(bm, faces=flat, use_verts=True)
        bm.to_mesh(obj.data)
        bm.free()
    return obj


def transform_obj(obj, loc=(0, 0, 0), rot_deg=(0, 0, 0), scale=(1, 1, 1), origin=(0, 0, 0)):
    """Scale, rotate (XYZ Euler degrees) about `origin`, then move by loc — baked into verts."""
    from mathutils import Euler
    ns.apply_all(obj)
    o = Vector(origin)
    R = Euler(tuple(math.radians(a) for a in rot_deg), "XYZ").to_matrix()
    for v in obj.data.vertices:
        p = v.co - o
        p = Vector((p.x * scale[0], p.y * scale[1], p.z * scale[2]))
        v.co = o + R @ p + Vector(loc)
    obj.data.update()
    return obj


def ico_blob(r, loc=(0, 0, 0), scale=(1, 1, 1), subdiv=2, seed=1, jitter=0.12, rot_z=None, name="Blob"):
    """Lumpy faceted blob: an icosphere (subdiv 1 = 20 tris, 2 = 80 tris) with deterministic
    radial noise, scaled and moved. For canopy / shrub clumps."""
    rnd = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=r)
    ob = bpy.context.active_object
    ob.name = name
    rz = rnd.uniform(0, math.tau) if rot_z is None else math.radians(rot_z)
    c, s = math.cos(rz), math.sin(rz)
    for v in ob.data.vertices:
        k = 1.0 + rnd.uniform(-jitter, jitter)
        x, y, z = v.co.x * k, v.co.y * k, v.co.z * k
        x, y = x * c - y * s, x * s + y * c
        v.co = Vector((x * scale[0] + loc[0], y * scale[1] + loc[1], z * scale[2] + loc[2]))
    ob.data.update()
    return ob


def hull_rock(n, rx, ry, rz, seed=1, noise=0.16, base_cut=0.45, cuts=(), name="Rock"):
    """Faceted boulder: convex hull of n noisy points on an ellipsoid (big chunky facets),
    flattened at the bottom (points below -base_cut*rz are clamped) and sat on z = 0.
    cuts = [(plane_normal, frac)]: chisel planes through centre + normal * frac * extent."""
    rnd = random.Random(seed)
    pts = []
    golden = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        zz = 1.0 - 2.0 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1.0 - zz * zz))
        th = golden * i + rnd.uniform(-0.35, 0.35)
        k = 1.0 + rnd.uniform(-noise, noise)
        pts.append(Vector((math.cos(th) * rr * rx * k, math.sin(th) * rr * ry * k, zz * rz * k)))
    zcut = -base_cut * rz
    pts = [Vector((p.x, p.y, max(p.z, zcut))) for p in pts]
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in pts]
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    junk = list({g for g in res["geom_interior"] + res["geom_unused"] if isinstance(g, bmesh.types.BMVert)})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    bmesh.ops.translate(bm, verts=bm.verts[:], vec=(0, 0, -zcut))
    # chisel cuts: slice the (convex) hull with planes and cap each cut with one flat face
    for nrm, frac in cuts:
        nv = Vector(nrm).normalized()
        centre = Vector((0, 0, rz * (1 - base_cut)))
        ext = max((v.co - centre).dot(nv) for v in bm.verts)
        co = centre + nv * (ext * frac)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=nv, clear_outer=True)
        cut_edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        if cut_edges:
            bmesh.ops.holes_fill(bm, edges=cut_edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def lathe(profile, verts=8, loc=(0, 0, 0), name="Lathe", phase=0.0):
    """ns.lathe with a phase (rotate the ring so facets don't all line up between parts)."""
    ob = ns.lathe(profile, verts=verts, loc=(0, 0, 0), name=name)
    if phase:
        transform_obj(ob, rot_deg=(0, 0, phase))
    if any(loc):
        transform_obj(ob, loc=loc)
    return ob


def box(size, loc, rot=(0, 0, 0), bevel=0.0, segments=1, name="Box"):
    return ns.box(size, loc=loc, rot=rot, bevel=bevel, segments=segments, name=name)


def beam(p0, p1, w, d, name="Beam", bevel=0.0, roll=0.0):
    """Rectangular bar from p0 to p1 (w across, d deep), optionally rolled about its axis."""
    p0, p1 = Vector(p0), Vector(p1)
    v = p1 - p0
    b = ns.box((w, d, v.length), loc=(0, 0, 0), bevel=bevel, segments=1, name=name)
    q = v.to_track_quat("Z", "Y")
    if roll:
        from mathutils import Quaternion
        q = q @ Quaternion((0, 0, 1), math.radians(roll))
    b.rotation_euler = q.to_euler()
    b.location = (p0 + p1) / 2
    return b


def ibeam(x, y, z0, z1, w=0.9, d=0.9, tf=0.16, tw=0.14, name="IBeam"):
    """Vertical steel I-beam (H section), flanges parallel to the XZ plane (front/back)."""
    hw, hd = w / 2, d / 2
    prof = [(-hw, -hd), (hw, -hd), (hw, -hd + tf), (tw / 2, -hd + tf), (tw / 2, hd - tf), (hw, hd - tf),
            (hw, hd), (-hw, hd), (-hw, hd - tf), (-tw / 2, hd - tf), (-tw / 2, -hd + tf), (-hw, -hd + tf)]
    prof = [(x + a, y + b) for a, b in prof]
    return prism(prof, "z", z0, z1, name=name)


def bipyramid(r, h, loc, sides=4, axis="y", name="Bulb"):
    """Tiny double pyramid (2*sides tris) — a marquee bulb that pokes out of both faces of
    a thin board when its axis crosses the board."""
    bm = bmesh.new()
    ring = []
    for i in range(sides):
        a = 2 * math.pi * (i + 0.5) / sides
        u, v = r * math.cos(a), r * math.sin(a)
        ring.append(bm.verts.new((u, 0.0, v) if axis == "y" else (u, v, 0.0)))
    tip_a = bm.verts.new((0, -h, 0) if axis == "y" else (0, 0, h))
    tip_b = bm.verts.new((0, h, 0) if axis == "y" else (0, 0, -h))
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new([ring[i], ring[j], tip_a])
        bm.faces.new([ring[j], ring[i], tip_b])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.translate(bm, verts=bm.verts[:], vec=Vector(loc))
    return ns.from_bmesh(bm, name)


def text_outline(txt, height, offset, loc, width=None, res=1, spacing=1.0, facing="-Y", name="Outline",
                 ref_width_text=None):
    """Flat (front caps only) glyph silhouette grown by `offset` studs: placed just behind
    modelled letters it reads as a neon outline round every letter. `width` fits the
    UN-grown text block to that width first, so it lines up with C.text(..., width=width)."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = txt
    cu.font = bpy.data.fonts.load(FONT_BOLD, check_existing=True)
    cu.size = height
    cu.extrude = 0.02
    cu.resolution_u = res
    cu.space_character = spacing
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    # scale factor from the plain text width
    if width:
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        me = ob.evaluated_get(dg).to_mesh()
        xs = [v.co.x for v in me.vertices]
        plain_w = max(xs) - min(xs)
        plain_c = (max(xs) + min(xs)) / 2
        ys = [v.co.y for v in me.vertices]
        plain_cy = (max(ys) + min(ys)) / 2
        ob.evaluated_get(dg).to_mesh_clear()
        k = width / plain_w
    else:
        k, plain_c, plain_cy = 1.0, 0.0, 0.0
    cu.offset = offset / k
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bm.normal_update()
    # keep only the caps facing +Z (they become the front, -Y, after standing the text up)
    dead = [f for f in bm.faces if f.normal.z < 0.95]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:])
    for v in bm.verts:
        v.co.x = (v.co.x - plain_c) * k
        v.co.y = (v.co.y - plain_cy) * k
        v.co.z = 0.0
    bm.to_mesh(ob.data)
    bm.free()
    # stand up in XZ facing -Y, centred on loc
    for v in ob.data.vertices:
        x, y = v.co.x, v.co.y
        v.co = Vector((loc[0] + x, loc[1], loc[2] + y))
    if facing == "+Y":
        # mirroring X alone is a reflection: the glyphs read correctly from behind and the
        # cap's winding now faces +Y (no face reversal needed)
        c = Vector(loc)
        for v in ob.data.vertices:
            v.co.x = 2 * c.x - v.co.x
    ob.data.update()
    ob.name = name
    return ob


# ---------------------------------------------------------------------------------------
# Distant buildings (skylines)
# ---------------------------------------------------------------------------------------

class QuadSet:
    """Collects single-sided axis-aligned quads (windows) into one bmesh."""

    def __init__(self):
        self.bm = bmesh.new()

    def add(self, centre, w, h, facing):
        """facing: '-Y', '+Y', '-X', '+X' (the side the quad is seen from)."""
        cx, cy, cz = centre
        hw, hh = w / 2, h / 2
        if facing == "-Y":
            pts = [(cx - hw, cy, cz - hh), (cx + hw, cy, cz - hh), (cx + hw, cy, cz + hh), (cx - hw, cy, cz + hh)]
        elif facing == "+Y":
            pts = [(cx + hw, cy, cz - hh), (cx - hw, cy, cz - hh), (cx - hw, cy, cz + hh), (cx + hw, cy, cz + hh)]
        elif facing == "+X":
            pts = [(cx, cy - hw, cz - hh), (cx, cy + hw, cz - hh), (cx, cy + hw, cz + hh), (cx, cy - hw, cz + hh)]
        else:  # -X
            pts = [(cx, cy + hw, cz - hh), (cx, cy - hw, cz - hh), (cx, cy - hw, cz + hh), (cx, cy + hw, cz + hh)]
        self.bm.faces.new([self.bm.verts.new(p) for p in pts])

    def obj(self, name):
        if not self.bm.faces:
            self.bm.free()
            return None
        return ns.from_bmesh(self.bm, name)


def no_bottom(obj):
    """Drop downward faces sitting on the ground (never visible) — saves 2 tris per box."""
    return drop_faces(obj, lambda c, n: n.z < -0.9 and c.z < 0.05)


def facade(dark, lit, rnd, x0, x1, z0, z1, face, facing, floor_h=3.6, kind="punched", win_w=1.3, win_h=1.8,
           pitch=2.6, lit_patches=(), lit_extra=0.0, proud=0.06):
    """Window grid on one facade. x0..x1 = the facade's horizontal span (world X for -Y/+Y
    facades, world Y for +-X), z0..z1 = window band heights, face = the facade plane
    coordinate. kind 'punched' = rows of single windows, 'ribbon' = one long dark band per
    floor. lit_patches = [(floor_a, floor_b, col_a, col_b)] (inclusive; for ribbons the
    columns index ~pitch-wide segments) lit in warm Neon; lit_extra = random lit chance."""
    sgn = -1 if facing in ("-Y", "-X") else 1
    fpos = face + sgn * proud
    floors = int((z1 - z0) // floor_h)
    span = x1 - x0
    cols = max(1, int((span - 0.8) // pitch))
    off = (span - cols * pitch) / 2 + pitch / 2

    def put(qs, u, z, w, h, extra=0.0):
        if facing in ("-Y", "+Y"):
            qs.add((u, fpos + sgn * extra, z), w, h, facing)
        else:
            qs.add((fpos + sgn * extra, u, z), w, h, facing)

    def is_lit(f, c):
        return any(a <= f <= b and ca <= c <= cb for a, b, ca, cb in lit_patches) or rnd.random() < lit_extra

    for f in range(floors):
        z = z0 + f * floor_h + floor_h / 2
        if kind == "ribbon":
            put(dark, (x0 + x1) / 2, z, span - 1.0, win_h * 0.8)
            for c in range(cols):
                if is_lit(f, c):
                    put(lit, x0 + off + c * pitch, z, pitch * 0.92, win_h * 0.62, extra=0.03)
        else:
            for c in range(cols):
                u = x0 + off + c * pitch
                put(lit if is_lit(f, c) else dark, u, z, win_w, win_h)


# ---------------------------------------------------------------------------------------
# Foliage builders
# ---------------------------------------------------------------------------------------

def pine_tier(R, H, z0, n=7, seed=1, notch=0.8, notch_lift=0.13, band=0.24, under=0.32,
              center=(0.0, 0.0), tilt=(0.0, 0.0)):
    """One stylized pine tier: a jagged skirt of n branch tips (2n rim points alternating
    tip / notch), a 'tips' band, a cone up to the apex and a recessed underside.
    Returns (cone, band, underside) objects (8n triangles in all) so they can carry
    different colours. tilt = (deg about X, deg about Y) round the tier's base centre."""
    rnd = random.Random(seed)
    tw = rnd.uniform(0, math.tau)
    m = 2 * n
    zb = z0 + band * H
    rim, top = [], []
    for i in range(m):
        a = tw + math.pi * i / n + rnd.uniform(-0.07, 0.07)
        if i % 2 == 0:
            r = R * rnd.uniform(0.93, 1.06)
            z = z0 + rnd.uniform(0.0, 0.05) * H
        else:
            r = R * notch * rnd.uniform(0.96, 1.04)
            z = z0 + notch_lift * H
        rim.append(Vector((r * math.cos(a), r * math.sin(a), z)))
        rb = R * (1.0 - band) * (0.98 if i % 2 == 0 else 0.92) * rnd.uniform(0.97, 1.03)
        top.append(Vector((rb * math.cos(a), rb * math.sin(a), zb)))
    apex = Vector((rnd.uniform(-0.04, 0.04) * R, rnd.uniform(-0.04, 0.04) * R, z0 + H))
    hub = Vector((0.0, 0.0, z0 + under * H))

    from mathutils import Euler
    Rm = Euler((math.radians(tilt[0]), math.radians(tilt[1]), 0.0), "XYZ").to_matrix()
    base = Vector((0.0, 0.0, z0))
    off = Vector((center[0], center[1], 0.0))

    def T(p):
        return base + Rm @ (p - base) + off

    rim = [T(p) for p in rim]
    top = [T(p) for p in top]
    apex, hub = T(apex), T(hub)

    cone = mesh_obj(top + [apex], [(i, (i + 1) % m, m) for i in range(m)], "TierCone")
    bandv = rim + top
    band_o = mesh_obj(bandv, [(i, (i + 1) % m, m + (i + 1) % m, m + i) for i in range(m)], "TierBand")
    und = mesh_obj(rim + [hub], [((i + 1) % m, i, m) for i in range(m)], "TierUnder")
    return cone, band_o, und


def pine(tiers, trunk_r, trunk_top, seed=3, n=7, lean=(0.0, 0.0), trunk_verts=7,
         colors=(GREEN_DARK, GREEN_MID), tip_colors=("#3D6634", "#4C7C3F"), under_color="#233D20"):
    """Build a stylized pine from tier specs [(R, H, z0), ...] (bottom to top).
    lean = (dx, dy) offset of the top tier; lower tiers interpolate (a baked lean).
    Tags: Foliage* parts (SmoothPlastic, no collision) and Trunk (Wood, collides)."""
    rnd = random.Random(seed)
    groups = {}
    k = len(tiers)
    for i, (R, H, z0) in enumerate(tiers):
        t = (i + 1) / k
        cx, cy = lean[0] * t * t, lean[1] * t * t
        tilt = (math.degrees(math.atan2(-lean[1] * 2 * t, max(z0, 1.0))) * 0.25 + rnd.uniform(-2.5, 2.5),
                math.degrees(math.atan2(lean[0] * 2 * t, max(z0, 1.0))) * 0.25 + rnd.uniform(-2.5, 2.5))
        cone, band_o, und = pine_tier(R, H, z0, n=n, seed=seed * 31 + i, center=(cx, cy), tilt=tilt)
        groups.setdefault(colors[i % 2], []).append(cone)
        groups.setdefault(tip_colors[i % 2], []).append(band_o)
        groups.setdefault(under_color, []).append(und)
    names = {colors[0]: "FoliageA", colors[1]: "FoliageB", tip_colors[0]: "TipsA", tip_colors[1]: "TipsB",
             under_color: "Underside"}
    for col, objs in groups.items():
        part(objs, names[col], col, "SmoothPlastic", smooth_angle=None)
    # trunk: flared base, tapering up into the canopy, leaning with the tree
    top_lean = (lean[0] * (1.0 / k) ** 2 * 1.4, lean[1] * (1.0 / k) ** 2 * 1.4)
    prof = [(trunk_r * 1.55, 0.0), (trunk_r * 1.08, 0.45), (trunk_r, 1.1), (trunk_r * 0.62, trunk_top)]
    tr = lathe(prof, verts=trunk_verts, phase=rnd.uniform(0, 50))
    for v in tr.data.vertices:
        f = max(0.0, v.co.z) / max(trunk_top, 1e-3)
        v.co.x += top_lean[0] * f
        v.co.y += top_lean[1] * f
    part([tr], "Trunk", BARK, "Wood", can_collide=True, smooth_angle=None)


# ---------------------------------------------------------------------------------------
# Hills
# ---------------------------------------------------------------------------------------

def hill_mesh(L_x, D_y, H, nu, nv, seed=5, crest=0.12, humps=((0.0, 1.0),), sink=0.5, end_w=0.18,
              taper=0.62, jitter=0.35, name="Hill"):
    """Low-poly rolling ridge heightfield. Footprint: X in [-L/2, L/2], Y in [-D/2, D/2],
    narrowing to `end_w` of the depth at the X ends (stadium-like). Height: cosine ridge
    across Y (crest at v = crest, + = toward the back), modulated along X by Gaussian
    `humps` [(u_centre, height_frac)], end taper. The boundary ring sits at z = -sink (it
    sinks below the ground plane), the underside is one flat cap at z = -sink.
    Returns the object (flat-shade it)."""
    rnd = random.Random(seed)
    verts, grid = [], []

    def width(u):
        a = min(1.0, abs(u))
        return end_w + (1.0 - end_w) * math.sqrt(max(0.0, 1.0 - a ** 4))

    def along(u):
        h = 0.0
        for uc, hf in humps:
            h = max(h, hf * math.exp(-((u - uc) / 0.42) ** 2))
        a = abs(u)
        e = 1.0 if a < taper else 0.5 * (1.0 + math.cos(math.pi * min(1.0, (a - taper) / (1.0 - taper))))
        return h * e

    for j in range(nv):
        row = []
        v = -1.0 + 2.0 * j / (nv - 1)
        for i in range(nu):
            u = -1.0 + 2.0 * i / (nu - 1)
            edge = (j in (0, nv - 1)) or (i in (0, nu - 1))
            uu = u
            vv = v
            if not edge:
                uu += rnd.uniform(-jitter, jitter) / (nu - 1)
                vv += rnd.uniform(-jitter, jitter) / (nv - 1)
            c = crest + 0.08 * math.sin(3.1 * uu + seed)
            if vv <= c:
                b = 0.5 * (1.0 + math.cos(math.pi * (vv - c) / (1.0 + c)))
            else:
                b = 0.5 * (1.0 + math.cos(math.pi * (vv - c) / (1.0 - c)))
            z = -sink + (H + sink) * b * along(uu)
            if not edge:
                z += rnd.uniform(-0.035, 0.035) * H * b
                z = max(z, -sink + 0.05)
            else:
                z = -sink
            x = uu * L_x / 2
            y = vv * D_y / 2 * width(uu)
            row.append(len(verts))
            verts.append((x, y, z))
        grid.append(row)
    faces = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            a, b_, c_, d = grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]
            # alternate the split diagonal for a more organic facet pattern
            if (i + j) % 2 == 0:
                faces += [(a, b_, c_), (a, c_, d)]
            else:
                faces += [(a, b_, d), (b_, c_, d)]
    # boundary ring (counter-clockwise from above) -> bottom cap faces down
    ring = [grid[0][i] for i in range(nu)] + [grid[j][nu - 1] for j in range(1, nv)] + \
           [grid[nv - 1][i] for i in range(nu - 2, -1, -1)] + [grid[j][0] for j in range(nv - 2, 0, -1)]
    faces.append(tuple(reversed(ring)))
    ob = mesh_obj(verts, faces, name)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(ob.data)
    bm.free()
    return ob


# ---------------------------------------------------------------------------------------
# Review renders: "game distance" dusk view, part listing, contact sheet
# ---------------------------------------------------------------------------------------
DUSK_FOG = "#4A4262"        # fog / horizon colour (purple-grey dusk)
DUSK_GROUND = "#2B302B"


def _lin(hexcol):
    return tuple(ns.srgb_to_linear(c) for c in ns.hex_rgb(hexcol))


def _fog_materials(start, end, color_hex, max_fog=1.0):
    r, g, b = _lin(color_hex)
    undo = []
    for m in bpy.data.materials:
        if not m.use_nodes or m.node_tree is None:
            continue
        nt = m.node_tree
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out is None or not out.inputs["Surface"].links:
            continue
        src = out.inputs["Surface"].links[0].from_socket
        cam = nt.nodes.new("ShaderNodeCameraData")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.clamp = True
        mr.inputs["From Min"].default_value = start
        mr.inputs["From Max"].default_value = end
        mr.inputs["To Min"].default_value = 0.0
        mr.inputs["To Max"].default_value = max_fog
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (r, g, b, 1.0)
        em.inputs["Strength"].default_value = 1.0
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(cam.outputs["View Distance"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], mix.inputs[0])
        nt.links.new(src, mix.inputs[1])
        nt.links.new(em.outputs["Emission"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
        undo.append((nt, out, src, [cam, mr, em, mix]))
    return undo


def _unfog(undo):
    for nt, out, src, nodes in undo:
        for n in nodes:
            nt.nodes.remove(n)
        nt.links.new(src, out.inputs["Surface"])


def far_view(asset, out_dir, res=384, samples=8, mult=4.0, fov=70.0, yaw=-28.0, eye=4.5, fog_at=0.33):
    """Dusk 'game distance' render: camera at eye height, mult x the asset's largest
    dimension away, Roblox-like 70 deg vertical FOV, purple dusk ambient + low warm sun,
    linear distance fog that reaches `fog_at` at the asset. Returns the PNG path."""
    sc = bpy.context.scene
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    size = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z)
    dist = mult * size
    tgt = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, max(0.0, lo.z) + (hi.z - max(0.0, lo.z)) * 0.42))
    a = math.radians(yaw)
    cam_loc = Vector((tgt.x + math.sin(a) * dist, tgt.y - math.cos(a) * dist, eye))
    ns._setup_render(res, samples, transparent=False)
    bg = sc.world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (*_lin(DUSK_FOG), 1.0)
    bg.inputs[1].default_value = 1.0
    bpy.ops.mesh.primitive_plane_add(size=dist * 12, location=(tgt.x, tgt.y, -0.002))
    fl = bpy.context.active_object
    fl.name = "Floor"
    fl.data.materials.append(ns.material(DUSK_GROUND, "Concrete"))
    cd = bpy.data.cameras.new("PreviewCam")
    cd.angle = math.radians(fov)
    cd.sensor_fit = "VERTICAL"
    cd.clip_start = 0.1
    cd.clip_end = dist * 8
    cam = bpy.data.objects.new("PreviewCam", cd)
    sc.collection.objects.link(cam)
    cam.location = cam_loc
    cam.rotation_euler = (tgt - cam_loc).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    # low warm sun from the camera's front-left, cool moon fill from the right
    for nm, col, energy, az, el in (("Key", "#FFB79A", 2.2, yaw - 70, 22), ("Fill", "#9AA8FF", 0.5, yaw + 80, 35)):
        ld = bpy.data.lights.new(nm, "SUN")
        ld.energy = energy
        ld.color = _lin(col)
        ld.angle = math.radians(3)
        ob = bpy.data.objects.new(nm, ld)
        sc.collection.objects.link(ob)
        az_r, el_r = math.radians(az), math.radians(el)
        d = -Vector((math.sin(az_r) * math.cos(el_r), -math.cos(az_r) * math.cos(el_r), math.sin(el_r)))
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    start = dist * 0.25
    end = start + (dist - start) / max(fog_at, 1e-3)
    undo = _fog_materials(start, end, DUSK_FOG)
    path = os.path.join(out_dir, f"{asset}_far.png")
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    _unfog(undo)
    ns._clear_rig()
    return path


def _combine(paths, out):
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in paths]
    h = max(im.height for im in ims)
    combo = Image.new("RGB", (sum(im.width for im in ims), h))
    x = 0
    for im in ims:
        combo.paste(im, (x, 0))
        x += im.width
    combo.save(out)
    return out


def print_parts(asset):
    dg = bpy.context.evaluated_depsgraph_get()
    tot = 0
    for o in sorted(ns._tagged_objects(), key=lambda o: o.name):
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        n = len(me.loop_triangles)
        tot += n
        print(f"  [{asset}] {o.name:18s} {n:5d} tris  {o['ns_material']:13s} {o['ns_color']} "
              f"collide={o['ns_can_collide']} role={o.get('ns_role')}")
        o.evaluated_get(dg).to_mesh_clear()
    lo, hi = ns.bbox_world(ns._tagged_objects())
    print(f"  [{asset}] bbox lo {tuple(round(c, 2) for c in lo)} hi {tuple(round(c, 2) for c in hi)} "
          f"size {tuple(round(h - l, 2) for l, h in zip(lo, hi))} total {tot}")


def closeup(asset, spec, res=448, samples=8):
    """Detail render for review: spec = "x,y,z,dist[,yaw,pitch]" (Blender coords, degrees;
    yaw 0 = looking at the front from -Y). Writes previews/I_world/_quick/<asset>_close.png."""
    vals = [float(v) for v in spec.split(",")]
    x, y, z, dist = vals[:4]
    yaw = vals[4] if len(vals) > 4 else -30.0
    pitch = vals[5] if len(vals) > 5 else 15.0
    sc = bpy.context.scene
    ns._setup_render(res, samples, transparent=False)
    tgt = Vector((x, y, z))
    a, p = math.radians(yaw), math.radians(pitch)
    loc = tgt + Vector((math.sin(a) * math.cos(p), -math.cos(a) * math.cos(p), math.sin(p))) * dist
    cd = bpy.data.cameras.new("PreviewCam")
    cd.angle = math.radians(40)
    cd.clip_start = 0.05
    cd.clip_end = dist * 20
    cam = bpy.data.objects.new("PreviewCam", cd)
    sc.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    ns._light("Key", "AREA", tgt + Vector((math.sin(a - 0.8), -math.cos(a - 0.8), 0.9)) * dist,
              60 * dist ** 2 / 9, size=dist * 0.6, target=tgt)
    ns._light("Fill", "AREA", tgt + Vector((math.sin(a + 1.2), -math.cos(a + 1.2), 0.3)) * dist,
              25 * dist ** 2 / 9, size=dist * 0.8, target=tgt)
    ns._light("Rim", "AREA", tgt + Vector((-math.sin(a), math.cos(a), 0.8)) * dist, 30 * dist ** 2 / 9,
              size=dist * 0.4, target=tgt)
    out_dir = os.path.join(PREVIEWS, "_quick")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{asset}_close.png")
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    ns._clear_rig()
    return path


def run(build, asset, sockets=None, pivot=(0.0, 0.0, 0.0), far=True, far_kw=None, **export_kw):
    """Standard I_world entry: build -> preview (2 nslib panels + the dusk far view) ->
    export when NS_EXPORT=1."""
    ns.reset()
    extra = build() or {}
    tris = ns.tri_count()
    print(f"[{asset}] triangles: {tris}")
    if os.environ.get("NS_PARTS") == "1":
        print_parts(asset)
    if os.environ.get("NS_NORENDER") != "1":
        quick = os.environ.get("NS_QUICK") == "1"
        res, spp = (320, 8) if quick else (512, 16)
        out_dir = os.path.join(PREVIEWS, "_quick") if quick else PREVIEWS
        os.makedirs(out_dir, exist_ok=True)
        prev = ns.render_preview(asset, out_dir=out_dir, res=res, samples=spp)
        if far:
            fv = far_view(asset, out_dir, res=res, samples=spp, **(far_kw or {}))
            _combine([prev, fv], prev)
            os.remove(fv)
        print(f"[{asset}] preview: {prev}")
    if os.environ.get("NS_CLOSEUP"):
        for i, spec in enumerate(os.environ["NS_CLOSEUP"].split(";")):
            p = closeup(asset if i == 0 else f"{asset}{i}", spec)
            print(f"[{asset}] closeup: {p}")
    if os.environ.get("NS_EXPORT") == "1":
        kw = dict(export_kw)
        kw.update(extra.get("export", {}))
        doc = ns.export_asset(asset, BATCH, group=GROUP, sockets=sockets, pivot=pivot, **kw)
        print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']}")
        for p in doc["parts"]:
            print(f"    part {p['name']:18s} {p['material']:13s} role={p['role']} tris={p['tris']} "
                  f"collide={p['canCollide']}")
        if doc.get("sockets"):
            print(f"    sockets {doc['sockets']}")
    return extra


def contact_sheet(cols=2, panel=240):
    """Labelled grid of every final <asset>_preview.png in previews/I_world/."""
    from PIL import Image, ImageDraw
    files = sorted(f for f in os.listdir(PREVIEWS) if f.endswith("_preview.png"))
    assert files, f"no previews in {PREVIEWS}"
    ims = [Image.open(os.path.join(PREVIEWS, f)).convert("RGB") for f in files]
    tw = panel * 3
    th = panel + 26
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols + 8 * (cols - 1), th * rows), (22, 24, 28))
    draw = ImageDraw.Draw(sheet)
    for i, (f, im) in enumerate(zip(files, ims)):
        im = im.resize((tw, int(im.height * tw / im.width)), Image.LANCZOS)
        x, y = (i % cols) * (tw + 8), (i // cols) * th
        sheet.paste(im, (x, y + 26))
        draw.text((x + 8, y + 7), f.replace("_preview.png", "") + "   (front 3/4 | rear 3/4 + 1-stud cube | dusk, 4x size away)",
                  fill=(235, 235, 235))
    out = os.path.join(PREVIEWS, "_contact.png")
    sheet.save(out)
    return out
