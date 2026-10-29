"""Creature_Paperface — ordinary body in a long trench coat, head = paper grocery bag.

Rigid-part rig (bones point +Y, roll 0; see _common). Front = Blender -Y, "L" = +X.
Bones: Hips (root) > Torso > Head > BagCorner, Smile, SmileBig; arms UpperArm/Forearm/Hand
L/R; legs Thigh/Shin/Foot L/R; coat skirt CoatL/CoatR > CoatLowerL/CoatLowerR.

Roles: "bag" (the paper shell, default white; tint by riddle rarity), "bag_corner" (the
torn-off corner piece: tint it with the bag; hide it from events.TearBag.hideCorner on,
the bag then shows a jagged hole), "receipt" (HandR; show only during PlaceReceipt).
The eye holes are real holes in the shell showing a dark inner head. The crayon smile (bone Smile)
stays; Happy slides a much bigger toothy crayon grin (bone SmileBig) out through the paper
from inside the bag wall (hidden at rest).

Clips (30 fps): Walk (loop, 5 studs/s), ChaseRun (loop, 18 studs/s = bible chase speed),
Idle (loop), PlaceReceipt, TearBag, Happy, Catch (one-shots, end on rest), Vault (one-shot
with ROOT MOTION: ends 5.3 studs forward, see meta.rootMotion).
Counter assumption (PlaceReceipt / Vault): near edge 1.1 studs in front of the pivot,
top 3.0, depth 3.0 (STYLE.md).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
rd = C.rot_deg

COAT = "#4A4036"
COAT_D = "#2E2823"
BUTTON = "#17140F"
SKIN = "#CFC8BA"
TROUSER = "#2A2C33"
SHOE = "#18181B"
BAG = C.PAPER_WHITE
SMILE = "#141113"

SHOULDER = (0.72, 0.05, 4.38)
ELBOW = (0.8, 0.08, 3.36)
WRIST = (0.84, 0.04, 2.42)
HIP_J = (0.3, 0.03, 2.85)
KNEE = (0.3, 0.03, 1.55)
ANKLE = (0.3, 0.03, 0.28)
SMILE_C = (0.0, -0.44, 4.74)
CORNER_J = (-0.42, 0.0, 5.42)
RECEIPT_C = Vector((-0.74, -0.06, 2.0))       # receipt centre (pinched in HandR)
FINGER_R = Vector((-0.86, -0.06, 1.95))       # right index fingertip area (draw / tap)
PALM_L = Vector((0.84, 0.04, 2.25))
PALM_R = Vector((-0.84, 0.04, 2.25))


def mx(p, s):
    return (p[0] * s, p[1], p[2])


JOINTS = [
    ("Hips", None, (0.0, 0.03, 2.95)),
    ("Torso", "Hips", (0.0, 0.05, 3.2)),
    ("Head", "Torso", (0.0, 0.0, 4.55)),
    ("BagCorner", "Head", CORNER_J),
    ("Smile", "Head", SMILE_C),
    ("SmileBig", "Head", SMILE_C),
    ("UpperArmL", "Torso", SHOULDER),
    ("ForearmL", "UpperArmL", ELBOW),
    ("HandL", "ForearmL", WRIST),
    ("UpperArmR", "Torso", mx(SHOULDER, -1)),
    ("ForearmR", "UpperArmR", mx(ELBOW, -1)),
    ("HandR", "ForearmR", mx(WRIST, -1)),
    ("ThighL", "Hips", HIP_J),
    ("ShinL", "ThighL", KNEE),
    ("FootL", "ShinL", ANKLE),
    ("ThighR", "Hips", mx(HIP_J, -1)),
    ("ShinR", "ThighR", mx(KNEE, -1)),
    ("FootR", "ShinR", mx(ANKLE, -1)),
    ("CoatL", "Hips", (0.3, 0.03, 3.0)),
    ("CoatLowerL", "CoatL", (0.45, 0.03, 1.62)),
    ("CoatR", "Hips", (-0.3, 0.03, 3.0)),
    ("CoatLowerR", "CoatR", (-0.45, 0.03, 1.62)),
]


# ======================================================================================
# Model
# ======================================================================================

def build_bag():
    """Paper grocery bag shell (closed end on top), crumpled, gusset folds on the sides,
    zig-zag bottom edge; eye holes cut; returns (bag, corner_piece, inner_head)."""
    import bpy
    secs = [(4.36, 0.57, 0.45), (4.45, 0.55, 0.43), (4.62, 0.52, 0.41), (5.0, 0.52, 0.41),
            (5.38, 0.515, 0.405), (5.56, 0.505, 0.4)]
    bag = C.loft([(z, rx, ry, 0.0, 0.0, 6.0) for z, rx, ry in secs], verts=28, cap_bottom=False, name="Bag")

    def shape(v):
        # side gussets fold inward along the middle of the side panels
        if abs(v.x) > 0.38:
            k = max(0.0, 1.0 - abs(v.y) / 0.36)
            v.x *= 1.0 - 0.07 * k
        # crumple: coherent low-frequency noise, stronger near the bottom opening
        n = C.noise3(v * 3.1, 1.7)
        amp = 0.022 + 0.022 * max(0.0, (4.8 - v.z) / 0.45)
        v.x += n * amp * (1 if v.x > 0 else -1)
        v.y += C.noise3(v * 2.7 + Vector((3, 1, 0)), 0.4) * amp
        # two soft horizontal creases where the bag was folded flat
        for zc in (4.9, 5.33):
            k = max(0.0, 1.0 - abs(v.z - zc) / 0.05)
            v.x *= 1.0 - 0.025 * k
            v.y *= 1.0 - 0.03 * k
        # sits a little crooked on the head
        v.z += 0.06 * v.x
        # top corners slumped
        if v.z > 5.45:
            v.z -= 0.05 * (abs(v.x) / 0.5) ** 2
        # zig-zag (serrated) bottom edge
        if v.z < 4.37:
            a = math.atan2(v.y, v.x)
            v.z += 0.035 * (1 if (int((a + math.pi) / (2 * math.pi) * 28) % 2) else -1)
        return v
    C.deform(bag, shape)
    sol = bag.modifiers.new("Solid", "SOLIDIFY")
    sol.thickness = 0.035
    sol.offset = -1.0
    ns.apply_all(bag)
    # eye holes: slightly mismatched, irregular
    for x, z, r, seed in ((0.19, 5.1, 0.105, 1), (-0.2, 5.075, 0.118, 2)):
        cut = ns.cyl(r, 0.4, loc=(x, -0.42, z), rot=(90, 0, 0), verts=11, bevel=0.0)
        ns.apply_all(cut)
        import random
        rnd = random.Random(seed)
        for v in cut.data.vertices:
            d = Vector((v.co.x - x, 0, v.co.z - z))
            if d.length > 1e-4:
                k = 1.0 + rnd.uniform(-0.18, 0.12)
                v.co.x = x + d.x * k
                v.co.z = z + d.z * k * 0.92
        ns.boolean(bag, cut, "DIFFERENCE")
    # torn corner (top, the creature's right = -X), through the full depth
    jag = [(-0.7, 5.7), (-0.7, 5.16), (-0.6, 5.24), (-0.55, 5.18), (-0.47, 5.3), (-0.41, 5.25),
           (-0.33, 5.39), (-0.27, 5.36), (-0.2, 5.5), (-0.16, 5.47), (-0.12, 5.7)]
    cutter = C.extrude(jag, 1.2, plane="XZ", offset=-0.6, name="CornerCut")
    keep = cutter.copy()
    keep.data = cutter.data.copy()
    bpy.context.scene.collection.objects.link(keep)
    piece = bag.copy()
    piece.data = bag.data.copy()
    bpy.context.scene.collection.objects.link(piece)
    ns.boolean(bag, cutter, "DIFFERENCE")
    ns.boolean(piece, keep, "INTERSECT")
    inner = C.ell((0, 0.0, 4.98), (0.43, 0.34, 0.48), segs=14, rings=8)
    return bag, piece, inner


def build_model(sk):
    arm = sk.arm
    A = lambda objs, name, color, bone, mat="SmoothPlastic", **kw: C.attach(objs, name, color, arm, bone, mat, **kw)  # noqa: E731

    # ---- torso ---------------------------------------------------------------------------
    torso = C.loft([(3.0, 0.5, 0.33, 0, 0.03), (3.4, 0.53, 0.34, 0, 0.04), (3.9, 0.62, 0.36, 0, 0.05),
                    (4.28, 0.72, 0.37, 0, 0.05), (4.46, 0.6, 0.33, 0, 0.04), (4.58, 0.3, 0.24, 0, 0.02)],
                   verts=16, n=2.3, name="TorsoCoat")
    collar = C.arc_loft([(4.2, 0.42, 0.33, 0, 0.0), (4.4, 0.49, 0.38, 0, 0.0), (4.5, 0.5, 0.39, 0, 0.0)],
                        -55, 235, segs=14, thickness=0.05, name="Collar")
    A([torso, collar], "Torso", COAT, "Torso", smooth_angle=60)
    lap = []
    for sx in (-1, 1):
        lap.append(C.extrude([(0.0, 3.25), (sx * 0.34, 4.3), (sx * 0.12, 4.4), (sx * 0.03, 3.3)], 0.04,
                             plane="XZ", offset=-0.4))
    A(lap, "Torso_Lapels", COAT_D, "Torso", smooth_angle=50)
    btn = [ns.cyl(0.045, 0.04, loc=(sx * 0.17, -0.37, z), rot=(90, 0, 0), verts=8, bevel=0.0)
           for sx in (-1, 1) for z in (3.5, 3.85)]
    A(btn, "Torso_Buttons", BUTTON, "Torso", smooth_angle=50)

    belt = C.loft([(3.05, 0.53, 0.35, 0, 0.03), (3.2, 0.53, 0.35, 0, 0.03)], verts=16, n=2.3, name="Belt")
    tail = C.plate(0.08, 0.5, 0.03, 0.03, (0.3, -0.36, 2.9), plane="XZ")
    tail.rotation_euler = (0, math.radians(-12), 0)
    A([belt, tail], "Hips", COAT_D, "Hips", smooth_angle=50)

    upper = [(1.55, 0.76, 0.56, 0, 0.04), (2.4, 0.63, 0.46, 0, 0.03), (3.15, 0.52, 0.36, 0, 0.03)]
    lower = [(0.82, 0.86, 0.63, 0, 0.05), (1.5, 0.79, 0.58, 0, 0.04), (1.72, 0.78, 0.57, 0, 0.04)]
    for s, side, (a0, a1) in (("L", 1, (-84, 96)), ("R", -1, (84, 264))):
        A([C.arc_loft(upper, a0, a1, segs=10, thickness=0.05)], "Coat" + s, COAT, "Coat" + s, smooth_angle=60)
        A([C.arc_loft(lower, a0, a1, segs=10, thickness=0.05)], "CoatLower" + s, COAT, "CoatLower" + s, smooth_angle=60)
    pk = [C.plate(0.36, 0.13, 0.04, 0.04, (sx * 0.52, -0.5, 2.62), plane="XZ") for sx in (-1, 1)]
    for o, sx in zip(pk, (-1, 1)):
        o.rotation_euler = (0, 0, math.radians(sx * 30))
    A(pk[:1], "CoatR_Pocket", COAT_D, "CoatR", smooth_angle=50)
    A(pk[1:], "CoatL_Pocket", COAT_D, "CoatL", smooth_angle=50)

    # ---- head: bag, corner, inner darkness, smile -----------------------------------------
    bag, piece, inner = build_bag()
    A([bag], "Head_Bag", BAG, "Head", recolor="bag", smooth_angle=40)
    A([piece], "BagCorner", BAG, "BagCorner", recolor="bag_corner", smooth_angle=40)
    A([inner], "Head", C.VOID, "Head", "Fabric", smooth_angle=80)
    # crayon smile (one stroke + end ticks)
    half = [(0.1, 4.742), (0.19, 4.765), (0.27, 4.805), (0.33, 4.86), (0.36, 4.91)]
    pts = [(-x, z) for x, z in reversed(half)] + [(0.0, 4.735)] + half
    sm = [C.stroke(pts, 0.052, 0.03, plane="XZ", offset=-0.472)]
    for sx in (-1, 1):
        sm.append(C.stroke([(sx * 0.32, 4.95), (sx * 0.4, 4.86)], 0.04, 0.03, plane="XZ", offset=-0.472))
    A(sm, "Smile", SMILE, "Smile", smooth_angle=None)
    # the BIG grin it draws in Happy: hidden inside the bag wall, slides out through the paper
    big = []
    u = [(0.44 * math.sin(math.radians(a)), 4.98 - 0.36 * math.cos(math.radians(a)) ** 0.8)
         for a in range(-80, 81, 10)]
    big.append(C.stroke(u, 0.06, 0.02, plane="XZ", offset=-0.358))
    big.append(C.stroke([(-0.36, 4.86), (-0.12, 4.83), (0.12, 4.83), (0.36, 4.86)], 0.045, 0.02, plane="XZ", offset=-0.358))
    for x in (-0.24, -0.12, 0.0, 0.12, 0.24):
        zb = 4.98 - 0.36 * max(0.0, 1 - (x / 0.44) ** 2) ** 0.45
        big.append(C.stroke([(x, 4.84), (x * 1.03, zb + 0.04)], 0.035, 0.02, plane="XZ", offset=-0.358))
    A(big, "SmileBig", SMILE, "SmileBig", smooth_angle=None)

    # ---- arms ----------------------------------------------------------------------------
    for s, side in (("L", 1), ("R", -1)):
        S, E, W = Vector(mx(SHOULDER, side)), Vector(mx(ELBOW, side)), Vector(mx(WRIST, side))
        A([C.capsule(S, E, 0.19, 0.16, verts=10, cap_rings=2)], "UpperArm" + s, COAT, "UpperArm" + s, smooth_angle=60)
        A([C.capsule(E, W + Vector((0, 0, 0.12)), 0.16, 0.17, verts=10, cap_rings=2)], "Forearm" + s, COAT,
          "Forearm" + s, smooth_angle=60)
        A([ns.cyl(0.18, 0.1, loc=W + Vector((0, 0, 0.14)), verts=10, bevel=0.02, segments=1)], "Forearm" + s + "_Cuff",
          COAT_D, "Forearm" + s, smooth_angle=50)
        hand = C.glove(W, side=side, palm=(0.065, 0.11, 0.13), fingers=4, flen=0.3, fr=0.034, curl=10, thumb=0.2)
        A(hand, "Hand" + s, SKIN, "Hand" + s, smooth_angle=70)

    # ---- legs ----------------------------------------------------------------------------
    for s, side in (("L", 1), ("R", -1)):
        x = 0.3 * side
        A([C.capsule((x, 0.03, 2.9), (x, 0.03, 1.6), 0.21, 0.17, verts=10, cap_rings=2)], "Thigh" + s, TROUSER,
          "Thigh" + s, smooth_angle=60)
        A([C.capsule((x, 0.03, 1.6), (x, 0.03, 0.32), 0.16, 0.13, verts=10, cap_rings=2)], "Shin" + s, TROUSER,
          "Shin" + s, smooth_angle=60)
        shoe = C.ell((x, -0.08, 0.13), (0.16, 0.33, 0.15), segs=12, rings=7)
        C.deform(shoe, lambda v: Vector((v.x, v.y, max(v.z, 0.0) if v.z < 0.03 else v.z)))
        A([shoe], "Foot" + s, SHOE, "Foot" + s, smooth_angle=60)

    # ---- receipt (pinched between thumb and fingers of HandR) -----------------------------
    rc = C.plate(0.3, 0.5, 0.02, 0.02, RECEIPT_C, plane="YZ")
    A([rc], "HandR_Receipt", C.PAPER_WHITE, "HandR", recolor="receipt", smooth_angle=None)


# ======================================================================================
# Clips
# ======================================================================================

ARM_R, ARM_L = C.ARM["R"], C.ARM["L"]
LEGS = [dict(thigh="Thigh" + s, shin="Shin" + s, foot="Foot" + s, ankle=mx(ANKLE, side), side=side,
             phase=ph, sole=[(0.3 * side, 0.22, 0.0), (0.3 * side, -0.41, 0.0)])
        for s, side, ph in (("L", 1, 0.0), ("R", -1, 0.5))]


def walk_clip(sk):
    n = 24

    def extra(u, pose, W):
        tw = -5.0 * math.cos(2 * math.pi * u)
        pose["Torso"] = (rd(-2, 0, -1.2 * tw), None)
        pose["Head"] = (rd(3 + 1.0 * math.cos(4 * math.pi * u), 9, 0.8 * tw), None)   # constant uncanny tilt
        for s, side, ph in (("L", 1, 0.0), ("R", -1, 0.5)):
            cs = math.cos(2 * math.pi * (u - 0.04 - ph))
            pose["UpperArm" + s] = (rd(6 * cs, side * -2, 0), None)
            pose["Forearm" + s] = (rd(-6 - 3 * max(0, -cs), 0, 0), None)
            pose["Hand" + s] = (rd(0, 0, 0), None)
        C.coat_follow(pose, 0.55)

    fn = C.biped_cycle(sk, LEGS, speed=5.0, period=n / C.FPS, duty=0.6, lift=0.22, lift_peak=0.45,
                       hip_height=2.9, bob=0.035, sway=0.03, roll=2.5, twist=5.0, lean=0.0, extra=extra)
    return C.sampled_clip(sk, "Walk", n, True, fn, step=2)


def chase_clip(sk):
    n = 16

    def extra(u, pose, W):
        tw = -6.0 * math.cos(2 * math.pi * u)
        pose["Torso"] = (rd(10 + 2 * math.cos(4 * math.pi * u), 0, -1.3 * tw), None)
        pose["Head"] = (rd(-14 + 7 * math.cos(4 * math.pi * (u - 0.1)), 20, 0.5 * tw), None)
        for s, side, ph in (("L", 1, 0.0), ("R", -1, 0.5)):
            cs = math.cos(2 * math.pi * (u - ph))
            # arms rigid at the sides, barely moving: wrong for a runner, and that's the point
            pose["UpperArm" + s] = (rd(14 + 3 * cs, side * -7, 0), None)
            pose["Forearm" + s] = (rd(-2, 0, 0), None)
            pose["Hand" + s] = (rd(8, 0, 0), None)
        C.coat_follow(pose, 0.6, lower_k=0.5)

    fn = C.biped_cycle(sk, LEGS, speed=18.0, period=n / C.FPS, duty=0.3, lift=0.75, lift_peak=0.38,
                       hip_height=2.78, bob=-0.07, sway=0.02, roll=3.0, twist=6.0, lean=8.0, extra=extra,
                       toe_off=25.0, heel_strike=-6.0)
    return C.sampled_clip(sk, "ChaseRun", n, True, fn, step=1)


def idle_clip(sk):
    def base(head=(0, 0, 0), breath=0.0, sway=0.0):
        p = {"Hips": (rd(0, 0, 0), (sway, 0, 0)), "Torso": rd(-breath, 0, 0), "Head": rd(*head),
             "UpperArmL": rd(0, -1, 0), "UpperArmR": rd(0, 1, 0),
             "ForearmL": rd(-3 - breath, 0, 0), "ForearmR": rd(-3 - breath, 0, 0)}
        C.plant(sk, p)
        C.coat_follow(p, 0.5)
        return p
    keys = [(0, base()), (20, base(breath=1.2)), (34, base(head=(4, 22, -6), breath=0.6, sway=0.02)),
            (52, base(head=(5, 26, -8), breath=1.0, sway=0.02)), (60, base(head=(5, 25, -8), breath=0.6, sway=0.02)),
            (64, base(head=(4, 27, -6), breath=0.6, sway=0.02)),        # tiny twitch
            (84, base(head=(1, -6, 3), breath=1.2)), (100, base(head=(2, -14, 6), breath=0.4)),
            (112, base(head=(1, -4, 2), breath=0.8))]
    return C.clip(sk, "Idle", 120, True, keys)


def place_clip(sk):
    pocket = Vector((-0.55, -0.43, 2.62))
    hr = rd(20, 0, 70)

    def fn(q):
        pose = {"Hips": (rd(q["hp"], 0, 0), (0, 0.06 * q["hp"], -0.01 * q["hp"])), "Torso": rd(q["tp"], 0, 0),
                "Head": rd(*q["head"])}
        C.plant(sk, pose)
        C.coat_follow(pose, 0.0, q["hp"])
        C.arm_mix(pose, ARM_R, q["wR"], lambda P: C.reach_l(sk, P, "R", RECEIPT_C, q["grip"], rd(*q["wrist"]),
                                                             (-1, 0.7, -0.2)))
        return pose
    keys = [
        (0, dict(hp=0, tp=0, head=(0, 0, 0), grip=tuple(pocket + Vector((0, 0, 0.3))), wrist=(0, 0, 0), wR=0.0), "sine"),
        (10, dict(grip=tuple(pocket), head=(10, 0, 0), wR=1.0), "sine"),                 # hand in the pocket
        (16, dict(grip=tuple(pocket + Vector((0, -0.05, 0.05)))), "out"),
        (28, dict(hp=6, tp=10, head=(14, 6, 0), grip=(-0.35, -1.45, 3.35), wrist=(20, 0, 70)), "sine"),
        (36, dict(hp=10, tp=14, head=(18, 8, 0), grip=(-0.3, -1.5, 3.04)), "sine"),     # set down
        (44, dict(grip=(-0.3, -1.5, 3.2)), "in"),                                          # tap
        (48, dict(grip=(-0.3, -1.5, 3.04)), "out"),
        (54, dict(grip=(-0.3, -1.5, 3.18)), "in"),                                         # tap
        (58, dict(grip=(-0.3, -1.5, 3.04)), "sine"),
        (66, dict(hp=4, tp=6, head=(6, 16, -4), grip=(-0.55, -1.0, 3.3)), "sine"),
        (78, dict(hp=0, tp=0, head=(0, 0, 0), grip=(-0.75, -0.4, 2.7), wR=0.0), "sine"),
    ]
    return C.param_clip(sk, "PlaceReceipt", 78, False, keys, fn)


LAND = Vector((-1.25, -1.15, 0.46))                # where the torn corner comes to rest (bone head)


def tear_clip(sk):
    corner_grip = Vector((-0.36, -0.3, 5.48))          # rest point on the corner piece the right hand grabs
    hold_l = Vector((0.05, -0.38, 5.42))                # left hand steadies the bag top-front
    grab_pt = Vector((-0.86, 0.0, 1.98))                # pinch point of HandR (fingertips)

    def fn(q):
        pose = {"Hips": (rd(0, 0, 0), (0, 0, 0)), "Torso": rd(q["tp"], 0, q["ty"]), "Head": rd(*q["head"])}
        C.plant(sk, pose)
        W = sk.fk(pose)
        tgtR = sk.point(W, "Head", corner_grip) + Vector(q["rip"])
        C.arm_mix(pose, ARM_R, q["wR"], lambda P: C.reach_l(sk, P, "R", grab_pt, tgtR, rd(-10, 0, 40), (-1, 0.3, -0.5)))
        tgtL = sk.point(W, "Head", hold_l)
        C.arm_mix(pose, ARM_L, q["wL"], lambda P: C.reach_l(sk, P, "L", Vector((0.86, 0.0, 1.98)), tgtL,
                                                             rd(-10, 0, -40), (1, 0.3, -0.5)))
        if q["carry"] > 0.5:
            # the torn piece travels with the right hand, then drops (q.fall) to the floor
            Wp = sk.fk(pose)
            hand_pt = sk.point(Wp, "HandR", grab_pt)
            R = Wp["Head"][0] @ rd(*q["spin"])          # tumbles relative to the head (no big inherited spins)
            carried = hand_pt + R @ (sk.head["BagCorner"] - corner_grip)
            pos = carried.lerp(LAND, q["fall"])         # flung, then drops onto the floor in front
            C.set_world(sk, pose, "BagCorner", R, pos)
        else:
            pose["BagCorner"] = (None, (0, 0, 0))
        return pose
    keys = [
        (0, dict(tp=0, ty=0, head=(0, 0, 0), rip=(0, 0, 0), wR=0.0, wL=0.0, carry=0.0, fall=0.0,
                 spin=(0, 0, 0)), "sine"),
        (12, dict(head=(4, -10, 0), wR=1.0, wL=1.0, rip=(0, -0.05, 0.05)), "sine"),        # grip
        (18, dict(head=(6, -16, 4), tp=4, rip=(0, 0, 0)), "in"),                            # wind
        (19, dict(carry=1.0), "out"),                                                        # RIP
        (24, dict(head=(-6, 14, -10), tp=-4, ty=10, rip=(-0.75, -0.55, -0.95), spin=(35, 0, 20)), "sine"),
        (32, dict(head=(-2, 10, -6), rip=(-1.1, -0.9, -1.25), spin=(70, 0, 35), wL=0.0, fall=0.0), "in"),  # fling
        (44, dict(fall=1.0, spin=(95, 0, 50), wR=0.0, tp=0, ty=0, head=(8, 18, 0)), "out"),
        (56, dict(head=(6, 20, 2)), "sine"),
        (57, dict(), "linear"),                                                              # hideCorner
        (60, dict(head=(0, 0, 0), carry=0.0, fall=0.0, spin=(0, 0, 0), rip=(0, 0, 0)), "sine"),
    ]
    return C.param_clip(sk, "TearBag", 60, False, keys, fn, step=1)


def happy_clip(sk):
    draw_pt = FINGER_R

    def fn(q):
        pose = {"Hips": (rd(0, 0, 0), (0, 0, q["bounce"])), "Torso": rd(q["tp"], q["tr"], 0), "Head": rd(*q["head"])}
        C.plant(sk, pose)
        W = sk.fk(pose)
        tgt = sk.point(W, "Head", Vector((q["dx"], -0.5, 4.78 + 0.25 * abs(q["dx"]))))
        C.arm_mix(pose, ARM_R, q["wR"], lambda P: C.reach_l(sk, P, "R", draw_pt, tgt, rd(-25, 0, 60), (-0.3, -0.25, -1)))
        pose["UpperArmL"] = rd(-q["clasp"] * 30, -q["clasp"] * 8, 0)
        pose["ForearmL"] = rd(-q["clasp"] * 75, 0, 0)
        g = q["grin"]
        pose["Smile"] = (None, (0, 0, 0))
        pose["SmileBig"] = (None, (0, -0.125 * g, 0))
        return pose
    keys = [
        (0, dict(tp=0, tr=0, head=(0, 0, 0), bounce=0.0, dx=-0.4, wR=0.0, clasp=0.0, grin=0.0), "sine"),
        (12, dict(head=(-4, 6, 0), wR=1.0, dx=-0.38), "sine"),
        (22, dict(dx=0.0, head=(-5, 1, 0)), "linear"),                     # draws across the face...
        (24, dict(grin=1.0), "sine"),                                       # ...and the big grin appears
        (32, dict(dx=0.38, head=(-6, -4, 0)), "sine"),
        (40, dict(wR=0.0, dx=0.2, head=(-8, 12, 0), clasp=1.0), "out"),
        (46, dict(bounce=0.06, head=(-6, 18, 0), tr=3), "sine"),
        (52, dict(bounce=0.0, head=(-8, 10, 0), tr=-2), "sine"),
        (58, dict(bounce=0.06, head=(-6, 18, 0), tr=3), "sine"),
        (64, dict(bounce=0.0, head=(-6, 14, 0), tr=0), "sine"),
        (76, dict(clasp=0.0, head=(0, 0, 0), grin=0.0, dx=-0.4), "sine"),
    ]
    return C.param_clip(sk, "Happy", 76, False, keys, fn)


def vault_clip(sk):
    def fn(q):
        pose = {"Hips": (rd(q["hp"], 0, 0), q["hl"]), "Torso": rd(q["tp"], 0, 0), "Head": rd(*q["head"])}
        fl = Vector(q["fl"])
        fr = Vector((-fl.x, fl.y, fl.z))
        C.plant(sk, pose, {"L": (tuple(fl), rd(q["fp"], 0, 0)), "R": (tuple(fr), rd(q["fp"], 0, 0))})
        C.coat_follow(pose, 0.55, q["hp"], cap=0.0)
        for s, side in (("L", 1), ("R", -1)):
            h = Vector(q["hand"])
            h.x *= side
            C.arm_mix(pose, C.ARM[s], q["wH"], lambda P, s=s, h=h, side=side: C.reach_l(
                sk, P, s, PALM_L if s == "L" else PALM_R, h, rd(30, 0, side * 90), (side, 0.6, -0.2)))
        return pose
    A0 = (0.3, 0.03, 0.28)
    keys = [
        (0, dict(hp=0, hl=(0, 0, 0), tp=0, head=(0, 0, 0), fl=A0, fp=0, hand=(0.48, -1.4, 3.3), wH=0.0), "sine"),
        (6, dict(hp=18, hl=(0, -0.3, -0.42), tp=14, head=(-16, 0, 0), hand=(0.48, -1.4, 3.2), wH=0.7), "sine"),
        (10, dict(hp=28, hl=(0, -0.65, -0.25), tp=20, head=(-22, 0, 0), hand=(0.46, -1.42, 3.05), wH=1.0,
                  fp=20, fl=(0.3, 0.07, 0.43)), "out"),
        (14, dict(hp=46, hl=(0, -1.35, 1.0), tp=18, head=(-34, 0, 0), fl=(0.3, -0.95, 3.35), fp=-10), "sine"),
        (18, dict(hp=36, hl=(0, -2.35, 1.3), tp=12, head=(-28, 0, 0), fl=(0.26, -2.3, 3.55), fp=-20), "sine"),
        (22, dict(hp=18, hl=(0, -3.5, 0.85), tp=6, head=(-14, 0, 0), fl=(0.3, -3.95, 3.45), fp=-10,
                  hand=(0.6, -2.6, 3.6), wH=0.0), "in"),
        (24, dict(hp=20, hl=(0, -4.4, 0.2), fl=(0.3, -4.8, 2.0), fp=0), "out"),
        (26, dict(hp=26, hl=(0, -5.15, -0.78), tp=16, head=(-18, 0, 0), fl=(0.32, -5.3, 0.28)), "out"),
        (34, dict(hp=14, hl=(0, -5.25, -0.5), tp=8, head=(-8, 0, 0)), "sine"),
        (44, dict(hp=0, hl=(0, -5.3, 0.0), tp=0, head=(0, 0, 0), fl=(0.3, -5.27, 0.28)), "sine"),
    ]
    return C.param_clip(sk, "Vault", 44, False, keys, fn, step=1)


def catch_clip(sk):
    def fn(q):
        pose = {"Hips": (rd(q["hp"], 0, 0), q["hl"]), "Torso": rd(q["tp"], 0, 0), "Head": rd(*q["head"])}
        C.plant(sk, pose, {"R": (q["fr"],)})
        C.coat_follow(pose, 0.5, q["hp"])
        for s, side in (("L", 1), ("R", -1)):
            h = Vector(q["hand"])
            h.x *= side
            C.arm_mix(pose, C.ARM[s], q["wH"], lambda P, s=s, h=h, side=side: C.reach_l(
                sk, P, s, PALM_L if s == "L" else PALM_R, h, rd(10, 0, side * 70), (side, 0.6, -0.3)))
        return pose
    keys = [
        (0, dict(hp=0, hl=(0, 0, 0), tp=0, head=(0, 0, 0), fr=(-0.3, 0.03, 0.28), hand=(1.0, -1.2, 3.6), wH=0.0), "sine"),
        (7, dict(hp=14, hl=(0, -0.7, -0.3), tp=8, head=(-10, 0, 0), fr=(-0.3, -1.0, 0.28), hand=(1.05, -2.0, 3.9),
                 wH=1.0), "out"),
        (12, dict(hand=(0.28, -1.75, 3.55), head=(10, 16, 0), tp=12), "out"),     # arms close round the victim
        (16, dict(hl=(0, -0.55, -0.25), hand=(0.24, -1.5, 3.6), head=(16, 22, 0)), "sine"),
        (32, dict(hand=(0.26, -1.52, 3.62), head=(18, 26, 4)), "sine"),
        (40, dict(hp=6, hl=(0, -0.4, -0.1), tp=4, hand=(0.8, -1.5, 3.4), head=(4, 8, 0), fr=(-0.3, -0.5, 0.28)), "sine"),
        (52, dict(hp=0, hl=(0, 0, 0), tp=0, head=(0, 0, 0), fr=(-0.3, 0.03, 0.28), hand=(1.0, -0.6, 3.0), wH=0.0), "sine"),
    ]
    return C.param_clip(sk, "Catch", 52, False, keys, fn)


# ======================================================================================

def build():
    sk = C.Skel("PaperfaceRig", JOINTS)
    build_model(sk)
    acts = [walk_clip(sk), idle_clip(sk), place_clip(sk), tear_clip(sk), happy_clip(sk), vault_clip(sk),
            chase_clip(sk), catch_clip(sk)]
    C.rest_pose(sk.arm)

    def checks():
        for a, v in ((acts[0], 5.0), (acts[6], 18.0)):
            for s, side in (("L", 1), ("R", -1)):
                for nm, pt in (("heel", (0.3 * side, 0.22, 0.0)), ("toe", (0.3 * side, -0.41, 0.0))):
                    print(f"  [slide] {a.name} Foot{s} {nm}: {C.foot_slide(sk, a, 'Foot' + s, pt, v)}")
        for a in acts:
            print(f"  [floor] {a.name}: lowest point {C.lowest_point(sk, a, skip=('BagCorner',))}")

    meta = {
        "root": {"center": [0, 2.95, -0.03], "size": [2.0, 2.0, 1.0]},
        "walkSpeed": 5, "chaseSpeed": 18,
        "clipSpeedRef": {"Walk": 5, "ChaseRun": 18},
        "rootMotion": {"Vault": [0, 0, -5.3]},
        "counter": {"nearEdge": 1.1, "top": 3.0, "depth": 3.0,
                    "note": "PlaceReceipt and Vault assume the counter's near edge 1.1 studs in front of the pivot"},
        "props": {"receipt": "HandR_Receipt: show from events.PlaceReceipt.show to events.PlaceReceipt.release",
                  "bag_corner": "BagCorner: tint with the bag; hide from events.TearBag.hideCorner for the rest of the visit"},
        "events": {"PlaceReceipt": {"show": 0.4, "release": 1.95}, "TearBag": {"rip": 0.63, "hideCorner": 1.88},
                   "Happy": {"grin": 0.77}, "Vault": {"plant": 0.33, "land": 0.87}, "Catch": {"grab": 0.4}},
    }
    return {"skel": sk, "arm": sk.arm, "actions": acts, "checks": [checks],
            "export": {"rig": sk.arm, "pivot": (0.0, 0.0, 0.0), "meta": meta}}


STRIPS = {
    "Walk": dict(frames=[0, 6, 12, 18]),
    "ChaseRun": dict(frames=[0, 4, 8, 12]),
    "Idle": dict(frames=[0, 52, 64, 100]),
    "PlaceReceipt": dict(frames=[10, 28, 36, 66]),
    "TearBag": dict(frames=[12, 19, 26, 44]),
    "Happy": dict(frames=[12, 24, 32, 46], yaw=-30),
    "Vault": dict(frames=[10, 14, 18, 22, 26, 44], yaw=-90, pitch=8),
    "Catch": dict(frames=[7, 12, 32, 40]),
}

if __name__ == "__main__":
    C.run(build, "Creature_Paperface", "Paperface", strips=STRIPS)
