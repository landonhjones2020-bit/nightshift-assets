"""Shared helpers for batch H (player R15 poses, rig "PlayerR15").

Contents
  * skeleton : the Roblox standard 1.0-scale block R15 joint set (15 joints) as a Blender
               armature; every bone points +Y with roll 0, so bone-local axes = world axes and
               the rest pose = identity Transform on every Motor6D.
  * body     : grey preview body (rounded boxes per R15 part) bound to the bones, plus the
               preview-only props (crate, spatula, flashlight) and the Roblox grip attachments.
  * math     : pure-mathutils forward kinematics that matches Blender's pose evaluation, two-bone
               leg IK (knee pole, foot orientation) and arm IK (R15 shoulder offset, elbow hinge,
               hand orientation).
  * keying   : Clip -> Blender action (quaternion sign continuity, per-key easing). Upper-body
               clips key ONLY the 8 upper joints, so the exporter leaves the rest out.
  * checks   : foot slip / floor / OBB penetration (SAT) / export sanity.
  * review   : Workbench pose strips (cheap on the shared CPU).

Coordinates are Blender world: 1 unit = 1 stud, Z up, the character faces -Y, its LEFT side is
+X (Roblox left = -X; x_r = -x_b, y_r = z_b, z_r = y_b). The floor is z = 0, the
HumanoidRootPart centre is z = 3.1924 (HipHeight 2.1924).

nslib is used unchanged: export_animations writes anim/PlayerR15.lua; add_meta() then appends
the clip meta table to that module (nslib's exporter has no meta argument).
"""
from __future__ import annotations

import math
import os
import re
import sys

import bpy  # noqa: F401
from mathutils import Matrix, Quaternion, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import nslib as ns  # noqa: E402

BATCH = "H_player"
RIG_NAME = "PlayerR15"
HRP_Y = 3.1924                 # HumanoidRootPart centre above the floor
HIP_HEIGHT = 2.1924            # Humanoid.HipHeight of the reference body
PREV = os.path.join(ns.REPO, "..", "previews", BATCH)
SCRATCH = os.environ.get("NS_H_SCRATCH",
                         "/tmp/claude-0/-home-claude/bee54a24-967a-5993-94e6-c9b5acdf45a4/scratchpad/h_player")

# --------------------------------------------------------------------------------------
# Skeleton (Roblox coordinates relative to the HRP centre, from the brief)
# --------------------------------------------------------------------------------------
JOINTS_R = {
    "Root": (0, -1.0, 0), "Waist": (0, -0.6, 0), "Neck": (0, 1.098, 0),
    "LeftShoulder": (-0.9716, 0.8465, 0), "RightShoulder": (0.9716, 0.8465, 0),
    "LeftElbow": (-1.4717, 0.0727, 0), "RightElbow": (1.4721, 0.0726, 0),
    "LeftWrist": (-1.4717, -0.7343, 0), "RightWrist": (1.4721, -0.7343, 0),
    "LeftHip": (-0.5, -1.0, 0), "RightHip": (0.5, -1.0, 0),
    "LeftKnee": (-0.5, -1.9207, 0), "RightKnee": (0.5, -1.9206, 0),
    "LeftAnkle": (-0.5, -2.9304, 0), "RightAnkle": (0.5, -2.9304, 0),
}
PARENT = {"Root": None, "Waist": "Root", "Neck": "Waist",
          "LeftShoulder": "Waist", "RightShoulder": "Waist",
          "LeftElbow": "LeftShoulder", "RightElbow": "RightShoulder",
          "LeftWrist": "LeftElbow", "RightWrist": "RightElbow",
          "LeftHip": "Root", "RightHip": "Root", "LeftKnee": "LeftHip", "RightKnee": "RightHip",
          "LeftAnkle": "LeftKnee", "RightAnkle": "RightKnee"}
BONES = list(JOINTS_R)         # brief order; every parent precedes its children
UPPER = ["Waist", "Neck", "LeftShoulder", "LeftElbow", "LeftWrist",
         "RightShoulder", "RightElbow", "RightWrist"]
LOWER = ["Root", "LeftHip", "LeftKnee", "LeftAnkle", "RightHip", "RightKnee", "RightAnkle"]

# part: (bone, centre_r, size_r)
PARTS_R = {
    "UpperTorso": ("Waist", (0, 0.249, 0), (1.943, 1.698, 1.004)),
    "LowerTorso": ("Root", (0, -0.8, 0), (1.991, 0.401, 1.004)),
    "Head": ("Neck", (0, 1.674, 0), (1.159, 1.182, 1.161)),
    "LeftUpperArm": ("LeftShoulder", (-1.472, 0.428, 0), (1.0, 1.242, 1.0)),
    "RightUpperArm": ("RightShoulder", (1.472, 0.428, 0), (1.0, 1.242, 1.0)),
    "LeftLowerArm": ("LeftElbow", (-1.472, -0.202, 0), (1.0, 1.118, 1.0)),
    "RightLowerArm": ("RightElbow", (1.472, -0.202, 0), (1.0, 1.118, 1.0)),
    "LeftHand": ("LeftWrist", (-1.472, -0.866, 0), (0.984, 0.316, 1.028)),
    "RightHand": ("RightWrist", (1.472, -0.866, 0), (0.984, 0.316, 1.028)),
    "LeftUpperLeg": ("LeftHip", (-0.5, -1.471, 0), (0.993, 1.363, 0.973)),
    "RightUpperLeg": ("RightHip", (0.5, -1.471, 0), (0.993, 1.363, 0.973)),
    "LeftLowerLeg": ("LeftKnee", (-0.5, -2.334, 0), (0.993, 1.301, 0.973)),
    "RightLowerLeg": ("RightKnee", (0.5, -2.334, 0), (0.993, 1.301, 0.973)),
    "LeftFoot": ("LeftAnkle", (-0.5, -3.036, 0), (1.009, 0.312, 1.001)),
    "RightFoot": ("RightAnkle", (0.5, -3.036, 0), (1.009, 0.312, 1.001)),
}

M_B2R = ns.M_B2R


def r2b(v) -> Vector:
    """Roblox point relative to the HRP centre -> Blender world point."""
    return Vector((-v[0], v[2], v[1] + HRP_Y))


def r2b_dir(v) -> Vector:
    return Vector((-v[0], v[2], v[1]))


def r2b_size(s) -> Vector:
    return Vector((s[0], s[2], s[1]))


J = {b: r2b(p) for b, p in JOINTS_R.items()}
PART = {n: (b, r2b(c), r2b_size(s)) for n, (b, c, s) in PARTS_R.items()}
SIDE_SIGN = {"Left": 1.0, "Right": -1.0}       # Blender x sign of each side


def make_rig(name="PlayerR15Rig"):
    spec = [(b, PARENT[b], tuple(J[b]), tuple(J[b] + Vector((0, 0.25, 0)))) for b in BONES]
    return ns.make_armature(name, spec)


# --------------------------------------------------------------------------------------
# Preview body + props
# --------------------------------------------------------------------------------------
GREY = "#BDBCC0"          # light neutral avatar grey (torso, head, hands)
GREY_MD = "#A3A2A5"       # Roblox "Medium stone grey" (arms)
GREY_DK = "#8C8B91"       # legs
EYE = "#2A2A2E"


def build_body(arm):
    """Rounded-box R15 body bound rigidly to the bones (tagged parts, preview only)."""
    objs = []
    for name, (bone, c, s) in PART.items():
        bev = 0.06 if "Hand" in name or "Foot" in name else 0.08
        if name == "Head":
            bev = 0.16
        o = ns.box(tuple(s), loc=tuple(c), bevel=bev, segments=2, name=name)
        col = GREY if ("Torso" in name or name == "Head" or "Hand" in name) else GREY_DK if ("Leg" in name or "Foot" in name) else GREY_MD
        ns.tag(o, name, col)
        ns.bind(o, arm, bone)
        objs.append(o)
    # face marker so head direction reads in the strips
    hc = PART["Head"][1]
    hs = PART["Head"][2]
    for sx, nm in ((1, "EyeL"), (-1, "EyeR")):
        e = ns.box((0.13, 0.04, 0.22), loc=(sx * 0.22, hc.y - hs.y / 2 - 0.005, hc.z + 0.08), bevel=0.02, name=nm)
        ns.tag(e, nm, EYE)
        ns.bind(e, arm, "Neck")
        objs.append(e)
    m = ns.box((0.36, 0.04, 0.07), loc=(0, hc.y - hs.y / 2 - 0.005, hc.z - 0.22), bevel=0.02, name="Mouth")
    ns.tag(m, "Mouth", EYE)
    ns.bind(m, arm, "Neck")
    objs.append(m)
    bpy.context.view_layer.update()
    return objs


# Roblox R15 grip attachments (hand-local CFrame): (0, -0.15, 0) with Orientation (-90, 0, 0).
# A held tool is pivoted on the attachment: its forward (-Z) runs down the arm, its up (+Y)
# along the hand's front.
GRIP_POS_R = Vector((0, -0.15, 0))
GRIP_ROT_R = Matrix.Rotation(math.radians(-90), 3, "X")


def r_cf_to_b(rot_r: Matrix, pos_r: Vector) -> Matrix:
    """Roblox-axes rotation/offset -> Blender 4x4 (no HRP shift: for local frames)."""
    R = M_B2R @ rot_r @ M_B2R
    t = M_B2R @ pos_r
    M = R.to_4x4()
    M.translation = t
    return M


def hand_rest_matrix(side) -> Matrix:
    M = Matrix.Identity(4)
    M.translation = PART[side + "Hand"][1]
    return M


def grip_rest_matrix(side) -> Matrix:
    """Blender world matrix of <Side>GripAttachment in the rest pose."""
    return hand_rest_matrix(side) @ r_cf_to_b(GRIP_ROT_R, GRIP_POS_R)


def _prop_box(size_r, centre_r, col, mat="SmoothPlastic", bevel=0.03, name="Prop"):
    """Box given in a tool's own Roblox model frame (pivot = grip point)."""
    o = ns.box(tuple(r2b_size(size_r)), loc=tuple(M_B2R @ Vector(centre_r)), bevel=bevel, segments=2, name=name)
    o.data.materials.append(ns.material(col, mat))
    o["h_prop"] = True
    return o


def _place(objs, M: Matrix, arm=None, bone=None):
    bpy.context.view_layer.update()          # matrix_world of freshly created objects is stale
    for o in objs:
        o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()
    if arm is not None:
        parent_rest(objs, arm, bone)
    return objs


def parent_rest(objs, arm, bone):
    """Parent objects (placed for the REST pose) to a bone, keeping their rest placement."""
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    for o in objs:
        mw = o.matrix_world.copy()
        o.parent = arm
        o.parent_type = "BONE"
        o.parent_bone = bone
        bpy.context.view_layer.update()
        o.matrix_world = mw
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()


def bone_delta(arm, bone) -> Matrix:
    """World transform of a bone relative to its rest pose (current evaluated frame)."""
    pb = arm.pose.bones[bone]
    return arm.matrix_world @ pb.matrix @ arm.data.bones[bone].matrix_local.inverted()


def build_flashlight(arm=None, side="Left"):
    """Kitchen_Flashlight proxy (A_kitchen part boxes) on <side>GripAttachment."""
    objs = [_prop_box((0.45, 0.439, 1.1), (0, 0, -0.05), "#2C2C3D", name="FL_Body"),
            _prop_box((0.304, 0.343, 0.974), (0, 0.023, 0.277), "#18181E", name="FL_Rubber"),
            _prop_box((0.49, 0.478, 0.1), (0, 0, -0.63), "#C9CED3", "Metal", 0.02, name="FL_Bezel"),
            _prop_box((0.39, 0.38, 0.065), (0, 0, -0.632), "#FFE9A8", "Neon", 0.01, name="FL_Lens")]
    return _place(objs, grip_rest_matrix(side), arm, side + "Wrist")


def build_spatula(arm=None, side="Right"):
    """Kitchen_Spatula proxy on <side>GripAttachment."""
    objs = [_prop_box((0.22, 0.151, 0.78), (0, 0, 0), "#2C2C3D", name="SP_Handle"),
            _prop_box((0.143, 0.1, 0.62), (0, -0.04, -0.6), "#C9CED3", "Metal", 0.02, name="SP_Neck"),
            _prop_box((0.66, 0.035, 0.76), (0, -0.142, -1.17), "#C9CED3", "Metal", 0.012, name="SP_Blade")]
    return _place(objs, grip_rest_matrix(side), arm, side + "Wrist")


CRATE_SIZE = Vector((2.06, 1.46, 1.03))     # Blender (width x, depth y, height z); Kitchen_Crate
CRATE_BODY = Vector((2.0, 1.4, 1.0))


def build_crate(M_world: Matrix, arm=None, bone=None):
    """Kitchen_Crate proxy; M_world = crate CENTRE frame (Blender) in the rest-pose scene."""
    objs = []

    def bx(size, loc, col, bev=0.03, name="Crate"):
        o = ns.box(size, loc=loc, bevel=bev, segments=2, name=name)
        o.data.materials.append(ns.material(col))
        o["h_prop"] = True
        objs.append(o)
        return o
    h = CRATE_SIZE.z / 2
    bx(tuple(CRATE_BODY), (0, 0, -h + 0.5), "#4FA04A", name="CR_Body")
    bx((2.06, 1.46, 0.12), (0, 0, h - 0.06), "#3B7D37", 0.02, name="CR_Rim")
    for sx in (-1, 1):   # handle slots on both short ends (dark insets)
        bx((0.02, 0.55, 0.2), (sx * 1.0, 0, -h + 0.75), "#1D3B1B", 0.0, name="CR_Slot")
    bx((0.95, 0.02, 0.26), (0, -0.71, -h + 0.7), "#F3EEE2", 0.005, name="CR_Label")
    return _place(objs, M_world, arm, bone)


# --------------------------------------------------------------------------------------
# Math: forward kinematics + IK (Blender world, rest frames = world axes)
# --------------------------------------------------------------------------------------
QI = Quaternion()


def qx(deg):
    return Quaternion((1, 0, 0), math.radians(deg))


def qy(deg):
    return Quaternion((0, 1, 0), math.radians(deg))


def qz(deg):
    return Quaternion((0, 0, 1), math.radians(deg))


def qe(x=0.0, y=0.0, z=0.0):
    """Euler XYZ degrees (bone-local = world axes): X+ tips an upright bone forward / swings a
    hanging limb back, Y+ tilts the top toward +X (character's left), Z+ turns the face left."""
    from mathutils import Euler
    return Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ").to_quaternion()


class Pose:
    def __init__(self, q=None, loc=None):
        self.q = dict(q or {})
        self.loc = Vector(loc) if loc is not None else Vector((0, 0, 0))

    def copy(self):
        return Pose({k: v.copy() for k, v in self.q.items()}, self.loc.copy())

    def get(self, b):
        return self.q.get(b, QI)


def fk(pose: Pose):
    """World rotation (Quaternion) and joint position (Vector) of every bone."""
    R, P = {}, {}
    for b in BONES:
        p = PARENT[b]
        qb = pose.get(b)
        if p is None:
            R[b] = qb.copy()
            P[b] = J[b] + pose.loc
        else:
            R[b] = R[p] @ qb
            P[b] = P[p] + R[p] @ (J[b] - J[p])
    return R, P


def part_obb(name, R, P):
    """(centre, 3x3 rotation, half extents) of a part at a pose."""
    bone, c, s = PART[name]
    rot = R[bone].to_matrix()
    return P[bone] + rot @ (c - J[bone]), rot, s / 2


def basis(a: Vector, b: Vector) -> Matrix:
    a = a.normalized()
    b = (b - a * b.dot(a)).normalized()
    return Matrix((a, b, a.cross(b))).transposed()


def leg_ik(pose: Pose, side: str, ankle: Vector, foot_rot: Quaternion = QI, pole=Vector((0, -1, 0))):
    """Two-bone leg IK. Puts the <side>Ankle joint at `ankle` (world) with the foot at world
    rotation `foot_rot`; the knee bends toward `pole`. Returns the reach slack (studs, <0 if
    the target was out of reach and clamped)."""
    hip, knee, ank = side + "Hip", side + "Knee", side + "Ankle"
    R, P = fk(pose)
    H = P[hip]
    a = (J[knee] - J[hip]).length
    b = (J[ank] - J[knee]).length
    D = Vector(ankle) - H
    d = D.length
    slack = a + b - d
    d = min(max(d, abs(a - b) + 1e-4), a + b - 1e-5)
    u = D.normalized()
    v = Vector(pole) - u * Vector(pole).dot(u)
    v.normalize()
    ca = (a * a + d * d - b * b) / (2 * a * d)
    sa = math.sqrt(max(0.0, 1 - ca * ca))
    K = H + a * (ca * u + sa * v)
    A = H + u * d
    X = v.cross(u).normalized()

    def frame(down):
        Z = -down.normalized()
        Y = Z.cross(X)
        return Matrix((X, Y, Z)).transposed().to_quaternion()
    Rt = frame(K - H)
    Rs = frame(A - K)
    pose.q[hip] = R["Root"].inverted() @ Rt
    pose.q[knee] = Rt.inverted() @ Rs
    pose.q[ank] = Rs.inverted() @ Quaternion(foot_rot)
    return slack


HAND_OFF = {s: PART[s + "Hand"][1] - J[s + "Wrist"] for s in ("Left", "Right")}


def arm_ik(pose: Pose, side: str, hand_pos: Vector, hand_rot: Quaternion, hinge=Vector((1, 0, 0))):
    """Arm IK for the R15 arm (shoulder joint 0.5 inside the arm axis). Places the <side>Hand
    centre at `hand_pos` with world rotation `hand_rot`; the elbow is a hinge about the upper
    arm's local X (flexion swings the forearm forward); `hinge` = desired world direction of
    the upper arm's local +X (swivel). Returns reach slack."""
    sh, el, wr = side + "Shoulder", side + "Elbow", side + "Wrist"
    R, P = fk(pose)
    S = P[sh]
    hand_rot = Quaternion(hand_rot)
    W = Vector(hand_pos) - hand_rot @ HAND_OFF[side]
    u0 = J[el] - J[sh]
    l0 = J[wr] - J[el]
    D = W - S
    d = D.length

    def vlen(phi):
        return (u0 + qx(-phi) @ l0).length
    lo, hi = 0.0, 170.0
    slack = vlen(0.0) - d
    if d >= vlen(0.0):
        phi = 0.0
    elif d <= vlen(170.0):
        phi = 170.0
    else:
        for _ in range(50):
            mid = (lo + hi) / 2
            if vlen(mid) > d:
                lo = mid
            else:
                hi = mid
        phi = (lo + hi) / 2
    v = u0 + qx(-phi) @ l0
    Rs = (basis(D, Vector(hinge)) @ basis(v, Vector((1, 0, 0))).transposed()).to_quaternion()
    pose.q[sh] = R["Waist"].inverted() @ Rs
    pose.q[el] = qx(-phi)
    Re = Rs @ pose.q[el]
    pose.q[wr] = Re.inverted() @ hand_rot
    return slack


def arm_ik_wrist(pose: Pose, side: str, hand_pos: Vector, wrist_local: Quaternion = QI,
                 hinge=Vector((1, 0, 0)), iters=6):
    """Arm IK where the hand keeps a given LOCAL wrist rotation (relative to the forearm)."""
    R, P = fk(pose)
    hand_rot = R[side + "Wrist"]
    slack = 0.0
    for _ in range(iters):
        slack = arm_ik(pose, side, hand_pos, hand_rot, hinge)
        R, P = fk(pose)
        hand_rot = R[side + "Elbow"] @ Quaternion(wrist_local)
    arm_ik(pose, side, hand_pos, hand_rot, hinge)
    return slack


def aim_rot(down_dir: Vector, front_dir: Vector) -> Quaternion:
    """World rotation for a limb part whose local -Z (down the limb) points along down_dir and
    whose local -Y (front at rest) points as close as possible to front_dir."""
    Z = -Vector(down_dir).normalized()
    Yn = -(Vector(front_dir) - Z * Vector(front_dir).dot(Z)).normalized()
    X = Yn.cross(Z)
    return Matrix((X, Yn, Z)).transposed().to_quaternion()


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def slerp(qa, qb, t):
    return Quaternion(qa).slerp(Quaternion(qb), t)


# --------------------------------------------------------------------------------------
# Keying
# --------------------------------------------------------------------------------------
EASE_DEFAULT = ("SINE", "EASE_IN_OUT")


def reset_pose(arm):
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)


def use_action(arm, act):
    """Assign an action and clear every pose channel first (unkeyed bones go back to rest)."""
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and len(getattr(act, "slots", [])) > 0:
        arm.animation_data.action_slot = act.slots[0]
    reset_pose(arm)


LIN = ("LINEAR", "EASE_IN_OUT")


class Clip:
    """Per-bone keys -> one Blender action. `bones` = the joints this clip keys (upper-body
    clips pass UPPER, so the other joints get no f-curves and are absent from the export).
    Loops: every keyed bone must have a key at 0; the end key is copied from frame 0."""

    def __init__(self, arm, name, end, fps=30, loop=True, bones=None):
        self.arm, self.name, self.end, self.fps, self.loop = arm, name, end, fps, loop
        self.bones = list(bones or BONES)
        self.keys: dict[str, dict[int, tuple]] = {b: {} for b in self.bones}
        self.info: dict = {}

    def key(self, bone, f, q, loc=None, ease=EASE_DEFAULT):
        if bone not in self.keys:
            return
        self.keys[bone][int(round(f))] = (Quaternion(q), None if loc is None else Vector(loc), ease)

    def key_pose(self, f, pose: Pose, bones=None, ease=EASE_DEFAULT):
        for b in (bones or self.bones):
            if b in self.keys:
                self.key(b, f, pose.get(b), pose.loc if b == "Root" else None, ease)

    def commit(self):
        arm = self.arm
        act = ns.new_action(arm, self.name, 0, self.end, loop=self.loop, fps=self.fps)
        self.act = act
        for b in self.bones:
            ks = self.keys[b]
            assert 0 in ks, f"{self.name}: {b} has no key at 0"
            if self.loop:
                ks[self.end] = ks[0]
            assert self.end in ks, f"{self.name}: {b} has no key at the end"
            pb = arm.pose.bones[b]
            prev = None
            for f in sorted(ks):
                q, loc, ease = ks[f]
                q = q.normalized()
                if prev is not None and q.dot(prev) < 0:
                    q = Quaternion((-q.w, -q.x, -q.y, -q.z))
                pb.rotation_quaternion = q
                pb.keyframe_insert("rotation_quaternion", frame=f)
                if b == "Root":
                    pb.location = loc if loc is not None else Vector()
                    pb.keyframe_insert("location", frame=f)
                prev = q
        for fc in ns._action_fcurves(act):
            m = re.match(r'pose\.bones\["([^"]+)"\]', fc.data_path)
            bn = m.group(1)
            for kp in fc.keyframe_points:
                f = int(round(kp.co.x))
                interp, d = self.keys[bn][f][2]
                kp.interpolation = interp
                kp.easing = d
            fc.update()
        reset_pose(arm)
        return act


# --------------------------------------------------------------------------------------
# Authoring curves: (t, value, ease) tracks evaluated like the game's per-segment easing
# --------------------------------------------------------------------------------------

def ease_fn(interp, d):
    if interp == "LINEAR":
        return lambda s: s
    if interp == "CONSTANT":
        return lambda s: 0.0
    p = {"SINE": None, "QUAD": 2, "CUBIC": 3, "QUART": 4, "QUINT": 5}.get(interp, None)
    if p is None:
        fin = lambda s: 1 - math.cos(s * math.pi / 2)   # noqa: E731
    else:
        fin = lambda s: s ** p                         # noqa: E731
    if d == "EASE_IN":
        return fin
    if d == "EASE_OUT":
        return lambda s: 1 - fin(1 - s)
    return lambda s: fin(2 * s) / 2 if s < 0.5 else 1 - fin(2 - 2 * s) / 2


class Track:
    """Keyed scalar/vector curve. keys = [(frame, value, ease)] (ease of the segment that
    starts at that key)."""

    def __init__(self, keys):
        self.keys = sorted(((k[0], k[1], k[2] if len(k) > 2 else EASE_DEFAULT) for k in keys), key=lambda k: k[0])

    def __call__(self, f):
        ks = self.keys
        if f <= ks[0][0]:
            return ks[0][1]
        for (f0, v0, e), (f1, v1, _) in zip(ks, ks[1:]):
            if f <= f1:
                s = ease_fn(*e)((f - f0) / (f1 - f0)) if f1 > f0 else 1.0
                if isinstance(v0, (tuple, list, Vector)):
                    return type(v0)(a + (b - a) * s for a, b in zip(v0, v1)) if not isinstance(v0, Vector) else v0.lerp(v1, s)
                return v0 + (v1 - v0) * s
        return ks[-1][1]

    def frames(self):
        return [k[0] for k in self.keys]

    def ease_at(self, f):
        for k in self.keys:
            if k[0] == f:
                return k[2]
        return EASE_DEFAULT


def set_frame(arm, act, f):
    use_action(arm, act)
    bpy.context.scene.frame_set(int(f))
    bpy.context.view_layer.update()


def blender_pose(arm):
    """(R, P) from the evaluated Blender pose (same structure as fk())."""
    R, P = {}, {}
    for b in BONES:
        pb = arm.pose.bones[b]
        M = arm.matrix_world @ pb.matrix
        R[b] = M.to_quaternion()
        P[b] = M.translation.copy()
    return R, P


# --------------------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------------------

def sat_depth(A, B) -> float:
    """Penetration depth of two OBBs (centre, rot3, half). >0 overlap (min translation),
    <=0 separated (largest separating gap, negated)."""
    ca, Ra, ha = A
    cb, Rb, hb = B
    axes = [Ra.col[i].copy() for i in range(3)] + [Rb.col[i].copy() for i in range(3)]
    for i in range(3):
        for j in range(3):
            c = Ra.col[i].cross(Rb.col[j])
            if c.length > 1e-6:
                axes.append(c.normalized())
    T = cb - ca
    best = 1e9
    for L in axes:
        ra = sum(ha[i] * abs(Ra.col[i].dot(L)) for i in range(3))
        rb = sum(hb[i] * abs(Rb.col[i].dot(L)) for i in range(3))
        o = ra + rb - abs(T.dot(L))
        best = min(best, o)
    return best


LIMBS = {"LeftArm": ["LeftUpperArm", "LeftLowerArm", "LeftHand"],
         "RightArm": ["RightUpperArm", "RightLowerArm", "RightHand"],
         "LeftLeg": ["LeftUpperLeg", "LeftLowerLeg", "LeftFoot"],
         "RightLeg": ["RightUpperLeg", "RightLowerLeg", "RightFoot"]}
CORE = ["UpperTorso", "LowerTorso", "Head"]
# parts that share a joint (their overlap is the rig's own seam, reported separately)
ADJ = {("LeftUpperArm", "UpperTorso"), ("RightUpperArm", "UpperTorso"),
       ("LeftUpperLeg", "LowerTorso"), ("RightUpperLeg", "LowerTorso"),
       ("Head", "UpperTorso"), ("LowerTorso", "UpperTorso")}


def penetration_pairs(include_legs=True):
    pairs = []
    limbs = [k for k in LIMBS if include_legs or "Arm" in k]
    for k in limbs:
        for p in LIMBS[k]:
            for c in CORE:
                if (p, c) in ADJ:
                    continue
                pairs.append((p, c))
    names = list(limbs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            for p in LIMBS[names[i]]:
                for q in LIMBS[names[j]]:
                    pairs.append((p, q))
    return pairs


def obbs_at(R, P):
    return {n: part_obb(n, R, P) for n in PART}


def tagged_vertices(arm, names):
    """{part: (N,3) rest-pose world vertices} of the evaluated preview meshes."""
    import numpy as np
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    for o in ns._tagged_objects():
        if o["ns_part"] not in names:
            continue
        me = o.evaluated_get(dg).to_mesh()
        M = o.matrix_world
        out[o["ns_part"]] = (o.get("ns_bone"), np.array([tuple(M @ v.co) for v in me.vertices]))
        o.evaluated_get(dg).to_mesh_clear()
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()
    return out


def posed_pts(arm, bone, pts):
    import numpy as np
    pb = arm.pose.bones[bone]
    M = arm.matrix_world @ pb.matrix @ arm.data.bones[bone].matrix_local.inverted()
    A = np.array(M)
    return pts @ A[:3, :3].T + A[:3, 3]


# --------------------------------------------------------------------------------------
# Review renders (Workbench: ~1 s per tile, light on the shared CPU)
# --------------------------------------------------------------------------------------

def setup_workbench(res_x, res_y):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x = res_x
    sc.render.resolution_y = res_y
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_shadows = False
    sh.shadow_intensity = 0.45
    sh.show_cavity = True
    sh.cavity_type = "WORLD"
    sh.cavity_ridge_factor = 0.6
    sh.cavity_valley_factor = 0.8
    sh.show_object_outline = True
    sh.object_outline_color = (0.05, 0.05, 0.06)
    sc.display.light_direction = (0.45, -0.55, 0.7)
    sc.display.shadow_shift = 0.05
    sc.display.render_aa = "8"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.55
    sh.studio_light = "paint.sl"
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.color = (0.05, 0.055, 0.065)


def camera(lo: Vector, hi: Vector, yaw_deg: float, pitch_deg: float, fov_deg=28.0, aspect=1.0, margin=1.06):
    for o in list(bpy.context.scene.objects):
        if o.name.startswith("PreviewCam"):
            bpy.data.objects.remove(o, do_unlink=True)
    ctr = (lo + hi) / 2
    yaw, pitch = math.radians(yaw_deg), math.radians(pitch_deg)
    fwd = -Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    right = fwd.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(fwd).normalized()
    # fit the 8 bbox corners in view (vertical fov = fov_deg)
    t = math.tan(math.radians(fov_deg) / 2)
    dist = 0.0
    for x in (lo.x, hi.x):
        for y in (lo.y, hi.y):
            for z in (lo.z, hi.z):
                v = Vector((x, y, z)) - ctr
                dz = v.dot(fwd)
                need = max(abs(v.dot(up)) / t, abs(v.dot(right)) / (t * aspect)) * margin - dz
                dist = max(dist, need)
    cd = bpy.data.cameras.new("PreviewCam")
    cd.angle = math.radians(fov_deg) if aspect <= 1 else 2 * math.atan(t * aspect)
    cd.sensor_fit = "VERTICAL" if aspect > 1 else "AUTO"
    if aspect > 1:
        cd.angle_y = math.radians(fov_deg)
    cd.clip_start = 0.05
    cd.clip_end = 500
    cam = bpy.data.objects.new("PreviewCam", cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = ctr - fwd * dist
    cam.rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def floor_plane(size=60.0, grid=None, y_range=(-6, 6)):
    objs = []
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, -0.002))
    fl = bpy.context.active_object
    fl.name = "Floor"
    fl.data.materials.append(ns.material("#4A4C55"))
    objs.append(fl)
    if grid:
        y = math.floor(y_range[0] / grid) * grid
        while y <= y_range[1]:
            major = abs(y - round(y)) < 1e-6
            ln = ns.box((4.0, 0.05 if major else 0.025, 0.004), loc=(0, y, 0.0), bevel=0, name="GridLine")
            ln.data.materials.append(ns.material("#D9DCE4" if major else "#7C7F89"))
            objs.append(ln)
            y += grid
    return objs


def bbox_objs(objs):
    return ns.bbox_world(objs)


def strip(arm, act, frames, out_path, title, views=((-35, 10), (90, 6)), res=280, speed=0.0,
          extra_objs=(), grid=None, labels=None):
    """Pose strip: columns = frames, rows = camera views (yaw, pitch). With speed > 0 the rig
    travels at `speed` studs/s along -Y over a floor grid (fixed camera), so a planted foot stays
    on the same grid line."""
    from PIL import Image, ImageDraw
    use_action(arm, act)
    fps = act.get("ns_fps", 30)
    body = [o for o in ns._tagged_objects()] + list(extra_objs)
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for f in frames:
        bpy.context.scene.frame_set(f)
        arm.location.y = -speed * f / fps
        bpy.context.view_layer.update()
        a, b = ns.bbox_world(body)
        lo = Vector(map(min, lo, a))
        hi = Vector(map(max, hi, b))
    lo.z = min(lo.z, 0.0)
    made = floor_plane(grid=grid, y_range=(lo.y - 1.5, hi.y + 1.5)) if True else []
    setup_workbench(res, res)
    tiles = []
    for vi, (yaw, pitch) in enumerate(views):
        camera(lo, hi, yaw, pitch)
        row = []
        for f in frames:
            bpy.context.scene.frame_set(f)
            arm.location.y = -speed * f / fps
            bpy.context.view_layer.update()
            p = os.path.join(SCRATCH, f"_tile_{vi}_{f}.png")
            bpy.context.scene.render.filepath = p
            bpy.ops.render.render(write_still=True)
            row.append(p)
        tiles.append(row)
    arm.location.y = 0
    for o in made:
        bpy.data.objects.remove(o, do_unlink=True)
    for o in list(bpy.context.scene.objects):
        if o.name.startswith("PreviewCam"):
            bpy.data.objects.remove(o, do_unlink=True)
    W, H = res * len(frames), res * len(views) + 28
    sheet = Image.new("RGB", (W, H), (22, 24, 28))
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 8), title, fill=(235, 235, 235))
    for r, row in enumerate(tiles):
        for i, p in enumerate(row):
            im = Image.open(p).convert("RGB")
            sheet.paste(im, (i * res, 28 + r * res))
            lab = labels[i] if labels else f"f{frames[i]}  {frames[i] / fps:.2f}s"
            dr.text((i * res + 6, 28 + r * res + 4), lab, fill=(255, 255, 255))
            os.remove(p)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path)
    bpy.context.scene.frame_set(0)
    return out_path


# --------------------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------------------

def _to_lua4(v, indent=0) -> str:
    """nslib._to_lua with 4-decimal numbers (meta needs HipHeight 2.1924 exactly)."""
    import json as _json
    pad = "\t" * indent
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        r = round(float(v), 4)
        return str(int(r)) if r == int(r) else repr(r)
    if isinstance(v, str):
        return _json.dumps(v)
    if v is None:
        return "nil"
    if isinstance(v, list):
        if all(not isinstance(x, (list, dict)) for x in v):
            return "{" + ", ".join(_to_lua4(x) for x in v) + "}"
        return "{\n" + ",\n".join(pad + "\t" + _to_lua4(x, indent + 1) for x in v) + ",\n" + pad + "}"
    if isinstance(v, dict):
        items = []
        for k, x in v.items():
            kk = k if (isinstance(k, str) and k.isidentifier()) else f"[{_json.dumps(k)}]"
            items.append(f"{pad}\t{kk} = {_to_lua4(x, indent + 1)}")
        return "{\n" + ",\n".join(items) + ",\n" + pad + "}"
    raise TypeError(type(v))


def add_meta(path: str, meta: dict) -> None:
    """Append `meta = {...}` to the module nslib wrote (top-level table)."""
    with open(path) as f:
        src = f.read()
    assert src.rstrip().endswith("}"), "unexpected module shape"
    body = src.rstrip()
    body = body[:-1].rstrip()
    if not body.endswith(","):
        body += ","
    lua_meta = _to_lua4(meta, 1)
    body += "\n\tmeta = " + lua_meta + ",\n}\n"
    with open(path, "w") as f:
        f.write(body)


# --------------------------------------------------------------------------------------
# Clip measurements (evaluated from the Blender action, i.e. what the exporter samples)
# --------------------------------------------------------------------------------------

def box_corners(obb):
    c, Rm, h = obb
    return [c + Rm @ Vector((sx * h.x, sy * h.y, sz * h.z)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]


def eval_clip(arm, act, step=1):
    """Yield (frame, R, P) for every frame of the action (Blender evaluation)."""
    use_action(arm, act)
    end = act["ns_end"]
    for f in range(0, end + 1, step):
        bpy.context.scene.frame_set(f)
        R, P = blender_pose(arm)
        yield f, R, P
    bpy.context.scene.frame_set(0)


def measure(arm, act, speed=0.0, contact_eps=0.02, pairs=None, upper_only=False, extra_obbs=None):
    """Foot slip (lowest corner of each foot box while in contact; root motion at `speed`
    studs/s along -Y), floor (lowest corner of every part box), planted-foot drift (static
    clips) and OBB penetration of non-adjacent part pairs."""
    fps = act["ns_fps"]
    res = {"minZ": 9.0, "minZ_part": None, "slide": {"LeftFoot": 0.0, "RightFoot": 0.0},
           "maxSlideSpeed": 0.0, "drift": {"LeftFoot": 0.0, "RightFoot": 0.0}, "pen": {}, "pen_frame": {}}
    prev = {}
    first = {}
    pairs = pairs if pairs is not None else penetration_pairs(include_legs=not upper_only)
    for f, R, P in eval_clip(arm, act):
        t = f / fps
        ob = obbs_at(R, P)
        if extra_obbs:
            ob.update(extra_obbs(f, R, P))
        if not upper_only:
            for n in PART:
                z = min(v.z for v in box_corners(ob[n]))
                if z < res["minZ"]:
                    res["minZ"], res["minZ_part"] = z, f"{n}@{f}"
            for foot in ("LeftFoot", "RightFoot"):
                cs = box_corners(ob[foot])
                for v in cs:
                    v.y -= speed * t
                if foot in prev:
                    p0 = prev[foot]
                    i = min(range(8), key=lambda k: p0[k].z)
                    if p0[i].z < contact_eps and cs[i].z < contact_eps:
                        d = math.hypot(cs[i].x - p0[i].x, cs[i].y - p0[i].y)
                        res["slide"][foot] += d
                        res["maxSlideSpeed"] = max(res["maxSlideSpeed"], d * fps)
                if foot not in first:
                    first[foot] = cs
                else:
                    res["drift"][foot] = max(res["drift"][foot], max((a - b).length for a, b in zip(cs, first[foot])))
                prev[foot] = cs
        for a, b in pairs:
            if a not in ob or b not in ob:
                continue
            dpt = sat_depth(ob[a], ob[b])
            if a in PART and b in PART:
                dpt -= max(0.0, rest_penetration(a, b))     # the R15 rig's own rest overlap
            key = f"{a}x{b}"
            if dpt > res["pen"].get(key, -9):
                res["pen"][key] = dpt
                res["pen_frame"][key] = f
    return res


def pen_summary(res, thresh=0.0):
    out = {k: round(v, 3) for k, v in sorted(res["pen"].items(), key=lambda kv: -kv[1]) if v > thresh}
    return out


# --------------------------------------------------------------------------------------
# Exported module checks (parses anim/<Rig>.lua)
# --------------------------------------------------------------------------------------

def parse_lua(text):
    """Tiny parser for the AnimData subset nslib writes (tables, strings, numbers, bools)."""
    i = text.index("return") + len("return")
    n = len(text)

    def ws(i):
        while i < n:
            if text[i] in " \t\r\n,;":
                i += 1
            elif text.startswith("--", i):
                while i < n and text[i] != "\n":
                    i += 1
            else:
                break
        return i

    def val(i):
        i = ws(i)
        ch = text[i]
        if ch == "{":
            i += 1
            arr, dct = [], {}
            while True:
                i = ws(i)
                if text[i] == "}":
                    return (dct if dct else arr), i + 1
                m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", text[i:])
                m2 = re.match(r'\["([^"]+)"\]\s*=', text[i:])
                if m:
                    k = m.group(1)
                    v, i = val(i + m.end())
                    dct[k] = v
                elif m2:
                    v, i = val(i + m2.end())
                    dct[m2.group(1)] = v
                else:
                    v, i = val(i)
                    arr.append(v)
        if ch == '"':
            j = text.index('"', i + 1)
            return text[i + 1:j], j + 1
        m = re.match(r"-?\d+(\.\d+)?(e-?\d+)?", text[i:])
        if m:
            return float(m.group(0)), i + m.end()
        for lit, v in (("true", True), ("false", False), ("nil", None)):
            if text.startswith(lit, i):
                return v, i + len(lit)
        raise ValueError(text[i:i + 40])
    v, _ = val(i)
    return v


def _cf_angles_q(r):
    """Quaternion of CFrame.Angles(rx, ry, rz) = Rx @ Ry @ Rz (Roblox axes)."""
    return (Matrix.Rotation(r[0], 3, "X") @ Matrix.Rotation(r[1], 3, "Y") @ Matrix.Rotation(r[2], 3, "Z")).to_quaternion()


def check_module(path, upper_clips):
    """Euler continuity, loop seams and keyed-joint sets of the written module."""
    with open(path) as f:
        data = parse_lua(f.read())
    rep = {}
    for name, clip in data["clips"].items():
        keys = clip["keys"]
        maxjump, seam, wraps, diverge = 0.0, 0.0, [], 0.0
        nkeys = 0
        for b, ks in keys.items():
            nkeys += len(ks)
            for a, c in zip(ks, ks[1:]):
                for j in (1, 2, 3):
                    d = abs(c[j] - a[j])
                    maxjump = max(maxjump, d)
                    if d > math.pi:                        # Euler wrap (representation jump)
                        wraps.append(f"{b}@{c[0]}")
                # would a per-component Euler lerp leave the slerp path? (mid-segment check)
                qa, qc = _cf_angles_q(a[1:4]), _cf_angles_q(c[1:4])
                if qa.dot(qc) < 0:
                    qc.negate()
                qm = qa.slerp(qc, 0.5)
                qe_mid = _cf_angles_q([(x + y) / 2 for x, y in zip(a[1:4], c[1:4])])
                diverge = max(diverge, math.degrees(qm.rotation_difference(qe_mid).angle))
            if clip["loop"]:
                s = max(abs(x - y) for x, y in zip(ks[0][1:-1], ks[-1][1:-1]))
                seam = max(seam, s)
            for k in ks:
                if len(k) == 8 and b != "Root":
                    wraps.append(f"translation on {b}")
        rep[name] = {"length": clip["length"], "loop": clip["loop"], "joints": sorted(keys),
                     "nJoints": len(keys), "nKeys": nkeys, "maxEulerStep": round(maxjump, 3),
                     "wraps": wraps, "eulerLerpVsSlerpMaxDeg": round(diverge, 2), "seam": round(seam, 4),
                     "upperOnly": (set(keys) == set(UPPER)) if name in upper_clips else None}
    return data, rep


def min_z(pose: Pose, parts):
    R, P = fk(pose)
    return min(min(v.z for v in box_corners(part_obb(n, R, P))) for n in parts)


TOE_TO_ANKLE = Vector((0.0, 0.5005, 0.262))      # front-bottom foot edge -> ankle joint (rest)


def foot_on_toe(toe: Vector, alpha: float):
    """Ankle position + foot rotation for a foot pivoting about its front-bottom edge (toe)
    by alpha degrees (heel up)."""
    q = qx(alpha)
    return Vector(toe) + q @ TOE_TO_ANKLE, q


def plant_leg(pose: Pose, side: str, toe: Vector, alpha_min=0.0, alpha_max=70.0, margin=0.004,
              pole=Vector((0, -1, 0))):
    """Leg IK with the foot pivoting on its toe edge; raises the heel (alpha) just enough that
    no corner of the LowerLeg/Foot boxes goes below the floor. Returns alpha used."""
    a = alpha_min
    while True:
        A, q = foot_on_toe(toe, a)
        leg_ik(pose, side, A, q, pole)
        if min_z(pose, [side + "LowerLeg", side + "UpperLeg"]) >= margin or a >= alpha_max:
            break
        a += 0.25
    return a


def limb_frame(down: Vector, hinge: Vector) -> Quaternion:
    """World rotation of a limb segment whose local -Z points along `down` and whose local +X
    (the hinge axis) is as close as possible to `hinge`."""
    Z = -Vector(down).normalized()
    X = (Vector(hinge) - Z * Vector(hinge).dot(Z)).normalized()
    Y = Z.cross(X)
    return Matrix((X, Y, Z)).transposed().to_quaternion()


def set_leg_dirs(pose: Pose, side: str, thigh_dir, shin_dir, foot_rot: Quaternion | None = None,
                 hinge=Vector((1, 0, 0))):
    """Set hip/knee/ankle from WORLD directions of thigh (hip->knee) and shin (knee->ankle).
    foot_rot = world foot rotation (None: same as the shin, i.e. ankle at rest)."""
    hip, knee, ank = side + "Hip", side + "Knee", side + "Ankle"
    R, P = fk(pose)
    Rt = limb_frame(thigh_dir, hinge)
    Rs = limb_frame(shin_dir, hinge)
    pose.q[hip] = R["Root"].inverted() @ Rt
    pose.q[knee] = Rt.inverted() @ Rs
    pose.q[ank] = Rs.inverted() @ (Rs if foot_rot is None else Quaternion(foot_rot))


def set_world(pose: Pose, bone: str, world_rot: Quaternion):
    """Set a bone's local rotation so its WORLD rotation is world_rot (parents already posed)."""
    R, P = fk(pose)
    par = PARENT[bone]
    pose.q[bone] = (R[par].inverted() if par else Quaternion()) @ Quaternion(world_rot)


def drop_to_floor(pose: Pose, parts, target=0.0):
    """Shift Root translation vertically so the lowest corner of `parts` sits at `target`."""
    pose.loc.z += target - min_z(pose, parts)
    return pose.loc.z


def arm_ik_elbow(pose: Pose, side: str, hand_pos: Vector, hand_rot: Quaternion, elbow_hint: Vector, steps=72,
                 twist_weight=0.25, prev_shoulder: Quaternion | None = None, prev_weight=1.5):
    """arm_ik with the swivel chosen so the elbow lands as close as possible to elbow_hint.
    When the arm is nearly straight the elbow barely moves with the swivel, so a small penalty
    on twisting the upper arm away from its rest orientation (local X = UpperTorso X) breaks
    the tie and keeps the limb from rolling about its own axis."""
    R, P = fk(pose)
    S = P[side + "Shoulder"]
    D = (Vector(hand_pos) - S).normalized()
    a = D.orthogonal().normalized()
    b = D.cross(a)
    pref = R["Waist"] @ Vector((1, 0, 0))

    def score(h):
        trial = pose.copy()
        arm_ik(trial, side, hand_pos, hand_rot, hinge=h)
        R2, P2 = fk(trial)
        d = (P2[side + "Elbow"] - Vector(elbow_hint)).length
        tw = 1.0 - (R2[side + "Shoulder"] @ Vector((1, 0, 0))).dot(pref)
        sc = d + twist_weight * tw
        if prev_shoulder is not None:          # stay on the previous frame's solution branch
            sc += prev_weight * (1.0 - abs(trial.q[side + "Shoulder"].dot(prev_shoulder)))
        return sc
    best = None
    for i in range(steps):
        ang = 2 * math.pi * i / steps
        h = a * math.cos(ang) + b * math.sin(ang)
        sc = score(h)
        if best is None or sc < best[0]:
            best = (sc, h)
    d0, h0 = best
    for _ in range(2):
        for da in (-0.04, -0.02, 0.02, 0.04):
            h = (h0 + D.cross(h0) * da).normalized()
            sc = score(h)
            if sc < d0:
                d0, h0 = sc, h
    return arm_ik(pose, side, hand_pos, hand_rot, hinge=h0)


HEEL_TO_ANKLE = Vector((0.0, -0.5005, 0.262))     # back-bottom foot edge -> ankle joint (rest)


def foot_on_heel(heel: Vector, alpha: float):
    """Ankle position + foot rotation for a foot pivoting on its heel edge, toes up alpha deg."""
    q = qx(-alpha)
    return Vector(heel) + q @ HEEL_TO_ANKLE, q


# ---- props as boxes for the checks --------------------------------------------------
TOOL_BOXES = {
    "Flashlight": [((0.45, 0.439, 1.1), (0, 0, -0.05)), ((0.304, 0.343, 0.974), (0, 0.023, 0.277)),
                   ((0.49, 0.478, 0.1), (0, 0, -0.63))],
    "Spatula": [((0.22, 0.151, 0.78), (0, 0, 0)), ((0.143, 0.1, 0.62), (0, -0.04, -0.6)),
                ((0.66, 0.035, 0.76), (0, -0.142, -1.17))],
}


def tool_rest_boxes(tool, side):
    """[(bone, centre, rot3, half)] of a held tool at rest (Blender world)."""
    G = grip_rest_matrix(side)
    out = []
    for size_r, c_r in TOOL_BOXES[tool]:
        c = G @ (M_B2R @ Vector(c_r))
        out.append((side + "Wrist", c, G.to_3x3(), r2b_size(size_r) / 2))
    return out


def crate_rest_boxes(M_rest: Matrix, bone="RightWrist"):
    h = CRATE_SIZE.z / 2
    boxes = [(CRATE_BODY, Vector((0, 0, -h + 0.5))), (Vector((2.06, 1.46, 0.12)), Vector((0, 0, h - 0.06)))]
    return [(bone, M_rest @ c, M_rest.to_3x3(), Vector(sz) / 2) for sz, c in boxes]


def posed_boxes(rest_boxes, R, P):
    out = []
    for bone, c, rot, half in rest_boxes:
        Rb = R[bone].to_matrix()
        t = P[bone] - Rb @ J[bone]
        out.append((Rb @ c + t, Rb @ rot, half))
    return out


_REST_PEN = {}


def rest_penetration(a, b):
    key = (a, b)
    if key not in _REST_PEN:
        R, P = fk(Pose())
        _REST_PEN[key] = sat_depth(part_obb(a, R, P), part_obb(b, R, P))
    return _REST_PEN[key]


def arm_ik_elbow_wrist(pose: Pose, side: str, hand_pos: Vector, wrist_local: Quaternion, elbow_hint: Vector,
                       iters=4, steps=48, prev_shoulder=None):
    """Arm IK to a hand position with the elbow near elbow_hint and the hand at a given LOCAL
    wrist rotation relative to the forearm."""
    R, P = fk(pose)
    hand_rot = R[side + "Wrist"]
    for _ in range(iters):
        arm_ik_elbow(pose, side, hand_pos, hand_rot, elbow_hint, steps=steps, prev_shoulder=prev_shoulder)
        R, P = fk(pose)
        hand_rot = R[side + "Elbow"] @ Quaternion(wrist_local)
    return arm_ik_elbow(pose, side, hand_pos, hand_rot, elbow_hint, steps=steps, prev_shoulder=prev_shoulder)


def catmull(points, u):
    """Catmull-Rom through points (list of Vector) at parameter u in [0, len-1]."""
    n = len(points)
    i = min(int(math.floor(u)), n - 2)
    t = u - i
    p0 = points[max(i - 1, 0)]
    p1, p2 = points[i], points[i + 1]
    p3 = points[min(i + 2, n - 1)]
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
