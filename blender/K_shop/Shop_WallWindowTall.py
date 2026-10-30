"""Shop_WallWindowTall — 8 x 20 wall module with a tall diner window (sill 3.5, head 16.5).

Opening 6.4 wide x 13 tall: one big pane with a chunky chrome transom bar at 12 (level with
the frieze rail on Shop_WallTall), in the Shop_WallWindow chrome frame language: room-side
casing, opening lining, a deep laminate sill whose top sits just above the chrome chair
rail, and an exterior casing + drip sill on the back (+Y, parking-lot side).
The lower 12 studs carry the same wainscot / checker / chair rail / pinstripes as the
12-tall modules; the crown sits at the top (19.45 .. 20).
Glass: ONE part `Glass` (role glass, Glass, transparency 0.6, collides) behind the transom.
Collision: Core (full module box) + Glass. Roles / presets / meta keys as Shop_WallWindow.
`build(hw, ox)` also makes Shop_WallWindowWide (16 wide, no centre mullion).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
H = C.TALL_H
HW = C.WALL_W / 2            # half module width
OX = 3.2                     # half opening width
Z0, Z1 = C.SILL_Z, 16.5      # sill / head
TRANSOM = C.FRIEZE_Z         # transom bar centre (12)
TB = 0.3                     # transom bar height
SILL_PROUD = 0.02            # room-side sill top above the opening sill line / chair rail top


def casing(ox, face_y, out_dir, w=0.32, proud=0.12):
    """U-shaped chrome casing around the opening on one face (bottom open: the sill covers it).
    out_dir = -1 for the room face (-Y), +1 for the back face."""
    pts = [(-ox - w, Z0), (-ox, Z0), (-ox, Z1), (ox, Z1), (ox, Z0), (ox + w, Z0), (ox + w, Z1 + w), (-ox - w, Z1 + w)]
    pts = C.fillet(pts, [0, 0, 0, 0, 0, 0, 0.1, 0.1], 2)
    a0, a1 = sorted((face_y, face_y + out_dir * proud))
    ob = C.prism(pts, "y", a0, a1)
    ns.bevel(ob, width=0.035, segments=2)
    return ob


def build(hw=HW, ox=OX):
    x0, x1 = -hw, hw
    pier = hw - ox
    core = [ns.box((2 * hw, 1, Z0), loc=(0, 0, Z0 / 2), bevel=0.0),
            ns.box((2 * hw, 1, H - Z1), loc=(0, 0, (H + Z1) / 2), bevel=0.0),
            ns.box((pier, 1, Z1 - Z0), loc=(-(hw + ox) / 2, 0, (Z0 + Z1) / 2), bevel=0.0),
            ns.box((pier, 1, Z1 - Z0), loc=((hw + ox) / 2, 0, (Z0 + Z1) / 2), bevel=0.0)]
    C.part(core, "Core", C.CREAM_SHADE, recolor="wall_back", can_collide=True)

    d = C.S.wainscot([(x0, x1)])
    d["upper"] = [C.skin(x0, -ox, C.CHECK_TOP, Z1), C.skin(ox, x1, C.CHECK_TOP, Z1),
                  C.skin(x0, x1, Z1, C.TALL_CROWN_Z + 0.05)]
    d["crown"] = [C.crown_tall(x0, x1)]
    # pinstripes + frieze rail (+ the exterior band) on the piers: their inner ends stop inside the
    # casings (ox .. ox + 0.32 room side, ox .. ox + 0.26 back), never on the casing's inner face plane
    e = ox + 0.12
    d["stripe"] = C.stripes(x0, -e) + C.stripes(e, x1)
    d["rail"] += [C.frieze_rail(x0, -e), C.frieze_rail(e, x1)]
    d["back"] = C.S.back_trim([(x0, x1)]) + [C.back_band(x0, -e), C.back_band(e, x1)]
    C.tag_wall_set(d)

    # deep room-side sill, runs into the reveal; lifted SILL_PROUD above the chair-rail / core tops (3.5)
    sill_pts = C.fillet([(0.0, Z0 - 0.16), (-1.02, Z0 - 0.16), (-1.08, Z0 - 0.06), (-1.02, Z0), (0.0, Z0)],
                        [0, 0.04, 0.05, 0.03, 0], 2)
    sill = C.prism(sill_pts, "x", -ox - 0.42, ox + 0.42, loc=(0, 0, SILL_PROUD))
    ns.bevel(sill, width=0.03, segments=2)
    C.part([sill], "Sill", C.LAMINATE, smooth_angle=40)

    # chrome frame: room casing, exterior casing, opening lining, transom bar, drip sill
    t = 0.2
    lining = [ns.box((2 * ox, 0.46, t), loc=(0, 0, Z1 - t / 2), bevel=0.02, segments=1),
              ns.box((t, 0.46, Z1 - Z0), loc=(-ox + t / 2, 0, (Z0 + Z1) / 2), bevel=0.02, segments=1),
              ns.box((t, 0.46, Z1 - Z0), loc=(ox - t / 2, 0, (Z0 + Z1) / 2), bevel=0.02, segments=1),
              ns.box((2 * ox, 0.46, 0.12), loc=(0, 0, Z0 + 0.06), bevel=0.02, segments=1)]
    transom = [ns.box((2 * ox - 0.1, 0.4, TB), loc=(0, 0, TRANSOM), bevel=0.05, segments=2)]
    drip = C.prism(C.fillet([(0.5, Z0 - 0.22), (0.86, Z0 - 0.3), (0.86, Z0 - 0.2), (0.5, Z0 + 0.02)],
                            [0, 0.03, 0.03, 0], 1), "x", -ox - 0.3, ox + 0.3)
    ns.bevel(drip, width=0.02, segments=1)
    frame = [casing(ox, -0.53, -1), casing(ox, 0.5, 1, w=0.26, proud=0.1)] + lining + transom + [drip]
    C.part(frame, "Frame", C.CHROME, "Metal", smooth_angle=40)

    glass = ns.box((2 * ox - 0.02, 0.06, Z1 - Z0 - 0.02), loc=(0, 0, (Z0 + Z1) / 2), bevel=0.0)
    ns.tag(glass, "Glass", C.GLASS, "Glass", transparency=0.6, recolor="glass", can_collide=True,
           cast_shadow=False)


def meta(hw=HW, ox=OX, grid=8):
    return dict(C.wall_presets_meta(), module="wall_window", grid=grid, size=[int(2 * hw), 20, 1], collider="Core+Glass",
                opening={"x": [-ox, ox], "z": [Z0, Z1]}, sill=Z0, head=Z1, transom=TRANSOM, height=20,
                placement="pivot on the wall centre line, bottom; room side = LookVector; back = exterior")


META = meta()

if __name__ == "__main__":
    C.run(build, "Shop_WallWindowTall", pivot=(0, 0, 0), meta=META)
