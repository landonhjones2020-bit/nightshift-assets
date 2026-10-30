"""Shop_PunchClock — the "clock in" time recorder with its time-card rack, back hall.

Left: a rounded steel-blue time clock — chrome-bezel dial (cream face, ticks, black hour /
minute hands, red second hand), a dark date window, a red-orange IN/OUT button, a mustard
name plate and a time card pushed half into the slot on top. Right: a stainless card rack
with eight slanted pockets, each holding a manila card with a coloured stripe.
Wall-mounted: pivot = bottom-centre of the back face (+Y, touches the wall). 1.6 x 2.4 x 0.7.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
BODY = "#55636F"
MANILA = "#E9DDBF"
CX, CW = -0.36, 0.86          # clock body centre x / width
CZ0, CZ1 = 0.7, 2.04          # clock body bottom / top
CD = 0.62                     # clock depth
RX, RW = 0.52, 0.5            # rack centre x / width
H = 2.4


def build():
    fy = -CD
    body = ns.box((CW, CD, CZ1 - CZ0), loc=(CX, -CD / 2, (CZ0 + CZ1) / 2), bevel=0.09, segments=2)
    C.part([body], "Body", BODY, smooth_angle=40)

    # dial: chrome bezel, cream face, ticks, hands (11:52)
    dz = CZ1 - 0.44
    bezel = ns.cyl(0.34, 0.07, loc=(CX, fy - 0.02, dz), rot=(90, 0, 0), verts=14, bevel=0.0)
    face = C.face_dir(C.disc(0.29, loc=(0, 0, 0), verts=14), "+Z")
    face.rotation_euler = (math.radians(90), 0, 0)
    face.location = (CX, fy - 0.066, dz)
    ns.apply_all(face)
    C.face_dir(face, "-Y")
    ticks, hands = [], []
    for k in range(12):
        a = math.radians(k * 30)
        r0, r1 = (0.2, 0.26) if k % 3 else (0.17, 0.26)
        w = 0.035 if k % 3 == 0 else 0.022
        ticks.append(C.strip_xz((CX + r0 * math.sin(a), dz + r0 * math.cos(a)), (CX + r1 * math.sin(a), dz + r1 * math.cos(a)),
                                w, fy - 0.074))
    for ang, ln, w in ((356, 0.15, 0.045), (312, 0.23, 0.032)):
        a = math.radians(ang)
        hands.append(C.strip_xz((CX - 0.03 * math.sin(a), dz - 0.03 * math.cos(a)), (CX + ln * math.sin(a), dz + ln * math.cos(a)),
                                w, fy - 0.082))
    a = math.radians(150)
    sec = [C.strip_xz((CX - 0.05 * math.sin(a), dz - 0.05 * math.cos(a)), (CX + 0.25 * math.sin(a), dz + 0.25 * math.cos(a)),
                      0.014, fy - 0.09)]
    cap = ns.cyl(0.03, 0.03, loc=(CX, fy - 0.09, dz), rot=(90, 0, 0), verts=6, bevel=0.0)
    C.part([bezel], "Bezel", C.CHROME, "Metal", smooth_angle=50)
    C.part([face], "Face", C.PAPER, smooth_angle=None)
    C.part(ticks + hands + [cap], "Hands", C.INK, smooth_angle=None)
    C.part(sec, "SecondHand", "#D9342B", smooth_angle=None)

    # lower front: date window, IN/OUT button, name plate
    wz = CZ0 + 0.42
    win = [C.quad_xz(CX - 0.28, CX + 0.08, wz - 0.08, wz + 0.08, fy - 0.004)]
    digits = [C.quad_xz(CX - 0.24 + 0.085 * k, CX - 0.19 + 0.085 * k, wz - 0.04, wz + 0.04, fy - 0.01) for k in range(4)]
    btn = ns.cyl(0.075, 0.08, loc=(CX + 0.24, fy - 0.03, wz), rot=(90, 0, 0), verts=10, bevel=0.0)
    plate = ns.box((0.44, 0.02, 0.12), loc=(CX, fy - 0.01, CZ0 + 0.17), bevel=0.0)
    C.part(win, "Window", "#17191D", smooth_angle=None)
    C.part(digits, "Digits", "#F2B33D", smooth_angle=None)
    C.part([btn], "Button", C.BRAND, smooth_angle=50)
    C.part([plate], "Plate", C.MUSTARD, smooth_angle=None)

    # card slot on top + a card pushed half in
    slot = ns.box((0.46, 0.06, 0.012), loc=(CX, -CD * 0.52, CZ1 + 0.002), bevel=0.0)
    C.part([slot], "Slot", "#17191D", smooth_angle=None)
    card_in = ns.box((0.36, 0.02, 0.5), loc=(CX, -CD * 0.52, CZ1 + 0.15), rot=(6, 0, 0), bevel=0.0)
    slot_stripe = ns.box((0.32, 0.006, 0.06), loc=(CX, -CD * 0.52 - 0.012 - 0.33 * math.sin(math.radians(6)), CZ1 + 0.33),
                         rot=(6, 0, 0), bevel=0.0)

    # card rack: back plate, side rails, eight slanted pockets with cards
    rack, cards, stripes = [], [card_in], {"#C9584C": [], "#4E7FB8": [], "#3E8A4F": []}
    rack.append(ns.box((RW, 0.04, H), loc=(RX, -0.02, H / 2), bevel=0.015, segments=1))
    for sx in (-1, 1):
        rack.append(ns.box((0.03, 0.12, H - 0.06), loc=(RX + sx * (RW / 2 - 0.015), -0.08, H / 2), bevel=0.0))
    n = 8
    pitch = (H - 0.12) / n
    cols = list(stripes)
    stripes["#C9584C"].append(slot_stripe)
    for k in range(n):
        z0 = 0.06 + k * pitch
        rack.append(ns.box((RW - 0.04, 0.025, 0.13), loc=(RX, -0.125, z0 + 0.065), rot=(-14, 0, 0), bevel=0.0))
        tilt = (-2, 3, -4, 2, 0, -3, 4, -1)[k]
        if k == 5:
            continue          # one empty pocket (someone is on shift)
        ch = 0.38
        # card + its stripe built around the card's bottom edge, tilted in the wall plane, then
        # leaned FORWARD out of its pocket so the top shows in front of the pocket above
        card = ns.box((0.34, 0.012, ch), loc=(0, 0, ch / 2), bevel=0.0)
        st = ns.box((0.3, 0.004, 0.06), loc=(0, -0.008, ch - 0.07), bevel=0.0)
        C.turn_y([card, st], tilt, 0, 0)
        C.place([card, st], loc=(RX + 0.01 * tilt, -0.085, z0 + 0.02), pitch=16)
        cards.append(card)
        stripes[cols[k % 3]].append(st)
    C.part(rack, "Rack", C.STAINLESS, "Metal", smooth_angle=40)
    C.part(cards, "Cards", MANILA, smooth_angle=None)
    for col, objs in stripes.items():
        C.part(objs, "Stripe" + col.lstrip("#"), col, smooth_angle=None)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)", "time_shown": "11:52"}

if __name__ == "__main__":
    C.run(build, "Shop_PunchClock", mount="wall", budget=800, meta=META)
