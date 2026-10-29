"""Kitchen_Register — retro diner cash register for the front counter.

A brand red-orange body with a sloped keyboard of chunky round keys (cream, plus a few
mustard function keys), a pop-up display box on top (role display, for a SurfaceGui
amount), a chrome crank on the right side and a stainless base whose cash drawer is a
separate part (role drawer). The drawer top has four bill compartments so it reads when
it slides open. Front (keys + drawer, the cashier side) faces -Y.

Meta: drawer_travel = how far the drawer slides out, along drawer_dir (Roblox model
space; Blender -Y = Roblox -Z).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D = 1.9, 1.7
BASE_H = 0.5
DRAWER_TRAVEL = 0.85


def build():
    # ---- stainless base with a drawer bay -------------------------------------------
    base = ns.box((W, D, BASE_H), loc=(0, 0, BASE_H / 2), bevel=0.0)
    ns.boolean(base, ns.box((W - 0.2, D, BASE_H - 0.14), loc=(0, -0.25, BASE_H / 2 + 0.01), bevel=0.0))
    ns.bevel(base, width=0.05, segments=2)
    feet = [ns.box((0.25, 0.25, 0.05), loc=(sx * (W / 2 - 0.22), sy * (D / 2 - 0.22), -0.0), bevel=0.02, segments=1)
            for sx in (-1, 1) for sy in (-1, 1)]
    C.part([base], "Base", C.STAINLESS, "Metal", smooth_angle=40)

    # ---- the cash drawer (slides out along -Y) ---------------------------------------
    dw, dd, dh = W - 0.24, D - 0.3, BASE_H - 0.18
    dy = -D / 2 + dd / 2 + 0.02
    drawer = ns.box((dw, dd, dh), loc=(0, dy, BASE_H / 2 + 0.01), bevel=0.0)
    for i, x in enumerate((-0.6, -0.2, 0.2, 0.6)):
        ns.boolean(drawer, ns.box((0.34, 0.6, 0.3), loc=(x, dy + 0.1, BASE_H / 2 + 0.01 + dh / 2), bevel=0.0))
    ns.bevel(drawer, width=0.03, segments=1)
    front = ns.box((W - 0.16, 0.08, BASE_H - 0.12), loc=(0, -D / 2 - 0.01, BASE_H / 2 + 0.01), bevel=0.04, segments=2)
    pull = ns.box((0.5, 0.08, 0.08), loc=(0, -D / 2 - 0.08, BASE_H / 2 + 0.03), bevel=0.03, segments=1)
    C.part([drawer, front, pull], "Drawer", C.STEEL, "Metal", recolor="drawer", smooth_angle=40)

    # ---- red-orange body: wedge with a sloped keyboard deck ----------------------------
    prof = [(-D / 2 + 0.06, BASE_H), (D / 2 - 0.06, BASE_H), (D / 2 - 0.06, 1.25), (0.2, 1.25), (-D / 2 + 0.06, 0.78)]
    body = C.extrude(prof, W - 0.08, plane="YZ", offset=-(W - 0.08) / 2, bevel=0.09, segments=2, name="Body")
    C.part([body] + feet, "Body", C.BRAND, "SmoothPlastic", smooth_angle=40)

    # chrome trim band where the body meets the base
    trim = ns.box((W - 0.02, D - 0.06, 0.07), loc=(0, 0, BASE_H + 0.02), bevel=0.025, segments=1)

    # ---- keys on the slope ------------------------------------------------------------
    import math
    from mathutils import Vector
    y0, z0 = -D / 2 + 0.06, 0.78
    y1, z1 = 0.2, 1.25
    slope = math.atan2(z1 - z0, y1 - y0)
    up = Vector((0, -math.sin(slope), math.cos(slope)))
    keys, fkeys = [], []
    cols = [-0.6, -0.3, 0.0, 0.3, 0.6]
    for r, t in enumerate((0.22, 0.5, 0.78)):
        p = Vector((0, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t)) + up * 0.04
        for c, x in enumerate(cols):
            k = ns.cyl(0.12, 0.11, loc=(x, p.y, p.z), rot=(-math.degrees(slope), 0, 0), verts=8, bevel=0.0, radius_top=0.095)
            (fkeys if c == 4 else keys).append(k)
    # (part names must not start with Key/Fill/Rim: nslib's preview light cleanup deletes those)
    C.part(keys, "Buttons", C.CREAM, "SmoothPlastic", smooth_angle=50)
    C.part(fkeys, "FunctionButtons", C.MUSTARD, "SmoothPlastic", smooth_angle=50)

    # ---- pop-up display box on top (both faces show the amount) ------------------------
    box = ns.box((1.0, 0.5, 0.42), loc=(0, 0.45, 1.25 + 0.2), bevel=0.08, segments=2)
    C.part(box, "DisplayBox", C.CREAM, "SmoothPlastic", smooth_angle=40)
    screens = [ns.box((0.78, 0.04, 0.24), loc=(0, 0.45 + sy * 0.25, 1.47), bevel=0.0) for sy in (-1, 1)]
    C.part(screens, "Display", "#22332B", "SmoothPlastic", recolor="display")

    # ---- crank handle on the right side + trim ----------------------------------------
    hub = ns.cyl(0.14, 0.08, loc=(W / 2 + 0.0, 0.2, 0.9), rot=(0, 90, 0), verts=12, bevel=0.03, segments=1)
    arm = C.rod((W / 2 + 0.05, 0.2, 0.9), (W / 2 + 0.1, -0.15, 0.62), 0.04, verts=6)
    knob = ns.sphere(0.09, loc=(W / 2 + 0.1, -0.15, 0.62), segs=10, rings=6)
    C.part([trim, hub, arm], "Chrome", C.STAINLESS, "Metal", smooth_angle=45)
    C.part(knob, "CrankKnob", C.CREAM, "SmoothPlastic")

    meta = {"drawer_travel": DRAWER_TRAVEL, "drawer_dir": [0, 0, -1], "drawer_part": "Drawer",
            "surface_display": {"part": "Display", "faces": ["Front", "Back"]}}
    return {"export": {"meta": meta}}


if __name__ == "__main__":
    C.run(build, "Kitchen_Register")
