"""Shop_HeatLamp — pass-through heat-lamp bar that hangs under the counter header.

Two header plates with drop rods carry a chrome rail; three chrome stems hang from it to
red-orange enamel shades (white insides, chrome socket caps), each with a glowing amber
heat bulb (part Bulbs, Neon, role "lamp").
PIVOT = TOP (the header plates' top face, z = 0); everything hangs below.
Sockets Lamp1..Lamp3 = bulb centres left to right (for SpotLights pointing down).
~6 x 2.2 x 1.2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
RAIL_Z = -0.5
SHADE_TOP = -1.18
XS = (-2.0, 0.0, 2.0)
BULB_Z = SHADE_TOP - 0.62


def build():
    chrome = []
    for sx in (-1, 1):
        chrome.append(ns.box((0.34, 0.42, 0.06), loc=(sx * 2.75, 0, -0.03), bevel=0.0))
        chrome.append(C.rod((sx * 2.75, 0, -0.06), (sx * 2.75, 0, RAIL_Z), 0.04, verts=6))
    chrome.append(ns.cyl(0.075, 5.9, loc=(0, 0, RAIL_Z), rot=(0, 90, 0), verts=8, bevel=0.0))
    for x in XS:
        chrome.append(C.rod((x, 0, RAIL_Z), (x, 0, SHADE_TOP + 0.02), 0.032, verts=6))
        chrome.append(ns.cyl(0.11, 0.16, loc=(x, 0, SHADE_TOP - 0.02), verts=8, bevel=0.0))
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=50)

    shades, inners, bulbs = [], [], []
    for x in XS:
        # thin enamel shell: red-orange outside, white inside, meeting at the rim (no caps)
        shades.append(C.lathe_open([(0.1, 0.0), (0.28, -0.12), (0.48, -0.42), (0.58, -0.72)], verts=10,
                                   loc=(x, 0, SHADE_TOP), normals="out"))
        inners.append(C.lathe_open([(0.1, -0.02), (0.27, -0.14), (0.47, -0.43), (0.58, -0.72)], verts=10,
                                   loc=(x, 0, SHADE_TOP), normals="in"))
        bulbs.append(ns.sphere(0.2, loc=(x, 0, BULB_Z), scale=(1, 1, 1.15), segs=7, rings=4))
    C.part(shades, "Shades", C.BRAND, smooth_angle=60)
    C.part(inners, "ShadeInner", "#F4F0E6", smooth_angle=60)
    C.part(bulbs, "Bulbs", "#FF9A4A", "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)


SOCKETS = {f"Lamp{i + 1}": ((x, 0, BULB_Z), 0.0) for i, x in enumerate(XS)}
META = {"pivot": "top (header plates' top face): hang under the counter header",
        "light_hint": {"type": "SpotLight", "face": "Bottom", "color": "#FFB27A", "range": 8, "angle": 70,
                       "sockets": ["Lamp1", "Lamp2", "Lamp3"]}}

if __name__ == "__main__":
    C.run(build, "Shop_HeatLamp", mount="hang", sockets=SOCKETS, budget=800, meta=META)
