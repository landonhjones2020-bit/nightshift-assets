"""Shared helpers for the A_kitchen batch (kitchen equipment and props).

Import from a generator in this folder with:
    import _common as C          (the folder is on sys.path when the script runs)
    ns = C.ns                     (the shared nslib)

Everything here is batch-local sugar on top of nslib: the kitchen palette, a few shape
builders nslib does not have (rods between points, rounded-rect slabs, extrusions in any
plane), and the shared stainless prep-table base so every worktop on the line matches.
"""
from __future__ import annotations

import math
import os
import sys

import bpy  # noqa: F401  (must load before bmesh/mathutils in the bpy module build)
import bmesh
from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import nslib as ns  # noqa: E402

BATCH = "A_kitchen"
GROUP = "Kitchen"
TOP = 3.0                    # worktop / counter height (STYLE.md §3)

# ---- palette (environment: a step greyer than food) ---------------------------------
STAINLESS = "#B9C0C6"        # worktops, bodies
STEEL = "#9AA2AA"            # inset steel (trays, shelves)
STEEL_DARK = "#6B727A"       # frames, rails, slots
GUNMETAL = "#4A4F56"         # belts, grilles, deep shadows
RUBBER = "#2B2D31"           # feet, grips, gaskets
CHARCOAL = "#3A3D42"         # basement / printer bodies
CREAM = "#EFE6D2"            # kitchen warm cream (boards, paper)
PAPER = "#F6F1E6"            # receipt / wrap paper (a hair brighter than cream)
BRAND = "#E8502A"            # STACKHOUSE red-orange
MUSTARD = "#F2B33D"          # STACKHOUSE mustard
ICY = "#9FD3E8"              # freezer icy blue
FROST = "#E4F3FA"            # frost / snow caps
HEAT = "#FF7A1E"             # glowing oven interior (Neon)
WARN_YELLOW = "#F2C230"      # warning stickers
BLACK = "#1E1F22"


def run(build, asset: str, **export_kw):
    """nslib.run_main with this batch's folder and Studio group."""
    if os.environ.get("NS_PARTS") == "1":
        def wrapped():
            out = build()
            _print_parts(asset)
            return out
        return ns.run_main(wrapped, asset, BATCH, GROUP, **export_kw)
    return ns.run_main(build, asset, BATCH, GROUP, **export_kw)


def _print_parts(asset):
    import bpy
    dg = bpy.context.evaluated_depsgraph_get()
    for o in sorted(ns._tagged_objects(), key=lambda o: o.name):
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        print(f"  [{asset}] {o.name:18s} {len(me.loop_triangles):5d} tris  role={o.get('ns_role')}")
        o.evaluated_get(dg).to_mesh_clear()


# ---- shape helpers --------------------------------------------------------------------

def rod(p0, p1, r, verts=8, bevel=0.0, segments=1, name="Rod", r_top=None):
    """Straight cylinder (or taper with r_top) from point p0 to p1."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = ns.cyl(r, d.length, loc=(p0 + p1) / 2, verts=verts, bevel=bevel, segments=segments,
               radius_top=r_top, name=name)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def rrect(w, h, r, n=4, cx=0.0, cy=0.0):
    """Closed 2D rounded-rectangle outline (w x h, corner radius r, n segments/corner)."""
    r = min(r, w / 2 - 1e-4, h / 2 - 1e-4)
    pts = []
    corners = ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
               (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270))
    for x, y, a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + x + r * math.cos(a), cy + y + r * math.sin(a)))
    return pts


def extrude(points2d, thickness, plane="XY", offset=0.0, loc=(0, 0, 0), bevel=0.0, segments=2, name="Ext"):
    """Extrude a closed 2D outline.

    plane "XY": outline in (x, y), extruded along +Z from z = offset.
    plane "XZ": outline in (x, z), extruded along +Y from y = offset (front-facing plates).
    plane "YZ": outline in (y, z), extruded along +X from x = offset (side profiles).
    """
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


def plate(w, h, t, r, loc, plane="XZ", bevel=0.01, n=3, name="Plate"):
    """Rounded-rect plate of thickness t centred at loc. plane XZ = facing -Y (front),
    XY = lying flat."""
    o = extrude(rrect(w, h, r, n), t, plane=plane, offset=-t / 2, bevel=bevel, segments=1, name=name)
    o.location = Vector(loc)
    return o


def mirror_x(objs_fn, xs):
    """Call objs_fn(x) for each x and return the flat list of objects."""
    out = []
    for x in xs:
        r = objs_fn(x)
        out.extend(r if isinstance(r, (list, tuple)) else [r])
    return out


def part(objs, name, color, mat="SmoothPlastic", **kw):
    """Join (applying modifiers) and tag in one go. objs may be one object or a list."""
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    if len(objs) == 1:
        o = objs[0]
        ns.apply_all(o)
    else:
        o = ns.join_applied(list(objs), name)
    return ns.tag(o, name, color, mat, **kw)


def screws(points, r=0.035, depth=0.03, axis="Y", verts=8):
    """Little domed screw heads facing -axis (front by default)."""
    out = []
    for p in points:
        if axis == "Y":
            out.append(ns.cyl(r, depth, loc=p, rot=(90, 0, 0), verts=verts, bevel=r * 0.5, segments=1))
        else:
            out.append(ns.cyl(r, depth, loc=p, verts=verts, bevel=r * 0.5, segments=1))
    return out


# ---- shared stainless prep-table base -------------------------------------------------

def table_base(width, depth, top=TOP, shelf_z=0.55, apron=0.32, leg=0.28, inset=0.2):
    """Legs, rubber feet and an undershelf for a stainless worktop (open front).

    Returns dict(legs=[objs], feet=[objs], shelf=obj). The worktop itself is built by the
    caller (each station cuts its own recesses). Legs stop under the apron.
    """
    lx = width / 2 - inset
    ly = depth / 2 - inset
    leg_top = top - apron + 0.02
    legs, feet = [], []
    for sx in (-1, 1):
        for sy in (-1, 1):
            legs.append(ns.box((leg, leg, leg_top - 0.12), loc=(sx * lx, sy * ly, 0.12 + (leg_top - 0.12) / 2),
                               bevel=0.05, segments=1))
            # bullet foot: wider pad tapering into the leg
            feet.append(ns.cyl(leg * 0.62, 0.14, loc=(sx * lx, sy * ly, 0.07), verts=8,
                               bevel=0.0, radius_top=leg * 0.5))
    # undershelf with a turned-up lip; side rails tie the legs together at shelf height
    shelf = ns.box((width - 2 * inset + leg * 0.9, depth - 2 * inset + leg * 0.9, 0.12),
                   loc=(0, 0, shelf_z), bevel=0.04, segments=1)
    rails = []
    for sx in (-1, 1):
        rails.append(ns.box((leg * 0.7, depth - 2 * inset, 0.14), loc=(sx * lx, 0, shelf_z - 0.04),
                            bevel=0.03, segments=1))
    return {"legs": legs + rails, "feet": feet, "shelf": shelf}


def worktop_slab(width, depth, top=TOP, apron=0.32, backsplash=0.45, splash_t=0.14):
    """Stainless worktop: thick rolled front edge + a rounded backsplash along +Y."""
    slab = ns.box((width, depth, apron), loc=(0, 0, top - apron / 2), bevel=0.07, segments=2)
    objs = [slab]
    if backsplash > 0:
        bs = ns.box((width, splash_t, backsplash + 0.06), loc=(0, depth / 2 - splash_t / 2, top + backsplash / 2 - 0.03),
                    bevel=0.05, segments=2)
        objs.append(bs)
    return objs


def open_pan(w, d, h, lip=0.06, lip_t=0.04, taper=0.05, r=0.09, n=2, loc=(0, 0, 0), name="Pan"):
    """Insert/hotel pan: flat lip ring at z = 0 (rim top), tapered inner walls down to a floor
    at z = -h. Only the faces you can see when it sits in a well are modelled (no outer
    walls under the lip), so six of these stay cheap. loc = rim-top centre."""
    bm = bmesh.new()

    def ring(ww, dd, rr, z):
        return [bm.verts.new((x, y, z)) for x, y in rrect(ww, dd, rr, n)]

    outer = ring(w, d, r, 0.0)
    outer_lo = ring(w, d, r, -lip_t)
    inner = ring(w - 2 * lip, d - 2 * lip, max(r - lip, 0.02), 0.0)
    bottom = ring(w - 2 * lip - 2 * taper, d - 2 * lip - 2 * taper, max(r - lip - taper, 0.02), -h)
    k = len(outer)
    # rrect runs counter-clockwise seen from +Z; windings below give outward/upward normals
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new([outer[i], outer[j], inner[j], inner[i]])            # lip top (up)
        bm.faces.new([outer_lo[i], outer_lo[j], outer[j], outer[i]])      # lip edge (out)
        bm.faces.new([inner[i], inner[j], bottom[j], bottom[i]])          # inner wall (in)
    bm.faces.new(bottom)                                                  # floor (up)
    return ns.from_bmesh(bm, name, loc)
