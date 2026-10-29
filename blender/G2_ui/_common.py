"""_common — shared rig, shape kit and review sheets for the G2_ui batch (UI icons).

Night Shift at STACKHOUSE, batch G2: every UI icon the game still showed as an initials
placeholder — HUD/rail glyphs, crate and ingredient-tag glyphs, currencies and shop products,
passes, meta progression (supplies, run upgrades, uniforms, abilities), the four Regulars'
photo-board portraits and the loading-screen key art. Everything is modelled here in Blender
(or rebuilt from this project's own generators: A_kitchen, A_food, D_characters, E_creatures,
B_shop, C_lobby) and rendered with Cycles.

Icon rig = nslib's render_icon rig (3/4 yaw/pitch camera, Key/Fill/Rim area lights scaled by
distance, transparent film, soft low-specular materials), driven per FAMILY so every icon in a
family shares camera, lights and look. Two additions, both batch-local (nslib untouched):
  * framing: fit_frame() aims and distances the camera on the projected silhouette (the
    G_icons technique), so each icon fills FAMILY[fill] of the frame instead of nslib's
    bounding-sphere fit (which leaves small, off-centre icons);
  * a second, low back-light ("RimKick", opposite the key) so silhouettes separate from the
    dark #1b1b26 HUD panel. Finals go to icons/<group>/<name>.png and are registered through
    nslib.export_icon (the only writer of manifests/icons.json); drafts go to the scratch dir.

Run (one Blender process at a time):
    bpyenv/bin/python blender/G2_ui/_batch.py <family|icon names...> [--draft]
    bpyenv/bin/python blender/G2_ui/_sheet.py <family> [--draft]
    bpyenv/bin/python blender/G2_ui/_verify.py
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import math
import os
import sys

sys.dont_write_bytecode = True          # never drop .pyc files into lib/ or other batches

HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(BLENDER, "lib"))
import nslib as ns  # noqa: E402

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

REPO = ns.REPO
SCRATCH = os.environ.get("NS_SCRATCH",
                         "/tmp/claude-0/-home-claude/bee54a24-967a-5993-94e6-c9b5acdf45a4/scratchpad/g2_icons")
DRAFT_DIR = os.path.join(SCRATCH, "drafts")

# ---- game palette (Theme) ------------------------------------------------------------------
AMBER = "#FFB020"       # Coins, Legendary
AMBER_D = "#D9860B"
AMBER_L = "#FFD873"
PINK = "#FF3D7F"        # Tokens
PINK_D = "#C21F5B"
PINK_L = "#FF8DB4"
CYAN = "#2EE6FF"
GREEN = "#4CFF7A"       # tips, Uncommon
GREEN_D = "#24B84E"
VIOLET = "#9B5CFF"
VIOLET_D = "#6B36C8"
RED = "#FF2E3A"         # danger, Cursed
BLUE = "#2E9BFF"        # Rare
PAPER = "#F3EEE2"
PAPER_D = "#D9D0BC"
INK = "#07070B"
INK_SOFT = "#23232E"
# diner / environment (STYLE.md)
BRAND = "#E8502A"
MUSTARD = "#F2B33D"
CREAM = "#EFE6D2"
STEEL = "#B9C0C6"
STEEL_D = "#7D858E"
CHROME = "#D3D8DC"
GUNMETAL = "#4A4F56"
RUBBER = "#2B2D31"
WOOD = "#A8774E"
WOOD_D = "#7A5233"
VINYL_RED = "#C8323C"
VINYL_RED_D = "#8E2530"
KRAFT = "#C49A63"
KRAFT_D = "#9C7445"
SKIN = "#F2C9A5"
GOLD = "#FFC23A"

PANEL = (0x1B, 0x1B, 0x26)   # HUD panel colour (review sheets)

# ---- icon families: one camera / framing / light set each -----------------------------------
FAMILY = {
    # HUD + rail glyphs (28-56 px on #1b1b26): flat glyphs are turned to show a little side
    "hud": dict(yaw=-28.0, pitch=20.0, fov=24.0, fill=0.90, kick=1.0, samples=48, exposure=0.3),
    # crates: the kitchen crate in its natural 3/4
    "crates": dict(yaw=-34.0, pitch=26.0, fov=24.0, fill=0.92, kick=1.0, samples=48, exposure=0.25),
    # ingredient tags (~20 px): nearly face-on, maximum fill
    "tags": dict(yaw=-28.0, pitch=20.0, fov=24.0, fill=0.94, kick=1.0, samples=48, exposure=0.35),
    # shop cards (120-200 px on a dark rarity-gradient card)
    "shop": dict(yaw=-30.0, pitch=24.0, fov=24.0, fill=0.90, kick=0.8, samples=48, exposure=0.2),
    # meta progression cards (supplies, upgrades, uniforms, abilities)
    "meta": dict(yaw=-30.0, pitch=24.0, fov=24.0, fill=0.90, kick=0.8, samples=48, exposure=0.2),
}

# ---- registry -------------------------------------------------------------------------------
REG: dict[str, dict] = {}
ORDER: dict[str, list] = {}


def icon(name: str, group: str, family: str, kind: str = "icon", **opts):
    """Decorator: register a builder for icon `name` (group = manifest/folder group)."""
    def deco(fn):
        REG[name] = dict(name=name, group=group, family=family, kind=kind, build=fn, opts=opts)
        ORDER.setdefault(family, []).append(name)
        return fn
    return deco


# --------------------------------------------------------------------------------------------
# other batches' generators (their helper module is also called `_common`)
# --------------------------------------------------------------------------------------------
_COMMONS: dict[str, object] = {}
_MODS: dict[tuple, object] = {}


def batch_common(batch: str):
    """blender/<batch>/_common.py loaded under the private name `<batch>__common`."""
    if batch not in _COMMONS:
        path = os.path.join(BLENDER, batch, "_common.py")
        if not os.path.exists(path):          # e.g. gate/: its scripts import nslib directly
            _COMMONS[batch] = None
            return None
        spec = importlib.util.spec_from_file_location(f"{batch}__common", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"{batch}__common"] = mod
        saved = sys.modules.get("_common")
        sys.modules["_common"] = mod
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                spec.loader.exec_module(mod)
        finally:
            sys.modules["_common"] = saved
        _COMMONS[batch] = mod
    return _COMMONS[batch]


def batch_module(batch: str, name: str):
    """Import blender/<batch>/<name>.py (an asset generator) so its build functions can be
    reused; its `import _common` resolves to that batch's helpers, not ours."""
    key = (batch, name)
    if key not in _MODS:
        common = batch_common(batch)
        path = os.path.join(BLENDER, batch, name + ".py")
        spec = importlib.util.spec_from_file_location(f"{batch}__{name}", path)
        mod = importlib.util.module_from_spec(spec)
        saved = sys.modules.get("_common")
        if common is not None:
            sys.modules["_common"] = common
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                spec.loader.exec_module(mod)
        finally:
            sys.modules["_common"] = saved
        _MODS[key] = mod
    return _MODS[key]


def build_foreign(batch: str, name: str, fn: str = "build", *args, quiet=True, **kw):
    """Run <batch>/<name>.<fn>(...) in the current scene; returns (result, new tagged objects)."""
    mod = batch_module(batch, name)
    before = set(ns._tagged_objects())
    if quiet:
        with contextlib.redirect_stdout(io.StringIO()):
            res = getattr(mod, fn)(*args, **kw)
    else:
        res = getattr(mod, fn)(*args, **kw)
    bpy.context.view_layer.update()
    return res, [o for o in ns._tagged_objects() if o not in before]


def shop_helpers():
    return batch_common("B_shop")


# --------------------------------------------------------------------------------------------
# tagging (render-only: parts are never exported, so no joins are needed)
# --------------------------------------------------------------------------------------------
_N = [0]


def T(objs, color: str, mat: str = "SmoothPlastic", name: str = "Part", smooth: float | None = 40.0,
      gloss: float | None = None, emit: float | None = None, alpha: float | None = None, shadow=True):
    """Tag one object or a list as render parts. Names are prefixed `G_` (nslib's light
    cleanup deletes objects whose names start with Key/Fill/Rim/Floor/RefCube/PreviewCam).
    gloss: keep this roughness in renders (chrome, glass, wet asphalt) instead of the icon
    rig's matte floor; emit: emission strength override (Neon); alpha: material alpha."""
    lst = objs if isinstance(objs, (list, tuple)) else [objs]
    out = []
    for o in lst:
        _N[0] += 1
        ns.tag(o, f"G_{name}_{_N[0]}", color, mat, smooth_angle=smooth, cast_shadow=shadow)
        if gloss is not None or emit is not None or alpha is not None:
            m = o.data.materials[0].copy()
            m.name = f"{m.name}_g{_N[0]}"
            b = m.node_tree.nodes.get("Principled BSDF")
            if gloss is not None:
                b.inputs["Roughness"].default_value = gloss
                m["g2_gloss"] = gloss
            if emit is not None:
                b.inputs["Emission Strength"].default_value = emit
            if alpha is not None:
                b.inputs["Alpha"].default_value = alpha
                m["g2_alpha"] = alpha
            o.data.materials.clear()
            o.data.materials.append(m)
        out.append(o)
    return out if isinstance(objs, (list, tuple)) else out[0]


def neon(objs, color: str, strength: float = 4.0, name="Glow", alpha=None):
    """Self-lit part (Roblox Neon)."""
    return T(objs, color, "Neon", name=name, emit=strength, alpha=alpha, shadow=False)


def glow_mat(obj, color: str, strength: float, alpha: float, name="Halo", falloff: float = 0.0):
    """Soft additive-looking halo: emission + transparency, no shadow (beams, auras).
    falloff > 0 fades it toward grazing angles (a sphere becomes a soft radial glow)."""
    _N[0] += 1
    m = bpy.data.materials.new(f"G2_{name}_{_N[0]}")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    r, g, b = (ns.srgb_to_linear(c) for c in ns.hex_rgb(color))
    em.inputs["Color"].default_value = (r, g, b, 1)
    em.inputs["Strength"].default_value = strength
    mix.inputs["Fac"].default_value = alpha
    if falloff > 0:
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.5
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        nt.links.new(lw.outputs["Facing"], inv.inputs[1])
        pw = nt.nodes.new("ShaderNodeMath")
        pw.operation = "POWER"
        pw.inputs[1].default_value = falloff
        nt.links.new(inv.outputs[0], pw.inputs[0])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = alpha
        nt.links.new(pw.outputs[0], mul.inputs[0])
        nt.links.new(mul.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    o = obj
    o.name = f"G_{name}_{_N[0]}"
    o["ns_part"] = o.name
    o["ns_color"] = color
    o["ns_material"] = "Neon"
    o["ns_transparency"] = 1 - alpha
    o["ns_cast_shadow"] = False
    o["ns_can_collide"] = False
    o["ns_smooth_angle"] = 60.0
    o.data.materials.clear()
    o.data.materials.append(m)
    o.visible_shadow = False
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def glass_mat(obj, tint="#DDF6FF", centre=0.12, edge=0.75, name="Glass"):
    """Toon glass for icons: nearly clear face-on, brighter and more opaque toward grazing
    angles (reads as a glass wall over whatever is inside), glossy, no shadow."""
    _N[0] += 1
    m = bpy.data.materials.new(f"G2_{name}_{_N[0]}")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    pb = nt.nodes.new("ShaderNodeBsdfPrincipled")
    r, g, b = (ns.srgb_to_linear(c) for c in ns.hex_rgb(tint))
    pb.inputs["Base Color"].default_value = (r, g, b, 1)
    pb.inputs["Roughness"].default_value = 0.12
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = centre
    mr.inputs["To Max"].default_value = edge
    nt.links.new(lw.outputs["Facing"], mr.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs["Result"], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(pb.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    m["g2_custom"] = True
    obj.name = f"G_{name}_{_N[0]}"
    obj["ns_part"] = obj.name
    obj["ns_color"] = tint
    obj["ns_material"] = "Glass"
    obj["ns_transparency"] = 0.7
    obj["ns_cast_shadow"] = False
    obj["ns_can_collide"] = False
    obj["ns_smooth_angle"] = 60.0
    obj.data.materials.clear()
    obj.data.materials.append(m)
    obj.visible_shadow = False
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


# --------------------------------------------------------------------------------------------
# 2D outlines (x, z) — z up, the glyph faces -Y
# --------------------------------------------------------------------------------------------

def circle(r, n=48, cx=0.0, cz=0.0, a0=0.0, rz=None):
    rz = r if rz is None else rz
    return [(cx + r * math.cos(a0 + 2 * math.pi * i / n), cz + rz * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def arc(r, a0, a1, n=12, cx=0.0, cz=0.0):
    """Points along an arc from a0 to a1 (degrees), inclusive."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def rrect(w, h, r, n=5, cx=0.0, cz=0.0):
    r = max(1e-4, min(r, w / 2 - 1e-4, h / 2 - 1e-4))
    pts = []
    for x, z, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                     (w / 2 - r, -h / 2 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + x + r * math.cos(a), cz + z + r * math.sin(a)))
    return pts


def star(n=5, r_out=1.0, r_in=0.45, a0=90.0, cx=0.0, cz=0.0, round_=0.0):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(a0 + 180.0 * i / n)
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return fillet(pts, round_) if round_ > 0 else pts


def heart(size=1.0, n=64, cx=0.0, cz=0.0, plump=1.0):
    """Classic cartoon heart, ~2*size wide, centred on its bbox."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        z = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x * plump, z))
    xs = [p[0] for p in pts]
    zs = [p[1] for p in pts]
    s = size * 2 / (max(xs) - min(xs))
    mz = (max(zs) + min(zs)) / 2
    return [(cx + x * s, cz + (z - mz) * s) for x, z in pts]


def fillet(pts, r, segs=3):
    """Round every corner of a closed polygon by radius r (clamped per corner)."""
    out = []
    n = len(pts)
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        a, b = (p0 - p1), (p2 - p1)
        la, lb = a.length, b.length
        if la < 1e-6 or lb < 1e-6:
            continue
        a.normalize()
        b.normalize()
        ang = math.acos(max(-1.0, min(1.0, a.dot(b))))
        if ang > math.radians(175) or ang < 1e-3:
            out.append(tuple(p1))
            continue
        t = r / math.tan(ang / 2)
        t = min(t, la * 0.48, lb * 0.48)
        rr = t * math.tan(ang / 2)
        s0 = p1 + a * t
        s1 = p1 + b * t
        bis = (a + b).normalized()
        c = p1 + bis * (rr / math.sin(ang / 2))
        v0, v1 = s0 - c, s1 - c
        a0 = math.atan2(v0.y, v0.x)
        a1 = math.atan2(v1.y, v1.x)
        d = a1 - a0
        while d > math.pi:
            d -= 2 * math.pi
        while d < -math.pi:
            d += 2 * math.pi
        for k in range(segs + 1):
            aa = a0 + d * k / segs
            out.append((c.x + rr * math.cos(aa), c.y + rr * math.sin(aa)))
    return out


def stroke(path, width, cap_round=True, n_cap=18):
    """Closed outline of a thick polyline `path` [(x, z)...] (mitred joins, round caps)."""
    P = [Vector(p) for p in path]
    hw = width / 2
    left, right = [], []
    for i, p in enumerate(P):
        if i == 0:
            d = (P[1] - P[0]).normalized()
            nrm = Vector((-d.y, d.x))
            m = 1.0
        elif i == len(P) - 1:
            d = (P[-1] - P[-2]).normalized()
            nrm = Vector((-d.y, d.x))
            m = 1.0
        else:
            d0 = (P[i] - P[i - 1]).normalized()
            d1 = (P[i + 1] - P[i]).normalized()
            n0 = Vector((-d0.y, d0.x))
            n1 = Vector((-d1.y, d1.x))
            nrm = (n0 + n1).normalized()
            m = 1.0 / max(0.35, nrm.dot(n0))
        left.append(p + nrm * hw * m)
        right.append(p - nrm * hw * m)
    out = [tuple(v) for v in left]
    if cap_round:
        d = (P[-1] - P[-2]).normalized()
        a = math.atan2(d.y, d.x)
        for k in range(1, n_cap):
            aa = a + math.pi / 2 - math.pi * k / n_cap
            out.append((P[-1].x + hw * math.cos(aa), P[-1].y + hw * math.sin(aa)))
    out += [tuple(v) for v in reversed(right)]
    if cap_round:
        d = (P[0] - P[1]).normalized()
        a = math.atan2(d.y, d.x)
        for k in range(1, n_cap):
            aa = a + math.pi / 2 - math.pi * k / n_cap
            out.append((P[0].x + hw * math.cos(aa), P[0].y + hw * math.sin(aa)))
    return out


def smooth_path(pts, n=8, closed=False):
    """Catmull-Rom resample of a polyline (x, z)."""
    P = [Vector(p) for p in pts]
    out = []
    m = len(P)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if closed else P[max(i - 1, 0)]
        p1 = P[i]
        p2 = P[(i + 1) % m] if closed else P[i + 1]
        p3 = P[(i + 2) % m] if closed else P[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            v = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            out.append((v.x, v.y))
    if not closed:
        out.append(tuple(P[-1]))
    return out


# --------------------------------------------------------------------------------------------
# solids
# --------------------------------------------------------------------------------------------

def _bevel(o, width, segs, angle=30.0, profile=0.5, clamp=True):
    if width <= 0:
        return o
    m = o.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segs
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(angle)
    m.profile = profile
    m.use_clamp_overlap = clamp
    m.harden_normals = False
    return o


def slab(pts, depth, bevel=0.0, segs=3, y=0.0, name="Slab", profile=0.5, angle=30.0, clamp=True):
    """Extrude a closed (x, z) outline along +Y, centred on y; the front face looks at -Y."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y - depth / 2, z)) for x, z in pts]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, depth, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = ns.from_bmesh(bm, name)
    return _bevel(o, bevel, segs, angle, profile, clamp)


def slab_holes(outer, holes, depth, bevel=0.0, segs=3, y=0.0, name="SlabH", profile=0.5):
    """Like slab() but the outline may have holes (list of inner outlines)."""
    bm = bmesh.new()
    edges = []
    for loop in [outer] + list(holes):
        vs = [bm.verts.new((x, y - depth / 2, z)) for x, z in loop]
        for i in range(len(vs)):
            edges.append(bm.edges.new((vs[i], vs[(i + 1) % len(vs)])))
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges, normal=Vector((0, -1, 0)))
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:])
    faces = bm.faces[:]
    ext = bmesh.ops.extrude_face_region(bm, geom=faces)
    top = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, depth, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = ns.from_bmesh(bm, name)
    return _bevel(o, bevel, segs, 30.0, profile)


def puffy_holes(outer, holes, depth, puff=0.42, segs=4, y=0.0, name="PuffyH"):
    return slab_holes(outer, holes, depth, bevel=depth * puff, segs=segs, y=y, name=name)


def puffy(pts, depth, puff=0.42, segs=4, y=0.0, name="Puffy"):
    """Chunky pillow glyph: an extruded outline whose front/back rims are rounded off by
    `puff` x depth (toy / soft-plastic read)."""
    return slab(pts, depth, bevel=depth * puff, segs=segs, y=y, name=name, profile=0.5)


def slab_xy(pts, height, bevel=0.0, segs=2, z=0.0, name="SlabXY"):
    """Extrude a closed (x, y) outline upward from z (lying flat)."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, yy, z)) for x, yy in pts]
    f = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, height))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = ns.from_bmesh(bm, name)
    return _bevel(o, bevel, segs)


def box(size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.06, segs=3, name="Box"):
    return ns.box(size, loc=loc, rot=rot, bevel=bevel, segments=segs, name=name)


def cyl(r, depth, loc=(0, 0, 0), rot=(0, 0, 0), verts=32, bevel=0.04, segs=3, r_top=None, name="Cyl"):
    return ns.cyl(r, depth, loc=loc, rot=rot, verts=verts, bevel=bevel, segments=segs, radius_top=r_top, name=name)


def sphere(r, loc=(0, 0, 0), scale=(1, 1, 1), segs=24, rings=14, rot=(0, 0, 0), name="Sphere"):
    o = ns.sphere(r, loc=loc, scale=scale, segs=segs, rings=rings, name=name)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    return o


def torus(R, r, loc=(0, 0, 0), rot=(0, 0, 0), segs=32, rsegs=12, scale=None, name="Torus"):
    o = ns.torus(R, r, loc=loc, rot=rot, major_segs=segs, minor_segs=rsegs, name=name)
    if scale:
        o.scale = scale
    return o


def lathe(profile, verts=32, loc=(0, 0, 0), rot=(0, 0, 0), name="Lathe"):
    o = ns.lathe(profile, verts=verts, loc=loc, name=name)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    return o


def tube(points, radii, sides=12, res=6, name="Tube"):
    if not isinstance(radii, (list, tuple)):
        radii = [radii] * len(points)
    return ns.tube(points, radii, sides=sides, resolution=res, name=name)


def rod(p0, p1, r, verts=16, bevel=0.0, r_top=None, name="Rod"):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = ns.cyl(r, d.length, loc=(p0 + p1) / 2, verts=verts, bevel=bevel, segments=2, radius_top=r_top, name=name)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def text(s, size, depth, loc=(0, 0, 0), bold=True, bevel=0.0, spacing=1.0, name="Text"):
    """Modelled Poppins text standing in the XZ plane, facing -Y, centred on loc."""
    S = shop_helpers()
    font = S.FONT_BOLD if bold else "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
    with contextlib.redirect_stdout(io.StringIO()):
        o = S.text_mesh(s, size, depth, font=font, bevel=bevel, resolution=3, spacing=spacing, loc=loc, name=name)
    return o


def fit_width(o, width):
    S = shop_helpers()
    S.fit_text_width(o, width)
    return o


def boolean(target, cutter, op="DIFFERENCE"):
    """Apply a boolean (target keeps its other modifiers; they are applied first)."""
    for m in list(target.modifiers):
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.select_all(action="DESELECT")
        target.select_set(True)
        bpy.ops.object.modifier_apply(modifier=m.name)
    for m in list(cutter.modifiers):
        bpy.context.view_layer.objects.active = cutter
        bpy.ops.object.select_all(action="DESELECT")
        cutter.select_set(True)
        bpy.ops.object.modifier_apply(modifier=m.name)
    mod = target.modifiers.new("Bool", "BOOLEAN")
    mod.operation = op
    mod.object = cutter
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return target


def apply(o):
    ns.apply_all(o)
    return o


def xform(objs, M: Matrix):
    """Pre-multiply world matrices (objects keep their modifiers)."""
    lst = objs if isinstance(objs, (list, tuple)) else [objs]
    bpy.context.view_layer.update()
    for o in lst:
        o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()
    return objs


def R(rx=0.0, ry=0.0, rz=0.0, about=(0, 0, 0)) -> Matrix:
    """Rotation (degrees, XYZ order) about a point."""
    c = Vector(about)
    M = (Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Rotation(math.radians(ry), 4, "Y")
         @ Matrix.Rotation(math.radians(rx), 4, "X"))
    return Matrix.Translation(c) @ M @ Matrix.Translation(-c)


def Tm(x=0.0, y=0.0, z=0.0) -> Matrix:
    return Matrix.Translation((x, y, z))


def S(s, about=(0, 0, 0)) -> Matrix:
    c = Vector(about)
    if isinstance(s, (int, float)):
        M = Matrix.Diagonal((s, s, s, 1.0))
    else:
        M = Matrix.Diagonal((s[0], s[1], s[2], 1.0))
    return Matrix.Translation(c) @ M @ Matrix.Translation(-c)


def tagged():
    return ns._tagged_objects()


def centre_of(objs=None):
    lo, hi = ns.bbox_world(objs or tagged())
    return (lo + hi) / 2


def face_cam(objs=None, family="hud", reveal=12.0, tilt=8.0):
    """Turn a flat glyph (built facing -Y) toward the family camera, leaving `reveal` degrees
    of 3/4 so its thickness shows, and tip it back `tilt` degrees toward the camera pitch."""
    objs = objs or tagged()
    f = FAMILY[family]
    c = centre_of(objs)
    xform(objs, R(rz=f["yaw"] + reveal, about=c) @ R(rx=-tilt, about=c))
    return objs


# --------------------------------------------------------------------------------------------
# framing (projected-silhouette fit, as G_icons) and rendering
# --------------------------------------------------------------------------------------------

def _world_points(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        pts.extend(mw @ v.co for v in me.vertices)
        ev.to_mesh_clear()
    return pts


def _cam_basis(yaw, pitch):
    y_, p_ = math.radians(yaw), math.radians(pitch)
    d = Vector((math.sin(y_) * math.cos(p_), -math.cos(y_) * math.cos(p_), math.sin(p_)))
    f = -d
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f)
    return d, f, r, u


def fit_frame(objs, yaw, pitch, fov, fill, offset=(0.0, 0.0)):
    """Aim point c and distance D so the projected silhouette is centred (plus `offset`, in
    frame halves) and its larger side fills `fill` of the frame."""
    pts = _world_points(objs)
    d, f, r, u = _cam_basis(yaw, pitch)
    th = math.tan(math.radians(fov) / 2)
    lo, hi = ns.bbox_world(objs)
    c = (lo + hi) / 2
    D = max((hi - lo).length, 0.1) / 2 / math.sin(math.radians(fov) / 2)
    for _ in range(12):
        cam = c + d * D
        xs, ys = [], []
        for p in pts:
            v = p - cam
            dep = v.dot(f)
            xs.append(v.dot(r) / dep / th)
            ys.append(v.dot(u) / dep / th)
        cx, cy = (min(xs) + max(xs)) / 2 - offset[0], (min(ys) + max(ys)) / 2 - offset[1]
        ext = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
        c = c + r * (cx * D * th) + u * (cy * D * th)
        D *= ext / fill
    return c, D


def make_camera(c, D, yaw, pitch, fov, name="PreviewCam"):
    d, f, r, u = _cam_basis(yaw, pitch)
    cd = bpy.data.cameras.new(name)
    cd.angle = math.radians(fov)
    cd.clip_start = max(0.01, D * 0.01)
    cd.clip_end = D * 20
    cam = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = c + d * D
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def icon_lights(c, D, yaw, kick=1.0):
    """nslib render_icon's three-point rig (same placements and energies) + a low kicker
    from behind, opposite the key, for a clean edge on dark panels."""
    k = math.radians(yaw)
    ns._light("Key", "AREA", c + Vector((math.sin(k - 0.7), -math.cos(k - 0.7), 1.0)) * D, 62 * D ** 2 / 9, size=D * 0.6, target=c)
    ns._light("Fill", "AREA", c + Vector((math.sin(k + 1.3), -math.cos(k + 1.3), 0.2)) * D, 18 * D ** 2 / 9, size=D * 0.9, target=c)
    ns._light("Rim", "AREA", c + Vector((-math.sin(k), math.cos(k), 0.9)) * D, 50 * D ** 2 / 9, size=D * 0.4, target=c)
    if kick > 0:
        ns._light("RimKick", "AREA", c + Vector((math.sin(k + 2.3), -math.cos(k + 2.3), 0.35)) * D,
                  kick * 30 * D ** 2 / 9, size=D * 0.35, target=c)


def _icon_materials():
    """render_icon's material tweak: soft, low-specular so colours read saturated."""
    for m in bpy.data.materials:
        if m.get("g2_custom"):
            continue
        b = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
        if b:
            g = m.get("g2_gloss")
            b.inputs["Roughness"].default_value = g if g is not None else max(0.62, b.inputs["Roughness"].default_value)
            b.inputs["Specular IOR Level"].default_value = 0.25 if g is None else 0.5


def render_icon(name, draft=False, objects=None, offset=(0.0, 0.0), fam_over=None):
    """Render registered icon `name` (scene already built)."""
    e = REG[name]
    f = dict(FAMILY[e["family"]])
    f.update(e["opts"].get("cam", {}))
    if fam_over:
        f.update(fam_over)
    objs = objects or [o for o in tagged() if not o.get("g2_noframe")]
    c, D = fit_frame(objs, f["yaw"], f["pitch"], f["fov"], f["fill"], offset=e["opts"].get("offset", offset))
    res = 128 if draft else 512
    samples = 12 if draft else f["samples"]
    ns._setup_render(res, samples, transparent=True)
    sc = bpy.context.scene
    sc.world.node_tree.nodes.get("Background").inputs[1].default_value = 0.45
    sc.cycles.use_denoising = True
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.exposure = f.get("exposure", 0.0)
    _icon_materials()
    make_camera(c, D, f["yaw"], f["pitch"], f["fov"])
    icon_lights(c, D, f["yaw"], f.get("kick", 1.0))
    if draft:
        out = os.path.join(DRAFT_DIR, f"{name}.png")
    else:
        out = os.path.join(REPO, "icons", e["group"], f"{name}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out
    with contextlib.redirect_stdout(io.StringIO()):
        bpy.ops.render.render(write_still=True)
    ns._clear_rig()
    for o in list(bpy.context.scene.objects):
        if o.name.startswith("RimKick"):
            bpy.data.objects.remove(o, do_unlink=True)
    return out


def publish(name, png):
    """Register a final PNG: .nsz beside it + manifests/icons.json entry (nslib.export_icon)."""
    e = REG[name]
    return ns.export_icon(png, name, e["group"])


def run(name, draft=False):
    e = REG[name]
    ns.reset()
    _N[0] = 0
    res = e["build"]() or {}
    if e["kind"] == "icon":
        out = render_icon(name, draft=draft, objects=res.get("frame") if isinstance(res, dict) else None)
        post = e["opts"].get("post")
        if post:
            post(out)
    else:
        out = res["render"](draft)
    if not draft:
        publish(name, out)
    print(f"[{name}] {'draft' if draft else 'final'}: {out}", flush=True)
    return out


# --------------------------------------------------------------------------------------------
# review sheets
# --------------------------------------------------------------------------------------------

def _font(size):
    from PIL import ImageFont
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf", size)
    except OSError:
        return ImageFont.load_default()


def card_bg(size, top=(0x3A, 0x2A, 0x10), bottom=(0x14, 0x12, 0x1C)):
    """Dark shop card with a rarity gradient (Legendary amber by default), for previews."""
    from PIL import Image
    im = Image.new("RGB", (size, size))
    px = im.load()
    for y in range(size):
        t = y / (size - 1)
        c = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(size):
            px[x, y] = c
    return im


def sheet(family, names, src=None, out=None, big=None):
    """Labelled review sheet: each icon at full size beside 56/32 px (and 20 px for tags,
    160 px card for shop/meta) copies on the #1b1b26 panel."""
    from PIL import Image, ImageDraw
    if src is None:
        paths = {n: os.path.join(REPO, "icons", REG[n]["group"], f"{n}.png") for n in names}
    else:
        paths = {n: os.path.join(src, f"{n}.png") for n in names}
    ims = {n: Image.open(p).convert("RGBA") for n, p in paths.items() if os.path.exists(p)}
    if not ims:
        raise SystemExit("no images")
    full_w = max(im.size[0] for im in ims.values())
    full_h = max(im.size[1] for im in ims.values())
    if big:
        full_w, full_h = big
    smalls = [56, 32] + ([20] if family == "tags" else [])
    card = 160 if family in ("shop", "meta") else 0
    side_w = max(smalls) + 24 + (card + 16 if card else 0)
    cell_w = full_w + side_w + 24
    cell_h = max(full_h, card + max(smalls) + 60 if card else 0) + 34
    cols = max(1, min(len(names), 8 if full_w <= 256 else 4))
    rows = (len(names) + cols - 1) // cols
    sh = Image.new("RGB", (cols * cell_w, rows * cell_h), PANEL)
    dr = ImageDraw.Draw(sh)
    fnt = _font(15)
    for i, n in enumerate(names):
        x, y = (i % cols) * cell_w, (i // cols) * cell_h
        dr.text((x + 10, y + 7), n, fill=(232, 232, 236), font=fnt)
        im = ims.get(n)
        if im is None:
            dr.text((x + 10, y + 40), "missing", fill=(255, 90, 90), font=fnt)
            continue
        disp = im if im.size[0] <= full_w else im.resize((full_w, int(im.size[1] * full_w / im.size[0])), Image.LANCZOS)
        # full-size tile on a slightly lighter well so the transparent edge is visible
        well = Image.new("RGB", disp.size, (0x24, 0x24, 0x31))
        sh.paste(well, (x + 8, y + 30))
        sh.paste(disp, (x + 8, y + 30), disp)
        sx = x + 8 + full_w + 16
        sy = y + 30
        for s in smalls:
            sm = im.resize((s, int(im.size[1] * s / im.size[0])), Image.LANCZOS)
            sh.paste(sm, (sx, sy), sm)
            dr.text((sx + s + 4, sy + s // 2 - 8), f"{s}", fill=(120, 120, 140), font=_font(11))
            sy += sm.size[1] + 14
        if card:
            cb = card_bg(card)
            sm = im.resize((int(card * 0.86), int(card * 0.86 * im.size[1] / im.size[0])), Image.LANCZOS)
            cb.paste(sm, ((card - sm.size[0]) // 2, (card - sm.size[1]) // 2), sm)
            sh.paste(cb, (sx, sy))
    out = out or os.path.join(SCRATCH, f"_sheet_{family}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sh.save(out)
    return out
