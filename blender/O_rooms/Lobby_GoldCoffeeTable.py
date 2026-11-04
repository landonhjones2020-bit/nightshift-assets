"""Lobby_GoldCoffeeTable — low round VIP coffee table (4 dia x 1.6 H) with two mini milkshakes.

A black lacquer top inside a raised gold rim band, on a waisted gold pedestal with a wide
stepped foot. On top a round gold tray with two mini soda-fountain milkshakes (strawberry with a
cyan straw, mint with a pink straw): Glass tulip glasses, whipped cream, cherries.

Pivot = bottom-centre. Collides (top, rim, pedestal). Sockets Tray = tray top centre; Shake1 /
Shake2 = the two glasses' bases (left / right as seen from the front).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
R = 2.0
TOP = 0.78                    # lacquer top surface
TRAY_Z = TOP + 0.005
SHAKES = ((-0.36, 0.12, C.SHAKE_PINK, C.CYAN, 40.0), (0.38, -0.15, C.SHAKE_MINT, C.PINK, 140.0))
V = 28


def build():
    top = ns.cyl(R - 0.09, 0.12, loc=(0, 0, TOP - 0.06), verts=V, bevel=0.0)
    C.part([top], "Top", C.LACQUER, can_collide=True, smooth_angle=30)
    rim = C.lathe_ring([(R - 0.1, TOP - 0.16), (R, TOP - 0.14), (R, TOP + 0.02), (R - 0.04, TOP + 0.06), (R - 0.1, TOP + 0.05)],
                       verts=V)
    k = (TOP - 0.12) / 0.74        # pedestal profile (drawn for a 0.74 tall pedestal) scaled to the top height
    base = ns.lathe([(0.0, 0.0), (1.15, 0.0), (1.15, 0.07 * k), (1.02, 0.13 * k), (0.5, 0.22 * k), (0.3, 0.4 * k),
                     (0.27, 0.52 * k), (0.36, 0.62 * k), (0.62, 0.7 * k), (0.9, TOP - 0.12), (0.0, TOP - 0.12)], verts=16)
    C.part([rim, base], "Gold", C.GOLD, "Metal", can_collide=True, smooth_angle=45)
    tray = ns.lathe([(0.0, 0.0), (0.86, 0.0), (0.9, 0.07), (0.87, 0.09), (0.82, 0.035), (0.0, 0.035)], verts=20,
                    loc=(0, 0, TRAY_Z))
    C.part([tray], "Tray", C.GOLD, "Metal", smooth_angle=45)
    glass, groups = [], {}
    for x, y, shake, straw, sy in SHAKES:
        d = C.milkshake((x, y, TRAY_Z + 0.035), h=0.48, r=0.18, shake=shake, straw=straw, straw_yaw=sy)
        glass += d.pop("glass")
        for col, objs in d.items():
            C.add(groups, col, objs)
    ns.tag(C.merge(glass, "Glasses"), "Glasses", C.GLASS_TINT, "Glass", transparency=0.55, cast_shadow=False, smooth_angle=50)
    C.parts_by_colour(groups, "Shake", smooth_angle=50)


SOCKETS = {"Tray": ((0, 0, TRAY_Z + 0.035), 0.0),
           "Shake1": ((SHAKES[0][0], SHAKES[0][1], TRAY_Z + 0.035), 0.0),
           "Shake2": ((SHAKES[1][0], SHAKES[1][1], TRAY_Z + 0.035), 0.0)}
META = {"table_height": TOP, "glass": "Glasses (Glass, transparency 0.55)"}

if __name__ == "__main__":
    C.run(build, "Lobby_GoldCoffeeTable", sockets=SOCKETS, budget=2000, meta=META, backdrop="#3A2440")
