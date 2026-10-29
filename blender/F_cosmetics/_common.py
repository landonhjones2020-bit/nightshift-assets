"""Shared helpers for the F_cosmetics batch (player cosmetics: aprons, hats, held-item skins).

Import from a generator in this folder with:
    import _common as C          (the folder is on sys.path when the script runs)
    ns = C.ns                     (the shared nslib)

How the game uses these meshes (the interface):
  * The game clones Assets.Cosmetics.Cosmetic_<Mesh>, recolours parts by role and welds the
    model with its PIVOT on an R15 attachment. Every asset here exports pivot = (0, 0, 0).
  * Roles: cos_body (main colour), cos_trim (accent), cos_beam (flashlight lens / glow).
    Parts with a fixed colour (stitches, rivets, pencil...) carry no role.
  * Aprons  -> BodyFrontAttachment. Body BEHIND the pivot (Blender +Y). R15 UpperTorso front
               face is the plane y = 0; see R15_* below for the reference body.
  * Hats    -> HatAttachment = top centre of the Head; head below the pivot.
  * Held    -> Left/RightGripAttachment = grip point at the origin, working end along -Y.

Env flags (on top of nslib's NS_EXPORT=1):
  NS_DRAFT=1       quick low-sample preview into the scratch drafts dir (no export)
  NS_ICON=1        render the catalogue icons that use this mesh with ns.render_icon
  NS_ICON_DRAFT=1  low-sample icon framing test into the drafts dir (no manifest write)
  NS_ONLY_ICON=1   skip preview/export (icons only)
  NS_ICON_IDS=a,b  restrict icon rendering to these catalogue ids
"""
from __future__ import annotations

import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import nslib as ns  # noqa: E402

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

BATCH = "F_cosmetics"
GROUP = "Cosmetics"
ICON_GROUP = "cosmetics"
DRAFT_DIR = os.environ.get(
    "NS_DRAFT_DIR", "/tmp/claude-0/-home-claude/bee54a24-967a-5993-94e6-c9b5acdf45a4/scratchpad/F_cosmetics/drafts")

# ---- reference R15 body (scale 1), in each slot's own Blender frame ------------------
APRON_REF = [1.943, 1.698, 1.004]     # UpperTorso size (x, y, z Roblox) the aprons fit
HAT_REF = [1.159, 1.182, 1.161]       # Head size the hats fit
TORSO_HW = 1.943 / 2                  # UpperTorso half width (x)
TORSO_TOP = 1.06                      # UpperTorso top above BodyFrontAttachment
TORSO_BOT = -0.64                     # UpperTorso bottom / LowerTorso top
LOWER_HW = 1.99 / 2
LOWER_BOT = -1.04                     # LowerTorso bottom = hips
BODY_DEPTH = 1.004                    # torso depth behind the pivot (+Y)
HEAD_R = 0.58                         # head half width (hats)
HEAD_H = 1.182
SHOULDER_Z_HAT = -1.09                # UpperTorso top in the hat frame (neck overlaps ~0.1)

SLOTS = {
    "Apron": {"slot": "Apron", "attach": "BodyFrontAttachment", "ref_size": APRON_REF},
    "Hat": {"slot": "Hat", "attach": "HatAttachment", "ref_size": HAT_REF},
    "Flashlight": {"slot": "Flashlight", "attach": "LeftGripAttachment"},
    "Spatula": {"slot": "Spatula", "attach": "RightGripAttachment"},
}

# ---- palette ---------------------------------------------------------------------------
STITCH_DARK = "#1C1714"
PENCIL = "#F2B33D"
PENCIL_WOOD = "#E8C79A"
GRAPHITE = "#2B2D31"
ERASER = "#F28CA0"
BRASS = "#C9A24A"
STEEL = "#9AA2AA"
RUBBER = "#2B2D31"
CREAM = "#EFE6D2"
BRAND = "#E8502A"
MUSTARD = "#F2B33D"
INK = "#2A2430"

# ---- cosmetics catalogue (Bible 11.12) -> icon recolours --------------------------------
# mesh: Cosmetic_<mesh>; body/trim/beam colours; *_mat Roblox material overrides.
CATALOGUE = {
    "apron_stackhouse": dict(mesh="Apron", body="#C8402F", trim="#F4F1EA"),
    "apron_checkered": dict(mesh="Apron_Checkered", body="#F4F1EA", trim="#C8402F"),
    "apron_ketchup": dict(mesh="Apron_Splash", body="#F4F1EA", trim="#D9302B"),
    "apron_night_owl": dict(mesh="Apron", body="#1F2A44", trim="#FFB020"),
    "apron_butcher": dict(mesh="Apron_Stripes", body="#F4F1EA", trim="#2E5FA8"),
    "apron_first_night": dict(mesh="Apron", body="#2C2C3D", trim="#2EE6FF"),
    "apron_midnight_velvet": dict(mesh="Apron", body="#2A1640", trim="#9B5CFF", body_mat="Fabric", trim_mat="Fabric"),
    "apron_neon": dict(mesh="Apron", body="#12121A", trim="#FF3D7F", trim_mat="Neon"),
    "apron_gravedigger": dict(mesh="Apron_Patched", body="#5A4B3A", trim="#2A2430"),
    "apron_dawn": dict(mesh="Apron", body="#FF9A4D", trim="#FFE16B"),
    "apron_chef_whites": dict(mesh="Apron_Chef", body="#FFFFFF", trim="#E8E4DA"),
    "apron_vip_gold": dict(mesh="Apron", body="#FFB020", trim="#FFF1B8", body_mat="Foil", trim_mat="Foil"),
    "apron_static": dict(mesh="Apron", body="#1B1B26", trim="#FF2E3A", extras="static"),
    "hat_paper_cap": dict(mesh="Hat_PaperCap", body="#F4F1EA", trim="#C8402F"),
    "hat_hairnet": dict(mesh="Hat_Hairnet", body="#D8D4CC"),
    "hat_trucker": dict(mesh="Hat_Trucker", body="#C8402F", trim="#F4F1EA"),
    "hat_chef_toque": dict(mesh="Hat_Toque", body="#FFFFFF"),
    "hat_night_owl": dict(mesh="Hat_Trucker", body="#1F2A44", trim="#FFB020"),
    "hat_neon": dict(mesh="Hat_Trucker", body="#12121A", trim="#2EE6FF", trim_mat="Neon"),
    "hat_paper_bag": dict(mesh="Hat_PaperBag", body="#C9A274"),
    "hat_rain_hood": dict(mesh="Hat_RainHood", body="#F2C230"),
    "hat_lampshade": dict(mesh="Hat_Lampshade", body="#E8DCC0", trim="#3A2E28"),
    "fl_standard": dict(mesh="Flashlight", body="#2C2C3D", trim="#A9A6B8"),
    "fl_candy": dict(mesh="Flashlight_Striped", body="#F4F1EA", trim="#FF3D7F"),
    "fl_chrome": dict(mesh="Flashlight", body="#C9CCD6", trim="#7A7F8C", body_mat="Metal", trim_mat="Metal"),
    "fl_red": dict(mesh="Flashlight", body="#D9302B", trim="#2C2C3D", beam="#FF6B5A"),
    "fl_midnight": dict(mesh="Flashlight", body="#1F2A44", trim="#2EE6FF"),
    "fl_ghost_glow": dict(mesh="Flashlight", body="#E9ECF5", trim="#7CFF5A", trim_mat="Neon", beam="#B8FFB0"),
    "fl_neon": dict(mesh="Flashlight", body="#12121A", trim="#FF3D7F", trim_mat="Neon"),
    "fl_lantern": dict(mesh="Flashlight_Lantern", body="#3A3A40", trim="#FFB020", beam="#FFD27A"),
    "sp_standard": dict(mesh="Spatula", body="#C9CCD6", trim="#2C2C3D", body_mat="Metal"),
    "sp_wooden": dict(mesh="Spatula_Wooden", body="#B9824A", body_mat="Wood"),
    "sp_rolling_pin": dict(mesh="Spatula_RollingPin", body="#D9A66B", body_mat="Wood"),
    "sp_frying_pan": dict(mesh="Spatula_Pan", body="#2C2C3D", trim="#5A4B3A", body_mat="Metal"),
    "sp_neon": dict(mesh="Spatula", body="#12121A", trim="#2EE6FF", trim_mat="Neon"),
    "sp_bone": dict(mesh="Spatula_Bone", body="#EDE6D6"),
    "sp_golden": dict(mesh="Spatula", body="#FFB020", trim="#FFF1B8", body_mat="Foil", trim_mat="Foil"),
}


def default_colours(mesh: str) -> dict:
    """Authored colours of a mesh = its first catalogue entry (what Studio shows untouched)."""
    for e in CATALOGUE.values():
        if e["mesh"] == mesh:
            return e
    raise KeyError(mesh)


def slot_meta(slot: str, **extra) -> dict:
    m = dict(SLOTS[slot])
    m.update(extra)
    return m


# --------------------------------------------------------------------------------------
# small maths
# --------------------------------------------------------------------------------------

def smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def catmull(points, per_seg=4, closed=False):
    """Catmull-Rom resample of a 3D control polyline (passes through every point)."""
    P = [Vector(p) for p in points]
    n = len(P)
    out = []
    segs = n if closed else n - 1
    for i in range(segs):
        p0 = P[(i - 1) % n] if closed else P[max(i - 1, 0)]
        p1 = P[i % n]
        p2 = P[(i + 1) % n] if closed else P[min(i + 1, n - 1)]
        p3 = P[(i + 2) % n] if closed else P[min(i + 2, n - 1)]
        for k in range(per_seg):
            t = k / per_seg
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed:
        out.append(P[-1])
    return out


def resample_vecs(vecs, n_out, closed=False):
    """Linear resample of a list of Vectors to n_out entries (for per-point normals)."""
    V = [Vector(v) for v in vecs]
    out = []
    m = len(V)
    for i in range(n_out):
        t = i / (n_out if closed else max(n_out - 1, 1)) * (m if closed else m - 1)
        k = int(math.floor(t))
        f = t - k
        a = V[k % m] if closed else V[min(k, m - 1)]
        b = V[(k + 1) % m] if closed else V[min(k + 1, m - 1)]
        out.append(a.lerp(b, f))
    return out


# --------------------------------------------------------------------------------------
# mesh construction
# --------------------------------------------------------------------------------------

def mesh_obj(name: str, verts, faces, recalc: bool = True, dedupe: float = 1e-5) -> bpy.types.Object:
    """Object from raw verts/faces (faces = index tuples)."""
    bm = bmesh.new()
    bv = [bm.verts.new(v) for v in verts]
    for f in faces:
        try:
            bm.faces.new([bv[i] for i in f])
        except ValueError:
            pass
    if dedupe:
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dedupe)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return obj


def split_mesh(names, verts, face_groups, recalc=True, dedupe=1e-5):
    """Build ONE closed mesh from all face groups (so normals are recalculated consistently),
    then return one object per group (list of index tuples) with only that group's faces."""
    bm = bmesh.new()
    bv = [bm.verts.new(v) for v in verts]
    gl = bm.faces.layers.int.new("grp")
    for g, faces in enumerate(face_groups):
        for f in faces:
            try:
                nf = bm.faces.new([bv[i] for i in f])
                nf[gl] = g
            except ValueError:
                pass
    if dedupe:
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=dedupe)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    out = []
    for g, name in enumerate(names):
        b2 = bm.copy()
        gl2 = b2.faces.layers.int.get("grp")
        bmesh.ops.delete(b2, geom=[f for f in b2.faces if f[gl2] != g], context="FACES")
        bmesh.ops.delete(b2, geom=[v for v in b2.verts if not v.link_faces], context="VERTS")
        me = bpy.data.meshes.new(name)
        b2.to_mesh(me)
        b2.free()
        obj = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(obj)
        out.append(obj)
    bm.free()
    return out


def loft(name: str, rings, cap_start: str | None = "ngon", cap_end: str | None = "ngon", closed_rings=True,
         recalc=True):
    """Skin a list of rings (each a list of (x, y, z) with equal counts).
    cap: "fan" (to the ring centre), "ngon", or None (open)."""
    N = len(rings[0])
    verts = [tuple(v) for r in rings for v in r]
    faces = []
    cols = N if closed_rings else N - 1
    for k in range(len(rings) - 1):
        for i in range(cols):
            j = (i + 1) % N
            faces.append((k * N + i, k * N + j, (k + 1) * N + j, (k + 1) * N + i))

    def cap(ring_idx, mode, reverse):
        base = ring_idx * N
        if mode == "ngon":
            idx = [base + i for i in range(N)]
            faces.append(tuple(reversed(idx)) if reverse else tuple(idx))
        elif mode == "fan":
            r = rings[ring_idx]
            c = tuple(sum(p[a] for p in r) / N for a in range(3))
            verts.append(c)
            ci = len(verts) - 1
            for i in range(N):
                j = (i + 1) % N
                faces.append((ci, base + j, base + i) if reverse else (ci, base + i, base + j))

    if cap_start:
        cap(0, cap_start, True)
    if cap_end:
        cap(len(rings) - 1, cap_end, False)
    return mesh_obj(name, verts, faces, recalc=recalc)


def rod(p0, p1, r, verts=8, bevel=0.0, segments=1, name="Rod", r_top=None):
    """Straight cylinder (or taper with r_top) from point p0 to p1."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = ns.cyl(r, d.length, loc=(p0 + p1) / 2, verts=verts, bevel=bevel, segments=segments,
               radius_top=r_top, name=name)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def rrect(w, h, r, n=4, cx=0.0, cy=0.0):
    """Closed 2D rounded-rectangle outline (w x h, corner radius r, n segments/corner), CCW."""
    r = min(r, w / 2 - 1e-4, h / 2 - 1e-4)
    pts = []
    corners = ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
               (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270))
    for x, y, a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + x + r * math.cos(a), cy + y + r * math.sin(a)))
    return pts


def circle2(r, N=12, cx=0.0, cy=0.0, phase=0.0, wob=None, sx=1.0, sy=1.0):
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N + phase
        rr = r * (1 + (wob(t) if wob else 0.0))
        pts.append((cx + rr * math.cos(t) * sx, cy + rr * math.sin(t) * sy))
    return pts


def rot2(pts, deg, cx=0.0, cy=0.0):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def ccw(pts):
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts)))
    return list(pts) if area > 0 else list(reversed(pts))


def extrude(points2d, thickness, plane="XY", offset=0.0, loc=(0, 0, 0), bevel=0.0, segments=2, name="Ext"):
    """Extrude a closed 2D outline.
    plane "XY": outline in (x, y), extruded along +Z from z = offset.
    plane "XZ": outline in (x, z), extruded along +Y from y = offset (front-facing plates).
    plane "YZ": outline in (y, z), extruded along +X from x = offset (side profiles)."""
    bm = bmesh.new()
    if plane == "XY":
        vs = [bm.verts.new((a, b, offset)) for a, b in points2d]
        dvec = (0, 0, thickness)
    elif plane == "XZ":
        vs = [bm.verts.new((a, offset, b)) for a, b in points2d]
        dvec = (0, thickness, 0)
    else:
        vs = [bm.verts.new((offset, a, b)) for a, b in points2d]
        dvec = (thickness, 0, 0)
    face = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=dvec)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name, loc, (0, 0, 0), bevel, segments)


def part(objs, name, color, mat="SmoothPlastic", **kw):
    """Join (applying modifiers) and tag in one go. objs may be one object or a list."""
    # nslib.render_preview deletes scene objects whose names start with these prefixes
    assert not name.startswith(("PreviewCam", "Key", "Fill", "Rim", "RefCube", "Floor")), name
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    objs = [o for o in objs if o is not None]
    if len(objs) == 1:
        o = objs[0]
        ns.apply_all(o)
    else:
        o = ns.join_applied(list(objs), name)
    return ns.tag(o, name, color, mat, **kw)


def strap(name, path, normals, width, thick, per_seg=4, chamfer=0.35, closed=False, cap=True, soft=False):
    """Flat fabric strap along a 3D control path. `normals` = outward direction per control
    point (the strap's inner face lies ON the path, the outer face thick further out).
    Cross-section: a rectangle (soft=True: chamfered hexagon, 50% more triangles)."""
    pts = catmull(path, per_seg, closed=closed)
    nrm = resample_vecs(normals, len(pts), closed=closed)
    e = min(width * 0.3, thick * chamfer * 2)
    if soft:
        prof = [(-width / 2, 0.5), (-width / 2 + e, 0.0), (width / 2 - e, 0.0), (width / 2, 0.5),
                (width / 2 - e, 1.0), (-width / 2 + e, 1.0)]
    else:
        prof = [(-width / 2, 0.0), (width / 2, 0.0), (width / 2, 1.0), (-width / 2, 1.0)]
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        if closed:
            a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        else:
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        t = (b - a).normalized()
        nn = Vector(nrm[i])
        nn = (nn - t * nn.dot(t)).normalized()
        side = t.cross(nn).normalized()
        rings.append([p + side * sx + nn * (sy * thick) for sx, sy in prof])
    if closed:
        rings.append(rings[0])
        return loft(name, rings, None, None)
    return loft(name, rings, "ngon" if cap else None, "ngon" if cap else None)


def cord(name, path, r, sides=4, per_seg=2, closed=False, cap=True, radii=None, up=(0, 0, 1)):
    """Round cord/tube through a 3D control path (Catmull-Rom), `sides`-gon cross-section.
    radii: optional per-control-point radius list (resampled)."""
    pts = catmull(path, per_seg, closed=closed)
    n = len(pts)
    if radii is not None:
        rr = [v.x for v in resample_vecs([(q, 0, 0) for q in radii], n, closed=closed)]
    else:
        rr = [r] * n
    rings = []
    side = None
    for i, p in enumerate(pts):
        if closed:
            a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        else:
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        t = (b - a).normalized()
        if side is None:                       # first frame: perpendicular to `up`
            side = t.cross(Vector(up))
            if side.length < 1e-4:
                side = t.cross(Vector((1, 0, 0)))
        side = side - t * side.dot(t)          # parallel transport (no twisting)
        side.normalize()
        nrm = side.cross(t).normalized()
        ring = []
        for k in range(sides):
            ang = 2 * math.pi * k / sides + math.pi / sides
            ring.append(p + (side * math.cos(ang) + nrm * math.sin(ang)) * rr[i])
        rings.append(ring)
    if closed:
        rings.append(rings[0])
        return loft(name, rings, None, None)
    return loft(name, rings, "ngon" if cap else None, "ngon" if cap else None)


def lathe_pts(profile, verts=16, phase=0.0, rfn=None):
    """Rings for a lathe: profile [(r, z)], optional rfn(theta, r, z) -> r'."""
    rings = []
    for r, z in profile:
        ring = []
        for i in range(verts):
            a = 2 * math.pi * i / verts + phase
            rr = rfn(a, r, z) if rfn else r
            ring.append((rr * math.cos(a), rr * math.sin(a), z))
        rings.append(ring)
    return rings


def decal(name, outline_xz, surf_y, z_front_off=0.0, thick=0.014, embed=0.01, walls=True):
    """Flat cut-out (patch, check, splat) laid on a front-facing surface.

    outline_xz  closed [(x, z)] outline (any winding, star-shaped / convex is safest).
    surf_y      surf_y(x, z) -> y of the surface it sits on (front = more negative y).
    The top face sits `thick` in front of the surface, the bottom `embed` behind it."""
    pts = ccw(list(outline_xz))
    N = len(pts)
    verts = [(x, surf_y(x, z) - thick, z) for x, z in pts] + [(x, surf_y(x, z) + embed, z) for x, z in pts]
    # CCW in (x, z) seen from the front => the n-gon normal points -Y (front)
    faces = [tuple(range(N))]
    if walls:
        for i in range(N):
            j = (i + 1) % N
            faces.append((j, i, N + i, N + j))
    return mesh_obj(name, verts, faces, recalc=False, dedupe=0)


def clip_band_x(x0, x1, z0, z1, hw_fn, inset=0.0, steps=4, x_min=None):
    """Outline (x, z) of the box [x0,x1] x [z0,z1] clipped to |x| <= hw(z) - inset.
    Returns None if nothing is left. Samples the clipped sides at `steps`+1 heights."""
    left, right = [], []
    for k in range(steps + 1):
        z = z0 + (z1 - z0) * k / steps
        hw = hw_fn(z) - inset
        lx, rx = max(x0, -hw), min(x1, hw)
        if rx - lx > 1e-3:
            left.append((lx, z))
            right.append((rx, z))
    if len(left) < 2:
        return None
    return right + list(reversed(left))


def jitter_verts(obj, amount, seed=1, axes=(1, 1, 1), fn=None):
    rnd = random.Random(seed)
    ns.apply_all(obj)
    for v in obj.data.vertices:
        k = fn(v.co) if fn else 1.0
        v.co.x += rnd.uniform(-amount, amount) * axes[0] * k
        v.co.y += rnd.uniform(-amount, amount) * axes[1] * k
        v.co.z += rnd.uniform(-amount, amount) * axes[2] * k
    obj.data.update()
    return obj


def deform(obj, fn):
    ns.apply_all(obj)
    for v in obj.data.vertices:
        v.co = fn(v.co.copy())
    obj.data.update()
    return obj


# --------------------------------------------------------------------------------------
# Aprons: shared bib apron (panel + binding, neck straps, waist ties, bow, pocket)
# --------------------------------------------------------------------------------------

APRON_TOP = 0.95
APRON_HEM = -2.0
APRON_THICK = 0.06
APRON_GAP = 0.035
BIND = 0.055           # binding width along the edges
BIB_HW = 0.63
WAIST_Z = -0.56        # where the ties leave the apron sides
TIE_W = 0.1


def apron_hw(z: float) -> float:
    """Half width of the apron outline at height z (bib -> armhole curve -> flared skirt)."""
    if z >= 0.30:
        return 0.60 + 0.03 * (APRON_TOP - z) / (APRON_TOP - 0.30)
    if z >= -0.50:
        t = (0.30 - z) / 0.80
        return BIB_HW + 0.335 * (1 - math.sqrt(max(0.0, 1 - t * t)))
    if z >= -0.64:
        return 0.965
    t = (-0.64 - z) / (-0.64 - APRON_HEM)
    return 0.965 + 0.035 * t


def apron_back_y(x: float, z: float) -> float:
    """y of the apron's BACK surface (toward the body): a constant gap over the torso, the
    skirt flaring forward below the hips, and a slight forward belly in the middle."""
    y = -APRON_GAP
    if z < TORSO_BOT:
        t = (TORSO_BOT - z) / (TORSO_BOT - APRON_HEM)
        y -= 0.13 * t ** 1.6
    hw = max(apron_hw(z), 0.3)
    y -= 0.014 * max(0.0, 1 - (x / hw) ** 2)
    return y


def apron_front_y(x: float, z: float) -> float:
    return apron_back_y(x, z) - APRON_THICK


APRON_ROWS = [APRON_TOP, APRON_TOP - BIND, 0.30, 0.16, -0.02, -0.21, -0.38, -0.50, -0.64,
              -1.05, -1.50, APRON_HEM + BIND, APRON_HEM]


def apron_panel(hem_fn=None, bind_bottom=True, bind_top=True, name="Panel", n_inner=3, hw_fn=None,
                back_fn=None, rows=None, top_fn=None, bind=BIND, thick=APRON_THICK):
    """The apron cloth: a lofted slab with rounded edges. Returns (body_obj, binding_obj).

    The outermost front/back column on both sides, the side rounding, and the top/bottom rows
    form the BINDING part (contrasting edge tape); the rest is the body cloth.
    hem_fn(x) -> extra z offset of the hem (torn hems); applied to the bottom two rows.
    top_fn(x) -> extra z offset of the top edge (necklines); applied to the top two rows.
    hw_fn / back_fn / rows default to the bib apron's cut (apron_hw, apron_back_y, APRON_ROWS)."""
    rows = list(rows or APRON_ROWS)
    hw_fn = hw_fn or apron_hw
    back_fn = back_fn or apron_back_y

    def front_fn(x, z):
        return back_fn(x, z) - thick

    rings = []
    lip = thick * 0.45
    for k, z0 in enumerate(rows):
        hw = hw_fn(z0)
        xs = [-hw, -(hw - bind)] + [lerp(-(hw - bind), hw - bind, (i + 1) / (n_inner + 1)) for i in range(n_inner)] + \
             [hw - bind, hw]

        def zz(x, z0=z0, k=k):
            if hem_fn and k >= len(rows) - 2:
                return z0 + hem_fn(x)
            if top_fn and k <= 1:
                return z0 + top_fn(x)
            return z0

        front = [(x, front_fn(x, zz(x)), zz(x)) for x in xs]
        back = [(x, back_fn(x, zz(x)), zz(x)) for x in reversed(xs)]
        ymr = (front_fn(hw, zz(hw)) + back_fn(hw, zz(hw))) / 2
        yml = (front_fn(-hw, zz(-hw)) + back_fn(-hw, zz(-hw))) / 2
        ring = front + [(hw + lip, ymr, zz(hw))] + back + [(-hw - lip, yml, zz(-hw))]
        rings.append(ring)

    # rounded top / bottom lips: rings pulled to mid-thickness and pushed beyond the edge
    def lip_ring(src, dz):
        out = []
        n = len(src)
        half = (n - 2) // 2
        for i, (x, y, z) in enumerate(src):
            if i < half:
                yb = src[n - 2 - i][1]
                ym = (y + yb) / 2
                out.append((x * 0.985, ym - thick * 0.22, z + dz))
            elif i == half or i == n - 1:
                out.append((x * 0.985, y, z + dz))
            else:
                yf = src[n - 2 - i][1]
                ym = (y + yf) / 2
                out.append((x * 0.985, ym + thick * 0.22, z + dz))
        return out

    rings = [lip_ring(rings[0], lip)] + rings + [lip_ring(rings[-1], -lip)]
    N = len(rings[0])
    nf = n_inner + 4                       # front points per ring
    verts = [v for r in rings for v in r]
    body_f, bind_f = [], []
    nr = len(rings)
    for k in range(nr - 1):
        top_band = k <= 1
        bot_band = k >= nr - 3
        for i in range(N):
            j = (i + 1) % N
            q = (k * N + i, k * N + j, (k + 1) * N + j, (k + 1) * N + i)
            # front columns: i in [0, nf-2]; outer ones are 0 and nf-2
            is_front = i <= nf - 2
            is_back = nf + 1 <= i <= 2 * nf - 1
            outer_col = i in (0, nf - 2, nf - 1, nf, nf + 1, 2 * nf - 1, 2 * nf, N - 1)
            if (top_band and bind_top) or (bot_band and bind_bottom) or outer_col:
                bind_f.append(q)
            elif is_front or is_back:
                body_f.append(q)
            else:
                bind_f.append(q)
    # caps
    cap_top = tuple(reversed(range(N)))
    cap_bot = tuple((nr - 1) * N + i for i in range(N))
    (bind_f if bind_top else body_f).append(cap_top)
    (bind_f if bind_bottom else body_f).append(cap_bot)
    body, binding = split_mesh([name, name + "Binding"], verts, [body_f, bind_f])
    return body, binding


def apron_straps(name="Straps"):
    """Neck/shoulder straps: from the bib top corners over the shoulders, crossing on the back
    down to the waist ties. Returns a list of objects (both straps)."""
    out = []
    for s in (-1, 1):
        x0 = s * 0.50
        xs = s * 0.69                      # over the shoulder, clear of the head (r 0.58)
        yb = BODY_DEPTH + 0.03             # back surface + gap
        lift = 0.012 if s > 0 else 0.0     # one strap sits on top where they cross
        path = [(x0, apron_front_y(x0, APRON_TOP - 0.10) + 0.012, APRON_TOP - 0.10),
                (s * 0.60, -0.07, 1.01),
                (xs, 0.06, TORSO_TOP + 0.03),
                (xs, 0.55, TORSO_TOP + 0.03),
                (s * 0.67, BODY_DEPTH - 0.02, TORSO_TOP + 0.01),
                (s * 0.60, yb, TORSO_TOP - 0.22),
                (0.0, yb + lift, 0.18),
                (-s * 0.8, yb, WAIST_Z + 0.02)]
        nrm = [(0, -1, 0), (0, -1, 0.5), (0, -0.2, 1), (0, 0, 1), (0, 0.7, 1),
               (0, 1, 0.1), (0, 1, 0), (0, 1, 0)]
        out.append(strap(f"{name}{'L' if s < 0 else 'R'}", path, nrm, 0.13, 0.028, per_seg=2))
    return out


def apron_ties(name="Ties", with_bow=True):
    """Waist ties around the torso sides to a bow at the back. Returns list of objects."""
    out = []
    z = WAIST_Z
    yb = BODY_DEPTH + 0.012
    xs = TORSO_HW + 0.004                  # in the 0.03 gap between torso side and arm
    for s in (-1, 1):
        hw = apron_hw(z)
        path = [(s * (hw - 0.06), apron_front_y(s * (hw - 0.06), z) + 0.015, z),
                (s * (hw + 0.02), -0.06, z),
                (s * xs, 0.08, z),
                (s * xs, 0.5, z),
                (s * xs, BODY_DEPTH - 0.08, z),
                (s * (TORSO_HW - 0.06), yb, z),
                (s * 0.12, yb + 0.01, z + 0.005)]
        nrm = [(0, -1, 0), (s * 0.7, -0.7, 0), (s, 0, 0), (s, 0, 0), (s, 0, 0), (s * 0.7, 0.7, 0), (0, 1, 0)]
        out.append(strap(f"{name}{'L' if s < 0 else 'R'}", path, nrm, TIE_W, 0.021, per_seg=1))
    if with_bow:
        out += apron_bow(z, yb + 0.03)
    return out


def apron_bow(z, y):
    objs = []
    # knot
    objs.append(ns.box((0.13, 0.07, 0.12), loc=(0, y + 0.015, z), bevel=0.03, segments=1))
    for s in (-1, 1):
        # flattened loop lying against the back, tilted up and out
        lp = ns.torus(0.105, 0.036, loc=(s * 0.155, y + 0.004, z + 0.03), rot=(90, s * 16, 0),
                      major_segs=9, minor_segs=4)
        lp.scale = (1.3, 0.85, 0.5)        # wide ribbon loop, flattened against the back
        ns.apply_all(lp)
        objs.append(lp)
        # tail hanging down and out
        tail = strap("Tail", [(s * 0.03, y + 0.01, z - 0.02), (s * 0.09, y + 0.012, z - 0.22),
                              (s * 0.17, y + 0.012, z - 0.40)],
                     [(0, 1, 0)] * 3, 0.085, 0.022, per_seg=2)
        objs.append(tail)
    return objs


def pocket_outline(cx, cz, w, h, r=0.05):
    pts = rrect(w, h, r, n=2)
    return [(cx + x, cz + y) for x, y in pts]


def apron_pocket(cx=0.24, cz=0.50, w=0.44, h=0.36, with_pencil=True):
    """Chest pocket patch (trim) with a pencil tucked in. Returns (pocket_objs, pencil_parts)."""
    pocket = decal("Pocket", pocket_outline(cx, cz, w, h, 0.06), apron_front_y, thick=0.03, embed=0.008)
    ns.bevel(pocket, width=0.01, segments=1, angle=50)
    # folded top hem of the pocket (a slightly thicker lip)
    lip = decal("PocketLip", pocket_outline(cx, cz + h / 2 - 0.045, w + 0.012, 0.075, 0.03),
                apron_front_y, thick=0.042, embed=0.0)
    ns.bevel(lip, width=0.01, segments=1, angle=50)
    pencil = []
    if with_pencil:
        # pencil tucked behind the pocket, leaning slightly; poking out of the top
        px = cx - w * 0.24
        base = Vector((px, apron_front_y(px, cz) - 0.017, cz + h / 2 - 0.07))
        top = Vector((px - 0.035, apron_front_y(px, cz) - 0.02, cz + h / 2 + 0.17))
        d = (top - base).normalized()
        body = rod(base, top, 0.027, verts=6, name="PencilBody")
        ns.apply_all(body)
        wood = rod(top, top + d * 0.06, 0.026, verts=6, r_top=0.01, name="PencilWood")
        ns.apply_all(wood)
        lead = rod(top + d * 0.06, top + d * 0.08, 0.01, verts=6, r_top=0.002, name="PencilLead")
        ns.apply_all(lead)
        pencil = [("Pencil", [body], PENCIL), ("PencilTip", [wood], PENCIL_WOOD), ("PencilLead", [lead], GRAPHITE)]
    return [pocket, lip], pencil


BIB_POCKET = (0.24, 0.50, 0.44, 0.36)       # cx, cz, w, h
HIP_POCKET = (0.0, -1.02, 1.26, 0.42)


def in_rect(x, z, rect, pad=0.0):
    cx, cz, w, h = rect
    return abs(x - cx) <= w / 2 + pad and abs(z - cz) <= h / 2 + pad


def flat_patches(name, polys, surf=None, lift=0.008, walls=False, wall_embed=0.008):
    """Many flat cut-outs (checks, stripes, splats) in ONE mesh, each polygon laid `lift` in
    front of the surface (vertex by vertex, so it follows the cloth). walls=True adds side
    walls down into the cloth (raised blobs). Polygons: closed [(x, z)] lists."""
    surf = surf or apron_front_y
    verts, faces = [], []
    for poly in polys:
        pts = ccw(list(poly))
        n = len(pts)
        b = len(verts)
        verts += [(x, surf(x, z) - lift, z) for x, z in pts]
        faces.append(tuple(range(b, b + n)))
        if walls:
            verts += [(x, surf(x, z) + wall_embed, z) for x, z in pts]
            for i in range(n):
                j = (i + 1) % n
                faces.append((b + j, b + i, b + n + i, b + n + j))
    return mesh_obj(name, verts, faces, recalc=False, dedupe=0)


def strip_quads(name, columns, surf=None, lift=0.008):
    """Vertical strips laid on the cloth as quad strips (so long stripes follow the curved
    skirt). columns: list of [(lx, rx, z), ...] samples ordered top -> bottom."""
    surf = surf or apron_front_y
    verts, faces = [], []
    for col in columns:
        b = len(verts)
        for lx, rx, z in col:
            verts += [(lx, surf(lx, z) - lift, z), (rx, surf(rx, z) - lift, z)]
        for k in range(len(col) - 1):
            L0, R0, L1, R1 = b + 2 * k, b + 2 * k + 1, b + 2 * k + 2, b + 2 * k + 3
            faces.append((L1, R1, R0, L0))
    return mesh_obj(name, verts, faces, recalc=False, dedupe=0)


def hip_pocket(cz=-1.02, w=1.26, h=0.42, gap=0.035):
    """Wide two-compartment pocket across the skirt (two patches + one folded top hem)."""
    objs = []
    pw = (w - gap) / 2
    for s in (-1, 1):
        cx = s * (pw + gap) / 2
        o = decal("HipPocket", pocket_outline(cx, cz, pw, h, 0.06), apron_front_y, thick=0.03, embed=0.008)
        ns.bevel(o, width=0.01, segments=1, angle=50)
        objs.append(o)
    lip = decal("HipLip", pocket_outline(0.0, cz + h / 2 - 0.04, w + 0.014, 0.08, 0.035), apron_front_y,
                thick=0.043, embed=0.0)
    ns.bevel(lip, width=0.01, segments=1, angle=50)
    objs.append(lip)
    return objs


def rivet(p, normal=(0, -1, 0), r=0.04, h=0.022, name="Rivet"):
    """Small domed rivet/stud whose base sits at p, dome toward `normal`."""
    o = ns.lathe([(0.0, 0.0), (r, 0.0), (r * 0.8, h * 0.75), (0.0, h)], verts=8, name=name)
    o.rotation_euler = Vector(normal).to_track_quat("Z", "Y").to_euler()
    o.location = Vector(p)
    ns.apply_all(o)
    return o


def apron_base(mesh="Apron", hem_fn=None, bind_bottom=True, pocket=True, pencil=True, hips=True, rivets=True,
               mat="SmoothPlastic", extra_trim=(), n_inner=3):
    """Build and tag the full bib apron in the mesh's authored (first catalogue) colours.
    extra_trim: more objects joined into the Trim part (pattern decals...)."""
    dc = default_colours(mesh)
    body_col, trim_col = dc["body"], dc.get("trim", dc["body"])
    panel, binding = apron_panel(hem_fn=hem_fn, bind_bottom=bind_bottom, n_inner=n_inner)
    body = part(panel, "Apron", body_col, mat, recolor="cos_body", smooth_angle=40)
    trims = [binding] + apron_straps() + apron_ties() + list(extra_trim)
    pencil_parts = []
    if pocket:
        pk, pencil_parts = apron_pocket(with_pencil=pencil)
        trims += pk
    if hips:
        trims += hip_pocket()
    trim = part(trims, "Trim", trim_col, mat, recolor="cos_trim", smooth_angle=50)
    for pname, objs, col in pencil_parts:
        part(objs, pname, col, "SmoothPlastic", smooth_angle=50)
    if rivets:
        rv = []
        for s in (-1, 1):
            x = s * 0.5
            z = APRON_TOP - 0.10
            rv.append(rivet((x, apron_front_y(x, z) - 0.016, z)))
        part(rv, "Rivets", BRASS, "Metal", smooth_angle=60)
    return {"body": body, "trim": trim}


# --------------------------------------------------------------------------------------
# Recolour / icons / drafts
# --------------------------------------------------------------------------------------

def recolour(entry: dict) -> None:
    """Apply one catalogue entry's colours/materials to every part by role."""
    for o in list(ns._tagged_objects()):
        role = o.get("ns_role")
        if role == "cos_body":
            col, mat = entry.get("body"), entry.get("body_mat")
        elif role == "cos_trim":
            col, mat = entry.get("trim"), entry.get("trim_mat")
        elif role == "cos_beam":
            col, mat = entry.get("beam"), entry.get("beam_mat")
        else:
            continue
        if col is None and mat is None:
            continue
        sm = o["ns_smooth_angle"]
        ns.tag(o, o["ns_part"], col or o["ns_color"], mat or o["ns_material"],
               transparency=o["ns_transparency"], cast_shadow=o["ns_cast_shadow"],
               can_collide=o["ns_can_collide"], smooth_angle=None if sm < 0 else sm, recolor=role)


def _shiny_metals():
    """render_icon flattens every 'Principled BSDF' to roughness >= 0.62 (good for plastic
    colours, but it turns Metal/Foil into dull grey-brown). For the icon render only, give
    Metal/Foil parts a copy of their material whose BSDF node has another name, so the shared
    rig leaves it glossy. Export data is untouched (icons are rendered after export)."""
    for o in ns._tagged_objects():
        mat = o.get("ns_material")
        if mat not in ("Metal", "Foil"):
            continue
        m = o.data.materials[0].copy()
        m.name = f"Icon_{o.name}_{mat}"
        b = m.node_tree.nodes.get("Principled BSDF")
        b.name = "CosmeticBSDF"
        b.inputs["Roughness"].default_value = 0.32 if mat == "Foil" else 0.34
        b.inputs["Metallic"].default_value = 0.78 if mat == "Foil" else 0.9
        b.inputs["Specular IOR Level"].default_value = 0.5
        o.data.materials[0] = m


def pose_root(objs, mat: Matrix):
    """Transform objects about the origin (icon posing)."""
    for o in objs:
        o.matrix_world = mat @ o.matrix_world


def camera_basis(yaw, pitch):
    yaw, pitch = math.radians(yaw), math.radians(pitch)
    to_cam = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    fwd = -to_cam
    right = fwd.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(fwd).normalized()
    return to_cam, right, up


def held_icon_matrix(yaw=-35.0, pitch=28.0, screen_deg=38.0, face=0.55, toward=0.25):
    """Rotation that lays a held item (working end -Y, top +Z) diagonally across the icon:
    the working end points to the upper right at `screen_deg`, tipped `toward` the camera,
    and the item's top faces the camera by `face` (0 = edge-on, 1 = flat-on)."""
    to_cam, right, up = camera_basis(yaw, pitch)
    a = math.radians(screen_deg)
    d = (right * math.cos(a) + up * math.sin(a)).normalized()
    d = (d + to_cam * toward).normalized()              # working end direction
    facing = to_cam - d * to_cam.dot(d)
    facing.normalize()
    u = facing * face + (up - d * up.dot(d)).normalized() * (1 - face)
    u = (u - d * u.dot(d)).normalized()                  # item +Z
    x = (-d).cross(u).normalized()                       # item +X  (y = -d)
    R = Matrix((x, -d, u)).transposed()                  # columns = images of X, Y, Z
    return R.to_4x4()


def facing_matrix(n, up=(0, 0, 1)):
    """Rotation that turns a front-facing asset (front = -Y, up = +Z) so its front faces n."""
    n = Vector(n).normalized()
    u = Vector(up)
    u = (u - n * u.dot(n)).normalized()
    y = -n
    x = y.cross(u).normalized()
    return Matrix((x, y, u)).transposed().to_4x4()


def apron_icon_matrix(yaw, pitch, w_cam=0.72):
    """Turn the apron to face between the camera and the icon rig's key light (the key comes
    from the upper left, so a flat front-on apron would be lit at a grazing angle)."""
    to_cam, _, _ = camera_basis(yaw, pitch)
    k = math.radians(yaw)
    key = Vector((math.sin(k - 0.7), -math.cos(k - 0.7), 1.0)).normalized()
    return facing_matrix(to_cam * w_cam + key * (1 - w_cam))


def holdout_material():
    m = bpy.data.materials.get("IconHoldout")
    if m:
        return m
    m = bpy.data.materials.new("IconHoldout")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    ho = nt.nodes.new("ShaderNodeHoldout")
    nt.links.new(ho.outputs[0], out.inputs["Surface"])
    return m


def invisible_body(slot):
    """Untagged holdout blocks where the wearer's body would be: icons then look like the
    cosmetic is worn by an invisible avatar (back straps/inside faces hidden, alpha cut out)."""
    objs = []
    if slot == "Apron":
        objs.append(ns.box((TORSO_HW * 2 - 0.01, BODY_DEPTH - 0.01, TORSO_TOP - TORSO_BOT - 0.01),
                           loc=(0, BODY_DEPTH / 2, (TORSO_TOP + TORSO_BOT) / 2), bevel=0.0, name="IconBody"))
        objs.append(ns.box((LOWER_HW * 2 - 0.01, BODY_DEPTH - 0.01, 0.4), loc=(0, BODY_DEPTH / 2, -0.84),
                           bevel=0.0, name="IconHips"))
    elif slot == "Hat":
        objs.append(ns.cyl(HEAD_R - 0.01, HEAD_H - 0.01, loc=(0, 0, -HEAD_H / 2), verts=32, bevel=0.14,
                           segments=3, name="IconHead"))
    for o in objs:
        ns.apply_all(o)
        o.data.materials.append(holdout_material())
    return objs


def fit_margin(yaw, pitch, fov=24.0, pad=1.07):
    """The `margin` for ns.render_icon / ns._camera_fit that makes the tagged objects' projected
    silhouette fill the square frame with `pad` breathing room (the rig's own fit uses the
    bounding-box diagonal, which leaves long or rotated items small)."""
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    ctr = (lo + hi) / 2
    radius = max((hi - lo).length / 2, 0.05)
    to_cam, right, up = camera_basis(yaw, pitch)
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        me = o.evaluated_get(dg).to_mesh()
        pts += [o.matrix_world @ v.co - ctr for v in me.vertices]
        o.evaluated_get(dg).to_mesh_clear()
    half = math.radians(fov) / 2
    margin = 1.0
    for _ in range(3):
        dist = radius * margin / math.sin(half)
        e = 0.0
        for p in pts:
            depth = p.dot(to_cam)
            k = dist / max(dist - depth, 1e-3)
            e = max(e, abs(p.dot(right)) * k, abs(p.dot(up)) * k)
        margin = e * pad * math.cos(half) / radius      # dist = e * pad / tan(half)
    return margin


def icon_pass(entry_id: str, entry: dict, build, slot: str, icon_kw: dict, draft=False):
    ns.reset()
    build()
    recolour(entry)
    if entry.get("extras") == "static":
        static_bars()
    objs = ns._tagged_objects()
    kw = dict(icon_kw)
    pose = kw.pop("pose", None)
    hide = invisible_body(slot) if kw.pop("holdout", slot in ("Apron", "Hat")) else []
    if pose is not None:
        pose_root(objs + hide, pose)
        bpy.context.view_layer.update()
    _shiny_metals()
    if kw.get("margin") is None:
        kw["margin"] = fit_margin(kw.get("yaw", -35.0), kw.get("pitch", 28.0), kw.get("fov", 24.0),
                                  kw.pop("pad", 1.07))
    kw.pop("pad", None)
    name = f"Cosmetic_{entry_id}"
    if draft:
        return draft_icon(name, **kw)
    return ns.render_icon(name, ICON_GROUP, **kw)


def static_bars():
    """Apron_static icon only: a few horizontal glitch bars across the apron."""
    rnd = random.Random(7)
    cols = ["#FF2E3A", "#F4F1EA", "#2EE6FF", "#FF2E3A", "#F4F1EA", "#FF2E3A"]
    for i, (z, h, dx, w) in enumerate([(0.62, 0.05, 0.10, 0.9), (0.18, 0.09, -0.16, 1.3), (-0.35, 0.035, 0.22, 1.7),
                                       (-0.95, 0.07, -0.10, 1.6), (-1.32, 0.04, 0.28, 1.2), (-1.68, 0.06, -0.2, 1.5)]):
        hw = min(apron_hw(z), w / 2)
        x0, x1 = max(-apron_hw(z), -hw + dx), min(apron_hw(z) + 0.15, hw + dx)
        outline = [(x0, z - h / 2), (x1, z - h / 2), (x1, z + h / 2), (x0, z + h / 2)]
        o = decal(f"Glitch{i}", outline, lambda x, z: apron_front_y(min(abs(x), 0.95), z) - 0.03, thick=0.012)
        ns.tag(o, f"Glitch{i}", cols[i], "Neon" if cols[i] != "#F4F1EA" else "SmoothPlastic", cast_shadow=False)
    # a couple of displaced 'pixel' blocks
    for i in range(5):
        z = rnd.uniform(-1.8, 0.8)
        x = rnd.uniform(-0.6, 0.6)
        s = rnd.uniform(0.06, 0.12)
        o = decal(f"Pixel{i}", [(x, z), (x + s, z), (x + s, z + s * 0.7), (x, z + s * 0.7)],
                  lambda x, z: apron_front_y(x, z) - 0.03, thick=0.012)
        ns.tag(o, f"Pixel{i}", "#2EE6FF" if i % 2 else "#FF2E3A", "Neon", cast_shadow=False)


def draft_icon(name: str, yaw=-35.0, pitch=28.0, fov=24.0, margin=1.02, res=256, samples=10, **_):
    """Low-sample stand-in for ns.render_icon (same camera and lights) into the drafts dir."""
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    ns._setup_render(res, samples, transparent=True)
    bg = bpy.context.scene.world.node_tree.nodes.get("Background")
    bg.inputs[1].default_value = 0.45
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
        if b:
            b.inputs["Roughness"].default_value = max(0.62, b.inputs["Roughness"].default_value)
            b.inputs["Specular IOR Level"].default_value = 0.25
    cam, ctr, dist = ns._camera_fit(lo, hi, yaw, pitch, fov_deg=fov, margin=margin)
    k = math.radians(yaw)
    ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.7), -math.cos(k - 0.7), 1.0)) * dist, 62 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
    ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.3), -math.cos(k + 1.3), 0.2)) * dist, 18 * dist ** 2 / 9, size=dist * 0.9, target=ctr)
    ns._light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.9)) * dist, 50 * dist ** 2 / 9, size=dist * 0.4, target=ctr)
    os.makedirs(DRAFT_DIR, exist_ok=True)
    out = os.path.join(DRAFT_DIR, f"{name}_icon.png")
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    ns._clear_rig()
    print(out)
    return out


def draft(build, name: str, res: int = 320, samples: int = 10):
    ns.reset()
    build()
    print(f"[{name}] triangles: {ns.tri_count()}")
    print_parts(name)
    out = ns.render_preview(name, out_dir=DRAFT_DIR, res=res, samples=samples)
    print(out)
    return out


def print_parts(asset):
    dg = bpy.context.evaluated_depsgraph_get()
    for o in sorted(ns._tagged_objects(), key=lambda o: o.name):
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        print(f"  [{asset}] {o.name:16s} {len(me.loop_triangles):5d} tris  role={o.get('ns_role')}  {o['ns_color']} {o['ns_material']}")
        o.evaluated_get(dg).to_mesh_clear()


DEFAULT_ICON_KW = {
    "Apron": dict(yaw=-22.0, pitch=10.0),
    "Hat": dict(yaw=-35.0, pitch=22.0),
    "Flashlight": dict(yaw=-35.0, pitch=28.0, held=dict(toward=0.75, face=0.6)),
    "Spatula": dict(yaw=-35.0, pitch=28.0, held=dict(toward=0.15, face=0.7)),
}


def run(build, asset: str, slot: str, sockets: dict | None = None, icon_kw: dict | None = None, extra_meta=None):
    """Standard F_cosmetics entry: preview (+ export with NS_EXPORT=1, + icons with NS_ICON=1)."""
    mesh = asset.replace("Cosmetic_", "", 1)
    meta = slot_meta(slot, **(extra_meta or {}))
    kw = {"meta": meta, "pivot": (0.0, 0.0, 0.0)}
    if sockets:
        kw["sockets"] = sockets
    ikw = dict(DEFAULT_ICON_KW[slot])
    ikw.update(icon_kw or {})
    held = ikw.pop("held", {})               # options for the diagonal held-item pose
    if "pose" not in ikw:
        if slot in ("Flashlight", "Spatula"):
            ikw["pose"] = held_icon_matrix(ikw["yaw"], ikw["pitch"], **held)
        elif slot == "Apron":
            ikw["pose"] = apron_icon_matrix(ikw["yaw"], ikw["pitch"])
    ids = [k for k, v in CATALOGUE.items() if v["mesh"] == mesh]
    only = os.environ.get("NS_ICON_IDS")
    if only:
        ids = [i for i in ids if i in only.split(",")]
    if os.environ.get("NS_DRAFT") == "1":
        draft(build, asset)
        return
    if os.environ.get("NS_ICON_DRAFT") == "1":
        for i in ids:
            icon_pass(i, CATALOGUE[i], build, slot, ikw, draft=True)
        return
    if os.environ.get("NS_ONLY_ICON") != "1":
        ns.run_main(build, asset, BATCH, GROUP, **kw)
        if os.environ.get("NS_PARTS") == "1":
            print_parts(asset)
    if os.environ.get("NS_ICON") == "1":
        for i in ids:
            print(f"[{asset}] icon:", icon_pass(i, CATALOGUE[i], build, slot, ikw))
