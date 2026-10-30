"""World_GasStation — abandoned roadside gas station (~40 wide x 18 tall x 28 deep).

Across the road from the diner. A cracked, oil-stained concrete pad with weeds; a flat
canopy on four columns whose dirty fascia carries a dead sign ("GAS" with the A fallen
askew) and one broken fascia panel hanging off a corner; three dead canopy lights and ONE
still-working cold lamp (Lamp, Neon, role "lamp" — flicker it); two faded pumps on a
raised island (one hose cut and lying on the ground); a small boarded-up kiosk behind
(boarded windows and door, faded sign band, rooftop AC box, a tyre and an oil drum by
the wall); and a faded tall price sign at the front-right corner with missing number
tiles and one crooked row (both faces dressed). Creepy, not gory.

Front = -Y (faces the road). Pivot = ground level, centre of the pad.
Socket Light = centre of the working lamp's lens (attach a SpotLight facing down).
Exports as 5 MeshParts (Concrete, Metal, SmoothPlastic, WoodPlanks, Lamp), no collision.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
PAD_TOP = 0.2
CAN_X, CAN_Y = -5.0, -6.0          # canopy centre
CAN_W, CAN_D = 22.0, 12.0
CAN_Z0, CAN_Z1 = 9.0, 10.6          # underside / top
COL_DX, COL_DY = 8.5, 3.5
KIOSK = (-12.0, 2.0, 4.0, 12.0, 8.0)   # x0, x1, y0, y1, height
SIGN_X, SIGN_Y = 15.5, -10.0
LAMP_AT = (CAN_X - 4.5, CAN_Y - 2.4)   # the one working light (front-left)

PAD = "#5F5E59"
STAIN = "#3B3A37"
FASCIA = "#A9A59B"
UNDER = "#55534E"
STRIPE = "#7A3B33"
COLUMN = "#8E8B83"
COLUMN_BASE = "#4F4D49"
ISLAND = "#7A7871"
BOLLARD = "#9C8540"
PUMP_RED = "#7E3A32"
PUMP_TOP = "#A7A296"
DARK = "#1E2124"
DEAD_LIGHT = "#2F3236"
KIOSK_WALL = "#6E6A62"
KIOSK_BASE = "#55524C"
BOARD = "#6B5A47"
BOARD_DARK = "#56483A"
SIGN_FACE = "#9C978C"
LOGO = "#6E3A34"
PRICE_PANEL = "#24262A"
TILE = "#C9C4B8"
STEEL = "#4A4F55"
WEED = "#3A5230"
TIRE = "#1F2023"
RUST = "#5B4434"
LAMP = "#D6F0DC"
ROOF = "#4E4C48"           # weathered roofing on the canopy top
LETTER = "#B9B3A6"         # faded off-white plastic sign letters


def plank(p0, p1, w=0.42, t=0.09, normal_y=-1, name="Plank"):
    """A board nailed flat against a -Y (or +Y) facing wall, from p0 to p1 in the XZ plane."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    b = ns.box((d.length, t, w), loc=(0, 0, 0), bevel=0.02, segments=1, name=name)
    b.rotation_euler = (0, -math.atan2(d.z, d.x), 0)
    b.location = (p0 + p1) / 2
    return b


def build():
    rnd = random.Random(13)
    concrete, metal, plastic, wood = [], [], [], []

    # ---- pad, stains, cracks, weeds
    concrete.append(C.box((40.0, 28.0, 0.25), loc=(0, 0, PAD_TOP - 0.125)))
    flat = []
    for (x, y, r, k) in ((-7.0, -6.6, 1.5, 7), (-2.0, -4.8, 1.0, 6), (6.0, -9.0, 1.3, 7), (-15.5, 0.5, 1.2, 6),
                         (9.0, 6.0, 1.4, 7)):
        pts = [(x + r * (0.7 + 0.5 * rnd.random()) * math.cos(2 * math.pi * i / k),
                y + r * (0.6 + 0.4 * rnd.random()) * math.sin(2 * math.pi * i / k)) for i in range(k)]
        flat.append(C.mesh_obj([(px, py, PAD_TOP + 0.03) for px, py in pts], [tuple(range(k))], "Stain"))
    # cracks: thin zig-zag strips
    for (x0, y0, ang, n) in ((-18.0, -12.0, 25, 5), (4.0, 3.0, -35, 4), (12.0, -4.0, 70, 4), (-3.0, 9.0, 10, 5)):
        x, y = x0, y0
        for i in range(n):
            a = math.radians(ang + rnd.uniform(-35, 35))
            L = rnd.uniform(1.4, 2.4)
            nx, ny = x + L * math.cos(a), y + L * math.sin(a)
            dx, dy = (ny - y) / L * 0.07, -(nx - x) / L * 0.07
            flat.append(C.mesh_obj([(x - dx, y - dy, PAD_TOP + 0.03), (x + dx, y + dy, PAD_TOP + 0.03),
                                    (nx + dx, ny + dy, PAD_TOP + 0.03), (nx - dx, ny - dy, PAD_TOP + 0.03)],
                                   [(0, 1, 2, 3)], "Crack"))
            x, y = nx, ny
    for o in flat:   # make sure every decal faces up
        bm_ = o.data
        for poly in bm_.polygons:
            if poly.normal.z < 0:
                poly.flip()
    plastic_stains = flat
    weeds = []
    for (x, y) in ((-18.5, -12.5), (-16.0, -10.8), (5.6, 3.8), (12.6, -2.6), (13.2, -2.0), (-2.4, 9.6), (18.0, 12.0),
                   (-13.0, 3.2), (3.0, 3.4), (16.6, -9.0)):
        for k in range(2):
            a = rnd.uniform(0, math.tau)
            h = rnd.uniform(0.5, 0.9)
            tip = (x + 0.15 * math.cos(a), y + 0.15 * math.sin(a), PAD_TOP + h)
            weeds.append(C.rod((x + 0.12 * k, y, PAD_TOP - 0.02), tip, 0.14, verts=3, r_top=0.0))

    # ---- canopy: deck + fascia, faded stripe, dead sign, hanging broken panel, lights
    deck = C.box((CAN_W, CAN_D, CAN_Z1 - CAN_Z0), loc=(CAN_X, CAN_Y, (CAN_Z0 + CAN_Z1) / 2), bevel=0.06)
    under = C.box((CAN_W - 0.5, CAN_D - 0.5, 0.06), loc=(CAN_X, CAN_Y, CAN_Z0 - 0.02))
    stripe = C.ring_slab(C.rrect(CAN_W + 0.1, CAN_D + 0.1, 0.06, 1, CAN_X, CAN_Y), C.rrect(CAN_W - 0.4, CAN_D - 0.4, 0.04, 1, CAN_X, CAN_Y),
                         "z", CAN_Z0 + 0.38, CAN_Z0 + 0.62)
    sz = CAN_Z0 + 1.08                     # dead sign panel centre (above the stripe band)
    sign_panel = C.box((6.2, 0.1, 0.84), loc=(CAN_X, CAN_Y - CAN_D / 2 - 0.04, sz))   # front at y0 - 0.09
    fy = CAN_Y - CAN_D / 2 - 0.13          # flat letter caps land 0.06 in front of the panel
    g = C.text("G", 0.62, 0.04, (CAN_X - 1.6, fy, sz), res=1, flat=True)
    s_ = C.text("S", 0.62, 0.04, (CAN_X + 1.5, fy, sz), res=1, flat=True)
    a_ = C.text("A", 0.62, 0.04, (0, 0, 0), res=1, flat=True)
    C.transform_obj(a_, loc=(CAN_X + 0.1, fy - 0.01, sz - 0.14), rot_deg=(0, 32, 0))
    # broken fascia panel hanging off the front-right corner by one edge
    hx, hy = CAN_X + CAN_W / 2 - 1.6, CAN_Y - CAN_D / 2 - 0.12
    hang = C.box((3.0, 0.12, 1.5), loc=(0, 0, 0), bevel=0.03)
    C.transform_obj(hang, loc=(hx, hy, CAN_Z0 - 0.35), rot_deg=(0, -38, 0), origin=(0, 0, 0))
    fascia_gap = C.box((3.0, 0.06, 1.3), loc=(hx, CAN_Y - CAN_D / 2 - 0.06, CAN_Z0 + 0.78))
    lights_dead, lamp = [], None
    for ix in (-1, 1):
        for iy in (-1, 1):
            lx, ly = CAN_X + ix * 4.5, CAN_Y + iy * 2.4
            panel = C.box((1.7, 1.7, 0.12), loc=(lx, ly, CAN_Z0 - 0.09))
            if (round(lx, 2), round(ly, 2)) == (round(LAMP_AT[0], 2), round(LAMP_AT[1], 2)):
                lamp = panel
            else:
                lights_dead.append(panel)

    # ---- columns
    cols, col_bases = [], []
    for ix in (-1, 1):
        for iy in (-1, 1):
            x, y = CAN_X + ix * COL_DX, CAN_Y + iy * COL_DY
            cols.append(C.box((0.9, 0.9, CAN_Z0 - PAD_TOP + 0.16), loc=(x, y, (CAN_Z0 + PAD_TOP) / 2 - 0.03), bevel=0.05))
            col_bases.append(C.box((1.2, 1.2, 1.3), loc=(x, y, PAD_TOP + 0.6), bevel=0.05))

    # ---- pump island + bollards + pumps
    isl = C.prism(C.rrect(12.5, 2.2, 1.0, 2, CAN_X, CAN_Y), "z", PAD_TOP - 0.02, PAD_TOP + 0.4)
    bollards = [C.lathe([(0.3, PAD_TOP + 0.38), (0.3, PAD_TOP + 1.8), (0.0, PAD_TOP + 2.0)], verts=6,
                        loc=(CAN_X + sx * 5.6, CAN_Y, 0)) for sx in (-1, 1)]
    pump_red, pump_top, pump_dark, hoses = [], [], [], []
    iz = PAD_TOP + 0.4
    for k, px in enumerate((CAN_X - 2.6, CAN_X + 2.6)):
        py = CAN_Y
        pump_red.append(C.box((1.6, 1.0, 2.7), loc=(px, py, iz + 1.35), bevel=0.06))
        pump_top.append(C.box((1.7, 1.1, 0.9), loc=(px, py, iz + 2.7 + 0.4), bevel=0.06))
        pump_top.append(C.box((1.9, 1.3, 0.25), loc=(px, py, iz + 0.1), bevel=0.03))
        for sy in (-1, 1):   # display windows on both faces
            pump_dark.append(C.box((1.1, 0.04, 0.55), loc=(px, py + sy * 0.57, iz + 3.12)))
            pump_dark.append(C.box((0.9, 0.04, 0.7), loc=(px, py + sy * 0.52, iz + 1.9)))
        # hose: from the pump side, one hanging to its holster, the other cut and lying on the pad
        sx = 1 if k == 0 else -1
        x0 = px + sx * 0.75
        if k == 0:
            # hose loops down and back up to the nozzle hanging in its holster (U wide enough
            # that the tube never passes through itself)
            pts = [(x0, py - 0.15, iz + 2.4), (x0 + sx * 0.55, py - 0.2, iz + 1.3), (x0 + sx * 0.5, py - 0.3, iz + 0.45),
                   (x0 + sx * 0.12, py - 0.42, iz + 1.2), (x0 + sx * 0.12, py - 0.48, iz + 1.75)]
            metal.append(C.box((0.25, 0.32, 0.6), loc=(x0 + 0.12 * sx, py - 0.68, iz + 2.0)))   # nozzle, clear of the body
        else:
            pts = [(x0, py - 0.2, iz + 2.4), (x0 + sx * 0.35, py - 0.45, iz + 1.0), (x0 + sx * 0.6, py - 1.25, PAD_TOP + 0.48),
                   (x0 + sx * 1.1, py - 1.7, PAD_TOP + 0.08), (x0 + sx * 2.2, py - 2.0, PAD_TOP + 0.08),
                   (x0 + sx * 2.9, py - 1.7, PAD_TOP + 0.08)]
        hoses.append(C.pipe(pts, 0.07, sides=4, corner=0.3, corner_segs=2))

    # ---- kiosk
    kx0, kx1, ky0, ky1, kh = KIOSK
    kcx, kcy = (kx0 + kx1) / 2, (ky0 + ky1) / 2
    walls = C.box((kx1 - kx0, ky1 - ky0, kh), loc=(kcx, kcy, PAD_TOP + kh / 2 - 0.05), bevel=0.05)
    base = C.box((kx1 - kx0 + 0.16, ky1 - ky0 + 0.16, 1.03), loc=(kcx, kcy, PAD_TOP + 0.435))
    cap = C.box((kx1 - kx0 + 0.5, ky1 - ky0 + 0.5, 0.5), loc=(kcx, kcy, PAD_TOP + kh + 0.1), bevel=0.04)
    concrete += [walls]
    kiosk_dark = []
    fyk = ky0 - 0.03
    openings = [(kx0 + 3.0, 3.6, 3.0, 2.4), (kcx + 1.6, 3.2, 2.2, 4.4), (kx1 - 3.0, 3.6, 3.0, 2.4)]  # (x, zc, w, h)
    for ox, oz, ow, oh in openings:
        kiosk_dark.append(C.box((ow, 0.06, oh), loc=(ox, fyk, PAD_TOP + oz)))
    boards = []
    by = ky0 - 0.08
    # left window: three boards, one hanging diagonally
    lx, lz = openings[0][0], PAD_TOP + openings[0][1]
    boards.append(plank((lx - 1.8, by, lz + 0.8), (lx + 1.8, by, lz + 0.8)))
    boards.append(plank((lx - 1.8, by, lz - 0.1), (lx + 1.8, by, lz + 0.05)))
    boards.append(plank((lx - 1.4, by, lz - 1.3), (lx + 1.7, by, lz - 0.55)))
    # door: an X of boards + one across
    dx_, dz_ = openings[1][0], PAD_TOP + openings[1][1]
    boards.append(plank((dx_ - 1.3, by, dz_ - 2.0), (dx_ + 1.3, by, dz_ + 2.0), w=0.48))
    boards.append(plank((dx_ + 1.3, by - 0.09, dz_ - 2.0), (dx_ - 1.3, by - 0.09, dz_ + 2.0), w=0.48))
    boards.append(plank((dx_ - 1.5, by - 0.18, dz_ + 0.2), (dx_ + 1.5, by - 0.18, dz_ + 0.2), w=0.48))
    # right window: boards plus a gap (one board missing)
    rx, rz = openings[2][0], PAD_TOP + openings[2][1]
    for k, dz in enumerate((0.85, 0.2, -0.9)):
        if k == 1:
            continue
        boards.append(plank((rx - 1.8, by, rz + dz), (rx + 1.8, by, rz + dz + (0.06 if k == 0 else -0.08))))
    sign_band = C.box((8.0, 0.14, 1.1), loc=(kcx - 1.0, ky0 - 0.05, PAD_TOP + 6.6), bevel=0.03)
    ac = C.box((2.6, 2.0, 1.4), loc=(kx1 - 2.5, ky1 - 2.0, PAD_TOP + kh + 0.35 + 0.65), bevel=0.05)
    tire = ns.torus(0.75, 0.3, loc=(kx1 - 1.2, ky0 - 0.45, PAD_TOP + 1.0), rot=(78, 0, 8), major_segs=10, minor_segs=4)
    drum = C.lathe([(0.62, PAD_TOP - 0.02), (0.62, PAD_TOP + 1.85), (0.0, PAD_TOP + 1.9)], verts=8,
                   loc=(kx0 + 1.1, ky0 - 0.9, 0))

    # ---- faded tall price sign (both faces)
    sbase = C.box((1.6, 1.6, 0.8), loc=(SIGN_X, SIGN_Y, PAD_TOP + 0.3), bevel=0.06)
    pole = C.lathe([(0.42, PAD_TOP + 0.6), (0.36, 12.2)], verts=8, loc=(SIGN_X, SIGN_Y, 0))
    sbox = C.box((5.2, 1.0, 6.2), loc=(SIGN_X, SIGN_Y, 12.0 + 3.1), bevel=0.08)
    sign_light, sign_logo, sign_panels, sign_tiles = [], [], [], []
    for sy in (-1, 1):
        f = SIGN_Y + sy * 0.52
        sign_light.append(C.box((4.6, 0.06, 2.3), loc=(SIGN_X, f, 16.65)))
        logo = C.disc(0.95, verts=10)
        logo.rotation_euler = (math.radians(90 if sy < 0 else -90), 0, 0)
        logo.location = (SIGN_X, f + sy * 0.05, 16.65)
        sign_logo.append(logo)
        for r, zc in enumerate((15.0, 13.85, 12.7)):
            crooked = (r == 1)
            rot = 7.0 if crooked else 0.0
            dzc = -0.15 if crooked else 0.0
            out_ = 0.05 if crooked else 0.02      # the crooked row hangs proud of its neighbours
            pnl = C.box((4.4, 0.06, 0.95), loc=(0, 0, 0))
            C.transform_obj(pnl, loc=(SIGN_X, f + sy * out_, zc + dzc), rot_deg=(0, rot * (1 if sy < 0 else -1), 0))
            sign_panels.append(pnl)
            for t in range(3):
                if (r, t) in ((0, 2), (2, 0)):
                    continue      # missing number tiles
                tx = -1.25 + t * 1.0
                tile = C.box((0.72, 0.05, 0.62), loc=(0, 0, 0))
                ang = math.radians(rot * (1 if sy < 0 else -1))
                ox, oz = tx * math.cos(ang), -tx * math.sin(ang)
                C.transform_obj(tile, loc=(SIGN_X + ox, f + sy * (out_ + 0.04), zc + dzc + oz),
                                rot_deg=(0, rot * (1 if sy < 0 else -1), 0))
                sign_tiles.append(tile)

    # ---- tag parts
    C.part(concrete, "Concrete", PAD, "Concrete", smooth_angle=None)
    C.part([base], "KioskBase", KIOSK_BASE, "Concrete", smooth_angle=None)
    C.part([isl], "Island", ISLAND, "Concrete", smooth_angle=None)
    C.part(col_bases, "ColumnBases", COLUMN_BASE, "Concrete", smooth_angle=None)
    C.part([sbase], "SignBase", ISLAND, "Concrete", smooth_angle=None)
    ns.apply_all(deck)
    sides = C.split_faces(deck, lambda c, n, i: "top" if n.z > 0.9 else "side", name="Deck")
    C.part([sides["side"], hang], "Canopy", FASCIA, "Metal", smooth_angle=None)
    C.part([sides["top"]], "CanopyRoof", ROOF, "Metal", smooth_angle=None)
    C.part([under], "CanopyUnder", UNDER, "Metal", smooth_angle=None)
    C.part(cols, "Columns", COLUMN, "Metal", smooth_angle=None)
    C.part([stripe], "Stripe", STRIPE, "Metal", smooth_angle=None)
    C.part(pump_red, "PumpBody", PUMP_RED, "Metal", smooth_angle=None)
    C.part(pump_top, "PumpTop", PUMP_TOP, "Metal", smooth_angle=None)
    C.part([pole, sbox] + metal, "SignSteel", STEEL, "Metal", smooth_angle=None)
    C.part(bollards, "Bollards", BOLLARD, "Metal", smooth_angle=None)
    C.part([drum], "Drum", RUST, "Metal", smooth_angle=None)
    C.part([cap, ac], "KioskTrim", KIOSK_WALL, "Metal", smooth_angle=None)
    C.part(plastic_stains, "Stains", STAIN, "SmoothPlastic", smooth_angle=None)
    C.part(weeds, "Weeds", WEED, "SmoothPlastic", smooth_angle=None)
    C.part(pump_dark + kiosk_dark + [sign_panel, fascia_gap], "DarkPanels", DARK, "SmoothPlastic", smooth_angle=None)
    C.part(lights_dead, "DeadLights", DEAD_LIGHT, "SmoothPlastic", smooth_angle=None)
    C.part(hoses + [tire], "Rubber", TIRE, "SmoothPlastic", smooth_angle=None)
    C.part([g, s_, a_], "SignLetters", LETTER, "SmoothPlastic", smooth_angle=None)
    C.part([sign_band], "SignBand", "#837D71", "SmoothPlastic", smooth_angle=None)
    C.part(sign_light, "SignFace", SIGN_FACE, "SmoothPlastic", smooth_angle=None)
    C.part(sign_logo, "SignLogo", LOGO, "SmoothPlastic", smooth_angle=None)
    C.part(sign_panels, "PricePanels", PRICE_PANEL, "SmoothPlastic", smooth_angle=None)
    C.part(sign_tiles, "PriceTiles", TILE, "SmoothPlastic", smooth_angle=None)
    C.part(boards[::2], "Boards", BOARD, "WoodPlanks", smooth_angle=None)
    C.part(boards[1::2], "BoardsDark", BOARD_DARK, "WoodPlanks", smooth_angle=None)
    ns.tag(lamp, "Lamp", LAMP, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)


SOCKETS = {"Light": ((LAMP_AT[0], LAMP_AT[1], CAN_Z0 - 0.15), 0.0)}
META = {"kind": "gas_station", "pivot": "ground level, pad centre", "abandoned": True,
        "roles": {"lamp": "Lamp (the one working canopy light — flicker / buzz it)"},
        "light_hint": {"type": "SpotLight", "at": "Socket_Light", "face": "Bottom", "color": LAMP, "range": 24,
                       "angle": 100, "brightness": 1.2, "flicker": True}}

if __name__ == "__main__":
    C.run(build, "World_GasStation", sockets=SOCKETS, meta=META)
