"""Shop_SpecialsBoard — A-frame chalkboard stand "TONIGHT'S SPECIAL" (2.8 x 5 x 2).

Two wood-framed dark-green chalkboards hinged at the top under a wooden cap with a hand
slot, splayed to a 2-stud footprint and held by chrome side stays. Front board: modelled
chalk "TONIGHT'S" (cream), a big "SPECIAL" (pink) with a yellow swoosh, "NIGHT OWL" (yellow),
"+ FRIES" (cream) and a pink chalk star. Back board: "OPEN ALL NIGHT" in cream chalk.
Floor prop: pivot = bottom-centre (between the feet), front (-Y) = the main board.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix  # noqa: E402

ns = C.ns
BW = 2.6                      # board width
HT = 4.82                     # hinge height
FOOT = 1.0                    # feet at y = +-FOOT
TH = math.atan2(FOOT, HT)     # lean from vertical
L = HT / math.cos(TH)         # board length along the slant
GREEN = "#25402F"
CH_WHITE = "#ECE8DC"
CH_PINK = "#F29BC4"
CH_YELLOW = "#F5D76E"


def board_xf(back=False):
    """Board-local (bottom z = 0, top z = L, face toward -Y) -> world, leaning on the hinge."""
    m = Matrix.Translation((0, 0, HT)) @ Matrix.Rotation(-TH, 4, "X") @ Matrix.Translation((0, 0, -L))
    if back:
        m = Matrix.Rotation(math.pi, 4, "Z") @ m
    return m


def xf(objs, m):
    for o in objs:
        ns.apply_all(o)
        o.matrix_world = m @ o.matrix_world
        ns.apply_all(o)
    return objs


def build():
    wood, chalk = [], []
    lines = {CH_WHITE: [], CH_PINK: [], CH_YELLOW: []}
    for back in (False, True):
        m = board_xf(back)
        fr = C.ring_slab(C.rrect(BW, L, 0.1, 2, 0, L / 2), C.rrect(BW - 0.36, L - 0.36, 0.04, 2, 0, L / 2),
                         "y", -0.07, 0.07)
        ns.bevel(fr, width=0.03, segments=1, angle=50)
        panel = ns.box((BW - 0.32, 0.08, L - 0.32), loc=(0, 0.0, L / 2), bevel=0.0)
        wood += xf([fr], m)
        chalk += xf([panel], m)
        fy = -0.04                                        # chalk surface (panel front) in board space
        if not back:
            items = [("TONIGHT'S", 0.42, 1.9, L - 0.72, CH_WHITE), ("SPECIAL", 0.62, 2.02, L - 1.38, CH_PINK),
                     ("NIGHT OWL", 0.36, 1.72, L - 2.42, CH_YELLOW), ("+ FRIES", 0.3, 1.12, L - 2.98, CH_WHITE)]
            for txt, hgt, wid, z, col in items:
                lines[col] += xf([C.text(txt, hgt, 0.02, (0, fy - 0.0, z), width=wid, res=1, flat=True)], m)
            sw = [(-0.95 + 1.9 * i / 10, L - 1.86 + 0.07 * math.sin(i / 10 * math.pi * 1.3) - 0.03 * i / 10)
                  for i in range(11)]
            swoosh = C.prism([(x, z + 0.035) for x, z in sw] + [(x, z - 0.035) for x, z in reversed(sw)], "y",
                             fy - 0.012, fy + 0.004)
            lines[CH_YELLOW] += xf([swoosh], m)
            star = C.prism(C.star(0.36, 0.15, 0.0, L - 3.75), "y", fy - 0.012, fy + 0.004)
            lines[CH_PINK] += xf([star], m)
        else:
            for txt, hgt, wid, z in (("OPEN", 0.5, 1.5, L - 1.3), ("ALL NIGHT", 0.42, 1.95, L - 2.0)):
                lines[CH_WHITE] += xf([C.text(txt, hgt, 0.02, (0, fy, z), width=wid, res=1, flat=True)], m)
            moon = C.prism([(x * 0.42, z * 0.42 + L - 3.2) for x, z in
                            [(math.cos(a), math.sin(a)) for a in [math.radians(60 + 24 * k) for k in range(11)]] +
                            [(0.55 * math.cos(a) + 0.32, 0.8 * math.sin(a)) for a in
                             [math.radians(300 - 24 * k) for k in range(11)]]], "y", fy - 0.012, fy + 0.004)
            lines[CH_YELLOW] += xf([moon], m)

    # wooden cap with a hand slot over the hinge, chrome hinges and side stays
    cap_pts = C.fillet([(-BW / 2 - 0.05, 0), (BW / 2 + 0.05, 0), (BW / 2 + 0.05, 0.3), (-BW / 2 - 0.05, 0.3)],
                       [0.02, 0.02, 0.1, 0.1], 2)
    cap = C.prism(cap_pts, "y", -0.2, 0.2, loc=(0, 0, HT - 0.12))
    ns.bevel(cap, width=0.03, segments=1)
    slot = C.prism(C.rrect(0.7, 0.12, 0.06, 2, 0, HT + 0.06), "y", -0.21, 0.21)
    wood.append(cap)
    C.part(wood, "Wood", C.WOOD, "Wood", smooth_angle=45)
    C.part([slot], "HandSlot", C.DARK_VOID, smooth_angle=None)
    C.part(chalk, "Chalkboard", GREEN, "Slate", smooth_angle=None)
    metal = []
    for sx in (-1, 1):
        zst = 2.0
        yst = FOOT * (1 - zst / HT) + 0.02
        metal.append(C.rod((sx * (BW / 2 + 0.04), -yst, zst), (sx * (BW / 2 + 0.04), yst, zst), 0.03, verts=6))
        for sy in (-1, 1):
            metal.append(ns.box((0.07, 0.06, 0.07), loc=(sx * (BW / 2 + 0.04), sy * yst, zst), bevel=0.0))
        metal.append(ns.box((0.26, 0.42, 0.06), loc=(sx * (BW / 2 - 0.35), 0, HT - 0.15), bevel=0.0))
    C.part(metal, "Metal", C.CHROME, "Metal", smooth_angle=45)
    for col, objs in lines.items():
        name = {CH_WHITE: "ChalkCream", CH_PINK: "ChalkPink", CH_YELLOW: "ChalkYellow"}[col]
        C.part(objs, name, col, smooth_angle=None)
    # the lean puts the back edge of each foot ~0.01 under z = 0: stand the whole stand on the floor
    lo, _ = ns.bbox_world(ns._tagged_objects())
    for o in ns._tagged_objects():
        o.location.z -= lo.z


META = {"pivot": "bottom-centre (between the feet)", "mount": "floor", "footprint": [BW + 0.1, 2 * FOOT + 0.14]}

if __name__ == "__main__":
    C.run(build, "Shop_SpecialsBoard", pivot=(0, 0, 0), meta=META)
