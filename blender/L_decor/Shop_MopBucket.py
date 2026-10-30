"""Shop_MopBucket — yellow commercial mop bucket on casters, with wringer and mop.

Tapered caution-yellow bucket with a rolled rim and dirty grey-blue water, four black
casters, "CAUTION" moulded on the front. A dark grey down-press wringer sits on the back
half of the rim with its chrome lever and black grip; a wooden-handled mop leans in it,
its grey-white strands bunched in the wringer and hanging over the front edge.
Front faces -Y, pivot = bottom-centre. ~2.0 x 4.5 x 1.6.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
Z0, Z1 = 0.24, 1.32           # bucket bottom / body top (rim above)
RIM = 1.42
WATER = 1.12
GREY = "#3D4045"
STRANDS = "#CFC8B6"


def ring(w, d, z, r):
    return C.ring3(C.rrect(w, d, r, 2), z)


def build():
    rings = [ring(1.56, 1.06, Z0, 0.22), ring(1.78, 1.28, Z1, 0.28), ring(1.88, 1.38, Z1 + 0.01, 0.3),
             ring(1.88, 1.38, RIM, 0.3), ring(1.7, 1.2, RIM, 0.26), ring(1.66, 1.16, WATER - 0.03, 0.25)]
    bucket = C.loft(rings, cap0=True, cap1=True)
    C.part([bucket], "Bucket", C.SAFETY_YELLOW, smooth_angle=40)
    water = C.prism(C.rrect(1.64, 1.14, 0.24, 2), "z", WATER - 0.03, WATER)
    C.part([water], "Water", "#6E858C", smooth_angle=None)

    # casters: fork + wheel at each bottom corner
    forks, wheels = [], []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.6, sy * 0.36
            forks.append(ns.box((0.16, 0.16, 0.1), loc=(x, y, Z0 - 0.04), bevel=0.0))
            wheels.append(ns.cyl(0.1, 0.09, loc=(x, y, 0.1), rot=(0, 90, 0), verts=6, bevel=0.0))
    C.part(forks, "Forks", GREY, smooth_angle=30)
    C.part(wheels, "Wheels", C.RUBBER, smooth_angle=40)

    # CAUTION moulded on the sloped front wall
    zc = 0.82
    yf = -(0.53 + 0.11 * (zc - Z0) / (Z1 - Z0)) - 0.012
    lean = math.degrees(math.atan2(0.11, Z1 - Z0))
    cau = C.text("CAUTION", 0.2, 0.01, (0, 0.005, 0), width=1.0, res=1, spacing=1.08, flat=True)
    C.place([cau], loc=(0, yf, zc), pitch=lean)
    C.part([cau], "Caution", "#26272B", smooth_angle=None)

    # wringer on the back half of the rim
    wy = 0.22
    wr = [ns.box((1.0, 0.62, 0.5), loc=(0, wy, RIM + 0.22), bevel=0.06, segments=1),
          ns.box((0.08, 0.7, 0.62), loc=(0.53, wy, RIM + 0.3), bevel=0.0),
          ns.box((0.08, 0.7, 0.62), loc=(-0.53, wy, RIM + 0.3), bevel=0.0)]
    C.part(wr, "Wringer", GREY, smooth_angle=35)
    lever = C.pipe([(0.6, wy - 0.1, RIM + 0.45), (0.66, wy + 0.25, RIM + 1.2), (0.62, wy + 0.55, RIM + 1.75)], 0.045, sides=6)
    C.part([lever], "Lever", C.CHROME, "Metal", smooth_angle=50)
    grip = ns.cyl(0.075, 0.42, loc=(0.62, wy + 0.6, RIM + 1.92), rot=(-28, 0, 0), verts=6, bevel=0.0)
    C.part([grip], "Grip", "#1E1F22", smooth_angle=40)

    # mop: handle leaning back-left out of the wringer, head bunched in it, strands over the front
    base = (-0.12, wy - 0.02, RIM + 0.15)
    top = (-0.55, wy + 0.42, 4.5)
    handle = C.rod(base, top, 0.055, verts=6)
    cap = C.rod((top[0] + 0.02, top[1] + 0.02, 4.38), (top[0], top[1], 4.5), 0.07, verts=6)
    C.part([handle], "MopHandle", "#B88A55", "Wood", smooth_angle=40)
    C.part([cap], "MopCap", "#2F6FB0", smooth_angle=40)
    head = ns.sphere(0.4, loc=(-0.1, wy - 0.1, RIM + 0.5), scale=(1.2, 0.9, 0.62), segs=8, rings=5)
    ns.jitter(head, amount=0.07, seed=3)
    strands = [head]
    import random
    rnd = random.Random(8)
    for k in range(6):
        # strands drape forward off the wringer's front edge and down into the water
        x = -0.42 + k * 0.15 + rnd.uniform(-0.03, 0.03)
        reach = rnd.uniform(0.0, 0.18)
        strands.append(C.pipe([(x, wy - 0.24, RIM + 0.52), (x + rnd.uniform(-0.04, 0.04), wy - 0.42, RIM + 0.5),
                               (x + rnd.uniform(-0.06, 0.06), wy - 0.52 - reach * 0.5, RIM + 0.22),
                               (x + rnd.uniform(-0.08, 0.08), wy - 0.56 - reach, WATER - 0.02)],
                              rnd.uniform(0.03, 0.042), sides=4))
    C.part(strands, "MopHead", STRANDS, "Fabric", smooth_angle=60)


META = {"note": "decor; wringer lever and mop are fixed in place"}

if __name__ == "__main__":
    C.run(build, "Shop_MopBucket", budget=800, meta=META)
