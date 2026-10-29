"""PlayerR15 — game-specific player poses on the Roblox R15 joint set (batch H).

Players keep Roblox's own walk/run/jump/idle; these clips are layered on top by the client
BlenderAnimator (ReplicatedStorage.AnimData.PlayerR15):
  full-body  Crouch, CrouchWalk (8 studs/s), Downed, HidePeek   -> key every joint incl. Root
  upper-body CarryCrate, FlashlightAim, Whack                    -> key ONLY the 8 upper joints
Only Root carries translation (authored for HipHeight 2.1924; the game rescales it).

Props are preview-only: the flashlight sits on LeftGripAttachment, the spatula on
RightGripAttachment (Roblox R15 default: hand centre + (0, -0.15, 0), Orientation (-90, 0, 0)),
the crate is held between the hands by its short ends (meta.props gives its RightHand offset).

Env: NS_CLIPS=Crouch,...  author only these (iteration)   NS_STRIPS=all|none|<list>
     NS_EXPORT=1          write anim/PlayerR15.lua          NS_QUICK=<clip>:<f,f,..> quick tiles
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from _common import Pose, Track, Vector, Quaternion, Matrix, qe, qx, qy, qz, QI, LIN  # noqa: E402

ns = C.ns
bpy = C.bpy

EASE = C.EASE_DEFAULT
SIDES = (("Left", 1.0), ("Right", -1.0))       # Blender x sign
ANKLE_Z = C.J["LeftAnkle"].z                    # 0.262
FOOT_HALF = 0.5005                              # foot half length (front/back of the ankle)


def rest_ankle(side):
    return C.J[side + "Ankle"].copy()


# ======================================================================================
# Crouch — idle crouch, feet flat and planted at rest, hips down 1.1
# ======================================================================================
# R15 block legs: the LowerLeg box reaches 0.054 below the ankle and is 0.97 deep, so with a
# flat foot the shin may tilt forward at most ~25 deg before its front-bottom edge goes under
# the floor. A 1.1 drop therefore puts the hips back over the heels (thighs ~horizontal).
CROUCH_DROP = 1.10
SHIN_TILT = 23.0


def crouch_hip_back(drop=CROUCH_DROP, tilt=SHIN_TILT):
    """Root y offset that gives the shin `tilt` with flat feet at rest and hips `drop` down."""
    kn = Vector((0, -1.0097 * math.sin(math.radians(tilt)), ANKLE_Z + 1.0097 * math.cos(math.radians(tilt))))
    hz = C.J["LeftHip"].z - drop
    dz = hz - kn.z
    return kn.y + math.sqrt(0.9207 ** 2 - dz ** 2)


CROUCH_BACK = crouch_hip_back()


def clip_crouch(arm):
    fps, end = 30, 90
    c = C.Clip(arm, "Crouch", end, fps=fps, loop=True)
    glance = Track([(0, 0.0), (16, -3.0), (24, 34.0, ("QUAD", "EASE_OUT")), (40, 29.0),
                    (46, -31.0, ("QUAD", "EASE_OUT")), (63, -26.0), (77, 0.0), (90, 0.0)])
    look_up = Track([(0, 0.0), (16, 0.0), (24, -4.0), (40, -3.0), (46, -5.0), (63, -3.0), (77, 0.0), (90, 0.0)])
    for f in range(0, end + 1, 3):          # Root + legs + torso dense (feet must stay planted)
        t = f / fps
        br = math.sin(2 * math.pi * t / 1.5)            # two breaths per 3 s loop
        p = Pose()
        p.loc = Vector((0.0, CROUCH_BACK, -CROUCH_DROP + 0.018 * br))
        p.q["Root"] = qe(1.0 + 0.4 * br, 0, 0)
        p.q["Waist"] = qe(14 - 1.1 * br, 0, 0.18 * glance(f))
        for side, s in SIDES:
            C.leg_ik(p, side, rest_ankle(side), QI)
        c.key_pose(f, p, ["Root", "Waist", "LeftHip", "LeftKnee", "LeftAnkle",
                          "RightHip", "RightKnee", "RightAnkle"], LIN)
        for side, s in SIDES:
            sway = 2.5 * math.sin(math.radians(glance(f)))
            c.key(side + "Shoulder", f, qe(-24 - 1.4 * br, -s * 9, sway), None, LIN)
            c.key(side + "Elbow", f, qx(-32 - 1.5 * br), None, LIN)
            c.key(side + "Wrist", f, qe(-8, 0, 0), None, LIN)
    for f in glance.frames():
        c.key("Neck", f, qe(-15 + look_up(f), 0, 0.82 * glance(f)), None, glance.ease_at(f))
    c.info = {"drop": CROUCH_DROP, "hipsBack": CROUCH_BACK}
    return c.commit()


# ======================================================================================
# CrouchWalk — sneaking walk at 8 studs/s (60 fps keys, 28-frame cycle = 0.467 s)
# ======================================================================================
CW_SPEED = 8.0
CW_T, CW_FPS, CW_ST = 28, 60, 15          # cycle, fps, stance frames (duty 0.536)
CW_DROP = 1.10
CW_BACK = 0.30                             # hips back (clip space +Y)
CW_YC = CW_BACK - 0.35                     # flat-ankle y at mid-stance (stance spans hips -1.35 .. +0.65)
CW_LAND = 9.0                              # toe-first landing (deg heel-up at contact)
CW_LIFT = 0.10


def _hermite(p0, p1, m0, m1, s):
    h00 = 2 * s ** 3 - 3 * s ** 2 + 1
    h10 = s ** 3 - 2 * s ** 2 + s
    h01 = -2 * s ** 3 + 3 * s ** 2
    h11 = s ** 3 - s ** 2
    return h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1


def cw_root(f):
    ph = 2 * math.pi * f / CW_T
    p = Pose()
    p.loc = Vector((0.04 * math.sin(ph), CW_BACK, -CW_DROP - 0.02 * math.cos(2 * ph)))
    yaw = -5.0 * math.cos(ph)
    roll = 1.6 * math.sin(2 * math.pi * (f - 15) / CW_T)
    p.q["Root"] = qe(3, roll, yaw)
    p.q["Waist"] = qe(10 + 1.0 * math.cos(2 * ph), -0.8 * roll, -0.75 * yaw)
    p.q["Neck"] = qe(-12 - 1.0 * math.cos(2 * ph - 0.5), 0, -0.2 * yaw)
    return p


def cw_toe(k, x):
    """Toe-edge position of a planted foot at stance frame k (moves back with the ground)."""
    dv = CW_SPEED / CW_FPS
    yflat = CW_YC - dv * CW_ST / 2 + dv * k
    return Vector((x, yflat - FOOT_HALF, 0.0))


def cw_sched(k):
    """Minimum heel-up angle through stance: toe-first landing, flat, then a heel peel."""
    if k < 4:
        return CW_LAND * (1 - C.smooth(k / 4))
    if k > CW_ST - 4:
        return 14.0 * C.smooth((k - (CW_ST - 4)) / 4)
    return 0.0


def cw_stance_state(f_abs, side, s, k):
    p = cw_root(f_abs)
    a = C.plant_leg(p, side, cw_toe(k, s * 0.5), alpha_min=cw_sched(k))
    A, q = C.foot_on_toe(cw_toe(k, s * 0.5), a)
    return A, a


def cw_pose(f):
    T = CW_T
    ph = 2 * math.pi * f / T
    p = cw_root(f)
    dv = CW_SPEED / CW_FPS
    for side, s, off in (("Left", 1.0, 0), ("Right", -1.0, T // 2)):
        k = (f - off) % T
        if k <= CW_ST:
            C.plant_leg(p, side, cw_toe(k, s * 0.5), alpha_min=cw_sched(k))
            continue
        A0, a0 = cw_stance_state(off + CW_ST, side, s, CW_ST)
        A1, a1 = cw_stance_state(off + T, side, s, 0)
        dur = T - CW_ST
        u = (k - CW_ST) / dur
        y = _hermite(A0.y, A1.y, 0.0, dv * dur, u)
        a = a0 * (1 - C.smooth(u / 0.45)) + a1 * C.smooth((u - 0.55) / 0.45)
        ra = math.radians(a)
        zfloor = FOOT_HALF * math.sin(ra) + ANKLE_Z * math.cos(ra)     # toe edge on the floor
        z = zfloor + CW_LIFT * math.sin(math.pi * u) ** 0.6
        z0 = z
        while True:                             # floor guard for the swinging shin
            C.leg_ik(p, side, Vector((s * 0.5, y, z)), qx(a))
            if C.min_z(p, [side + "UpperLeg", side + "LowerLeg", side + "Foot"]) >= 0.004:
                break
            if z < z0 + 0.15:
                z += 0.005
            else:
                y -= 0.01
    for side, s in SIDES:
        sw = s * math.cos(ph)                 # left arm forward when the right leg is forward
        p.q[side + "Shoulder"] = qe(-30 + 8 * sw, -s * 9, 0)
        p.q[side + "Elbow"] = qx(-80 - 6 * sw)
        p.q[side + "Wrist"] = qe(32, 0, 0)
    return p


def clip_crouch_walk(arm):
    c = C.Clip(arm, "CrouchWalk", CW_T, fps=CW_FPS, loop=True)
    for f in range(0, CW_T):
        p = cw_pose(f)
        bones = C.LOWER if f % 2 else C.BONES
        c.key_pose(f, p, bones, LIN)
    c.info = {"speed": CW_SPEED}
    return c.commit()


# ======================================================================================
# HidePeek — tucked in a hiding spot: sitting on the floor (hips ~1.6 down), knees up, forearms
# folded across the knees, head peeking over them; slow cautious peeks left and right
# ======================================================================================
HP_FEET = {"Left": Vector((0.51, -0.42, ANKLE_Z)), "Right": Vector((-0.51, -0.42, ANKLE_Z))}
HP_BUTT = ["LeftUpperLeg", "RightUpperLeg", "LowerTorso"]
# arms folded across the knees (hand/elbow targets relative to each knee joint)
HP_ARM = {"hx": 0.62, "hy": -0.85, "hz": 1.04, "ex": 1.60, "ey": -0.15, "ez": 1.04, "dx": -1.0, "dy": -0.55, "dz": -0.05,
          "waist": 10.0, "root": -18.0, "neck": -8.0, "hipy": 0.40, "kp": 0.02}


def hp_pose(f, peek, look, scan, br, A=None):
    """Seated tuck in a hiding spot: butt on the floor (hips ~1.6 down), knees pulled up,
    forearms folded across the knees, head low peeking over them.
    peek -1..1 (+ = lean out to the character's left)."""
    A = A or HP_ARM
    p = Pose()
    p.loc = Vector((0.14 * peek, A["hipy"], -1.6))
    p.q["Root"] = qe(A["root"], 4.0 * peek, 2.0 * peek)

    def legs():
        for side, s in SIDES:
            C.leg_ik(p, side, HP_FEET[side], QI, pole=Vector((s * A["kp"], -1, 0.2)))
    for _ in range(4):                       # butt on the floor, feet planted
        legs()
        p.loc.z += -min(C.min_z(p, HP_BUTT), C.min_z(p, ["LeftLowerLeg", "RightLowerLeg"]) - 0.002)
    p.loc.z += 0.004 * (br + 1) / 2
    legs()
    p.q["Waist"] = qe(A["waist"] - 3.0 * abs(peek) - 1.2 * br, 19 * peek, 9 * peek)
    p.q["Neck"] = qe(A["neck"] + 2 * abs(peek), -9 * peek, look + scan)
    R, P = C.fk(p)
    for side, s in SIDES:
        k = P[side + "Knee"]
        tgt = Vector((s * A["hx"] + 0.52 * peek, k.y + A["hy"], k.z + A["hz"] + 0.012 * br))
        hr = C.aim_rot(Vector((s * A["dx"], A["dy"], A["dz"])), Vector((0, -0.2, 1)))
        elbow = Vector((s * A["ex"] + 0.60 * peek, k.y + A["ey"], k.z + A["ez"]))
        C.arm_ik_elbow(p, side, tgt, hr, elbow, steps=36)
    return p


def clip_hide_peek(arm):
    fps, end = 30, 120
    c = C.Clip(arm, "HidePeek", end, fps=fps, loop=True)
    peek = Track([(0, 0.0), (10, 0.0), (32, 1.0), (52, 1.0), (66, 0.0), (72, 0.0), (94, -1.0), (110, -1.0), (120, 0.0)])
    look = Track([(0, 0.0), (10, 0.0), (32, 12.0), (52, 12.0), (66, 0.0), (72, 0.0), (94, -12.0), (110, -12.0), (120, 0.0)])
    scan = Track([(0, 0.0), (32, 0.0), (40, 9.0), (46, -6.0), (52, 0.0), (94, 0.0), (101, -9.0), (106, 5.0), (110, 0.0), (120, 0.0)])
    for f in range(0, end + 1):
        br = math.sin(2 * math.pi * f / 40)          # shallow, quick breaths
        p = hp_pose(f, peek(f), look(f), scan(f), br)
        c.key_pose(f, p, C.LOWER if f % 2 else C.BONES, LIN)   # Root + legs every frame (planted feet)
    return c.commit()


# ======================================================================================
# Downed — on hands and knees, slumped toward the left arm, right arm reaching out weakly
# ======================================================================================

def dn_pose(f, br, reach, lift):
    p = Pose()
    p.q["Root"] = qe(52 + 1.5 * br, 0, 3)
    # legs: kneeling, thighs near vertical, shins flat behind, toes tucked
    for side, s in SIDES:
        C.set_leg_dirs(p, side, Vector((s * 0.06, -0.20, -1)), Vector((0, 1, 0.05)))
    p.loc = Vector((0.0, 0.10, 0.0))
    C.drop_to_floor(p, ["LeftLowerLeg", "RightLowerLeg", "LeftFoot", "RightFoot"])
    # torso nearly horizontal, sagging and rolled down toward the propping left arm
    C.set_world(p, "Waist", qx(74 + 2.5 * br) @ qz(-13 - 1.0 * br))
    C.set_world(p, "Neck", qx(88 - 26 * lift - 2 * br) @ qz(-4 + 8 * lift))
    # left arm props straight down onto a flat hand
    R, P = C.fk(p)
    sh = P["LeftShoulder"]
    hz = 0.163
    for _ in range(40):                      # palm flat on the floor; nothing of the arm below it
        C.arm_ik(p, "Left", Vector((sh.x + 0.60, sh.y - 0.30, hz)), qz(-14), hinge=Vector((1, 0.3, 0)))
        if C.min_z(p, ["LeftLowerArm", "LeftHand"]) >= 0.004:
            break
        hz += 0.002
    # right arm reaching forward along the floor, weakly lifting and sagging
    sh = P["RightShoulder"]
    tgt = Vector((sh.x - 0.70 - 0.08 * reach + 0.15 * lift, sh.y - 1.40 - 0.22 * reach, sh.z - 0.95 + 0.80 * lift))
    fw = (tgt - sh).normalized()
    droop = fw + Vector((0, 0, -0.55 - 0.25 * (1 - lift)))          # limp wrist
    hr = C.aim_rot(droop, Vector((0, 0, -1)))
    C.arm_ik(p, "Right", tgt, hr, hinge=Vector((1, 0, -0.3)))
    return p


def clip_downed(arm):
    fps, end = 30, 90
    c = C.Clip(arm, "Downed", end, fps=fps, loop=True)
    reach = Track([(0, 0.0), (20, 0.0), (42, 1.0), (54, 1.0), (75, 0.0), (90, 0.0)])
    lift = Track([(0, 0.0), (20, 0.0), (40, 1.0), (52, 0.8), (70, 0.0), (90, 0.0)])
    for f in range(0, end + 1, 2):
        br = math.sin(2 * math.pi * f / 30)          # laboured: 3 heavy breaths in 3 s
        p = dn_pose(f, br, reach(f), lift(f))
        c.key_pose(f, p, C.BONES, LIN)
    return c.commit()


# ======================================================================================
# CarryCrate (upper body) — crate held by its short ends at belly/chest height
# ======================================================================================
# Crate centre in the UpperTorso frame (origin = Waist joint, axes = UpperTorso), Blender axes.
CRATE_IN_TORSO = Vector((0.0, -1.32, 0.52))
CRATE_HALF_W = C.CRATE_SIZE.x / 2                # 1.03: outer face of the rim
HAND_HALF_W = C.PART["LeftHand"][2].x / 2       # 0.492
CRATE_GRIP = Vector((CRATE_HALF_W + HAND_HALF_W, 0.24, 0.05))   # left-hand centre in the crate frame


def crate_matrix(p: Pose, bounce: float, tilt: float) -> Matrix:
    R, P = C.fk(p)
    Rw = R["Waist"].to_matrix().to_4x4()
    M = Matrix.Translation(P["Waist"]) @ Rw @ Matrix.Translation(CRATE_IN_TORSO + Vector((0, 0, bounce))) \
        @ qx(tilt).to_matrix().to_4x4()
    return M


def carry_pose(f, fps=30, T=60):
    t = f / T
    ph = 2 * math.pi * t
    b2 = math.cos(2 * ph)                       # two bounces per loop
    p = Pose()
    p.q["Waist"] = qe(-6.5 + 1.0 * b2, 1.2 * math.sin(ph), 2.0 * math.sin(ph + 0.4))
    p.q["Neck"] = qe(7.0 - 1.0 * math.cos(2 * ph - 0.5), -0.6 * math.sin(ph), -1.5 * math.sin(ph + 0.4))
    M = crate_matrix(p, 0.035 * math.cos(2 * ph - 0.7), 1.2 * math.sin(2 * ph - 1.0))
    Rc = M.to_quaternion()
    for side, s in SIDES:
        tgt = M @ Vector((s * CRATE_GRIP.x, CRATE_GRIP.y, CRATE_GRIP.z))
        # palm flat on the crate end (hand X = crate X); hand pitch follows the forearm
        R, P = C.fk(p)
        hr = Rc
        for _ in range(5):
            C.arm_ik(p, side, tgt, hr, hinge=Rc @ Vector((1, 0, 0)))
            R, P = C.fk(p)
            fore = R[side + "Elbow"] @ Vector((0, 0, -1))
            X = Rc @ Vector((1, 0, 0))
            hr = C.limb_frame(fore - X * fore.dot(X), X)
        C.arm_ik(p, side, tgt, hr, hinge=Rc @ Vector((1, 0, 0)))
    return p, M


def clip_carry_crate(arm):
    fps, end = 30, 60
    c = C.Clip(arm, "CarryCrate", end, fps=fps, loop=True, bones=C.UPPER)
    for f in range(0, end, 3):
        p, M = carry_pose(f, fps, end)
        c.key_pose(f, p, C.UPPER, LIN)
    act = c.commit()
    p0, M0 = carry_pose(0, fps, end)
    act["h_crate_f0"] = [list(r) for r in M0]
    return act


# ======================================================================================
# FlashlightAim (upper body) — LEFT arm raised forward at shoulder height, beam along -Y
# ======================================================================================

def flash_pose(f, T=75):
    t = f / T
    ph = 2 * math.pi * t
    by = 1.4 * math.sin(ph) + 0.5 * math.sin(3 * ph + 0.6)          # beam yaw / pitch sway (deg)
    bp = 0.9 * math.sin(2 * ph + 0.8)
    br = math.sin(2 * ph)
    p = Pose()
    p.q["Waist"] = qe(3 + 0.6 * br, 0, -6 + 0.3 * by)
    R, P = C.fk(p)
    d = Vector((math.sin(math.radians(by)), -math.cos(math.radians(by)), math.sin(math.radians(bp))))
    hr = C.aim_rot(d, Vector((0, 0, 1)))                  # grip forward = down the arm; up = hand front
    sh = P["LeftShoulder"]
    tgt = Vector((sh.x + 0.50, sh.y - 1.69, sh.z - 0.03 + 0.01 * br))
    C.arm_ik(p, "Left", tgt, hr, hinge=Vector((1, 0, -0.2)))
    # head looks along the beam
    R, P = C.fk(p)
    head_world = qz(by) @ qx(-bp + 1.0)
    C.set_world(p, "Neck", head_world)
    # right arm hangs relaxed (free for the spatula)
    p.q["RightShoulder"] = qe(2.5 + 1.2 * br, 4.0, 0)
    p.q["RightElbow"] = qx(-11 - 1.5 * br)
    p.q["RightWrist"] = qx(-4)
    return p


def clip_flashlight_aim(arm):
    fps, end = 30, 75
    c = C.Clip(arm, "FlashlightAim", end, fps=fps, loop=True, bones=C.UPPER)
    for f in range(0, end, 3):
        c.key_pose(f, flash_pose(f, end), C.UPPER, LIN)
    return c.commit()


# ======================================================================================
# Whack (upper body, one-shot) — overhead spatula swing with the right arm, hit at 0.25 s
# ======================================================================================
WHACK_FPS, WHACK_END, WHACK_HIT = 60, 33, 15
# Sparse eased keys. The right arm moves in its own sagittal plane (shoulder/elbow/wrist flex
# about X plus a little abduction), so the 1-stud arm stays outside the torso and head width
# all through the swing; the torso twist and lean carry the power.
WHACK_KEYS = [
    # frame, ease of the segment that starts here, {bone: Euler XYZ deg}
    (0, ("SINE", "EASE_OUT"), {}),
    (9, ("CUBIC", "EASE_IN"), {          # wind-up 0.15 s: arm cocked up and back over the shoulder
        "Waist": (-7, -3, -22), "Neck": (5, 2, 17),
        "RightShoulder": (-160, 9, 0), "RightElbow": (-108, 0, 0), "RightWrist": (-30, 0, 0),
        "LeftShoulder": (-32, -10, 0), "LeftElbow": (-38, 0, 0), "LeftWrist": (-6, 0, 0)}),
    (15, ("QUAD", "EASE_OUT"), {         # impact 0.25 s: snapped down and forward, torso twisted into it
        "Waist": (15, 3, 13), "Neck": (-6, -2, -10),
        "RightShoulder": (-74, 9, 0), "RightElbow": (-6, 0, 0), "RightWrist": (12, 0, 0),
        "LeftShoulder": (20, -12, 0), "LeftElbow": (-26, 0, 0), "LeftWrist": (-4, 0, 0)}),
    (21, ("SINE", "EASE_IN_OUT"), {      # follow-through 0.35 s
        "Waist": (18, 2, 14), "Neck": (-8, -2, -11),
        "RightShoulder": (-50, 12, 0), "RightElbow": (-14, 0, 0), "RightWrist": (6, 0, 0),
        "LeftShoulder": (24, -12, 0), "LeftElbow": (-24, 0, 0), "LeftWrist": (-4, 0, 0)}),
    (33, ("SINE", "EASE_IN_OUT"), {}),   # recovered to rest 0.55 s
]


def _whack_rot(b, r):
    if b == "RightShoulder":          # abduct first (rest frame), then flex: stays out to the side
        return qx(r[0]) @ qy(r[1]) @ qz(r[2])
    return qe(*r)


def clip_whack(arm):
    c = C.Clip(arm, "Whack", WHACK_END, fps=WHACK_FPS, loop=False, bones=C.UPPER)
    for f, ease, rots in WHACK_KEYS:
        for b in C.UPPER:
            c.key(b, f, _whack_rot(b, rots.get(b, (0, 0, 0))), None, ease)
    act = c.commit()
    act["h_hit"] = WHACK_HIT / WHACK_FPS
    return act


# ======================================================================================
CLIPS = {
    "Crouch": clip_crouch,
    "CrouchWalk": clip_crouch_walk,
    "HidePeek": clip_hide_peek,
    "Downed": clip_downed,
    "CarryCrate": clip_carry_crate,
    "FlashlightAim": clip_flashlight_aim,
    "Whack": clip_whack,
}
UPPER_CLIPS = ["CarryCrate", "FlashlightAim", "Whack"]


def props_for(name, arm, act):
    """Preview-only props parented to the hand bones (untagged, not exported)."""
    if name == "FlashlightAim":
        return C.build_flashlight(arm, "Left")
    if name == "Whack":
        return C.build_spatula(arm, "Right")
    if name == "CarryCrate":
        objs = C.build_crate(crate_rest_matrix(arm, act), None, None)
        C.parent_rest(objs, arm, "RightWrist")
        return objs
    return []


def crate_rest_matrix(arm, act):
    """Crate centre frame expressed in the right hand's REST frame (constant: the IK keeps the
    right palm fixed on the crate end)."""
    C.use_action(arm, act)
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    d0 = C.bone_delta(arm, "RightWrist")
    bpy.context.scene.frame_set(0)
    return d0.inverted() @ Matrix(act["h_crate_f0"])


def build():
    ns.reset()
    arm = C.make_rig()
    C.build_body(arm)
    return arm


# ======================================================================================
# Checks
# ======================================================================================
ARMS = C.LIMBS["LeftArm"] + C.LIMBS["RightArm"]
LEGS = C.LIMBS["LeftLeg"] + C.LIMBS["RightLeg"]


def categorise(pen):
    cat = {"armVsTorsoHead": {}, "armVsLeg": {}, "armVsArm": {}, "legVsTorso(fold)": {}, "legVsLeg": {}, "prop": {}}
    for k, v in pen.items():
        a, b = k.split("x")
        if a.startswith("Prop") or b.startswith("Prop"):
            cat["prop"][k] = v
        elif a in ARMS and b in C.CORE:
            cat["armVsTorsoHead"][k] = v
        elif a in ARMS and b in LEGS or b in ARMS and a in LEGS:
            cat["armVsLeg"][k] = v
        elif a in ARMS and b in ARMS:
            cat["armVsArm"][k] = v
        elif a in LEGS and b in C.CORE:
            cat["legVsTorso(fold)"][k] = v
        elif a in LEGS and b in LEGS:
            cat["legVsLeg"][k] = v
    return {c: dict(sorted(((k, round(v, 3)) for k, v in d.items() if v > 0.005), key=lambda kv: -kv[1])) for c, d in cat.items()}


def clip_checks(arm, name, act):
    upper = name in UPPER_CLIPS
    rest_boxes = []
    if name == "FlashlightAim":
        rest_boxes = [("PropFlashlight%d" % i, bx) for i, bx in enumerate(C.tool_rest_boxes("Flashlight", "Left"))]
    elif name == "Whack":
        rest_boxes = [("PropSpatula%d" % i, bx) for i, bx in enumerate(C.tool_rest_boxes("Spatula", "Right"))]
    elif name == "CarryCrate":
        Mr = crate_rest_matrix(arm, act)
        rest_boxes = [("PropCrate%d" % i, bx) for i, bx in enumerate(C.crate_rest_boxes(Mr))]

    def extra(f, R, P):
        return {n: C.posed_boxes([bx], R, P)[0] for n, bx in rest_boxes}
    pairs = C.penetration_pairs(include_legs=True)
    holder = {"FlashlightAim": "LeftHand", "Whack": "RightHand", "CarryCrate": None}.get(name)
    for n, _ in rest_boxes:
        for part in C.PART:
            if name == "CarryCrate" and part in ("LeftHand", "RightHand"):
                continue                         # palms are checked as contact below
            if part == holder or (holder and part == holder.replace("Hand", "LowerArm")):
                continue                         # the tool's handle sits in the fist (Roblox grip)
            pairs.append((n, part))
    sp = CW_SPEED if name == "CrouchWalk" else 0.0
    r = C.measure(arm, act, speed=sp, pairs=pairs, upper_only=upper, extra_obbs=extra if rest_boxes else None)
    out = {"minZ": None if upper else round(r["minZ"], 4), "minZ_part": r["minZ_part"],
           "footSlide": {k: round(v, 4) for k, v in r["slide"].items()},
           "maxSlideSpeed": round(r["maxSlideSpeed"], 4),
           "plantedDrift": {k: round(v, 4) for k, v in r["drift"].items()},
           "penetration": categorise(r["pen"])}
    if name == "CarryCrate":
        out["palmToCrate"] = palm_gap(arm, act, Mr)
    return out


def palm_gap(arm, act, Mr):
    """Inner face of each hand vs the crate's end faces (crate frame x = +-1.03)."""
    res = {}
    for side, s in SIDES:
        gaps, cover = [], []
        for f, R, P in C.eval_clip(arm, act):
            Mc = C.bone_delta(arm, "RightWrist") @ Mr
            inv = Mc.inverted()
            c, Rm, h = C.part_obb(side + "Hand", R, P)
            corners = [c + Rm @ Vector((-s * h.x, sy * h.y, sz * h.z)) for sy in (-1, 1) for sz in (-1, 1)]
            loc = [inv @ v for v in corners]
            gaps += [s * v.x - CRATE_HALF_W for v in loc]
            cover.append((sum(v.y for v in loc) / 4, sum(v.z for v in loc) / 4))
        res[side + "Hand"] = {"gapMin": round(min(gaps), 4), "gapMax": round(max(gaps), 4),
                              "faceCentreInCrate_yz": [round(sum(c[0] for c in cover) / len(cover), 3),
                                                       round(sum(c[1] for c in cover) / len(cover), 3)]}
    return res


# ======================================================================================
# Export + meta
# ======================================================================================

def b2r_cframe(M: Matrix):
    """Blender 4x4 (relative transform) -> Roblox CFrame components {x,y,z,R00..R22}."""
    Rr = C.M_B2R @ M.to_3x3() @ C.M_B2R
    t = C.M_B2R @ M.translation
    vals = [t.x, t.y, t.z] + [Rr[i][j] for i in range(3) for j in range(3)]
    return [round(v, 4) + 0.0 for v in vals]


def crate_meta(arm, act):
    C.use_action(arm, act)
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    R, P = C.blender_pose(arm)
    Mc = Matrix(act["h_crate_f0"]) @ Matrix.Translation(Vector((0, 0, -C.CRATE_SIZE.z / 2)))   # pivot = bottom centre
    hc, hr, _ = C.part_obb("RightHand", R, P)
    H = hr.to_4x4()
    H.translation = hc
    ut, urt, _ = C.part_obb("UpperTorso", R, P)
    U = urt.to_4x4()
    U.translation = ut
    hrp = Matrix.Translation(Vector((0, 0, C.HRP_Y)))
    bpy.context.scene.frame_set(0)
    return {"model": "Kitchen_Crate", "pivot": "bottom centre (asset pivot), label side forward",
            "rightHandToPivot": b2r_cframe(H.inverted() @ Mc),
            "upperTorsoToPivot_f0": b2r_cframe(U.inverted() @ Mc),
            "rootPartToPivot_f0": b2r_cframe(hrp.inverted() @ Mc),
            "note": "weld the crate to RightHand with rightHandToPivot (CFrame components x,y,z,R00..R22): "
                    "both palms then stay on the crate ends through the whole clip"}


def export_all(arm, acts):
    order = ["Crouch", "CrouchWalk", "CarryCrate", "FlashlightAim", "Whack", "Downed", "HidePeek"]
    actions = [acts[n] for n in order if n in acts]
    path = ns.export_animations(arm, C.RIG_NAME, actions)
    meta = {
        "referenceHipHeight": C.HIP_HEIGHT,
        "translationNote": "only Root carries translation; scale it by Humanoid.HipHeight / referenceHipHeight",
        "clipSpeedRef": {"CrouchWalk": CW_SPEED},
        "upperBody": list(UPPER_CLIPS),
        "fullBody": ["Crouch", "CrouchWalk", "Downed", "HidePeek"],
        "upperBodyJoints": list(C.UPPER),
        "events": {"Whack": {"hit": round(WHACK_HIT / WHACK_FPS, 3)}},
        "props": {
            "Flashlight": {"attach": "LeftGripAttachment", "clips": ["FlashlightAim"],
                           "grip": "R15 default: LeftHand (0, -0.15, 0), Orientation (-90, 0, 0); beam = tool LookVector"},
            "Spatula": {"attach": "RightGripAttachment", "clips": ["Whack"],
                        "grip": "R15 default: RightHand (0, -0.15, 0), Orientation (-90, 0, 0)"},
            "Crate": dict(crate_meta(arm, acts["CarryCrate"]), clips=["CarryCrate"]) if "CarryCrate" in acts else None,
        },
    }
    C.add_meta(path, meta)
    return path


# ======================================================================================
# Previews
# ======================================================================================
STRIPS = {
    "Crouch": ([0, 12, 24, 36, 46, 58, 70, 84], ((-35, 10), (-90, 4))),
    "CrouchWalk": ([0, 4, 7, 10, 14, 18, 21, 24], ((-35, 12), (-90, 4))),
    "CarryCrate": ([0, 8, 15, 23, 30, 38, 45, 53], ((-35, 10), (-90, 4))),
    "FlashlightAim": ([0, 12, 25, 37, 50, 62], ((35, 10), (90, 4))),
    "Whack": ([0, 5, 9, 12, 15, 21, 27, 33], ((-35, 10), (-90, 4))),
    "Downed": ([0, 15, 30, 40, 52, 65, 78], ((30, 30), (-90, 4))),
    "HidePeek": ([0, 20, 32, 44, 60, 80, 94, 106], ((0, 12), (-90, 4))),
}
LINEUP = [("Crouch", 24, -35, 14), ("CrouchWalk", 7, -35, 14), ("CarryCrate", 0, -35, 14), ("FlashlightAim", 0, 40, 12),
          ("Whack", 9, -60, 12), ("Whack", 15, -60, 12), ("Downed", 40, 30, 28), ("HidePeek", 40, -20, 14)]


def walk_overlay(arm, act, period_frames):
    """Copy of an upper-body action with a simple in-place walk on the lower joints (preview
    stand-in for Roblox's default walk: legs swing, knees bend, slight bob)."""
    w = act.copy()
    w.name = act.name + "_walkPreview"
    C.use_action(arm, w)
    fps = act["ns_fps"]
    end = act["ns_end"]
    step = 2 if fps >= 60 else 1
    for f in range(0, end + 1, step):
        ph = 2 * math.pi * f / period_frames
        loc = Vector((0, 0, -0.08 + 0.07 * math.cos(2 * ph)))
        rot = {"Root": qe(2, 0, 5 * math.sin(ph))}
        for side, s in SIDES:
            sw = math.sin(ph) * s
            rot[side + "Hip"] = qe(-30 * sw, 0, 0)
            rot[side + "Knee"] = qx(8 + 34 * max(0.0, math.sin(ph * 1 + (0 if s > 0 else math.pi) + math.pi / 2)))
            rot[side + "Ankle"] = qx(-6 * sw)
        for b in C.LOWER:
            pb = arm.pose.bones[b]
            pb.rotation_quaternion = rot[b]
            pb.keyframe_insert("rotation_quaternion", frame=f)
            if b == "Root":
                pb.location = loc
                pb.keyframe_insert("location", frame=f)
    for fc in ns._action_fcurves(w):
        for kp in fc.keyframe_points:
            if any(fc.data_path.startswith(f'pose.bones["{b}"]') for b in C.LOWER):
                kp.interpolation = "LINEAR"
    C.reset_pose(arm)
    return w


def render_previews(arm, acts, which="all"):
    os.makedirs(C.PREV, exist_ok=True)
    props = {n: props_for(n, arm, acts[n]) for n in ("FlashlightAim", "Whack", "CarryCrate") if n in acts}

    def show(name):
        for n, objs in props.items():
            for o in objs:
                o.hide_render = n != name
    out = []
    for name, act in acts.items():
        if which != "all" and name not in which:
            continue
        frames, views = STRIPS[name]
        show(name)
        sp = CW_SPEED if name == "CrouchWalk" else 0.0
        fps = act["ns_fps"]
        title = (f"PlayerR15 {name}  len {act['ns_end'] / fps:.2f}s  loop={bool(act['ns_loop'])}"
                 + ("  upper-body (legs at rest)" if name in UPPER_CLIPS else "  full-body")
                 + (f"  root motion {sp:g} studs/s over a 0.5-stud grid" if sp else ""))
        out.append(C.strip(arm, act, frames, os.path.join(C.PREV, f"PlayerR15_{name}_strip.png"), title,
                           views=views, res=280, speed=sp, extra_objs=props.get(name, []), grid=0.5 if sp else None))
        if name in UPPER_CLIPS:
            period = {"CarryCrate": 30, "FlashlightAim": 25, "Whack": 66}[name]
            w = walk_overlay(arm, act, period)
            out.append(C.strip(arm, w, frames, os.path.join(C.PREV, f"PlayerR15_{name}_walk_strip.png"),
                               f"PlayerR15 {name} layered over a stand-in walk (lower joints NOT part of the clip)",
                               views=views[:1] + ((-90, 4),) if name != "FlashlightAim" else views, res=280,
                               extra_objs=props.get(name, [])))
            bpy.data.actions.remove(w)
    show(None)
    if which == "all" or "lineup" in which:
        out.append(lineup(arm, acts, props))
    return out


def lineup(arm, acts, props):
    from PIL import Image, ImageDraw
    res = 300
    tiles = []
    lo, hi = Vector((-2.4, -3.6, 0.0)), Vector((2.4, 1.6, 5.6))
    for name, f, yaw, pitch in LINEUP:
        if name not in acts:
            continue
        for n, objs in props.items():
            for o in objs:
                o.hide_render = n != name
        act = acts[name]
        C.use_action(arm, act)
        made = C.floor_plane()
        C.setup_workbench(res, res)
        C.camera(lo, hi, yaw, pitch)
        bpy.context.scene.frame_set(f)
        p = os.path.join(C.SCRATCH, f"_lu_{name}_{f}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        for o in made:
            bpy.data.objects.remove(o, do_unlink=True)
        tiles.append((f"{name}  f{f} ({f / act['ns_fps']:.2f}s)", p))
    for objs in props.values():
        for o in objs:
            o.hide_render = False
    sheet = Image.new("RGB", (res * len(tiles), res + 26), (22, 24, 28))
    dr = ImageDraw.Draw(sheet)
    for i, (lab, p) in enumerate(tiles):
        sheet.paste(Image.open(p).convert("RGB"), (i * res, 26))
        dr.text((i * res + 6, 7), lab, fill=(235, 235, 235))
        os.remove(p)
    out = os.path.join(C.PREV, "_lineup.png")
    sheet.save(out)
    bpy.context.scene.frame_set(0)
    return out


def quick(arm, act, frames, name, views=((-35, 10), (90, 6)), speed=0.0, extra=(), grid=None):
    out = os.path.join(C.SCRATCH, f"q_{name}.png")
    return C.strip(arm, act, frames, out, f"{name} (draft)", views=views, res=240, speed=speed,
                   extra_objs=extra, grid=grid)


if __name__ == "__main__":
    arm = build()
    want = os.environ.get("NS_CLIPS")
    names = want.split(",") if want else list(CLIPS)
    acts = {n: CLIPS[n](arm) for n in names}
    arm.animation_data.action = None
    C.reset_pose(arm)
    report = {}
    if os.environ.get("NS_MEASURE", "1") == "1":
        for n, act in acts.items():
            report[n] = clip_checks(arm, n, act)
            print(f"[{n}]", json.dumps(report[n]))
    if os.environ.get("NS_EXPORT") == "1" and not want:
        path = export_all(arm, acts)
        data, mod = C.check_module(path, UPPER_CLIPS)
        report["_module"] = mod
        report["_moduleBytes"] = os.path.getsize(path)
        print("[export]", path, os.path.getsize(path), "bytes")
        for n, m in mod.items():
            print(f"[module {n}]", json.dumps(m))
    if report:
        with open(os.path.join(C.SCRATCH, "checks.json"), "w") as fh:
            json.dump(report, fh, indent=1)
    which = os.environ.get("NS_STRIPS", "none")
    if which != "none":
        for pth in render_previews(arm, acts, which if which == "all" else which.split(",")):
            print("[preview]", pth)
    q = os.environ.get("NS_QUICK")
    if q:
        for item in q.split(";"):
            n, fr = item.split(":")
            frames = [int(x) for x in fr.split(",")]
            sp = CW_SPEED if n == "CrouchWalk" else 0.0
            print("quick:", quick(arm, acts[n], frames, n, speed=sp, grid=0.5 if sp else None,
                                  extra=props_for(n, arm, acts[n])))
