"""Lobby_VIPNeonSign — big neon "VIP" with a crown (10 W x 4 H x 0.6 D), wall-mounted.

A black-lacquer backer shaped like a wide rounded plaque with an arched tab in the middle,
rimmed by a gold tube. On it chunky deep-plum channel letters "VIP" (Poppins Bold) traced by
hot-pink neon tubes (LetterNeon), a gold neon crown in the arch (CrownNeon: outline, band,
five glowing tip balls) and two pairs of cyan neon sparkles either side of the letters
(Sparkles). Every lit part is Neon with role "neon" so the lighting system can flicker them.

Wall-mounted: back face on the wall plane (Blender y = 0), front -Y; pivot = bottom-centre of the
back face. Socket Glow = 2 studs in front of the sign centre (PointLight / SurfaceLight).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
W, H = 10.0, 4.0
BACK_D = 0.3                  # backer y -BACK_D .. 0
E = 0.06                      # gold rim tube extent (4-sided tube r 0.085 -> 0.06): the backer is inset by it (sign = W x H)
BODY_H = 2.6                  # plaque height (the arch tab rises above it)
ARCH_W, ARCH_H = 4.0, H - E - BODY_H
LET_Y = -BACK_D - 0.17        # letter front face (letters 0.17 deep, back caps on the backer)
TUBE_R = 0.075
PLUM = "#3A1238"
NEON_GOLD = "#FFC94A"


def outline():
    """Backer silhouette (x, z): rounded plaque + arched crown tab, CCW."""
    pts = [(-W / 2 + E, E), (W / 2 - E, E), (W / 2 - E, BODY_H)]
    hw = ARCH_W / 2
    pts.append((hw + 0.35, BODY_H))
    for k in range(13):
        a = math.pi * k / 12
        pts.append((hw * math.cos(a), BODY_H + ARCH_H * math.sin(a) ** 0.9))
    pts.append((-hw - 0.35, BODY_H))
    pts.append((-W / 2 + E, BODY_H))
    r = [0.55, 0.55, 0.55, 0.25] + [0.0] * 13 + [0.25, 0.55]
    return C.fillet(pts, r, 2)


def sparkle(cx, cz, r, y):
    """Four-pointed sparkle (flat neon star with depth)."""
    pts = []
    for i in range(8):
        a = math.pi / 2 + math.pi * i / 4
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(a), cz + rr * math.sin(a)))
    return C.prism(pts, "y", y - 0.06, y + 0.02)


def build():
    out = outline()
    backer = C.prism(out, "y", -BACK_D, 0.0)
    ns.bevel(backer, width=0.04, segments=1)
    C.part([backer], "Backer", C.LACQUER, smooth_angle=40)
    rim = C.pipe([(x, -BACK_D * 0.5, z) for x, z in out], 0.085, sides=4, closed=True)
    C.part([rim], "GoldEdge", C.GOLD, "Metal", smooth_angle=50)

    # channel letters + pink neon contour tubes
    w = C.Word("VIP", 0.0, cap=1.95, spacing=1.12, base=0.42)
    letters = w.solid(LET_Y, (-BACK_D + 0.02) - LET_Y, back=False, name="Letters")   # back edge sunk 0.02 into the backer
    C.part([letters], "Letters", PLUM, smooth_angle=30)
    tubes = C.contour_tubes(w.loops(offset=-0.09), LET_Y - 0.03, TUBE_R, sides=5)
    ns.tag(tubes, "LetterNeon", C.PINK, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # gold neon crown in the arch: outline (band + five points), a band line, tip balls
    cz0, cw = BODY_H + 0.06, 2.2
    tips = [(-cw / 2, cz0 + 0.72), (-cw / 4, cz0 + 0.5), (0.0, cz0 + 0.86), (cw / 4, cz0 + 0.5), (cw / 2, cz0 + 0.72)]
    crown = [(-cw / 2 + 0.12, cz0), (cw / 2 - 0.12, cz0), (cw / 2 - 0.05, cz0 + 0.24), tips[4], (cw / 2 - 0.4, cz0 + 0.4),
             tips[3], (0.17, cz0 + 0.46), tips[2], (-0.17, cz0 + 0.46), tips[1], (-cw / 2 + 0.4, cz0 + 0.4), tips[0],
             (-cw / 2 + 0.05, cz0 + 0.24)]
    cy = -BACK_D - 0.1
    neon_gold = [C.pipe([(x, cy, z) for x, z in crown], TUBE_R, sides=5, closed=True),
                 C.pipe([(-cw / 2 + 0.1, cy, cz0 + 0.24), (cw / 2 - 0.1, cy, cz0 + 0.24)], TUBE_R * 0.8, sides=5)]
    neon_gold.append(C.spheres([(x, cy, z + 0.08) for x, z in tips], 0.1, segs=6, rings=4))
    ns.tag(C.merge(neon_gold, "CrownNeon"), "CrownNeon", NEON_GOLD, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    # crown tube standoffs (small gold posts into the backer)
    posts = [C.rod((x, -BACK_D + 0.01, z), (x, cy, z), 0.03, verts=4) for x, z in ((-0.8, cz0), (0.8, cz0), (0.0, cz0 + 0.46))]
    C.part(posts, "Standoffs", C.GOLD, "Metal", smooth_angle=50)

    # cyan sparkles either side of the letters
    sp = []
    for sx in (-1, 1):
        sp.append(sparkle(sx * 3.75, 1.55, 0.55, -BACK_D - 0.02))
        sp.append(sparkle(sx * 4.35, 2.3, 0.3, -BACK_D - 0.02))
        sp.append(sparkle(sx * 3.2, 0.62, 0.22, -BACK_D - 0.02))
    ns.tag(C.merge(sp, "Sparkles"), "Sparkles", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=None)


SOCKETS = {"Glow": ((0, -2.0, 1.6), 0.0)}
META = {"mount": "wall", "pivot": "bottom-centre of the back face (on the wall plane)", "wall_back_z": 0.0,
        "neon_parts": ["LetterNeon (pink)", "CrownNeon (gold)", "Sparkles (cyan)"],
        "roles": {"neon": "LetterNeon, CrownNeon, Sparkles"},
        "light_hint": {"type": "PointLight", "at": "Socket_Glow", "color": C.PINK, "range": 16, "brightness": 1.5}}

if __name__ == "__main__":
    C.run(build, "Lobby_VIPNeonSign", sockets=SOCKETS, mount="wall", budget=2000, pivot=(0, 0, 0), meta=META,
          backdrop="#3A2440")
