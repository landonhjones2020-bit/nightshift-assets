"""Basement_Boiler — the old cast-iron boiler in the basement corner.

A squat cast-iron firebox base on four stubby feet carries a tall round boiler drum in dull
green paint with a domed top. Rusty riveted seam bands ring the drum (bottom, middle,
top), rust streaks run down from them. On the front: two brass pressure gauges on stalks
(cream dials, black needles, red zones), a riveted furnace door with hinges, a latch
handle and a barred window glowing orange (part Glow, Neon, role "glow" - the game can
pulse or kill it), and a row of glowing ash-pit vents under it. Two thick pipes rise from the
drum to the 11-stud ceiling: a fat iron flue with collars and a steam riser with flanges, a
valve body and a red hand wheel; ceiling collars where they meet the ceiling. Base, drum and flue collide.
Front faces -Y, pivot = bottom-centre. 5 x 11 x 5 (drum 8 tall + pipes to the ceiling).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
R = 2.2                       # drum radius
BASE_W, BASE_Z0, BASE_Z1 = 4.6, 0.22, 2.1
DRUM_Z0, DRUM_Z1 = 2.05, 6.4
SEAMS = (2.35, 4.3, 6.2)      # seam band centres
TOP = C.CEILING
FRONT = -BASE_W / 2           # base front face y


def drum_y(x):
    """Front surface y of the drum at x."""
    return -math.sqrt(max(R * R - x * x, 0.0))


def build():
    # ---- drum: cylinder + dome (one lathe), painted green ----------------------------
    prof = [(R - 0.05, DRUM_Z0), (R, DRUM_Z0 + 0.1), (R, DRUM_Z1), (R - 0.08, DRUM_Z1 + 0.42),
            (R - 0.36, DRUM_Z1 + 0.85), (R - 0.85, DRUM_Z1 + 1.17), (R - 1.5, DRUM_Z1 + 1.36), (0.0, DRUM_Z1 + 1.42)]
    drum = ns.lathe(prof, verts=16)
    C.part([drum], "Drum", C.GREEN, can_collide=True, smooth_angle=50)

    # ---- seam bands + rivets (rust) -----------------------------------------------------
    bands, rivets = [], []
    for k, z in enumerate(SEAMS):
        bands.append(ns.cyl(R + 0.06, 0.24, loc=(0, 0, z), verts=16, bevel=0.0))
        if k:   # rivet heads on the middle and top seams (the bottom one hides behind the gauges' sightline)
            rivets += C.rivet_ring(0, 0, R + 0.06, z, 10, a0=18.0 * (k % 2), rr=0.065)
    # manhole boss on the dome
    boss = ns.cyl(0.55, 0.42, loc=(-0.55, 0.6, DRUM_Z1 + 1.29), verts=8, bevel=0.0)   # top 0.1 above the crown
    C.part(bands + [boss], "Bands", C.RUST, "Metal", smooth_angle=40)
    C.part(rivets, "Rivets", "#8A6A48", "Metal", smooth_angle=60)

    # ---- cast-iron firebox base on feet, furnace door, vents ---------------------------
    base = ns.box((BASE_W, BASE_W, BASE_Z1 - BASE_Z0), loc=(0, 0, (BASE_Z0 + BASE_Z1) / 2), bevel=0.12, segments=1)
    lip = ns.box((BASE_W + 0.14, BASE_W + 0.14, 0.14), loc=(0, 0, BASE_Z1 - 0.02), bevel=0.05, segments=1)
    feet = [ns.cyl(0.3, BASE_Z0 + 0.04, loc=(sx * 1.85, sy * 1.85, (BASE_Z0 + 0.04) / 2), verts=6,
                   radius_top=0.22, bevel=0.0) for sx in (-1, 1) for sy in (-1, 1)]
    C.part([base, lip] + feet, "Base", C.IRON, "Metal", can_collide=True, smooth_angle=40)

    fy = FRONT
    door_zc, door_w, door_h = 1.3, 2.3, 1.22
    door = C.slab(C.rrect(door_w, door_h, 0.14, 2, 0, door_zc), 0.08, axis="y", at=fy - 0.07, bevel=0.0)
    win_z, win_w, win_h = door_zc + 0.06, 1.3, 0.48
    frame = C.ring_slab(C.rrect(win_w + 0.24, win_h + 0.2, 0.08, 1, 0, win_z), C.rrect(win_w, win_h, 0.04, 1, 0, win_z),
                        "y", fy - 0.13, fy - 0.06)
    bars = [ns.box((0.06, 0.05, win_h + 0.02), loc=(x, fy - 0.1, win_z), bevel=0.0) for x in (-0.39, -0.13, 0.13, 0.39)]
    hinges = [ns.cyl(0.07, 0.3, loc=(-door_w / 2 - 0.03, fy - 0.07, door_zc + dz), verts=6, bevel=0.0)
              for dz in (-0.36, 0.36)]
    hx_ = door_w / 2 - 0.22
    latch = [C.rod((hx_, fy - 0.1, door_zc - 0.3), (hx_, fy - 0.28, door_zc - 0.3), 0.045, verts=6),
             C.rod((hx_, fy - 0.28, door_zc - 0.3), (hx_ - 0.42, fy - 0.28, door_zc - 0.4), 0.05, verts=6)]
    vent_plate = ns.box((1.5, 0.05, 0.3), loc=(0, fy - 0.02, 0.45), bevel=0.0)
    vent_bars = [ns.box((1.42, 0.04, 0.04), loc=(0, fy - 0.085, 0.45 + dz), bevel=0.0) for dz in (-0.05, 0.05)]
    C.part([door, frame] + bars + hinges + latch + [vent_plate] + vent_bars,
           "Door", "#33353A", "Metal", smooth_angle=40)
    rivets_door = [C.rivet((x, fy - 0.07, z), (0, -1, 0), r=0.05)
                   for x in (-0.95, 0.95) for z in (door_zc - 0.44, door_zc + 0.44)]
    C.part(rivets_door, "DoorRivets", "#8A6A48", "Metal", smooth_angle=60)
    # glowing fire behind the window bars and the vent slats (0.012 proud of their plates)
    glow = [ns.box((win_w, 0.02, win_h), loc=(0, fy - 0.075, win_z), bevel=0.0),
            ns.box((1.3, 0.02, 0.22), loc=(0, fy - 0.056, 0.45), bevel=0.0)]
    C.part(glow, "Glow", C.GLOW, "Neon", recolor="glow", cast_shadow=False, smooth_angle=None)

    # ---- pressure gauges on the drum front ------------------------------------------------
    parts = {"bezel": [], "face": [], "ink": [], "red": [], "stalk": []}
    for x, deg, zz in ((-0.72, 35.0, 5.25), (0.72, -20.0, 5.25)):
        y0 = drum_y(x)
        g = C.gauge((x, y0 - 0.36, zz), (0, -1, 0), r=0.4, stalk=0.22, needle_deg=deg, verts=10)
        for k, v in g.items():
            parts[k] += v
    C.part(parts["bezel"], "GaugeBezels", C.BRASS, "Metal", smooth_angle=45)
    C.part(parts["face"], "GaugeFaces", C.CREAM, smooth_angle=None)
    C.part(parts["ink"], "GaugeInk", C.INK, smooth_angle=None)
    C.part(parts["red"], "GaugeRed", C.BRAND, smooth_angle=None)

    # ---- pipes to the ceiling -------------------------------------------------------------
    iron = []
    # fat flue from the dome's back up to the ceiling, two collars + ceiling thimble
    fx, fy_ = 0.55, 0.85
    iron.append(ns.cyl(0.42, TOP - 0.05 - 7.4, loc=(fx, fy_, (TOP - 0.05 + 7.4) / 2), verts=10, bevel=0.0))
    for z in (8.3, 9.7):
        iron.append(ns.cyl(0.48, 0.18, loc=(fx, fy_, z), verts=10, bevel=0.0))
    iron.append(ns.cyl(0.6, 0.2, loc=(fx, fy_, TOP - 0.1), verts=10, radius_top=0.68, bevel=0.0))
    C.part(iron, "Flue", C.IRON, "Metal", can_collide=True, smooth_angle=45)
    # steam riser (front-left) with two flanges, a gate valve body and a red hand wheel
    sx_, sy_ = -1.0, -0.55
    steel = [C.pipe([(sx_, sy_, 7.55), (sx_, sy_, TOP - 0.05)], 0.24, sides=8),
             ns.cyl(0.38, 0.1, loc=(sx_, sy_, 8.35), verts=8, bevel=0.0),
             ns.cyl(0.38, 0.1, loc=(sx_, sy_, 9.25), verts=8, bevel=0.0),
             ns.cyl(0.34, 0.6, loc=(sx_, sy_, 8.8), verts=8, bevel=0.04, segments=1),
             ns.cyl(0.36, 0.12, loc=(sx_, sy_, TOP - 0.06), verts=8, bevel=0.0)]
    stem = C.rod((sx_, sy_ - 0.3, 8.8), (sx_, sy_ - 0.66, 8.8), 0.05, verts=6)
    C.part(steel + [stem], "Pipes", C.CONCRETE_DARK, "Metal", smooth_angle=45)
    wheel = C.handwheel((sx_, sy_ - 0.7, 8.8), (0, -1, 0), r=0.38)
    C.part(wheel, "Valve", C.VALVE_RED, smooth_angle=45)

    # ---- rust streaks down the drum and the base front ---------------------------------
    streaks = []
    for k, (ang, z, ln) in enumerate(((-28, SEAMS[2] - 0.12, 1.2), (24, SEAMS[2] - 0.12, 0.8), (62, SEAMS[1] - 0.12, 1.0),
                                       (-70, SEAMS[1] - 0.12, 1.3), (160, SEAMS[2] - 0.12, 1.1), (-140, SEAMS[1] - 0.12, 0.9))):
        streaks.append(C.streak_cyl(0, 0, R, ang, z, ln, 0.16, seed=k))
    for k, (x, ln) in enumerate(((-1.25, 0.7), (1.35, 0.55))):
        streaks.append(C.streak_flat(x, BASE_Z1 - 0.12, ln, 0.14, fy, seed=10 + k))
    C.part(streaks, "Rust", C.RUST_DARK, smooth_angle=None)


META = {"size_note": "drum + base 5 x 8 x 5; pipes reach the 11-stud ceiling", "glow_part": "Glow",
        "light_hint": {"type": "PointLight", "socket": "FireGlow", "color": C.GLOW, "range": 10, "brightness": 1.2},
        "collide": "base, drum, flue"}
SOCKETS = {"FireGlow": ((0, FRONT - 0.6, 1.36), 0.0)}

if __name__ == "__main__":
    C.run(build, "Basement_Boiler", sockets=SOCKETS, budget=2000, meta=META)
