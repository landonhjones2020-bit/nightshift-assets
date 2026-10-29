"""Lobby_Bench — locker-room bench (6 long x 1.5 wide, seat height 1.6).

Three rounded maple slats on two red-orange steel pedestals (round post, flat foot plate,
T-bracket under the slats), chrome bolt caps, and a folded cream towel with a red-orange
stripe on one end. Collides.

Front = -Y (players sit facing -Y or straddle it), pivot = bottom-centre.
Sockets: Seat1 / Seat2 (seat surface, facing front), at x = -1.25 / +1.0 (Blender; the towel
sits on the +X end).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L, WD, SEAT = 6.0, 1.5, 1.6
MAPLE = "#C8955F"
TOWEL = "#F1EBDD"


def build():
    slats = []
    for k in range(3):
        y = -WD / 2 + 0.25 + k * 0.5
        slats.append(ns.box((L, 0.44, 0.16), loc=(0, y, SEAT - 0.08), bevel=0.06, segments=1))
    C.part(slats, "Slats", MAPLE, "Wood", can_collide=True, smooth_angle=40)
    steel, chrome = [], []
    for sx in (-1, 1):
        x = sx * (L / 2 - 0.9)
        steel.append(ns.cyl(0.13, SEAT - 0.3, loc=(x, 0, (SEAT - 0.3) / 2 + 0.05), verts=10, bevel=0.0))
        steel.append(ns.box((0.5, 1.2, 0.08), loc=(x, 0, 0.04), bevel=0.03, segments=1))
        steel.append(ns.box((0.24, WD - 0.1, 0.1), loc=(x, 0, SEAT - 0.21), bevel=0.03, segments=1))
        for sy in (-1, 1):
            chrome.append(ns.cyl(0.07, 0.05, loc=(x, sy * 0.45, 0.1), verts=6, bevel=0.0))
    C.part(steel, "Pedestals", C.BRAND, "Metal", can_collide=True, smooth_angle=40)
    C.part(chrome, "Bolts", C.CHROME, "Metal", smooth_angle=50)
    towel = ns.box((0.9, 0.95, 0.24), loc=(2.15, 0.05, SEAT + 0.12), rot=(0, 0, -10), bevel=0.09, segments=2)
    C.part([towel], "Towel", TOWEL, "Fabric", smooth_angle=50)
    stripe = ns.box((0.16, 0.99, 0.25), loc=(2.42, 0.0, SEAT + 0.12), rot=(0, 0, -10), bevel=0.05, segments=1)
    C.part([stripe], "TowelStripe", C.BRAND, "Fabric", smooth_angle=50)


SOCKETS = {"Seat1": ((-1.25, 0, SEAT), 0.0), "Seat2": ((1.0, 0, SEAT), 0.0)}
META = {"seat_height": SEAT, "seats": 2}

if __name__ == "__main__":
    C.run(build, "Lobby_Bench", sockets=SOCKETS, meta=META)
