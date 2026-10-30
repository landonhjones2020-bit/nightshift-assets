"""Shop_TallPendant — Shop_PendantLamp's diner pendant on a long cord for the 20-stud ceiling.

Chrome ceiling canopy, ~6.5 studs of black cloth cord, chrome cap, a red-orange enamel dome
shade (part Shade, role "shade", like Shop_PendantLamp) with a white inside and a chrome
rolled rim, and a warm bulb (part Bulb, Neon, role "lamp").
PIVOT = TOP of the canopy (z = 0, flush on the ceiling); everything hangs below.
Socket Light = just under the bulb (SpotLight facing down / PointLight).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
CORD = 6.5
SZ = -CORD - 0.2         # shade top (cap bottom) z
SH = 0.98                # shade height
V = 10                   # lathe segments


def build():
    canopy = ns.lathe([(0.0, 0.0), (0.36, 0.0), (0.34, -0.1), (0.16, -0.16), (0.0, -0.16)], verts=V)
    cap = ns.cyl(0.15, 0.32, loc=(0, 0, SZ + 0.1), verts=8, bevel=0.0)
    rim = C.lathe_ring([(0.94, SZ - SH + 0.02), (1.0, SZ - SH - 0.02), (0.95, SZ - SH - 0.05)], verts=V)
    sock = ns.cyl(0.09, 0.22, loc=(0, 0, SZ - 0.18), verts=6, bevel=0.0)
    C.part([canopy, cap, rim, sock], "Chrome", C.CHROME, "Metal", smooth_angle=50)
    cord = C.pipe([(0, 0, -0.14), (0, 0, SZ + 0.24)], 0.04, sides=4, cap=False)
    ns.tag(cord, "Cord", "#1C1C1F", "Fabric", smooth_angle=60)
    outer = C.lathe_open([(0.14, SZ), (0.38, SZ - 0.1), (0.7, SZ - 0.38), (0.9, SZ - 0.7), (0.97, SZ - SH)], verts=V)
    ns.tag(outer, "Shade", C.BRAND, recolor="shade", smooth_angle=60)
    inner = C.lathe_open([(0.13, SZ - 0.06), (0.36, SZ - 0.16), (0.67, SZ - 0.43), (0.86, SZ - 0.73), (0.93, SZ - SH)],
                         verts=V, outward=False)
    ns.tag(inner, "ShadeInner", "#F4F0E6", smooth_angle=60)
    bulb = ns.sphere(0.24, loc=(0, 0, SZ - 0.58), scale=(1, 1, 1.15), segs=8, rings=5)
    ns.tag(bulb, "Bulb", "#FFE3A8", "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)


LIGHT_Z = SZ - 0.58 - 0.24 * 1.15 - 0.08
SOCKETS = {"Light": ((0, 0, LIGHT_Z), 0.0)}
META = {"pivot": "top of the ceiling canopy (hangs below)", "drop": round(-(SZ - SH - 0.05), 2),
        "light_hint": {"type": "SpotLight", "face": "Bottom", "color": "#FFD9A0", "range": 16, "angle": 80}}

if __name__ == "__main__":
    C.run(build, "Shop_TallPendant", sockets=SOCKETS, pivot=(0, 0, 0), meta=META,
          preview=lambda a, o, r, s: C.dir_preview(a, o, r, s, [(-0.45, -1.0, -0.3), (0.35, -0.6, -1.0)]))
