"""Lobby_ShiftVan — the STACKHOUSE shift van (party pad), ~16.5 long x 7 wide x 7.5 tall.

Boxy retro step-van in cream-white livery (Body, role "van_paint", collides) with a
red-orange belt stripe and mustard pinstripe, a navy sandwich-logo badge on both sides
(the -X one rides on the open sliding door), round chrome-rimmed headlights, chrome grille
and bumpers, whitewall wheels, and a roof light bar (Lights, Neon, role "van_lights":
code can pulse it during the countdown). The sliding door on the -X side (the van's
curb side) is slid OPEN toward the back, showing two forward-facing 2-seat benches in red
vinyl under a warm dome light (DomeLight, role "lamp").
Number badge (NumberPlate, role "van_number") sits on the -X side just in front of the
door at eye height: code writes the van number 1-4 on it (SurfaceGui on its Right face).

Front = -Y. Pivot = bottom-centre on the ground plane (tyres touch it). Sockets:
  Seat1..Seat4  seat surface centres (sitting CFrame), all facing the front (yaw 0).
                Seat1 front bench door side, Seat2 front bench far side,
                Seat3 rear bench door side,  Seat4 rear bench far side.
  Pad           on the ground just outside the open door (the join prompt), facing the door.
  Door          centre of the door opening, facing out of the van (-X).
  NumberPlate   centre of the number badge face, facing out (-X).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
HW, HL = C.VAN_HW, C.VAN_HL
FLOOR = C.VAN_FLOOR
DY0, DY1 = C.VAN_DOOR_Y
DZ0, DZ1 = C.VAN_DOOR_Z
ROOF = 7.0
AXLES = (-5.4, 5.3)
WR = 1.1                      # wheel radius
SEAT_Z = 3.1                  # seat surface height
ROWS = (-1.75, 0.95)          # seat centre y of the front / rear bench
SEAT_X = (-1.35, 1.35)
STRIPE = (2.7, 3.25)
PIN = (3.42, 3.56)
NUM = (-3.98, 5.0, 1.3)       # number badge centre y, z and size
SEAT_RED = "#C9432C"
LINING = "#D6CEBE"
FLOOR_COL = "#8F959B"
DOOR_OPEN_Y = 5.35            # door panel slid back (centre y)


def body_shell():
    prof = [(-HL, 1.0), (-HL, 3.2), (-7.6, 3.9), (-7.0, 4.1), (-6.5, 6.6), (-6.0, ROOF), (7.9, ROOF),
            (HL, 6.7), (HL, 1.0)]
    prof = C.fillet(prof, [0.15, 0.5, 0.3, 0.15, 0.25, 0.6, 0.4, 0.2, 0.15], 2)
    body = C.prism(prof, "x", -HW, HW)
    # cargo cavity, the sliding-door opening, and wheel wells (sides only)
    ns.boolean(body, ns.box((2 * HW - 0.6, HL - 0.35 + 4.2, 6.7 - FLOOR), loc=(0, (-4.2 + HL - 0.35) / 2, (FLOOR + 6.7) / 2),
                            bevel=0.0))
    door = C.fillet([(DY0, DZ0), (DY1, DZ0), (DY1, DZ1), (DY0, DZ1)], [0, 0, 0.35, 0.35], 3)
    ns.boolean(body, C.prism(door, "x", -HW - 0.5, -HW + 0.6))
    for y in AXLES:
        for sx in (-1, 1):
            ns.boolean(body, ns.cyl(WR + 0.22, 1.3, loc=(sx * (HW - 0.5), y, WR), rot=(0, 90, 0), verts=16, bevel=0.0))
    ns.bevel(body, width=0.07, segments=1)
    return body


def sliding_door():
    """Door panel slid back over the rear quarter, just outside the body side."""
    w = DY1 - DY0
    pts = C.fillet([(-w / 2, DZ0 - 0.08), (w / 2, DZ0 - 0.08), (w / 2, DZ1 + 0.02), (-w / 2, DZ1 + 0.02)],
                   [0.08, 0.08, 0.35, 0.35], 3)
    pts = [(y + DOOR_OPEN_Y, z) for y, z in pts]
    door = C.prism(pts, "x", -HW - 0.32, -HW - 0.12)
    # notch around the rear wheel arch (the door rides over the rear quarter)
    ns.boolean(door, ns.cyl(WR + 0.32, 1.0, loc=(-HW, AXLES[1], WR), rot=(0, 90, 0), verts=16, bevel=0.0))
    ns.bevel(door, width=0.05, segments=1)
    return door


def badge(cx, cy, cz, facing):
    """Navy logo badge with a mustard rim and the stacked-sandwich icon.
    facing: +1 = the +X side (faces +X), -1 = the -X side (faces -X)."""
    yaw = 90 if facing > 0 else -90
    outer = C.prism(C.rrect(4.3, 2.55, 0.6, 3), "y", -0.06, 0.0)
    inner = C.prism(C.rrect(4.0, 2.25, 0.48, 3), "y", -0.1, -0.03)
    icon = C.sandwich_icon(s=0.95, depth=0.1)
    C.place(icon, (0, -0.09, 0.08))
    out = {"rim": [outer], "navy": [inner], "icon": icon}
    for objs in (out["rim"], out["navy"]):
        C.place(objs, (cx, cy, cz), yaw=yaw)
    C.place(icon, (cx, cy, cz), yaw=yaw)
    return out


def wheel(x, y, sx):
    tire = ns.cyl(WR, 0.82, loc=(x, y, WR), rot=(0, 90, 0), verts=14, bevel=0.22, segments=1)
    # whitewall: a thin closed washer half-sunk into the tyre's flat side (the single-sided ring floated
    # 0.015 off the tyre and read as see-through from low angles)
    wall = ns.ring(0.62, 0.88, 0.04, loc=(x + sx * 0.41, y, WR), verts=16)
    wall.rotation_euler = (0, math.radians(90), 0)
    hub = ns.cyl(0.58, 0.14, loc=(x + sx * 0.4, y, WR), rot=(0, 90, 0), verts=10, radius_top=0.48, bevel=0.0)
    if sx < 0:
        hub.rotation_euler = (0, math.radians(-90), 0)
    cap = ns.cyl(0.2, 0.1, loc=(x + sx * 0.48, y, WR), rot=(0, 90, 0), verts=8, bevel=0.0)
    return tire, wall, hub, cap


def build():
    body = body_shell()
    door = sliding_door()
    handle = C.rod((-HW - 0.36, DOOR_OPEN_Y - 2.2, 3.7), (-HW - 0.36, DOOR_OPEN_Y - 2.2, 4.5), 0.06, verts=6)
    C.part([body, door], "Body", C.VAN_WHITE, recolor="van_paint", can_collide=True, smooth_angle=40)

    # --- livery: stripe + pinstripe on both sides and the back, door copies --------------
    stripe, pin = [], []
    for (z0, z1), lst in ((STRIPE, stripe), (PIN, pin)):
        zc, h = (z0 + z1) / 2, z1 - z0
        lst.append(ns.box((0.05, 2 * HL - 0.3, h), loc=(HW + 0.015, 0.0, zc), bevel=0.0))           # +X side
        # stops 0.08 before the door opening: ending on the jamb line it overhung the bevelled edge and
        # its end face lay in the jamb plane (z-fighting)
        lst.append(ns.box((0.05, DY0 - 0.08 + HL - 0.15, h), loc=(-HW - 0.015, (-HL + 0.15 + DY0 - 0.08) / 2, zc),
                          bevel=0.0))
        lst.append(ns.box((0.05, DY1 - DY0 - 0.12, h), loc=(-HW - 0.335, DOOR_OPEN_Y, zc), bevel=0.0))  # on door
        lst.append(ns.box((2 * HW - 0.3, 0.05, h), loc=(0, HL + 0.015, zc), bevel=0.0))              # back
    stripe.append(ns.box((2 * HW - 0.5, 0.05, 0.34), loc=(0, -HL - 0.015, 2.86), bevel=0.0))         # front band
    stripe.append(ns.box((2.6, 12.0, 0.05), loc=(0, 1.4, ROOF + 0.01), bevel=0.0))                    # roof band
    C.part(stripe, "Stripe", C.BRAND, smooth_angle=30)

    badges = [badge(HW - 0.02, 0.6, 5.05, +1), badge(-HW - 0.30, DOOR_OPEN_Y, 5.05, -1)]
    # front medallion: small navy disc + mustard rim + mini sandwich, on the nose
    med_rim = ns.cyl(0.52, 0.08, loc=(0, 0, 0), verts=16, bevel=0.0)
    med = ns.cyl(0.44, 0.06, loc=(0, 0, 0.05), verts=16, bevel=0.0)
    C.place([med_rim, med], (0, -HL - 0.12, 2.86), pitch=90)
    mini = C.sandwich_icon(s=0.3, depth=0.06)
    C.place(mini, (0, -HL - 0.17, 2.88))
    badges.append({"rim": [med_rim], "navy": [med], "icon": mini})
    icon_cols = {}
    for b in badges:
        for col, objs in b["icon"].items():
            icon_cols.setdefault(col, []).extend(objs)
    C.part([b["navy"] for b in badges], "BadgeNavy", C.NAVY, smooth_angle=40)
    mustard = pin + [b["rim"] for b in badges] + icon_cols.pop(C.CHEESE)
    C.part(mustard, "Mustard", C.MUSTARD, smooth_angle=40)
    C.part(icon_cols[C.BUN], "IconBun", C.BUN, smooth_angle=40)
    C.part(icon_cols[C.LETTUCE], "IconLettuce", C.LETTUCE, smooth_angle=40)
    C.part(icon_cols[C.TOMATO], "IconTomato", C.TOMATO, smooth_angle=40)

    # --- number badge (-X side, in front of the door) ---------------------------------
    ny, nz, ns_ = NUM
    rim = C.prism(C.rrect(ns_ + 0.24, ns_ + 0.24, 0.26, 2, ny, nz), "x", -HW - 0.06, -HW + 0.02)
    plate = C.prism(C.rrect(ns_, ns_, 0.16, 2, ny, nz), "x", -HW - 0.1, -HW - 0.04)
    ns.tag(plate, "NumberPlate", C.NAVY_DEEP, recolor="van_number", cast_shadow=False, smooth_angle=30)

    # --- glass: windshield (split), cab side windows, rear windows, bulkhead window ------
    glass = []
    a, b = (-7.0, 4.1), (-6.5, 6.6)
    d = (b[0] - a[0], b[1] - a[1])
    ln = math.hypot(*d)
    n = (-d[1] / ln, d[0] / ln)            # outward normal of the windshield line (-Y, +Z)
    quad = []
    for t, off in ((0.1, -0.02), (0.9, -0.02), (0.9, 0.05), (0.1, 0.05)):
        quad.append((a[0] + d[0] * t + n[0] * off, a[1] + d[1] * t + n[1] * off))
    for x0, x1 in ((-HW + 0.35, -0.13), (0.13, HW - 0.35)):
        g = C.prism(quad, "x", x0, x1)
        glass.append(g)
    side_win = C.fillet([(-6.62, 4.42), (-5.0, 4.42), (-5.0, 6.3), (-6.24, 6.3)], 0.14, 2)
    for sx in (-1, 1):
        a0, a1 = sorted((sx * (HW - 0.02), sx * (HW + 0.04)))
        glass.append(C.prism(side_win, "x", a0, a1))
    for sx in (-1, 1):
        glass.append(C.prism(C.rrect(2.2, 1.55, 0.18, 2, sx * 1.55, 5.45), "y", HL - 0.02, HL + 0.04))
    C.part(glass, "Glass", C.GLASS_DARK, "Glass", smooth_angle=30)

    # --- chrome: bumpers, grille surround, headlight rims, mirrors, hubcaps, rails ------
    chrome, dark = [], []
    for y, sgn in ((-HL - 0.12, -1), (HL + 0.12, 1)):
        chrome.append(ns.box((2 * HW + 0.2, 0.42, 0.55), loc=(0, y, 1.3), bevel=0.16, segments=1))
    chrome.append(C.ring_slab(C.rrect(2.7, 1.3, 0.22, 2, 0, 2.05), C.rrect(2.36, 0.98, 0.12, 2, 0, 2.05), "y",
                              -HL - 0.08, -HL + 0.02))
    for k in range(4):
        dark.append(ns.box((2.3, 0.06, 0.1), loc=(0, -HL - 0.02, 1.7 + k * 0.23), bevel=0.0))
    dark.append(ns.box((2.36, 0.04, 0.98), loc=(0, -HL + 0.01, 2.05), bevel=0.0))
    lamps = []
    for sx in (-1, 1):
        rimh = ns.cyl(0.56, 0.14, loc=(0, 0, 0), verts=12, radius_top=0.5, bevel=0.0)
        C.place(rimh, (sx * 2.45, -HL - 0.03, 2.15), pitch=90)
        chrome.append(rimh)
        lens = ns.cyl(0.44, 0.12, loc=(0, 0, 0), verts=12, radius_top=0.3, bevel=0.0)
        C.place(lens, (sx * 2.45, -HL - 0.13, 2.15), pitch=90)
        lamps.append(lens)
        # side mirror on a chrome arm
        chrome.append(C.rod((sx * (HW - 0.05), -6.55, 4.7), (sx * (HW + 0.55), -6.75, 5.0), 0.06, verts=6))
        dark.append(ns.box((0.22, 0.42, 0.85), loc=(sx * (HW + 0.62), -6.75, 5.15), bevel=0.0))
        # tail lights + rear door handles
        lamps_tail = ns.box((0.42, 0.08, 1.0), loc=(sx * (HW - 0.4), HL + 0.03, 2.05), bevel=0.05, segments=1)
        chrome.append(ns.box((0.42, 0.1, 0.12), loc=(sx * 0.4, HL + 0.06, 3.9), bevel=0.04, segments=1))
        ns.tag(lamps_tail, f"TailLight{'R' if sx < 0 else 'L'}", "#B3221E", cast_shadow=False, smooth_angle=40)
    ns.tag(C.merge(lamps, "Headlights"), "Headlights", "#F7F0D2", recolor="headlight", cast_shadow=False,
           smooth_angle=50)
    # rear door seam, wipers, cab door seams
    dark.append(ns.box((0.06, 0.05, 5.3), loc=(0, HL + 0.02, 4.0), bevel=0.0))
    # wipers rest on the windshield glass (they hovered 0.07-0.15 off the cowl): points along the windshield
    # line (-7.0, 4.1) -> (-6.5, 6.6) at fraction t, lifted to the glass face (+0.05) plus the rod radius
    ws_d = (0.5, 2.5)
    ws_n = (-2.5 / math.hypot(*ws_d), 0.5 / math.hypot(*ws_d))

    def on_glass(t, lift=0.08):
        return (-7.0 + ws_d[0] * t + ws_n[0] * lift, 4.1 + ws_d[1] * t + ws_n[1] * lift)
    for sx in (-1, 1):
        (y0w, z0w), (y1w, z1w) = on_glass(0.12), on_glass(0.17)
        dark.append(C.rod((sx * 0.3, y0w, z0w), (sx * 2.0, y1w, z1w), 0.04, verts=5))
        a0, a1 = sorted((sx * (HW - 0.01), sx * (HW + 0.03)))
        dark.append(ns.box((a1 - a0, 0.05, 3.3), loc=((a0 + a1) / 2, -4.9, 4.55), bevel=0.0))
    # door tracks (chrome) above and below the opening, + entry step + grab bar
    for z, y1 in ((DZ1 + 0.12, DOOR_OPEN_Y + 2.4), (1.42, AXLES[1] - WR - 0.45)):
        chrome.append(ns.box((0.08, y1 - DY0 + 0.3, 0.09), loc=(-HW - 0.05, (DY0 - 0.3 + y1) / 2, z),
                             bevel=0.02, segments=1))
    chrome.append(ns.box((0.75, DY1 - DY0 - 0.4, 0.12), loc=(-HW - 0.3, (DY0 + DY1) / 2, 0.95), bevel=0.04, segments=1))
    # roller brackets carrying the slid-open door on the tracks (the door hung 0.12 off the body side with
    # nothing joining them): body side -> door's inner face, track -> into the door edge
    for yb, z0, z1 in ((DOOR_OPEN_Y - 1.6, DZ1 - 0.15, DZ1 + 0.15), (DOOR_OPEN_Y + 1.6, DZ1 - 0.15, DZ1 + 0.15),
                       (DOOR_OPEN_Y - 1.75, 1.38, 1.75)):
        chrome.append(ns.box((0.15, 0.28, z1 - z0), loc=(-HW - 0.065, yb, (z0 + z1) / 2), bevel=0.02, segments=1))
    chrome.append(C.rod((-HW + 0.2, DY0 + 0.2, 2.4), (-HW + 0.2, DY0 + 0.2, 5.6), 0.06, verts=6))
    for zg in (2.55, 5.45):     # grab-bar standoffs into the front jamb (the bar stood 0.14 clear of everything)
        chrome.append(ns.box((0.1, 0.27, 0.12), loc=(-HW + 0.2, DY0 + 0.085, zg), bevel=0.02, segments=1))
    chrome.append(handle)
    chrome.append(rim)
    hubs, tires, walls, caps = [], [], [], []
    for y in AXLES:
        for sx in (-1, 1):
            t, w, h, c = wheel(sx * (HW - 0.48), y, sx)
            tires.append(t)
            walls.append(w)
            hubs.append(h)
            caps.append(c)
    chrome += hubs
    chrome.append(ns.box((1.3, 1.5, 0.3), loc=(0, 4.2, ROOF + 0.12), bevel=0.1, segments=1))         # roof vent
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    under = ns.box((2 * HW - 1.2, 2 * HL - 1.2, 0.5), loc=(0, 0, 0.78), bevel=0.05, segments=1)
    C.part(tires + [under] + [o for o in dark if o is not None], "Rubber", C.RUBBER, smooth_angle=45)
    C.part(walls, "Whitewall", C.CREAM, smooth_angle=45)
    C.part(caps, "HubCaps", C.BRAND, smooth_angle=45)

    # --- roof light bar ----------------------------------------------------------------
    base = ns.box((5.0, 0.7, 0.16), loc=(0, -5.15, ROOF + 0.06), bevel=0.05, segments=1)
    C.part([base], "LightBarBase", C.STEEL, "Metal", smooth_angle=40)
    pods = []
    for i in range(5):
        x = -2.0 + i * 1.0
        pods.append(ns.box((0.78, 0.56, 0.34), loc=(x, -5.15, ROOF + 0.3), bevel=0.12, segments=1))
    ns.tag(C.merge(pods, "Lights"), "Lights", C.MUSTARD, "Neon", recolor="van_lights", cast_shadow=False,
           smooth_angle=50)

    # --- interior: lining, diamond-plate floor, benches, dome light ---------------------
    lin = [ns.box((0.04, HL - 0.4 + 4.15, 6.65 - FLOOR - 0.1), loc=(HW - 0.32, (-4.15 + HL - 0.4) / 2, (FLOOR + 6.62) / 2),
                  bevel=0.0),
           ns.box((2 * HW - 0.66, 0.04, 6.65 - FLOOR - 0.1), loc=(0, -4.17, (FLOOR + 6.62) / 2), bevel=0.0),
           ns.box((2 * HW - 0.66, HL + 4.15 - 0.4, 0.04), loc=(0, (-4.15 + HL - 0.4) / 2, 6.67), bevel=0.0)]
    C.part(lin, "Lining", LINING, smooth_angle=30)
    fl = ns.box((2 * HW - 0.64, HL + 4.15 - 0.4, 0.07), loc=(0, (-4.15 + HL - 0.4) / 2, FLOOR + 0.045), bevel=0.0)
    C.part([fl], "CargoFloor", FLOOR_COL, "DiamondPlate", smooth_angle=30)
    vinyl, frames = [], []
    for yc in ROWS:
        for x in SEAT_X:
            vinyl.append(ns.box((2.5, 1.45, 0.42), loc=(x, yc, SEAT_Z - 0.21), bevel=0.16, segments=1))
            # backrest seated into the cushion (its bevelled foot hovered ~0.03 above it)
            vinyl.append(ns.box((2.5, 0.38, 2.1), loc=(x, yc + 0.82, SEAT_Z + 0.94), rot=(-8, 0, 0), bevel=0.16,
                                segments=1))
        frames.append(ns.box((5.3, 1.2, SEAT_Z - 0.42 - FLOOR), loc=(0, yc + 0.05, (FLOOR + SEAT_Z - 0.42) / 2 + 0.04),
                             bevel=0.05, segments=1))
        frames.append(C.rod((-2.7, yc + 1.05, SEAT_Z + 2.15), (2.7, yc + 1.05, SEAT_Z + 2.15), 0.07, verts=8))
        for xr in (-2.3, -0.45, 0.45, 2.3):     # grab-rail posts down into the backrests (the rail floated)
            frames.append(C.rod((xr, yc + 0.97, SEAT_Z + 1.8), (xr, yc + 1.05, SEAT_Z + 2.15), 0.045, verts=6))
    C.part(vinyl, "Seats", SEAT_RED, smooth_angle=50)
    C.part(frames, "SeatFrames", C.STEEL, "Metal", smooth_angle=40)
    dome = ns.cyl(0.45, 0.12, loc=(0, -0.4, 6.6), verts=10, bevel=0.0)
    ns.tag(dome, "DomeLight", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=50)


def sockets():
    s = {}
    k = 1
    for yc in ROWS:
        for x in SEAT_X:
            s[f"Seat{k}"] = ((x, yc - 0.05, SEAT_Z), 0.0)
            k += 1
    s["Pad"] = ((C.VAN_PAD[0], C.VAN_PAD[1], 0.0), 90.0)
    s["Door"] = ((-HW, C.VAN_DOOR_YC, (DZ0 + DZ1) / 2), -90.0)
    s["NumberPlate"] = ((-HW - 0.1, NUM[0], NUM[1]), -90.0)
    return s


META = {
    "front": "-Y (LookVector)", "door_side": "Blender -X = Roblox +X (the van's right / curb side)",
    "seat_height": SEAT_Z, "seat_order": "1 front-door, 2 front-far, 3 rear-door, 4 rear-far; all face front",
    "door_opening": {"width": DY1 - DY0, "height": round(DZ1 - DZ0, 2), "sill": DZ0},
    "number_size": [NUM[2], NUM[2]],
    "surfaces": [{"part": "NumberPlate", "face": "Right", "screen_size": [NUM[2], NUM[2]]}],
    "pad_radius": 1.8,
    "roles": {"van_paint": "Body (body + open sliding door)", "van_number": "NumberPlate",
              "van_lights": "Lights (roof light bar, Neon)", "lamp": "DomeLight", "headlight": "Headlights"},
    "paint_variants": ["#F3EEE2", "#F6D9A8", "#D9E6EC", "#F2C9C0"],
    "light_hint": {"DomeLight": {"type": "PointLight", "color": C.LAMP_WARM, "range": 10, "brightness": 1.2}},
}

if __name__ == "__main__":
    C.run(build, "Lobby_ShiftVan", meta=META, sockets=sockets(), socket_views=((-80, 22), (-30, 50)), pivot=(0, 0, 0))
