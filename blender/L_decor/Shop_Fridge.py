"""Shop_Fridge — 1950s two-door fridge in the Break Room, covered in magnets and notes.

Warm cream body with the classic big rounded top-front edge and soft side bevels, a dark
recessed kick plate with a chrome grille, two proud door panels (freezer on top) with
chrome lever handles on the right and a chrome badge. The fridge door is covered in
paper notes (a shift reminder, sticky notes, a takeout menu, a photo, a kid's drawing),
held by bright round magnets. Collides. Front faces -Y, pivot = bottom-centre.
2.8 x 6.0 x 2.6.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 2.8, 6.0, 2.5
KICK = 0.32
BODY = "#F0E3C4"
FY = -D / 2
FREEZER = (4.32, 5.36)          # freezer door z0, z1
FRIDGE = (KICK + 0.12, 4.2)     # fridge door z0, z1
DOOR_X = (-W / 2 + 0.1, W / 2 - 0.1)
MAG_COLS = {"MagRed": "#E0453A", "MagBlue": "#3D7BD0", "MagYellow": "#F2C230", "MagGreen": "#45A85A",
            "MagPink": "#F07AB0"}


def build():
    prof = C.fillet([(FY, KICK), (D / 2, KICK), (D / 2, H), (FY, H)], [0, 0, 0.25, 0.62], 3)
    body = C.prism(prof, "x", -W / 2, W / 2)
    ns.bevel(body, width=0.1, segments=2, angle=50)
    C.part([body], "Body", BODY, can_collide=True, smooth_angle=40)
    kick = ns.box((W - 0.2, D - 0.2, KICK + 0.02), loc=(0, 0.06, (KICK + 0.02) / 2), bevel=0.0)
    C.part([kick], "Kick", C.BASE_DARK, can_collide=True, smooth_angle=30)

    # door panels (proud of the front), freezer + fridge
    doors = []
    for z0, z1 in (FREEZER, FRIDGE):
        pts = C.rrect(DOOR_X[1] - DOOR_X[0], z1 - z0, 0.14, 2, 0, (z0 + z1) / 2)
        d = C.prism(pts, "y", FY - 0.07, FY + 0.02)
        ns.bevel(d, width=0.03, segments=1, angle=50)
        doors.append(d)
    C.part(doors, "Doors", BODY, can_collide=True, smooth_angle=40)
    dy = FY - 0.07                 # door front plane

    # chrome: lever handles (right side), badge, kick grille
    hx = DOOR_X[1] - 0.32
    chrome = [C.pipe([(hx, dy, FRIDGE[1] - 0.35), (hx, dy - 0.16, FRIDGE[1] - 0.45), (hx, dy - 0.16, FRIDGE[1] - 1.55),
                      (hx, dy, FRIDGE[1] - 1.65)], 0.055, sides=6),
              C.pipe([(hx, dy, FREEZER[0] + 0.2), (hx, dy - 0.14, FREEZER[0] + 0.28), (hx, dy - 0.14, FREEZER[0] + 0.8),
                      (hx, dy, FREEZER[0] + 0.88)], 0.05, sides=6)]
    badge_pts = C.rrect(0.8, 0.22, 0.1, 2, -0.45, FREEZER[0] + 0.62)
    chrome.append(C.prism(badge_pts, "y", dy - 0.03, dy + 0.005))
    for k in range(3):
        chrome.append(ns.box((W - 0.6, 0.04, 0.035), loc=(0, FY + 0.06, 0.08 + k * 0.08), bevel=0.0))
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    badge_txt = C.quad_xz(-0.75, -0.15, FREEZER[0] + 0.585, FREEZER[0] + 0.655, dy - 0.04)
    C.part([badge_txt], "BadgeScript", "#B83D22", smooth_angle=None)

    # notes on the fridge door (quads on y layers) + scribbles
    y1, y2, y3 = dy - 0.006, dy - 0.014, dy - 0.022
    papers, ink, colour_paper, mags = [], [], {}, {k: [] for k in MAG_COLS}

    def note(x, z, w, h, ang, col=C.PAPER, lines=3, layer=y1):
        q = [C.quad_xz(x - w / 2, x + w / 2, z - h / 2, z + h / 2, layer)]
        sc = [C.quad_xz(x - w * 0.36, x + w * (0.36 - 0.12 * (k % 2)), z + h * 0.25 - k * h * 0.2,
                        z + h * 0.25 - k * h * 0.2 + 0.035, layer - 0.006) for k in range(lines)]
        C.turn_y(q + sc, ang, x, z)
        if col == C.PAPER:
            papers.extend(q)
        else:
            colour_paper.setdefault(col, []).extend(q)
        ink.extend(sc)

    def magnet(x, z, col):
        mags[col].append(ns.cyl(0.075, 0.06, loc=(x, dy - 0.05, z), rot=(90, 0, 0), verts=6, bevel=0.0))

    note(-0.55, 3.45, 0.8, 0.95, 4)                       # shift reminder
    magnet(-0.55, 3.86, "MagRed")
    note(0.25, 3.62, 0.5, 0.5, -6, C.STICKY, 2, y2)       # sticky
    magnet(0.25, 3.82, "MagBlue")
    note(-0.25, 2.55, 0.62, 0.9, -3, "#C9432F", 0)        # takeout menu (red) ...
    note(-0.25, 2.5, 0.48, 0.42, -3, C.PAPER, 2, y2)      # ... with its white panel
    magnet(-0.25, 2.95, "MagYellow")
    note(0.5, 2.7, 0.62, 0.52, 7, C.PAPER, 0)             # photo frame
    pic = [C.quad_xz(0.27, 0.73, 2.58, 2.86, y2)]
    C.turn_y(pic, 7, 0.5, 2.7)
    magnet(0.5, 2.95, "MagGreen")
    note(-0.75, 1.6, 0.6, 0.66, 5, "#F7F2FF", 0)          # kid's drawing (sun + house)
    sun = ns.cyl(0.09, 0.01, loc=(-0.6, y2, 1.78), rot=(90, 0, 0), verts=8, bevel=0.0)
    house = C.face_dir(C.poly([(-0.95, y2, 1.38), (-0.68, y2, 1.38), (-0.68, y2, 1.56), (-0.815, y2, 1.7),
                               (-0.95, y2, 1.56)]), "-Y")
    C.turn_y([sun, house], 5, -0.75, 1.6)
    magnet(-0.75, 1.9, "MagPink")
    note(0.35, 1.75, 0.44, 0.44, -8, "#9FD8F0", 2, y1)    # blue sticky
    magnet(0.35, 1.92, "MagRed")
    note(0.32, 4.78, 0.46, 0.4, 5, C.STICKY, 2, y1)       # freezer sticky (badge stays clear)
    magnet(0.32, 4.95, "MagGreen")
    # loose round magnets + letter magnets (N, S, H)
    # loose magnets
    for x, z, col in ((0.75, 3.95, "MagYellow"), (0.82, 1.15, "MagBlue"), (-0.05, 1.18, "MagYellow"),
                      (-0.45, 1.0, "MagRed"), (0.25, 0.92, "MagGreen"), (0.68, 4.42, "MagPink"), (-0.95, 2.95, "MagBlue")):
        magnet(x, z, col)

    C.part(papers, "Papers", C.PAPER, smooth_angle=None)
    for i, (col, objs) in enumerate(colour_paper.items()):
        C.part(objs, f"Paper{i}", col, smooth_angle=None)
    C.part(ink + pic, "Ink", C.INK, smooth_angle=None)
    C.part([sun], "DrawSun", "#F2B33D", smooth_angle=None)
    C.part([house], "DrawHouse", "#D9472F", smooth_angle=None)
    for k, objs in mags.items():
        if objs:
            C.part(objs, k, MAG_COLS[k], smooth_angle=40)


META = {"collide": "body, kick plate and door panels collide"}

if __name__ == "__main__":
    C.run(build, "Shop_Fridge", budget=1000, meta=META)
