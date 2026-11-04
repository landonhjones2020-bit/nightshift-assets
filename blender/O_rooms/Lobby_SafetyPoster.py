"""Lobby_SafetyPoster — framed staff safety poster (3 W x 4 H x 0.1 D), wall-mounted.

A brushed-steel snap frame around a printed poster: a red-orange header band with cream
"SAFETY FIRST" letters, a big mustard caution triangle with a black border and "!", a blank
text panel (Screen, role "screen", Front face) where the game writes the safety rule, and a
mustard / black hazard stripe along the bottom.

Wall-mounted: back face on the wall plane (Blender y = 0), front -Y; pivot = bottom-centre of
the back face. Socket Screen = centre of the text panel's face (yaw 0).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 3.0, 4.0, 0.1
BORDER = 0.14
PAPER_Y = -0.055                 # poster face
SCR_W, SCR_H = 2.36, 1.42
SCR_Z = 1.06
SCR_Y = PAPER_Y - 0.008
HAZ = (0.17, 0.29)               # hazard stripe band z


def build():
    zc = H / 2
    frame = C.ring_slab(C.rrect(W, H, 0.12, 2, 0, zc), C.rrect(W - 2 * BORDER, H - 2 * BORDER, 0.04, 2, 0, zc), "y", -T, 0.0)
    ns.bevel(frame, width=0.025, segments=1, angle=50)
    C.part([frame], "Frame", C.STEEL, "Metal", smooth_angle=40)
    paper = ns.box((W - 2 * BORDER + 0.04, 0.02, H - 2 * BORDER + 0.04), loc=(0, PAPER_Y + 0.01, zc), bevel=0.0)
    C.part([paper], "Paper", C.PAPER, smooth_angle=None)

    x0, x1 = -W / 2 + BORDER, W / 2 - BORDER
    y1, y2, y3 = PAPER_Y - 0.008, PAPER_Y - 0.016, PAPER_Y - 0.024
    # header band + letters
    band = C.quad_xz(x0, x1, H - BORDER - 0.62, H - BORDER, y1)
    C.part([band], "HeaderBand", C.BRAND, smooth_angle=None)
    letters = C.text("SAFETY FIRST", 0.34, 0.01, (0, y2 + 0.005, H - BORDER - 0.31), width=2.3, res=1, spacing=1.04,
                     flat=True)
    C.part([letters], "HeaderText", C.CREAM, smooth_angle=None)
    # caution triangle: black border, mustard inside, black "!"
    tz, tr = 2.36, 0.78            # centre, circumradius
    import math
    outer = [(tr * 1.18 * math.cos(math.radians(90 + 120 * k)), tz + tr * 1.18 * math.sin(math.radians(90 + 120 * k)) - 0.06)
             for k in range(3)]
    inner = [(tr * 0.92 * math.cos(math.radians(90 + 120 * k)), tz + tr * 0.92 * math.sin(math.radians(90 + 120 * k)) - 0.06)
             for k in range(3)]
    black = [C.face_dir(C.flat_poly(C.fillet(outer, 0.08, 2), y1), "-Y")]
    yellow = [C.face_dir(C.flat_poly(C.fillet(inner, 0.05, 2), y2), "-Y")]
    black.append(C.face_dir(C.flat_poly([(-0.07, tz + 0.32), (0.07, tz + 0.32), (0.045, tz - 0.12), (-0.045, tz - 0.12)], y3), "-Y"))
    black.append(C.face_dir(C.flat_poly(C.circle_pts(0.075, 8, 0, tz - 0.27), y3), "-Y"))
    # hazard stripes along the bottom: black band with mustard diagonal bars
    hz0, hz1 = HAZ
    black.append(C.quad_xz(x0 + 0.06, x1 - 0.06, hz0, hz1, y1))
    for k in range(9):
        a = x0 + 0.1 + k * 0.29
        bar = C.clip_band([(a, hz0), (a + 0.14, hz0), (a + 0.26, hz1), (a + 0.12, hz1)], x0 + 0.06, x1 - 0.06)
        if len(bar) >= 3:
            yellow.append(C.face_dir(C.flat_poly(bar, y2), "-Y"))
    C.part(black, "Black", "#1A1A1D", smooth_angle=None)
    C.part(yellow, "Caution", C.MUSTARD, smooth_angle=None)
    # text panel (the screen)
    scr = ns.box((SCR_W, 0.012, SCR_H), loc=(0, SCR_Y + 0.006, SCR_Z), bevel=0.0)
    ns.tag(scr, "Screen", "#FBF9F3", recolor="screen", cast_shadow=False, smooth_angle=None)
    # thin ink rule framing the text panel
    rule = C.ring_slab(C.rrect(SCR_W + 0.08, SCR_H + 0.08, 0.04, 1, 0, SCR_Z), C.rrect(SCR_W + 0.03, SCR_H + 0.03, 0.02, 1, 0, SCR_Z),
                       "y", y2, y1 + 0.004)
    C.part([rule], "Rule", C.INK, smooth_angle=None)


SOCKETS = {"Screen": ((0, SCR_Y, SCR_Z), 0.0)}
META = {"mount": "wall", "pivot": "bottom-centre of the back face (on the wall plane)", "wall_back_z": 0.0,
        "screen_size": [SCR_W, SCR_H], "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
        "screen_hint": "white text panel: draw dark ink text on a transparent background",
        "roles": {"screen": "Screen (the poster's text panel)"}}

if __name__ == "__main__":
    C.run(build, "Lobby_SafetyPoster", sockets=SOCKETS, mount="wall", budget=2000, pivot=(0, 0, 0), meta=META,
          backdrop="#7E8E9A")
