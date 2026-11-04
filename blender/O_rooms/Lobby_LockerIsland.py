"""Lobby_LockerIsland — free-standing double-sided staff locker island (10 W x 7 H x 3 D).

A dark-red carcass spine (the Lobby_LockerBank family) carrying six red-orange lockers on EACH
long side (Doors, role "locker_door"): louvre vents top and bottom, a brushed-steel name-plate
holder with a cream name card on every door, chrome lift latches. Brushed-steel end panels with
a cream STACKHOUSE mark, a gabled top cap over a mustard pinstripe band, a black kick plinth.
A built-in maple slat bench runs along each long side on red-orange steel gusset brackets; a
folded cream towel lies on the front bench and a mustard gym bag on the back one.

Front = -Y (the back side mirrors it, facing +Y), pivot = bottom-centre. Collides (carcass,
cap, end panels, plinth, doors, benches). Sockets Seat1..Seat3 = front bench seat points left
to right as seen from the front (yaw 0); Seat4..Seat6 = back bench seat points left to right as
seen from the back (yaw 180).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 10.0, 7.0, 3.0
CX = 4.7                    # carcass half width (steel end panels outside it, to 4.88; logos to 5.0)
EX = 4.88                   # end panel outer face
CY = 0.72                   # carcass half depth (locker faces)
Z_PL = 0.32                 # kick plinth top
Z_TOP = 6.7                 # carcass top
CAP_Z = 6.68                # cap underside / end panel top
N = 6                       # lockers per side
LW = 2 * CX / N             # locker pitch 1.6
DOOR_Z = (1.72, 6.42)
DT = 0.08                   # door thickness
FY = CY + DT                # door front plane (abs y) 0.80
SEAT = 1.5                  # bench seat top
SLAT_T = 0.16
BENCH_Y = (D / 2, CY + 0.04)   # bench outer edge .. inner edge (abs y)
BRACKET_X = (-3.9, -1.3, 1.3, 3.9)
SEATS_X = (-3.2, 0.0, 3.0)


def side(s, g):
    """Lockers + bench on one long side. s = -1 front (faces -Y), +1 back (faces +Y)."""
    face = "-Y" if s < 0 else "+Y"
    for i in range(N):
        x0 = -CX + i * LW
        xc = x0 + LW / 2
        dw = LW - 0.08
        z0, z1 = DOOR_Z
        g["doors"].append(ns.box((dw, DT, z1 - z0), loc=(xc, s * (CY + DT / 2), (z0 + z1) / 2), bevel=0.03, segments=1))
        y = s * (FY + 0.012)
        for zt in (z1 - 0.3, z0 + 0.66):          # louvre groups (4 slats each)
            for k in range(4):
                z = zt - k * 0.13
                g["vents"].append(C.face_dir(C.quad_xz(xc - dw / 2 + 0.25, xc + dw / 2 - 0.25, z - 0.035, z + 0.035, y), face))
        # name-plate holder (brushed steel) + cream card + name scribble
        pz = 5.32
        g["steel"].append(ns.box((0.86, 0.04, 0.32), loc=(xc, s * (FY + 0.015), pz), bevel=0.0))
        g["cards"].append(C.face_dir(C.quad_xz(xc - 0.37, xc + 0.37, pz - 0.11, pz + 0.11, s * (FY + 0.046)), face))
        ln = (0.46, 0.34, 0.52, 0.4, 0.3, 0.44)[(i + (0 if s < 0 else 3)) % 6]
        g["ink"].append(C.face_dir(C.quad_xz(xc - ln / 2, xc + ln / 2, pz - 0.025, pz + 0.025, s * (FY + 0.056)), face))
        # chrome lift latch on the free (left) edge of the door, as seen from its own side
        lx = xc + (-(dw / 2) + 0.22) * (1 if s < 0 else -1)
        latch = C.prism(C.rrect(0.15, 0.58, 0.05, 1, lx, 3.55), "y", s * (FY - 0.01), s * (FY + 0.075))
        g["chrome"].append(latch)
    # bench: two maple slats on red-orange gusset brackets
    yo, yi = BENCH_Y
    mid = (yo + yi) / 2
    for a, b in ((yo, mid + 0.025), (mid - 0.025, yi)):
        lo_, hi_ = sorted((a, b))
        g["slats"].append(ns.box((2 * CX - 0.02, hi_ - lo_, SLAT_T), loc=(0, s * (lo_ + hi_) / 2, SEAT - SLAT_T / 2),
                                 bevel=0.05, segments=1))
    g["brackets"].append(ns.box((2 * CX - 0.02, 0.07, 0.2), loc=(0, s * (yo - 0.13), SEAT - SLAT_T - 0.115), bevel=0.02,
                                segments=1))
    for x in BRACKET_X:
        prof = [(s * (CY - 0.02), SEAT - SLAT_T + 0.01), (s * (yo - 0.14), SEAT - SLAT_T + 0.01),
                (s * (yo - 0.14), SEAT - SLAT_T - 0.13), (s * (CY + 0.14), 0.62), (s * (CY - 0.02), 0.62)]
        br = C.prism(prof, "x", x - 0.07, x + 0.07)
        g["brackets"].append(br)


def build():
    g = {k: [] for k in ("doors", "vents", "steel", "cards", "ink", "chrome", "slats", "brackets")}
    carcass = ns.box((2 * CX, 2 * CY, Z_TOP - Z_PL + 0.02), loc=(0, 0, (Z_PL - 0.02 + Z_TOP) / 2), bevel=0.04, segments=1)
    cap = C.prism(C.fillet([(-0.92, CAP_Z), (0.92, CAP_Z), (0.92, CAP_Z + 0.1), (0.0, H), (-0.92, CAP_Z + 0.1)],
                           [0.02, 0.02, 0.04, 0.06, 0.04], 1), "x", -EX - 0.06, EX + 0.06)
    ns.bevel(cap, width=0.03, segments=1)
    C.part([carcass, cap], "Carcass", C.LOCKER_DARK, can_collide=True, smooth_angle=40)
    plinth = ns.box((2 * CX - 0.1, 2 * CY - 0.24, Z_PL), loc=(0, 0, Z_PL / 2), bevel=0.03, segments=1)
    C.part([plinth], "Plinth", C.BLACK, can_collide=True, smooth_angle=40)
    for sx in (-1, 1):   # brushed-steel end panels, full height up to the cap
        g["steel"].append(ns.box((EX - CX, 2 * (FY + 0.04), CAP_Z), loc=(sx * (CX + (EX - CX) / 2), 0, CAP_Z / 2),
                                 bevel=0.05, segments=1))
    end_panels = g["steel"][-2:]
    del g["steel"][-2:]
    C.part(end_panels, "EndPanels", C.STEEL, "Metal", can_collide=True, smooth_angle=40)
    band = []
    for s in (-1, 1):    # mustard pinstripe band under the cap
        band.append(ns.box((2 * CX, 0.05, 0.14), loc=(0, s * (CY + 0.02), 6.55), bevel=0.0))
    C.part(band, "Band", C.MUSTARD, smooth_angle=None)

    side(-1, g)
    side(1, g)
    C.part(g["doors"], "Doors", C.LOCKER_RED, recolor="locker_door", can_collide=True, smooth_angle=40)
    C.part(g["vents"], "Vents", C.VENT, smooth_angle=None)
    C.part(g["steel"], "Plates", C.STEEL, "Metal", smooth_angle=40)
    C.part(g["cards"], "Cards", C.CREAM, smooth_angle=None)
    C.part(g["ink"], "Names", C.NAVY, smooth_angle=None)
    C.part(g["chrome"], "Latches", C.CHROME, "Metal", smooth_angle=45)
    C.part(g["slats"], "Benches", C.MAPLE, "Wood", can_collide=True, smooth_angle=40)
    C.part(g["brackets"], "Brackets", C.BRAND, "Metal", can_collide=True, smooth_angle=40)

    # STACKHOUSE marks on the end panels
    logos = {}
    for sx, yaw in ((1, 90.0), (-1, -90.0)):
        C.merge_into(logos, C.mini_logo((sx * EX, 0, 4.4), r=0.55, yaw=yaw, depth=0.06, disc=C.CREAM))
    C.parts_by_colour(logos, "Logo", smooth_angle=None)

    # folded towel (front bench, right end) + mustard gym bag (back bench)
    ty = -(BENCH_Y[0] + BENCH_Y[1]) / 2
    towel = ns.box((0.95, 0.62, 0.22), loc=(3.95, ty, SEAT + 0.11), rot=(0, 0, -8), bevel=0.08, segments=2)
    C.part([towel], "Towel", C.TOWEL, "Fabric", smooth_angle=50)
    stripe = ns.box((0.16, 0.66, 0.24), loc=(4.2, ty - 0.035, SEAT + 0.11), rot=(0, 0, -8), bevel=0.04, segments=1)
    C.part([stripe], "TowelStripe", C.BRAND, "Fabric", smooth_angle=50)
    by = (BENCH_Y[0] + BENCH_Y[1]) / 2
    bag = ns.cyl(0.27, 1.15, loc=(-3.4, by, SEAT + 0.26), rot=(0, 90, 6), verts=10, bevel=0.12, segments=2)
    straps = C.pipe([(-3.75, by - 0.18, SEAT + 0.45), (-3.62, by - 0.05, SEAT + 0.78), (-3.18, by - 0.05, SEAT + 0.8),
                     (-3.05, by - 0.18, SEAT + 0.46)], 0.035, sides=4)
    C.part([bag], "GymBag", C.MUSTARD, "Fabric", smooth_angle=50)
    C.part([straps], "BagStraps", C.NAVY, "Fabric", smooth_angle=50)


def sockets():
    yb = (BENCH_Y[0] + BENCH_Y[1]) / 2
    s = {}
    for i, x in enumerate(SEATS_X):
        s[f"Seat{i + 1}"] = ((x, -yb, SEAT), 0.0)
    for i, x in enumerate(SEATS_X):          # back side, left to right as seen from the back
        s[f"Seat{i + 4}"] = ((-x, yb, SEAT), 180.0)
    return s


META = {"lockers_per_side": N, "seat_height": SEAT, "double_sided": True,
        "seat_order": "Seat1..3 front bench left->right (front view, yaw 0); Seat4..6 back bench left->right "
                      "(as seen from the back, yaw 180)",
        "roles": {"locker_door": "Doors (all twelve)"}}

if __name__ == "__main__":
    C.run(build, "Lobby_LockerIsland", sockets=sockets(), budget=3000, meta=META)
