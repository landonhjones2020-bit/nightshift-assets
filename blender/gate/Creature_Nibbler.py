"""Creature_Nibbler — chubby rat with glowing eyes (pipeline-gate asset #3, rig + clips).

Rigid-part rig. Bones: Body (root), Head, Tail, LegFL, LegFR, LegBL, LegBR.
Every bone points +Y with zero roll, so bone-local Euler keys read as world axes:
X = pitch, Y = roll, Z = yaw. The creature faces Blender -Y (Roblox LookVector).
Clips: Idle (loop 2.0 s), Scurry (loop 0.6 s, authored for 8 studs/s), and (2026-10-30)
Nibble (loop 0.8 s, stealing from a bin), Squeak (one-shot 0.9 s, the tell at the drain;
events peak / land), Flee (loop 0.36 s, authored for ~14 studs/s), Whacked (one-shot 1.1 s,
hit by a spatula; events hit / up) and Stunned (loop 1.2 s, after Whacked). Events and the
Flee speed reference are written into anim/Nibbler.lua as a top-level `meta` table.

Env: NS_EXPORT=1 exports mesh + animations; NS_ANIM=1 exports ONLY anim/Nibbler.lua (use it
for clip changes: with today's nslib a mesh re-export rewrites meshes/gate/Creature_Nibbler.json
with the same geometry in canonical vertex order -> new hashes -> the importer re-publishes).
NS_PREVIEW_DIR = preview / pose-strip folder (default previews/gate); NS_STRIPS=Clip,Clip
limits the strips; NS_NORENDER=1 skips preview + strips. Every run prints a clip report
(lowest point over all frames = ground clipping, largest rotation step per frame = flips).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import nslib as ns  # noqa: E402
import bpy  # noqa: E402
from mathutils import Euler, Matrix, Vector  # noqa: E402

FUR = "#6E6673"
BELLY = "#A99DAB"
PINK = "#E890A6"
EYES = "#D4FF3A"
TEETH = "#F4F1EA"

PIVOT = (0.0, 0.05, 0.0)
BONES = [
    ("Body", None, (0, 0.05, 0.36), (0, 0.15, 0.36)),
    ("Head", "Body", (0, -0.3, 0.42), (0, -0.2, 0.42)),
    ("Tail", "Body", (0, 0.42, 0.3), (0, 0.52, 0.3)),
    ("LegFL", "Body", (0.17, -0.22, 0.2), (0.17, -0.12, 0.2)),
    ("LegFR", "Body", (-0.17, -0.22, 0.2), (-0.17, -0.12, 0.2)),
    ("LegBL", "Body", (0.19, 0.25, 0.22), (0.19, 0.35, 0.22)),
    ("LegBR", "Body", (-0.19, 0.25, 0.22), (-0.19, 0.35, 0.22)),
]


def pear(obj, amount=0.18):
    """Fatten the rear (+Y) of an ellipsoid so the body reads as a chubby pear."""
    ns.apply_all(obj)
    ys = [v.co.y for v in obj.data.vertices]
    y0, y1 = min(ys), max(ys)
    for v in obj.data.vertices:
        t = (v.co.y - y0) / (y1 - y0)
        k = 1.0 + amount * (t - 0.5)
        v.co.x *= k
        v.co.z = 0.36 + (v.co.z - 0.36) * k
    return obj


def build():
    arm = ns.make_armature("NibblerRig", BONES)

    body = pear(ns.sphere(1.0, loc=(0, 0.05, 0.36), scale=(0.29, 0.42, 0.26), segs=18, rings=10))
    ns.bind(ns.tag(body, "Body", FUR, "SmoothPlastic", smooth_angle=70), arm, "Body")
    belly = ns.sphere(1.0, loc=(0, -0.2, 0.31), scale=(0.19, 0.2, 0.17), segs=14, rings=8)
    ns.bind(ns.tag(belly, "Body_Belly", BELLY, "SmoothPlastic", smooth_angle=70), arm, "Body")

    skull = ns.sphere(1.0, loc=(0, -0.42, 0.43), scale=(0.21, 0.24, 0.19), segs=16, rings=9)
    snout = ns.cyl(0.115, 0.2, loc=(0, -0.62, 0.395), rot=(90, 0, 0), verts=12, radius_top=0.05, bevel=0.0)
    ears = [ns.cyl(0.115, 0.035, loc=(sx * 0.15, -0.35, 0.6), rot=(80, sx * 25, 0), verts=14, bevel=0.012)
            for sx in (-1, 1)]
    head = ns.join_applied([skull, snout] + ears, "Head")
    ns.bind(ns.tag(head, "Head", FUR, "SmoothPlastic", smooth_angle=60), arm, "Head")

    nose = ns.sphere(0.05, loc=(0, -0.725, 0.4), segs=10, rings=6)
    inner = [ns.cyl(0.075, 0.02, loc=(sx * 0.148, -0.372, 0.595), rot=(80, sx * 25, 0), verts=12, bevel=0.0)
             for sx in (-1, 1)]
    pinks = ns.join_applied([nose] + inner, "Head_Pink")
    ns.bind(ns.tag(pinks, "Head_Pink", PINK, "SmoothPlastic", smooth_angle=60), arm, "Head")

    eyes = ns.join_applied([ns.sphere(0.058, loc=(sx * 0.105, -0.555, 0.5), segs=10, rings=6) for sx in (-1, 1)],
                           "Head_Eyes")
    ns.bind(ns.tag(eyes, "Head_Eyes", EYES, "Neon", cast_shadow=False, smooth_angle=80), arm, "Head")

    teeth = ns.join_applied([ns.box((0.034, 0.02, 0.06), loc=(sx * 0.019, -0.66, 0.325), bevel=0.006, segments=1)
                             for sx in (-1, 1)], "Head_Teeth")
    ns.bind(ns.tag(teeth, "Head_Teeth", TEETH, "SmoothPlastic"), arm, "Head")

    tail = ns.tube([(0, 0.4, 0.31), (0, 0.68, 0.17), (0.07, 0.96, 0.12), (0.17, 1.2, 0.2)],
                   [0.055, 0.042, 0.03, 0.014], sides=8, resolution=4, name="Tail")
    ns.bind(ns.tag(tail, "Tail", PINK, "SmoothPlastic", smooth_angle=80), arm, "Tail")

    for bone, (x, y), back in (("LegFL", (0.17, -0.24), False), ("LegFR", (-0.17, -0.24), False),
                               ("LegBL", (0.19, 0.25), True), ("LegBR", (-0.19, 0.25), True)):
        if back:
            leg = ns.sphere(1.0, loc=(x, y, 0.15), scale=(0.1, 0.15, 0.13), segs=12, rings=7)
            paw = ns.sphere(1.0, loc=(x, y - 0.03, 0.028), scale=(0.075, 0.12, 0.03), segs=10, rings=5)
        else:
            leg = ns.sphere(1.0, loc=(x, y, 0.11), scale=(0.07, 0.08, 0.11), segs=10, rings=6)
            paw = ns.sphere(1.0, loc=(x, y - 0.035, 0.026), scale=(0.07, 0.085, 0.028), segs=10, rings=5)
        ns.bind(ns.tag(leg, bone, FUR, "SmoothPlastic", smooth_angle=70), arm, bone)
        ns.bind(ns.tag(paw, bone + "_Paw", PINK, "SmoothPlastic", smooth_angle=70), arm, bone)

    # ---------------- animation ----------------
    idle = ns.new_action(arm, "Idle", 0, 60, loop=True)
    for f, z in ((0, 0.0), (30, 0.018), (60, 0.0)):
        ns.key(arm, "Body", f, rot=(0, 0, 0), loc=(0, 0, z))
    for f, rot in ((0, (0, 0, 0)), (12, (-10, 0, 14)), (24, (-4, 0, 16)), (36, (-12, 0, -12)), (48, (-3, 0, -10)), (60, (0, 0, 0))):
        ns.key(arm, "Head", f, rot=rot)
    for f, rot in ((0, (0, 0, 0)), (30, (6, 0, 22)), (60, (0, 0, 0))):
        ns.key(arm, "Tail", f, rot=rot)

    scurry = ns.new_action(arm, "Scurry", 0, 18, loop=True)
    swing = 34
    for leg, phase in (("LegFL", 1), ("LegBR", 1), ("LegFR", -1), ("LegBL", -1)):
        for f, s in ((0, -phase), (9, phase), (18, -phase)):
            ns.key(arm, leg, f, rot=(swing * s, 0, 0))
    for f, z, roll in ((0, 0.0, -3), (4, 0.04, 0), (9, 0.0, 3), (13, 0.04, 0), (18, 0.0, -3)):
        ns.key(arm, "Body", f, rot=(0, roll, 0), loc=(0, 0, z))
    for f, p in ((0, 4), (4, -3), (9, 4), (13, -3), (18, 4)):
        ns.key(arm, "Head", f, rot=(p, 0, 0))
    for f, yaw in ((0, -20), (9, 20), (18, -20)):
        ns.key(arm, "Tail", f, rot=(8, 0, yaw))

    return {"arm": arm, "actions": [idle, scurry] + add_clips(arm),
            "export": {"rig": arm, "pivot": PIVOT,
                       "meta": {"root": {"center": [0, 0.36, 0.0], "size": [0.6, 0.5, 0.84]},
                                "walkSpeed": 8, "clipSpeedRef": {"Scurry": 8}}}}


# ======================================================================================
# Extra clips (batch L_decor, 2026-10-30): Nibble, Squeak, Flee, Whacked, Stunned.
# Every bone's rest frame is a pure translation (bones point +Y, roll 0), so a bone's
# world matrix is Body(T R T^-1) . bone(T R T^-1). The helpers below use that to plant
# paws, rest the body / head / tail on the ground and keep everything above z = 0.
# Keys: rot = (pitch X, roll Y, yaw Z) degrees, Body also loc (studs, bone frame = world).
# ======================================================================================
HEADS = {name: Vector(head) for name, _parent, head, _tail in BONES}
LEFT_LEGS = ("LegFL", "LegBL")       # +X side
RIGHT_LEGS = ("LegFR", "LegBR")
# events (seconds from clip start) and speed references, written into anim/Nibbler.lua meta
CLIP_EVENTS = {"Squeak": {"peak": round(10 / 30, 3), "land": round(22 / 30, 3)},
               "Whacked": {"hit": round(3 / 30, 3), "up": round(25 / 30, 3)}}
CLIP_SPEED = {"Flee": 14}


def _rm(rot):
    return Euler(tuple(math.radians(a) for a in rot), "XYZ").to_matrix().to_4x4()


def _mats(pose):
    """World matrix per bone for pose = {"Body": (rot, loc), "<Bone>": rot, ...}."""
    rot_b, loc_b = pose["Body"]
    hb = HEADS["Body"]
    mb = Matrix.Translation(hb + Vector(loc_b)) @ _rm(rot_b) @ Matrix.Translation(-hb)
    out = {"Body": mb}
    for b, h in HEADS.items():
        if b != "Body":
            out[b] = mb @ Matrix.Translation(h) @ _rm(pose.get(b, (0, 0, 0))) @ Matrix.Translation(-h)
    return out


def _rest_points(arm):
    """World-space rest vertices of the parts bound to each bone."""
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    pts = {}
    for o in bpy.context.scene.objects:
        if o.type == "MESH" and "ns_bone" in o:
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            pts.setdefault(o["ns_bone"], []).extend(o.matrix_world @ v.co for v in me.vertices)
            ev.to_mesh_clear()
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()
    return pts


def _minz(P, mats, bones=None):
    return min((mats[b] @ p).z for b in (bones or list(P)) for p in P[b])


def _solve(P, pose, bone, axis, lo, hi, prefer, target=0.0, contact=True, step=0.5):
    """Set `bone`'s angle on `axis` (0 pitch, 1 roll, 2 yaw) within [lo, hi]: the one nearest
    `prefer` that keeps the bone's parts above `target`; contact=True prefers its lowest
    point touching `target` (planted paw, head / tail lying on the floor)."""
    base = list(pose.get(bone, (0, 0, 0)))
    best = fallback = None
    for i in range(int(round((hi - lo) / step)) + 1):
        a = lo + i * step
        r = list(base)
        r[axis] = a
        p2 = dict(pose)
        p2[bone] = tuple(r)
        z = _minz(P, _mats(p2), [bone])
        if fallback is None or z > fallback[1]:
            fallback = (a, z)
        if z - target >= -0.002:
            score = (abs(z - target) if contact else 0.0) + 0.0015 * abs(a - prefer)
            if best is None or score < best[1]:
                best = (a, score)
    r = list(base)
    r[axis] = round((best or fallback)[0], 2)
    pose[bone] = tuple(r)
    return pose


def _drop_to(P, pose, bones, target):
    """Move the Body (loc z) so the lowest point of `bones` sits at `target`."""
    rot, loc = pose["Body"]
    z = _minz(P, _mats(pose), bones)
    pose["Body"] = (rot, (loc[0], loc[1], round(loc[2] + target - z, 4)))
    return pose


def _lift(P, pose, floor=0.0):
    """Raise the Body if anything dips below `floor`."""
    z = _minz(P, _mats(pose))
    if z < floor:
        rot, loc = pose["Body"]
        pose["Body"] = (rot, (loc[0], loc[1], round(loc[2] + floor - z, 4)))
    return pose


def _hip_loc(pitch, hip_z=None):
    """Body loc that keeps the hind hips (x = 0 midpoint) fixed while the body pitches
    (rearing pivots on the hind paws); hip_z overrides the hip height."""
    h = HEADS["LegBL"] - HEADS["Body"]
    h = Vector((0.0, h.y, h.z))
    rh = _rm((pitch, 0, 0)).to_3x3() @ h
    loc = h - rh
    if hip_z is not None:
        loc.z = hip_z - (HEADS["Body"].z + rh.z)
    return (0.0, round(loc.y, 4), round(loc.z, 4))


def _key_pose(arm, f, pose, ease="SINE", direction="EASE_IN_OUT"):
    rot_b, loc_b = pose["Body"]
    ns.key(arm, "Body", f, rot=rot_b, loc=loc_b, ease=ease, direction=direction)
    for b in HEADS:
        if b != "Body":
            ns.key(arm, b, f, rot=pose.get(b, (0, 0, 0)), ease=ease, direction=direction)


def _ease_io(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def _wrap(d):
    return min(abs(d), 1.0 - abs(d))


def _hind_planted(P, pose, pitch, window=10.0):
    """Hind paws planted, legs near upright in the world (narrow window: no solution flips)."""
    for b in ("LegBL", "LegBR"):
        _solve(P, pose, b, 0, -pitch - window, -pitch + window, -pitch)
    return pose


def _front_planted(P, pose, lo, hi, prefer):
    for b in ("LegFL", "LegFR"):
        _solve(P, pose, b, 0, lo, hi, prefer)
    return pose


def clip_nibble(arm, P):
    """Loop 0.8 s: front half dips at a bin edge (front paws braced forward), head bobs and
    chews (three bites), tail swishes twice."""
    act = ns.new_action(arm, "Nibble", 0, 24, loop=True)
    for f in range(0, 25, 2):
        ph = (f % 24) / 24.0
        dip = math.exp(-(_wrap(ph - 0.12) / 0.1) ** 2)
        pitch = round(5.0 + 3.5 * dip, 2)
        pose = {"Body": ((pitch, round(1.2 * math.sin(2 * math.pi * ph), 2), 0.0), _hip_loc(pitch, 0.224))}
        pose["Head"] = (round(22 + 12 * dip + 6 * math.sin(2 * math.pi * 3 * ph + 0.6), 2),
                        round(3 * math.sin(2 * math.pi * 3 * ph + 1.2), 2), round(6 * math.sin(2 * math.pi * ph), 2))
        pose["Tail"] = (round(6 + 4 * math.sin(2 * math.pi * 2 * ph + 1.6), 2), 0.0,
                        round(24 * math.sin(2 * math.pi * 2 * ph), 2))
        _hind_planted(P, pose, pitch, 12.0)
        _front_planted(P, pose, -75.0, -5.0, -40.0)
        _lift(P, pose)
        _key_pose(arm, f, pose, ease="LINEAR")
    return act


def clip_squeak(arm, P):
    """One-shot 0.9 s: rears up on the hind legs (pivoting on the hind paws), head tilts up,
    quick shiver at the top (event peak = the squeak), drops back to all fours (event land)."""
    act = ns.new_action(arm, "Squeak", 0, 27, loop=False)
    top = -52.0

    def reared(f, pitch, roll=0.0, head=None, tail_yaw=0.0, falling=False):
        t = pitch / top                                    # 0 = on all fours, 1 = fully reared
        pose = {"Body": ((round(pitch, 2), roll, 0.0), _hip_loc(pitch))}
        pose["Head"] = head if head is not None else (round(-18.0 * t, 2), 0.0, 0.0)
        for b, s in (("LegFL", 1), ("LegFR", -1)):        # front paws tucked up to the chest ...
            fp = 26.0 * t - (32.0 * (1.0 - t) if falling else 0.0)   # ... reaching out again to land
            pose[b] = (round(fp, 2), round(9.0 * s * t, 2), 0.0)
        _hind_planted(P, pose, pitch)
        pose["Tail"] = (0.0, 0.0, tail_yaw)
        if t > 0.75:
            _solve(P, pose, "Tail", 0, -10, 90, 45, target=0.004)              # tail lying on the floor
        else:
            _solve(P, pose, "Tail", 0, -10, 90, 45 * t, target=0.004, contact=False)
        _lift(P, pose)
        _key_pose(arm, f, pose, ease="LINEAR")

    for f in (0, 2, 4, 6, 8):                              # rise (eased), pivoting on the hind paws
        reared(f, top * _ease_io(f / 8.0))
    reared(10, top, roll=3.5, head=(-26, 0, 4), tail_yaw=4)
    for f, roll, yaw in ((11, -3.5, -6), (12, 3.5, 6), (13, -3.0, -5), (14, 3.0, 5), (15, -2.0, -3), (16, 1.5, 2)):
        reared(f, top, roll=roll, head=(-26, 0, yaw), tail_yaw=-yaw)
    reared(17, top)
    for f in (19, 20, 21):                                 # fall (accelerating), still on the hind paws
        t = (f - 17) / 5.0
        reared(f, top + (top * -1 + 5.0) * t * t, falling=True)
    # land: nose slightly down, front paws reaching forward to catch it
    land = {"Body": ((5.0, 0.0, 0.0), _hip_loc(5.0, 0.215)), "Head": (9, 0, 0)}
    _hind_planted(P, land, 5.0)
    _front_planted(P, land, -70.0, 0.0, -30.0)
    _lift(P, land)
    _key_pose(arm, 22, land, ease="SINE", direction="EASE_OUT")
    settle = {"Body": ((-1.5, 0.0, 0.0), _hip_loc(-1.5, 0.214)), "Head": (-4, 0, 0), "Tail": (2, 0, 8)}
    _hind_planted(P, settle, -1.5)
    _front_planted(P, settle, -40.0, 10.0, -5.0)
    _lift(P, settle)
    _key_pose(arm, 25, settle, ease="SINE", direction="EASE_IN_OUT")
    _key_pose(arm, 27, {"Body": ((0, 0, 0), (0, 0, 0))})
    return act


def clip_flee(arm, P):
    """Loop 0.36 s (50 fps): bounding gallop - longer stride (+-50 deg vs Scurry's 34), body
    lower on average and rocking, head low, tail held straight back. Authored for ~14 st/s."""
    act = ns.new_action(arm, "Flee", 0, 18, loop=True, fps=50)
    for f in range(0, 19, 2):
        ph = (f % 18) / 18.0
        c = math.cos(2 * math.pi * ph)
        pitch = 3.5 * c
        pose = {"Body": ((round(pitch, 2), round(2.0 * math.sin(2 * math.pi * ph), 2), 0.0),
                         (0.0, 0.0, round(-0.03 - 0.022 * math.cos(4 * math.pi * ph), 4)))}
        lag = math.cos(2 * math.pi * (ph - 0.06))
        pose["LegFL"] = (round(-50 * c, 2), 0.0, 0.0)
        pose["LegFR"] = (round(-46 * lag, 2), 0.0, 0.0)
        pose["LegBL"] = (round(46 * c, 2), 0.0, 0.0)
        pose["LegBR"] = (round(42 * lag, 2), 0.0, 0.0)
        pose["Head"] = (round(9 - 4 * math.cos(4 * math.pi * ph), 2), 0.0, 0.0)
        pose["Tail"] = (round(7 + 1.5 * math.sin(4 * math.pi * ph), 2), 0.0, round(2.5 * math.sin(2 * math.pi * ph), 2))
        _lift(P, pose, floor=0.002)
        _key_pose(arm, f, pose, ease="LINEAR")
    return act


def _splat(P, roll, pitch=3.0, yaw=-4.0, splay=85.0, t=1.0):
    """Flattened pose (t = 0..1 of the way there): legs splayed out flat, then the body
    dropped until body or legs touch the floor; head slammed down, tail limp on the floor."""
    pose = {"Body": ((pitch * t, roll * t, yaw * t), (0.0, 0.0, 0.0))}
    for b, s in (("LegFL", -1), ("LegBL", -1), ("LegFR", 1), ("LegBR", 1)):
        pose[b] = (round((-25.0 if b in ("LegFL", "LegFR") else 25.0) * t, 2), round(s * splay * t, 2), 0.0)
    pose["Head"] = (0.0, 0.0, 0.0)
    pose["Tail"] = (0.0, 0.0, round(18.0 * t, 2))
    rot, _loc = pose["Body"]
    full = dict(pose)
    _drop_to(P, full, ["Body", "LegFL", "LegFR", "LegBL", "LegBR"], 0.004)
    pose["Body"] = (rot, (0.0, 0.0, round(full["Body"][1][2] * t, 4)))
    if t >= 0.99:
        _solve(P, pose, "Head", 0, 0, 70, 35, target=0.004)
        _solve(P, pose, "Tail", 0, -60, 10, -18, target=0.004)
    else:
        pose["Head"] = (round(30.0 * t, 2), 0.0, 0.0)
        pose["Tail"] = (round(-12.0 * t, 2), 0.0, round(18.0 * t, 2))
    _lift(P, pose)
    return pose


def clip_whacked(arm, P):
    """One-shot 1.1 s: flattened by a spatula (event hit) - body slams down tilted, legs
    splay flat, head slams down, tail limp; a dizzy wobble; then it pops back up onto its
    legs (event up) and settles to rest."""
    act = ns.new_action(arm, "Whacked", 0, 33, loop=False)
    rest = {"Body": ((0, 0, 0), (0, 0, 0))}
    _key_pose(arm, 0, rest, ease="LINEAR")
    _key_pose(arm, 1, _splat(P, 9.0, t=0.22), ease="LINEAR")         # accelerating into the hit
    _key_pose(arm, 2, _splat(P, 9.0, t=0.62), ease="LINEAR")
    _key_pose(arm, 3, _splat(P, 9.0), ease="QUAD", direction="EASE_OUT")
    bounce = _splat(P, 6.0)
    rot, loc = bounce["Body"]
    bounce["Body"] = (rot, (loc[0], loc[1], loc[2] + 0.014))
    hp = bounce["Head"]
    bounce["Head"] = (hp[0] - 8, hp[1], hp[2])
    _lift(P, bounce)
    _key_pose(arm, 5, bounce, ease="QUAD", direction="EASE_IN")
    _key_pose(arm, 7, _splat(P, 7.0))
    for f, roll, hyaw, hroll in ((10, -4.0, 14, -6), (13, 5.0, -12, 6), (16, -3.0, 9, -4), (19, 2.0, -6, 3)):
        p = _splat(P, roll, yaw=-4.0 + roll * 0.5)
        hp = p["Head"]
        p["Head"] = (hp[0], hroll, hyaw)
        _key_pose(arm, f, p)
    gather = _splat(P, 0.0, pitch=2.0, yaw=0.0, splay=45.0)
    _key_pose(arm, 22, gather, ease="QUAD", direction="EASE_OUT")      # spring up
    pop = {"Body": ((-6.0, 0.0, 0.0), (0.0, 0.0, 0.09)), "Head": (-12, 0, 0), "Tail": (18, 0, -6),
           "LegFL": (-12, -4, 0), "LegFR": (-12, 4, 0), "LegBL": (12, -4, 0), "LegBR": (12, 4, 0)}
    _key_pose(arm, 25, pop, ease="QUAD", direction="EASE_IN")          # fall back down
    land = {"Body": ((2.0, 0.0, 0.0), _hip_loc(2.0, 0.21)), "Head": (5, 0, 0), "Tail": (5, 0, 4)}
    _hind_planted(P, land, 2.0, 15.0)
    _front_planted(P, land, -50.0, 10.0, -10.0)
    _lift(P, land)
    _key_pose(arm, 28, land, ease="SINE", direction="EASE_OUT")
    settle = {"Body": ((-1.0, 0.0, 0.0), (0.0, 0.0, 0.004)), "Head": (-2, 0, 0), "Tail": (0, 0, 10)}
    _key_pose(arm, 30, settle)
    _key_pose(arm, 33, rest)
    return act


def clip_stunned(arm, P):
    """Loop 1.2 s: dizzy sway (body rolls and yaws) with the head circling; paws stay planted
    (legs re-angled every key), tail drifts."""
    act = ns.new_action(arm, "Stunned", 0, 36, loop=True)
    for f in range(0, 37, 3):
        ph = (f % 36) / 36.0
        w = 2 * math.pi * ph
        pose = {"Body": ((round(2 + 1.5 * math.sin(2 * w), 2), round(7 * math.sin(w), 2), round(5 * math.cos(w), 2)),
                         (0.0, 0.0, -0.006))}
        pose["Head"] = (round(10 + 12 * math.sin(w), 2), round(10 * math.cos(w + 0.3), 2), round(22 * math.cos(w), 2))
        pose["Tail"] = (round(-2 + 3 * math.sin(w), 2), 0.0, round(14 * math.sin(w + 0.6), 2))
        for b, s, p0 in (("LegFL", -1, -6), ("LegBL", -1, 6), ("LegFR", 1, -6), ("LegBR", 1, 6)):
            pose[b] = (p0, 6.0 * s, 0.0)
            lo, hi = (-35.0, 10.0) if s < 0 else (-10.0, 35.0)
            _solve(P, pose, b, 1, lo, hi, 6.0 * s)
        _lift(P, pose)
        _key_pose(arm, f, pose, ease="LINEAR")
    return act


def add_clips(arm):
    """Build the extra clips (after Idle / Scurry, which stay untouched)."""
    P = _rest_points(arm)
    return [clip_nibble(arm, P), clip_squeak(arm, P), clip_flee(arm, P), clip_whacked(arm, P), clip_stunned(arm, P)]


def anim_meta():
    return {"events": CLIP_EVENTS, "clipSpeedRef": CLIP_SPEED,
            "note": "events in seconds from clip start; Flee authored for ~14 studs/s (Scurry 8, in the mesh meta)"}


def append_anim_meta(path, meta):
    """Append `meta = {...}` to the module nslib wrote (top-level table), like PlayerR15.lua."""
    with open(path) as f:
        src = f.read().rstrip()
    assert src.endswith("}"), "unexpected module shape"
    body = src[:-1].rstrip()
    if not body.endswith(","):
        body += ","
    body += "\n\tmeta = " + ns._to_lua(meta, 1) + ",\n}\n"
    with open(path, "w") as f:
        f.write(body)


# ------------------------------- review helpers -------------------------------------
STRIPS = {"Scurry": [0, 4, 9, 13], "Idle": [0, 12, 36, 48],
          "Nibble": [0, 2, 4, 8, 12, 16, 20], "Squeak": [0, 4, 8, 10, 13, 17, 20, 22, 25],
          "Flee": [0, 2, 4, 6, 8, 10, 12, 14, 16], "Whacked": [0, 3, 5, 10, 16, 22, 24, 25, 28, 31],
          "Stunned": [0, 6, 12, 18, 24, 30]}


def clip_report(arm, actions):
    """Per clip: lowest point over every frame (ground clipping) and the largest per-frame
    bone rotation step (limb flips show up as huge steps)."""
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and "ns_part" in o]
    dg = bpy.context.evaluated_depsgraph_get()
    local = {}
    for o in objs:
        me = o.evaluated_get(dg).to_mesh()
        local[o.name] = [v.co.copy() for v in me.vertices]
        o.evaluated_get(dg).to_mesh_clear()
    lines = []
    for act in actions:
        arm.animation_data.action = act
        if hasattr(arm.animation_data, "action_slot") and len(getattr(act, "slots", [])) > 0:
            arm.animation_data.action_slot = act.slots[0]
        lo_z, lo_f, max_step, step_bone = 1e9, None, 0.0, None
        prev = None
        for f in range(act["ns_start"], act["ns_end"] + 1):
            bpy.context.scene.frame_set(f)
            z = min((o.matrix_world @ c).z for o in objs for c in local[o.name])
            if z < lo_z:
                lo_z, lo_f = z, f
            q = {pb.name: pb.rotation_quaternion.copy() for pb in arm.pose.bones}
            if prev:
                for b, qq in q.items():
                    d = math.degrees(prev[b].rotation_difference(qq).angle)
                    if d > max_step:
                        max_step, step_bone = d, b
            prev = q
        fps = act.get("ns_fps", 30)
        lines.append(f"{act.name:8s} {(act['ns_end'] - act['ns_start']) / fps:5.3f}s loop={bool(act['ns_loop'])!s:5s} "
                     f"min z {lo_z:+.4f} @f{lo_f}  max step/frame {max_step:5.1f} deg ({step_bone})")
    bpy.context.scene.frame_set(0)
    return lines


def _pil_path():
    """Previews / strips need Pillow; the bpy venv may not ship it (borrow the system copy)."""
    try:
        import PIL  # noqa: F401
    except ImportError:
        import glob
        v = f"python{sys.version_info.major}.{sys.version_info.minor}"
        for sp in glob.glob(f"/usr/local/lib/{v}/site-packages") + glob.glob(f"/usr/lib/{v}/site-packages"):
            if os.path.isdir(os.path.join(sp, "PIL")):
                sys.path.append(sp)
                break


if __name__ == "__main__":
    _pil_path()
    prev_dir = os.environ.get("NS_PREVIEW_DIR") or os.path.join(ns.REPO, "..", "previews", "gate")
    render = os.environ.get("NS_NORENDER") != "1"
    if render:
        os.makedirs(prev_dir, exist_ok=True)
    ns.reset()
    out = build()
    print(f"[Creature_Nibbler] triangles: {ns.tri_count()}")
    if render:
        print("[Creature_Nibbler] preview:", ns.render_preview("Creature_Nibbler", out_dir=prev_dir))
    if os.environ.get("NS_EXPORT") == "1":
        doc = ns.export_asset("Creature_Nibbler", "gate", group="Creatures", **out["export"])
        print(f"[Creature_Nibbler] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']}")
    for line in clip_report(out["arm"], out["actions"]):
        print("[Creature_Nibbler] clip", line)
    wanted = set(os.environ["NS_STRIPS"].split(",")) if os.environ.get("NS_STRIPS") else set(STRIPS)
    for act in out["actions"]:
        if render and act.name in wanted:
            print("[Creature_Nibbler] strip:", ns.render_pose_strip(out["arm"], act, STRIPS[act.name],
                                                                    f"Nibbler_{act.name}", prev_dir))
    if os.environ.get("NS_EXPORT") == "1" or os.environ.get("NS_ANIM") == "1":
        path = ns.export_animations(out["arm"], "Nibbler", out["actions"])
        append_anim_meta(path, anim_meta())
        print("[Creature_Nibbler] anim:", path)
