"""Lobby_LotArch — entrance arch over the van lot (~44.4 wide x ~17.4 tall x 3.5 deep).

Two chunky brick pillars (cast-stone bases and caps, warm globe lamps, STACKHOUSE logo badges) carry
a curved navy steel box truss (front and back chord pairs, Warren web, cross ties). Big modelled
letters "SHIFT VANS" stand on the top chord, each one turned to follow the curve — red-orange faces
with cyan neon edging (LetterNeon, role "neon"). Warm marquee bulbs run along the front of the bottom
chord (Bulbs, role "lamp"); globe lamps on the pillar caps (Globes, role "lamp").
Clear opening: 36.4 wide between the pillars x 12.05 tall under the bottom chord at the pillars
(13.6 at the centre).

Front = -Y, pivot = bottom-centre. Sockets: Gate (ground centre of the opening, yaw 0 = drivers face
front through it), Sign (centre of the lettering, facing front: put the sign light here).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

PX0, PX1 = 18.2, 21.8         # pillar x span (mirrored); inner faces give a 36.4 opening
PY = 1.5                      # pillar half depth
P_TOP = 13.4
CHORD_END_X = 18.75           # chords run into the pillars
B_END_Z, B_MID_Z = 12.25, 13.5   # bottom chord centre at the pillar faces / centre (tube underside >= 12.07)
BAND = 1.25                   # radial distance bottom -> top chord
TY = 0.62                     # truss planes at y = +-TY
CH = 0.26                     # chord tube radius (4-sided: ~0.18 half width)
CAP = 2.6
LET_Y = -0.45                 # letter front face
LET_D = 0.7
BULB_R = 0.2


def arc_geom():
    """Radius and centre height of the bottom chord arc."""
    half = PX0
    s = B_MID_Z - B_END_Z
    R = (half ** 2 + s ** 2) / (2 * s)
    zc = B_MID_Z - R
    return R, zc


R_B, ZC = arc_geom()
R_T = R_B + BAND


def arc_pts(R, x0, x1, n):
    out = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        out.append((x, ZC + math.sqrt(R * R - x * x)))
    return out


def arc_slab(r0, r1, y0, y1, xmax, n):
    """Curved plate between radii r0 < r1 about the arch centre (0, ZC), spanning y0..y1, x -xmax..xmax."""
    import bmesh
    bm = bmesh.new()
    a_max = math.asin(xmax / r1)
    rings = []
    for i in range(n + 1):
        a = -a_max + 2 * a_max * i / n
        rings.append([bm.verts.new((r * math.sin(a), y, ZC + r * math.cos(a)))
                      for r, y in ((r0, y0), (r1, y0), (r1, y1), (r0, y1))])
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(4):
            kk = (k + 1) % 4
            bm.faces.new([a[k], a[kk], b[kk], b[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return C.obj_from_bm(bm, "Deck")


def build():
    # ----- pillars -------------------------------------------------------------------------------
    brick, stone, dark = [], [], []
    globes = []
    for s in (-1, 1):
        x0, x1 = sorted((s * PX0, s * PX1))
        xc, w = (x0 + x1) / 2, x1 - x0
        brick.append(ns.box((w, 2 * PY, P_TOP - 1.0), loc=(xc, 0, 1.0 + (P_TOP - 1.0) / 2), bevel=0.1, segments=1))
        stone.append(ns.box((w + 0.4, 2 * PY + 0.4, 1.0), loc=(xc, 0, 0.5), bevel=0.12, segments=1))
        stone.append(ns.box((w + 0.14, 2 * PY + 0.14, 0.4), loc=(xc, 0, 6.2), bevel=0.05, segments=1))
        stone.append(ns.box((w + 0.5, 2 * PY + 0.5, 0.5), loc=(xc, 0, P_TOP + 0.25), bevel=0.12, segments=1))
        stone.append(ns.box((w - 0.5, 2 * PY - 0.5, 0.3), loc=(xc, 0, P_TOP + 0.65), bevel=0.08, segments=1))
        dark.append(ns.cyl(0.55, 0.32, loc=(xc, 0, P_TOP + 0.96), verts=8, bevel=0.0))
        globes.append((xc, 0, P_TOP + 1.82))
    ns.tag(C.spheres(globes, 0.75, segs=10, rings=6), "Globes", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False,
           smooth_angle=80)
    badges = {}
    for s in (-1, 1):
        C.merge_into(badges, C.badge((s * (PX0 + PX1) / 2, -PY + 0.001, 8.8), r=1.15, n=12))

    # ----- truss ----------------------------------------------------------------------------------
    steel = []
    n = 20
    bot = arc_pts(R_B, -CHORD_END_X, CHORD_END_X, n)
    top_x = CHORD_END_X - 0.0
    top = arc_pts(R_T, -top_x, top_x, n)
    for y in (-TY, TY):
        steel.append(C.pipe([(x, y, z) for x, z in bot], CH, sides=4))
        steel.append(C.pipe([(x, y, z) for x, z in top], CH, sides=4))
    # Warren web on both planes + ties between the planes
    panels = 12
    xs = [-PX0 + 2 * PX0 * i / panels for i in range(panels + 1)]

    def zb(x):
        return ZC + math.sqrt(R_B * R_B - x * x)

    def zt(x):
        return ZC + math.sqrt(R_T * R_T - x * x)

    for y in (-TY, TY):
        for i in range(panels):
            xa, xb = xs[i], xs[i + 1]
            if i % 2 == 0:
                steel.append(C.rod((xa, y, zb(xa)), (xb, y, zt(xb)), 0.09, verts=4))
            else:
                steel.append(C.rod((xa, y, zt(xa)), (xb, y, zb(xb)), 0.09, verts=4))
    for i in range(0, panels + 1, 2):    # ties between the bottom chords (the deck ties the top ones)
        x = xs[i]
        steel.append(C.rod((x, -TY, zb(x)), (x, TY, zb(x)), 0.1, verts=4))

    # ----- letters on the top chord, each turned to the curve --------------------------------------
    # curved deck plate on the top chords; the letters stand on it
    deck_r0, deck_r1 = R_T + 0.1, R_T + 0.34
    steel.append(arc_slab(deck_r0, deck_r1, -TY - 0.22, TY + 0.22, CHORD_END_X - 0.3, 28))
    R_L = deck_r1 - 0.05                        # baseline radius (letters sit 0.05 into the deck)
    w = C.Word("SHIFT VANS", 0.0, cap=CAP, spacing=1.15, base=0.0, xscale=1.2)
    solid = w.solid(LET_Y, LET_D, offset=0.1, name="Letters")   # inflated: a heavier weight
    islands = C.split_islands(solid)
    info = []
    for isl in islands:
        xs_i = [solid.data.vertices[i].co.x for i in isl]
        info.append(((min(xs_i) + max(xs_i)) / 2, min(xs_i), max(xs_i), isl))

    def place_xz(x, z, cx):
        phi = cx / R_L
        px, pz = R_L * math.sin(phi), ZC + R_L * math.cos(phi)
        tx, tz = math.cos(phi), -math.sin(phi)
        nx, nz = math.sin(phi), math.cos(phi)
        dx = x - cx
        return px + dx * tx + z * nx, pz + dx * tz + z * nz

    for cx, _, _, isl in info:
        for i in isl:
            co = solid.data.vertices[i].co
            co.x, co.z = place_xz(co.x, co.z, cx)
    solid.data.update()
    C.part([solid], "Letters", C.BRAND, smooth_angle=30)
    tubes = []
    for lp in w.loops(offset=0.16):
        lx = sum(p[0] for p in lp) / len(lp)
        cx = min(info, key=lambda t: 0 if t[1] - 0.2 <= lx <= t[2] + 0.2 else abs(t[0] - lx))[0]
        pts = [(X, LET_Y + 0.02, Z) for X, Z in (place_xz(x, z, cx) for x, z in lp)]
        tubes.append(C.pipe(C._simplify(pts, 0.02), 0.11, sides=3, closed=True))
    ns.tag(C.merge(tubes, "LetterNeon"), "LetterNeon", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # ----- marquee bulbs along the front of the bottom chord ----------------------------------------
    fine = arc_pts(R_B, -PX0 + 0.5, PX0 - 0.5, 120)
    bpts = C.path_points([(x, -TY - CH * 0.7, z) for x, z in fine], 1.25)
    bulbs = C.domes(bpts, BULB_R, axis=(0, -1, 0), segs=6, rings=2)
    ns.tag(bulbs, "Bulbs", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=80)

    C.part(brick, "Pillars", C.BRICK, "Brick", can_collide=True, smooth_angle=40)
    C.part(stone, "Stone", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(steel, "Truss", C.STEEL_NAVY, "Metal", smooth_angle=50)
    C.part(dark, "LampBases", C.NAVY_DEEP, smooth_angle=40)
    C.part(badges.pop(C.BRAND), "BadgeRed", C.BRAND, smooth_angle=40)
    C.add_parts(badges, "Badge", smooth_angle=40)
    return {}


def sockets():
    zc = ZC + R_T + 0.29 + CAP / 2
    return {"Gate": ((0.0, 0.0, 0.0), 0.0), "Sign": ((0.0, LET_Y - 2.5, zc), 0.0)}


META = {
    "clear_opening": {"width": 2 * PX0, "height_at_pillars": B_END_Z, "height_at_centre": B_MID_Z},
    "lettering": "SHIFT VANS, cap 2.6, each letter turned to the arch",
    "roles": {"neon": "LetterNeon (cyan edging)", "lamp": "Bulbs (marquee along the bottom chord), Globes"},
    "light_hint": {"type": "PointLight", "at": "Socket_Sign", "color": C.LAMP_WARM, "range": 22, "brightness": 1.2},
}

if __name__ == "__main__":
    C.run(build, "Lobby_LotArch", sockets=sockets(), meta=META, budget=5000, far=True)
