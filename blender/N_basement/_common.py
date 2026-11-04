"""_common — shared helpers for the N_basement batch (the diner's storage basement).

Import from an asset script in this folder with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Builds on blender/lib/nslib.py and re-uses the L_decor helpers (part, loft, carton,
lathe_open, quad_xz, strip_xz, poly, face_dir ...) which bring the B_shop shape helpers
(fillet, rrect, prism, pipe, ring_slab, band, text_mesh ...) and the C_lobby builders (rod,
text, catenary, place, disc, annulus ...), plus K_shop's lathe_ring / dir_preview and
A_kitchen's extrude / rbx, each loaded under its own module name the way L_decor loads
B_shop's.

Conventions used by every N_basement asset (group "Shop", names Basement_<Name>)
  * 1 stud = 1 Blender unit, Z up, the user-facing side looks at Blender -Y.
  * The basement is 11 studs floor to ceiling, charcoal walls, lit by flashlights and a few
    dim bulbs: props are concrete greys, rusty metal, dull green paint, dingy cream and the
    faded STACKHOUSE red-orange / mustard (palette below).
  * Floor props: pivot bottom-centre (nslib default). Ceiling-hung props (mount "hang"):
    pivot on the ceiling plane z = 0, everything hangs below. Wall props (mount "wall"):
    back face on the wall plane y = 0.
  * nslib merges role-less parts per material at export (vertex colours); only parts code
    must find (lamps, glow, screen, lid, gate, neon) carry a `recolor` role.
  * can_collide on what players should bump into (shelves, boiler, heater, bench, freezer,
    arcade, cage, column, crates); small and overhead things never collide.
  * Roblox draws single-sided: decals face out of their surface and sit 0.006-0.012 proud
    of it (never coplanar), nothing floats (every piece touches what holds it).
  * Env: NS_QUICK=1 fast low-res preview (previews/N_basement/_quick), NS_SOCKETS=1 socket
    check render (previews/N_basement/_checks), NS_PARTS=1 prints the part list,
    NS_NORENDER=1 skips the preview, NS_EXPORT=1 exports.
"""
from __future__ import annotations

import importlib.util
import math
import os
import random
import sys

sys.dont_write_bytecode = True   # don't drop .pyc caches into other batches' folders

import bpy  # noqa: F401  (must load before bmesh in the bpy module build)
import bmesh
from mathutils import Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "lib"))
import nslib as ns  # noqa: E402


def _load(modname, rel):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(_HERE, "..", rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# L_decor (with its B_shop `S` and C_lobby `L`), K_shop and A_kitchen helpers, each under its
# own module name (every batch calls its helper module `_common`). L_decor also puts PIL on
# the path for the previews.
D = _load("decor_common", os.path.join("L_decor", "_common.py"))
S, L = D.S, D.L
K = _load("kshop_common", os.path.join("K_shop", "_common.py"))
A = _load("kitchen_common", os.path.join("A_kitchen", "_common.py"))

fillet, rrect, circle_pts, ellipse_pts = S.fillet, S.rrect, S.circle_pts, S.ellipse_pts
prism, slab, pipe, round_path, ring_slab = S.prism, S.slab, S.pipe, S.round_path, S.ring_slab
text_mesh, fit_text_width, bbox_of, merge, band = S.text_mesh, S.fit_text_width, S.bbox_of, S.merge, S.band
rod, text, catenary, place, yaw_point = L.rod, L.text, L.catenary, L.place, L.yaw_point
disc, annulus, arc_solid, arc_profile_sweep = L.disc, L.annulus, L.arc_solid, L.arc_profile_sweep
part, loft, lathe_open, ring3, poly = D.part, D.loft, D.lathe_open, D.ring3, D.poly
quad_xz, strip_xz, face_dir, turn_y, jbox = D.quad_xz, D.strip_xz, D.face_dir, D.turn_y, D.jbox
lathe_ring, flip_y = K.lathe_ring, K.flip_y
extrude, rbx, rbx_dir = A.extrude, A.rbx, A.rbx_dir
FONT_BOLD, FONT_BOLD_ITALIC = S.FONT_BOLD, S.FONT_BOLD_ITALIC

BATCH = "N_basement"
GROUP = "Shop"
PREVIEWS = os.path.join(ns.REPO, "..", "previews", BATCH)
CEILING = 11.0                 # basement floor to ceiling

# ---------------------------------------------------------------------------------------
# Palette (brief for the basement; a step greyer than the shop upstairs)
# ---------------------------------------------------------------------------------------
WALL = "#3A3D42"               # basement charcoal walls (STYLE.md)
CONCRETE = "#6A6C70"
CONCRETE_DARK = "#4A4C50"
RUST = "#7A5A3A"
RUST_DARK = "#5E4430"
GREEN = "#4E5B4A"              # dull green paint
GREEN_DARK = "#3C463A"
CREAM = "#CFC6B0"              # dingy cream
CREAM_DARK = "#B3AA94"
BRAND = "#B8492A"              # faded STACKHOUSE red-orange
MUSTARD = "#C9952F"            # faded mustard
BULB = "#FFD9A0"               # warm bulb (Neon)
GLOW = "#FF7A2A"               # furnace glow (Neon)
STEEL = "#8A8E93"              # bare galvanised steel (shelving, cage wire)
IRON = "#3F4145"               # cast iron / black iron pipe
COPPER = "#A86B45"             # old copper, a step greyer
BRASS = "#A68A4E"
INK = "#232428"                # stencil / print ink, gauge needles
DARK_VOID = "#121317"
CARDBOARD = "#A68A66"          # dusty cardboard
CARDBOARD_DARK = "#8A7253"
CARDBOARD_LIGHT = "#B79E7B"
DUST = "#B4AFA3"
TAPE = "#C2AE86"
WOOD = "#7A5E44"               # old wood
WOOD_DARK = "#5A4532"
WOOD_LIGHT = "#94775A"
GLASS_DULL = "#9AA1A4"         # dead neon / dusty glass
WEB = "#D8D5CC"                # cobweb strands
RUBBER = "#1D1E22"
VALVE_RED = "#A63A2C"

FORBIDDEN = D.FORBIDDEN


# ---------------------------------------------------------------------------------------
# Small builders
# ---------------------------------------------------------------------------------------

def bar(p0, p1, w, t, normal=(0, -1, 0), name="Bar"):
    """Flat rectangular bar w wide, t thick, from p0 to p1; its broad faces look along
    `normal` (made orthogonal to the bar)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    n = Vector(normal)
    n = (n - d * n.dot(d)).normalized()
    b = d.cross(n)
    bm = bmesh.new()
    rings = []
    for p in (p0, p1):
        rings.append([bm.verts.new(p + b * (sb * w / 2) + n * (sn * t / 2))
                      for sb, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    a, c = rings
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new([a[k], a[j], c[j], c[k]])
    bm.faces.new(list(reversed(a)))
    bm.faces.new(c)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def angle_iron(corner, sx, sy, a, t, z0, z1):
    """L-section upright (angle iron) from z0 to z1. `corner` = (x, y) of the outer corner;
    the two flanges run from it toward -sx * X and -sy * Y (sx, sy = +-1 point outward)."""
    x, y = corner
    pts = [(0, 0), (-a, 0), (-a, -t), (-t, -t), (-t, -a), (0, -a)]
    pts = [(x + sx * px, y + sy * py) for px, py in pts]
    if sx * sy < 0:
        pts = list(reversed(pts))
    return prism(pts, "z", z0, z1)


def can(x, y, z, r=0.17, h=0.42, verts=8):
    """Tin can standing on (x, y, z): metal body + a closed label sleeve. Returns (metal, label)."""
    metal = ns.cyl(r * 0.94, h, loc=(x, y, z + h / 2), verts=verts, bevel=0.0)
    label = ns.cyl(r, h * 0.7, loc=(x, y, z + h / 2), verts=verts, bevel=0.0)
    return metal, label


def jar(x, y, z, r=0.2, h=0.5, verts=8):
    """Glass preserve jar standing on (x, y, z): body (contents colour) + lid + label sleeve.
    Returns (body, lid, label)."""
    body = ns.lathe([(r * 0.85, 0.0), (r, 0.05), (r, h * 0.82), (r * 0.78, h * 0.94), (0.0, h * 0.94)],
                    verts=verts, loc=(x, y, z))
    lid = ns.cyl(r * 0.8, h * 0.12, loc=(x, y, z + h * 0.97), verts=verts, bevel=0.0)
    label = ns.cyl(r + 0.008, h * 0.32, loc=(x, y, z + h * 0.42), verts=verts, bevel=0.0)
    return body, lid, label


def carton(w, d, h, loc=(0, 0, 0), yaw=0.0, open_top=False, flap_angle=118.0, tape=True, bevel=0.03):
    """L_decor's carton (same return dict), except a closed box's front/back tape drops are
    0.006 narrower than the strip over the top, so their side faces never lie in one plane."""
    if open_top or not tape:
        return D.carton(w, d, h, loc=loc, yaw=yaw, open_top=open_top, flap_angle=flap_angle, tape=tape, bevel=bevel)
    out = {"body": [ns.box((w, d, h), loc=(0, 0, h / 2), bevel=bevel, segments=1)], "tape": [], "inside": [],
           "flaps": []}
    tw, t = min(0.3, w * 0.22), 0.012
    drop = min(0.38, h * 0.3)
    # strip over the top (z h-0.002 .. h+0.010, ends 0.016 past the faces); the drops (0.008 thick,
    # 0.006 proud of the faces) end at z = h, buried in the top strip
    out["tape"].append(ns.box((tw, d + 0.032, t), loc=(0, 0, h + t / 2 - 0.002), bevel=0.0))
    for sy in (-1, 1):
        out["tape"].append(ns.box((tw - 0.006, 0.008, drop), loc=(0, sy * (d / 2 + 0.002), h - drop / 2),
                                  bevel=0.0))
    for lst in out.values():
        place(lst, loc=loc, yaw=yaw)
    return out


def dust_cap(w, d, top_z, loc=(0, 0), yaw=0.0, t=0.014):
    """Thin pale dust layer lying on a box top (bottom buried 0.004 in the top)."""
    o = ns.box((w, d, t), loc=(0, 0, top_z + t / 2 - 0.004), bevel=0.0)
    place([o], loc=(loc[0], loc[1], 0), yaw=yaw)
    return o


def streak_flat(x, z_top, length, width, y_face, seed=0, segs=4, sway=0.03):
    """Rust / grime streak running down a flat face that looks along -Y (face plane y_face):
    a tapering, slightly wavy strip 0.008 proud of the face."""
    rnd = random.Random(seed)
    y = y_face - 0.008
    left, right = [], []
    xc = x
    for i in range(segs + 1):
        f = i / segs
        z = z_top - length * f
        w = width * (1.0 - f) ** 0.8 + 0.006
        xc += rnd.uniform(-sway, sway) if i else 0.0
        left.append((xc - w / 2, y, z))
        right.append((xc + w / 2, y, z))
    bm = bmesh.new()
    lv = [bm.verts.new(p) for p in left]
    rv = [bm.verts.new(p) for p in right]
    for i in range(segs):
        bm.faces.new([lv[i], lv[i + 1], rv[i + 1], rv[i]])
    o = ns.from_bmesh(bm, "Streak")
    return face_dir(o, "-Y")


def streak_cyl(cx, cy, r, ang, z_top, length, width, seed=0, segs=4, sway=0.03):
    """Streak running down the outside of a vertical cylinder (centre cx, cy, radius r) at
    angle `ang` degrees (0 = the -Y front, positive toward +X), 0.008 proud, facing out."""
    rnd = random.Random(seed)
    rr = r + 0.008
    a0 = math.radians(ang)
    bm = bmesh.new()
    rows = []
    da = 0.0
    for i in range(segs + 1):
        f = i / segs
        z = z_top - length * f
        w = width * (1.0 - f) ** 0.8 + 0.006
        da += rnd.uniform(-sway, sway) / rr if i else 0.0
        row = []
        for s in (-1, 1):
            a = a0 + da + s * (w / 2) / rr
            row.append(bm.verts.new((cx + rr * math.sin(a), cy - rr * math.cos(a), z)))
        rows.append(row)
    for i in range(segs):
        bm.faces.new([rows[i][0], rows[i + 1][0], rows[i + 1][1], rows[i][1]])
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.dot(Vector((c.x - cx, c.y - cy, 0.0))) < 0:
            f.normal_flip()
    return ns.from_bmesh(bm, "StreakCyl")


def patch_cyl(cx, cy, r, ang, width, z0, z1, segs=3, proud=0.008):
    """Curved rectangular decal (label, plate) on the outside of a vertical cylinder, centred
    at angle `ang` degrees (0 = the -Y front, positive toward +X), `width` studs of arc,
    `proud` above the surface, facing out."""
    rr = r + proud
    a0 = math.radians(ang)
    half = (width / 2) / rr
    bm = bmesh.new()
    cols = []
    for i in range(segs + 1):
        a = a0 - half + 2 * half * i / segs
        x, y = cx + rr * math.sin(a), cy - rr * math.cos(a)
        cols.append((bm.verts.new((x, y, z0)), bm.verts.new((x, y, z1))))
    for i in range(segs):
        bm.faces.new([cols[i][0], cols[i + 1][0], cols[i + 1][1], cols[i][1]])
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.dot(Vector((c.x - cx, c.y - cy, 0.0))) < 0:
            f.normal_flip()
    return ns.from_bmesh(bm, "PatchCyl")


def outline_band(pts2d, z0, z1, proud=0.01, skip=None):
    """Vertical decal band following a closed 2D outline (x, y; e.g. an rrect), pushed
    `proud` outward along the outline's normals, faces looking out. skip(i) -> True drops
    the segment from point i to i+1 (e.g. leave the back off)."""
    n = len(pts2d)
    P = [Vector((x, y, 0.0)) for x, y in pts2d]
    area = sum(P[i].x * P[(i + 1) % n].y - P[(i + 1) % n].x * P[i].y for i in range(n))
    sgn = 1.0 if area > 0 else -1.0                   # CCW: outward normal of edge d is (d.y, -d.x)
    off = []
    for i in range(n):
        d0 = (P[i] - P[i - 1]).normalized()
        d1 = (P[(i + 1) % n] - P[i]).normalized()
        n0 = Vector((d0.y, -d0.x, 0.0)) * sgn
        n1 = Vector((d1.y, -d1.x, 0.0)) * sgn
        m = (n0 + n1).normalized()
        off.append(P[i] + m * (proud / max(0.5, m.dot(n1))))
    bm = bmesh.new()
    lo = [bm.verts.new((p.x, p.y, z0)) for p in off]
    hi = [bm.verts.new((p.x, p.y, z1)) for p in off]
    for i in range(n):
        if skip and skip(i):
            continue
        j = (i + 1) % n
        f = bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
        edge_n = Vector(((off[j] - off[i]).y, -(off[j] - off[i]).x, 0.0)) * sgn
        f.normal_update()
        if f.normal.dot(edge_n) < 0:
            f.normal_flip()
    bm.verts.ensure_lookup_table()
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    return ns.from_bmesh(bm, "OutlineBand")


def blob(cx, cz, r, y, seed=0, n=7, facing="-Y"):
    """Irregular flat spot (rust, stain) in the XZ plane at depth y, facing `facing`."""
    rnd = random.Random(seed)
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        rr = r * rnd.uniform(0.6, 1.0)
        pts.append((cx + rr * math.cos(a), y, cz + rr * math.sin(a) * rnd.uniform(0.75, 1.1)))
    return face_dir(poly(pts, "Blob"), facing)


def rivet(p, normal, r=0.05, h=0.035):
    """Low four-sided rivet head on a surface at p (base buried 0.006), facing `normal`."""
    n = Vector(normal).normalized()
    up = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = n.cross(up).normalized()
    v = n.cross(u)
    p = Vector(p) - n * 0.006
    bm = bmesh.new()
    base = [bm.verts.new(p + (u * math.cos(a) + v * math.sin(a)) * r) for a in
            (math.pi / 4 + k * math.pi / 2 for k in range(4))]
    top = [bm.verts.new(p + n * (h + 0.006) + (u * math.cos(a) + v * math.sin(a)) * r * 0.5) for a in
           (math.pi / 4 + k * math.pi / 2 for k in range(4))]
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new([base[k], base[j], top[j], top[k]])
    bm.faces.new(top)
    bm.normal_update()
    for f in bm.faces:
        if f.normal.dot(f.calc_center_median() - p) < 0:
            f.normal_flip()
    return ns.from_bmesh(bm, "Rivet")


def rivet_ring(cx, cy, r, z, n, a0=0.0, rr=0.05):
    """n rivets round a vertical cylinder of radius r at height z."""
    out = []
    for k in range(n):
        a = math.radians(a0) + 2 * math.pi * k / n
        d = Vector((math.sin(a), -math.cos(a), 0.0))
        out.append(rivet((cx + d.x * r, cy + d.y * r, z), d, r=rr))
    return out


def flange(p, axis, r, t=0.08, verts=10):
    """Pipe flange disc centred at p, its faces along `axis` (unit vector)."""
    o = ns.cyl(r, t, loc=(0, 0, 0), verts=verts, bevel=0.015, segments=1)
    o.rotation_euler = Vector(axis).to_track_quat("Z", "Y").to_euler()
    o.location = Vector(p)
    return o


def handwheel(p, axis, r=0.28, verts=10, spokes=2):
    """Valve hand-wheel: rim, cross spokes and a hub centred at p, wheel plane normal = axis.
    Returns a list of objects (one colour)."""
    ax = Vector(axis).normalized()
    up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(up).normalized()
    v = ax.cross(u)
    rim = ns.torus(r, r * 0.13, loc=(0, 0, 0), major_segs=verts, minor_segs=4)
    rim.rotation_euler = ax.to_track_quat("Z", "Y").to_euler()
    rim.location = Vector(p)
    out = [rim]
    for k in range(spokes):
        a = math.pi * k / spokes + math.pi / 4
        d = u * math.cos(a) + v * math.sin(a)
        out.append(rod(Vector(p) - d * r, Vector(p) + d * r, r * 0.09, verts=4))
    out.append(rod(Vector(p) - ax * r * 0.18, Vector(p) + ax * r * 0.18, r * 0.24, verts=6))
    return out


def gauge(p, normal=(0, -1, 0), r=0.32, stalk=0.25, needle_deg=35.0, verts=12):
    """Round pressure gauge whose dial looks along `normal`, dial centre at p; a short stalk
    pipe runs back to the surface. Returns {"bezel", "face", "ink", "stalk"} lists."""
    n = Vector(normal).normalized()
    p = Vector(p)
    q = n.to_track_quat("Z", "Y")
    # local frame: dial looks along +Z, body top cap at z = 0, layers stacked 0.006 apart above it
    body = ns.cyl(r, 0.16, loc=(0, 0, -0.08), verts=verts, bevel=0.0)
    rim = ns.torus(r - 0.025, 0.04, loc=(0, 0, 0.01), major_segs=verts, minor_segs=3)
    face = disc(r - 0.055, loc=(0, 0, 0.008), verts=verts)
    ink = []
    a = math.radians(90 - needle_deg)
    zn = 0.026
    tip = Vector((math.cos(a) * (r - 0.1), math.sin(a) * (r - 0.1), zn))
    nb = bmesh.new()
    side = Vector((-math.sin(a), math.cos(a), 0)) * 0.022
    pts = [Vector((0, 0, zn)) - side, tip, Vector((0, 0, zn)) + side,
           Vector((0, 0, zn)) - Vector((math.cos(a), math.sin(a), 0)) * 0.05]
    nb.faces.new([nb.verts.new(v) for v in pts])
    ink.append(ns.from_bmesh(nb, "Needle"))
    ink.append(disc(0.035, loc=(0, 0, 0.036), verts=6))
    for k in range(5):                              # tick marks round the upper dial
        ta = math.radians(210 - k * 60)
        c0 = Vector((math.cos(ta), math.sin(ta), 0)) * (r - 0.11)
        c1 = Vector((math.cos(ta), math.sin(ta), 0)) * (r - 0.07)
        tb = bmesh.new()
        sd = Vector((-math.sin(ta), math.cos(ta), 0)) * 0.012
        tb.faces.new([tb.verts.new(v + Vector((0, 0, 0.02))) for v in (c0 - sd, c1 - sd, c1 + sd, c0 + sd)])
        ink.append(ns.from_bmesh(tb, "Tick"))
    for o in ink:
        face_dir(o, "+Z")
    red = []
    rb = bmesh.new()
    za = math.radians(-30)
    zb = math.radians(-60)
    arc = [Vector((math.cos(za + (zb - za) * i / 3), math.sin(za + (zb - za) * i / 3), 0)) for i in range(4)]
    vs_o = [rb.verts.new(c * (r - 0.07) + Vector((0, 0, 0.014))) for c in arc]
    vs_i = [rb.verts.new(c * (r - 0.12) + Vector((0, 0, 0.014))) for c in arc]
    for i in range(3):
        rb.faces.new([vs_i[i], vs_i[i + 1], vs_o[i + 1], vs_o[i]])
    red.append(face_dir(ns.from_bmesh(rb, "RedZone"), "+Z"))
    st = rod((0, 0, -0.14), (0, 0, -0.16 - stalk), 0.06, verts=6)
    nut = ns.cyl(0.085, 0.09, loc=(0, 0, -0.16 - stalk * 0.45), verts=6, bevel=0.0)
    groups = {"bezel": [body, rim], "face": [face], "ink": ink, "red": red, "stalk": [st, nut]}
    for lst in groups.values():
        for o in lst:
            ns.apply_all(o)
            o.rotation_euler = q.to_euler()
            o.location = p
            ns.apply_all(o)
    return groups


def padlock(p, yaw=0.0, s=1.0):
    """Chunky padlock hanging with its shackle top at p (front -Y). Returns (body, shackle)."""
    body = ns.box((0.34 * s, 0.16 * s, 0.3 * s), loc=(0, 0, -0.32 * s), bevel=0.05 * s, segments=1)
    shackle = pipe([(-0.1 * s, 0, -0.2 * s), (-0.1 * s, 0, -0.06 * s), (-0.05 * s, 0, 0.0),
                    (0.05 * s, 0, 0.0), (0.1 * s, 0, -0.06 * s), (0.1 * s, 0, -0.2 * s)], 0.028 * s, sides=6)
    key = disc(0.035 * s, loc=(0, 0, 0), verts=6)
    key.rotation_euler = (math.radians(90), 0, 0)
    key.location = (0, -0.088 * s, -0.36 * s)
    ns.apply_all(key)
    face_dir(key, "-Y")
    place([body, shackle, key], loc=p, yaw=yaw)
    return body, shackle, key


def stencil(txt, height, loc, width=None, depth=0.02, res=1, spacing=1.08, raised=False, yaw=0.0):
    """Stencilled lettering on a face looking along -Y: flat single-sided decal (default) or
    raised letters (front + sides) whose back sits on the face at loc.y. Built facing -Y
    at loc, then turned by `yaw` about loc."""
    x, y, z = loc
    if raised:
        o = text(txt, height, depth, (x, y - depth / 2 + 0.004, z), width=width, res=res, spacing=spacing,
                 back=False)
    else:   # front caps only, 0.012 proud of the face
        o = text(txt, height, 0.02, (x, y - 0.002, z), width=width, res=res, spacing=spacing, flat=True)
    if yaw:
        ns.apply_all(o)
        a = math.radians(yaw)
        c, s_ = math.cos(a), math.sin(a)
        for v in o.data.vertices:
            dx, dy = v.co.x - x, v.co.y - y
            v.co.x, v.co.y = x + dx * c - dy * s_, y + dx * s_ + dy * c
    return o


# ---------------------------------------------------------------------------------------
# Cobweb (shared by Basement_Cobweb and the sparse shelf)
# ---------------------------------------------------------------------------------------

def web_fan(apex, dir_a, dir_b, radius, spokes=6, rings=4, bulge=(0, 0, 0), sag=0.16, r_strand=0.016,
            r_edge=None, seed=1, wisps=2, spoke_len=None, dirs=None, wisp_len=(0.18, 0.32)):
    """Stylised cobweb: `spokes` threads radiating from `apex` between the directions dir_a
    .. dir_b (slerped), the middle of the fan pushed by `bulge` (a vector, scaled by
    sin(pi t)), and `rings` cross threads that sag between neighbouring spokes (gravity, -Z).
    The outermost ring is the edge thread (r_edge). A few loose wisps hang off the edge.
    dirs: explicit spoke directions (overrides dir_a / dir_b / spokes).
    Returns a list of thin 3-sided pipes (one colour; tag them with transparency)."""
    rnd = random.Random(seed)
    A, B = Vector(dir_a).normalized(), Vector(dir_b).normalized()
    ap = Vector(apex)
    bv = Vector(bulge)
    ang = A.angle(B)
    r_edge = r_edge or r_strand * 1.3
    # cross threads sit a hair off the spoke plane: 3-sided tubes lying in one plane all have a
    # face parallel to it, which would be coplanar (z-fight) wherever two threads cross
    nrm = A.cross(B)
    lift = nrm.normalized() * r_strand * 0.9 if nrm.length > 1e-6 else Vector((0, 0, 0))

    def dirn(t):
        if ang < 1e-4:
            return A
        return (A * math.sin((1 - t) * ang) + B * math.sin(t * ang)) / math.sin(ang)

    if dirs:
        spokes = len(dirs)
    tips = []
    for k in range(spokes):
        t = k / (spokes - 1)
        ln = radius * (spoke_len[k] if spoke_len else (0.9 + 0.12 * math.sin(math.pi * t)) * rnd.uniform(0.94, 1.04))
        dk = Vector(dirs[k]).normalized() if dirs else dirn(t)
        tips.append(ap + dk * ln + bv * math.sin(math.pi * t))
    out = []
    for k, tip in enumerate(tips):   # neighbouring spokes a hair apart too (they converge at the apex)
        o = lift * (0.35 * (k % 3))
        out.append(pipe([ap + o, ap.lerp(tip, 0.5) + Vector((0, 0, -0.012 * radius)) + o, tip + o], r_strand, sides=3))
    fr = [0.2 + 0.8 * (j + 1) / rings for j in range(rings)]
    fr = [f ** 1.15 for f in fr]
    for j, f in enumerate(fr):
        pts = []
        for k in range(spokes):
            p = ap.lerp(tips[k], f) + lift
            if k:
                q = pts[-1]
                m = (q + p) / 2
                m.z -= sag * (p - q).length * (0.7 + 0.3 * f)
                pts.append(m)
            pts.append(p)
        out.append(pipe(pts, r_edge if j == rings - 1 else r_strand, sides=3))
    for w in range(wisps):
        k = rnd.randrange(1, spokes - 1)
        p = ap.lerp(tips[k], fr[-1]) + lift * 2.6    # hangs off the edge thread, out of its face planes
        q = ap.lerp(tips[k + 1], fr[-1]) + lift * 2.6
        s0 = p.lerp(q, rnd.uniform(0.3, 0.7))
        s0.z -= sag * (q - p).length * 0.8
        drop = radius * rnd.uniform(*wisp_len)
        out.append(pipe([s0, s0 + Vector((rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), -drop * 0.6)),
                         s0 + Vector((rnd.uniform(-0.08, 0.08), rnd.uniform(-0.08, 0.08), -drop))], r_strand, sides=3))
    return out


# ---------------------------------------------------------------------------------------
# Shared metal shelving frame (Basement_MetalShelf / Basement_MetalShelfSparse)
# ---------------------------------------------------------------------------------------
SHELF_W, SHELF_D, SHELF_H = 6.0, 2.0, 8.0
SHELF_TOPS = (0.42, 2.6, 4.78, 6.96)     # shelf top surfaces (4 shelves)
SHELF_T = 0.07                          # deck thickness
UP_A, UP_T = 0.24, 0.05                 # angle-iron flange width / thickness


def shelf_frame(w=SHELF_W, d=SHELF_D, h=SHELF_H, tops=SHELF_TOPS):
    """Slotted-angle steel shelving unit: four angle-iron uprights, four decks with a folded
    front/back lip, X-braced sides and back, foot plates; slot holes on the front flanges.
    Returns {"steel": [...], "slots": [...], "feet": [...]} (untagged)."""
    steel, slots, feet = [], [], []
    hx, hy = w / 2, d / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            steel.append(angle_iron((sx * hx, sy * hy), sx, sy, UP_A, UP_T, 0.04, h))
            feet.append(ns.box((UP_A + 0.04, UP_A + 0.04, 0.05), loc=(sx * (hx - UP_A / 2 - 0.02), sy * (hy - UP_A / 2 - 0.02),
                                                                      0.025), bevel=0.0))   # flush with the outline
    for zt in tops:   # decks bury 0.01 into the side flanges and end inside the lips
        steel.append(ns.box((w - 2 * UP_T + 0.02, d - 2 * UP_T - 0.02, SHELF_T), loc=(0, 0, zt - SHELF_T / 2),
                            bevel=0.0))
        for sy in (-1, 1):   # folded lips on the long edges, standing 0.015 proud of the deck, bolted to the uprights
            steel.append(ns.box((w - 2 * UP_T - 0.012, 0.045, 0.215), loc=(0, sy * (hy - UP_T - 0.0075), zt - 0.0925),
                                bevel=0.0))
    # X-braces: flat straps on both sides (YZ) and the back (XZ), between the lowest and top decks
    zb0, zb1 = tops[0] - 0.12, h - 0.25
    zm = (zb0 + zb1) / 2
    for sx in (-1, 1):
        x = sx * (hx + 0.01)    # 0.001 into the side flanges they are bolted to
        for z0, z1 in ((zb0, zm), (zm, zb1)):
            steel.append(bar((x, -hy + 0.1, z0), (x, hy - 0.1, z1), 0.09, 0.022, normal=(1, 0, 0)))
            steel.append(bar((x, hy - 0.1, z0), (x, -hy + 0.1, z1), 0.09, 0.022, normal=(1, 0, 0)))
    y = hy + 0.01
    steel.append(bar((-hx + 0.12, y, zb0), (hx - 0.12, y, zb1), 0.09, 0.022, normal=(0, 1, 0)))
    steel.append(bar((hx - 0.12, y, zb0), (-hx + 0.12, y, zb1), 0.09, 0.022, normal=(0, 1, 0)))
    # slot holes punched along the front-facing flanges of the two front uprights
    for sx in (-1, 1):
        xc = sx * (hx - UP_A / 2 - 0.01)
        z = 0.32
        while z < h - 0.2:
            if all(abs(z - (zt - 0.1)) > 0.2 for zt in tops):
                slots.append(quad_xz(xc - 0.03, xc + 0.03, z - 0.07, z + 0.07, -hy - 0.006))
            z += 0.4
    return {"steel": steel, "slots": slots, "feet": feet}


# ---------------------------------------------------------------------------------------
# Ceiling pipe bundle (Basement_PipeRun / Basement_PipeCorner): three pipes side by side,
# resting on trapeze brackets hung from the ceiling (z = 0); 1 deep x 0.9 tall.
# ---------------------------------------------------------------------------------------
STRUT_Z0, STRUT_Z1 = -0.9, -0.78          # strut channel bottom / top
# (lateral offset from the bundle centre line, radius, colour, name) - lateral +1 = the
# left of the direction of travel (+Y for a run along +X)
BUNDLE = ((-0.32, 0.14, CONCRETE, "PipeGrey"), (0.0, 0.09, COPPER, "PipeCopper"),
          (0.32, 0.14, CONCRETE_DARK, "PipeDark"))
ROD_OFF = 0.43                              # threaded rods, lateral


def bundle_z(r):
    """Centre height of a bundle pipe of radius r (it rests on the strut)."""
    return STRUT_Z1 + r


def pipe_bracket(c, d):
    """Trapeze hanger at c = (x, y) on the bundle centre line, d = bundle direction (2D unit).
    Returns {"strut": [...], "rods": [...], "clamps": [...]}: a strut channel across the
    bundle, two threaded rods up to small ceiling plates, and a U-bolt over each pipe."""
    c = Vector((c[0], c[1], 0.0))
    dv = Vector((d[0], d[1], 0.0)).normalized()
    lat = Vector((-dv.y, dv.x, 0.0))                  # left of travel
    zc = (STRUT_Z0 + STRUT_Z1) / 2
    strut = bar(c + lat * -0.5 + Vector((0, 0, zc)), c + lat * 0.5 + Vector((0, 0, zc)), 0.14, STRUT_Z1 - STRUT_Z0,
                normal=(0, 0, 1))
    rods, plates = [], []
    for s in (-1, 1):
        p = c + lat * (s * ROD_OFF)
        rods.append(rod((p.x, p.y, -0.01), (p.x, p.y, zc), 0.025, verts=4))
        plates.append(ns.box((0.14, 0.14, 0.04), loc=(p.x, p.y, -0.02), bevel=0.0))
        rods.append(ns.cyl(0.045, 0.05, loc=(p.x, p.y, STRUT_Z1 + 0.025), verts=6, bevel=0.0))   # nut on the strut
    clamps = []
    for off, r, _col, _n in BUNDLE:
        zp = bundle_z(r)
        g = r + 0.02     # U-bolt centre line (legs of neighbouring bolts stay >= 0.05 apart)
        pts = [(-g, STRUT_Z1 - 0.01), (-g, zp)] + [(-g * math.cos(a), zp + g * math.sin(a))
                                                   for a in (math.radians(45), math.radians(90), math.radians(135))]
        pts += [(g, zp), (g, STRUT_Z1 - 0.01)]
        world = [c + lat * (off + u) + Vector((0, 0, z)) for u, z in pts]
        clamps.append(pipe(world, 0.017, sides=4))
    return {"strut": [strut], "rods": rods + plates, "clamps": clamps}


# ---------------------------------------------------------------------------------------
# Previews (configurable views; wall / ceiling / corner backdrops in the basement charcoal)
# ---------------------------------------------------------------------------------------
VIEWS_FLOOR = ((-35, 28, False), (150, 22, True))
VIEWS_FRONT = ((-35, 22, False), (35, 14, True))      # wall-backed floor props: both from the room
VIEWS_WALL = ((-35, 18, False), (32, 10, True))
VIEWS_HANG = ((-35, -14, False), (40, -6, True))
BACKDROP_COL = "#55585E"      # a lighter charcoal than the real walls so silhouettes read


def preview(asset, out_dir, res=512, samples=16, views=VIEWS_FLOOR, backdrop=None, floor=True,
            backdrop_col=BACKDROP_COL):
    """Two-panel preview like nslib.render_preview with configurable (yaw, pitch, ref) views.
    backdrop: None | "wall" (plane on the back face, y = bbox max) | "ceiling" (plane on
    z = bbox max) | "corner" (back wall + the +X side wall + ceiling meeting at the bbox's
    top back +X corner)."""
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True)
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    span = max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z, 0.5)
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=max(span * 8, 8),
                                         location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z - 0.001))
        fl = bpy.context.active_object
        fl.name = "Floor"
        fl.data.materials.append(ns.material("#3A3B42"))
    planes = []
    if backdrop in ("wall", "corner"):
        planes.append(((lo.x + hi.x) / 2, hi.y + 0.002, (lo.z + hi.z) / 2, (math.radians(90), 0, 0)))
    if backdrop in ("ceiling", "corner"):
        planes.append(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z + 0.002, (0, 0, 0)))
    if backdrop == "corner":
        planes.append((hi.x + 0.002, (lo.y + hi.y) / 2, (lo.z + hi.z) / 2, (0, math.radians(90), 0)))
    for i, (x, y, z, rot) in enumerate(planes):
        bpy.ops.mesh.primitive_plane_add(size=max(span * 6, 8), location=(x, y, z), rotation=rot)
        w = bpy.context.active_object
        w.name = f"FloorBackdrop{i}"
        w.data.materials.append(ns.material(backdrop_col))
    ns._setup_render(res, samples, transparent=False)
    for m in bpy.data.materials:   # preview only: Roblox Glass reflects far less (see L_decor)
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
            ry = (lo.y + hi.y) / 2 if backdrop not in ("wall", "corner") else hi.y - 0.5
            rz = lo.z + 0.5 if floor else hi.z - 0.5
            ref = ns.box((1, 1, 1), loc=(lo.x - 0.7, ry, rz), bevel=0.0, name="RefCube")
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


def socket_check(asset, sockets, views=((-35, 28),), res=448, samples=8):
    """Render the asset with magenta arrow markers at every socket (previews/N_basement/_checks)."""
    from PIL import Image
    markers = []
    for name, spec in sockets.items():
        if len(spec) == 2 and not isinstance(spec[0], (int, float)):
            loc, yaw = spec
        else:
            loc, yaw = spec, 0.0
        markers += L._arrow(loc, yaw, size=0.4)
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs + markers)
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


def hang_preview(dirs=((-0.45, -1.0, -0.35), (0.55, -0.7, -0.9)), lens=50, margin=1.12):
    """Preview for ceiling-hung pieces: a ceiling plane on z = bbox top, then K_shop's
    tightly framed views from below (dir_preview)."""
    def fn(asset, out_dir, res, spp):
        lo, hi = ns.bbox_world(ns._tagged_objects())
        span = max(hi.x - lo.x, hi.y - lo.y, 1.0)
        bpy.ops.mesh.primitive_plane_add(size=span * 6, location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z + 0.002))
        c = bpy.context.active_object
        c.name = "FloorCeiling"
        c.data.materials.append(ns.material(BACKDROP_COL))
        return K.dir_preview(asset, out_dir, res, spp, list(dirs), lens=lens, margin=margin)
    return fn


def run(build, asset, sockets=None, views=None, backdrop=None, budget=2000, mount="floor",
        socket_views=((-35, 28),), backdrop_col=BACKDROP_COL, preview_fn=None, **export_kw):
    """Standard N_basement entry: build -> preview (quick with NS_QUICK=1) -> optional socket
    check render -> export when NS_EXPORT=1. `budget` = triangle budget (warns if over or
    under the 200 props minimum). mount: "floor" (pivot bottom-centre, nslib default),
    "wall" (wall views + backdrop; pass pivot=) or "hang" (pivot = top-centre of the bbox
    unless pivot= is given; views from below, ceiling backdrop, no floor).
    build() may return {"export": {...}} with sockets / meta / pivot overrides.
    Socket positions are Blender world points (exported relative to the pivot)."""
    if views is None:
        views = {"wall": VIEWS_WALL, "hang": VIEWS_HANG}.get(mount, VIEWS_FLOOR)
    if backdrop is None:
        backdrop = {"wall": "wall", "hang": "ceiling"}.get(mount)
    ns.reset()
    extra = build() or {}
    exp = dict(export_kw)
    exp.update(extra.get("export", {}))
    sockets = exp.pop("sockets", sockets)
    tris = ns.tri_count()
    flag = ""
    if budget is not None and tris > budget:
        flag = f"   *** OVER BUDGET ({budget}) ***"
    elif tris < 200:
        flag = "   *** UNDER the 200-tri props minimum ***"
    print(f"[{asset}] triangles: {tris}" + (f" / {budget}" if budget else "") + flag)
    if os.environ.get("NS_PARTS") == "1":
        D._print_parts(asset)
    if os.environ.get("NS_NORENDER") != "1":
        quick = os.environ.get("NS_QUICK") == "1"
        res, spp = (384, 8) if quick else (512, 16)
        out_dir = os.path.join(PREVIEWS, "_quick") if quick else PREVIEWS
        os.makedirs(out_dir, exist_ok=True)
        if preview_fn is not None:
            prev = preview_fn(asset, out_dir, res, spp)
        else:
            prev = preview(asset, out_dir, res=res, samples=spp, views=views, backdrop=backdrop,
                           floor=(mount != "hang"), backdrop_col=backdrop_col)
        print(f"[{asset}] preview: {os.path.abspath(prev)}")
    if sockets and os.environ.get("NS_SOCKETS") == "1":
        print(f"[{asset}] sockets: {socket_check(asset, sockets, views=socket_views)}")
    if os.environ.get("NS_EXPORT") == "1":
        if mount == "hang" and "pivot" not in exp:
            lo, hi = ns.bbox_world(ns._tagged_objects())
            exp["pivot"] = ((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, hi.z)
            print(f"[{asset}] pivot (hang): {tuple(round(c, 3) for c in exp['pivot'])}")
        doc = ns.export_asset(asset, BATCH, group=GROUP, sockets=sockets, **exp)
        print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']} "
              f"(Roblox x,y,z = W,H,D)")
        for p in doc["parts"]:
            print(f"    part {p['name']:18s} {p['material']:13s} role={p['role']} collide={p['canCollide']} "
                  f"tris={p['tris']}")
        if doc.get("sockets"):
            print(f"    sockets {doc['sockets']}")
    return extra


def contact_sheet(cols=3, thumb=340):
    """Labelled grid of every <asset>_preview.png in previews/N_basement -> _contact.png."""
    return ns.contact_sheet(BATCH, cols=cols, thumb=thumb)
