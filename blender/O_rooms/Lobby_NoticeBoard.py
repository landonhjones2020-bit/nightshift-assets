"""Lobby_NoticeBoard — locker-room staff notice board (6 W x 4 H x 0.3 D), wall-mounted.

A maple frame around a recessed cork panel. Across the top a red-orange header plate with cream
"STAFF NOTICES" letters and chrome screws. In the middle a large blank white sheet pinned at its
corners (Screen, role "screen", Front face) where the game draws the SHIFT ROSTER SurfaceGui.
Around it, pinned flyers with printed headers and lines (a mustard "party" flyer with a
starburst, a slate-blue memo), sticky notes, a polaroid and coloured push pins.

Wall-mounted: modelled with its back face on the wall plane (Blender y = 0), front -Y; pivot =
bottom-centre of the back face. Socket Screen = centre of the roster sheet's face (yaw 0).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 6.0, 4.0, 0.3
FR = 0.22                    # frame width
CORK_Y = -0.12               # cork surface
SCR_W, SCR_H = 2.9, 2.45
SCR_Z = 1.66                 # sheet centre
SCR_Y = CORK_Y - 0.02        # sheet front face
HDR_W, HDR_H, HDR_Z = 2.9, 0.44, 3.4
STICKY = "#F4D85A"
PINK_NOTE = "#F49AC1"
PIN_COLS = {"PinsRed": "#D63A3A", "PinsBlue": "#3C6FB0", "PinsYellow": "#F2C94C"}


def build():
    zc = H / 2
    frame = C.ring_slab([(-W / 2, 0.0), (W / 2, 0.0), (W / 2, H), (-W / 2, H)],
                        [(-W / 2 + FR, FR), (W / 2 - FR, FR), (W / 2 - FR, H - FR), (-W / 2 + FR, H - FR)], "y", -T, 0.0)
    ns.bevel(frame, width=0.05, segments=1, angle=50)
    C.part([frame], "Frame", C.MAPLE, "Wood", smooth_angle=35)
    cork = ns.box((W - 2 * FR + 0.04, 0.06, H - 2 * FR + 0.04), loc=(0, CORK_Y + 0.03, zc), bevel=0.0)
    C.part([cork], "Cork", C.CORK, "Fabric", smooth_angle=None)

    # header plate + letters + screws
    plate = C.prism(C.rrect(HDR_W, HDR_H, 0.08, 2, 0, HDR_Z), "y", CORK_Y - 0.06, CORK_Y + 0.01)
    C.part([plate], "Header", C.BRAND, smooth_angle=40)
    letters = C.text("STAFF NOTICES", 0.26, 0.03, (0, CORK_Y - 0.075, HDR_Z), width=HDR_W - 0.6, res=1, spacing=1.05,
                     flat=True)
    C.part([letters], "HeaderText", C.CREAM, smooth_angle=None)
    pins = {k: [] for k in PIN_COLS}
    chrome = []
    for sx in (-1, 1):
        s_ = ns.cyl(0.06, 0.03, verts=6, bevel=0.0)
        C.place(s_, (sx * (HDR_W / 2 - 0.16), CORK_Y - 0.07, HDR_Z), pitch=90)
        chrome.append(s_)

    def pin(x, z, col, y=CORK_Y - 0.04):
        p = ns.cyl(0.06, 0.07, verts=6, bevel=0.0)
        C.place(p, (x, y - 0.035, z), pitch=90)
        pins[col].append(p)

    # roster sheet (the screen) + corner pins
    scr = ns.box((SCR_W, 0.02, SCR_H), loc=(0, SCR_Y + 0.01, SCR_Z), bevel=0.0)
    ns.tag(scr, "Screen", "#FBF9F3", recolor="screen", cast_shadow=False, smooth_angle=None)
    for sx in (-1, 1):
        for sz in (-1, 1):
            pin(sx * (SCR_W / 2 - 0.12), SCR_Z + sz * (SCR_H / 2 - 0.12), "PinsRed" if sz > 0 else "PinsBlue", y=SCR_Y)

    y1, y2, y3 = CORK_Y - 0.012, CORK_Y - 0.024, CORK_Y - 0.036     # paper layers
    paper, ink, groups = [], [], {}

    # left: mustard party flyer with a starburst + printed lines (tilted)
    fx0, fx1, fz0, fz1 = -2.62, -1.62, 1.75, 3.0
    fl = [C.quad_xz(fx0, fx1, fz0, fz1, y1)]
    hd = [C.quad_xz(fx0 + 0.06, fx1 - 0.06, fz1 - 0.34, fz1 - 0.06, y2)]
    burst = [C.face_dir(C.flat_poly(C.star_pts(0.3, 0.17, (fx0 + fx1) / 2, fz0 + 0.62, n=10), y2), "-Y")]
    lines = [C.quad_xz(fx0 + 0.12, fx1 - 0.12 - 0.15 * k, fz0 + 0.24 - 0.09 * k, fz0 + 0.27 - 0.09 * k, y2) for k in range(2)]
    C.turn_y(fl + hd + burst + lines, 4.0, (fx0 + fx1) / 2, (fz0 + fz1) / 2)
    paper += fl
    C.add(groups, C.MUSTARD, hd)
    C.add(groups, C.BRAND, burst)
    ink += lines
    pin((fx0 + fx1) / 2 - 0.02, fz1 - 0.06, "PinsYellow")
    # left: sticky note + polaroid
    q = [C.quad_xz(-2.55, -2.0, 0.85, 1.4, y1)]
    sc = [C.strip_xz((-2.47, 1.24 - k * 0.12), (-2.1 - 0.06 * k, 1.25 - k * 0.12), 0.03, y2) for k in range(3)]
    C.turn_y(q + sc, -6.0, -2.27, 1.12)
    C.add(groups, STICKY, q)
    ink += sc
    pin(-2.27, 1.33, "PinsRed")
    ph = [C.quad_xz(-1.95, -1.6, 0.36, 0.84, y1)]
    pic = [C.quad_xz(-1.91, -1.64, 0.5, 0.8, y2)]
    C.turn_y(ph + pic, 7.0, -1.78, 0.6)
    paper += ph
    C.add(groups, C.SLATE, pic)
    pin(-1.78, 0.78, "PinsBlue")

    # right: slate-blue memo (header band + lines)
    mx0, mx1, mz0, mz1 = 1.62, 2.62, 1.55, 2.95
    memo = [C.quad_xz(mx0, mx1, mz0, mz1, y1)]
    mh = [C.quad_xz(mx0 + 0.06, mx1 - 0.06, mz1 - 0.3, mz1 - 0.06, y2)]
    ml = [C.quad_xz(mx0 + 0.12, mx1 - 0.12 - 0.12 * (k % 2), mz1 - 0.48 - 0.15 * k, mz1 - 0.45 - 0.15 * k, y2) for k in range(5)]
    C.turn_y(memo + mh + ml, -3.0, (mx0 + mx1) / 2, (mz0 + mz1) / 2)
    paper += memo
    C.add(groups, C.SLATE, mh)
    ink += ml
    pin((mx0 + mx1) / 2 + 0.03, mz1 - 0.06, "PinsBlue")
    # right: two sticky notes
    for (x, z, ang, col, pc) in ((2.1, 1.0, 5.0, PINK_NOTE, "PinsYellow"), (1.82, 0.5, -4.0, STICKY, "PinsRed")):
        q = [C.quad_xz(x - 0.26, x + 0.26, z - 0.26, z + 0.26, y1 if col == PINK_NOTE else y3)]
        sc = [C.strip_xz((x - 0.17, z + 0.06 - k * 0.12), (x + 0.12 - 0.08 * k, z + 0.07 - k * 0.12), 0.03,
                         (y2 if col == PINK_NOTE else y3 - 0.012)) for k in range(2)]
        C.turn_y(q + sc, ang, x, z)
        C.add(groups, col, q)
        ink += sc
        pin(x, z + 0.18, pc, y=(y1 if col == PINK_NOTE else y3))

    C.part(paper, "Papers", C.PAPER, smooth_angle=None)
    C.part(ink, "Ink", C.INK, smooth_angle=None)
    C.parts_by_colour(groups, "Prints", smooth_angle=None)
    C.part(chrome, "Screws", C.CHROME, "Metal", smooth_angle=40)
    for k, objs in pins.items():
        if objs:
            C.part(objs, k, PIN_COLS[k], smooth_angle=40)


SOCKETS = {"Screen": ((0, SCR_Y, SCR_Z), 0.0)}
META = {"mount": "wall", "pivot": "bottom-centre of the back face (on the wall plane)", "wall_back_z": 0.0,
        "screen_size": [SCR_W, SCR_H], "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
        "screen_hint": "white paper sheet: draw dark ink text (SHIFT ROSTER) on a transparent background",
        "roles": {"screen": "Screen (the roster sheet)"}}

if __name__ == "__main__":
    C.run(build, "Lobby_NoticeBoard", sockets=SOCKETS, mount="wall", budget=2000, pivot=(0, 0, 0), meta=META,
          backdrop="#7E8E9A")
