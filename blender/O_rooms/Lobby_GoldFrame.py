"""Lobby_GoldFrame — ornate gilded picture frame (4 W x 5 H x 0.3 D), wall-mounted.

A stepped gilded moulding: an antique-gold outer band, a raised bright-gold ridge with a row of
pearl beads, an antique-gold inner lip and a cream linen liner around the picture. Rococo shell
ornaments sit on the four corners, a bigger fan crest rises from the top centre and small shell
lozenges mark the middle of each side and the bottom. The picture area is a dark canvas (Screen,
role "screen", Front face) where the game draws the painting / portrait.

Wall-mounted: back face on the wall plane (Blender y = 0), front -Y; pivot = bottom-centre of
the back face. Socket Screen = centre of the picture face (yaw 0).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
W, H, T = 4.0, 5.0, 0.3
ZC = 2.33                      # frame centre height
FW, FH = 3.7, 4.42             # frame body outer size
PIC_W, PIC_H = 2.5, 3.2        # picture (screen) size
PIC_Y = -0.06                  # picture face
ANTIQUE = "#B98A32"
CANVAS = "#2A2030"
LINEN = "#DCD0B8"


def ring(ow, oh, iw, ih, y0, y1, r_o=0.12, r_i=0.06, bevel=0.0):
    o = C.ring_slab(C.rrect(ow, oh, r_o, 2, 0, ZC), C.rrect(iw, ih, r_i, 2, 0, ZC), "y", y0, y1)
    if bevel:
        ns.bevel(o, width=bevel, segments=1, angle=50)
    return o


def shell(cx, cz, r, a_mid, span=110.0, lobes=5, y0=-0.3, y1=-0.12, bevel=True):
    """Fan / shell ornament: lobed fan centred on (cx, cz) opening toward a_mid (degrees)."""
    pts = [(cx, cz)]
    n = lobes * 2
    for k in range(n + 1):
        a = math.radians(a_mid - span / 2 + span * k / n)
        rr = r if k % 2 == 0 else r * 0.72
        pts.append((cx + rr * math.cos(a), cz + rr * math.sin(a)))
    o = C.prism(pts, "y", y0, y1)
    if bevel:
        ns.bevel(o, width=0.03, segments=1, angle=30)
    return o


def build():
    antique = [ring(FW, FH, FW - 0.36, FH - 0.36, -0.2, 0.0, bevel=0.03),                       # outer band
               ring(PIC_W + 0.56, PIC_H + 0.56, PIC_W + 0.24, PIC_H + 0.24, -0.17, -0.02, 0.06, 0.04, 0.02)]  # inner lip
    C.part(antique, "Antique", ANTIQUE, "Metal", smooth_angle=45)
    gold = [ring(FW - 0.3, FH - 0.3, PIC_W + 0.5, PIC_H + 0.5, -0.27, -0.12, 0.1, 0.06, 0.05)]    # raised ridge
    liner = ring(PIC_W + 0.26, PIC_H + 0.26, PIC_W - 0.02, PIC_H - 0.02, -0.09, -0.03, 0.04, 0.02)
    C.part([liner], "Liner", LINEN, "Fabric", smooth_angle=None)
    # pearl beads along the ridge
    bx, bz = (FW - 0.3 + PIC_W + 0.5) / 4, (FH - 0.3 + PIC_H + 0.5) / 4     # ridge centre-line half sizes
    pts = []
    for k in range(5):
        x = -bx + 2 * bx * (k + 0.5) / 5
        pts += [(x, -0.26, ZC - bz), (x, -0.26, ZC + bz)]
    for k in range(1, 7):
        z = ZC - bz + 2 * bz * k / 7
        pts += [(-bx, -0.26, z), (bx, -0.26, z)]
    gold.append(C.domes(pts, 0.045, axis=(0, -1, 0), segs=5, rings=2))
    # ornaments: corner shells, top crest, side / bottom lozenges
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * (FW / 2 - 0.16), ZC + sz * (FH / 2 - 0.16)
            a = math.degrees(math.atan2(sz, sx))
            gold.append(shell(cx, cz, 0.3, a, lobes=4))
    gold.append(shell(0.0, ZC + FH / 2 - 0.18, 0.63, 90.0, span=170, lobes=6))
    gold.append(shell(0.0, ZC - FH / 2 + 0.16, 0.28, -90.0, span=150, lobes=3, bevel=False))
    for sx in (-1, 1):
        gold.append(shell(sx * (FW / 2 - 0.16), ZC, 0.26, 0.0 if sx > 0 else 180.0, span=150, lobes=3, bevel=False))
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=45)
    # picture canvas (the screen) + backing board
    scr = ns.box((PIC_W, 0.04, PIC_H), loc=(0, PIC_Y + 0.02, ZC), bevel=0.0)
    ns.tag(scr, "Screen", CANVAS, recolor="screen", cast_shadow=False, smooth_angle=None)


SOCKETS = {"Screen": ((0, PIC_Y, ZC), 0.0)}
META = {"mount": "wall", "pivot": "bottom-centre of the back face (on the wall plane)", "wall_back_z": 0.0,
        "screen_size": [PIC_W, PIC_H], "surfaces": [C.screen_meta("Screen", PIC_W, PIC_H)],
        "screen_hint": "picture area (dark canvas): draw the painting / portrait image here",
        "roles": {"screen": "Screen (the picture area)"}}

if __name__ == "__main__":
    C.run(build, "Lobby_GoldFrame", sockets=SOCKETS, mount="wall", budget=2000, pivot=(0, 0, 0), meta=META,
          backdrop="#3A2440")
