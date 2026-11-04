"""Lobby_FoodTruck — the STACKHOUSE food truck (16 x 10 x 8).

A rounded retro van: cream upper body and red-orange lower body split by a chrome belt strip,
big soft roof / nose / tail radii, a slanted split windshield, round headlights, chrome grille and
bumpers, whitewall wheels with red hubs. The -Y side (the front of the asset) has the big serving
window: a lit stainless kitchen inside (InteriorLight, role "lamp"), a cyan neon frame round the
opening (WindowNeon, role "neon"), a striped red-orange / cream awning on chrome struts with a
festoon of warm bulbs swagging along its front edge (Bulbs, role "lamp"), a stainless counter
shelf with a napkin box and ketchup / mustard bottles, a navy MENU board with a dark screen
(Screen, role "screen") and big cream STACKHOUSE letters on the red lower body. Pink neon lines
run along both sides under the roof (RoofNeon, role "neon"). A giant sub sandwich rides on the
roof. The +Y side carries a STACKHOUSE logo badge. Body and wheels collide.

Front (serving side) = -Y, cab / windshield at Blender +X (Roblox -X). Pivot = ground under the
centre of the body (the awning overhangs the front).
Sockets: Screen (menu screen face centre, yaw 0), Prompt (order spot in front of the counter),
Light (under the awning in front of the window, for the warm PointLight).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns

HL, HW = 7.6, 3.0            # body half length (x), half width (y)
Z_BOT, BELT, ROOF = 0.9, 3.6, 8.2
WIN = (-6.0, 0.8, 3.82, 6.9)                 # serving window x0, x1, z0, z1
CAV_Y = -1.75                                # cavity back wall
AWN = (-6.3, 1.1, 7.3, -4.3, 6.8)            # awning x0, x1, back z, front y, front z
MENU = (2.55, 5.45, 2.2, 3.0)                # menu board centre x, centre z, w, h
SCR_W, SCR_H = 1.8, 2.05
SCR_Z = 5.2
WHEELS = (-4.7, 5.0)
WR = 1.02
COUNTER_Z = 3.86
VAN_CREAM = "#F3EAD6"
STEEL_IN = "#A9B0B7"
WARM_IN = "#FFE2B0"


def silhouette():
    pts = [(-HL, Z_BOT), (HL, Z_BOT), (HL, 4.4), (7.0, 5.3), (6.0, ROOF), (-HL, ROOF)]
    return C.fillet(pts, [0.35, 0.4, 0.6, 0.5, 0.9, 1.4], 3)


def round_edges(obj, offset, segs, keep_z=None):
    """Bevel the hard (> 40 deg) edges of an applied mesh, except edges lying on z = keep_z."""
    ns.apply_all(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    edges = []
    for e in bm.edges:
        if len(e.link_faces) != 2 or e.calc_face_angle(0.0) < math.radians(40):
            continue
        if keep_z is not None and all(abs(v.co.z - keep_z) < 1e-4 for v in e.verts):
            continue
        edges.append(e)
    bmesh.ops.bevel(bm, geom=edges, offset=offset, offset_type="OFFSET", segments=segs, profile=0.5, affect="EDGES",
                    clamp_overlap=True)
    # the bevel leaves zero-area slivers where it stops at the kept seam; the exact boolean
    # solver returns an EMPTY mesh on them, so dissolve them before any boolean
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def body_parts():
    sil = silhouette()
    lower = C.prism(C.J.clip_rect(sil, -20, 20, -1, BELT), "y", -HW, HW)
    upper = C.prism(C.J.clip_rect(sil, -20, 20, BELT, 20), "y", -HW, HW)
    round_edges(lower, 0.5, 2, keep_z=BELT)
    round_edges(upper, 0.5, 3, keep_z=BELT)
    for x in WHEELS:
        ns.boolean(lower, ns.cyl(WR + 0.24, 2 * HW + 1.0, loc=(x, 0, 1.0), rot=(90, 0, 0), verts=16, bevel=0.0))
    x0, x1, z0, z1 = WIN
    ns.boolean(upper, ns.box((x1 - x0, 2.0, z1 - z0), loc=((x0 + x1) / 2, -HW - 1.0 + (CAV_Y + HW) + 0.0, (z0 + z1) / 2),
                             bevel=0.0))
    return lower, upper


def wheel(x, sy):
    y = sy * (HW - 0.55)
    tyre = ns.cyl(WR, 0.8, loc=(x, y, WR), rot=(90, 0, 0), verts=10, bevel=0.16, segments=1)
    wall = C.annulus(0.58, 0.82, verts=10)
    C.place(wall, (x, y + sy * 0.402, WR), pitch=-90 * sy)
    hub = ns.cyl(0.56, 0.12, verts=8, radius_top=0.44, bevel=0.0)
    C.place(hub, (x, y + sy * 0.43, WR), pitch=-90 * sy)
    return tyre, wall, hub


def roof_sandwich(cx, z0):
    """Giant sub on the roof (top at z0 + 1.8): {colour: [objs]}."""
    L, Wd = 6.4, 1.6
    out = {}
    stands = [ns.box((0.5, 1.2, 0.2), loc=(cx + s * 2.0, 0, z0 + 0.1), bevel=0.0) for s in (-1, 1)]
    out.setdefault(C.CHROME, []).extend(stands)
    zb = z0 + 0.2
    bot = ns.box((L, Wd, 0.5), loc=(cx, 0, zb + 0.25), bevel=0.22, segments=1)
    out.setdefault(C.BUN, []).append(bot)
    chz = ns.box((L - 0.2, Wd + 0.1, 0.09), loc=(cx, 0, zb + 0.53), bevel=0.0)
    drips = []
    for k, x in enumerate((-2.2, -0.7, 0.9, 2.3)):
        drips.append(C.prism([(cx + x - 0.28, zb + 0.56), (cx + x + 0.28, zb + 0.56), (cx + x + 0.02, zb + 0.24 - 0.06 * (k % 2))],
                             "y", -Wd / 2 - 0.08, -Wd / 2 + 0.02))
    out.setdefault(C.CHEESE, []).extend([chz] + drips)
    toms = [ns.cyl(0.55, 0.12, loc=(cx + x, -0.12 + 0.1 * (k % 2), zb + 0.63), verts=8, bevel=0.0)
            for k, x in enumerate((-1.6, 1.6))]
    out.setdefault(C.TOMATO, []).extend(toms)
    wave = [(cx - L / 2 - 0.15, zb + 0.84), (cx + L / 2 + 0.15, zb + 0.84)]
    for i in range(13):
        x = cx + L / 2 + 0.15 - (L + 0.3) * i / 12
        wave.append((x, zb + 0.68 + (0.07 if i % 2 else -0.04)))
    out.setdefault(C.LETTUCE, []).append(C.prism(wave, "y", -Wd / 2 - 0.14, Wd / 2 + 0.14))
    top = ns.box((L + 0.1, Wd + 0.05, 0.8), loc=(cx, 0, zb + 0.8 + 0.4), bevel=0.38, segments=2)
    out[C.BUN].append(top)
    for x in (-1.9, 0.0, 1.9):
        sl = ns.box((0.95, 0.16, 0.05), loc=(cx + x, 0, zb + 1.585), rot=(0, 0, 62), bevel=0.0)
        out.setdefault(C.CREAM, []).append(sl)
    return out


def build():
    lower, upper = body_parts()
    x0, x1, z0, z1 = WIN
    xc = (x0 + x1) / 2
    fy = -HW

    # --- belt strip, pinstripe ----------------------------------------------------------------
    ring = C.inset_poly(C.rrect(2 * HL, 2 * HW, 0.5, 3), -0.03)
    belt = C.pipe([(x, y, BELT) for x, y in ring], 0.07, sides=3, closed=True)

    # --- serving window: interior, light, counter, neon frame ------------------------------------
    cav_w, cav_h = x1 - x0, z1 - z0
    inner = [ns.box((cav_w, 0.06, cav_h), loc=(xc, CAV_Y + 0.02, (z0 + z1) / 2), bevel=0.0)]
    cream_in = [ns.box((cav_w, CAV_Y - fy, 0.06), loc=(xc, (fy + CAV_Y) / 2, z1 - 0.02), bevel=0.0),
                ns.box((0.06, CAV_Y - fy, cav_h), loc=(x0 + 0.02, (fy + CAV_Y) / 2, (z0 + z1) / 2), bevel=0.0),
                ns.box((0.06, CAV_Y - fy, cav_h), loc=(x1 - 0.02, (fy + CAV_Y) / 2, (z0 + z1) / 2), bevel=0.0)]
    light = ns.box((cav_w - 0.8, 0.4, 0.06), loc=(xc, (fy + CAV_Y) / 2 + 0.25, z1 - 0.07), bevel=0.0)
    # back-wall dressing: shelf with bread rolls, ticket rail with tickets, a heat-lamp hood
    shelf = ns.box((cav_w - 0.6, 0.35, 0.08), loc=(xc - 0.4, CAV_Y - 0.18, 5.6), bevel=0.0)
    rolls = [ns.box((1.3, 0.34, 0.34), loc=(xc - 1.6 + 1.6 * k, CAV_Y - 0.2, 5.81), bevel=0.15, segments=1) for k in range(2)]
    rail = C.rod((xc - 2.5, CAV_Y - 0.08, 6.45), (xc + 0.8, CAV_Y - 0.08, 6.45), 0.04, verts=4)
    tickets = [ns.box((0.36, 0.02, 0.5), loc=(xc - 2.0 + 0.7 * k, CAV_Y - 0.1, 6.17), rot=(0, (k - 1.5) * 4, 0), bevel=0.0)
               for k in range(4)]
    counter_in = ns.box((cav_w, CAV_Y - fy, 0.1), loc=(xc, (fy + CAV_Y) / 2, z0 - 0.03), bevel=0.0)
    shelf_out = ns.box((cav_w + 0.5, 1.05, 0.14), loc=(xc, fy - 0.45, COUNTER_Z), bevel=0.0)
    brackets = [C.prism([(fy, COUNTER_Z - 0.06), (fy - 0.85, COUNTER_Z - 0.06), (fy, COUNTER_Z - 0.75)], "x", xb - 0.06, xb + 0.06)
                for xb in (x0 + 0.5, xc, x1 - 0.5)]
    neon_path = [(x0 - 0.2, fy - 0.06, COUNTER_Z + 0.1), (x0 - 0.2, fy - 0.06, z1 + 0.2), (x1 + 0.2, fy - 0.06, z1 + 0.2),
                 (x1 + 0.2, fy - 0.06, COUNTER_Z + 0.1)]
    win_neon = C.pipe(neon_path, 0.075, sides=5, corner=0.3, corner_segs=3)
    # counter top props: napkin box + napkins, ketchup + mustard bottles
    nap_box = ns.box((0.6, 0.4, 0.4), loc=(xc + 1.6, fy - 0.5, COUNTER_Z + 0.27), bevel=0.0)
    napkins = ns.box((0.44, 0.26, 0.16), loc=(xc + 1.6, fy - 0.5, COUNTER_Z + 0.5), rot=(0, 0, 5), bevel=0.0)
    bottles = {}
    for bx, col in ((xc - 1.9, C.KETCHUP), (xc - 1.4, C.MUSTARD_SAUCE)):
        bottles.setdefault(col, []).append(ns.cyl(0.19, 0.78, loc=(bx, fy - 0.45, COUNTER_Z + 0.46), verts=8, bevel=0.0))
        bottles[col].append(C.rod((bx, fy - 0.45, COUNTER_Z + 0.84), (bx, fy - 0.45, COUNTER_Z + 1.16), 0.12, verts=6, r_top=0.03))

    # --- awning + struts + festoon bulbs -----------------------------------------------------------
    ax0, ax1, azb, ayf, azf = AWN
    awn = C.awning(ax0, ax1, fy + 0.05, azb, ayf, azf, n=7, t=0.09, valance=0.5, cols=(C.BRAND, C.PAPER))
    struts = []
    for xs in (ax0 + 0.25, ax1 - 0.25):
        struts.append(C.rod((xs, fy + 0.05, 5.35), (xs, ayf + 0.12, azf - 0.06), 0.05, verts=5))
    hooks = [ax0 + 0.15 + (ax1 - ax0 - 0.3) * k / 4 for k in range(5)]
    cable_pts, bulb_c, socks = [], [], []
    yb, zh = ayf - 0.1, azf - 0.42
    for xa, xb in zip(hooks[:-1], hooks[1:]):
        swag = C.catenary((xa, yb, zh), (xb, yb, zh), 0.42, n=6)
        cable_pts.append(C.pipe(swag, 0.035, sides=3))
        s_objs, cents = C.hang_bulbs(swag, 3, r=0.2, drop=0.0, sock_r=0.075, sock_h=0.14, end_pad=0.32,
                                     fine=C.catenary((xa, yb, zh), (xb, yb, zh), 0.42, n=60), wires=False, sock_verts=4)
        socks += s_objs
        bulb_c += cents
    bulbs = C.spheres(bulb_c, 0.2, segs=6, rings=3, scale=(1, 1, 1.1))

    # --- menu board + screen ---------------------------------------------------------------------
    mx, mz, mw, mh = MENU
    board = C.prism(C.rrect(mw, mh, 0.16, 2, mx, mz), "y", fy - 0.1, fy + 0.02)
    frame = C.ring_slab(C.rrect(mw + 0.2, mh + 0.2, 0.22, 1, mx, mz), C.rrect(mw, mh, 0.16, 1, mx, mz), "y", fy - 0.13, fy + 0.02)
    screen = C.prism(C.rrect(SCR_W, SCR_H, 0.08, 1, mx, SCR_Z), "y", fy - 0.13, fy - 0.09)
    mw_ = C.Word("MENU", mx, cap=0.34, spacing=1.15, base=mz + mh / 2 - 0.58, res=1)
    menu_txt = mw_.solid(fy - 0.14, 0.03, front_only=True, name="MenuText")

    # --- livery: STACKHOUSE letters (front), badge (back), pinstripe ------------------------------
    sw = C.Word("STACKHOUSE", -2.6, cap=0.72, spacing=1.08, base=2.55, res=1, xscale=1.05)
    sw.fit_width(6.6)
    letters = sw.solid(fy - 0.05, 0.05, front_only=True, name="Livery")
    pin = [ns.box((2 * HL - 1.2, 0.04, 0.1), loc=(-0.1, sy * (HW + 0.01), 3.32), bevel=0.0) for sy in (-1, 1)]
    for o in pin:      # keep the pinstripe off the wheel arches: split round them
        for x in WHEELS:
            ns.boolean(o, ns.box((2 * (WR + 0.3), 1.0, 2.0), loc=(x, 0, 2.0), bevel=0.0))
    badge = C.mini_logo((-2.4, HW - 0.001, 5.4), r=1.45, yaw=180, depth=0.12, disc=C.BRAND, n=14)

    # --- cab: windshield, side windows, door seams, mirrors, lamps, grille, bumpers ----------------
    glass = []
    a, b = Vector((6.98, 5.55)), Vector((6.22, 7.75))
    d = (b - a).normalized()
    nrm = Vector((d.y, -d.x))                      # outward (+x, +z side)
    quad = [tuple(a + nrm * -0.02), tuple(b + nrm * -0.02), tuple(b + nrm * 0.05), tuple(a + nrm * 0.05)]
    for y0, y1 in ((-HW + 0.55, -0.07), (0.07, HW - 0.55)):
        glass.append(C.prism(quad, "y", y0, y1))
    for sy in (-1, 1):
        a0, a1 = sorted((sy * (HW - 0.02), sy * (HW + 0.04)))
        glass.append(C.prism(C.fillet([(4.55, 5.3), (6.05, 5.3), (6.05, 7.35), (4.55, 7.35)], 0.22, 1), "y", a0, a1))
    dark = []
    for sy in (-1, 1):
        a0, a1 = sorted((sy * (HW - 0.01), sy * (HW + 0.03)))
        for xd in (4.3, 6.35):
            dark.append(ns.box((0.05, a1 - a0, 6.3), loc=(xd, (a0 + a1) / 2, 4.45), bevel=0.0))
    chrome = [shelf_out, nap_box, rail, frame, belt] + brackets + struts
    for sy in (-1, 1):
        chrome.append(C.rod((6.55, sy * (HW - 0.05), 6.0), (6.6, sy * (HW + 0.32), 6.15), 0.06, verts=5))
        m = ns.cyl(0.22, 0.1, verts=6, bevel=0.0)
        C.place(m, (6.62, sy * (HW + 0.34), 6.3), yaw=90, pitch=90)
        dark.append(m)
        chrome.append(ns.box((0.26, 0.08, 0.08), loc=(4.6, sy * (HW + 0.05), 4.9), bevel=0.0))   # door handle
    lamps, lenses = [], []
    for sy in (-1, 1):
        rim = ns.cyl(0.46, 0.14, verts=8, radius_top=0.4, bevel=0.0)
        C.place(rim, (HL - 0.02, sy * 2.15, 3.35), yaw=-90, pitch=90)
        chrome.append(rim)
        lens = ns.cyl(0.36, 0.1, verts=8, radius_top=0.26, bevel=0.0)
        C.place(lens, (HL + 0.06, sy * 2.15, 3.35), yaw=-90, pitch=90)
        lenses.append(lens)
        tail = ns.box((0.08, 0.5, 0.9), loc=(-HL - 0.02, sy * 2.25, 2.6), bevel=0.0)
        lamps.append(tail)
    chrome.append(C.prism(C.rrect(1.9, 1.1, 0.3, 2, 0, 3.0), "x", HL - 0.03, HL + 0.04))
    for k in range(2):
        dark.append(ns.box((0.04, 1.5, 0.14), loc=(HL + 0.06, 0, 2.8 + 0.4 * k), bevel=0.0))
    for xb, sx in ((HL + 0.12, 1), (-HL - 0.12, -1)):
        chrome.append(ns.box((0.42, 2 * HW + 0.2, 0.5), loc=(xb, 0, 1.3), bevel=0.18, segments=1))
    tyres, walls, hubs = [], [], []
    for x in WHEELS:
        for sy in (-1, 1):
            t, w, h = wheel(x, sy)
            tyres.append(t)
            walls.append(w)
            hubs.append(h)
    under = ns.box((2 * HL - 1.4, 2 * HW - 1.4, 0.4), loc=(0, 0, 0.9), bevel=0.0)
    sand = roof_sandwich(-1.3, ROOF)
    roof_neon = [C.pipe([(-HL + 0.9, sy * (HW + 0.04), 7.68), (5.75, sy * (HW + 0.04), 7.68)], 0.06, sides=5) for sy in (-1, 1)]

    # --- parts ----------------------------------------------------------------------------------------
    C.part([upper], "BodyCream", VAN_CREAM, can_collide=True, smooth_angle=40)
    C.part([lower], "BodyRed", C.BRAND, can_collide=True, smooth_angle=40)
    C.part(tyres + [under], "Tyres", C.RUBBER, can_collide=True, smooth_angle=45)
    C.part(walls, "Whitewalls", C.CREAM, smooth_angle=None)
    C.part(hubs, "Hubs", C.BRAND, smooth_angle=45)
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    C.part(dark, "Trim", C.CHARCOAL, smooth_angle=40)
    C.part(glass, "Glass", C.GLASS_DARK, "Glass", smooth_angle=30)
    C.part(lenses, "Headlights", "#F7F0D2", smooth_angle=50)
    C.part(lamps, "TailLights", "#B3221E", smooth_angle=40)
    C.part(inner + [counter_in], "Stainless", STEEL_IN, "Metal", smooth_angle=30)
    C.part(cream_in + [shelf], "InteriorCream", "#E2D6BD", smooth_angle=30)
    C.part(tickets + [napkins], "Paper", C.PAPER, smooth_angle=30)
    C.part(rolls, "Rolls", C.BUN, smooth_angle=50)
    C.part(awn[C.BRAND], "AwningRed", C.BRAND, "Fabric", smooth_angle=None)
    C.part(awn[C.PAPER], "AwningCream", C.PAPER, "Fabric", smooth_angle=None)
    C.part(cable_pts + socks, "Cable", C.CABLE, smooth_angle=60)
    C.part([board], "MenuBoard", C.NAVY, smooth_angle=40)
    C.part([menu_txt] + pin, "MustardTrim", C.MUSTARD, smooth_angle=None)
    C.part([letters], "Livery", VAN_CREAM, smooth_angle=None)
    C.part(bottles[C.KETCHUP], "Ketchup", C.KETCHUP, smooth_angle=45)
    C.part(bottles[C.MUSTARD_SAUCE], "Mustard", C.MUSTARD_SAUCE, smooth_angle=45)
    names = {C.CHROME: "SandwichStands", C.BUN: "SandwichBun", C.CHEESE: "SandwichCheese", C.TOMATO: "SandwichTomato",
             C.LETTUCE: "SandwichLettuce", C.CREAM: "SandwichScores"}
    for col, objs in sand.items():
        C.part(objs, names[col], col, "Metal" if col == C.CHROME else "SmoothPlastic", smooth_angle=50)
    C.add_parts(badge, "Badge", smooth_angle=40)
    ns.tag(screen, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
    ns.tag(light, "InteriorLight", WARM_IN, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=30)
    ns.tag(bulbs, "Bulbs", C.BULB, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=80)
    ns.tag(win_neon, "WindowNeon", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    ns.tag(C.merge(roof_neon, "RoofNeon"), "RoofNeon", C.PINK, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    return {}


def sockets():
    mx, mz, mw, mh = MENU
    xc = (WIN[0] + WIN[1]) / 2
    return {"Screen": ((mx, -HW - 0.13, SCR_Z), 0.0), "Prompt": ((xc, -HW - 2.4, 3.0), 0.0),
            "Light": ((xc, -HW - 1.2, 6.2), 0.0)}


META = {"screen_size": [SCR_W, SCR_H], "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
        "counter_height": COUNTER_Z + 0.07, "serving_side": "-Y (front)", "cab": "Blender +X = Roblox -X",
        "roles": {"screen": "Screen (menu board)", "lamp": "Bulbs (awning festoon), InteriorLight (kitchen ceiling)",
                  "neon": "WindowNeon (cyan window frame), RoofNeon (pink side lines)"},
        "light_hint": {"type": "PointLight", "at": "Socket_Light", "color": C.BULB, "range": 14, "brightness": 1.1}}

if __name__ == "__main__":
    C.run(build, "Lobby_FoodTruck", sockets=sockets(), meta=META, budget=4000, pivot=(0.0, 0.0, 0.0),
          far=True, far_kw={"dist": 40.0})
