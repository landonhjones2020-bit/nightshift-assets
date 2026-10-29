"""Lobby_Jukebox — classic arched neon jukebox for the VIP lounge (3.1 wide x 5.1 tall).

Walnut arched cabinet on a chrome plinth. A hot-pink bubble tube runs up both front edges
and over the arch (TubePink) and a cyan tube follows the record window (TubeCyan); both
are Neon with role "neon". Through the arched glass window (Window, Glass) you see a black
record with a gold label and a chrome tone arm. Below: a cream selector strip with two rows
of chrome buttons under a mustard title band, and a red-orange speaker grille behind
chrome bars. Chrome finial on top.

Front = -Y, pivot = bottom-centre. Socket Prompt = in front of the selector strip;
Speaker = grille centre (attach the music Sound / a light).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 3.0, 4.6, 1.9
Z0 = 0.3
FY = -D / 2
WIN_W, WIN_H, WIN_Z = 1.9, 1.85, 2.6
WALNUT = "#6B3F2A"
BLACK = "#141416"


def build():
    body = C.prism(C.arch(W, H, Z0, n=10), "y", FY, -FY)
    ns.boolean(body, C.prism(C.arch(WIN_W, WIN_H, WIN_Z, n=8), "y", FY - 0.1, FY + 0.38))
    ns.bevel(body, width=0.08, segments=1, angle=50)
    C.part([body], "Cabinet", WALNUT, "Wood", can_collide=True, smooth_angle=40)
    plinth = ns.box((W + 0.12, D + 0.12, Z0), loc=(0, 0, Z0 / 2), bevel=0.05, segments=1)

    # window contents: back plate, record, label, tone arm, then the glass
    wy = FY + 0.38
    rec = ns.cyl(0.72, 0.04, verts=20, bevel=0.0)
    C.place(rec, (0, wy - 0.06, WIN_Z + 0.85), pitch=90)
    C.part([rec], "Record", BLACK, smooth_angle=None)
    label = ns.cyl(0.24, 0.03, verts=12, bevel=0.0)
    C.place(label, (0, wy - 0.09, WIN_Z + 0.85), pitch=90)
    chrome = [plinth, C.rod((0.85, wy - 0.12, WIN_Z + 1.45), (0.3, wy - 0.12, WIN_Z + 0.95), 0.04, verts=5),
              ns.cyl(0.09, 0.08, loc=(0.85, wy - 0.12, WIN_Z + 1.45), rot=(90, 0, 0), verts=8, bevel=0.0)]
    glass = C.prism(C.arch(WIN_W, WIN_H, WIN_Z, n=8), "y", FY + 0.04, FY + 0.08)
    ns.tag(glass, "Window", "#B9DCE6", "Glass", transparency=0.7, cast_shadow=False, smooth_angle=None)

    # selector strip (slanted cream band), buttons, title band
    sel = C.prism([(FY - 0.02, 1.95), (FY + 0.05, 1.95), (FY + 0.05, 2.5), (FY - 0.22, 2.42)], "x", -1.2, 1.2)
    ns.bevel(sel, width=0.03, segments=1)
    C.part([sel], "Selector", C.CREAM, smooth_angle=40)
    for row in range(2):
        for k in range(6):
            x = -0.95 + k * 0.38
            z = 2.04 + row * 0.17
            y = FY - 0.04 - (z - 1.95) / 0.47 * 0.17
            chrome.append(ns.box((0.24, 0.06, 0.1), loc=(x, y - 0.02, z + 0.04), rot=(-20, 0, 0), bevel=0.0))
    title = ns.box((2.3, 0.06, 0.12), loc=(0, FY - 0.2, 2.47), rot=(-20, 0, 0), bevel=0.0)
    # speaker grille
    grille_bg = ns.box((2.0, 0.05, 1.25), loc=(0, FY - 0.0, 1.12), bevel=0.0)
    C.part([grille_bg], "Grille", C.BRAND, "Fabric", smooth_angle=None)
    chrome.append(C.ring_slab(C.rrect(2.2, 1.45, 0.2, 2, 0, 1.12), C.rrect(2.0, 1.25, 0.15, 2, 0, 1.12), "y", FY - 0.08,
                              FY + 0.03))
    for k in range(5):
        chrome.append(ns.cyl(0.05, 1.25, loc=(-0.72 + k * 0.36, FY - 0.06, 1.12), verts=6, bevel=0.0))
    chrome.append(ns.cyl(0.14, 0.25, loc=(0, -0.2, Z0 + H + 0.06), verts=8, radius_top=0.08, bevel=0.0))
    chrome.append(ns.sphere(0.13, loc=(0, -0.2, Z0 + H + 0.25), segs=8, rings=5))
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    C.part([label, title], "Gold", C.MUSTARD, smooth_angle=40)

    # bubble tubes
    outer = [(x, FY - 0.08, z) for x, z in C.arch_path(W - 0.32, H - 0.22, Z0 + 0.15, n=10)]
    pink = C.pipe(outer, 0.14, sides=8)
    ns.tag(pink, "TubePink", C.PINK, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)
    inner = [(x, FY - 0.06, z) for x, z in C.arch_path(WIN_W + 0.36, WIN_H + 0.2, WIN_Z - 0.08, n=8)]
    cyan = C.pipe(inner, 0.09, sides=6)
    ns.tag(cyan, "TubeCyan", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)


SOCKETS = {"Prompt": ((0, FY - 1.2, 2.3), 0.0), "Speaker": ((0, FY - 0.1, 1.12), 0.0)}
META = {"roles": {"neon": "TubePink, TubeCyan"},
        "light_hint": {"type": "PointLight", "color": C.PINK, "range": 10, "brightness": 1.2}}

if __name__ == "__main__":
    C.run(build, "Lobby_Jukebox", sockets=SOCKETS, meta=META)
