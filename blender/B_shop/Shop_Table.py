"""Shop_Table — freestanding 3 x 3 diner table (top 2.8): cream laminate top on a chrome
band, chrome pedestal with a round foot. Square flat sides so tables push together
(the Night 5 Patron's Plate).
Sockets: Top (centre of the top), ChairA (-Y side, facing the table), ChairB (+Y side).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
S, TZ = 3.0, 2.8


def build():
    top = C.prism(C.rrect(S - 0.06, S - 0.06, 0.22, 3), "z", TZ - 0.12, TZ)
    ns.bevel(top, width=0.02, segments=1)
    C.part([top], "Top", C.LAMINATE, can_collide=True, smooth_angle=40)
    band = C.prism(C.rrect(S, S, 0.25, 3), "z", TZ - 0.2, TZ - 0.01)
    ns.bevel(band, width=0.02, segments=1)
    post = ns.cyl(0.17, TZ - 0.3, loc=(0, 0, (TZ - 0.3) / 2 + 0.1), verts=12, bevel=0.0)
    collar = ns.cyl(0.34, 0.12, loc=(0, 0, TZ - 0.26), verts=14, bevel=0.03, segments=1)
    plate = ns.box((1.2, 1.2, 0.06), loc=(0, 0, TZ - 0.21), bevel=0.02, segments=1)
    foot = ns.cyl(0.95, 0.14, loc=(0, 0, 0.07), verts=18, radius_top=0.78, bevel=0.0)
    ring = ns.cyl(0.4, 0.12, loc=(0, 0, 0.18), verts=14, radius_top=0.2, bevel=0.0)
    C.part([band, post, collar, plate, foot, ring], "Frame", C.CHROME, "Metal", can_collide=False, smooth_angle=50)
    glide = ns.cyl(0.98, 0.03, loc=(0, 0, 0.015), verts=18, bevel=0.0)
    ns.tag(glide, "Glide", C.RUBBER)


META = {"table_height": TZ, "size": [S, TZ, S], "push_together": True}

if __name__ == "__main__":
    C.run(build, "Shop_Table", meta=META,
          sockets={"Top": ((0, 0, TZ), 0.0), "ChairA": ((0, -2.3, 0), 180.0), "ChairB": ((0, 2.3, 0), 0.0)})
