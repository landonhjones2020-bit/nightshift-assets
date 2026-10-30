"""Shop_WallWindow — 8 x 12 wall module with a big diner window (sill 3.5, head 9).

Opening 6.4 wide x 5.5 tall, four panes (centre mullion + transom) in a chunky chrome frame,
a deep laminate sill on the room side whose top is flush with the chrome chair rail, and an
exterior chrome casing + drip sill on the back (+Y, parking-lot side).
Same wainscot/trim/roles as Shop_Wall so the modules tile seamlessly.
Collision: Core (full module box) + Glass (pane, role "glass").
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
X0, X1 = -C.WALL_W / 2, C.WALL_W / 2
OX = 3.2                     # half opening width
Z0, Z1 = C.SILL_Z, 9.0       # sill / head
TRANSOM = 7.85
SILL_PROUD = 0.02            # room-side sill top above the opening sill line / chair rail top


def casing(face_y, out_dir, w=0.32, proud=0.12, with_bottom=False):
    """U-shaped (or full) chrome casing around the opening on one face.
    out_dir = -1 for the room face (-Y), +1 for the back face."""
    zb = Z0 if not with_bottom else Z0 - w
    pts = [(-OX - w, zb), (-OX, zb), (-OX, Z1), (OX, Z1), (OX, zb), (OX + w, zb), (OX + w, Z1 + w), (-OX - w, Z1 + w)]
    pts = C.fillet(pts, [0, 0, 0, 0, 0, 0, 0.1, 0.1], 2)
    a0, a1 = sorted((face_y, face_y + out_dir * proud))
    ob = C.prism(pts, "y", a0, a1)
    ns.bevel(ob, width=0.035, segments=2)
    return ob


def build():
    core = [ns.box((8, 1, Z0), loc=(0, 0, Z0 / 2), bevel=0.0),
            ns.box((8, 1, 12 - Z1), loc=(0, 0, (12 + Z1) / 2), bevel=0.0),
            ns.box((4 - OX, 1, Z1 - Z0), loc=(-(4 + OX) / 2, 0, (Z0 + Z1) / 2), bevel=0.0),
            ns.box((4 - OX, 1, Z1 - Z0), loc=((4 + OX) / 2, 0, (Z0 + Z1) / 2), bevel=0.0)]
    C.part(core, "Core", C.CREAM_SHADE, recolor="wall_back", can_collide=True)

    d = C.wainscot([(X0, X1)])
    d["upper"] = [C.skin(X0, -OX, C.CHECK_TOP, Z1), C.skin(OX, X1, C.CHECK_TOP, Z1),
                  C.skin(X0, X1, Z1, C.CROWN_Z + 0.05)]
    d["crown"] = [C.crown(X0, X1)]
    d["stripe"] = C.stripes(X0, X1)
    d["back"] = C.back_trim([(X0, X1)])
    C.tag_wall_set(d)

    # deep room-side sill, runs into the reveal. Lifted SILL_PROUD so its top sits above the chair-rail top
    # and the core's top (both at 3.5): flush (coplanar) tops z-fought across the whole sill.
    sill_pts = C.fillet([(0.0, Z0 - 0.16), (-1.02, Z0 - 0.16), (-1.08, Z0 - 0.06), (-1.02, Z0), (0.0, Z0)],
                        [0, 0.04, 0.05, 0.03, 0], 2)
    sill = C.prism(sill_pts, "x", -OX - 0.42, OX + 0.42, loc=(0, 0, SILL_PROUD))
    ns.bevel(sill, width=0.03, segments=2)
    C.part([sill], "Sill", C.LAMINATE, smooth_angle=40)

    # chrome frame: room casing, exterior casing, opening lining, mullion, transom, drip sill
    t = 0.2
    lining = [ns.box((2 * OX, 0.46, t), loc=(0, 0, Z1 - t / 2), bevel=0.02, segments=1),
              ns.box((t, 0.46, Z1 - Z0), loc=(-OX + t / 2, 0, (Z0 + Z1) / 2), bevel=0.02, segments=1),
              ns.box((t, 0.46, Z1 - Z0), loc=(OX - t / 2, 0, (Z0 + Z1) / 2), bevel=0.02, segments=1),
              ns.box((2 * OX, 0.46, 0.12), loc=(0, 0, Z0 + 0.06), bevel=0.02, segments=1)]
    mull = [ns.box((0.17, 0.4, Z1 - Z0 - 0.1), loc=(0, 0, (Z0 + Z1) / 2), bevel=0.04, segments=2),
            ns.box((2 * OX - 0.1, 0.36, 0.15), loc=(0, 0, TRANSOM), bevel=0.04, segments=2)]
    drip = C.prism(C.fillet([(0.5, Z0 - 0.22), (0.86, Z0 - 0.3), (0.86, Z0 - 0.2), (0.5, Z0 + 0.02)],
                            [0, 0.03, 0.03, 0], 1), "x", -OX - 0.3, OX + 0.3)
    ns.bevel(drip, width=0.02, segments=1)
    frame = [casing(-0.53, -1), casing(0.5, 1, w=0.26, proud=0.1)] + lining + mull + [drip]
    C.part(frame, "Frame", C.CHROME, "Metal", smooth_angle=40)

    glass = ns.box((2 * OX - 0.02, 0.06, Z1 - Z0 - 0.02), loc=(0, 0, (Z0 + Z1) / 2), bevel=0.0)
    ns.tag(glass, "Glass", C.GLASS, "Glass", transparency=0.6, recolor="glass", can_collide=True,
           cast_shadow=False)


META = dict(C.wall_presets_meta(), module="wall_window", grid=8, size=[8, 12, 1], collider="Core+Glass",
            opening={"x": [-OX, OX], "z": [Z0, Z1]}, sill=Z0, head=Z1,
            placement="pivot on the wall centre line, bottom; room side = LookVector; back = exterior")

if __name__ == "__main__":
    C.run(build, "Shop_WallWindow", pivot=(0, 0, 0), meta=META)
