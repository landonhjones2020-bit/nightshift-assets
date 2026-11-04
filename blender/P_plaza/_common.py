"""_common — shared helpers for the P_plaza batch (lobby plaza fill-out: seating, a food truck,
planting, dusk lighting, festoons and bunting, an arcade cabinet, a photo board, a neon arrow
sign, a giant fries statue and hedges).

Import from an asset script in this folder with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Re-uses blender/J_lobby/_common.py (word_solid / contour_tubes / domes neon-and-marquee kit,
awning, badge, mini_logo, loft, spheres, the dusk far-view check), which re-uses
blender/C_lobby/_common.py (palette, part, rod, catenary, text, place, screen_meta ...) and the
B_shop shape helpers (prism, pipe, fillet, rrect, ring_slab ...), so the plaza props share the
lobby's family look. The faceted-foliage helpers (split_faces, two_tone, cull_hidden,
ico_blob, flatten_below) come from blender/I_world/_common.py.

New here:
  * grid_box() / round_box() / noise_displace()  lumpy rounded boxes (trimmed hedges, mounds)
  * noise_field()                               smooth 3D noise (dappled two-tone foliage)
  * tulip() / daisy() / blossom()               cheap chunky flowers
  * hang_bulbs()                                festoon bulbs (sockets + globes) along a cable
  * inset_poly()                                miter inset / outset of a closed 2D outline
  * along_x()                                   Blender x of a point that lies `d` studs along
                                                Roblox +X from the pivot (spans: x_b = -d)

Conventions (as J_lobby): 1 stud = 1 Blender unit, Z up, front faces Blender -Y, pivot
bottom-centre unless a script says otherwise, role-less parts merge per material at export,
part names never start with Key/Fill/Rim/Floor/RefCube/PreviewCam. Glowing parts: role "lamp"
(bulbs) or "neon" (tubes / trim), material Neon; every lit asset has a `Light` socket where the
map's PointLight goes. Screens: role "screen" (dark Glass), socket at the screen face centre,
meta screen_size / surfaces. Env: NS_QUICK=1 fast preview (previews/P_plaza/_quick), NS_FAR=1
dusk far-view check (previews/P_plaza/_checks), NS_SOCKETS=1 socket check, NS_PARTS=1 part
list, NS_NORENDER=1 no renders, NS_EXPORT=1 export.
"""
from __future__ import annotations

import importlib.util
import math
import os
import random
import sys

import bpy  # noqa: F401  (must load before bmesh in the bpy module build)
import bmesh
from mathutils import Matrix, Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "lib"))
import nslib as ns  # noqa: E402


def _load(modname, folder):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(_HERE, "..", folder, "_common.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


J = _load("jlobby_common", "J_lobby")     # J_lobby kit (loads C_lobby + B_shop itself)
W = _load("world_common", "I_world")      # faceted foliage helpers
L, S = J.L, J.S

BATCH = "P_plaza"
GROUP = "Lobby"
PREVIEWS = os.path.join(ns.REPO, "..", "previews", BATCH)
J.PREVIEWS = PREVIEWS        # J's dusk / socket check renders write to previews/P_plaza/_checks

# ---------------------------------------------------------------------------------------
# Re-exported helpers
# ---------------------------------------------------------------------------------------
fillet, rrect, circle_pts, ellipse_pts = S.fillet, S.rrect, S.circle_pts, S.ellipse_pts
prism, slab, pipe, round_path, ring_slab = S.prism, S.slab, S.pipe, S.round_path, S.ring_slab
text_mesh, fit_text_width, bbox_of, merge, band = S.text_mesh, S.fit_text_width, S.bbox_of, S.merge, S.band
FONT_BOLD, FONT_BOLD_ITALIC = S.FONT_BOLD, S.FONT_BOLD_ITALIC
part, rod, yaw_point, facing_yaw = L.part, L.rod, L.yaw_point, L.facing_yaw
arc_solid, arc_profile_sweep, arch, arch_path = L.arc_solid, L.arc_profile_sweep, L.arch, L.arch_path
annulus, disc, catenary, text, sandwich_icon, place = L.annulus, L.disc, L.catenary, L.text, L.sandwich_icon, L.place
screen_meta = L.screen_meta
star_pts, obj_from_bm, domes, spheres, loft = J.star_pts, J.obj_from_bm, J.domes, J.spheres, J.loft
flat_poly, flat_poly_3d, path_points, rect_path = J.flat_poly, J.flat_poly_3d, J.path_points, J.rect_path
badge, mini_logo, add_parts, merge_into, awning = J.badge, J.mini_logo, J.add_parts, J.merge_into, J.awning
Word, contour_tubes, stroke_points, stroke_paths = J.Word, J.contour_tubes, J.stroke_points, J.stroke_paths
resample, split_islands, simplify = J.resample, J.split_islands, J._simplify
split_faces, two_tone, cull_hidden, ico_blob = W.split_faces, W.two_tone, W.cull_hidden, W.ico_blob
flatten_below, drop_faces, transform_obj = W.flatten_below, W.drop_faces, W.transform_obj

# ---------------------------------------------------------------------------------------
# Palette (the brief's plaza palette + J_lobby / C_lobby shades)
# ---------------------------------------------------------------------------------------
BRAND, BRAND_DARK, MUSTARD = J.BRAND, J.BRAND_DARK, J.MUSTARD      # #E8502A, #B83D22, #F2B33D
CREAM, CREAM_SHADE, PAPER = J.CREAM, J.CREAM_SHADE, J.PAPER         # #EFE6D2, #DCD0B8, #F3EEE2
NAVY, NAVY_DEEP, STEEL_NAVY = J.NAVY, J.NAVY_DEEP, J.STEEL_NAVY     # #1E2A44, #141C2E, #2A3550
PINK, CYAN = J.PINK, J.CYAN                                         # #FF4FA3, #38E1FF
BRICK = "#9C4A3A"            # plaza brick (brief)
BRICK_DARK = "#7E3A2E"
MORTAR = J.MORTAR
BULB = "#FFD9A0"             # warm festoon bulbs (brief)
CHROME, STEEL, CHARCOAL, RUBBER = J.CHROME, J.STEEL, J.CHARCOAL, J.RUBBER
STAINLESS = J.STAINLESS
SCREEN = J.SCREEN
GLASS, GLASS_DARK = J.GLASS, J.GLASS_DARK
WOOD, WOOD_LIGHT, WOOD_DARK = J.WOOD, J.WOOD_LIGHT, J.WOOD_DARK
STONE, STONE_DARK, CONCRETE = J.STONE, J.STONE_DARK, J.CONCRETE
LETTUCE, TOMATO, CHEESE, BUN, BUN_DARK = J.LETTUCE, J.TOMATO, J.CHEESE, J.BUN, J.BUN_DARK
KETCHUP, MUSTARD_SAUCE = J.KETCHUP, J.MUSTARD_SAUCE
FOLIAGE, FOLIAGE_DARK, FOLIAGE_DEEP = J.FOLIAGE, J.FOLIAGE_DARK, J.FOLIAGE_DEEP   # #4E8A3A ...
LEAF_LIGHT = "#6FA84A"       # sunlit tops of trimmed foliage
SOIL = "#3B2A20"
CABLE = "#1E1F23"
BLACK = J.BLACK
PETAL_PINK = "#FF7DB8"
PETAL_VIOLET = "#9A6BD8"
PETAL_WHITE = "#F6F1E4"
FRY = "#F5C04A"              # golden fries
FRY_DARK = "#E0A033"

FORBIDDEN = J.FORBIDDEN


# ---------------------------------------------------------------------------------------
# Spans: the map places them from a start hook along the model's +X (Roblox RightVector)
# ---------------------------------------------------------------------------------------

def along_x(d):
    """Blender x of a point d studs along Roblox +X from the pivot (x_r = -x_b)."""
    return -d


# ---------------------------------------------------------------------------------------
# 2D outlines
# ---------------------------------------------------------------------------------------

def inset_poly(pts, d, min_cos=0.25):
    """Miter-offset a closed 2D polygon inward by d (either winding; d < 0 grows it)."""
    area = sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts))) / 2
    sgn = 1.0 if area > 0 else -1.0          # CCW: inward = left normal
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((-e0.y, e0.x)) * sgn, Vector((-e1.y, e1.x)) * sgn
        b = (n0 + n1)
        b = b.normalized() if b.length > 1e-9 else n0
        out.append(tuple(p1 + b * (d / max(b.dot(n0), min_cos))))
    return out


# ---------------------------------------------------------------------------------------
# Lumpy rounded boxes (hedges, leaf mounds)
# ---------------------------------------------------------------------------------------

def grid_box(size, cells, loc=(0, 0, 0), name="GridBox", bottom=True):
    """Closed box surface subdivided into a grid: size (x, y, z), cells (nx, ny, nz) per axis.
    bottom=False leaves the underside open (things standing on the ground)."""
    sx, sy, sz = size
    nx, ny, nz = cells
    bm = bmesh.new()
    hx, hy, hz = sx / 2, sy / 2, sz / 2

    def face(origin, du, dv, nu, nv):
        rows = []
        for j in range(nv + 1):
            rows.append([bm.verts.new(Vector(origin) + Vector(du) * (i / nu) + Vector(dv) * (j / nv)) for i in range(nu + 1)])
        for j in range(nv):
            for i in range(nu):
                bm.faces.new([rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]])

    face((-hx, -hy, -hz), (sx, 0, 0), (0, 0, sz), nx, nz)        # front (-Y)
    face((hx, hy, -hz), (-sx, 0, 0), (0, 0, sz), nx, nz)         # back (+Y)
    face((hx, -hy, -hz), (0, sy, 0), (0, 0, sz), ny, nz)         # +X
    face((-hx, hy, -hz), (0, -sy, 0), (0, 0, sz), ny, nz)        # -X
    face((-hx, -hy, hz), (sx, 0, 0), (0, sy, 0), nx, ny)         # top
    if bottom:
        face((-hx, hy, -hz), (sx, 0, 0), (0, -sy, 0), nx, ny)    # bottom
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = obj_from_bm(bm, name)
    for v in ob.data.vertices:
        v.co += Vector(loc)
    ob.data.update()
    return ob


def round_box(obj, centre, half, r, r_bottom=None):
    """Map the vertices of a (subdivided) box onto a rounded box with corner radius r about
    `centre` with half extents `half` (clamp to the inner box, push out by r). r_bottom
    (default r) is the radius used for vertices below the centre."""
    c = Vector(centre)
    for v in obj.data.vertices:
        p = v.co - c
        rr = r if (r_bottom is None or p.z >= 0) else r_bottom
        inner = Vector((max(-(half[0] - rr), min(half[0] - rr, p.x)), max(-(half[1] - rr), min(half[1] - rr, p.y)),
                        max(-(half[2] - rr), min(half[2] - rr, p.z))))
        d = p - inner
        if d.length > 1e-9:
            v.co = c + inner + d.normalized() * rr
    obj.data.update()
    return obj


def noise_field(freq=1.6, seed=1):
    """Smooth deterministic 3D noise f(p) in about [-1, 1] (a few random plane waves)."""
    rnd = random.Random(seed)
    waves = []
    for _ in range(6):
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized()
        waves.append((d * freq * rnd.uniform(0.7, 1.4), rnd.uniform(0, math.tau), rnd.uniform(0.5, 1.0)))
    norm = sum(w[2] for w in waves) * 0.6

    def f(p):
        p = Vector(p)
        return max(-1.0, min(1.0, sum(a * math.sin(d.dot(p) + ph) for d, ph, a in waves) / norm))
    return f


def noise_displace(obj, amp=0.08, freq=1.6, seed=1, jitter=0.0, keep=None):
    """Displace vertices along their (vertex) normal by a smooth deterministic noise (a few
    random plane waves) + optional per-vertex jitter. keep(co) -> True leaves a vertex alone."""
    rnd = random.Random(seed)
    waves = []
    for _ in range(6):
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized()
        waves.append((d * freq * rnd.uniform(0.7, 1.4), rnd.uniform(0, math.tau), rnd.uniform(0.5, 1.0)))
    norm = sum(w[2] for w in waves)
    me = obj.data
    me.update()
    for v in me.vertices:
        if keep is not None and keep(v.co):
            continue
        n = sum(a * math.sin(d.dot(v.co) + ph) for d, ph, a in waves) / norm
        n += rnd.uniform(-jitter, jitter)
        v.co += v.normal * (amp * n)
    me.update()
    return obj


# ---------------------------------------------------------------------------------------
# Flowers (chunky, read at a distance; each returns {colour: [objs]})
# ---------------------------------------------------------------------------------------

def tulip(x, y, z, h, col, r=0.17, tilt=(0.0, 0.0), stem_col=None, seed=0):
    """Cup-shaped tulip on a stem from (x, y, z) up to height h: 6-sided cup with 3 pointed
    petal tips. tilt = (deg about X, deg about Y) of the whole flower."""
    from mathutils import Euler
    rnd = random.Random(seed)
    stem_col = stem_col or FOLIAGE_DARK
    out = {col: [], stem_col: []}
    top = Vector((0, 0, h))
    R = Euler((math.radians(tilt[0]), math.radians(tilt[1]), 0.0)).to_matrix()
    base = Vector((x, y, z))
    head = base + R @ top
    out[stem_col].append(rod(base, head, 0.05, verts=3))
    prof = [(0.0, -0.02), (r * 0.75, 0.0), (r, r * 0.9), (r * 0.9, r * 1.9), (0.0, r * 1.25)]
    cup = ns.lathe(prof, verts=6)
    ns.apply_all(cup)
    for v in cup.data.vertices:          # every other rim vertex rises into a petal tip
        if v.co.z > r * 1.5:
            a = math.atan2(v.co.y, v.co.x)
            k = int(round(a / (math.pi / 3))) % 2
            v.co.z += (0.12 if k == 0 else -0.05) * r / 0.17
    cup.data.update()
    cup.rotation_euler = (math.radians(tilt[0]), math.radians(tilt[1]), rnd.uniform(0, math.tau))
    cup.location = head - R @ Vector((0, 0, 0.02))
    out[col].append(cup)
    return out


def daisy(x, y, z, col, r=0.32, centre=None, n=5, tilt=(0.0, 0.0), yaw=0.0, t=0.06):
    """Flat round-petalled flower head (n lobes) with a domed centre, at (x, y, z), tilted
    (deg about X, deg about Y) so it faces the viewer. No stem (sits on leaves)."""
    from mathutils import Euler, Matrix
    centre = centre or MUSTARD
    pts = []
    m = n * 4
    for i in range(m):
        a = 2 * math.pi * i / m
        rr = r * (0.62 + 0.38 * abs(math.cos(n * a / 2)) ** 0.7)
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    head = prism(pts, "z", -t / 2, t / 2)
    dome = ns.sphere(r * 0.34, loc=(0, 0, t / 2), scale=(1, 1, 0.55), segs=6, rings=3)
    M = Matrix.Translation((x, y, z)) @ Euler((math.radians(tilt[0]), math.radians(tilt[1]), math.radians(yaw))).to_matrix().to_4x4()
    for o in (head, dome):
        ns.apply_all(o)
        o.data.transform(M)
        o.data.update()
    return {col: [head], centre: [dome]}


def blossom(p, normal, r, up_tilt=0.35, spin=0.0):
    """Five-petal flower head facing along `normal` (tilted up a little): a flat star cap
    (front only) + a small centre dome. Returns (petal_obj, centre_obj)."""
    n = (Vector(normal).normalized() + Vector((0, 0, up_tilt))).normalized()
    R = Vector((0, 0, 1)).rotation_difference(n).to_matrix().to_4x4() @ Matrix.Rotation(spin, 4, "Z")
    M = Matrix.Translation(Vector(p)) @ R
    bm = bmesh.new()
    pts = []
    for i in range(15):                               # five round petals
        a = 2 * math.pi * i / 15
        rr = r * (0.5 + 0.5 * abs(math.cos(5 * a / 2)) ** 0.6)
        pts.append(bm.verts.new(M @ Vector((rr * math.cos(a), rr * math.sin(a), 0.0))))
    f = bm.faces.new(pts)
    bm.normal_update()
    if f.normal.dot(n) < 0:
        f.normal_flip()
    petals = obj_from_bm(bm, "Petals")
    dome = domes([tuple(M @ Vector((0, 0, 0.005)))], r * 0.36, axis=tuple(n), segs=5, rings=1)
    return petals, dome


# ---------------------------------------------------------------------------------------
# Festoon bulbs
# ---------------------------------------------------------------------------------------

def hang_bulbs(cable_pts, n, r=0.24, drop=0.1, sock_r=0.085, sock_h=0.2, segs=6, rings=4, end_pad=0.5,
               fine=None, wires=True, sock_verts=6):
    """n bulbs evenly spaced (by arc length) along a cable polyline, end_pad studs in from each
    end. Returns (sockets: [objs], bulb centres: [xyz]) - the sockets hang `drop` below the
    cable, globes below them (merge the globes with spheres(centres, r, ...))."""
    pts = [Vector(p) for p in (fine or cable_pts)]
    seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seg)

    def at(t):
        acc = 0.0
        for i, sl in enumerate(seg):
            if acc + sl >= t or i == len(seg) - 1:
                u = 0.0 if sl < 1e-9 else min(1.0, max(0.0, (t - acc) / sl))
                return pts[i].lerp(pts[i + 1], u)
            acc += sl
        return pts[-1]

    socks, centres = [], []
    for k in range(n):
        t = end_pad + (total - 2 * end_pad) * (k / (n - 1) if n > 1 else 0.5)
        p = at(t)
        top = p - Vector((0, 0, 0.02))
        socks.append(ns.cyl(sock_r, sock_h, loc=(p.x, p.y, top.z - drop - sock_h / 2 + 0.02), verts=sock_verts, bevel=0.0))
        if wires and drop > 0.02:
            socks.append(rod(top + Vector((0, 0, 0.03)), top - Vector((0, 0, drop)), 0.025, verts=3))
        centres.append((p.x, p.y, top.z - drop - sock_h - r * 0.92))
    return socks, centres


# ---------------------------------------------------------------------------------------
# Run wrapper (J_lobby's, exporting to P_plaza)
# ---------------------------------------------------------------------------------------

def run(build, asset, sockets=None, socket_views=((-35, 28),), budget=2000, far=False, far_kw=None, **export_kw):
    """build -> preview (NS_QUICK=1: fast, to _quick/) -> dusk far view (NS_FAR=1, or on every
    final preview when far=True) -> socket check (NS_SOCKETS=1) -> export (NS_EXPORT=1)."""
    ns.reset()
    extra = build() or {}
    tris = ns.tri_count()
    print(f"[{asset}] triangles: {tris} / budget {budget}")
    if budget and tris > budget:
        print(f"[{asset}] WARNING: over the triangle budget by {tris - budget}")
    if os.environ.get("NS_PARTS") == "1":
        J._print_parts(asset)
    lo, hi = ns.bbox_world(ns._tagged_objects())
    print(f"[{asset}] size (Roblox X width, Y height, Z depth): "
          f"{hi.x - lo.x:.2f} x {hi.z - lo.z:.2f} x {hi.y - lo.y:.2f}")
    quick = os.environ.get("NS_QUICK") == "1"
    norender = os.environ.get("NS_NORENDER") == "1"
    if not norender and os.environ.get("NS_ONLYFAR") != "1":
        res, spp = (384, 8) if quick else (512, 16)
        out_dir = os.path.join(PREVIEWS, "_quick") if quick else PREVIEWS
        prev = ns.render_preview(asset, out_dir=out_dir, res=res, samples=spp)
        print(f"[{asset}] preview: {os.path.normpath(prev)}")
    if os.environ.get("NS_FAR") == "1" or os.environ.get("NS_ONLYFAR") == "1" or (far and not quick and not norender):
        kw = far_kw or {}
        out = J.render_dusk(asset, J.far_views(**kw), samples=10 if quick else 16)
        print(f"[{asset}] dusk check: {os.path.normpath(out)}")
    if sockets and os.environ.get("NS_SOCKETS") == "1":
        print(f"[{asset}] sockets: {os.path.normpath(J.socket_check(asset, sockets, views=socket_views))}")
    if os.environ.get("NS_EXPORT") == "1":
        kw = dict(export_kw)
        kw.update(extra.get("export", {}))
        doc = ns.export_asset(asset, BATCH, group=GROUP, sockets=sockets, **kw)
        print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']}")
        for p in doc["parts"]:
            print(f"    part {p['name']:20s} {p['material']:13s} role={p['role']} collide={p['canCollide']} tris={p['tris']}")
        print(f"[{asset}] sockets (Roblox, from pivot): {doc.get('sockets')}")
    return extra
