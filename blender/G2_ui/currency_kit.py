"""currency_kit — the STACKHOUSE Coin and Token (2026-11-06 redesign).

Landon: "create our own custom images for the coin and tokens rn they look very bland" and "for
the gold token make it a little more complex and clean". The old pieces were a flat matte amber
disc with an "S" and a matte pink gear with a star.

  COIN   struck gold: a reeded (milled) edge, a raised polished rim, a ring of beads, a satin
         field, and the STACKHOUSE stamp in polished relief in the middle: top bun with sesame
         seeds, a wavy lettuce leaf, the patty, the bottom bun. Polished relief on a satin field
         is how real coins read; the edge reeding and beads carry the detail, the four big stamp
         layers stay legible at HUD size (~30 px).
  TOKEN  premium arcade token, a different silhouette from the coin: a rounded hexagon of glossy
         pink enamel with a chrome inner frame, six chrome studs, and a faceted pink gem in a
         chrome bezel. Pink and chrome only: Coins and Tokens never share a colour (Bible).

Both are built lying flat, centred at the origin, face up +Z, radius ~1, so fam_shop's stack /
heap / stand helpers place them as before. Materials are custom PBR (g2_custom, so the icon
rig's matte pass leaves them alone): metal needs gloss and the studio world (_common.studio_world)
to read as metal.
"""
from __future__ import annotations

import math

import bpy
import bmesh

import _common as G
from _common import ns, Vector

COIN_R, COIN_T = 1.0, 0.26
TOKEN_R, TOKEN_T = 1.04, 0.26        # circumradius of the hexagon
TOKEN_APOTHEM = TOKEN_R * math.cos(math.radians(30))

# coin metal (gold tones around the game's Coins amber #FFB020)
GOLD_POLISH = "#FFD15E"
GOLD_SATIN = "#D9890F"
GOLD_EDGE = "#F2AE2E"
# token
TOKEN_PINK = "#FF3D7F"
TOKEN_PINK_D = "#C21F5B"
GEM_PINK = "#F2387A"
CHROME = "#EEF2F7"

_M = [0]


def pbr(obj, color, metallic=0.0, rough=0.4, coat=0.0, coat_rough=0.08, emit=0.0, emit_col=None,
        spec=0.5, name="PBR", smooth=40.0, flat=False):
    """Tag `obj` as a render part with its own Principled material (left alone by the icon
    rig's matte pass)."""
    _M[0] += 1
    key = f"{color}|{metallic}|{rough}|{coat}|{emit}|{flat}"
    m = bpy.data.materials.get(f"CK_{key}")
    if m is None:
        m = bpy.data.materials.new(f"CK_{key}")
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        r, g, bb = (ns.srgb_to_linear(c) for c in ns.hex_rgb(color))
        b.inputs["Base Color"].default_value = (r, g, bb, 1)
        b.inputs["Metallic"].default_value = metallic
        b.inputs["Roughness"].default_value = rough
        b.inputs["Specular IOR Level"].default_value = spec
        if coat > 0:
            b.inputs["Coat Weight"].default_value = coat
            b.inputs["Coat Roughness"].default_value = coat_rough
        if emit > 0:
            er, eg, eb = (ns.srgb_to_linear(c) for c in ns.hex_rgb(emit_col or color))
            b.inputs["Emission Color"].default_value = (er, eg, eb, 1)
            b.inputs["Emission Strength"].default_value = emit
        m["g2_custom"] = True
        m.diffuse_color = (r, g, bb, 1)
    o = obj
    o.name = f"G_{name}_{_M[0]}"
    o["ns_part"] = o.name
    o["ns_color"] = color
    o["ns_material"] = "Metal" if metallic > 0.5 else "SmoothPlastic"
    o["ns_transparency"] = 0.0
    o["ns_cast_shadow"] = True
    o["ns_can_collide"] = False
    o["ns_smooth_angle"] = -1.0 if flat else float(smooth)
    o.data.materials.clear()
    o.data.materials.append(m)
    if flat:
        for p in o.data.polygons:
            p.use_smooth = False
    else:
        ns._set_sharp_by_angle(o.data, float(smooth))
    return o



def _spheres(centres, r, scale=(1.0, 1.0, 1.0), segs=10, rings=6, name="Beads"):
    """Many small spheres as one mesh (one object instead of dozens: heaps of coins build fast)."""
    from mathutils import Matrix
    bm = bmesh.new()
    S = Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
    for c in centres:
        bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r, matrix=Matrix.Translation(c) @ S)
    o = ns.from_bmesh(bm, name)
    for poly in o.data.polygons:
        poly.use_smooth = True
    return o

# ---------------------------------------------------------------------------------------------
# the STACKHOUSE stamp (x across, z up, facing -Y; ~1.0 wide, ~0.86 tall)
# ---------------------------------------------------------------------------------------------

def _dome(w, h, z0, n=28):
    """Top bun: a rounded dome with a softly rounded underside."""
    pts = []
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((w / 2 * math.cos(a), z0 + 0.03 + h * math.sin(a) ** 0.85))
    pts.append((-w / 2 + 0.02, z0))
    pts.append((w / 2 - 0.02, z0))
    return G.fillet(pts, 0.03, 2)


def _wave(x0, x1, ztop, zbot, waves=6, amp=0.035, n=72):
    """Lettuce: a flat top and a scalloped hem."""
    pts = [(x1, ztop), (x0, ztop)]
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        z = zbot + amp * (0.5 + 0.5 * math.cos(2 * math.pi * waves * t))
        pts.append((x, z))
    return G.fillet(pts, 0.012, 2)


def stamp_parts(depth=0.07):
    """The stamp's layers as relief slabs (built in XZ facing -Y). Returns [(obj, role)]."""
    out = []
    W = 1.0
    # top bun
    bun = G.puffy(_dome(W * 0.86, 0.30, 0.14), depth, puff=0.48)
    out.append((bun, "bun"))
    for x, z, r in ((-0.2, 0.33, 0.0), (0.02, 0.38, 8.0), (0.22, 0.31, -10.0), (-0.07, 0.26, 4.0)):
        seed = G.puffy(G.circle(0.045, 16, rz=0.026), 0.03, puff=0.45)
        G.xform(seed, G.Tm(x, -depth / 2 - 0.006, z) @ G.R(ry=r))
        out.append((seed, "seed"))
    # lettuce
    leaf = G.puffy(_wave(-W * 0.5, W * 0.5, 0.115, 0.03), depth * 0.8, puff=0.45)
    out.append((leaf, "leaf"))
    # patty
    patty = G.puffy(G.rrect(W * 0.9, 0.15, 0.07, cz=-0.06), depth * 0.9, puff=0.48)
    out.append((patty, "patty"))
    # bottom bun
    bot = G.puffy(G.rrect(W * 0.84, 0.13, 0.06, cz=-0.24), depth, puff=0.48)
    out.append((bot, "bun"))
    return out


# ---------------------------------------------------------------------------------------------
# COIN
# ---------------------------------------------------------------------------------------------

def _reeded(r, depth=0.009, n=120, k=4):
    """Circle outline with `n` milled grooves."""
    pts = []
    for i in range(n * k):
        a = 2 * math.pi * i / (n * k)
        ph = (i % k) / k
        rr = r - (depth if 0.25 <= ph < 0.75 else 0.0)
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    return pts


def coin(emboss="stamp", detail=True, scale=1.0):
    """The STACKHOUSE coin, face up +Z. detail=False: body, rim and a plain field (for the
    deep layers of heaps)."""
    R, T = COIN_R, COIN_T
    parts = []
    if detail:
        body = G.slab_xy(_reeded(R), T, bevel=0.012, segs=1, z=-T / 2)
    else:
        body = G.cyl(R, T, verts=48, bevel=0.03, segs=2)
    pbr(body, GOLD_EDGE, metallic=1.0, rough=0.32, name="CoinBody", smooth=30)
    parts.append(body)
    # the raised rim, both faces (a flipped coin reads too)
    for s in (1, -1):
        rim = G.lathe([(0.8, 0.0), (0.83, 0.035), (0.955, 0.04), (0.985, 0.0)], verts=64 if detail else 40)
        if s < 0:
            G.xform(rim, G.S((1, 1, -1)))
        G.xform(rim, G.Tm(0, 0, s * T / 2))
        pbr(rim, GOLD_POLISH, metallic=1.0, rough=0.16, name="CoinRim", smooth=50)
        parts.append(rim)
        # the field: a satin disc just proud of the face
        field = G.cyl(0.805, 0.012, loc=(0, 0, s * (T / 2 + 0.004)), verts=64 if detail else 40, bevel=0.0)
        pbr(field, GOLD_SATIN, metallic=1.0, rough=0.5, name="CoinField")
        parts.append(field)
    if detail:
        # a ring of beads inside the rim
        nb = 44
        beads = _spheres([(0.735 * math.cos(2 * math.pi * i / nb), 0.735 * math.sin(2 * math.pi * i / nb), T / 2 + 0.008) for i in range(nb)], 0.024)
        pbr(beads, GOLD_POLISH, metallic=1.0, rough=0.18, name="CoinBead")
        parts.append(beads)
        if emboss == "stamp":
            st = stamp_parts(0.07)
            objs = [o for o, _ in st]
            # lie the stamp on the face, its top toward +Y (away from the viewer of the 3/4 pose)
            G.xform(objs, G.Tm(0, 0, T / 2 + 0.01 + 0.035) @ G.R(rx=-90) @ G.S(0.98) @ G.Tm(0, 0, -0.08))
            for o, role in st:
                pbr(o, GOLD_POLISH, metallic=1.0, rough=0.15 if role != "seed" else 0.25, name=f"Stamp_{role}", smooth=60)
                parts.append(o)
        elif emboss == "arrow":
            e = G.puffy(G.fillet([(0.0, 0.62), (0.48, 0.1), (0.2, 0.1), (0.2, -0.56), (-0.2, -0.56), (-0.2, 0.1), (-0.48, 0.1)], 0.05, 2),
                        0.12, puff=0.35)
            G.xform(e, G.Tm(0, 0, T / 2 + 0.02) @ G.R(rx=-90) @ G.S(0.9))
            G.T(e, G.GREEN, name="CoinMark")
            parts.append(e)
    if scale != 1.0:
        G.xform(parts, G.S(scale))
    return parts


# ---------------------------------------------------------------------------------------------
# TOKEN
# ---------------------------------------------------------------------------------------------

def hexagon(r, corner=0.14, rot=90.0, n=6):
    """Rounded regular polygon (pointy top with rot=90)."""
    pts = [(r * math.cos(math.radians(rot + 360 * i / n)), r * math.sin(math.radians(rot + 360 * i / n))) for i in range(n)]
    return G.fillet(pts, corner, 4)


def _gem(r=0.4, table=0.56, crown=0.15, facets=8):
    """A brilliant-cut gem: girdle ring, crown facets up to a flat table (flat shaded)."""
    bm = bmesh.new()
    girdle = [bm.verts.new((r * math.cos(2 * math.pi * i / facets), r * math.sin(2 * math.pi * i / facets), 0.0)) for i in range(facets)]
    mid = [bm.verts.new((r * 0.82 * math.cos(2 * math.pi * (i + 0.5) / facets), r * 0.82 * math.sin(2 * math.pi * (i + 0.5) / facets), crown * 0.55)) for i in range(facets)]
    top = [bm.verts.new((r * table * math.cos(2 * math.pi * i / facets), r * table * math.sin(2 * math.pi * i / facets), crown)) for i in range(facets)]
    bottom = bm.verts.new((0, 0, -0.06))
    for i in range(facets):
        j = (i + 1) % facets
        bm.faces.new((girdle[i], girdle[j], mid[i]))
        bm.faces.new((girdle[j], top[j], mid[i]))
        bm.faces.new((top[i], girdle[i], mid[i]))
        bm.faces.new((top[j], top[i], mid[i]))
        bm.faces.new((girdle[j], girdle[i], bottom))
    bm.faces.new(top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, "Gem")


def token(detail=True, scale=1.0):
    """The STACKHOUSE token, face up +Z, a pointy-top rounded hexagon."""
    R, T = TOKEN_R, TOKEN_T
    parts = []
    body = G.slab_xy(hexagon(R, 0.16), T, bevel=0.05, segs=3, z=-T / 2)
    pbr(body, TOKEN_PINK, rough=0.24, coat=0.6, name="TokenBody", smooth=35)
    parts.append(body)
    for s in (1, -1):
        # chrome inner frame (a hexagonal ring) on both faces
        frame = G.slab_holes(hexagon(R * 0.86, 0.12), [list(reversed(hexagon(R * 0.75, 0.1)))], 0.05, bevel=0.016, segs=2)
        G.xform(frame, G.Tm(0, 0, s * (T / 2 + 0.006)) @ G.R(rx=-90 if s > 0 else 90))
        pbr(frame, CHROME, metallic=1.0, rough=0.14, name="TokenFrame", smooth=40)
        parts.append(frame)
    if detail:
        # six studs inside the frame's corners
        studs = _spheres([(0.6 * math.cos(math.radians(90 + 60 * i)), 0.6 * math.sin(math.radians(90 + 60 * i)), T / 2 + 0.01) for i in range(6)],
                         0.045, scale=(1, 1, 0.7), segs=12, rings=8, name="Studs")
        pbr(studs, CHROME, metallic=1.0, rough=0.12, name="TokenStud")
        parts.append(studs)
        # the gem in its bezel
        gem = _gem(0.36, table=0.58, crown=0.17, facets=12)
        G.xform(gem, G.Tm(0, 0, T / 2 + 0.02) @ G.R(rz=15))
        pbr(gem, GEM_PINK, rough=0.02, spec=1.0, emit=0.12, emit_col="#FF4F8F", name="TokenGem", flat=True)
        bezel = G.torus(0.38, 0.04, loc=(0, 0, T / 2 + 0.025), segs=40, rsegs=8)
        pbr(bezel, CHROME, metallic=1.0, rough=0.12, name="TokenBezel")
        parts += [gem, bezel]
    else:
        dot = G.cyl(0.3, 0.03, loc=(0, 0, T / 2 + 0.01), verts=8, bevel=0.0)
        pbr(dot, GEM_PINK, rough=0.1, emit=0.25, emit_col="#FF4F8F", name="TokenGem", flat=True)
        parts.append(dot)
    if scale != 1.0:
        G.xform(parts, G.S(scale))
    return parts
