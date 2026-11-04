"""Food_BBQSauce_Ribbon — squeezed BBQ sauce ribbon (M_food batch).

A thick glossy bead zig-zagging along the roll (X), flat underside at Z 0, tapered ends — the A_food
sauce bead (same path and profile as Food_Chipotle_Ribbon) in dark brown-red. Part: Sauce.
Icon: Kitchen_SauceBottle in this sauce's colours (_common.SAUCES) with a little squiggle in front.
Run:  bpyenv/bin/python blender/M_food/Food_BBQSauce_Ribbon.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SAUCE = "bbq_sauce"


def build():
    C.sauce_ribbon(SAUCE)
    C.check_bounds("Food_BBQSauce_Ribbon")


def icon():
    C.sauce_icon(SAUCE)


if __name__ == "__main__":
    C.run(build, "Food_BBQSauce_Ribbon", C.meta(SAUCE, 0.05),
          icon=("Ingredient_bbq_sauce", icon, {"pitch": 24.0, "yaw": -30.0, "margin": 0.86}))
