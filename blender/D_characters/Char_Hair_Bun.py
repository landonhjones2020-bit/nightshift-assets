"""Char_Hair_Bun — Slicked-back hair with a top-back bun (role hair) and a hair tie.

Accessory for Character_Human (group Characters). Modelled in body space on the real head /
torso (blender/D_characters/_common.py) and exported with pivot = the HairSocket point, so the
runtime welds it to the Head part at Socket_HairSocket.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

if __name__ == "__main__":
    C.run_accessory("Char_Hair_Bun")
