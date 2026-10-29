"""Food_Bacon — crispy bacon layer (A_food batch).

Three wavy strips laid along the roll; each is a crisp meat ribbon with two lengthwise fat
stripes. Parts: Meat (cooked red-brown), Fat (cream-pink stripes).
Run:  bpyenv/bin/python blender/A_food/Food_Bacon.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402


def build():
    m = C.bacon_strips()
    C.check_bounds("Food_Bacon", m)


def icon():
    C.bacon_strips(ys=(-0.17, 0.17), length=1.6, seed=4, amp=0.045)


if __name__ == "__main__":
    C.run(build, "Food_Bacon", C.meta("bacon", 0.08),
          icon=("Ingredient_bacon", icon, {"pitch": 34.0}))
