"""Lobby_StoreWall — 8 x 14 solid exterior wall module of the STACKHOUSE HQ building.

Matches Lobby_StoreFrontBay course for course: concrete plinth, red brick with modelled
mortar (staggered head joints outside, course lines inside), the red-orange header band
with bolts at the same height as the storefront's steel header, mustard pinstripes, brick
parapet and cream coping. A gooseneck barn-light sconce with a red-orange enamel shade
hangs on the exterior face (Bulb, Neon, role "lamp").

Pivot = bottom-centre of the wall centre line; exterior = front (-Y). Ends land on the
8-stud grid so walls and storefront bays butt seamlessly. can_collide = False (the map adds
collision). Socket Light = bulb centre (attach a SpotLight facing down).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W = 8.0
X0, X1 = -W / 2, W / 2
HT = C.HQ_T / 2
SC_Z = 8.5                    # sconce wall plate height


def build():
    hz0, hz1 = C.HQ_HEADER
    # brick stops under / resumes over the header band so their end faces never share a plane
    body = [ns.box((W, C.HQ_T, hz0 - C.HQ_PLINTH), loc=(0, 0, (C.HQ_PLINTH + hz0) / 2), bevel=0.0),
            ns.box((W, C.HQ_T, C.HQ_COPING - hz1), loc=(0, 0, (hz1 + C.HQ_COPING) / 2), bevel=0.0)]
    C.part(body, "Brick", C.BRICK, recolor="brick", smooth_angle=30)
    mortar = []
    for z0, z1 in ((C.HQ_PLINTH, hz0 - 0.2), (hz1, C.HQ_COPING)):
        mortar += C.hq_mortar_face(X0, X1, z0, z1, -1)
        mortar += C.hq_mortar_face(X0, X1, z0, z1, 1, heads=False)
    C.part(mortar, "Mortar", C.MORTAR, smooth_angle=30)
    C.part([C.hq_plinth(X0, X1)], "Plinth", C.CONCRETE, "Concrete", smooth_angle=35)
    C.part([C.hq_coping(X0, X1)], "Cream", C.CREAM, smooth_angle=35)
    C.part([C.hq_header_band(X0, X1)], "Header", C.BRAND, recolor="header", smooth_angle=35)
    C.part(C.hq_pinstripes(X0, X1), "Pinstripe", C.MUSTARD, smooth_angle=30)
    bolts = []
    for k in range(5):
        x = X0 + 0.8 + k * 1.6
        for z in (hz0 + 0.22, hz1 - 0.22):
            bolts.append(ns.box((0.13, 0.06, 0.13), loc=(x, -HT - 0.08, z), bevel=0.0))

    # gooseneck barn light
    fy = -HT - 0.02
    plate = ns.cyl(0.32, 0.08, verts=12, bevel=0.0)
    C.place(plate, (0, fy - 0.04, SC_Z), pitch=90)
    arm = C.pipe([(0, fy - 0.05, SC_Z), (0, fy - 0.5, SC_Z + 0.1), (0, fy - 1.1, SC_Z + 0.55), (0, fy - 1.55, SC_Z + 0.45),
                  (0, fy - 1.7, SC_Z + 0.2)], 0.06, sides=6, corner=0.25, corner_segs=2)
    sx, sy, sz = 0, fy - 1.7, SC_Z + 0.2
    # lamp socket from the arm end down into the bulb's top (the bulb hung 0.22 under the shade, unattached)
    socket = ns.cyl(0.07, 0.3, loc=(sx, sy, sz - 0.1), verts=8, radius_top=0.06, bevel=0.0)
    C.part(bolts + [plate, arm, socket], "Chrome", C.CHROME, "Metal", smooth_angle=50)
    shade = ns.lathe([(0.08, 0.0), (0.16, -0.05), (0.42, -0.28), (0.62, -0.55), (0.6, -0.58), (0.4, -0.31),
                      (0.14, -0.08), (0.06, -0.03)], verts=14, loc=(sx, sy, sz))
    C.part([shade], "Shade", C.BRAND, smooth_angle=60)
    bulb = ns.sphere(0.18, loc=(sx, sy, sz - 0.4), segs=8, rings=5)
    ns.tag(bulb, "Bulb", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)


SOCKETS = {"Light": ((0, -HT - 0.02 - 1.7, SC_Z + 0.2 - 0.4), 0.0)}
META = {"module": "hq_wall", "grid": 8, "size": [8, 14, 1.5], "exterior": "front (-Y / LookVector)",
        "matches": "Lobby_StoreFrontBay", "header_band_z": list(C.HQ_HEADER),
        "roles": {"brick": "Brick", "header": "Header", "lamp": "Bulb"},
        "light_hint": {"type": "SpotLight", "face": "Bottom", "color": "#FFD9A0", "range": 16, "angle": 90,
                       "brightness": 1.5},
        "collision": "none (map adds collision)"}

if __name__ == "__main__":
    C.run(build, "Lobby_StoreWall", sockets=SOCKETS, pivot=(0, 0, 0), meta=META)
