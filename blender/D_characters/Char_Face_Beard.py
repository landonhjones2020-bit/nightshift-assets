"""Char_Face_Beard — Full jaw/chin beard (role hair so it follows the hair colour); mouth stays visible. Attach at FaceSocket.

Accessory for Character_Human (group Characters). Modelled in body space on the real head /
torso (blender/D_characters/_common.py) and exported with pivot = the FaceSocket point, so the
runtime welds it to the Head part at Socket_FaceSocket.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

if __name__ == "__main__":
    C.run_accessory("Char_Face_Beard")
