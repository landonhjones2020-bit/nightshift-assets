"""Lobby_ApronShop — the APRONS outfitter boutique: the clear spot to get aprons (~32.5 x 20.5 x 16).

A navy boutique building (stone plinth, red-orange band, navy-deep cornice; sides and back plain
but finished) with an open front between two lit display windows:

  * Open front (centre): a chrome clothes rail with six flat aprons on chrome hangers, each with
    a neck loop, waist ties and a pocket, left to right as seen from the front: STACKHOUSE
    red-orange, red/white gingham (two-tone tiles), ketchup red with mustard splats, navy with an
    owl-ish yellow patch, navy/cream butcher stripes, chef white. Behind them a wood counter with
    the shop screen on the wall above it (Screen, 5 x 3), and a tall standing cheval mirror
    (MirrorGlass, role "mirror"). A mustard/cream striped awning shades the opening.
  * Display windows: three headless charcoal dress-form mannequins on chrome stands — two in the
    left window (Mannequin1 left, Mannequin2 right), one in the right window (Mannequin3) beside a
    stack of folded aprons. Each torso is an R15 UpperTorso envelope (2.0 wide x 1.6 tall x 1.0
    deep) with a LowerTorso-sized waist below; the game dresses them with real apron cosmetics.
    Label screens above them on the facade (Tag1..Tag3, 4.2 x 1.4). Windows are cream-lit recesses
    (LampStrips, role "lamp") behind glass panes (Glass, role "glass").
  * Roof sign: big APRONS letters (mustard, cyan neon outline tubes LetterNeon, role "neon") on a
    steel raceway, over a navy "& UNIFORMS" panel with pink neon letters (PanelNeon, role "neon").

Front = -Y, pivot = bottom-centre. Sockets: Mannequin1..3 (torso FRONT centre = the R15
BodyFrontAttachment spot, facing front), Tag1..3 and Screen (screen face centres), Mirror (glass
face centre, facing the way the mirror faces), PromptAprons (at the rail, y 3), PromptUniforms (at
the mannequin window, y 3).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

HX = 16.0
FY, WY, CY, BY = -6.0, -5.3, -1.3, 8.0     # facade face, front-slab back, window recess back, back face
OPEN_BACK = 3.0                            # open-front interior back wall
PLINTH = 0.6
BAND = (10.6, 11.2)
CORNICE = (11.2, 12.2)
WIN_L = (-15.5, -6.5, 1.2, 8.4)
WIN_R = (6.5, 15.5, 1.2, 8.4)
OPEN = (-5.5, 5.5, PLINTH + 0.05, 10.4)
FRAME = 0.3
TAG_W, TAG_H, TAG_Z = 4.2, 1.4, 9.55
MANNEQUINS = (-13.25, -8.75, 11.0)         # x of Mannequin1..3
M_Y = -3.3                                 # mannequin centre line (depth)
TORSO_W, TORSO_H, TORSO_D = 2.0, 1.6, 1.0
DISPLAY_FLOOR = WIN_L[2]
TORSO_Z0 = DISPLAY_FLOOR + 0.15 + 2.0 + 0.4      # base + R15 legs (hip height 2.0) + LowerTorso 0.4
RAIL_Y, RAIL_BAR_Z, RAIL_HX = -4.6, 5.85, 5.15
APRON_Y = RAIL_Y - 0.15
APRON_TOP = 4.95
APRON_XS = [-4.05 + 1.62 * i for i in range(6)]
SCR_W, SCR_H, SCR_Z = 5.0, 3.0, 7.4
SCR_Y = OPEN_BACK - 0.12
MIRROR_AT, MIRROR_YAW = (4.05, -0.6), -32.0
SIGN_CAP = 5.3
SIGN_BASE = 14.85
LET_Y = -6.3                               # APRONS letter front face
PANEL = (-6.8, 6.8, 12.2, 14.2)

FABRIC_DARK = "#33363C"
INTERIOR = "#EFE6D2"
WOOD = "#8A5A3B"
FLOOR_WOOD = "#A8774E"
GINGHAM_RED = "#D9472F"
WHITE = "#F4F2EC"
KETCHUP = "#D0262B"
CHEF_GREY = "#D3D7DB"
BEAK = "#F39A2B"
GLASS_TINT = "#D3E8EF"


def liner(x0, x1, z0, z1, y0, y1, bottom=True):
    """Open box (back, sides, top[, bottom]) with faces pointing INTO the recess."""
    bm = bmesh.new()
    v = {}
    for xi, x in enumerate((x0, x1)):
        for yi, y in enumerate((y0, y1)):
            for zi, z in enumerate((z0, z1)):
                v[(xi, yi, zi)] = bm.verts.new((x, y, z))
    quads = [[v[0, 1, 0], v[1, 1, 0], v[1, 1, 1], v[0, 1, 1]], [v[0, 0, 0], v[0, 1, 0], v[0, 1, 1], v[0, 0, 1]],
             [v[1, 0, 0], v[1, 0, 1], v[1, 1, 1], v[1, 1, 0]], [v[0, 0, 1], v[0, 1, 1], v[1, 1, 1], v[1, 0, 1]]]
    if bottom:
        quads.append([v[0, 0, 0], v[1, 0, 0], v[1, 1, 0], v[0, 1, 0]])
    for q in quads:
        bm.faces.new(q)
    bm.normal_update()
    ctr = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    for f in bm.faces:
        if (f.calc_center_median() - ctr).dot(f.normal) > 0:
            f.normal_flip()
    return C.obj_from_bm(bm, "Liner")


# ------------------------------------------------------------------------------------------------
# Aprons
# ------------------------------------------------------------------------------------------------
BIB, HW, AH = 0.36, 0.75, 2.3       # half bib width, half skirt width, apron height


def apron_outline(cx, top):
    """Apron silhouette (x, z), CCW: rounded bottom, straight sides, elliptical armholes, bib."""
    pts = []
    r = 0.16
    for k in range(3):   # bottom-left corner
        a = math.pi + (math.pi / 2) * k / 2
        pts.append((cx - HW + r + r * math.cos(a), top - AH + r + r * math.sin(a)))
    for k in range(3):   # bottom-right corner
        a = 1.5 * math.pi + (math.pi / 2) * k / 2
        pts.append((cx + HW - r + r * math.cos(a), top - AH + r + r * math.sin(a)))
    for k in range(5):   # right armhole: (HW, -0.95) up to (BIB, 0)
        t = (math.pi / 2) * (4 - k) / 4
        pts.append((cx + HW - (HW - BIB) * math.cos(t), top - 0.95 * math.sin(t)))
    for k in range(5):   # left armhole: (-BIB, 0) down to (-HW, -0.95)
        t = (math.pi / 2) * k / 4
        pts.append((cx - HW + (HW - BIB) * math.cos(t), top - 0.95 * math.sin(t)))
    return pts


def blob(cx, cz, r, n=9, seed=1):
    """Splat outline: a circle with lumpy radius."""
    import random
    rnd = random.Random(seed)
    return [(cx + r * (1 + rnd.uniform(-0.28, 0.32)) * math.cos(2 * math.pi * i / n),
             cz + r * (1 + rnd.uniform(-0.28, 0.32)) * math.sin(2 * math.pi * i / n)) for i in range(n)]


def apron(i, cx, groups):
    """Build apron i at x cx; adds objects to groups {colour: [objs]}; returns nothing."""
    top = APRON_TOP
    y = APRON_Y
    t = 0.07
    fy = y - t / 2                       # front face plane
    base_col, pocket_col = [(C.BRAND, C.MUSTARD), (WHITE, GINGHAM_RED), (KETCHUP, C.MUSTARD), (C.NAVY, C.MUSTARD),
                            (C.CREAM, C.NAVY), (WHITE, CHEF_GREY)][i]
    out = apron_outline(cx, top)
    body = C.prism(out, "y", fy, fy + t)
    groups.setdefault(base_col, []).append(body)
    # pocket (raised patch) + its top hem
    pk = C.prism(C.rrect(0.92, 0.52, 0.1, 1, cx, top - 1.62), "y", fy - 0.045, fy + 0.01)
    groups.setdefault(pocket_col, []).append(pk)
    # neck loop over the hanger bar, waist ties
    strap_col = C.CREAM if base_col not in (C.CREAM, WHITE) else C.NAVY
    loop = C.pipe([(cx - BIB + 0.07, y, top - 0.03), (cx - 0.3, y, top + 0.18), (cx - 0.12, y, top + 0.3),
                   (cx + 0.12, y, top + 0.3), (cx + 0.3, y, top + 0.18), (cx + BIB - 0.07, y, top - 0.03)], 0.045,
                  sides=4)
    ties = [C.pipe([(cx + s * (HW - 0.02), y, top - 0.97), (cx + s * (HW + 0.16), y - 0.02, top - 1.25),
                    (cx + s * (HW + 0.12), y - 0.03, top - 1.6)], 0.04, sides=4) for s in (-1, 1)]
    groups.setdefault(strap_col, []).extend([loop] + ties)
    py = fy - 0.022                      # pattern plane (front-only polygons)
    if i == 1:   # gingham: red checker cells clipped to the silhouette (two-tone tiles)
        cell = 0.25
        inset = C.rrect(2 * HW - 0.06, AH - 0.06, 0.13, 2, cx, top - AH / 2)   # keeps a thin white hem
        for gx in range(6):
            for gz in range(10):
                if (gx + gz) % 2:
                    continue
                x0 = cx - HW + gx * cell
                z1 = top - gz * cell
                poly = C.clip_rect(out, x0, x0 + cell, z1 - cell, z1)
                poly = [p for p in poly]
                if len(poly) >= 3:
                    shrunk = [(cx + (x - cx) * 0.985, top - AH / 2 + (z - (top - AH / 2)) * 0.985) for x, z in poly]
                    groups.setdefault(GINGHAM_RED, []).append(C.flat_poly(shrunk, py))
    elif i == 2:  # ketchup red with mustard (and one cream) splats
        for (dx, dz, r, sd), col in (((0.28, -0.62, 0.2, 3), C.MUSTARD), ((-0.32, -1.25, 0.24, 5), C.MUSTARD),
                                     ((0.36, -2.0, 0.15, 8), C.CREAM), ((-0.1, -0.3, 0.1, 11), C.MUSTARD)):
            groups.setdefault(col, []).append(C.flat_poly(blob(cx + dx, top + dz, r, seed=sd), py))
    elif i == 3:  # navy with an owl-ish yellow patch
        patch = C.circle_pts(0.34, 14, cx, top - 0.5)
        ears = [C.flat_poly([(cx + s * 0.3, top - 0.32), (cx + s * 0.13, top - 0.2), (cx + s * 0.31, top - 0.06)], py)
                for s in (-1, 1)]
        groups.setdefault(C.MUSTARD, []).extend([C.flat_poly(patch, py)] + ears)
        eyes = [C.flat_poly(C.circle_pts(0.12, 10, cx + s * 0.13, top - 0.45), py - 0.015) for s in (-1, 1)]
        pupils = [C.flat_poly(C.circle_pts(0.055, 8, cx + s * 0.13, top - 0.46), py - 0.03) for s in (-1, 1)]
        beak = C.flat_poly([(cx - 0.07, top - 0.58), (cx + 0.07, top - 0.58), (cx, top - 0.7)], py - 0.015)
        groups.setdefault(WHITE, []).extend(eyes)
        groups.setdefault(C.NAVY_DEEP, []).extend(pupils)
        groups.setdefault(BEAK, []).append(beak)
    elif i == 4:  # butcher stripes: navy bands clipped to the silhouette
        for k in range(5):
            a = cx - HW + 0.09 + k * 0.32
            poly = C.clip_band(out, a, a + 0.16)
            if len(poly) >= 3:
                groups.setdefault(C.NAVY, []).append(C.flat_poly(poly, py))
    elif i == 5:  # chef white: a red-orange pen clipped in the pocket
        groups.setdefault(C.BRAND, []).append(C.rod((cx + 0.22, fy - 0.07, top - 1.62), (cx + 0.26, fy - 0.07, top - 1.08),
                                                    0.04, verts=6))
    elif i == 0:  # brand apron: a small mustard star on the bib
        groups.setdefault(C.MUSTARD, []).append(C.flat_poly(C.star_pts(0.17, 0.075, cx, top - 0.42), py))


def rail_and_hangers(chrome):
    for s in (-1, 1):   # uprights with T-feet
        x = s * RAIL_HX
        chrome.append(C.rod((x, RAIL_Y, OPEN[2]), (x, RAIL_Y, RAIL_BAR_Z + 0.05), 0.09, verts=8))
        chrome.append(C.rod((x, RAIL_Y - 0.65, OPEN[2] + 0.08), (x, RAIL_Y + 0.65, OPEN[2] + 0.08), 0.07, verts=6))
    chrome.append(C.rod((-RAIL_HX - 0.12, RAIL_Y, RAIL_BAR_Z), (RAIL_HX + 0.12, RAIL_Y, RAIL_BAR_Z), 0.08, verts=8))
    for cx in APRON_XS:   # hook over the bar + wire hanger
        y = APRON_Y
        chrome.append(C.pipe([(cx, RAIL_Y + 0.1, RAIL_BAR_Z - 0.05), (cx, RAIL_Y + 0.1, RAIL_BAR_Z + 0.13),
                              (cx, y, RAIL_BAR_Z + 0.13), (cx, y, APRON_TOP + 0.6)], 0.03, sides=4))
        hz = APRON_TOP + 0.3
        chrome.append(C.pipe([(cx - 0.62, y, hz), (cx, y, APRON_TOP + 0.6), (cx + 0.62, y, hz), (cx - 0.62, y, hz)], 0.03,
                             sides=4))


# ------------------------------------------------------------------------------------------------
# Mannequins
# ------------------------------------------------------------------------------------------------

def mannequin(x):
    """Headless dress form on a chrome stand. Returns (fabric, chrome, brass)."""
    y = M_Y
    z0 = TORSO_Z0
    torso = C.loft([(z0 + 0.0, 1.7, 0.86, 0.4), (z0 + 0.45, 1.86, 0.94, 0.44), (z0 + 0.95, 2.0, 1.0, 0.46),
                    (z0 + 1.32, 2.0, 0.96, 0.44), (z0 + 1.52, 1.72, 0.8, 0.38), (z0 + TORSO_H, 1.1, 0.6, 0.28)],
                   segs=2, cx=x, cy=y)
    waist = C.loft([(z0 - 0.42, 1.74, 0.88, 0.4), (z0 - 0.08, 1.8, 0.9, 0.42), (z0 + 0.01, 1.7, 0.86, 0.4)], segs=2,
                   cx=x, cy=y, cap_top=False)
    neck = ns.cyl(0.3, 0.3, loc=(x, y, z0 + TORSO_H + 0.12), verts=8, bevel=0.0)
    fabric = [torso, waist, neck]
    chrome = [C.rod((x, y, DISPLAY_FLOOR + 0.1), (x, y, z0 - 0.4), 0.075, verts=8),
              ns.cyl(0.82, 0.14, loc=(x, y, DISPLAY_FLOOR + 0.07), verts=12, bevel=0.04, segments=1),
              ns.cyl(0.22, 0.2, loc=(x, y, DISPLAY_FLOOR + 0.24), verts=8, bevel=0.0)]
    brass = [ns.sphere(0.2, loc=(x, y, z0 + TORSO_H + 0.36), scale=(1, 1, 0.8), segs=8, rings=4),
             ns.cyl(0.16, 0.12, loc=(x, y, z0 - 0.48), verts=8, bevel=0.0)]
    return fabric, chrome, brass


def cheval_mirror():
    """Tall standing mirror built at the origin facing -Y, then turned to MIRROR_YAW.
    Returns (frame_objs, glass, glass_centre)."""
    gw, gh, gz = 1.4, 4.0, 3.75
    frame = [C.ring_slab(C.rrect(gw + 0.34, gh + 0.34, 0.75, 3, 0, gz), C.rrect(gw, gh, 0.6, 3, 0, gz), "y", -0.07, 0.07)]
    frame.append(C.prism(C.rrect(gw, gh, 0.6, 3, 0, gz), "y", 0.0, 0.06))                     # backing board
    glass = C.prism(C.rrect(gw - 0.02, gh - 0.02, 0.59, 3, 0, gz), "y", -0.04, 0.005)
    for s in (-1, 1):
        x = s * (gw / 2 + 0.3)
        frame.append(C.rod((x, 0, OPEN[2]), (x, 0, gz + 0.3), 0.08, verts=6))
        frame.append(C.rod((x, -0.55, OPEN[2] + 0.04), (x, 0.55, OPEN[2] + 0.04), 0.07, verts=6))
        frame.append(C.rod((x, 0, gz + 0.1), (s * (gw / 2 + 0.12), 0, gz + 0.1), 0.06, verts=6))   # pivot pins
    objs = frame + [glass]
    C.place(objs, (MIRROR_AT[0], MIRROR_AT[1], 0.0), yaw=MIRROR_YAW)
    a = math.radians(MIRROR_YAW)
    ctr = (MIRROR_AT[0] + 0.04 * math.sin(a), MIRROR_AT[1] - 0.04 * math.cos(a), gz)
    return frame, glass, ctr


def build():
    navy, deep, band, stone, cream, chrome, interior, lamps, glass = [], [], [], [], [], [], [], [], []
    groups = {}
    # ----- shell (outer walls only; recesses are lined, the enclosed void is never seen) ------------
    stone.append(ns.box((2 * HX + 0.4, BY - FY + 0.4, PLINTH), loc=(0, (FY + BY) / 2, PLINTH / 2), bevel=0.1, segments=1))

    def slab(x0, x1, z0, z1):
        navy.append(ns.box((x1 - x0, WY - FY, z1 - z0), loc=((x0 + x1) / 2, (FY + WY) / 2, (z0 + z1) / 2), bevel=0.0))

    for s in (-1, 1):
        slab(*sorted((s * 15.5, s * HX)), PLINTH, BAND[0])          # end piers
        slab(*sorted((s * 5.5, s * 6.5)), PLINTH, BAND[0])          # piers beside the open front
        wx0, wx1 = sorted((s * 6.5, s * 15.5))
        slab(wx0, wx1, PLINTH, WIN_L[2] - 0.2)                      # under the sills
        slab(wx0, wx1, WIN_L[3], BAND[0])                           # above the windows (tags)
        stone.append(ns.box((wx1 - wx0 + 0.4, WY - FY + 0.3, 0.2), loc=((wx0 + wx1) / 2, (FY + WY) / 2 - 0.15, WIN_L[2] - 0.1),
                            bevel=0.04, segments=1))
        navy.append(ns.box((0.4, BY - WY, BAND[0] - PLINTH), loc=(s * (HX - 0.2), (WY + BY) / 2, (PLINTH + BAND[0]) / 2),
                           bevel=0.0))                               # side walls
    slab(OPEN[0], OPEN[1], OPEN[3], BAND[0])                         # header over the open front
    navy.append(ns.box((2 * HX - 0.8, 0.4, BAND[0] - PLINTH), loc=(0, BY - 0.2, (PLINTH + BAND[0]) / 2), bevel=0.0))
    band.append(ns.box((2 * HX + 0.16, BY - FY + 0.16, BAND[1] - BAND[0]), loc=(0, (FY + BY) / 2, sum(BAND) / 2), bevel=0.04,
                       segments=1))
    deep.append(ns.box((2 * HX + 0.5, BY - FY + 0.5, CORNICE[1] - CORNICE[0]), loc=(0, (FY + BY) / 2, sum(CORNICE) / 2),
                       bevel=0.1, segments=1))
    pins = [ns.box((2 * HX + 0.56, BY - FY + 0.56, 0.12), loc=(0, (FY + BY) / 2, CORNICE[0] + 0.3), bevel=0.0)]
    # back door
    deep.append(ns.box((4.0, 0.2, 7.0), loc=(-8.0, BY + 0.08, PLINTH + 3.5), bevel=0.04, segments=1))
    chrome.append(ns.box((0.25, 0.25, 0.9), loc=(-6.5, BY + 0.25, PLINTH + 3.3), bevel=0.05, segments=1))
    stone.append(ns.box((4.8, 0.3, 0.45), loc=(-8.0, BY + 0.1, PLINTH + 7.2), bevel=0.05, segments=1))

    # ----- recesses ------------------------------------------------------------------------------------
    for (x0, x1, z0, z1) in (WIN_L, WIN_R):
        interior.append(liner(x0, x1, z0, z1, WY, CY))
        glass.append(ns.box((x1 - x0 + 0.1, 0.06, z1 - z0 + 0.1), loc=((x0 + x1) / 2, FY + 0.45, (z0 + z1) / 2), bevel=0.0))
        lamps.append(ns.box((x1 - x0 - 0.6, 0.22, 0.14), loc=((x0 + x1) / 2, WY + 0.25, z1 - 0.06), bevel=0.0))
    for (x0, x1, z0, z1) in (WIN_L, WIN_R):
        fo = C.rrect(x1 - x0 + 2 * FRAME, z1 - z0 + 2 * FRAME, 0.25, 2, (x0 + x1) / 2, (z0 + z1) / 2)
        fi = C.rrect(x1 - x0 - 0.12, z1 - z0 - 0.12, 0.08, 2, (x0 + x1) / 2, (z0 + z1) / 2)
        cream.append(C.ring_slab(fo, fi, "y", FY - 0.2, FY + 0.05))
    # open front: two jambs standing on the plinth + a header bar (a U, not a ring)
    for xa, xb in ((OPEN[0] - FRAME, OPEN[0] + 0.06), (OPEN[1] - 0.06, OPEN[1] + FRAME)):
        cream.append(ns.box((xb - xa, 0.25, OPEN[3] - 0.06 - PLINTH), loc=((xa + xb) / 2, FY - 0.075, (PLINTH + OPEN[3] - 0.06) / 2),
                            bevel=0.05, segments=1))    # jambs stop under the header bar (no shared front face)
    cream.append(ns.box((OPEN[1] - OPEN[0] + 2 * FRAME, 0.25, FRAME + 0.06), loc=(0, FY - 0.075, OPEN[3] + (FRAME - 0.06) / 2),
                        bevel=0.05, segments=1))
    interior.append(liner(OPEN[0], OPEN[1], OPEN[2], OPEN[3], WY, OPEN_BACK, bottom=False))
    floor = ns.box((OPEN[1] - OPEN[0], OPEN_BACK - FY, 0.05), loc=(0, (FY + OPEN_BACK) / 2, PLINTH + 0.025), bevel=0.0)
    C.part([floor], "ShopFloor", FLOOR_WOOD, "WoodPlanks", smooth_angle=None)
    lamps.append(ns.box((OPEN[1] - OPEN[0] - 0.6, 0.22, 0.14), loc=(0, WY + 0.25, OPEN[3] - 0.06), bevel=0.0))
    lamps.append(ns.box((OPEN[1] - OPEN[0] - 0.6, 0.22, 0.14), loc=(0, OPEN_BACK - 0.35, OPEN[3] - 0.06), bevel=0.0))

    # ----- tags ----------------------------------------------------------------------------------------
    for i, x in enumerate(MANNEQUINS):
        s = C.prism(C.rrect(TAG_W, TAG_H, 0.1, 1, x, TAG_Z), "y", FY - 0.12, FY + 0.02)
        ns.tag(s, f"Tag{i + 1}", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
        chrome.append(C.ring_slab(C.rrect(TAG_W + 0.24, TAG_H + 0.24, 0.16, 1, x, TAG_Z), C.rrect(TAG_W, TAG_H, 0.1, 1, x, TAG_Z),
                                  "y", FY - 0.17, FY + 0.02))

    # ----- awning over the open front -------------------------------------------------------------------
    aw = C.awning(-6.3, 6.3, FY + 0.12, BAND[0] - 0.1, FY - 2.45, 9.8, n=8, t=0.08, valance=0.42, cols=(C.MUSTARD, C.PAPER))

    # ----- rail + aprons ----------------------------------------------------------------------------------
    rail_and_hangers(chrome)
    for i, cx in enumerate(APRON_XS):
        apron(i, cx, groups)

    # ----- counter + screen + mirror ------------------------------------------------------------------------
    wood = [ns.box((5.2, 1.4, 2.25), loc=(0, OPEN_BACK - 1.0, PLINTH + 0.05 + 1.125), bevel=0.06, segments=1)]
    cream.append(C.prism(C.rrect(5.6, 1.7, 0.12, 1, 0, OPEN_BACK - 1.05), "z", 2.85, 3.0))
    chrome.append(ns.box((5.0, 0.06, 0.24), loc=(0, OPEN_BACK - 1.72, PLINTH + 0.2), bevel=0.0))
    pins.append(ns.box((4.6, 0.05, 0.12), loc=(0, OPEN_BACK - 1.72, 2.45), bevel=0.0))
    scr = C.prism(C.rrect(SCR_W, SCR_H, 0.1, 1, 0, SCR_Z), "y", SCR_Y, OPEN_BACK + 0.02)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
    chrome.append(C.ring_slab(C.rrect(SCR_W + 0.3, SCR_H + 0.3, 0.2, 1, 0, SCR_Z), C.rrect(SCR_W, SCR_H, 0.1, 1, 0, SCR_Z),
                              "y", SCR_Y - 0.06, OPEN_BACK + 0.01))
    for sx in (-1, 1):
        for zs in (4.2, 5.9):
            xc = sx * 4.1
            wood.append(ns.box((2.2, 0.75, 0.14), loc=(xc, OPEN_BACK - 0.375, zs), bevel=0.03, segments=1))
            cols = (C.BRAND, C.NAVY, GINGHAM_RED) if (sx + int(zs)) % 2 else (C.MUSTARD, WHITE, KETCHUP)
            for k, col in enumerate(cols):
                groups.setdefault(col, []).append(ns.box((0.58, 0.55, 0.42), loc=(xc - 0.68 + 0.68 * k, OPEN_BACK - 0.36,
                                                                                    zs + 0.28), bevel=0.04, segments=1))
    mframe, mglass, mctr = cheval_mirror()
    ns.tag(C.merge([mglass], "MirrorGlass"), "MirrorGlass", "#C9DCE3", "Glass", recolor="mirror", cast_shadow=False,
           smooth_angle=30)

    # ----- mannequins + folded aprons --------------------------------------------------------------------------
    fabric, brass = [], []
    for x in MANNEQUINS:
        f, ch, br = mannequin(x)
        fabric += f
        chrome += ch
        brass += br
    stack_x = 13.75
    cream.append(ns.box((1.3, 1.3, 0.9), loc=(stack_x, M_Y + 0.2, DISPLAY_FLOOR + 0.45), bevel=0.06, segments=1))
    for k, col in enumerate((C.BRAND, C.NAVY, WHITE, C.MUSTARD)):
        groups.setdefault(col, []).append(ns.box((1.0, 0.8, 0.16), loc=(stack_x + 0.03 * (k % 2), M_Y + 0.2,
                                                                          DISPLAY_FLOOR + 0.98 + 0.165 * k),
                                                 rot=(0, 0, 4 * (k % 3 - 1)), bevel=0.04, segments=1))

    # ----- roof sign ---------------------------------------------------------------------------------------------
    w = C.Word("APRONS", 0.0, cap=SIGN_CAP, spacing=1.04, base=SIGN_BASE, xscale=0.94)
    letters = w.solid(LET_Y, 1.0, name="Letters")
    C.part([letters], "Letters", C.MUSTARD, smooth_angle=30)
    tubes = C.contour_tubes(w.loops(offset=0.06), LET_Y + 0.02, 0.13, sides=4)
    ns.tag(tubes, "LetterNeon", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    steel = [ns.box((2 * 14.0, 0.6, 0.65), loc=(0, LET_Y + 1.3, SIGN_BASE + 0.25), bevel=0.05, segments=1)]
    for x in (-10.0, 0.0, 10.0):
        steel.append(ns.box((0.5, 0.5, SIGN_BASE + 0.3 - CORNICE[1]), loc=(x, LET_Y + 1.9, (CORNICE[1] + SIGN_BASE + 0.3) / 2),
                            bevel=0.04, segments=1))
        steel.append(C.rod((x, LET_Y + 1.9, SIGN_BASE - 0.4), (x, LET_Y + 4.2, CORNICE[1]), 0.12, verts=6))
    px0, px1, pz0, pz1 = PANEL
    pnl = C.prism(C.rrect(px1 - px0, pz1 - pz0, 0.35, 2, 0, (pz0 + pz1) / 2), "y", FY - 0.35, FY + 0.4)
    ns.bevel(pnl, width=0.05, segments=1)
    deep.append(pnl)
    chrome.append(C.ring_slab(C.rrect(px1 - px0 + 0.24, pz1 - pz0 + 0.24, 0.45, 2, 0, (pz0 + pz1) / 2),
                              C.rrect(px1 - px0 - 0.06, pz1 - pz0 - 0.06, 0.32, 2, 0, (pz0 + pz1) / 2), "y", FY - 0.42, FY - 0.2))
    uw = C.Word("& UNIFORMS", 0.0, cap=1.1, spacing=1.12, base=(pz0 + pz1) / 2 - 0.55)
    uw.res = 1
    ns.tag(uw.solid(FY - 0.45, 0.06, front_only=True, name="PanelNeon"), "PanelNeon", C.PINK, "Neon", recolor="neon",
           cast_shadow=False, smooth_angle=30)

    # ----- tag parts -------------------------------------------------------------------------------------------
    C.part(navy, "Facade", C.NAVY, can_collide=True, smooth_angle=40)
    C.part(deep, "Cornice", C.NAVY_DEEP, can_collide=True, smooth_angle=40)
    C.part(band, "RedBand", C.BRAND, can_collide=True, smooth_angle=40)
    C.part(stone, "Stone", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(cream, "CreamTrim", C.CREAM, smooth_angle=40)
    C.part(interior, "Interior", INTERIOR, smooth_angle=None)
    C.part(chrome + steel, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    C.part(brass + mframe[:1] + mframe[2:], "Brass", C.BRASS, "Metal", smooth_angle=45)
    C.part(fabric, "DressForms", FABRIC_DARK, "Fabric", smooth_angle=50)
    C.part(wood + mframe[1:2], "Counter", WOOD, "Wood", can_collide=True, smooth_angle=40)
    C.part(pins, "Pinstripe", C.MUSTARD, smooth_angle=40)
    C.part(aw[C.MUSTARD] + groups.pop(C.MUSTARD, []), "MustardCloth", C.MUSTARD, "Fabric", smooth_angle=None)
    C.part(aw[C.PAPER], "AwningCream", C.PAPER, "Fabric", smooth_angle=None)
    ns.tag(C.merge(lamps, "LampStrips"), "LampStrips", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False,
           smooth_angle=40)
    ns.tag(C.merge(glass, "Glass"), "Glass", GLASS_TINT, "Glass", transparency=0.8, recolor="glass", cast_shadow=False,
           smooth_angle=30)
    names = {C.BRAND: "ApronRed", WHITE: "ApronWhite", KETCHUP: "ApronKetchup", C.NAVY: "ApronNavy",
             C.CREAM: "ApronCream", GINGHAM_RED: "ApronGingham", CHEF_GREY: "ApronGrey", C.NAVY_DEEP: "ApronDark",
             BEAK: "ApronBeak"}
    for col, objs in groups.items():
        C.part(objs, names.get(col, "Apron" + col.lstrip("#")), col, "Fabric", smooth_angle=None)
    return {"mirror": mctr}


def sockets():
    s = {"Screen": ((0.0, SCR_Y, SCR_Z), 0.0),
         "PromptAprons": ((0.0, FY + 0.1, 3.0), 0.0),
         "PromptUniforms": (((WIN_L[0] + WIN_L[1]) / 2, FY - 1.2, 3.0), 0.0)}
    for i, x in enumerate(MANNEQUINS):
        s[f"Mannequin{i + 1}"] = ((x, M_Y - TORSO_D / 2, TORSO_Z0 + TORSO_H / 2), 0.0)
        s[f"Tag{i + 1}"] = ((x, FY - 0.12, TAG_Z), 0.0)
    a = math.radians(MIRROR_YAW)
    s["Mirror"] = ((MIRROR_AT[0] + 0.04 * math.sin(a), MIRROR_AT[1] - 0.04 * math.cos(a), 3.75), MIRROR_YAW)
    return s


META = {
    "screens": {"Screen": [SCR_W, SCR_H], "Tag1": [TAG_W, TAG_H], "Tag2": [TAG_W, TAG_H], "Tag3": [TAG_W, TAG_H]},
    "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)] + [C.screen_meta(f"Tag{i + 1}", TAG_W, TAG_H) for i in range(3)],
    "mannequin_torso_width": TORSO_W,
    "mannequin_torso_size": [TORSO_W, TORSO_H, TORSO_D],
    "mannequin_socket": "torso front centre (R15 BodyFrontAttachment spot); the torso centre is 0.5 behind it "
                        "(Roblox +Z of the socket), LowerTorso-sized waist below, chrome stand",
    "mannequin_order": "Mannequin1 / Mannequin2 left window (left, right as seen from the front), Mannequin3 right window",
    "apron_order": ["STACKHOUSE red-orange", "red/white gingham", "ketchup red with splats", "navy with owl patch",
                    "butcher stripes navy/cream", "chef white"],
    "apron_order_note": "left to right as seen from the front, on the rail in the open front",
    "roles": {"screen": "Screen, Tag1, Tag2, Tag3", "glass": "Glass (2 window panes)", "mirror": "MirrorGlass",
              "neon": "LetterNeon (cyan APRONS outlines), PanelNeon (pink & UNIFORMS)", "lamp": "LampStrips"},
    "light_hint": {"sign": {"type": "PointLight", "at": "3 studs in front of the letters", "color": C.CYAN,
                            "range": 24, "brightness": 1.2},
                   "windows": {"type": "PointLight", "per": "window + shop interior", "color": C.LAMP_WARM, "range": 10,
                               "brightness": 1}},
}

if __name__ == "__main__":
    C.run(build, "Lobby_ApronShop", sockets=sockets(), meta=META, budget=9000, far=True)
