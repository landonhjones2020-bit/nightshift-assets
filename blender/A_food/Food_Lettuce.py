"""Food_Lettuce — lettuce layer (A_food batch).

Two layered leaves: a darker base leaf along the whole roll and a lighter inner leaf on top, both
with bumpy, ruffled (frilly) edges that wave up and down and hang just past the bread; a pale
midrib marks the inner leaf. Parts: LeafDark, LeafLight, Rib.
Run:  bpyenv/bin/python blender/A_food/Food_Lettuce.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
DARK, LIGHT, RIB = "#3FA535", "#8CD655", "#D9F2A6"


def leaves(scale_a=1.0, two=True):
    base = C.frilly_leaf("LeafDark", 1.02 * scale_a, 0.435, N=48, frills=14, seed=2, amp_z=0.05, amp_xy=0.1)
    C.drape(base, C.overhang_droop(k=0.5, kx=0.3))
    ns.tag(base, "LeafDark", DARK, "SmoothPlastic", smooth_angle=80)
    top = C.frilly_leaf("LeafLight", 0.76 * scale_a, 0.37, N=40, frills=10, seed=5, amp_z=0.035, lift=0.035,
                        amp_xy=0.07)
    top.location.x = 0.12 * scale_a
    top.rotation_euler.z = 0.06
    ns.apply_all(top)
    ns.tag(top, "LeafLight", LIGHT, "SmoothPlastic", smooth_angle=80)
    tree = C.bvh(top)
    pts = [(-0.62 * scale_a + 0.12 * scale_a + 1.3 * scale_a * t, 0.03 * C.math.sin(5 * t)) for t in
           [i / 6 for i in range(7)]]
    rib = C.surface_ribbon("Rib", tree, pts, [0.03, 0.05, 0.055, 0.05, 0.045, 0.035, 0.02], lift=0.01, depth=0.02)
    ns.tag(rib, "Rib", RIB, "SmoothPlastic", smooth_angle=60)
    return base, top, rib


def build():
    parts = leaves()
    C.check_bounds("Food_Lettuce", list(parts))


def icon():
    leaves(scale_a=0.62)


if __name__ == "__main__":
    C.run(build, "Food_Lettuce", C.meta("lettuce", 0.09),
          icon=("Ingredient_lettuce", icon, {"pitch": 42.0}))
