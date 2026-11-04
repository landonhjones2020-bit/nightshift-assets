"""Basement_WoodenCrates — a pile of three old slatted wooden crates.

Each crate: a dark core showing through the gaps between horizontal side planks, top
boards and bevelled corner battens. Bottom left: a big pale crate stencilled FRAGILE in
faded red-orange raised letters. Bottom right: a darker crate turned a little, with two
black "this side up" arrows and one top board missing. On top of the big one: a weathered
grey crate stencilled 1987 in raised black numerals. Crates collide; stencils do not.
Front faces -Y, pivot = bottom-centre. 4 x 3 x 3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
GAP = 0.05
PT = 0.06                     # plank thickness
CORE = "#2E241B"
WOODS = {"pale": "#94775A", "dark": "#6E5440", "grey": "#857865"}


def crate(w, d, h, loc, yaw, wood, missing_top=None, n=3):
    """Slatted crate standing on loc (bottom-centre), turned by yaw. Returns {"core", "wood",
    "batten", "front_z"} (front_z = centre heights of the front planks, for stencils)."""
    core = [ns.box((w - 2 * PT + 0.02, d - 2 * PT + 0.02, h - 0.02), loc=(0, 0, (h - 0.02) / 2), bevel=0.0)]
    planks, battens = [], []
    L = h - 0.08
    ph = (L - (n - 1) * GAP) / n
    zs = [0.02 + ph / 2 + k * (ph + GAP) for k in range(n)]
    for z in zs:
        for sy in (-1, 1):   # front / back planks run along X
            planks.append(ns.box((w - 0.3, PT, ph), loc=(0, sy * (d / 2 - PT / 2), z), bevel=0.0))
        for sx in (-1, 1):   # side planks run along Y
            planks.append(ns.box((PT, d - 0.3, ph), loc=(sx * (w / 2 - PT / 2), 0, z), bevel=0.0))
    tw = (d - (n - 1) * GAP - 0.04) / n
    for k in range(n):
        if k == missing_top:
            continue
        y = -d / 2 + 0.02 + tw / 2 + k * (tw + GAP)
        planks.append(ns.box((w - 0.04, tw, PT), loc=(0, y, h - PT / 2), bevel=0.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            battens.append(ns.box((0.18, 0.18, h - 0.1), loc=(sx * (w / 2 - 0.08), sy * (d / 2 - 0.08), (h - 0.1) / 2 + 0.01),
                                  bevel=0.03, segments=1))
    for lst in (core, planks, battens):
        C.place(lst, loc=loc, yaw=yaw)
    return {"core": core, "wood": planks, "batten": battens, "front_z": zs}


def build():
    parts = {"core": [], "pale": [], "dark": [], "grey": [], "batten": []}
    red, black = [], []

    def add(c, wood):
        parts["core"] += c["core"]
        parts[wood] += c["wood"]
        parts["batten"] += c["batten"]

    # bottom left: big pale crate, FRAGILE on the middle front plank
    aw, ad, ah = 2.05, 2.3, 1.5
    a_loc, a_yaw = (-0.95, 0.15, 0.0), -2.0
    A = crate(aw, ad, ah, a_loc, a_yaw, "pale")
    add(A, "pale")
    t = C.stencil("FRAGILE", 0.3, (0, -ad / 2, A["front_z"][1]), width=1.45, depth=0.03, raised=True)
    C.place([t], loc=a_loc, yaw=a_yaw)
    red.append(t)

    # bottom right: darker crate, turned, two up-arrows, a top board missing
    bw, bd, bh = 1.85, 2.0, 1.42
    b_loc, b_yaw = (1.08, -0.05, 0.0), 7.0
    B = crate(bw, bd, bh, b_loc, b_yaw, "dark", missing_top=1)
    add(B, "dark")
    arrows = []
    fy = -bd / 2 - 0.008
    for ax in (-0.42, 0.42):
        zc = B["front_z"][1]
        arrows.append(C.strip_xz((ax, zc - 0.17), (ax, zc + 0.06), 0.08, fy))
        arrows.append(C.face_dir(C.poly([(ax - 0.14, fy, zc + 0.04), (ax + 0.14, fy, zc + 0.04), (ax, fy, zc + 0.2)]), "-Y"))
    for o in arrows:
        C.face_dir(o, "-Y")
    C.place(arrows, loc=b_loc, yaw=b_yaw)
    black += arrows

    # on top of the big one: weathered grey crate, 1987
    cw, cd, chh = 1.6, 1.6, 1.42
    c_loc, c_yaw = (-1.0, 0.2, ah), -9.0
    Cc = crate(cw, cd, chh, c_loc, c_yaw, "grey")
    add(Cc, "grey")
    t2 = C.stencil("1987", 0.32, (0, -cd / 2, Cc["front_z"][1]), width=0.8, depth=0.03, raised=True)
    C.place([t2], loc=c_loc, yaw=c_yaw)
    black.append(t2)

    C.part(parts["core"], "Core", CORE, can_collide=True, smooth_angle=None)
    for k in ("pale", "dark", "grey"):
        C.part(parts[k], "Planks" + k.capitalize(), WOODS[k], "Wood", can_collide=True, smooth_angle=30)
    C.part(parts["batten"], "Battens", "#7A5E44", "Wood", can_collide=True, smooth_angle=30)
    C.part(red, "StencilRed", C.BRAND, smooth_angle=None)
    C.part(black, "StencilBlack", C.INK, smooth_angle=None)


META = {"collide": "crates (core, planks, battens)", "stencils": ["FRAGILE", "1987"]}

if __name__ == "__main__":
    C.run(build, "Basement_WoodenCrates", budget=2000, meta=META, views=((-32, 22, False), (40, 16, True)))
