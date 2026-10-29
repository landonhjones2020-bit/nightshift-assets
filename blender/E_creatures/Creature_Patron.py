"""Creature_Patron — the Night 5 finale: a colossal face at the dining-room windows + two hands.

ONE rig. Model space: z = 0 is the dining-room floor; the pivot is ON THE GROUND outside the
dining room. In the shipped map the pivot stands 3.5 studs farther out than the rig was first
authored for: the window wall's centre plane is at Blender y = -14.1 (1 stud thick, outer
face -13.6, inner face -14.6; Roblox model z = -14.1), so the face front (y about -10.4) sits
about 3.2 studs behind the glass. The eye line is at 6.25 (window centre: sill 3.5, head 9);
at rest the hands sit on the wall either side of the face (x = +-16.5) with their fingers
hooked over the sills. Face 24 wide x 26 tall (crown above the 12-stud roof); the mouth sits
below the sill until the head rises to eat or burp.

Rigid-part rig (bones point +Y, roll 0; see _common). Front = Blender -Y, "L" = +X.
Bones: Root > Head > Jaw, EyeL/EyeR (look direction; eyeball + pupil), LidL/LidR (upper
lids, role "eyelid"), CheekL/CheekR (puff); Root > HandL/HandR (wrist; sleeve + palm) >
ThumbL > ThumbL2, IndexL > IndexL2, FingersL (middle+ring+pinky) > FingersL2 (and R).
Roles: "eyelid" (each upper lid; skin tone), "receipt" (THE BIG ONE, under HandR's palm:
show only during HandSlam).

Sleeves: long tapered capsules (24 studs; r 2.35 inside the cuff -> 2.05 -> 1.65 -> 1.3 -> 1.0)
pitched 8 deg up and turned 20 deg outward (pinky side) from the hand, so a hand deep in the
room still has its forearm running back out through the window it came in by. At rest they
run back outside, behind the wall. In both refit clips the forearm pivots in the window like a
lever (arm_fn's aim): its axis passes the window centre on every frame once the cuff is in.

Clips (30 fps): Blink (one-shot), Look (loop), Chew (loop), HandSlam, HandGrabLift, Burp
(one-shots, end on rest). No locomotion (clipSpeedRef is empty). The two hand clips are fitted
to the shipped map (MAP_* constants below, Blender rig space) and use the windows right beside
each hand's rest spot:
  * M5-M7 are out for a hand: Booth4-6 fill Y -14.1..-19.35 up to z 4.6 under them, leaving 4.4
    of window height, and the cuff is 4.9 across. M5/M6 also have the face right behind them,
    so a forearm through M5 runs into it. M4 is the front door. M3 and M8 are clear.
  HandSlam (80 f): HandR unhooks, goes in straight through M3, reaches and winds up over the
    counter, SLAMS THE BIG ONE onto the counter top (3.0) at x -4, y -30.1 (f28), settles,
    lifts and withdraws out through M3. The shipped palm's front underside sits 0.2 below the
    receipt, so the hand lands 3.4 deg nose-up: the receipt's back edge and the palm's front
    edge rest on 3.0. meta.slamPoint = the receipt's centre at f28.
  HandGrabLift (104 f): HandL goes in through M8, rolls thumb-up and closes round the tower on
    the Patron's Plate at meta.grabPoint (f32: palm on the +X face, fingers round -Y onto -X),
    lifts it off the plate, tips it toward the face and holds it up at the windows while the
    head rises, slides 8 studs toward it and opens wide; CHOMP (f60; the game removes the
    tower), the hand lets go empty and goes back out through M8 while the face chews. The
    booths, the 12-stud ceiling and the forearm through M8 keep the tower ~4 studs inside the
    wall, so the bite happens across the window (lips ~7.5 studs from the tower), not at it.
Run:  bpyenv/bin/python blender/E_creatures/Creature_Patron.py   (NS_EXPORT=1 export; NS_PREVIEW=0
NS_STRIPS=none skips the renders). The export prints the map-fit checks ([fit] lines).
Map review strips with proxy diner geometry (preview only, never exported):
      NS_MAP_STRIPS=<out dir> bpyenv/bin/python blender/E_creatures/Creature_Patron.py
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
PALM_OFF = Vector((0.0, -2.5, -0.95))           # palm centre (underside) from the wrist, canonical
RECEIPT_OFF = Vector((0.0, -2.6, -1.0))         # THE BIG ONE's centre from the wrist, canonical

# ---- the shipped dining room, in Blender rig space (Roblox world x = X, y = Z, z = -38.1 - Y) ----
MAP_WALL_Y = -14.1                              # window wall centre plane (1 stud thick)
MAP_WALL_OUT, MAP_WALL_IN = -13.6, -14.6
MAP_CEILING = 12.0
MAP_OPENINGS = {                                # glass openings: (x0, x1, z0, z1)
    "M3": (-23.2, -16.8, 3.5, 9.0), "M4": (-14.5, -9.5, 1.3, 7.5),      # M4 = front door (avoid)
    "M5": (-7.2, -0.8, 3.5, 9.0), "M6": (0.8, 7.2, 3.5, 9.0),
    "M7": (8.8, 15.2, 3.5, 9.0), "M8": (16.8, 23.2, 3.5, 9.0)}
MAP_BOOTHS = {"Booth4": (-8.0, 0.0), "Booth5": (0.0, 8.0), "Booth6": (8.0, 16.0)}   # x ranges
MAP_BOOTH_Y = (-19.35, -14.1)
MAP_BOOTH_TOP = 4.6
MAP_COUNTER = ((-8.0, 8.0), (-31.6, -28.6), 3.0)                       # x, y, top z
MAP_PLATE = ((11.4, 16.6), (-25.6, -22.6), 2.8)                         # three tables, top z
MAP_TOWER = ((12.0, 16.0), (-26.1, -22.1), (2.8, 10.3))                 # biggest tower the game stacks
SLAM_PALM = Vector((-4.0, -30.1, 3.095))         # palm-centre underside at the slam (receipt on 3.0)
GRAB_PT = Vector((14.0, -24.1, 6.5))            # where HandL's fingers close round the tower
SLAM_WINDOW, GRAB_WINDOW = "M3", "M8"

# ---- sleeves: tapered capsule behind the cuff (canonical hand coords, mirrored for R) ----
SLEEVE_A = Vector((0.0, 1.0, 0.36))             # start: a flat end inside the cuff
SLEEVE_PITCH, SLEEVE_YAW = 8.0, 20.0            # up / outward (toward the pinky side), degrees
SLEEVE_LEN = 24.0
SLEEVE_PROFILE = [(0.0, 2.35), (2.0, 2.05), (6.0, 1.65), (15.0, 1.3), (24.0, 1.0)]   # (s, radius)


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
    sleeve = sleeve_mesh()
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


def sleeve_mesh(verts=14, cap_rings=2):
    """Tapered sleeve along sleeve_dir() from SLEEVE_A (canonical L-hand coords): round caps,
    radius from SLEEVE_PROFILE."""
    r0, r1, L = SLEEVE_PROFILE[0][1], SLEEVE_PROFILE[-1][1], SLEEVE_LEN
    prof = []
    prof.append((0.0, 0.0))                                 # flat start, hidden inside the cuff
    prof.append((r0, 0.0))
    for s, r in SLEEVE_PROFILE[1:-1]:
        prof.append((r, s))
    for i in range(cap_rings + 1):                          # far cap
        a = (math.pi / 2) * i / cap_rings
        prof.append((r1 * math.cos(a), L + r1 * math.sin(a)))
    o = ns.lathe([(max(r, 0.0), z) for r, z in prof], verts=verts, name="Sleeve")
    ns.apply_all(o)
    o.rotation_euler = sleeve_dir().to_track_quat("Z", "Y").to_euler()
    o.location = SLEEVE_A
    ns.apply_all(o)
    return o


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


def fingers2(s, curl=0.0, open_=0.0, spread=0.0, thumb=0.0, tpitch=0.0, troll=0.0, tcurl=0.0, icurl=None):
    """Finger groups for the refit clips: fingers_pose plus thumb pitch (tpitch > 0 lifts the tip
    toward the back of the hand), thumb roll and a separate thumb tip curl. thumb < 0 tucks the
    thumb in along the fingers (the hand then fits a 6.4-wide window); icurl curls the index
    separately (default = curl)."""
    side = C.SIDE[s]
    ic = curl if icurl is None else icurl
    return {"Index" + s: rd(ic * 0.9, 0, side * spread), "Index" + s + "2": rd(ic * 0.8 - open_, 0, 0),
            "Fingers" + s: rd(curl, 0, -side * spread * 0.5), "Fingers" + s + "2": rd(curl * 0.8 - open_, 0, 0),
            "Thumb" + s: rd(-tpitch, side * troll, -side * thumb), "Thumb" + s + "2": rd(tcurl, 0, -side * thumb * 0.4)}


ARM_DEF = dict(hp=0.0, hr=0.0, hy=0.0, aim=0.0, ax=0.0, az=0.0, curl=0.0, icurl=0.0, open=0.0, spread=0.0,
               thumb=0.0, tpitch=0.0, troll=0.0, tcurl=0.0, head_p=0.0, head_y=0.0, head_r=0.0, hx=0.0, hyy=0.0,
               rise=0.0, jaw=0.0, eye_p=0.0, eye_y=0.0, lid=0.0, puff=0.0)


def window_centre(name):
    x0, x1, z0, z1 = MAP_OPENINGS[name]
    return Vector(((x0 + x1) / 2, MAP_WALL_Y, (z0 + z1) / 2))


def aim_rot(s, wrist, R_key, target):
    """Hand rotation whose sleeve axis runs from the cuff to `target` (a point in the window),
    keeping the hand's up vector as close as possible to R_key's: the forearm pivots in the
    window like a lever, every frame."""
    side = C.SIDE[s]
    d = sleeve_dir()
    d_c = Vector((side * d.x, d.y, d.z))
    a_c = Vector((side * SLEEVE_A.x, SLEEVE_A.y, SLEEVE_A.z))
    up = R_key @ Vector((0.0, 0.0, 1.0))
    R = R_key.copy()
    for _ in range(4):
        A = Vector(wrist) + R @ a_c
        R = C.aim(d_c, (Vector(target) - A).normalized(), Vector((0.0, 0.0, 1.0)), up)
    return R


def solve_grip(s, point_c, target, R_key, window, iters=10):
    """(wrist, R): canonical hand point on `target`, sleeve aimed through `window`'s centre."""
    R = R_key
    for _ in range(iters):
        w = wrist_for(s, point_c, target, R)
        R = aim_rot(s, w, R_key, window_centre(window))
    return Vector(wrist_for(s, point_c, target, R)), R


def hand_rot(p=0.0, r=0.0, y=0.0):
    """Hand rotation from yaw (about world Z), pitch (X: + tips the fingers down) and roll (about the
    hand's long axis, + tilts its back toward +X), applied roll first: R = Rz(y) Rx(p) Ry(r). Keys
    use this order so a rolled (thumb-up) hand interpolates without gimbal flips."""
    from mathutils import Euler
    return Euler((math.radians(p), math.radians(r), math.radians(y)), "YXZ").to_matrix()


def euler_deg(R):
    """(pitch, roll, yaw) of a hand rotation in hand_rot's order."""
    e = R.to_euler("YXZ")
    return math.degrees(e.x), math.degrees(e.y), math.degrees(e.z)


def arm_fn(s, window):
    """param_clip pose function shared by HandSlam (s = R) and HandGrabLift (s = L).
    Hand: wrist (world) + world Euler XYZ (hp, hr, hy, degrees); aim (0..1) blends in the lever
    constraint (sleeve through the window centre + (ax, 0, az)). Head: pitch/yaw/roll + offset
    (hx, hyy, rise); hyy < 0 leans the face toward the windows."""
    wc = window_centre(window)

    def fn(q):
        R = hand_rot(q["hp"], q["hr"], q["hy"])
        if q["aim"] > 1e-4:
            Ra = aim_rot(s, q["wrist"], R, wc + Vector((q["ax"], 0.0, q["az"])))
            inside = max(0.0, min(1.0, (MAP_WALL_IN - q["wrist"][1] - 0.7) / 1.5))   # 0 while the cuff passes
            w = min(1.0, q["aim"]) * inside
            R = R.to_quaternion().slerp(Ra.to_quaternion(), w).to_matrix()
        pose = {"Hand" + s: hand_target(s, q["wrist"], R),
                "Head": (rd(q["head_p"], q["head_r"], q["head_y"]), (q["hx"], q["hyy"], q["rise"])),
                "Jaw": rd(q["jaw"], 0, 0),
                "EyeL": rd(q["eye_p"], 0, q["eye_y"]), "EyeR": rd(q["eye_p"], 0, q["eye_y"]),
                "LidL": rd(q["lid"], 0, 0), "LidR": rd(q["lid"], 0, 0),
                "CheekL": (None, (0.3 * q["puff"], -0.5 * q["puff"], 0)),
                "CheekR": (None, (-0.3 * q["puff"], -0.5 * q["puff"], 0))}
        pose.update(fingers2(s, curl=q["curl"], icurl=q["icurl"], open_=q["open"], spread=q["spread"],
                             thumb=q["thumb"], tpitch=q["tpitch"], troll=q["troll"], tcurl=q["tcurl"]))
        return pose
    return fn


def wrist_for(s, point_canon, target, R):
    """Wrist position so that the canonical hand point lands on `target` with hand rotation R."""
    side = C.SIDE[s]
    p = Vector((side * point_canon[0], point_canon[1], point_canon[2]))
    return tuple(Vector(target) - R @ p)


def straight_rot(s, roll=0.0):
    """Hand rotation that runs the sleeve straight out along +Y, level (cuff passing a window)."""
    side = C.SIDE[s]
    d = sleeve_dir()
    d_c = Vector((side * d.x, d.y, d.z))
    up = hand_rot(0, roll, 0) @ Vector((0.0, 0.0, 1.0))
    return C.aim(d_c, Vector((0.0, 1.0, 0.0)), Vector((0.0, 0.0, 1.0)), up)


def straight_key(s, x, roll=0.0, y=-15.3, z=None):
    """Key params with the cuff and sleeve start centred in the window (sleeve level along +Y)."""
    R = straight_rot(s, roll)
    hp, hr, hy = euler_deg(R)
    a = R @ Vector((C.SIDE[s] * SLEEVE_A.x, SLEEVE_A.y, SLEEVE_A.z))
    zc = 6.25 if z is None else z
    return dict(wrist=(x - a.x, y, zc - a.z), hp=hp, hr=hr, hy=hy, aim=0.0)


def pass_key(s, window, y, pitch=-6.0):
    """Key params for the hand + cuff passing straight through the window: hand pointing straight
    into the room (no yaw), cuff centred in the opening, fingers open and thumb tucked."""
    R = hand_rot(pitch, 0.0, 0.0)
    c = window_centre(window)
    cuff = R @ Vector((0.0, 1.0, 0.36))
    return dict(wrist=(c.x - cuff.x, y, c.z - cuff.z), hp=pitch, hr=0.0, hy=0.0, aim=0.0, open=55.0, spread=2.0,
                thumb=-26.0, tpitch=12.0)


# ---- HandSlam: in through M3, slam THE BIG ONE flat on the counter, back out through M3 -------
SLAM_F = 28                                     # impact frame (events.HandSlam.slam)
SLAM_LEN = 80
SLAM_NOSE_UP = -3.4                             # the shipped palm's front underside sits 0.2 below the receipt
SLAM_LOW_PTS = [(x, y, -1.04) for x in (-1.6, 1.6) for y in (-0.8, -4.4)] + \
    [(x, -4.85, -1.244) for x in (-1.9, 0.1, 2.1)]   # receipt corners + palm front underside (canonical)


def slam_pose():
    """Impact pose: hand nose-up SLAM_NOSE_UP, palm centre over SLAM_PALM (x, y), lowest point
    (receipt back edge / palm front) on the counter top, yaw solved so the forearm runs out through
    the middle of M3."""
    side = C.SIDE["R"]
    target_x = window_centre(SLAM_WINDOW).x
    pc = Vector((0.0, PALM_OFF.y, -0.962))

    def place(psi):
        R = hand_rot(SLAM_NOSE_UP, 0, psi)
        low = min((R @ Vector((side * x, y, z))).z for x, y, z in SLAM_LOW_PTS)
        off = R @ Vector((side * pc.x, pc.y, pc.z))
        w = Vector((SLAM_PALM.x - off.x, SLAM_PALM.y - off.y, MAP_COUNTER[2] + 0.004 - low))
        d = sleeve_dir()
        a = w + R @ Vector((side * SLEEVE_A.x, SLEEVE_A.y, SLEEVE_A.z))
        dw = R @ Vector((side * d.x, d.y, d.z))
        x_cross = a.x + dw.x * (MAP_WALL_Y - a.y) / dw.y
        return w, R, x_cross
    lo, hi = 0.0, 70.0                                       # x_cross decreases as the yaw grows
    for _ in range(50):
        mid = (lo + hi) / 2
        if place(mid)[2] > target_x:
            lo = mid
        else:
            hi = mid
    w, R, _ = place((lo + hi) / 2)
    return w, R


def slam_keys():
    rest = tuple(WRIST["R"])
    w_s, R_s = slam_pose()
    hp_s, hr_s, hy_s = euler_deg(R_s)
    c3 = window_centre(SLAM_WINDOW)
    look = dict(eye_y=-6.0, eye_p=4.0, head_y=-2.0)
    return [
        (0, dict(ARM_DEF, wrist=rest), "sine"),
        (2, dict(wrist=(-16.6, -2.7, 6.0), hp=-4.0, eye_y=-4.0, eye_p=3.0), "sine"),             # unhooks
        (6, dict(pass_key("R", SLAM_WINDOW, -2.4), **look), "sine"),                             # lines up on M3
        (10, dict(pass_key("R", SLAM_WINDOW, -12.6)), "linear"),                                 # hand through M3
        (13, dict(pass_key("R", SLAM_WINDOW, -15.3)), "sine"),                                   # cuff through M3
        (17, dict(wrist=(c3.x + 0.3, -19.6, 6.5), aim=1.0, hp=-6.0, spread=4.0), "sine"),        # in, straight
        (23, dict(wrist=(-9.0, -24.6, 8.4), hp=-12.0, hy=30.0, spread=8.0, jaw=8.0, eye_p=16.0, eye_y=-16.0,
                  head_p=1.5, head_y=-5.0, hyy=0.3, rise=0.4), "in3"),                          # wind-up
        (SLAM_F, dict(wrist=tuple(w_s), hp=hp_s, hr=hr_s, hy=hy_s, aim=0.0, spread=10.0, jaw=14.0, eye_p=24.0,
                      eye_y=-18.0, head_p=3.0, head_y=-7.0, hyy=0.0, rise=-0.3, tpitch=28.0), "out"),  # SLAM
        (30, dict(wrist=tuple(w_s + Vector((0, 0, 0.12)))), "sine"),                              # settle
        (32, dict(wrist=tuple(w_s)), "sine"),
        (44, dict(jaw=4.0), "sine"),
        (51, dict(wrist=tuple(w_s + Vector((-1.8, 1.8, 2.4))), aim=1.0, hp=-10.0, open=30.0, spread=4.0, head_p=1.5,
                  hyy=0.0, rise=0.0, eye_p=10.0, eye_y=-8.0), "sine"),                           # lifts
        (61, dict(wrist=(c3.x + 0.3, -19.6, 6.5), hp=-6.0, hy=0.0, open=50.0, spread=3.0), "sine"),   # withdraws
        (64, dict(pass_key("R", SLAM_WINDOW, -15.3)), "sine"),                                   # cuff out of M3
        (67, dict(pass_key("R", SLAM_WINDOW, -12.6), head_p=0.0, head_y=0.0, hyy=0.0, jaw=0.0, eye_p=0.0,
                  eye_y=0.0), "linear"),
        (73, dict(pass_key("R", SLAM_WINDOW, -2.4)), "sine"),
        (77, dict(wrist=(-16.6, -2.7, 6.0), hp=-4.0, hy=0.0, open=0.0, spread=0.0, thumb=0.0, tpitch=0.0), "sine"),
        (SLAM_LEN, dict(ARM_DEF, wrist=rest), "sine"),
    ]


def slam_clip(sk):
    return C.param_clip(sk, "HandSlam", SLAM_LEN, False, slam_keys(), arm_fn("R", SLAM_WINDOW), step=1)


# ---- HandGrabLift: in through M8, close round the tower, present it to the mouth, CHOMP ---------
GRAB_F, CHOMP_F, GRAB_LEN = 32, 60, 104
GRAB_PALM = Vector((15.95, -24.6, 6.65))        # palm-centre contact on the tower's +X face
# carry keys (fitted numerically against the booths, plate, ceiling and M8; see fit_checks)
LIFT_OFF = (-1.665, -0.377, 0.852)              # f40: off the plate, toward the face
PRESENT_WRIST = (13.832, -21.558, 8.424)        # f52: tower tipped toward the face, held up at the windows
PRESENT_ROT = (-8.19, 64.25, -15.66)            # (pitch, roll, yaw) up reference; the lever aim does the rest
PRESENT_AZ = -0.4                               # forearm aimed 0.4 below M8's centre while presenting
OFFER_OFF = (0.0, 0.193, -0.029)                # f56
CHOMP_OFF = (0.0, 1.343, -0.52)                 # f60: shoved toward the window
FACE_SLIDE = 8.0                                # the face slides along the windows so its mouth is behind M7


def grab_pose():
    """Grip: thumb up (roll +90), palm on the tower's +X face, forearm through the middle of M8."""
    return solve_grip("L", PALM_OFF, GRAB_PALM, hand_rot(0, 90.0, 0), GRAB_WINDOW)


def grab_keys():
    rest = tuple(WRIST["L"])
    w_g, R_g = grab_pose()
    hp_g, hr_g, hy_g = euler_deg(R_g)
    c8 = window_centre(GRAB_WINDOW)
    tuck = dict(thumb=-20.0, tpitch=5.0)
    pw = Vector(PRESENT_WRIST)
    return [
        (0, dict(ARM_DEF, wrist=rest), "sine"),
        (2, dict(wrist=(16.6, -2.7, 6.0), hp=-4.0, eye_y=4.0, eye_p=4.0), "sine"),                # unhooks
        (5, dict(pass_key("L", GRAB_WINDOW, -2.4), eye_y=10.0, eye_p=10.0), "sine"),             # lines up on M8
        (9, dict(pass_key("L", GRAB_WINDOW, -12.6)), "linear"),                                  # hand through M8
        (12, dict(pass_key("L", GRAB_WINDOW, -15.3)), "sine"),                                   # cuff through M8
        (16, dict(wrist=(c8.x - 0.2, -19.0, 6.6), aim=1.0, hp=-4.0, hr=0.0, hy=0.0, spread=6.0, **tuck), "sine"),
        (21, dict(wrist=(c8.x - 0.8, -20.6, 7.0), hr=45.0, spread=8.0), "sine"),                # rolls thumb-up
        (26, dict(wrist=tuple(w_g + Vector((0.9, 1.4, 0.3))), hp=hp_g, hr=hr_g, hy=hy_g, spread=10.0,
                  eye_p=18.0, eye_y=12.0, head_p=4.0), "out"),
        (29, dict(wrist=tuple(w_g)), "sine"),                                                     # round the tower
        (GRAB_F, dict(curl=78.0, icurl=76.0, open=90.0, spread=0.0, tcurl=0.0), "out"),         # GRAB
        (40, dict(wrist=tuple(w_g + Vector(LIFT_OFF)), rise=3.0, hyy=-0.3, jaw=6.0, eye_p=10.0, eye_y=12.0,
                  hx=3.0, head_y=4.0), "sine"),                                                              # lifts it off the plate
        (52, dict(wrist=tuple(pw), hp=PRESENT_ROT[0], hr=PRESENT_ROT[1], hy=PRESENT_ROT[2], az=PRESENT_AZ,
                  rise=8.5, hyy=-0.7, head_y=8.0, head_p=2.0, hx=FACE_SLIDE, jaw=30.0, lid=8.0, eye_p=6.0,
                  eye_y=8.0),
         "sine"),                                                                                # presents it
        (56, dict(wrist=tuple(pw + Vector(OFFER_OFF)), jaw=34.0), "in"),                         # offers it up
        (CHOMP_F, dict(wrist=tuple(pw + Vector(CHOMP_OFF)), jaw=0.0, puff=1.0, lid=28.0), "out"),   # CHOMP
        (66, dict(curl=30.0, icurl=30.0, open=60.0, spread=4.0, tcurl=0.0, jaw=0.0, puff=0.9), "out"),  # lets go
        (71, dict(wrist=(c8.x - 0.8, -20.6, 7.0), az=0.0, hr=45.0, jaw=8.0), "sine"),
        (77, dict(wrist=(c8.x - 0.2, -19.0, 6.6), az=0.0, hp=-4.0, hr=0.0, hy=0.0, jaw=10.0, puff=0.4, lid=18.0,
                  eye_p=10.0, eye_y=0.0, curl=0.0, icurl=0.0, open=50.0, hx=3.0, rise=3.0, hyy=0.0, head_y=0.0,
                  head_p=0.0), "sine"),
        (81, dict(pass_key("L", GRAB_WINDOW, -15.3), jaw=0.0, puff=0.6, hx=0.0, rise=0.0), "sine"),   # cuff out of M8
        (84, dict(pass_key("L", GRAB_WINDOW, -12.6)), "linear"),
        (89, dict(pass_key("L", GRAB_WINDOW, -2.4), lid=0.0, puff=0.0, eye_p=0.0), "sine"),
        (98, dict(wrist=(16.6, -2.7, 6.0), hp=-4.0, hy=0.0, open=0.0, spread=0.0, thumb=0.0, tpitch=0.0), "sine"),
        (GRAB_LEN, dict(ARM_DEF, wrist=rest), "sine"),
    ]


def grab_clip(sk):
    return C.param_clip(sk, "HandGrabLift", GRAB_LEN, False, grab_keys(), arm_fn("L", GRAB_WINDOW), step=1)


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
# Map-fit checks (run by the export; every line starts with "[fit]")
# ======================================================================================

ARM_PARTS = {s: ["Hand" + s, "Hand" + s + "_Cuff", "Index" + s, "Index" + s + "2", "Index" + s + "2_Nails",
                 "Fingers" + s, "Fingers" + s + "2", "Fingers" + s + "2_Nails", "Thumb" + s, "Thumb" + s + "2"]
             + (["HandR_Receipt"] if s == "R" else []) for s in ("L", "R")}
FINGER_PARTS = {s: ["Index" + s, "Index" + s + "2", "Fingers" + s, "Fingers" + s + "2", "Thumb" + s, "Thumb" + s + "2"]
                for s in ("L", "R")}
FIT_SLEEVE_CLEAR = 0.3                          # sleeve vs window frame
FIT_HAND_CLEAR = 0.1                            # hand / cuff / tower vs window frame (no visible cut)


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


def _canon(s, p):
    np = _np()
    return np.array([C.SIDE[s] * p[0], p[1], p[2]], float)


def _opening_at(x, z):
    for k, (x0, x1, z0, z1) in MAP_OPENINGS.items():
        if x0 <= x <= x1 and z0 <= z <= z1:
            return k
    return None


def _slab_report(P):
    """Points inside the wall slab: (openings used, worst clearance to the frame edges)."""
    np = _np()
    m = (P[:, 1] <= MAP_WALL_OUT) & (P[:, 1] >= MAP_WALL_IN)
    if not m.any():
        return set(), None
    Q = P[m]
    best = np.full(len(Q), -1.0)
    which = np.array([None] * len(Q), dtype=object)
    for k, (x0, x1, z0, z1) in MAP_OPENINGS.items():
        c = np.minimum.reduce([Q[:, 0] - x0, x1 - Q[:, 0], Q[:, 2] - z0, z1 - Q[:, 2]])
        better = c > best
        best[better] = c[better]
        which[better & (c >= 0)] = k
    used = {w for w in which if w is not None}
    if (which == None).any():                                               # noqa: E711  in solid wall
        used.add("WALL")
    return used, float(best.min())


def _room_hits(P, tag, frame, out, floor=True):
    """Record points inside booths (below 4.6), the counter body (below 3.0), above the ceiling in
    the room, or under the floor."""
    np = _np()
    eps = 0.005
    inroom = P[:, 1] < MAP_WALL_IN
    for name, (x0, x1) in MAP_BOOTHS.items():
        m = (P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 1] > MAP_BOOTH_Y[0]) & (P[:, 1] < MAP_WALL_IN) \
            & (P[:, 2] < MAP_BOOTH_TOP - eps)
        if m.any():
            out.append((tag, frame, name, float(MAP_BOOTH_TOP - P[m, 2].min())))
    (cx0, cx1), (cy0, cy1), ctop = MAP_COUNTER
    m = (P[:, 0] > cx0) & (P[:, 0] < cx1) & (P[:, 1] > cy0) & (P[:, 1] < cy1) & (P[:, 2] < ctop - eps)
    if m.any():
        out.append((tag, frame, "counter", float(ctop - P[m, 2].min())))
    m = inroom & (P[:, 2] > MAP_CEILING + eps)
    if m.any():
        out.append((tag, frame, "ceiling", float(P[m, 2].max() - MAP_CEILING)))
    if floor and (P[:, 2] < -eps).any():
        out.append((tag, frame, "floor", float(-P[:, 2].min())))


def _ellipsoid_depth(P, c, r):
    """Largest penetration (studs, approx.) of points into an axis-aligned ellipsoid."""
    np = _np()
    d = np.sqrt((((P - c) / r) ** 2).sum(axis=1))
    k = d < 1.0
    if not k.any():
        return 0.0
    return float(((1.0 - d[k]) * min(r)).max())


def _head_depth(arm, P):
    """How deep points go into the face (head ellipsoid with nose, ears, eyes and chin)."""
    np = _np()
    Rh, hh = _bone(arm, "Head")
    local = (P - hh) @ Rh + np.array([0.0, 1.0, -6.0])          # back into the head's rest frame
    worst = _ellipsoid_depth(local, np.array(tuple(HEAD_C)), np.array((12.3, 9.8, 13.0)))
    worst = max(worst, _ellipsoid_depth(local, np.array((0.0, -10.6, 2.5)), np.array((2.0, 2.0, 2.4))))
    for sx in (-1, 1):
        worst = max(worst, _ellipsoid_depth(local, np.array((sx * 11.7, 0.5, 4.5)), np.array((1.4, 2.2, 3.2))))
    for e in ("EyeL", "EyeR"):
        Re, he = _bone(arm, e)
        worst = max(worst, _ellipsoid_depth((P - he) @ Re, np.zeros(3), np.full(3, EYE_R)))
    Rj, hj = _bone(arm, "Jaw")
    lj = (P - hj) @ Rj + np.array([0.0, -0.5, 0.5])
    worst = max(worst, _ellipsoid_depth(lj, np.array((0.0, -6.0, -5.6)), np.array((7.8, 3.3, 2.6))))
    return worst


def _sleeve_axis(arm, s):
    np = _np()
    R, h = _bone(arm, "Hand" + s)
    a = h + R @ _canon(s, SLEEVE_A)
    d = R @ _canon(s, sleeve_dir())
    return a, d


def _sleeve_section(a, d, y, s_at):
    """X/Z extents where the tapered sleeve crosses the plane Y = y (ellipse of the radius at s_at)."""
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
    """Where the sleeve axis crosses Y = -14.1: (x, z, opening, radius, clearance over the wall's
    thickness) or None when the sleeve does not reach the wall."""
    a, d = _sleeve_axis(arm, s)
    if d[1] <= 1e-6:
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
    on = (np.isclose(g[:, 0], x0) | np.isclose(g[:, 0], x1) | np.isclose(g[:, 1], y0) | np.isclose(g[:, 1], y1)
          | np.isclose(g[:, 2], z0) | np.isclose(g[:, 2], z1))
    return g[on]


def fit_checks(sk, acts):
    """Prints the map-fit report for HandSlam and HandGrabLift; returns the list of failures."""
    import bpy
    np = _np()
    arm = sk.arm
    arm.data.pose_position = "POSE"
    sc = bpy.context.scene
    objs = {o.name: o for o in ns._tagged_objects()}
    samp = {n: _samples(o) for n, o in objs.items() if n.startswith(("Hand", "Index", "Fingers", "Thumb"))}
    samp_head = {n: _samples(o, 1.0) for n, o in objs.items() if n.startswith(("Head", "Jaw", "Eye", "Lid", "Cheek"))}
    fails = []

    def pts(names):
        return np.concatenate([_world(objs[n], samp[n]) for n in names])

    hook = {s: ["Index" + s, "Index" + s + "2", "Index" + s + "2_Nails", "Fingers" + s, "Fingers" + s + "2",
                "Fingers" + s + "2_Nails"] for s in ("L", "R")}

    def run_clip(act, s, window, extra=None):
        """Per frame: sleeve-axis crossing, arm mesh inside the wall slab, booth/counter/ceiling/floor
        hits, depth into the face. Contacts that come only from the fingers hooked over the sill in
        the shipped rest pose (first/last frames, wrist still outside) are listed as rest-pose items."""
        C.set_action(arm, act)
        n0, n1 = act["ns_start"], act["ns_end"]
        hits, worst_sleeve, worst_hand, worst_head = [], (9.0, None), (9.0, None), (0.0, None)
        rest_items = []
        face_front = (9.0, None)
        print(f"  [fit] {act.name}: per-frame sleeve crossing of the wall plane y={MAP_WALL_Y} "
              f"(x, z, opening, radius, clearance)")
        for f in range(n0, n1 + 1):
            sc.frame_set(f)
            parts = {n: _world(objs[n], samp[n]) for n in ARM_PARTS[s]}
            hand = np.concatenate(list(parts.values()))
            slv = pts(["Hand" + s + "_Sleeve"])
            _, wr = _bone(arm, "Hand" + s)
            near_rest = (f - n0 <= 3 or n1 - f <= 3) and wr[1] > MAP_WALL_OUT
            inside = bool((hand[:, 1] < MAP_WALL_OUT).any())
            cr = _sleeve_crossing(arm, s)
            line = f"  [fit]   f{f:3d} hand {'in ' if inside else 'out'} "
            if cr:
                x, z, op, rr, cl = cr
                line += f"axis ({x:6.2f}, {z:5.2f}) {op or 'WALL'} r {rr:.2f} clear {cl:.2f}"
                if op != window or cl < FIT_SLEEVE_CLEAR:
                    fails.append(f"{act.name} f{f}: sleeve crosses {op or 'solid wall'} clear {cl:.2f}")
                if cl < worst_sleeve[0]:
                    worst_sleeve = (cl, f)
            elif inside:
                line += "axis does not reach the wall (hand/cuff in the opening)"
            else:
                line += "outside"
            fh = []
            for n, P_ in list(parts.items()) + [("Hand" + s + "_Sleeve", slv)]:
                used, cl_mesh = _slab_report(P_)
                if cl_mesh is not None and (used - {window} or cl_mesh < FIT_HAND_CLEAR):
                    fh.append((n, sorted(used), cl_mesh))
                _room_hits(P_, n, f, fh)
            used, cl_mesh = _slab_report(np.concatenate([hand, slv]))
            if cl_mesh is not None:
                line += f" | mesh in wall: {','.join(sorted(used))} clear {cl_mesh:.2f}"
            if fh and near_rest and all(h[0] in hook[s] for h in fh):
                line += "  (rest-pose finger hook)"
                rest_items.append((f, min((h[2] if len(h) == 3 else -h[3]) for h in fh)))
            else:
                for h in fh:
                    if len(h) == 3:
                        fails.append(f"{act.name} f{f}: {h[0]} in the wall at {h[1]} clear {h[2]:.2f}")
                    else:
                        hits.append(h)
                if cl_mesh is not None and cl_mesh < worst_hand[0]:
                    worst_hand = (cl_mesh, f)
            print(line)
            hp_ = np.concatenate([_world(objs[n], samp_head[n]) for n in samp_head])
            gap = float(hp_[:, 1].min() - MAP_WALL_OUT)
            if gap < face_front[0]:
                face_front = (gap, f)
            hd = _head_depth(arm, np.concatenate([hand, slv]))
            if hd > worst_head[0]:
                worst_head = (hd, f)
            if extra:
                extra(f, hand, hits)
        for tag, f, what, depth in hits:
            fails.append(f"{act.name} f{f}: {tag} in {what} by {depth:.2f}")
        print(f"  [fit] {act.name}: worst sleeve clearance {worst_sleeve[0]:.2f} (f{worst_sleeve[1]}), worst arm-mesh "
              f"clearance in the wall {worst_hand[0]:.2f} (f{worst_hand[1]}), booth/counter/ceiling/floor hits "
              f"{len(hits)}, arm into the face {worst_head[0]:.2f} (f{worst_head[1]})")
        if rest_items:
            print(f"  [fit] {act.name}: shipped rest pose - fingers hooked into the sill/mullion/booth at frames "
                  f"{[f for f, _ in rest_items]} (deepest {-min(c for _, c in rest_items):.2f}); unchanged rest pose, "
                  f"clears by f{max(f for f, _ in rest_items if f < (n0 + n1) / 2) + 1 if any(f < (n0 + n1) / 2 for f, _ in rest_items) else n0}")
        print(f"  [fit] {act.name}: face front vs the wall's outer face: closest {face_front[0]:.2f} (f{face_front[1]})"
              f"{' - face pushes into the wall' if face_front[0] < 0 else ''}")
        if face_front[0] < 0:
            fails.append(f"{act.name}: face pushes {-face_front[0]:.2f} into the wall at f{face_front[1]}")
        if worst_head[0] > 0.05:
            fails.append(f"{act.name}: arm goes {worst_head[0]:.2f} into the face at f{worst_head[1]}")
        sc.frame_set(0)

    # ---------------- HandSlam ----------------
    slam = acts[3]
    C.set_action(arm, slam)
    sc.frame_set(SLAM_F)
    R, h = _bone(arm, "HandR")
    palm = h + R @ _canon("R", PALM_OFF)
    hand = pts([n for n in ARM_PARTS["R"] if n != "HandR_Cuff"])
    rc = objs["HandR_Receipt"]
    rp = _world(rc, samp["HandR_Receipt"])
    rcen = (rp.min(axis=0) + rp.max(axis=0)) / 2
    nrm = R @ np.array((0.0, 0.0, 1.0))
    tilt = math.degrees(math.acos(min(1.0, abs(nrm[2]))))
    fwd = R @ np.array((0.0, -1.0, 0.0))
    ryaw = math.degrees(math.atan2(fwd[0], -fwd[1]))
    print(f"  [fit] HandSlam f{SLAM_F} (t={SLAM_F / C.FPS:.3f}s): palm centre ({palm[0]:.2f}, {palm[1]:.2f}, "
          f"{palm[2]:.2f}) vs target ({SLAM_PALM.x}, {SLAM_PALM.y}, 3.0-3.1); hand lowest z {hand[:, 2].min():.3f}")
    print(f"  [fit] HandSlam receipt centre ({rcen[0]:.2f}, {rcen[1]:.2f}, {rcen[2]:.3f}), underside z "
          f"{rp[:, 2].min():.3f} vs counter top {MAP_COUNTER[2]}, tilt {tilt:.2f} deg, yaw {ryaw:.1f} deg")
    low = float(min(hand[:, 2].min(), rp[:, 2].min()))
    print(f"  [fit] HandSlam palm underside: lowest point {low:.3f} (target 3.0-3.1; the shipped palm's front "
          f"underside sits 0.2 below the receipt, so the hand lands {-SLAM_NOSE_UP:.1f} deg nose-up and the palm "
          f"centre's underside is at {palm[2]:.2f})")
    if abs(palm[0] - SLAM_PALM.x) > 0.3 or abs(palm[1] - SLAM_PALM.y) > 0.3 or not (3.0 <= low <= 3.1):
        fails.append("HandSlam: palm misses the target")
    if tilt >= 5.0 or abs(rp[:, 2].min() - MAP_COUNTER[2]) > 0.02:
        fails.append(f"HandSlam: receipt tilt {tilt:.2f} / underside {rp[:, 2].min():.3f}")
    run_clip(slam, "R", SLAM_WINDOW)

    # ---------------- HandGrabLift ----------------
    grab = acts[4]
    C.set_action(arm, grab)
    sc.frame_set(GRAB_F)
    Rg, hg = _bone(arm, "HandL")
    Mg = np.eye(4)
    Mg[:3, :3], Mg[:3, 3] = Rg, hg
    Mg_inv = np.linalg.inv(Mg)
    tower0 = _tower_local_pts()
    (tx0, tx1), (ty0, ty1), (tz0, tz1) = MAP_TOWER
    tc = np.array(((tx0 + tx1) / 2, (ty0 + ty1) / 2))
    # closure: the hand's inner contour round the tower axis (z band of the grip), one nearest point
    # per 10-deg bin; the closure centre is the centre of the 4x4 square that best fits that contour
    gp = pts(FINGER_PARTS["L"] + ["HandL"])
    band = gp[np.abs(gp[:, 2] - GRAB_PT.z) < 2.6]
    half = 2.0

    def contour(c):
        rel = band[:, :2] - c
        ang = np.degrees(np.arctan2(rel[:, 1], rel[:, 0]))
        dist = np.max(np.abs(rel), axis=1)
        near = dist < half + 1.6
        bins = {}
        for a_, d_, p_ in zip(ang[near], dist[near], band[near][:, :2]):
            k = int((a_ + 180) // 10)
            if k not in bins or d_ < bins[k][0]:
                bins[k] = (d_, p_)
        return bins
    ctr = tc.copy()
    for _ in range(3):                                  # fit: inner contour on the square's sides
        inner = np.array([v[1] for v in contour(ctr).values()])
        best_c, best_e = ctr, 1e9
        for dx in np.linspace(-1.0, 1.0, 41):
            for dy in np.linspace(-1.0, 1.0, 41):
                c = ctr + (dx, dy)
                e = float(((np.max(np.abs(inner - c), axis=1) - half) ** 2).sum())
                if e < best_e:
                    best_c, best_e = c, e
        ctr = best_c
    bins = contour(ctr)
    cover = len(bins) * 10
    cheb = np.max(np.abs(band[:, :2] - tc), axis=1)
    sink = float(max(0.0, half - cheb.min())) if len(cheb) else 0.0
    zc = float(np.mean(band[:, 2])) if len(band) else float("nan")
    print(f"  [fit] HandGrabLift grab f{GRAB_F} (t={GRAB_F / C.FPS:.3f}s): finger/palm closure centre "
          f"({ctr[0]:.2f}, {ctr[1]:.2f}, z~{zc:.2f}) vs tower grab point ({GRAB_PT.x}, {GRAB_PT.y}, {GRAB_PT.z}) "
          f"-> off by {np.linalg.norm(ctr - tc):.2f} in plan; the hand wraps {cover} deg round the 4x4 block "
          f"(palm on +X, fingers round -Y onto -X, thumb on +X); deepest sink into the block {sink:.2f} "
          f"(block centre untouched while < {half})")
    if not (np.linalg.norm(ctr - tc) < 0.6 and abs(zc - GRAB_PT.z) < 0.6 and cover >= 180 and sink < 1.0):
        fails.append("HandGrabLift: grab does not surround the tower")

    def tower_world(f):
        R_, h_ = _bone(arm, "HandL")
        M = np.eye(4)
        M[:3, :3], M[:3, 3] = R_, h_
        T = M @ Mg_inv
        return tower0 @ T[:3, :3].T + T[:3, 3]

    tower_hits = []
    tower_wall = [9.0, None]

    def tower_extra(f, hand, hits):
        if not (GRAB_F < f <= CHOMP_F):
            return
        T = tower_world(f)
        _room_hits(T, "tower", f, tower_hits)
        (px0, px1), (py0, py1), ptop = MAP_PLATE
        m = (T[:, 0] > px0) & (T[:, 0] < px1) & (T[:, 1] > py0) & (T[:, 1] < py1) & (T[:, 2] < ptop - 0.005)
        if m.any():
            tower_hits.append(("tower", f, "plate", float(ptop - T[m, 2].min())))
        used, cl = _slab_report(T)
        if cl is not None and cl < tower_wall[0]:
            tower_wall[0], tower_wall[1] = cl, f
            if used - {GRAB_WINDOW, "M6"} or cl < FIT_HAND_CLEAR:
                tower_hits.append(("tower", f, "wall " + ",".join(sorted(used)), -cl))

    run_clip(grab, "L", GRAB_WINDOW, tower_extra)
    for tag, f, what, depth in tower_hits:
        fails.append(f"HandGrabLift f{f}: tower in {what} by {depth:.2f}")
    print(f"  [fit] HandGrabLift tower (attached f{GRAB_F}..f{CHOMP_F}): {len(tower_hits)} hits on booths/"
          f"counter/plate/ceiling/wall" + (f"; closest to the wall frame {tower_wall[0]:.2f} at f{tower_wall[1]}"
                                           if tower_wall[1] is not None else "; never enters the wall"))
    C.set_action(arm, grab)
    sc.frame_set(CHOMP_F)
    T = tower_world(CHOMP_F)
    lips = np.concatenate([_world(objs[n], _samples(objs[n], 1.0)) for n in ("Head_Lip", "Jaw_Lip")])
    lc = (lips.min(axis=0) + lips.max(axis=0)) / 2
    from_t = T[np.argmin(np.linalg.norm(T - lc, axis=1))]
    dmin = float(np.min(np.linalg.norm(T[:, None, :] - lips[None, ::4, :], axis=2)))
    R_, h_ = _bone(arm, "HandL")
    pc = h_ + R_ @ _canon("L", PALM_OFF)
    print(f"  [fit] HandGrabLift CHOMP f{CHOMP_F} (t={CHOMP_F / C.FPS:.3f}s): lips centre ({lc[0]:.2f}, {lc[1]:.2f}, "
          f"{lc[2]:.2f}); tower point nearest the lips ({from_t[0]:.2f}, {from_t[1]:.2f}, {from_t[2]:.2f}) -> "
          f"gap {dmin:.2f}; tower bbox x {T[:, 0].min():.1f}..{T[:, 0].max():.1f} y {T[:, 1].min():.1f}.."
          f"{T[:, 1].max():.1f} z {T[:, 2].min():.1f}..{T[:, 2].max():.1f}; palm centre ({pc[0]:.2f}, {pc[1]:.2f}, "
          f"{pc[2]:.2f})")
    print(f"  [fit] HandGrabLift CHOMP: NOT MET - 'tower right at the mouth' is out of reach in this map: the booths "
          f"(top {MAP_BOOTH_TOP}) under M5-M7, the {MAP_CEILING}-stud ceiling and the forearm through {GRAB_WINDOW} keep the "
          f"tower about 4 studs inside the wall, and the lips cannot come closer than ~3.6 studs outside it")
    sc.frame_set(0)
    print(f"  [fit] RESULT: {'PASS' if not fails else 'FAIL'} ({len(fails)} issue(s)) for the geometry checks above "
          f"(rest-pose finger hook listed separately)")
    for m in fails:
        print("  [fit]   - " + m)
    return fails


# ======================================================================================

def build():
    sk = C.Skel("PatronRig", JOINTS, bone_len=0.8)
    build_model(sk)
    acts = [blink_clip(sk), look_clip(sk), chew_clip(sk), slam_clip(sk), grab_clip(sk), burp_clip(sk)]
    C.rest_pose(sk.arm)

    def checks():
        fit_checks(sk, acts)

    # slamPoint: THE BIG ONE's centre at the slam frame; grabPoint: the tower grab point. Both in
    # Roblox model-local coords (-X, Z, Y of the Blender point).
    slam_wrist, R_slam = slam_pose()
    rc = slam_wrist + R_slam @ Vector((-RECEIPT_OFF.x, RECEIPT_OFF.y, RECEIPT_OFF.z))
    meta = {
        "root": {"center": [0, 4.75, 0], "size": [24, 26, 20]},
        "clipSpeedRef": {},
        "placement": {"floor": 0.0, "eyeLine": 6.25, "windowWallZ": MAP_WALL_Y,
                      "note": "pivot on the ground outside, 14.1 studs behind the dining-room window wall's centre "
                              "plane (Roblox +Z; 3.5 farther out than first authored); eyes at the window centre, "
                              "hands on the wall between the windows"},
        "slamPoint": [round(-rc.x, 3), round(rc.z, 3), round(rc.y, 3)],
        "grabPoint": [round(-GRAB_PT.x, 3), round(GRAB_PT.z, 3), round(GRAB_PT.y, 3)],
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
    "HandSlam": dict(frames=[0, 17, 23, SLAM_F, 51, 64], yaw=-60, pitch=20),
    "HandGrabLift": dict(frames=[16, GRAB_F, 52, CHOMP_F, 77], yaw=-55, pitch=15),
    "Burp": dict(frames=[0, 12, 22, 48], yaw=-25),
}


# ======================================================================================
# Map review strips (preview only): proxy diner geometry, never tagged, never exported
# ======================================================================================

def _proxy_box(name, x, y, z, color):
    o = ns.box((x[1] - x[0], y[1] - y[0], z[1] - z[0]), loc=((x[0] + x[1]) / 2, (y[0] + y[1]) / 2, (z[0] + z[1]) / 2),
               bevel=0.0, name=name)
    ns.apply_all(o)
    o.name = name
    o.data.materials.append(ns.material(color))
    return o


def map_proxies():
    """Wall with its openings, booths, counter, plate tables and a 4x4x7.5 tower block. Names start
    with 'Px' and none carry ns_part, so nothing here can reach an export."""
    WALL, GLASS, BOOTH, COUNTER_C, TABLE, TOWER_C = "#8A8F99", "#3B5A70", "#7A3B48", "#B9C0C6", "#C8A777", "#E8C15A"
    objs = []
    xs = sorted({v for k, (x0, x1, _, _) in MAP_OPENINGS.items() for v in (x0, x1)})
    y = (MAP_WALL_IN, MAP_WALL_OUT)
    xmin, xmax = -32.0, 32.0
    objs.append(_proxy_box("PxWallTop", (xmin, xmax), y, (9.0, MAP_CEILING), WALL))
    objs.append(_proxy_box("PxWallLow", (xmin, -14.5), y, (0.0, 3.5), WALL))
    objs.append(_proxy_box("PxWallLowB", (-9.5, xmax), y, (0.0, 3.5), WALL))
    objs.append(_proxy_box("PxDoorLow", (-14.5, -9.5), y, (0.0, 1.3), WALL))
    objs.append(_proxy_box("PxDoorTop", (-14.5, -9.5), y, (7.5, 9.0), WALL))
    edges = [xmin] + xs + [xmax]
    for a, b in zip(edges[:-1], edges[1:]):
        if not any(abs(a - x0) < 1e-6 and abs(b - x1) < 1e-6 for x0, x1, _, _ in MAP_OPENINGS.values()):
            objs.append(_proxy_box(f"PxMullion{a:+.1f}", (a, b), y, (3.5, 9.0), WALL))
    for k, (x0, x1) in MAP_BOOTHS.items():
        objs.append(_proxy_box("Px" + k + "Seat", (x0 + 0.15, x1 - 0.15), (-19.35, MAP_WALL_IN), (0.0, 1.6), BOOTH))
        objs.append(_proxy_box("Px" + k + "Back", (x0 + 0.15, x1 - 0.15), (-17.2, -16.4), (1.6, MAP_BOOTH_TOP), BOOTH))
        objs.append(_proxy_box("Px" + k + "BackW", (x0 + 0.15, x1 - 0.15), (-15.4, MAP_WALL_IN), (1.6, MAP_BOOTH_TOP),
                               BOOTH))
    (cx0, cx1), (cy0, cy1), ctop = MAP_COUNTER
    objs.append(_proxy_box("PxCounter", (cx0, cx1), (cy0, cy1), (0.0, ctop), COUNTER_C))
    (px0, px1), (py0, py1), ptop = MAP_PLATE
    objs.append(_proxy_box("PxPlate", (px0, px1), (py0, py1), (ptop - 0.25, ptop), TABLE))
    objs.append(_proxy_box("PxPlateBase", (px0 + 1.0, px1 - 1.0), (py0 + 0.8, py1 - 0.8), (0.0, ptop - 0.25), TABLE))
    (tx0, tx1), (ty0, ty1), (tz0, tz1) = MAP_TOWER
    objs.append(_proxy_box("PxTower", (tx0, tx1), (ty0, ty1), (tz0, tz1), TOWER_C))
    objs.append(_proxy_box("PxFloorRoom", (xmin, xmax), (-40.0, MAP_WALL_IN), (-0.1, 0.0), "#4A4038"))
    objs.append(_proxy_box("PxCeiling", (xmin, xmax), (-40.0, MAP_WALL_IN), (MAP_CEILING, MAP_CEILING + 0.3), "#3A3E46"))
    objs.append(_proxy_box("PxGround", (xmin, xmax), (MAP_WALL_OUT, 30.0), (-0.1, 0.0), "#2E3236"))
    return objs


def map_strips(out_dir, res=320):
    """Render HandSlam and HandGrabLift with the proxy diner from inside the room and from the side.
    The tower follows HandL from grab to chomp, the receipt swaps to a loose copy at the slam."""
    import bpy
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    ns.reset()
    out = build()
    C.finalize(out["skel"], out["actions"])
    sk, acts = out["skel"], out["actions"]
    arm = sk.arm
    arm.data.pose_position = "POSE"
    objs = map_proxies()
    tower = bpy.data.objects["PxTower"]
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "MATERIAL"
    sc.display.shading.show_shadows = True
    sc.display.shading.show_cavity = False
    sc.render.resolution_x = res
    sc.render.resolution_y = int(res * 0.75)
    sc.render.film_transparent = False
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.color = (0.05, 0.06, 0.09)
    cam_d = bpy.data.cameras.new("MapCam")
    cam = bpy.data.objects.new("MapCam", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    loose = None
    rc = bpy.data.objects["HandR_Receipt"]

    def aim(loc, target, lens):
        cam.location = Vector(loc)
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        cam_d.lens = lens
        cam_d.clip_end = 400

    shots = {
        "HandSlam": dict(act=acts[3], frames=[0, 6, 10, 13, 17, 23, SLAM_F, 44, 51, 57, 61, 64, 67, 73],
                         cams=[((-27.0, -37.0, 8.0), (-10.0, -20.0, 5.0), 20), ((-36.0, -24.0, 9.0), (-6.0, -20.0, 5.0), 22)]),
        "HandGrabLift": dict(act=acts[4], frames=[5, 9, 12, 16, 21, 29, GRAB_F, 40, 52, 56, CHOMP_F, 66, 77, 81, 89],
                             cams=[((2.0, -32.1, 6.5), (8.0, -8.1, 6.0), 18), ((34.0, -24.0, 9.0), (6.0, -17.0, 6.0), 22)]),
    }
    pick = os.environ.get("NS_MAP_FRAMES")          # review aid: "HandSlam:17,22;HandGrabLift:52"
    if pick:
        want = {k: [int(v) for v in fs.split(",")] for k, fs in (t.split(":") for t in pick.split(";"))}
        shots = {k: dict(v, frames=want[k]) for k, v in shots.items() if k in want}
    paths = {}
    for name, spec in shots.items():
        act = spec["act"]
        C.set_action(arm, act)
        sc.frame_set(GRAB_F)
        R_, h_ = _bone(arm, "HandL")
        import numpy as np
        Mg = np.eye(4)
        Mg[:3, :3], Mg[:3, 3] = R_, h_
        tower_rest = tower.matrix_world.copy()
        rows = []
        for ci, (loc, tgt, lens) in enumerate(spec["cams"]):
            aim(loc, tgt, lens)
            ims = []
            for f in spec["frames"]:
                sc.frame_set(f)
                tower.hide_render = False
                tower.matrix_world = tower_rest
                if name == "HandGrabLift":
                    rc.hide_render = True
                    if GRAB_F < f <= CHOMP_F:
                        R_, h_ = _bone(arm, "HandL")
                        M = np.eye(4)
                        M[:3, :3], M[:3, 3] = R_, h_
                        T = M @ np.linalg.inv(Mg)
                        from mathutils import Matrix as _M
                        tower.matrix_world = _M(T.tolist()) @ tower_rest
                    elif f > CHOMP_F:
                        tower.hide_render = True
                else:
                    rc.hide_render = f >= SLAM_F
                    if loose is not None:
                        loose.hide_render = f < SLAM_F
                bpy.context.view_layer.update()
                if name == "HandSlam" and f == SLAM_F and loose is None:
                    loose = rc.copy()
                    loose.data = rc.data.copy()
                    loose.name = "PxLooseReceipt"
                    for k in list(loose.keys()):
                        del loose[k]
                    loose.parent = None
                    loose.matrix_world = rc.matrix_world.copy()
                    sc.collection.objects.link(loose)
                    loose.hide_render = False
                    rc.hide_render = True
                p = os.path.join(out_dir, f"_{name}_c{ci}_f{f}.png")
                sc.render.filepath = p
                bpy.ops.render.render(write_still=True)
                im = Image.open(p).convert("RGB")
                d = ImageDraw.Draw(im)
                d.rectangle((0, 0, res, 14), fill=(20, 20, 24))
                d.text((3, 1), f"{name} f{f} {'interior' if ci == 0 else 'side'}", fill=(235, 235, 235))
                ims.append(im)
                os.remove(p)
            rows.append(ims)
        W = res * len(rows[0])
        H = sc.render.resolution_y
        combo = Image.new("RGB", (W, H * len(rows)))
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
        map_strips(os.environ["NS_MAP_STRIPS"], res=min(480, int(os.environ.get("NS_MAP_RES", "320"))))
    else:
        C.run(build, "Creature_Patron", "Patron", strips=STRIPS)
