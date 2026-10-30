"""Lobby_ShopFront — the SHOP: a stand-alone two-storey storefront (~38.5 x 29 x 18).

A closed brick-and-cream building box (stone plinth, red-orange floor band with a mustard
pinstripe, navy cornice; sides and back plain but finished, with a back door). Facade:

  * ground floor: display window 1 (left, coins) | the open service counter window | display
    window 3 (right, gift). The counter (top at 3.0) is red-orange with a cream laminate top and
    chrome edge; behind it, on the navy back wall of the booth, the featured-offer screen (Screen,
    9 x 5). A red-orange / cream striped awning with a scalloped valance shades the counter.
  * upper floor: display window 2 (centre, star tokens), flanked by STACKHOUSE logo badges.
  * Each display window is a lit recess (warm lamp strip, LampStrips role "lamp") behind a glass
    pane (Glass role "glass") with a round cream pedestal ringed by a warm glowing band (role
    "lamp") holding a giant hero prop: a mountain of amber star-stamped coins, a heap of big pink
    star tokens, a red gift box with a mustard bow. A label screen sits above each window
    (Label1 / Label2 / Label3, 6.5 x 1.8).
  * On the roof front: a navy sign box with GIANT neon "SHOP" letters — magenta letter backers,
    pink neon outline tubes (SignPink) and a cyan neon centre line (SignCyan), both role "neon" —
    ringed by warm marquee bulbs (Bulbs, role "lamp"), on steel struts.

Front = -Y, pivot = bottom-centre. Sockets: Screen (featured-offer screen face centre), Label1..3
(label face centres), Prompt (in front of the counter at y 3). All screens face front.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

HX = 19.0                    # building half width
FY, WY, CY, BY = -6.5, -5.5, 0.0, 8.0   # facade face, front-slab back, recess back (core front), back face
PLINTH = 0.8
BAND = (10.6, 11.3)
TOP = 19.6                   # facade top (cornice starts)
CORNICE = (19.5, 20.5)
# openings (x0, x1, z0, z1)
DW1 = (-17.2, -8.2, 1.75, 8.0)
DW3 = (8.2, 17.2, 1.75, 8.0)
CTR = (-6.0, 6.0, 3.0, 9.0)
DW2 = (-6.0, 6.0, 12.0, 16.9)
LBL_W, LBL_H = 6.5, 1.8
LBL = {"Label1": (-12.7, 9.45), "Label2": (0.0, 18.4), "Label3": (12.7, 9.45)}
SCR_W, SCR_H, SCR_Z = 9.0, 5.0, 6.05
SCR_Y = CY - 0.15
COUNTER_TOP = 3.0
SIGN = (-16.6, 16.6, 20.5, 29.0)
SIGN_Y = (-7.1, -5.7)
SIGN_CAP = 7.0
MAGENTA = "#6E1E52"
GIFT_RED = "#D22F3A"
STAR_PINK = "#FF4FA3"
STAR_LIGHT = "#FFA6D2"
INTERIOR = "#1E2A44"
PED_R = 2.4
GLASS_TINT = "#D3E8EF"


def liner(x0, x1, z0, z1, y0, y1, bottom=True):
    """Open box (back, sides, top[, bottom]) with faces pointing INTO the recess."""
    bm = bmesh.new()
    v = {}
    for xi, x in enumerate((x0, x1)):
        for yi, y in enumerate((y0, y1)):
            for zi, z in enumerate((z0, z1)):
                v[(xi, yi, zi)] = bm.verts.new((x, y, z))
    quads = [
        [v[0, 1, 0], v[1, 1, 0], v[1, 1, 1], v[0, 1, 1]],      # back (normal -Y)
        [v[0, 0, 0], v[0, 1, 0], v[0, 1, 1], v[0, 0, 1]],      # left wall (normal +X)
        [v[1, 0, 0], v[1, 0, 1], v[1, 1, 1], v[1, 1, 0]],      # right wall (normal -X)
        [v[0, 0, 1], v[0, 1, 1], v[1, 1, 1], v[1, 0, 1]],      # ceiling (normal -Z)
    ]
    if bottom:
        quads.append([v[0, 0, 0], v[1, 0, 0], v[1, 1, 0], v[0, 1, 0]])   # floor (normal +Z)
    for q in quads:
        bm.faces.new(q)
    bm.normal_update()
    ctr = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    for f in bm.faces:
        if (f.calc_center_median() - ctr).dot(f.normal) > 0:   # must point at the centre
            f.normal_flip()
    return C.obj_from_bm(bm, "Liner")


def coin(r, t, loc, rot, stars=2, verts=12):
    """Upright coin (axis along Y before rot), optional star stamps. -> (coin_objs, star_objs)."""
    body = ns.cyl(r, t, loc=(0, 0, 0), verts=verts, bevel=0.0)
    body.rotation_euler = (math.radians(90), 0, 0)
    ns.apply_all(body)
    st = []
    if stars:
        st.append(C.prism(C.star_pts(r * 0.62, r * 0.27), "y", -t / 2 - 0.07, -t / 2 + 0.01))
        if stars > 1:
            st.append(C.prism(C.star_pts(r * 0.62, r * 0.27), "y", t / 2 - 0.01, t / 2 + 0.07))
    objs = [body] + st
    for o in objs:
        o.rotation_euler = tuple(math.radians(a) for a in rot)
        o.location = Vector(loc)
        ns.apply_all(o)
    return [body], st


def star_token(r, t, loc, rot, light=False):
    """Chunky 5-point star token (faces along Y before rot); the lit hero one is bevelled.
    -> (star, inner_light or None)."""
    s = C.prism(C.star_pts(r, r * 0.47), "y", -t / 2, t / 2)
    if light:
        ns.bevel(s, width=min(0.1, t * 0.22), segments=1)
    ns.apply_all(s)
    inner = None
    if light:
        inner = C.prism(C.star_pts(r * 0.52, r * 0.24), "y", -t / 2 - 0.12, -t / 2 + 0.02)
    for o in [s] + ([inner] if inner else []):
        o.rotation_euler = tuple(math.radians(a) for a in rot)
        o.location = Vector(loc)
        ns.apply_all(o)
    return s, inner


def coin_mountain(cx, cy, z0, k=1.17):
    mound = ns.lathe([(r * k, z * k) for r, z in ((1.85, 0.0), (1.78, 0.3), (1.45, 0.95), (0.95, 1.65), (0.42, 2.15),
                                                   (0.0, 2.3))], verts=12)
    mound.location = (cx, cy, z0)
    ns.apply_all(mound)
    coins, stars = [mound], []
    specs = [  # (r, t, (dx, dy, dz), (rx, ry, rz), stars)
        (1.3, 0.34, (0.0, -0.1, 2.9), (0, 8, 0), 2),            # big upright coin on the summit
        (0.92, 0.28, (-1.25, -0.95, 1.25), (-18, -6, 24), 1),   # front-left, leaning back
        (0.86, 0.28, (1.3, -0.85, 1.05), (-16, 10, -28), 1),    # front-right
    ]
    for i in range(5):   # flat coins on the slopes
        a = math.radians(30 + 72 * i)
        specs.append((0.8, 0.26, (1.55 * math.cos(a), 1.55 * math.sin(a) * 0.9, 0.62),
                      (90 - 32, 0, math.degrees(a) - 90), 0))
    for r, t, (dx, dy, dz), rot, ns_ in specs:
        c, s = coin(r * k, t * k, (cx + dx * k, cy + dy * k, z0 + dz * k), rot, stars=ns_)
        coins += c
        stars += s
    # short stacks of flat coins round the foot of the pile (front-left, front, front-right)
    for (dx, dy), n in (((-1.75, -1.0), 2), ((0.15, -1.75), 2), ((1.8, -0.95), 3)):
        for j in range(n):
            jx, jy = 0.05 * ((j * 37) % 3 - 1), 0.05 * ((j * 53) % 3 - 1)
            coins.append(ns.cyl(0.62, 0.22, loc=(cx + dx + jx, cy + dy + jy, z0 + 0.11 + 0.23 * j), verts=10, bevel=0.0))
    return coins, stars


def star_heap(cx, cy, z0, k=1.12):
    stars, inner = [], []
    specs = [  # (r, t, (dx, dy, dz), rot, light)
        (1.1, 0.5, (-1.35, 0.4, 0.8), (52, -14, 28), False),
        (1.05, 0.5, (1.4, 0.45, 0.78), (50, 16, -30), False),
        (0.95, 0.46, (0.0, -0.95, 0.55), (62, 0, 6), False),
        (0.95, 0.46, (-1.05, -0.55, 1.45), (22, -20, -16), False),
        (0.95, 0.46, (1.1, -0.45, 1.5), (20, 22, 20), False),
        (1.45, 0.6, (0.0, 0.05, 2.1), (-6, 0, 0), True),      # the big upright token on top
    ]
    for r, t, (dx, dy, dz), rot, light in specs:
        s, i = star_token(r * k, t * k, (cx + dx * k, cy + dy * k, z0 + dz * k), rot, light)
        stars.append(s)
        if i:
            inner.append(i)
    return stars, inner


def gift_box(cx, cy, z0, yaw=12.0, k=1.18):
    red, gold = [], []
    w, h = 2.6 * k, 2.1 * k
    red.append(ns.box((w, w, h), loc=(0, 0, h / 2), bevel=0.08, segments=1))
    red.append(ns.box((w + 0.24, w + 0.24, 0.55), loc=(0, 0, h + 0.2), bevel=0.08, segments=1))
    for k, (sx, sy) in enumerate(((1, 0), (0, 1))):   # ribbon bands over sides and lid (2nd one 0.02 proud,
        e = 0.02 * k                                       # so their crossing top faces are not coplanar)
        gold.append(ns.box((w + 0.3 + e if sx else 0.5 + e, w + 0.3 + e if sy else 0.5 + e, h + 0.62 + 2 * e),
                           loc=(0, 0, (h + 0.62) / 2 - 0.02), bevel=0.02, segments=1))
    for side in (-1, 1):   # bow loops
        loop = ns.torus(0.5 * k, 0.17 * k, major_segs=8, minor_segs=4)
        loop.scale = (1.0, 0.5, 0.8)
        loop.rotation_euler = (math.radians(90), math.radians(side * 48), math.radians(side * 10))
        loop.location = (side * 0.55 * k, 0, h + 0.47 + 0.48 * k)
        gold.append(loop)
    gold.append(ns.sphere(0.27 * k, loc=(0, 0, h + 0.62), scale=(1.1, 0.9, 0.85), segs=8, rings=5))
    for side in (-1, 1):  # tails
        gold.append(C.prism([(0, h + 0.55), (side * 0.75 * k, h + 0.15), (side * 0.95 * k, h + 0.32), (side * 0.25 * k, h + 0.62)],
                            "y", -0.38 * k, -0.2 * k))
    C.place(red + gold, (cx, cy, z0), yaw=yaw)
    return red, gold


def build():
    brick, cream, band, stone, navy, chrome, interior, lamps, glass = [], [], [], [], [], [], [], [], []
    # ----- shell ----------------------------------------------------------------------------
    stone.append(ns.box((2 * HX + 0.4, BY - FY + 0.4, PLINTH), loc=(0, (FY + BY) / 2, PLINTH / 2), bevel=0.1, segments=1))
    # solid core behind the recesses; its front sits 0.1 behind the liners' back walls (coplanar faces
    # facing the same way would z-fight in Roblox)
    cf = CY + 0.1
    brick.append(ns.box((2 * HX, BY - cf, BAND[0] - PLINTH), loc=(0, (cf + BY) / 2, (PLINTH + BAND[0]) / 2), bevel=0.0))
    cream.append(ns.box((2 * HX, BY - cf, TOP - BAND[1]), loc=(0, (cf + BY) / 2, (BAND[1] + TOP) / 2), bevel=0.0))
    for s in (-1, 1):   # front-zone side slabs (behind the end piers, reaching back to the core)
        x = s * (HX - 0.5)
        brick.append(ns.box((1.0, cf - WY, BAND[0] - PLINTH), loc=(x, (WY + cf) / 2, (PLINTH + BAND[0]) / 2), bevel=0.0))
        cream.append(ns.box((1.0, cf - WY, TOP - BAND[1]), loc=(x, (WY + cf) / 2, (BAND[1] + TOP) / 2), bevel=0.0))
    band.append(ns.box((2 * HX + 0.16, BY - FY + 0.16, BAND[1] - BAND[0]), loc=(0, (FY + BY) / 2, sum(BAND) / 2), bevel=0.04,
                       segments=1))
    pin = [ns.box((2 * HX + 0.22, BY - FY + 0.22, 0.12), loc=(0, (FY + BY) / 2, BAND[0] - 0.1), bevel=0.0)]
    navy.append(ns.box((2 * HX + 0.5, BY - FY + 0.5, CORNICE[1] - CORNICE[0]), loc=(0, (FY + BY) / 2, sum(CORNICE) / 2),
                       bevel=0.1, segments=1))
    pin.append(ns.box((2 * HX + 0.56, BY - FY + 0.56, 0.12), loc=(0, (FY + BY) / 2, CORNICE[0] + 0.22), bevel=0.0))

    def slab(x0, x1, z0, z1, lst):
        lst.append(ns.box((x1 - x0, WY - FY, z1 - z0), loc=((x0 + x1) / 2, (FY + WY) / 2, (z0 + z1) / 2), bevel=0.0))

    # ground floor front slabs (brick)
    for s in (-1, 1):
        slab(*sorted((s * 17.2, s * HX)), PLINTH, BAND[0], brick)       # end piers
        slab(*sorted((s * 6.0, s * 8.2)), PLINTH, BAND[0], brick)       # counter piers
        dx0, dx1 = sorted((s * 8.2, s * 17.2))
        slab(dx0, dx1, PLINTH, DW1[2] - 0.25, brick)                    # under the sill
        slab(dx0, dx1, DW1[3], BAND[0], brick)                          # above the window
        stone.append(ns.box((dx1 - dx0 + 0.5, WY - FY + 0.3, 0.25), loc=((dx0 + dx1) / 2, (FY + WY) / 2 - 0.15, DW1[2] - 0.125),
                            bevel=0.05, segments=1))                     # sills
    slab(CTR[0], CTR[1], CTR[3], BAND[0], brick)                         # over the counter opening
    # upper floor front slabs (cream)
    for s in (-1, 1):
        slab(*sorted((s * 6.0, s * HX)), BAND[1], TOP, cream)
    slab(DW2[0], DW2[1], BAND[1], DW2[2], cream)
    slab(DW2[0], DW2[1], DW2[3], TOP, cream)
    # recess liners + glass + frames + lamp strips
    for (x0, x1, z0, z1), bottom in ((DW1, True), (DW3, True), (DW2, True), (CTR, False)):
        interior.append(liner(x0, x1, z0, z1, WY, CY, bottom=bottom))
        # the reveal between the facade and the liner (front-slab thickness) also gets the interior colour
        if (x0, x1, z0, z1) != CTR:
            glass.append(ns.box((x1 - x0 + 0.1, 0.06, z1 - z0 + 0.1), loc=((x0 + x1) / 2, FY + 0.45, (z0 + z1) / 2), bevel=0.0))
        fo = C.rrect(x1 - x0 + 0.76, z1 - z0 + 0.76, 0.3, 2, (x0 + x1) / 2, (z0 + z1) / 2)
        fi = C.rrect(x1 - x0 - 0.12, z1 - z0 - 0.12, 0.08, 2, (x0 + x1) / 2, (z0 + z1) / 2)
        fr = C.ring_slab(fo, fi, "y", FY - 0.22, FY + 0.06)
        cream.append(fr) if (x0, x1, z0, z1) != CTR else chrome.append(fr)
        lamps.append(ns.box((x1 - x0 - 0.6, 0.22, 0.14), loc=((x0 + x1) / 2, WY + 0.25, z1 - 0.06), bevel=0.0))
    # ----- counter ----------------------------------------------------------------------------
    counter = [ns.box((CTR[1] - CTR[0], WY - FY + 0.4, COUNTER_TOP - 0.18 - PLINTH),
                      loc=(0, (FY - 0.4 + WY) / 2, PLINTH + (COUNTER_TOP - 0.18 - PLINTH) / 2), bevel=0.0)]
    top = C.prism(C.rrect(CTR[1] - CTR[0], CY - (FY - 0.8), 0.12, 1, 0, (CY + FY - 0.8) / 2), "z", COUNTER_TOP - 0.18,
                  COUNTER_TOP)
    cream.append(top)
    chrome.append(C.pipe([(CTR[0], FY - 0.8, COUNTER_TOP - 0.09), (CTR[1], FY - 0.8, COUNTER_TOP - 0.09)], 0.1, sides=6))
    chrome.append(ns.box((CTR[1] - CTR[0], 0.08, 0.32), loc=(0, FY - 0.43, PLINTH + 0.16), bevel=0.0))   # kick plate
    pin.append(ns.box((CTR[1] - CTR[0], 0.06, 0.14), loc=(0, FY - 0.42, COUNTER_TOP - 0.55), bevel=0.0))
    scr = C.prism(C.rrect(SCR_W, SCR_H, 0.12, 1, 0, SCR_Z), "y", SCR_Y, CY + 0.02)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
    chrome.append(C.ring_slab(C.rrect(SCR_W + 0.44, SCR_H + 0.44, 0.25, 1, 0, SCR_Z), C.rrect(SCR_W, SCR_H, 0.12, 1, 0, SCR_Z),
                              "y", SCR_Y - 0.08, CY + 0.01))
    # awning over the counter
    aw = C.awning(-7.4, 7.4, FY + 0.05, BAND[0] - 0.15, FY - 3.3, 9.45, n=10, t=0.09, valance=0.5)
    # ----- labels ---------------------------------------------------------------------------------
    for name, (x, z) in LBL.items():
        s = C.prism(C.rrect(LBL_W, LBL_H, 0.1, 1, x, z), "y", FY - 0.12, FY + 0.02)
        ns.tag(s, name, C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
        chrome.append(C.ring_slab(C.rrect(LBL_W + 0.36, LBL_H + 0.36, 0.2, 1, x, z), C.rrect(LBL_W, LBL_H, 0.1, 1, x, z), "y",
                                  FY - 0.18, FY + 0.02))
    # ----- pedestals + hero props -------------------------------------------------------------------
    peds, glow = [], []
    py = (WY + CY) / 2
    tops = {}
    for key, (x0, x1, z0, z1), h in (("coins", DW1, 0.9), ("gift", DW3, 0.9), ("stars", DW2, 0.7)):
        xc = (x0 + x1) / 2
        ped = C.prism(C.circle_pts(PED_R, 14, xc, py), "z", z0, z0 + h)   # same vertex phase as the glow band
        ns.bevel(ped, width=0.06, segments=1)
        peds.append(ped)
        glow.append(C.band(PED_R + 0.03, 0.2, loc=(xc, py, z0 + h - 0.16), verts=14))
        tops[key] = (xc, py, z0 + h)
    coins, coin_stars = coin_mountain(*tops["coins"])
    stars, star_inner = star_heap(*tops["stars"])
    gred, ggold = gift_box(*tops["gift"])
    # ----- upper-floor badges -----------------------------------------------------------------------
    badges = {}
    for s in (-1, 1):
        C.merge_into(badges, C.badge((s * 12.6, FY + 0.001, 15.3), r=2.3, n=12))
    # ----- back door ---------------------------------------------------------------------------------
    navy.append(ns.box((4.0, 0.2, 7.2), loc=(8.0, BY + 0.08, PLINTH + 3.6), bevel=0.04, segments=1))
    chrome.append(ns.box((0.25, 0.25, 0.9), loc=(9.5, BY + 0.25, PLINTH + 3.4), bevel=0.05, segments=1))
    stone.append(ns.box((4.8, 0.3, 0.45), loc=(8.0, BY + 0.1, PLINTH + 7.35), bevel=0.05, segments=1))
    # ----- roof sign --------------------------------------------------------------------------------
    sx0, sx1, sz0, sz1 = SIGN
    box_o = C.rrect(sx1 - sx0, sz1 - sz0, 0.7, 3, 0, (sz0 + sz1) / 2)
    sbox = C.prism(box_o, "y", SIGN_Y[0], SIGN_Y[1])
    ns.bevel(sbox, width=0.08, segments=1)
    navy.append(sbox)
    chrome.append(C.ring_slab(C.rrect(sx1 - sx0 + 0.36, sz1 - sz0 + 0.36, 0.85, 3, 0, (sz0 + sz1) / 2),
                              C.rrect(sx1 - sx0 - 0.1, sz1 - sz0 - 0.1, 0.66, 3, 0, (sz0 + sz1) / 2), "y",
                              SIGN_Y[0] - 0.1, SIGN_Y[0] + 0.3))
    zc = (sz0 + sz1) / 2
    w = C.Word("SHOP", 0.0, cap=SIGN_CAP, spacing=1.12, base=zc - SIGN_CAP / 2, xscale=1.05)
    backer = w.solid(SIGN_Y[0] - 0.36, 0.38, offset=0.3, back=False, name="Backer")
    C.part([backer], "SignBacker", MAGENTA, smooth_angle=30)
    pink = C.contour_tubes(w.loops(offset=-0.24), SIGN_Y[0] - 0.43, 0.13, sides=4)
    ns.tag(pink, "SignPink", C.PINK, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    cy_objs = [C.pipe([(x, SIGN_Y[0] - 0.44, z) for x, z in p], 0.1, sides=4, closed=cl)
               for cl, p in C.stroke_paths(w.loops(), spacing=0.5)]
    ns.tag(C.merge(cy_objs, "SignCyan"), "SignCyan", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    bulb_path = C.rect_path(sx0 + 0.55, sx1 - 0.55, sz0 + 0.55, sz1 - 0.55, SIGN_Y[0] + 0.01, r=0.5, segs=2)
    bpts = C.path_points(bulb_path, 1.25, closed=True)
    bulbs = C.domes(bpts, 0.21, axis=(0, -1, 0), segs=6, rings=2)
    ns.tag(bulbs, "Bulbs", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=80)
    steel = []
    for x in (-11.5, 0.0, 11.5):
        steel.append(C.rod((x, SIGN_Y[1] - 0.1, sz1 - 1.6), (x, CY + 0.5, CORNICE[1]), 0.16, verts=6))
        steel.append(C.rod((x, SIGN_Y[1] - 0.1, sz0 + 1.2), (x, CY - 1.4, CORNICE[1]), 0.14, verts=6))
        steel.append(ns.box((0.9, 0.9, 0.12), loc=(x, CY + 0.5, CORNICE[1] + 0.06), bevel=0.0))
        steel.append(ns.box((0.7, 0.7, 0.12), loc=(x, CY - 1.4, CORNICE[1] + 0.06), bevel=0.0))

    # ----- tag -----------------------------------------------------------------------------------------
    C.part(brick, "Brick", C.BRICK, "Brick", can_collide=True, smooth_angle=40)
    C.part(cream, "Cream", C.CREAM, can_collide=True, smooth_angle=40)
    C.part(band + counter, "BrandBand", C.BRAND, can_collide=True, smooth_angle=40)
    C.part(stone, "Stone", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(navy, "Navy", C.NAVY, can_collide=True, smooth_angle=40)
    C.part(pin + ggold + badges.pop(C.CHEESE, []), "Mustard", C.MUSTARD, smooth_angle=40)
    C.part(chrome + steel, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    C.part(interior, "Interior", INTERIOR, smooth_angle=None)
    C.part(peds, "Pedestals", C.CREAM, "Marble", smooth_angle=40)
    ns.tag(C.merge(glow, "PedestalGlow"), "PedestalGlow", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False,
           smooth_angle=60)
    ns.tag(C.merge(lamps, "LampStrips"), "LampStrips", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False,
           smooth_angle=40)
    ns.tag(C.merge(glass, "Glass"), "Glass", GLASS_TINT, "Glass", transparency=0.8, recolor="glass", cast_shadow=False,
           smooth_angle=30)
    C.part(coins, "Coins", C.AMBER, "Metal", smooth_angle=40)
    C.part(coin_stars, "CoinStars", "#FFD45C", "Metal", smooth_angle=30)
    C.part(stars, "StarTokens", STAR_PINK, smooth_angle=40)
    C.part(star_inner, "StarShine", STAR_LIGHT, smooth_angle=30)
    C.part(gred, "GiftBox", GIFT_RED, smooth_angle=40)
    C.part(aw[C.BRAND] + badges.pop(C.BRAND), "AwningRed", C.BRAND, smooth_angle=None)
    C.part(aw[C.PAPER], "AwningCream", C.PAPER, smooth_angle=None)
    C.add_parts(badges, "Badge", smooth_angle=40)


def sockets():
    s = {"Screen": ((0.0, SCR_Y, SCR_Z), 0.0), "Prompt": ((0.0, FY - 2.3, COUNTER_TOP), 0.0)}
    for name, (x, z) in LBL.items():
        s[name] = ((x, FY - 0.12, z), 0.0)
    return s


META = {
    "screens": {"Screen": [SCR_W, SCR_H], "Label1": [LBL_W, LBL_H], "Label2": [LBL_W, LBL_H], "Label3": [LBL_W, LBL_H]},
    "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)] + [C.screen_meta(n, LBL_W, LBL_H) for n in LBL],
    "displays": {"Label1": "window 1, ground floor left (as seen from the front): gold coin mountain",
                 "Label2": "window 2, upper floor centre: pink star tokens",
                 "Label3": "window 3, ground floor right: red gift box"},
    "counter_height": COUNTER_TOP,
    "roles": {"screen": "Screen, Label1, Label2, Label3", "glass": "Glass (3 display panes)",
              "neon": "SignPink (letter outlines), SignCyan (centre lines)",
              "lamp": "Bulbs (sign marquee), LampStrips (window + booth lights), PedestalGlow"},
    "light_hint": {"sign": {"type": "PointLight", "at": "in front of the sign, ~4 studs", "color": C.PINK, "range": 30,
                            "brightness": 1.5},
                   "windows": {"type": "PointLight", "per": "display window + booth", "color": C.LAMP_WARM, "range": 9,
                               "brightness": 1}},
}

if __name__ == "__main__":
    C.run(build, "Lobby_ShopFront", sockets=sockets(), meta=META, budget=9000, far=True)
