"""Shop_NeonSign — the big "STACKHOUSE" neon sign for the dining room / facade.

Modelled Poppins Bold letters in hot-pink Neon on a deep-navy backing board with a chrome
rim, a cyan neon border tube, and a stacked-sandwich neon icon (mustard buns, pink
filling, cyan lettuce wave). Every lit part has role "neon" so the lighting system can
flicker / kill them in blackouts (find by role; names: Letters, Border, IconBun,
IconFill).
Wall-mounted: pivot = bottom-centre of the BACK face (+Y), so it sits flush on a wall face
with the lettering facing the room (LookVector). Two chrome standoff brackets hold it 0.4
off the wall.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H = 15.0, 3.6
BACK_Y = 0.4            # board back face sits 0.4 in front of the wall (y = 0 is the wall)
TH = 0.3                # board thickness
FRONT_Y = -BACK_Y - TH  # (board spans y = -0.7 .. -0.4)
ZC = H / 2 + 0.15       # rim bottom sits on z = 0


def build():
    # backing board + chrome rim (a slightly larger rounded plate behind it)
    board = C.prism(C.rrect(W, H, 0.55, 4, 0, ZC), "y", FRONT_Y, -BACK_Y)
    ns.bevel(board, width=0.06, segments=1)
    ns.tag(board, "Board", C.NAVY_DEEP, can_collide=False, smooth_angle=40)
    rim = C.prism(C.rrect(W + 0.3, H + 0.3, 0.68, 4, 0, ZC), "y", FRONT_Y + 0.12, -BACK_Y + 0.02)
    ns.bevel(rim, width=0.06, segments=1)
    brackets = []
    for x in (-W / 2 + 2.0, W / 2 - 2.0):
        brackets.append(ns.box((0.9, BACK_Y + 0.05, 0.9), loc=(x, -BACK_Y / 2, ZC), bevel=0.05, segments=1))
        brackets.append(ns.box((1.3, 0.08, 1.3), loc=(x, -0.04, ZC), bevel=0.03, segments=1))
    C.part([rim] + brackets, "Frame", C.CHROME, "Metal", smooth_angle=40)

    # letters
    lx = 1.15                        # text block centre (icon on the left)
    letters = C.text_mesh("STACKHOUSE", 2.1, 0.14, font=C.FONT_BOLD, resolution=2, spacing=1.04,
                          loc=(lx, FRONT_Y - 0.07, ZC))
    C.fit_text_width(letters, 11.2)
    ns.tag(letters, "Letters", C.PINK, "Neon", recolor="neon", cast_shadow=False, smooth_angle=30)

    # border tube, inset from the board edge
    lo = C.rrect(W - 0.5, H - 0.5, 0.35, 3, 0, ZC)
    border = C.pipe([(x, FRONT_Y - 0.06, z) for x, z in lo], 0.06, sides=6, closed=True)
    ns.tag(border, "Border", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # stacked-sandwich icon: bun dome, filling bar, lettuce wave, bottom bun
    ix = -W / 2 + 1.65
    y = FRONT_Y - 0.06
    dome = [(ix + 1.0 * __import__("math").cos(a / 10 * 3.14159), ZC + 0.35 + 0.75 * __import__("math").sin(a / 10 * 3.14159))
            for a in range(11)]
    bun_top = C.prism(dome, "y", y - 0.06, y + 0.04)
    bun_bot = C.prism(C.rrect(2.0, 0.42, 0.18, 2, ix, ZC - 0.75), "y", y - 0.06, y + 0.04)
    ns.tag(C.merge([bun_top, bun_bot], "IconBun"), "IconBun", C.MUSTARD, "Neon", recolor="neon", cast_shadow=False)
    fill = C.prism(C.rrect(2.1, 0.32, 0.14, 2, ix, ZC - 0.28), "y", y - 0.05, y + 0.04)
    import math
    wave = [(ix - 1.05 + 2.1 * i / 12, y - 0.02, ZC + 0.12 + 0.09 * math.sin(i * math.pi / 2)) for i in range(13)]
    lettuce = C.pipe(wave, 0.07, sides=6)
    ns.tag(C.merge([fill], "IconFill"), "IconFill", C.PINK, "Neon", recolor="neon", cast_shadow=False)
    ns.tag(lettuce, "IconLeaf", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)", "size": [W, H, 0.75],
        "neon_parts": ["Letters", "Border", "IconBun", "IconFill", "IconLeaf"],
        "light_hint": {"color": C.PINK, "range": 18, "brightness": 2}}

if __name__ == "__main__":
    C.run(build, "Shop_NeonSign", pivot=(0, 0, 0), meta=META, sockets={"Glow": ((0, -1.6, ZC), 0.0)})
