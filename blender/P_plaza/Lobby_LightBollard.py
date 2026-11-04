"""Lobby_LightBollard — short plaza path light (1 x 3 x 1).

A cast-stone footing, a flared navy shoe and a tapered navy post with a mustard collar, a warm
glowing lantern band (LampGlass, Neon, role "lamp") caged by four navy bars, and a red-orange
mushroom cap with a mustard finial. Footing and post collide.

Front = -Y (round, reads the same from every side), pivot = bottom-centre.
Socket Light = centre of the glowing band (put the PointLight here).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

GLASS_Z = (2.02, 2.56)
CAP_Z = 2.56


def build():
    stone = [C.prism(C.rrect(1.0, 1.0, 0.16, 2), "z", 0.0, 0.2)]
    ns.bevel(stone[0], width=0.05, segments=1)
    shoe = ns.lathe([(0.42, 0.18), (0.42, 0.26), (0.33, 0.42), (0.25, 0.56), (0.0, 0.56)], verts=8)
    post = C.rod((0, 0, 0.5), (0, 0, GLASS_Z[0] + 0.04), 0.23, verts=8, r_top=0.19)
    collar_lo = ns.lathe([(0.3, GLASS_Z[0] - 0.12), (0.34, GLASS_Z[0] - 0.04), (0.34, GLASS_Z[0] + 0.02),
                          (0.0, GLASS_Z[0] + 0.02)], verts=8)
    band = ns.cyl(0.255, 0.1, loc=(0, 0, 1.55), verts=8, bevel=0.0)
    ring = ns.cyl(0.262, 0.05, loc=(0, 0, 0.62), verts=8, bevel=0.0)
    glass = ns.lathe([(0.0, GLASS_Z[0]), (0.27, GLASS_Z[0]), (0.31, (GLASS_Z[0] + GLASS_Z[1]) / 2), (0.27, GLASS_Z[1]),
                      (0.0, GLASS_Z[1])], verts=10)
    bars = []
    for k in range(4):
        p = C.yaw_point((0.3, 0, 0), 45 + 90 * k)
        bars.append(C.rod((p[0] * 0.92, p[1] * 0.92, GLASS_Z[0] - 0.02), (p[0] * 1.06, p[1] * 1.06, (GLASS_Z[0] + GLASS_Z[1]) / 2),
                          0.04, verts=4))
        bars.append(C.rod((p[0] * 1.06, p[1] * 1.06, (GLASS_Z[0] + GLASS_Z[1]) / 2), (p[0] * 0.92, p[1] * 0.92, GLASS_Z[1] + 0.02),
                          0.04, verts=4))
    cap = ns.lathe([(0.2, CAP_Z - 0.02), (0.46, CAP_Z), (0.47, CAP_Z + 0.07), (0.36, CAP_Z + 0.22), (0.16, CAP_Z + 0.33),
                    (0.0, CAP_Z + 0.36)], verts=10)
    finial = ns.sphere(0.075, loc=(0, 0, 2.93), segs=6, rings=4)
    stem = C.rod((0, 0, CAP_Z + 0.3), (0, 0, 2.88), 0.04, verts=4)

    C.part(stone, "Footing", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part([shoe, post, collar_lo], "Post", C.STEEL_NAVY, "Metal", can_collide=True, smooth_angle=50)
    C.part(bars + [stem], "Cage", C.STEEL_NAVY, "Metal", smooth_angle=50)
    C.part([band, ring, finial], "Collars", C.MUSTARD, "Metal", smooth_angle=50)
    C.part([cap], "Cap", C.BRAND, smooth_angle=50)
    ns.tag(glass, "LampGlass", C.BULB, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=60)


SOCKETS = {"Light": ((0.0, 0.0, (GLASS_Z[0] + GLASS_Z[1]) / 2), 0.0)}
META = {"roles": {"lamp": "LampGlass"},
        "light_hint": {"type": "PointLight", "at": "Socket_Light", "color": C.BULB, "range": 9, "brightness": 0.8}}

if __name__ == "__main__":
    C.run(build, "Lobby_LightBollard", sockets=SOCKETS, meta=META, budget=2000, pivot=(0.0, 0.0, 0.0), far=True,
          far_kw={"dist": 16.0})
