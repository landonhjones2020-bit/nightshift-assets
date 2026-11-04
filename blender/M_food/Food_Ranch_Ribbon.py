"""Food_Ranch_Ribbon — squeezed ranch ribbon (M_food batch).

A thick glossy bead zig-zagging along the roll (X), flat underside at Z 0, tapered ends — the A_food
sauce bead (same path and profile as the other ribbons) in creamy white, dotted with tiny green herb
flecks along the crest (they are what tells it from mayo). Parts: Sauce, Herbs.
Icon: Kitchen_SauceBottle in this sauce's colours (_common.SAUCES) with a flecked squiggle in front.
Run:  bpyenv/bin/python blender/M_food/Food_Ranch_Ribbon.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
SAUCE = "ranch"
HERB = C.SAUCES[SAUCE]["herb"]


def build():
    s = C.sauce_ribbon(SAUCE)
    C.herb_flecks("Herbs", s, C.zigzag_path(), HERB)
    C.check_bounds("Food_Ranch_Ribbon")


def icon():
    C.sauce_icon(SAUCE)
    sq = bpy.data.objects["Sauce"]          # the squiggle (scaled / turned, not applied)
    bpy.context.view_layer.update()
    path = [tuple(sq.matrix_world @ Vector(p)) for p in C.zigzag_path(x0=-0.3, x1=0.3, amp=0.1, period=0.3, n=26)]
    C.herb_flecks("Herbs", sq, path, HERB, every=2, side=0.03, size=(0.03, 0.02, 0.01))


if __name__ == "__main__":
    C.run(build, "Food_Ranch_Ribbon", C.meta(SAUCE, 0.05),
          icon=("Ingredient_ranch", icon, {"pitch": 24.0, "yaw": -30.0, "margin": 0.86}))
