"""Shop_Chair — 1950s diner chair: bent chrome tube frame, red vinyl seat and back pads.
Seat top 1.6 (= booth seat). Front (the side you sit from) faces -Y.
Socket Seat = seat-top centre, yaw 0 = sitter faces the chair front (-Y / LookVector).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SZ = 1.6
HW, HD = 0.78, 0.75   # half width / half depth of the frame


def build():
    tubes = []
    r = 0.065
    for sx in (-1, 1):
        x = sx * HW
        # one continuous bent tube per side: front leg -> seat rail -> rear leg -> up into the back
        path = [(x, -HD, 0.05), (x, -HD + 0.08, SZ - 0.3), (x, HD - 0.05, SZ - 0.3), (x, HD + 0.05, 0.05)]
        tubes.append(C.pipe(path, r, sides=8, corner=0.18, corner_segs=2))
        tubes.append(C.pipe([(x * 0.86, HD - 0.15, SZ - 0.32), (x * 0.86, HD + 0.02, SZ + 0.6), (x * 0.86, HD + 0.12, 3.25)],
                            0.055, sides=8, corner=0.25, corner_segs=2))
    # cross stretchers
    tubes.append(C.pipe([(-HW, -HD + 0.04, 0.55), (HW, -HD + 0.04, 0.55)], 0.04, sides=6))
    tubes.append(C.pipe([(-HW, HD - 0.02, 0.55), (HW, HD - 0.02, 0.55)], 0.04, sides=6))
    # seat pan
    tubes.append(ns.box((2 * HW - 0.1, 2 * HD - 0.25, 0.08), loc=(0, 0, SZ - 0.32), bevel=0.02, segments=1))
    C.part(tubes, "Frame", C.CHROME, "Metal", smooth_angle=60)

    seat = ns.box((2 * HW + 0.06, 2 * HD + 0.02, 0.3), loc=(0, -0.02, SZ - 0.15), bevel=0.12, segments=2)
    back = ns.box((2 * HW * 0.86 + 0.1, 0.24, 1.05), loc=(0, HD + 0.1, 2.75), rot=(-8, 0, 0), bevel=0.11, segments=2)
    C.part([seat, back], "Vinyl", C.VINYL_RED, recolor="chair_vinyl", smooth_angle=50)
    # piping band around the seat edge
    band = C.prism(C.rrect(2 * HW + 0.1, 2 * HD + 0.06, 0.16, 2, 0, -0.02), "z", SZ - 0.27, SZ - 0.19)
    feet = [ns.cyl(0.08, 0.05, loc=(sx * HW, sy * (HD + (0.05 if sy > 0 else 0)), 0.025), verts=8, bevel=0.0)
            for sx in (-1, 1) for sy in (-1, 1)]
    C.part([band] + feet, "Piping", C.BASE_DARK, smooth_angle=50)


META = {"seat_height": SZ, "front": "-Y (sit facing LookVector)"}

if __name__ == "__main__":
    C.run(build, "Shop_Chair", meta=META, sockets={"Seat": ((0, -0.05, SZ), 0.0)})
