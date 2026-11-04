"""Lobby_ArcadeCabinet — retro upright arcade cabinet "STACK ATTACK" (2.4 x 6 x 2.6).

Classic upright silhouette: navy side panels (stepped profile: marquee overhang, recessed screen,
jutting control panel) with STACKHOUSE stacked-sandwich side art and hot-pink neon T-molding
along their edges (SideNeon, role "neon"); a backlit marquee (MarqueeLight, Neon, role "lamp")
with chunky red-orange STACK / ATTACK letters outlined in navy (geometry); a dark screen
(Screen, role "screen", vertical, front face) in a black bezel; a red-orange control panel with a
joystick and four buttons; a chrome coin door with two lit coin slots; a black kick plate.
Cabinet collides.

Front = -Y, pivot = bottom-centre.
Sockets: Screen (screen face centre, yaw 0), Prompt (in front of the control panel),
Light (in front of the screen, for the screen-glow PointLight).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns

HW = 1.16                    # half width (outer face of the side panels)
SIDE_T = 0.14
IN = HW - SIDE_T             # inner half width
SCR_W, SCR_H = 1.62, 1.2
SCR_Z = 4.08
SCR_Y = -0.52                # screen face
MARQ = (4.98, 5.86)          # marquee front z range
MARQ_Y = -1.0
PANEL_FRONT = (-1.26, 2.9, 3.1)      # control panel lip y, z0, z1
PANEL_BACK = (-0.84, 3.3)            # top surface rises to here
BACKLIGHT = "#FFE6B0"


def side_profile():
    """(y, z) outline of a side panel (front = -y)."""
    return [(-0.76, 0.0), (-0.76, 2.55), (-1.3, 2.86), (-1.3, 3.14), (-0.86, 3.34), (-0.56, 4.86), (-1.05, 4.96),
            (-1.05, 5.88), (-0.92, 6.0), (1.3, 6.0), (1.3, 0.0)]


def body_profile():
    """(y, z) outline of the cabinet between the side panels (slightly inset at the front)."""
    return [(-0.72, 0.22), (-0.72, 2.55), (PANEL_FRONT[0], 2.88), (PANEL_FRONT[0], PANEL_FRONT[2]), PANEL_BACK,
            (SCR_Y + 0.04, PANEL_BACK[1]), (SCR_Y + 0.04, 4.86), (MARQ_Y, 4.97), (MARQ_Y, 5.87), (-0.9, 5.97),
            (1.26, 5.97), (1.26, 0.22)]


def build():
    sp = C.fillet(side_profile(), [0, 0.06, 0.1, 0.06, 0.06, 0.06, 0.06, 0.05, 0.12, 0.08, 0], 1)
    sides = []
    for s in (-1, 1):
        a0, a1 = sorted((s * IN, s * HW))
        o = C.prism(sp, "x", a0, a1)
        ns.bevel(o, width=0.04, segments=1)
        sides.append(o)
    body = C.prism(body_profile(), "x", -IN - 0.01, IN + 0.01)
    kick = ns.box((2 * IN, 0.06, 0.22), loc=(0, -0.73, 0.11), bevel=0.0)

    # neon T-molding: just inside the front, top and back edges of each side panel, on its outer face
    ring = C.inset_poly(side_profile(), 0.09)
    k_fb = 0                                       # inset of the front-bottom corner
    k_bb = len(ring) - 1                           # inset of the back-bottom corner
    path2 = [(ring[k_fb][0], 0.14)] + ring[k_fb + 1:k_bb] + [(ring[k_bb][0], 0.14)]
    path2 = C.round_path([(0.0, y, z) for y, z in path2], 0.07, segs=1)
    tubes = []
    for s in (-1, 1):
        x = s * (HW + 0.0)
        tubes.append(C.pipe([(x, y, z) for _, y, z in path2], 0.045, sides=4))

    # side art: big STACKHOUSE sandwich stack on each side panel
    art = {}
    for s in (-1, 1):
        icon = C.sandwich_icon(s=0.62, depth=0.05)
        C.place(icon, (s * (HW + 0.002), 0.35, 2.1), yaw=90 if s > 0 else -90)
        C.merge_into(art, icon)
        plate = C.prism(C.circle_pts(0.95, 14, 0.35, 2.15), "x", *sorted((s * (HW - 0.01), s * (HW + 0.025))))
        art.setdefault(C.BRAND_DARK, []).append(plate)
        for objs in list(icon.values()) + [[plate]]:   # drop the caps that face into the panel (never seen)
            for o in objs:
                C.drop_faces(o, lambda c, n, s=s: n.x * s < -0.9)

    # marquee: backlit panel + outlined letters
    panel = C.prism(C.rrect(2 * IN - 0.14, MARQ[1] - MARQ[0] - 0.12, 0.05, 1, 0, (MARQ[0] + MARQ[1]) / 2), "y",
                    MARQ_Y - 0.02, MARQ_Y + 0.01)
    frame = C.ring_slab(C.rrect(2 * IN + 0.02, MARQ[1] - MARQ[0] + 0.04, 0.06, 1, 0, (MARQ[0] + MARQ[1]) / 2),
                        C.rrect(2 * IN - 0.14, MARQ[1] - MARQ[0] - 0.12, 0.05, 1, 0, (MARQ[0] + MARQ[1]) / 2), "y",
                        MARQ_Y - 0.06, MARQ_Y + 0.02)
    letters, outlines = [], []
    for txt, width, base in (("STACK", 1.5, 5.43), ("ATTACK", 1.86, 5.07)):
        w = C.Word(txt, 0.0, cap=0.3, spacing=1.06, base=base, res=1, xscale=1.08)
        w.fit_width(width)
        letters.append(w.solid(MARQ_Y - 0.075, 0.03, front_only=True, name="Let" + txt))
        outlines.append(w.solid(MARQ_Y - 0.05, 0.03, offset=0.045, front_only=True, name="Out" + txt))

    # screen + bezel
    bezel = C.ring_slab(C.rrect(2 * IN - 0.02, 1.52, 0.08, 2, 0, SCR_Z), C.rrect(SCR_W, SCR_H, 0.12, 2, 0, SCR_Z), "y",
                        SCR_Y - 0.03, SCR_Y + 0.05)
    screen = C.prism(C.rrect(SCR_W, SCR_H, 0.12, 2, 0, SCR_Z), "y", SCR_Y, SCR_Y + 0.04)

    # control panel top + lip (red-orange), joystick and buttons on the slope
    (fy, z0, z1), (by, bz) = PANEL_FRONT, PANEL_BACK
    ctl = C.prism([(fy - 0.02, z0 - 0.01), (fy - 0.02, z1 + 0.01), (by + 0.02, bz + 0.012), (by + 0.02, bz - 0.06),
                   (-0.72, 2.56)], "x", -IN, IN)
    slope = math.atan2(bz - z1, by - fy)

    def on_panel(x, t, lift=0.0):
        y = fy + (by - fy) * t
        z = z1 + (bz - z1) * t
        n = Vector((0, -math.sin(slope), math.cos(slope)))
        return Vector((x, y, z)) + n * lift, n

    tilt = Matrix.Rotation(-slope, 4, "X")
    knobs, buttons = [], {C.CYAN: [], C.PINK: [], C.MUSTARD: [], C.CREAM: []}
    p, n = on_panel(-0.5, 0.62)
    knobs.append(C.rod(p, p + n * 0.38, 0.035, verts=5))
    ball = ns.sphere(0.12, loc=tuple(p + n * 0.42), segs=7, rings=4)
    plate = ns.cyl(0.13, 0.03, verts=8, bevel=0.0)
    ns.apply_all(plate)
    plate.data.transform(Matrix.Translation(p + n * 0.012) @ tilt)
    knobs.append(plate)
    for (x, t), col in zip(((0.08, 0.62), (0.4, 0.66), (0.72, 0.62), (0.4, 0.3)), (C.CYAN, C.PINK, C.MUSTARD, C.CREAM)):
        p, n = on_panel(x, t)
        b = ns.cyl(0.1, 0.07, verts=7, bevel=0.0)
        ns.apply_all(b)
        b.data.transform(Matrix.Translation(p + n * 0.03) @ tilt)
        buttons[col].append(b)

    # coin door + lit slots
    door = C.prism(C.rrect(0.86, 0.95, 0.06, 1, 0, 1.55), "y", -0.75, -0.71)
    slots, rets = [], []
    for x in (-0.2, 0.2):
        slots.append(C.prism(C.rrect(0.13, 0.26, 0.03, 1, x, 1.78), "y", -0.765, -0.745))
        rets.append(C.prism(C.rrect(0.22, 0.12, 0.03, 1, x, 1.32), "y", -0.765, -0.745))

    C.part(sides, "SidePanels", C.NAVY, can_collide=True, smooth_angle=40)
    C.part([body], "Cabinet", C.NAVY_DEEP, can_collide=True, smooth_angle=30)
    C.part([ctl], "ControlPanel", C.BRAND, smooth_angle=30)
    C.part([kick, bezel] + knobs + outlines, "Black", C.BLACK, smooth_angle=40)
    C.part([ball], "Joystick", C.KETCHUP, smooth_angle=60)
    for col, nm in ((C.CYAN, "ButtonCyan"), (C.PINK, "ButtonPink"), (C.MUSTARD, "ButtonGold"), (C.CREAM, "ButtonCream")):
        C.part(buttons[col], nm, col, smooth_angle=40)
    C.part([door, frame] + rets, "Chrome", C.CHROME, "Metal", smooth_angle=40)
    C.part(letters, "Letters", C.BRAND, smooth_angle=None)
    names = {C.BUN: "ArtBun", C.LETTUCE: "ArtLettuce", C.TOMATO: "ArtTomato", C.CHEESE: "ArtCheese", C.BRAND_DARK: "ArtDisc"}
    for col, objs in art.items():
        C.part(objs, names[col], col, smooth_angle=None)
    ns.tag(C.merge(tubes, "SideNeon"), "SideNeon", C.PINK, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    ns.tag(C.merge([panel] + slots, "MarqueeLight"), "MarqueeLight", BACKLIGHT, "Neon", recolor="lamp", cast_shadow=False,
           smooth_angle=30)
    ns.tag(screen, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
    return {}


SOCKETS = {"Screen": ((0.0, SCR_Y, SCR_Z), 0.0), "Prompt": ((0.0, -2.1, 3.0), 0.0), "Light": ((0.0, -1.5, SCR_Z), 0.0)}
META = {"screen_size": [SCR_W, SCR_H], "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
        "game": "STACK ATTACK (marquee modelled; the game draws the screen)",
        "roles": {"screen": "Screen", "neon": "SideNeon (pink T-molding, both side panels)",
                  "lamp": "MarqueeLight (backlit marquee panel + coin slots)"},
        "light_hint": {"type": "PointLight", "at": "Socket_Light", "color": C.CYAN, "range": 8, "brightness": 0.8}}

if __name__ == "__main__":
    C.run(build, "Lobby_ArcadeCabinet", sockets=SOCKETS, meta=META, budget=2000, pivot=(0.0, 0.0, 0.0), far=True,
          far_kw={"dist": 14.0})
