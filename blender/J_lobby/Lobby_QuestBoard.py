"""Lobby_QuestBoard — the plaza landmark: a giant DAILY QUESTS billboard stand (~46.8 x 35.5 x 7).

Two chunky brick pillars (cast-stone plinths, bands and caps, warm globe lamps on top,
STACKHOUSE logo badges) hold a wide navy board cabinet whose bottom edge sits 4.5 above the
ground so it reads over the crowd. The cabinet has a red-orange frame with a cyan neon inlay
(FrameNeon, role "neon"); on its face the ticker screen (Ticker, 18 x 3.2, where the game writes
"RESETS IN 2h 38m") between a clock and a reward star, and three quest card screens side by side
(Card1 left, Card2 centre, Card3 right as seen from the front; 10.5 x 11 each). Screens are dark
glossy Glass parts (role "screen") in chrome bezels.

On the cabinet top, carried by a steel frame behind them, GIANT 3D marquee letters in two lines —
DAILY over QUESTS (cap height 5.7, ~6.5 with the outline): mustard faces with a chamfered rim, a
deep red-orange inflated outline / body behind, and warm marquee bulbs running down the centre of
every stroke (Bulbs, Neon, role "lamp"). Two flood-lamp arms under the board aim up at it
(FloodLenses, Neon, role "lamp"); globe lamps on the pillar caps (Globes, Neon, role "lamp").

Front = -Y, pivot = bottom-centre. Sockets: Ticker, Card1..Card3 (screen face centres, facing
front), Prompt (centred 4 studs in front of the board at chest height), Lamp1 / Lamp2 (flood lens
centres; aim SpotLights at Socket_Card2).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

# --- cabinet ------------------------------------------------------------------------------
BX = 20.2                     # cabinet half width (ends sit 0.2 inside the pillars)
BZ0, BZ1 = 4.5, 21.9          # bottom edge 4.5 above the ground
BODY_Y = (-0.9, 1.4)          # navy body front / back
FRAME_W = 0.7
FRAME_Y = (-1.4, -0.85)       # red-orange frame front / back (embedded in the body)
PANEL_Y = -1.0                # recessed face panel front plane
SCR_Y = -1.1                  # screen face plane
BEZ = 0.22
CARD_W, CARD_H = 10.5, 11.0
CARD_X = (-11.4, 0.0, 11.4)   # Card1 (left from the front), Card2, Card3
CARD_Z = 11.17                # 5.67 .. 16.67
TICK_W, TICK_H = 18.0, 3.2
TICK_Z = 19.01                # 17.41 .. 20.61
# --- pillars --------------------------------------------------------------------------------
PX0, PX1 = 20.0, 23.2         # pillar x span (mirrored)
PY0, PY1 = -1.9, 2.1
P_TOP = 22.0
# --- letters --------------------------------------------------------------------------------
CAP = 5.7
OUTLINE = 0.42
GAP = 0.45
Q_BASE = BZ1 + OUTLINE        # QUESTS baseline (outline rests on the cabinet top)
D_BASE = Q_BASE + CAP + 2 * OUTLINE + GAP
L_FACE_Y = -1.75              # letter face front plane
L_FACE_D = 0.45
L_BODY_Y = (-1.32, 0.05)      # red-orange body front / back
BULB_R = 0.26
# --- flood lamps ----------------------------------------------------------------------------
LAMP_X = (-9.5, 9.5)
POSTS = (-12.9, 10.4)
AIM = Vector((0.0, SCR_Y, CARD_Z + 0.5))
LAMP_ARM_END = (0.0, -4.0, BZ0 + 0.1)
LAMP_HEAD_OFF = (0.0, -0.3, 0.55)


def flood_lamp(x):
    """Arm from under the cabinet + housing + lens aimed at the board. Returns (steel, housing,
    lens, lens_centre)."""
    steel = [ns.box((1.1, 1.5, 0.4), loc=(x, -0.3, BZ0 - 0.2), bevel=0.06, segments=1)]
    p_end = Vector(LAMP_ARM_END) + Vector((x, 0, 0))
    steel.append(C.pipe([(x, -0.35, BZ0 - 0.24), (x, -2.9, BZ0 - 0.24), tuple(p_end)], 0.14, sides=6, corner=0.5,
                        corner_segs=2))
    head = p_end + Vector(LAMP_HEAD_OFF)
    d = (AIM - head).normalized()
    q = d.to_track_quat("Z", "Y")
    hous = ns.box((1.6, 1.05, 1.2), loc=(0, 0, 0), bevel=0.16, segments=2)
    hous.rotation_euler = q.to_euler()
    hous.location = head
    yoke = C.rod(p_end, head - d * 0.3, 0.12, verts=6)
    lens = ns.box((1.2, 0.68, 0.1), loc=(0, 0, 0), bevel=0.04, segments=1)
    lens.rotation_euler = q.to_euler()
    lens.location = head + d * 0.6
    return steel + [yoke], [hous], [lens], head + d * 0.65


def letters():
    """Both lines: (faces, bodies, bulb points)."""
    faces, bodies, bulbs = [], [], []
    for txt, base in (("QUESTS", Q_BASE), ("DAILY", D_BASE)):
        w = C.Word(txt, 0.0, cap=CAP, spacing=1.06, base=base, res=2, xscale=1.12)
        faces.append(w.solid(L_FACE_Y, L_FACE_D, bevel=0.14, back=False, name="Face" + txt))
        bodies.append(w.solid(L_BODY_Y[0], L_BODY_Y[1] - L_BODY_Y[0], offset=OUTLINE, name="Body" + txt))
        pts, _ = C.stroke_points(w.loops(), 1.12)
        bulbs += [(x, L_FACE_Y + 0.01, z) for x, z in pts]
    return faces, bodies, bulbs


def build():
    # ----- pillars ------------------------------------------------------------------------
    brick, stone = [], []
    for s in (-1, 1):
        x0, x1 = sorted((s * PX0, s * PX1))
        xc = (x0 + x1) / 2
        w, dpt = x1 - x0, PY1 - PY0
        yc = (PY0 + PY1) / 2
        brick.append(ns.box((w, dpt, P_TOP - 1.2), loc=(xc, yc, 1.2 + (P_TOP - 1.2) / 2), bevel=0.1, segments=1))
        stone.append(ns.box((w + 0.4, dpt + 0.4, 1.2), loc=(xc, yc, 0.6), bevel=0.12, segments=1))
        stone.append(ns.box((w + 0.16, dpt + 0.16, 0.45), loc=(xc, yc, BZ0 - 0.1), bevel=0.06, segments=1))
        stone.append(ns.box((w + 0.16, dpt + 0.16, 0.45), loc=(xc, yc, 14.2), bevel=0.06, segments=1))
        stone.append(ns.box((w + 0.5, dpt + 0.5, 0.55), loc=(xc, yc, P_TOP + 0.27), bevel=0.12, segments=1))
        stone.append(ns.box((w - 0.4, dpt - 0.4, 0.3), loc=(xc, yc, P_TOP + 0.69), bevel=0.08, segments=1))
    C.part(brick, "Pillars", C.BRICK, "Brick", can_collide=True, smooth_angle=40)

    # globe lamps on the pillar caps
    lamp_base, globes = [], []
    for s in (-1, 1):
        xc = s * (PX0 + PX1) / 2
        yc = (PY0 + PY1) / 2
        lamp_base.append(ns.cyl(0.62, 0.36, loc=(xc, yc, P_TOP + 1.02), verts=10, bevel=0.06, segments=1))
        lamp_base.append(ns.cyl(0.42, 0.25, loc=(xc, yc, P_TOP + 1.3), verts=10, bevel=0.0))
        globes.append((xc, yc, P_TOP + 2.15))
    g = C.spheres(globes, 0.82, segs=10, rings=6)
    ns.tag(g, "Globes", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=80)

    # ----- cabinet ------------------------------------------------------------------------
    outline = C.rrect(2 * BX, BZ1 - BZ0, 0.6, 3, 0, (BZ0 + BZ1) / 2)
    body = C.prism(outline, "y", BODY_Y[0], BODY_Y[1])
    ns.bevel(body, width=0.08, segments=1)
    C.part([body], "Cabinet", C.NAVY, can_collide=True, smooth_angle=40)
    ix0, ix1, iz0, iz1 = -BX + FRAME_W, BX - FRAME_W, BZ0 + FRAME_W, BZ1 - FRAME_W
    inner = C.rrect(ix1 - ix0, iz1 - iz0, 0.3, 3, 0, (iz0 + iz1) / 2)
    panel = C.prism(inner, "y", PANEL_Y, BODY_Y[0] + 0.02)
    C.part([panel], "Panel", C.NAVY_DEEP, smooth_angle=40)
    frame = C.ring_slab(outline, inner, "y", FRAME_Y[0], FRAME_Y[1])
    ns.bevel(frame, width=0.06, segments=1)
    C.part([frame], "Frame", C.BRAND, smooth_angle=40)
    neon_path = C.rect_path(-BX + 0.35, BX - 0.35, BZ0 + 0.35, BZ1 - 0.35, FRAME_Y[0] - 0.07, r=0.45, segs=3)
    neon = C.pipe(neon_path, 0.1, sides=4, closed=True)
    ns.tag(neon, "FrameNeon", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    # back: red-orange belt + mustard pinstripe
    belt = [ns.box((2 * BX - 1.2, 0.05, 0.8), loc=(0, BODY_Y[1] + 0.02, BZ1 - 1.9), bevel=0.0)]
    pin = [ns.box((2 * BX - 1.2, 0.05, 0.16), loc=(0, BODY_Y[1] + 0.02, BZ1 - 2.6), bevel=0.0)]

    # ----- screens + bezels -----------------------------------------------------------------
    chrome = []
    specs = [("Card%d" % (i + 1), x, CARD_Z, CARD_W, CARD_H) for i, x in enumerate(CARD_X)]
    specs.append(("Ticker", 0.0, TICK_Z, TICK_W, TICK_H))
    for name, x, z, w, h in specs:
        scr = C.prism(C.rrect(w, h, 0.12, 1, x, z), "y", SCR_Y, PANEL_Y + 0.04)
        ns.tag(scr, name, C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
        chrome.append(C.ring_slab(C.rrect(w + 2 * BEZ, h + 2 * BEZ, 0.3, 1, x, z), C.rrect(w, h, 0.12, 1, x, z), "y",
                                  SCR_Y - 0.08, PANEL_Y + 0.03))

    # clock (left of the ticker) and reward star (right)
    cxk = -(TICK_W / 2 + BEZ + (BX - FRAME_W - TICK_W / 2 - BEZ) / 2)
    face = C.prism(C.circle_pts(1.42, 20, cxk, TICK_Z), "y", PANEL_Y - 0.18, PANEL_Y + 0.02)
    rim = C.ring_slab(C.circle_pts(1.78, 20, cxk, TICK_Z), C.circle_pts(1.42, 20, cxk, TICK_Z), "y", PANEL_Y - 0.3,
                      PANEL_Y + 0.02)
    # hands at 2:38 (angles clockwise from 12 as seen from the front; rot about +Y maps up -> (sin, cos))
    hands = []
    for ang, ln, wd, y in ((79.0, 0.82, 0.22, PANEL_Y - 0.2), (228.0, 1.15, 0.16, PANEL_Y - 0.235)):
        a = math.radians(ang)
        hands.append(ns.box((wd, 0.06, ln), loc=(cxk + 0.5 * ln * math.sin(a), y, TICK_Z + 0.5 * ln * math.cos(a)),
                            rot=(0, ang, 0), bevel=0.0))
    ticks = []
    for k in range(4):
        a = math.radians(90 * k)
        ticks.append(ns.box((0.16, 0.05, 0.3), loc=(cxk + 1.12 * math.sin(a), PANEL_Y - 0.2, TICK_Z + 1.12 * math.cos(a)),
                            rot=(0, 90 * k, 0), bevel=0.0))
    cap = ns.cyl(0.2, 0.14, loc=(cxk, PANEL_Y - 0.28, TICK_Z), rot=(90, 0, 0), verts=8, bevel=0.0)
    star_x = -cxk
    star_face = C.prism(C.star_pts(1.7, 0.78, star_x, TICK_Z - 0.06), "y", PANEL_Y - 0.4, PANEL_Y - 0.16)
    ns.bevel(star_face, width=0.06, segments=1)
    star_back = C.prism(C.star_pts(2.05, 0.98, star_x, TICK_Z - 0.06), "y", PANEL_Y - 0.17, PANEL_Y + 0.02)

    # ----- giant letters + their steel frame ------------------------------------------------
    faces, bodies, bulb_pts = letters()
    C.part(faces, "LetterFaces", C.MUSTARD, smooth_angle=30)
    C.part(bodies, "LetterBodies", C.BRAND, smooth_angle=30)
    bulbs = C.domes(bulb_pts, BULB_R, axis=(0, -1, 0), segs=6, rings=2)
    ns.tag(bulbs, "Bulbs", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=80)

    # DAILY stands on a raceway along its base, carried by two posts that hide behind the stems of
    # QUESTS' T / DAILY's Y (x 10.4) and QUESTS' Q / DAILY's D (x -12.9); QUESTS sits on the cabinet.
    steel = []
    ry = (L_BODY_Y[1] - 0.05, L_BODY_Y[1] + 0.55)
    # raceway ends hidden behind the D's stem (left) and the Y's stem (right; only the stem reaches the base)
    rx0, rx1 = -13.4, 11.2
    steel.append(ns.box((rx1 - rx0, ry[1] - ry[0], 0.62), loc=((rx0 + rx1) / 2, sum(ry) / 2, D_BASE - 0.08), bevel=0.06,
                        segments=1))
    for x in POSTS:
        steel.append(ns.box((0.62, 0.62, D_BASE + 0.25 - BZ1), loc=(x, ry[1] + 0.31, (BZ1 + D_BASE + 0.25) / 2),
                            bevel=0.06, segments=1))
        steel.append(ns.box((1.1, 1.1, 0.14), loc=(x, ry[1] + 0.31, BZ1 + 0.07), bevel=0.0))
        steel.append(C.rod((x, ry[1] + 0.31, BZ1 + 3.4), (x, BODY_Y[1] - 0.12, BZ1 + 0.1), 0.14, verts=6))

    # ----- flood lamps ----------------------------------------------------------------------
    housings, lenses, lens_pts = [], [], []
    for x in LAMP_X:
        st, ho, le, lc = flood_lamp(x)
        steel += st
        housings += ho
        lenses += le
        lens_pts.append(lc)
    C.part(housings, "FloodHousings", C.CHARCOAL, "Metal", smooth_angle=40)
    ns.tag(C.merge(lenses, "FloodLenses"), "FloodLenses", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False,
           smooth_angle=40)

    # ----- logo badges on the pillars ----------------------------------------------------------
    badges = {}
    for s in (-1, 1):
        C.merge_into(badges, C.badge((s * (PX0 + PX1) / 2, PY0 + 0.001, 9.4), r=1.25, n=16))
    # big badge on the cabinet back (the landmark stands mid-plaza: the back is seen too)
    C.merge_into(badges, C.badge((0.0, BODY_Y[1] - 0.001, (BZ0 + BZ1) / 2 - 0.9), r=3.0, yaw=180.0, depth=0.2, n=20))

    C.part(steel, "Steel", C.STEEL, "Metal", smooth_angle=50)
    C.part(stone, "Stone", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(lamp_base + hands + ticks, "Dark", C.NAVY_DEEP, smooth_angle=40)
    C.part(chrome, "Bezels", C.CHROME, "Metal", smooth_angle=40)
    C.part([face], "ClockFace", C.CREAM, smooth_angle=30)
    C.part([rim, star_back] + belt + badges.pop(C.BRAND), "BrandTrim", C.BRAND, smooth_angle=40)
    C.part([star_face, cap] + pin + badges.pop(C.CHEESE, []), "MustardTrim", C.MUSTARD, smooth_angle=40)
    C.add_parts(badges, "Badge", smooth_angle=40)
    return {"lens_pts": lens_pts}


def sockets():
    s = {"Ticker": ((0.0, SCR_Y, TICK_Z), 0.0), "Prompt": ((0.0, FRAME_Y[0] - 4.0, 3.0), 0.0)}
    for i, x in enumerate(CARD_X):
        s[f"Card{i + 1}"] = ((x, SCR_Y, CARD_Z), 0.0)
    for i, x in enumerate(LAMP_X):
        p = Vector(LAMP_ARM_END) + Vector((x, 0, 0)) + Vector(LAMP_HEAD_OFF)
        d = (AIM - p).normalized()
        s[f"Lamp{i + 1}"] = (tuple(p + d * 0.65), 180.0)
    return s


META = {
    "screens": {"Ticker": [TICK_W, TICK_H], "Card1": [CARD_W, CARD_H], "Card2": [CARD_W, CARD_H],
                "Card3": [CARD_W, CARD_H]},
    "surfaces": [C.screen_meta("Ticker", TICK_W, TICK_H)] +
                [C.screen_meta(f"Card{i + 1}", CARD_W, CARD_H) for i in range(3)],
    "card_order": "Card1 left, Card2 centre, Card3 right (as seen from the front)",
    "ticker_text": "RESETS IN 2h 38m",
    "board_bottom": BZ0,
    "lettering": "DAILY over QUESTS, cap height 5.7 (6.5 with outline), marquee bulbs on the strokes",
    "roles": {"screen": "Ticker, Card1, Card2, Card3", "lamp": "Bulbs (letter marquee), FloodLenses, Globes",
              "neon": "FrameNeon (cyan inlay round the board frame)"},
    "light_hint": {"type": "SpotLight", "at": "Socket_Lamp1/Lamp2", "aim": "Socket_Card2", "color": C.LAMP_WARM,
                   "range": 26, "angle": 75, "brightness": 2,
                   "letters": "optional PointLight ~3 in front of each line, warm, range 16"},
}

if __name__ == "__main__":
    C.run(build, "Lobby_QuestBoard", sockets=sockets(), meta=META, budget=9000, far=True)
