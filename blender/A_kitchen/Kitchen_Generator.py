"""Kitchen_Generator — chunky portable generator in the basement.

A charcoal tubular roll-cage frame holding a pillowy mustard fuel tank (black fuel cap,
role fuel_cap), a finned engine with a red recoil starter and a black T-handle pull cord
(role pull_handle; the client yanks it out along meta pull_dir by pull_travel), a round
alternator with a control panel (two outlets, a status lamp with role status_light), a
muffler at the back, two wheels and rubber feet. Front faces -Y. Bulky parts collide.

Sockets: PullHandle (the T-handle grip), Prompt (in front of the starter).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
FX, FY, FZ0, FZ1 = 1.35, 0.85, 0.16, 2.05     # frame loop half-length/half-depth, bottom/top
ENG_X = 0.62


def build():
    # ---- frame: two rounded U-loops + top rails + skids --------------------------------
    frame = []
    for x in (-FX, FX):
        frame.append(ns.tube([(x, -FY, FZ0), (x, -FY, FZ1 - 0.12), (x, -FY + 0.12, FZ1), (x, FY - 0.12, FZ1),
                              (x, FY, FZ1 - 0.12), (x, FY, FZ0)], [0.075] * 6, sides=8, resolution=2, name="Loop"))
    for y in (-FY, FY):
        frame.append(C.rod((-FX, y, FZ1 - 0.25), (FX, y, FZ1 - 0.25), 0.07, verts=8))
        frame.append(C.rod((-FX - 0.05, y, FZ0), (FX + 0.05, y, FZ0), 0.08, verts=8))
    # engine/alternator and tank were free-floating inside the frame: cross rails between the skids under
    # both units (rubber mounts on top, below) and four tank tabs out to the top rails
    for x in (ENG_X, -0.6):
        frame.append(C.rod((x, -FY, FZ0 + 0.02), (x, FY, FZ0 + 0.02), 0.07, verts=8))
    for x in (-0.8, 0.8):
        for sy in (-1, 1):
            frame.append(ns.box((0.14, FY - 0.6 + 0.04, 0.1), loc=(x, sy * (0.6 + FY + 0.04) / 2, FZ1 - 0.25), bevel=0.02,
                                segments=1))
    C.part(frame, "Frame", C.CHARCOAL, "Metal", can_collide=True, smooth_angle=50)

    # ---- fuel tank + cap ------------------------------------------------------------
    tank = ns.box((2.35, 1.35, 0.6), loc=(0, 0, 1.73), bevel=0.2, segments=2)
    C.part(tank, "Tank", C.MUSTARD, "SmoothPlastic", can_collide=True, smooth_angle=50)
    cap = ns.lathe([(0.0, 0.0), (0.2, 0.0), (0.21, 0.08), (0.18, 0.13), (0.0, 0.14)], verts=12, name="Cap")
    cap.location = (-0.55, -0.1, 2.02)
    C.part(cap, "FuelCap", C.BLACK, "SmoothPlastic", recolor="fuel_cap", smooth_angle=50)
    gauge = ns.cyl(0.13, 0.05, loc=(0.35, -0.2, 2.04), verts=12, bevel=0.0)
    C.part(gauge, "Gauge", C.CREAM, "SmoothPlastic")

    # ---- engine block, finned head, muffler -----------------------------------------
    block = ns.box((1.1, 1.05, 0.85), loc=(ENG_X, 0.0, 0.66), bevel=0.08, segments=1)
    head = ns.box((0.62, 0.62, 0.3), loc=(ENG_X, 0.18, 1.2), bevel=0.05, segments=1)
    fins = [ns.box((0.78, 0.74, 0.035), loc=(ENG_X, 0.18, 1.08 + 0.075 * k), bevel=0.0) for k in range(4)]
    C.part([block, head] + fins, "Engine", C.GUNMETAL, "Metal", can_collide=True, smooth_angle=40)
    muffler = ns.cyl(0.22, 0.75, loc=(ENG_X, FY - 0.2, 1.0), rot=(0, 90, 0), verts=10, bevel=0.05, segments=1)
    shield = ns.box((0.85, 0.06, 0.5), loc=(ENG_X, FY - 0.45, 1.0), bevel=0.03, segments=1)
    C.part([muffler, shield], "Muffler", C.STEEL_DARK, "Metal", smooth_angle=45)

    # ---- recoil starter (red) + pull handle (separate part) -----------------------------
    housing = ns.cyl(0.34, 0.16, loc=(ENG_X, -0.58, 0.72), rot=(90, 0, 0), verts=16, bevel=0.05, segments=1)
    C.part(housing, "Starter", C.BRAND, "SmoothPlastic", smooth_angle=45)
    hp = (ENG_X, -0.86, 0.72)
    cord = C.rod((ENG_X, -0.66, 0.72), hp, 0.022, verts=6)
    tbar = C.rod((ENG_X - 0.2, hp[1], hp[2]), (ENG_X + 0.2, hp[1], hp[2]), 0.065, verts=8, bevel=0.025)
    C.part([cord, tbar], "PullHandle", C.BLACK, "SmoothPlastic", recolor="pull_handle", smooth_angle=45)

    # ---- alternator + control panel ---------------------------------------------------
    alt = ns.cyl(0.5, 1.05, loc=(-0.6, 0.05, 0.75), rot=(0, 90, 0), verts=16, bevel=0.06, segments=1)
    endcap = ns.cyl(0.36, 0.12, loc=(-1.17, 0.05, 0.75), rot=(0, 90, 0), verts=16, bevel=0.04, segments=1)
    C.part([alt, endcap], "Alternator", C.STEEL_DARK, "Metal", can_collide=True, smooth_angle=45)
    panel = ns.box((0.86, 0.14, 0.62), loc=(-0.6, -0.6, 0.78), bevel=0.05, segments=1)
    # stand-offs from the panel back into the alternator (the panel hung 0.08 in front of it)
    stand = [ns.box((0.12, 0.16, 0.3), loc=(x, -0.475, 0.78), bevel=0.02, segments=1) for x in (-0.85, -0.35)]
    C.part([panel] + stand, "Panel", C.CHARCOAL, "SmoothPlastic", smooth_angle=40)
    outlets = [ns.box((0.2, 0.04, 0.24), loc=(x, -0.68, 0.7), bevel=0.02, segments=1) for x in (-0.82, -0.56)]
    C.part(outlets, "Outlets", C.CREAM, "SmoothPlastic")
    switch = ns.box((0.1, 0.08, 0.16), loc=(-0.33, -0.7, 0.68), bevel=0.02, segments=1)
    lamp = ns.cyl(0.06, 0.04, loc=(-0.33, -0.68, 0.94), rot=(90, 0, 0), verts=8, bevel=0.0)
    C.part(lamp, "StatusLight", "#7CFF8A", "SmoothPlastic", recolor="status_light")

    # ---- wheels at the engine end, rubber feet at the other ----------------------------
    rub = [switch]
    # rubber mounts: cross rail top (z 0.25) up into the engine block (bottom 0.235) / alternator (bottom 0.25)
    rub.append(ns.box((0.3, 0.7, 0.1), loc=(ENG_X, 0.0, 0.27), bevel=0.02, segments=1))
    rub.append(ns.box((0.3, 0.5, 0.1), loc=(-0.6, 0.05, 0.28), bevel=0.02, segments=1))
    for y in (-FY - 0.16, FY + 0.16):
        rub.append(ns.cyl(0.36, 0.22, loc=(FX - 0.25, y, 0.36), rot=(90, 0, 0), verts=14, bevel=0.07, segments=1))
        rub.append(ns.box((0.22, 0.22, 0.12), loc=(-FX + 0.2, y + (0.16 if y < 0 else -0.16), 0.06), bevel=0.03, segments=1))
    C.part(rub, "Rubber", C.RUBBER, "SmoothPlastic", smooth_angle=45)
    hubs = [ns.cyl(0.16, 0.24, loc=(FX - 0.25, y, 0.36), rot=(90, 0, 0), verts=8, bevel=0.0) for y in (-FY - 0.16, FY + 0.16)]
    C.part(hubs, "Hubs", C.MUSTARD, "SmoothPlastic", smooth_angle=45)

    sockets = {"PullHandle": (hp, 0), "Prompt": ((ENG_X, -1.6, 1.0), 0)}
    meta = {"pull_dir": C.rbx_dir((0, -1, 0)), "pull_travel": 0.9}
    return {"export": {"sockets": sockets, "meta": meta}}


if __name__ == "__main__":
    C.run(build, "Kitchen_Generator")
