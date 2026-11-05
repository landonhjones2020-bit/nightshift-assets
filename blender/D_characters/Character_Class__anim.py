"""Character_Class__anim — writes anim/ClassCast.lua: the six Display_<id> clips of the class
characters (see _classes.py). Not an asset; run after changing a pose."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import _classes as K  # noqa: E402

if __name__ == "__main__":
    C.ns.reset()
    arm = C.make_rig()
    acts = [K.display_clip(arm, cid) for cid in K.ORDER]
    print("[ClassCast] anim:", C.ns.export_animations(arm, K.RIG, acts))
