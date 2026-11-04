"""Lobby_Chandelier — two-tier gold chandelier for the VIP Lounge (6 dia x 5 H), ceiling-hung.

A gold ceiling canopy and a beaded rod drop to a turned gold column: an urn carrying four upper
S-arms and a hub bowl carrying eight lower S-arms. Every arm ends in a gold candle cup with a
cream candle sleeve and a warm flame-shaped candle bulb (Bulbs, Neon, role "lamp"). Crystal
(Glass) bead swags hang between the lower cups, a crystal drop hangs under each lower cup and a
big crystal drop finishes the bottom finial.

PIVOT = TOP of the canopy (z = 0, flush on the ceiling); everything hangs below. Socket Light =
the chandelier's centre (bbox centre, between the two candle tiers) for a warm PointLight.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
LOW_N, LOW_R = 8, 2.8
UP_N, UP_R = 4, 1.6
CANDLE_H = 0.3
SLEEVE = "#F3EEE2"


def radial(path_rz, a_deg):
    a = math.radians(a_deg)
    return [(r * math.cos(a), r * math.sin(a), z) for r, z in path_rz]


def bipyramid(c, r, h_up, h_dn, sides=4, rot=0.0):
    """Crystal bead / drop: a double pyramid (sides x 2 triangles)."""
    bm = C.bmesh.new()
    c = Vector(c)
    ring = [bm.verts.new(c + Vector((r * math.cos(rot + 2 * math.pi * i / sides), r * math.sin(rot + 2 * math.pi * i / sides), 0)))
            for i in range(sides)]
    top = bm.verts.new(c + Vector((0, 0, h_up)))
    bot = bm.verts.new(c + Vector((0, 0, -h_dn)))
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new([ring[i], ring[j], top])
        bm.faces.new([ring[j], ring[i], bot])
    C.bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, "Crystal")


def build():
    gold, sleeves, flames, crystals = [], [], [], []
    gold.append(ns.lathe([(0.0, 0.0), (0.55, 0.0), (0.52, -0.08), (0.3, -0.22), (0.1, -0.3), (0.0, -0.3)], verts=10))
    gold.append(C.rod((0, 0, -0.28), (0, 0, -1.35), 0.05, verts=6))
    gold.append(C.spheres([(0, 0, -0.85)], 0.11, segs=6, rings=4))
    # turned column: urn (upper arms) -> neck -> hub bowl (lower arms) -> finial
    col = [(0.0, -1.3), (0.12, -1.3), (0.09, -1.55), (0.26, -1.85), (0.3, -2.1), (0.2, -2.35), (0.1, -2.55), (0.14, -2.85),
           (0.42, -3.15), (0.46, -3.35), (0.3, -3.55), (0.14, -3.75), (0.2, -4.05), (0.08, -4.45), (0.0, -4.55)]
    gold.append(ns.lathe(col, verts=8))
    tips = []
    # lower tier: S-arms from the hub bowl out and up to the candle cups
    for k in range(LOW_N):
        a = 360.0 * k / LOW_N
        path = [(0.4, -3.3), (1.0, -3.65), (1.88, -3.63), (2.53, -3.38), (LOW_R, -3.08)]
        gold.append(C.pipe(radial(path, a), 0.055, sides=4))
        tips.append((a, LOW_R, -3.08, True))
    # upper tier: shorter arms from the urn, between the lower ones
    for k in range(UP_N):
        a = 360.0 * k / UP_N + 22.5
        path = [(0.25, -2.12), (0.75, -2.37), (1.28, -2.3), (UP_R, -2.02)]
        gold.append(C.pipe(radial(path, a), 0.05, sides=4))
        tips.append((a, UP_R, -2.02, False))
    for a, r, z, low in tips:
        x, y, _ = radial([(r, z)], a)[0]
        gold.append(ns.cyl(0.19, 0.06, loc=(x, y, z + 0.03), verts=6, bevel=0.0))
        gold.append(ns.cyl(0.09, 0.08, loc=(x, y, z + 0.1), verts=5, bevel=0.0))
        sleeves.append(ns.cyl(0.065, CANDLE_H, loc=(x, y, z + 0.14 + CANDLE_H / 2), verts=5, bevel=0.0))
        flames.append((x, y, z + 0.14 + CANDLE_H + 0.1))
        if low:   # crystal drop under each lower cup
            crystals.append(bipyramid((x, y, z - 0.16), 0.07, 0.07, 0.17, sides=4, rot=math.radians(a)))
    # crystal bead swags between neighbouring lower cups
    for k in range(LOW_N):
        a0, a1 = 360.0 * k / LOW_N, 360.0 * (k + 1) / LOW_N
        p0 = Vector(radial([(LOW_R - 0.05, -3.12)], a0)[0])
        p1 = Vector(radial([(LOW_R - 0.05, -3.12)], a1)[0])
        for p in C.catenary(p0, p1, 0.5, n=5)[1:-1]:
            crystals.append(bipyramid(p, 0.065, 0.07, 0.07, sides=4))
    crystals.append(bipyramid((0, 0, -4.7), 0.14, 0.12, 0.3, sides=6))
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=50)
    C.part(sleeves, "Candles", SLEEVE, smooth_angle=40)
    ns.tag(C.spheres(flames, 0.085, segs=6, rings=3, scale=(1, 1, 1.6)), "Bulbs", C.LAMP_WARM, "Neon", recolor="lamp",
           cast_shadow=False, smooth_angle=70)
    ns.tag(C.merge(crystals, "Crystals"), "Crystals", C.CRYSTAL, "Glass", transparency=0.25, cast_shadow=False, smooth_angle=None)


SOCKETS = {"Light": ((0, 0, -2.5), 0.0)}
META = {"mount": "ceiling", "pivot": "top of the ceiling canopy (hangs below)", "drop": 5.0, "candles": LOW_N + UP_N,
        "roles": {"lamp": "Bulbs (12 candle bulbs)"},
        "light_hint": {"type": "PointLight", "at": "Socket_Light", "color": C.LAMP_WARM, "range": 22, "brightness": 1.5}}

if __name__ == "__main__":
    C.run(build, "Lobby_Chandelier", sockets=SOCKETS, mount="hang", budget=2000, pivot=(0, 0, 0), meta=META,
          backdrop="#3A2440")
