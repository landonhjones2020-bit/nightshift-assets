"""Shop_PosterC — framed "EMPLOYEE OF THE MONTH" plaque (4 x 3 x 0.2).

Walnut plaque board with a chamfered edge, a thin gold inlay border, gold "EMPLOYEE OF THE
MONTH" lettering, a gold-framed blank photo area on the left (part Photo, role "screen",
dark glossy Glass: the game draws the employee's avatar there), and on the right a brass
nameplate (part Nameplate, role "nameplate", optional: the name can be drawn on it), a gold
star and a small STACKHOUSE wordmark. Brass rosette screws in the corners.
Sockets: Photo (photo face centre, yaw 0 = facing front), Name (nameplate face centre).
Wall-mounted: pivot = bottom-centre of the back face (+Y, flat on the wall).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 4.0, 3.0, 0.14
FY = -T                          # board front face
PH_W, PH_H = 1.3, 1.62           # photo screen size
PX, PZ = -0.98, 1.3              # photo centre
NP_W, NP_H = 1.62, 0.44          # nameplate
NX, NZ = 0.92, 1.86
WALNUT = "#4E3222"


def build():
    board = C.prism(C.rrect(W, H, 0.14, 2, 0, H / 2), "y", FY, 0.0)
    ns.bevel(board, width=0.05, segments=1, angle=50)
    C.part([board], "Board", WALNUT, "Wood", smooth_angle=45)

    gold = []
    gold.append(C.ring_slab(C.rrect(W - 0.24, H - 0.24, 0.08, 2, 0, H / 2), C.rrect(W - 0.32, H - 0.32, 0.05, 2, 0, H / 2),
                            "y", FY - 0.012, FY + 0.005))
    # gold photo frame + star
    gold.append(C.ring_slab(C.rrect(PH_W + 0.26, PH_H + 0.26, 0.05, 1, PX, PZ), C.rrect(PH_W, PH_H, 0.02, 1, PX, PZ),
                            "y", FY - 0.07, FY + 0.005))
    gold.append(C.prism(C.star(0.3, 0.13, NX, 1.06), "y", FY - 0.04, FY + 0.005))
    title = C.text("EMPLOYEE OF THE MONTH", 0.3, 0.02, (0, FY - 0.01, H - 0.42), width=W - 0.72, res=1, spacing=1.05,
                   flat=True)
    gold.append(title)
    C.part(gold, "Gilding", C.GOLD, "Metal", smooth_angle=40)

    word = C.text("STACKHOUSE", 0.16, 0.02, (NX, FY - 0.01, 0.5), width=1.05, res=1, spacing=1.1, flat=True)
    C.part([word], "Wordmark", C.CREAM, smooth_angle=None)

    photo = ns.box((PH_W, 0.03, PH_H), loc=(PX, FY - 0.015, PZ), bevel=0.0)
    ns.tag(photo, "Photo", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)

    plate = C.prism(C.rrect(NP_W, NP_H, 0.06, 2, NX, NZ), "y", FY - 0.05, FY + 0.005)
    ns.bevel(plate, width=0.015, segments=1)
    ns.tag(plate, "Nameplate", C.BRASS, "Metal", recolor="nameplate", smooth_angle=40)
    screws = C.screw_heads([(sx * (W / 2 - 0.13), sz) for sx in (-1, 1) for sz in (0.13, H - 0.13)], FY - 0.02,
                           r=0.06, verts=8)
    screws += C.screw_heads([(NX + sx * (NP_W / 2 - 0.1), NZ) for sx in (-1, 1)], FY - 0.07, r=0.035, verts=6)
    C.part(screws, "Screws", C.BRASS, "Metal", smooth_angle=40)


SOCKETS = {"Photo": ((PX, FY - 0.03, PZ), 0.0), "Name": ((NX, FY - 0.05, NZ), 0.0)}
META = {"mount": "wall", "pivot": "bottom-centre of the back face (flat on the wall)", "hang_height": 4.5,
        "screen_size": [PH_W, PH_H], "surfaces": [C.screen_meta("Photo", PH_W, PH_H), C.screen_meta("Nameplate", NP_W, NP_H)],
        "name_size": [NP_W, NP_H], "roles": {"screen": "Photo", "nameplate": "Nameplate"}}

if __name__ == "__main__":
    C.run(build, "Shop_PosterC", sockets=SOCKETS, pivot=(0, 0, 0), meta=META,
          preview=lambda *a: C.front_preview(*a, backdrop=C.NAVY))
