"""Lobby_HQSign — the big "STACKHOUSE HQ" roof sign (20 wide x ~9 tall).

Navy backing board with a chrome rim on two steel roof trusses. Modelled neon lettering:
"STACKHOUSE" in red-orange (Letters) and "HQ" in cyan (LettersHQ) inside a mustard neon
ring (Ring); all three are Neon with role "neon". Warm marquee bulbs run along the top and
bottom edges (Bulbs, Neon, role "marquee": code can chase / twinkle them).

Front = -Y (faces the parking lot), pivot = on the roof plane directly under the centre of
the board face (the trusses run 3 studs back from there). Socket Glow = in front of the board centre (attach the sign's light).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H = 20.0, 4.6
BZ0 = 4.0                    # board bottom
ZC = BZ0 + H / 2
BT = 0.5                     # board thickness (y -0.25 .. 0.25)
FY = -BT / 2
NEON_RED = "#FF6A3D"
TX = (-W / 2 + 0.8, 0.0)     # x span reserved for the badge on the right
HQ_X = W / 2 - 2.35


def build():
    board = C.prism(C.rrect(W, H, 0.6, 3, 0, ZC), "y", FY, -FY)
    ns.bevel(board, width=0.06, segments=1)
    C.part([board], "Board", C.NAVY_DEEP, smooth_angle=40)
    rim = C.ring_slab(C.rrect(W + 0.36, H + 0.36, 0.75, 3, 0, ZC), C.rrect(W - 0.1, H - 0.1, 0.56, 3, 0, ZC), "y",
                      FY - 0.08, -FY + 0.02)

    letters = C.text("STACKHOUSE", 2.3, 0.18, (-1.95, FY - 0.08, ZC + 0.02), width=13.6, res=1, spacing=1.04,
                     back=False)
    ns.tag(letters, "Letters", NEON_RED, "Neon", recolor="neon", cast_shadow=False, smooth_angle=30)
    hq = C.text("HQ", 1.7, 0.18, (HQ_X, FY - 0.08, ZC), width=2.15, res=1, spacing=1.05, back=False)
    ns.tag(hq, "LettersHQ", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=30)
    ring = C.pipe([(HQ_X + x, FY - 0.1, z) for x, z in C.circle_pts(1.75, 20, 0, ZC)], 0.1, sides=5, closed=True)
    ns.tag(ring, "Ring", C.MUSTARD, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    bulbs = []
    n = 11
    for zb in (BZ0 + 0.32, BZ0 + H - 0.32):
        for k in range(n):
            x = -W / 2 + 0.9 + (W - 1.8) * k / (n - 1)
            bulbs.append(ns.sphere(0.15, loc=(x, FY - 0.12, zb), segs=6, rings=3))
    ns.tag(C.merge(bulbs, "Bulbs"), "Bulbs", C.LAMP_WARM, "Neon", recolor="marquee", cast_shadow=False,
           smooth_angle=70)

    # steel roof trusses: front post up behind the board, back strut, braces, ties, base plates
    steel = []
    for x in (-6.5, 6.5):
        steel.append(C.rod((x, 0.45, 0.1), (x, 0.45, BZ0 + H - 0.4), 0.14, verts=6))
        steel.append(C.rod((x, 3.0, 0.1), (x, 0.5, BZ0 + H - 1.0), 0.12, verts=6))
        steel.append(C.rod((x, 0.5, 0.4), (x, 2.55, 1.7), 0.07, verts=5))
        steel.append(C.rod((x, 0.5, 2.6), (x, 1.75, 3.7), 0.07, verts=5))
        for y in (0.45, 3.0):
            steel.append(ns.box((0.6, 0.6, 0.1), loc=(x, y, 0.05), bevel=0.02, segments=1))
    for z in (1.5, BZ0 - 0.4):
        steel.append(C.rod((-6.5, 0.45, z), (6.5, 0.45, z), 0.08, verts=5))
    for x in (-3.0, 3.0):   # board brackets
        steel.append(ns.box((0.3, 0.4, H - 0.6), loc=(x, 0.4, ZC), bevel=0.03, segments=1))
    C.part(steel, "Truss", C.STEEL, "Metal", smooth_angle=50)
    C.part([rim], "Chrome", C.CHROME, "Metal", smooth_angle=40)


SOCKETS = {"Glow": ((0, FY - 2.5, ZC), 0.0)}
META = {"mount": "roof", "pivot": "roof plane under the board centre", "board_size": [W, H],
        "roles": {"neon": "Letters, LettersHQ, Ring", "marquee": "Bulbs"},
        "light_hint": {"type": "SurfaceLight/PointLight", "at": "Socket_Glow", "color": NEON_RED, "range": 30,
                       "brightness": 2}}

if __name__ == "__main__":
    C.run(build, "Lobby_HQSign", sockets=SOCKETS, pivot=(0, 0, 0), meta=META)
