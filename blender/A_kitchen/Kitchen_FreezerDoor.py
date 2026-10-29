"""Kitchen_FreezerDoor — heavy insulated walk-in freezer door leaf (5 x 8, STYLE.md §5).

A thick (0.5) stainless leaf with chunky bevels, two big chrome strap hinges on the left,
a diamond-plate kick plate, a frosted heated window at eye level, an icy-blue snowflake
badge and a big chrome lever latch on the right (role handle, so the client can rock it
when the door is pulled). The freezer side (+Y) carries a translucent PVC strip curtain
hanging from a header bar, plus a black rubber gasket round the edge.

Front (kitchen side) faces -Y. Pivot = the hinge axis at the bottom of the left edge (the
hinge barrels), so rotating the model about its pivot's up axis swings the door. The leaf
body collides. Socket Handle = the lever grip (yaw 0).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, T = 5.0, 8.0, 0.5
FY = -T / 2                       # front face y
CHROME = "#D0D6DB"
HINGE = (-W / 2 - 0.04, FY - 0.12)   # hinge barrel axis (x, y)


def build():
    # ---- leaf ------------------------------------------------------------------------
    leaf = ns.box((W, T, H), loc=(0, 0, H / 2), bevel=0.12, segments=2)
    C.part(leaf, "Leaf", C.STAINLESS, "Metal", can_collide=True, recolor="door_leaf", smooth_angle=40)

    # raised perimeter frame on the front (reads as an insulated panel door)
    fr = []
    bw = 0.22
    fr.append(ns.box((W - 0.2, 0.06, bw), loc=(0, FY - 0.02, H - 0.1 - bw / 2), bevel=0.03, segments=1))
    for sx in (-1, 1):
        fr.append(ns.box((bw, 0.06, H - 0.2), loc=(sx * (W / 2 - 0.1 - bw / 2), FY - 0.02, H / 2), bevel=0.03, segments=1))
    C.part(fr, "Trim", C.STEEL, "Metal", smooth_angle=40)

    # kick plate fits between the trim rails (no coplanar overlap with them)
    kick = ns.box((W - 0.2 - 2 * bw - 0.02, 0.05, 1.3), loc=(0, FY - 0.02, 0.1 + 0.65), bevel=0.03, segments=1)
    C.part(kick, "KickPlate", "#A8B0B7", "DiamondPlate", smooth_angle=40)

    # ---- frosted window ------------------------------------------------------------
    wx, wz = 0.35, 5.25
    ring = C.extrude(C.rrect(1.5, 1.25, 0.3, 3), 0.1, plane="XZ", offset=-0.05, name="Gasket")
    ns.boolean(ring, C.extrude(C.rrect(1.2, 0.95, 0.18, 3), 0.4, plane="XZ", offset=-0.2, name="Cut"))
    ring.location = (wx, FY - 0.04, wz)
    pane = C.extrude(C.rrect(1.24, 0.99, 0.2, 3), 0.04, plane="XZ", offset=-0.02, name="Pane")
    pane.location = (wx, FY - 0.0, wz)
    C.part(ring, "WindowFrame", C.RUBBER, "SmoothPlastic", smooth_angle=50)
    C.part(pane, "Window", "#BFE3F0", "Ice", smooth_angle=50)

    # ---- snowflake badge -------------------------------------------------------------
    bx, bz = 0.35, 6.95
    badge = ns.cyl(0.6, 0.06, loc=(bx, FY - 0.05, bz), rot=(90, 0, 0), verts=16, bevel=0.02, segments=1)
    C.part(badge, "Badge", C.ICY, "SmoothPlastic", smooth_angle=45)
    flake = []
    for a in (0, 60, 120):
        # bars, ticks and hub sit on distinct planes (overlapping coplanar faces z-fight)
        flake.append(ns.box((0.1, 0.05, 0.9), loc=(bx, FY - 0.095 - 0.004 * (a // 60), bz), rot=(0, a, 0), bevel=0.0))
        for sgn in (-1, 1):
            # little V-ticks near each arm end
            import math
            r = 0.3
            ax = bx + sgn * r * math.sin(math.radians(a))
            az = bz + sgn * r * math.cos(math.radians(a))
            for t in (-35, 35):
                flake.append(ns.box((0.07, 0.03, 0.2), loc=(ax, FY - 0.09, az), rot=(0, a + t, 0), bevel=0.0))
    flake.append(ns.cyl(0.13, 0.06, loc=(bx, FY - 0.11, bz), rot=(90, 0, 0), verts=6, bevel=0.0))
    C.part(flake, "Snowflake", "#F4FBFF", "SmoothPlastic", smooth_angle=None)

    # ---- round door thermometer (cream dial, red needle) ------------------------------
    tx, tz = 1.75, 5.25
    dial = ns.cyl(0.3, 0.05, loc=(tx, FY - 0.06, tz), rot=(90, 0, 0), verts=14, bevel=0.0)
    C.part(dial, "Dial", C.CREAM, "SmoothPlastic")
    needle = ns.box((0.04, 0.02, 0.22), loc=(tx + 0.05, FY - 0.095, tz + 0.06), rot=(0, 30, 0), bevel=0.0)
    C.part(needle, "Needle", "#D63A2A", "SmoothPlastic")

    # ---- strap hinges ---------------------------------------------------------------
    hinges = []
    for z in (1.5, 6.5):
        hinges.append(ns.box((1.5, 0.08, 0.42), loc=(-W / 2 + 0.7, FY - 0.08, z), bevel=0.04, segments=1))
        hinges.append(ns.cyl(0.13, 0.75, loc=(HINGE[0], HINGE[1], z), verts=10, bevel=0.04, segments=1))
        for x in (-W / 2 + 0.45, -W / 2 + 1.15):
            hinges.append(ns.cyl(0.06, 0.05, loc=(x, FY - 0.13, z), rot=(90, 0, 0), verts=6, bevel=0.0))
    bezel = C.ns.ring(0.28, 0.36, 0.1, loc=(tx, FY - 0.07, tz), verts=14)
    bezel.rotation_euler = (1.5708, 0, 0)
    hinges.append(bezel)
    # latch housing on the right edge
    hinges.append(ns.box((0.4, 0.22, 1.1), loc=(W / 2 - 0.45, FY - 0.11, 3.6), bevel=0.07, segments=1))
    C.part(hinges, "Hardware", CHROME, "Metal", smooth_angle=45)

    # ---- big lever handle (separate part) --------------------------------------------
    pivot_pt = (W / 2 - 0.45, FY - 0.28, 3.85)
    boss = ns.cyl(0.16, 0.16, loc=pivot_pt, rot=(90, 0, 0), verts=12, bevel=0.04, segments=1)
    arm = C.rod(pivot_pt, (W / 2 - 1.45, FY - 0.32, 3.62), 0.08, verts=8)
    grip_a, grip_b = (W / 2 - 1.45, FY - 0.32, 3.62), (W / 2 - 1.95, FY - 0.32, 3.52)
    grip = C.rod(grip_a, grip_b, 0.13, verts=10, bevel=0.05)
    C.part([boss, arm, grip], "Handle", CHROME, "Metal", recolor="handle", smooth_angle=45)

    # ---- freezer side: header bar, strip curtain, gasket -----------------------------
    by = T / 2
    header = ns.box((W - 0.1, 0.14, 0.22), loc=(0, by + 0.07, H - 0.25), bevel=0.04, segments=1)
    C.part(header, "Header", C.STEEL, "Metal", smooth_angle=40)
    strips = []
    n = 6
    sw = (W - 0.2) / n
    for i in range(n):
        x = -W / 2 + 0.1 + sw * (i + 0.5)
        strips.append(ns.box((sw + 0.12, 0.03, H - 0.55), loc=(x, by + 0.16 + 0.035 * (i % 2), (H - 0.36) / 2 + 0.05),
                             bevel=0.01, segments=1))
    C.part(strips, "Strips", "#BFE3F0", "SmoothPlastic", transparency=0.45, cast_shadow=False, smooth_angle=None)
    gasket = [ns.box((W - 0.1, 0.06, 0.1), loc=(0, by + 0.03, z), bevel=0.0) for z in (0.06, H - 0.06)]
    gasket += [ns.box((0.1, 0.06, H - 0.1), loc=(sx * (W / 2 - 0.06), by + 0.03, H / 2), bevel=0.0) for sx in (-1, 1)]
    C.part(gasket, "Gasket", C.RUBBER, "SmoothPlastic", smooth_angle=None)

    pivot = (HINGE[0], HINGE[1], 0.0)
    grip_mid = tuple((a + b) / 2 for a, b in zip(grip_a, grip_b))
    meta = {"hinge": "left", "open_dir": "positive yaw about the pivot (CFrame.Angles(0, a, 0)) swings the free edge toward +Z (freezer side)",
            "handle_pivot": C.rbx(pivot_pt, pivot), "handle_axis": C.rbx_dir((0, -1, 0)), "handle_throw_deg": 25}
    return {"export": {"sockets": {"Handle": (grip_mid, 0)}, "meta": meta, "pivot": pivot}}


if __name__ == "__main__":
    C.run(build, "Kitchen_FreezerDoor")
