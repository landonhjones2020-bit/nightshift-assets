"""Lobby_TestKitchenSign — hanging enamel "TEST KITCHEN" sign (8 wide), chains + bracket.

A glossy red-orange enamel panel with rounded corners, a cream inset border line and
cream "TEST KITCHEN" letters on both faces (the back copy reads correctly from behind),
small mustard sandwich-star rivets in the corners, hung on two steel chains from a black
ceiling bracket bar with two mounting plates.

PIVOT = top centre of the bracket (hang point, everything hangs below), like
Shop_PendantLamp. Front = -Y. Socket Hang = the pivot (top of the bracket bar).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 8.0, 1.9, 0.14
DROP = 1.55                    # bracket top -> panel top
ZC = -DROP - H / 2
CHAIN_X = 3.2
ENAMEL = "#E24E2A"


def build():
    panel = C.prism(C.rrect(W, H, 0.35, 3, 0, ZC), "y", -T / 2, T / 2)
    ns.bevel(panel, width=0.04, segments=1, angle=50)
    C.part([panel], "Enamel", ENAMEL, smooth_angle=40)
    cream = []
    for sy in (-1, 1):
        a0, a1 = sorted((sy * (T / 2 - 0.01), sy * (T / 2 + 0.02)))
        cream.append(C.ring_slab(C.rrect(W - 0.32, H - 0.32, 0.24, 3, 0, ZC), C.rrect(W - 0.48, H - 0.48, 0.18, 3, 0, ZC),
                                 "y", a0, a1))
    cream.append(C.text("TEST KITCHEN", 0.9, 0.04, (0, -T / 2 - 0.0, ZC), width=6.3, res=1, spacing=1.05, flat=True))
    cream.append(C.text("TEST KITCHEN", 0.9, 0.04, (0, T / 2 + 0.0, ZC), width=6.3, res=1, spacing=1.05, facing="+Y",
                        flat=True))
    C.part(cream, "Lettering", C.CREAM, smooth_angle=None)
    rivets = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            rivets.append(ns.sphere(0.09, loc=(sx * (W / 2 - 0.42), 0, ZC + sz * (H / 2 - 0.42)), scale=(1, 1.2, 1),
                                    segs=6, rings=4))
    C.part(rivets, "Rivets", C.MUSTARD, "Metal", smooth_angle=60)

    # chains: alternating links from the panel's top eyes up to the bracket
    links, steel = [], []
    n = 6
    for sx in (-1, 1):
        x = sx * CHAIN_X
        z0, z1 = -DROP + 0.05, -0.12
        for k in range(n):
            z = z0 + (z1 - z0) * (k + 0.5) / n
            l = ns.torus(0.12, 0.03, major_segs=6, minor_segs=3)
            l.scale = (1.0, 1.0, 1.0)
            C.place(l, (x, 0, z), yaw=90 * (k % 2), pitch=90)
            l.scale = (1, 1, 1)
            links.append(l)
        steel.append(ns.box((0.22, 0.22, 0.1), loc=(x, 0, -DROP + 0.02), bevel=0.02, segments=1))
    steel.append(ns.box((W - 0.6, 0.3, 0.18), loc=(0, 0, -0.09), bevel=0.05, segments=1))
    for sx in (-1, 1):
        steel.append(ns.box((0.7, 0.7, 0.06), loc=(sx * (W / 2 - 0.6), 0, -0.03), bevel=0.02, segments=1))
    C.part(links, "Chains", C.STEEL, "Metal", smooth_angle=60)
    C.part(steel, "Bracket", C.BLACK, "Metal", smooth_angle=40)


SOCKETS = {"Hang": ((0, 0, 0), 0.0)}
META = {"pivot": "top centre of the bracket (hang point)", "drop": round(DROP + H, 2), "size": [W, round(DROP + H, 2)],
        "two_sided": True}

if __name__ == "__main__":
    C.run(build, "Lobby_TestKitchenSign", sockets=SOCKETS, pivot=(0, 0, 0), meta=META)
