"""Shop_PhotoBoard — cork board of the Regulars' photos in the manager's office.

Wood-framed cork board with a paper label strip (role sign_panel: "REGULARS"), four
polaroid cards whose photo windows are blank panels (Photo1..Photo4, role "photo": the
Regular's picture + favourite sandwich via SurfaceGui/Decal), a yellow sticky note under
each (Note1..Note4, role sign_panel: the two handwritten notes), red push pins and red
yarn strung between the pins. Photo/note panels are axis-aligned so SurfaceGuis fit.
Wall-mounted: pivot = bottom-centre of the back face (+Y, touches the wall).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 6.6, 4.6, 0.16
STICKY = "#F4D85A"
PIN = "#D63A3A"
XS = (-2.4, -0.8, 0.8, 2.4)


def build():
    zc = H / 2
    frame = C.prism(C.rrect(W, H, 0.12, 2, 0, zc), "y", -T, 0.0)
    ns.boolean(frame, ns.box((W - 0.5, 1, H - 0.5), loc=(0, 0, zc), bevel=0.0))
    ns.bevel(frame, width=0.04, segments=1)
    ns.tag(frame, "Frame", C.WOOD, "Wood", smooth_angle=40)
    cork = ns.box((W - 0.48, 0.08, H - 0.48), loc=(0, -0.08, zc), bevel=0.0)
    ns.tag(cork, "Cork", C.CORK, "Fabric")
    face = -0.12      # cork surface y

    label = ns.box((2.6, 0.02, 0.48), loc=(0, face - 0.012, H - 0.62), bevel=0.0)
    ns.tag(label, "Label", C.PAPER, recolor="sign_panel")

    cards, pins, pin_pts = [], [], []
    for i, x in enumerate(XS):
        z_card = 2.55 + (0.08 if i % 2 else -0.04)
        cards.append(ns.box((1.3, 0.03, 1.6), loc=(x, face - 0.02, z_card), bevel=0.01, segments=1))
        photo = ns.box((1.1, 0.012, 1.1), loc=(x, face - 0.04, z_card + 0.16), bevel=0.0)
        ns.tag(photo, f"Photo{i + 1}", "#3B4252", recolor="photo")
        note = ns.box((1.05, 0.02, 0.9), loc=(x + (0.08 if i % 2 == 0 else -0.08), face - 0.015, 1.05), bevel=0.0)
        ns.tag(note, f"Note{i + 1}", STICKY, recolor="sign_panel")
        for px, pz in ((x, z_card + 0.68), (x + (0.08 if i % 2 == 0 else -0.08), 1.42)):
            pins.append(ns.sphere(0.075, loc=(px, face - 0.13, pz), segs=8, rings=5))
            pins.append(ns.cyl(0.05, 0.08, loc=(px, face - 0.07, pz), rot=(90, 0, 0), verts=6, bevel=0.0))
        pin_pts.append((x, face - 0.13, z_card + 0.68))
    C.part(cards, "Cards", "#F5F2EA", smooth_angle=30)
    C.part(pins, "Pins", PIN, smooth_angle=60)
    # red yarn between the photo pins (sagging) and down to one note
    yarn = []
    for a, b in zip(pin_pts[:-1], pin_pts[1:]):
        m = ((a[0] + b[0]) / 2, a[1] + 0.01, (a[2] + b[2]) / 2 - 0.22)
        yarn.append(C.pipe([a, m, b], 0.02, sides=4))
    yarn.append(C.pipe([pin_pts[1], (0.1, face - 0.12, 2.0), (0.88, face - 0.13, 1.42)], 0.02, sides=4))
    C.part(yarn, "Yarn", "#C42C2C", smooth_angle=60)
    # a couple of loose scraps (decor only, rotated)
    scraps = [ns.box((0.8, 0.012, 0.55), loc=(-2.65, face - 0.008, 4.0), rot=(0, 9, 0), bevel=0.0),
              ns.box((0.6, 0.012, 0.75), loc=(2.75, face - 0.008, 3.95), rot=(0, -7, 0), bevel=0.0)]
    C.part(scraps, "Scraps", "#E6DCC4")


META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)",
        "surfaces": ([{"part": f"Photo{i}", "face": "Front"} for i in range(1, 5)]
                     + [{"part": f"Note{i}", "face": "Front"} for i in range(1, 5)]
                     + [{"part": "Label", "face": "Front"}]),
        "regular_order": ["Gus", "Mina", "Walt", "Jo"]}

if __name__ == "__main__":
    C.run(build, "Shop_PhotoBoard", pivot=(0, 0, 0), meta=META, sockets={"Read": ((0, -3.0, 0), 180.0)})
