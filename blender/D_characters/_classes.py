"""_classes — the six class characters of the CLASS SHOP (2026-11-04).

Landon: "design distinct characters for each class like in 99 nights" — and they stay in the
shop (the lobby's CLASS SHOP windows and the Classes screen), not on the players' avatars.

Each class is a person on the shared Character_Human kit (same 9-bone rigid rig, proportions
and sockets as the Regulars) with a signature outfit and prop, posed by its own looping
Display clip (anim/ClassCast.lua, written by Character_Class__anim.py):

  trainee         paper soda-jerk hat, grey polo, crooked clip-on tie, TRAINEE badge; waves
                  shyly with the left hand, a mop standing in its yellow bucket in the right
  line_cook       red dotted bandana, an order ticket behind the ear, short-sleeved whites,
                  half apron + towel, a beard; holds out a spatula with a cheeseburger patty
  stock_runner    backwards cap, hi-vis vest with reflective tape over a navy tee, work
                  gloves, cargo pockets, lime soles; a STACKHOUSE crate in both hands, bouncing
  security_guard  peaked cap, navy shirt with badge, epaulettes and a shoulder radio, duty
                  belt, moustache, a stern look; sweeps a big flashlight (with its beam)
  night_manager   bun, glasses and a headset, pale-blue shirt, long red tie, ID badge; holds
                  the keys up high ("Closing Time!"), a clipboard in the other hand
  head_chef       tall pleated toque, double-breasted whites, red neckerchief, big grey
                  moustache and rosy cheeks; presents the perfect stack on a plate, a golden
                  ladle raised in the other hand

Rig: the models export with meta.animRig = "ClassCast" (Studio sets Rig = "ClassCast") and
meta.displayClip = "Display_<id>" (play it as AnimState). Props held in a hand are modelled
where they belong in the Display pose (frame 0) and bound to that hand while the rig is
posed, so the REST-pose export carries them in hand space: without the clip playing they
float, so always play the Display clip.
"""
from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
bpy = C.bpy
Vector = C.Vector
Matrix = C.Matrix
D = C.D2R

ORDER = ["trainee", "line_cook", "stock_runner", "security_guard", "night_manager", "head_chef"]
TITLES = {"trainee": "Trainee", "line_cook": "Line Cook", "stock_runner": "Stock Runner",
          "security_guard": "Security Guard", "night_manager": "Night Manager", "head_chef": "Head Chef"}
RIG = "ClassCast"
END = 120          # every Display clip: 4 s loop at 30 fps

RED = "#C8302E"
WHITE = "#F6F3EC"
BRAND = C.BRAND
GOLD = C.GOLD
CHROME = C.CHROME
INK = "#1E1F22"


# --------------------------------------------------------------------------------------
# small geometry helpers
# --------------------------------------------------------------------------------------

def basis(z, y_hint):
    """Orthonormal frame with local Z = z and local Y as close to y_hint as possible."""
    z = Vector(z).normalized()
    y = Vector(y_hint)
    y = (y - z * y.dot(z)).normalized()
    x = y.cross(z)
    return x, y, z


def place(objs, origin, z, y_hint):
    """Move objects modelled about the origin (prop axis = local Z) into the world."""
    x, y, zz = basis(z, y_hint)
    M = Matrix(((x[0], y[0], zz[0], origin[0]), (x[1], y[1], zz[1], origin[1]),
                (x[2], y[2], zz[2], origin[2]), (0, 0, 0, 1)))
    for o in objs:
        ns.apply_all(o)
        C.xform(o, M)
    return objs


def zcyl(r, z0, z1, verts=12, bevel=0.0, x=0.0, y=0.0, name="Cyl"):
    """Cylinder along local Z from z0 to z1."""
    return ns.cyl(r, z1 - z0, loc=(x, y, (z0 + z1) / 2), verts=verts, bevel=bevel, name=name)


def chest_pt(x, z, infl):
    """Point on the shirt front at height z, x studs across (the torso surface + infl)."""
    t = C.gt(z)
    zz, a, b, n, cy = C.torso_frame(t, C.GARMENT)
    phi = math.asin(max(-0.98, min(0.98, x / max(a, 0.2))))
    return C.torso_pt(phi, t, infl, C.GARMENT)


def chest_panel(z0, z1, half_w, infl, thick, centre_x=None, nu=4, nv=8, name="Panel"):
    """Narrow panel lying on the shirt front from z0 (bottom) to z1 (top); half_w(z) and
    centre_x(z) in studs. Used for ties."""
    cx = centre_x or (lambda z: 0.0)

    def pt(u, v, off):
        z = z0 + (z1 - z0) * v
        x = cx(z) + (2 * u - 1) * half_w(z)
        return chest_pt(x, z, infl + off)
    return C.patch(lambda u, v: pt(u, v, thick), lambda u, v: pt(u, v, 0.0), nu, nv, closed_u=False,
                   pole=False, inner="full", centre=Vector((0, 0, 2.9)), name=name)


def collar_flaps(color, arm, name="Collar", spread=0.19, drop=0.22):
    """Two pointed shirt-collar flaps lying on the shoulders at the neck (Walt's collar)."""
    flaps = []
    for s in (1, -1):
        pts = [(0.0, 0.0), (s * spread, 0.02), (s * 0.05, -drop)]
        o = ns.profile_slab(pts, 0.03, bevel=0.01, segments=1)
        ns.apply_all(o)
        C.xform(o, Matrix.Translation((s * 0.05, -0.3, 3.63)) @ Matrix.Rotation(math.radians(60), 4, "X"))
        flaps.append(o)
    return C.part(flaps, name, color, "Fabric", arm=arm, bone="Torso", smooth=40)


def buttons(xs_zs, color, arm, r=0.035, infl=0.075, name="Buttons", mat="SmoothPlastic"):
    objs = [ns.sphere(r, loc=tuple(chest_pt(x, z, infl)), segs=8, rings=4) for x, z in xs_zs]
    return C.part(objs, name, color, mat, arm=arm, bone="Torso", smooth=50)


def ring_band(z0, z1, a, b, n=2.4, segs=24, name="Band"):
    return C.loft_z([(z0, a, b, n), (z1, a, b, n)], segs=segs, cap0=False, cap1=False, name=name)


def head_band_tube(phi, psis, infl, r, sides=8, name="Band"):
    pts = [C.head_pt(phi, p, infl) for p in psis]
    return C.tube(pts, [r] * len(pts), sides=sides, res=3, name=name)


def gloves(arm, color, cuff):
    for side, s in C.SIDES:
        hd = C.hand_mesh(s)
        C.part([hd], "Hand" + side, color, "Fabric", arm=arm, bone="Hand" + side, smooth=60)
        c = ns.cyl(0.15, 0.13, loc=(0, 0, 0), verts=12, bevel=0.0)
        ns.apply_all(c)
        C.xform(c, Matrix.Translation(C.wrist(s) + C.arm_dir(s) * 0.03) @ Matrix.Rotation(math.radians(-s * C.ARM_SPLAY), 4, "Y"))
        C.part([c], "Hand" + side + "_Cuff", cuff, "Fabric", arm=arm, bone="Hand" + side, smooth=50)


# --------------------------------------------------------------------------------------
# posing helpers
# --------------------------------------------------------------------------------------

def hold(c, side, f, axis, palm):
    """Hand rotation so the fist's grip (the thumb axis) runs along `axis`, palm facing `palm`."""
    s = 1.0 if side == "L" else -1.0
    a = Vector(axis).normalized()
    p = Vector(palm)
    p = (p - a * p.dot(a)).normalized()
    cw = -a if s > 0 else a
    return c.orient_hand(side, f, p.cross(cw), p)


def hold_min(c, side, f, axis, arm_d):
    """Grip along `axis` with the least wrist bend for an arm pointing along arm_d."""
    s = 1.0 if side == "L" else -1.0
    a = Vector(axis).normalized()
    d = Vector(arm_d).normalized()
    long = (d - a * d.dot(a)).normalized()
    palm = a.cross(long) * (1.0 if s < 0 else -1.0)
    return c.orient_hand(side, f, long, palm)


def hand_frame(arm, side):
    """Posed frame of a hand at the current frame: grip centre P, thumb axis A, finger
    axis L (wrist -> fingertips) and palm normal N."""
    s = 1.0 if side == "L" else -1.0
    pb = arm.pose.bones["Hand" + side]
    Dm = arm.matrix_world @ pb.matrix @ arm.data.bones["Hand" + side].matrix_local.inverted()
    long_r = C.arm_dir(s)
    grip_r = C.wrist(s) + long_r * 0.25 + Vector((-s * 0.03, 0, 0))
    R = Dm.to_3x3()
    return (Dm @ grip_r, (R @ Vector((0, -1, 0))).normalized(), (R @ long_r).normalized(),
            (R @ Vector((-s, 0, 0))).normalized())


def breathe(c, pitch=1.2, sway=0.6, base=(0.0, 0.0, 0.0)):
    for f, p, r in ((0, 0, 0), (30, -pitch, sway), (60, 0, 0), (90, -pitch, -sway), (END, 0, 0)):
        c.k("Torso", f, (base[0] + p, base[1] + r, base[2]))


def rot_z(deg, v):
    return Matrix.Rotation(math.radians(deg), 3, "Z") @ Vector(v)


# --------------------------------------------------------------------------------------
# Display poses (frame 0 is the pose the props are modelled in)
# --------------------------------------------------------------------------------------

def pose_trainee(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=1.0, base=(1.5, 0, 4))
    for f, rot in ((0, (3, 9, 10)), (20, (2, 11, 13)), (40, (3, 9, 10)), (70, (4, 6, 4)), (95, (2, 8, 8)), (END, (3, 9, 10))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for f in (0, 60, END):
        c.k("ArmR", f, c.aim_arm("R", f, direction=(-0.36, -0.52, -0.78)))
    for f, d in ((0, (0.8, -0.26, 0.55)), (20, (0.8, -0.24, 0.58)), (40, (0.8, -0.26, 0.55)), (60, (0.82, -0.2, 0.53)), (END, (0.8, -0.26, 0.55))):
        c.k("ArmL", f, c.aim_arm("L", f, direction=d))
    c.commit(["ArmR", "ArmL"])
    for f in (0, 60, END):
        c.k("HandR", f, hold(c, "R", f, axis=(0.02, 0.06, 1.0), palm=(0.9, -0.43, 0.0)))
    # a shy wave: fingers up, palm to the front, rocking side to side (then a rest)
    for f, tilt in ((0, 0), (7, 1), (14, -1), (21, 1), (28, -1), (36, 0), (END, 0)):
        long = Vector((0.2 * tilt + 0.12, -0.12, 1.0)).normalized()
        c.k("HandL", f, c.orient_hand("L", f, long, Vector((0.05, -1.0, 0.0))))


def pose_line_cook(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=1.0, base=(-1.5, 0, -8))
    for f, rot in ((0, (-3, -4, -12)), (40, (-2, -2, -16)), (80, (-4, -5, -8)), (END, (-3, -4, -12))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for f, d in ((0, (-0.42, -0.78, -0.42)), (30, (-0.42, -0.8, -0.37)), (60, (-0.42, -0.78, -0.42)),
                 (90, (-0.42, -0.8, -0.37)), (END, (-0.42, -0.78, -0.42))):
        c.k("ArmR", f, c.aim_arm("R", f, direction=d))
    for f in (0, 60, END):
        c.k("ArmL", f, c.aim_arm("L", f, direction=(0.3, 0.06, -0.95)))
    c.commit(["ArmR", "ArmL"])
    for f in (0, 30, 60, 90, END):
        c.k("HandR", f, hold(c, "R", f, axis=(-0.2, -0.96, 0.18), palm=(1.0, 0.0, 0.0)))
    for f in (0, END):
        c.k("HandL", f, (-6, 0, 0))


def pose_stock_runner(c):
    # light on its feet: a little bounce, ready to run
    for f in range(0, END + 1, 15):
        z = 0.035 if (f // 15) % 2 == 1 else 0.0
        c.k("Hips", f, (0, 0, 0), loc=(0, 0, z), ease="QUAD", d="EASE_OUT" if z > 0 else "EASE_IN")
    C._static(c, ["LegL", "LegR"])
    breathe(c, pitch=0.8, base=(2.0, 0, 0))
    for f, rot in ((0, (-4, 3, 6)), (30, (-3, 2, 3)), (60, (-4, 3, 6)), (90, (-5, 4, 9)), (END, (-4, 3, 6))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for side, s in C.SIDES:
        for f in (0, END):
            c.k("Arm" + side, f, c.aim_arm(side, f, direction=(-s * 0.15, -0.78, -0.6)))
    c.commit(["ArmL", "ArmR"])
    for side, s in C.SIDES:
        for f in (0, END):
            c.k("Hand" + side, f, c.orient_hand(side, f, Vector((-s * 0.1, -0.72, -0.68)), Vector((-s, 0, 0))))


SWEEP = ((0, 0.0), (40, 14.0), (80, -14.0), (END, 0.0))


def pose_security_guard(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=0.8, base=(-1.0, 0, -4))
    for f, yaw in SWEEP:
        c.k("Head", f, (8, 0, yaw * 0.7 - 4))
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for f, yaw in SWEEP:
        c.k("ArmR", f, c.aim_arm("R", f, direction=rot_z(yaw, (-0.38, -0.56, -0.74))))
    for f in (0, END):
        c.k("ArmL", f, c.aim_arm("L", f, direction=(0.2, 0.02, -0.98)))
    c.commit(["ArmR", "ArmL"])
    for f, yaw in SWEEP:
        c.k("HandR", f, hold_min(c, "R", f, axis=rot_z(yaw, (-0.62, -0.68, -0.38)), arm_d=rot_z(yaw, (-0.38, -0.56, -0.74))))
    for f in (0, END):
        c.k("HandL", f, (-4, 0, 0))


def pose_night_manager(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=1.0, base=(-1.0, 0, -5))
    for f, rot in ((0, (-7, -3, -10)), (30, (-8, -4, -13)), (60, (-6, -2, -8)), (90, (-7, -3, -11)), (END, (-7, -3, -10))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for f, d in ((0, (-0.3, -0.26, 0.92)), (60, (-0.32, -0.24, 0.92)), (END, (-0.3, -0.26, 0.92))):
        c.k("ArmR", f, c.aim_arm("R", f, direction=d))
    for f in (0, END):
        c.k("ArmL", f, c.aim_arm("L", f, direction=(0.26, -0.16, -0.95)))
    c.commit(["ArmR", "ArmL"])
    # the keys jingle: a quick shake of the raised hand, then held still
    for f, w in ((0, 0), (5, 1), (10, -1), (15, 1), (20, -1), (26, 0), (END, 0)):
        palm = Vector((0.25 * w, -1.0, 0.0))
        c.k("HandR", f, c.orient_hand("R", f, Vector((-0.3, -0.26, 0.92)), palm))
    for f in (0, END):
        c.k("HandL", f, hold(c, "L", f, axis=(1.0, 0.0, 0.0), palm=(0.0, -1.0, 0.0)))


def pose_head_chef(c):
    C._static(c, ["Hips", "LegL", "LegR"])
    breathe(c, pitch=1.0, base=(-2.5, 0, 0))
    for f, rot in ((0, (-6, -4, -6)), (40, (-7, -5, -9)), (80, (-5, -3, -4)), (END, (-6, -4, -6))):
        c.k("Head", f, rot)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for f in (0, END):
        c.k("ArmL", f, c.aim_arm("L", f, direction=(0.78, -0.56, 0.22)))
    for f, d in ((0, (-0.66, -0.6, 0.14)), (30, (-0.66, -0.58, 0.22)), (60, (-0.66, -0.6, 0.14)), (END, (-0.66, -0.6, 0.14))):
        c.k("ArmR", f, c.aim_arm("R", f, direction=d))
    c.commit(["ArmR", "ArmL"])
    for f in (0, END):
        c.k("HandL", f, c.orient_hand("L", f, Vector((0.8, -0.58, 0.1)), Vector((0.0, 0.0, 1.0))))
    for f in (0, 30, 60, END):
        c.k("HandR", f, hold(c, "R", f, axis=(-0.04, 0.12, 1.0), palm=(0.72, -0.69, 0.0)))


POSES = {"trainee": pose_trainee, "line_cook": pose_line_cook, "stock_runner": pose_stock_runner,
         "security_guard": pose_security_guard, "night_manager": pose_night_manager, "head_chef": pose_head_chef}


def display_clip(arm, cid):
    c = C.Clip(arm, "Display_" + cid, END, loop=True, fps=30)
    POSES[cid](c)
    return c.finish()


# --------------------------------------------------------------------------------------
# props (built in the posed scene at Display frame 0; see build_class)
# --------------------------------------------------------------------------------------

def prop_mop_bucket(arm):
    P, A, L, N = hand_frame(arm, "R")
    down = (P.z - 0.42) / max(A.z, 0.3)
    handle = place([zcyl(0.048, -down, 0.62, verts=10)], P, A, N)
    knob = place([ns.sphere(0.07, loc=(0, 0, 0.66), segs=10, rings=6)], P, A, N)
    C.part(handle + knob, "MopHandle", "#C89B5E", "Wood", arm=arm, bone="HandR", smooth=50)
    Q = P - A * down
    clamp = ns.cyl(0.11, 0.12, loc=(Q.x, Q.y, Q.z + 0.02), verts=12, bevel=0.02)
    strands = []
    rnd = random.Random(7)
    for k in range(12):
        a = 2 * math.pi * k / 12 + rnd.uniform(-0.15, 0.15)
        p0 = Vector((Q.x + 0.06 * math.cos(a), Q.y + 0.06 * math.sin(a), Q.z - 0.02))
        p1 = Vector((Q.x + 0.2 * math.cos(a), Q.y + 0.2 * math.sin(a), Q.z - 0.22))
        strands.append(C.tube([p0, p1], [0.035, 0.03], sides=6, res=1))
    C.part([clamp], "MopClamp", "#3D6FB6", arm=arm, bone="HandR", smooth=40)
    C.part(strands, "MopHead", "#D9D4C8", "Fabric", arm=arm, bone="HandR", smooth=60)
    # the yellow mop bucket the mop stands in (on the floor: bound to the hips)
    bx, by = Q.x, Q.y
    body = C.loft_z([(0.06, 0.36, 0.36, 2.0, bx, by), (0.62, 0.42, 0.42, 2.0, bx, by)], segs=20, name="Bucket")
    water = ns.cyl(0.39, 0.02, loc=(bx, by, 0.55), verts=20, bevel=0.0)
    rim = ns.torus(0.42, 0.035, loc=(bx, by, 0.62), major_segs=20, minor_segs=5)
    wheels = [ns.cyl(0.07, 0.06, loc=(bx + 0.27 * math.cos(a), by + 0.27 * math.sin(a), 0.07), rot=(0, 90, 0), verts=10, bevel=0.0)
              for a in (0.6, 2.2, 3.8, 5.4)]
    wring = C.rbox((0.5, 0.24, 0.3), loc=(bx, by + 0.3, 0.78), bevel=0.04, seg=1)
    whandle = C.tube([Vector((bx + 0.2, by + 0.32, 0.92)), Vector((bx + 0.24, by + 0.6, 1.3)), Vector((bx + 0.22, by + 0.62, 1.42))],
                     [0.035] * 3, sides=6, res=3)
    C.part([body, rim], "Bucket", "#F2C230", arm=arm, bone="Hips", smooth=45)
    C.part([water], "BucketWater", "#6E8592", arm=arm, bone="Hips", smooth=30)
    C.part(wheels + [wring, whandle], "Wringer", "#3A3D44", arm=arm, bone="Hips", smooth=40)


def prop_spatula(arm):
    P, A, L, N = hand_frame(arm, "R")
    # local frame: Z = the grip axis (forward), Y = finger axis (down) -> blade lies flat
    handle = place([zcyl(0.046, -0.22, 0.42, verts=10, bevel=0.01)], P, A, L)
    ferrule = place([zcyl(0.052, 0.42, 0.5, verts=10)], P, A, L)
    neck = place([C.rbox((0.06, 0.02, 0.14), loc=(0, -0.01, 0.56), rot=(-12, 0, 0), bevel=0.005, seg=1)], P, A, L)
    blade = place([C.rbox((0.48, 0.024, 0.52), loc=(0, -0.03, 0.88), bevel=0.014, seg=1)], P, A, L)
    patty = place([ns.cyl(0.21, 0.1, loc=(0, -0.1, 0.9), rot=(90, 0, 0), verts=16, bevel=0.03)], P, A, L)
    cheese = place([C.rbox((0.36, 0.018, 0.36), loc=(0, -0.158, 0.9), rot=(0, 45, 0), bevel=0.004, seg=1)], P, A, L)
    C.part(handle, "SpatulaHandle", INK, arm=arm, bone="HandR", smooth=50)
    C.part(ferrule + neck + blade, "SpatulaBlade", CHROME, "Metal", arm=arm, bone="HandR", smooth=30)
    C.part(patty, "Patty", "#6B3A22", arm=arm, bone="HandR", smooth=55)
    C.part(cheese, "Cheese", "#F2B33D", arm=arm, bone="HandR", smooth=30)


def prop_crate(arm):
    PL, _, _, _ = hand_frame(arm, "L")
    PR, _, _, _ = hand_frame(arm, "R")
    ctr = (PL + PR) / 2 + Vector((0, -0.06, 0.02))
    w = max(0.8, (PL - PR).length - 0.3)
    box = C.rbox((w, 0.92, 0.78), loc=tuple(ctr), bevel=0.05, seg=1)
    tape = C.rbox((w + 0.01, 0.2, 0.012), loc=(ctr.x, ctr.y, ctr.z + 0.39), bevel=0.0, seg=1)
    tape2 = C.rbox((w + 0.01, 0.012, 0.2), loc=(ctr.x, ctr.y - 0.46, ctr.z + 0.29), bevel=0.0, seg=1)
    label = C.rbox((w * 0.62, 0.014, 0.3), loc=(ctr.x, ctr.y - 0.463, ctr.z - 0.04), bevel=0.0, seg=1)
    arrows = []
    for dx in (-0.18, 0.18):
        pts = [(-0.05, 0.0), (0.05, 0.0), (0.05, 0.08), (0.1, 0.08), (0.0, 0.17), (-0.1, 0.08), (-0.05, 0.08)]
        o = ns.profile_slab(pts, 0.012, bevel=0.0, segments=1)
        ns.apply_all(o)
        C.xform(o, Matrix.Translation((ctr.x + w * 0.5 + 0.006, ctr.y + dx, ctr.z - 0.12)) @ Matrix.Rotation(math.radians(90), 4, "Y") @ Matrix.Rotation(math.radians(-90), 4, "Z"))
        arrows.append(o)
    C.part([box], "Crate", "#C49A6C", arm=arm, bone="Torso", smooth=30)
    C.part([tape, tape2], "CrateTape", "#E3CDA0", arm=arm, bone="Torso", smooth=30)
    C.part([label], "CrateLabel", BRAND, arm=arm, bone="Torso", role="crate_label", smooth=30)
    C.part(arrows, "CrateArrows", INK, arm=arm, bone="Torso", smooth=30)


def prop_flashlight(arm):
    P, A, L, N = hand_frame(arm, "R")
    body = place([zcyl(0.092, -0.4, 0.34, verts=14, bevel=0.01)], P, A, L)
    head = place([C.loft_z([(0.34, 0.1, 0.1, 2.0), (0.44, 0.15, 0.15, 2.0), (0.66, 0.16, 0.16, 2.0)], segs=16)], P, A, L)
    rings = place([zcyl(0.099, z, z + 0.035, verts=14) for z in (-0.34, -0.25, 0.24)], P, A, L)
    tail = place([zcyl(0.1, -0.47, -0.4, verts=14, bevel=0.015)], P, A, L)
    lens = place([zcyl(0.135, 0.655, 0.68, verts=16)], P, A, L)
    C.part(body + head + tail, "Flashlight", "#2B2E35", arm=arm, bone="HandR", smooth=40)
    C.part(rings, "FlashlightGrip", "#596070", arm=arm, bone="HandR", smooth=40)
    C.part(lens, "FlashlightLens", "#FFF1C8", "Neon", arm=arm, bone="HandR", role="lens", smooth=30)


def prop_keys_clipboard(arm):
    P, A, L, N = hand_frame(arm, "R")
    ring_c = P + L * 0.5 + N * 0.2
    ring = ns.torus(0.14, 0.028, loc=tuple(ring_c), major_segs=14, minor_segs=5)
    ns.apply_all(ring)
    C.xform(ring, Matrix.Translation(ring_c) @ Matrix.Rotation(math.radians(90), 4, "X") @ Matrix.Translation(-ring_c))
    keys = []
    brass = []
    for i, (dx, ln, rot) in enumerate(((-0.08, 0.4, 12), (0.0, 0.5, -4), (0.08, 0.36, -18), (0.04, 0.3, 26))):
        top = ring_c + Vector((dx, -0.025 * i, -0.13))
        shaft = C.rbox((0.07, 0.02, ln), loc=(top.x, top.y, top.z - ln / 2), rot=(0, rot, 0), bevel=0.008, seg=1)
        bow = ns.cyl(0.07, 0.025, loc=(top.x, top.y, top.z - 0.02), rot=(90, 0, 0), verts=10, bevel=0.0)
        (brass if i % 2 else keys).extend([shaft, bow])
    tag = C.rbox((0.16, 0.025, 0.22), loc=(ring_c.x - 0.16, ring_c.y - 0.04, ring_c.z - 0.26), rot=(0, -14, 0), bevel=0.012, seg=1)
    C.part([ring] + keys, "Keys", "#D7DCE2", arm=arm, bone="HandR", smooth=40)
    C.part(brass, "BrassKeys", "#E2B64A", arm=arm, bone="HandR", smooth=40)
    C.part([tag], "KeyTag", RED, arm=arm, bone="HandR", smooth=30)
    # the clipboard, held by its clip at the left side, facing front
    P, A, L, N = hand_frame(arm, "L")
    down = Vector((0, 0, -1))
    ctr = P + down * 0.5 + Vector((0, -0.04, 0))
    fx = A.copy()
    fx.z = 0
    fx.normalize()
    ang = math.atan2(fx.y, fx.x)
    M = Matrix.Translation(ctr) @ Matrix.Rotation(ang, 4, "Z")
    board = C.rbox((0.64, 0.035, 0.86), bevel=0.02, seg=1)
    paper = C.rbox((0.56, 0.008, 0.74), loc=(0, -0.022, -0.03), bevel=0.0, seg=1)
    clip = C.rbox((0.26, 0.05, 0.1), loc=(0, -0.02, 0.4), bevel=0.015, seg=1)
    lines = [C.rbox((0.4 if k % 2 else 0.32, 0.006, 0.025), loc=(-0.04 + (0.04 if k % 2 else 0.0), -0.028, 0.2 - 0.12 * k), bevel=0.0, seg=1)
             for k in range(5)]
    check = C.rbox((0.06, 0.006, 0.06), loc=(-0.22, -0.028, 0.2), bevel=0.0, seg=1)
    for o in [board, paper, clip, check] + lines:
        ns.apply_all(o)
        C.xform(o, M)
    C.part([board], "Clipboard", "#8A5A33", "Wood", arm=arm, bone="HandL", smooth=30)
    C.part([paper], "ClipPaper", "#F7F5EF", arm=arm, bone="HandL", smooth=30)
    C.part([clip], "Clip", CHROME, "Metal", arm=arm, bone="HandL", smooth=30)
    C.part(lines, "ClipLines", "#3A4A66", arm=arm, bone="HandL", smooth=30)
    C.part([check], "ClipCheck", RED, arm=arm, bone="HandL", smooth=30)


def prop_plate_ladle(arm):
    P, A, L, N = hand_frame(arm, "L")
    up = Vector((0, 0, 1))
    pc = P + up * 0.2 + L * 0.06
    plate = ns.cyl(0.5, 0.05, loc=tuple(pc), verts=24, bevel=0.015)
    rim = ns.torus(0.47, 0.03, loc=(pc.x, pc.y, pc.z + 0.03), major_segs=24, minor_segs=5)
    C.part([plate, rim], "Plate", "#F7F5EF", arm=arm, bone="HandL", smooth=40)
    # the perfect stack: toast, lettuce, tomato, cheese, ham, toast, a toothpick flag
    R = Matrix.Translation(pc) @ Matrix.Rotation(math.radians(18), 4, "Z")
    z = 0.05

    def lay(o):
        ns.apply_all(o)
        C.xform(o, R)
        return o
    bread = [lay(C.rbox((0.62, 0.62, 0.12), loc=(0, 0, z + 0.06), bevel=0.05, seg=2))]
    lettuce = [lay(C.ellipsoid((0, 0, z + 0.14), (0.4, 0.38, 0.035), segs=12, rings=4))]
    tomato = [lay(ns.cyl(0.13, 0.04, loc=(dx, dy, z + 0.18), verts=12, bevel=0.0)) for dx, dy in ((-0.13, -0.06), (0.14, 0.08))]
    cheese = [lay(C.rbox((0.62, 0.62, 0.025), loc=(0, 0, z + 0.215), rot=(0, 0, 45), bevel=0.004, seg=1))]
    ham = [lay(C.ellipsoid((0, 0, z + 0.25), (0.31, 0.3, 0.035), segs=12, rings=4))]
    top = [lay(C.rbox((0.62, 0.62, 0.12), loc=(0, 0, z + 0.33), bevel=0.05, seg=2))]
    pick = [lay(ns.cyl(0.012, 0.42, loc=(0.05, 0.02, z + 0.5), verts=6, bevel=0.0))]
    flag = [lay(C.rbox((0.012, 0.16, 0.1), loc=(0.05, 0.1, z + 0.66), bevel=0.0, seg=1))]
    C.part(bread + top, "Toast", "#D9A35B", arm=arm, bone="HandL", smooth=40)
    C.part(lettuce, "Lettuce", "#6DBE45", arm=arm, bone="HandL", smooth=50)
    C.part(tomato, "Tomato", "#D8433A", arm=arm, bone="HandL", smooth=40)
    C.part(cheese, "StackCheese", "#F2C14E", arm=arm, bone="HandL", smooth=30)
    C.part(ham, "Ham", "#E8A0A0", arm=arm, bone="HandL", smooth=50)
    C.part(pick, "Toothpick", "#E3CDA0", "Wood", arm=arm, bone="HandL", smooth=40)
    C.part(flag, "Flag", RED, arm=arm, bone="HandL", smooth=30)
    # the golden ladle, raised
    P, A, L, N = hand_frame(arm, "R")
    hp = [P - A * 0.3, P + A * 0.3, P + A * 0.78]
    handle = C.tube(hp, [0.038, 0.038, 0.034], sides=8, res=2)
    bc = P + A * 0.94
    bowl = C.ellipsoid(bc, (0.2, 0.2, 0.13), segs=14, rings=8)
    hook = ns.sphere(0.055, loc=tuple(P - A * 0.33), segs=8, rings=4)
    C.part([handle, bowl, hook], "Ladle", "#E2B64A", "Metal", arm=arm, bone="HandR", smooth=40)


PROPS = {"trainee": prop_mop_bucket, "line_cook": prop_spatula, "stock_runner": prop_crate,
         "security_guard": prop_flashlight, "night_manager": prop_keys_clipboard, "head_chef": prop_plate_ladle}


# --------------------------------------------------------------------------------------
# outfits (rest pose)
# --------------------------------------------------------------------------------------

def paper_hat(color=WHITE, stripe=RED, tilt=5.0):
    """Soda-jerk paper hat: a folded boat round the crown (the band hugs the hair just above
    the brows), its two sides rising to a ridge, flat triangular ends, a red band, a logo."""
    NY, L, ZB = 15, 0.62, 4.74

    def section(y, inset):
        u = min(1.0, abs(y) / L)
        a = 0.645 * (1 - u * u) ** 0.3 - inset
        top = 5.36 - 0.06 * u * u - inset * 1.6
        h = top - ZB
        pts = [(-1.0, 0.0), (-0.72, 0.42), (-0.4, 0.8), (0.0, 1.0), (0.4, 0.8), (0.72, 0.42), (1.0, 0.0)]
        return [Vector((x * a, y, ZB + inset * 0.3 + k * h)) for x, k in pts]
    bm = C.bmesh.new()
    rings = []
    for i in range(NY):
        y = -L + 2 * L * i / (NY - 1)
        rings.append([bm.verts.new(p) for p in section(y, 0.0) + list(reversed(section(y, 0.035)))])
    n = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(n):
            k = (j + 1) % n
            bm.faces.new((r0[j], r0[k], r1[k], r1[j]))
    for row in (rings[0], rings[-1]):
        bm.faces.new(row)
    C.bmesh.ops.triangulate(bm, faces=bm.faces[:])
    C.bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    hat = ns.from_bmesh(bm, "PaperHat")
    strips = []
    for s in (1, -1):
        bm2 = C.bmesh.new()
        row = []
        for i in range(NY):
            y = -L * 0.97 + 2 * L * 0.97 * i / (NY - 1)
            sec = section(y, -0.01)
            p0, p1 = (sec[-1], sec[-2]) if s > 0 else (sec[0], sec[1])
            row.append((bm2.verts.new(p0), bm2.verts.new(p0.lerp(p1, 0.3))))
        for (a0, b0), (a1, b1) in zip(row, row[1:]):
            bm2.faces.new((a0, a1, b1, b0))
        st = ns.from_bmesh(bm2, "Stripe")
        sol = st.modifiers.new("T", "SOLIDIFY")
        sol.thickness = 0.014
        strips.append(st)
    mid = section(0.0, -0.012)
    lp = mid[-2].lerp(mid[-3], 0.5)
    logo = C.rbox((0.014, 0.15, 0.15), loc=tuple(lp), rot=(45, 0, 0), bevel=0.0, seg=1)
    ns.apply_all(logo)
    C.xform(logo, Matrix.Translation(lp) @ Matrix.Rotation(math.radians(-38), 4, "Y") @ Matrix.Translation(-lp))
    c = Vector((0.0, 0.0, 5.0))
    T = Matrix.Translation(c + Vector((0.02, -0.02, 0.0))) @ Matrix.Rotation(math.radians(tilt), 4, "Y") @ Matrix.Translation(-c)
    for o in [hat, logo] + strips:
        ns.apply_all(o)
        C.xform(o, T)
    return [C.spec("PaperHat", [hat], color, "Fabric", smooth=35),
            C.spec("PaperHatStripe", strips + [logo], stripe, smooth=30)]


def toque(color=WHITE):
    """Tall pleated chef's toque: a band round the head, a flared pleated column, a puff."""
    segs = 48
    bm = C.bmesh.new()
    rings = []
    spec_r = [(4.58, 0.68, 0.64, 0.0), (4.9, 0.68, 0.64, 0.0), (4.93, 0.69, 0.65, 0.03),
              (5.3, 0.72, 0.68, 0.035), (5.72, 0.76, 0.72, 0.035)]
    for z, a, b, pleat in spec_r:
        row = []
        for i in range(segs):
            ph = 2 * math.pi * i / segs
            k = 1 + pleat * math.cos(16 * ph)
            x, y = C.se_point(ph, a * k, b * k, 2.2)
            row.append(bm.verts.new((x, y - 0.02, z)))
        rings.append(row)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    C.bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    col = ns.from_bmesh(bm, "Toque")
    sol = col.modifiers.new("T", "SOLIDIFY")
    sol.thickness = 0.03
    puff = C.ellipsoid((0, -0.02, 5.78), (0.84, 0.8, 0.36), segs=24, rings=12)
    seam = ring_band(4.88, 4.94, 0.695, 0.655, n=2.2, segs=48, name="Seam")
    return [C.spec("Toque", [col, puff], color, "Fabric", smooth=50),
            C.spec("ToqueSeam", [seam], "#E4E0D6", "Fabric", smooth=50)]


def bandana(color=RED, dots="#F6F3EC"):
    edge = lambda phi: C.hairline(phi, front=56, side=84, back=104, ear_notch=8)
    cap = C.hair_cap(edge, lambda phi, v: 0.035, infl=0.03, nu=36, name="Bandana")
    knot_c = C.head_pt(math.pi, 1.8, 0.09)
    knot = C.ellipsoid(knot_c, (0.13, 0.08, 0.1), segs=10, rings=6)
    tails = [C.tube([knot_c, knot_c + Vector((s * 0.09, 0.08, -0.16)), knot_c + Vector((s * 0.12, 0.1, -0.34))],
                    [0.05, 0.045, 0.03], sides=6, res=2) for s in (1, -1)]
    rnd = random.Random(5)
    ds = []
    for _ in range(18):
        phi = rnd.uniform(-math.pi, math.pi)
        psi = rnd.uniform(0.15, edge(phi) - 0.12)
        p = C.head_pt(phi, psi, 0.03 + 0.035 + 0.004)
        n = (p - C.HEAD_C).normalized()
        o = ns.sphere(0.034, loc=tuple(p), segs=8, rings=4)
        o.scale = (1, 1, 0.35)
        ns.apply_all(o)
        q = Vector((0, 0, 1)).rotation_difference(n)
        C.xform(o, Matrix.Translation(p) @ q.to_matrix().to_4x4() @ Matrix.Translation(-p))
        ds.append(o)
    return [C.spec("Bandana", [cap, knot] + tails, color, "Fabric", smooth=55),
            C.spec("BandanaDots", ds, dots, smooth=50)]


def headset(color=INK):
    band = head_band_tube(math.pi / 2, [1.75, 1.3, 0.9, 0.5, 0.15], 0.15, 0.03, name="HeadBand")
    band2 = head_band_tube(-math.pi / 2, [1.75, 1.3, 0.9, 0.5, 0.15], 0.15, 0.03, name="HeadBand2")
    top = C.tube([C.head_pt(math.pi / 2, 0.15, 0.15), C.head_pt(0, 0, 0.15), C.head_pt(-math.pi / 2, 0.15, 0.15)],
                 [0.03] * 3, sides=8, res=4)
    cups = [ns.cyl(0.13, 0.08, loc=(s * 0.69, 0.04, 4.33), rot=(0, 90, 0), verts=14, bevel=0.02) for s in (1, -1)]
    boom = C.tube([Vector((-0.72, -0.06, 4.28)), Vector((-0.6, -0.4, 4.12)), Vector((-0.3, -0.66, 4.02))],
                  [0.022, 0.02, 0.02], sides=6, res=3)
    mic = ns.sphere(0.055, loc=(-0.27, -0.68, 4.02), segs=8, rings=5)
    return [C.spec("Headset", [band, band2, top] + cups + [boom, mic], color, smooth=50)]


def build_trainee(arm):
    look = {"skin": "#F2C9A5", "top": "#C9CFD6", "pants": "#C8B48A", "shoes": "#F2F2EE", "sole": "#C9CED3",
            "brow": "#6B4A2E", "brow_tilt": 16.0, "lid_drop": 0.0, "mouth_curve": 0.012, "generic": False,
            "sleeve": "short"}
    C.build_body(arm, look)
    collar_flaps("#C9CFD6", arm, name="PoloCollar")
    plk = chest_panel(3.08, 3.56, lambda z: 0.055, 0.035, 0.012, name="Placket")
    C.part([plk], "Placket", "#AEB5BE", "Fabric", arm=arm, bone="Torso", smooth=40)
    buttons([(0.0, 3.2), (0.0, 3.36)], "#F6F3EC", arm, r=0.028, infl=0.058)
    # the crooked clip-on tie
    tilt = lambda z: 0.05 * (3.45 - z)
    knot = chest_panel(3.36, 3.5, lambda z: 0.07, 0.06, 0.05, centre_x=tilt, name="TieKnot")
    blade = chest_panel(2.86, 3.37, lambda z: 0.05 + 0.06 * C.smoothstep(3.37, 3.1, z) - 0.09 * C.smoothstep(2.98, 2.86, z),
                        0.06, 0.025, centre_x=tilt, nv=10, name="TieBlade")
    C.part([knot, blade], "Tie", RED, "Fabric", arm=arm, bone="Torso", smooth=40)
    # TRAINEE badge on the left chest (role badge: the lobby may print the word on it)
    bc = chest_pt(0.33, 3.12, 0.075)
    badge = C.rbox((0.38, 0.03, 0.2), loc=tuple(bc), rot=(4, 0, 24), bevel=0.02, seg=1)
    C.part([badge], "Badge", "#F07B2A", arm=arm, bone="Torso", role="badge", smooth=30)
    bar = C.rbox((0.28, 0.012, 0.07), loc=tuple(bc + Vector((0.006, -0.018, 0.0))), rot=(4, 0, 24), bevel=0.0, seg=1)
    C.part([bar], "BadgeBar", "#FFFFFF", arm=arm, bone="Torso", smooth=30)
    C.place_accessory(C.strip_roles(C.acc_hair_short(color="#6B4A2E")), arm=arm, bone="Head")
    C.place_accessory(paper_hat(), arm=arm, bone="Head")


def build_line_cook(arm):
    look = {"skin": "#8D5A3B", "top": "#F4F1EA", "pants": "#2B2D33", "shoes": INK, "sole": "#3A3D44",
            "brow": "#211B18", "brow_tilt": -5.0, "lid_drop": 0.035, "mouth_curve": 0.028, "generic": False,
            "sleeve": "short"}
    C.build_body(arm, look)
    band = ring_band(3.56, 3.7, 0.3, 0.27, n=2.0, segs=20, name="CookCollar")
    C.part([band], "CookCollar", "#F4F1EA", "Fabric", arm=arm, bone="Torso", smooth=45)
    buttons([(0.2, z) for z in (2.55, 2.85, 3.15, 3.42)], INK, arm, r=0.032)
    # half apron + waist tie, a striped towel tucked at the left hip
    def apron(u, v, off):
        phi = (-72 + 144 * u) * D
        z = 2.3 - 1.06 * v
        a = 0.68 + 0.05 * v
        b = 0.48 + 0.08 * v
        x, y = C.se_point(phi, a + off, b + off, 2.4)
        return Vector((x, y, z))
    ap = C.patch(lambda u, v: apron(u, v, 0.03), lambda u, v: apron(u, v, 0.0), 14, 6, closed_u=False, pole=False,
                 inner="full", centre=Vector((0, 0, 1.8)), name="Apron")
    tie = ring_band(2.2, 2.32, 0.7, 0.5, segs=24, name="ApronTie")
    bow = [C.ellipsoid((s * 0.12, 0.52, 2.27), (0.12, 0.05, 0.07), segs=8, rings=5, rot=(0, 0, s * 20)) for s in (1, -1)]
    C.part([ap, tie] + bow, "Apron", "#ECE8DE", "Fabric", arm=arm, bone="Hips", smooth=45)
    towel = C.rbox((0.07, 0.3, 0.5), loc=(0.68, -0.12, 1.98), rot=(0, -8, 0), bevel=0.02, seg=1)
    C.part([towel], "Towel", "#E6EEF6", "Fabric", arm=arm, bone="Hips", smooth=40)
    stripes = [C.rbox((0.075, 0.31, 0.04), loc=(0.68, -0.12, z), rot=(0, -8, 0), bevel=0.0, seg=1) for z in (1.86, 2.08)]
    C.part(stripes, "TowelStripes", "#3D6FB6", "Fabric", arm=arm, bone="Hips", smooth=40)
    C.place_accessory(C.strip_roles(C.acc_face_beard(color="#211B18")), arm=arm, bone="Head")
    C.place_accessory(bandana(), arm=arm, bone="Head")
    ticket = C.rbox((0.014, 0.13, 0.3), loc=(-0.66, 0.16, 4.5), rot=(-30, 0, 4), bevel=0.0, seg=1)
    tline = C.rbox((0.016, 0.131, 0.03), loc=(-0.66, 0.2, 4.6), rot=(-30, 0, 4), bevel=0.0, seg=1)
    C.part([ticket], "Ticket", "#FBF8EE", arm=arm, bone="Head", smooth=30)
    C.part([tline], "TicketLine", RED, arm=arm, bone="Head", smooth=30)


def build_stock_runner(arm):
    look = {"skin": "#C98B62", "top": "#273043", "pants": "#5A5E52", "shoes": "#2B2D33", "sole": "#C8E83A",
            "brow": "#211B18", "brow_tilt": 4.0, "lid_drop": 0.0, "mouth_curve": 0.03, "generic": False,
            "sleeve": "short", "skip": ("HandL", "HandR")}
    C.build_body(arm, look)
    t0, t1 = C.gt(2.08), C.gt(3.555)
    vest = C.garment(t0, t1, 0.03, 0.04, open_front=lambda t: 3 * D, nu=28, nv=8, name="HiVis")
    C.part([vest], "HiVis", "#C8E83A", "Fabric", arm=arm, bone="Torso", smooth=45)
    tape = []
    for z in (2.36, 2.66):
        tape.append(C.garment(C.gt(z - 0.05), C.gt(z + 0.05), 0.072, 0.012, open_front=lambda t: 3 * D, nu=28, nv=2,
                              inner="none", name="TapeH"))
    for a in (34, -34, 146, -146):
        tape.append(C.garment(C.gt(2.72), C.gt(3.5), 0.072, 0.012, phi_range=((a - 5) * D, (a + 5) * D), nu=2, nv=6,
                              inner="none", name="TapeV"))
    C.part(tape, "Reflective", "#E1E6EA", "Foil", arm=arm, bone="Torso", smooth=40)
    zp = [C.torso_pt(0, C.gt(z), 0.075) for z in (2.12, 2.6, 3.1, 3.5)]
    C.part([C.tube(zp, [0.014] * 4, sides=6, res=1)], "Zip", "#3A3D44", "Metal", arm=arm, bone="Torso", smooth=40)
    gloves(arm, "#C9A26B", "#8A6A3E")
    for side, s in C.SIDES:
        pk = C.rbox((0.11, 0.32, 0.34), loc=(s * 0.66, -0.02, 1.25), bevel=0.03, seg=1)
        flap = C.rbox((0.12, 0.33, 0.08), loc=(s * 0.67, -0.02, 1.42), bevel=0.02, seg=1)
        C.part([pk, flap], "Leg" + side + "_Pocket", "#4A4E44", "Fabric", arm=arm, bone="Leg" + side, smooth=40)
    C.place_accessory(C.strip_roles(C.acc_hair_short(color="#211B18")), arm=arm, bone="Head")
    C.place_accessory(C.acc_hat_trucker(color=BRAND, mesh="#D9481F", patch_col="#FFFFFF", backwards=True), arm=arm, bone="Head")


def build_security_guard(arm):
    look = {"skin": "#E3AC85", "top": "#1B2A4A", "pants": "#23262E", "shoes": "#141518", "sole": "#141518",
            "brow": "#3D2A1E", "brow_tilt": -10.0, "brow_size": (0.21, 0.06, 0.06), "lid_drop": 0.075,
            "mouth_curve": -0.004, "generic": False}
    C.build_body(arm, look)
    C.place_accessory(C.strip_roles(C.acc_top_badge(color="#1B2A4A", gold=GOLD, bar=GOLD)), arm=arm, bone="Torso")
    collar_flaps("#1B2A4A", arm, name="ShirtCollar")
    eps = []
    for s in (1, -1):
        e = C.rbox((0.46, 0.22, 0.045), loc=(s * 0.6, 0.0, 3.5), rot=(0, s * 17, 0), bevel=0.015, seg=1)
        eps.append(e)
    C.part(eps, "Epaulettes", "#16213A", "Fabric", arm=arm, bone="Torso", smooth=40)
    C.part([ns.sphere(0.035, loc=(s * 0.4, 0.0, 3.6), segs=8, rings=4) for s in (1, -1)], "EpButtons", GOLD, "Metal",
           arm=arm, bone="Torso", smooth=40)
    rc = C.torso_pt(-38 * D, C.gt(3.2), 0.1)
    radio = C.rbox((0.17, 0.1, 0.3), loc=tuple(rc), rot=(4, 0, -36), bevel=0.03, seg=1)
    ant = C.tube([rc + Vector((0.04, 0.01, 0.14)), rc + Vector((0.05, 0.01, 0.42))], [0.02, 0.016], sides=6, res=1)
    C.part([radio, ant], "Radio", "#16171A", arm=arm, bone="Torso", smooth=40)
    C.part([ns.sphere(0.025, loc=tuple(rc + Vector((-0.03, -0.06, 0.1))), segs=6, rings=4)], "RadioLight", "#FF4A3A",
           "Neon", arm=arm, bone="Torso", smooth=40)
    belt = ring_band(2.1, 2.3, 0.665, 0.462, segs=24, name="Belt")
    pouches = [C.rbox((0.16, 0.22, 0.24), loc=(s * 0.66, -0.06, 2.12), rot=(0, 0, s * 8), bevel=0.03, seg=1) for s in (1, -1)]
    C.part([belt] + pouches, "DutyBelt", "#141518", arm=arm, bone="Hips", smooth=40)
    buckle = C.rbox((0.2, 0.04, 0.15), loc=(0, -0.47, 2.2), bevel=0.02, seg=1)
    C.part([buckle], "Buckle", GOLD, "Metal", arm=arm, bone="Hips", smooth=30)
    C.place_accessory(C.strip_roles(C.acc_hair_short(color="#3D2A1E")), arm=arm, bone="Head")
    C.place_accessory(C.strip_roles(C.acc_face_mustache(color="#3D2A1E")), arm=arm, bone="Head")
    C.place_accessory(C.acc_hat_cop(navy="#16213A", black="#111216", gold=GOLD), arm=arm, bone="Head", prefix="Cap")


def build_night_manager(arm):
    look = {"skin": "#6E4530", "top": "#A9C8E8", "pants": "#2E3240", "shoes": "#4A2E1E", "sole": "#2B2520",
            "brow": "#211B18", "brow_tilt": 2.0, "lid_drop": 0.04, "mouth_curve": 0.022, "generic": False}
    C.build_body(arm, look)
    collar_flaps("#A9C8E8", arm, name="ShirtCollar")
    knot = chest_panel(3.4, 3.55, lambda z: 0.075, 0.06, 0.05, name="TieKnot")
    blade = chest_panel(2.42, 3.41, lambda z: 0.06 + 0.07 * C.smoothstep(3.41, 3.0, z) - 0.13 * C.smoothstep(2.58, 2.42, z),
                        0.06, 0.025, nv=12, name="TieBlade")
    C.part([knot, blade], "Tie", RED, "Fabric", arm=arm, bone="Torso", smooth=40)
    bc = chest_pt(0.36, 3.05, 0.075)
    card = C.rbox((0.26, 0.03, 0.34), loc=tuple(bc), rot=(4, 0, 26), bevel=0.015, seg=1)
    C.part([card], "IDCard", "#F7F5EF", arm=arm, bone="Torso", role="badge", smooth=30)
    head = C.rbox((0.262, 0.012, 0.08), loc=tuple(bc + Vector((0.006, -0.017, 0.12))), rot=(4, 0, 26), bevel=0.0, seg=1)
    photo = C.rbox((0.1, 0.012, 0.12), loc=tuple(bc + Vector((-0.03, -0.017, -0.03))), rot=(4, 0, 26), bevel=0.0, seg=1)
    C.part([head, photo], "IDCardPrint", "#3B6FB6", arm=arm, bone="Torso", smooth=30)
    clip = C.rbox((0.06, 0.04, 0.1), loc=tuple(bc + Vector((0.0, -0.01, 0.2))), rot=(4, 0, 26), bevel=0.01, seg=1)
    C.part([clip], "IDClip", CHROME, "Metal", arm=arm, bone="Torso", smooth=30)
    C.place_accessory(C.strip_roles(C.acc_hair_bun(color="#211B18", tie=RED)), arm=arm, bone="Head", prefix="Bun")
    C.place_accessory(C.acc_face_glasses(frame="#24211F", lens="#BFE3F2", round_=False, w=0.34, h=0.22), arm=arm, bone="Head")
    C.place_accessory(headset(), arm=arm, bone="Head")


def build_head_chef(arm):
    look = {"skin": "#F2C9A5", "top": "#F7F5EF", "pants": "#1E1F22", "shoes": "#1E1F22", "sole": "#111214",
            "brow": "#D2CDC4", "brow_size": (0.24, 0.08, 0.09), "brow_tilt": -3.0, "lid_drop": 0.085,
            "mouth_curve": 0.032, "generic": False}
    C.build_body(arm, look)
    band = ring_band(3.55, 3.7, 0.31, 0.28, n=2.0, segs=20, name="ChefCollar")
    C.part([band], "ChefCollar", "#F7F5EF", "Fabric", arm=arm, bone="Torso", smooth=45)
    edge = [chest_pt(x, z, 0.05) for x, z in ((-0.12, 3.5), (-0.22, 3.2), (-0.27, 2.8), (-0.28, 2.4), (-0.28, 2.1))]
    C.part([C.tube(edge, [0.022] * len(edge), sides=6, res=2)], "JacketEdge", "#E2DED4", "Fabric", arm=arm, bone="Torso", smooth=50)
    buttons([(s * 0.17, z) for s in (1, -1) for z in (2.5, 2.82, 3.14)], INK, arm, r=0.042)
    nk = ns.torus(0.29, 0.065, loc=(0, -0.005, 3.62), major_segs=16, minor_segs=6)
    nk.scale = (1.0, 0.9, 1.0)
    knot_c = Vector((0.0, -0.34, 3.5))
    knot = C.ellipsoid(knot_c, (0.1, 0.07, 0.09), segs=10, rings=6)
    tips = []
    for s in (1, -1):
        pts = [(0.0, 0.0), (s * 0.16, -0.02), (s * 0.05, -0.3)]
        o = ns.profile_slab(pts, 0.03, bevel=0.01, segments=1)
        ns.apply_all(o)
        C.xform(o, Matrix.Translation(knot_c + Vector((s * 0.02, -0.02, -0.02))) @ Matrix.Rotation(math.radians(80), 4, "X"))
        tips.append(o)
    C.part([nk, knot] + tips, "Neckerchief", RED, "Fabric", arm=arm, bone="Torso", smooth=45)
    C.place_accessory(C.strip_roles(C.acc_hair_short(color="#C9C5BE")), arm=arm, bone="Head")
    C.place_accessory(C.strip_roles(C.acc_face_mustache(color="#D9D4CC", big=True)), arm=arm, bone="Head")
    cheeks = []
    for s in (1, -1):
        p = C.head_pt(s * 0.78, 1.93, 0.004)
        o = C.ellipsoid(p, (0.11, 0.03, 0.075), segs=10, rings=5, rot=(0, 0, -s * 44))
        cheeks.append(o)
    C.part(cheeks, "Cheeks", "#EE9C92", arm=arm, bone="Head", smooth=60)
    C.place_accessory(toque(), arm=arm, bone="Head")


OUTFITS = {"trainee": build_trainee, "line_cook": build_line_cook, "stock_runner": build_stock_runner,
           "security_guard": build_security_guard, "night_manager": build_night_manager, "head_chef": build_head_chef}


# --------------------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------------------

def reset_pose(arm):
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()


def build_class(arm, cid):
    """Outfit in the rest pose, then the Display clip, then the props in its frame-0 pose
    (bound while posed), then back to rest. Returns the Display action."""
    OUTFITS[cid](arm)
    act = display_clip(arm, cid)
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and len(act.slots):
        arm.animation_data.action_slot = act.slots[0]
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    PROPS[cid](arm)
    reset_pose(arm)
    return act


def meta(cid):
    m = C.base_meta({"animRig": RIG, "displayClip": "Display_" + cid, "class": cid, "title": TITLES[cid],
                     "note": "Shop display cast: play AnimState Display_" + cid + " (props are held in that pose)"})
    m.pop("clipSpeedRef", None)
    m.pop("events", None)
    m.pop("sit", None)
    return m


def run_class(cid):
    asset = "Character_Class_" + cid

    def build():
        C.reset_caches()
        arm = C.make_rig()
        act = build_class(arm, cid)
        return {"arm": arm, "act": act, "export": {"rig": arm, "pivot": (0.0, 0.0, 0.0), "meta": meta(cid),
                                                   "sockets": C.socket_spec()}}
    out = ns.run_main(build, asset, C.BATCH, C.GROUP)
    if os.environ.get("NS_POSES", "1") == "1":
        print(f"[{asset}] poses:", C.pose_tiles(out["arm"], [(out["act"], 0, -20, False), (out["act"], 0, 25, False),
                                                             (out["act"], 0, 90, False), (out["act"], 40, 0, False)], asset))
    return out


# the six classes added on 2026-11-06 register themselves into ORDER / TITLES / POSES / PROPS / OUTFITS
import _classes2  # noqa: E402,F401
