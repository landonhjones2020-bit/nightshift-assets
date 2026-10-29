"""Creature_Shiver — pale, gangly, frost-covered thing hanging upside down in the freezer.

Modelled in its HANGING pose: toes curled over a rail at the hang point, body hanging head-
down, very long arms dangling to ~2.5 studs above the floor (12-stud ceiling). The asset
pivot IS the hang point (Blender (0, 0, 12)); meta.hangPoint = [0, 0, 0]. Place the pivot at
Freezer.ShiverHang / on the ceiling path (CFrame-driven entity, not a Humanoid).

Rigid-part rig (bones point +Y, roll 0; see _common). Front = Blender -Y, "L" = +X (world
side, not anatomical). Bones: Root (at the hang point) > Hips > Thigh/Shin/Foot L/R (legs
go UP to the grip) and Chest > Head > Jaw, Hair, FogA, FogB; Chest > UpperArm/Forearm/Hand.
Roles: "eyes" (the two glowing icy pupils, Neon).

Clips (30 fps): HangIdle (loop), Scream, Lunge (one-shots from the hang, end on rest),
CeilingCrawl (loop, 14 studs/s = bible rampage speed; belly-up on the ceiling, face looking
forward-down, hands/feet planted on the ceiling plane = pivot height, body centred under the
pivot), DropLunge (one-shot from the crawl pose: telegraph 0.6 s, drops head-first to grab
below the pivot, climbs back; ends on the crawl pose), Retreat (loop, 14 studs/s, fast crawl
glancing back).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
rd = C.rot_deg

SKIN = "#C9D6DD"
SKIN_D = "#A7B8C3"
FROST = "#F2FAFF"
ICE = "#BFEFFF"
CLAW = "#2B3038"
EYES = "#8FF3FF"
TEETH = "#E9EEF0"
HAIR = "#1A2230"
FOG = "#EAF6FF"

CEIL = 12.0
HANG = (0.0, 0.0, CEIL)
HEAD_C = Vector((0.0, -0.02, 6.12))            # head centre (head is modelled upright, then flipped)
SHOULDER = (0.6, 0.05, 6.88)
ELBOW = (0.66, 0.0, 5.1)
WRIST = (0.7, -0.04, 3.38)
HIP_J = (0.2, 0.05, 8.95)
KNEE = (0.2, 0.05, 10.15)
ANKLE = (0.2, 0.05, 11.35)
TOE_TOP = (0.2, -0.12, 11.98)                   # top of the toe hook (ceiling contact)
PALM = (0.7, -0.06, 3.1)                         # palm centre
FINGERTIP = (0.54, -0.1, 2.29)                   # middle claw tip (ceiling contact in the crawl)


def mx(p, s):
    return (p[0] * s, p[1], p[2])


def H(p):
    """Upright head-local point -> world (head flipped upside down, still facing -Y)."""
    return HEAD_C + Vector((-p[0], p[1], -p[2]))


JOINTS = [
    ("Root", None, HANG),
    ("Hips", "Root", (0.0, 0.05, 8.85)),
    ("ThighL", "Hips", HIP_J),
    ("ShinL", "ThighL", KNEE),
    ("FootL", "ShinL", ANKLE),
    ("ThighR", "Hips", mx(HIP_J, -1)),
    ("ShinR", "ThighR", mx(KNEE, -1)),
    ("FootR", "ShinR", mx(ANKLE, -1)),
    ("Chest", "Hips", (0.0, 0.05, 8.35)),
    ("Head", "Chest", (0.0, -0.02, 6.62)),
    ("Jaw", "Head", tuple(H((0, 0.06, -0.2)))),
    ("Hair", "Head", tuple(H((0, 0.0, 0.48)))),
    ("FogA", "Head", tuple(H((0.05, -0.5, -0.24)))),
    ("FogB", "Head", tuple(H((-0.08, -0.46, -0.3)))),
    ("UpperArmL", "Chest", SHOULDER),
    ("ForearmL", "UpperArmL", ELBOW),
    ("HandL", "ForearmL", WRIST),
    ("UpperArmR", "Chest", mx(SHOULDER, -1)),
    ("ForearmR", "UpperArmR", mx(ELBOW, -1)),
    ("HandR", "ForearmR", mx(WRIST, -1)),
]


# ======================================================================================
# Model
# ======================================================================================

def to_head(objs):
    """Transform objects built upright around the origin into the flipped head position."""
    for o in objs:
        ns.apply_all(o)
        for v in o.data.vertices:
            v.co = H(v.co)
        o.data.update()
        if o.matrix_world.determinant() < 0:
            pass
    return objs


def crystals(points, size=0.14, seed=0):
    """Clusters of ice shards: (position, outward normal) pairs."""
    import random
    rnd = random.Random(seed)
    out = []
    for p, nrm in points:
        p, nrm = Vector(p), Vector(nrm).normalized()
        for k in range(3):
            d = (nrm + Vector((rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5)))).normalized()
            L = size * rnd.uniform(0.7, 1.4)
            base = p + Vector((rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05)))
            out.append(C.rod(base - d * 0.03, base + d * L, size * 0.28, verts=5, r_top=0.004))
    return out


def frost(points, seed=1):
    import random
    rnd = random.Random(seed)
    out = []
    for p, r in points:
        o = C.ell(p, (r * rnd.uniform(0.8, 1.2), r * rnd.uniform(0.8, 1.2), r * rnd.uniform(0.6, 1.0)), segs=8, rings=5)
        out.append(o)
    return out


def build_model(sk):
    arm = sk.arm
    A = lambda objs, name, color, bone, mat="SmoothPlastic", **kw: C.attach(objs, name, color, arm, bone, mat, **kw)  # noqa: E731

    # ---- torso (hangs from the hips down to the shoulders) ---------------------------------
    torso = C.loft([(6.78, 0.5, 0.26, 0, 0.06), (6.95, 0.62, 0.3, 0, 0.05), (7.35, 0.56, 0.31, 0, 0.04),
                    (7.8, 0.44, 0.27, 0, 0.05), (8.15, 0.3, 0.2, 0, 0.07), (8.45, 0.27, 0.19, 0, 0.07)],
                   verts=14, n=2.0, name="Torso")
    ribs = []
    for z, w in ((7.0, 0.5), (7.18, 0.52), (7.36, 0.5), (7.54, 0.44)):
        r = ns.torus(1.0, 0.025, rot=(0, 0, 0), major_segs=14, minor_segs=4)
        C.deform(r, lambda v, w=w: Vector((v.x * w, v.y * 0.29, v.z)))
        r.location = (0, 0.06, z)
        ribs.append(r)
    spine = [C.ell((0, 0.27, z), (0.05, 0.04, 0.05), segs=6, rings=4) for z in (7.0, 7.3, 7.6, 7.9, 8.2)]
    neck = C.capsule((0, 0.04, 7.0), (0, 0.0, 6.55), 0.1, 0.09, verts=8, cap_rings=2)
    A([torso, neck] + spine, "Chest", SKIN, "Chest", smooth_angle=70)
    A(ribs, "Chest_Ribs", SKIN_D, "Chest", smooth_angle=70)
    A(frost([((0.4, 0.15, 6.92), 0.17), ((-0.42, 0.2, 6.95), 0.15), ((0.1, 0.3, 7.4), 0.13), ((-0.2, 0.29, 7.9), 0.11)]),
      "Chest_Frost", FROST, "Chest", smooth_angle=70)
    A(crystals([((0.45, 0.2, 6.88), (0.4, 0.6, -0.3)), ((-0.48, 0.22, 6.9), (-0.4, 0.6, -0.3)),
                ((0.0, 0.3, 7.55), (0, 1, 0.1)), ((0.12, 0.27, 8.1), (0.3, 1, 0.3))], 0.2, 3),
      "Chest_Ice", ICE, "Chest", "Ice", smooth_angle=None)

    pelvis = C.ell((0, 0.05, 8.75), (0.3, 0.2, 0.22), segs=12, rings=7)
    A([pelvis], "Hips", SKIN, "Hips", smooth_angle=70)
    A(crystals([((0.2, 0.22, 8.8), (0.4, 1, 0.3)), ((-0.18, 0.2, 8.7), (-0.4, 1, 0))], 0.16, 5), "Hips_Ice", ICE,
      "Hips", "Ice", smooth_angle=None)

    # ---- legs (go up to the grip) -----------------------------------------------------------
    for s, side in (("L", 1), ("R", -1)):
        x = 0.2 * side
        A([C.capsule((x, 0.05, 8.9), (x, 0.05, 10.12), 0.14, 0.11, verts=8, cap_rings=2)], "Thigh" + s, SKIN,
          "Thigh" + s, smooth_angle=70)
        shin = C.capsule((x, 0.05, 10.15), (x, 0.05, 11.32), 0.1, 0.075, verts=8, cap_rings=2)
        knee = C.ell((x, 0.0, 10.15), (0.14, 0.14, 0.15), segs=8, rings=5)
        A([shin, knee], "Shin" + s, SKIN, "Shin" + s, smooth_angle=70)
        A(frost([((x, -0.08, 10.2), 0.11)], seed=7 + side), "Shin" + s + "_Frost", FROST, "Shin" + s, smooth_angle=70)
        A(crystals([((x, -0.1, 10.15), (side * 0.3, -1, 0))], 0.13, 9 + side), "Shin" + s + "_Ice", ICE, "Shin" + s,
          "Ice", smooth_angle=None)
        # long bony foot pointing up, toes curling over toward the front into a hook
        foot = C.capsule((x, 0.05, 11.35), (x, -0.02, 11.82), 0.085, 0.07, verts=8, cap_rings=2)
        toes, claws = [], []
        for k, dx in enumerate((-0.06, 0.0, 0.06)):
            pts = [(x + dx, -0.02, 11.8), (x + dx * 1.2, -0.08, 11.95), (x + dx * 1.3, -0.2, 11.97),
                   (x + dx * 1.3, -0.3, 11.86)]
            toes.append(ns.tube(pts, [0.035, 0.032, 0.028, 0.022], sides=6, resolution=2))
            claws.append(C.rod((x + dx * 1.3, -0.3, 11.87), (x + dx * 1.3, -0.3, 11.74), 0.02, verts=4, r_top=0.003))
        A([foot] + toes, "Foot" + s, SKIN, "Foot" + s, smooth_angle=70)
        A(claws, "Foot" + s + "_Claws", CLAW, "Foot" + s, smooth_angle=None)

    # ---- arms (dangling to just above the floor) ---------------------------------------------
    for s, side in (("L", 1), ("R", -1)):
        S, E, W = Vector(mx(SHOULDER, side)), Vector(mx(ELBOW, side)), Vector(mx(WRIST, side))
        up = C.capsule(S + Vector((0, 0, 0.05)), E, 0.13, 0.095, verts=8, cap_rings=2)
        sh = C.ell(S + Vector((side * 0.04, 0.0, 0.0)), (0.17, 0.16, 0.15), segs=8, rings=5)
        A([up, sh], "UpperArm" + s, SKIN, "UpperArm" + s, smooth_angle=70)
        fo = C.capsule(E, W + Vector((0, 0, 0.05)), 0.09, 0.07, verts=8, cap_rings=2)
        el = C.ell(E, (0.12, 0.12, 0.13), segs=8, rings=5)
        A([fo, el], "Forearm" + s, SKIN, "Forearm" + s, smooth_angle=70)
        A(crystals([(E + Vector((0, 0.08, 0)), (side * 0.3, 1, 0))], 0.13, 20 + side), "Forearm" + s + "_Ice", ICE,
          "Forearm" + s, "Ice", smooth_angle=None)
        palm = C.ell(W + Vector((0, 0, -0.18)), (0.06, 0.12, 0.18), segs=8, rings=5)
        fingers, tips = [], []
        for k in range(4):
            t = k / 3
            y = -0.1 + 0.2 * t
            L = 0.78 - 0.16 * abs(t - 0.4)
            base = W + Vector((0, y, -0.32))
            mid = base + Vector((-side * 0.05, y * 0.4, -L * 0.55))
            tip = base + Vector((-side * 0.16, y * 0.7, -L))
            fingers.append(ns.tube([base, mid, tip], [0.032, 0.026, 0.018], sides=6, resolution=2))
            d = (tip - mid).normalized()
            tips.append(C.rod(tip - d * 0.02, tip + d * 0.14, 0.02, verts=4, r_top=0.003))
        thumb_b = W + Vector((-side * 0.04, -0.12, -0.15))
        fingers.append(ns.tube([thumb_b, thumb_b + Vector((-side * 0.12, -0.12, -0.25)),
                                thumb_b + Vector((-side * 0.2, -0.14, -0.48))], [0.032, 0.026, 0.02], sides=6, resolution=2))
        A([palm] + fingers, "Hand" + s, SKIN, "Hand" + s, smooth_angle=70)
        A(tips, "Hand" + s + "_Claws", CLAW, "Hand" + s, smooth_angle=None)

    # ---- head (built upright, flipped) -----------------------------------------------------
    skull = C.ell((0, 0.0, 0.08), (0.34, 0.4, 0.44), segs=16, rings=10)

    def gaunt(v):
        # hollow cheeks + narrow chin, high cranium
        if v.z < 0.05 and v.y < 0.1:
            k = max(0.0, 1.0 - abs(v.z + 0.12) / 0.25)
            v.x *= 1.0 - 0.18 * k
        if v.z < -0.2:
            v.x *= 0.82
            v.y *= 0.92
        return v
    C.deform(skull, gaunt)
    to_head([skull])
    A([skull], "Head", SKIN, "Head", smooth_angle=60)
    sockets = to_head([C.ell((sx * 0.145, -0.31, 0.07), (0.12, 0.09, 0.105), segs=10, rings=6) for sx in (-1, 1)])
    mouth = to_head([C.ell((0, -0.3, -0.2), (0.21, 0.08, 0.06), segs=12, rings=6)])
    A(sockets + mouth, "Head_Void", C.VOID, "Head", "Fabric", smooth_angle=80)
    eyes = to_head([C.ell((sx * 0.145, -0.385, 0.075), (0.052, 0.035, 0.05), segs=8, rings=5) for sx in (-1, 1)])
    A(eyes, "Head_Eyes", EYES, "Head", "Neon", recolor="eyes", cast_shadow=False, smooth_angle=80)
    upper_teeth = to_head([C.rod((x, -0.33, -0.165), (x * 1.05, -0.35, -0.24), 0.022, verts=4, r_top=0.004)
                           for x in (-0.13, -0.08, -0.03, 0.03, 0.08, 0.13)])
    A(upper_teeth, "Head_Teeth", TEETH, "Head", smooth_angle=None)
    brow = to_head([C.ell((sx * 0.15, -0.3, 0.2), (0.12, 0.06, 0.05), segs=8, rings=4) for sx in (-1, 1)])
    A(brow, "Head_Frost", FROST, "Head", smooth_angle=70)
    A(to_head(crystals([((0.12, 0.05, 0.45), (0.3, 0.2, 1)), ((-0.18, 0.12, 0.42), (-0.4, 0.3, 1))], 0.15, 31)),
      "Head_Ice", ICE, "Head", "Ice", smooth_angle=None)

    jaw = to_head([C.ell((0, -0.1, -0.33), (0.21, 0.27, 0.12), segs=12, rings=6)])
    A(jaw, "Jaw", SKIN, "Jaw", smooth_angle=60)
    lower_teeth = to_head([C.rod((x, -0.31, -0.25), (x * 1.05, -0.33, -0.18), 0.02, verts=4, r_top=0.004)
                           for x in (-0.1, -0.035, 0.035, 0.1)])
    A(lower_teeth, "Jaw_Teeth", TEETH, "Jaw", smooth_angle=None)

    # stringy hair from the crown: built "standing up" in head space so it hangs down
    import random
    rnd = random.Random(4)
    strands = []
    for k in range(9):
        a = 2 * math.pi * k / 9 + rnd.uniform(-0.2, 0.2)
        base = Vector((0.22 * math.cos(a), 0.2 + 0.18 * math.sin(a), 0.36))
        L = rnd.uniform(0.6, 1.15)
        pts = [base, base + Vector((0.05 * math.cos(a), 0.06, L * 0.5)), base + Vector((0.08 * math.cos(a), 0.12, L))]
        strands.append(ns.tube(pts, [0.035, 0.025, 0.012], sides=5, resolution=2))
    A(to_head(strands), "Hair", HAIR, "Hair", smooth_angle=70)

    # breath fog puffs
    fog = dict(mat="SmoothPlastic", transparency=0.55, cast_shadow=False, smooth_angle=80)
    fa = to_head([C.ell((0.05, -0.5, -0.24), (0.08, 0.08, 0.07), segs=8, rings=5),
                  C.ell((0.11, -0.55, -0.2), (0.06, 0.06, 0.05), segs=8, rings=5)])
    fb = to_head([C.ell((-0.08, -0.46, -0.3), (0.07, 0.07, 0.06), segs=8, rings=5)])
    A(fa, "FogA", FOG, "FogA", **fog)
    A(fb, "FogB", FOG, "FogB", **fog)


# ======================================================================================
# Poses
# ======================================================================================

ARM_R, ARM_L = C.ARM["R"], C.ARM["L"]


def hand_ceiling(side):
    """Hand flat on the ceiling: palm up, fingers forward and splayed outward."""
    return C.aim((0, 0, -1), (side * 0.45, -0.85, 0.12), (-side, 0, 0), (0, 0, 1))


def crawl_body(q):
    """Base crawl pose (no limbs): belly up along the ceiling, head bent back to look
    forward-down. q: dict with bob, roll, twist, head_yaw, head_pitch, jaw, lift."""
    pose = {
        "Root": (rd(-90, q.get("roll", 0.0), 0), (0, 4.45, -1.45 + q.get("bob", 0.0) + q.get("lift", 0.0))),
        "Hips": rd(0, 0, q.get("twist", 0.0)),
        "Chest": rd(32, 0, -1.4 * q.get("twist", 0.0)),
        "Head": rd(q.get("head_pitch", 112), 0, 0) @ rd(0, 0, q.get("head_yaw", 0.0)),
        "Jaw": rd(q.get("jaw", 10), 0, 0),
    }
    return pose


def hair_hang(sk, pose):
    """Point the hair straight down (world) whatever the head does."""
    W = sk.fk(pose)
    pose["Hair"] = (sk.local_rot(W, "Hair", C.I3), None)


def limb_ceiling(sk, pose, s, kind, target, knee_hang=0.0):
    """Hand (palm) or foot (toe hook) onto a ceiling point. Wrists/ankles keep a fixed
    LOCAL pose (palm pushed flat / toes continuing the shin) so no joint needs a big twist."""
    side = C.SIDE[s]
    if kind == "hand":
        up, fo, ha = C.ARM[s]
        C.reach_rel(sk, pose, up, fo, ha, FINGERTIP if s == "L" else mx(FINGERTIP, -1), target, rd(0, side * 12, 0),
                    Vector((side * 1.0, 0.1, -0.9)), f0=(0, -1, 0), iters=12)
    else:
        th, sh, ft = C.LEG[s]
        # knees splay out while crawling; blend toward the rest fold plane as the body hangs
        W = sk.fk(pose)
        hang_pole = W["Hips"][0] @ Vector((0, 1, 0))
        pole = Vector((side * 1.0, 0.0, 0.15)).lerp(hang_pole, knee_hang)
        C.reach_rel(sk, pose, th, sh, ft, TOE_TOP if s == "L" else mx(TOE_TOP, -1), target, rd(10, 0, 0),
                    pole, f0=(0, -1, 0), iters=12)


# contact points (world) at mid-stance, body frame centred under the pivot
HAND_C = {"L": (1.2, -2.1, CEIL - 0.05), "R": (-1.2, -2.1, CEIL - 0.05)}
FOOT_C = {"L": (0.8, 2.4, CEIL), "R": (-0.8, 2.4, CEIL)}


def crawl_cycle(sk, *, speed, n, duty=0.55, lift=0.6, head_yaw=0.0, head_pitch=112, jaw=10, twist=6.0,
                bob=0.06, spread=1.0):
    period = n / C.FPS
    stride = speed * duty * period
    phases = {("hand", "L"): 0.0, ("foot", "R"): 0.0, ("hand", "R"): 0.5, ("foot", "L"): 0.5}

    def contact(kind, s, u):
        u = (u - phases[(kind, s)]) % 1.0
        base = Vector((HAND_C if kind == "hand" else FOOT_C)[s])
        base.x *= spread
        if u < duty:
            t = u / duty
            return base + Vector((0, -stride / 2 + stride * t, 0))
        t = (u - duty) / (1 - duty)
        m = stride * (1 - duty) / duty
        p0, p1 = stride / 2, -stride / 2
        t2, t3 = t * t, t * t * t
        y = (2 * t3 - 3 * t2 + 1) * p0 + (t3 - 2 * t2 + t) * m + (-2 * t3 + 3 * t2) * p1 + (t3 - t2) * m
        return base + Vector((0, y, -lift * math.sin(math.pi * t)))

    def fn(frame):
        u = (frame % n) / n
        q = dict(bob=bob * math.cos(4 * math.pi * u), roll=4.0 * math.sin(2 * math.pi * u),
                 twist=twist * math.sin(2 * math.pi * u), head_yaw=head_yaw + 4 * math.sin(2 * math.pi * (u + 0.2)),
                 head_pitch=head_pitch + 3 * math.cos(4 * math.pi * u), jaw=jaw)
        pose = crawl_body(q)
        for s in ("L", "R"):
            limb_ceiling(sk, pose, s, "hand", contact("hand", s, u))
            limb_ceiling(sk, pose, s, "foot", contact("foot", s, u))
        hair_hang(sk, pose)
        pose["FogA"] = (None, None)
        pose["FogB"] = (None, None)
        return pose
    return fn


def crawl_neutral(sk, lift=0.0, jaw=10, head_pitch=112):
    pose = crawl_body(dict(lift=lift, jaw=jaw, head_pitch=head_pitch))
    for s in ("L", "R"):
        limb_ceiling(sk, pose, s, "hand", HAND_C[s])
        limb_ceiling(sk, pose, s, "foot", FOOT_C[s])
    hair_hang(sk, pose)
    return pose


# ======================================================================================
# Clips
# ======================================================================================

def hang_idle_clip(sk):
    def base(p=0.0, r=0.0, arm=0.0, head=(0, 0, 0), fin=0.0, jaw=4.0):
        return {"Root": rd(p, r, 0), "Chest": rd(-0.3 * p, -0.3 * r, 0), "Head": rd(*head), "Jaw": rd(jaw, 0, 0),
                "UpperArmL": rd(-0.8 * p + arm, 0.6 * r - 2, 0), "UpperArmR": rd(-0.8 * p - arm, 0.6 * r + 2, 0),
                "ForearmL": rd(-6 - 0.5 * p, 0, 0), "ForearmR": rd(-6 + 0.5 * p, 0, 0),
                "HandL": rd(-8 + fin, 0, 0), "HandR": rd(-8 - fin, 0, 0),
                "Hair": rd(-0.9 * p, -0.9 * r, 0)}
    keys = [(0, base()), (30, base(p=3.0, r=1.5, arm=1.5, head=(4, 0, 8), fin=6)),
            (60, base(p=0.0, r=2.5, arm=0.0, head=(0, -4, -4), jaw=8)),
            (72, base(p=-1.0, r=2.0, arm=-1.0, head=(-2, -4, -10), fin=-8)),     # twitch
            (90, base(p=-2.5, r=-1.0, arm=-2.0, head=(-3, 3, -6))), (120, base())]
    # breath puffs: drift out and rise toward the ceiling, then re-form at the mouth
    for f0 in (8, 68):
        keys += [(f0, {"FogA": (None, (0, 0, 0)), "FogB": (None, (0, 0, 0))}, "SINE", "EASE_OUT"),
                 (f0 + 34, {"FogA": (None, (0.15, -0.55, 0.7)), "FogB": (None, (-0.12, -0.45, 0.55))}, "LINEAR"),
                 (f0 + 35, {"FogA": (None, (0, 0, 0)), "FogB": (None, (0, 0, 0))})]
    return C.clip(sk, "HangIdle", 120, True, C.merge_keys(keys))


def scream_clip(sk):
    def p(root=0.0, head=(0, 0, 0), jaw=0.0, flare=0.0, fwd=0.0, shake=0.0, fog=0.0):
        return {"Root": rd(root, shake * 0.5, 0), "Chest": rd(-0.5 * root, shake, 0), "Head": rd(*head),
                "Jaw": rd(jaw, 0, 0),
                "UpperArmL": rd(-fwd, -flare + shake, 0), "UpperArmR": rd(-fwd, flare + shake, 0),
                "ForearmL": rd(-0.5 * flare, 0, 0), "ForearmR": rd(-0.5 * flare, 0, 0),
                "HandL": rd(25 * flare / 50, 0, 0), "HandR": rd(25 * flare / 50, 0, 0),
                "FogA": (None, (0.2 * fog, -0.9 * fog, 0.5 * fog)), "FogB": (None, (-0.25 * fog, -0.8 * fog, 0.35 * fog))}
    keys = [(0, p()), (6, p(root=6, head=(10, 0, 0), jaw=6, flare=-6, fwd=-4)),
            (10, p(root=-8, head=(-22, 0, 0), jaw=48, flare=55, fwd=25, fog=1.0), "BACK", "EASE_OUT")]
    for i, f in enumerate(range(12, 36, 2)):
        sh = 4 if i % 2 else -4
        keys.append((f, p(root=-8, head=(-22 + sh * 0.5, sh, 0), jaw=50 - (i % 2) * 6, flare=55 + sh, fwd=25, shake=sh,
                          fog=1.0 + 0.04 * i), "LINEAR"))
    keys += [(40, p(root=-3, head=(-8, 0, 0), jaw=12, flare=12, fwd=6, fog=0.0)), (48, p())]
    return C.clip(sk, "Scream", 48, False, keys)


def lunge_clip(sk):
    def p(root=0.0, drop=0.0, head=(0, 0, 0), jaw=0.0, reach=0.0, spread=0.0, claw=0.0):
        return {"Root": (rd(root, 0, 0), (0, 0, -drop)), "Chest": rd(-0.25 * root, 0, 0), "Head": rd(*head),
                "Jaw": rd(jaw, 0, 0),
                "UpperArmL": rd(-reach, -spread, 0), "UpperArmR": rd(-reach, spread, 0),
                "ForearmL": rd(-0.3 * reach, 0, 0), "ForearmR": rd(-0.3 * reach, 0, 0),
                "HandL": rd(claw, 0, -claw * 0.5), "HandR": rd(claw, 0, claw * 0.5),
                "Hair": rd(-0.8 * root, 0, 0)}
    keys = [(0, p()), (9, p(root=14, head=(14, 0, 0), jaw=8, reach=-28, spread=8), "SINE", "EASE_IN"),
            (14, p(root=-40, drop=0.5, head=(-34, 0, 0), jaw=40, reach=46, spread=16, claw=-30), "BACK", "EASE_OUT"),
            (22, p(root=-44, drop=0.6, head=(-36, 0, 4), jaw=44, reach=50, spread=12, claw=-35)),
            (30, p(root=-38, drop=0.5, head=(-32, 0, -4), jaw=36, reach=47, spread=10, claw=-30)),
            (45, p())]
    return C.clip(sk, "Lunge", 45, False, keys)


def crawl_clip(sk):
    fn = crawl_cycle(sk, speed=14.0, n=10, duty=0.55, lift=0.6)
    return C.sampled_clip(sk, "CeilingCrawl", 10, True, fn, step=1)


def retreat_clip(sk):
    fn = crawl_cycle(sk, speed=14.0, n=10, duty=0.5, lift=0.45, head_yaw=75, head_pitch=104, jaw=24, twist=9.0,
                     bob=0.04, spread=1.12)
    return C.sampled_clip(sk, "Retreat", 10, True, fn, step=1)


def drop_lunge_clip(sk):
    neutral = crawl_neutral(sk)

    def fn(q):
        d = q["drop"]                         # 0 = crawl body, 1 = hanging down to grab
        body = crawl_body(dict(lift=q["lift"], jaw=q["jaw"], head_pitch=q["hp"], head_yaw=q["hy"]))
        # interpolate the root between the crawl attitude and a near-vertical hang
        root_p = -90 + 78 * d
        root_loc = Vector((0, 4.45, -1.45 + q["lift"])).lerp(Vector((0, 0.6, 0.15)), d)
        body["Root"] = (rd(root_p, 0, 0), tuple(root_loc))
        body["Chest"] = rd(32 * (1 - d) - 8 * d, 0, 0)
        body["Head"] = rd(q["hp"] * (1 - d) - 30 * d, 0, q["hy"])
        pose = body
        for s in ("L", "R"):
            side = C.SIDE[s]
            # feet keep gripping the ceiling, sliding in to the hang point as it drops
            ft = Vector(FOOT_C[s]).lerp(Vector((side * 0.3, 0.4, CEIL)), d)
            limb_ceiling(sk, pose, s, "foot", ft, knee_hang=d)
            # hands: on the ceiling while crawling; reach down-forward to grab when dropped
            limb_ceiling(sk, pose, s, "hand", HAND_C[s])
            ceil_pose = {b: pose[b] for b in C.ARM[s]}
            grab = Vector((side * q["grab_w"], -1.3, 3.9))
            C.reach_l(sk, pose, s, PALM if s == "L" else mx(PALM, -1), grab, rd(-25, 0, side * -30),
                      (side * 1.0, 0.4, 0.2))
            C.blend(pose, C.ARM[s], q["hands"], ceil_pose)
        hair_hang(sk, pose)
        pose["FogA"] = (None, (0, -0.5 * q["fog"], 0.4 * q["fog"]))
        pose["FogB"] = (None, (0, -0.4 * q["fog"], 0.3 * q["fog"]))
        return pose
    keys = [
        (0, dict(drop=0.0, lift=0.0, jaw=10, hp=112, hy=0, hands=0.0, grab_w=1.2, fog=0.0), "sine"),
        (5, dict(lift=0.32, jaw=40, hp=104, hy=12, fog=0.6), "sine"),         # tense up to the ceiling, screech
        (9, dict(hy=-12, jaw=44), "sine"),
        (13, dict(hy=10, jaw=46), "sine"),
        (18, dict(hy=0, jaw=50, lift=0.38, fog=1.0), "in"),                     # 0.6 s: DROP
        (26, dict(drop=1.0, lift=0.0, hands=1.0, grab_w=0.45, jaw=55, fog=0.0), "out"),
        (34, dict(grab_w=0.25, jaw=50), "sine"),
        (42, dict(grab_w=0.3, jaw=30), "sine"),
        (56, dict(drop=0.0, hands=0.0, grab_w=1.2, jaw=12, hp=112), "sine"),
        (63, dict(jaw=10), "sine"),
    ]
    act = C.param_clip(sk, "DropLunge", 63, False, keys, fn)
    return act, neutral


# ======================================================================================

def build():
    sk = C.Skel("ShiverRig", JOINTS)
    build_model(sk)
    drop, neutral = drop_lunge_clip(sk)
    acts = [hang_idle_clip(sk), scream_clip(sk), lunge_clip(sk), crawl_clip(sk), drop, retreat_clip(sk)]
    C.rest_pose(sk.arm)

    def checks():
        for a in (acts[3], acts[5]):
            for s, side in (("L", 1), ("R", -1)):
                print(f"  [slide] {a.name} Hand{s}: {C.foot_slide(sk, a, 'Hand' + s, FINGERTIP if s == 'L' else mx(FINGERTIP, -1), 14.0, z_floor=CEIL - 0.05)}")
                print(f"  [slide] {a.name} Foot{s}: {C.foot_slide(sk, a, 'Foot' + s, TOE_TOP if s == 'L' else mx(TOE_TOP, -1), 14.0, z_floor=CEIL)}")
        import bpy
        arm = sk.arm
        arm.data.pose_position = "POSE"
        objs = [o for o in ns._tagged_objects() if not o.name.startswith(("Fog",))]
        for a in acts:
            C.set_action(arm, a)
            hi, lo, who = -1e9, 1e9, None
            for f in range(a["ns_start"], a["ns_end"] + 1, 2):
                bpy.context.scene.frame_set(f)
                for o in objs:
                    for v in o.data.vertices:
                        z = (o.matrix_world @ v.co).z
                        if z > hi:
                            hi, who = z, (o.name, f)
                        lo = min(lo, z)
            print(f"  [extent] {a.name}: z from {lo:.2f} to {hi:.2f} (ceiling {CEIL}) top={who}")
        bpy.context.scene.frame_set(0)

    meta = {
        "root": {"center": [0, -4.0, 0.05], "size": [1.6, 5.0, 1.0]},
        "hangPoint": [0, 0, 0],
        "hangNote": "pivot = hang point (toe grip, top); the body hangs ~9.5 studs below it; built for a 12-stud ceiling",
        "headRest": [0, -5.88, -0.02],
        "crawlSpeed": 14,
        "clipSpeedRef": {"CeilingCrawl": 14, "Retreat": 14},
        "crawl": {"bodyBelowCeiling": 1.5, "note": "pivot stays on the ceiling plane; body centred under the pivot"},
        "events": {"Scream": {"peak": 0.33}, "Lunge": {"hit": 0.47}, "DropLunge": {"drop": 0.6, "grab": 0.87}},
    }
    return {"skel": sk, "arm": sk.arm, "actions": acts, "checks": [checks], "ceiling_z": CEIL,
            "export": {"rig": sk.arm, "pivot": HANG, "meta": meta}}


STRIPS = {
    "HangIdle": dict(frames=[0, 30, 72, 90], ceiling_z=CEIL),
    "Scream": dict(frames=[0, 10, 20, 40], ceiling_z=CEIL),
    "Lunge": dict(frames=[9, 14, 22, 36], ceiling_z=CEIL, yaw=-80),
    "CeilingCrawl": dict(frames=[0, 2, 5, 7], ceiling_z=CEIL, yaw=-70, pitch=-8),
    "DropLunge": dict(frames=[0, 13, 22, 26, 42, 56], ceiling_z=CEIL, yaw=-75, pitch=0),
    "Retreat": dict(frames=[0, 2, 5, 7], ceiling_z=CEIL, yaw=-70, pitch=-8),
}

if __name__ == "__main__":
    C.run(build, "Creature_Shiver", "Shiver", strips=STRIPS)
