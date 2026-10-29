"""Shop_Stool — counter stool: round red vinyl cushion with a chrome band on a chrome
pedestal, footrest ring and weighted round foot. Seat top 2.1 (counter top 3.0).
Socket Seat = seat-top centre, yaw 0 (stools swivel; any yaw works).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SZ = 2.1


def build():
    cush = ns.lathe([(0.0, 0.0), (0.66, 0.0), (0.74, 0.06), (0.76, 0.16), (0.72, 0.28), (0.6, 0.34), (0.0, 0.36)],
                    verts=20, loc=(0, 0, SZ - 0.36))
    C.part([cush], "Cushion", C.VINYL_RED, recolor="stool_vinyl", smooth_angle=60)
    band = ns.cyl(0.77, 0.14, loc=(0, 0, SZ - 0.33), verts=20, bevel=0.03, segments=1)
    skirt = ns.cyl(0.55, 0.12, loc=(0, 0, SZ - 0.46), verts=16, radius_top=0.7, bevel=0.0)
    post = ns.cyl(0.12, SZ - 0.5, loc=(0, 0, (SZ - 0.5) / 2 + 0.05), verts=10, bevel=0.0)
    ring = ns.torus(0.5, 0.045, loc=(0, 0, 0.85), major_segs=18, minor_segs=6)
    spokes = [C.pipe([(0, 0, 0.85), (0.5, 0, 0.85)], 0.035, sides=6) for _ in range(1)]
    spokes.append(C.pipe([(-0.5, 0, 0.85), (0, 0, 0.85)], 0.035, sides=6))
    collar = ns.cyl(0.2, 0.2, loc=(0, 0, 0.85), verts=10, bevel=0.03, segments=1)
    foot = ns.cyl(0.62, 0.12, loc=(0, 0, 0.06), verts=18, radius_top=0.45, bevel=0.0)
    C.part([band, skirt, post, ring, collar, foot] + spokes, "Frame", C.CHROME, "Metal", smooth_angle=55)
    glide = ns.cyl(0.64, 0.03, loc=(0, 0, 0.015), verts=18, bevel=0.0)
    ns.tag(glide, "Glide", C.RUBBER)


META = {"seat_height": SZ, "counter_height": 3.0}

if __name__ == "__main__":
    C.run(build, "Shop_Stool", meta=META, sockets={"Seat": ((0, 0, SZ), 0.0)})
