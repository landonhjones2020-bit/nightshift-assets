"""Food_Mustard_Ribbon — squeezed mustard ribbon (A_food batch).

A thick glossy bead zig-zagging along the roll (X), flat underside at Z 0, tapered ends.
Part: Sauce.
Icon: Kitchen_SauceBottle in this sauce's colours with a little squiggle in front.
Run:  bpyenv/bin/python blender/A_food/Food_Mustard_Ribbon.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SAUCE = "mustard"


def build():
    C.sauce_ribbon(SAUCE)
    C.check_bounds("Food_Mustard_Ribbon")


def icon():
    C.sauce_icon(SAUCE)


if __name__ == "__main__":
    C.run(build, "Food_Mustard_Ribbon", C.meta(SAUCE, 0.05),
          icon=("Ingredient_mustard", icon, {"pitch": 24.0, "yaw": -30.0, "margin": 0.86}))
