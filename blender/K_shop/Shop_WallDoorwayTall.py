"""Shop_WallDoorwayTall — 8 x 20 wall module with the 5 x 8 door opening + a transom window.

The door half is Shop_WallDoorway exactly: clear 5 x 8 opening, stainless jamb lining,
chunky casing with plinth blocks on both faces, cornice cap, diamond-plate threshold and
the same DoorHinge socket (left jamb, floor, wall centre), so Shop_DoorFront /
Shop_DoorInterior hang in it unchanged. Above the door cap sits a transom light
(glass x +-2.5, z 9 .. 15.5): its own part `TransomGlass` (role glass), framed by a stainless
lining and a casing + cornice cap on both faces that stands on the door's cap.
Lower 12 studs: the standard wainscot / checker / chair rail / pinstripes beside the
opening; frieze rail at 12 and the crown at the top (19.45 .. 20) like Shop_WallTall.
Collision: Core (jambs + header) + TransomGlass.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
H = C.TALL_H
X0, X1 = -C.WALL_W / 2, C.WALL_W / 2
OX, OH = 2.5, 8.0        # half opening width, opening height (= Shop_WallDoorway)
CW = 0.42                # casing width
CASE_IN = 0.02           # casing laps this far over the opening edge (buries the trim ends)
STEEL = C.STAINLESS
TZ0, TZ1 = 9.0, 15.5     # transom glass bottom / top
TW = 0.34                # transom casing width
CAP_TOP = OH + CW + 0.14  # top of the door's cornice cap (8.56)


def casing_side(sx, face_y, out_dir):
    """One vertical door casing leg (+ plinth block) on one face. sx = -1 left, +1 right."""
    xa, xb = sorted((sx * (OX - CASE_IN), sx * (OX + CW)))
    proud = 0.24
    a0, a1 = sorted((face_y, face_y + out_dir * proud))
    leg = ns.box((xb - xa, a1 - a0, OH + CW), loc=((xa + xb) / 2, (a0 + a1) / 2, (OH + CW) / 2), bevel=0.05)
    b0, b1 = sorted((face_y, face_y + out_dir * (proud + 0.05)))
    plinth = ns.box((xb - xa + 0.06, b1 - b0, 0.7), loc=((xa + xb) / 2, (b0 + b1) / 2, 0.35), bevel=0.04)
    return [leg, plinth]


def casing_head(face_y, out_dir):
    proud = 0.24
    a0, a1 = sorted((face_y, face_y + out_dir * proud))
    head = ns.box((2 * (OX + CW), a1 - a0, CW + CASE_IN), loc=(0, (a0 + a1) / 2, OH + (CW - CASE_IN) / 2), bevel=0.05)
    c0, c1 = sorted((face_y, face_y + out_dir * (proud + 0.08)))
    cap = ns.box((2 * (OX + CW) + 0.24, c1 - c0, 0.14), loc=(0, (c0 + c1) / 2, OH + CW + 0.07), bevel=0.04)
    return [head, cap]


def transom_casing(face_y, out_dir):
    """Casing ring round the transom light, standing on the door's cornice cap, + its own cap."""
    proud = 0.2
    a0, a1 = sorted((face_y, face_y + out_dir * proud))
    xo = OX - CASE_IN
    zb = CAP_TOP - 0.02                      # sinks 0.02 into the door cap (no coplanar faces)
    outer = C.rrect(2 * (xo + TW), TZ1 + TW - zb, 0.06, 1, 0, (zb + TZ1 + TW) / 2)
    inner = C.rrect(2 * xo, TZ1 - TZ0 - 2 * CASE_IN, 0.04, 1, 0, (TZ0 + TZ1) / 2)
    ring = C.ring_slab(outer, inner, "y", a0, a1)
    ns.bevel(ring, width=0.04, segments=1)
    c0, c1 = sorted((face_y, face_y + out_dir * (proud + 0.08)))
    cap = ns.box((2 * (xo + TW) + 0.24, c1 - c0, 0.14), loc=(0, (c0 + c1) / 2, TZ1 + TW + 0.07), bevel=0.04)
    return [ring, cap]


def build():
    pier = X1 - OX
    core = [ns.box((pier, 1, TZ1), loc=(-(X1 + OX) / 2, 0, TZ1 / 2), bevel=0.0),
            ns.box((pier, 1, TZ1), loc=((X1 + OX) / 2, 0, TZ1 / 2), bevel=0.0),
            ns.box((2 * OX, 1, TZ0 - OH), loc=(0, 0, (OH + TZ0) / 2), bevel=0.0),
            ns.box((C.WALL_W, 1, H - TZ1), loc=(0, 0, (H + TZ1) / 2), bevel=0.0)]
    C.part(core, "Core", C.CREAM_SHADE, recolor="wall_back", can_collide=True)

    sides = ((X0, -OX), (OX, X1))
    d = C.S.wainscot(list(sides))
    d["upper"] = ([C.skin(x0, x1, C.CHECK_TOP, TZ1) for x0, x1 in sides] +
                  [C.skin(-OX, OX, OH, TZ0), C.skin(X0, X1, TZ1, C.TALL_CROWN_Z + 0.05)])
    d["crown"] = [C.crown_tall(X0, X1)]
    # pinstripes, frieze rail and the exterior band stop inside the transom casing ring
    # (x 2.48 .. 2.82, 0.2 proud), never on its inner face plane
    e = OX + 0.15
    d["stripe"] = C.stripes(X0, -e) + C.stripes(e, X1)
    d["rail"] += [C.frieze_rail(X0, -e), C.frieze_rail(e, X1)]
    d["back"] = C.S.back_trim(list(sides)) + [C.back_band(X0, -e), C.back_band(e, X1)]
    C.tag_wall_set(d)

    # door: stainless jamb lining through the wall + chunky casing (plinth blocks) on both faces
    frame = []
    for sx in (-1, 1):
        frame.append(ns.box((0.08, 1.02, OH), loc=(sx * (OX + 0.03), 0, OH / 2), bevel=0.0))
        frame += casing_side(sx, -0.5, -1) + casing_side(sx, 0.5, 1)
    frame.append(ns.box((2 * OX + 0.16, 1.02, 0.08), loc=(0, 0, OH + 0.03), bevel=0.0))
    frame += casing_head(-0.5, -1) + casing_head(0.5, 1)
    # transom: lining round the light + casing ring and cap on both faces
    lt = 0.16
    frame += [ns.box((2 * OX, 0.5, lt), loc=(0, 0, TZ1 - lt / 2), bevel=0.02, segments=1),
              ns.box((2 * OX, 0.5, lt), loc=(0, 0, TZ0 + lt / 2), bevel=0.02, segments=1),
              ns.box((lt, 0.5, TZ1 - TZ0), loc=(-OX + lt / 2, 0, (TZ0 + TZ1) / 2), bevel=0.02, segments=1),
              ns.box((lt, 0.5, TZ1 - TZ0), loc=(OX - lt / 2, 0, (TZ0 + TZ1) / 2), bevel=0.02, segments=1)]
    # muntin at 12: the same line as the tall windows' transom bars and the frieze rail
    frame.append(ns.box((2 * OX - 0.1, 0.4, 0.3), loc=(0, 0, C.FRIEZE_Z), bevel=0.05, segments=2))
    frame += transom_casing(-0.5, -1) + transom_casing(0.5, 1)
    C.part(frame, "Frame", STEEL, "Metal", smooth_angle=40)
    thr = ns.box((2 * OX, 1.1, 0.06), loc=(0, 0, 0.03), bevel=0.025, segments=1)
    ns.tag(thr, "Threshold", C.STAINLESS, "DiamondPlate")

    glass = ns.box((2 * OX - 0.02, 0.06, TZ1 - TZ0 - 0.02), loc=(0, 0, (TZ0 + TZ1) / 2), bevel=0.0)
    ns.tag(glass, "TransomGlass", C.GLASS, "Glass", transparency=0.6, recolor="glass", can_collide=True,
           cast_shadow=False)


META = dict(C.wall_presets_meta(), module="wall_doorway", grid=8, size=[8, 20, 1],
            collider="Core (jambs + header) + TransomGlass", opening={"x": [-OX, OX], "z": [0, OH], "clear": [5, 8]},
            transom_opening={"x": [-OX, OX], "z": [TZ0, TZ1]}, height=20,
            door_leaves=["Shop_DoorFront", "Shop_DoorInterior"],
            placement="pivot on the wall centre line, bottom; leaf pivot -> Socket_DoorHinge")

if __name__ == "__main__":
    C.run(build, "Shop_WallDoorwayTall", pivot=(0, 0, 0), meta=META,
          sockets={"DoorHinge": ((-OX, 0, 0), 0.0)})
