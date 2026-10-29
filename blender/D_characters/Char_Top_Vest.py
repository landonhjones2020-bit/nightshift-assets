"""Char_Top_Vest — Quilted puffer vest (role top) with a stand-up collar and a zip.

Accessory for Character_Human (group Characters). Modelled in body space on the real head /
torso (blender/D_characters/_common.py) and exported with pivot = the TorsoSocket point, so the
runtime welds it to the Torso part at Socket_TorsoSocket.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

if __name__ == "__main__":
    C.run_accessory("Char_Top_Vest")
