"""Basement_Workbench — old wooden workbench with a pegboard "shadow board".

Chunky wood bench (worktop at 3, plank seams, legs, aprons, a lower shelf holding a coiled
green hose, a paint can and a small crate). On top: a cast-iron vise at the front-left
corner, a red toolbox, a hammer, a screwdriver, a wrench and a crumpled rag. Behind it a
dingy-cream pegboard (punched holes, wood frame, side posts up to 6) painted with dark tool
silhouettes: the hammer and the wrench still hang on their outlines, the saw, the pliers and
the screwdriver are missing - just their painted shapes left.
Bench and pegboard collide; tools do not. Back (+Y) goes against the wall. Front faces -Y,
pivot = bottom-centre. 6 x 6 x 2.5 (worktop 3).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D, TOP = 6.0, 2.5, 3.0
TT = 0.22                      # worktop thickness
PB_Y = 1.13                    # pegboard front face y
PB_Z0, PB_Z1 = TOP, 6.0
PB_T = 0.08
RED = C.VALVE_RED
HOSE = "#4F6B45"


def build():
    rnd = random.Random(5)
    # ---- bench -------------------------------------------------------------------------
    top = ns.box((W, D, TT), loc=(0, 0, TOP - TT / 2), bevel=0.06, segments=1)
    C.part([top], "Worktop", C.WOOD_LIGHT, "Wood", can_collide=True, smooth_angle=35)
    seams = [C.face_dir(C.poly([(-W / 2 + 0.08, y - 0.013, TOP + 0.008), (W / 2 - 0.08, y - 0.013, TOP + 0.008),
                                (W / 2 - 0.08, y + 0.013, TOP + 0.008), (-W / 2 + 0.08, y + 0.013, TOP + 0.008)]), "+Z")
             for y in (-0.42, 0.42)]
    C.part(seams, "Seams", C.WOOD_DARK, smooth_angle=None)
    frame = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            frame.append(ns.box((0.26, 0.26, TOP - TT), loc=(sx * (W / 2 - 0.25), sy * (D / 2 - 0.22), (TOP - TT) / 2),
                                bevel=0.04, segments=1))
    for sy in (-1, 1):
        frame.append(ns.box((W - 0.6, 0.1, 0.3), loc=(0, sy * (D / 2 - 0.22), TOP - TT - 0.15), bevel=0.0))
        frame.append(ns.box((W - 0.6, 0.1, 0.14), loc=(0, sy * (D / 2 - 0.22), 0.3), bevel=0.0))
    for sx in (-1, 1):
        frame.append(ns.box((0.1, D - 0.6, 0.3), loc=(sx * (W / 2 - 0.25), 0, TOP - TT - 0.15), bevel=0.0))
    shelf = ns.box((W - 0.62, D - 0.56, 0.1), loc=(0, 0, 0.42), bevel=0.0)
    C.part(frame + [shelf], "Frame", C.WOOD, "Wood", can_collide=True, smooth_angle=35)

    # ---- pegboard: panel, frame strips, side posts, holes ------------------------------
    pz = (PB_Z0 + PB_Z1) / 2
    panel = ns.box((W - 0.4, PB_T, PB_Z1 - PB_Z0 - 0.1), loc=(0, PB_Y + PB_T / 2, pz + 0.05), bevel=0.0)
    C.part([panel], "Pegboard", C.CREAM, can_collide=True, smooth_angle=None)
    posts = [ns.box((0.22, 0.22, PB_Z1 - TOP), loc=(sx * (W / 2 - 0.11), D / 2 - 0.11, (TOP + PB_Z1) / 2), bevel=0.03,
                    segments=1) for sx in (-1, 1)]
    strips = [ns.box((W - 0.4, 0.06, 0.12), loc=(0, PB_Y - 0.02, PB_Z1 - 0.06), bevel=0.0)]
    C.part(posts + strips, "PegFrame", C.WOOD, "Wood", can_collide=True, smooth_angle=35)
    # painted tool silhouettes (0.016 proud of the panel); holes are punched everywhere else
    sy_ = PB_Y - 0.016
    sil = []
    sil.append(C.quad_xz(-2.06, -1.82, 3.48, 4.56, sy_))                       # hammer handle (tool hangs on it)
    sil.append(C.quad_xz(-2.3, -1.58, 4.5, 4.8, sy_))                          # hammer head
    saw = [(-1.35, 5.02), (0.2, 5.12), (0.2, 5.68), (-1.35, 5.42)]            # saw blade (missing)
    sil.append(C.face_dir(C.poly([(x, sy_, z) for x, z in saw]), "-Y"))
    sil.append(C.face_dir(C.poly([(x, sy_, z) for x, z in C.rrect(0.5, 0.74, 0.16, 2, 0.45, 5.4)]), "-Y"))   # saw handle
    sil.append(C.quad_xz(0.82, 1.02, 3.5, 4.48, sy_))                          # wrench shank (tool hangs on it)
    sil.append(C.quad_xz(0.72, 1.12, 4.42, 4.72, sy_))                         # wrench jaw
    sil.append(C.strip_xz((1.48, 3.5), (1.66, 4.3), 0.13, sy_))                 # pliers (missing)
    sil.append(C.strip_xz((1.84, 3.5), (1.66, 4.3), 0.13, sy_))
    sil.append(C.quad_xz(1.58, 1.74, 4.24, 4.78, sy_))
    sil.append(C.quad_xz(2.32, 2.4, 4.0, 4.72, sy_))                           # screwdriver (missing)
    sil.append(C.quad_xz(2.24, 2.48, 3.5, 4.0, sy_))
    for o in sil:
        C.face_dir(o, "-Y")
    boxes = []
    for o in sil:
        lo, hi = C.bbox_of(o)
        boxes.append((lo.x - 0.05, hi.x + 0.05, lo.z - 0.05, hi.z + 0.05))
    C.part(sil, "Silhouettes", C.INK, smooth_angle=None)
    holes = []
    fy = PB_Y - 0.006
    for i in range(11):
        for j in range(5):
            x, z = -2.5 + i * 0.5, 3.4 + j * 0.5
            if any(x0 < x < x1 and z0 < z < z1 for x0, x1, z0, z1 in boxes):
                continue
            holes.append(C.quad_xz(x - 0.03, x + 0.03, z - 0.03, z + 0.03, fy))
    C.part(holes, "Holes", C.DARK_VOID, smooth_angle=None)

    # hooks + the two tools still hanging
    hooks = []
    for x, z in ((-1.94, 4.95), (0.92, 4.95), (-0.5, 4.45), (2.36, 4.95)):
        hooks.append(C.pipe([(x, PB_Y + 0.02, z), (x, PB_Y - 0.16, z), (x, PB_Y - 0.16, z + 0.09)], 0.022, sides=4))
    ham_y = PB_Y - 0.1
    handle = C.rod((-1.94, ham_y, 3.56), (-1.94, ham_y, 4.6), 0.075, verts=6)
    head = ns.box((0.64, 0.15, 0.22), loc=(-1.94, ham_y, 4.64), bevel=0.04, segments=1)
    wrench = [ns.box((0.13, 0.05, 0.92), loc=(0.92, PB_Y - 0.08, 4.0), bevel=0.0),
              ns.box((0.32, 0.05, 0.24), loc=(0.92, PB_Y - 0.08, 4.56), bevel=0.0)]
    C.part(hooks + wrench, "Steel", C.STEEL, "Metal", smooth_angle=40)

    # ---- vise at the front-left corner ------------------------------------------------
    vx, vy = -2.3, -0.62
    vise = [ns.box((0.6, 0.55, 0.12), loc=(vx, vy, TOP + 0.06), bevel=0.03, segments=1),
            ns.box((0.36, 0.62, 0.3), loc=(vx, vy - 0.03, TOP + 0.27), bevel=0.05, segments=1),
            ns.box((0.66, 0.16, 0.36), loc=(vx, vy + 0.24, TOP + 0.36), bevel=0.04, segments=1),
            ns.box((0.66, 0.16, 0.36), loc=(vx, vy - 0.4, TOP + 0.36), bevel=0.04, segments=1)]
    C.part(vise, "Vise", "#3E4A55", "Metal", smooth_angle=40)
    vbar = [C.rod((vx, vy - 0.48, TOP + 0.3), (vx, vy - 0.72, TOP + 0.3), 0.05, verts=6),
            C.rod((vx - 0.36, vy - 0.72, TOP + 0.3), (vx + 0.36, vy - 0.72, TOP + 0.3), 0.035, verts=6),
            ns.box((0.6, 0.02, 0.06), loc=(vx, vy - 0.49, TOP + 0.48), bevel=0.0),
            ns.box((0.6, 0.02, 0.06), loc=(vx, vy + 0.15, TOP + 0.48), bevel=0.0)]
    for x in (vx - 0.37, vx + 0.37):
        vbar.append(ns.sphere(0.06, loc=(x, vy - 0.72, TOP + 0.3), segs=6, rings=4))

    # ---- red toolbox ------------------------------------------------------------------
    tx, ty = 1.55, 0.35
    tb = [ns.box((1.3, 0.62, 0.42), loc=(tx, ty, TOP + 0.21), bevel=0.04, segments=1),
          ns.box((1.34, 0.66, 0.16), loc=(tx, ty, TOP + 0.5), bevel=0.05, segments=1)]
    C.part(tb, "Toolbox", RED, smooth_angle=35)
    tb_steel = [C.rod((tx - 0.3, ty, TOP + 0.58), (tx - 0.3, ty, TOP + 0.72), 0.03, verts=4),
                C.rod((tx + 0.3, ty, TOP + 0.58), (tx + 0.3, ty, TOP + 0.72), 0.03, verts=4),
                C.rod((tx - 0.34, ty, TOP + 0.72), (tx + 0.34, ty, TOP + 0.72), 0.045, verts=6)]
    tb_steel += [ns.box((0.12, 0.04, 0.16), loc=(tx + dx, ty - 0.33, TOP + 0.42), bevel=0.0) for dx in (-0.4, 0.4)]

    # ---- loose tools on the top --------------------------------------------------------
    loose_wood, loose_iron = [], []
    a = math.radians(24)
    hx, hy = -0.75, -0.45
    d = (math.cos(a), math.sin(a), 0)
    loose_wood.append(C.rod((hx - d[0] * 0.45, hy - d[1] * 0.45, TOP + 0.05), (hx + d[0] * 0.45, hy + d[1] * 0.45, TOP + 0.05),
                            0.05, verts=6))
    loose_iron.append(ns.box((0.13, 0.4, 0.13), loc=(hx + d[0] * 0.5, hy + d[1] * 0.5, TOP + 0.065), rot=(0, 0, 24),
                             bevel=0.02, segments=1))
    sd = [ns.cyl(0.06, 0.32, loc=(0.35, -0.75, TOP + 0.06), rot=(0, 90, -10), verts=6, bevel=0.0)]
    tb_steel.append(C.rod((0.51, -0.778, TOP + 0.06), (0.95, -0.856, TOP + 0.06), 0.022, verts=4))
    tb_steel += [ns.box((0.62, 0.09, 0.035), loc=(0.15, -0.05, TOP + 0.018), rot=(0, 0, -35), bevel=0.0),
                 ns.box((0.2, 0.2, 0.06), loc=(0.15 + 0.3 * math.cos(math.radians(-35)), -0.05 + 0.3 * math.sin(math.radians(-35)),
                                               TOP + 0.02), rot=(0, 0, -35), bevel=0.0)]   # jaw: thicker, foot in the top
    rag = ns.sphere(0.32, loc=(-0.1, 0.55, TOP + 0.06), scale=(1.2, 0.9, 0.22), segs=8, rings=4)
    ns.jitter(rag, amount=0.04, seed=3)
    C.part(loose_wood, "Handles", C.WOOD_LIGHT, "Wood", smooth_angle=50)
    C.part(loose_iron + [head] + vbar, "Iron", C.IRON, "Metal", smooth_angle=40)
    C.part([handle], "HangHandle", C.WOOD_LIGHT, "Wood", smooth_angle=50)
    C.part(tb_steel, "SteelSmall", C.STEEL, "Metal", smooth_angle=40)
    C.part(sd, "Grip", C.MUSTARD, smooth_angle=50)
    C.part([rag], "Rag", "#B9AE96", "Fabric", smooth_angle=60)

    # ---- lower shelf: coiled hose, paint can, small crate --------------------------------
    sz = 0.47
    hose = [ns.torus(0.42, 0.07, loc=(-1.6, 0.05, sz + 0.07 + k * 0.13), major_segs=12, minor_segs=4) for k in range(2)]
    C.part(hose, "Hose", HOSE, smooth_angle=50)
    can_m, can_l = C.can(0.1, -0.2, sz, r=0.28, h=0.62, verts=8)
    C.part([can_m], "CanMetal", C.STEEL, "Metal", smooth_angle=60)
    C.part([can_l], "CanLabel", C.BRAND, smooth_angle=60)
    crate = ns.box((1.1, 0.9, 0.7), loc=(1.5, 0.1, sz + 0.35), rot=(0, 0, rnd.uniform(-6, 6)), bevel=0.04, segments=1)
    C.part([crate], "Crate", C.WOOD_DARK, "Wood", smooth_angle=35)


META = {"worktop": TOP, "pegboard_top": PB_Z1, "collide": "bench + pegboard", "back": "+Y against the wall",
        "story": "saw, pliers and screwdriver are missing from their painted outlines"}

if __name__ == "__main__":
    C.run(build, "Basement_Workbench", budget=2000, meta=META)
