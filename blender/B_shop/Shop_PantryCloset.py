"""Shop_PantryCloset — the pantry's hiding closet: a 4.2 x 3 x 8.6 wooden closet with two
louvred (slatted) doors — you can peek out between the slats.

Frame + cornice in dark wood, painted pine doors each with an upper and lower louvre panel,
brass knobs, dark interior. Doors are separate parts DoorL / DoorR (role "closet_door") with
hinge sockets so code can swing them open when Lights-Out searches the spot.
Front = -Y. Pivot = bottom-centre.
Sockets: Hide (centre of the interior volume, facing out through the slats), HideFloor,
DoorHingeL / DoorHingeR (hinge lines at the door bottoms; L opens with negative yaw,
R with positive yaw, both outward to -Y).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D, H = 4.2, 3.0, 8.6
FT = 0.22                    # frame thickness
DZ0, DZ1 = 0.25, 7.9         # door bottom / top
PINE = "#C2A57A"
BRASS = "#C9A045"


def door(x0, x1):
    """Louvred door between x0 and x1 on the front plane. Returns (frame objs, slat objs)."""
    y = -D / 2 + 0.08
    t = 0.14
    w = x1 - x0
    cx = (x0 + x1) / 2
    st = 0.2
    frame = [ns.box((st, t, DZ1 - DZ0), loc=(x0 + st / 2, y, (DZ0 + DZ1) / 2), bevel=0.03, segments=1),
             ns.box((st, t, DZ1 - DZ0), loc=(x1 - st / 2, y, (DZ0 + DZ1) / 2), bevel=0.03, segments=1)]
    for zc, h in ((DZ0 + 0.18, 0.36), (3.6, 0.3), (DZ1 - 0.13, 0.26)):
        frame.append(ns.box((w - 2 * st + 0.02, t, h), loc=(cx, y, zc), bevel=0.03, segments=1))
    slats = []
    for z0, z1 in ((DZ0 + 0.36, 3.45), (3.75, DZ1 - 0.26)):
        n = int((z1 - z0) / 0.24)
        pitch = (z1 - z0) / n
        for i in range(n):
            slats.append(ns.box((w - 2 * st + 0.02, 0.24, 0.035), loc=(cx, y, z0 + pitch * (i + 0.5)),
                                rot=(-42, 0, 0), bevel=0.0))
    return frame, slats


def build():
    wood = []
    # carcass: sides, top, back, floor, front frame + cornice
    for sx in (-1, 1):
        wood.append(ns.box((FT, D, H - 0.3), loc=(sx * (W / 2 - FT / 2), 0, (H - 0.3) / 2), bevel=0.04, segments=1))
    wood.append(ns.box((W, D, FT), loc=(0, 0, H - 0.3 - FT / 2), bevel=0.04, segments=1))
    wood.append(ns.box((W, 0.12, H - 0.3), loc=(0, D / 2 - 0.06, (H - 0.3) / 2), bevel=0.04, segments=1))
    wood.append(ns.box((W, D + 0.04, 0.2), loc=(0, 0, 0.1), bevel=0.03, segments=1))
    cornice = C.prism(C.fillet([(-D / 2 - 0.25, H - 0.3), (D / 2, H - 0.3), (D / 2, H), (-D / 2 - 0.3, H),
                                (-D / 2 - 0.3, H - 0.12)], [0, 0, 0, 0.04, 0.04], 1), "x", -W / 2 - 0.2, W / 2 + 0.2)
    wood.append(cornice)
    C.part(wood, "Carcass", C.WOOD_DARK, "Wood", can_collide=True, smooth_angle=40)
    # dark interior liners (back + sides) seen through the slats
    gloom = [ns.box((W - 2 * FT, 0.05, H - 0.6), loc=(0, D / 2 - 0.15, (H - 0.6) / 2 + 0.2), bevel=0.0)]
    for sx in (-1, 1):
        gloom.append(ns.box((0.05, D - 0.4, H - 0.6), loc=(sx * (W / 2 - FT - 0.03), 0.05, (H - 0.6) / 2 + 0.2),
                            bevel=0.0))
    C.part(gloom, "Gloom", C.DARK_VOID)

    gap = 0.03
    xs = ((-W / 2 + FT + gap, -gap / 2), (gap / 2, W / 2 - FT - gap))
    knobs = []
    for (x0, x1), nm in zip(xs, ("DoorL", "DoorR")):
        frame, slats = door(x0, x1)
        ns.tag(C.merge(frame + slats, nm), nm, PINE, "Wood", recolor="closet_door", can_collide=True, smooth_angle=40)
        kx = x1 - 0.32 if nm == "DoorL" else x0 + 0.32
        knobs.append(ns.sphere(0.09, loc=(kx, -D / 2 - 0.05, 3.6), segs=8, rings=6))
        knobs.append(ns.cyl(0.05, 0.12, loc=(kx, -D / 2 + 0.02, 3.6), rot=(90, 0, 0), verts=6, bevel=0.0))
    C.part(knobs, "Knobs", BRASS, "Metal", smooth_angle=60)


def sockets():
    y = -D / 2 + 0.08
    return {"Hide": ((0, 0.2, 2.5), 0.0), "HideFloor": ((0, 0.2, 0.2), 0.0),
            "DoorHingeL": ((-W / 2 + FT, y, DZ0), 0.0), "DoorHingeR": ((W / 2 - FT, y, DZ0), 0.0)}


META = {"size": [W, H, D], "hide_spots": ["Hide"], "doors": ["DoorL", "DoorR"], "hide_floor": 0.2}

if __name__ == "__main__":
    C.run(build, "Shop_PantryCloset", meta=META, sockets=sockets())
