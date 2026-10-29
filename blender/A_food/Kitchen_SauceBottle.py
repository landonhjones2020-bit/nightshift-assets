"""Kitchen_SauceBottle — diner squeeze bottle for the sauce rail (A_food batch).

~0.35 wide x 1.1 tall, pivot bottom-centre, label facing -Y. One mesh for all four sauces: the
client recolours Body (role "sauce_body") and Cap (role "sauce_cap") per sauce; Label stays
cream. Default colours = mustard. Suggested per-sauce colours: _common.SAUCES.
Exported to the A_food batch but stored under Assets.Kitchen (group "Kitchen"), like Kitchen_Crate.
Run:  bpyenv/bin/python blender/A_food/Kitchen_SauceBottle.py   (NS_EXPORT=1 export)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402


def build():
    s = C.SAUCES["mustard"]
    C.squeeze_bottle(s["body"], s["cap"])
    C.check_bounds("Kitchen_SauceBottle", layer=False)


if __name__ == "__main__":
    C.run(build, "Kitchen_SauceBottle", meta_=None, pivot=None, group="Kitchen")
