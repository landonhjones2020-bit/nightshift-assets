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


def build_bread_bottom(crust_col: str, crumb_col: str, N: int = 28, lump=None):
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
    return crust, crumb


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


def run(build, asset: str, meta_: dict | None = None, icon=None, pivot=(0.0, 0.0, 0.0), **export_kw):
    """Standard A_food entry: preview (+ export with NS_EXPORT=1, + icon with NS_ICON=1).

    pivot  defaults to the contract origin (0, 0, 0): bottom-centre of the layer even when parts
           (melted drips, flecks) poke below or the outline is asymmetric. Pass None for nslib's
           bounding-box default.
    icon   (icon_name, icon_build_fn, render_icon_kwargs) or None.
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
        ns.run_main(build, asset, BATCH, GROUP, **kw)
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
    "white_sub": dict(crust="#E9A957", crumb="#FFF2D6", lump=(3, 0.010)),
    "wheat_sub": dict(crust="#97582B", crumb="#D9AC76", extra="#EED9A8", lump=(5, 0.012)),
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
            x = x0 - 0.2 + 0.4 * t
            y = -0.27 + 0.54 * t
            pts.append((x, y))
            ws.append(0.02 + 0.10 * math.sin(math.pi * t) ** 0.7)
        objs.append(surface_ribbon(f"Score{k}", tree, pts, ws, lift=0.022, depth=0.03))
    s = ns.join(objs, "Scores")
    ns.tag(s, "Scores", col, "SmoothPlastic", smooth_angle=60)
    return s


def _bread_cracks(tree, col):
    """Black bread: jagged fissures splitting the crust, showing the purple crumb."""
    rnd = random.Random(4)
    objs = []
    for k, (x0, x1, y0) in enumerate(((-0.85, -0.25, -0.05), (-0.05, 0.45, 0.06), (0.55, 0.9, -0.08))):
        pts, ws = [], []
        n = 6
        for i in range(n):
            t = i / (n - 1)
            x = x0 + (x1 - x0) * t
            y = y0 + (0.05 if i % 2 else -0.05) * (0.4 + 0.6 * math.sin(math.pi * t)) + rnd.uniform(-0.015, 0.015)
            pts.append((x, y))
            ws.append(0.008 + 0.045 * math.sin(math.pi * t) ** 0.7)
        objs.append(surface_ribbon(f"Crack{k}", tree, pts, ws, lift=0.006, depth=0.03))
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
        return build_bread_bottom(b["crust"], b["crumb"], lump=roll_lump(seed, amp * 0.6))
    crust, crumb = build_bread_top(b["crust"], b["crumb"], lump=roll_lump(seed + 1, amp))
    if kind == "sourdough":
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
                 names=("Meat", "MeatEdge"), rim_on_top: bool = False, cup: float = 0.02, yaws=(-6, 2, 7),
                 tilt=(-4, 0, 4), zstep: float = 0.013, smooth_angle: float = 80.0, droop: bool = True):
    """Like rippled_slices but on the polar `sheet` topology: smooth outlines for the budget."""
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
            return (amp * math.sin(2 * math.pi * (x + sk * y) / wavelength + ph) * (0.3 + 0.7 * s)
                    + cup * s * s)
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
                 width=0.27, thick=0.035, amp=0.032, wavelength=0.46, segs=18, seed=2, scale=1.0):
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
            z = a_ * (1 + math.sin(2 * math.pi * x / wavelength + ph)) + 0.004 + 0.012 * k
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


def flecks_on(name: str, targets, spots, col: str, mat: str = "Neon", size=(0.032, 0.022, 0.012), verts: int = 5,
              seed: int = 3):
    """Small chips sitting on the top of `targets` (ray-cast) — glowing flecks, pepper bits."""
    tree = bvh(ns.join([t.copy() for t in []] or targets, "_tmp") if False else targets[0]) if len(targets) == 1 else None
    if tree is None:
        tmp = []
        for t in targets:
            c = t.copy()
            c.data = t.data.copy()
            bpy.context.scene.collection.objects.link(c)
            tmp.append(c)
        j = ns.join(tmp, "_flecktmp")
        tree = bvh(j)
        bpy.data.objects.remove(j, do_unlink=True)
    rnd = random.Random(seed)
    objs = []
    for i, (x, y) in enumerate(spots):
        f = ns.cyl(1.0, 1.0, verts=verts, bevel=0, name=f"{name}{i}")
        s = rnd.uniform(0.8, 1.2)
        f.scale = (size[0] * s, size[1] * s, size[2])
        ns.apply_all(f)
        place_on(f, tree, x, y, sink=size[2] * 0.25, spin=rnd.uniform(0, 180))
        ns.apply_all(f)
        objs.append(f)
    o = ns.join(objs, name)
    ns.tag(o, name, col, mat, smooth_angle=None)
    return o
