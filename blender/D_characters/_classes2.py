"""_classes2 — the six class characters added on 2026-11-06 (Landon: "we are going to want more
classes before we drop ... like 99 Nights where there are weekly deals"), on the same Human kit,
rig (ClassCast) and conventions as _classes.py, which imports this module and so carries them in
ORDER / TITLES / POSES / PROPS / OUTFITS (Character_Class__anim.py writes all twelve clips).

  exterminator  olive coverall with a NO RATS patch, yellow rubber gloves, utility belt, cap and
                a bushy moustache; leans on a long rat-whacking spatula, a snap trap dangling from
                the other hand
  cashier       red diner shirt, white collar, HI! badge, ponytail and a pencil behind the ear;
                takes your order on a pad, pencil scribbling, a smile up at you
  food_critic   purple blazer with gold buttons, a gold ascot, pocket square and monocle, silver
                slicked hair; a fork raised with a bite on it, chin up, a little notebook
  detective     belted tan trench coat (popped collar, skirt to the knee) and fedora, a squint;
                peers through a magnifying glass, sweeping it slowly
  bouncer       black tee, chain, sunglasses, earpiece with its coiled wire, beard, bald; hands
                clasped at the belt beside a brass stanchion with its velvet rope; a slow, stern
                look round
  mascot        mustard STACKHOUSE jersey with the burger crest and red trim, a foam burger hat,
                a pink #1 foam finger pumping the air, bouncing on the spot
"""
from __future__ import annotations

import math

import _common as C
import _classes as K

ns = C.ns
Vector = C.Vector
Matrix = C.Matrix
D = C.D2R
hold, hold_min, hand_frame, breathe, rot_z = K.hold, K.hold_min, K.hand_frame, K.breathe, K.rot_z
place, zcyl, chest_pt, chest_panel, collar_flaps, buttons, ring_band, gloves = (
    K.place, K.zcyl, K.chest_pt, K.chest_panel, K.collar_flaps, K.buttons, K.ring_band, K.gloves)
END = K.END
WHITE, RED, GOLD, CHROME, INK = K.WHITE, K.RED, K.GOLD, K.CHROME, K.INK

NEW = ["exterminator", "cashier", "food_critic", "detective", "bouncer", "mascot"]
TITLES = {"exterminator": "Exterminator", "cashier": "Cashier", "food_critic": "Food Critic",
          "detective": "Detective", "bouncer": "Bouncer", "mascot": "Mascot"}


# --------------------------------------------------------------------------------------
# poses (frame 0 is the pose the props are modelled in)
# --------------------------------------------------------------------------------------

def pose_exterminator(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=0.9, base=(-1.0, 0, -6))
    for f, rot in ((0, (2, 0, -14)), (30, (2, 0, -4)), (60, (3, 0, 10)), (90, (2, 0, -4)), (END, (2, 0, -14))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    # the spatula held upright like a staff (a little tap on the beat), the trap at the left side
    for f, d in ((0, (-0.3, -0.62, -0.72)), (40, (-0.3, -0.62, -0.7)), (80, (-0.3, -0.62, -0.72)), (END, (-0.3, -0.62, -0.72))):
        c.k("ArmR", f, c.aim_arm("R", f, direction=d))
    for f, d in ((0, (0.4, -0.3, -0.86)), (60, (0.41, -0.28, -0.86)), (END, (0.4, -0.3, -0.86))):
        c.k("ArmL", f, c.aim_arm("L", f, direction=d))
    c.commit(["ArmR", "ArmL"])
    for f, tilt in ((0, 0.0), (40, 0.06), (80, 0.0), (END, 0.0)):
        c.k("HandR", f, hold(c, "R", f, axis=(-0.14 + tilt, 0.22, 1.0), palm=(0.9, -0.4, 0.0)))
    for f in (0, END):
        c.k("HandL", f, hold(c, "L", f, axis=(0.0, -1.0, 0.0), palm=(-1.0, 0.0, 0.0)))


def pose_cashier(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=1.0, base=(2.0, 3, 6))
    # writing on the pad, then a smile up at the customer
    for f, rot in ((0, (16, 4, 6)), (40, (18, 3, 8)), (70, (-4, -6, 2)), (95, (-3, -6, 0)), (END, (16, 4, 6))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    # the pad held in front (left hand), the pencil hand meeting it from the right
    for f in (0, 60, END):
        c.k("ArmL", f, c.aim_arm("L", f, direction=(-0.24, -0.74, -0.63)))
    for f, d in ((0, (0.34, -0.72, -0.6)), (8, (0.38, -0.71, -0.6)), (16, (0.33, -0.72, -0.61)), (24, (0.37, -0.72, -0.59)),
                 (32, (0.33, -0.72, -0.6)), (40, (0.36, -0.72, -0.6)), (70, (0.3, -0.7, -0.65)), (END, (0.34, -0.72, -0.6))):
        c.k("ArmR", f, c.aim_arm("R", f, direction=d))
    c.commit(["ArmL", "ArmR"])
    for f in (0, END):
        c.k("HandL", f, c.orient_hand("L", f, Vector((-0.5, -0.6, 0.62)), Vector((-0.2, 0.55, 0.8))))
    for f in (0, END):
        c.k("HandR", f, hold(c, "R", f, axis=(0.78, -0.12, -0.6), palm=(0.0, 1.0, 0.0)))


def pose_food_critic(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=0.7, base=(-3.0, 0, -6))
    # chin up, a thoughtful nod at the bite
    for f, rot in ((0, (-10, 4, -10)), (30, (-12, 5, -14)), (55, (-4, 2, -8)), (75, (-11, 4, -12)), (END, (-10, 4, -10))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for f, d in ((0, (-0.42, -0.62, 0.66)), (60, (-0.44, -0.6, 0.66)), (END, (-0.42, -0.62, 0.66))):
        c.k("ArmR", f, c.aim_arm("R", f, direction=d))
    for f in (0, END):
        c.k("ArmL", f, c.aim_arm("L", f, direction=(0.26, -0.56, -0.79)))
    c.commit(["ArmR", "ArmL"])
    # the fork twirls a little
    for f, w in ((0, 0.0), (20, 0.25), (40, -0.2), (60, 0.0), (END, 0.0)):
        c.k("HandR", f, hold(c, "R", f, axis=(0.06 + w * 0.2, -0.1, 1.0), palm=(0.85, -0.5 + w, 0.0)))
    for f in (0, END):
        c.k("HandL", f, c.orient_hand("L", f, Vector((-0.2, -0.5, -0.84)), Vector((-0.2, -0.85, 0.5))))


SWEEP2 = ((0, 0.0), (40, 10.0), (80, -10.0), (END, 0.0))


def pose_detective(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=0.7, base=(8.0, 0, -4))
    for f, yaw in SWEEP2:
        c.k("Head", f, (14, 0, yaw * 0.6 - 6))
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for f, yaw in SWEEP2:
        c.k("ArmR", f, c.aim_arm("R", f, direction=rot_z(yaw, (-0.12, -0.84, -0.53))))
    for f in (0, END):
        c.k("ArmL", f, c.aim_arm("L", f, direction=(0.22, 0.12, -0.97)))
    c.commit(["ArmR", "ArmL"])
    for f, yaw in SWEEP2:
        c.k("HandR", f, hold_min(c, "R", f, axis=rot_z(yaw, (0.15, -0.2, 0.97)), arm_d=rot_z(yaw, (-0.12, -0.84, -0.53))))
    for f in (0, END):
        c.k("HandL", f, (8, 0, 0))


def pose_bouncer(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=0.6, base=(-2.0, 0, 0))
    for f, rot in ((0, (-4, 0, 0)), (35, (-4, 0, 18)), (60, (-4, 0, 18)), (85, (-2, 0, -12)), (105, (-4, 0, -12)), (END, (-4, 0, 0))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    # hands clasped in front of the belt
    for side, s in C.SIDES:
        for f in (0, END):
            c.k("Arm" + side, f, c.aim_arm(side, f, direction=(-s * 0.36, -0.42, -0.83)))
    c.commit(["ArmL", "ArmR"])
    for side, s in C.SIDES:
        for f in (0, END):
            c.k("Hand" + side, f, c.orient_hand(side, f, Vector((-s * 0.55, -0.2, -0.81)), Vector((-s * 0.85, -0.2, 0.45))))


def pose_mascot(c):
    # bouncing on the spot, the foam finger pumping the air
    for f in range(0, END + 1, 15):
        z = 0.06 if (f // 15) % 2 == 1 else 0.0
        c.k("Hips", f, (0, 0, 0), loc=(0, 0, z), ease="QUAD", d="EASE_OUT" if z > 0 else "EASE_IN")
    C._static(c, ["LegL", "LegR"])
    breathe(c, pitch=1.4, sway=1.6, base=(-2.0, 0, 6))
    for f, rot in ((0, (-6, -6, 8)), (15, (-4, -2, 6)), (30, (-8, -6, 10)), (45, (-4, -2, 6)), (60, (-6, -6, 8)),
                   (75, (-4, -2, 6)), (90, (-8, -6, 10)), (105, (-4, -2, 6)), (END, (-6, -6, 8))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for f in range(0, END + 1, 15):
        up = (f // 15) % 2 == 0
        c.k("ArmR", f, c.aim_arm("R", f, direction=(-0.42, -0.24, 0.87) if up else (-0.5, -0.3, 0.8)))
    for f in (0, 60, END):
        c.k("ArmL", f, c.aim_arm("L", f, direction=(0.62, -0.1, -0.78)))
    c.commit(["ArmR", "ArmL"])
    for f in range(0, END + 1, 15):
        c.k("HandR", f, hold(c, "R", f, axis=(0.0, 0.0, 1.0), palm=(0.9, -0.44, 0.0)))
    for f in (0, END):
        c.k("HandL", f, c.orient_hand("L", f, Vector((0.4, -0.1, -0.9)), Vector((-0.6, -0.3, -0.2))))


POSES = {"exterminator": pose_exterminator, "cashier": pose_cashier, "food_critic": pose_food_critic,
         "detective": pose_detective, "bouncer": pose_bouncer, "mascot": pose_mascot}


# --------------------------------------------------------------------------------------
# props (built at Display frame 0)
# --------------------------------------------------------------------------------------

def prop_spatula_trap(arm):
    P, A, L, N = hand_frame(arm, "R")
    handle = place([zcyl(0.05, -0.55, 1.35, verts=10, bevel=0.01)], P, A, N)
    grip = place([zcyl(0.06, -0.55, -0.1, verts=10, bevel=0.01)], P, A, N)
    ferrule = place([zcyl(0.06, 1.35, 1.45, verts=10)], P, A, N)
    blade = place([C.rbox((0.62, 0.035, 0.66), loc=(0, 0, 1.78), bevel=0.02, seg=1)], P, A, N)
    slots = place([C.rbox((0.06, 0.04, 0.38), loc=(x, 0, 1.78), bevel=0.0, seg=1) for x in (-0.15, 0.0, 0.15)], P, A, N)
    C.part(handle + ferrule + blade, "WhackerBlade", CHROME, "Metal", arm=arm, bone="HandR", smooth=30)
    C.part(grip, "WhackerGrip", "#2B2D31", arm=arm, bone="HandR", smooth=50)
    # (Metal like the blade: a lone SmoothPlastic grip keeps its own name - a merged
    # "HandR_SmoothPlastic" would make the mesh asset name longer than Roblox's 50 characters)
    C.part(slots, "WhackerSlots", "#3A3D44", "Metal", arm=arm, bone="HandR", smooth=30)
    # a wooden snap trap dangling flat from the left hand by its end
    P, A, L, N = hand_frame(arm, "L")
    fwd = Vector((0, -1, 0))
    tc = P + fwd * 0.42 + Vector((0, 0, -0.08))
    board = C.rbox((0.42, 0.78, 0.08), loc=tuple(tc), bevel=0.02, seg=1)
    bar = C.tube([tc + Vector((-0.17, 0.05, 0.05)), tc + Vector((-0.17, -0.3, 0.05)), tc + Vector((0.17, -0.3, 0.05)),
                  tc + Vector((0.17, 0.05, 0.05))], [0.018] * 4, sides=6, res=1)
    bait = C.rbox((0.12, 0.12, 0.05), loc=tuple(tc + Vector((0, 0.22, 0.06))), bevel=0.01, seg=1)
    cheese = C.rbox((0.16, 0.1, 0.1), loc=tuple(tc + Vector((0, 0.22, 0.12))), rot=(0, 0, 20), bevel=0.01, seg=1)
    C.part([board], "Trap", "#C8925A", "Wood", arm=arm, bone="HandL", smooth=30)
    C.part([bar, bait], "TrapWire", CHROME, "Metal", arm=arm, bone="HandL", smooth=30)
    C.part([cheese], "TrapCheese", "#FFD23A", arm=arm, bone="HandL", smooth=30)


def prop_pad_pencil(arm):
    P, A, L, N = hand_frame(arm, "L")
    # the order pad lies in the palm, its face toward the cashier's eyes
    up = (L + N * 0.4).normalized()
    ctr = P + N * 0.12 + L * 0.1
    x, y, z = K.basis(N, up)
    M = Matrix(((x[0], y[0], z[0], ctr[0]), (x[1], y[1], z[1], ctr[1]), (x[2], y[2], z[2], ctr[2]), (0, 0, 0, 1)))
    pad = C.rbox((0.46, 0.62, 0.06), bevel=0.012, seg=1)
    sheet = C.rbox((0.42, 0.56, 0.01), loc=(0, -0.02, 0.035), bevel=0.0, seg=1)
    head = C.rbox((0.47, 0.1, 0.075), loc=(0, 0.28, 0.0), bevel=0.01, seg=1)
    lines = [C.rbox((0.3, 0.025, 0.01), loc=(-0.02, 0.12 - 0.11 * k, 0.042), bevel=0.0, seg=1) for k in range(4)]
    for o in [pad, sheet, head] + lines:
        ns.apply_all(o)
        C.xform(o, M)
    C.part([pad, head], "Pad", RED, arm=arm, bone="HandL", smooth=30)
    C.part([sheet], "PadSheet", "#FBF8EE", arm=arm, bone="HandL", smooth=30)
    C.part(lines, "PadLines", "#3A4A66", arm=arm, bone="HandL", smooth=30)
    P, A, L, N = hand_frame(arm, "R")
    pencil = place([zcyl(0.035, -0.22, 0.34, verts=6)], P, A, N)
    tip = place([ns.cyl(0.035, 0.1, loc=(0, 0, 0.39), verts=6, bevel=0.0, radius_top=0.004)], P, A, N)
    eraser = place([zcyl(0.036, -0.3, -0.22, verts=6)], P, A, N)
    C.part(pencil, "Pencil", "#FFC93C", arm=arm, bone="HandR", smooth=20)
    C.part(tip, "PencilTip", "#E3CDA0", "Wood", arm=arm, bone="HandR", smooth=20)
    C.part(eraser, "Eraser", "#F08FB0", arm=arm, bone="HandR", smooth=30)


def prop_fork_notebook(arm):
    P, A, L, N = hand_frame(arm, "R")
    handle = place([C.rbox((0.06, 0.025, 0.62), loc=(0, 0, 0.2), bevel=0.01, seg=1)], P, A, N)
    neck = place([C.rbox((0.1, 0.025, 0.14), loc=(0, 0, 0.56), bevel=0.008, seg=1)], P, A, N)
    tines = place([C.rbox((0.022, 0.022, 0.22), loc=(x, 0, 0.72), bevel=0.006, seg=1) for x in (-0.045, -0.015, 0.015, 0.045)], P, A, N)
    bite = place([C.rbox((0.16, 0.12, 0.12), loc=(0, 0, 0.78), bevel=0.03, seg=1)], P, A, N)
    filling = place([C.rbox((0.17, 0.125, 0.035), loc=(0, 0, 0.79), bevel=0.01, seg=1)], P, A, N)
    C.part(handle + neck + tines, "Fork", CHROME, "Metal", arm=arm, bone="HandR", smooth=30)
    C.part(bite, "Bite", "#D9A35B", arm=arm, bone="HandR", smooth=40)
    C.part(filling, "BiteFilling", "#6DBE45", arm=arm, bone="HandR", smooth=40)
    P, A, L, N = hand_frame(arm, "L")
    ctr = P + N * 0.1 + L * 0.06
    x, y, z = K.basis(N, L)
    M = Matrix(((x[0], y[0], z[0], ctr[0]), (x[1], y[1], z[1], ctr[1]), (x[2], y[2], z[2], ctr[2]), (0, 0, 0, 1)))
    book = C.rbox((0.34, 0.46, 0.09), bevel=0.015, seg=1)
    band = C.rbox((0.35, 0.04, 0.095), loc=(0, -0.12, 0.0), bevel=0.0, seg=1)
    for o in (book, band):
        ns.apply_all(o)
        C.xform(o, M)
    C.part([book], "Notebook", "#3A2A1E", arm=arm, bone="HandL", smooth=30)
    C.part([band], "NotebookBand", GOLD, arm=arm, bone="HandL", smooth=30)


def prop_magnifier(arm):
    P, A, L, N = hand_frame(arm, "R")
    handle = place([zcyl(0.06, -0.2, 0.32, verts=12, bevel=0.015)], P, A, N)
    collar = place([zcyl(0.075, 0.32, 0.42, verts=12)], P, A, N)
    # the lens ring at the top of the handle, turned to face the detective's eye
    c0 = P + A * 0.72
    eye = Vector((0.0, -0.6, 4.4))
    nrm = (eye - c0).normalized()
    q = Vector((0, 0, 1)).rotation_difference(nrm).to_matrix().to_4x4()
    ring = ns.torus(0.3, 0.045, loc=(0, 0, 0), major_segs=24, minor_segs=8)
    lens = ns.cyl(0.28, 0.025, loc=(0, 0, 0), verts=24, bevel=0.0)
    for o in (ring, lens):
        ns.apply_all(o)
        C.xform(o, Matrix.Translation(c0) @ q)
    C.part(handle, "MagHandle", "#3B2A1A", "Wood", arm=arm, bone="HandR", smooth=40)
    C.part(collar + [ring], "MagRing", GOLD, "Metal", arm=arm, bone="HandR", smooth=40)
    C.part([lens], "MagLens", "#CFEFFF", "Glass", arm=arm, bone="HandR", smooth=30, transparency=0.55, shadow=False)


def prop_stanchion(arm):
    # a brass stanchion at the bouncer's left and its velvet rope sweeping off to the side
    bx, by = 1.25, -0.25
    base = ns.cyl(0.32, 0.08, loc=(bx, by, 0.04), verts=24, bevel=0.03)
    post = zcyl(0.06, 0.08, 2.4, verts=14, bevel=0.0, x=bx, y=by)
    ball = ns.sphere(0.13, loc=(bx, by, 2.48), segs=14, rings=8)
    hook = ns.torus(0.07, 0.022, loc=(bx - 0.1, by, 2.2), major_segs=12, minor_segs=5)
    C.part([base, post, ball, hook], "Stanchion", "#E2B64A", "Metal", arm=arm, bone="Hips", smooth=40)
    rope = C.tube([Vector((bx + 0.12, by, 2.18)), Vector((bx + 0.5, by - 0.1, 1.7)), Vector((bx + 1.0, by - 0.2, 1.55)),
                   Vector((bx + 1.45, by - 0.25, 1.8))], [0.06] * 4, sides=8, res=4)
    C.part([rope], "VelvetRope", "#8E1B2C", "Fabric", arm=arm, bone="Hips", smooth=60)


def prop_foam_finger(arm):
    P, A, L, N = hand_frame(arm, "R")
    # the foam hand swallows the real one; its index finger points up along the arm
    palm = place([C.ellipsoid((0, 0, 0.12), (0.3, 0.18, 0.34), segs=14, rings=8)], P, A, N)
    finger = place([C.ellipsoid((0.02, 0, 0.78), (0.11, 0.1, 0.42), segs=12, rings=8)], P, A, N)
    knuckles = place([C.ellipsoid((x, -0.04, 0.38), (0.1, 0.12, 0.12), segs=10, rings=6) for x in (-0.18, -0.06)], P, A, N)
    thumb = place([C.ellipsoid((0.26, -0.05, 0.24), (0.09, 0.09, 0.18), segs=10, rings=6, rot=(0, -30, 0))], P, A, N)
    cuff = place([zcyl(0.24, -0.34, -0.12, verts=16, bevel=0.03)], P, A, N)
    one = place([C.rbox((0.05, 0.03, 0.22), loc=(0.0, -0.19, 0.08), bevel=0.0, seg=1),
                 C.rbox((0.09, 0.03, 0.04), loc=(-0.03, -0.19, 0.17), rot=(0, 30, 0), bevel=0.0, seg=1)], P, A, N)
    C.part(palm + finger + knuckles + thumb, "FoamHand", "#FF3D7F", "Fabric", arm=arm, bone="HandR", smooth=60)
    C.part(cuff, "FoamCuff", WHITE, "Fabric", arm=arm, bone="HandR", smooth=50)
    C.part(one, "FoamNumber", WHITE, arm=arm, bone="HandR", smooth=30)


PROPS = {"exterminator": prop_spatula_trap, "cashier": prop_pad_pencil, "food_critic": prop_fork_notebook,
         "detective": prop_magnifier, "bouncer": prop_stanchion, "mascot": prop_foam_finger}


# --------------------------------------------------------------------------------------
# outfits (rest pose)
# --------------------------------------------------------------------------------------

def _patch_disc(centre_z, x, r, color, ring_col, arm, name):
    """A round sewn-on chest patch with an embroidered edge."""
    p = chest_pt(x, centre_z, 0.07)
    disc = ns.cyl(r, 0.025, loc=tuple(p), rot=(90, 0, 0), verts=20, bevel=0.0)
    edge = ns.torus(r, 0.018, loc=tuple(p + Vector((0, -0.012, 0))), major_segs=20, minor_segs=5)
    ns.apply_all(edge)
    C.xform(edge, Matrix.Translation(p) @ Matrix.Rotation(math.radians(90), 4, "X") @ Matrix.Translation(-p))
    C.part([disc], name, color, "Fabric", arm=arm, bone="Torso", smooth=40)
    C.part([edge], name + "Edge", ring_col, "Fabric", arm=arm, bone="Torso", smooth=40)
    return p


def build_exterminator(arm):
    OLIVE = "#6F7F3A"
    look = {"skin": "#D9A07A", "top": OLIVE, "pants": OLIVE, "shoes": "#2B2D31", "sole": "#1E1F22",
            "brow": "#4A3322", "brow_tilt": -6.0, "lid_drop": 0.05, "mouth_curve": 0.02, "generic": False,
            "skip": ("HandL", "HandR")}
    C.build_body(arm, look)
    collar_flaps("#56652C", arm, name="CoverallCollar")
    zp = [C.torso_pt(0, C.gt(z), 0.06) for z in (2.12, 2.6, 3.1, 3.52)]
    C.part([C.tube(zp, [0.016] * 4, sides=6, res=1)], "Zip", CHROME, "Metal", arm=arm, bone="Torso", smooth=40)
    pc = _patch_disc(3.08, 0.34, 0.15, WHITE, RED, arm, "NoRatsPatch")
    rat = C.ellipsoid(pc + Vector((0.0, -0.03, -0.01)), (0.08, 0.02, 0.045), segs=8, rings=5)
    slash = C.rbox((0.25, 0.02, 0.03), loc=tuple(pc + Vector((0, -0.035, 0))), rot=(0, -38, 0), bevel=0.0, seg=1)
    C.part([rat], "PatchRat", "#5A5F68", arm=arm, bone="Torso", smooth=40)
    C.part([slash], "PatchSlash", RED, arm=arm, bone="Torso", smooth=30)
    belt = ring_band(2.1, 2.28, 0.67, 0.465, segs=24, name="Belt")
    pouch = C.rbox((0.18, 0.22, 0.24), loc=(-0.66, -0.05, 2.08), rot=(0, 0, -8), bevel=0.03, seg=1)
    C.part([belt, pouch], "UtilityBelt", "#3A3326", arm=arm, bone="Hips", smooth=40)
    C.part([C.rbox((0.2, 0.04, 0.15), loc=(0, -0.475, 2.19), bevel=0.02, seg=1)], "Buckle", CHROME, "Metal",
           arm=arm, bone="Hips", smooth=30)
    gloves(arm, "#F2C230", "#D9A720")
    C.place_accessory(C.strip_roles(C.acc_hair_short(color="#4A3322")), arm=arm, bone="Head")
    C.place_accessory(C.strip_roles(C.acc_face_mustache(color="#4A3322", big=True)), arm=arm, bone="Head")
    C.place_accessory(C.acc_hat_trucker(color="#3E4A22", mesh="#2B2D31", patch_col=RED), arm=arm, bone="Head")


def build_cashier(arm):
    RED_SHIRT = "#D94B4B"
    look = {"skin": "#A86B4A", "top": RED_SHIRT, "pants": "#2B2D33", "shoes": "#F2F2EE", "sole": "#C9CED3",
            "brow": "#2A1C14", "brow_tilt": 8.0, "lid_drop": 0.0, "mouth_curve": 0.034, "generic": False,
            "sleeve": "short"}
    C.build_body(arm, look)
    collar_flaps(WHITE, arm, name="Collar")
    plk = chest_panel(3.0, 3.56, lambda z: 0.055, 0.035, 0.012, name="Placket")
    C.part([plk], "Placket", "#B83A3A", "Fabric", arm=arm, bone="Torso", smooth=40)
    buttons([(0.0, 3.12), (0.0, 3.3), (0.0, 3.48)], WHITE, arm, r=0.03, infl=0.058)
    bc = chest_pt(0.34, 3.12, 0.075)
    badge = C.rbox((0.34, 0.03, 0.19), loc=tuple(bc), rot=(4, 0, 24), bevel=0.02, seg=1)
    C.part([badge], "Badge", WHITE, arm=arm, bone="Torso", role="badge", smooth=30)
    bar = C.rbox((0.24, 0.012, 0.07), loc=tuple(bc + Vector((0.006, -0.018, 0.0))), rot=(4, 0, 24), bevel=0.0, seg=1)
    C.part([bar], "BadgeHi", RED_SHIRT, arm=arm, bone="Torso", smooth=30)
    for s in (1, -1):
        trim = ring_band(2.8, 2.85, 0.27, 0.262, n=2.0, segs=16, name="SleeveTrim")
        ns.apply_all(trim)
        C.xform(trim, C._arm_matrix(s) @ Matrix.Translation((0, 0, -2.8 - 0.49)))
        C.part([trim], "Arm" + ("L" if s > 0 else "R") + "_Trim", WHITE, "Fabric", arm=arm, bone="Arm" + ("L" if s > 0 else "R"), smooth=50)
    C.place_accessory(C.strip_roles(C.acc_hair_ponytail(color="#2A1C14", tie=WHITE, high=True)), arm=arm, bone="Head")
    pencil = C.rbox((0.04, 0.04, 0.36), loc=(-0.66, 0.1, 4.52), rot=(-28, 0, 6), bevel=0.0, seg=1)
    C.part([pencil], "EarPencil", "#FFC93C", arm=arm, bone="Head", smooth=20)


def build_food_critic(arm):
    PURPLE, PURPLE_D = "#5B3A8C", "#43296A"
    look = {"skin": "#F0C8A8", "top": PURPLE, "pants": "#2E2A3A", "shoes": "#4A2E1E", "sole": "#2B2520",
            "brow": "#B9B4AD", "brow_tilt": -4.0, "brow_size": (0.21, 0.05, 0.06), "lid_drop": 0.07,
            "mouth_curve": 0.006, "generic": False}
    C.build_body(arm, look)
    # lapels: two long tapering panels down the jacket front
    for s, side in ((1, "L"), (-1, "R")):
        lap = chest_panel(2.55, 3.55, lambda z: 0.04 + 0.1 * C.smoothstep(2.6, 3.4, z), 0.04, 0.03,
                          centre_x=(lambda z, s=s: s * (0.1 + 0.16 * C.smoothstep(2.6, 3.45, z))), nv=10, name="Lapel")
        C.part([lap], "Lapel" + side, PURPLE_D, "Fabric", arm=arm, bone="Torso", smooth=40)
    ascot_knot = C.ellipsoid((0.0, -0.36, 3.52), (0.13, 0.08, 0.1), segs=10, rings=6)
    ascot = chest_panel(2.95, 3.48, lambda z: 0.05 + 0.08 * C.smoothstep(3.45, 3.1, z), 0.07, 0.03, nv=8, name="Ascot")
    C.part([ascot_knot, ascot], "Ascot", "#E8B23A", "Fabric", arm=arm, bone="Torso", smooth=50)
    dots = [ns.sphere(0.02, loc=tuple(chest_pt(x, z, 0.105)), segs=6, rings=4) for x, z in ((-0.04, 3.32), (0.05, 3.2), (-0.02, 3.08))]
    C.part(dots, "AscotDots", "#B5452F", arm=arm, bone="Torso", smooth=40)
    sq = chest_pt(0.36, 3.15, 0.075)
    C.part([C.rbox((0.2, 0.03, 0.08), loc=tuple(sq), rot=(4, 0, 24), bevel=0.01, seg=1)], "PocketSquare", WHITE, arm=arm,
           bone="Torso", smooth=30)
    buttons([(0.12, 2.6), (0.12, 2.85)], GOLD, arm, r=0.04, mat="Metal")
    C.place_accessory(C.strip_roles(C.acc_hair_short(color="#C9C5BE")), arm=arm, bone="Head")
    C.place_accessory(C.strip_roles(C.acc_face_mustache(color="#C9C5BE")), arm=arm, bone="Head")
    # the monocle over his right eye on a fine gold chain to the lapel
    ez, ex = 4.42, 0.235
    cy = C._face_y(-ex, ez) - 0.1
    mc = Vector((-ex, cy, ez))
    mono = ns.torus(0.13, 0.022, loc=(0, 0, 0), major_segs=20, minor_segs=5)
    lens = ns.cyl(0.12, 0.01, loc=(0, 0, 0), verts=20, bevel=0.0)
    for o in (mono, lens):
        ns.apply_all(o)
        C.xform(o, Matrix.Translation(mc) @ Matrix.Rotation(math.radians(90), 4, "X") @ Matrix.Rotation(math.radians(8), 4, "Y"))
    chain = C.tube([mc + Vector((-0.08, 0.0, -0.1)), mc + Vector((-0.12, 0.06, -0.45)), Vector((-0.22, -0.36, 3.6))],
                   [0.012] * 3, sides=5, res=4)
    C.part([mono], "Monocle", GOLD, "Metal", arm=arm, bone="Head", smooth=40)
    C.part([lens], "MonocleLens", "#DDF6FF", "Glass", arm=arm, bone="Head", smooth=30, transparency=0.6, shadow=False)
    C.part([chain], "MonocleChain", GOLD, "Metal", arm=arm, bone="Head", smooth=40)


def fedora(color="#5A4632", band="#2B1F17"):
    """A fedora: pinched crown, a band, a wide brim snapped down at the front."""
    infl = 0.12
    crown = C.loft_z([(4.86, 0.66, 0.62, 2.3), (5.12, 0.64, 0.6, 2.3), (5.3, 0.56, 0.52, 2.4), (5.36, 0.4, 0.36, 2.4)],
                     segs=28, cap0=False, cap1=True, name="Crown")
    for v in crown.data.vertices:          # the front pinch and the top crease
        if v.co.z > 5.2:
            v.co.y += 0.05 * math.exp(-(v.co.x / 0.18) ** 2)
            v.co.z -= 0.06 * math.exp(-(v.co.x / 0.12) ** 2)
    hb = ring_band(4.86, 5.0, 0.665, 0.625, n=2.3, segs=28, name="HatBand")

    def brim_pt(u, v, off):
        phi = 2 * math.pi * u
        r0a, r0b = 0.64, 0.6
        rr = 1.0 + 0.62 * v
        x, y = C.se_point(phi, r0a * rr, r0b * rr, 2.0)
        front = max(0.0, -math.cos(phi))                # snap brim: down at the front, up at the back
        z = 4.88 - 0.14 * v * front + 0.06 * v * (1 - front) + off
        return Vector((x, y - 0.02, z))
    brim = C.patch(lambda u, v: brim_pt(u, v, 0.03), lambda u, v: brim_pt(u, v, 0.0), 40, 3, closed_u=True, pole=False,
                   inner="full", name="Brim")
    return [C.spec("Fedora", [crown, brim], color, "Fabric", smooth=50),
            C.spec("FedoraBand", [hb], band, "Fabric", smooth=50)]


def build_detective(arm):
    TAN, TAN_D = "#8A6A44", "#6E5233"
    look = {"skin": "#C48A63", "top": TAN, "pants": "#3B3530", "shoes": "#2B1F17", "sole": "#1E1712",
            "brow": "#2E2118", "brow_tilt": -14.0, "brow_size": (0.22, 0.06, 0.06), "lid_drop": 0.085,
            "mouth_curve": -0.006, "generic": False}
    C.build_body(arm, look)
    # trench coat skirt to the knee (closed, belted), popped collar, epaulettes, belt + buckle
    skirt = C.loft_z([(2.32, 0.7, 0.5, 2.3), (2.0, 0.74, 0.55, 2.3), (1.5, 0.79, 0.6, 2.3), (1.05, 0.84, 0.64, 2.3)],
                     segs=28, cap0=False, cap1=False, name="CoatSkirt")
    C.part([skirt], "CoatSkirt", TAN, "Fabric", arm=arm, bone="Hips", smooth=50)
    seam = C.tube([Vector((0.03, -0.71, 2.3)), Vector((0.04, -0.78, 1.6)), Vector((0.05, -0.85, 1.07))], [0.016] * 3, sides=5, res=2)
    C.part([seam], "CoatSeam", TAN_D, "Fabric", arm=arm, bone="Hips", smooth=50)
    belt = ring_band(2.22, 2.36, 0.71, 0.51, segs=28, name="CoatBelt")
    C.part([belt], "CoatBelt", TAN_D, "Fabric", arm=arm, bone="Hips", smooth=45)
    C.part([C.rbox((0.22, 0.05, 0.17), loc=(0.0, -0.52, 2.29), bevel=0.02, seg=1)], "CoatBuckle", "#3B2A1A", arm=arm,
           bone="Hips", smooth=30)
    pop = []
    for s in (1, -1):
        pts = [(0.0, 0.0), (s * 0.3, 0.06), (s * 0.12, -0.36)]
        o = ns.profile_slab(pts, 0.035, bevel=0.01, segments=1)
        ns.apply_all(o)
        C.xform(o, Matrix.Translation((s * 0.06, -0.28, 3.72)) @ Matrix.Rotation(math.radians(105), 4, "X"))
        pop.append(o)
    C.part(pop, "PoppedCollar", TAN_D, "Fabric", arm=arm, bone="Torso", smooth=40)
    eps = [C.rbox((0.42, 0.2, 0.045), loc=(s * 0.6, 0.0, 3.5), rot=(0, s * 17, 0), bevel=0.015, seg=1) for s in (1, -1)]
    C.part(eps, "Epaulettes", TAN_D, "Fabric", arm=arm, bone="Torso", smooth=40)
    buttons([(s * 0.2, z) for s in (1, -1) for z in (2.62, 2.95)], "#3B2A1A", arm, r=0.04)
    C.place_accessory(C.strip_roles(C.acc_hair_short(color="#2E2118")), arm=arm, bone="Head")
    C.place_accessory(fedora(), arm=arm, bone="Head")


def build_bouncer(arm):
    look = {"skin": "#5C3A28", "top": "#2B2B30", "pants": "#1E1F22", "shoes": "#141518", "sole": "#141518",
            "brow": "#160F0B", "brow_tilt": -14.0, "brow_size": (0.23, 0.07, 0.07), "lid_drop": 0.06,
            "mouth_curve": -0.01, "generic": False, "sleeve": "short"}
    C.build_body(arm, look)
    # a heavy silver chain round the neck
    links = []
    for k in range(18):
        a = math.radians(-80 + 160 * k / 17)
        p = Vector((0.33 * math.sin(a), -0.27 * math.cos(a) - 0.02, 3.55 - 0.14 * math.cos(a) ** 2))
        links.append(ns.torus(0.035, 0.012, loc=tuple(p), major_segs=8, minor_segs=4))
    C.part(links, "Chain", "#D7DCE2", "Metal", arm=arm, bone="Torso", smooth=40)
    # STAFF print: a white block on the chest
    sp = chest_pt(0.0, 3.05, 0.065)
    C.part([C.rbox((0.58, 0.02, 0.15), loc=tuple(sp), bevel=0.0, seg=1)], "StaffPrint", WHITE, arm=arm, bone="Torso", smooth=30)
    C.place_accessory(C.strip_roles(C.acc_face_beard(color="#1A1412")), arm=arm, bone="Head")
    sg = C.acc_face_glasses(frame="#111111", lens="#15161C", round_=False, w=0.36, h=0.2)
    for s_ in sg:
        if s_["name"] == "Lens":
            s_["transparency"] = 0.1
    C.place_accessory(sg, arm=arm, bone="Head", prefix="Shades")
    # earpiece and its coiled wire down into the collar
    ep = C.head_pt(-math.pi / 2, 1.75, 0.05)
    C.part([ns.sphere(0.06, loc=tuple(ep), segs=8, rings=5)], "Earpiece", "#1E1F22", arm=arm, bone="Head", smooth=40)
    coil = []
    for i in range(48):
        t = i / 47
        a = t * 2 * math.pi * 7
        base = ep.lerp(Vector((-0.4, 0.18, 3.62)), t)
        coil.append(base + Vector((0.025 * math.cos(a), 0.025 * math.sin(a), 0)))
    C.part([C.tube(coil, [0.01] * len(coil), sides=4, res=1)], "EarWire", "#D9E6EE", arm=arm, bone="Head", smooth=40)


def burger_hat():
    """A foam burger hat: bun, lettuce, patty, cheese, bun, with sesame seeds."""
    z0 = 4.95
    bottom = C.ellipsoid((0, -0.02, z0 + 0.06), (0.86, 0.82, 0.14), segs=24, rings=8)
    patty = C.loft_z([(z0 + 0.16, 0.9, 0.86, 2.0), (z0 + 0.32, 0.9, 0.86, 2.0)], segs=24, name="Patty")
    cheese = C.rbox((1.5, 1.5, 0.05), loc=(0, -0.02, z0 + 0.35), rot=(0, 0, 45), bevel=0.01, seg=1)
    lettuce = C.loft_z([(z0 + 0.36, 0.98, 0.94, 2.0), (z0 + 0.42, 0.98, 0.94, 2.0)], segs=24, name="Lettuce")
    for v in lettuce.data.vertices:
        a = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.06 * math.sin(10 * a)
        v.co.x *= k
        v.co.y *= k
    top = C.ellipsoid((0, -0.02, z0 + 0.46), (0.9, 0.86, 0.5), segs=24, rings=12)
    C._bisect_keep(top, Vector((0, 0, z0 + 0.46)), Vector((0, 0, 1)))
    seeds = []
    for k in range(9):
        a = 2 * math.pi * k / 9 + 0.3
        r = 0.45 if k % 2 else 0.62
        p = Vector((r * math.cos(a), -0.02 + r * math.sin(a), 0))
        p.z = z0 + 0.46 + 0.5 * math.sqrt(max(0.0, 1 - (p.x / 0.9) ** 2 - ((p.y + 0.02) / 0.86) ** 2)) + 0.01
        o = ns.sphere(0.05, loc=tuple(p), segs=8, rings=4)
        o.scale = (1.4, 0.8, 0.5)
        seeds.append(o)
    return [C.spec("HatBun", [bottom, top], "#E9A955", "Fabric", smooth=60),
            C.spec("HatPatty", [patty], "#6B3A1E", "Fabric", smooth=50),
            C.spec("HatCheese", [cheese], "#FFD23A", "Fabric", smooth=30),
            C.spec("HatLettuce", [lettuce], "#5CC24B", "Fabric", smooth=50),
            C.spec("HatSeeds", seeds, WHITE, smooth=50)]


def build_mascot(arm):
    MUSTARD = "#E8A93A"
    look = {"skin": "#EBB894", "top": MUSTARD, "pants": "#C8302E", "shoes": WHITE, "sole": "#C8302E",
            "brow": "#5A3A22", "brow_tilt": 12.0, "lid_drop": 0.0, "mouth_curve": 0.045, "generic": False,
            "sleeve": "short"}
    C.build_body(arm, look)
    band = ring_band(3.55, 3.68, 0.3, 0.27, n=2.0, segs=20, name="JerseyCollar")
    C.part([band], "JerseyCollar", RED, "Fabric", arm=arm, bone="Torso", smooth=45)
    for s, side in ((1, "L"), (-1, "R")):
        trim = ring_band(2.8, 2.86, 0.272, 0.264, n=2.0, segs=16, name="SleeveTrim")
        ns.apply_all(trim)
        C.xform(trim, C._arm_matrix(s) @ Matrix.Translation((0, 0, -2.8 - 0.49)))
        C.part([trim], "Arm" + side + "_Trim", RED, "Fabric", arm=arm, bone="Arm" + side, smooth=50)
    # the burger crest on the chest
    cz = 3.02
    crest = []
    for dz, w, h, col, name in ((0.16, 0.36, 0.12, "#C97A2C", "CrestBun"), (0.06, 0.4, 0.05, "#4FC04A", "CrestLettuce"),
                                (-0.02, 0.38, 0.07, "#6B3A1E", "CrestPatty"), (-0.12, 0.34, 0.08, "#C97A2C", "CrestBase")):
        p = chest_pt(0.0, cz + dz, 0.07)
        o = C.rbox((w, 0.04, h), loc=tuple(p), bevel=min(0.03, h * 0.4), seg=1)
        crest.append((o, col, name))
    for o, col, name in crest:
        C.part([o], name, col, arm=arm, bone="Torso", smooth=40)
    C.place_accessory(C.strip_roles(C.acc_hair_curly(color="#5A3A22")), arm=arm, bone="Head")
    C.place_accessory(burger_hat(), arm=arm, bone="Head")


OUTFITS = {"exterminator": build_exterminator, "cashier": build_cashier, "food_critic": build_food_critic,
           "detective": build_detective, "bouncer": build_bouncer, "mascot": build_mascot}


def register():
    for cid in NEW:
        if cid not in K.ORDER:
            K.ORDER.append(cid)
    K.TITLES.update(TITLES)
    K.POSES.update(POSES)
    K.PROPS.update(PROPS)
    K.OUTFITS.update(OUTFITS)


register()
