"""Kitchen_Spatula — the diner flipper every player carries (whack = noise 15).

Held tool: the pivot is the grip point (middle of the handle) at the origin. The business
end points forward along Blender -Y (Roblox -Z = LookVector) with the blade face up, so an
identity grip holds it out front. A wooden handle with brass rivets, a steel shank with the
classic offset bend, and a wide slotted blade. Blade and handle carry roles
(spatula_blade / spatula_handle) so cosmetic skins can recolour them.

Meta grip: point (always 0,0,0 = pivot), forward and up directions in Roblox model space.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
WOOD = "#8A5A3C"
BRASS = "#C9A24A"
HANDLE_L = 0.78


def build():
    # ---- handle: lathed along Z then laid along Y (rot X +90 maps +Z -> -Y) -------------
    hl = HANDLE_L
    prof = [(0.0, -hl / 2), (0.085, -hl / 2), (0.105, -hl / 2 + 0.04), (0.11, -hl / 2 + 0.2), (0.1, 0.1), (0.088, hl / 2 - 0.05),
            (0.07, hl / 2), (0.0, hl / 2)]
    handle = ns.lathe(prof, verts=10, name="Handle")
    handle.scale = (1.0, 0.72, 1.0)                       # oval cross-section (flatter top/bottom)
    handle.rotation_euler = (1.5708, 0, 0)
    C.part(handle, "Handle", WOOD, "Wood", recolor="spatula_handle", smooth_angle=60)
    rivets = [ns.cyl(0.032, 0.17, loc=(0, y, 0), verts=6, bevel=0.0) for y in (0.18, 0.0, -0.18)]
    C.part(rivets, "Rivets", BRASS, "Metal", smooth_angle=50)

    # ---- shank: ferrule + offset neck down to the blade -------------------------------
    y0 = -hl / 2
    ferrule = C.rod((0, y0 + 0.02, 0), (0, y0 - 0.1, 0), 0.075, verts=10, r_top=0.06)
    neck = ns.box((0.12, 0.34, 0.04), loc=(0, y0 - 0.25, -0.075), rot=(27, 0, 0), bevel=0.012, segments=1)
    C.part([ferrule, neck], "Shank", C.STEEL, "Metal", smooth_angle=40)

    # ---- blade: wide, rounded front corners, three slots ------------------------------
    bw, bl, r = 0.66, 0.76, 0.12
    by0 = y0 - 0.4                        # blade back edge (where the neck lands)
    import math
    outline = [(-0.08, 0.0), (0.08, 0.0), (bw / 2, -0.16)]
    for i in range(4):                    # front-right rounded corner
        a = math.radians(0 - 90 * i / 3)
        outline.append((bw / 2 - r + r * math.cos(a), -bl + r + r * math.sin(a)))
    for i in range(4):                    # front-left rounded corner
        a = math.radians(-90 - 90 * i / 3)
        outline.append((-bw / 2 + r + r * math.cos(a), -bl + r + r * math.sin(a)))
    outline.append((-bw / 2, -0.16))
    blade = C.extrude(outline, 0.035, plane="XY", offset=0.0, name="Blade")
    blade.location = (0, by0, -0.16)
    ns.apply_all(blade)
    for x in (-0.15, 0.0, 0.15):
        ns.boolean(blade, ns.box((0.055, 0.36, 0.2), loc=(x, by0 - 0.4, -0.14), bevel=0.0))
    ns.bevel(blade, width=0.012, segments=1)
    C.part(blade, "Blade", C.STAINLESS, "Metal", recolor="spatula_blade", smooth_angle=40)

    meta = {"grip": {"point": [0, 0, 0], "forward": [0, 0, -1], "up": [0, 1, 0]}, "tool": True}
    return {"export": {"meta": meta, "pivot": (0, 0, 0)}}


if __name__ == "__main__":
    C.run(build, "Kitchen_Spatula")
