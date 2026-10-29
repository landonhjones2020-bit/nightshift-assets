"""Char_Hat_Beanie — Cuffed knit beanie (role hat) with a ribbed fold-up cuff and a leather tag. Attach at HatSocket.

Accessory for Character_Human (group Characters). Modelled in body space on the real head /
torso (blender/D_characters/_common.py) and exported with pivot = the HatSocket point, so the
runtime welds it to the Head part at Socket_HatSocket.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

if __name__ == "__main__":
    C.run_accessory("Char_Hat_Beanie")
