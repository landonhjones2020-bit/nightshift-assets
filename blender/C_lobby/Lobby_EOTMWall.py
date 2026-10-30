"""Lobby_EOTMWall — "Employee of the Month" wall piece (12 wide x 8 tall).

Navy backing board with a mustard pinstripe border, a red-orange swallowtail banner with
modelled cream "EMPLOYEE OF THE MONTH" letters and gold stars, three gilded portrait
frames (each photo window is its own part Photo1..Photo3, role "photo", Front face: code
puts the weekly top players' avatars there), a gold star over the centre (#1) frame,
small brass name tabs under each frame, and a brass plaque (Plaque, role "plaque", Front
face) at the bottom for the week / board name.

Wall-mounted: modelled with its back face on the wall plane (Blender y = 0), front -Y.
PIVOT = bottom-centre of the back face, so wall_back_z = 0. Suggested hang: pivot ~1.5
above the floor. Sockets: Frame1..Frame3 (photo face centres, left to right as seen from
the front), Name1..Name3 (name tab faces), Plaque (plaque face).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 12.0, 8.0, 0.25
FX = (-3.8, 0.0, 3.8)          # frame centres (x, Blender) left -> right as seen from the front
FZ = 4.1
FO_W, FO_H = 3.1, 3.7          # frame outer
PH_W, PH_H = 2.3, 2.9          # photo window
NAME_W, NAME_H, NAME_Z = 1.9, 0.42, 1.85
PL_W, PL_H, PL_Z = 4.4, 0.8, 0.95
BAN_Z = 7.05
PHOTO = "#3B4252"


def star(r_out, r_in, cx, cz, n=5):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(90 + 180.0 * i / n)
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def build():
    back = C.prism(C.rrect(W, H, 0.4, 3, 0, H / 2), "y", -T, 0.0)
    ns.bevel(back, width=0.05, segments=1)
    C.part([back], "Backing", C.NAVY, smooth_angle=40)
    border = C.ring_slab(C.rrect(W - 0.5, H - 0.5, 0.25, 2, 0, H / 2), C.rrect(W - 0.66, H - 0.66, 0.2, 2, 0, H / 2), "y",
                         -T - 0.03, -T + 0.02)

    # banner: main band + swallowtails behind it
    band = C.prism(C.rrect(9.2, 0.98, 0.12, 2, 0, BAN_Z), "y", -T - 0.2, -T - 0.08)
    ns.bevel(band, width=0.03, segments=1)
    C.part([band], "Banner", C.BRAND, smooth_angle=40)
    tails = []
    for sx in (-1, 1):
        pts = [(4.1, BAN_Z - 0.62), (5.75, BAN_Z - 0.62), (5.35, BAN_Z - 0.22), (5.75, BAN_Z + 0.18), (4.1, BAN_Z + 0.18)]
        pts = [(sx * x, z) for x, z in pts]
        tails.append(C.prism(pts, "y", -T - 0.12, -T - 0.02))
    C.part(tails, "BannerTails", C.BRAND_DARK, smooth_angle=None)
    # flat (single-sided) letter decals sit depth/2 in front of loc: 0.01 proud of the band's face (-T - 0.2);
    # at loc -T - 0.22 they hovered 0.05 in front of it
    letters = C.text("EMPLOYEE OF THE MONTH", 0.56, 0.06, (0, -T - 0.18, BAN_Z), width=8.2, res=1, spacing=1.04,
                     flat=True)
    C.part([letters], "Letters", C.CREAM, smooth_angle=None)

    gold = []
    for sx in (-1, 1):
        gold.append(C.prism(star(0.42, 0.18, sx * 5.0, BAN_Z + 0.02), "y", -T - 0.3, -T - 0.16))
    gold.append(C.prism(star(0.42, 0.18, 0.0, FZ + FO_H / 2 + 0.36), "y", -T - 0.27, -T - 0.06))
    # gilded frames: outer bevelled ring, darker inner lip, corner rosettes
    lip, photos = [], []
    for i, x in enumerate(FX):
        outer = C.ring_slab(C.rrect(FO_W, FO_H, 0.18, 1, x, FZ), C.rrect(PH_W + 0.5, PH_H + 0.5, 0.06, 1, x, FZ), "y",
                            -T - 0.3, -T + 0.02)
        ns.bevel(outer, width=0.06, segments=1, angle=50)
        gold.append(outer)
        lip.append(C.ring_slab(C.rrect(PH_W + 0.56, PH_H + 0.56, 0.06, 1, x, FZ), C.rrect(PH_W, PH_H, 0.04, 1, x, FZ), "y",
                               -T - 0.18, -T + 0.02))
        ph = C.prism(C.rrect(PH_W, PH_H, 0.04, 1, x, FZ), "y", -T - 0.12, -T + 0.01)
        ns.tag(ph, f"Photo{i + 1}", PHOTO, recolor="photo", cast_shadow=False, smooth_angle=None)
    C.part(gold, "Gilding", C.GOLD, "Metal", smooth_angle=40)
    C.part(lip, "FrameLip", "#A87C2A", "Metal", smooth_angle=40)

    # brass name tabs + the plaque (own part, role plaque) on a brass-screwed mount
    brass = []
    for x in FX:
        brass.append(ns.box((NAME_W, 0.08, NAME_H), loc=(x, -T - 0.04, NAME_Z), bevel=0.03, segments=1))
    mount = C.prism(C.rrect(PL_W + 0.36, PL_H + 0.3, 0.12, 2, 0, PL_Z), "y", -T - 0.06, -T + 0.02)
    screws = [ns.cyl(0.06, 0.06, loc=(0, 0, 0), verts=6, bevel=0.0) for _ in range(4)]
    for k, (sx, sz) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        C.place(screws[k], (sx * (PL_W / 2 + 0.08), -T - 0.12, PL_Z + sz * (PL_H / 2 - 0.05)), pitch=90)
    C.part(brass + screws, "Brass", C.BRASS, "Metal", smooth_angle=40)
    C.part([mount, border], "Trim", C.MUSTARD, smooth_angle=40)
    pl = C.prism(C.rrect(PL_W, PL_H, 0.1, 2, 0, PL_Z), "y", -T - 0.12, -T - 0.03)
    ns.bevel(pl, width=0.03, segments=1)
    ns.tag(pl, "Plaque", C.BRASS, "Metal", recolor="plaque", smooth_angle=40)


def sockets():
    s = {}
    for i, x in enumerate(FX):
        s[f"Frame{i + 1}"] = ((x, -T - 0.12, FZ), 0.0)
        s[f"Name{i + 1}"] = ((x, -T - 0.08, NAME_Z), 0.0)
    s["Plaque"] = ((0, -T - 0.12, PL_Z), 0.0)
    return s


META = {"mount": "wall", "pivot": "bottom-centre of the back face (on the wall plane)", "wall_back_z": 0.0,
        "hang_height": 1.5, "frame_size": [PH_W, PH_H], "name_size": [NAME_W, NAME_H], "plaque_size": [PL_W, PL_H],
        "frame_order": "Frame1 left, Frame2 centre (#1, star above), Frame3 right (as seen from the front)",
        "surfaces": [C.screen_meta(f"Photo{i}", PH_W, PH_H) for i in (1, 2, 3)] + [C.screen_meta("Plaque", PL_W, PL_H)],
        "roles": {"photo": "Photo1..Photo3", "plaque": "Plaque"}}

if __name__ == "__main__":
    C.run(build, "Lobby_EOTMWall", sockets=sockets(), pivot=(0, 0, 0), meta=META)
