"""Lobby_NeonArrowSign — neon wayfinding arrow on a post (7 x 9 x 1.1 overall; sign box 7 x 2.4 x 0.5).

An arrow-shaped navy sign box (soft bevels, pointing to Blender +X = Roblox -X, i.e. to the right
as seen from the front) on a tapered navy post with a mustard collar, a saddle bracket and a
cast-stone footing. Both faces carry a cyan neon tube following the arrow outline (Neon, role
"neon"), a mustard chevron in the arrowhead and a dark label screen in the shaft (role "screen") for a SurfaceGui label such as
SHIFT VANS or SHOP - no text is baked in. Turn the model 180 deg for a left-pointing arrow: the
back face then faces the viewer and has its own screen. Post and footing collide.

Front = -Y, pivot = bottom-centre (the post base).
Sockets: Screen (front label face centre, yaw 0), ScreenBack (back label face centre, yaw 180),
Light (in front of the sign face, for a cyan PointLight).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

SZ = 7.76                    # sign centre height (box 6.56 .. 8.96 + bevel)
HALF_T = 0.25                # box half thickness
SHAFT_H = 1.56
NECK_X = 1.45                # where the arrowhead starts
POST_X = 0.0                 # post x (= pivot, the middle of the 7-wide sign)
SCR_W, SCR_H = 3.9, 0.98
SCR_X = -1.05                # label centre x (shaft centre, clear of the neon)


def outline():
    hs = SHAFT_H / 2
    return [(-3.5, SZ - hs), (NECK_X, SZ - hs), (NECK_X, SZ - 1.26), (3.66, SZ), (NECK_X, SZ + 1.26), (NECK_X, SZ + hs),
            (-3.5, SZ + hs)]


def build():
    pts = outline()
    radii = [0.3, 0.08, 0.14, 0.18, 0.14, 0.08, 0.3]
    box = C.prism(C.fillet(pts, radii, 3), "y", -HALF_T, HALF_T)
    ns.bevel(box, width=0.07, segments=2, angle=50)
    # neon outline tubes, both faces
    tube_pts = C.fillet(C.inset_poly(pts, 0.2), [0.18, 0.05, 0.08, 0.1, 0.08, 0.05, 0.18], 3)
    tubes = []
    for sy in (-1, 1):
        y = sy * (HALF_T + 0.05)
        tubes.append(C.pipe([(x, y, z) for x, z in tube_pts], 0.07, sides=6, closed=True))
    # mustard chevron in the arrowhead, both faces
    chev = []
    cx0 = NECK_X + 0.45
    shape = [(cx0, SZ + 0.62), (cx0 + 0.36, SZ + 0.62), (cx0 + 0.98, SZ), (cx0 + 0.36, SZ - 0.62), (cx0, SZ - 0.62),
             (cx0 + 0.62, SZ)]
    for sy in (-1, 1):
        a0, a1 = sorted((sy * (HALF_T - 0.01), sy * (HALF_T + 0.035)))
        chev.append(C.prism(C.fillet(shape, 0.04, 1), "y", a0, a1))
    # label screens (flush on each face) + chrome bezels
    screens, bezels = [], []
    for sy in (-1, 1):
        a0, a1 = sorted((sy * (HALF_T - 0.01), sy * (HALF_T + 0.03)))
        screens.append(C.prism(C.rrect(SCR_W, SCR_H, 0.1, 2, SCR_X, SZ), "y", a0, a1))
        b0, b1 = sorted((sy * (HALF_T - 0.01), sy * (HALF_T + 0.05)))
        bezels.append(C.ring_slab(C.rrect(SCR_W + 0.18, SCR_H + 0.18, 0.16, 2, SCR_X, SZ), C.rrect(SCR_W, SCR_H, 0.1, 2, SCR_X, SZ),
                                  "y", b0, b1))
    # post, collar, saddle bracket, footing
    post = C.rod((POST_X, 0, 0.45), (POST_X, 0, SZ - 1.2 + 0.05), 0.25, verts=10, r_top=0.19)
    collar = [ns.cyl(0.25, 0.18, loc=(POST_X, 0, 5.55), verts=10, bevel=0.0),
              ns.cyl(0.3, 0.2, loc=(POST_X, 0, 1.0), verts=10, bevel=0.0)]
    saddle = [ns.box((1.9, HALF_T * 2 + 0.18, 0.14), loc=(POST_X, 0, SZ - 1.2 - 0.05), bevel=0.05, segments=1),
              C.rod((POST_X, 0, SZ - 1.2 - 0.75), (POST_X - 0.8, 0, SZ - 1.2 - 0.1), 0.065, verts=6),
              C.rod((POST_X, 0, SZ - 1.2 - 0.75), (POST_X + 0.8, 0, SZ - 1.2 - 0.1), 0.065, verts=6)]
    flange = ns.lathe([(0.0, 0.28), (0.46, 0.28), (0.46, 0.34), (0.34, 0.48), (0.25, 0.64), (0.0, 0.64)], verts=10)
    flange.location.x = POST_X
    foot = C.prism(C.circle_pts(0.55, 12, POST_X, 0), "z", 0.0, 0.3)
    ns.bevel(foot, width=0.06, segments=1)
    bolts = [ns.cyl(0.05, 0.06, loc=(POST_X + 0.33 * math.cos(a), 0.33 * math.sin(a), 0.33), verts=6, bevel=0.0)
             for a in (math.radians(45 + 90 * k) for k in range(4))]

    C.part([box], "SignBox", C.NAVY, smooth_angle=40)
    C.part([post, flange], "Post", C.STEEL_NAVY, "Metal", can_collide=True, smooth_angle=50)
    C.part([foot], "Footing", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(saddle, "Bracket", C.STEEL_NAVY, "Metal", smooth_angle=45)
    C.part(collar, "Collars", C.MUSTARD, "Metal", smooth_angle=45)
    C.part(chev, "Chevrons", C.MUSTARD, smooth_angle=None)
    C.part(bezels + bolts, "Bezels", C.CHROME, "Metal", smooth_angle=45)
    ns.tag(C.merge(tubes, "Neon"), "Neon", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    ns.tag(screens[0], "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
    ns.tag(screens[1], "ScreenBack", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
    return {}


SOCKETS = {"Screen": ((SCR_X, -(HALF_T + 0.03), SZ), 0.0), "ScreenBack": ((SCR_X, HALF_T + 0.03, SZ), 180.0),
           "Light": ((0.0, -1.6, SZ), 0.0)}
META = {"screen_size": [SCR_W, SCR_H],
        "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H, "Front"), C.screen_meta("ScreenBack", SCR_W, SCR_H, "Back")],
        "points": "Roblox -X (right as seen from the front); yaw the model 180 deg to point the other way",
        "label": "no baked text: draw the label (e.g. SHIFT VANS, SHOP) with a SurfaceGui on Screen / ScreenBack",
        "roles": {"neon": "Neon (cyan outline, both faces)", "screen": "Screen, ScreenBack"},
        "light_hint": {"type": "PointLight", "at": "Socket_Light", "color": C.CYAN, "range": 12, "brightness": 1}}

if __name__ == "__main__":
    C.run(build, "Lobby_NeonArrowSign", sockets=SOCKETS, meta=META, budget=2000, pivot=(0.0, 0.0, 0.0), far=True,
          far_kw={"dist": 30.0})
