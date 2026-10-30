"""Lobby_StoreFrontBay — 16 x 14 storefront bay of the STACKHOUSE HQ building.

Two red-brick piers (concrete plinths, cream capitals, modelled mortar) carry a red-orange
steel header beam with chrome bolts; above it a brick parapet with a recessed sign band
(SignBand, role "sign_band", Front face: an optional SurfaceGui / sign mount) and a cream
coping with mustard pinstripes. The 14-wide opening holds a big roll-up glass garage door
RAISED: its bottom glass section still shows under the header (aluminium frame, Glass
panes with role "glass", rubber seal, pull handle) and its steel tracks run up the jambs to
a coil drum behind the header, so the Test Kitchen inside stays fully visible.

Pivot = bottom-centre of the wall centre line (same grid contract as Lobby_StoreWall);
exterior = front (-Y), interior = +Y. Thickness 1.5 (the coil drum sits 1 stud further
inside, up high). can_collide = False everywhere (the map adds collision).
Sockets: SignBand (sign band face centre), Doorway (centre of the opening on the ground,
facing out), Inside (a point 3 studs inside the opening, on the ground).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W = 16.0
X0, X1 = -W / 2, W / 2
OX = 7.0                       # opening half width
HT = C.HQ_T / 2
SIGN = (-6.6, 6.6, 11.75, 13.15)   # recess x0, x1, z0, z1
DOOR_Z0 = 9.0                  # raised door's bottom edge
DOOR_Y = 0.35                  # door plane (inside the jambs)
ALU = "#C3C9CE"


def build():
    hz0, hz1 = C.HQ_HEADER
    brick = [ns.box((X1 - OX, C.HQ_T, hz0 - C.HQ_PLINTH), loc=(sx * (OX + X1) / 2, 0, (C.HQ_PLINTH + hz0) / 2), bevel=0.0)
             for sx in (-1, 1)]
    parapet = ns.box((W, C.HQ_T, C.HQ_COPING - hz1), loc=(0, 0, (hz1 + C.HQ_COPING) / 2), bevel=0.0)
    ns.boolean(parapet, ns.box((SIGN[1] - SIGN[0], 0.6, SIGN[3] - SIGN[2]), loc=(0, -HT - 0.05, (SIGN[2] + SIGN[3]) / 2),
                               bevel=0.0))
    brick.append(parapet)
    C.part(brick, "Brick", C.BRICK, recolor="brick", smooth_angle=30)

    mortar = []
    for sx in (-1, 1):
        a0, a1 = sorted((sx * OX, sx * X1))
        mortar += C.hq_pier_rings(a0, a1, C.HQ_PLINTH, hz0 - 0.55, grow=(-0.01, 0.02) if sx > 0 else (0.02, -0.01))
        for sy in (-1, 1):
            mortar += C.hq_mortar_face(a0, a1, C.HQ_PLINTH, hz0 - 0.55, sy, head_every=1, lines=False)
        b0, b1 = sorted((sx * -SIGN[0], sx * X1))
        mortar += C.hq_mortar_face(b0, b1, hz1, C.HQ_COPING, -1)
    mortar += C.hq_mortar_face(SIGN[0], SIGN[1], hz1, SIGN[2], -1, heads=False)
    mortar += C.hq_mortar_face(X0, X1, hz1, C.HQ_COPING, 1)
    C.part(mortar, "Mortar", C.MORTAR, smooth_angle=30)

    # plinths, pier capitals, coping (cream / concrete)
    conc = [C.hq_plinth(X0, -OX), C.hq_plinth(OX, X1)]
    C.part(conc, "Plinth", C.CONCRETE, "Concrete", smooth_angle=35)
    cream = [C.hq_coping(X0, X1)]
    for sx in (-1, 1):
        a0, a1 = sorted((sx * OX, sx * X1))
        # capitals 0.01 deeper per face than the pinstripes (at HQ_T + 0.12 their faces were coplanar with the
        # stripe under the header -> cream / mustard z-fighting on both piers)
        cream.append(ns.box((a1 - a0 + 0.12, C.HQ_T + 0.14, 0.55), loc=((a0 + a1) / 2, 0, hz0 - 0.275), bevel=0.04,
                            segments=1))
    frame = C.ring_slab(C.rrect(SIGN[1] - SIGN[0] - 0.12, SIGN[3] - SIGN[2] - 0.12, 0.08, 1, 0, (SIGN[2] + SIGN[3]) / 2),
                        C.rrect(SIGN[1] - SIGN[0] - 0.36, SIGN[3] - SIGN[2] - 0.36, 0.06, 1, 0, (SIGN[2] + SIGN[3]) / 2),
                        "y", -HT + 0.18, -HT + 0.27)
    cream.append(frame)
    C.part(cream, "Cream", C.CREAM, smooth_angle=35)
    sw, sh = SIGN[1] - SIGN[0] - 0.36, SIGN[3] - SIGN[2] - 0.36
    sign = ns.box((sw, 0.06, sh), loc=(0, -HT + 0.22, (SIGN[2] + SIGN[3]) / 2), bevel=0.0)
    ns.tag(sign, "SignBand", C.NAVY, recolor="sign_band", smooth_angle=None)

    # header beam + bolts + pinstripes
    C.part([C.hq_header_band(X0, X1)], "Header", C.BRAND, recolor="header", smooth_angle=35)
    bolts = []
    for k in range(10):
        x = X0 + 0.8 + k * (W - 1.6) / 9
        for z in (hz0 + 0.22, hz1 - 0.22):
            bolts.append(ns.box((0.13, 0.06, 0.13), loc=(x, -HT - 0.08, z), bevel=0.0))
    C.part(C.hq_pinstripes(X0, X1), "Pinstripe", C.MUSTARD, smooth_angle=30)

    # raised roll-up glass door: visible bottom section, tracks, coil drum
    alu = [ns.box((2 * OX - 0.4, 0.22, 0.26), loc=(0, DOOR_Y, DOOR_Z0 + 0.13), bevel=0.04, segments=1)]
    n = 6
    pw = (2 * OX - 0.4) / n
    for k in range(n + 1):
        x = -OX + 0.2 + k * pw
        alu.append(ns.box((0.14, 0.2, hz0 - DOOR_Z0 + 0.1), loc=(x, DOOR_Y, (DOOR_Z0 + hz0) / 2 + 0.05), bevel=0.02,
                          segments=1))
    alu.append(ns.box((2 * OX - 0.4, 0.2, 0.12), loc=(0, DOOR_Y, 9.85), bevel=0.02, segments=1))
    handle = C.pipe([(-0.5, DOOR_Y - 0.11, DOOR_Z0 + 0.08), (-0.5, DOOR_Y - 0.25, DOOR_Z0 + 0.08),
                     (0.5, DOOR_Y - 0.25, DOOR_Z0 + 0.08), (0.5, DOOR_Y - 0.11, DOOR_Z0 + 0.08)], 0.04, sides=5,
                    corner=0.08, corner_segs=1)
    C.part(alu + bolts + [handle], "Aluminium", ALU, "Metal", smooth_angle=40)
    panes = []
    for k in range(n):
        x = -OX + 0.2 + (k + 0.5) * pw
        panes.append(ns.box((pw - 0.14, 0.05, hz0 - DOOR_Z0 - 0.26 + 0.1), loc=(x, DOOR_Y, (DOOR_Z0 + 0.26 + hz0 + 0.1) / 2),
                            bevel=0.0))
    ns.tag(C.merge(panes, "DoorGlass"), "DoorGlass", C.GLASS, "Glass", transparency=0.5, recolor="glass",
           cast_shadow=False, smooth_angle=None)
    steel = [ns.box((2 * OX - 0.4, 0.24, 0.06), loc=(0, DOOR_Y, DOOR_Z0 - 0.03), bevel=0.0)]   # rubber seal
    for sx in (-1, 1):
        steel.append(ns.box((0.22, 0.42, hz0 - 0.02), loc=(sx * (OX - 0.11), DOOR_Y, (hz0 - 0.02) / 2 + 0.02), bevel=0.02,
                            segments=1))
    drum = ns.cyl(0.6, 2 * OX - 0.2, loc=(0, HT + 0.62, hz0 + 0.55), rot=(0, 90, 0), verts=12, bevel=0.04, segments=1)
    steel.append(drum)
    for sx in (-1, 1):
        steel.append(ns.box((0.12, 1.3, 1.3), loc=(sx * (OX - 0.05), HT + 0.6, hz0 + 0.55), bevel=0.03, segments=1))
    C.part(steel, "Steel", C.STEEL, "Metal", smooth_angle=40)
    sill = ns.box((2 * OX, C.HQ_T - 0.2, 0.06), loc=(0, 0, 0.05), bevel=0.0)
    C.part([sill], "Threshold", "#9AA1A8", "DiamondPlate", smooth_angle=None)


SOCKETS = {"SignBand": ((0, -HT + 0.19, (SIGN[2] + SIGN[3]) / 2), 0.0),
           "Doorway": ((0, 0, 0), 0.0),
           "Inside": ((0, 3.0, 0), 180.0)}
META = {"module": "hq_storefront", "grid": 8, "size": [16, 14, 1.5], "exterior": "front (-Y / LookVector)",
        "opening": {"x": [-OX, OX], "clear_height": DOOR_Z0}, "door": "raised (open); bottom section visible",
        "sign_band_size": [round(SIGN[1] - SIGN[0] - 0.36, 2), round(SIGN[3] - SIGN[2] - 0.36, 2)],
        "surfaces": [C.screen_meta("SignBand", SIGN[1] - SIGN[0] - 0.36, SIGN[3] - SIGN[2] - 0.36)],
        "header_band_z": list(C.HQ_HEADER), "roles": {"brick": "Brick", "header": "Header", "sign_band": "SignBand",
                                                      "glass": "DoorGlass"},
        "collision": "none (map adds collision)"}

if __name__ == "__main__":
    C.run(build, "Lobby_StoreFrontBay", sockets=SOCKETS, pivot=(0, 0, 0), meta=META)
