"""Cosmetic_Apron — the classic STACKHOUSE bib apron (also Night Owl, First Night, Midnight
Velvet, Neon, Dawn, VIP Gold and Static skins: one mesh, recoloured by role).

Worn on BodyFrontAttachment (pivot = origin, body behind it along +Y). A cloth panel with a
narrow bib, curved armholes and a skirt that flares slightly forward to a hem at -2.0;
contrasting edge binding, crossed neck straps over the shoulders, waist ties around the
torso sides to a bow at the back, and a chest pocket with a pencil tucked in.

Roles: Apron = cos_body; Trim (binding, straps, ties, bow, pocket) = cos_trim.
The pencil keeps fixed colours.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402


def build():
    C.apron_base()


if __name__ == "__main__":
    C.run(build, "Cosmetic_Apron", "Apron")
