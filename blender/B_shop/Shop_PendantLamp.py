"""Shop_PendantLamp — diner pendant lamp: red-orange enamel dome shade with a white inside,
chrome rim and cap, cloth cord ~2 studs to a ceiling canopy, warm bulb (part Bulb, Neon,
role "lamp"). Hang over booths and the counter.
PIVOT = top of the cord (the ceiling canopy's top face, z = 0); everything hangs below.
Socket Light = bulb centre.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
CORD = 2.1
SZ = -CORD - 0.15        # shade top (cap) z


def build():
    canopy = ns.cyl(0.32, 0.14, loc=(0, 0, -0.07), verts=14, radius_top=0.34, bevel=0.03, segments=1)
    cap = ns.cyl(0.13, 0.3, loc=(0, 0, SZ - 0.05), verts=10, bevel=0.03, segments=1)
    rim = ns.torus(0.84, 0.045, loc=(0, 0, SZ - 1.02), major_segs=24, minor_segs=5)
    C.part([canopy, cap, rim], "Chrome", C.CHROME, "Metal", smooth_angle=50)
    cord = C.pipe([(0, 0, -0.12), (0, 0, SZ + 0.08)], 0.035, sides=6)
    ns.tag(cord, "Cord", "#1C1C1F", "Fabric", smooth_angle=60)
    outer = ns.lathe([(0.12, 0.0), (0.3, -0.08), (0.6, -0.32), (0.78, -0.62), (0.86, -0.86), (0.8, -0.86),
                      (0.72, -0.64), (0.55, -0.36), (0.28, -0.13), (0.1, -0.06)], verts=20, loc=(0, 0, SZ - 0.18))
    ns.tag(outer, "Shade", C.BRAND, recolor="shade", smooth_angle=60)
    inner = ns.lathe([(0.09, -0.075), (0.27, -0.145), (0.54, -0.375), (0.71, -0.655), (0.79, -0.858),
                      (0.77, -0.858), (0.69, -0.655), (0.52, -0.38), (0.26, -0.16), (0.08, -0.09)],
                     verts=20, loc=(0, 0, SZ - 0.18))
    ns.tag(inner, "ShadeInner", "#F4F0E6", smooth_angle=60)
    bulb = ns.sphere(0.2, loc=(0, 0, SZ - 0.62), scale=(1, 1, 1.15), segs=10, rings=7)
    ns.tag(bulb, "Bulb", "#FFE3A8", "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)


META = {"pivot": "top of the cord (ceiling canopy top)", "drop": round(-SZ + 0.9, 2),
        "light_hint": {"type": "SpotLight", "face": "Bottom", "color": "#FFD9A0", "range": 14, "angle": 80}}

if __name__ == "__main__":
    C.run_hanging(build, "Shop_PendantLamp", pivot=(0, 0, 0), meta=META, sockets={"Light": ((0, 0, SZ - 0.62), 0.0)})
