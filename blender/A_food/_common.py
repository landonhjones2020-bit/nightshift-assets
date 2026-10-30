"""_common — shared helpers for the A_food batch (Night Shift at STACKHOUSE).

Everything here builds on blender/lib/nslib.py. Asset scripts in this folder import it:

    import _common as C
    ns = C.ns

Sandwich contract (STYLE.md section 4): a sandwich lies along Blender X, centred, bottom at Z=0.
Sub roll 2.2 long x 0.85 wide; bottom half 0.30 tall, top half 0.42 tall. Fillings may overhang
the roll by <= 0.08 (|x| <= 1.18, |y| <= 0.505).
"""
from __future__ import annotations

import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
sys.path.insert(0, HERE)
import nslib as ns  # noqa: E402

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

BATCH = "A_food"
GROUP = "Food"

ROLL_L = 2.2
ROLL_W = 0.85
ROLL_A = ROLL_L / 2          # half length
ROLL_B = ROLL_W / 2          # half width
ROLL_EXP = 2.4               # superellipse exponent of the roll's plan outline
BOTTOM_H = 0.30
TOP_H = 0.42
OVERHANG = 0.08
MAX_X = ROLL_A + OVERHANG    # 1.18
MAX_Y = ROLL_B + OVERHANG    # 0.505

PREVIEW_DIR = os.path.join(ns.REPO, "..", "previews", BATCH)
DRAFT_DIR = os.environ.get("NS_DRAFT_DIR", "/tmp/claude-0/-home-claude/bee54a24-967a-5993-94e6-c9b5acdf45a4/scratchpad/drafts")


# --------------------------------------------------------------------------------------
# small maths helpers
# --------------------------------------------------------------------------------------

def spow(v: float, e: float) -> float:
    return math.copysign(abs(v) ** e, v)


def smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def superellipse(a: float, b: float, n: float = ROLL_EXP, N: int = 32, phase: float = 0.0):
    """Closed superellipse outline [(x, y)], CCW, N points (uniform in the angle parameter,
    which puts more points on the tight ends of an elongated shape)."""
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N + phase
        pts.append((a * spow(math.cos(t), 2 / n), b * spow(math.sin(t), 2 / n)))
    return pts


def circle(r: float, N: int = 16, cx: float = 0.0, cy: float = 0.0, phase: float = 0.0, wobble=None):
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N + phase
        rr = r * (1 + (wobble(t) if wobble else 0.0))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    return pts


def rot2(pts, deg: float, cx: float = 0.0, cy: float = 0.0):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def move2(pts, dx: float, dy: float):
    return [(x + dx, y + dy) for x, y in pts]


# --------------------------------------------------------------------------------------
# mesh construction
# --------------------------------------------------------------------------------------

def mesh_obj(name: str, verts, faces, recalc: bool = True) -> bpy.types.Object:
    """Object from raw verts/faces (faces = index tuples)."""
    bm = bmesh.new()
    bv = [bm.verts.new(v) for v in verts]
    for f in faces:
        try:
            bm.faces.new([bv[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return obj


def loft(name: str, rings, cap_start: str | None = "fan", cap_end: str | None = "fan",
         start_center=None, end_center=None) -> bpy.types.Object:
    """Skin a list of closed rings (each a list of (x, y, z) with equal counts).
    cap: "fan" (to a centre vertex — shades smoothly), "ngon", or None (open)."""
    N = len(rings[0])
    verts = [v for r in rings for v in r]
    faces = []
    for k in range(len(rings) - 1):
        for i in range(N):
            j = (i + 1) % N
            faces.append((k * N + i, k * N + j, (k + 1) * N + j, (k + 1) * N + i))

    def cap(ring_idx, mode, centre, reverse):
        base = ring_idx * N
        if mode == "ngon":
            idx = [base + i for i in range(N)]
            faces.append(tuple(reversed(idx)) if reverse else tuple(idx))
        elif mode == "fan":
            r = rings[ring_idx]
            c = centre or (sum(p[0] for p in r) / N, sum(p[1] for p in r) / N, sum(p[2] for p in r) / N)
            verts.append(tuple(c))
            ci = len(verts) - 1
            for i in range(N):
                j = (i + 1) % N
                faces.append((ci, base + j, base + i) if reverse else (ci, base + i, base + j))

    if cap_start:
        cap(0, cap_start, start_center, True)
    if cap_end:
        cap(len(rings) - 1, cap_end, end_center, False)
    return mesh_obj(name, verts, faces)


def ccw(pts):
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts)))
    return pts if area > 0 else list(reversed(pts))


def sheet(name: str, outline, thickness: float, zfn=None, center=None, inner=(0.5,),
          edge: float = 0.5, bulge: float = 0.0, round_edge: bool = True, split_edge: bool = False,
          rim_on_top: bool = False):
    """A soft-edged slab from a star-shaped outline (food slices, leaves, cheese...).

    outline    closed [(x, y)] polygon, star-shaped about `center` (any winding).
    thickness  slab thickness (vertical).
    zfn        zfn(x, y, s, i) -> bottom height at a point; s = 0 centre .. 1 rim, i = outline
               index (lets callers add ruffles, droop, drape). Default flat at 0.
    inner      extra top rings (fractions of the radius) so the top can bend.
    edge       rim rounding as a fraction of thickness.
    bulge      extra top height at the centre (pillowy slices).
    split_edge return (faces_obj, rim_band_obj) instead of one object, so the rim can be its
               own part/colour (reads as an outline between overlapping slices).
    rim_on_top with split_edge, the outermost ring of top quads (last inner ring -> edge) also
               goes to the rim part (roast-beef crust, casing).
    """
    outline = ccw(list(outline))
    zfn = zfn or (lambda x, y, s, i: 0.0)
    N = len(outline)
    if center is None:
        cx = sum(p[0] for p in outline) / N
        cy = sum(p[1] for p in outline) / N
    else:
        cx, cy = center
    e = thickness * edge

    def at(i, s):
        ox, oy = outline[i]
        return cx + (ox - cx) * s, cy + (oy - cy) * s

    def s_inset(i, d):
        ox, oy = outline[i]
        L = math.hypot(ox - cx, oy - cy) or 1.0
        return max(0.05, 1.0 - d / L)

    verts = []
    rings = []
    for s in inner:
        ring = []
        for i in range(N):
            x, y = at(i, s)
            ring.append(len(verts))
            verts.append((x, y, zfn(x, y, s, i) + thickness + bulge * (1 - s * s)))
        rings.append(ring)
    top_edge = []
    for i in range(N):
        s = s_inset(i, e * 0.8) if round_edge else 1.0
        x, y = at(i, s)
        top_edge.append(len(verts))
        verts.append((x, y, zfn(x, y, s, i) + thickness - (e * 0.15 if round_edge else 0)))
    band = [top_edge]
    if round_edge and e > 0:
        ring = []
        for i in range(N):
            x, y = at(i, 1.0)
            ring.append(len(verts))
            verts.append((x, y, zfn(x, y, 1.0, i) + thickness * 0.5))
        band.append(ring)
    bot_edge = []
    for i in range(N):
        s = s_inset(i, e * 0.8) if round_edge else 1.0
        x, y = at(i, s)
        bot_edge.append(len(verts))
        verts.append((x, y, zfn(x, y, s, i) + (e * 0.15 if round_edge else 0)))
    band.append(bot_edge)

    face_f, edge_f = [], []
    tc = len(verts)
    verts.append((cx, cy, zfn(cx, cy, 0.0, 0) + thickness + bulge))
    tops = rings + [top_edge]
    for i in range(N):
        face_f.append((tc, tops[0][i], tops[0][(i + 1) % N]))
    for k, (ra, rb) in enumerate(zip(tops[:-1], tops[1:])):
        dest = edge_f if (rim_on_top and k == len(tops) - 2) else face_f
        for i in range(N):
            j = (i + 1) % N
            dest.append((ra[i], rb[i], rb[j], ra[j]))
    for ra, rb in zip(band[:-1], band[1:]):
        for i in range(N):
            j = (i + 1) % N
            edge_f.append((ra[i], rb[i], rb[j], ra[j]))
    bc = len(verts)
    verts.append((cx, cy, zfn(cx, cy, 0.0, 0)))
    for i in range(N):
        face_f.append((bc, bot_edge[(i + 1) % N], bot_edge[i]))
    if not split_edge:
        return mesh_obj(name, verts, face_f + edge_f, recalc=False)
    return (mesh_obj(name, verts, face_f, recalc=False),
            mesh_obj(name + "Edge", verts, edge_f, recalc=False))


def _grid_coords(count: int, rim: float | None):
    if not rim:
        return [-1 + 2 * i / (count - 1) for i in range(count)]
    inner = [-(1 - rim) + 2 * (1 - rim) * i / (count - 3) for i in range(count - 2)]
    return [-1.0] + inner + [1.0]


def grid_sheet(name: str, a: float, b: float, nu: int, nv: int, thick: float, zfn=None, n: float = 2.0,
               wob=None, round_edge: float = 0.45, split_edge: bool = False, top_only_fn=None,
               rim: float | None = None, rim_on_top: bool = False):
    """Grid-topology slab mapped onto a (super)ellipse a x b (n = 2 disc, larger n = squarer).
    Unlike `sheet`, the top can ripple/fold anywhere (cheese drape, rippled deli slices).

    zfn(x, y, r) -> bottom height (r = 0 centre .. 1 rim, square-ring distance).
    wob(theta)   -> radial multiplier on the outline (ruffled / frilly edges).
    top_only_fn(x, y, r) -> extra height added to the top surface only.
    The bottom is a fan to the centre (it lies on the layer below), the rim is a rounded band.
    rim          width of the outermost grid ring as a fraction (thin crust/casing ring).
    rim_on_top   with split_edge, the outermost ring of TOP quads also goes to the edge part.
    """
    us, vs = _grid_coords(nu, rim), _grid_coords(nv, rim)
    zfn = zfn or (lambda x, y, r: 0.0)
    top_only_fn = top_only_fn or (lambda x, y, r: 0.0)
    P = {}
    for i in range(nu):
        for j in range(nv):
            u, v = us[i], vs[j]
            linf = max(abs(u), abs(v))
            ln = (abs(u) ** n + abs(v) ** n) ** (1 / n) if linf > 0 else 1.0
            sc = linf / ln if linf > 0 else 0.0
            x, y = a * u * sc, b * v * sc
            if wob and linf > 0:
                th = math.atan2(v, u)
                w = wob(th)
                x *= 1 + (w - 1) * linf ** 2
                y *= 1 + (w - 1) * linf ** 2
            P[(i, j)] = (x, y, linf)
    loop = [(i, 0) for i in range(nu - 1)] + [(nu - 1, j) for j in range(nv - 1)] + \
           [(i, nv - 1) for i in range(nu - 1, 0, -1)] + [(0, j) for j in range(nv - 1, 0, -1)]
    verts, face_f, edge_f = [], [], []
    top = {}
    for key, (x, y, r) in P.items():
        top[key] = len(verts)
        verts.append((x, y, zfn(x, y, r) + thick + top_only_fn(x, y, r)))
    for i in range(nu - 1):
        for j in range(nv - 1):
            q = (top[(i, j)], top[(i + 1, j)], top[(i + 1, j + 1)], top[(i, j + 1)])
            outer = i == 0 or j == 0 or i == nu - 2 or j == nv - 2
            (edge_f if (rim_on_top and outer) else face_f).append(q)
    L = len(loop)
    e = thick * round_edge
    mid, bot = [], []
    for k, key in enumerate(loop):
        x, y, r = P[key]
        xa, ya, _ = P[loop[k - 1]]
        xb, yb, _ = P[loop[(k + 1) % L]]
        tx, ty = xb - xa, yb - ya
        tl = math.hypot(tx, ty) or 1.0
        nx, ny = ty / tl, -tx / tl          # outward normal of a CCW loop
        zb = zfn(x, y, r)
        mid.append(len(verts))
        verts.append((x + nx * e, y + ny * e, zb + thick * 0.5))
        bot.append(len(verts))
        verts.append((x, y, zb))
    tl_ = [top[key] for key in loop]
    for ra, rb in ((tl_, mid), (mid, bot)):
        for k in range(L):
            m = (k + 1) % L
            edge_f.append((ra[k], rb[k], rb[m], ra[m]))
    cx, cy, _ = P[(nu // 2, nv // 2)]
    bc = len(verts)
    verts.append((cx, cy, zfn(cx, cy, 0.0) + 0.002))
    for k in range(L):
        face_f.append((bc, bot[(k + 1) % L], bot[k]))
    if not split_edge:
        return mesh_obj(name, verts, face_f + edge_f, recalc=False)
    return (mesh_obj(name, verts, face_f, recalc=False),
            mesh_obj(name + "Edge", verts, edge_f, recalc=False))


def drape(obj, fn):
    """World-space vertex deformation: fn(Vector) -> Vector (applied after transforms)."""
    ns.apply_all(obj)
    for v in obj.data.vertices:
        v.co = fn(v.co.copy())
    obj.data.update()
    return obj


def overhang_droop(k: float = 0.35, kx: float = 0.25):
    """Fillings sag a little where they hang past the roll's edges."""
    def f(co):
        dy = max(0.0, abs(co.y) - ROLL_B)
        dx = max(0.0, abs(co.x) - ROLL_A + 0.05)
        co.z -= k * dy + kx * dx
        return co
    return f


def folded_slice(name: str, R: float, thick: float, ruffles: int = 5, ruffle_amp: float = 0.02,
                 seed: int = 1, Nc: int = 15, Ns: int = 4, wobble: float = 0.02, fold_lift: float = 0.012,
                 split_edge: bool = True):
    """A round deli slice folded in half: a half-moon with the fold along local X (y = 0) and the
    ruffled round edge toward local -Y. Two plies thick (thick = total)."""
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 6.28)
    pts, kinds = [], []
    for k in range(Nc):
        th = math.pi + math.pi * k / (Nc - 1)
        r = R * (1 + wobble * math.sin(3 * th + ph) + rnd.uniform(-wobble, wobble) * 0.5)
        pts.append((r * math.cos(th), r * math.sin(th) * 0.98))
        kinds.append(th)
    for k in range(1, Ns + 1):
        u = k / (Ns + 1)
        x = R * (1 - 2 * u)
        pts.append((x, 0.02 * R * math.sin(math.pi * u)))
        kinds.append(None)

    def zfn(x, y, s, i):
        th = kinds[i]
        z = 0.0
        if th is not None:
            edge = math.sin(th - math.pi) ** 0.5  # 0 at the fold ends, 1 at the middle of the arc
            z += ruffle_amp * math.sin(ruffles * (th - math.pi) + ph) * (s ** 2) * (0.35 + 0.65 * edge)
        z += fold_lift * (1 - smooth(abs(y) / (0.35 * R)))
        return z

    return sheet(name, pts, thick, zfn=zfn, center=(0.0, -0.42 * R), inner=(0.55,), edge=0.55,
                 split_edge=split_edge)


def ribbon_solid(name: str, path, widths, thick, up=None, round_sides: bool = True):
    """A flat ribbon solid along a 3D polyline `path` (list of (x, y, z)), cross-section
    width w (per point) x thickness `thick` (scalar or per point). The ribbon's flat side
    faces `up` (default +Z). Rounded long edges when round_sides."""
    up = Vector(up or (0, 0, 1))
    n = len(path)
    th = thick if isinstance(thick, (list, tuple)) else [thick] * n
    rings = []
    for k in range(n):
        p = Vector(path[k])
        t = (Vector(path[min(k + 1, n - 1)]) - Vector(path[max(k - 1, 0)])).normalized()
        side = t.cross(up).normalized()
        nrm = side.cross(t).normalized()
        w, h = widths[k] / 2, th[k] / 2
        if round_sides:
            prof = [(-w, -h), (-w * 0.6, -h * 1.0), (w * 0.6, -h), (w, -h * 0.0 - h * 0.0), (w, 0.0),
                    (w * 0.6, h), (-w * 0.6, h), (-w, 0.0)]
            prof = [(-w * 0.85, -h), (w * 0.85, -h), (w, 0.0), (w * 0.85, h), (-w * 0.85, h), (-w, 0.0)]
        else:
            prof = [(-w, -h), (w, -h), (w, h), (-w, h)]
        rings.append([tuple(p + side * a + nrm * (b + h)) for a, b in prof])
    return loft(name, rings, cap_start="ngon", cap_end="ngon")


# --------------------------------------------------------------------------------------
# surface projection (scores, cracks, flakes on bread)
# --------------------------------------------------------------------------------------

def bvh(obj) -> BVHTree:
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = ev.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(obj.matrix_world)
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    ev.to_mesh_clear()
    return tree


def hit(tree: BVHTree, x: float, y: float, z0: float = 20.0):
    loc, nor, _, _ = tree.ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)))
    return loc, nor


def surface_ribbon(name: str, tree: BVHTree, center2d, widths, lift: float, depth: float = 0.02):
    """A thin strip draped on a surface (found by ray-casting straight down): sits `lift` above
    it, extends `depth` into it. center2d = [(x, y)] polyline, widths per point."""
    n = len(center2d)
    top, bot = [], []
    for k in range(n):
        x, y = center2d[k]
        xa, ya = center2d[max(k - 1, 0)]
        xb, yb = center2d[min(k + 1, n - 1)]
        tx, ty = xb - xa, yb - ya
        L = math.hypot(tx, ty) or 1.0
        sx, sy = -ty / L, tx / L
        rowt, rowb = [], []
        for f in (-1.0, 0.0, 1.0):
            px, py = x + sx * widths[k] / 2 * f, y + sy * widths[k] / 2 * f
            loc, nor = hit(tree, px, py)
            if loc is None:
                loc, nor = Vector((px, py, 0)), Vector((0, 0, 1))
            edge_drop = 0.6 if f != 0 else 1.0
            rowt.append(tuple(loc + nor * (lift * edge_drop)))
            rowb.append(tuple(loc - nor * depth))
        top.append(rowt)
        bot.append(rowb)
    verts = []
    idx = {}
    for k in range(n):
        for c in range(3):
            idx[("t", k, c)] = len(verts)
            verts.append(top[k][c])
            idx[("b", k, c)] = len(verts)
            verts.append(bot[k][c])
    faces = []
    for k in range(n - 1):
        for c in range(2):
            faces.append((idx[("t", k, c)], idx[("t", k, c + 1)], idx[("t", k + 1, c + 1)], idx[("t", k + 1, c)]))
            faces.append((idx[("b", k, c)], idx[("b", k + 1, c)], idx[("b", k + 1, c + 1)], idx[("b", k, c + 1)]))
        for c in (0, 2):
            faces.append((idx[("t", k, c)], idx[("t", k + 1, c)], idx[("b", k + 1, c)], idx[("b", k, c)]))
    for k in (0, n - 1):
        faces.append((idx[("t", k, 0)], idx[("t", k, 1)], idx[("t", k, 2)], idx[("b", k, 2)], idx[("b", k, 1)], idx[("b", k, 0)]))
    return mesh_obj(name, verts, faces)


def place_on(obj, tree: BVHTree, x: float, y: float, sink: float = 0.0, spin: float = 0.0):
    """Move/rotate an object (modelled at the origin, Z up) so it sits on the surface at (x, y)."""
    loc, nor = hit(tree, x, y)
    if loc is None:
        return obj
    q = Vector((0, 0, 1)).rotation_difference(nor)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = q @ Matrix.Rotation(math.radians(spin), 4, "Z").to_quaternion()
    obj.location = loc - nor * sink
    return obj


# --------------------------------------------------------------------------------------
# bread (sub roll halves)
# --------------------------------------------------------------------------------------

def roll_ring(d: float, z: float, N: int = 32, lump=None, n: float = ROLL_EXP):
    """Plan outline of the roll inset by d, at height z."""
    pts = []
    for (x, y) in superellipse(ROLL_A - d, ROLL_B - d, n, N):
        zz = z + (lump(x, y, z) if lump else 0.0)
        pts.append((x, y, zz))
    return pts


def dome_profile(base_z: float, top_z: float, steps=(0, 14, 28, 42, 56, 70, 84), m: float = 2.4,
                 inset0: float = 0.0):
    """(inset, z) pairs for a rounded dome cross-section: half-width ROLL_B at base_z -> crest."""
    out = []
    for deg in steps:
        ph = math.radians(deg)
        y = (ROLL_B - inset0) * spow(math.cos(ph), 2 / m)
        z = base_z + (top_z - base_z) * spow(math.sin(ph), 2 / m)
        out.append((ROLL_B - y, z))
    return out


def build_bread_bottom(crust_col: str, crumb_col: str, N: int = 28, lump=None, pores=None):
    """Bottom half: crust boat (recolor toast) + crumb slab whose top face is exactly Z=0.30."""
    H = BOTTOM_H
    rim_z = H - 0.055
    prof = [(0.15, 0.0), (0.06, 0.012), (0.02, 0.045), (0.0, 0.11), (0.002, 0.19), (0.012, rim_z)]
    rings = [roll_ring(d, z, N, lump if z > 0.02 else None) for d, z in prof]
    crust = loft("Crust", rings, cap_start="fan", cap_end="ngon", start_center=(0, 0, 0.0))
    ns.tag(crust, "Crust", crust_col, "SmoothPlastic", smooth_angle=70, recolor="toast")

    ci = 0.026
    cprof = [(ci + 0.006, rim_z - 0.03), (ci, H - 0.03), (ci + 0.008, H - 0.006), (ci + 0.03, H)]
    crings = [roll_ring(d, z, N) for d, z in cprof]
    crumb = loft("Crumb", crings, cap_start="ngon", cap_end="fan", end_center=(0, 0, H + 0.003))
    ns.tag(crumb, "Crumb", crumb_col, "SmoothPlastic", smooth_angle=60)
    if pores:
        bread_pores(crumb, shade(crumb_col, 0.8), big=pores == "big")
    return crust, crumb


def shade(hexcol: str, f: float) -> str:
    r, g, b = (int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))


def bread_pores(crumb, col: str, big: bool = False, seed: int = 5):
    """A few shallow air pockets on the cut crumb face so it reads as bread, not frosting."""
    rnd = random.Random(seed)
    spots = []
    for i in range(10):
        spots.append((-0.82 + 1.64 * (i + rnd.uniform(0.1, 0.9)) / 10, rnd.uniform(-0.22, 0.22)))
    sz = (0.066, 0.042, 0.005) if big else (0.048, 0.03, 0.005)
    return flecks_on("Pores", [crumb], spots, col, "SmoothPlastic", size=sz, verts=6, seed=seed, sink=0.1,
                     smooth_angle=60)


def build_bread_top(crust_col: str, crumb_col: str, N: int = 28, lump=None, height: float = TOP_H,
                    steps=(0, 16, 32, 48, 64, 80)):
    """Top half (dome): crumb band at the cut (Z 0..~0.06) + crust dome (recolor toast)."""
    base = 0.055
    prof = [(0.006, base)] + dome_profile(base + 0.025, height, steps=steps)
    rings = [roll_ring(d, z, N, lump) for d, z in prof]
    crust = loft("Crust", rings, cap_start="ngon", cap_end="fan",
                 end_center=(0, 0, height + (lump(0, 0, height) if lump else 0)))
    ns.tag(crust, "Crust", crust_col, "SmoothPlastic", smooth_angle=70, recolor="toast")

    ci = 0.022
    cprof = [(ci + 0.025, 0.0), (ci + 0.004, 0.006), (ci, base + 0.03)]
    crings = [roll_ring(d, z, N) for d, z in cprof]
    crumb = loft("Crumb", crings, cap_start="fan", cap_end="ngon", start_center=(0, 0, 0.0))
    ns.tag(crumb, "Crumb", crumb_col, "SmoothPlastic", smooth_angle=60)
    return crust, crumb


def roll_lump(seed: int = 1, amp: float = 0.012):
    """Gentle low-frequency lumpiness for the crust (organic, not noisy)."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(4)]

    def f(x, y, z):
        w = smooth(z / 0.2)
        return amp * w * (math.sin(2.3 * x + ph[0]) * 0.6 + math.sin(4.1 * x + ph[1]) * 0.4
                          + math.sin(5.0 * y + ph[2]) * 0.3)
    return f


# --------------------------------------------------------------------------------------
# meta / run helpers
# --------------------------------------------------------------------------------------

def meta(ingredient: str, layer_height: float, layer_count: int = 1, layer_spacing: float = 0.0, **extra) -> dict:
    m = {"ingredient": ingredient, "layer_height": round(layer_height, 3),
         "layer_count": int(layer_count), "layer_spacing": round(layer_spacing, 3)}
    m.update(extra)
    return m


def run(build, asset: str, meta_: dict | None = None, icon=None, pivot=(0.0, 0.0, 0.0), group: str = GROUP,
        **export_kw):
    """Standard A_food entry: preview (+ export with NS_EXPORT=1, + icon with NS_ICON=1).

    pivot  defaults to the contract origin (0, 0, 0): bottom-centre of the layer even when parts
           (melted drips, flecks) poke below or the outline is asymmetric. Pass None for nslib's
           bounding-box default.
    icon   (icon_name, icon_build_fn, render_icon_kwargs) or None.
    group  ReplicatedStorage.Assets.<group> (default "Food"; Kitchen_ assets pass "Kitchen").
    Env:   NS_DRAFT=1 -> quick low-sample render to the scratch drafts dir only.
           NS_ICON_DRAFT=1 -> quick icon test render to the drafts dir (no manifest write).
           NS_ONLY_ICON=1 -> skip preview/export, just the icon.
    """
    kw = dict(export_kw)
    if meta_ is not None:
        kw["meta"] = meta_
    if pivot is not None:
        kw["pivot"] = pivot
    if os.environ.get("NS_DRAFT") == "1":
        draft(build, asset)
        return
    if os.environ.get("NS_ICON_DRAFT") == "1":
        if icon:
            name, fn, rkw = icon
            draft_icon(fn, name, **(rkw or {}))
        return
    if os.environ.get("NS_ONLY_ICON") != "1":
        ns.run_main(build, asset, BATCH, group, **kw)
    if icon and os.environ.get("NS_ICON") == "1":
        name, fn, rkw = icon
        ns.reset()
        fn()
        print(f"[{asset}] icon:", ns.render_icon(name, "ingredients", **(rkw or {})))


def draft_icon(fn, name: str, yaw=-35.0, pitch=28.0, fov=24.0, margin=1.02, res=256, samples=12, **_):
    """Low-sample stand-in for ns.render_icon (same camera and lights) that writes only to the
    drafts dir — for framing checks before the real icon render."""
    ns.reset()
    fn()
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
    print(out)
    return out


def draft(build, name: str, res: int = 384, samples: int = 12):
    """Quick low-res review render into the scratch previews (used while iterating)."""
    ns.reset()
    build()
    print(f"[{name}] triangles: {ns.tri_count()}")
    out = ns.render_preview(name, out_dir=DRAFT_DIR, res=res, samples=samples)
    print(out)
    return out


def part_tris() -> dict:
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    for o in ns._tagged_objects():
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        out[o.name] = len(me.loop_triangles)
        o.evaluated_get(dg).to_mesh_clear()
    return out


# --------------------------------------------------------------------------------------
# the four breads (shared by the eight Food_<Bread>_Bottom/_Top scripts and the icons)
# --------------------------------------------------------------------------------------

BREADS = {
    # id: crust, crumb, extra-feature colour, lump seed/amp
    "white_sub": dict(crust="#E9A957", crumb="#FFF2D6", extra="#F6CF8E", lump=(3, 0.010)),
    "wheat_sub": dict(crust="#8C5A33", crumb="#D6AE7C", extra="#EED9A8", lump=(5, 0.012)),
    "sourdough": dict(crust="#C98B48", crumb="#F5E7C8", extra="#F3DFB6", lump=(7, 0.016)),
    "black_bread": dict(crust="#2A2230", crumb="#5E4475", extra="#8C55C4", lump=(11, 0.024)),
}


def _bread_scores(tree, col):
    """Sourdough: three diagonal scores, each a pale floury slash with a soft ear."""
    objs = []
    for k, x0 in enumerate((-0.6, 0.0, 0.6)):
        pts, ws = [], []
        n = 5
        for i in range(n):
            t = i / (n - 1)
            x = x0 - 0.17 + 0.34 * t
            y = -0.22 + 0.44 * t
            pts.append((x, y))
            ws.append(0.02 + 0.10 * math.sin(math.pi * t) ** 0.7)
        objs.append(surface_ribbon(f"Score{k}", tree, pts, ws, lift=0.022, depth=0.03))
    s = ns.join(objs, "Scores")
    ns.tag(s, "Scores", col, "SmoothPlastic", smooth_angle=60)
    return s


def _bread_split(tree, col):
    """White sub: one long, shallow lengthwise split along the crest, lighter where it opened."""
    n = 8
    pts, ws = [], []
    for i in range(n):
        t = i / (n - 1)
        pts.append((-0.78 + 1.56 * t, 0.015 * math.sin(3.0 * t)))
        ws.append(0.012 + 0.05 * math.sin(math.pi * t) ** 0.6)
    s = surface_ribbon("Split", tree, pts, ws, lift=0.01, depth=0.03)
    ns.tag(s, "Split", col, "SmoothPlastic", smooth_angle=60)
    return s


def _bread_cracks(tree, col):
    """Black bread: irregular fissures splitting the crust, showing the purple crumb."""
    rnd = random.Random(21)
    objs = []
    # (start x, end x, y, points, max width)
    cracks = [(-0.92, -0.18, -0.04, 7, 0.06), (0.05, 0.86, 0.05, 7, 0.065), (-0.5, -0.3, 0.02, 3, 0.03),
              (0.42, 0.6, -0.02, 3, 0.03)]
    for k, (x0, x1, y0, n, wmax) in enumerate(cracks):
        pts, ws = [], []
        y = y0
        for i in range(n):
            t = i / (n - 1)
            x = x0 + (x1 - x0) * (t + rnd.uniform(-0.04, 0.04) * (0 < i < n - 1))
            y += rnd.uniform(-0.05, 0.05)
            if k >= 2:      # short branches angle off the main cracks
                y = y0 + (0.14 if k == 2 else -0.14) * t
            pts.append((x, y))
            ws.append(0.006 + wmax * math.sin(math.pi * t) ** 0.6 * rnd.uniform(0.6, 1.0))
        objs.append(surface_ribbon(f"Crack{k}", tree, pts, ws, lift=0.004, depth=0.03))
    c = ns.join(objs, "Cracks")
    ns.tag(c, "Cracks", col, "SmoothPlastic", smooth_angle=None)
    return c


def _bread_oats(tree, col):
    """Wheat sub: rolled-oat flakes scattered along the crest."""
    rnd = random.Random(9)
    flakes = []
    spots = [(-0.82, -0.07), (-0.58, 0.1), (-0.36, -0.1), (-0.12, 0.06), (0.1, -0.09), (0.32, 0.11),
             (0.55, -0.05), (0.78, 0.08), (-0.2, 0.22), (0.45, 0.24)]
    for i, (x, y) in enumerate(spots):
        f = ns.cyl(1.0, 1.0, verts=6, bevel=0, name=f"Oat{i}")
        f.scale = (0.055, 0.036, 0.012)
        ns.apply_all(f)
        place_on(f, tree, x, y, sink=0.0, spin=rnd.uniform(0, 180))
        ns.apply_all(f)
        flakes.append(f)
    o = ns.join(flakes, "Oats")
    ns.tag(o, "Oats", col, "SmoothPlastic", smooth_angle=70)
    return o


def build_bread(kind: str, half: str):
    """Build Food_<Bread>_<Half> parts in the scene (half = "bottom" | "top")."""
    b = BREADS[kind]
    seed, amp = b["lump"]
    if half == "bottom":
        return build_bread_bottom(b["crust"], b["crumb"], lump=roll_lump(seed, amp * 0.6),
                                  pores="big" if kind == "sourdough" else "small")
    crust, crumb = build_bread_top(b["crust"], b["crumb"], lump=roll_lump(seed + 1, amp))
    if kind == "white_sub":
        _bread_split(bvh(crust), b["extra"])
    elif kind == "sourdough":
        _bread_scores(bvh(crust), b["extra"])
    elif kind == "black_bread":
        _bread_cracks(bvh(crust), b["extra"])
    elif kind == "wheat_sub":
        _bread_oats(bvh(crust), b["extra"])
    return crust, crumb


def bread_meta(kind: str, half: str) -> dict:
    return meta(kind, BOTTOM_H if half == "bottom" else TOP_H)


def build_open_roll(kind: str, open_deg: float = 0.0, gap: float = 0.0):
    """Icon helper: bottom half + top half (optionally hinged open at the back edge)."""
    before = set(ns._tagged_objects())
    build_bread(kind, "bottom")
    for o in ns._tagged_objects():
        if o not in before:
            o["ns_part"] = o["ns_part"] + "Bottom"
            o.name = o["ns_part"]
    before = set(ns._tagged_objects())
    build_bread(kind, "top")
    top = [o for o in ns._tagged_objects() if o not in before]
    hinge = Vector((0, ROLL_B - 0.03, BOTTOM_H + gap))
    R = Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-open_deg), 4, "X") @ Matrix.Translation(-hinge)
    for o in top:
        o["ns_part"] = o["ns_part"] + "Top"
        o.name = o["ns_part"]
        o.matrix_world = R @ Matrix.Translation((0, 0, BOTTOM_H + gap)) @ o.matrix_world
    return top


# --------------------------------------------------------------------------------------
# deli meats
# --------------------------------------------------------------------------------------

def deli_layer(meat_col: str, edge_col: str, R: float = 0.47, thick: float = 0.045, seed: int = 1,
               xs=(-0.7, -0.35, 0.0, 0.35, 0.7), ruffle_amp: float = 0.022, Nc: int = 13, Ns: int = 3,
               names=("Meat", "MeatEdge"), droop: bool = True):
    """Folded half-moon slices alternating front/back along the roll (Subway style): round
    ruffled edges hang just past the long sides, folds meet along the middle."""
    faces, edges = [], []
    for k, x in enumerate(xs):
        front = k % 2 == 0
        f, e = folded_slice(f"S{k}", R, thick, seed=seed + k, ruffle_amp=ruffle_amp, Nc=Nc, Ns=Ns,
                            ruffles=4 + (k % 2))
        yaw = (0.0 if front else 180.0) + (k * 7 % 9 - 4)
        for o in (f, e):
            o.rotation_euler = (math.radians(-3 if front else 3), 0, math.radians(yaw))
            o.location = (x, 0.035 if front else -0.035, 0.004 + 0.011 * (k % 2) + 0.003 * k)
            if droop:
                drape(o, overhang_droop())
            else:
                ns.apply_all(o)
        faces.append(f)
        edges.append(e)
    m = ns.join(faces, names[0])
    ns.tag(m, names[0], meat_col, "SmoothPlastic", smooth_angle=75)
    ed = ns.join(edges, names[1])
    ns.tag(ed, names[1], edge_col, "SmoothPlastic", smooth_angle=75)
    return m, ed


def under_bread(kind: str = "white_sub"):
    """Draft helper: a bottom roll under the layer (context only, renamed so it never exports)."""
    before = set(ns._tagged_objects())
    build_bread(kind, "bottom")
    for o in ns._tagged_objects():
        if o not in before:
            o["ns_part"] = "Ctx" + o["ns_part"]
            o.name = o["ns_part"]
            o.location.z -= BOTTOM_H


def rippled_slices(meat_col: str, edge_col: str, *, xs=(-0.66, 0.0, 0.66), a: float = 0.46, b: float = 0.475,
                   thick: float = 0.045, amp: float = 0.03, wavelength: float = 0.42, nu: int = 9, nv: int = 6,
                   seed: int = 1, wob_amp: float = 0.04, wob_k: int = 6, names=("Meat", "MeatEdge"),
                   rim=None, rim_on_top=False, n: float = 2.0, cup: float = 0.02, yaws=(-5, 1, 6),
                   tilt=(-4, 0, 4), smooth_angle: float = 75.0):
    """Deli slices gathered into soft folds (ripples across X), overlapping along the roll,
    edges hanging just past the long sides. Returns (meat_part, edge_part)."""
    rnd = random.Random(seed)
    F, E = [], []
    for k, x0 in enumerate(xs):
        ph = rnd.uniform(0, 6.28)
        sk = rnd.uniform(-0.6, 0.6)

        def zfn(x, y, r, ph=ph, sk=sk):
            return (amp * math.sin(2 * math.pi * (x + sk * y) / wavelength + ph) * (0.35 + 0.65 * r)
                    + cup * r * r)

        def wob(t, ph=ph):
            return 1 + wob_amp * math.sin(wob_k * t + ph)
        f, e = grid_sheet(f"R{k}", a, b, nu, nv, thick, zfn=zfn, wob=wob, split_edge=True, rim=rim,
                          rim_on_top=rim_on_top, n=n)
        for o in (f, e):
            o.location = (x0, 0.0, 0.004 + 0.013 * k)
            o.rotation_euler = (0, math.radians(tilt[k % len(tilt)]), math.radians(yaws[k % len(yaws)]))
            drape(o, overhang_droop())
        F.append(f)
        E.append(e)
    m = ns.join(F, names[0])
    ns.tag(m, names[0], meat_col, "SmoothPlastic", smooth_angle=smooth_angle)
    d = ns.join(E, names[1])
    ns.tag(d, names[1], edge_col, "SmoothPlastic", smooth_angle=smooth_angle)
    return m, d


def check_bounds(asset: str, objs=None, layer: bool = True):
    """Print the bbox and flag contract violations (overhang > 0.08 for fillings)."""
    lo, hi = ns.bbox_world(objs or ns._tagged_objects())
    msg = f"[{asset}] bbox x {lo.x:.3f}..{hi.x:.3f}  y {lo.y:.3f}..{hi.y:.3f}  z {lo.z:.3f}..{hi.z:.3f}"
    if layer and (max(-lo.x, hi.x) > MAX_X + 1e-3 or max(-lo.y, hi.y) > MAX_Y + 1e-3):
        msg += "   <-- OVERHANG EXCEEDS CONTRACT"
    print(msg)
    return lo, hi


def polar_slices(meat_col: str, edge_col: str, *, xs=(-0.66, 0.0, 0.66), a: float = 0.46, b: float = 0.47,
                 thick: float = 0.045, amp: float = 0.03, wavelength: float = 0.45, N: int = 24,
                 inner=(0.35, 0.7), seed: int = 1, wob_amp: float = 0.035, wob_k: int = 5,
                 names=("Meat", "MeatEdge"), rim_on_top: bool = False, cup: float = 0.012, yaws=(-6, 2, 7),
                 tilt=(-3, 0, 3), zstep: float = 0.008, smooth_angle: float = 80.0, droop: bool = True,
                 pleat: float = 1.0):
    """Like rippled_slices but on the polar `sheet` topology: smooth outlines for the budget.
    pleat < 1 sharpens the fold valleys (0.5 = pressed pleats); 1.0 = plain |sin| folds."""
    rnd = random.Random(seed)
    F, E = [], []
    for k, x0 in enumerate(xs):
        ph = rnd.uniform(0, 6.28)
        ph2 = rnd.uniform(0, 6.28)
        sk = rnd.uniform(-0.5, 0.5)
        outline = []
        for i in range(N):
            t = 2 * math.pi * i / N
            w = 1 + wob_amp * math.sin(wob_k * t + ph2) + wob_amp * 0.4 * math.sin((wob_k + 3) * t)
            outline.append((a * w * math.cos(t), b * w * math.sin(t)))

        def zfn(x, y, s, i, ph=ph, sk=sk):
            u = math.pi * (x + sk * y) / wavelength + ph
            # pleat profile: rounded crests, crisp valleys -> reads as folds, not ripples
            fold = 2.0 * abs(math.sin(u)) ** pleat - 1.0
            return amp * fold * (0.3 + 0.7 * s) + cup * s * s
        f, e = sheet(f"P{k}", outline, thick, zfn=zfn, center=(0, 0), inner=inner, edge=0.5,
                     split_edge=True, rim_on_top=rim_on_top)
        for o in (f, e):
            o.location = (x0, 0.0, 0.004 + zstep * k)
            o.rotation_euler = (0, math.radians(tilt[k % len(tilt)]), math.radians(yaws[k % len(yaws)]))
            if droop:
                drape(o, overhang_droop())
            else:
                ns.apply_all(o)
        F.append(f)
        E.append(e)
    m = ns.join(F, names[0])
    ns.tag(m, names[0], meat_col, "SmoothPlastic", smooth_angle=smooth_angle)
    d = ns.join(E, names[1])
    ns.tag(d, names[1], edge_col, "SmoothPlastic", smooth_angle=smooth_angle)
    return m, d


def strip_on(name: str, path, side_offset: float, width: float, lift: float):
    """Single-sided flat strip lying on top of a ribbon path (bacon fat stripes, sauce shine):
    offset sideways from the path centre-line, raised `lift` along the ribbon's up-normal."""
    up = Vector((0, 0, 1))
    n = len(path)
    verts, faces = [], []
    for k in range(n):
        p = Vector(path[k])
        t = (Vector(path[min(k + 1, n - 1)]) - Vector(path[max(k - 1, 0)])).normalized()
        side = t.cross(up).normalized()
        nrm = side.cross(t).normalized()
        c = p + side * side_offset + nrm * lift
        verts.append(tuple(c - side * width / 2))
        verts.append(tuple(c + side * width / 2))
    for k in range(n - 1):
        a, b, c, d = 2 * k, 2 * k + 1, 2 * k + 3, 2 * k + 2
        faces.append((a, d, c, b))
    obj = mesh_obj(name, verts, faces, recalc=False)
    # make sure the strip faces up
    me = obj.data
    me.update()
    if sum(p.normal.z for p in me.polygons) < 0:
        for p in me.polygons:
            p.flip()
    return obj


def bacon_strips(meat_col="#B8432F", fat_col="#F5CBA3", ys=(-0.285, 0.0, 0.285), length=2.24,
                 width=0.27, thick=0.035, amp=0.024, wavelength=0.46, segs=18, seed=2, scale=1.0):
    """Crisp wavy bacon strips along X: meat ribbon + two lengthwise fat stripes on top."""
    rnd = random.Random(seed)
    meats, fats = [], []
    for k, y0 in enumerate(ys):
        ph = rnd.uniform(0, 6.28)
        ph2 = rnd.uniform(0, 6.28)
        L = length * rnd.uniform(0.95, 1.0)
        path, widths = [], []
        for i in range(segs + 1):
            t = i / segs
            x = -L / 2 + L * t
            a_ = amp * (0.8 + 0.4 * math.sin(3.1 * t + ph2))
            z = a_ * (1 + math.sin(2 * math.pi * x / wavelength + ph)) + 0.004 + 0.008 * k
            y = y0 + 0.025 * math.sin(2 * math.pi * x / 0.9 + ph2)
            path.append((x * scale, y * scale, z * scale))
            widths.append(width * scale * (0.92 + 0.08 * math.sin(7 * t + ph)))
        meats.append(ribbon_solid(f"BMeat{k}", path, widths, thick * scale, round_sides=False))
        fats.append(strip_on(f"BFat{k}a", path, width * scale * 0.33, width * scale * 0.2, thick * scale + 0.003))
        fats.append(strip_on(f"BFat{k}b", path, -width * scale * 0.08, width * scale * 0.11, thick * scale + 0.003))
    m = ns.join(meats, "Meat")
    ns.tag(m, "Meat", meat_col, "SmoothPlastic", smooth_angle=60)
    f = ns.join(fats, "Fat")
    ns.tag(f, "Fat", fat_col, "SmoothPlastic", smooth_angle=60)
    return m, f


def bvh_multi(targets) -> BVHTree:
    """BVH over several objects (world space)."""
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    for t in targets:
        ev = t.evaluated_get(dg)
        me = ev.to_mesh()
        tmp = bmesh.new()
        tmp.from_mesh(me)
        tmp.transform(t.matrix_world)
        m2 = bpy.data.meshes.new("_tmp")
        tmp.to_mesh(m2)
        tmp.free()
        bm.from_mesh(m2)
        bpy.data.meshes.remove(m2)
        ev.to_mesh_clear()
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    return tree


def flecks_on(name: str, targets, spots, col: str, mat: str = "Neon", size=(0.032, 0.022, 0.012), verts: int = 5,
              seed: int = 3, sink: float = 0.25, smooth_angle=None):
    """Small chips sitting on the top of `targets` (ray-cast down) — glowing flecks, pepper bits."""
    tree = bvh_multi(targets)
    rnd = random.Random(seed)
    objs = []
    for i, (x, y) in enumerate(spots):
        f = ns.cyl(1.0, 1.0, verts=verts, bevel=0, name=f"{name}{i}")
        sc = rnd.uniform(0.8, 1.2)
        f.scale = (size[0] * sc, size[1] * sc, size[2])
        ns.apply_all(f)
        place_on(f, tree, x, y, sink=size[2] * sink, spin=rnd.uniform(0, 180))
        ns.apply_all(f)
        objs.append(f)
    o = ns.join(objs, name)
    ns.tag(o, name, col, mat, smooth_angle=smooth_angle)
    return o


# --------------------------------------------------------------------------------------
# cheese
# --------------------------------------------------------------------------------------

def rounded_rect(w: float, h: float, r: float, corner_pts: int = 3, side_pts: int = 3, wob=None):
    """Rounded rectangle outline (CCW) with points spread so corners stay round."""
    pts = []
    cx, cy = w / 2 - r, h / 2 - r
    corners = [(cx, cy, 0), (-cx, cy, 90), (-cx, -cy, 180), (cx, -cy, 270)]
    for k, (ox, oy, a0) in enumerate(corners):
        for i in range(corner_pts):
            a = math.radians(a0 + 90 * (i + 0.5) / corner_pts)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
        nx, ny, _ = corners[(k + 1) % 4]
        ex = ox + r * math.cos(math.radians(a0 + 90))
        ey = oy + r * math.sin(math.radians(a0 + 90))
        fx = nx + r * math.cos(math.radians(a0 + 90))
        fy = ny + r * math.sin(math.radians(a0 + 90))
        for i in range(side_pts):
            t = (i + 0.5) / side_pts
            pts.append((ex + (fx - ex) * t, ey + (fy - ey) * t))
    if wob:
        pts = [(x * (1 + wob(math.atan2(y, x))), y * (1 + wob(math.atan2(y, x)))) for x, y in pts]
    return pts


def holes_cut(obj, holes, depth: float = 1.0, verts: int = 10):
    """Boolean round holes (x, y, rx, ry) straight through `obj` (Swiss cheese)."""
    cutters = []
    for i, (x, y, rx, ry) in enumerate(holes):
        c = ns.cyl(1.0, depth, loc=(x, y, 0), verts=verts, bevel=0, name=f"HoleCut{i}")
        c.scale = (rx, ry, 1)
        ns.apply_all(c)
        cutters.append(c)
    cut = ns.join(cutters, "HoleCutters")
    mod = obj.modifiers.new("Holes", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cut
    mod.solver = "EXACT"
    ns.apply_all(obj)
    bpy.data.objects.remove(cut, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def cheese_slices(col: str, edge_col: str, *, xs=(-0.68, 0.0, 0.68), size: float = 0.8, yaws=(9, -6, 12),
                  thick: float = 0.035, seed: int = 1, holes=None, names=("Cheese", "CheeseEdge"),
                  zstep: float = 0.012, droop: bool = True, tilt=(-3, 0, 3), corner_pts=3, side_pts=3):
    """Square deli cheese slices overlapping along the roll; corners overhang a touch and sag.
    holes: per-slice list of (x, y, rx, ry) in slice-local coordinates (Swiss)."""
    rnd = random.Random(seed)
    F, E = [], []
    for k, x0 in enumerate(xs):
        ph = rnd.uniform(0, 6.28)
        outline = rounded_rect(size, size, 0.07, corner_pts=corner_pts, side_pts=side_pts,
                               wob=lambda t, ph=ph: 0.012 * math.sin(3 * t + ph))

        def zfn(x, y, s, i, ph=ph):
            return 0.006 * math.sin(4 * x + ph) * s
        if holes:
            hl = [circle(1.0, 8, phase=0.3) for _ in holes[k % len(holes)]]
            hl = [[(hx + rx * px, hy + ry * py) for px, py in c] for c, (hx, hy, rx, ry) in zip(hl, holes[k % len(holes)])]
            f = holed_slab(f"C{k}", outline, hl, thick, zfn=lambda x, y, ph=ph: 0.006 * math.sin(4 * x + ph))
            parts = [f]
        else:
            parts = list(sheet(f"C{k}", outline, thick, zfn=zfn, center=(0, 0), inner=(0.4, 0.78), edge=0.45,
                               split_edge=True))
        for o in parts:
            o.location = (x0, 0.0, 0.003 + zstep * k)
            o.rotation_euler = (math.radians(tilt[k % len(tilt)] * 0.5), math.radians(tilt[k % len(tilt)]),
                                math.radians(yaws[k % len(yaws)]))
            drape(o, overhang_droop(k=0.6, kx=0.4)) if droop else ns.apply_all(o)
        F.append(parts[0])
        if len(parts) > 1:
            E.append(parts[1])
    m = ns.join(F, names[0])
    ns.tag(m, names[0], col, "SmoothPlastic", smooth_angle=70)
    out = [m]
    if E:
        d = ns.join(E, names[1])
        ns.tag(d, names[1], edge_col, "SmoothPlastic", smooth_angle=70)
        out.append(d)
    return out


def holed_slab(name: str, outline, holes, thick: float, zfn=None, round_out: float = 0.0, split_holes: bool = False):
    """Slab with through-holes (Swiss): clean scanline fill of the top/bottom faces, rounded
    outer rim, straight hole walls. holes = [[(x, y), ...], ...] (any winding)."""
    zfn = zfn or (lambda x, y: 0.0)
    outline = ccw(list(outline))
    bm = bmesh.new()

    def ring(pts, z, push=0.0):
        n = len(pts)
        out = []
        for i, (x, y) in enumerate(pts):
            if push:
                xa, ya = pts[i - 1]
                xb, yb = pts[(i + 1) % n]
                tx, ty = xb - xa, yb - ya
                L = math.hypot(tx, ty) or 1.0
                x, y = x + ty / L * push, y - tx / L * push
            out.append(bm.verts.new((x, y, z + zfn(x, y))))
        return out

    loops_top = [ring(outline, thick)] + [ring(ccw(h), thick) for h in holes]
    loops_bot = [ring(outline, 0.0)] + [ring(ccw(h), 0.0) for h in holes]
    mid = ring(outline, thick * 0.5, push=thick * round_out) if round_out else None

    def edges_of(vs):
        return [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]

    et = [e for lp in loops_top for e in edges_of(lp)]
    eb = [e for lp in loops_bot for e in edges_of(lp)]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=et)
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=eb)

    def wall(A, B):
        n = len(A)
        for i in range(n):
            j = (i + 1) % n
            try:
                bm.faces.new((A[i], B[i], B[j], A[j]))
            except ValueError:
                pass
    if mid:
        wall(loops_top[0], mid)
        wall(mid, loops_bot[0])
    else:
        wall(loops_top[0], loops_bot[0])
    nf = len(bm.faces)
    for t, b_ in zip(loops_top[1:], loops_bot[1:]):
        wall(t, b_)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if split_holes:
        bm.faces.ensure_lookup_table()
        hole_faces = [(tuple(v.co) for v in f.verts) for f in bm.faces[nf:]]
        hv, hf = [], []
        for f in bm.faces[nf:]:
            idx = []
            for v in f.verts:
                idx.append(len(hv))
                hv.append(tuple(v.co))
            hf.append(tuple(idx))
        bmesh.ops.delete(bm, geom=list(bm.faces[nf:]), context="FACES_ONLY")
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        obj = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(obj)
        return obj, mesh_obj(name + "Holes", hv, hf, recalc=False)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def teardrop(name: str, length: float, r: float, verts: int = 6, flat: float = 0.6):
    """A hanging drip (tip at -length), top at z=0, flattened along Y by `flat`."""
    prof = [(r * 1.1, 0.03), (r * 0.82, -0.3 * length), (r * 0.9, -0.62 * length), (r * 0.72, -0.9 * length),
            (0.0, -length)]
    o = ns.lathe(list(reversed(prof)), verts=verts, name=name)
    o.scale = (1, flat, 1)
    ns.apply_all(o)
    return o


MELT_LOBES = [(-90, 0.09, 22), (-45, 0.06, 14), (-135, 0.075, 16), (95, 0.08, 22), (55, 0.05, 13),
              (140, 0.065, 15), (0, 0.05, 20), (180, 0.06, 20)]
MELT_DRIPS = [(-91, 0.065), (-136, 0.05), (96, 0.058)]


def melted_sheet(name: str, col: str, *, N: int = 40, thick: float = 0.035, lobes=None, drips=None,
                 seed: int = 1, half=(1.12, 0.455), holes=None, smooth_angle: float = 80.0,
                 base_hang: float = 0.03, inner=(0.55, 0.86, 0.955)):
    """Melted cheese: one gooey sheet over the whole roll (bottom of the plateau at Z 0). Between
    lobes the edge just curls over the layer below (base_hang); rounded lobes
    (angle_deg, drop, width_deg) flow further down its sides; teardrop drips (angle_deg, length)
    hang from the deepest ones. Built on `sheet` (the hidden underside is a simple fan)."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    lobes = lobes or []
    drips = drips or []
    A, B = half
    s_hang = inner[-2]

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

    obj = sheet(name, outline, thick, zfn=zfn, center=(0, 0), inner=inner, edge=0.6)
    if holes:
        holes_cut(obj, holes, depth=0.3, verts=8)
    parts = [obj]
    for k, (ang, length) in enumerate(drips):
        t = math.radians(ang)
        i = min(range(N), key=lambda j: abs(math.atan2(math.sin(ts[j] - t), math.cos(ts[j] - t))))
        x, y = outline[i]
        z = zfn(x, y, 1.0, i) + 0.055
        d = teardrop(f"Drip{k}", length + 0.045, 0.048 + 0.008 * (k % 2), flat=0.5)
        d.location = (x * 1.004, y * 1.004, z)
        d.rotation_euler = (0, 0, math.atan2(y, x) - math.pi / 2)
        ns.apply_all(d)
        parts.append(d)
    out = ns.join(parts, name) if len(parts) > 1 else obj
    ns.tag(out, name, col, "SmoothPlastic", smooth_angle=smooth_angle)
    return out


CHEESES = {
    "cheddar": dict(col="#F7A01C", edge="#E3850F", melt="#F99B12"),
    "swiss": dict(col="#F7E6A2", edge="#E3CC7E", melt="#F9E28C"),
    "pepper_jack": dict(col="#F3E9C9", edge="#DCCFA8", melt="#F6E8BE", red="#D93A2B", green="#3F9A3A"),
}

SWISS_HOLES = [  # per slice, (x, y, rx, ry) in slice-local studs (slices are 0.8 square)
    [(-0.17, 0.13, 0.1, 0.092), (0.16, -0.12, 0.08, 0.08), (0.21, 0.22, 0.06, 0.058), (-0.13, -0.23, 0.066, 0.06)],
    [(0.14, 0.15, 0.094, 0.088), (-0.16, -0.1, 0.1, 0.094), (-0.2, 0.24, 0.054, 0.054), (0.22, -0.21, 0.06, 0.066)],
    [(-0.06, 0.17, 0.08, 0.08), (0.17, -0.06, 0.094, 0.094), (-0.19, -0.17, 0.074, 0.066), (0.25, 0.24, 0.048, 0.048)],
]


# --------------------------------------------------------------------------------------
# veggies
# --------------------------------------------------------------------------------------

def frilly_leaf(name: str, a: float, b: float, *, N: int = 44, frills: int = 13, amp_z: float = 0.035,
                amp_xy: float = 0.06, thick: float = 0.03, seed: int = 1, inner=(0.62,), lift: float = 0.0,
                cup: float = 0.03):
    """Lettuce leaf: elongated sheet with a ruffled, bumpy (frilly) edge that waves up and down."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(4)]
    out, angles = [], []
    for i in range(N):
        t = 2 * math.pi * i / N
        # scalloped: rounded bumps with notched valleys (frills = number of bumps)
        sc = abs(math.sin(0.5 * frills * t + ph[0])) ** 0.7
        w = 1 + amp_xy * (sc - 0.5) * 2 * (0.8 + 0.2 * math.sin(5 * t + ph[1]))
        w += 0.04 * math.sin(3 * t + ph[2])
        out.append((a * w * spow(math.cos(t), 2 / 2.6), b * w * spow(math.sin(t), 2 / 2.6)))
        angles.append(t)

    def zfn(x, y, s, i):
        t = angles[i]
        frill = amp_z * math.sin(0.5 * frills * t + ph[0] + 0.8) * s ** 3
        bump = 0.012 * math.sin(5.0 * x + ph[3]) * math.sin(7.0 * y + ph[2]) * s
        return lift + frill + bump + cup * s * s
    return sheet(name, out, thick, zfn=zfn, center=(0, 0), inner=inner, edge=0.5)


def ridged_chip(name: str, R: float, thick: float, *, ridges: float = 3.0, amp: float = 0.012, M: int = 10):
    """Crinkle-cut chip (pickle): round, parallel ridges across both faces. Returns (flesh, skin)."""
    xs = [-R + 2 * R * i / M for i in range(M + 1)]
    lam = 2 * R / ridges

    def zt(x):
        return thick + amp * math.cos(2 * math.pi * x / lam)

    def zb(x):
        return amp * 0.6 * math.cos(2 * math.pi * x / lam)
    verts, faces, skin = [], [], []
    top_r, top_l, bot_r, bot_l = [], [], [], []
    for i, x in enumerate(xs):
        yy = math.sqrt(max(0.0, R * R - x * x)) * 0.995
        if i in (0, M):
            k = len(verts)
            verts.append((x, 0.0, (zt(x) + zb(x)) / 2))
            top_r.append(k)
            top_l.append(k)
            bot_r.append(k)
            bot_l.append(k)
            continue
        for lst, y, z in ((top_r, yy, zt(x)), (top_l, -yy, zt(x)), (bot_r, yy, zb(x)), (bot_l, -yy, zb(x))):
            lst.append(len(verts))
            verts.append((x, y, z))
    def poly(*idx):
        # the two tip columns collapse to one vertex: drop the repeat so the end quads become triangles
        # (as quads with a repeated vertex they were rejected, leaving both chip tips open)
        out = []
        for v in idx:
            if v not in out:
                out.append(v)
        return tuple(out)
    for i in range(M):
        faces.append(poly(top_l[i], top_l[i + 1], top_r[i + 1], top_r[i]))
        faces.append(poly(bot_l[i], bot_r[i], bot_r[i + 1], bot_l[i + 1]))
        skin.append(poly(top_r[i], top_r[i + 1], bot_r[i + 1], bot_r[i]))
        skin.append(poly(top_l[i], bot_l[i], bot_l[i + 1], top_l[i + 1]))
    flesh = mesh_obj(name, verts, [f for f in faces], recalc=False)
    sk = mesh_obj(name + "Skin", verts, skin, recalc=False)
    # orient: top faces up, skin outward (fix any flipped by checking the first face)
    for o, want in ((flesh, None), (sk, None)):
        me = o.data
        for p in me.polygons:
            c = p.center
            if o is flesh:
                if (c.z > thick * 0.5) != (p.normal.z > 0):
                    p.flip()
            else:
                if Vector((c.x, c.y, 0)).dot(Vector((p.normal.x, p.normal.y, 0))) < 0:
                    p.flip()
        me.update()
    return flesh, sk


def annulus(name: str, r_in: float, r_out: float, h: float, N: int = 16, round_: float = 0.25, wob=None):
    """Soft onion-ring style annulus (6-vert cross-section, slightly rounded sides)."""
    e = (r_out - r_in) * round_
    prof = [(r_in, 0.0), (r_out, 0.0), (r_out + e * 0.5, h * 0.5), (r_out, h), (r_in, h), (r_in - e * 0.5, h * 0.5)]
    rings = []
    for k, (r, z) in enumerate(prof):
        ring = []
        for i in range(N):
            t = 2 * math.pi * i / N
            w = 1 + (wob(t) if wob else 0.0)
            ring.append((r * w * math.cos(t), r * w * math.sin(t), z))
        rings.append(ring)
    rings.append(rings[0])
    verts = [v for r in rings[:-1] for v in r]
    faces = []
    P = len(prof)
    for k in range(P):
        k2 = (k + 1) % P
        for i in range(N):
            j = (i + 1) % N
            faces.append((k * N + i, k * N + j, k2 * N + j, k2 * N + i))
    return mesh_obj(name, verts, faces, recalc=True)


def flat_ring(name: str, r_in: float, r_out: float, z: float, N: int = 16, wob=None):
    """Single-sided flat annulus facing +Z (painted-on rings, onion flesh, beet rings)."""
    verts, faces = [], []
    for i in range(N):
        t = 2 * math.pi * i / N
        w = 1 + (wob(t) if wob else 0.0)
        verts.append((r_in * w * math.cos(t), r_in * w * math.sin(t), z))
        verts.append((r_out * w * math.cos(t), r_out * w * math.sin(t), z))
    for i in range(N):
        j = (i + 1) % N
        faces.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))
    o = mesh_obj(name, verts, faces, recalc=False)
    if sum(p.normal.z for p in o.data.polygons) < 0:
        for p in o.data.polygons:
            p.flip()
    return o


# --------------------------------------------------------------------------------------
# sauces
# --------------------------------------------------------------------------------------

SAUCES = {
    # id: ribbon colour, material, bottle body, bottle cap (icon colours / suggested recolours)
    "mayo": dict(col="#FFF5D6", mat="SmoothPlastic", body="#FFF3D2", cap="#3E7FD6", label="#3E7FD6"),
    "mustard": dict(col="#F7C21A", mat="SmoothPlastic", body="#F7C21A", cap="#E8502A"),
    "chipotle": dict(col="#DE5F27", mat="SmoothPlastic", body="#D9572A", cap="#4A2418"),
    "glow_sauce": dict(col="#62FF3B", mat="Neon", body="#56E33A", cap="#3B2352"),
}


def bead(name: str, path, w: float, h: float, taper: int = 4):
    """Squeezed-sauce bead along a 3D path: flat bottom, rounded top, tapered rounded ends."""
    n = len(path)
    prof = [(-1.0, 0.0), (-0.78, 0.62), (-0.32, 0.96), (0.32, 0.96), (0.78, 0.62), (1.0, 0.0)]
    rings = []
    up = Vector((0, 0, 1))
    for k in range(n):
        p = Vector(path[k])
        t = (Vector(path[min(k + 1, n - 1)]) - Vector(path[max(k - 1, 0)])).normalized()
        side = t.cross(up).normalized()
        e = min(k, n - 1 - k)
        f = 1.0 if e >= taper else 0.35 + 0.65 * math.sin(0.5 * math.pi * e / taper)
        ww, hh = w * f, h * (0.55 + 0.45 * f)
        rings.append([tuple(p + side * (a * ww) + up * (b * hh)) for a, b in prof])
    return loft(name, rings, cap_start="fan", cap_end="fan")


def zigzag_path(x0: float = -1.0, x1: float = 1.0, amp: float = 0.27, period: float = 0.62, n: int = 44,
                seed: int = 1, z: float = 0.0):
    rnd = random.Random(seed)
    ph = rnd.uniform(-0.3, 0.3)
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = x0 + (x1 - x0) * t
        s = math.sin(2 * math.pi * (x - x0) / period + ph)
        y = amp * spow(s, 0.75) * (0.92 + 0.08 * math.sin(9 * t))
        pts.append((x, y, z + 0.004 * math.sin(13 * t + ph)))
    return pts


def sauce_ribbon(sauce: str, name: str = "Sauce", **kw):
    s = SAUCES[sauce]
    o = bead(name, zigzag_path(**kw), 0.058, 0.064)
    ns.tag(o, name, s["col"], s["mat"], smooth_angle=80)
    return o


def squeeze_bottle(body_col: str = "#F2B33D", cap_col: str = "#E8502A", label_col: str = "#F3EBD8",
                   verts: int = 20, suffix: str = ""):
    """Diner squeeze bottle ~0.35 wide x 1.1 tall: Body (recolor sauce_body), Cap (screw collar +
    cone nozzle, recolor sauce_cap), Label band."""
    body = ns.lathe([(0.0, 0.0), (0.135, 0.0), (0.163, 0.022), (0.174, 0.075), (0.175, 0.6), (0.168, 0.68),
                     (0.142, 0.745), (0.1, 0.79), (0.085, 0.8)], verts=verts, name="Body")
    ns.tag(body, "Body" + suffix, body_col, "SmoothPlastic", smooth_angle=50, recolor="sauce_body")
    cap = ns.lathe([(0.0, 0.775), (0.104, 0.775), (0.108, 0.79), (0.108, 0.87), (0.098, 0.885), (0.07, 0.895),
                    (0.05, 0.93), (0.022, 1.06), (0.016, 1.09), (0.0, 1.1)], verts=verts, name="Cap")
    ns.tag(cap, "Cap" + suffix, cap_col, "SmoothPlastic", smooth_angle=50, recolor="sauce_cap")
    label = ns.lathe([(0.176, 0.25), (0.179, 0.255), (0.179, 0.5), (0.176, 0.505)], verts=verts, name="Label")
    # close the band's inner side so it is a proper solid
    ns.tag(label, "Label" + suffix, label_col, "SmoothPlastic", smooth_angle=50)
    return body, cap, label


def sauce_icon(sauce: str):
    """Ingredient card for a sauce: the squeeze bottle in that sauce's colours, tipped nozzle-down
    over the squiggle it is squeezing out."""
    s = SAUCES[sauce]
    parts = squeeze_bottle(s["body"], s["cap"], label_col=s.get("label", "#F3EBD8"))
    R = Matrix.Rotation(math.radians(-138), 4, "Y")
    tip = R @ Vector((0, 0, 1.1))
    T = Matrix.Translation((-tip.x - 0.05, 0.05, -tip.z + 0.13))
    for o in parts:
        o.matrix_world = T @ R @ o.matrix_world
        ns.apply_all(o)
    sq = sauce_ribbon(sauce, x0=-0.3, x1=0.3, amp=0.1, period=0.3, n=26)
    sq.scale = (1.2, 1.2, 1.2)
    sq.rotation_euler.z = math.radians(-6)
    sq.location = (0.05, -0.05, 0.0)
