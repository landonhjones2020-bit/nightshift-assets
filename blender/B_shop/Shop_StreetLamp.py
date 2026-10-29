"""Shop_StreetLamp — parking-lot cobra-head street light, 18.5 tall.

Concrete footing, tapered dark steel pole, curved arm reaching 4.6 forward (-Y), cobra-head
housing with a sodium-orange lens underneath (part Lens, Neon, role "lamp": the lighting
system flickers or kills it). Pivot = bottom-centre of the footing.
Socket Light = lens centre (attach a SpotLight facing down).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
POLE_H = 16.6
STEEL = "#3B4046"
SODIUM = "#FFB55E"
REACH = 4.6


def build():
    base = ns.cyl(0.75, 1.0, loc=(0, 0, 0.5), verts=12, radius_top=0.65, bevel=0.05, segments=1)
    ns.tag(base, "Footing", "#8E8D88", "Concrete", can_collide=True, smooth_angle=40)
    pole = ns.cyl(0.26, POLE_H, loc=(0, 0, 1.0 + POLE_H / 2), verts=10, radius_top=0.15, bevel=0.0)
    collar = ns.cyl(0.4, 0.5, loc=(0, 0, 1.25), verts=10, radius_top=0.3, bevel=0.03, segments=1)
    bolts = [ns.box((0.16, 0.16, 0.14), loc=(0.5 * c, 0.5 * s, 1.05), bevel=0.02, segments=1)
             for c, s in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    top = 1.0 + POLE_H
    arm = C.pipe([(0, 0, top - 0.6), (0, -0.3, top + 0.4), (0, -1.6, top + 0.95), (0, -REACH + 0.4, top + 1.05)],
                 0.12, sides=8, corner=0.7, corner_segs=3)
    cap = ns.sphere(0.17, loc=(0, 0, top), segs=8, rings=5)
    hx, hy, hz = 0, -REACH - 0.5, top + 1.0
    housing = ns.sphere(1.0, loc=(hx, hy, hz), scale=(0.78, 1.7, 0.45), segs=14, rings=8)
    ns.boolean(housing, ns.box((3, 4, 1), loc=(hx, hy, hz - 0.5), bevel=0.0))
    skirt = C.prism(C.ellipse_pts(0.76, 1.66, 16, hx, hy), "z", hz - 0.12, hz + 0.02)
    C.part([pole, collar, arm, cap, housing, skirt] + bolts, "Pole", STEEL, "Metal", can_collide=True, smooth_angle=50)
    lens = C.prism(C.ellipse_pts(0.6, 1.4, 16, hx, hy), "z", hz - 0.22, hz - 0.1)
    ns.bevel(lens, width=0.04, segments=1)
    ns.tag(lens, "Lens", SODIUM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=50)


META = {"height": round(1.0 + POLE_H + 1.4, 2), "reach": REACH, "light_hint": {"type": "SpotLight", "face": "Bottom",
        "color": SODIUM, "range": 40, "angle": 110, "brightness": 2}}

if __name__ == "__main__":
    C.run(build, "Shop_StreetLamp", meta=META,
          sockets={"Light": ((0, -REACH - 0.5, 1.0 + POLE_H + 1.0 - 0.24), 0.0)})
