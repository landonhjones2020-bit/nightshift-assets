"""Shop_WallDoorway — 8 x 12 wall module with a 5 x 8 door opening (clear, floor to 8).

Stainless jamb lining + chunky casing on both faces, plinth blocks where the baseboard meets
the casing, a diamond-plate threshold, and the standard wainscot/trim either side.
The map adds its own invisible collision Parts; Core marks the solid wall volume.
Socket DoorHinge = hinge line of the leaf (left jamb, floor, wall centre); Shop_DoorFront /
Shop_DoorInterior pivots go there (leaf.PivotTo(doorway:GetPivot() * Socket_DoorHinge)).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
X0, X1 = -C.WALL_W / 2, C.WALL_W / 2
OX, OH = 2.5, 8.0        # half opening width, opening height
CW = 0.42                # casing width
STEEL = C.STAINLESS


def casing_side(sx, face_y, out_dir):
    """One vertical casing leg (+ plinth block) on one face. sx = -1 left, +1 right."""
    xa, xb = sorted((sx * OX, sx * (OX + CW)))
    proud = 0.24
    a0, a1 = sorted((face_y, face_y + out_dir * proud))
    leg = ns.box((xb - xa, a1 - a0, OH + CW), loc=((xa + xb) / 2, (a0 + a1) / 2, (OH + CW) / 2), bevel=0.05)
    # plinth block (slightly proud of the casing) where the baseboard stops
    b0, b1 = sorted((face_y, face_y + out_dir * (proud + 0.05)))
    plinth = ns.box((xb - xa + 0.06, b1 - b0, 0.7), loc=((xa + xb) / 2, (b0 + b1) / 2, 0.35), bevel=0.04)
    return [leg, plinth]


def casing_head(face_y, out_dir):
    proud = 0.24
    a0, a1 = sorted((face_y, face_y + out_dir * proud))
    head = ns.box((2 * (OX + CW), a1 - a0, CW), loc=(0, (a0 + a1) / 2, OH + CW / 2), bevel=0.05)
    # small cornice cap over the head casing
    c0, c1 = sorted((face_y, face_y + out_dir * (proud + 0.08)))
    cap = ns.box((2 * (OX + CW) + 0.24, c1 - c0, 0.14), loc=(0, (c0 + c1) / 2, OH + CW + 0.07), bevel=0.04)
    return [head, cap]


def build():
    core = [ns.box((4 - OX, 1, OH), loc=(-(4 + OX) / 2, 0, OH / 2), bevel=0.0),
            ns.box((4 - OX, 1, OH), loc=((4 + OX) / 2, 0, OH / 2), bevel=0.0),
            ns.box((8, 1, 12 - OH), loc=(0, 0, (12 + OH) / 2), bevel=0.0)]
    C.part(core, "Core", C.CREAM_SHADE, recolor="wall_back", can_collide=True)

    sides = ((X0, -OX), (OX, X1))
    d = C.wainscot(list(sides))
    d["upper"] = [C.skin(x0, x1, C.CHECK_TOP, OH) for x0, x1 in sides] + [C.skin(X0, X1, OH, C.CROWN_Z + 0.05)]
    d["crown"] = [C.crown(X0, X1)]
    d["stripe"] = C.stripes(X0, X1)
    d["back"] = C.back_trim(list(sides))
    C.tag_wall_set(d)

    # stainless jamb lining through the wall + chunky casing (with plinth blocks) on both faces
    frame = []
    for sx in (-1, 1):
        frame.append(ns.box((0.08, 1.02, OH), loc=(sx * (OX + 0.03), 0, OH / 2), bevel=0.0))
        frame += casing_side(sx, -0.5, -1) + casing_side(sx, 0.5, 1)
    frame.append(ns.box((2 * OX + 0.16, 1.02, 0.08), loc=(0, 0, OH + 0.03), bevel=0.0))
    frame += casing_head(-0.5, -1) + casing_head(0.5, 1)
    C.part(frame, "Frame", STEEL, "Metal", smooth_angle=40)
    thr = ns.box((2 * OX, 1.1, 0.06), loc=(0, 0, 0.03), bevel=0.025, segments=1)
    ns.tag(thr, "Threshold", C.STAINLESS, "DiamondPlate")


META = dict(C.wall_presets_meta(), module="wall_doorway", grid=8, size=[8, 12, 1],
            collider="Core (jambs + header)", opening={"x": [-OX, OX], "z": [0, OH], "clear": [5, 8]},
            door_leaves=["Shop_DoorFront", "Shop_DoorInterior"],
            placement="pivot on the wall centre line, bottom; leaf pivot -> Socket_DoorHinge")

if __name__ == "__main__":
    C.run(build, "Shop_WallDoorway", pivot=(0, 0, 0), meta=META,
          sockets={"DoorHinge": ((-OX, 0, 0), 0.0)})
