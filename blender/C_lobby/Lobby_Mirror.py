"""Lobby_Mirror — full-length cheval mirror on a stand (locker-room "try it on" mirror).

An arch-topped mirror (Glass, role "mirror", Front face) in a gilded frame swings between
two turned walnut posts on splayed feet, held by brass pivot knobs; five warm vanity bulbs
ride the top of the arch (Bulbs, Neon, role "lamp") for the dressing-room feel. The glass
is upright so the yaw-only socket describes it exactly.

Front = -Y, pivot = bottom-centre. Socket Mirror = centre of the glass face (facing front);
Stand = ground point in front of the mirror where a player stands to look (facing the
mirror, yaw 180).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
GW, GH = 2.3, 5.2               # glass (arch included)
GZ0 = 0.75                      # glass bottom
PX = GW / 2 + 0.55              # post centre x
MIRROR = "#C6D3D8"


def arch(w, h, z0, n=8):
    """Arch-topped panel outline (x, z): straight sides, semicircular top."""
    r = w / 2
    zs = z0 + h - r
    pts = [(-r, z0), (r, z0)]
    for k in range(n + 1):
        a = math.pi * k / n
        pts.append((r * math.cos(a), zs + r * math.sin(a)))
    return pts


def build():
    frame = C.ring_slab(arch(GW + 0.5, GH + 0.5, GZ0 - 0.25), arch(GW, GH, GZ0), "y", -0.14, 0.14)
    ns.bevel(frame, width=0.05, segments=1, angle=50)
    C.part([frame], "Frame", C.GOLD, "Metal", smooth_angle=40)
    back = C.prism(arch(GW + 0.06, GH + 0.06, GZ0 - 0.03), "y", 0.02, 0.1)
    C.part([back], "Backing", C.WOOD_DARK, "Wood", smooth_angle=40)
    glass = C.prism(arch(GW, GH, GZ0), "y", -0.06, 0.02)
    ns.tag(glass, "Glass", MIRROR, "Glass", recolor="mirror", cast_shadow=False, smooth_angle=None)

    wood = []
    pz = GZ0 + 2.9                       # pivot height
    for sx in (-1, 1):
        x = sx * PX
        wood.append(ns.lathe([(0.16, 0.0), (0.16, 0.25), (0.1, 0.4), (0.12, 2.0), (0.09, pz - 0.2), (0.15, pz),
                              (0.0, pz + 0.35)], verts=8, loc=(x, 0, 0.35)))
        wood.append(ns.box((0.32, 2.3, 0.22), loc=(x, 0, 0.2), bevel=0.08, segments=1))
    C.part(wood, "Stand", C.WOOD, "Wood", can_collide=True, smooth_angle=50)
    brass = []
    for sx in (-1, 1):
        k = ns.sphere(0.17, loc=(sx * (PX - 0.28), 0, pz + 0.35), segs=8, rings=5)
        brass.append(k)
        brass.append(C.rod((sx * (GW / 2 + 0.2), 0, pz + 0.35), (sx * PX, 0, pz + 0.35), 0.06, verts=6))
        for sy in (-1, 1):
            brass.append(ns.sphere(0.12, loc=(sx * PX, sy * 1.05, 0.12), segs=6, rings=4))
    C.part(brass, "Brass", C.BRASS, "Metal", smooth_angle=50)

    bulbs = []
    r = GW / 2 + 0.25
    zs = GZ0 + GH - GW / 2
    for k in range(5):
        a = math.pi * (0.1 + 0.8 * k / 4)
        bulbs.append(ns.sphere(0.15, loc=(r * math.cos(a), -0.18, zs + r * math.sin(a)), segs=6, rings=4))
    ns.tag(C.merge(bulbs, "Bulbs"), "Bulbs", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)


GLASS_CZ = GZ0 + GH / 2
SOCKETS = {"Mirror": ((0, -0.06, GLASS_CZ), 0.0), "Stand": ((0, -3.0, 0), 180.0)}
META = {"glass_size": [GW, GH], "surfaces": [{"part": "Glass", "face": "Front", "screen_size": [GW, GH]}],
        "roles": {"mirror": "Glass", "lamp": "Bulbs"}}

if __name__ == "__main__":
    C.run(build, "Lobby_Mirror", sockets=SOCKETS, meta=META)
