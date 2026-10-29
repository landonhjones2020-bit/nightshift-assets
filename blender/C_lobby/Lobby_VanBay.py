"""Lobby_VanBay — painted parking bay for one Lobby_ShiftVan (14 wide x 20 long).

Ground paint (every flat marking sits 0.02 above the ground, pivot at ground level):
warm-white bay lines (U-shape around the van, open to the front), a loading lane on the
van's door side (-X) with a mustard chevron trail leading from the front to the join pad
and a hatched keep-clear box behind it. The join pad is a raised navy disc ringed by a
glowing tube (PadRing, Neon, role "pad_glow": code recolours / pulses it). Two concrete
wheel stops sit behind the van's rear wheels. A sign post at the front of the lane holds a
red-orange sign box with a countdown screen (Screen, role "screen", Front face).

PIVOT = where Lobby_ShiftVan's pivot goes (same orientation, front -Y). The van's door side
faces the loading lane; place bays side by side every 14 studs along X.
Sockets: Van (van pivot), Pad (pad centre on the ground, facing the van door; matches the
van's Socket_Pad), Sign (centre of the countdown screen face, facing front).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
X0, X1 = -9.4, 4.6            # bay footprint (14 wide)
Y0, Y1 = -10.0, 10.0          # 20 long
Z0, ZP = 0.02, 0.025          # paint bottom (above ground) and paint thickness
LINE = 0.3
PAD_X, PAD_Y = C.VAN_PAD
PAD_R = 1.8
PAINT_WHITE = "#ECE5D4"
POST = (-8.55, -8.9)          # sign post position
SCR_W, SCR_H = 2.3, 1.35
SCR_Z = 5.35                  # screen centre height


def paint(poly, z0=Z0, t=ZP):
    """Flat paint decal from a 2D polygon (x, y), bottom at z0."""
    return C.prism(poly, "z", z0, z0 + t)


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def clip(poly, x0, x1, y0, y1):
    """Sutherland-Hodgman clip of a polygon to an axis-aligned rectangle."""
    def edge(pts, inside, cut):
        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            ia, ib = inside(a), inside(b)
            if ib:
                if not ia:
                    out.append(cut(a, b))
                out.append(b)
            elif ia:
                out.append(cut(a, b))
        return out

    def cx(v):
        return lambda a, b: (v, a[1] + (b[1] - a[1]) * (v - a[0]) / (b[0] - a[0]))

    def cy(v):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (v - a[1]) / (b[1] - a[1]), v)

    pts = poly
    for inside, cut in ((lambda p: p[0] >= x0, cx(x0)), (lambda p: p[0] <= x1, cx(x1)),
                        (lambda p: p[1] >= y0, cy(y0)), (lambda p: p[1] <= y1, cy(y1))):
        pts = edge(pts, inside, cut)
        if not pts:
            return []
    return pts


def chevron(cx, cy, w=1.9, h=0.75, t=0.42):
    """Chevron pointing +Y (toward the pad), centred at (cx, cy)."""
    return [(cx - w / 2, cy - h / 2), (cx, cy + h / 2 - t), (cx + w / 2, cy - h / 2), (cx + w / 2, cy - h / 2 + t),
            (cx, cy + h / 2), (cx - w / 2, cy - h / 2 + t)]


def build():
    white, mustard = [], []
    # bay lines: right side, back, left side (broken at the loading door zone), lane outer edge
    white.append(paint(rect(X1 - LINE, X1, Y0 + 0.4, Y1 - 0.4 - LINE)))
    white.append(paint(rect(X0, X1, Y1 - 0.4 - LINE, Y1 - 0.4)))
    lx = -4.75
    white.append(paint(rect(lx - LINE, lx, Y0 + 0.4, PAD_Y - PAD_R - 0.6)))
    white.append(paint(rect(lx - LINE, lx, PAD_Y + PAD_R + 0.6, Y1 - 0.4 - LINE)))
    white.append(paint(rect(X0, X0 + LINE, Y0 + 0.4, Y1 - 0.4 - LINE)))
    # chevron trail from the front edge to the pad (lane centre = pad x)
    for k in range(4):
        mustard.append(paint(chevron(PAD_X, Y0 + 1.6 + k * 1.45)))
    # hatched keep-clear box behind the pad
    hx0, hx1, hy0, hy1 = X0 + LINE + 0.45, lx - LINE - 0.45, PAD_Y + PAD_R + 1.0, Y1 - 1.6
    frame_t = 0.22
    for r in (rect(hx0, hx1, hy0, hy0 + frame_t), rect(hx0, hx1, hy1 - frame_t, hy1),
              rect(hx0, hx0 + frame_t, hy0 + frame_t, hy1 - frame_t), rect(hx1 - frame_t, hx1, hy0 + frame_t, hy1 - frame_t)):
        mustard.append(paint(r))
    ix0, ix1, iy0, iy1 = hx0 + frame_t + 0.15, hx1 - frame_t - 0.15, hy0 + frame_t + 0.15, hy1 - frame_t - 0.15
    w = 0.32
    for k in range(-6, 12):
        b = iy0 + k * 0.85
        stripe = [(ix0, b), (ix0, b + w), (ix1, b + w + (ix1 - ix0)), (ix1, b + (ix1 - ix0))]
        pc = clip(stripe, ix0, ix1, iy0, iy1)
        if len(pc) >= 3:
            mustard.append(paint(pc))
    C.part(white, "PaintWhite", PAINT_WHITE, smooth_angle=None)
    C.part(mustard, "PaintMustard", C.MUSTARD, smooth_angle=None)

    # join pad: raised navy disc + glowing ring + a thin mustard inner ring
    disc = C.prism(C.circle_pts(PAD_R - 0.33, 28, PAD_X, PAD_Y), "z", Z0, 0.09)
    ns.bevel(disc, width=0.02, segments=1)
    C.part([disc], "PadDisc", C.NAVY, smooth_angle=40)
    ring = C.ring_slab(C.circle_pts(PAD_R, 28, PAD_X, PAD_Y), C.circle_pts(PAD_R - 0.3, 28, PAD_X, PAD_Y), "z", Z0, 0.13)
    ns.tag(ring, "PadRing", C.CYAN, "Neon", recolor="pad_glow", cast_shadow=False, smooth_angle=50)
    inner = C.ring_slab(C.circle_pts(0.95, 24, PAD_X, PAD_Y), C.circle_pts(0.8, 24, PAD_X, PAD_Y), "z", 0.09, 0.1)
    arrow = C.prism([(PAD_X + 0.95, PAD_Y), (PAD_X + 0.35, PAD_Y + 0.45), (PAD_X + 0.35, PAD_Y - 0.45)], "z", 0.09, 0.1)
    C.part([inner, arrow], "PadMark", C.MUSTARD, smooth_angle=None)

    # concrete wheel stops behind the van's rear wheels
    stops = []
    for sx in (-1, 1):
        prof = C.fillet([(-0.4, 0.0), (0.4, 0.0), (0.28, 0.42), (-0.28, 0.42)], [0, 0, 0.1, 0.1], 2)
        stops.append(C.prism([(y + 7.1, z) for y, z in prof], "x", sx * 2.2 - 1.0, sx * 2.2 + 1.0))
    for o in stops:
        ns.bevel(o, width=0.05, segments=1)
    C.part(stops, "WheelStops", C.CONCRETE, "Concrete", smooth_angle=40)
    # yellow reflector stripes on the stops
    refl = [ns.box((0.5, 0.02, 0.14), loc=(sx * 2.2 + dx, 6.72, 0.22), rot=(-17, 0, 0), bevel=0.0)
            for sx in (-1, 1) for dx in (-0.55, 0.55)]

    # sign post: concrete footing, navy pole, red-orange sign box with screen + VAN header
    px, py = POST
    foot = ns.cyl(0.55, 0.5, loc=(px, py, 0.25), verts=12, radius_top=0.45, bevel=0.04, segments=1)
    C.part([foot], "Footing", C.CONCRETE, "Concrete", smooth_angle=40)
    pole = ns.cyl(0.17, SCR_Z - 0.4, loc=(px, py, 0.5 + (SCR_Z - 0.9) / 2), verts=10, bevel=0.0)
    collar = ns.cyl(0.26, 0.3, loc=(px, py, 0.62), verts=10, bevel=0.03, segments=1)
    C.part([pole, collar], "Pole", C.NAVY, "Metal", smooth_angle=40)
    bw, bh, bd = SCR_W + 0.5, SCR_H + 1.15, 0.5
    bz = SCR_Z - SCR_H / 2 - 0.25 + bh / 2
    box = C.prism(C.rrect(bw, bh, 0.22, 3, px, bz), "y", py - bd / 2, py + bd / 2)
    ns.bevel(box, width=0.05, segments=1)
    C.part([box], "SignBox", C.BRAND, smooth_angle=40)
    bez = C.ring_slab(C.rrect(SCR_W + 0.22, SCR_H + 0.22, 0.12, 2, px, SCR_Z), C.rrect(SCR_W, SCR_H, 0.08, 2, px, SCR_Z),
                      "y", py - bd / 2 - 0.06, py - bd / 2 + 0.02)
    hdr_z = SCR_Z + SCR_H / 2 + 0.42
    letters = C.text("VAN", 0.5, 0.06, (px, py - bd / 2 - 0.02, hdr_z), width=1.15, res=1, spacing=1.15)
    C.part([bez, letters] + refl, "SignTrim", C.MUSTARD, smooth_angle=40)
    scr = C.prism(C.rrect(SCR_W, SCR_H, 0.08, 2, px, SCR_Z), "y", py - bd / 2 - 0.04, py - bd / 2 + 0.02)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)
    # little lamp hood over the sign
    hood = C.prism(C.fillet([(py - bd / 2 - 0.35, 0.0), (py + bd / 2, 0.0), (py + bd / 2, 0.16), (py - bd / 2 - 0.35, 0.06)],
                            [0.02, 0, 0, 0.02], 1), "x", px - bw / 2 - 0.05, px + bw / 2 + 0.05)
    C.place(hood, (0, 0, bz + bh / 2 - 0.02))
    C.part([hood], "SignCap", C.NAVY_DEEP, smooth_angle=40)
    return {}


def sockets():
    return {"Van": ((0, 0, 0), 0.0),
            "Pad": ((PAD_X, PAD_Y, 0.0), 90.0),
            "Sign": ((POST[0], POST[1] - 0.25 - 0.04, SCR_Z), 0.0)}


META = {"pivot": "the van pivot (place Lobby_ShiftVan at this CFrame)", "bay_size": [14, 20],
        "bay_spacing": 14, "footprint_center": [2.4, 0, 0],
        "door_side": "Roblox +X (Blender -X): the loading lane", "pad_radius": PAD_R,
        "screen_size": [SCR_W, SCR_H], "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
        "roles": {"pad_glow": "PadRing (Neon)", "screen": "Screen (countdown)"},
        "paint_height": Z0}

if __name__ == "__main__":
    C.run(build, "Lobby_VanBay", sockets=sockets(), pivot=(0, 0, 0), meta=META, socket_views=((-30, 55),))
