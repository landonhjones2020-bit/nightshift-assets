"""Lobby_GoldTrophy — giant gold trophy cup with a star on a black plinth (3 W x 6.5 H x 3 D).

A stepped black-lacquer plinth with gold trim bands and a blank gold plaque on its front
(Plaque, role "plaque", Front face: the game can write a name there). On it a turned gold
trophy cup: domed foot, knotted stem, a tall flared bowl (ruby-red star inlay on its front) with a
rolled rim and a domed lid, two big ear handles, and a chunky bevelled five-point star on a finial
at the top.

Front = -Y, pivot = bottom-centre. Collides (plinth, cup). Socket Plaque = plaque face centre
(yaw 0).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H = 3.0, 6.5
PL_TOP = 1.75
PLQ_W, PLQ_H, PLQ_Z = 1.7, 0.66, 0.92
BLOCK = 2.4                    # main plinth block width / depth
PLQ_Y = -BLOCK / 2 - 0.05      # plaque face
STAR_Z, STAR_R = 5.96, 0.58


def build():
    lac = [C.prism(C.rrect(3.0, 3.0, 0.24, 2), "z", 0.0, 0.26),
           C.prism(C.rrect(BLOCK, BLOCK, 0.14, 2), "z", 0.24, PL_TOP - 0.18),
           C.prism(C.rrect(2.6, 2.6, 0.18, 2), "z", PL_TOP - 0.2, PL_TOP)]
    for o in lac:
        ns.bevel(o, width=0.04, segments=1)
    C.part(lac, "Plinth", C.LACQUER, can_collide=True, smooth_angle=40)
    trim = [C.ring_slab(C.rrect(BLOCK + 0.08, BLOCK + 0.08, 0.18, 2), C.rrect(BLOCK - 0.02, BLOCK - 0.02, 0.13, 2), "z", z - 0.04, z + 0.04)
            for z in (0.42, PL_TOP - 0.36)]
    plaque = C.prism(C.rrect(PLQ_W, PLQ_H, 0.1, 2, 0, PLQ_Z), "y", PLQ_Y, -BLOCK / 2 + 0.02)
    ns.bevel(plaque, width=0.03, segments=1)
    ns.tag(plaque, "Plaque", C.GOLD, "Metal", recolor="plaque", smooth_angle=40)
    screws = []
    for sx in (-1, 1):
        s = ns.cyl(0.045, 0.03, verts=6, bevel=0.0)
        C.place(s, (sx * (PLQ_W / 2 - 0.12), PLQ_Y - 0.01, PLQ_Z), pitch=90)
        screws.append(s)
    cup = ns.lathe([(0.0, PL_TOP), (0.9, PL_TOP), (0.9, PL_TOP + 0.09), (0.75, PL_TOP + 0.17), (0.42, PL_TOP + 0.27),
                    (0.2, 2.2), (0.17, 2.55), (0.3, 2.7), (0.17, 2.86), (0.2, 3.0), (0.32, 3.08), (0.7, 3.3), (0.92, 3.7),
                    (1.0, 4.2), (1.02, 4.6), (1.09, 4.66), (1.09, 4.75), (1.0, 4.79), (0.88, 4.93), (0.55, 5.1), (0.25, 5.2),
                    (0.14, 5.28), (0.0, 5.3)], verts=14)
    C.part([cup], "Cup", C.GOLD, "Metal", can_collide=True, smooth_angle=50)
    gold = trim + screws
    for sx in (-1, 1):   # ear handles
        pts = [(sx * x, 0.0, z) for x, z in ((0.95, 4.48), (1.28, 4.53), (1.39, 4.18), (1.25, 3.74), (0.8, 3.4))]
        gold.append(C.pipe(C.round_path(pts, 0.16, 2), 0.105, sides=6))
    gold.append(C.rod((0, 0, 5.26), (0, 0, 5.76), 0.075, verts=6))
    gold.append(C.spheres([(0, 0, 5.36)], 0.13, segs=8, rings=5))
    star = C.prism(C.star_pts(STAR_R, STAR_R * 0.45, 0.0, STAR_Z), "y", -0.14, 0.14)
    ns.bevel(star, width=0.05, segments=1, angle=30)
    gold.append(star)
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=45)
    # ruby star inlay on the bowl front (thick enough to sink into the curved bowl at its tips)
    gem = C.prism(C.star_pts(0.44, 0.19, 0.0, 4.1), "y", -1.03, -0.84)
    ns.bevel(gem, width=0.025, segments=1, angle=30)
    C.part([gem], "StarInlay", C.CHERRY, smooth_angle=30)


SOCKETS = {"Plaque": ((0, PLQ_Y, PLQ_Z), 0.0)}
META = {"plaque_size": [PLQ_W, PLQ_H], "surfaces": [C.screen_meta("Plaque", PLQ_W, PLQ_H)],
        "roles": {"plaque": "Plaque (blank gold plate on the plinth front)"},
        "light_hint": {"type": "SpotLight", "above": True, "color": C.LAMP_WARM, "range": 14, "angle": 35}}

if __name__ == "__main__":
    C.run(build, "Lobby_GoldTrophy", sockets=SOCKETS, budget=2000, meta=META, backdrop="#3A2440")
