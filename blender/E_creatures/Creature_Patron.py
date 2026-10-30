"""Creature_Patron — the Night 5 finale: a colossal face at the dining-room picture window + two hands.

ONE rig, fitted to the double-height dining room (front wall centre plane at Roblox world z = -40,
1 stud thick; ceiling 20; picture window x -7.2..7.2 with lower pane y 3.5..11.85 and upper pane
12.15..16.5 either side of the 0.3 transom; side windows M1-M3 / M7-M10 have the same panes; M4 is the
front door). Rig space (Blender): z = 0 is the floor, -Y is the Patron's front, "L" = +X. World <->
rig: to_rig(x, y, z) = (x, PIVOT_Z - z, y). Placement: pivot CFrame.new(0, 0, -55.5) *
CFrame.Angles(0, math.pi, 0) (faces +Z), so the wall's centre plane is 15.5 studs in front of the pivot.
Head authored in a design frame and scaled by HEAD_S = 1.1: face 26.4 wide x 28.6 tall, eyes at world
y 8.3 (x +-5.8) in the picture window's lower pane, nose tip 1.2 behind the glass, crown 21.1 (over the
20-stud roof). The mouth sits below the sill at rest; it rises into the window to eat and burp.

Rigid-part rig (bones point +Y, roll 0; see _common). Bones: Root > Head > Jaw, EyeL/EyeR, LidL/LidR
(role "eyelid"), CheekL/CheekR; Root > HandL/HandR (palm, wrist ball) > ThumbX > ThumbX2, IndexX > IndexX2,
FingersX (middle+ring+pinky) > FingersX2; Root > ForearmL/ForearmR (pivot at the wrist: cuff + button,
exported as "ForearmL"/"ForearmR", and the 44-stud tapered sleeve "HandL_Sleeve"/"HandR_Sleeve").
Role "receipt": HandR_Receipt (THE BIG ONE, under HandR's palm; show only during HandSlam).
At rest the hands stand fingers-up on the glass either side of the face (HandL on M7's lower pane at
x 12.4, HandR on the transom glass over the door at x -12.4, palm centres at y 12.6), palm turned
HAND_ROLL = 70 deg toward the face with the little-finger edge 0.13 outside the glass; the sleeves run
back outside. The roll keeps every hand key away from the CFrame.Angles(rx, ry, rz) singularity
(ry = +-90): no exported Euler angle jumps more than ~55 deg between frames and nothing wraps. The
forearm swings from its rest direction (fu), can lever about a window aim point (fwin, fw) and can
twist about its own axis (ftw; only the cuff button shows it).

Clips (30 fps): Blink (0.43 s, closed 0.13), Look (4 s loop), Chew (1 s loop), Burp (2.2 s, burp 0.73:
the head rises 8 to show the mouth), HandSlam (3.0 s), HandGrabLift (4.2 s). No locomotion.
  HandSlam: HandR leaves the transom glass, lines up and goes in through M3's lower pane, reaches 32
    studs across the room (the forearm levers in M3), winds up and SLAMS THE BIG ONE flat on the
    counter at x -3.9, z -8.0 (slam f34 = 1.133 s; receipt underside 3.03, 3.4 deg nose-up; the 4-stud
    receipt overhangs the 3-deep counter ~0.5 each side), settles, lifts straight back and withdraws
    through M3. meta.slamPoint = the receipt centre at f34.
  HandGrabLift: HandL leaves the M7 glass, goes in through the right half of the picture window's lower
    pane (cuff under the transom), closes thumb-up round the tower on the Plate (grab f32 = 1.067 s;
    palm on the tower's +X face at y 9.3, fingers round the room side; meta.grabPoint), slides it off,
    lays it over and carries it out through the same pane, holds it bottom-first just outside the glass
    while the head rises and leans back, and the face lunges onto it: CHOMP f76 = 2.533 s, about 50% of
    the tower behind the lip line, teeth 0.4 into it, lips closing round it (the game deletes the tower
    here). The hand lets go beside the lips, slides right past the cheek, turns its fingers out, rolls
    back and returns to the glass while the face chews (the tail is planned in exported Euler angles).
    The hand holds the tower's top end, so the hand stops at the lips: ~50% is the geometric limit.
The client hides a pane while an arm or the tower crosses it: M3 lower pane (HandSlam), picture window
lower pane (HandGrabLift). The face never reaches the glass plane (>= 0.7 behind the outer face).

Map-fit checks (fit_checks, printed as [fit] lines, all in MAP_* rig-space constants): rest pose (palms
outside the glass, nothing in the face); per clip and frame the sleeve's section where it crosses the
wall (inside its own pane, >= FIT_SLEEVE_CLEAR from the frame, transom counts as wall), the hand/cuff/
sleeve mesh inside the wall slab (only in openings, >= FIT_HAND_CLEAR from a frame), booths, counter,
back wall (pass-through x -8..8, y 3..12), ceiling, floor/ground, seated customers (head top 4.6 at the
booths), arm into the face, wrist bend, face vs the wall; the carried tower vs booths/plate/counter/
ceiling/wall and through the face outside the mouth; and the chomp (>= 50% behind the lip line, both
lips within 1.5, no hand behind the lip line).

Finale camera (Roblox world, both inside the dining room): SHOT1 the bite, SHOT2 the chewing/burp face
(constants below). Review strips render them with a proxy diner (never exported).
Run:  bpyenv/bin/python blender/E_creatures/Creature_Patron.py   (NS_EXPORT=1 exports; NS_PREVIEW=0 /
NS_STRIPS=none skip the standard renders; NS_PREV_DIR=<dir> sends review renders there, NS_STD_PREVIEW=1
adds the standard preview there). Map review strips (preview only, never with NS_EXPORT):
      NS_MAP_STRIPS=<out dir> [NS_MAP_RES=480] [NS_MAP_CLIPS=HandGrabLift] [NS_MAP_FRAMES="HandGrabLift:32,76"]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Euler, Matrix, Quaternion, Vector  # noqa: E402

ns = C.ns
rd = C.rot_deg
if os.environ.get("NS_PREV_DIR"):                   # review renders go where the caller says
    C.PREV_DIR = os.path.abspath(os.environ["NS_PREV_DIR"])

SKIN = "#DECBB6"
SKIN_D = "#D2BBA5"
BLUSH = "#D9AA9C"
LIP = "#B85C62"
TEETH = "#F5F1E6"
MOUTH = "#3A1418"
TONGUE = "#C4626C"
EYE_W = "#F4F1EA"
PUPIL = "#121014"
BROW = "#5A4636"
NAIL = "#EFC9C0"
SLEEVE = "#1E2A44"
CUFF = "#F2F0EA"
BUTTON = "#C9CDD3"

# ---- the face as authored (design frame); it is built at HEAD_S about the origin + HEAD_T -------
HEAD_C = Vector((0.0, 0.0, 4.75))
HEAD_R = Vector((12.0, 10.0, 13.0))
EYE = {"L": Vector((5.3, -7.1, 6.25)), "R": Vector((-5.3, -7.1, 6.25))}
EYE_R = 2.95
CHEEK = {"L": Vector((7.4, -8.0, 1.4)), "R": Vector((-7.4, -8.0, 1.4))}
MOUTH_Z = -2.6                                  # where the teeth meet
NOSE_C, NOSE_R = Vector((0.0, -10.6, 2.5)), Vector((2.0, 2.0, 2.4))
CHIN_C, CHIN_R = Vector((0.0, -6.0, -5.6)), Vector((7.8, 3.3, 2.6))
EAR_C, EAR_R = {"L": Vector((11.7, 0.5, 4.5)), "R": Vector((-11.7, 0.5, 4.5))}, Vector((1.4, 2.2, 3.2))
MOUTH_C = Vector((0.0, -6.9, -2.8))             # mouth cavity centre
HEAD_JOINT, JAW_JOINT = Vector((0.0, 1.0, -6.0)), Vector((0.0, -0.5, 0.5))

HEAD_S = 1.1
EYE_LINE = 8.3
HEAD_T = Vector((0.0, 0.0, EYE_LINE - EYE["L"].z * HEAD_S))


def hx(v):
    """Design-frame face point -> rig space."""
    return Vector(v) * HEAD_S + HEAD_T


# ---- placement: rig space <-> Roblox world (pivot CFrame.new(0, 0, PIVOT_Z) * yaw 180, facing +Z) --
PIVOT_Z = -55.5


def to_rig(x, y, z):
    """Roblox world point -> rig space."""
    return Vector((x, PIVOT_Z - z, y))


def to_world(v):
    """Rig point -> Roblox world (x, y, z)."""
    return (v[0], v[2], PIVOT_Z - v[1])


def to_local(v):
    """Rig point -> Roblox model-local (meta points)."""
    return (-v[0], v[2], v[1])


# ---- the new double-height dining room in rig space (Roblox x = X, y = Z, z = PIVOT_Z - Y) --------
MAP_WALL_Y = PIVOT_Z + 40.0                     # front wall centre plane (z = -40), 1 thick
MAP_WALL_OUT, MAP_WALL_IN = MAP_WALL_Y + 0.5, MAP_WALL_Y - 0.5
MAP_CEILING = 20.0
SILL, HEAD_OP, TRANSOM = 3.5, 16.5, (11.85, 12.15)
WINDOWS = {"M1": (-39.2, -32.8), "M2": (-31.2, -24.8), "M3": (-23.2, -16.8), "PW": (-7.2, 7.2),
           "M7": (8.8, 15.2), "M8": (16.8, 23.2), "M9": (24.8, 31.2), "M10": (32.8, 39.2)}
MAP_OPENINGS = {}                               # (x0, x1, z0, z1): each pane on its own (transom = wall)
for _k, (_x0, _x1) in WINDOWS.items():
    MAP_OPENINGS[_k + "lo"] = (_x0, _x1, SILL, TRANSOM[0])
    MAP_OPENINGS[_k + "hi"] = (_x0, _x1, TRANSOM[1], HEAD_OP)
MAP_OPENINGS["M4door"] = (-14.5, -9.5, 0.0, 8.0)     # front door (avoid)
MAP_OPENINGS["M4top"] = (-14.5, -9.5, 9.0, 15.5)     # transom glass over the door
MAP_BOOTH_X = {"M1": -36.0, "M2": -28.0, "M3": -20.0, "M7": 12.0, "M8": 20.0, "M9": 28.0, "M10": 36.0}
MAP_BOOTHS = {"Booth" + k: (x - 2.9, x + 2.9) for k, x in MAP_BOOTH_X.items()}
MAP_BOOTH_Y = (PIVOT_Z + 35.4, PIVOT_Z + 39.4)  # z -35.4 .. -39.4
MAP_BOOTH_TOP = 4.6
MAP_COUNTER = ((-8.0, 8.0), (PIVOT_Z + 6.5, PIVOT_Z + 9.5), 3.0)       # x, y, top z
MAP_BACK_WALL_Y = PIVOT_Z + 8.0                 # wall line z = -8 (pass-through x -8..8, header at 12)
MAP_PLATE = ((-3.9, 3.9), (PIVOT_Z + 35.9, PIVOT_Z + 38.5), 2.9)      # three tables, top z
MAP_TOWER = ((-2.0, 2.0), (PIVOT_Z + 35.2, PIVOT_Z + 39.2), (2.9, 10.4))   # biggest tower (4 x 4 x 7.5)

# ---- hands: palms rest on the glass either side of the face (M7 and the transom glass over the door) --
REST_PALM = {"L": (12.4, 12.6), "R": (-12.4, 12.6)}   # (x, z) palm centre
HAND_TILT = 12.0                                # fingertips lean outward (deg)
HAND_ROLL = 70.0                                # palm turned toward the face, little-finger edge on the glass (see Euler note)
GLASS_GAP = 0.3                                 # palm side vs the wall's outer face
REST_CURL = 10.0                                # distal finger joints at rest
PALM_OFF = Vector((0.0, -2.5, -0.95))           # palm centre (underside) from the wrist, canonical
RECEIPT_OFF = Vector((0.0, -2.6, -1.0))         # THE BIG ONE's centre from the wrist, canonical


def _hand_rest(s):
    """Rest rotation of the canonical hand (palm down, fingers -Y): fingers up against the glass, palm cupped
    HAND_ROLL toward the face."""
    side = C.SIDE[s]
    return (Matrix.Rotation(math.radians(side * HAND_TILT), 3, "Y") @ Matrix.Rotation(math.radians(-90.0), 3, "X")
            @ Matrix.Rotation(math.radians(side * HAND_ROLL), 3, "Y"))


HAND_REST = {s: _hand_rest(s) for s in ("L", "R")}
# canonical points on the palm side (most -Y at rest): thumb tip (capsule r 0.58), palm front underside
_PALM_SIDE = [(-4.0, -5.2, -1.3, 0.58), (-2.0, -4.85, -1.24, 0.0), (2.0, -4.85, -1.24, 0.0), (0.0, -0.3, -0.7, 0.0),
              (2.3, -2.4, -0.5, 0.0), (1.55, -7.6, -0.3, 0.52), (0.55, -8.0, -0.3, 0.6), (-0.52, -8.0, -0.3, 0.6),
              (-1.6, -7.7, -0.3, 0.6), (1.55, -4.55, 0.25, 0.62), (2.2, -1.0, -0.6, 0.0)]


def _wrist_rest(s):
    side = C.SIDE[s]
    R0 = HAND_REST[s]
    px, pz = REST_PALM[s]
    w = Vector((px, 0.0, pz)) - R0 @ Vector((side * PALM_OFF.x, PALM_OFF.y, PALM_OFF.z))
    low = min((R0 @ Vector((side * x, y, z))).y - r for x, y, z, r in _PALM_SIDE)
    w.y = MAP_WALL_OUT + GLASS_GAP - low
    return w


WRIST = {s: _wrist_rest(s) for s in ("L", "R")}

# ---- forearms (own bones, pivot at the wrist): cuff + long tapered sleeve --------------------------
FA_A0 = Vector((0.0, 0.3, 0.3))                 # forearm axis start, canonical hand coords (wrist = origin)
CUFF_LEN, CUFF_R = 1.3, 2.45
SLEEVE_PITCH, SLEEVE_YAW = 8.0, 20.0            # natural forearm direction: up / outward (pinky side)
SLEEVE_S0 = 0.55                                # sleeve starts inside the cuff
SLEEVE_LEN = 44.0
SLEEVE_PROFILE = [(0.0, 2.35), (2.0, 2.2), (8.0, 2.0), (24.0, 1.8), (44.0, 1.6)]   # (s, radius)
FA_REST_OUT, FA_REST_UP = 22.0, 4.0             # rest forearm: straight back, turned out, raised (deg)


def sleeve_dir():
    p, y = math.radians(SLEEVE_PITCH), math.radians(SLEEVE_YAW)
    return Vector((math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), math.sin(p)))


def sleeve_r(s):
    pts = SLEEVE_PROFILE
    if s <= pts[0][0]:
        return pts[0][1]
    for (s0, r0), (s1, r1) in zip(pts[:-1], pts[1:]):
        if s <= s1:
            return r0 + (r1 - r0) * (s - s0) / (s1 - s0)
    return pts[-1][1]


def canon(s, p):
    return Vector((C.SIDE[s] * p[0], p[1], p[2]))


def fa_rest_dir(s):
    o, u = math.radians(FA_REST_OUT), math.radians(FA_REST_UP)
    return Vector((C.SIDE[s] * math.sin(o) * math.cos(u), math.cos(o) * math.cos(u), math.sin(u)))


def bend_to(H, s, u):
    """Forearm rotation (canonical frame) that points the forearm axis along u with the least twist
    relative to the hand H (a pure wrist bend)."""
    return (H @ canon(s, sleeve_dir())).rotation_difference(Vector(u).normalized()).to_matrix() @ H


FOREARM_REST = {s: bend_to(HAND_REST[s], s, fa_rest_dir(s)) for s in ("L", "R")}

# ---- canonical hand: wrist at origin, fingers along -Y, palm down (-Z), thumb on the inner side -----
FINGER_SEGS = {"Index": (2.6, 2.2), "Middle": (2.7, 2.4), "Ring": (2.85, 2.2), "Pinky": (3.05, 1.7)}
KNUCKLE_X = {"Index": -1.6, "Middle": -0.52, "Ring": 0.55, "Pinky": 1.55}
KNUCKLE_Y = {"Index": -4.7, "Middle": -4.9, "Ring": -4.75, "Pinky": -4.55}


def hand_joints(s):
    side = C.SIDE[s]
    W = WRIST[s]
    R0 = HAND_REST[s]

    def P(x, y, z):
        return tuple(W + R0 @ Vector((side * x, y, z)))
    js = [("Hand" + s, "Root", tuple(W))]
    js += [("Thumb" + s, "Hand" + s, P(-2.0, -1.4, -0.4)), ("Thumb" + s + "2", "Thumb" + s, P(-3.4, -3.3, -0.55))]
    js += [("Index" + s, "Hand" + s, P(KNUCKLE_X["Index"], KNUCKLE_Y["Index"], 0.0)),
           ("Index" + s + "2", "Index" + s, P(KNUCKLE_X["Index"], KNUCKLE_Y["Index"] - FINGER_SEGS["Index"][0], 0.0))]
    js += [("Fingers" + s, "Hand" + s, P(KNUCKLE_X["Ring"], KNUCKLE_Y["Middle"], 0.0)),
           ("Fingers" + s + "2", "Fingers" + s, P(KNUCKLE_X["Ring"], KNUCKLE_Y["Middle"] - FINGER_SEGS["Middle"][0], 0.0))]
    return js


JOINTS = ([("Root", None, (0.0, 0.0, 0.0)),
           ("Head", "Root", tuple(hx(HEAD_JOINT))),
           ("Jaw", "Head", tuple(hx(JAW_JOINT))),
           ("EyeL", "Head", tuple(hx(EYE["L"]))), ("EyeR", "Head", tuple(hx(EYE["R"]))),
           ("LidL", "Head", tuple(hx(EYE["L"]))), ("LidR", "Head", tuple(hx(EYE["R"]))),
           ("CheekL", "Head", tuple(hx(CHEEK["L"]))), ("CheekR", "Head", tuple(hx(CHEEK["R"])))]
          + hand_joints("L") + hand_joints("R")
          + [("ForearmL", "Root", tuple(WRIST["L"])), ("ForearmR", "Root", tuple(WRIST["R"]))])


# ======================================================================================
# Model
# ======================================================================================

def _bm(o):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    return bm


def build_head(sk):
    import bmesh
    arm = sk.arm
    XF = Matrix.Translation(HEAD_T) @ Matrix.Scale(HEAD_S, 4)

    def A(objs, name, color, bone, mat="SmoothPlastic", **kw):
        o = C.part(objs, name, color, mat, **kw)
        o.data.transform(XF)
        o.data.update()
        return ns.bind(o, arm, bone)

    head = C.ell(tuple(HEAD_C), tuple(HEAD_R), segs=30, rings=19, name="HeadShape")

    def face(v):
        rel = v - HEAD_C
        t = rel.z / HEAD_R.z                     # heavy jowls, narrower crown
        w = 1.0 + 0.08 * max(0.0, -t) - 0.1 * max(0.0, t) ** 2
        v.x = HEAD_C.x + rel.x * w
        if rel.y < -6:                          # flatten the face front a little
            v.y = HEAD_C.y + rel.y * 0.97
        if v.z < -1.2 and abs(v.x) < 8.4 and v.y < -5.0:      # recess the lower face behind the jaw
            k = min(1.0, (-1.2 - v.z) / 1.5) * max(0.0, 1.0 - (abs(v.x) / 8.4) ** 4)
            v.y += 1.6 * k
        return v
    C.deform(head, face)
    ears = [C.ell(tuple(EAR_C[s]), tuple(EAR_R), segs=12, rings=7) for s in ("L", "R")]
    nose = C.ell(tuple(NOSE_C), tuple(NOSE_R), segs=14, rings=9)
    lower_lids = []
    for s, E in EYE.items():
        t = ns.torus(EYE_R * 0.98, 0.42, major_segs=16, minor_segs=5)
        C.deform(t, lambda v: Vector((v.x, v.y * 0.6, v.z)))
        t.rotation_euler = (math.radians(90), 0, 0)
        t.location = E + Vector((0, -0.15, -0.35))
        ns.apply_all(t)
        bm = _bm(t)                             # keep only the lower half of the ring
        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > E.z - 0.4], context="VERTS")
        bm.to_mesh(t.data)
        bm.free()
        lower_lids.append(t)
    upper_lip = ns.torus(4.6, 0.55, major_segs=24, minor_segs=6)
    C.deform(upper_lip, lambda v: Vector((v.x * 1.45, v.y * 0.32, v.z * 0.85)))
    upper_lip.rotation_euler = (math.radians(90), 0, 0)
    upper_lip.location = (0, -8.55, MOUTH_Z + 0.25)
    ns.apply_all(upper_lip)
    bm = _bm(upper_lip)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < MOUTH_Z + 0.9], context="VERTS")
    bm.to_mesh(upper_lip.data)
    bm.free()
    A([head, nose] + ears + lower_lids, "Head", SKIN, "Head", smooth_angle=70)
    A([upper_lip], "Head_Lip", LIP, "Head", smooth_angle=70)
    nost = [C.ell((sx * 0.85, -12.2, 1.2), (0.42, 0.3, 0.3), segs=8, rings=5) for sx in (-1, 1)]
    cavity = C.ell(tuple(MOUTH_C), (7.2, 0.8, 2.2), segs=18, rings=8)
    A(nost + [cavity], "Head_Mouth", MOUTH, "Head", smooth_angle=70)
    brows = [ns.tube([(sx * 2.6, -9.2, 10.3), (sx * 5.0, -8.9, 11.0), (sx * 7.6, -7.8, 10.2)], [0.3, 0.36, 0.22],
                     sides=6, resolution=3) for sx in (-1, 1)]
    comb = [ns.tube([(x, 2.0, 17.4), (x + 2.2, -1.5, 17.8), (x + 4.0, -5.5, 16.4)], [0.12, 0.1, 0.06], sides=5,
                    resolution=3) for x in (-3.0, -1.6, -0.3)]
    A(brows + comb, "Head_Brows", BROW, "Head", smooth_angle=70)
    upper_teeth = []
    for i in range(10):
        x = -5.4 + 1.2 * i
        z0 = MOUTH_Z + 0.04 * x * x
        upper_teeth.append(ns.box((1.06, 0.5, 1.05), loc=(x, -8.15 + 0.035 * x * x, z0 + 0.52), bevel=0.16, segments=1))
    A(upper_teeth, "Head_Teeth", TEETH, "Head", smooth_angle=50)

    # ---- jaw: chin + lower lip + lower teeth + tongue -------------------------------------
    chin = C.ell(tuple(CHIN_C), tuple(CHIN_R), segs=20, rings=10)
    C.deform(chin, lambda v: Vector((v.x * (1.0 - 0.15 * max(0.0, (-5.4 - v.z) / 2.7)), v.y, v.z)))
    A([chin], "Jaw", SKIN, "Jaw", smooth_angle=70)
    lower_lip = ns.torus(4.3, 0.6, major_segs=24, minor_segs=6)
    C.deform(lower_lip, lambda v: Vector((v.x * 1.42, v.y * 0.32, v.z * 0.85)))
    lower_lip.rotation_euler = (math.radians(90), 0, 0)
    lower_lip.location = (0, -8.45, MOUTH_Z - 0.35)
    ns.apply_all(lower_lip)
    bm = _bm(lower_lip)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > MOUTH_Z - 1.0], context="VERTS")
    bm.to_mesh(lower_lip.data)
    bm.free()
    A([lower_lip], "Jaw_Lip", LIP, "Jaw", smooth_angle=70)
    lower_teeth = []
    for i in range(9):
        x = -4.8 + 1.2 * i
        lower_teeth.append(ns.box((1.04, 0.5, 0.95), loc=(x, -8.1 + 0.035 * x * x, MOUTH_Z - 0.5 + 0.04 * x * x),
                                  bevel=0.16, segments=1))
    A(lower_teeth, "Jaw_Teeth", TEETH, "Jaw", smooth_angle=50)
    tongue = C.ell((0, -6.9, MOUTH_Z - 1.3), (4.0, 1.4, 0.6), segs=14, rings=7)
    A([tongue], "Jaw_Tongue", TONGUE, "Jaw", smooth_angle=70)

    # ---- eyes (whites + tiny pupils), lids, cheeks -------------------------------------------
    for s, E in EYE.items():
        ball = C.ell(tuple(E), (EYE_R, EYE_R, EYE_R), segs=20, rings=12)
        A([ball], "Eye" + s, EYE_W, "Eye" + s, smooth_angle=80)
        pupil = C.ell(tuple(E + Vector((0, -EYE_R + 0.06, 0))), (0.42, 0.18, 0.42), segs=10, rings=6)
        A([pupil], "Eye" + s + "_Pupil", PUPIL, "Eye" + s, smooth_angle=80)
        lid = C.ell((0, 0, 0), (EYE_R + 0.22, EYE_R + 0.22, EYE_R + 0.22), segs=20, rings=12)
        bm = _bm(lid)                           # spherical shell cap over the top of the eye
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < (EYE_R + 0.22) * 0.66 - 0.01], context="VERTS")
        bm.to_mesh(lid.data)
        bm.free()
        lid.location = E
        sol = lid.modifiers.new("S", "SOLIDIFY")
        sol.thickness = 0.28
        A([lid], "Lid" + s, SKIN, "Lid" + s, recolor="eyelid", smooth_angle=70)
        ch = C.ell(tuple(CHEEK[s]), (2.5, 1.4, 2.1), segs=12, rings=7)
        A([ch], "Cheek" + s, BLUSH, "Cheek" + s, smooth_angle=70)


def _place(objs, s, W, R):
    """Canonical (L) geometry -> rig space: W + R @ mirrored point; mirrored meshes get their normals
    flipped back outward."""
    side = C.SIDE[s]
    for o in objs:
        ns.apply_all(o)
        for v in o.data.vertices:
            v.co = W + R @ Vector((side * v.co.x, v.co.y, v.co.z))
        o.data.update()
        if side < 0:
            bm = _bm(o)
            for f in bm.faces:
                f.normal_flip()
            bm.to_mesh(o.data)
            bm.free()
    return objs


def build_hand(sk, s):
    arm = sk.arm
    W = WRIST[s]
    R0 = HAND_REST[s]
    A = lambda objs, name, color, bone, mat="SmoothPlastic", **kw: C.attach(objs, name, color, arm, bone, mat, **kw)  # noqa: E731

    def place(objs):
        return _place(objs, s, W, R0)

    palm = C.loft([(-0.95, 2.2, 2.35, 0.1, -2.5, 3.2), (0.0, 2.3, 2.45, 0.0, -2.4, 3.2), (0.75, 2.0, 2.1, 0.0, -2.2, 3.0)],
                  verts=18, name="Palm")
    C.deform(palm, lambda v: Vector((v.x, v.y, v.z + 0.12 * (v.y + 2.4))))
    knuck = [C.ell((KNUCKLE_X[f] * 1.0, KNUCKLE_Y[f] + 0.25, 0.25), (0.72, 0.7, 0.62), segs=10, rings=6)
             for f in ("Index", "Middle", "Ring", "Pinky")]
    wrist = C.ell((0.0, 0.05, -0.12), (1.95, 1.05, 0.9), segs=14, rings=7)       # fills the wrist when it bends
    A(place([palm, wrist] + knuck), "Hand" + s, SKIN, "Hand" + s, smooth_angle=60)
    if s == "R":
        rc = C.plate(3.2, 3.6, 0.08, 0.12, tuple(RECEIPT_OFF), plane="XY", bevel=0.0)
        A(place([rc]), "HandR_Receipt", C.PAPER_WHITE, "HandR", recolor="receipt", smooth_angle=None)

    def finger(x, y0, L1, L2, r, z=0.0, curl=REST_CURL):
        b = Vector((x, y0, z))
        m = b + Vector((0, -L1, 0))
        d = Vector((0, -math.cos(math.radians(curl)), -math.sin(math.radians(curl))))
        tip = m + d * L2
        prox = C.capsule(b, m, r, r * 0.92, verts=8, cap_rings=2)
        dist = C.capsule(m, tip - d * 0.1, r * 0.92, r * 0.8, verts=8, cap_rings=2)
        up = Vector((1, 0, 0)).cross(d).normalized()          # back-of-finger direction
        nail = C.ell((0, 0, 0), (r * 0.7, 0.42, 0.16), segs=8, rings=4)
        nail.rotation_euler = (math.radians(-curl), 0, 0)
        ns.apply_all(nail)
        nail.location = tip - d * 0.5 + up * r * 0.82
        ns.apply_all(nail)
        return prox, dist, nail
    groups = {"Index": ("Index",), "Fingers": ("Middle", "Ring", "Pinky")}
    for bone, fingers in groups.items():
        prox, dist, nails = [], [], []
        for f in fingers:
            p_, d_, n_ = finger(KNUCKLE_X[f], KNUCKLE_Y[f], *FINGER_SEGS[f], r=0.62 if f != "Pinky" else 0.52)
            prox.append(p_)
            dist.append(d_)
            nails.append(n_)
        A(place(prox), bone + s, SKIN, bone + s, smooth_angle=60)
        A(place(dist), bone + s + "2", SKIN, bone + s + "2", smooth_angle=60)
        A(place(nails), bone + s + "2_Nails", NAIL, bone + s + "2", smooth_angle=70)
    tb, tm = Vector((-2.0, -1.4, -0.4)), Vector((-3.4, -3.3, -0.55))
    tt = Vector((-4.0, -5.2, -1.3))
    A(place([C.capsule(tb, tm, 0.75, 0.68, verts=8, cap_rings=2)]), "Thumb" + s, SKIN, "Thumb" + s, smooth_angle=60)
    A(place([C.capsule(tm, tt, 0.68, 0.58, verts=8, cap_rings=2)]), "Thumb" + s + "2", SKIN, "Thumb" + s + "2",
      smooth_angle=60)


def sleeve_mesh(verts=14, cap_rings=2):
    """Tapered sleeve along sleeve_dir() from inside the cuff (canonical L coords)."""
    r1, L = SLEEVE_PROFILE[-1][1], SLEEVE_LEN
    prof = [(0.0, 0.0), (SLEEVE_PROFILE[0][1], 0.0)]
    for s, r in SLEEVE_PROFILE[1:-1]:
        prof.append((r, s))
    for i in range(cap_rings + 1):                          # far cap
        a = (math.pi / 2) * i / cap_rings
        prof.append((r1 * math.cos(a), L + r1 * math.sin(a)))
    o = ns.lathe([(max(r, 0.0), z) for r, z in prof], verts=verts, name="Sleeve")
    ns.apply_all(o)
    o.rotation_euler = sleeve_dir().to_track_quat("Z", "Y").to_euler()
    o.location = FA_A0 + sleeve_dir() * SLEEVE_S0
    ns.apply_all(o)
    return o


def build_forearm(sk, s):
    """Cuff (+ button) and sleeve on their own bone, pivoting at the wrist."""
    arm = sk.arm
    d = sleeve_dir()
    cuff = C.rod(FA_A0, FA_A0 + d * CUFF_LEN, CUFF_R, verts=16, bevel=0.16, segments=2)
    n = Vector((0.75, 0.0, 0.66))
    n = (n - d * n.dot(d)).normalized()
    btn = C.ell((0, 0, 0), (0.38, 0.38, 0.17), segs=10, rings=6)
    btn.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
    btn.location = FA_A0 + d * (CUFF_LEN * 0.55) + n * (CUFF_R - 0.03)
    ns.apply_all(btn)
    sl = sleeve_mesh()
    W, R = WRIST[s], FOREARM_REST[s]
    C.attach(_place([cuff], s, W, R), "Hand" + s + "_Cuff", CUFF, arm, "Forearm" + s, smooth_angle=50)
    C.attach(_place([btn], s, W, R), "Hand" + s + "_CuffButton", BUTTON, arm, "Forearm" + s, smooth_angle=70)
    C.attach(_place([sl], s, W, R), "Hand" + s + "_Sleeve", SLEEVE, arm, "Forearm" + s, "Fabric", smooth_angle=60)


def build_model(sk):
    build_head(sk)
    for s in ("L", "R"):
        build_hand(sk, s)
        build_forearm(sk, s)


# ======================================================================================
# Pose helpers (canonical hand / forearm rotations -> bone rotations)
# ======================================================================================

def hand_pose(s, wrist, H):
    """Hand bone (rot, loc): canonical hand at world rotation H, wrist at `wrist`."""
    return (H @ HAND_REST[s].inverted(), tuple(Vector(wrist) - WRIST[s]))


def forearm_pose(s, wrist, F):
    return (F @ FOREARM_REST[s].inverted(), tuple(Vector(wrist) - WRIST[s]))


def fconj(s, pose):
    """Finger rotations written in the canonical hand frame -> bone frame (the hand rests rotated)."""
    R0 = HAND_REST[s]
    return {b: R0 @ C.as_mat(r) @ R0.inverted() for b, r in pose.items()}


def fingers_pose(s, curl=0.0, spread=0.0, thumb=0.0, open_=0.0):
    """Finger groups: curl > 0 closes the hand; open_ > 0 straightens the distals."""
    side = C.SIDE[s]
    return fconj(s, {"Index" + s: rd(curl * 0.9, 0, side * spread), "Index" + s + "2": rd(curl * 0.8 - open_, 0, 0),
                     "Fingers" + s: rd(curl, 0, -side * spread * 0.5), "Fingers" + s + "2": rd(curl * 0.8 - open_, 0, 0),
                     "Thumb" + s: rd(0, 0, -side * thumb), "Thumb" + s + "2": rd(thumb * 0.3, 0, -side * thumb * 0.6)})


# ======================================================================================
# Clips
# ======================================================================================

def blink_clip(sk):
    def p(lid):
        return {"LidL": rd(lid, 0, 0), "LidR": rd(lid, 0, 0)}
    keys = [(0, p(0)), (4, p(78), "QUAD", "EASE_IN"), (7, p(80)), (13, p(0), "SINE", "EASE_OUT")]
    return C.clip(sk, "Blink", 13, False, keys)


def look_clip(sk):
    def p(yaw, pitch, head_yaw=0.0, head_pitch=0.0, lid=0.0):
        return {"EyeL": rd(pitch, 0, yaw), "EyeR": rd(pitch, 0, yaw),
                "LidL": rd(lid + 0.4 * max(0.0, pitch), 0, 0), "LidR": rd(lid + 0.4 * max(0.0, pitch), 0, 0),
                "Head": rd(head_pitch, 0, head_yaw)}
    keys = [(0, p(0, 0)), (8, p(26, 4, 3)), (30, p(28, 6, 4)),
            (36, p(-6, 26, 0, 3)), (64, p(-10, 28, -1, 4)),
            (70, p(-27, 8, -4)), (92, p(-26, 6, -4)),
            (98, p(0, 18, 0, 2)), (112, p(4, 16, 0, 2)), (120, p(0, 0))]
    return C.clip(sk, "Look", 120, True, keys)


def chew_clip(sk):
    S = HEAD_S

    def p(jaw, cl=0.0, cr=0.0, bob=0.0, roll=0.0):
        return {"Jaw": rd(jaw, 0, 0), "Head": (rd(-0.15 * jaw, roll, 0), (0, 0, bob * S)),
                "CheekL": (None, (0.35 * cl * S, -0.45 * cl * S, 0)), "CheekR": (None, (-0.35 * cr * S, -0.45 * cr * S, 0)),
                "LidL": rd(14, 0, 0), "LidR": rd(14, 0, 0)}
    keys = [(0, p(0, 0.3, 0.3)), (7, p(13, 1.0, 0.2, 0.25, 1.0)), (15, p(0, 0.5, 0.5, 0.0)),
            (22, p(11, 0.2, 1.0, 0.22, -1.0)), (30, p(0, 0.3, 0.3))]
    return C.clip(sk, "Chew", 30, True, keys)


def burp_clip(sk):
    """Burp, re-fitted for the tall picture window: the head rises and tips back so the open mouth is
    in the lower pane at the burp (the mouth sits below the sill at rest), then settles back to rest."""
    S = HEAD_S

    def p(rise=0.0, tilt=0.0, fwd=0.0, jaw=0.0, puff=0.0, lid=0.0, shake=0.0, spread=0.0):
        d = {"Head": (rd(-tilt, shake, 0), (0, -fwd, rise)), "Jaw": rd(jaw, 0, 0),
             "CheekL": (None, (0.4 * puff * S, -0.6 * puff * S, 0.1 * puff * S)),
             "CheekR": (None, (-0.4 * puff * S, -0.6 * puff * S, 0.1 * puff * S)),
             "LidL": rd(lid, 0, 0), "LidR": rd(lid, 0, 0)}
        d.update(fingers_pose("L", spread=spread, open_=-0.5 * spread))
        d.update(fingers_pose("R", spread=spread, open_=-0.5 * spread))
        return d
    keys = [(0, p()), (12, p(rise=4.0, tilt=-3, puff=0.8, lid=-6)), (18, p(rise=5.5, tilt=-2, puff=1.3, lid=-8)),
            (22, p(rise=BURP_RISE, tilt=BURP_TILT, fwd=0.6, jaw=30, puff=1.0, lid=40, spread=6), "BACK", "EASE_OUT")]
    for i, f in enumerate(range(24, 40, 2)):
        keys.append((f, p(rise=BURP_RISE, tilt=BURP_TILT, fwd=0.6, jaw=29 - i, puff=0.9, lid=42,
                          shake=(1.6 if i % 2 else -1.6), spread=6), "LINEAR"))
    keys += [(48, p(rise=4.0, tilt=3, jaw=0, puff=0.5, lid=30, spread=2)), (66, p())]
    return C.clip(sk, "Burp", 66, False, keys)


BURP_RISE, BURP_TILT = 8.0, 12.0


# ======================================================================================
# Arm clips: interpolated PARAMETERS, re-solved on every frame (C.param_clip)
# ======================================================================================

def qt(R):
    q = Matrix(R).to_3x3().to_quaternion()
    return (q.w, q.x, q.y, q.z)


def qm(t):
    q = Quaternion(t)
    q.normalize()
    return q.to_matrix()


def hand_rot(p=0.0, r=0.0, y=0.0):
    """Canonical hand rotation from yaw (world Z), pitch (X: + tips the fingers down) and roll (about the
    hand's long axis, + tilts its back toward +X), applied roll first: R = Rz(y) Rx(p) Ry(r)."""
    return Euler((math.radians(p), math.radians(r), math.radians(y)), "YXZ").to_matrix()


def euler_H(s, rx, ry, rz):
    """Canonical hand rotation whose exported key (Roblox axes, relative to rest) is CFrame.Angles(rx, ry, rz),
    angles in degrees."""
    R = Euler((math.radians(rx), math.radians(ry), math.radians(rz)), "ZYX").to_matrix()
    return ns.M_B2R @ R @ ns.M_B2R @ HAND_REST[s]


def H_euler(s, H):
    """Exported (rx, ry, rz) in degrees of a canonical hand rotation (inverse of euler_H)."""
    e = (ns.M_B2R @ (H @ HAND_REST[s].inverted()) @ ns.M_B2R).to_euler("ZYX")
    return tuple(math.degrees(v) for v in (e.x, e.y, e.z))


def unit(x, y, z):
    return tuple(Vector((x, y, z)).normalized())


def nat(s, H):
    """Natural forearm direction of a canonical hand rotation (no wrist bend)."""
    return tuple((H @ canon(s, sleeve_dir())).normalized())


ARM_DEF = dict(mode="free", wrist=(0.0, 0.0, 0.0), hq=(1.0, 0.0, 0.0, 0.0), tc=(0.0, 0.0, 0.0), tq=(1.0, 0.0, 0.0, 0.0),
               fu=(0.0, 1.0, 0.0), fwin=(0.0, 0.0, 0.0), fw=0.0, ftw=0.0,
               curl=0.0, icurl=0.0, open=0.0, spread=0.0, thumb=0.0, tpitch=0.0, troll=0.0, tcurl=0.0,
               head_p=0.0, head_r=0.0, head_y=0.0, hx=0.0, hyy=0.0, rise=0.0, jaw=0.0, eye_p=0.0, eye_y=0.0,
               lid=0.0, puff=0.0)


def rest_arm(s):
    return dict(ARM_DEF, wrist=tuple(WRIST[s]), hq=qt(HAND_REST[s]), fu=tuple(fa_rest_dir(s)))


def fingers2(s, curl=0.0, open_=0.0, spread=0.0, thumb=0.0, tpitch=0.0, troll=0.0, tcurl=0.0, icurl=None):
    """fingers_pose plus thumb pitch (tpitch > 0 lifts the tip toward the back of the hand), thumb roll
    and thumb tip curl; thumb < 0 tucks the thumb in along the fingers; icurl curls the index apart."""
    side = C.SIDE[s]
    ic = curl if icurl is None else icurl
    return fconj(s, {"Index" + s: rd(ic * 0.9, 0, side * spread), "Index" + s + "2": rd(ic * 0.8 - open_, 0, 0),
                     "Fingers" + s: rd(curl, 0, -side * spread * 0.5), "Fingers" + s + "2": rd(curl * 0.8 - open_, 0, 0),
                     "Thumb" + s: rd(-tpitch, side * troll, -side * thumb),
                     "Thumb" + s + "2": rd(tcurl, 0, -side * thumb * 0.4)})


def arm_state(s, q, grip=None):
    """(wrist, H, F): canonical hand rotation H and forearm rotation F (world) for the params q.
    mode "free": wrist + hand quaternion hq; mode "carry": the hand follows the tower pose (tc, tq)
    through the grip. The forearm points along fu, blended (fw) toward the window aim point fwin
    (aimed from the cuff, so it pivots in the window like a lever)."""
    if q["mode"] == "carry":
        Rt = qm(q["tq"])
        wrist = Vector(q["tc"]) + Rt @ grip[1]
        H = Rt @ grip[0]
    else:
        wrist = Vector(q["wrist"])
        H = qm(q["hq"])
    u = Vector(q["fu"]).normalized()
    F = swing_to(s, u)
    if q["fw"] > 1e-4:
        for _ in range(3):
            uw = (Vector(q["fwin"]) - (wrist + F @ FA_A0)).normalized()
            F = swing_to(s, u.lerp(uw, min(1.0, q["fw"])).normalized())
    if abs(q["ftw"]) > 1e-4:                 # twist about the forearm's own axis (only the cuff button shows it)
        F = Matrix.Rotation(math.radians(q["ftw"]), 3, F @ canon(s, sleeve_dir())) @ F
    return wrist, H, F


def swing_to(s, u):
    """Forearm rotation (canonical frame) pointing its axis along u: the least rotation from the rest
    forearm (the sleeve and cuff are round, so their twist is free)."""
    return fa_rest_dir(s).rotation_difference(Vector(u).normalized()).to_matrix() @ FOREARM_REST[s]


def arm_fn(s, grip=None):
    S = HEAD_S

    def fn(q):
        wrist, H, F = arm_state(s, q, grip)
        pose = {"Hand" + s: hand_pose(s, wrist, H), "Forearm" + s: forearm_pose(s, wrist, F),
                "Head": (rd(q["head_p"], q["head_r"], q["head_y"]), (q["hx"], q["hyy"], q["rise"])),
                "Jaw": rd(q["jaw"], 0, 0),
                "EyeL": rd(q["eye_p"], 0, q["eye_y"]), "EyeR": rd(q["eye_p"], 0, q["eye_y"]),
                "LidL": rd(q["lid"], 0, 0), "LidR": rd(q["lid"], 0, 0),
                "CheekL": (None, (0.3 * q["puff"] * S, -0.5 * q["puff"] * S, 0)),
                "CheekR": (None, (-0.3 * q["puff"] * S, -0.5 * q["puff"] * S, 0))}
        pose.update(fingers2(s, curl=q["curl"], icurl=q["icurl"], open_=q["open"], spread=q["spread"],
                             thumb=q["thumb"], tpitch=q["tpitch"], troll=q["troll"], tcurl=q["tcurl"]))
        return pose
    return fn


def fix_signs(keys, names=("hq", "tq")):
    """Keep consecutive quaternion params in one hemisphere (they are interpolated component-wise)."""
    last = {}
    for k in keys:
        for n in names:
            if n in k[1]:
                q = k[1][n]
                if n in last and sum(a * b for a, b in zip(last[n], q)) < 0:
                    q = tuple(-c for c in q)
                    k[1][n] = q
                last[n] = q
    return keys


def window_point(name, dx=0.0, dz=0.0):
    x0, x1, z0, z1 = MAP_OPENINGS[name]
    return Vector(((x0 + x1) / 2 + dx, MAP_WALL_Y, (z0 + z1) / 2 + dz))


def cuff_wrist(s, H, x, y, z):
    """Wrist position that puts the cuff's centre at (x, z) in the plane Y = y with no wrist bend."""
    c = H @ canon(s, FA_A0 + sleeve_dir() * (CUFF_LEN / 2))
    return (x - c.x, y, z - c.z)


def off_glass(s, back=4.6, drop=1.0, out=0.0):
    """Key params a moment after the palm leaves the glass: wrist pulled straight back, fingers tipped
    away from the wall (so nothing sweeps through the wall before the hand turns)."""
    side = C.SIDE[s]
    return dict(wrist=tuple(WRIST[s] + Vector((side * (1.2 + out), back, -drop))),
                hq=qt(Matrix.Rotation(math.radians(side * HAND_TILT), 3, "Y") @ hand_rot(-104.0, side * HAND_ROLL, 0.0)),
                fu=unit(side * 0.78, 1.0, 0.06), open=-8.0)


# ---- HandSlam: in through M3, THE BIG ONE slammed flat on the counter, back out through M3 ---------
SLAM_WINDOW = "M3lo"
SLAM_F, SLAM_LEN = 34, 90
SLAM_RC = to_rig(-3.9, 3.0, -8.0)              # THE BIG ONE's centre on the counter top at the slam
SLAM_NOSE_UP = -3.4                             # the palm's front underside sits 0.2 below the receipt
SLAM_LOW_PTS = [(x, y, -1.04) for x in (-1.6, 1.6) for y in (-0.8, -4.4)] + \
    [(x, -4.85, -1.244) for x in (-1.9, 0.1, 2.1)] + [(0.0, 0.05, -1.02), (1.5, 0.0, -0.75), (-1.5, 0.0, -0.75)]
SLAM_LEVER = window_point(SLAM_WINDOW, 0.1, 1.55)  # the forearm pivots here while the hand is in the room


def slam_pose():
    """Impact: hand nose-up SLAM_NOSE_UP, receipt centre over SLAM_RC, lowest point on the counter top;
    yaw chosen so the wrist bends least with the forearm through SLAM_LEVER."""
    s = "R"
    best = None
    for yaw10 in range(-20, 251, 5):                    # fingers straight in or toward +X (pass-through)
        psi = yaw10 / 10.0
        H = hand_rot(SLAM_NOSE_UP, 0.0, psi)
        low = min((H @ canon(s, p)).z for p in SLAM_LOW_PTS)
        off = H @ canon(s, RECEIPT_OFF)
        w = Vector((SLAM_RC.x - off.x, SLAM_RC.y - off.y, MAP_COUNTER[2] + 0.004 - low))
        u = (SLAM_LEVER - (w + H @ FA_A0)).normalized()
        bend = math.degrees((H @ canon(s, sleeve_dir())).angle(u))
        if best is None or bend < best[0]:
            best = (bend, w, H, psi)
    return best[1], best[2], best[3]


def slam_keys():
    s = "R"
    rest = rest_arm(s)
    w_s, H_s, _ = slam_pose()
    yaw_s = euler_yaw(H_s)
    lever = tuple(SLAM_LEVER)
    xw, _, zw = window_point(SLAM_WINDOW)
    Hin = hand_rot(-3.0, 0.0, 0.0)                      # straight into the room, fingers together, thumb tucked
    w_line = cuff_wrist(s, Hin, xw - 0.12, MAP_WALL_OUT + 3.4, zw)   # cuff centred on M3's lower pane
    w_pass = cuff_wrist(s, Hin, xw - 0.12, MAP_WALL_Y + 0.6, zw)    # (the tucked thumb rides on the +X side)
    w_in = cuff_wrist(s, Hin, xw - 0.12, MAP_WALL_IN - 1.4, zw)
    lever0 = tuple(window_point(SLAM_WINDOW, 0.2, 1.4))
    glass = off_glass(s)
    look = dict(eye_y=-10.0, eye_p=6.0, head_y=-4.0)
    tuck = dict(open=30.0, spread=0.0, thumb=-34.0, tpitch=14.0)
    keys = [
        (0, rest, "sine"),
        (3, dict(glass, **look), "sine"),                                                    # off the glass
        (6, dict(wrist=(-15.5, MAP_WALL_OUT + 10.5, 9.4)), "sine"),
        (9, dict(wrist=(w_line[0], MAP_WALL_OUT + 8.5, w_line[2] + 0.4), hq=qt(Hin), fu=unit(-0.25, 1.0, -0.02),
                 eye_y=-18.0, **tuck), "sine"),                                              # lined up, far out
        (12, dict(wrist=w_line, fu=nat(s, Hin)), "sine"),
        (15, dict(wrist=w_pass, fwin=tuple(window_point(SLAM_WINDOW)), fw=0.0, fu=unit(-0.08, 1.0, 0.0)), "linear"),  # cuff in M3
        (18, dict(wrist=w_in, fw=0.0), "sine"),
        (21, dict(wrist=(xw + 2.6, MAP_WALL_IN - 6.0, zw + 1.5), hq=qt(hand_rot(-6.0, 0.0, -10.0)), fwin=lever0, fw=1.0,
                  spread=6.0, open=35.0, thumb=-10.0), "sine"),                             # over the booth
        (27, dict(wrist=(-9.0, PIVOT_Z + 20.0, 11.0), hq=qt(hand_rot(-12.0, 0.0, 4.0)), fwin=lever, spread=8.0, open=0.0,
                  jaw=8.0,
                  eye_p=16.0, eye_y=-16.0, head_p=2.0, head_y=-6.0), "sine"),                  # reaches across
        (31, dict(wrist=tuple(w_s + Vector((-0.3, 3.2, 2.6))), hq=qt(hand_rot(-16.0, 0.0, yaw_s)), spread=10.0, open=-4.0,
                  jaw=12.0, eye_p=24.0), "in3"),                                               # wind-up
        (SLAM_F, dict(wrist=tuple(w_s), hq=qt(H_s), spread=10.0, jaw=16.0, eye_p=26.0, eye_y=-18.0, head_p=3.5,
                      head_y=-7.0, tpitch=30.0, open=0.0, thumb=0.0), "out"),                 # SLAM
        (36, dict(wrist=tuple(w_s + Vector((0, 0, 0.12)))), "sine"),
        (38, dict(wrist=tuple(w_s)), "sine"),
        (48, dict(jaw=5.0), "sine"),
        (55, dict(wrist=tuple(w_s + Vector((0.0, 3.6, 2.2))), hq=qt(hand_rot(-8.0, 0.0, yaw_s)), open=0.0,
                  spread=4.0, head_p=1.5, eye_p=10.0, eye_y=-8.0), "sine"),                    # lifts straight back
        (59, dict(wrist=(-5.0, PIVOT_Z + 18.5, 7.6), hq=qt(hand_rot(-8.0, 0.0, 0.0)), open=10.0), "sine"),
        (63, dict(wrist=(-9.0, PIVOT_Z + 20.0, 11.0), hq=qt(hand_rot(-8.0, 0.0, -6.0)), open=40.0), "sine"),
        (69, dict(wrist=(xw + 2.6, MAP_WALL_IN - 6.0, zw + 1.5), hq=qt(hand_rot(-6.0, 0.0, -10.0)), fwin=lever0, fw=1.0,
                  spread=4.0), "sine"),
        (72, dict(wrist=w_in, hq=qt(Hin), fwin=tuple(window_point(SLAM_WINDOW)), fw=0.0, fu=unit(-0.08, 1.0, 0.0), **tuck),
         "sine"),
        (75, dict(wrist=w_pass, head_p=0.0, head_y=0.0, jaw=0.0, eye_p=0.0, eye_y=0.0), "linear"),   # cuff out
        (78, dict(wrist=w_line), "linear"),
        (81, dict(wrist=(w_line[0], MAP_WALL_OUT + 10.5, w_line[2] + 0.4), fu=unit(-0.25, 1.0, -0.02)), "sine"),
        (84, dict(wrist=(-15.5, MAP_WALL_OUT + 11.0, 9.4)), "sine"),
        (87, dict(glass, spread=0.0, thumb=0.0, tpitch=0.0), "sine"),
        (SLAM_LEN, dict(rest), "sine"),
    ]
    return fix_signs(keys)


def euler_yaw(H):
    return math.degrees(H.to_euler("YXZ").z)


def slam_clip(sk):
    return C.param_clip(sk, "HandSlam", SLAM_LEN, False, slam_keys(), arm_fn("R"), step=1)


# ---- HandGrabLift: in through the picture window, the tower out through it and INTO the mouth ------
GRAB_F, CHOMP_F, GRAB_LEN = 32, 76, 126
TOWER_C0 = Vector((0.0, (MAP_TOWER[1][0] + MAP_TOWER[1][1]) / 2, (MAP_TOWER[2][0] + MAP_TOWER[2][1]) / 2))
TOWER_HALF = Vector((2.0, 2.0, 3.75))
PALM_SINK = 0.962                               # palm underside below the wrist line (canonical -Z)
GRAB_Z = 9.3                                    # palm centre on the tower's +X face: the cuff passes under the transom
GRAB_WRIST_Y = MAP_WALL_IN - 0.15               # the wrist rests in the window, palm + fingers round the tower
GRAB_YAW = 0.0
TWIST_IN = 135.0                                # forearm twist while the cuff is in the pane (drops it under the transom)
BATON = Matrix(((0.0, 1.0, 0.0), (0.0, 0.0, -1.0), (-1.0, 0.0, 0.0)))   # tower: bottom -> +Y, +X face -> down
BITE_HEAD = dict(head_p=-12.0, head_r=0.0, head_y=0.0, hx=0.0, hyy=0.2, rise=8.5)
CHOMP_HEAD = dict(BITE_HEAD, rise=8.0, head_p=-10.5)    # dips into the bite
BITE_JAW = 42.0                                 # wide open while the tower goes in
BITE_DEPTH = 3.35                               # tower's far end past the upper teeth at chomp
LUNGE = 5.0                                     # the face comes this far forward onto the tower
BITE_SINK = 0.4                                 # the teeth sink this far into the tower at chomp
BITE_SPIN = -90.0                               # hand+tower turned about the tower's axis: palm lower-right
GRAB_WIN = Vector((8.0, MAP_WALL_Y + 13.5, 8.3))   # forearm aim while the hand works in the room (out through the right of the pane)
CARRY_FAR = Vector((10.5, MAP_WALL_Y + 15.0, 7.0))  # forearm aim while the hand carries the tower out
CARRY_TWIST = 58.0                              # supination that lays the tower over to pass the lower pane
HEAD_ASIDE = dict(hyy=9.0, hx=-8.5, head_y=8.0, rise=1.0)   # the face backs off while the hand works


def grab_grip():
    """Canonical hand rotation + wrist at the grab: thumb up, palm on the tower's +X face near the top,
    fingers round the room side; returns (H, wrist, grip) with grip = (H, wrist - tower centre)."""
    H = hand_rot(0.0, 90.0, GRAB_YAW)
    w = Vector((MAP_TOWER[0][1] + PALM_SINK, GRAB_WRIST_Y, GRAB_Z))
    return H, w, (H, w - TOWER_C0)


def head_fk(sk, head):
    pose = {"Head": (rd(head.get("head_p", 0.0), head.get("head_r", 0.0), head.get("head_y", 0.0)),
                     (head.get("hx", 0.0), head.get("hyy", 0.0), head.get("rise", 0.0))),
            "Jaw": rd(head.get("jaw", 0.0), 0, 0)}
    return sk.fk(pose)


def mouth_frame(sk, head):
    """(upper teeth bottom-front, lower teeth top-front, axis into the mouth, head up) in rig space."""
    W = head_fk(sk, head)
    ut = sk.point(W, "Head", hx((0.0, -8.15, -2.6)))
    lt = sk.point(W, "Jaw", hx((0.0, -8.1, -2.63)))
    a = (sk.point(W, "Head", hx((0.0, 0.0, -2.6))) - sk.point(W, "Head", hx((0.0, -10.0, -2.6)))).normalized()
    up = (sk.point(W, "Head", hx((0.0, -8.15, 0.0))) - ut).normalized()
    return ut, lt, a, up


def bite_tower(sk, head, depth, sink=BITE_SINK):
    """Tower pose (centre, rotation) lying in the mouth along its axis, bottom end first: its top face
    `sink` above the upper teeth's edge, its far end `depth` past the teeth."""
    ut, _, a, _ = mouth_frame(sk, head)
    Rt = Vector((0.0, 1.0, 0.0)).rotation_difference(a).to_matrix() @ Matrix.Rotation(math.radians(BITE_SPIN), 3, "Y") @ BATON
    up = (mouth_frame(sk, head)[3])
    n_top = up - a * up.dot(a)
    n_top.normalize()
    half = max(abs((Rt @ Vector(v)).dot(n_top)) for v in ((2.0, 2.0, 0.0), (2.0, -2.0, 0.0)))
    axis_pt = ut - n_top * (half - sink)
    return axis_pt + a * (depth - TOWER_HALF.z), Rt


def chomp_jaw(sk, head, tc, Rt, sink=BITE_SINK):
    """Jaw angle at which the lower teeth sink `sink` into the tower's underside."""
    _, _, a, up = mouth_frame(sk, head)
    n_top = up - a * up.dot(a)
    n_top.normalize()
    half = max(abs((Rt @ Vector(v)).dot(n_top)) for v in ((2.0, 2.0, 0.0), (2.0, -2.0, 0.0)))
    bottom = Vector(tc) - n_top * half
    best = None
    for j10 in range(0, 551, 2):
        j = j10 / 10.0
        _, lt, _, _ = mouth_frame(sk, dict(head, jaw=j))
        e = (lt - bottom).dot(n_top) - sink
        if best is None or abs(e) < abs(best[1]):
            best = (j, e)
    return best[0]


def R_ry(deg):
    return Matrix.Rotation(math.radians(deg), 3, "Y")


def grab_keys(sk):
    s = "L"
    rest = rest_arm(s)
    Hg, wg, grip = grab_grip()
    c0 = TOWER_C0
    I3 = Matrix.Identity(3)
    Ha = hand_rot(0.0, 90.0, 0.0)
    twist = Matrix.Rotation(math.radians(CARRY_TWIST), 3, "Y")
    tc_c, Rt_b = bite_tower(sk, CHOMP_HEAD, BITE_DEPTH)              # where the tower is held for the bite
    jaw_c = chomp_jaw(sk, CHOMP_HEAD, tc_c, Rt_b)
    a_in = Rt_b @ Vector((0.0, 0.0, -1.0))                            # into the mouth
    tc_h = tc_c - a_in * 0.4                                         # held out, then pushed the last 0.4
    tc_o = Vector((-0.8, MAP_WALL_Y + 3.4, 7.6))
    R_m = Quaternion(qt(twist)).slerp(Quaternion(qt(Rt_b)), 0.5).to_matrix()

    def carried(tc, Rt):                    # hand pose of a carry key (for the free keys at the switch)
        return Vector(tc) + Rt @ grip[1], Rt @ grip[0]
    w_c, H_c = carried(tc_c, Rt_b)
    glass = off_glass(s)
    w_line = cuff_wrist(s, Ha, 4.0, MAP_WALL_OUT + 2.4, 8.4)
    w_pass = cuff_wrist(s, Ha, 3.9, MAP_WALL_Y + 0.4, 8.6)
    win = tuple(GRAB_WIN)
    far = tuple(CARRY_FAR)
    tuck = dict(thumb=-30.0, tpitch=10.0, open=35.0, spread=0.0)
    lean_back = dict(BITE_HEAD, hyy=BITE_HEAD["hyy"] + LUNGE, rise=BITE_HEAD["rise"] - 2.0, head_p=-6.0)
    E_c = H_euler(s, H_c)                                    # exported Euler of the hand at the bite (deg)
    E_1 = (E_c[0] - math.copysign(20.0, E_c[0]), 0.0, 90.0)   # fingers out (+X), still turned over
    E_2 = (0.0, 0.0, 90.0)                                   # rolled back (fingers still out)

    def eh(*e):
        return qt(euler_H(s, *e))
    keys = [
        (0, rest, "sine"),
        (3, dict(glass, eye_y=8.0, eye_p=6.0, hyy=4.0, hx=-3.0, head_y=4.0), "sine"),         # off the M7 glass
        (6, dict(wrist=(9.0, MAP_WALL_OUT + 10.5, 9.4), hyy=7.0, hx=-5.5, head_y=7.0), "sine"),
        (9, dict(wrist=(w_line[0], MAP_WALL_OUT + 10.0, w_line[2] + 0.3), hq=qt(Ha), fu=unit(0.3, 1.0, -0.02),
                 eye_y=12.0, eye_p=14.0, **dict(HEAD_ASIDE, head_y=9.0), **tuck), "sine"),     # lined up, far out
        (12, dict(wrist=(w_line[0], MAP_WALL_OUT + 5.5, w_line[2] + 0.1), ftw=60.0), "sine"),
        (14, dict(wrist=w_line, eye_p=18.0, ftw=TWIST_IN), "sine"),                           # fingers into the pane
        (16, dict(wrist=w_pass, eye_y=8.0, **HEAD_ASIDE), "linear"),                         # cuff through the pane
        (22, dict(wrist=(3.5, MAP_WALL_IN - 0.4, GRAB_Z - 0.1), fwin=win, open=65.0, spread=8.0, thumb=-12.0, tpitch=4.0, eye_p=22.0,
                  eye_y=6.0, fu=unit(0.2, 1.0, -0.03)), "sine"),
        (28, dict(wrist=tuple(wg + Vector((0.45, 0.0, 0.0))), hq=qt(Hg), open=75.0, spread=4.0, thumb=-8.0,
                  tpitch=0.0, fu=unit(0.3, 1.0, -0.03)), "sine"),
        (GRAB_F, dict(mode="carry", wrist=tuple(wg), hq=qt(Hg), tc=tuple(c0), tq=qt(I3), curl=72.0, icurl=68.0,
                      open=4.0, spread=-5.0, thumb=4.0, tcurl=16.0), "out"),              # GRAB
        (37, dict(tc=tuple(c0 + Vector((0.0, -2.3, 0.12))), fw=1.0, eye_p=18.0), "sine"),  # off the plate
        (43, dict(tc=tuple(c0 + Vector((-0.8, -3.4, 0.8))), tq=qt(Matrix.Rotation(math.radians(30.0), 3, "Y")), ftw=0.0),
         "sine"),
        (48, dict(tc=(-0.8, MAP_WALL_Y - 3.8, 7.7), tq=qt(twist), fwin=far, eye_p=12.0, eye_y=4.0), "sine"),   # laid over
        (54, dict(tc=tuple(tc_o), hyy=8.0, hx=-4.5, rise=2.5, jaw=6.0, eye_p=8.0, head_y=6.0), "sine"),  # out through the pane
        (61, dict(tc=tuple((tc_o + tc_h) / 2), tq=qt(R_m), fu=unit(1.0, 0.45, 0.05), fw=0.0, hyy=lean_back["hyy"] + 1.5,
                  hx=-1.5, rise=lean_back["rise"] - 1.0, head_p=-4.0, jaw=20.0, head_y=2.0, eye_p=14.0, eye_y=0.0,
                  lid=4.0), "sine"),
        (66, dict(tc=tuple(tc_h), tq=qt(Rt_b), fu=unit(1.0, 0.25, 0.3), jaw=BITE_JAW, lid=8.0, eye_p=20.0, **lean_back),
         "in"),                                                                              # held out, mouth wide
        (72, dict(jaw=BITE_JAW - 1.0, lid=14.0, puff=0.2, **BITE_HEAD), "sine"),             # the face lunges onto it
        (CHOMP_F, dict(tc=tuple(tc_c), wrist=tuple(w_c), hq=qt(H_c), jaw=jaw_c, lid=26.0, puff=0.5,
                       **CHOMP_HEAD), "out"),                                               # CHOMP
        (CHOMP_F + 1, dict(mode="free", jaw=max(0.0, jaw_c - 4.0)), "out"),
        (79, dict(wrist=tuple(w_c + Vector((2.4, 0.2, 0.5))), curl=56.0, icurl=52.0, open=0.0, spread=0.0, thumb=-30.0,
                  tpitch=8.0, tcurl=0.0, jaw=jaw_c - 10.0, puff=0.7), "sine"),               # lets go, clears the lips
        (82, dict(jaw=0.0, puff=1.0, lid=30.0), "sine"),
        (85, dict(wrist=tuple(w_c + Vector((6.5, 0.8, 0.8))), fu=unit(1.0, 0.4, 0.2), jaw=11.0, puff=0.8, rise=7.6,
                  hyy=0.4), "sine"),                                                         # slides along the wall
        # back to the glass with the fingers kept in the wall plane: past the cheek with the fingers down,
        # turned out (+X) while the forearm swings back, palm rolled over, then up to the glass. Planned in
        # the exported Euler angles so the clip never crosses the CFrame.Angles singularity or wraps.
        (90, dict(wrist=(18.0, MAP_WALL_OUT + 3.7, 9.3), hq=eh(*E_c), curl=36.0, icurl=34.0, fu=unit(1.0, 0.3, 0.1),
                  jaw=0.0, puff=1.0, head_r=1.5, rise=6.8, hyy=0.5, head_p=-8.0), "sine"),
        (94, dict(wrist=(18.6, MAP_WALL_OUT + 4.8, 9.5), hq=eh(*E_1), curl=18.0, icurl=16.0, fu=unit(0.05, 1.0, 0.05),
                  jaw=9.0, puff=0.8, head_r=-1.5, rise=5.6, hyy=0.6, head_p=-6.0), "sine"),
        (100, dict(wrist=(17.6, MAP_WALL_OUT + 5.4, 9.8), hq=eh(*E_2), curl=0.0, icurl=0.0, thumb=0.0, tpitch=0.0,
                  fu=unit(0.12, 1.0, 0.05), jaw=0.0, puff=1.0, head_r=0.0, rise=4.9, hyy=0.5, head_p=-5.0), "sine"),
        (105, dict(off_glass(s, out=1.8), fu=unit(0.35, 1.0, 0.06), jaw=6.0, puff=0.8, spread=0.0, thumb=0.0, tpitch=0.0, rise=3.4, hyy=0.4,
                   head_p=-4.0), "sine"),
        (111, dict(rest, jaw=0.0, puff=0.7, lid=20.0, rise=3.0, hyy=0.2, head_p=-3.0), "sine"),
        (119, dict(jaw=5.0, puff=0.5, rise=1.4, hyy=0.0, head_p=-1.2, lid=14.0), "sine"),
        (GRAB_LEN, dict(rest), "sine"),
    ]
    return fix_signs(keys)


def grab_clip(sk):
    _, _, grip = grab_grip()
    return C.param_clip(sk, "HandGrabLift", GRAB_LEN, False, grab_keys(sk), arm_fn("L", grip), step=1)


# ======================================================================================
# Map-fit checks (run by the export; every line starts with "[fit]")
# ======================================================================================

FIT_SLEEVE_CLEAR = 0.3                          # sleeve vs window frame
FIT_HAND_CLEAR = 0.1                            # hand / cuff / tower vs window frame (no visible cut)
CUSTOMER_TOP = 4.6                              # 4.1-stud avatars + 0.5


def arm_parts(s):
    return ["Hand" + s, "Hand" + s + "_Cuff", "Hand" + s + "_CuffButton", "Index" + s, "Index" + s + "2",
            "Index" + s + "2_Nails", "Fingers" + s, "Fingers" + s + "2", "Fingers" + s + "2_Nails", "Thumb" + s,
            "Thumb" + s + "2"] + (["HandR_Receipt"] if s == "R" else [])


def _np():
    import numpy as np
    return np


def _samples(o, step=0.3):
    """Object-local points: vertices plus points along every edge (<= step apart)."""
    np = _np()
    me = o.data
    co = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    ev = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ev)
    ev = ev.reshape(-1, 2)
    pts = [co]
    a, b = co[ev[:, 0]], co[ev[:, 1]]
    n = np.ceil(np.linalg.norm(b - a, axis=1) / step).astype(int)
    for k in sorted(set(n.tolist())):
        if k < 2:
            continue
        m = n == k
        t = np.linspace(0, 1, k + 1)[1:-1]
        pts.append((a[m][:, None, :] + t[None, :, None] * (b[m] - a[m])[:, None, :]).reshape(-1, 3))
    return np.concatenate(pts)


def _world(o, local):
    np = _np()
    M = np.array(o.matrix_world)
    return local @ M[:3, :3].T + M[:3, 3]


def _bone(arm, b):
    """(R 3x3, posed head) of a bone in world space (bones rest with identity rotation)."""
    np = _np()
    M = np.array(arm.matrix_world @ arm.pose.bones[b].matrix)
    return M[:3, :3], M[:3, 3]


def _opening_at(x, z):
    for k, (x0, x1, z0, z1) in MAP_OPENINGS.items():
        if x0 <= x <= x1 and z0 <= z <= z1:
            return k
    return None


def _slab_report(P):
    """Points inside the wall slab: (openings used, worst clearance to the frame edges); 'WALL' when a
    point is in solid wall (including the transom bars)."""
    np = _np()
    m = (P[:, 1] <= MAP_WALL_OUT) & (P[:, 1] >= MAP_WALL_IN)
    if not m.any():
        return set(), None
    Q = P[m]
    best = np.full(len(Q), -9.0)
    which = np.array([None] * len(Q), dtype=object)
    for k, (x0, x1, z0, z1) in MAP_OPENINGS.items():
        c = np.minimum.reduce([Q[:, 0] - x0, x1 - Q[:, 0], Q[:, 2] - z0, z1 - Q[:, 2]])
        better = c > best
        best[better] = c[better]
        which[better & (c >= 0)] = k
    used = {w[:-2] if w.endswith(("lo", "hi")) else w for w in which if w is not None}
    if (which == None).any():                                               # noqa: E711
        used.add("WALL")
    return used, float(best.min())


def _in_room(P):
    return (P[:, 1] < MAP_WALL_IN) & (P[:, 1] > MAP_BACK_WALL_Y + 0.5)


def _room_hits(P, tag, frame, out, floor=True):
    """Booths (below 4.6), counter body (below 3.0), back wall, ceiling (20) in the room, floor/ground."""
    np = _np()
    eps = 0.005
    for name, (x0, x1) in MAP_BOOTHS.items():
        m = (P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 1] > MAP_BOOTH_Y[0]) & (P[:, 1] < MAP_BOOTH_Y[1]) \
            & (P[:, 2] < MAP_BOOTH_TOP - eps)
        if m.any():
            out.append((tag, frame, name, float(MAP_BOOTH_TOP - P[m, 2].min())))
    (cx0, cx1), (cy0, cy1), ctop = MAP_COUNTER
    m = (P[:, 0] > cx0) & (P[:, 0] < cx1) & (P[:, 1] > cy0) & (P[:, 1] < cy1) & (P[:, 2] < ctop - eps)
    if m.any():
        out.append((tag, frame, "counter", float(ctop - P[m, 2].min())))
    yb = MAP_BACK_WALL_Y
    m = (np.abs(P[:, 1] - yb) < 0.5) & ~((np.abs(P[:, 0]) < 8.0) & (P[:, 2] > 3.0) & (P[:, 2] < 12.0))
    if m.any():
        out.append((tag, frame, "back wall", 0.5 - float(np.abs(P[m, 1] - yb).min())))
    m = _in_room(P) & (P[:, 2] > MAP_CEILING + eps)
    if m.any():
        out.append((tag, frame, "ceiling", float(P[m, 2].max() - MAP_CEILING)))
    if floor and (P[:, 2] < -eps).any():
        out.append((tag, frame, "floor", float(-P[:, 2].min())))


def _customer_dip(P):
    """Lowest arm point over the dining-room floor outside the booths and the counter (avatars stand
    up to CUSTOMER_TOP), and its distance in front of the counter's customer edge."""
    np = _np()
    m = _in_room(P) & (P[:, 2] < CUSTOMER_TOP)
    (cx0, cx1), (cy0, cy1), _ = MAP_COUNTER
    m &= ~((P[:, 0] > cx0) & (P[:, 0] < cx1) & (P[:, 1] > cy0 - 0.01) & (P[:, 1] < cy1 + 0.01))
    for x0, x1 in MAP_BOOTHS.values():
        m &= ~((P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 1] > MAP_BOOTH_Y[0]) & (P[:, 1] < MAP_BOOTH_Y[1]))
    if not m.any():
        return None
    Q = P[m]
    return float(Q[:, 2].min()), float((Q[:, 1] - cy1).max())       # lowest z, farthest reach from the counter


def _ellipsoid_depth(P, c, r):
    np = _np()
    d = np.sqrt((((P - c) / r) ** 2).sum(axis=1))
    k = d < 1.0
    if not k.any():
        return 0.0
    return float(((1.0 - d[k]) * min(r)).max())


def _to_design(arm, P, bone):
    """World points -> the face's design frame carried by `bone` (Head or Jaw)."""
    np = _np()
    R, h = _bone(arm, bone)
    rest = np.array(tuple(hx(HEAD_JOINT if bone == "Head" else JAW_JOINT)))
    local = (P - h) @ R + rest
    return (local - np.array(tuple(HEAD_T))) / HEAD_S


def _head_depth(arm, P):
    """How deep points go into the face (head, nose, ears, eyes, chin), in studs."""
    np = _np()
    d = _to_design(arm, P, "Head")
    worst = _ellipsoid_depth(d, np.array(tuple(HEAD_C)), np.array((12.3, 9.8, 13.0)))
    worst = max(worst, _ellipsoid_depth(d, np.array(tuple(NOSE_C)), np.array(tuple(NOSE_R))))
    for s in ("L", "R"):
        worst = max(worst, _ellipsoid_depth(d, np.array(tuple(EAR_C[s])), np.array(tuple(EAR_R))))
        worst = max(worst, _ellipsoid_depth(d, np.array(tuple(EYE[s])), np.full(3, EYE_R)))
    dj = _to_design(arm, P, "Jaw")
    worst = max(worst, _ellipsoid_depth(dj, np.array(tuple(CHIN_C)), np.array(tuple(CHIN_R))))
    return worst * HEAD_S


def _tower_face_poke(arm, T):
    """The tower may only go into the head through the mouth: tower points inside the face volume and
    near its surface (< 0.8 studs deep; deeper ones are hidden inside the head) must lie in the opening
    between the lips, inside the lip corners. Returns (worst depth of an offending point, fraction of
    the tower points inside the head)."""
    np = _np()
    d = _to_design(arm, T, "Head")
    dj = _to_design(arm, T, "Jaw")
    r = np.array((12.3, 9.8, 13.0))
    eh = np.sqrt((((d - np.array(tuple(HEAD_C))) / r) ** 2).sum(axis=1))
    ec = np.sqrt((((dj - np.array(tuple(CHIN_C))) / np.array(tuple(CHIN_R))) ** 2).sum(axis=1))
    inside = (eh < 1.0) | (ec < 1.0)
    depth = np.maximum((1.0 - eh) * 9.8, (1.0 - ec) * 2.6) * HEAD_S
    x = d[:, 0]
    corridor = (np.abs(x) < 6.2) & (d[:, 2] < -1.06 - 0.018 * x ** 2) & (dj[:, 2] > -4.14 + 0.0187 * dj[:, 0] ** 2)
    bad = inside & (depth < 0.8 * HEAD_S) & ~corridor
    worst = float(depth[bad].max()) if bad.any() else 0.0
    return worst, float(inside.mean())


def _forearm_axis(arm, s):
    np = _np()
    R, h = _bone(arm, "Forearm" + s)
    R0 = np.array(FOREARM_REST[s])
    a = h + R @ (R0 @ np.array(tuple(canon(s, FA_A0 + sleeve_dir() * SLEEVE_S0))))
    d = R @ (R0 @ np.array(tuple(canon(s, sleeve_dir()))))
    return a, d


def _sleeve_section(a, d, y, s_at):
    np = _np()
    t = (y - a[1]) / d[1]
    c = a + t * d
    n1 = np.cross(d, (0.0, 0.0, 1.0))
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(d, n1)
    ang = np.linspace(0, 2 * math.pi, 64, endpoint=False)
    rr = sleeve_r(s_at)
    pts = c + rr * (np.cos(ang)[:, None] * n1 + np.sin(ang)[:, None] * n2)
    pts = pts + ((y - pts[:, 1]) / d[1])[:, None] * d
    return c, rr, pts[:, [0, 2]].min(axis=0), pts[:, [0, 2]].max(axis=0)


def _sleeve_crossing(arm, s):
    """Where the sleeve axis crosses the wall plane: (x, z, opening, radius, clearance) or None."""
    a, d = _forearm_axis(arm, s)
    if abs(d[1]) <= 1e-6:
        return None
    t = (MAP_WALL_Y - a[1]) / d[1]
    if t < 0.0 or t > SLEEVE_LEN:
        return None
    c, rr, _, _ = _sleeve_section(a, d, MAP_WALL_Y, t)
    op = _opening_at(c[0], c[2])
    clear = -9.0
    if op:
        x0, x1, z0, z1 = MAP_OPENINGS[op]
        clear = 9.0
        for y in (MAP_WALL_OUT, MAP_WALL_Y, MAP_WALL_IN):
            ty = min(max((y - a[1]) / d[1], 0.0), SLEEVE_LEN)
            _, _, mn, mx = _sleeve_section(a, d, y, ty)
            clear = min(clear, mn[0] - x0, x1 - mx[0], mn[1] - z0, z1 - mx[1])
    return float(c[0]), float(c[2]), op, rr, float(clear)


def _tower_local_pts(step=0.5):
    np = _np()
    (x0, x1), (y0, y1), (z0, z1) = MAP_TOWER
    xs = np.linspace(x0, x1, int((x1 - x0) / step) + 1)
    ys = np.linspace(y0, y1, int((y1 - y0) / step) + 1)
    zs = np.linspace(z0, z1, int((z1 - z0) / step) + 1)
    g = np.array(np.meshgrid(xs, ys, zs, indexing="ij")).reshape(3, -1).T
    return g


def _wrist_bend(arm, s):
    np = _np()
    Rh, _ = _bone(arm, "Hand" + s)
    Rf, _ = _bone(arm, "Forearm" + s)
    H = Rh @ np.array(HAND_REST[s])
    F = Rf @ np.array(FOREARM_REST[s])
    d = np.array(tuple(canon(s, sleeve_dir())))
    c = float(np.clip((H @ d) @ (F @ d), -1.0, 1.0))
    return math.degrees(math.acos(c))


def fit_checks(sk, acts):
    """Prints the map-fit report for the rest pose, HandSlam, HandGrabLift, Burp; returns the failures."""
    import bpy
    np = _np()
    arm = sk.arm
    arm.data.pose_position = "POSE"
    sc = bpy.context.scene
    objs = {o.name: o for o in ns._tagged_objects()}
    samp = {n: _samples(o) for n, o in objs.items() if n.startswith(("Hand", "Index", "Fingers", "Thumb"))}
    samp_head = {n: _samples(o, 0.8) for n, o in objs.items() if n.startswith(("Head", "Jaw", "Eye", "Lid", "Cheek"))}
    fails = []
    by_name = {a.name: a for a in acts}

    def P(names):
        return np.concatenate([_world(objs[n], samp[n]) for n in names])

    def head_pts():
        return np.concatenate([_world(objs[n], samp_head[n]) for n in samp_head])

    # ---------------- rest pose ----------------
    C.set_action(arm, by_name["Look"])
    sc.frame_set(0)
    print("  [fit] rest pose (Look f0 = rest):")
    for s in ("L", "R"):
        hand = P(arm_parts(s))
        slv = P(["Hand" + s + "_Sleeve"])
        gap = float(hand[:, 1].min() - MAP_WALL_OUT)
        hd = _head_depth(arm, np.concatenate([hand, slv]))
        used, cl = _slab_report(np.concatenate([hand, slv]))
        print(f"  [fit]   Hand{s}: palm side {gap:.2f} outside the wall's outer face (palm on the glass of "
              f"{'M7' if s == 'L' else 'the transom over the door'}), wrist bend {_wrist_bend(arm, s):.0f} deg, "
              f"arm into the face {hd:.2f}, sleeve end at Roblox {tuple(round(c, 1) for c in to_world(Vector(slv[np.argmax(slv[:, 1])])))}")
        if gap < 0.0 or used:
            fails.append(f"rest: Hand{s} touches the wall/glass ({gap:.2f}, {sorted(used)})")
        if hd > 0.05:
            fails.append(f"rest: Hand{s} arm goes {hd:.2f} into the face")
    hp = head_pts()
    used, cl = _slab_report(hp)
    front = float(hp[:, 1].min() - MAP_WALL_OUT)
    eyes = [tuple(round(c, 2) for c in to_world(sk.head["Eye" + s])) for s in ("L", "R")]
    print(f"  [fit]   face: closest point {front:.2f} behind the wall's outer face (nose tip), eyes at Roblox {eyes} "
          f"(picture window x +-7.2, panes y 3.5-11.85 / 12.15-16.5), crown y {hp[:, 2].max():.2f}")
    if used:
        fails.append(f"rest: face in the wall {sorted(used)}")

    def run_clip(act, s, window, extra=None):
        C.set_action(arm, act)
        n0, n1 = act["ns_start"], act["ns_end"]
        hits, worst_sleeve, worst_hand, worst_head = [], (9.0, None), (9.0, None), (0.0, None)
        face_wall, bend, dip = (9.0, None), (0.0, None), (9.0, None, None)
        print(f"  [fit] {act.name}: per frame - sleeve axis crossing of the wall plane (x, z, pane, radius, "
              f"clearance) | arm mesh in the wall | wrist bend | lowest point over the room floor")
        for f in range(n0, n1 + 1):
            sc.frame_set(f)
            parts = {n: _world(objs[n], samp[n]) for n in arm_parts(s)}
            hand = np.concatenate(list(parts.values()))
            slv = P(["Hand" + s + "_Sleeve"])
            inside = bool((hand[:, 1] < MAP_WALL_OUT).any())
            cr = _sleeve_crossing(arm, s)
            line = f"  [fit]   f{f:3d} hand {'in ' if inside else 'out'} "
            if cr:
                x, z, op, rr, cl = cr
                line += f"axis ({x:6.2f}, {z:5.2f}) {op or 'WALL'} r {rr:.2f} clear {cl:5.2f}"
                if not op or not op.startswith(window) or cl < FIT_SLEEVE_CLEAR:
                    fails.append(f"{act.name} f{f}: sleeve crosses {op or 'solid wall'} clear {cl:.2f}")
                if cl < worst_sleeve[0]:
                    worst_sleeve = (cl, f)
            elif inside:
                line += "axis does not reach the wall (hand/cuff in the opening)        "
            else:
                line += "outside                                                       "
            fh = []
            for n, P_ in list(parts.items()) + [("Hand" + s + "_Sleeve", slv)]:
                used, cl_mesh = _slab_report(P_)
                if cl_mesh is not None and ({u for u in used} - {window} or cl_mesh < FIT_HAND_CLEAR):
                    fh.append((n, sorted(used), cl_mesh))
                _room_hits(P_, n, f, hits)
            used, cl_mesh = _slab_report(np.concatenate([hand, slv]))
            if cl_mesh is not None:
                line += f" | wall: {','.join(sorted(used))} {cl_mesh:5.2f}"
                if cl_mesh < worst_hand[0]:
                    worst_hand = (cl_mesh, f)
            for h in fh:
                fails.append(f"{act.name} f{f}: {h[0]} in the wall at {h[1]} clear {h[2]:.2f}")
            b = _wrist_bend(arm, s)
            line += f" | bend {b:4.0f}"
            if b > bend[0]:
                bend = (b, f)
            cd = _customer_dip(np.concatenate([hand, slv]))
            if cd:
                line += f" | low {cd[0]:4.2f} ({cd[1]:+.1f} from counter)"
                if cd[0] < dip[0]:
                    dip = (cd[0], f, cd[1])
            print(line)
            hp_ = head_pts()
            used_h, cl_h = _slab_report(hp_)
            if cl_h is not None and (used_h - {"PW"} or cl_h < 0.0):
                fails.append(f"{act.name} f{f}: face in the wall {sorted(used_h)} {cl_h:.2f}")
            gap = float(hp_[:, 1].min() - MAP_WALL_OUT)
            if gap < face_wall[0]:
                face_wall = (gap, f)
            hd = _head_depth(arm, np.concatenate([hand, slv]))
            if hd > worst_head[0]:
                worst_head = (hd, f)
            if extra:
                extra(f, hand, hits)
        for tag, f, what, depth in hits:
            fails.append(f"{act.name} f{f}: {tag} in {what} by {depth:.2f}")
        print(f"  [fit] {act.name}: worst sleeve clearance {worst_sleeve[0]:.2f} (f{worst_sleeve[1]}), worst arm-mesh "
              f"clearance in the wall {worst_hand[0]:.2f} (f{worst_hand[1]}), booth/counter/back-wall/ceiling/floor hits "
              f"{len(hits)}, arm into the face {worst_head[0]:.2f} (f{worst_head[1]}), max wrist bend {bend[0]:.0f} deg "
              f"(f{bend[1]}), face front vs the wall's outer face {face_wall[0]:.2f} (f{face_wall[1]}; < 0 = through the "
              f"picture window, panes hide)")
        if dip[1] is not None:
            print(f"  [fit] {act.name}: arm dips to {dip[0]:.2f} over the room floor at f{dip[1]} ({dip[2]:+.1f} studs from "
                  f"the counter's customer edge; avatars + margin = {CUSTOMER_TOP})")
        else:
            print(f"  [fit] {act.name}: arm never below {CUSTOMER_TOP} over the room floor")
        if worst_head[0] > 0.05:
            fails.append(f"{act.name}: arm goes {worst_head[0]:.2f} into the face at f{worst_head[1]}")
        sc.frame_set(0)
        return dip

    # ---------------- HandSlam ----------------
    slam = by_name["HandSlam"]
    C.set_action(arm, slam)
    sc.frame_set(SLAM_F)
    hand = P([n for n in arm_parts("R") if not n.startswith("HandR_Cuff")])
    rp = _world(objs["HandR_Receipt"], samp["HandR_Receipt"])
    rcen = (rp.min(axis=0) + rp.max(axis=0)) / 2
    Rh, _ = _bone(arm, "HandR")
    nrm = Rh @ np.array(HAND_REST["R"]) @ np.array((0.0, 0.0, 1.0))
    tilt = math.degrees(math.acos(min(1.0, abs(nrm[2]))))
    low = float(min(hand[:, 2].min(), rp[:, 2].min()))
    print(f"  [fit] HandSlam f{SLAM_F} (t={SLAM_F / C.FPS:.3f}s): THE BIG ONE centre Roblox "
          f"{tuple(round(c, 2) for c in to_world(Vector(rcen)))} (target {tuple(round(c, 2) for c in to_world(SLAM_RC))}), "
          f"underside {rp[:, 2].min():.3f} vs counter top {MAP_COUNTER[2]}, tilt {tilt:.2f} deg, hand lowest {low:.3f}; "
          f"receipt x {rp[:, 0].min():.2f}..{rp[:, 0].max():.2f} z(Roblox) {PIVOT_Z - rp[:, 1].max():.2f}.."
          f"{PIVOT_Z - rp[:, 1].min():.2f} on the counter x -8..8 z -9.5..-6.5")
    if (np.linalg.norm(rcen[:2] - np.array(tuple(SLAM_RC))[:2]) > 0.3 or not (3.0 <= low <= 3.1)
            or tilt >= 5.0 or abs(rp[:, 2].min() - MAP_COUNTER[2]) > 0.06):
        fails.append("HandSlam: THE BIG ONE does not land flat on the counter target")
    run_clip(slam, "R", "M3")

    # ---------------- HandGrabLift ----------------
    grab = by_name["HandGrabLift"]
    C.set_action(arm, grab)
    sc.frame_set(GRAB_F)
    Rg, hg = _bone(arm, "HandL")
    Mg = np.eye(4)
    Mg[:3, :3], Mg[:3, 3] = Rg, hg
    Mg_inv = np.linalg.inv(Mg)
    tower0 = _tower_local_pts()
    (tx0, tx1), (ty0, ty1), (tz0, tz1) = MAP_TOWER
    on_surf = (np.isclose(tower0[:, 0], tx0) | np.isclose(tower0[:, 0], tx1) | np.isclose(tower0[:, 1], ty0)
               | np.isclose(tower0[:, 1], ty1) | np.isclose(tower0[:, 2], tz0) | np.isclose(tower0[:, 2], tz1))
    tower_s = tower0[on_surf]
    gp = P(["HandL", "IndexL", "IndexL2", "FingersL", "FingersL2", "ThumbL", "ThumbL2"])
    tc = np.array(((tx0 + tx1) / 2, (ty0 + ty1) / 2))
    band = gp[np.abs(gp[:, 2] - GRAB_Z) < 2.4]
    rel = band[:, :2] - tc
    cheb = np.max(np.abs(rel), axis=1)
    near = cheb < 2.0 + 1.3
    ang = np.degrees(np.arctan2(rel[near, 1], rel[near, 0]))
    cover = len({int((a + 180) // 10) for a in ang}) * 10
    sink = float(max(0.0, 2.0 - cheb.min())) if len(cheb) else 0.0
    zc = float(np.mean(band[near, 2])) if near.any() else float("nan")
    grab_pt = Vector((0.0, (ty0 + ty1) / 2, GRAB_Z))
    print(f"  [fit] HandGrabLift grab f{GRAB_F} (t={GRAB_F / C.FPS:.3f}s): grabPoint Roblox "
          f"{tuple(round(c, 2) for c in to_world(grab_pt))}; palm + fingers wrap {cover} deg round the 4x4 tower at "
          f"z~{zc:.2f} (palm on +X, fingers round the room side onto -X, thumb over the top); deepest sink into the "
          f"tower {sink:.2f}")
    if cover < 180 or sink > 0.6:
        fails.append(f"HandGrabLift: grip wraps {cover} deg, sinks {sink:.2f}")

    def tower_world(f=None):
        R_, h_ = _bone(arm, "HandL")
        M = np.eye(4)
        M[:3, :3], M[:3, 3] = R_, h_
        T = M @ Mg_inv
        return T

    tower_hits = []
    tower_wall = [9.0, None]
    poke = [0.0, None]

    def tower_extra(f, hand, hits):
        if not (GRAB_F < f <= CHOMP_F):
            return
        T = tower_world()
        Ts = tower_s @ T[:3, :3].T + T[:3, 3]
        _room_hits(Ts, "tower", f, tower_hits)
        (px0, px1), (py0, py1), ptop = MAP_PLATE
        m = (Ts[:, 0] > px0) & (Ts[:, 0] < px1) & (Ts[:, 1] > py0) & (Ts[:, 1] < py1) & (Ts[:, 2] < ptop - 0.005)
        if m.any() and f > GRAB_F + 1:
            tower_hits.append(("tower", f, "plate", float(ptop - Ts[m, 2].min())))
        used, cl = _slab_report(Ts)
        if cl is not None:
            if cl < tower_wall[0]:
                tower_wall[0], tower_wall[1] = cl, f
            if used - {"PW"} or cl < FIT_HAND_CLEAR:
                tower_hits.append(("tower", f, "wall " + ",".join(sorted(used)), -cl))
        dp, _ = _tower_face_poke(arm, Ts)
        if dp > poke[0]:
            poke[0], poke[1] = dp, f

    run_clip(grab, "L", "PW", tower_extra)
    for tag, f, what, depth in tower_hits:
        fails.append(f"HandGrabLift f{f}: tower in {what} by {depth:.2f}")
    print(f"  [fit] HandGrabLift tower (carried f{GRAB_F}..f{CHOMP_F}): {len(tower_hits)} hits on booths/counter/plate/"
          f"ceiling/wall; closest to a window frame {tower_wall[0]:.2f} (f{tower_wall[1]}); tower through the face "
          f"outside the mouth {poke[0]:.2f} (f{poke[1]})")
    if poke[0] > 0.15:
        fails.append(f"HandGrabLift: tower pokes {poke[0]:.2f} through the face outside the mouth at f{poke[1]}")
    C.set_action(arm, grab)
    sc.frame_set(CHOMP_F)
    T = tower_world()
    Tv = tower0 @ T[:3, :3].T + T[:3, 3]
    _, frac = _tower_face_poke(arm, Tv)
    lips = np.concatenate([_world(objs[n], _samples(objs[n], 0.5)) for n in ("Head_Lip", "Jaw_Lip")])
    Ts = tower_s @ T[:3, :3].T + T[:3, 3]
    dmin = float(np.min(np.linalg.norm(Ts[:, None, :] - lips[None, ::3, :], axis=2)))
    up = _world(objs["Head_Lip"], _samples(objs["Head_Lip"], 0.5))
    lo = _world(objs["Jaw_Lip"], _samples(objs["Jaw_Lip"], 0.5))
    du = float(np.min(np.linalg.norm(Ts[:, None, :] - up[None, ::2, :], axis=2)))
    dl = float(np.min(np.linalg.norm(Ts[:, None, :] - lo[None, ::2, :], axis=2)))
    hl = np.concatenate([P(["HandL", "IndexL", "IndexL2", "FingersL", "FingersL2"])])
    hand_lip = float(np.min(np.linalg.norm(hl[::3, None, :] - lips[None, ::3, :], axis=2)))
    dT = _to_design(arm, Tv, "Head")
    behind = float((dT[:, 1] > -8.73).mean())               # behind the lip line (only reachable via the mouth)
    dH = _to_design(arm, hl, "Head")
    dHj = _to_design(arm, hl, "Jaw")
    xh = dH[:, 0]
    in_mouth = (np.abs(xh) < 6.2) & (dH[:, 2] < -1.06 - 0.018 * xh ** 2) & (dHj[:, 2] > -4.14 + 0.0187 * dHj[:, 0] ** 2)
    hand_ahead = float(-8.73 - (dH[in_mouth, 1].max() if in_mouth.any() else -99.0)) * HEAD_S   # hand vs the lip line
    print(f"  [fit] HandGrabLift CHOMP f{CHOMP_F} (t={CHOMP_F / C.FPS:.3f}s): {behind * 100:.0f}% of the tower's volume "
          f"is behind the lip line ({frac * 100:.0f}% inside the head shell), in through the mouth; tower to upper lip "
          f"{du:.2f}, to lower lip {dl:.2f}, nearest lip {dmin:.2f}; hand {hand_ahead:.2f} in front of the lip line, "
          f"{hand_lip:.2f} from the lips; tower centre Roblox {tuple(round(c, 2) for c in to_world(Vector(Tv.mean(axis=0))))}")
    if behind < 0.5 or du > 1.5 or dl > 1.5 or hand_ahead < 0.0:
        fails.append(f"HandGrabLift: tower not in the mouth at chomp ({behind * 100:.0f}% in, lips {du:.2f}/{dl:.2f}, "
                     f"hand {hand_ahead:.2f})")

    # ---------------- face clips: face vs the wall (head rises / tips) ----------------
    for name in ("Look", "Chew", "Burp", "Blink"):
        act = by_name[name]
        C.set_action(arm, act)
        worst = (9.0, None)
        for f in range(act["ns_start"], act["ns_end"] + 1):
            sc.frame_set(f)
            hp_ = head_pts()
            used_h, cl_h = _slab_report(hp_)
            if cl_h is not None and (used_h - {"PW"} or cl_h < 0.0):
                fails.append(f"{name} f{f}: face in the wall {sorted(used_h)}")
            g = float(hp_[:, 1].min() - MAP_WALL_OUT)
            if g < worst[0]:
                worst = (g, f)
        print(f"  [fit] {name}: face front vs the wall's outer face closest {worst[0]:.2f} (f{worst[1]})")
    sc.frame_set(0)
    print(f"  [fit] RESULT: {'PASS' if not fails else 'FAIL'} ({len(fails)} issue(s))")
    for m in fails[:400]:
        print("  [fit]   - " + m)
    if len(fails) > 400:
        print(f"  [fit]   ... {len(fails) - 400} more")
    return fails


# ======================================================================================

def build():
    sk = C.Skel("PatronRig", JOINTS, bone_len=0.8)
    build_model(sk)
    acts = [blink_clip(sk), look_clip(sk), chew_clip(sk), slam_clip(sk), grab_clip(sk), burp_clip(sk)]
    C.rest_pose(sk.arm)

    def checks():
        fit_checks(sk, acts)

    w_s, H_s, _ = slam_pose()
    rc = w_s + H_s @ canon("R", RECEIPT_OFF)
    grab_pt = Vector((0.0, TOWER_C0.y, GRAB_Z))
    hc = hx(HEAD_C)
    meta = {
        "root": {"center": [0, round(hc.z, 3), round(hc.y, 3)],
                 "size": [round(24 * HEAD_S, 3), round(26 * HEAD_S, 3), round(20 * HEAD_S, 3)]},
        "clipSpeedRef": {},
        "placement": {"pivot": [0.0, 0.0, PIVOT_Z], "yaw": 180, "floor": 0.0, "eyeLine": EYE_LINE,
                      "headScale": HEAD_S, "windowWallZ": MAP_WALL_Y,
                      "note": f"pivot CFrame.new(0, 0, {PIVOT_Z}) * CFrame.Angles(0, math.pi, 0) (faces +Z): the front "
                              f"wall's centre plane is {-MAP_WALL_Y:.1f} studs in front of the pivot; eyes in the picture "
                              f"window's lower pane, palms on the M7 glass and the transom glass over the door"},
        "slamPoint": [round(c, 3) for c in to_local(rc)],
        "grabPoint": [round(c, 3) for c in to_local(grab_pt)],
        "windows": {"HandSlam": "M3 lower pane", "HandGrabLift": "picture window lower pane (right half)"},
        "props": {"receipt": "HandR_Receipt (THE BIG ONE): show during HandSlam until events.HandSlam.slam, then "
                             "hide and spawn the real receipt at slamPoint"},
        "events": {"Blink": {"closed": 0.13}, "HandSlam": {"slam": round(SLAM_F / C.FPS, 3)},
                   "HandGrabLift": {"grab": round(GRAB_F / C.FPS, 3), "chomp": round(CHOMP_F / C.FPS, 3)},
                   "Burp": {"burp": 0.73}},
    }
    return {"skel": sk, "arm": sk.arm, "actions": acts, "checks": [checks],
            "export": {"rig": sk.arm, "pivot": (0.0, 0.0, 0.0), "meta": meta}}


STRIPS = {
    "Blink": dict(frames=[0, 4, 7, 13], yaw=-20),
    "Look": dict(frames=[0, 30, 64, 92], yaw=-15),
    "Chew": dict(frames=[0, 7, 15, 22], yaw=-25),
    "HandSlam": dict(frames=[0, 9, 19, 26, SLAM_F, 63], yaw=-60, pitch=20),
    "HandGrabLift": dict(frames=[10, GRAB_F, 49, 63, 74, CHOMP_F], yaw=-55, pitch=15),
    "Burp": dict(frames=[0, 12, 22, 48], yaw=-25),
}

# ---- finale cameras (Roblox world: position, look-at, vertical FOV), both inside the dining room ----
SHOT1 = dict(pos=(-10.0, 7.4, -27.0), look=(1.2, 8.0, -45.0), fov=50.0)     # the bite: grab -> chomp
SHOT2 = dict(pos=(0.0, 4.6, -24.0), look=(0.0, 10.8, -46.0), fov=50.0)      # after chomp: chewing, burp


# ======================================================================================
# Map review strips (preview only): proxy diner geometry, never tagged, never exported
# ======================================================================================

def _proxy_box(name, x, y, z, color, mat="SmoothPlastic"):
    o = ns.box((x[1] - x[0], y[1] - y[0], z[1] - z[0]), loc=((x[0] + x[1]) / 2, (y[0] + y[1]) / 2, (z[0] + z[1]) / 2),
               bevel=0.0, name=name)
    ns.apply_all(o)
    o.name = name
    o.data.materials.append(ns.material(color, mat))
    return o


def _wall_boxes(prefix, y0, y1, openings, x_range=(-40.0, 40.0), z_range=(0.0, 20.0), color="#7E8490"):
    xs = sorted({x_range[0], x_range[1]} | {v for (x0, x1, _, _) in openings for v in (x0, x1)})
    objs = []
    for xa, xb in zip(xs[:-1], xs[1:]):
        xm = (xa + xb) / 2
        holes = sorted((z0, z1) for (x0, x1, z0, z1) in openings if x0 <= xm <= x1)
        z = z_range[0]
        for z0, z1 in holes + [(z_range[1], z_range[1])]:
            if z0 - z > 1e-4:
                objs.append(_proxy_box(f"{prefix}{xa:+.1f}_{z:.1f}", (xa, xb), (y0, y1), (z, z0), color))
            z = max(z, z1)
    return objs


def map_proxies():
    """Front wall with every pane/transom/door, back wall + pass-through, booths, the Plate's three tables,
    a 4x4x7.5 chunk tower, counter, floor, 20-stud ceiling, neon sign, outside ground. Names start with
    'Px' and none carry ns_part, so nothing here can reach an export."""
    objs = _wall_boxes("PxWall", MAP_WALL_IN, MAP_WALL_OUT, list(MAP_OPENINGS.values()), color="#2B3550")
    yb = MAP_BACK_WALL_Y
    objs += _wall_boxes("PxBack", yb - 0.5, yb + 0.5, [(-8.0, 8.0, 3.0, 12.0)], color="#3A3150")
    objs.append(_proxy_box("PxFloor", (-40, 40), (yb, MAP_WALL_IN), (-0.1, 0.0), "#2E2A33"))
    for i in range(8):                               # checker strip along the window booths
        objs.append(_proxy_box(f"PxChk{i}", (-40 + i * 10, -35 + i * 10), (MAP_WALL_IN - 6, MAP_WALL_IN - 0.1),
                               (-0.08, 0.005), "#D9D2C4"))
    objs.append(_proxy_box("PxCeil", (-40, 40), (yb, MAP_WALL_IN), (20.0, 20.4), "#1C2133"))
    objs.append(_proxy_box("PxSideL", (-40.5, -40.0), (yb, MAP_WALL_IN), (0, 20), "#2B3550"))
    objs.append(_proxy_box("PxSideR", (40.0, 40.5), (yb, MAP_WALL_IN), (0, 20), "#2B3550"))
    objs.append(_proxy_box("PxGround", (-90, 90), (MAP_WALL_OUT, 90), (-0.1, 0.0), "#1E2328"))
    objs.append(_proxy_box("PxKitchen", (-8, 8), (yb - 12, yb - 0.5), (-0.1, 12), "#C9C0AE"))   # behind the pass-through
    objs.append(_proxy_box("PxSign", (-13, 13), (yb - 0.8, yb - 0.5), (12.6, 18.6), "#FF4FA3", "Neon"))
    objs.append(_proxy_box("PxNeonL", (-39.9, -39.7), (yb, MAP_WALL_IN), (18.6, 18.9), "#38E1FF", "Neon"))
    objs.append(_proxy_box("PxNeonR", (39.7, 39.9), (yb, MAP_WALL_IN), (18.6, 18.9), "#38E1FF", "Neon"))
    objs.append(_proxy_box("PxNeonW", (-40, 40), (MAP_WALL_IN - 0.25, MAP_WALL_IN - 0.05), (18.6, 18.9), "#FF4FA3", "Neon"))
    (cx0, cx1), (cy0, cy1), ctop = MAP_COUNTER
    objs.append(_proxy_box("PxCounter", (cx0, cx1), (cy0, cy1), (0.0, ctop), "#B9C0C6", "Metal"))
    for k, (x0, x1) in MAP_BOOTHS.items():
        by0, by1 = MAP_BOOTH_Y
        objs.append(_proxy_box("Px" + k + "Seat", (x0, x1), (by1 - 2.2, by1), (0.0, 1.6), "#C23A52"))
        objs.append(_proxy_box("Px" + k + "Back", (x0, x1), (by1 - 0.9, by1), (1.6, MAP_BOOTH_TOP), "#C23A52"))
        objs.append(_proxy_box("Px" + k + "Table", (x0 + 0.4, x1 - 0.4), (by0, by0 + 1.7), (2.6, 2.8), "#E8E1D0"))
    (px0, px1), (py0, py1), ptop = MAP_PLATE
    for i in range(3):
        a = px0 + i * 2.6
        objs.append(_proxy_box(f"PxPlate{i}", (a + 0.04, a + 2.56), (py0, py1), (ptop - 0.2, ptop), "#E8E1D0"))
        objs.append(_proxy_box(f"PxPlateLeg{i}", (a + 1.0, a + 1.6), (py0 + 1.0, py1 - 1.0), (0.0, ptop - 0.2), "#B9C0C6"))
    (tx0, tx1), (ty0, ty1), (tz0, tz1) = MAP_TOWER
    h = (tz1 - tz0) / 3
    fill = ["#C0392B", "#7DBB4A", "#F2B33D"]
    for i in range(3):
        z = tz0 + i * h
        objs.append(_proxy_box(f"PxTowerB{i}", (tx0, tx1), (ty0, ty1), (z, z + 0.7), "#D9A24E"))
        objs.append(_proxy_box(f"PxTowerF{i}", (tx0 + 0.12, tx1 - 0.12), (ty0 + 0.12, ty1 - 0.12), (z + 0.7, z + 1.5), fill[i]))
        objs.append(_proxy_box(f"PxTowerT{i}", (tx0, tx1), (ty0, ty1), (z + 1.5, z + h - 0.06), "#E6B866"))
    return objs


def _setup_strip_render(res):
    import bpy
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "MATERIAL"
    sc.display.shading.show_shadows = False
    sc.display.shading.show_cavity = False
    sc.render.resolution_x = res
    sc.render.resolution_y = int(res * 0.5625)
    sc.render.film_transparent = False
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.color = (0.16, 0.09, 0.2)
    cam_d = bpy.data.cameras.new("MapCam")
    cam = bpy.data.objects.new("MapCam", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def _aim_cam(cam, shot):
    pos, look = to_rig(*shot["pos"]), to_rig(*shot["look"])
    cam.location = pos
    cam.rotation_euler = (look - pos).to_track_quat("-Z", "Y").to_euler()
    cam.data.sensor_fit = "VERTICAL"
    cam.data.angle = math.radians(shot["fov"])
    cam.data.clip_start = 0.1
    cam.data.clip_end = 600


SLAM_CAM = dict(pos=(12.0, 9.0, -26.0), look=(-10.0, 4.0, -18.0), fov=70.0)    # a player in the dining room
SIDE_CAM = dict(pos=(30.0, 14.0, -30.0), look=(0.0, 8.0, -44.0), fov=55.0)    # review only (inside, from the right)


def map_strips(out_dir, res=320, which=None):
    """Render HandSlam, HandGrabLift and Burp with the proxy diner from the finale cameras (and a player
    view for the slam). The tower follows HandL from grab to chomp; the receipt swaps to a loose copy at
    the slam. Returns {name: png path}."""
    import bpy
    import numpy as np
    from PIL import Image, ImageDraw
    from mathutils import Matrix as _M
    os.makedirs(out_dir, exist_ok=True)
    ns.reset()
    out = build()
    C.finalize(out["skel"], out["actions"])
    sk, acts = out["skel"], out["actions"]
    by_name = {a.name: a for a in acts}
    arm = sk.arm
    arm.data.pose_position = "POSE"
    objs = map_proxies()
    tower = [o for o in objs if o.name.startswith("PxTower")]
    rest_mw = {o.name: o.matrix_world.copy() for o in tower}
    sc = bpy.context.scene
    cam = _setup_strip_render(res)
    rc = bpy.data.objects["HandR_Receipt"]
    loose = None
    shots = {
        "HandSlam": dict(cams=[("player", SLAM_CAM), ("side", SIDE_CAM)], frames=[0, 9, 13, 19, 26, 31, SLAM_F, 55, 63, 72, 79]),
        "HandGrabLift": dict(cams=[("shot1", SHOT1), ("shot2", SHOT2), ("side", SIDE_CAM)],
                             frames=[10, 16, 28, GRAB_F, 43, 49, 53, 56, 63, 68, 72, CHOMP_F, 80, 92, 112]),
        "Burp": dict(cams=[("shot2", SHOT2)], frames=[0, 12, 18, 22, 30, 48]),
    }
    pick = os.environ.get("NS_MAP_FRAMES")          # review aid: "HandSlam:17,22;HandGrabLift:52"
    if pick:
        want = {k: [int(v) for v in fs.split(",")] for k, fs in (t.split(":") for t in pick.split(";"))}
        shots = {k: dict(v, frames=want[k]) for k, v in shots.items() if k in want}
    if which:
        shots = {k: v for k, v in shots.items() if k in which}
    paths = {}
    for name, spec in shots.items():
        act = by_name[name]
        C.set_action(arm, act)
        sc.frame_set(GRAB_F)
        Rg, hg = _bone(arm, "HandL")
        Mg = np.eye(4)
        Mg[:3, :3], Mg[:3, 3] = Rg, hg
        Mg_inv = np.linalg.inv(Mg)
        rows = []
        for cname, shot in spec["cams"]:
            _aim_cam(cam, shot)
            ims = []
            for f in spec["frames"]:
                sc.frame_set(f)
                for o in tower:
                    o.hide_render = False
                    o.matrix_world = rest_mw[o.name]
                if name == "HandGrabLift":
                    rc.hide_render = True
                    if GRAB_F < f <= CHOMP_F:
                        R_, h_ = _bone(arm, "HandL")
                        M = np.eye(4)
                        M[:3, :3], M[:3, 3] = R_, h_
                        T = _M((M @ Mg_inv).tolist())
                        for o in tower:
                            o.matrix_world = T @ rest_mw[o.name]
                    elif f > CHOMP_F:
                        for o in tower:
                            o.hide_render = True
                elif name == "HandSlam":
                    rc.hide_render = f >= SLAM_F
                    if loose is not None:
                        loose.hide_render = f < SLAM_F
                else:
                    rc.hide_render = True
                    for o in tower:
                        o.hide_render = True
                bpy.context.view_layer.update()
                if name == "HandSlam" and f >= SLAM_F and loose is None:
                    cur = sc.frame_current
                    sc.frame_set(SLAM_F)
                    loose = rc.copy()
                    loose.data = rc.data.copy()
                    loose.name = "PxLooseReceipt"
                    for k in list(loose.keys()):
                        del loose[k]
                    loose.parent = None
                    loose.matrix_world = rc.matrix_world.copy()
                    sc.collection.objects.link(loose)
                    sc.frame_set(cur)
                    loose.hide_render = False
                    rc.hide_render = True
                    bpy.context.view_layer.update()
                p = os.path.join(out_dir, f"_{name}_{cname}_f{f}.png")
                sc.render.filepath = p
                bpy.ops.render.render(write_still=True)
                im = Image.open(p).convert("RGB")
                d = ImageDraw.Draw(im)
                d.rectangle((0, 0, res, 13), fill=(20, 20, 24))
                d.text((3, 1), f"{name} f{f} t={f / C.FPS:.2f}s {cname}", fill=(235, 235, 235))
                ims.append(im)
                os.remove(p)
            rows.append(ims)
        H = sc.render.resolution_y
        cols = len(rows[0])
        combo = Image.new("RGB", (res * cols, H * len(rows)))
        for r, ims in enumerate(rows):
            for i, im in enumerate(ims):
                combo.paste(im, (i * res, r * H))
        paths[name] = os.path.join(out_dir, f"_strip_{name}.png")
        combo.save(paths[name])
        print(f"[Creature_Patron] map strip: {paths[name]}")
    for o in objs + ([loose] if loose else []):
        bpy.data.objects.remove(o, do_unlink=True)
    return paths


if __name__ == "__main__":
    if os.environ.get("NS_MAP_STRIPS"):
        assert os.environ.get("NS_EXPORT") != "1", "map strips are a preview-only run"
        map_strips(os.environ["NS_MAP_STRIPS"], res=min(480, int(os.environ.get("NS_MAP_RES", "320"))),
                   which=(os.environ.get("NS_MAP_CLIPS") or None) and os.environ["NS_MAP_CLIPS"].split(","))
    else:
        if os.environ.get("NS_PREV_DIR"):
            os.environ["NS_PREVIEW"] = "0"          # nslib's standard preview path is fixed to previews/<batch>
        out = C.run(build, "Creature_Patron", "Patron", strips=STRIPS)
        if os.environ.get("NS_PREV_DIR") and os.environ.get("NS_STD_PREVIEW") == "1":
            out["arm"].data.pose_position = "REST"
            import bpy
            bpy.context.view_layer.update()
            print("[Creature_Patron] preview:", ns.render_preview("Creature_Patron", out_dir=C.PREV_DIR))
