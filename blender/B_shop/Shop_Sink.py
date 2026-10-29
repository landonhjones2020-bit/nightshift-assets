"""Shop_Sink — restroom pedestal sink: chunky porcelain basin with a bowl, tapered pedestal,
chrome gooseneck faucet with two cross taps and a drain. Rim height 3.0.
Back (+Y) goes against the wall. Pivot = bottom-centre.
Socket Tap = faucet spout (for a drip/running-water effect).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
RIM = 3.0
BW, BD = 2.6, 1.9


def build():
    yc = 0.0
    basin = C.prism(C.fillet([(-BW / 2, -BD / 2), (BW / 2, -BD / 2), (BW / 2, BD / 2), (-BW / 2, BD / 2)],
                             [0.6, 0.6, 0.1, 0.1], 4), "z", RIM - 0.55, RIM)
    ns.bevel(basin, width=0.07, segments=2)
    ns.apply_all(basin)
    bowl = ns.sphere(1.0, loc=(0, -0.12, RIM + 0.02), scale=(0.95, 0.66, 0.42), segs=16, rings=8)
    ns.boolean(basin, bowl)
    ped = ns.lathe([(0.42, 0.0), (0.32, 0.12), (0.24, 0.9), (0.22, 1.7), (0.32, 2.3), (0.55, RIM - 0.5),
                    (0.0, RIM - 0.5)], verts=16, loc=(0, 0.15, 0))
    back = ns.box((BW, 0.22, 0.55), loc=(0, BD / 2 - 0.11, RIM + 0.27), bevel=0.06, segments=2)
    C.part([basin, ped, back], "Porcelain", C.PORCELAIN, smooth_angle=50)

    ty = BD / 2 - 0.36
    spout = C.pipe([(0, ty, RIM + 0.05), (0, ty, RIM + 0.75), (0, ty - 0.45, RIM + 0.75), (0, ty - 0.5, RIM + 0.55)],
                   0.06, sides=8, corner=0.18, corner_segs=3)
    base = ns.cyl(0.13, 0.1, loc=(0, ty, RIM + 0.05), verts=10, bevel=0.03, segments=1)
    taps = []
    for sx in (-1, 1):
        x = sx * 0.62
        taps.append(ns.cyl(0.08, 0.2, loc=(x, ty, RIM + 0.1), verts=8, bevel=0.0))
        taps.append(ns.box((0.36, 0.07, 0.07), loc=(x, ty, RIM + 0.24), bevel=0.025, segments=1))
        taps.append(ns.box((0.07, 0.36, 0.07), loc=(x, ty, RIM + 0.24), bevel=0.025, segments=1))
    drain = ns.cyl(0.13, 0.03, loc=(0, -0.12, RIM - 0.38), verts=10, bevel=0.0)
    C.part([spout, base, drain] + taps, "Chrome", C.CHROME, "Metal", smooth_angle=55)
    caps = [ns.cyl(0.05, 0.03, loc=(sx * 0.62, ty, RIM + 0.29), verts=8, bevel=0.0) for sx in (-1, 1)]
    ns.tag(caps[0], "TapHot", "#D9443A")
    ns.tag(caps[1], "TapCold", "#3A7BD9")


META = {"rim_height": RIM, "back": "+Y against the wall", "depth": BD}

if __name__ == "__main__":
    C.run(build, "Shop_Sink", meta=META, sockets={"Tap": ((0, BD / 2 - 0.86, RIM + 0.5), 0.0)})
