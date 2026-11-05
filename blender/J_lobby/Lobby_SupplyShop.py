"""Lobby_SupplyShop — SUPPLIES: the staff supply depot on the lobby's shop row (~30.6 x 19.6 x 16).

2026-11-04: the fifth storefront of the row (Landon: shops "right next to each other" with a
glowing circle each). An industrial depot in teal-green corrugated metal with a hazard-striped
band and a steel cornice:

  * A wide roll-up door, its shutter rolled most of the way up, opens on the depot: two steel
    shelf units against the back wall stocked with the five Config.Monetization supplies
    (spare battery packs, energy-drink cans, recipe-card boxes, lucky-clue magnifiers, gold
    Second Shift tickets), a counter with a till between them, fluorescent tubes overhead, and
    two hero props on the floor — a giant battery and a giant energy-drink can.
  * Over the door a long LED ticker screen (Screen); on the corrugated side panels two
    backlit price boards (Label1 / Label2).
  * Outside: stacked STACKHOUSE crates and a hand truck.
  * Roof sign: big white SUPPLIES letters with green neon outlines on a steel raceway.

Front = -Y, pivot = bottom-centre. Sockets: Screen, Label1, Label2 (screen face centres), Pad (on the
ground in front).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

HX = 15.0
FY, WY, BY = -6.0, -5.3, 9.0
BACK_Y = 6.0                       # interior back wall face
PLINTH = 0.6
BAND = (11.0, 11.9)
CORNICE = (11.9, 12.9)
DOOR = (-8.0, 8.0, PLINTH, 9.0)
SHUTTER_Z = 7.3                    # shutter bottom (rolled up to here)
SCR_W, SCR_H, SCR_Z = 10.0, 1.3, 10.0
LBL_W, LBL_H, LBL_Z = 4.6, 3.4, 6.2
LBL_X = 11.6
SIGN_CAP = 4.2
SIGN_BASE = 14.0
LET_Y = -6.1

TEAL = "#2F5D50"
TEAL_RIB = "#3B7062"
HAZARD_Y = "#F2B33D"
HAZARD_K = "#1E1F24"
STEEL = "#9AA3AA"
STEEL_DARK = "#5C646B"
CONCRETE_IN = "#8C8A84"
WALL_IN = "#C9CDD0"
CRATE = "#B07A4A"
CRATE_DARK = "#7E5433"
BATT_Y = "#F5C518"
CAN_CYAN = "#38E1FF"
CAN_PINK = "#FF4FA3"
CARD = "#F4EDE0"
TICKET = "#F0B030"
GREEN_NEON = "#4CFF7A"


def liner(x0, x1, z0, z1, y0, y1, bottom=True):
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


def battery(x, y, z, r, h, g):
    """Battery cell standing at (x, y, z): yellow body, black base band, steel cap. -> groups."""
    g.setdefault(BATT_Y, []).append(ns.cyl(r, h * 0.72, loc=(x, y, z + h * 0.36 + h * 0.2), verts=8, bevel=0.0))
    g.setdefault(HAZARD_K, []).append(ns.cyl(r, h * 0.2, loc=(x, y, z + h * 0.1), verts=8, bevel=0.0))
    g.setdefault(STEEL, []).append(ns.cyl(r * 0.42, h * 0.08, loc=(x, y, z + h * 0.96), verts=6, bevel=0.0))


def can(x, y, z, r, h, col, g):
    g.setdefault(col, []).append(ns.cyl(r, h * 0.86, loc=(x, y, z + h * 0.45), verts=8, bevel=0.0))
    g.setdefault(STEEL, []).append(ns.cyl(r * 0.86, h * 0.1, loc=(x, y, z + h * 0.93), verts=8, bevel=0.0))


def shelf_unit(x0, x1, g, steel):
    """Steel shelving against the back wall from x0 to x1 with four stocked levels."""
    d = 1.6
    y0, y1 = BACK_Y - d, BACK_Y - 0.05
    levels = (PLINTH + 0.5, PLINTH + 2.3, PLINTH + 4.1, PLINTH + 5.9)
    for x in (x0, x1):
        for y in (y0 + 0.08, y1 - 0.08):
            steel.append(ns.box((0.14, 0.14, 7.2), loc=(x, y, PLINTH + 3.6), bevel=0.0))
    for z in levels:
        steel.append(ns.box((x1 - x0 + 0.14, d, 0.1), loc=((x0 + x1) / 2, (y0 + y1) / 2, z), bevel=0.0))
        steel.append(ns.box((x1 - x0 + 0.14, 0.06, 0.22), loc=((x0 + x1) / 2, y0 - 0.02, z + 0.06), bevel=0.0))
    w = x1 - x0
    ym = (y0 + y1) / 2
    for li, z in enumerate(levels):
        zt = z + 0.05
        kind = (li + (0 if x0 < 0 else 2)) % 5
        n = 6
        for k in range(n):
            x = x0 + (k + 0.5) * w / n
            if kind == 0:      # battery packs: two cells on a black card
                g.setdefault(HAZARD_K, []).append(ns.box((0.62, 0.3, 0.9), loc=(x, ym + 0.2, zt + 0.45), bevel=0.0))
                for dx in (-0.15, 0.15):
                    battery(x + dx, ym - 0.05, zt, 0.12, 0.8, g)
            elif kind == 1:    # energy drinks: three cans
                for dx, col in ((-0.2, CAN_CYAN), (0.0, CAN_PINK), (0.2, CAN_CYAN)):
                    can(x + dx, ym - 0.1 + abs(dx), zt, 0.12, 0.62, col, g)
            elif kind == 2:    # recipe-card boxes
                g.setdefault(CARD, []).append(ns.box((0.6, 0.5, 0.75), loc=(x, ym, zt + 0.375), bevel=0.0))
                g.setdefault(C.BRAND, []).append(ns.box((0.62, 0.06, 0.22), loc=(x, ym - 0.26, zt + 0.5), bevel=0.0))
            elif kind == 3:    # lucky-clue magnifiers in a display stand
                g.setdefault(STEEL_DARK, []).append(ns.box((0.6, 0.4, 0.2), loc=(x, ym, zt + 0.1), bevel=0.0))
                ring = C.ns.torus(0.24, 0.05, major_segs=10, minor_segs=4)
                ring.rotation_euler = (math.radians(90), 0, 0)
                ring.location = (x, ym - 0.05, zt + 0.72)
                g.setdefault(C.GOLD, []).append(ring)
                g.setdefault(CRATE_DARK, []).append(C.rod((x, ym - 0.05, zt + 0.2), (x, ym - 0.05, zt + 0.48), 0.05, verts=5))
            else:              # Second Shift tickets: gold cards leaning
                g.setdefault(TICKET, []).append(ns.box((0.66, 0.06, 0.4), loc=(x, ym + 0.1, zt + 0.32), rot=(-14, 0, 0), bevel=0.0))
                g.setdefault(TICKET, []).append(ns.box((0.66, 0.06, 0.4), loc=(x + 0.06, ym - 0.12, zt + 0.25), rot=(-20, 0, 0), bevel=0.0))


def crate(x, y, z, s, g, yaw=0.0):
    """Wooden STACKHOUSE crate (s = size) with darker slats on the visible sides."""
    objs_l, objs_d = [ns.box((s, s, s), loc=(0, 0, s / 2), bevel=0.04, segments=1)], []
    for k in (-1, 1):
        objs_d.append(ns.box((s + 0.04, s * 0.14, s * 0.12), loc=(0, k * 0.0 - s / 2 - 0.0, s / 2 + k * s * 0.3), bevel=0.0))
        objs_d.append(ns.box((s * 0.12, s + 0.04, s * 0.12), loc=(-s / 2, 0, s / 2 + k * s * 0.3), bevel=0.0))
        objs_d.append(ns.box((s * 0.12, s + 0.04, s * 0.12), loc=(s / 2, 0, s / 2 + k * s * 0.3), bevel=0.0))
    logo = C.mini_logo((0, -s / 2 - 0.001, s / 2), r=s * 0.24, depth=0.04)
    C.place(objs_l + objs_d, (x, y, z), yaw=yaw)
    for col, objs in logo.items():
        C.place(objs, (x, y, z), yaw=yaw)
        g.setdefault(col, []).extend(objs)
    g.setdefault(CRATE, []).extend(objs_l)
    g.setdefault(CRATE_DARK, []).extend(objs_d)


def build():
    teal, ribs, band_y, band_k, steel, steel_d, stone, interior, lamps, glass = ([] for _ in range(10))
    g = {}
    # ----- shell ----------------------------------------------------------------------------------
    stone.append(ns.box((2 * HX + 0.4, BY - FY + 0.4, PLINTH), loc=(0, (FY + BY) / 2, PLINTH / 2), bevel=0.08, segments=1))

    def slab(x0, x1, z0, z1):
        teal.append(ns.box((x1 - x0, WY - FY, z1 - z0), loc=((x0 + x1) / 2, (FY + WY) / 2, (z0 + z1) / 2), bevel=0.0))

    for s in (-1, 1):
        slab(*sorted((s * HX, s * DOOR[1])), PLINTH, BAND[0])                       # side panels
        teal.append(ns.box((0.5, BY - WY, BAND[0] - PLINTH), loc=(s * (HX - 0.25), (WY + BY) / 2, (PLINTH + BAND[0]) / 2),
                           bevel=0.0))                                               # side walls
    slab(DOOR[0], DOOR[1], DOOR[3], BAND[0])                                        # over the door
    teal.append(ns.box((2 * HX - 1.0, 0.5, BAND[0] - PLINTH), loc=(0, BY - 0.25, (PLINTH + BAND[0]) / 2), bevel=0.0))
    # corrugation ribs on the side panels and the header (front) + the side walls
    for s in (-1, 1):
        x = s * DOOR[1] + s * 0.45
        while abs(x) < HX - 0.3:
            ribs.append(ns.box((0.22, 0.12, BAND[0] - PLINTH - 0.5), loc=(x, FY - 0.06, (PLINTH + 0.25 + BAND[0] - 0.25) / 2),
                               bevel=0.0))
            x += s * 0.7
    x = DOOR[0] + 0.35
    while x < DOOR[1] - 0.2:
        ribs.append(ns.box((0.22, 0.12, BAND[0] - DOOR[3] - 0.4), loc=(x, FY - 0.06, (DOOR[3] + 0.2 + BAND[0] - 0.2) / 2), bevel=0.0))
        x += 0.7
    for s in (-1, 1):
        y = WY + 0.6
        while y < BY - 0.3:
            ribs.append(ns.box((0.12, 0.22, BAND[0] - PLINTH - 0.5), loc=(s * (HX + 0.06), y, (PLINTH + BAND[0]) / 2), bevel=0.0))
            y += 0.9
    # hazard band: yellow base with black diagonal stripes on the front and sides
    band_y.append(ns.box((2 * HX + 0.16, BY - FY + 0.16, BAND[1] - BAND[0]), loc=(0, (FY + BY) / 2, sum(BAND) / 2), bevel=0.03,
                         segments=1))
    h = BAND[1] - BAND[0]
    xk = -HX + 0.2
    while xk < HX - 0.6:
        para = [(xk, BAND[0] + 0.04), (xk + 0.45, BAND[0] + 0.04), (xk + 0.45 + h - 0.08, BAND[1] - 0.04),
                (xk + h - 0.08, BAND[1] - 0.04)]
        para = [(min(max(px, -HX), HX), pz) for px, pz in para]
        band_k.append(C.flat_poly(para, FY - 0.09))
        xk += 1.1
    steel.append(ns.box((2 * HX + 0.5, BY - FY + 0.5, CORNICE[1] - CORNICE[0]), loc=(0, (FY + BY) / 2, sum(CORNICE) / 2), bevel=0.08,
                        segments=1))
    # ----- the depot behind the roll-up door ----------------------------------------------------------
    interior.append(liner(DOOR[0], DOOR[1], DOOR[2] + 0.01, DOOR[3], WY, BACK_Y, bottom=False))
    floor = ns.box((DOOR[1] - DOOR[0], BACK_Y - FY, 0.05), loc=(0, (FY + BACK_Y) / 2, PLINTH + 0.025), bevel=0.0)
    C.part([floor], "DepotFloor", CONCRETE_IN, "Concrete", smooth_angle=None)
    for xs in ((-6.8, -2.4), (2.4, 6.8)):
        shelf_unit(xs[0], xs[1], g, steel_d)
    # counter + till between the shelves
    steel_d.append(ns.box((4.0, 1.3, 2.6), loc=(0, BACK_Y - 1.6, PLINTH + 1.3), bevel=0.05, segments=1))
    steel.append(ns.box((4.3, 1.5, 0.12), loc=(0, BACK_Y - 1.6, PLINTH + 2.66), bevel=0.0))
    g.setdefault(HAZARD_K, []).append(ns.box((1.0, 0.8, 0.5), loc=(-0.8, BACK_Y - 1.6, PLINTH + 2.97), bevel=0.06, segments=1))
    g.setdefault(GREEN_NEON, []).append(ns.box((0.7, 0.05, 0.3), loc=(-0.8, BACK_Y - 2.02, PLINTH + 3.05), bevel=0.0))
    # fluorescent tubes
    for x in (-5.0, 0.0, 5.0):
        lamps.append(ns.box((0.3, 3.4, 0.14), loc=(x, (WY + BACK_Y) / 2, DOOR[3] - 0.1), bevel=0.0))
    # hero props: giant battery (left) and giant can (right)
    battery(-5.6, BACK_Y - 4.6, PLINTH, 0.75, 2.6, g)
    g.setdefault(HAZARD_K, []).append(C.prism([(-0.2, 1.4), (0.25, 1.4), (0.0, 1.0), (0.35, 1.0), (-0.25, 0.3), (-0.05, 0.85),
                                               (-0.35, 0.85)], "y", -0.02, 0.0))
    g[HAZARD_K][-1].location = (-5.6, BACK_Y - 4.6 - 0.74, PLINTH + 0.25)
    can(5.6, BACK_Y - 4.6, PLINTH, 0.85, 2.8, CAN_CYAN, g)
    g.setdefault(CAN_PINK, []).append(C.band(0.87, 0.6, loc=(5.6, BACK_Y - 4.6, PLINTH + 1.4), verts=8))
    # ----- the rolled-up shutter, its guide rails and a pull handle ---------------------------------------
    sy = FY + 0.32
    z = DOOR[3] - 0.05
    while z > SHUTTER_Z + 0.2:
        steel.append(ns.box((DOOR[1] - DOOR[0] - 0.1, 0.12, 0.3), loc=(0, sy, z - 0.15), bevel=0.03, segments=1))
        z -= 0.34
    steel_d.append(ns.box((DOOR[1] - DOOR[0] - 0.1, 0.22, 0.24), loc=(0, sy, SHUTTER_Z + 0.12), bevel=0.04, segments=1))
    for s in (-1, 1):
        steel_d.append(ns.box((0.3, 0.3, DOOR[3] - PLINTH), loc=(s * (DOOR[1] + 0.05), sy, (PLINTH + DOOR[3]) / 2), bevel=0.0))
    g.setdefault(HAZARD_K, []).append(C.rod((-0.8, sy - 0.25, SHUTTER_Z - 0.12), (0.8, sy - 0.25, SHUTTER_Z - 0.12), 0.06, verts=5))
    # hazard-striped door frame
    for s in (-1, 1):
        x = s * (DOOR[1] + 0.3)
        band_y.append(ns.box((0.3, 0.2, DOOR[3] - PLINTH), loc=(x, FY - 0.1, (PLINTH + DOOR[3]) / 2), bevel=0.0))
        zz = PLINTH + 0.3
        while zz < DOOR[3] - 0.4:
            band_k.append(C.flat_poly([(x - 0.15, zz), (x + 0.15, zz + 0.3), (x + 0.15, zz + 0.6), (x - 0.15, zz + 0.3)], FY - 0.205))
            zz += 0.9
    band_y.append(ns.box((DOOR[1] - DOOR[0] + 0.9, 0.2, 0.3), loc=(0, FY - 0.1, DOOR[3] + 0.15), bevel=0.0))
    # ----- screen + price boards -----------------------------------------------------------------------------
    scr = C.prism(C.rrect(SCR_W, SCR_H, 0.1, 1, 0, SCR_Z), "y", FY - 0.2, FY + 0.02)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
    steel_d.append(C.ring_slab(C.rrect(SCR_W + 0.3, SCR_H + 0.3, 0.16, 1, 0, SCR_Z), C.rrect(SCR_W, SCR_H, 0.1, 1, 0, SCR_Z), "y",
                               FY - 0.26, FY + 0.01))
    for i, s in enumerate((-1, 1)):
        x = s * LBL_X
        lb = C.prism(C.rrect(LBL_W, LBL_H, 0.12, 1, x, LBL_Z), "y", FY - 0.34, FY - 0.12)
        ns.tag(lb, f"Label{i + 1}", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
        steel.append(C.ring_slab(C.rrect(LBL_W + 0.4, LBL_H + 0.4, 0.2, 1, x, LBL_Z), C.rrect(LBL_W, LBL_H, 0.12, 1, x, LBL_Z), "y",
                                 FY - 0.42, FY - 0.1))
        lamps.append(ns.box((LBL_W, 0.3, 0.12), loc=(x, FY - 0.55, LBL_Z + LBL_H / 2 + 0.35), bevel=0.0))
        steel.append(C.rod((x, FY - 0.13, LBL_Z + LBL_H / 2 + 0.45), (x, FY - 0.55, LBL_Z + LBL_H / 2 + 0.45), 0.06, verts=5))
    # ----- outside: crates + hand truck ----------------------------------------------------------------------
    crate(-12.4, FY - 1.3, 0.0, 2.0, g, yaw=6)
    crate(-10.2, FY - 1.2, 0.0, 1.8, g, yaw=-8)
    crate(-11.5, FY - 1.25, 2.0, 1.6, g, yaw=14)
    crate(12.2, FY - 1.4, 0.0, 2.0, g, yaw=-5)
    ht = [C.rod((10.0 + dx, FY - 0.7, 0.2), (10.0 + dx, FY - 0.25, 4.0), 0.07, verts=5) for dx in (-0.45, 0.45)]
    ht.append(C.rod((9.5, FY - 0.25, 4.0), (10.5, FY - 0.25, 4.0), 0.06, verts=5))
    ht.append(ns.box((1.1, 0.7, 0.08), loc=(10.0, FY - 0.95, 0.24), bevel=0.0))
    for dx in (-0.55, 0.55):
        g.setdefault(HAZARD_K, []).append(ns.cyl(0.32, 0.18, loc=(10.0 + dx, FY - 0.55, 0.32), rot=(0, 90, 0), verts=10, bevel=0.0))
    g.setdefault(C.BRAND, []).extend(ht)
    # ----- roof sign: SUPPLIES ----------------------------------------------------------------------------------
    w = C.Word("SUPPLIES", 0.0, cap=SIGN_CAP, spacing=1.06, base=SIGN_BASE, xscale=0.98)
    if w.width > 27.0:
        w.fit_width(27.0)
    letters = w.solid(LET_Y, 0.8, name="Letters")
    tubes = C.contour_tubes(w.loops(offset=0.08), LET_Y + 0.02, 0.12, sides=4)
    steel.append(ns.box((2 * 13.6, 0.6, 0.6), loc=(0, LET_Y + 1.1, SIGN_BASE + 0.2), bevel=0.05, segments=1))
    for x in (-10.0, 0.0, 10.0):
        steel.append(ns.box((0.45, 0.45, SIGN_BASE + 0.3 - CORNICE[1]), loc=(x, LET_Y + 1.6, (CORNICE[1] + SIGN_BASE + 0.3) / 2),
                            bevel=0.03, segments=1))
        steel.append(C.rod((x, LET_Y + 1.6, SIGN_BASE - 0.3), (x, LET_Y + 3.8, CORNICE[1]), 0.1, verts=5))
    # ----- tag parts ---------------------------------------------------------------------------------------------
    C.part(teal, "Facade", TEAL, "CorrugatedSteel", can_collide=True, smooth_angle=40)
    C.part(ribs, "Ribs", TEAL_RIB, "CorrugatedSteel", smooth_angle=None)
    C.part(band_y, "HazardYellow", HAZARD_Y, smooth_angle=40)
    C.part(band_k + g.pop(HAZARD_K, []), "HazardBlack", HAZARD_K, smooth_angle=40)
    C.part(steel + g.pop(STEEL, []), "Steel", STEEL, "Metal", can_collide=False, smooth_angle=45)
    C.part(steel_d + g.pop(STEEL_DARK, []), "SteelDark", STEEL_DARK, "Metal", smooth_angle=45)
    C.part(stone, "Stone", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(interior, "DepotWalls", WALL_IN, smooth_angle=None)
    ns.tag(C.merge(lamps, "Tubes"), "Tubes", "#EAF6FF", "Neon", recolor="lamp", cast_shadow=False, smooth_angle=40)
    C.part([letters], "Letters", C.PAPER, smooth_angle=30)
    ns.tag(tubes, "LetterNeon", GREEN_NEON, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    ns.tag(C.merge(g.pop(GREEN_NEON), "TillScreen"), "TillScreen", GREEN_NEON, "Neon", recolor="lamp", cast_shadow=False)
    names = {BATT_Y: "Batteries", CAN_CYAN: "CansCyan", CAN_PINK: "CansPink", CARD: "RecipeCards", C.BRAND: "RedStuff",
             TICKET: "Tickets", C.GOLD: "Magnifiers", CRATE: "Crates", CRATE_DARK: "CrateSlats"}
    for col, objs in g.items():
        C.part(objs, names.get(col, "Stock" + col.lstrip("#")), col, "Metal" if col in (C.GOLD, TICKET) else "SmoothPlastic",
               smooth_angle=40)


def sockets():
    return {"Screen": ((0.0, FY - 0.2, SCR_Z), 0.0), "Label1": ((-LBL_X, FY - 0.34, LBL_Z), 0.0),
            "Label2": ((LBL_X, FY - 0.34, LBL_Z), 0.0), "Pad": ((0.0, FY - 8.5, 0.0), 0.0)}


META = {
    "screens": {"Screen": [SCR_W, SCR_H], "Label1": [LBL_W, LBL_H], "Label2": [LBL_W, LBL_H]},
    "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H), C.screen_meta("Label1", LBL_W, LBL_H), C.screen_meta("Label2", LBL_W, LBL_H)],
    "roles": {"screen": "Screen (LED ticker over the door), Label1 / Label2 (price boards, left / right as seen from the front)",
              "neon": "LetterNeon (green SUPPLIES outlines)", "lamp": "Tubes (depot lights, board lamps), TillScreen"},
    "light_hint": {"sign": {"type": "PointLight", "at": "3 studs in front of the letters", "color": GREEN_NEON, "range": 22,
                            "brightness": 1.2},
                   "depot": {"type": "PointLight", "at": "inside the door, 6 up", "color": "#EAF6FF", "range": 16,
                             "brightness": 1}},
}

if __name__ == "__main__":
    C.run(build, "Lobby_SupplyShop", sockets=sockets(), meta=META, budget=12000, far=True)
