"""Cosmetic_Spatula — the spatula skin mesh (Standard, Neon, Golden): the same diner flipper as
Kitchen_Spatula, split into recolour roles.

Held in the right hand: pivot = grip point (middle of the handle) at the origin, the blade
points along Blender -Y (Roblox -Z = the grip attachment's LookVector), blade face up (+Z).
Roles: Blade (slotted blade + shank) = cos_body; Handle = cos_trim. Rivets keep fixed brass.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
BRASS = "#C9A24A"
HANDLE_L = 0.78


def blade_obj(y0, slots=(-0.15, 0.0, 0.15)):
    """Wide slotted blade with rounded front corners; back edge at y0 - 0.4."""
    bw, bl, r = 0.66, 0.76, 0.12
    by0 = y0 - 0.4
    outline = [(-0.08, 0.0), (0.08, 0.0), (bw / 2, -0.16)]
    for i in range(4):
        a = math.radians(0 - 90 * i / 3)
        outline.append((bw / 2 - r + r * math.cos(a), -bl + r + r * math.sin(a)))
    for i in range(4):
        a = math.radians(-90 - 90 * i / 3)
        outline.append((-bw / 2 + r + r * math.cos(a), -bl + r + r * math.sin(a)))
    outline.append((-bw / 2, -0.16))
    blade = C.extrude(outline, 0.035, plane="XY", offset=0.0, name="Blade")
    blade.location = (0, by0, -0.16)
    ns.apply_all(blade)
    for x in slots:
        ns.boolean(blade, ns.box((0.055, 0.36, 0.2), loc=(x, by0 - 0.4, -0.14), bevel=0.0))
    ns.bevel(blade, width=0.012, segments=1)
    return blade


def build():
    dc = C.default_colours("Spatula")
    hl = HANDLE_L
    prof = [(0.0, -hl / 2), (0.085, -hl / 2), (0.105, -hl / 2 + 0.04), (0.11, -hl / 2 + 0.2), (0.1, 0.1),
            (0.088, hl / 2 - 0.05), (0.07, hl / 2), (0.0, hl / 2)]
    handle = ns.lathe(prof, verts=10, name="Handle")
    handle.scale = (1.0, 0.72, 1.0)
    handle.rotation_euler = (1.5708, 0, 0)
    C.part(handle, "Handle", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=60)
    rivets = [ns.cyl(0.032, 0.17, loc=(0, y, 0), verts=6, bevel=0.0) for y in (0.18, 0.0, -0.18)]
    C.part(rivets, "Rivets", BRASS, "Metal", smooth_angle=50)

    y0 = -hl / 2
    ferrule = C.rod((0, y0 + 0.02, 0), (0, y0 - 0.1, 0), 0.075, verts=10, r_top=0.06)
    neck = ns.box((0.12, 0.34, 0.04), loc=(0, y0 - 0.25, -0.075), rot=(27, 0, 0), bevel=0.012, segments=1)
    C.part([ferrule, neck, blade_obj(y0)], "Blade", dc["body"], "Metal", recolor="cos_body", smooth_angle=40)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Spatula", "Spatula")
