"""Shop_RestroomStall — toilet stall (hiding spot): mint steel partitions raised off the floor
on chrome feet (you can see feet under the door), front pilasters with a chrome headrail,
a door leaf (role "stall_door") with an occupied latch indicator (role "stall_latch"),
and a chunky porcelain toilet inside.
Footprint 3.6 wide x 5.4 deep; the back (+Y) is the room wall (no back panel).
Sockets: Hide (centre of the stall interior volume, facing the door), HideFloor (floor
point inside), DoorHinge (door leaf hinge line, bottom of the leaf; rotate Door about it).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
HW, HD = 1.8, 2.7            # half width / half depth
GAP, TOPZ = 0.65, 6.6        # panel bottom gap, panel top
T = 0.14
PANEL = "#86AE9E"
DOOR_X0, DOOR_X1 = -1.15, 1.15


def build():
    panels = []
    for sx in (-1, 1):
        panels.append(ns.box((T, 2 * HD - 0.1, TOPZ - GAP), loc=(sx * HW, 0.05, (GAP + TOPZ) / 2), bevel=0.05,
                             segments=1))
    for x0, x1 in ((-HW - T / 2, DOOR_X0 - 0.03), (DOOR_X1 + 0.03, HW + T / 2)):
        panels.append(ns.box((x1 - x0, T + 0.04, TOPZ + 0.25 - 0.12), loc=((x0 + x1) / 2, -HD, (TOPZ + 0.25 + 0.12) / 2),
                             bevel=0.05, segments=1))
    C.part(panels, "Partitions", PANEL, can_collide=True, smooth_angle=40)

    door = ns.box((DOOR_X1 - DOOR_X0 - 0.04, T, TOPZ - GAP - 0.1), loc=(0, -HD, (GAP + TOPZ) / 2 + 0.03), bevel=0.05,
                  segments=1)
    ns.tag(door, "Door", PANEL, recolor="stall_door", can_collide=True, smooth_angle=40)
    latch = ns.box((0.32, 0.05, 0.16), loc=(DOOR_X1 - 0.35, -HD - T / 2 - 0.035, 3.6), bevel=0.02, segments=1)
    ns.tag(latch, "Latch", "#D93B3B", recolor="stall_latch")

    hw = [C.pipe([(-HW - 0.1, -HD - 0.02, TOPZ + 0.3), (HW + 0.1, -HD - 0.02, TOPZ + 0.3)], 0.07, sides=8)]
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        x = sx * HW
        y = -HD if sy < 0 else HD - 0.1
        hw.append(ns.box((0.3, 0.3, 0.12), loc=(x, y, 0.06), bevel=0.03, segments=1))
        hw.append(ns.cyl(0.06, GAP, loc=(x, y, GAP / 2), verts=8, bevel=0.0))
    for z in (GAP + 0.6, TOPZ - 0.6):         # door hinges
        hw.append(ns.box((0.12, 0.22, 0.35), loc=(DOOR_X0 - 0.01, -HD, z), bevel=0.03, segments=1))
    hw.append(ns.box((0.42, 0.14, 0.22), loc=(DOOR_X1 - 0.35, -HD - 0.02, 3.6), bevel=0.03, segments=1))
    # toilet paper holder on the right partition
    hw.append(ns.box((0.08, 0.5, 0.35), loc=(HW - 0.11, 0.7, 2.4), bevel=0.03, segments=1))
    C.part(hw, "Hardware", C.CHROME, "Metal", smooth_angle=50)
    roll = ns.cyl(0.2, 0.42, loc=(HW - 0.32, 0.7, 2.25), rot=(90, 0, 0), verts=12, bevel=0.03, segments=1)
    ns.tag(roll, "Paper", C.PAPER, smooth_angle=50)

    # chunky toilet against the back wall
    ty = HD - 1.25
    bowl = ns.lathe([(0.0, 0.0), (0.5, 0.0), (0.45, 0.4), (0.55, 1.0), (0.62, 1.42), (0.0, 1.42)], verts=16,
                    loc=(0, ty, 0))
    bowl.scale = (1.0, 1.25, 1.0)
    tank = ns.box((1.5, 0.6, 1.4), loc=(0, HD - 0.4, 2.1), bevel=0.1, segments=2)
    lid_t = ns.box((1.6, 0.7, 0.12), loc=(0, HD - 0.4, 2.86), bevel=0.05, segments=1)
    C.part([bowl, tank, lid_t], "Porcelain", C.PORCELAIN, smooth_angle=50)
    seat = ns.torus(0.5, 0.09, loc=(0, ty, 1.5), major_segs=16, minor_segs=6)
    seat.scale = (1.0, 1.25, 1.0)
    lid = ns.box((1.15, 0.12, 1.25), loc=(0, ty + 0.85, 2.05), rot=(-12, 0, 0), bevel=0.1, segments=2)
    C.part([seat, lid], "Seat", "#2C2E33", smooth_angle=50)
    handle = ns.box((0.3, 0.06, 0.08), loc=(-0.55, HD - 0.72, 2.55), bevel=0.02, segments=1)
    ns.tag(handle, "Flush", C.CHROME, "Metal")


META = {"size": [2 * HW, TOPZ + 0.4, 2 * HD], "back": "+Y = room wall (no back panel)", "hide_floor": 0.0,
        "door": {"part": "Door", "hinge_socket": "DoorHinge", "opens": "inward (+Y) up to 100 deg"},
        "latch": {"part": "Latch", "occupied": "#D93B3B", "vacant": "#3FBF5A"}}

if __name__ == "__main__":
    C.run(build, "Shop_RestroomStall", meta=META,
          sockets={"Hide": ((0, -0.4, 2.5), 0.0), "HideFloor": ((0, -0.4, 0.0), 0.0),
                   "DoorHinge": ((DOOR_X0, -HD, GAP - 0.02), 0.0)})
