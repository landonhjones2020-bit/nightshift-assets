"""Basement_HangingBulb — a bare bulb on a cord, the basement's only fixed light.

A dark steel ceiling cover, a slightly kinked black cloth cord, a ribbed dingy-cream
porcelain pull-chain lampholder with its brass shell, a brass bead chain with a little
pull bob, and a bare pear-shaped bulb (part Bulb, Neon, role "lamp": the game switches it
between Neon and off in blackouts, like Shop_TallPendant).
PIVOT = TOP of the ceiling cover (z = 0, on the ceiling); everything hangs below.
Socket Light = bulb centre (PointLight). No collision. ~0.6 x 2.6 x 0.6.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SOCK_TOP = -1.72          # lampholder top
SOCK_BOT = -2.1           # lampholder bottom (brass shell starts)
BULB_TOP = -2.2           # bulb neck
BULB_Z = -2.36            # bulb centre (widest part)


def build():
    cover = ns.lathe([(0.0, -0.1), (0.24, -0.1), (0.3, -0.06), (0.3, 0.0), (0.0, 0.0)], verts=12)
    C.part([cover], "Cover", C.CONCRETE_DARK, "Metal", smooth_angle=50)
    cord = C.pipe([(0, 0, -0.08), (0.015, 0.01, -0.6), (-0.01, 0.0, -1.15), (0.0, 0.0, SOCK_TOP + 0.04)], 0.03, sides=5)
    C.part([cord], "Cord", C.INK, "Fabric", smooth_angle=60)

    # porcelain pull-chain lampholder: tapered body, two ribs, cap where the cord enters
    holder = ns.lathe([(0.07, SOCK_TOP + 0.06), (0.12, SOCK_TOP), (0.17, SOCK_TOP - 0.12), (0.17, SOCK_BOT + 0.06),
                       (0.14, SOCK_BOT), (0.0, SOCK_BOT)], verts=10)
    ribs = [ns.cyl(0.185, 0.04, loc=(0, 0, z), verts=10, bevel=0.0) for z in (SOCK_TOP - 0.16, SOCK_TOP - 0.26)]
    C.part([holder] + ribs, "Holder", C.CREAM, smooth_angle=50)
    shell = ns.cyl(0.11, 0.14, loc=(0, 0, SOCK_BOT - 0.06), verts=10, bevel=0.0)
    knob = C.rod((0.16, 0, SOCK_TOP - 0.2), (0.24, 0, SOCK_TOP - 0.2), 0.03, verts=6)
    chain = C.pipe([(0.235, 0, SOCK_TOP - 0.2), (0.25, -0.01, SOCK_TOP - 0.55), (0.24, -0.005, SOCK_TOP - 0.82)], 0.012,
                   sides=3)
    bob = ns.cyl(0.03, 0.09, loc=(0.24, -0.005, SOCK_TOP - 0.86), verts=6, radius_top=0.018, bevel=0.0)
    C.part([shell, knob, chain, bob], "Brass", C.BRASS, "Metal", smooth_angle=50)

    # bare A-shape bulb
    bulb = ns.lathe([(0.0, BULB_TOP + 0.03), (0.1, BULB_TOP + 0.03), (0.105, BULB_TOP - 0.03), (0.17, BULB_Z + 0.08),
                     (0.215, BULB_Z), (0.2, BULB_Z - 0.1), (0.14, BULB_Z - 0.19), (0.0, BULB_Z - 0.23)], verts=10)
    C.part([bulb], "Bulb", C.BULB, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)


SOCKETS = {"Light": ((0.0, 0.0, BULB_Z), 0.0)}
META = {"pivot": "top of the ceiling cover (hangs below)", "drop": round(-(BULB_Z - 0.23), 2), "lamp_part": "Bulb",
        "light_hint": {"type": "PointLight", "socket": "Light", "color": C.BULB, "range": 14, "brightness": 0.8}}

if __name__ == "__main__":
    C.run(build, "Basement_HangingBulb", mount="hang", pivot=(0.0, 0.0, 0.0), sockets=SOCKETS, budget=2000,
          meta=META, preview_fn=C.hang_preview(dirs=((-0.5, -1.0, -0.15), (0.6, -0.8, -0.55))))
