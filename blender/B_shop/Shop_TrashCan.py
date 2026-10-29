"""Shop_TrashCan — dented galvanized alley trash can with a ribbed body, side handles and a
domed lid knocked slightly askew (role "trash_lid" so it can rattle/lift: the Mr. Usual
"trash can" clue spot). A crumpled paper bag pokes out from under the lid.
Pivot = bottom-centre. Socket Clue = inside, under the lid.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
R, H = 1.05, 3.1
GALV = "#B3BABF"
GALV_DARK = "#868E93"


def build():
    prof = [(0.0, 0.0), (R * 0.88, 0.0), (R * 0.92, 0.1)]
    for z in (0.7, 1.55, 2.4):          # three pressed ribs, flat galvanized walls between
        r = R * (0.93 + 0.025 * z)
        prof += [(r, z - 0.12), (r + 0.07, z - 0.04), (r + 0.07, z + 0.04), (r, z + 0.12)]
    prof += [(R + 0.02, H - 0.14), (R + 0.07, H - 0.06), (R + 0.07, H), (R - 0.04, H), (0.0, H - 0.1)]
    body = ns.lathe(prof, verts=18)
    # a dent: push a few vertices inward on one side
    for v in body.data.vertices:
        d = math.hypot(v.co.x - 0.7, v.co.y + 0.75)
        if d < 0.55 and 0.6 < v.co.z < 1.9:
            k = (0.55 - d) / 0.55 * 0.18
            v.co.x -= 0.7 * k
            v.co.y += 0.75 * k
    ns.tag(body, "Body", GALV, "Metal", smooth_angle=50)
    handles = []
    for sx in (-1, 1):
        handles.append(C.pipe([(sx * (R + 0.02), -0.35, 2.55), (sx * (R + 0.22), -0.3, 2.45), (sx * (R + 0.22), 0.3, 2.45),
                               (sx * (R + 0.02), 0.35, 2.55)], 0.04, sides=6, corner=0.08, corner_segs=1))
    C.part(handles, "Handles", GALV_DARK, "Metal", smooth_angle=60)

    lid = ns.lathe([(0.0, 0.42), (0.35, 0.38), (0.8, 0.22), (R + 0.1, 0.06), (R + 0.12, 0.0), (R + 0.02, -0.06),
                    (0.0, -0.02)], verts=18)
    knob = C.pipe([(-0.3, 0, 0.4), (-0.25, 0, 0.6), (0.25, 0, 0.6), (0.3, 0, 0.4)], 0.05, sides=6, corner=0.08,
                  corner_segs=1)
    lidp = C.merge([lid, knob], "Lid")
    lidp.location = (0.18, -0.12, H + 0.2)
    lidp.rotation_euler = (math.radians(-9), math.radians(7), 0)
    ns.apply_all(lidp)
    ns.tag(lidp, "Lid", GALV, "Metal", recolor="trash_lid", smooth_angle=50)
    bag = ns.box((0.9, 0.7, 0.7), loc=(-0.45, 0.35, H - 0.05), rot=(12, -10, 25), bevel=0.2, segments=1)
    ns.tag(bag, "Bag", C.CARDBOARD, smooth_angle=30)


META = {"size": [2.4, 3.6, 2.2], "clue_spot": True}

if __name__ == "__main__":
    C.run(build, "Shop_TrashCan", meta=META, sockets={"Clue": ((0, 0, H - 0.4), 0.0)})
