"""Shop_CorkBoard — Break Room cork board.

Light wood frame around a recessed cork panel. Pinned on it: the weekly shift SCHEDULE
(red-orange header with white letters, a ruled grid with coloured shift marks), a
"SAFETY FIRST" flyer (green header, white letters, a green cross and printed lines), four
sticky notes with scribbles and a little photo, all held by coloured push pins.
Wall-mounted: pivot = bottom-centre of the back face (+Y, touches the wall). 4 x 3 x 0.2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 4.0, 3.0, 0.2
FR = 0.17                 # frame width
CORK_Y = -0.09            # cork surface (recessed into the frame)
GREEN = "#3E8A4F"
PIN_COLS = {"PinsRed": "#D63A3A", "PinsBlue": "#3C6FB0", "PinsYellow": "#F2C94C"}


def build():
    zc = H / 2
    outer = [(-W / 2, 0.0), (W / 2, 0.0), (W / 2, H), (-W / 2, H)]
    inner = [(-W / 2 + FR, FR), (W / 2 - FR, FR), (W / 2 - FR, H - FR), (-W / 2 + FR, H - FR)]
    frame = C.ring_slab(outer, inner, "y", -T, 0.0)
    ns.bevel(frame, width=0.03, segments=1, angle=50)
    C.part([frame], "Frame", C.WOOD_LIGHT, "Wood", smooth_angle=35)
    cork = ns.box((W - 2 * FR + 0.02, 0.04, H - 2 * FR + 0.02), loc=(0, CORK_Y + 0.02, zc), bevel=0.0)
    C.part([cork], "Cork", C.CORK, "Fabric", smooth_angle=None)

    y1, y2, y3 = CORK_Y - 0.01, CORK_Y - 0.02, CORK_Y - 0.03     # paper layers
    papers, ink, white, pins = [], [], [], {k: [] for k in PIN_COLS}
    brand, green, notes = [], [], {}

    def pin(x, z, col):
        pins[col].append(ns.cyl(0.055, 0.07, loc=(x, CORK_Y - 0.075, z), rot=(90, 0, 0), verts=6, bevel=0.0))

    # --- shift schedule (left) ---
    sx0, sx1, sz0, sz1 = -1.72, -0.12, 1.0, 2.7
    sch = [C.quad_xz(sx0, sx1, sz0, sz1, y1)]
    hdr = [C.quad_xz(sx0 + 0.06, sx1 - 0.06, sz1 - 0.36, sz1 - 0.06, y2)]
    txt = [C.text("SCHEDULE", 0.2, 0.01, ((sx0 + sx1) / 2, y3 + 0.005, sz1 - 0.21), width=1.12, res=1, spacing=1.08,
                  flat=True)]
    grid = []
    gx0, gx1, gz0, gz1 = sx0 + 0.1, sx1 - 0.1, sz0 + 0.1, sz1 - 0.44
    rows, cols = 5, 4
    for r in range(rows + 1):
        z = gz0 + (gz1 - gz0) * r / rows
        grid.append(C.quad_xz(gx0, gx1, z - 0.011, z + 0.011, y2))
    for c in range(1, cols):
        x = gx0 + (gx1 - gx0) * c / cols
        grid.append(C.quad_xz(x - 0.011, x + 0.011, gz0, gz1, y2))
    marks = {"#E8502A": [(1, 0), (3, 2)], "#3C6FB0": [(0, 1), (2, 3), (3, 4)], "#3E8A4F": [(2, 1), (1, 3)]}
    cw, rh = (gx1 - gx0) / cols, (gz1 - gz0) / rows
    for col, cells in marks.items():
        for c, r in cells:
            x = gx0 + cw * (c + 0.5)
            z = gz0 + rh * (r + 0.5)
            notes.setdefault(col, []).append(C.quad_xz(x - cw * 0.32, x + cw * 0.32, z - rh * 0.22, z + rh * 0.22, y3))
    C.turn_y(sch + hdr + txt + grid + [o for v in notes.values() for o in v], 1.5, (sx0 + sx1) / 2, (sz0 + sz1) / 2)
    papers += sch
    brand += hdr
    white += txt
    ink += grid
    pin(sx0 + 0.16, sz1 - 0.02, "PinsRed")
    pin(sx1 - 0.16, sz1 + 0.02, "PinsBlue")

    # --- SAFETY FIRST flyer (right) ---
    fx0, fx1, fz0, fz1 = 0.08, 1.2, 1.05, 2.72
    fly = [C.quad_xz(fx0, fx1, fz0, fz1, y1)]
    fh = [C.quad_xz(fx0 + 0.05, fx1 - 0.05, fz1 - 0.56, fz1 - 0.05, y2)]
    ftxt = [C.text("SAFETY", 0.2, 0.01, ((fx0 + fx1) / 2, y3 + 0.005, fz1 - 0.19), width=0.86, res=1, spacing=1.06,
                   flat=True),
            C.text("FIRST", 0.2, 0.01, ((fx0 + fx1) / 2, y3 + 0.005, fz1 - 0.42), width=0.7, res=1, spacing=1.06,
                   flat=True)]
    cx, cz = (fx0 + fx1) / 2, fz0 + 0.68
    a, b = 0.08, 0.24     # one 12-point cross polygon (two overlapping quads would z-fight)
    cpts = [(a, -b), (a, -a), (b, -a), (b, a), (a, a), (a, b), (-a, b), (-a, a), (-b, a), (-b, -a), (-a, -a), (-a, -b)]
    cross = [C.face_dir(C.poly([(cx + u, y2, cz + v) for u, v in cpts]), "-Y")]
    flines = [C.quad_xz(fx0 + 0.14, fx1 - 0.14 - 0.12 * k, fz0 + 0.3 - 0.11 * k, fz0 + 0.34 - 0.11 * k, y2) for k in range(2)]
    C.turn_y(fly + fh + ftxt + cross + flines, -3.0, (fx0 + fx1) / 2, (fz0 + fz1) / 2)
    papers += fly
    green += fh + cross
    white += ftxt
    ink += flines
    pin((fx0 + fx1) / 2 + 0.05, fz1 - 0.03, "PinsYellow")

    # --- sticky notes + scribbles ---
    for i, (x, z, s, ang, col) in enumerate(((1.52, 2.32, 0.5, 6, C.STICKY), (1.5, 1.62, 0.5, -5, "#F49AC1"),
                                             (-1.38, 0.55, 0.52, -4, "#9FD8F0"), (-0.72, 0.52, 0.5, 5, C.STICKY))):
        q = [C.quad_xz(x - s / 2, x + s / 2, z - s / 2, z + s / 2, y1)]
        sc = [C.strip_xz((x - s * 0.34, z + s * 0.12 - k * 0.12), (x + s * (0.3 - 0.1 * k), z + s * 0.16 - k * 0.12),
                         0.03, y2) for k in range(2)]
        C.turn_y(q + sc, ang, x, z)
        notes.setdefault(col, []).extend(q)
        ink += sc
        pin(x + 0.02, z + s / 2 - 0.08, ("PinsRed", "PinsBlue", "PinsYellow", "PinsBlue")[i])

    # --- little photo (white border + dark picture) ---
    px, pz = 0.5, 0.58
    ph = [C.quad_xz(px - 0.32, px + 0.32, pz - 0.38, pz + 0.38, y1)]
    pic = [C.quad_xz(px - 0.26, px + 0.26, pz - 0.2, pz + 0.32, y2)]
    C.turn_y(ph + pic, -7, px, pz)
    papers += ph
    pin(px, pz + 0.3, "PinsRed")

    C.part(papers, "Papers", C.PAPER, smooth_angle=None)
    C.part(brand, "Header", C.BRAND, smooth_angle=None)
    C.part(green, "Green", GREEN, smooth_angle=None)
    C.part(white, "WhiteText", "#FBF8F0", smooth_angle=None)
    C.part(ink, "Ink", C.INK, smooth_angle=None)
    C.part(pic, "Photo", "#3D4A5C", smooth_angle=None)
    for i, (col, objs) in enumerate(notes.items()):
        C.part(objs, f"Notes{i}", col, smooth_angle=None)
    for k, objs in pins.items():
        if objs:
            C.part(objs, k, PIN_COLS[k], smooth_angle=40)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)"}

if __name__ == "__main__":
    C.run(build, "Shop_CorkBoard", mount="wall", budget=800, meta=META)
