"""Shop_OfficeDesk — the manager's heavy wooden desk (CCTV station + hiding spot).

Dark wood double pedestal: three drawers on the left (top one = role "drawer", the
Mr. Usual "office drawer" clue spot), a cupboard on the right, an open knee space in the
middle big enough to hide in (modesty panel at the back). On top: green leather blotter,
a banker's lamp (green shade, warm bulb part role "lamp" for the desk-lamp light), a
coffee mug and a few loose papers. The CCTV bank (Shop_CCTVMonitor) goes on Socket_Monitor.
User side = front (-Y). Sockets:
  Hide     centre of the knee space, facing out (-Y)        Chair   where the sitter stands/sits, facing the desk
  Monitor  top surface, back centre (CCTV bank pivot, yaw 0)  Drawer  front of the top-left drawer (clue spot)
  LampLight bulb position (attach a SpotLight/PointLight)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D, TZ = 6.6, 3.0, 2.8
KX0, KX1 = -1.4, 1.75          # knee space x range
BRASS = "#C9A045"
LEATHER = "#2F5B45"
SHADE = "#2E8B57"
MUG = "#E8502A"


def build():
    top = C.prism(C.fillet([(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)], 0.12, 2), "z",
                  TZ - 0.22, TZ)
    ns.bevel(top, width=0.05, segments=2)
    wood = [top]
    # pedestals (with a plinth recess at the bottom)
    for x0, x1 in ((-W / 2 + 0.12, KX0), (KX1, W / 2 - 0.12)):
        wood.append(ns.box((x1 - x0, D - 0.3, TZ - 0.22 - 0.25), loc=((x0 + x1) / 2, 0.05, 0.25 + (TZ - 0.47) / 2),
                           bevel=0.04, segments=1))
    wood.append(ns.box((KX1 - KX0, 0.12, 1.6), loc=((KX0 + KX1) / 2, D / 2 - 0.3, TZ - 0.22 - 0.8), bevel=0.03,
                       segments=1))
    # drawer fronts (left) and cupboard door (right)
    dz = (TZ - 0.5) / 3
    for i in range(1, 3):
        z = 0.3 + dz * (i + 0.5) - dz
        wood.append(ns.box((KX0 + W / 2 - 0.4, 0.08, dz - 0.1), loc=((-W / 2 + KX0) / 2 + 0.06, -D / 2 + 0.11, z + 0.02),
                           bevel=0.035, segments=1))
    wood.append(ns.box((W / 2 - KX1 - 0.4, 0.08, TZ - 0.75), loc=((KX1 + W / 2) / 2 - 0.06, -D / 2 + 0.11, 0.3 + (TZ - 0.75) / 2),
                       bevel=0.035, segments=1))
    C.part(wood, "Wood", C.WOOD_DARK, "Wood", can_collide=True, smooth_angle=40)
    drawer = ns.box((KX0 + W / 2 - 0.4, 0.1, dz - 0.1), loc=((-W / 2 + KX0) / 2 + 0.06, -D / 2 + 0.11,
                                                          0.3 + dz * 2.5 + 0.02), bevel=0.035, segments=1)
    ns.tag(drawer, "Drawer", C.WOOD_DARK, "Wood", recolor="drawer", smooth_angle=40)
    plinth = [ns.box((x1 - x0 - 0.1, D - 0.45, 0.25), loc=((x0 + x1) / 2, 0.1, 0.125), bevel=0.02, segments=1)
              for x0, x1 in ((-W / 2 + 0.12, KX0), (KX1, W / 2 - 0.12))]
    C.part(plinth, "Plinth", C.RUBBER)

    # brass pulls (drawers + cupboard) and the lamp body
    pulls = []
    for i in range(3):
        z = 0.3 + dz * (i + 0.5) + 0.12
        pulls.append(C.pipe([(-2.65, -D / 2 + 0.05, z), (-2.65, -D / 2 - 0.06, z), (-2.05, -D / 2 - 0.06, z),
                             (-2.05, -D / 2 + 0.05, z)], 0.035, sides=6, corner=0.05, corner_segs=1))
    pulls.append(ns.cyl(0.07, 0.1, loc=(KX1 + 0.3, -D / 2 + 0.02, 1.7), rot=(90, 0, 0), verts=8, bevel=0.02,
                        segments=1))
    lx, ly = -2.7, 0.75
    pulls.append(ns.cyl(0.42, 0.1, loc=(lx, ly, TZ + 0.05), verts=14, radius_top=0.34, bevel=0.0))
    pulls.append(ns.cyl(0.045, 1.25, loc=(lx, ly, TZ + 0.68), verts=8, bevel=0.0))
    pulls.append(ns.cyl(0.04, 0.9, loc=(lx, ly, TZ + 1.32), rot=(0, 90, 0), verts=8, bevel=0.0))
    pulls.append(C.pipe([(lx + 0.15, ly - 0.15, TZ + 1.35), (lx + 0.15, ly - 0.15, TZ + 0.95)], 0.012, sides=4))
    pulls.append(ns.sphere(0.04, loc=(lx + 0.15, ly - 0.15, TZ + 0.93), segs=6, rings=4))
    C.part(pulls, "Brass", BRASS, "Metal", smooth_angle=55)
    shade = ns.cyl(0.3, 1.1, loc=(lx, ly, TZ + 1.42), rot=(0, 90, 0), verts=16, bevel=0.0)
    ns.boolean(shade, ns.box((2, 1, 0.5), loc=(lx, ly, TZ + 1.17), bevel=0.0))
    ns.boolean(shade, ns.cyl(0.25, 1.0, loc=(lx, ly, TZ + 1.42), rot=(0, 90, 0), verts=16, bevel=0.0))
    ns.tag(shade, "Shade", SHADE, "Glass", smooth_angle=50)
    bulb = ns.cyl(0.08, 0.75, loc=(lx, ly, TZ + 1.36), rot=(0, 90, 0), verts=8, bevel=0.0)
    ns.tag(bulb, "Bulb", "#FFE2A0", "Neon", recolor="lamp", cast_shadow=False)

    pad = ns.box((2.6, 0.62, 0.04), loc=(-0.2, -1.1, TZ + 0.02), bevel=0.015, segments=1)
    ns.tag(pad, "Blotter", LEATHER, "Fabric")
    papers = [ns.box((1.1, 0.8, 0.012), loc=(2.15, -1.0, TZ + 0.012), rot=(0, 0, 10), bevel=0.0),
              ns.box((1.1, 0.8, 0.012), loc=(2.35, -0.95, TZ + 0.026), rot=(0, 0, -6), bevel=0.0)]
    C.part(papers, "Papers", C.PAPER)
    mug = ns.cyl(0.17, 0.36, loc=(2.75, -0.3, TZ + 0.18), verts=12, bevel=0.03, segments=1)
    ns.boolean(mug, ns.cyl(0.13, 0.36, loc=(2.75, -0.3, TZ + 0.3), verts=12, bevel=0.0))
    handle = ns.torus(0.1, 0.03, loc=(2.93, -0.3, TZ + 0.18), rot=(90, 0, 0), major_segs=10, minor_segs=4)
    C.part([mug, handle], "Mug", MUG, smooth_angle=50)
    coffee = ns.cyl(0.13, 0.02, loc=(2.75, -0.3, TZ + 0.3), verts=12, bevel=0.0)
    ns.tag(coffee, "Coffee", "#3B2416")


def sockets():
    return {"Hide": (((KX0 + KX1) / 2, 0.0, 1.2), 0.0),
            "Chair": ((0.15, -D / 2 - 1.3, 0.0), 180.0),
            "Monitor": ((0.15, 0.7, TZ), 0.0),
            "Drawer": (((-W / 2 + KX0) / 2 + 0.06, -D / 2 + 0.05, 0.3 + (TZ - 0.5) / 3 * 2.5), 0.0),
            "LampLight": ((-2.7, 0.75, TZ + 1.3), 0.0)}


META = {"top": TZ, "size": [W, TZ, D], "user_side": "front (-Y)", "knee_space": {"x": [KX0, KX1], "z": [0, TZ - 0.22]},
        "hide_spots": ["Hide"], "light_hint": {"part": "Bulb", "color": "#FFD9A0", "range": 12, "brightness": 1.2}}

if __name__ == "__main__":
    C.run(build, "Shop_OfficeDesk", meta=META, sockets=sockets())
