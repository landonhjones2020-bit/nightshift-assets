"""Shop_DoorFront — glass diner entrance door leaf (fits Shop_WallDoorway, 5 x 8 opening).

Brushed-aluminium frame with a tall kick rail, one big glass pane, chrome push bars on both
faces, top/bottom pivot hinges, a brass shop bell on a curled bracket (role "chime",
socket Chime = the door-chime sound emitter) and a blank hours sticker (role sign_panel).
Pivot = hinge line, bottom (leaf extends toward +X). Place at the doorway's Socket_DoorHinge;
rotate about the pivot's Y axis to open (either direction).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L0, L1 = 0.05, 4.95      # leaf x extent (hinge at x = 0)
T = 0.22                 # leaf thickness
Z0, Z1 = 0.03, 7.95
STILE, TOP, BOT = 0.42, 0.5, 1.25
BAR_Z = 3.6
ALU = "#A9B1B8"
BRASS = "#C9A045"


def build():
    w = L1 - L0
    cx = (L0 + L1) / 2
    frame = ns.box((w, T, Z1 - Z0), loc=(cx, 0, (Z0 + Z1) / 2), bevel=0.0)
    gx0, gx1, gz0, gz1 = L0 + STILE, L1 - STILE, Z0 + BOT, Z1 - TOP
    ns.boolean(frame, ns.box((gx1 - gx0, 1, gz1 - gz0), loc=((gx0 + gx1) / 2, 0, (gz0 + gz1) / 2), bevel=0.0))
    ns.bevel(frame, width=0.05, segments=2)
    # glazing beads (slightly proud ring around the glass, both faces) + kick-rail groove strips
    beads = []
    for sy in (-1, 1):
        bead = ns.box((gx1 - gx0 + 0.12, 0.04, gz1 - gz0 + 0.12), loc=((gx0 + gx1) / 2, sy * (T / 2 + 0.02), (gz0 + gz1) / 2),
                      bevel=0.0)
        ns.boolean(bead, ns.box((gx1 - gx0, 1, gz1 - gz0), loc=((gx0 + gx1) / 2, 0, (gz0 + gz1) / 2), bevel=0.0))
        ns.bevel(bead, width=0.015, segments=1)
        beads.append(bead)
    C.part([frame] + beads, "Frame", ALU, "Metal", can_collide=True, smooth_angle=40)

    # kick plates (stainless, both faces) with two raised ribs
    kick = []
    for sy in (-1, 1):
        kick.append(ns.box((w - 0.3, 0.03, 0.95), loc=(cx, sy * (T / 2 + 0.015), Z0 + 0.6), bevel=0.012, segments=1))
        for zz in (0.45, 0.8):
            kick.append(ns.box((w - 0.5, 0.05, 0.06), loc=(cx, sy * (T / 2 + 0.035), Z0 + zz), bevel=0.02, segments=1))
    C.part(kick, "KickPlate", C.STAINLESS, "Metal", smooth_angle=40)

    glass = ns.box((gx1 - gx0 + 0.04, 0.06, gz1 - gz0 + 0.04), loc=((gx0 + gx1) / 2, 0, (gz0 + gz1) / 2), bevel=0.0)
    ns.tag(glass, "Glass", C.GLASS, "Glass", transparency=0.6, recolor="glass", can_collide=True, cast_shadow=False)

    # push bars on both faces: chunky chrome tube on two standoffs
    bars = []
    for sy in (-1, 1):
        y = sy * (T / 2 + 0.34)
        bars.append(C.pipe([(0.75, y, BAR_Z), (L1 - 0.3, y, BAR_Z)], 0.09, sides=12))
        for x in (0.95, L1 - 0.55):
            # standoffs are over the glass (y = +-0.03): rosettes sit on the pane, standoffs run to the bar
            gy = 0.03
            bars.append(ns.cyl(0.055, T / 2 + 0.34 - gy, loc=(x, sy * (gy + T / 2 + 0.34) / 2, BAR_Z), rot=(90, 0, 0),
                               verts=10, bevel=0.0))
            bars.append(ns.cyl(0.13, 0.04, loc=(x, sy * (gy + 0.02), BAR_Z), rot=(90, 0, 0), verts=12, bevel=0.012,
                               segments=1))
    # pivot hinges (top and bottom) on the hinge stile
    for z in (Z0 + 0.12, Z1 - 0.12):
        bars.append(ns.box((0.22, T + 0.08, 0.16), loc=(0.14, 0, z), bevel=0.03))
    C.part(bars, "PushBar", C.CHROME, "Metal", smooth_angle=50)

    # brass shop bell on a curled spring bracket at the top of the latch side (room face)
    bx = L1 - 0.75
    bell = ns.lathe([(0.0, 0.0), (0.2, 0.0), (0.19, 0.04), (0.15, 0.14), (0.1, 0.27), (0.04, 0.32), (0.0, 0.33)],
                    verts=14, loc=(bx, -T / 2 - 0.38, Z1 - TOP - 0.5))
    clap = ns.sphere(0.05, loc=(bx, -T / 2 - 0.38, Z1 - TOP - 0.53), segs=8, rings=5)
    bracket = C.pipe([(bx, -T / 2, Z1 - TOP / 2), (bx, -T / 2 - 0.3, Z1 - TOP / 2 + 0.05),
                      (bx, -T / 2 - 0.38, Z1 - TOP / 2 - 0.1), (bx, -T / 2 - 0.38, Z1 - TOP - 0.18)],
                     0.025, sides=6, corner=0.08)
    C.part([bell, clap, bracket], "Chime", BRASS, "Metal", recolor="chime", smooth_angle=60)

    # blank "hours" sticker on the glass (room face), for a SurfaceGui
    sticker = ns.box((1.3, 0.015, 0.75), loc=(L1 - STILE - 0.85, -0.04, 5.6), bevel=0.0)
    ns.tag(sticker, "Sticker", C.PAPER, recolor="sign_panel")


META = {"leaf": True, "leaf_size": [4.9, 7.92, T], "hinge": "pivot (x=0 edge, bottom, leaf centre plane)",
        "fits": "Shop_WallDoorway Socket_DoorHinge", "open_axis": "pivot Y (yaw)", "surfaces": [{"part": "Sticker", "face": "Front"}]}

if __name__ == "__main__":
    C.run(build, "Shop_DoorFront", pivot=(0, 0, 0), meta=META,
          sockets={"Handle": ((L1 - 0.9, 0, BAR_Z), 0.0), "Chime": ((L1 - 0.75, -T / 2 - 0.38, Z1 - TOP - 0.4), 0.0)})
