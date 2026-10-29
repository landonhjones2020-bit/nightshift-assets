"""Creature_Patron — the Night 5 finale: a colossal face at the dining-room windows + two hands.

ONE rig. Model space: z = 0 is the dining-room floor; the pivot is ON THE GROUND 10.6 studs
behind the window wall (face front at about y = -10.4, i.e. pressed to the glass when the
window wall is at Blender y = -10.6 / Roblox z = -10.6). The eye line is at 6.25 (window
centre: sill 3.5, head 9); at rest the hands grip the window sills either side of the face
with their fingers hooked over into the room. Face 24 wide x 26 tall (crown above the 12-stud
roof); the mouth sits below the sill until the head rises to eat or burp.

Rigid-part rig (bones point +Y, roll 0; see _common). Front = Blender -Y, "L" = +X.
Bones: Root > Head > Jaw, EyeL/EyeR (look direction; eyeball + pupil), LidL/LidR (upper
lids, role "eyelid"), CheekL/CheekR (puff); Root > HandL/HandR (wrist; sleeve + palm) >
ThumbL > ThumbL2, IndexL > IndexL2, FingersL (middle+ring+pinky) > FingersL2 (and R).
Roles: "eyelid" (each upper lid; skin tone), "receipt" (THE BIG ONE, under HandR's palm:
show only during HandSlam).

Clips (30 fps): Blink (one-shot), Look (loop), Chew (loop), HandSlam, HandGrabLift, Burp
(one-shots, end on rest). No locomotion (clipSpeedRef is empty). Targets: HandSlam palm lands
at meta.slamPoint (counter top 3.0, 11.5 studs inside the window wall); HandGrabLift grabs
the tower at meta.grabPoint (tables 2.8), raises the head so the mouth reaches the windows,
eats, and puts everything back.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
rd = C.rot_deg

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

HEAD_C = Vector((0.0, 0.0, 4.75))
HEAD_R = Vector((12.0, 10.0, 13.0))
EYE = {"L": Vector((5.3, -7.1, 6.25)), "R": Vector((-5.3, -7.1, 6.25))}
EYE_R = 2.95
CHEEK = {"L": Vector((7.4, -8.0, 1.4)), "R": Vector((-7.4, -8.0, 1.4))}
MOUTH_Z = -2.6                                  # where the teeth meet
WRIST = {"L": Vector((16.5, -6.5, 4.6)), "R": Vector((-16.5, -6.5, 4.6))}
WINDOW_Y = -10.6
SLAM_PALM = Vector((-6.0, -22.0, 3.32))         # palm-centre landing point (counter top 3.0)
GRAB_PT = Vector((6.0, -20.0, 5.0))             # where the hand closes round the tower
PALM_OFF = Vector((0.0, -2.5, -0.95))           # palm centre (underside) from the wrist, canonical


def surf_y(x, z):
    """Front surface of the head ellipsoid (before deformation)."""
    k = 1 - (x / HEAD_R.x) ** 2 - ((z - HEAD_C.z) / HEAD_R.z) ** 2
    return HEAD_C.y - HEAD_R.y * math.sqrt(max(0.0, k))


# canonical hand: wrist at origin, fingers along -Y, palm down (-Z), thumb on the inner side
FINGER_SEGS = {"Index": (2.6, 2.2), "Middle": (2.7, 2.4), "Ring": (2.85, 2.2), "Pinky": (3.05, 1.7)}
KNUCKLE_X = {"Index": -1.6, "Middle": -0.52, "Ring": 0.55, "Pinky": 1.55}
KNUCKLE_Y = {"Index": -4.7, "Middle": -4.9, "Ring": -4.75, "Pinky": -4.55}   # middle joints line up at -7.6
REST_CURL = 55.0                                 # distal joints hooked over the sill at rest


def hand_joints(s):
    side = C.SIDE[s]
    W = WRIST[s]

    def P(x, y, z):
        return tuple(W + Vector((side * x, y, z)))
    js = [("Hand" + s, "Root", tuple(W))]
    js += [("Thumb" + s, "Hand" + s, P(-2.0, -1.4, -0.4)), ("Thumb" + s + "2", "Thumb" + s, P(-3.4, -3.3, -0.55))]
    js += [("Index" + s, "Hand" + s, P(KNUCKLE_X["Index"], KNUCKLE_Y["Index"], 0.0)),
           ("Index" + s + "2", "Index" + s, P(KNUCKLE_X["Index"], KNUCKLE_Y["Index"] - FINGER_SEGS["Index"][0], 0.0))]
    js += [("Fingers" + s, "Hand" + s, P(KNUCKLE_X["Ring"], KNUCKLE_Y["Middle"], 0.0)),
           ("Fingers" + s + "2", "Fingers" + s, P(KNUCKLE_X["Ring"], KNUCKLE_Y["Middle"] - FINGER_SEGS["Middle"][0], 0.0))]
    return js


JOINTS = ([("Root", None, (0.0, 0.0, 0.0)),
           ("Head", "Root", (0.0, 1.0, -6.0)),
           ("Jaw", "Head", (0.0, -0.5, 0.5)),
           ("EyeL", "Head", tuple(EYE["L"])), ("EyeR", "Head", tuple(EYE["R"])),
           ("LidL", "Head", tuple(EYE["L"])), ("LidR", "Head", tuple(EYE["R"])),
           ("CheekL", "Head", tuple(CHEEK["L"])), ("CheekR", "Head", tuple(CHEEK["R"]))]
          + hand_joints("L") + hand_joints("R"))


# ======================================================================================
# Model
# ======================================================================================

def build_head(sk):
    arm = sk.arm
    A = lambda objs, name, color, bone, mat="SmoothPlastic", **kw: C.attach(objs, name, color, arm, bone, mat, **kw)  # noqa: E731

    head = C.ell(tuple(HEAD_C), tuple(HEAD_R), segs=30, rings=19, name="HeadShape")

    def face(v):
        rel = v - HEAD_C
        # heavy jowls, narrower crown
        t = rel.z / HEAD_R.z
        w = 1.0 + 0.08 * max(0.0, -t) - 0.1 * max(0.0, t) ** 2
        v.x = HEAD_C.x + rel.x * w
        # flatten the face front a little and recess the lower face behind the jaw
        if rel.y < -6:
            v.y = HEAD_C.y + rel.y * 0.97
        if v.z < -1.2 and abs(v.x) < 8.4 and v.y < -5.0:
            k = min(1.0, (-1.2 - v.z) / 1.5) * max(0.0, 1.0 - (abs(v.x) / 8.4) ** 4)
            v.y += 1.6 * k
        return v
    C.deform(head, face)
    ears = [C.ell((sx * 11.7, 0.5, 4.5), (1.4, 2.2, 3.2), segs=12, rings=7) for sx in (-1, 1)]
    nose = C.ell((0, -10.6, 2.5), (2.0, 2.0, 2.4), segs=14, rings=9)
    lower_lids = []
    for s, E in EYE.items():
        t = ns.torus(EYE_R * 0.98, 0.42, major_segs=16, minor_segs=5)
        C.deform(t, lambda v: Vector((v.x, v.y * 0.6, v.z)))
        t.rotation_euler = (math.radians(90), 0, 0)
        t.location = E + Vector((0, -0.15, -0.35))
        ns.apply_all(t)
        # keep only the lower half of the ring
        bm_keep = [v.index for v in t.data.vertices if v.co.z > E.z - 0.4]
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(t.data)
        bm.verts.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[bm.verts[i] for i in bm_keep], context="VERTS")
        bm.to_mesh(t.data)
        bm.free()
        lower_lids.append(t)
    upper_lip = ns.torus(4.6, 0.55, major_segs=24, minor_segs=6)
    C.deform(upper_lip, lambda v: Vector((v.x * 1.45, v.y * 0.32, v.z * 0.85)))
    upper_lip.rotation_euler = (math.radians(90), 0, 0)
    upper_lip.location = (0, -8.55, MOUTH_Z + 0.25)
    ns.apply_all(upper_lip)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(upper_lip.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < MOUTH_Z + 0.9], context="VERTS")
    bm.to_mesh(upper_lip.data)
    bm.free()
    A([head, nose] + ears + lower_lids, "Head", SKIN, "Head", smooth_angle=70)
    A([upper_lip], "Head_Lip", LIP, "Head", smooth_angle=70)
    nost = [C.ell((sx * 0.85, -12.2, 1.2), (0.42, 0.3, 0.3), segs=8, rings=5) for sx in (-1, 1)]
    cavity = C.ell((0, -6.9, MOUTH_Z - 0.2), (7.2, 0.8, 2.2), segs=18, rings=8)
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
        o = ns.box((1.06, 0.5, 1.05), loc=(x, -8.15 + 0.035 * x * x, z0 + 0.52), bevel=0.16, segments=1)
        upper_teeth.append(o)
    A(upper_teeth, "Head_Teeth", TEETH, "Head", smooth_angle=50)

    # ---- jaw: chin + lower lip + lower teeth + tongue -------------------------------------
    chin = C.ell((0, -6.0, -5.6), (7.8, 3.3, 2.6), segs=20, rings=10)
    C.deform(chin, lambda v: Vector((v.x * (1.0 - 0.15 * max(0.0, (-5.4 - v.z) / 2.7)), v.y, v.z)))
    A([chin], "Jaw", SKIN, "Jaw", smooth_angle=70)
    lower_lip = ns.torus(4.3, 0.6, major_segs=24, minor_segs=6)
    C.deform(lower_lip, lambda v: Vector((v.x * 1.42, v.y * 0.32, v.z * 0.85)))
    lower_lip.rotation_euler = (math.radians(90), 0, 0)
    lower_lip.location = (0, -8.45, MOUTH_Z - 0.35)
    ns.apply_all(lower_lip)
    bm = bmesh.new()
    bm.from_mesh(lower_lip.data)
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
        # upper lid: spherical shell cap over the top of the eye (rotates forward/down to blink)
        lid = C.ell((0, 0, 0), (EYE_R + 0.22, EYE_R + 0.22, EYE_R + 0.22), segs=20, rings=12)
        bm = bmesh.new()
        bm.from_mesh(lid.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < (EYE_R + 0.22) * 0.66 - 0.01], context="VERTS")
        bm.to_mesh(lid.data)
        bm.free()
        lid.location = E
        sol = lid.modifiers.new("S", "SOLIDIFY")
        sol.thickness = 0.28
        A([lid], "Lid" + s, SKIN, "Lid" + s, recolor="eyelid", smooth_angle=70)
        ch = C.ell(tuple(CHEEK[s]), (2.5, 1.4, 2.1), segs=12, rings=7)
        A([ch], "Cheek" + s, BLUSH, "Cheek" + s, smooth_angle=70)


def build_hand(sk, s):
    arm = sk.arm
    side = C.SIDE[s]
    W = WRIST[s]
    A = lambda objs, name, color, bone, mat="SmoothPlastic", **kw: C.attach(objs, name, color, arm, bone, mat, **kw)  # noqa: E731

    def place(objs):
        for o in objs:
            ns.apply_all(o)
            for v in o.data.vertices:
                v.co = W + Vector((side * v.co.x, v.co.y, v.co.z))
            o.data.update()
            if side < 0:          # mirrored geometry: flip normals back outward
                bm = bmesh_new(o)
                for f in bm.faces:
                    f.normal_flip()
                bm.to_mesh(o.data)
                bm.free()
        return objs

    palm = C.loft([(-0.95, 2.2, 2.35, 0.1, -2.5, 3.2), (0.0, 2.3, 2.45, 0.0, -2.4, 3.2), (0.75, 2.0, 2.1, 0.0, -2.2, 3.0)],
                  verts=18, name="Palm")
    C.deform(palm, lambda v: Vector((v.x, v.y, v.z + 0.12 * (v.y + 2.4))))
    knuck = [C.ell((KNUCKLE_X[f] * 1.0, KNUCKLE_Y[f] + 0.25, 0.25), (0.72, 0.7, 0.62), segs=10, rings=6)
             for f in ("Index", "Middle", "Ring", "Pinky")]
    sleeve = C.capsule((0, 1.4, 0.4), (0, 9.0, 3.6), 2.35, 2.6, verts=14, cap_rings=2)
    cuff = C.rod((0, 0.35, 0.2), (0, 1.6, 0.5), 2.45, verts=14)
    A(place([palm] + knuck), "Hand" + s, SKIN, "Hand" + s, smooth_angle=60)
    A(place([sleeve]), "Hand" + s + "_Sleeve", SLEEVE, "Hand" + s, "Fabric", smooth_angle=60)
    A(place([cuff]), "Hand" + s + "_Cuff", CUFF, "Hand" + s, smooth_angle=50)
    if s == "R":
        rc = C.plate(3.2, 3.6, 0.08, 0.12, (0, -2.6, -1.0), plane="XY", bevel=0.0)
        A(place([rc]), "HandR_Receipt", C.PAPER_WHITE, "HandR", recolor="receipt", smooth_angle=None)

    # fingers: proximal along -Y, distal hooked down by REST_CURL (over the sill edge)
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
    # thumb: from the inner wrist side, forward and in
    tb, tm = Vector((-2.0, -1.4, -0.4)), Vector((-3.4, -3.3, -0.55))
    tt = Vector((-4.0, -5.2, -1.3))
    A(place([C.capsule(tb, tm, 0.75, 0.68, verts=8, cap_rings=2)]), "Thumb" + s, SKIN, "Thumb" + s, smooth_angle=60)
    A(place([C.capsule(tm, tt, 0.68, 0.58, verts=8, cap_rings=2)]), "Thumb" + s + "2", SKIN, "Thumb" + s + "2",
      smooth_angle=60)


def bmesh_new(o):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    return bm


def build_model(sk):
    build_head(sk)
    build_hand(sk, "L")
    build_hand(sk, "R")


# ======================================================================================
# Clips
# ======================================================================================

def fingers_pose(s, curl=0.0, spread=0.0, thumb=0.0, open_=0.0):
    """Finger groups: curl > 0 closes the hand; open_ > 0 straightens the hooked distals."""
    side = C.SIDE[s]
    return {"Index" + s: rd(curl * 0.9, 0, side * spread), "Index" + s + "2": rd(curl * 0.8 - open_, 0, 0),
            "Fingers" + s: rd(curl, 0, -side * spread * 0.5), "Fingers" + s + "2": rd(curl * 0.8 - open_, 0, 0),
            "Thumb" + s: rd(0, 0, -side * thumb), "Thumb" + s + "2": rd(thumb * 0.3, 0, -side * thumb * 0.6)}


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
    keys = [(0, p(0, 0)), (8, p(26, 4, 3)), (30, p(28, 6, 4)),          # darts to one side, lingers
            (36, p(-6, 26, 0, 3)), (64, p(-10, 28, -1, 4)),             # down at the players
            (70, p(-27, 8, -4)), (92, p(-26, 6, -4)),
            (98, p(0, 18, 0, 2)), (112, p(4, 16, 0, 2)), (120, p(0, 0))]
    return C.clip(sk, "Look", 120, True, keys)


def chew_clip(sk):
    def p(jaw, cl=0.0, cr=0.0, bob=0.0, roll=0.0):
        return {"Jaw": rd(jaw, 0, 0), "Head": (rd(-0.15 * jaw, roll, 0), (0, 0, bob)),
                "CheekL": (None, (0.35 * cl, -0.45 * cl, 0)), "CheekR": (None, (-0.35 * cr, -0.45 * cr, 0)),
                "LidL": rd(14, 0, 0), "LidR": rd(14, 0, 0)}
    keys = [(0, p(0, 0.3, 0.3)), (7, p(13, 1.0, 0.2, 0.25, 1.0)), (15, p(0, 0.5, 0.5, 0.0)),
            (22, p(11, 0.2, 1.0, 0.22, -1.0)), (30, p(0, 0.3, 0.3))]
    return C.clip(sk, "Chew", 30, True, keys)


def hand_target(s, wrist_pos, rot):
    """Hand bone (rot, loc) so the wrist sits at wrist_pos (world) with world rotation rot."""
    return (rot, tuple(Vector(wrist_pos) - WRIST[s]))


def slam_clip(sk):
    def fn(q):
        R = rd(q["hp"], 0, q["hy"])
        pose = {"HandR": hand_target("R", q["wrist"], R),
                "Head": (rd(q["head_p"], 0, -2 * q["lean"]), (0, -0.8 * q["lean"], 0)),
                "Jaw": rd(q["jaw"], 0, 0),
                "EyeL": rd(q["eye_p"], 0, -q["eye_y"]), "EyeR": rd(q["eye_p"], 0, -q["eye_y"])}
        pose.update(fingers_pose("R", curl=q["curl"], open_=q["open"], spread=q["spread"], thumb=q["thumb"]))
        return pose
    rest = tuple(WRIST["R"])
    slam_wrist = tuple(SLAM_PALM - rd(0, 0, 15) @ Vector((-PALM_OFF.x, PALM_OFF.y, PALM_OFF.z)))
    keys = [
        (0, dict(wrist=rest, hp=0, hy=0, curl=0, open=0, spread=0, thumb=0, head_p=0, lean=0, jaw=0, eye_p=0,
                 eye_y=0), "sine"),
        (14, dict(wrist=(-14.5, -4.0, 13.5), hp=-38, hy=10, open=REST_CURL, spread=6, head_p=4, lean=0.5, eye_p=-6,
                  eye_y=6), "sine"),
        (22, dict(wrist=(-12.0, -6.0, 16.0), hp=-48, hy=14, jaw=6, eye_p=8, eye_y=12), "in3"),       # wind-up
        (27, dict(wrist=slam_wrist, hp=0, hy=15, spread=10, thumb=6, head_p=8, lean=1.0, jaw=12, eye_p=24,
                  eye_y=16), "out"),                                                                   # SLAM
        (29, dict(hp=3), "sine"),
        (44, dict(hp=0, jaw=4), "sine"),
        (54, dict(wrist=(-12.0, -14.0, 9.0), hp=-20, hy=8, open=20, spread=4, head_p=2, lean=0.4, eye_p=10,
                  eye_y=6), "sine"),
        (70, dict(wrist=rest, hp=0, hy=0, curl=0, open=0, spread=0, thumb=0, head_p=0, lean=0, jaw=0, eye_p=0,
                  eye_y=0), "sine"),
    ]
    return C.param_clip(sk, "HandSlam", 70, False, keys, fn)


def grab_clip(sk):
    def fn(q):
        R = rd(q["hp"], q["hr"], q["hy"])
        pose = {"HandL": hand_target("L", q["wrist"], R),
                "Head": (rd(q["head_p"], 0, q["head_y"]), (0, -q["lean"], q["rise"])),
                "Jaw": rd(q["jaw"], 0, 0),
                "EyeL": rd(q["eye_p"], 0, q["eye_y"]), "EyeR": rd(q["eye_p"], 0, q["eye_y"]),
                "LidL": rd(q["lid"], 0, 0), "LidR": rd(q["lid"], 0, 0),
                "CheekL": (None, (0.3 * q["puff"], -0.5 * q["puff"], 0)),
                "CheekR": (None, (-0.3 * q["puff"], -0.5 * q["puff"], 0))}
        pose.update(fingers_pose("L", curl=q["curl"], open_=q["open"], spread=q["spread"], thumb=q["thumb"]))
        return pose
    rest = tuple(WRIST["L"])
    keys = [
        (0, dict(wrist=rest, hp=0, hr=0, hy=0, curl=0, open=0, spread=0, thumb=0, head_p=0, head_y=0, lean=0, rise=0,
                 jaw=0, eye_p=0, eye_y=0, lid=0, puff=0), "sine"),
        (16, dict(wrist=(9.5, -15.5, 9.5), hp=-10, hr=-35, hy=-20, open=REST_CURL, spread=8, thumb=-10, eye_p=18,
                  eye_y=-10, head_p=4), "sine"),                                                      # reaches in
        (26, dict(wrist=(9.6, -17.6, 6.6), hr=-62, hy=-25), "out"),                                    # around the tower
        (32, dict(curl=58, open=0, thumb=28, spread=0), "out"),                                        # GRAB
        (44, dict(wrist=(7.0, -15.0, 11.0), hp=-6, hr=-40, hy=-35, rise=6.5, lean=1.2, head_p=-6, jaw=16, eye_p=6,
                  eye_y=-16), "sine"),                                                                  # lifts; head rises
        (54, dict(wrist=(4.0, -14.2, 8.4), hr=-30, hy=-50, rise=8.5, jaw=30, lid=8, eye_y=-20), "sine"),  # to the mouth
        (58, dict(wrist=(3.2, -13.0, 7.8), jaw=0, puff=1.0, lid=28), "in"),                            # CHOMP
        (64, dict(wrist=(6.5, -16.0, 10.5), curl=8, open=10, thumb=0, jaw=0, puff=0.9), "out"),        # lets go
        (76, dict(jaw=10, puff=0.4, lid=18, eye_p=10, eye_y=0), "sine"),
        (84, dict(jaw=0, puff=0.6), "sine"),
        (100, dict(wrist=rest, hp=0, hr=0, hy=0, curl=0, open=0, spread=0, thumb=0, head_p=0, head_y=0, lean=0,
                   rise=0, jaw=0, eye_p=0, eye_y=0, lid=0, puff=0), "sine"),
    ]
    return C.param_clip(sk, "HandGrabLift", 100, False, keys, fn)


def burp_clip(sk):
    def p(rise=0.0, tilt=0.0, jaw=0.0, puff=0.0, lid=0.0, shake=0.0, curl=0.0):
        d = {"Head": (rd(-tilt, shake, 0), (0, 0, rise)), "Jaw": rd(jaw, 0, 0),
             "CheekL": (None, (0.4 * puff, -0.6 * puff, 0.1 * puff)), "CheekR": (None, (-0.4 * puff, -0.6 * puff, 0.1 * puff)),
             "LidL": rd(lid, 0, 0), "LidR": rd(lid, 0, 0)}
        d.update(fingers_pose("L", curl=curl))
        d.update(fingers_pose("R", curl=curl))
        return d
    keys = [(0, p()), (12, p(rise=2.5, tilt=-3, puff=0.8, lid=-6)), (18, p(rise=3.0, tilt=-2, puff=1.3, lid=-8)),
            (22, p(rise=5.0, tilt=10, jaw=28, puff=1.0, lid=40, curl=12), "BACK", "EASE_OUT")]
    for i, f in enumerate(range(24, 40, 2)):
        keys.append((f, p(rise=5.0, tilt=10, jaw=27 - i, puff=0.9, lid=42, shake=(1.6 if i % 2 else -1.6), curl=12),
                     "LINEAR"))
    keys += [(48, p(rise=2.0, tilt=2, jaw=0, puff=0.5, lid=30, curl=4)), (66, p())]
    return C.clip(sk, "Burp", 66, False, keys)


# ======================================================================================

def build():
    sk = C.Skel("PatronRig", JOINTS, bone_len=0.8)
    build_model(sk)
    acts = [blink_clip(sk), look_clip(sk), chew_clip(sk), slam_clip(sk), grab_clip(sk), burp_clip(sk)]
    C.rest_pose(sk.arm)

    def checks():
        import bpy
        arm = sk.arm
        arm.data.pose_position = "POSE"
        slam = acts[3]
        C.set_action(arm, slam)
        bpy.context.scene.frame_set(27)
        o = bpy.data.objects["HandR"]
        pts = [o.matrix_world @ v.co for v in o.data.vertices]
        print(f"  [slam] HandR lowest at impact {min(p.z for p in pts):.2f} (counter top 3.0), "
              f"palm centre ~ ({sum(p.x for p in pts) / len(pts):.1f}, {sum(p.y for p in pts) / len(pts):.1f})")
        grab = acts[4]
        C.set_action(arm, grab)
        for f in (32, 58):
            bpy.context.scene.frame_set(f)
            W = sk.fk({})  # noqa
            pts = [bpy.data.objects["HandL"].matrix_world @ v.co for v in bpy.data.objects["HandL"].data.vertices]
            jaw = bpy.data.objects["Jaw_Lip"]
            lip = [jaw.matrix_world @ v.co for v in jaw.data.vertices]
            print(f"  [grab f{f}] HandL centre ({sum(p.x for p in pts) / len(pts):.1f}, {sum(p.y for p in pts) / len(pts):.1f}, "
                  f"{sum(p.z for p in pts) / len(pts):.1f}); lower lip z {min(p.z for p in lip):.1f}..{max(p.z for p in lip):.1f}")
        bpy.context.scene.frame_set(0)

    meta = {
        "root": {"center": [0, 4.75, 0], "size": [24, 26, 20]},
        "clipSpeedRef": {},
        "placement": {"floor": 0.0, "eyeLine": 6.25, "windowWallZ": -10.6,
                      "note": "pivot on the ground outside, 10.6 studs behind the dining-room window wall "
                              "(Roblox +Z); eyes at the window centre, hands on the sills (3.5)"},
        "slamPoint": [6.0, 3.0, -22.0],
        "grabPoint": [-6.0, 2.8, -20.0],
        "props": {"receipt": "HandR_Receipt (THE BIG ONE): show during HandSlam until events.HandSlam.slam, then "
                             "hide and spawn the real receipt at slamPoint"},
        "events": {"Blink": {"closed": 0.13}, "HandSlam": {"slam": 0.9}, "HandGrabLift": {"grab": 1.07, "chomp": 1.93},
                   "Burp": {"burp": 0.73}},
    }
    return {"skel": sk, "arm": sk.arm, "actions": acts, "checks": [checks],
            "export": {"rig": sk.arm, "pivot": (0.0, 0.0, 0.0), "meta": meta}}


STRIPS = {
    "Blink": dict(frames=[0, 4, 7, 13], yaw=-20),
    "Look": dict(frames=[0, 30, 64, 92], yaw=-15),
    "Chew": dict(frames=[0, 7, 15, 22], yaw=-25),
    "HandSlam": dict(frames=[0, 22, 27, 54], yaw=-60, pitch=20),
    "HandGrabLift": dict(frames=[16, 32, 54, 58, 76], yaw=-55, pitch=15),
    "Burp": dict(frames=[0, 12, 22, 48], yaw=-25),
}

if __name__ == "__main__":
    C.run(build, "Creature_Patron", "Patron", strips=STRIPS)
