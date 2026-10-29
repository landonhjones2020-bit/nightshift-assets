"""Creature_MrUsual — 8-stud figure in a long yellow raincoat, hood in shadow, two pinprick eyes.

Rigid-part rig (bones point +Y, roll 0; see _common). Front = Blender -Y, "L" = +X.
Bones: Hips (root) > Torso > Head > DripHat; arms UpperArm/Forearm/Hand L/R; legs
Thigh/Shin/Foot L/R; coat skirt halves CoatL/CoatR (follow the thighs) > DripHem.
Props: a closed umbrella held like a cane in HandL; a receipt in HandR (role "receipt",
the client shows it only during SlideReceipt). Rain drops are Glass parts on several bones;
DripHat / DripHem are single drops that fall and re-form in Idle.

Clips (30 fps): Walk (loop, heavy, 5 studs/s), StalkWalk (loop, 9 studs/s = bible stalk
speed), Idle (loop), SitStare (loop, seated on a 1.6-stud booth seat centred on the pivot),
SlideReceipt, TipHat, Lunge (one-shots, end on the rest pose).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
rd = C.rot_deg

YELLOW = "#E9B824"
YELLOW_D = "#B8870F"
TOGGLE = "#2A2622"
RUBBER = "#1C1D21"
TROUSER = "#2B3040"
EYE = "#FFF1B5"
UMB = "#262B3A"
WOOD = "#6B4426"
METAL = "#AEB5BC"
DRIPC = "#A9D8F2"

HIPS = (0.0, 0.05, 4.3)
SHOULDER = (1.0, 0.0, 6.05)
ELBOW = (1.12, 0.02, 4.45)
WRIST = (1.2, -0.02, 2.95)
HIP_J = (0.42, 0.05, 4.15)
KNEE = (0.42, 0.05, 2.2)
ANKLE = (0.42, 0.05, 0.4)
DRIP_HAT = (0.06, -1.22, 7.36)
DRIP_HEM = (-0.45, -0.9, 1.05)
UMB_GRIP = Vector((1.2, -0.06, 2.5))
UMB_TIP = Vector((1.46, -0.36, 0.22))
RECEIPT_C = Vector((-1.06, -0.04, 2.42))       # receipt centre (in HandR's palm)
PINCH_R = Vector((-1.2, -0.12, 2.12))          # right-hand pinch point (fingertips)
BRIM_PINCH = Vector((-0.3, -1.12, 7.32))       # point on the hood brim the hand pinches


def mx(p, s):
    return (p[0] * s, p[1], p[2])


JOINTS = [
    ("Hips", None, HIPS),
    ("Torso", "Hips", (0.0, 0.08, 4.65)),
    ("Head", "Torso", (0.0, -0.22, 6.4)),
    ("DripHat", "Head", DRIP_HAT),
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
    ("CoatL", "Hips", (0.4, 0.05, 4.3)),
    ("CoatLowerL", "CoatL", (0.6, 0.05, 2.5)),
    ("CoatR", "Hips", (-0.4, 0.05, 4.3)),
    ("CoatLowerR", "CoatR", (-0.6, 0.05, 2.5)),
    ("DripHem", "CoatLowerR", DRIP_HEM),
]


# ======================================================================================
# Model
# ======================================================================================

def build_model(sk):
    arm = sk.arm
    A = lambda objs, name, color, bone, mat="SmoothPlastic", **kw: C.attach(objs, name, color, arm, bone, mat, **kw)  # noqa: E731

    # ---- torso (upper coat), collar, toggles ------------------------------------------
    torso = C.loft([(4.42, 0.64, 0.47, 0, 0.05), (5.2, 0.76, 0.52, 0, 0.1), (5.75, 0.9, 0.55, 0, 0.12),
                    (6.05, 0.98, 0.52, 0, 0.08), (6.3, 0.78, 0.47, 0, -0.02), (6.46, 0.42, 0.36, 0, -0.12)],
                   verts=16, n=2.15, name="TorsoCoat")
    collar = C.arc_loft([(6.12, 0.5, 0.42, 0, -0.08), (6.52, 0.6, 0.52, 0, -0.14), (6.86, 0.7, 0.62, 0, -0.2)],
                        -60, 240, segs=14, thickness=0.09, name="Collar")
    A([torso, collar], "Torso", YELLOW, "Torso", smooth_angle=60)
    toggles = []
    for z, y in ((4.95, -0.47), (5.4, -0.46), (5.85, -0.47)):
        toggles.append(C.capsule((0.0, y, z), (0.24, y + 0.02, z), 0.045, verts=6, cap_rings=2))
        toggles.append(C.rod((0.24, y - 0.01, z), (0.42, y + 0.03, z), 0.018, verts=4))
    A(toggles, "Torso_Toggles", TOGGLE, "Torso", smooth_angle=60)
    seam = C.arc_loft([(4.42, 0.66, 0.49, 0, 0.05), (4.6, 0.67, 0.5, 0, 0.055)], 0, 360, segs=16, thickness=0.05)
    A([seam], "Torso_Seam", YELLOW_D, "Torso", smooth_angle=60)

    # ---- belt on the hips (covers the skirt/torso seam) ---------------------------------
    belt = C.loft([(4.33, 0.69, 0.51, 0, 0.05), (4.53, 0.69, 0.51, 0, 0.05)], verts=16, n=2.4, name="Belt")
    buckle = C.plate(0.3, 0.22, 0.06, 0.05, (0.0, -0.53, 4.43), plane="XZ")
    A([belt], "Hips", YELLOW_D, "Hips", smooth_angle=50)
    A([buckle], "Hips_Buckle", TOGGLE, "Hips", smooth_angle=50)

    # ---- coat skirt halves --------------------------------------------------------------
    upper = [(2.42, 1.07, 0.84, 0, 0.08), (3.3, 0.85, 0.64, 0, 0.06), (4.48, 0.66, 0.48, 0, 0.05)]
    lower = [(1.12, 1.25, 1.0, 0, 0.1), (2.2, 1.1, 0.87, 0, 0.08), (2.62, 1.07, 0.85, 0, 0.08)]
    hem = [(1.08, 1.28, 1.03, 0, 0.1), (1.3, 1.24, 0.99, 0, 0.1)]
    for s, side, (a0, a1) in (("L", 1, (-87, 97)), ("R", -1, (83, 267))):
        up_half = C.arc_loft(upper, a0, a1, segs=12, thickness=0.07, name="Skirt" + s)
        flap = C.plate(0.42, 0.18, 0.05, 0.05, (side * 0.83, -0.56, 3.15), plane="XZ")
        flap.rotation_euler = (0, 0, math.radians(side * 38))
        A([up_half, flap], "Coat" + s, YELLOW, "Coat" + s, smooth_angle=60)
        lo_half = C.arc_loft(lower, a0, a1, segs=12, thickness=0.07, name="SkirtLo" + s)
        A([lo_half], "CoatLower" + s, YELLOW, "CoatLower" + s, smooth_angle=60)
        hb = C.arc_loft(hem, a0, a1, segs=12, thickness=0.09, name="Hem" + s)
        A([hb], "CoatLower" + s + "_Hem", YELLOW_D, "CoatLower" + s, smooth_angle=60)
    # one toggle column on the left front edge of the skirt
    st = [C.capsule((0.04, -0.66 - 0.06 * k, z), (0.24, -0.64 - 0.06 * k, z), 0.042, verts=6, cap_rings=2)
          for k, z in enumerate((3.95, 3.3))]
    A(st, "CoatL_Toggles", TOGGLE, "CoatL", smooth_angle=60)

    # ---- head: hood, void, rim, brim, eyes -----------------------------------------------
    hood = C.ell((0, -0.1, 7.12), (0.74, 0.84, 0.86), segs=20, rings=12, name="Hood")

    def cowl(v):
        # pointed cowl tip drooping down the back
        if v.y > -0.2:
            k = max(0.0, (v.z - 6.9) / 1.1) * max(0.0, (v.y + 0.2) / 0.84)
            v.y += 0.55 * k * k
            v.z -= 0.25 * k * k * k
            v.x *= 1.0 - 0.45 * k * k
        if v.y < -0.3:
            fr = min(1.0, (-v.y - 0.3) / 0.64)
            v.y -= 0.26 * fr * fr                      # the face opening juts forward (a tunnel)
            up = max(0.0, (v.z - 6.98) / 0.9)
            v.y -= 0.5 * (up ** 1.1) * fr              # top-front overhang
            v.z -= 0.1 * up * fr * fr
        return v
    C.deform(hood, cowl)
    ns.apply_all(hood)
    # the face tunnel: elliptical cut into the front, lined with darkness
    tun = C.loft([(0.0, 0.4, 0.5, 0, 0, 2.3), (1.1, 0.4, 0.5, 0, 0, 2.3)], verts=20, name="Tunnel")
    tun.rotation_euler = (math.radians(90), 0, 0)
    tun.location = (0, -0.66, 6.96)
    ns.apply_all(tun)
    ns.boolean(hood, tun, "DIFFERENCE")
    A([hood], "Head", YELLOW, "Head", smooth_angle=55)
    lining = C.loft([(0.0, 0.395, 0.495, 0, 0, 2.3), (0.46, 0.395, 0.495, 0, 0, 2.3)], verts=20,
                    cap_bottom=True, cap_top=False, name="Lining")
    lining.rotation_euler = (math.radians(90), 0, 0)
    lining.location = (0, -0.68, 6.96)
    sol = lining.modifiers.new("S", "SOLIDIFY")
    sol.thickness = 0.02
    A([lining], "Head_Void", C.VOID, "Head", "Fabric", smooth_angle=80)
    eyes = [C.ell((-0.13, -0.74, 7.0), (0.042, 0.03, 0.042), segs=8, rings=5),
            C.ell((0.14, -0.74, 7.03), (0.04, 0.03, 0.04), segs=8, rings=5)]
    A(eyes, "Head_Eyes", EYE, "Head", "Neon", cast_shadow=False, smooth_angle=80)

    # ---- arms --------------------------------------------------------------------------
    for s, side in (("L", 1), ("R", -1)):
        S, E, W = Vector(mx(SHOULDER, side)), Vector(mx(ELBOW, side)), Vector(mx(WRIST, side))
        up = C.capsule(S + Vector((-side * 0.04, 0, -0.1)), E, 0.31, 0.26, verts=10, cap_rings=3)
        A([up], "UpperArm" + s, YELLOW, "UpperArm" + s, smooth_angle=60)
        fo = C.capsule(E, W + Vector((0, 0, 0.2)), 0.26, 0.29, verts=10, cap_rings=2)
        A([fo], "Forearm" + s, YELLOW, "Forearm" + s, smooth_angle=60)
        cuff = ns.cyl(0.32, 0.17, loc=W + Vector((0, 0, 0.2)), verts=12, bevel=0.03, segments=1)
        A([cuff], "Forearm" + s + "_Cuff", YELLOW_D, "Forearm" + s, smooth_angle=50)
        hand = C.glove(W, side=side, palm=(0.1, 0.18, 0.22), fingers=4, flen=0.62, fr=0.052, curl=14, thumb=0.32)
        A(hand, "Hand" + s, RUBBER, "Hand" + s, smooth_angle=70)

    # ---- legs --------------------------------------------------------------------------
    for s, side in (("L", 1), ("R", -1)):
        x = 0.42 * side
        th = C.capsule((x, 0.05, 4.2), (x, 0.05, 2.25), 0.3, 0.25, verts=10, cap_rings=2)
        A([th], "Thigh" + s, TROUSER, "Thigh" + s, smooth_angle=60)
        sh = C.capsule((x, 0.05, 2.25), (x, 0.05, 1.35), 0.24, 0.23, verts=10, cap_rings=2)
        A([sh], "Shin" + s + "_Trouser", TROUSER, "Shin" + s, smooth_angle=60)
        boot = C.loft([(0.42, 0.27, 0.29, x, 0.06), (1.3, 0.28, 0.3, x, 0.05), (1.44, 0.31, 0.33, x, 0.05)],
                      verts=12, n=2.0, cap_top=False, name="BootShaft")
        A([boot], "Shin" + s, RUBBER, "Shin" + s, smooth_angle=60)
        foot = C.ell((x, -0.13, 0.22), (0.28, 0.45, 0.25), segs=12, rings=8)
        C.deform(foot, lambda v: Vector((v.x, v.y, max(v.z, 0.0) if v.z < 0.04 else v.z)))
        A([foot], "Foot" + s, RUBBER, "Foot" + s, smooth_angle=60)

    # ---- umbrella (closed, held like a cane in HandL) -------------------------------------
    d = (UMB_TIP - UMB_GRIP)
    L = d.length
    q = d.normalized().to_track_quat("-Z", "Y")
    R = q.to_matrix()

    def place(o):
        ns.apply_all(o)
        for v in o.data.vertices:
            v.co = UMB_GRIP + R @ v.co
        o.data.update()
        return o
    canopy = place(ns.lathe([(0.0, -L + 0.45), (0.06, -L + 0.52), (0.17, -L + 0.95), (0.2, -L + 1.35),
                             (0.13, -0.5), (0.05, -0.36), (0.0, -0.33)], verts=10))
    strap = place(ns.torus(0.2, 0.035, loc=(0, 0, -L + 1.15), major_segs=10, minor_segs=4))
    A([canopy, strap], "HandL_Umbrella", UMB, "HandL", "Fabric", smooth_angle=50)
    shaft = place(C.rod((0, 0, 0.2), (0, 0, -0.4), 0.04, verts=6))
    tip = place(C.rod((0, 0, -L + 0.48), (0, 0, -L + 0.02), 0.04, verts=6, r_top=0.014))
    A([shaft, tip], "HandL_UmbrellaMetal", METAL, "HandL", "Metal", smooth_angle=50)
    crook = ns.tube([UMB_GRIP + Vector((0, 0, -0.05)), UMB_GRIP + Vector((0, -0.02, 0.26)),
                     UMB_GRIP + Vector((0.0, -0.2, 0.42)), UMB_GRIP + Vector((0, -0.4, 0.3)),
                     UMB_GRIP + Vector((0, -0.42, 0.12))], [0.065, 0.065, 0.065, 0.06, 0.055], sides=8, resolution=3)
    A([crook], "HandL_Crook", WOOD, "HandL", smooth_angle=60)

    # ---- receipt in the right hand (role, hidden by the client except in SlideReceipt) ---
    rc = C.plate(0.4, 0.62, 0.025, 0.03, RECEIPT_C, plane="YZ")
    A([rc], "HandR_Receipt", C.PAPER_WHITE, "HandR", recolor="receipt", smooth_angle=None)

    # ---- rain drops ----------------------------------------------------------------------
    drip = dict(mat="Glass", transparency=0.35, cast_shadow=False, smooth_angle=80)
    A([C.drop((0.3, -1.1, 7.26), 0.06), C.drop((-0.33, -1.08, 7.27), 0.05)], "Head_Drops", DRIPC, "Head", **drip)
    A([C.drop(DRIP_HAT, 0.065)], "DripHat", DRIPC, "DripHat", **drip)
    A([C.drop((0.98, -0.57, 1.0), 0.06), C.drop((0.44, 1.07, 1.01), 0.055)], "CoatLowerL_Drops", DRIPC, "CoatLowerL", **drip)
    A([C.drop((-1.19, 0.45, 1.0), 0.055)], "CoatLowerR_Drops", DRIPC, "CoatLowerR", **drip)
    A([C.drop(DRIP_HEM, 0.06)], "DripHem", DRIPC, "DripHem", **drip)
    A([C.drop(UMB_GRIP + (UMB_TIP - UMB_GRIP) * 0.62 + Vector((0.17, 0.0, -0.05)), 0.05)], "HandL_Drops", DRIPC, "HandL", **drip)
    A([C.drop((-1.22, -0.14, 1.9), 0.05)], "HandR_Drops", DRIPC, "HandR", **drip)


# ======================================================================================
# Posing helpers
# ======================================================================================

def hand_rot(side, fingers, palm):
    """World rotation for a hand: rest fingers (0,0,-1) -> fingers, rest palm normal
    (-side,0,0) -> palm."""
    return C.aim((0, 0, -1), fingers, (-side, 0, 0), palm)


def reach(sk, pose, s, grip_rest, target, hrot, pole):
    Rh = C.as_mat(hrot)
    wr = sk.head["Hand" + s]
    wt = Vector(target) - Rh @ (Vector(grip_rest) - wr)
    return C.solve_limb(sk, pose, "UpperArm" + s, "Forearm" + s, wr, wt, Vector(pole), f0=(0, -1, 0),
                        end="Hand" + s, end_world=Rh)


def reach_l(sk, pose, s, grip_rest, target, local, pole):
    """Hand reach with the wrist at a LOCAL rotation (relative to the forearm)."""
    return C.reach_rel(sk, pose, "UpperArm" + s, "Forearm" + s, "Hand" + s, grip_rest, target, local,
                       Vector(pole), f0=(0, -1, 0))


def palm_world(sk, pose, s):
    side = 1 if s == "L" else -1
    W = sk.fk(pose)
    R = W["Hand" + s][0]
    return tuple(round(c, 2) for c in R @ Vector((-side, 0, 0))), tuple(round(c, 2) for c in R @ Vector((0, 0, -1)))


def plant(sk, pose, feet=None):
    """IK both legs so each ankle sits at its target (default: rest) with a flat foot."""
    feet = feet or {}
    for s, side in (("L", 1), ("R", -1)):
        spec = feet.get(s)
        T = Vector(spec[0]) if spec else sk.head["Foot" + s].copy()
        Rf = C.as_mat(spec[1]) if (spec and len(spec) > 1) else C.I3
        C.solve_limb(sk, pose, "Thigh" + s, "Shin" + s, sk.head["Foot" + s], T,
                     pole=Vector((0.12 * side, -1, 0)), f0=(0, 1, 0), end="Foot" + s, end_world=Rf)


def coat_follow(pose, k=0.5, hips_pitch=0.0, lag=0.0):
    """Coat halves follow the thighs (k) and hang plumb against the hips' pitch; the lower
    halves counter-swing a little (cloth hanging from the knee line)."""
    for s in ("L", "R"):
        th = C._split(pose.get("Thigh" + s))[0]
        p = math.degrees(C.as_mat(th).to_euler("XYZ").x) if th is not None else 0.0
        up = k * min(p, 10.0) - 0.85 * hips_pitch
        pose["Coat" + s] = (rd(up, 0, 0), None)
        pose["CoatLower" + s] = (rd(-0.35 * (up + hips_pitch) + lag, 0, 0), None)


def umbrella_clear(sk, pose, zmin=0.12):
    """If the umbrella tip is below zmin, pitch HandL the least amount that clears it."""
    base = C.as_mat(C._split(pose.get("HandL"))[0])
    if sk.point(sk.fk(pose), "HandL", UMB_TIP).z >= zmin:
        return
    for i in range(1, 121):
        for a in (0.5 * i, -0.5 * i):
            pose["HandL"] = (base @ rd(a, 0, 0), None)
            if sk.point(sk.fk(pose), "HandL", UMB_TIP).z >= zmin:
                return
    pose["HandL"] = (base, None)


def umbrella_tip_to(sk, pose, z_target=0.04):
    """Pitch HandL so the umbrella tip touches z_target (drag), bisection on wrist pitch."""
    base = C.as_mat(C._split(pose.get("HandL"))[0])
    samples = []
    for i in range(0, 241):
        a = -30.0 + 0.5 * i                     # + pitch swings the tip backward
        pose["HandL"] = (base @ rd(a, 0, 0), None)
        samples.append((a, sk.point(sk.fk(pose), "HandL", UMB_TIP).z))
    amin, zmin = min(samples, key=lambda t: t[1])
    best = amin
    if zmin < z_target:
        behind = [(a, z) for a, z in samples if a >= amin and z >= z_target]
        best = behind[0][0] if behind else amin
    pose["HandL"] = (base @ rd(best, 0, 0), None)
    return sk.point(sk.fk(pose), "HandL", UMB_TIP)


# ======================================================================================
# Clips
# ======================================================================================

LEGS = [dict(thigh="Thigh" + s, shin="Shin" + s, foot="Foot" + s, ankle=mx(ANKLE, side), side=side,
             phase=ph, sole=[(0.42 * side, 0.32, 0.0), (0.42 * side, -0.58, 0.0)])
        for s, side, ph in (("L", 1, 0.0), ("R", -1, 0.5))]


def walk_clip(sk):
    n = 36

    def extra(u, pose, W):
        tw = -7.0 * math.cos(2 * math.pi * u)
        pose["Torso"] = (rd(6 + 2.5 * math.cos(4 * math.pi * (u - 0.1)), 2.0 * math.sin(2 * math.pi * u), -1.5 * tw), None)
        pose["Head"] = (rd(-5 - 2.0 * math.cos(4 * math.pi * (u - 0.17)), -1.5 * math.sin(2 * math.pi * u), 0.6 * tw), None)
        for s, side, ph in (("L", 1, 0.0), ("R", -1, 0.5)):
            cs = math.cos(2 * math.pi * (u - 0.05 - ph))
            ap = 15.0 * cs
            fl = -(14 + 12 * max(0.0, -cs))
            pose["UpperArm" + s] = (rd(ap, side * -4, 0), None)
            pose["Forearm" + s] = (rd(fl, 0, 0), None)
            if s == "L":
                pose["HandL"] = (rd(8 + 0.3 * ap - (ap + fl), 0, 0), None)
            else:
                pose["HandR"] = (rd(-6, 0, 0), None)
        umbrella_clear(sk, pose, 0.14)
        coat_follow(pose, 0.5)
        pose["DripHat"] = (None, None)
        pose["DripHem"] = (None, None)

    fn = C.biped_cycle(sk, LEGS, speed=5.0, period=n / C.FPS, duty=0.62, lift=0.34, lift_peak=0.42,
                       hip_height=4.17, bob=0.07, sway=0.07, roll=3.5, twist=7.0, lean=3.0, extra=extra)
    return C.sampled_clip(sk, "Walk", n, True, fn, step=3)


def stalk_clip(sk):
    n = 28

    def extra(u, pose, W):
        tw = -5.0 * math.cos(2 * math.pi * u)
        pose["Torso"] = (rd(17 + 1.0 * math.cos(4 * math.pi * u), 0, -1.6 * tw), None)
        pose["Head"] = (rd(-24, 0, 1.2 * tw), None)           # face locked level on the target
        cs = math.cos(2 * math.pi * (u - 0.05))
        pose["UpperArmR"] = (rd(-16 - 5 * cs, 6, 0), None)    # right arm hangs forward, reaching
        pose["ForearmR"] = (rd(-28 - 6 * cs, 0, 0), None)
        pose["HandR"] = (rd(-18, 0, 0), None)
        pose["UpperArmL"] = (rd(14 + 4 * cs, -10, 0), None)   # umbrella dragged behind
        pose["ForearmL"] = (rd(-6, 0, 0), None)
        pose["HandL"] = (rd(0, 0, 0), None)
        umbrella_tip_to(sk, pose, 0.03)
        coat_follow(pose, 0.45)
        pose["DripHat"] = (None, None)
        pose["DripHem"] = (None, None)

    fn = C.biped_cycle(sk, LEGS, speed=9.0, period=n / C.FPS, duty=0.5, lift=0.3, lift_peak=0.5,
                       hip_height=3.95, bob=0.025, sway=0.04, roll=2.0, twist=5.0, lean=6.0, extra=extra)
    return C.sampled_clip(sk, "StalkWalk", n, True, fn, step=2)


def idle_clip(sk):
    def base(head=(2, 0, 0), breath=0.0, hand_l=0.0, fore_l=0.0, sway=0.0):
        return planted({
            "Hips": (rd(0, 0, 0), (sway, 0, 0)),
            "Torso": rd(breath, 0, 0),
            "Head": rd(*head),
            "UpperArmL": rd(-breath * 0.5, -2, 0), "ForearmL": rd(-6 + fore_l, 0, 0), "HandL": rd(4 + hand_l, 0, 0),
            "UpperArmR": rd(-breath * 0.5, 2, 0), "ForearmR": rd(-8, 0, 0), "HandR": rd(-4, 0, 0),
            "CoatL": rd(0.8 * breath, 0, 0), "CoatR": rd(-0.5 * breath, 0, 0),
            "CoatLowerL": rd(-0.5 * breath, 0, 0), "CoatLowerR": rd(0.4 * breath, 0, 0),
        })

    def planted(p):
        plant(sk, p)
        return p
    keys = []
    poses = {
        0: base(),
        14: base(breath=0.6),
        30: base(breath=1.5, sway=0.02),
        48: base(head=(7, 17, -9), breath=0.4, sway=0.03),
        60: base(head=(8, 19, -7), breath=0.0, sway=0.03),
        80: base(head=(7, 18, -8), breath=1.4, sway=0.02),
        88: base(head=(5, 9, -4), breath=1.2, fore_l=-10, hand_l=-4),
        94: base(head=(3, 2, 0), breath=1.0, fore_l=0, hand_l=0),
        104: base(head=(2, 0, 0), breath=0.6),
    }
    for f, p in poses.items():
        e = "QUAD" if f == 88 else "SINE"
        keys.append((f, p, e, "EASE_IN" if f == 88 else "EASE_IN_OUT"))
    # falling drops (bone loc in its rest frame = world axes; the head is neutral here)
    for f, z, e in ((0, 0.0, "SINE"), (12, 0.0, "QUAD"), (24, -7.9, "LINEAR"), (25, 0.0, "SINE")):
        keys.append((f, {"DripHat": (None, (0, 0, z))}, e, "EASE_IN"))
    for f, z, e in ((0, 0.0, "SINE"), (68, 0.0, "QUAD"), (77, -1.75, "LINEAR"), (78, 0.0, "SINE")):
        keys.append((f, {"DripHem": (None, (0, 0, z))}, e, "EASE_IN"))
    return C.clip(sk, "Idle", 120, True, merge_keys(keys))


def merge_keys(keys):
    """Combine several (frame, pose, ease, dir) lists; frames shared by several entries
    merge their pose dicts (the first entry's ease wins). Frames that only list a few
    bones key only those bones."""
    merged = {}
    for k in keys:
        f = k[0]
        if f in merged:
            merged[f] = (f, {**merged[f][1], **k[1]}) + tuple(merged[f][2:])
        else:
            merged[f] = tuple(k)
    return [merged[f] for f in sorted(merged)]


def sit_pose(sk, head=(4, 0, 0), breath=0.0):
    pose = {"Hips": (rd(-3, 0, 0), (0, 0.0, -2.28)), "Torso": rd(6 + breath, 0, 0), "Head": rd(*head)}
    plant(sk, pose, {"L": ((0.5, -1.72, 0.4),), "R": ((-0.5, -1.72, 0.4),)})
    for s in ("L", "R"):            # skirt drapes over the lap and falls at the knees
        pose["Coat" + s] = rd(-84, 0, 0)
        pose["CoatLower" + s] = rd(88, 0, 0)
    # both hands stacked on the umbrella handle, umbrella planted between the feet
    d = (UMB_TIP - UMB_GRIP).normalized()
    Rl = C.aim(d, (0.0, -0.08, -1.0), (0, -1, 0), (0, -1, 0))
    tipT = Vector((0.04, -2.0, 0.2))
    grip = tipT - Rl @ (UMB_TIP - UMB_GRIP)
    reach(sk, pose, "L", UMB_GRIP, grip, Rl, (1, 0.6, -0.2))
    W = sk.fk(pose)
    top = sk.point(W, "HandL", sk.head["HandL"]) + Vector((-0.02, -0.05, 0.12))
    Rr = hand_rot(-1, (0.25, -0.55, -0.8), (0.1, -0.2, -1))
    reach(sk, pose, "R", Vector(mx(WRIST, -1)) + Vector((0, 0, -0.18)), top, Rr, (-1, 0.5, -0.3))
    return pose


def sit_clip(sk):
    keys = [(0, sit_pose(sk)), (20, sit_pose(sk, breath=1.2)), (44, sit_pose(sk, head=(6, -13, 5), breath=0.3)),
            (74, sit_pose(sk, head=(7, -15, 6), breath=1.2)), (98, sit_pose(sk, head=(5, -3, 1), breath=0.2))]
    return C.clip(sk, "SitStare", 120, True, keys)


ARM_R = ("UpperArmR", "ForearmR", "HandR")
ARM_L = ("UpperArmL", "ForearmL", "HandL")


def arm_mix(pose, bones, w, solve):
    """Solve an arm (IK) and blend it in by weight w from its current (FK/rest) rotation."""
    if w <= 1e-4:
        return
    base = {b: pose.get(b) for b in bones}
    solve(pose)
    C.blend(pose, bones, w, base)


def slide_clip(sk):
    hr = rd(25, 0, 90)         # wrist rolled so the palm lies flat on the receipt

    def fn(q):
        pose = {"Hips": (rd(q["hp"], 0, 0), q["hl"]), "Torso": rd(q["tp"], 0, 0), "Head": rd(*q["head"])}
        plant(sk, pose)
        coat_follow(pose, 0.0, q["hp"])
        arm_mix(pose, ARM_R, q["wR"], lambda P: reach_l(sk, P, "R", RECEIPT_C, q["grip"], hr, (-1, 0.8, 0.2)))
        # left hand keeps the umbrella standing where it was
        arm_mix(pose, ARM_L, q["wL"], lambda P: reach(sk, P, "L", UMB_GRIP, UMB_GRIP + Vector((0.05, -0.15, 0.0)),
                                                      C.I3, (1, 0.6, -0.2)))
        return pose
    keys = [
        (0, dict(hp=0, hl=(0, 0, 0), tp=0, head=(0, 0, 0), grip=(-0.66, -1.3, 3.55), wR=0.0, wL=0.0), "sine"),
        (12, dict(hp=8, hl=(0, 0.15, -0.06), tp=10, head=(-2, 0, 0), grip=(-0.62, -1.45, 3.45), wR=1.0, wL=1.0), "out"),
        (20, dict(hp=12, hl=(0, 0.22, -0.1), tp=16, head=(-8, 0, 0), grip=(-0.58, -1.62, 3.06)), "sine"),
        (50, dict(hp=20, hl=(0, 0.34, -0.2), tp=26, head=(-16, 6, 0), grip=(-0.52, -2.72, 3.06)), "out"),
        (56, dict(grip=(-0.52, -2.72, 3.24), head=(-16, 9, 0)), "sine"),
        (64, dict(hp=18, hl=(0, 0.3, -0.18), tp=24, head=(-14, 13, -3), grip=(-0.6, -2.3, 3.6)), "sine"),
        (78, dict(hp=0, hl=(0, 0, 0), tp=0, head=(0, 0, 0), grip=(-0.7, -1.2, 3.6), wR=0.0, wL=0.0), "sine"),
    ]
    return C.param_clip(sk, "SlideReceipt", 78, False, keys, fn)


def tiphat_clip(sk):
    hr = rd(-20, 0, 0)        # fingers continue the forearm, slight wrist bend

    def fn(q):
        hips = q["hp"]
        pose = {"Hips": (rd(hips, 0, 0), (0, 0.04 * hips, 0)), "Torso": rd(q["tp"], 0, 0), "Head": rd(*q["head"])}
        plant(sk, pose)
        coat_follow(pose, 0.0, hips)

        def solve(P):
            tgt = sk.point(sk.fk(P), "Head", BRIM_PINCH) + Vector(q["off"])
            reach_l(sk, P, "R", PINCH_R, tgt, hr, (-1, 0.7, -0.4))
        arm_mix(pose, ARM_R, q["wR"], solve)
        return pose
    keys = [
        (0, dict(head=(0, 0, 0), tp=0, hp=0, off=(-0.3, -0.5, -0.9), wR=0.0), "sine"),
        (14, dict(off=(-0.15, -0.25, -0.35), tp=2, wR=1.0), "out"),
        (22, dict(head=(-4, 0, 0), off=(0, 0, 0)), "sine"),
        (34, dict(head=(24, -4, 0), tp=10, hp=4), "sine"),
        (42, dict(head=(22, -4, 0), tp=9), "sine"),
        (50, dict(head=(0, 0, 0), tp=2, hp=0, off=(-0.1, -0.2, 0.15)), "sine"),
        (60, dict(head=(0, 0, 0), tp=0, hp=0, off=(-0.3, -0.5, -0.9), wR=0.0), "sine"),
    ]
    return C.param_clip(sk, "TipHat", 60, False, keys, fn)


def lunge_clip(sk):
    claw = rd(25, 0, 90)        # palm toward the victim, fingers clawing forward-up
    wind_pose = {"UpperArmR": rd(38, 22, 0), "ForearmR": rd(-70, 0, 0), "HandR": rd(-20, 0, 0)}

    def fn(q):
        pose = {"Hips": (rd(q["hp"], 0, 0), q["hl"]), "Torso": rd(q["tp"], 0, 0), "Head": rd(*q["head"])}
        plant(sk, pose, {"L": (q["footL"],)})
        coat_follow(pose, 0.4, q["hp"])
        for b, r in wind_pose.items():
            pose[b] = r
        C.blend(pose, ARM_R, q["wind"])
        arm_mix(pose, ARM_R, q["wR"], lambda P: reach_l(sk, P, "R", PINCH_R, q["grip"], claw, (-1, 0.5, -0.4)))
        la = q["larm"]
        pose["UpperArmL"] = rd(la, -8 * min(1.0, abs(la) / 10), 0)
        pose["ForearmL"] = rd(-10 * min(1.0, abs(la) / 10), 0, 0)
        pose["HandL"] = rd(-0.4 * la, 0, 0)
        umbrella_clear(sk, pose, 0.08)
        return pose
    rest_ankle = tuple(ANKLE)
    keys = [
        (0, dict(hp=0, hl=(0, 0, 0), tp=0, head=(0, 0, 0), grip=(-0.6, -2.8, 5.6), wR=0.0, wind=0.0, larm=0,
                 footL=rest_ankle), "sine"),
        (10, dict(hp=-8, hl=(0, 0.3, -0.22), tp=-10, head=(-8, 0, 0), wind=1.0, larm=-8), "in"),
        (13, dict(hp=4, hl=(0, -0.6, -0.35), tp=6, head=(-14, 0, 0), grip=(-0.5, -2.8, 5.6), wR=1.0, larm=10,
                  footL=(0.44, -1.0, 0.95)), "out"),
        (16, dict(hp=20, hl=(0, -1.5, -0.62), tp=24, head=(-30, 0, 0), grip=(-0.45, -4.1, 4.4), larm=28,
                  footL=(0.46, -2.05, 0.4)), "sine"),
        (26, dict(hp=22, hl=(0, -1.62, -0.66), tp=26, head=(-32, 4, 0), grip=(-0.42, -4.25, 4.2), larm=30), "sine"),
        (36, dict(hp=8, hl=(0, -0.7, -0.35), tp=10, head=(-12, 0, 0), grip=(-0.8, -2.2, 3.8), larm=12,
                  footL=(0.44, -1.0, 0.9), wind=0.0), "sine"),
        (48, dict(hp=0, hl=(0, 0, 0), tp=0, head=(0, 0, 0), grip=(-1.0, -1.0, 3.2), wR=0.0, larm=0,
                  footL=rest_ankle), "sine"),
    ]
    return C.param_clip(sk, "Lunge", 48, False, keys, fn)


# ======================================================================================

def build():
    sk = C.Skel("MrUsualRig", JOINTS)
    build_model(sk)
    acts = [walk_clip(sk), idle_clip(sk), slide_clip(sk), sit_clip(sk), stalk_clip(sk), tiphat_clip(sk), lunge_clip(sk)]
    C.rest_pose(sk.arm)

    def checks():
        for a, v in ((acts[0], 5.0), (acts[4], 9.0)):
            for s, side in (("L", 1), ("R", -1)):
                for nm, pt in (("heel", (0.42 * side, 0.32, 0.0)), ("toe", (0.42 * side, -0.58, 0.0))):
                    print(f"  [slide] {a.name} Foot{s} {nm}: {C.foot_slide(sk, a, 'Foot' + s, pt, v)}")
        for a in acts:
            print(f"  [floor] {a.name}: lowest point {C.lowest_point(sk, a)}")

    meta = {
        "root": {"center": [0, 4.3, -0.05], "size": [2.4, 2.4, 1.4]},
        "walkSpeed": 5, "stalkSpeed": 9,
        "clipSpeedRef": {"Walk": 5, "StalkWalk": 9},
        "props": {"receipt": "HandR_Receipt: show only during SlideReceipt (hide at events.SlideReceipt.release)"},
        "sit": {"clip": "SitStare", "seatHeight": 1.6, "hipsOverPivot": True,
                "note": "place the pivot on the floor at the booth seat centre, facing the counter"},
        "events": {"SlideReceipt": {"release": 1.8}, "TipHat": {"tip": 1.1}, "Lunge": {"hit": 0.53},
                   "Idle": {"dripHat": 0.8, "dripHem": 2.57}},
    }
    return {"skel": sk, "arm": sk.arm, "actions": acts, "checks": [checks],
            "export": {"rig": sk.arm, "pivot": (0.0, 0.0, 0.0), "meta": meta}}


STRIPS = {
    "Walk": dict(frames=[0, 9, 18, 27]),
    "StalkWalk": dict(frames=[0, 7, 14, 21]),
    "Idle": dict(frames=[0, 18, 60, 90]),
    "SitStare": dict(frames=[0, 60], yaw=-50),
    "SlideReceipt": dict(frames=[0, 20, 50, 64]),
    "TipHat": dict(frames=[14, 22, 34, 50]),
    "Lunge": dict(frames=[10, 13, 16, 36]),
}

if __name__ == "__main__":
    C.run(build, "Creature_MrUsual", "MrUsual", strips=STRIPS)
