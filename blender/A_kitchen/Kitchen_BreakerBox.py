"""Kitchen_BreakerBox — the basement breaker panel (bible §9.1: hold 4 s, flip 3 switches).

Wall-mounted grey steel box, modelled with its back on the wall plane (Blender y = 0),
front -Y. The door hangs open on its left hinge (role door) so the three big numbered
switches (roles switch1..3, one / two / three mustard dots above them) and a bank of small
breakers are visible. A big red main lever on the right side (role lever) and a yellow
high-voltage sticker on the header band. Conduit runs up out of the top.

Rest pose = power ON: lever and switches up. To show OFF the client rotates each about its
hinge by the *_off_deg angle around the given axis (Roblox model space, right-hand rule).
Pivot = bottom-centre of the box body (not of the open door); the wall plane is
wall_back_z behind it. Sockets: Lever (the lever's grip), Prompt (in front of the box).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
BW, BH, BD = 2.0, 2.8, 0.55
GREY = "#8A9096"
PANEL = "#2F3237"
HEADER = 0.62                  # solid header band on the front (sticker lives here)
DOOR_OPEN = -112               # degrees about the hinge (negative = swings out to -Y)
LEVER_ON = 40                  # lever elevation above forward (deg)
SWITCH_ON = 35


def build():
    pivot = (0.0, -BD / 2, 0.0)

    # ---- body with the front recess ---------------------------------------------------
    body = ns.box((BW, BD, BH), loc=(0, -BD / 2, BH / 2), bevel=0.0)
    rz0, rz1 = 0.16, BH - HEADER
    ns.boolean(body, ns.box((BW - 0.28, 0.9, rz1 - rz0), loc=(0, -BD, (rz0 + rz1) / 2), bevel=0.0))
    ns.bevel(body, width=0.05, segments=2)
    lid = ns.box((BW + 0.14, BD + 0.12, 0.12), loc=(0, -BD / 2 - 0.06, BH + 0.04), bevel=0.05, segments=1)
    boss = ns.cyl(0.19, 0.14, loc=(BW / 2 + 0.07, -BD / 2 - 0.02, 1.55), rot=(0, 90, 0), verts=12, bevel=0.03, segments=1)
    C.part([body, lid, boss], "Body", GREY, "SmoothPlastic", smooth_angle=40)

    # interior back panel + small breaker bank + switch bases
    inner_y = -BD + 0.45
    panel = ns.box((BW - 0.3, 0.04, rz1 - rz0), loc=(0, inner_y - 0.02, (rz0 + rz1) / 2), bevel=0.0)
    C.part(panel, "Panel", PANEL, "SmoothPlastic", smooth_angle=None)
    smalls = []
    for col in (-0.42, 0.0, 0.42):
        for row in range(4):
            smalls.append(ns.box((0.26, 0.12, 0.12), loc=(col, inner_y - 0.08, 0.36 + 0.24 * row), bevel=0.0))
    sw_xs = (-0.55, 0.0, 0.55)
    sw_z = 1.58
    bases = [ns.box((0.36, 0.18, 0.42), loc=(x, inner_y - 0.1, sw_z), bevel=0.04, segments=1) for x in sw_xs]
    C.part(smalls + bases, "Breakers", C.BLACK, "SmoothPlastic", smooth_angle=40)

    # numbered dots above the three big switches (1, 2, 3)
    dots = []
    for i, x in enumerate(sw_xs):
        n = i + 1
        for k in range(n):
            dx = (k - (n - 1) / 2) * 0.11
            dots.append(ns.cyl(0.04, 0.03, loc=(x + dx, inner_y - 0.04, sw_z + 0.36), rot=(90, 0, 0), verts=8, bevel=0.0))
    C.part(dots, "Numbers", C.MUSTARD, "SmoothPlastic")

    # ---- three big switch handles (each its own part) ---------------------------------
    a = math.radians(SWITCH_ON)
    sdir = Vector((0, -math.cos(a), math.sin(a)))
    switch_hinges = []
    for i, x in enumerate(sw_xs, start=1):
        h = Vector((x, inner_y - 0.19, sw_z))
        tip = h + sdir * 0.46
        stem = C.rod(h, tip, 0.06, verts=8)
        knob = ns.box((0.25, 0.18, 0.14), loc=tip, rot=(-(90 - SWITCH_ON), 0, 0), bevel=0.045, segments=1)
        C.part([stem, knob], f"Switch{i}", C.BRAND, "SmoothPlastic", recolor=f"switch{i}", smooth_angle=45)
        switch_hinges.append(C.rbx(h, pivot))

    # ---- main lever on the right side (ON = up) ---------------------------------------
    hinge = Vector((BW / 2 + 0.2, -BD / 2 - 0.02, 1.55))
    la = math.radians(LEVER_ON)
    ldir = Vector((0, -math.cos(la), math.sin(la)))
    lend = hinge + ldir * 1.05
    arm = C.rod(hinge + Vector((0.0, 0, 0)), lend, 0.07, verts=8)
    hub = ns.cyl(0.13, 0.1, loc=hinge, rot=(0, 90, 0), verts=12, bevel=0.03, segments=1)
    grip = C.rod(lend + Vector((-0.02, 0, 0)), lend + Vector((0.42, 0, 0)), 0.1, verts=10, bevel=0.03)
    C.part([arm, hub, grip], "Lever", "#D63A2A", "SmoothPlastic", recolor="lever", smooth_angle=45)
    lever_grip = lend + Vector((0.2, 0, 0))

    # ---- door hanging open on the left hinge ------------------------------------------
    hx, hy = -BW / 2, -BD
    dw, dh = BW - 0.04, BH - 0.06
    door = ns.box((dw, 0.07, dh), loc=(dw / 2, -0.035, BH / 2), bevel=0.03, segments=1)
    latch = ns.box((0.1, 0.1, 0.32), loc=(dw - 0.18, -0.11, BH / 2), bevel=0.03, segments=1)
    rib1 = ns.box((dw - 0.4, 0.03, 0.06), loc=(dw / 2, -0.085, BH - 0.4), bevel=0.0)
    rib2 = ns.box((dw - 0.4, 0.03, 0.06), loc=(dw / 2, -0.085, 0.4), bevel=0.0)
    hinge_pins = [ns.cyl(0.05, 0.3, loc=(0, -0.07, z), verts=8, bevel=0.0) for z in (0.45, BH - 0.45)]
    dobj = ns.join_applied([door, latch, rib1, rib2] + hinge_pins, "Door")
    dobj.location = (hx, hy, 0)
    dobj.rotation_euler = (0, 0, math.radians(DOOR_OPEN))
    C.part(dobj, "Door", GREY, "SmoothPlastic", recolor="door", smooth_angle=40)

    # ---- warning sticker on the header band + conduit ---------------------------------
    sy = -BD - 0.006
    tri = [(-0.3, -0.26), (0.3, -0.26), (0.0, 0.26)]
    sticker = C.extrude(tri, 0.02, plane="XZ", offset=-0.01, bevel=0.012, segments=1, name="Sticker")
    sticker.location = (-0.45, sy, BH - HEADER / 2)
    plate = ns.box((0.95, 0.02, 0.22), loc=(0.35, sy, BH - HEADER / 2), bevel=0.01, segments=1)
    C.part([sticker, plate], "Sticker", C.WARN_YELLOW, "SmoothPlastic")
    bolt = [(0.04, 0.18), (-0.07, -0.01), (0.0, -0.01), (-0.05, -0.18), (0.08, 0.03), (0.01, 0.03)]
    b = C.extrude(bolt, 0.02, plane="XZ", offset=-0.02, name="Bolt")
    b.location = (-0.45, sy - 0.004, BH - HEADER / 2 - 0.04)
    stripes = [ns.box((0.07, 0.02, 0.24), loc=(0.35 + dx, sy - 0.014, BH - HEADER / 2), rot=(0, 35, 0), bevel=0.0)
               for dx in (-0.36, -0.18, 0.0, 0.18, 0.36)]
    C.part([b] + stripes, "StickerInk", C.BLACK, "SmoothPlastic", smooth_angle=None)
    conduit = [C.rod((0.55, -0.22, BH + 0.08), (0.55, -0.22, BH + 1.3), 0.11, verts=10),
               ns.cyl(0.16, 0.14, loc=(0.55, -0.22, BH + 0.15), verts=10, bevel=0.03, segments=1)]
    C.part(conduit, "Conduit", C.GUNMETAL, "Metal", smooth_angle=50)

    sockets = {"Lever": (tuple(lever_grip), 0), "Prompt": ((0, -BD - 1.0, 1.5), 0)}
    meta = C.wall_meta(BD, suggested_bottom=2.4)
    meta.update({
        "lever_hinge": C.rbx(hinge, pivot), "lever_axis": C.rbx_dir((1, 0, 0)), "lever_off_deg": 2 * LEVER_ON + 20,
        "switch_hinges": switch_hinges, "switch_axis": C.rbx_dir((1, 0, 0)), "switch_off_deg": 2 * SWITCH_ON,
        "door_hinge": C.rbx((hx, hy, 0), pivot), "door_axis": C.rbx_dir((0, 0, 1)), "door_close_deg": -DOOR_OPEN,
        "rest_state": "on",
    })
    return {"export": {"sockets": sockets, "meta": meta, "pivot": pivot}}


if __name__ == "__main__":
    C.run(build, "Kitchen_BreakerBox")
