"""_common — shared helpers for the J_lobby batch (99-Nights-style lobby landmarks + plaza decor).

Import from an asset script in this folder with:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import _common as C
    ns = C.ns

Re-uses blender/C_lobby/_common.py (palette, part, text, sandwich_icon, screen_meta, rod,
catenary, place ...) which itself re-uses the B_shop shape helpers (prism, pipe, fillet,
rrect, ring_slab, text_mesh ...), so the new lobby landmarks share the HQ lobby's family look.

New here (giant-lettering kit for the landmarks):
  * word_loops()   2D glyph outlines of a word (Blender font curve), placed in the XZ plane.
  * word_solid()   extruded letters (optionally inflated with `offset`, chamfer-bevelled,
                   back caps dropped) standing in the XZ plane facing -Y.
  * contour_tubes() neon tubes that follow the letter outlines (inset / outset).
  * stroke_points() points along the CENTRE of every letter stroke (distance-transform
                   ridge + farthest-point sampling + relaxation) — marquee bulbs on letters.
  * domes()        many low-poly bulb domes in ONE mesh (cheap marquee rows).
  * run()          build -> preview (NS_QUICK=1 fast) -> optional dusk far-view check
                   (NS_FAR=1, also rendered on every final preview of assets that pass far=True)
                   -> optional socket check (NS_SOCKETS=1) -> export (NS_EXPORT=1).

Conventions (as C_lobby): 1 stud = 1 Blender unit, Z up, front faces Blender -Y, pivot
bottom-centre, role-less parts merge per material at export, part names never start with
Key/Fill/Rim/Floor/RefCube/PreviewCam.
"""
from __future__ import annotations

import importlib.util
import math
import os
import sys

import bpy  # noqa: F401  (must load before bmesh in the bpy module build)
import bmesh
from mathutils import Matrix, Vector

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "lib"))
import nslib as ns  # noqa: E402

# Pillow (nslib's previews and our check renders need it) is not installed in the Blender venv;
# the system Python of the same 3.13 build has it. Appended LAST so the venv's numpy still wins.
_SYS_SITE = "/usr/local/lib/python3.13/site-packages"
if os.path.isdir(_SYS_SITE) and _SYS_SITE not in sys.path:
    sys.path.append(_SYS_SITE)

# C_lobby helpers, loaded under their own module name (every batch calls its file `_common`)
_spec = importlib.util.spec_from_file_location("lobby_common", os.path.join(_HERE, "..", "C_lobby", "_common.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)
S = L.S  # B_shop helpers

fillet, rrect, circle_pts, ellipse_pts = S.fillet, S.rrect, S.circle_pts, S.ellipse_pts
prism, slab, pipe, round_path, ring_slab = S.prism, S.slab, S.pipe, S.round_path, S.ring_slab
text_mesh, fit_text_width, bbox_of, merge, band = S.text_mesh, S.fit_text_width, S.bbox_of, S.merge, S.band
FONT_BOLD, FONT_BOLD_ITALIC = S.FONT_BOLD, S.FONT_BOLD_ITALIC
part, rod, yaw_point, facing_yaw = L.part, L.rod, L.yaw_point, L.facing_yaw
arc_solid, arc_profile_sweep, arch, arch_path = L.arc_solid, L.arc_profile_sweep, L.arch, L.arch_path
annulus, disc, catenary, text, sandwich_icon, place = L.annulus, L.disc, L.catenary, L.text, L.sandwich_icon, L.place
screen_meta = L.screen_meta

BATCH = "J_lobby"
GROUP = "Lobby"
PREVIEWS = os.path.join(ns.REPO, "..", "previews", BATCH)

# ---------------------------------------------------------------------------------------
# Palette (SHARED.md + C_lobby accents)
# ---------------------------------------------------------------------------------------
CREAM, CREAM_SHADE, PAPER = L.CREAM, L.CREAM_SHADE, L.PAPER
BRAND, BRAND_DARK, MUSTARD = L.BRAND, L.BRAND_DARK, L.MUSTARD
NAVY, NAVY_DEEP, PINK, CYAN = L.NAVY, L.NAVY_DEEP, L.PINK, L.CYAN
CHROME, STEEL, CHARCOAL, RUBBER = L.CHROME, L.STEEL, L.CHARCOAL, L.RUBBER
STAINLESS = "#B9C0C6"
SCREEN = L.SCREEN
GLASS, GLASS_DARK = L.GLASS, L.GLASS_DARK
GOLD, BRASS = L.GOLD, L.BRASS
WOOD, WOOD_LIGHT, WOOD_DARK = L.WOOD, L.WOOD_LIGHT, L.WOOD_DARK
BRICK, BRICK_DARK, MORTAR, CONCRETE = L.BRICK, L.BRICK_DARK, L.MORTAR, L.CONCRETE
LAMP_WARM = L.LAMP_WARM
LETTUCE, TOMATO, CHEESE, BUN, BUN_DARK = L.LETTUCE, L.TOMATO, L.CHEESE, L.BUN, L.BUN_DARK
BLACK = L.BLACK
FOLIAGE = "#4E8A3A"
FOLIAGE_DARK = "#3E6B35"
FOLIAGE_DEEP = "#2F5229"
BARK = "#5A3926"
STONE = "#C9BFAE"          # light cast stone (caps, plinths)
STONE_DARK = "#A89E8E"
AMBER = "#F0A830"          # coin gold (brief: amber)
KETCHUP = "#D0262B"
MUSTARD_SAUCE = "#F5C518"
WATER = "#5FD8F0"
STEEL_NAVY = "#2A3550"     # painted structural steel (navy family)
SEAT_RED = "#B8323C"

FORBIDDEN = L.FORBIDDEN


# ---------------------------------------------------------------------------------------
# Small builders
# ---------------------------------------------------------------------------------------

def star_pts(r_out, r_in, cx=0.0, cz=0.0, n=5, rot=90.0):
    """Closed star outline in a 2D plane (x, z by convention)."""
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + 180.0 * i / n)
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def obj_from_bm(bm, name="Mesh"):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _axis_rot(axis):
    """Rotation matrix taking +Z to `axis`."""
    a = Vector(axis).normalized()
    return Vector((0, 0, 1)).rotation_difference(a).to_matrix()


def domes(points, r, axis=(0, -1, 0), segs=6, rings=2, squash=1.0, name="Domes"):
    """Many hemispherical bulb domes (open base) in one mesh. `points` = base centres; each
    dome bulges along `axis` (a single vector, or a list of vectors, one per point).
    segs=6, rings=2 -> 18 tris a bulb."""
    bm = bmesh.new()
    axes = axis if (isinstance(axis, list) and axis and not isinstance(axis[0], (int, float))) else [axis] * len(points)
    for p, ax in zip(points, axes):
        R = _axis_rot(ax)
        c = Vector(p)
        ringv = []
        for k in range(rings):
            phi = (math.pi / 2) * k / rings
            rr, z = r * math.cos(phi), r * math.sin(phi) * squash
            ringv.append([bm.verts.new(c + R @ Vector((rr * math.cos(2 * math.pi * i / segs + 0.3),
                                                          rr * math.sin(2 * math.pi * i / segs + 0.3), z)))
                          for i in range(segs)])
        top = bm.verts.new(c + R @ Vector((0, 0, r * squash)))
        for k in range(rings - 1):
            a, b = ringv[k], ringv[k + 1]
            for i in range(segs):
                j = (i + 1) % segs
                bm.faces.new([a[i], a[j], b[j], b[i]])
        last = ringv[-1]
        for i in range(segs):
            bm.faces.new([last[i], last[(i + 1) % segs], top])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(bm, name)


def spheres(points, r, segs=6, rings=4, scale=(1, 1, 1), name="Spheres"):
    """Many low-poly closed spheres in one mesh (bulbs seen from every side)."""
    bm = bmesh.new()
    for p in points:
        c = Vector(p)
        rows = []
        for k in range(1, rings):
            th = math.pi * k / rings
            rows.append([bm.verts.new(c + Vector((r * scale[0] * math.sin(th) * math.cos(2 * math.pi * i / segs),
                                                  r * scale[1] * math.sin(th) * math.sin(2 * math.pi * i / segs),
                                                  -r * scale[2] * math.cos(th)))) for i in range(segs)])
        bot = bm.verts.new(c + Vector((0, 0, -r * scale[2])))
        top = bm.verts.new(c + Vector((0, 0, r * scale[2])))
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new([bot, rows[0][j], rows[0][i]])
            bm.faces.new([top, rows[-1][i], rows[-1][j]])
        for k in range(len(rows) - 1):
            a, b = rows[k], rows[k + 1]
            for i in range(segs):
                j = (i + 1) % segs
                bm.faces.new([a[i], a[j], b[j], b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(bm, name)


def loft(sections, segs=2, cap_top=True, cap_bottom=True, cx=0.0, cy=0.0, name="Loft"):
    """Stack of horizontal rounded-rect cross-sections [(z, w, d, r), ...] (bottom to top), joined
    by quads (dress-form torsos, bottles, cups). Every section has the same point count."""
    bm = bmesh.new()
    rings = []
    for z, w, d, r in sections:
        rr = max(0.0, min(r, w / 2 - 1e-3, d / 2 - 1e-3))
        pts = rrect(w, d, rr, segs, cx, cy)
        rings.append([bm.verts.new((x, y, z)) for x, y in pts])
    n = len(rings[0])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([a[i], a[j], b[j], b[i]])
    if cap_bottom:
        bm.faces.new(list(reversed(rings[0])))
    if cap_top:
        bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bm(bm, name)


def flat_poly(points2d, y, name="Flat", facing=-1):
    """Single-sided flat polygon (x, z points) in the plane y, facing -Y (facing=-1) or +Y."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z)) for x, z in points2d]
    f = bm.faces.new(vs)
    bm.normal_update()
    if (f.normal.y > 0) != (facing > 0):
        f.normal_flip()
    return obj_from_bm(bm, name)


def flat_poly_3d(points, up=True, facing_out=None, name="Poly"):
    """Single-sided polygon through 3D points. Orientation: facing_out (normal along that vector)
    or up=True / False (normal +Z / -Z)."""
    bm = bmesh.new()
    vs = [bm.verts.new(tuple(p)) for p in points]
    f = bm.faces.new(vs)
    bm.normal_update()
    if facing_out is not None:
        if f.normal.dot(Vector(facing_out)) < 0:
            f.normal_flip()
    elif up is not None and (f.normal.z > 0) != up:
        f.normal_flip()
    return obj_from_bm(bm, name)


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i - 1]
        x1, y1 = poly[i]
        if (y0 > y) != (y1 > y):
            xc = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if xc > x:
                inside = not inside
    return inside


def clip_band(poly, a, b):
    """Sutherland-Hodgman clip of a 2D polygon to the vertical band a <= x <= b."""
    def clip(pl, keep, inter):
        out = []
        for i in range(len(pl)):
            p, q = pl[i - 1], pl[i]
            if keep(q):
                if not keep(p):
                    out.append(inter(p, q))
                out.append(q)
            elif keep(p):
                out.append(inter(p, q))
        return out

    def at(x0):
        return lambda p, q: (x0, p[1] + (q[1] - p[1]) * (x0 - p[0]) / (q[0] - p[0]))

    pl = clip(poly, lambda p: p[0] >= a, at(a))
    return clip(pl, lambda p: p[0] <= b, at(b)) if pl else []


def clip_rect(poly, x0, x1, z0, z1):
    """Intersection of a (possibly concave) 2D polygon with an axis-aligned rectangle."""
    def clip(pl, keep, inter):
        out = []
        for i in range(len(pl)):
            p, q = pl[i - 1], pl[i]
            if keep(q):
                if not keep(p):
                    out.append(inter(p, q))
                out.append(q)
            elif keep(p):
                out.append(inter(p, q))
        return out

    def at_x(xv):
        return lambda p, q: (xv, p[1] + (q[1] - p[1]) * (xv - p[0]) / (q[0] - p[0]))

    def at_z(zv):
        return lambda p, q: (p[0] + (q[0] - p[0]) * (zv - p[1]) / (q[1] - p[1]), zv)

    pl = list(poly)
    for keep, inter in ((lambda p: p[0] >= x0, at_x(x0)), (lambda p: p[0] <= x1, at_x(x1)),
                        (lambda p: p[1] >= z0, at_z(z0)), (lambda p: p[1] <= z1, at_z(z1))):
        if not pl:
            return []
        pl = clip(pl, keep, inter)
    return pl


def path_points(path, spacing, closed=False, start_offset=None):
    """Evenly spaced points along a 3D polyline (approx. arc-length, centred on the path)."""
    pts = [Vector(p) for p in path]
    if closed:
        pts = pts + [pts[0]]
    seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seg)
    if total < 1e-6:
        return []
    n = max(1, int(round(total / spacing)))
    step = total / n
    if closed:
        ts = [step * (k + 0.5) for k in range(n)]
    else:
        n_open = max(1, int(total // spacing))
        step = total / n_open
        off = 0.0 if start_offset is None else start_offset
        ts = [off + step * k for k in range(n_open + 1)] if start_offset is None else [off + step * k for k in range(n_open)]
    out = []
    for t in ts:
        acc = 0.0
        for i, sl in enumerate(seg):
            if acc + sl >= t - 1e-9 or i == len(seg) - 1:
                u = 0.0 if sl < 1e-9 else min(1.0, max(0.0, (t - acc) / sl))
                out.append(tuple(pts[i].lerp(pts[i + 1], u)))
                break
            acc += sl
    return out


def rect_path(x0, x1, z0, z1, y, r=0.0, segs=3):
    """Closed rounded-rectangle path in the XZ plane at depth y (for bulbs / neon frames)."""
    pts2 = rrect(x1 - x0, z1 - z0, r, segs, (x0 + x1) / 2, (z0 + z1) / 2) if r > 0 else \
        [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    return [(x, y, z) for x, z in pts2]


def badge(loc, r=1.2, yaw=0.0, depth=0.16, rim=CREAM_SHADE, n=18):
    """Round STACKHOUSE logo badge (back face on loc's plane, facing -Y before yaw).
    Returns {colour: [objs]}: red-orange disc, cream rim ring, sandwich icon layers."""
    disc_ = prism(circle_pts(r, n), "y", -depth, 0.0)
    # rim ring starts exactly at the disc edge (an overlap made coplanar back faces)
    ring = ring_slab(circle_pts(r + 0.14 * max(1.0, r / 1.6), n), circle_pts(r, n), "y", -depth - 0.05, 0.0)
    icon = sandwich_icon(s=r * 0.42, depth=0.1)
    for col, objs in icon.items():
        for o in objs:
            o.location.y -= depth - 0.001
    out = {BRAND: [disc_], rim: [ring]}
    for col, objs in icon.items():
        out.setdefault(col, []).extend(objs)
    place(out, loc, yaw=yaw)
    return out


def mini_logo(loc, r=0.6, yaw=0.0, depth=0.1, disc=CREAM, n=10):
    """Low-poly STACKHOUSE mark (~110 tris): a disc with a sandwich silhouette (domed top bun,
    wavy lettuce, bottom bun). Back face on loc's plane, facing -Y before yaw. {colour: [objs]}."""
    s = r * 0.62
    d = prism(circle_pts(r, n), "y", -depth, 0.0)
    dome = [(s, 0.12 * s)] + [(s * math.cos(t * math.pi / 5), 0.18 * s + 0.62 * s * math.sin(t * math.pi / 5))
                              for t in range(1, 5)] + [(-s, 0.12 * s)]
    lettuce = [(-1.08 * s + 2.16 * s * i / 6, (0.02 if i % 2 else -0.08) * s) for i in range(7)] + \
              [(1.04 * s, -0.2 * s), (-1.04 * s, -0.2 * s)]
    bottom = rrect(2.0 * s, 0.34 * s, 0.14 * s, 1, 0, -0.45 * s)
    fy = -depth - 0.06
    out = {disc: [d], BUN: [prism(dome, "y", fy, -depth + 0.01), prism(bottom, "y", fy, -depth + 0.01)],
           LETTUCE: [prism(lettuce, "y", fy + 0.01, -depth + 0.01)]}
    place(out, loc, yaw=yaw)
    return out


def add_parts(groups, prefix, **kw):
    """Tag a {colour: [objs]} dict as one part per colour (name = prefix + index)."""
    out = []
    for i, (col, objs) in enumerate(groups.items()):
        objs = [o for o in objs if o is not None]
        if objs:
            out.append(part(objs, f"{prefix}{i + 1}", col, **kw))
    return out


def merge_into(groups, extra):
    """Merge {colour: [objs]} dicts (extra into groups)."""
    for col, objs in extra.items():
        groups.setdefault(col, []).extend(objs)
    return groups


def awning(x0, x1, y_back, z_back, y_front, z_front, n=8, t=0.08, valance=0.45, cols=(BRAND, PAPER),
           cheeks=True):
    """Sloped striped awning (Lobby_ShopKiosk pattern) from the wall (y_back, z_back) down to
    the front edge (y_front, z_front), n stripes across x0..x1 with scalloped valance tabs.
    Returns {colour: [objs]}."""
    sw = (x1 - x0) / n
    out = {cols[0]: [], cols[1]: []}
    for i in range(n):
        col = cols[i % 2]
        a, b = x0 + i * sw, x0 + (i + 1) * sw
        prof = [(y_back, z_back), (y_front, z_front), (y_front, z_front - t), (y_back, z_back - t)]
        out[col].append(prism(prof, "x", a, b))
        tab = [(a, z_front), (b, z_front), (b, z_front - valance * 0.55)]
        for k in range(1, 6):
            ang = math.pi * k / 6
            tab.append(((a + b) / 2 + (sw / 2) * math.cos(ang), z_front - valance * 0.55 - (valance * 0.45) * math.sin(ang)))
        tab.append((a, z_front - valance * 0.55))
        out[col].append(prism(tab, "y", y_front - t / 2, y_front + t / 2))
    if cheeks:
        for sx, xe in ((-1, x0), (1, x1)):
            a0, a1 = sorted((xe - sx * 0.02 - 0.04, xe - sx * 0.02 + 0.04))
            out[cols[0]].append(prism([(y_back, z_back + 0.015), (y_front, z_front + 0.015), (y_front, z_front - valance * 0.55),
                                       (y_back, z_front - valance * 0.3)], "x", a0, a1))
    return out


# ---------------------------------------------------------------------------------------
# Giant lettering kit
# ---------------------------------------------------------------------------------------

def _font_mesh(txt, size, *, font=None, spacing=1.0, res=2, extrude=0.0, offset=0.0, bevel=0.0, bevel_res=0):
    cu = bpy.data.curves.new("WordCurve", "FONT")
    cu.body = txt
    f = font or FONT_BOLD
    if os.path.exists(f):
        cu.font = bpy.data.fonts.load(f, check_existing=True)
    cu.size = size
    cu.space_character = spacing
    cu.resolution_u = res
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = extrude
    cu.offset = offset
    cu.bevel_depth = bevel
    cu.bevel_resolution = bevel_res
    cu.fill_mode = "BOTH"
    ob = bpy.data.objects.new("WordCurve", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.curves.remove(cu)
    return me


def _loops_from_mesh(me):
    """Boundary loops of a flat (z = 0) mesh, oriented so the material is on the LEFT of each
    directed edge (outer contours CCW, holes CW). Returns [[(x, y), ...], ...]."""
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bm.normal_update()
    nxt = {}
    for f in bm.faces:
        vs = list(f.verts)
        if f.normal.z < 0:
            vs = vs[::-1]
        for i in range(len(vs)):
            a, b = vs[i], vs[(i + 1) % len(vs)]
            e = bm.edges.get((a, b))
            if e is not None and len(e.link_faces) == 1:
                nxt[a.index] = b.index
    co = {v.index: (v.co.x, v.co.y) for v in bm.verts}
    loops, seen = [], set()
    for s in list(nxt):
        if s in seen:
            continue
        loop, v = [], s
        while v is not None and v not in seen:
            seen.add(v)
            loop.append(co[v])
            v = nxt.get(v)
        if len(loop) >= 3:
            loops.append(loop)
    bm.free()
    return loops


class Word:
    """A line of text placed in the Blender XZ plane, facing -Y, centred (by its glyph bbox at
    offset 0) on (cx, cz). Every derived mesh / outline uses the same placement, so tubes and
    bulbs line up with the solids. size = font size (cap height ~= 0.41 * size for Poppins
    Bold); or pass cap= to size by cap height."""

    def __init__(self, txt, cx=0.0, cz=0.0, size=None, cap=None, font=None, spacing=1.0, res=2, base=None,
                 xscale=1.0):
        if size is None:
            size = (cap or 1.0) / 0.41
        self.txt, self.size, self.font, self.spacing, self.res = txt, size, font, spacing, res
        me = _font_mesh(txt, size, font=font, spacing=spacing, res=res)
        xs = [v.co.x for v in me.vertices]
        ys = [v.co.y for v in me.vertices]
        bpy.data.meshes.remove(me)
        self.fcx, self.fcy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        self.w, self.h = max(xs) - min(xs), max(ys) - min(ys)
        # baseline / cap line in font space (from an "H", which has no overshoot or descender)
        hm = _font_mesh("H", size, font=font, res=1)
        self.fbase = min(v.co.y for v in hm.vertices)
        self.fcap = max(v.co.y for v in hm.vertices)
        bpy.data.meshes.remove(hm)
        self.cx, self.cz = cx, cz
        self.base = base          # if set: vertical placement by baseline height instead of bbox centre
        self.scale = 1.0
        self.xscale = xscale      # horizontal stretch (extended, chunkier letters)

    @property
    def cap_height(self):
        return (self.fcap - self.fbase) * self.scale

    def fit_width(self, width):
        """Scale the word uniformly so its glyph bbox is `width` wide."""
        self.scale = width / (self.w * self.xscale)
        return self

    @property
    def width(self):
        return self.w * self.scale * self.xscale

    def to_xz(self, x, y):
        X = self.cx + (x - self.fcx) * self.scale * self.xscale
        if self.base is not None:
            return (X, self.base + (y - self.fbase) * self.scale)
        return (X, self.cz + (y - self.fcy) * self.scale)

    def loops(self, offset=0.0):
        """2D outlines [(x, z) ...] (material on the left). offset > 0 grows, < 0 insets."""
        me = _font_mesh(self.txt, self.size, font=self.font, spacing=self.spacing, res=self.res,
                        offset=offset / self.scale)
        out = [[self.to_xz(x, y) for x, y in lp] for lp in _loops_from_mesh(me)]
        bpy.data.meshes.remove(me)
        return out

    def solid(self, y_front, depth, offset=0.0, bevel=0.0, bevel_res=0, back=True, name="Word", front_only=False):
        """Extruded letters from y_front (front face) back to y_front + depth. offset inflates
        the outline (studs); bevel = chamfer width on the front/back rims."""
        s = self.scale
        bev = bevel / s
        ext = max(0.001, (depth / s - 2 * bev) / 2)
        me = _font_mesh(self.txt, self.size, font=self.font, spacing=self.spacing, res=self.res,
                        extrude=ext, offset=(offset - bevel) / s if bevel else offset / s, bevel=bev,
                        bevel_res=bevel_res)
        bm = bmesh.new()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
        zmax = max(v.co.z for v in bm.verts)
        for v in bm.verts:
            x, y, z = v.co
            X, Z = self.to_xz(x, y)
            v.co = Vector((X, y_front + (zmax - z) * s, Z))
        bm.normal_update()
        if front_only:
            drop = [f for f in bm.faces if f.normal.y > -0.95]
            bmesh.ops.delete(bm, geom=drop, context="FACES")
            for f in bm.faces:
                f.normal_flip() if f.normal.y > 0 else None
            return obj_from_bm(bm, name)
        if not back:
            drop = [f for f in bm.faces if f.normal.y > 0.95]
            bmesh.ops.delete(bm, geom=drop, context="FACES")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        if not back:
            # recalc may flip an open shell inside-out: make the front caps face -Y again
            fronts = [f for f in bm.faces if abs(f.normal.y) > 0.95]
            if fronts and sum(f.normal.y for f in fronts) > 0:
                for f in bm.faces:
                    f.normal_flip()
        return obj_from_bm(bm, name)


def contour_tubes(loops, y, radius, sides=5, name="Tubes", min_len=0.0):
    """Closed neon tubes along 2D outlines (x, z) at depth y."""
    objs = []
    for lp in loops:
        per = sum(math.dist(lp[i], lp[(i + 1) % len(lp)]) for i in range(len(lp)))
        if per < min_len:
            continue
        pts = _simplify([(x, y, z) for x, z in lp], 0.02)
        objs.append(pipe(pts, radius, sides=sides, closed=True))
    return merge(objs, name) if objs else None


def _simplify(pts, tol):
    """Drop points closer than tol to the previous kept one (font meshes repeat corners)."""
    out = [pts[0]]
    for p in pts[1:]:
        if (Vector(p) - Vector(out[-1])).length > tol:
            out.append(p)
    if len(out) > 2 and (Vector(out[0]) - Vector(out[-1])).length <= tol:
        out.pop()
    return out


def stroke_points(loops, spacing, px=0.07, min_frac=0.72, relax=8, seed_left=True):
    """Points along the centre line of the letter strokes described by `loops` (2D, x/z),
    about `spacing` apart: rasterise (even-odd), exact distance transform, ridge pixels
    (local maxima along any of 4 directions, distance >= min_frac * typical half-stroke),
    farthest-point sampling, then a few rounds of Lloyd relaxation restricted to the ridge
    (evens the spacing along curves). Returns [(x, z), ...] and the half-stroke width."""
    import numpy as np
    from PIL import Image, ImageDraw
    xs = [p[0] for lp in loops for p in lp]
    zs = [p[1] for lp in loops for p in lp]
    x0, z1 = min(xs) - 3 * px, max(zs) + 3 * px
    W = int((max(xs) - x0) / px) + 4
    H = int((z1 - min(zs)) / px) + 4
    mask = np.zeros((H, W), dtype=bool)
    for lp in loops:
        im = Image.new("1", (W, H), 0)
        ImageDraw.Draw(im).polygon([((x - x0) / px, (z1 - z) / px) for x, z in lp], fill=1)
        mask ^= np.array(im, dtype=bool)
    # boundary pixels = outside pixels touching the inside (distance measured to them)
    pad = np.pad(mask, 1)
    near = np.zeros_like(mask)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            near |= pad[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
    bnd = np.argwhere(near & ~mask).astype(np.float32)
    ins = np.argwhere(mask)
    dist = np.zeros((H, W), dtype=np.float32)
    for k in range(0, len(ins), 1500):
        chunk = ins[k:k + 1500].astype(np.float32)
        d2 = ((chunk[:, None, :] - bnd[None, :, :]) ** 2).sum(-1)
        dist[ins[k:k + 1500, 0], ins[k:k + 1500, 1]] = np.sqrt(d2.min(1))
    dp = np.pad(dist, 1)
    c = dp[1:-1, 1:-1]
    ridge = np.zeros_like(mask)
    for (ay, ax), (by, bx) in (((0, -1), (0, 1)), ((-1, 0), (1, 0)), ((-1, -1), (1, 1)), ((-1, 1), (1, -1))):
        a = dp[1 + ay:1 + ay + H, 1 + ax:1 + ax + W]
        b = dp[1 + by:1 + by + H, 1 + bx:1 + bx + W]
        ridge |= (c >= a) & (c >= b) & ((c > a) | (c > b))
    ridge &= mask
    if not ridge.any():
        return [], 0.0
    hw = float(np.percentile(dist[ridge], 70))
    ridge &= dist >= min_frac * hw
    rp = np.argwhere(ridge)
    P = np.stack([x0 + (rp[:, 1] + 0.5) * px, z1 - (rp[:, 0] + 0.5) * px], axis=1)
    # farthest-point sampling, seeded at the left-most (then top-most) ridge point
    start = int(np.lexsort((-P[:, 1], P[:, 0]))[0]) if seed_left else int(np.argmax(dist[ridge]))
    sel = [start]
    dmin = np.sqrt(((P - P[start]) ** 2).sum(1))
    while dmin.max() >= spacing:
        k = int(np.argmax(dmin))
        sel.append(k)
        dmin = np.minimum(dmin, np.sqrt(((P - P[k]) ** 2).sum(1)))
    Q = P[sel].copy()
    for _ in range(relax):
        d2 = ((P[:, None, :] - Q[None, :, :]) ** 2).sum(-1)
        own = d2.argmin(1)
        for i in range(len(Q)):
            m = P[own == i]
            if len(m):
                ctr = m.mean(0)
                # snap the centroid back onto the ridge
                j = int(((m - ctr) ** 2).sum(1).argmin())
                Q[i] = m[j]
    return [tuple(map(float, q)) for q in Q], hw * px


def _glyph_mask(loops, px, margin=3):
    """Even-odd raster of 2D outlines -> (mask[H, W] bool, x0, z1) with pixel (i, j) centred at
    (x0 + (j + .5) px, z1 - (i + .5) px)."""
    import numpy as np
    from PIL import Image, ImageDraw
    xs = [p[0] for lp in loops for p in lp]
    zs = [p[1] for lp in loops for p in lp]
    x0, z1 = min(xs) - margin * px, max(zs) + margin * px
    W = int((max(xs) - x0) / px) + 2 * margin
    H = int((z1 - min(zs)) / px) + 2 * margin
    mask = np.zeros((H, W), dtype=bool)
    for lp in loops:
        im = Image.new("1", (W, H), 0)
        ImageDraw.Draw(im).polygon([((x - x0) / px, (z1 - z) / px) for x, z in lp], fill=1)
        mask ^= np.array(im, dtype=bool)
    return mask, x0, z1


def _zhang_suen(mask):
    """Zhang-Suen thinning (vectorised) -> 1-px wide 8-connected skeleton."""
    import numpy as np
    img = mask.astype(np.uint8).copy()
    while True:
        changed = False
        for step in (0, 1):
            P = np.pad(img, 1)
            p2, p3, p4 = P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:]
            p5, p6, p7 = P[2:, 2:], P[2:, 1:-1], P[2:, :-2]
            p8, p9 = P[1:-1, :-2], P[:-2, :-2]
            nb = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            A = sum(((nb[i] == 0) & (nb[i + 1] == 1)).astype(np.uint8) for i in range(8))
            if step == 0:
                c = ((p2 * p4 * p6) == 0) & ((p4 * p6 * p8) == 0)
            else:
                c = ((p2 * p4 * p8) == 0) & ((p2 * p6 * p8) == 0)
            m = (img == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if m.any():
                img[m] = 0
                changed = True
        if not changed:
            return img.astype(bool)


def _skel_graph(S):
    """Pixel graph of a skeleton set S: 4-neighbours, plus diagonals only where no orthogonal
    pixel already joins the two (removes staircase triangles)."""
    adj = {}
    for (y, x) in S:
        nb = set()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if (y + dy, x + dx) in S:
                nb.add((y + dy, x + dx))
        for dy, dx in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            q = (y + dy, x + dx)
            if q in S and (y + dy, x) not in S and (y, x + dx) not in S:
                nb.add(q)
        adj[(y, x)] = nb
    return adj


def _trace(adj):
    """Chains between end / junction pixels, plus pure loops: [(closed, [pixels])]."""
    used = set()
    out = []

    def ek(a, b):
        return (a, b) if a < b else (b, a)

    for s in [v for v in adj if len(adj[v]) != 2]:
        for w in adj[s]:
            if ek(s, w) in used:
                continue
            used.add(ek(s, w))
            chain, prev, cur = [s, w], s, w
            while len(adj[cur]) == 2:
                nx = [q for q in adj[cur] if q != prev][0]
                if ek(cur, nx) in used:
                    break
                used.add(ek(cur, nx))
                prev, cur = cur, nx
                chain.append(cur)
            out.append((False, chain))
    for v in adj:
        for w in adj[v]:
            if ek(v, w) in used:
                continue
            used.add(ek(v, w))
            chain, prev, cur = [v], v, w
            while cur != v:
                chain.append(cur)
                nx = [q for q in adj[cur] if q != prev and ek(cur, q) not in used]
                if not nx:
                    break
                used.add(ek(cur, nx[0]))
                prev, cur = cur, nx[0]
            out.append((True, chain))
    return out


def stroke_paths(loops, spacing=0.5, px=0.05, spur=None, smooth=4):
    """Ordered centre-line polylines of letter strokes (single-line neon): even-odd raster,
    Zhang-Suen thinning, pixel graph (staircase diagonals dropped), corner spurs pruned (end
    chains shorter than `spur` studs, default ~0.75 x the stroke width), chains smoothed with a
    moving average and resampled every `spacing` studs. Junctions split chains (an H gives 5).
    Returns [(closed, [(x, z), ...]), ...]."""
    import numpy as np
    mask, x0, z1 = _glyph_mask(loops, px)
    sk = _zhang_suen(mask)
    S = set(map(tuple, np.argwhere(sk)))
    if spur is None:
        # stroke width ~ 2 x mean distance from skeleton to the outline: estimate from area / length
        spur = 0.75 * (mask.sum() / max(1, len(S))) * px
    for _ in range(3):
        adj = _skel_graph(S)
        chains = _trace(adj)
        drop = set()
        for closed, ch in chains:
            if closed:
                continue
            e0, e1 = len(adj[ch[0]]), len(adj[ch[-1]])
            if (e0 == 1 or e1 == 1) and len(ch) * px < spur and not (e0 == 1 and e1 == 1 and len(ch) * px > spur * 0.5):
                keep = {ch[0]} if e0 > 2 else set()
                keep |= {ch[-1]} if e1 > 2 else set()
                drop |= set(ch) - keep
        if not drop:
            break
        S -= drop
    adj = _skel_graph(S)
    out = []
    for closed, ch in _trace(adj):
        if len(ch) < 3:
            continue
        pts = np.array([(x0 + (x + 0.5) * px, z1 - (y + 0.5) * px) for y, x in ch])
        k = smooth
        if len(pts) > 2 * k + 1:
            if closed:
                ext = np.concatenate([pts[-k:], pts, pts[:k]])
                sm = np.array([ext[i:i + 2 * k + 1].mean(0) for i in range(len(pts))])
            else:
                sm = pts.copy()
                for i in range(1, len(pts) - 1):
                    a, b = max(0, i - k), min(len(pts), i + k + 1)
                    w = min(i - a, b - 1 - i)
                    sm[i] = pts[i - w:i + w + 1].mean(0)
            pts = sm
        rs = resample([tuple(p) for p in pts], spacing, closed=closed)
        out.append((closed, [(v.x, v.z) for v in rs]))
    return out


def resample(path, spacing, closed=False):
    """Resample a 2D/3D polyline at ~even spacing (keeps the end points of open paths)."""
    pts = [Vector(p if len(p) == 3 else (p[0], 0.0, p[1])) for p in path]
    if closed:
        pts.append(pts[0])
    seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seg)
    n = max(2 if not closed else 3, int(round(total / spacing)))
    out = []
    for k in range(n + (0 if closed else 1)):
        t = total * k / n
        acc = 0.0
        for i, sl in enumerate(seg):
            if acc + sl >= t - 1e-9 or i == len(seg) - 1:
                u = 0.0 if sl < 1e-9 else min(1.0, max(0.0, (t - acc) / sl))
                out.append(pts[i].lerp(pts[i + 1], u))
                break
            acc += sl
    return out


def split_islands(obj):
    """Split a mesh object into connected islands -> list of vertex index lists."""
    me = obj.data
    adj = {i: set() for i in range(len(me.vertices))}
    for e in me.edges:
        a, b = e.vertices
        adj[a].add(b)
        adj[b].add(a)
    seen, out = set(), []
    for v in range(len(me.vertices)):
        if v in seen:
            continue
        stack, isl = [v], []
        seen.add(v)
        while stack:
            u = stack.pop()
            isl.append(u)
            for w in adj[u]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        out.append(isl)
    return out


# ---------------------------------------------------------------------------------------
# Check renders (dusk far view, sockets) and the run wrapper
# ---------------------------------------------------------------------------------------

def _dusk_world(strength=1.0):
    sc = bpy.context.scene
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.use_nodes = True
    nt = sc.world.node_tree
    bg = nt.nodes.get("Background")
    # vertical gradient: purple-pink horizon -> deep violet zenith
    tex = nt.nodes.new("ShaderNodeTexGradient")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    mp.inputs["Rotation"].default_value = (0, math.pi / 2, 0)   # gradient along the view direction's z
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.45, 0.17, 0.30, 1)
    cr.elements[1].position = 0.45
    cr.elements[1].color = (0.07, 0.04, 0.17, 1)
    bg.inputs[1].default_value = strength
    return [tex, tc, mp, ramp]


def render_dusk(asset, views, res=(512, 384), samples=12, tag="far", floor_col="#2E2A36"):
    """Dusk check: purple-pink sky gradient, weak warm key + cool fill, Neon parts glowing.
    views = [(cam_loc, look_at, lens_mm)]. Saved to previews/J_lobby/_checks/<asset>_<tag>.png."""
    from PIL import Image
    sc = bpy.context.scene
    ns._setup_render(res[0], samples, transparent=False)
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Standard"
    extra = _dusk_world(0.9)
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    ctr = (lo + hi) / 2
    d = (hi - lo).length
    bpy.ops.mesh.primitive_plane_add(size=max(d * 12, 200), location=(ctr.x, ctr.y, min(lo.z, 0.0) - 0.002))
    fl = bpy.context.active_object
    fl.name = "Floor"
    fl.data.materials.append(ns.material(floor_col))
    # moon/sky key from upper left front, warm low sun rim from behind
    ns._light("Key", "SUN", (0, 0, 0), 0.6, target=(0.5, 0.9, -0.55))
    ns._light("Rim", "SUN", (0, 0, 0), 1.2, target=(-0.4, -0.8, -0.25))
    for o in sc.objects:
        if o.name in ("Key", "Rim") and o.type == "LIGHT":
            o.data.color = (0.75, 0.7, 1.0) if o.name == "Key" else (1.0, 0.62, 0.42)
    # front glow (like the map's PointLights near the landmark)
    ns._light("Fill", "AREA", (ctr.x, lo.y - d * 0.35, lo.z + (hi.z - lo.z) * 0.35), 18 * d ** 2 / 9, size=d * 0.5,
              target=tuple(ctr))
    paths = []
    for i, (cl, at, lens) in enumerate(views):
        for o in list(sc.objects):
            if o.name.startswith("PreviewCam"):
                bpy.data.objects.remove(o, do_unlink=True)
        cd = bpy.data.cameras.new("PreviewCam")
        cd.lens = lens
        cd.clip_end = 5000
        cam = bpy.data.objects.new("PreviewCam", cd)
        sc.collection.objects.link(cam)
        cam.location = Vector(cl)
        cam.rotation_euler = (Vector(at) - Vector(cl)).to_track_quat("-Z", "Y").to_euler()
        sc.camera = cam
        out_dir = os.path.join(PREVIEWS, "_checks")
        os.makedirs(out_dir, exist_ok=True)
        p = os.path.join(out_dir, f"{asset}_{tag}{i}.png")
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append(p)
    ns._clear_rig()
    for n in extra:
        sc.world.node_tree.nodes.remove(n)
    sc.view_settings.view_transform = "Standard"
    ims = [Image.open(p).convert("RGB") for p in paths]
    combo = Image.new("RGB", (sum(im.width for im in ims), max(im.height for im in ims)))
    x = 0
    for im in ims:
        combo.paste(im, (x, 0))
        x += im.width
    out = os.path.join(PREVIEWS, "_checks", f"{asset}_{tag}.png")
    combo.save(out)
    for p in paths:
        os.remove(p)
    return out


def far_views(dist=60.0, eye=5.0):
    """Default dusk check: straight-on front view from `dist` studs at player eye height, and
    a 3/4 view from the plaza."""
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    ctr = (lo + hi) / 2
    hgt = hi.z - lo.z
    wid = max(hi.x - lo.x, hgt * 1.33)
    look = Vector((ctr.x, ctr.y, lo.z + hgt * 0.55))
    fov_w = wid * 1.25
    lens = 36.0 * dist / fov_w  # sensor 36 mm horizontal
    v1 = ((ctr.x, lo.y - dist, eye), tuple(look), max(18.0, min(120.0, lens)))
    a = math.radians(-32)
    d2 = dist * 0.75
    v2 = ((ctr.x + math.sin(a) * d2, lo.y - math.cos(a) * d2, eye + 2.0), tuple(look), max(18.0, min(120.0, lens * 0.78)))
    return [v1, v2]


def _print_parts(asset):
    dg = bpy.context.evaluated_depsgraph_get()
    tot = 0
    for o in sorted(ns._tagged_objects(), key=lambda o: o.name):
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        n = len(me.loop_triangles)
        tot += n
        print(f"  [{asset}] {o.name:22s} {n:5d} tris  {o['ns_material']:13s} {o['ns_color']} role={o.get('ns_role')}"
              f" collide={o['ns_can_collide']}")
        o.evaluated_get(dg).to_mesh_clear()
    lo, hi = ns.bbox_world(ns._tagged_objects())
    print(f"  [{asset}] bbox lo {tuple(round(c, 2) for c in lo)} hi {tuple(round(c, 2) for c in hi)} total {tot}")


def socket_check(asset, sockets, views=((-35, 28),), res=448, samples=8):
    """Render the asset with magenta arrow markers at every socket (C_lobby pattern)."""
    from PIL import Image
    markers = []
    for name, spec in sockets.items():
        if len(spec) == 2 and not isinstance(spec[0], (int, float)):
            loc, yaw = spec
        else:
            loc, yaw = spec, 0.0
        markers += L._arrow(loc, yaw, size=0.9)
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    span = max(hi.x - lo.x, hi.y - lo.y, 0.5)
    bpy.ops.mesh.primitive_plane_add(size=max(span * 8, 8), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, -0.001))
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


def run(build, asset, sockets=None, socket_views=((-35, 28),), budget=None, far=False, far_kw=None, **export_kw):
    """Standard J_lobby entry: build -> preview (NS_QUICK=1: fast, to _quick/) -> dusk far
    view (NS_FAR=1, or always on a final preview when far=True) -> socket check
    (NS_SOCKETS=1) -> export (NS_EXPORT=1)."""
    ns.reset()
    extra = build() or {}
    tris = ns.tri_count()
    print(f"[{asset}] triangles: {tris}" + (f" / budget {budget}" if budget else ""))
    if budget and tris > budget:
        print(f"[{asset}] WARNING: over the triangle budget by {tris - budget}")
    if os.environ.get("NS_PARTS") == "1":
        _print_parts(asset)
    quick = os.environ.get("NS_QUICK") == "1"
    if os.environ.get("NS_NORENDER") != "1" and os.environ.get("NS_ONLYFAR") != "1":
        res, spp = (384, 8) if quick else (512, 16)
        out_dir = os.path.join(PREVIEWS, "_quick") if quick else PREVIEWS
        prev = ns.render_preview(asset, out_dir=out_dir, res=res, samples=spp)
        print(f"[{asset}] preview: {prev}")
    if os.environ.get("NS_FAR") == "1" or os.environ.get("NS_ONLYFAR") == "1" or \
            (far and not quick and os.environ.get("NS_NORENDER") != "1"):
        kw = far_kw or {}
        print(f"[{asset}] dusk check: {render_dusk(asset, far_views(**kw), samples=10 if quick else 16)}")
    if sockets and os.environ.get("NS_SOCKETS") == "1":
        print(f"[{asset}] sockets: {socket_check(asset, sockets, views=socket_views)}")
    if os.environ.get("NS_EXPORT") == "1":
        kw = dict(export_kw)
        kw.update(extra.get("export", {}))
        doc = ns.export_asset(asset, BATCH, group=GROUP, sockets=sockets, **kw)
        print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']}")
        for p in doc["parts"]:
            print(f"    part {p['name']:20s} {p['material']:13s} role={p['role']} tris={p['tris']}")
        print(f"[{asset}] sockets: {doc.get('sockets')}")
    return extra
