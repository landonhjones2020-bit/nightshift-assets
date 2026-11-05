"""Lobby_ClassShop — the CLASS SHOP: the biggest storefront on the lobby's shop row (~48 x 42.7 x 20).

2026-11-04 (Landon: "it's also purposeful to have the Class shop as the biggest since that will
likely be the strongest income driver"). A grand two-storey uniform outfitter in navy and cream
with gold trim, taller than every other building in the lobby:

  * Ground floor: two lit display windows with three full mannequins each, dressed as the six
    classes (Config.Uniforms, left to right as seen from the front): Trainee (white shirt, red
    paper cap), Line Cook (blue, white skull cap + neckerchief), Stock Runner (green, red cap),
    Security Guard (navy, peaked cap + gold star), Night Manager (purple, gold tie + name badge),
    Head Chef (white, tall toque, gold buttons). Each shirt is its own part (role shirt1..shirt6)
    so the map can repaint it from the config. Round marble pedestals ring-lit in warm light.
    Label screens over the windows (Tag1..Tag6).
  * Centre: recessed double glass doors under a theatre canopy whose fascia carries a gold
    "CLASSES" sign framed by marquee bulbs.
  * Upper floor: the big class screen (Screen) in a gold frame between two arched windows lit
    from inside; cream pilasters with gold capitals; red-orange brand band with a gold pinstripe.
  * Roof: a navy sign box with GIANT gold "CLASS SHOP" letters, warm bulbs along every letter
    stroke (Broadway style), cyan neon outlines and a marquee frame; on top, a gold-ringed crest
    with a white chef's toque and two stars. Two flood lamps on the cornice.

Front = -Y, pivot = bottom-centre. Sockets: Screen, Tag1..6 (screen face centres), Mannequin1..6
(torso front centres), Pad (on the ground in front), Flood1/2 (lamp lenses), Sign (sign face
centre). All screens face front.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

HX = 24.0
FY, WY, CY, BY = -8.0, -7.2, -3.4, 12.0    # facade face, front-slab back, recess back, back face
PLINTH = 0.9
BAND = (13.4, 14.4)
TOP = 24.0
CORNICE = (24.0, 25.4)
PILASTERS = ((-24.0, -22.2), (-8.2, -6.4), (6.4, 8.2), (22.2, 24.0))
PIL_PROUD = 0.45
WIN_L = (-21.2, -9.4, 2.1, 10.8)
WIN_R = (9.4, 21.2, 2.1, 10.8)
DOOR = (-5.0, 5.0, PLINTH, 10.2)
DOOR_Y = -4.9                                # door leaves plane (recessed)
FRAME = 0.32
MAN_X = (-19.0, -15.3, -11.6, 11.6, 15.3, 19.0)
M_Y = -5.2                                   # mannequin centre line (depth)
DISPLAY_FLOOR = WIN_L[2]
PED_R, PED_H = 1.2, 0.35
TAG_W, TAG_H, TAG_Z = 3.3, 1.15, 12.25
SCR_W, SCR_H, SCR_Z = 11.4, 6.0, 19.2
SCR_Y = FY - 0.32
ARCH_X, ARCH_W, ARCH_H, ARCH_Z0 = 15.3, 6.0, 7.6, 15.3
CANOPY = (-6.4, 6.4)                         # canopy x extent
CAN_D = 3.4                                  # canopy projection
CAN_Z = (10.6, 11.4)                         # canopy roof slab
FASCIA_Z = (10.3, 12.9)
SIGN = (-22.4, 22.4, 26.0, 34.4)
SIGN_Y = (-8.7, -7.0)                        # sign box front / back
SIGN_CAP = 5.3
CREST_Z, CREST_R = 38.6, 3.9

NAVY_FACADE = "#22305A"
GOLD_TRIM = "#E5B43C"
GOLD_LETTER = "#FFC93C"
INTERIOR = "#F1E7D4"
PANTS = "#2A2D33"
SKIN = "#D9D2C6"
GLASS_TINT = "#D3E8EF"
MARBLE = "#EFE9DE"

# Config.Uniforms looks (ids in mannequin order) — the map repaints shirts from the config too
CLASSES = [("trainee", "#F4F1EA"), ("line_cook", "#2E9BFF"), ("stock_runner", "#4CFF7A"),
           ("security_guard", "#1B2A4A"), ("night_manager", "#9B5CFF"), ("head_chef", "#F4F1EA")]


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
# Mannequins
# ------------------------------------------------------------------------------------------------

def mannequin(i, x, groups, shirts):
    """A full display mannequin dressed as class i (0..5) at x, standing on its pedestal.
    Adds pieces to groups {colour: [objs]}; the shirt goes to shirts[i]."""
    y = M_Y
    z_base = DISPLAY_FLOOR + PED_H
    hip = z_base + 0.12 + 2.0
    z0 = hip + 0.35                                   # torso bottom
    th = 1.6
    shirt_col = CLASSES[i][1]
    add = lambda col, o: groups.setdefault(col, []).append(o)  # noqa: E731
    # stand + legs + hips
    add(C.CHROME, ns.cyl(0.62, 0.12, loc=(x, y, z_base + 0.06), verts=10, bevel=0.03, segments=1))
    for s in (-1, 1):
        add(PANTS, C.rod((x + s * 0.3, y, z_base + 0.12), (x + s * 0.32, y, hip + 0.05), 0.22, verts=6, r_top=0.27))
        add(C.CHARCOAL, ns.box((0.42, 0.62, 0.2), loc=(x + s * 0.3, y - 0.12, z_base + 0.22), bevel=0.06, segments=1))
    add(PANTS, C.loft([(hip - 0.1, 1.3, 0.72, 0.3), (hip + 0.2, 1.36, 0.76, 0.32), (z0 + 0.02, 1.4, 0.78, 0.33)],
                      segs=2, cx=x, cy=y))
    # torso (the shirt)
    torso = C.loft([(z0, 1.42, 0.8, 0.34), (z0 + 0.5, 1.56, 0.86, 0.38), (z0 + 1.05, 1.72, 0.9, 0.4),
                    (z0 + 1.4, 1.74, 0.86, 0.38), (z0 + th, 1.4, 0.72, 0.3), (z0 + th + 0.08, 0.7, 0.5, 0.2)],
                   segs=2, cx=x, cy=y)
    shirts[i].append(torso)
    # arms: sleeve + hand
    for s in (-1, 1):
        sh = (x + s * 0.96, y, z0 + th - 0.18)
        el = (x + s * 1.12, y - 0.05, z0 + 0.55)
        hand = (x + s * 1.08, y - 0.18, z0 - 0.15)
        shirts[i].append(C.rod(sh, el, 0.23, verts=6))
        add(SKIN, C.rod(el, hand, 0.17, verts=6))
        add(SKIN, ns.sphere(0.19, loc=hand, scale=(0.8, 0.8, 1.1), segs=6, rings=4))
    # neck + head
    add(SKIN, ns.cyl(0.2, 0.32, loc=(x, y, z0 + th + 0.2), verts=8, bevel=0.0))
    hz = z0 + th + 0.72
    add(SKIN, ns.sphere(0.46, loc=(x, y, hz), scale=(0.92, 0.92, 1.1), segs=10, rings=6))
    top = hz + 0.5
    # class accessories
    if i == 0:      # Trainee: red paper (garrison) cap
        cap = C.prism([(-0.44, 0), (0.44, 0), (0.3, 0.34), (-0.3, 0.34)], "y", -0.27, 0.27)
        C.place([cap], (x, y, top - 0.14))
        add(C.BRAND, cap)
    elif i == 1:    # Line Cook: white skull cap + neckerchief
        add(C.PAPER, ns.sphere(0.48, loc=(x, y, hz + 0.12), scale=(0.98, 0.98, 0.72), segs=10, rings=5))
        add(C.PAPER, C.prism([(-0.36, z0 + th - 0.02), (0.36, z0 + th - 0.02), (0.0, z0 + th - 0.5)], "y",
                             y - 0.47, y - 0.36))
    elif i == 2:    # Stock Runner: red ball cap
        add(C.BRAND, ns.sphere(0.5, loc=(x, y, hz + 0.1), scale=(0.98, 0.98, 0.7), segs=10, rings=5))
        add(C.BRAND, ns.box((0.62, 0.5, 0.06), loc=(x, y - 0.68, hz + 0.08), bevel=0.02, segments=1))
    elif i == 3:    # Security Guard: navy peaked cap with a gold badge, gold star on the chest
        add(C.NAVY_DEEP, ns.cyl(0.52, 0.3, loc=(x, y, top - 0.02), verts=12, bevel=0.03, segments=1, radius_top=0.6))
        add(C.CHARCOAL, ns.box((0.66, 0.42, 0.06), loc=(x, y - 0.6, top - 0.15), bevel=0.02, segments=1))
        add(C.GOLD, C.prism(C.star_pts(0.14, 0.06, x, top - 0.02), "y", y - 0.63, y - 0.55))
        add(C.GOLD, C.prism(C.star_pts(0.2, 0.09, x - 0.42, z0 + 1.15), "y", y - 0.5, y - 0.42))
    elif i == 4:    # Night Manager: gold tie + name badge
        add(C.GOLD, C.prism([(x - 0.08, z0 + th - 0.08), (x + 0.08, z0 + th - 0.08), (x + 0.14, z0 + 0.55), (x, z0 + 0.4),
                             (x - 0.14, z0 + 0.55)], "y", y - 0.52, y - 0.42))
        add(C.PAPER, ns.box((0.42, 0.06, 0.2), loc=(x + 0.42, y - 0.46, z0 + 1.2), bevel=0.02, segments=1))
    elif i == 5:    # Head Chef: tall toque + gold buttons
        band_ = ns.cyl(0.47, 0.42, loc=(x, y, top + 0.02), verts=12, bevel=0.0)
        puff = [ns.sphere(0.36, loc=(x + dx, y + dy, top + 0.68), segs=8, rings=5)
                for dx, dy in ((-0.2, -0.12), (0.2, -0.12), (0.0, 0.2))]
        puff.append(ns.sphere(0.42, loc=(x, y - 0.02, top + 0.9), segs=8, rings=5))
        add(C.PAPER, band_)
        for p in puff:
            add(C.PAPER, p)
        for k in range(3):
            for s in (-1, 1):
                add(C.GOLD, ns.sphere(0.07, loc=(x + s * 0.2, y - 0.45, z0 + 0.55 + 0.33 * k), segs=6, rings=3))


# ------------------------------------------------------------------------------------------------
# Crest + floods
# ------------------------------------------------------------------------------------------------

def crest(gold, navy, white):
    zc = CREST_Z
    yc = (SIGN_Y[0] + SIGN_Y[1]) / 2
    navy.append(C.prism(C.circle_pts(CREST_R, 28, 0, zc), "y", yc - 0.35, yc + 0.35))
    gold.append(C.ring_slab(C.circle_pts(CREST_R + 0.55, 28, 0, zc), C.circle_pts(CREST_R, 28, 0, zc), "y", yc - 0.5, yc + 0.5))
    gold.append(C.ring_slab(C.circle_pts(CREST_R - 0.35, 28, 0, zc), C.circle_pts(CREST_R - 0.55, 28, 0, zc), "y",
                            yc - 0.45, yc - 0.3))
    # toque: band + three puffs (front relief)
    fy0, fy1 = yc - 0.62, yc - 0.32
    white.append(C.prism(C.rrect(2.4, 0.8, 0.12, 1, 0, zc - 1.5), "y", fy0, fy1))
    for cx, cz, r in ((-0.85, zc - 0.25, 0.85), (0.85, zc - 0.25, 0.85), (0.0, zc + 0.35, 1.05)):
        white.append(C.prism(C.circle_pts(r, 16, cx, cz), "y", fy0 + 0.02, fy1))
    white.append(C.prism(C.rrect(2.2, 1.1, 0.2, 1, 0, zc - 0.85), "y", fy0 + 0.01, fy1))
    for s in (-1, 1):
        gold.append(C.prism(C.star_pts(0.62, 0.27, s * 2.35, zc + 0.9), "y", yc - 0.6, yc - 0.3))
    # pedestal between the sign box and the crest
    gold.append(ns.box((3.2, 1.4, CREST_Z - CREST_R - SIGN[3] + 0.2), loc=(0, yc, (SIGN[3] + CREST_Z - CREST_R) / 2),
                       bevel=0.08, segments=1))


def flood(x, steel, lens):
    """A flood lamp on the cornice top aimed up and back at the sign. Returns the lens centre."""
    base_z = CORNICE[1]
    y = FY + 1.2
    steel.append(ns.box((0.9, 0.9, 0.25), loc=(x, y, base_z + 0.12), bevel=0.04, segments=1))
    steel.append(C.rod((x, y, base_z + 0.2), (x, y, base_z + 1.1), 0.12, verts=6))
    head = (x, y - 0.25, base_z + 1.45)
    aim = Vector((0.0, SIGN_Y[0], (SIGN[2] + SIGN[3]) / 2)) - Vector(head)
    aim.normalize()
    housing = ns.cyl(0.62, 0.9, loc=(0, 0, 0), verts=10, bevel=0.04, segments=1, radius_top=0.7)
    glass = ns.cyl(0.6, 0.06, loc=(0, 0, 0.47), verts=10, bevel=0.0)
    for o in (housing, glass):
        o.rotation_euler = aim.to_track_quat("Z", "Y").to_euler()
        o.location = Vector(head)
        ns.apply_all(o)
    steel.append(housing)
    lens.append(glass)
    return tuple(Vector(head) + aim * 0.5)


# ------------------------------------------------------------------------------------------------
# Build
# ------------------------------------------------------------------------------------------------

def build():
    navy, deep, band, stone, cream, gold, chrome, interior, lamps, glass, steel = ([] for _ in range(11))
    groups = {}
    shirts = [[] for _ in CLASSES]

    # ----- shell ------------------------------------------------------------------------------------
    stone.append(ns.box((2 * HX + 0.5, BY - FY + 0.5, PLINTH), loc=(0, (FY + BY) / 2, PLINTH / 2), bevel=0.1, segments=1))
    cf = CY + 0.1
    navy.append(ns.box((2 * HX, BY - cf, TOP - PLINTH), loc=(0, (cf + BY) / 2, (PLINTH + TOP) / 2), bevel=0.0))
    for s in (-1, 1):   # front-zone side slabs (reaching back to the core)
        navy.append(ns.box((1.0, cf - WY, TOP - PLINTH), loc=(s * (HX - 0.5), (WY + cf) / 2, (PLINTH + TOP) / 2), bevel=0.0))

    def slab(x0, x1, z0, z1, lst=navy):
        lst.append(ns.box((x1 - x0, WY - FY, z1 - z0), loc=((x0 + x1) / 2, (FY + WY) / 2, (z0 + z1) / 2), bevel=0.0))

    # ground floor front slabs around the two windows and the door
    for s in (-1, 1):
        w0, w1 = (WIN_L[0], WIN_L[1]) if s < 0 else (WIN_R[0], WIN_R[1])
        slab(*sorted((s * HX, s * abs(WIN_L[0]))), PLINTH, BAND[0])            # outer pier
        slab(*sorted((s * abs(WIN_L[1]), s * abs(DOOR[0]))), PLINTH, BAND[0])  # inner pier (to the door)
        slab(w0, w1, PLINTH, WIN_L[2] - 0.22)                                   # under the sill
        slab(w0, w1, WIN_L[3], BAND[0])                                         # over the window
        stone.append(ns.box((w1 - w0 + 0.5, WY - FY + 0.34, 0.22), loc=((w0 + w1) / 2, (FY + WY) / 2 - 0.17, WIN_L[2] - 0.11),
                            bevel=0.05, segments=1))                            # sills
    slab(DOOR[0], DOOR[1], DOOR[3], BAND[0])                                    # over the door
    slab(-HX, HX, BAND[1], TOP)                                                 # upper floor (solid)
    # band, cornice, pinstripes (wrapping round the sides)
    band.append(ns.box((2 * HX + 0.16, BY - FY + 0.16, BAND[1] - BAND[0]), loc=(0, (FY + BY) / 2, sum(BAND) / 2), bevel=0.04,
                       segments=1))
    pins = [ns.box((2 * HX + 0.22, BY - FY + 0.22, 0.12), loc=(0, (FY + BY) / 2, BAND[0] + 0.25), bevel=0.0)]
    deep.append(ns.box((2 * HX + 0.6, BY - FY + 0.6, CORNICE[1] - CORNICE[0]), loc=(0, (FY + BY) / 2, sum(CORNICE) / 2),
                       bevel=0.12, segments=1))
    gold.append(ns.box((2 * HX + 0.66, BY - FY + 0.66, 0.14), loc=(0, (FY + BY) / 2, CORNICE[0] + 0.28), bevel=0.0))
    gold.append(ns.box((2 * HX + 0.7, BY - FY + 0.7, 0.12), loc=(0, (FY + BY) / 2, CORNICE[1] - 0.2), bevel=0.0))

    # ----- pilasters (cream, gold capitals and bases) ---------------------------------------------------
    for x0, x1 in PILASTERS:
        w = x1 - x0
        cx = (x0 + x1) / 2
        cream.append(ns.box((w, PIL_PROUD + 0.05, TOP - PLINTH - 1.4), loc=(cx, FY - PIL_PROUD / 2 + 0.02, (PLINTH + 0.6 + TOP - 0.8) / 2),
                            bevel=0.05, segments=1))
        gold.append(ns.box((w + 0.3, PIL_PROUD + 0.3, 0.8), loc=(cx, FY - PIL_PROUD / 2 - 0.1, TOP - 0.4), bevel=0.06,
                           segments=1))
        gold.append(ns.box((w + 0.24, PIL_PROUD + 0.24, 0.6), loc=(cx, FY - PIL_PROUD / 2 - 0.07, PLINTH + 0.3), bevel=0.05,
                           segments=1))
        # fluting: two recessed-looking navy lines on the shaft
        for k in (-1, 1):
            navy.append(ns.box((0.14, 0.04, TOP - PLINTH - 3.4), loc=(cx + k * w * 0.22, FY - PIL_PROUD - 0.0, (PLINTH + TOP) / 2 - 0.2),
                               bevel=0.0))

    # ----- display windows -------------------------------------------------------------------------------
    for (x0, x1, z0, z1) in (WIN_L, WIN_R):
        interior.append(liner(x0, x1, z0, z1, WY, CY))
        glass.append(ns.box((x1 - x0 + 0.1, 0.06, z1 - z0 + 0.1), loc=((x0 + x1) / 2, FY + 0.42, (z0 + z1) / 2), bevel=0.0))
        lamps.append(ns.box((x1 - x0 - 0.6, 0.22, 0.14), loc=((x0 + x1) / 2, WY + 0.3, z1 - 0.06), bevel=0.0))
        lamps.append(ns.box((x1 - x0 - 0.6, 0.14, 0.12), loc=((x0 + x1) / 2, CY - 0.2, z1 - 0.06), bevel=0.0))
        fo = C.rrect(x1 - x0 + 2 * FRAME, z1 - z0 + 2 * FRAME, 0.28, 2, (x0 + x1) / 2, (z0 + z1) / 2)
        fi = C.rrect(x1 - x0 - 0.12, z1 - z0 - 0.12, 0.08, 2, (x0 + x1) / 2, (z0 + z1) / 2)
        gold.append(C.ring_slab(fo, fi, "y", FY - 0.2, FY + 0.05))
    # pedestals with warm glow bands
    peds, glow = [], []
    for x in MAN_X:
        ped = C.prism(C.circle_pts(PED_R, 14, x, M_Y), "z", DISPLAY_FLOOR, DISPLAY_FLOOR + PED_H)
        peds.append(ped)
        glow.append(C.band(PED_R + 0.03, 0.12, loc=(x, M_Y, DISPLAY_FLOOR + PED_H - 0.1), verts=14))
    for i, x in enumerate(MAN_X):
        mannequin(i, x, groups, shirts)

    # ----- door: recess, two glass leaves with gold frames and push bars, transom -------------------------
    interior.append(liner(DOOR[0], DOOR[1], DOOR[2] + 0.02, DOOR[3], WY, DOOR_Y - 0.02, bottom=False))
    floor = ns.box((DOOR[1] - DOOR[0], DOOR_Y - FY, 0.05), loc=(0, (FY + DOOR_Y) / 2, PLINTH + 0.025), bevel=0.0)
    C.part([floor], "Entry", C.STONE_DARK, "Marble", smooth_angle=None)
    leaf_h = 7.5
    for s in (-1, 1):
        x0, x1 = sorted((0.04 * s, s * (DOOR[1] - 0.04)))
        cx = (x0 + x1) / 2
        gold.append(C.ring_slab(C.rrect(x1 - x0, leaf_h, 0.08, 1, cx, PLINTH + leaf_h / 2),
                                C.rrect(x1 - x0 - 0.5, leaf_h - 0.6, 0.06, 1, cx, PLINTH + leaf_h / 2 + 0.05), "y",
                                DOOR_Y - 0.08, DOOR_Y + 0.08))
        glass.append(ns.box((x1 - x0 - 0.46, 0.04, leaf_h - 0.56), loc=(cx, DOOR_Y, PLINTH + leaf_h / 2 + 0.05), bevel=0.0))
        gold.append(C.rod((s * 0.9, DOOR_Y - 0.32, PLINTH + 3.0), (s * 0.9, DOOR_Y - 0.32, PLINTH + 5.0), 0.07, verts=6))
        for zb in (3.1, 4.9):
            gold.append(C.rod((s * 0.9, DOOR_Y - 0.32, PLINTH + zb), (s * 0.9, DOOR_Y - 0.06, PLINTH + zb), 0.05, verts=6))
    tz0 = PLINTH + leaf_h + 0.15
    gold.append(ns.box((DOOR[1] - DOOR[0], 0.18, 0.18), loc=(0, DOOR_Y, tz0 - 0.08), bevel=0.0))
    glass.append(ns.box((DOOR[1] - DOOR[0] - 0.2, 0.04, DOOR[3] - tz0 - 0.1), loc=(0, DOOR_Y, (tz0 + DOOR[3]) / 2), bevel=0.0))
    lamps.append(ns.box((DOOR[1] - DOOR[0] - 0.4, 0.2, 0.12), loc=(0, WY + 0.3, DOOR[3] - 0.08), bevel=0.0))
    fo = C.rrect(DOOR[1] - DOOR[0] + 2 * FRAME, DOOR[3] - DOOR[2] + FRAME, 0.0, 1, 0, (DOOR[2] + DOOR[3] + FRAME) / 2)
    for xa, xb in ((DOOR[0] - FRAME, DOOR[0] + 0.05), (DOOR[1] - 0.05, DOOR[1] + FRAME)):   # jambs (a U, no sill)
        gold.append(ns.box((xb - xa, 0.25, DOOR[3] - PLINTH), loc=((xa + xb) / 2, FY - 0.075, (PLINTH + DOOR[3]) / 2),
                           bevel=0.04, segments=1))
    gold.append(ns.box((DOOR[1] - DOOR[0] + 2 * FRAME, 0.25, FRAME), loc=(0, FY - 0.075, DOOR[3] + FRAME / 2 - 0.02),
                       bevel=0.04, segments=1))

    # ----- theatre canopy with the CLASSES fascia -----------------------------------------------------------
    cx0, cx1 = CANOPY
    deep.append(ns.box((cx1 - cx0, CAN_D, CAN_Z[1] - CAN_Z[0]), loc=(0, FY - CAN_D / 2, sum(CAN_Z) / 2), bevel=0.05, segments=1))
    fy_f = FY - CAN_D
    deep.append(ns.box((cx1 - cx0 + 0.3, 0.4, FASCIA_Z[1] - FASCIA_Z[0]), loc=(0, fy_f - 0.2 + 0.02, sum(FASCIA_Z) / 2),
                       bevel=0.06, segments=1))
    for s in (-1, 1):   # canopy cheeks
        deep.append(ns.box((0.3, CAN_D, FASCIA_Z[1] - CAN_Z[0] - 0.4), loc=(s * (cx1 - 0.15), FY - CAN_D / 2,
                                                                           (CAN_Z[0] + FASCIA_Z[1] - 0.4) / 2), bevel=0.04,
                           segments=1))
    gold.append(C.ring_slab(C.rrect(cx1 - cx0 + 0.3, FASCIA_Z[1] - FASCIA_Z[0], 0.2, 2, 0, sum(FASCIA_Z) / 2),
                            C.rrect(cx1 - cx0 - 0.1, FASCIA_Z[1] - FASCIA_Z[0] - 0.4, 0.12, 2, 0, sum(FASCIA_Z) / 2), "y",
                            fy_f - 0.48, fy_f - 0.36))
    cw = C.Word("CLASSES", 0.0, cap=1.25, spacing=1.12, cz=sum(FASCIA_Z) / 2)
    letters_c = cw.solid(fy_f - 0.52, 0.16, name="ClassesWord")
    canopy_bulbs = C.path_points(C.rect_path(cx0 + 0.45, cx1 - 0.45, FASCIA_Z[0] + 0.25, FASCIA_Z[1] - 0.25, fy_f - 0.42),
                                 0.75, closed=True)
    soffit_pts = [(x, FY - CAN_D + 0.45, CAN_Z[0] - 0.01) for x in [cx0 + 0.6 + k * (cx1 - cx0 - 1.2) / 7 for k in range(8)]]
    soffit_pts += [(x, FY - 1.2, CAN_Z[0] - 0.01) for x in [cx0 + 0.6 + k * (cx1 - cx0 - 1.2) / 7 for k in range(8)]]

    # ----- tags over the windows ----------------------------------------------------------------------------
    for i, x in enumerate(MAN_X):
        t = C.prism(C.rrect(TAG_W, TAG_H, 0.1, 1, x, TAG_Z), "y", FY - 0.12, FY + 0.02)
        ns.tag(t, f"Tag{i + 1}", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
        gold.append(C.ring_slab(C.rrect(TAG_W + 0.24, TAG_H + 0.24, 0.16, 1, x, TAG_Z), C.rrect(TAG_W, TAG_H, 0.1, 1, x, TAG_Z),
                                "y", FY - 0.17, FY + 0.02))

    # ----- upper floor: the class screen and two arched windows ---------------------------------------------
    scr = C.prism(C.rrect(SCR_W, SCR_H, 0.14, 1, 0, SCR_Z), "y", SCR_Y, FY + 0.02)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
    gold.append(C.ring_slab(C.rrect(SCR_W + 0.7, SCR_H + 0.7, 0.4, 2, 0, SCR_Z), C.rrect(SCR_W, SCR_H, 0.14, 2, 0, SCR_Z), "y",
                            SCR_Y - 0.12, FY + 0.01))
    for s in (-1, 1):
        x = s * ARCH_X
        outer = C.arch(ARCH_W + 0.8, ARCH_H + 0.4, ARCH_Z0 - 0.4, n=12, cx=x)
        inner = C.arch(ARCH_W, ARCH_H, ARCH_Z0, n=12, cx=x)
        cream.append(C.ring_slab(outer, inner, "y", FY - 0.28, FY + 0.02))
        lit = C.prism(inner, "y", FY - 0.06, FY + 0.02)
        ns.tag(lit, f"ArchGlow{1 if s < 0 else 2}", "#FFE2B0", "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)
        # muntins (cream) over the glow: a centre post, a transom bar and a fan in the arch
        zs = ARCH_Z0 + ARCH_H - ARCH_W / 2
        cream.append(ns.box((0.16, 0.14, ARCH_H - 0.1), loc=(x, FY - 0.13, ARCH_Z0 + (ARCH_H - 0.1) / 2), bevel=0.0))
        cream.append(ns.box((ARCH_W - 0.05, 0.14, 0.16), loc=(x, FY - 0.13, zs), bevel=0.0))
        for a in (45, 135):
            r = ARCH_W / 2 - 0.05
            cream.append(C.rod((x, FY - 0.13, zs), (x + r * math.cos(math.radians(a)), FY - 0.13, zs + r * math.sin(math.radians(a))),
                               0.07, verts=4))
        stone.append(ns.box((ARCH_W + 1.0, 0.5, 0.25), loc=(x, FY - 0.25, ARCH_Z0 - 0.52), bevel=0.04, segments=1))
    # small STACKHOUSE badges between the arches and the screen
    badges = {}
    for s in (-1, 1):
        C.merge_into(badges, C.badge((s * 9.9, FY + 0.001, 21.3), r=1.25, n=14))

    # ----- back door ---------------------------------------------------------------------------------------------
    deep.append(ns.box((4.0, 0.2, 7.4), loc=(10.0, BY + 0.08, PLINTH + 3.7), bevel=0.04, segments=1))
    chrome.append(ns.box((0.25, 0.25, 0.9), loc=(11.5, BY + 0.25, PLINTH + 3.4), bevel=0.05, segments=1))
    stone.append(ns.box((4.8, 0.3, 0.45), loc=(10.0, BY + 0.1, PLINTH + 7.55), bevel=0.05, segments=1))

    # ----- roof sign ---------------------------------------------------------------------------------------------
    sx0, sx1, sz0, sz1 = SIGN
    zc = (sz0 + sz1) / 2
    sbox = C.prism(C.rrect(sx1 - sx0, sz1 - sz0, 0.8, 3, 0, zc), "y", SIGN_Y[0], SIGN_Y[1])
    ns.bevel(sbox, width=0.08, segments=1)
    deep.append(sbox)
    gold.append(C.ring_slab(C.rrect(sx1 - sx0 + 0.4, sz1 - sz0 + 0.4, 0.95, 3, 0, zc),
                            C.rrect(sx1 - sx0 - 0.12, sz1 - sz0 - 0.12, 0.74, 3, 0, zc), "y", SIGN_Y[0] - 0.12, SIGN_Y[0] + 0.3))
    w = C.Word("CLASS SHOP", 0.0, cap=SIGN_CAP, spacing=1.08, base=zc - SIGN_CAP / 2, xscale=1.0)
    if w.width > 38.6:
        w.fit_width(38.6)
    letters = w.solid(SIGN_Y[0] - 0.55, 0.5, back=False, name="Letters")
    tubes = C.contour_tubes(w.loops(offset=0.18), SIGN_Y[0] - 0.42, 0.12, sides=4)
    stroke_pts = []
    for closed, path in C.stroke_paths(w.loops(), spacing=0.5):
        p3 = [(x, SIGN_Y[0] - 0.56, z) for x, z in path]
        stroke_pts += C.path_points(p3, 0.78, closed=closed)
    bulbs_letters = C.domes(stroke_pts, 0.17, axis=(0, -1, 0), segs=6, rings=2) if stroke_pts else None
    frame_path = C.rect_path(sx0 + 0.6, sx1 - 0.6, sz0 + 0.6, sz1 - 0.6, SIGN_Y[0] + 0.01, r=0.55, segs=2)
    bulbs_frame = C.domes(C.path_points(frame_path, 1.45, closed=True), 0.22, axis=(0, -1, 0), segs=6, rings=2)
    for x in (-15.0, 0.0, 15.0):
        steel.append(C.rod((x, SIGN_Y[1] - 0.1, sz1 - 1.6), (x, CY + 1.0, CORNICE[1]), 0.18, verts=6))
        steel.append(C.rod((x, SIGN_Y[1] - 0.1, sz0 + 1.2), (x, CY - 1.6, CORNICE[1]), 0.16, verts=6))
        steel.append(ns.box((1.0, 1.0, 0.12), loc=(x, CY + 1.0, CORNICE[1] + 0.06), bevel=0.0))
        steel.append(ns.box((0.8, 0.8, 0.12), loc=(x, CY - 1.6, CORNICE[1] + 0.06), bevel=0.0))
    white = []
    crest(gold, deep, white)
    lens = []
    floods = [flood(s * 19.0, steel, lens) for s in (-1, 1)]

    # ----- tag parts ------------------------------------------------------------------------------------------------
    C.part(navy, "Facade", NAVY_FACADE, can_collide=True, smooth_angle=40)
    C.part(deep, "NavyDeep", C.NAVY_DEEP, smooth_angle=40)
    C.part(band, "RedBand", C.BRAND, can_collide=True, smooth_angle=40)
    C.part(stone, "Stone", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(cream, "Cream", C.CREAM, smooth_angle=40)
    C.part(gold + pins + badges.pop(C.CHEESE, []) + groups.pop(C.GOLD, []), "Gold", GOLD_TRIM, "Metal", smooth_angle=45)
    C.part(interior, "Interior", INTERIOR, smooth_angle=None)
    C.part(peds, "Pedestals", MARBLE, "Marble", smooth_angle=40)
    C.part(chrome + steel + groups.pop(C.CHROME, []), "Chrome", C.CHROME, "Metal", smooth_angle=45)
    ns.tag(C.merge(lamps, "LampStrips"), "LampStrips", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=40)
    ns.tag(C.merge(glow, "PedestalGlow"), "PedestalGlow", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=60)
    ns.tag(C.merge(glass, "Glass"), "Glass", GLASS_TINT, "Glass", transparency=0.8, recolor="glass", cast_shadow=False,
           smooth_angle=30)
    C.part([letters, letters_c], "Letters", GOLD_LETTER, smooth_angle=30)
    ns.tag(tubes, "LetterNeon", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    bulbs = [b for b in (bulbs_letters, bulbs_frame) if b] + [C.domes(canopy_bulbs, 0.16, axis=(0, -1, 0), segs=6, rings=2),
                                                              C.domes(soffit_pts, 0.16, axis=(0, 0, -1), segs=6, rings=2)]
    ns.tag(C.merge(bulbs, "Bulbs"), "Bulbs", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=80)
    ns.tag(C.merge(lens, "FloodLens"), "FloodLens", "#FFF4D6", "Neon", recolor="lamp", cast_shadow=False, smooth_angle=60)
    C.part(white + groups.pop(C.PAPER, []), "White", C.PAPER, smooth_angle=40)
    for i, objs in enumerate(shirts):
        ns.tag(C.merge(objs, f"Shirt{i + 1}"), f"Shirt{i + 1}", CLASSES[i][1], "Fabric", recolor=f"shirt{i + 1}", smooth_angle=50)
    names = {PANTS: "Pants", SKIN: "MannequinSkin", C.BRAND: "CapRed", C.NAVY_DEEP: "CapNavy", C.CHARCOAL: "Shoes"}
    for col, objs in groups.items():
        C.part(objs, names.get(col, "Dress" + col.lstrip("#")), col, smooth_angle=45)
    C.add_parts(badges, "Badge", smooth_angle=40)
    return {"floods": floods}


def sockets():
    s = {"Screen": ((0.0, SCR_Y, SCR_Z), 0.0), "Pad": ((0.0, FY - 10.0, 0.0), 0.0),
         "Sign": ((0.0, SIGN_Y[0] - 0.6, (SIGN[2] + SIGN[3]) / 2), 0.0)}
    for i, x in enumerate(MAN_X):
        s[f"Tag{i + 1}"] = ((x, FY - 0.12, TAG_Z), 0.0)
        s[f"Mannequin{i + 1}"] = ((x, M_Y - 0.45, DISPLAY_FLOOR + PED_H + 0.12 + 2.0 + 0.35 + 0.8), 0.0)
    for k, sgn in enumerate((-1, 1)):
        x = sgn * 19.0
        s[f"Flood{k + 1}"] = ((x, FY + 0.95, CORNICE[1] + 1.45), 0.0)
    return s


META = {
    "screens": {"Screen": [SCR_W, SCR_H], **{f"Tag{i + 1}": [TAG_W, TAG_H] for i in range(6)}},
    "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)] + [C.screen_meta(f"Tag{i + 1}", TAG_W, TAG_H) for i in range(6)],
    "class_order": [c[0] for c in CLASSES],
    "class_order_note": "Mannequin1..6 / Tag1..6 / roles shirt1..shirt6, left to right as seen from the front",
    "roles": {"screen": "Screen, Tag1..Tag6", "glass": "Glass (window panes, door leaves, transom)",
              "neon": "LetterNeon (cyan CLASS SHOP outlines)",
              "lamp": "Bulbs (letters, sign frame, canopy), LampStrips, PedestalGlow, ArchGlow1/2, FloodLens",
              "shirt1..shirt6": "the mannequins' shirts (Config.Uniforms look.shirt)"},
    "light_hint": {"sign": {"type": "SpotLight", "from": "Flood1 / Flood2", "at": "Sign", "color": "#FFE7B8", "range": 40,
                            "brightness": 3},
                   "windows": {"type": "PointLight", "per": "display window + door", "color": C.LAMP_WARM, "range": 12,
                               "brightness": 1}},
}

if __name__ == "__main__":
    C.run(build, "Lobby_ClassShop", sockets=sockets(), meta=META, budget=20000, far=True)
