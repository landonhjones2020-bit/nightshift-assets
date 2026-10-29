"""Creature_LightsOut — 9-stud, rail-thin thing with an old lampshade for a head.

Rigid-part rig (bones point +Y, roll 0; see _common). Front = Blender -Y, "L" = +X.
Bones: Hips (root) > Torso > Head (neck, lampshade, socket, bulb); arms UpperArm/Forearm/
Hand/Fingers L/R (Fingers = the very long finger set, curls in Catch); legs Thigh/Shin/Foot.
Roles: "glow" = the dead bulb inside the shade (default dull grey SmoothPlastic; the client
lights it, e.g. Neon + warm yellow, when a flashlight hits it). The darkness haze is a few
near-black parts at Transparency 0.6 bound to the torso, hips, thighs and upper arms.

Clips (30 fps): IdleSway (loop), Walk (loop, stilted, 10 studs/s = patrol), Investigate
(loop, head-tilt search), ChaseRun (loop, 19 studs/s), Recoil (shields its face, trembles),
Catch (one-shots, end on rest), Dissolve (TERMINAL: shrieks, collapses and sinks fully
below the floor; despawn at events.Dissolve.gone - it does not return to rest).
Authored at 9.14 studs, then the whole rig is scaled uniformly by SCALE (0.825 -> 7.54 tall,
under the 8-stud doorways it walks through): meshes, bone rest positions and every clip's
translation keys (C.rescale). Rotations are unchanged, so clipSpeedRef = authored speed x SCALE.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
rd = C.rot_deg

SUIT = "#22222A"
SUIT_D = "#141418"
SKIN = "#3A3940"            # long grey-black fingers
SHADE = "#D8C9A3"
SHADE_IN = "#4A3B2A"
STAIN = "#7A6040"
BURN = "#120E0B"
FRINGE = "#8C6A3A"
BRASS = "#9C7E45"
BULB = "#6F6C62"
HAZE = "#0A0A10"

SHOULDER = (0.62, 0.05, 6.95)
ELBOW = (0.7, 0.08, 5.15)
WRIST = (0.74, 0.03, 3.4)
KNUCKLE = (0.75, 0.0, 3.05)
HIP_J = (0.25, 0.03, 4.55)
KNEE = (0.25, 0.03, 2.45)
ANKLE = (0.25, 0.03, 0.38)
SHADE_LO, SHADE_HI = 7.68, 8.9
SCALE = 0.825                 # final uniform scale (authored 9.14 tall -> 7.54)
SHADE_C = Vector((0.0, -0.02, 0.0))


def mx(p, s):
    return (p[0] * s, p[1], p[2])


JOINTS = [
    ("Hips", None, (0.0, 0.03, 4.65)),
    ("Torso", "Hips", (0.0, 0.05, 5.0)),
    ("Head", "Torso", (0.0, 0.0, 7.12)),
    ("UpperArmL", "Torso", SHOULDER),
    ("ForearmL", "UpperArmL", ELBOW),
    ("HandL", "ForearmL", WRIST),
    ("FingersL", "HandL", KNUCKLE),
    ("UpperArmR", "Torso", mx(SHOULDER, -1)),
    ("ForearmR", "UpperArmR", mx(ELBOW, -1)),
    ("HandR", "ForearmR", mx(WRIST, -1)),
    ("FingersR", "HandR", mx(KNUCKLE, -1)),
    ("ThighL", "Hips", HIP_J),
    ("ShinL", "ThighL", KNEE),
    ("FootL", "ShinL", ANKLE),
    ("ThighR", "Hips", mx(HIP_J, -1)),
    ("ShinR", "ThighR", mx(KNEE, -1)),
    ("FootR", "ShinR", mx(ANKLE, -1)),
]


# ======================================================================================
# Model
# ======================================================================================

def wisps(specs, seed):
    """Darkness haze: elongated soft blobs (centre, radii) with a little jitter."""
    rnd = random.Random(seed)
    out = []
    for c, r in specs:
        o = C.ell(c, r, segs=10, rings=6)
        sd = rnd.random() * 10
        C.deform(o, lambda v, sd=sd: v + Vector((C.noise3(v * 2.0, sd) * 0.07, C.noise3(v * 2.3, sd + 1.3) * 0.07,
                                                 C.noise3(v * 1.7, sd + 2.1) * 0.1)))
        out.append(o)
    return out


def build_model(sk):
    arm = sk.arm
    A = lambda objs, name, color, bone, mat="SmoothPlastic", **kw: C.attach(objs, name, color, arm, bone, mat, **kw)  # noqa: E731
    haze = dict(mat="SmoothPlastic", transparency=0.6, cast_shadow=False, smooth_angle=80)

    # ---- torso: narrow, bony suit ----------------------------------------------------------
    torso = C.loft([(4.9, 0.2, 0.15, 0, 0.03), (5.4, 0.2, 0.15, 0, 0.04), (6.2, 0.3, 0.19, 0, 0.05),
                    (6.75, 0.42, 0.2, 0, 0.06), (7.0, 0.55, 0.19, 0, 0.06), (7.12, 0.36, 0.15, 0, 0.05),
                    (7.18, 0.12, 0.1, 0, 0.03)], verts=12, n=2.2, name="Torso")
    lap = [C.extrude([(0.0, 5.6), (sx * 0.2, 6.95), (sx * 0.07, 7.0)], 0.03, plane="XZ", offset=-0.17)
           for sx in (-1, 1)]
    A([torso], "Torso", SUIT, "Torso", smooth_angle=60)
    A(lap, "Torso_Lapels", SUIT_D, "Torso", smooth_angle=50)
    A(wisps([((0.22, 0.12, 6.0), (0.32, 0.3, 0.75)), ((-0.25, 0.05, 6.6), (0.3, 0.32, 0.55))], 1), "Torso_Haze", HAZE,
      "Torso", **haze)
    hips = C.ell((0, 0.03, 4.72), (0.27, 0.18, 0.22), segs=12, rings=6)
    A([hips], "Hips", SUIT, "Hips", smooth_angle=60)
    A(wisps([((0.0, 0.12, 4.6), (0.38, 0.3, 0.45))], 2), "Hips_Haze", HAZE, "Hips", **haze)

    # ---- head: long neck, socket, dead bulb, lampshade --------------------------------------
    neck = C.capsule((0, 0.03, 7.05), (0, -0.02, 7.72), 0.07, 0.06, verts=8, cap_rings=2)
    A([neck], "Head", SUIT_D, "Head", smooth_angle=60)
    socket = [ns.cyl(0.13, 0.22, loc=(0, -0.02, 7.83), verts=12, bevel=0.02, segments=1),
              ns.cyl(0.16, 0.05, loc=(0, -0.02, 7.73), verts=12, bevel=0.0)]
    harp = [C.rod((sx * 0.13, -0.02, 7.8), (sx * 0.62, -0.02, 8.86), 0.018, verts=4) for sx in (-1, 1)]
    A(socket + harp, "Head_Brass", BRASS, "Head", "Metal", smooth_angle=50)
    bulb = ns.lathe([(0.0, 7.93), (0.09, 7.95), (0.1, 8.05), (0.2, 8.2), (0.24, 8.33), (0.22, 8.45),
                     (0.14, 8.53), (0.0, 8.56)], verts=14)
    bulb.location = (0, -0.02, 0)
    A([bulb], "Head_Bulb", BULB, "Head", recolor="glow", smooth_angle=70)
    filament = C.rod((-0.05, -0.02, 8.2), (0.05, -0.02, 8.26), 0.012, verts=4)
    A([filament], "Head_Filament", "#2A2420", "Head", smooth_angle=None)

    prof = [(0.98, SHADE_LO), (0.9, 8.0), (0.75, 8.45), (0.6, SHADE_HI)]
    outer = C.loft([(z, r, r, 0.0, -0.02) for r, z in prof], verts=22, cap_bottom=False, cap_top=False, name="Shade")

    def crooked(v):
        # dented, slightly crooked old shade
        n = C.noise3(v * 2.4, 3.3)
        k = 1.0 + 0.035 * n
        v.x *= k
        v.y = -0.02 + (v.y + 0.02) * k
        v.z += 0.09 * v.x
        return v
    C.deform(outer, crooked)
    inner = outer.copy()
    inner.data = outer.data.copy()
    import bpy
    bpy.context.scene.collection.objects.link(inner)
    C.deform(inner, lambda v: Vector((v.x * 0.965, -0.02 + (v.y + 0.02) * 0.965, v.z)))
    sol = outer.modifiers.new("S", "SOLIDIFY")
    sol.thickness = 0.03
    A([outer], "Head_Shade", SHADE, "Head", "Fabric", smooth_angle=40)
    A([inner], "Head_ShadeInside", SHADE_IN, "Head", "Fabric", smooth_angle=40)
    top = ns.torus(0.6, 0.025, loc=(0, -0.02, SHADE_HI + 0.0), major_segs=22, minor_segs=4)
    rim = ns.torus(0.98, 0.03, loc=(0, -0.02, SHADE_LO), major_segs=22, minor_segs=4)
    for o in (top, rim):
        C.deform(o, lambda v: Vector((v.x, v.y, v.z + 0.09 * v.x)))
    finial = [ns.cyl(0.05, 0.12, loc=(0, -0.02, SHADE_HI + 0.08), verts=8, bevel=0.0),
              C.ell((0, -0.02, SHADE_HI + 0.17), (0.07, 0.07, 0.07), segs=8, rings=5)]
    A([top, rim] + finial, "Head_Trim", FRINGE, "Head", "Metal", smooth_angle=50)
    tassels = []
    for i in range(18):
        a = 2 * math.pi * i / 18
        x, y = 0.99 * math.cos(a), -0.02 + 0.99 * math.sin(a)
        z0 = SHADE_LO + 0.09 * x
        L = 0.22 if i % 2 else 0.3
        tassels.append(C.rod((x, y, z0), (x * 1.01, y, z0 - L), 0.025, verts=4, r_top=0.012))
    A(tassels, "Head_Fringe", FRINGE, "Head", smooth_angle=None)
    # stains + two scorched holes where a face would be
    stains = []
    rnd = random.Random(9)
    for ang, z, r in ((-114, 8.25, 0.16), (-68, 8.21, 0.15), (40, 8.05, 0.2), (160, 8.5, 0.15), (-160, 7.95, 0.12)):
        a = math.radians(ang)
        rr = 0.9 - 0.32 * (z - SHADE_LO) / (SHADE_HI - SHADE_LO) + 0.03
        p = Vector((rr * math.cos(a), -0.02 + rr * math.sin(a), z + 0.09 * rr * math.cos(a)))
        o = C.ell((0, 0, 0), (r * 1.2, 0.035, r), segs=10, rings=5)
        o.rotation_euler = (0, 0, a + math.pi / 2)
        ns.apply_all(o)
        o.location = p
        ns.apply_all(o)
        stains.append((o, ang))
    A([o for o, ang in stains if ang not in (-114, -68)], "Head_Stains", STAIN, "Head", "Fabric", smooth_angle=70)
    A([o for o, ang in stains if ang in (-114, -68)], "Head_Burns", BURN, "Head", "Fabric", smooth_angle=70)

    # ---- arms: long, thin, with very long fingers ---------------------------------------------
    for s, side in (("L", 1), ("R", -1)):
        S, E, W, K = (Vector(mx(p, side)) for p in (SHOULDER, ELBOW, WRIST, KNUCKLE))
        up = C.capsule(S, E, 0.12, 0.1, verts=8, cap_rings=2)
        sh = C.ell(S + Vector((side * 0.04, 0, 0.02)), (0.15, 0.14, 0.12), segs=8, rings=5)
        A([up, sh], "UpperArm" + s, SUIT, "UpperArm" + s, smooth_angle=60)
        A(wisps([(S + Vector((side * 0.1, 0.1, -0.5)), (0.2, 0.2, 0.55))], 10 + side), "UpperArm" + s + "_Haze", HAZE,
          "UpperArm" + s, **haze)
        fo = C.capsule(E, W + Vector((0, 0, 0.1)), 0.1, 0.09, verts=8, cap_rings=2)
        cuff = ns.cyl(0.11, 0.12, loc=W + Vector((0, 0, 0.12)), verts=8, bevel=0.02, segments=1)
        A([fo, cuff], "Forearm" + s, SUIT, "Forearm" + s, smooth_angle=60)
        palm = C.ell(W + Vector((0, -0.01, -0.18)), (0.05, 0.11, 0.2), segs=8, rings=5)
        A([palm], "Hand" + s, SKIN, "Hand" + s, smooth_angle=70)
        fingers = []
        for k in range(4):
            t = k / 3
            y = -0.09 + 0.18 * t
            L = 1.05 - 0.22 * abs(t - 0.45)
            base = K + Vector((0, y, 0.0))
            j1 = base + Vector((-side * 0.03, y * 0.25, -L * 0.45))
            j2 = base + Vector((-side * 0.1, y * 0.45, -L * 0.8))
            tip = base + Vector((-side * 0.2, y * 0.5, -L))
            fingers.append(ns.tube([base, j1, j2, tip], [0.028, 0.024, 0.02, 0.01], sides=5, resolution=2))
            for jp in (j1, j2):
                fingers.append(C.ell(jp, (0.032, 0.032, 0.035), segs=6, rings=4))
        tb = W + Vector((-side * 0.04, -0.1, -0.12))
        fingers.append(ns.tube([tb, tb + Vector((-side * 0.08, -0.12, -0.3)), tb + Vector((-side * 0.16, -0.14, -0.6))],
                               [0.028, 0.022, 0.01], sides=5, resolution=2))
        A(fingers, "Fingers" + s, SKIN, "Fingers" + s, smooth_angle=70)

    # ---- legs: stilts ---------------------------------------------------------------------
    for s, side in (("L", 1), ("R", -1)):
        x = 0.25 * side
        A([C.capsule((x, 0.03, 4.62), (x, 0.03, 2.48), 0.13, 0.1, verts=8, cap_rings=2)], "Thigh" + s, SUIT, "Thigh" + s,
          smooth_angle=60)
        A(wisps([((x * 1.2, 0.05, 3.4), (0.2, 0.2, 0.6))], 20 + side), "Thigh" + s + "_Haze", HAZE, "Thigh" + s, **haze)
        shin = C.capsule((x, 0.03, 2.45), (x, 0.03, 0.42), 0.09, 0.075, verts=8, cap_rings=2)
        knee = C.ell((x, 0.0, 2.45), (0.12, 0.13, 0.13), segs=8, rings=5)
        A([shin, knee], "Shin" + s, SUIT, "Shin" + s, smooth_angle=60)
        shoe = C.loft([(0.0, 0.12, 0.14, x, 0.12), (0.12, 0.13, 0.2, x, -0.06), (0.26, 0.1, 0.16, x, 0.0),
                       (0.42, 0.07, 0.08, x, 0.03)], verts=10, name="Shoe")
        toe = C.ell((x, -0.4, 0.07), (0.07, 0.3, 0.07), segs=8, rings=5)
        C.deform(toe, lambda v: Vector((v.x, v.y, max(v.z, 0.0))))
        A([shoe, toe], "Foot" + s, SUIT_D, "Foot" + s, smooth_angle=60)


# ======================================================================================
# Clips
# ======================================================================================

ARM_R, ARM_L = C.ARM["R"], C.ARM["L"]
LEGS = [dict(thigh="Thigh" + s, shin="Shin" + s, foot="Foot" + s, ankle=mx(ANKLE, side), side=side,
             phase=ph, sole=[(0.25 * side, 0.16, 0.0), (0.25 * side, -0.66, 0.0)])
        for s, side, ph in (("L", 1, 0.0), ("R", -1, 0.5))]


def walk_clip(sk):
    n = 20

    def extra(u, pose, W):
        tw = -4.0 * math.cos(2 * math.pi * u)
        # stilted: torso rigid, the shade jerks/tilts on each footfall
        pose["Torso"] = (rd(4, 0, -1.2 * tw), None)
        jolt = math.exp(-((u % 0.5) / 0.08) ** 2)      # sharp nod right after each heel strike
        pose["Head"] = (rd(-2 + 7 * jolt, 7 * math.sin(2 * math.pi * u), 0.8 * tw), None)
        for s, side, ph in (("L", 1, 0.0), ("R", -1, 0.5)):
            cs = math.cos(2 * math.pi * (u - ph))
            pose["UpperArm" + s] = (rd(5 * cs, side * -3, 0), None)
            pose["Forearm" + s] = (rd(-4, 0, 0), None)
            pose["Hand" + s] = (rd(0, 0, 0), None)
            pose["Fingers" + s] = (rd(-6 - 6 * max(0, cs), 0, 0), None)

    fn = C.biped_cycle(sk, LEGS, speed=10.0, period=n / C.FPS, duty=0.6, lift=0.42, lift_peak=0.35,
                       hip_height=4.63, bob=0.16, sway=0.05, roll=3.0, twist=4.0, lean=0.0, extra=extra,
                       toe_off=14.0, heel_strike=-8.0)
    return C.sampled_clip(sk, "Walk", n, True, fn, step=1)


def chase_clip(sk):
    n = 18

    def extra(u, pose, W):
        tw = -7.0 * math.cos(2 * math.pi * u)
        pose["Torso"] = (rd(20 + 3 * math.cos(4 * math.pi * u), 0, -1.4 * tw), None)
        pose["Head"] = (rd(-14 + 6 * math.cos(4 * math.pi * (u - 0.1)), 6 * math.sin(2 * math.pi * u), 0.6 * tw), None)
        for s, side, ph in (("L", 1, 0.0), ("R", -1, 0.5)):
            cs = math.cos(2 * math.pi * (u - ph))
            # long arms reaching ahead, clawing alternately
            pose["UpperArm" + s] = (rd(-62 + 14 * cs, side * -8, 0), None)
            pose["Forearm" + s] = (rd(-18 - 10 * max(0, cs), 0, 0), None)
            pose["Hand" + s] = (rd(-12, 0, 0), None)
            pose["Fingers" + s] = (rd(-20 - 22 * max(0, -cs), 0, 0), None)

    fn = C.biped_cycle(sk, LEGS, speed=19.0, period=n / C.FPS, duty=0.38, lift=0.8, lift_peak=0.4,
                       hip_height=4.45, bob=-0.08, sway=0.04, roll=3.0, twist=7.0, lean=8.0, extra=extra,
                       toe_off=24.0, heel_strike=-6.0)
    return C.sampled_clip(sk, "ChaseRun", n, True, fn, step=1)


def idle_clip(sk):
    def base(sw=0.0, head=(0, 0, 0), fl=0.0, fr=0.0, br=0.0):
        p = {"Hips": (rd(0, sw, 0), (0.15 * sw / 3, 0, 0)), "Torso": rd(br, -1.6 * sw, 0),
             "Head": rd(head[0] + 6, head[1], head[2]),
             "UpperArmL": rd(0, -0.8 * sw - 1, 0), "UpperArmR": rd(0, -0.8 * sw + 1, 0),
             "ForearmL": rd(-3, 0, 0), "ForearmR": rd(-3, 0, 0),
             "FingersL": rd(-8 + fl, 0, 0), "FingersR": rd(-8 + fr, 0, 0)}
        C.plant(sk, p)
        return p
    keys = [(0, base()), (30, base(sw=2.5, head=(3, -6, 4), br=1)), (52, base(sw=1.0, head=(6, -12, 8), fl=-25)),
            (56, base(sw=0.8, head=(6, -12, 8), fl=5)), (60, base(sw=0.5, head=(6, -12, 8), fl=-22)),
            (90, base(sw=-2.5, head=(2, 8, -6), br=1, fr=-18)), (104, base(sw=-1.0, head=(1, 4, -3), fr=0)),
            (120, base())]
    return C.clip(sk, "IdleSway", 120, True, keys)


def investigate_clip(sk):
    def base(lean=0.0, head=(0, 0, 0), reach=0.0, fl=0.0):
        return {"Hips": (rd(lean * 0.4, 0, 0), (0, 0.04 * lean, -0.01 * lean)), "Torso": rd(lean, 0, head[2] * 0.3),
                "Head": rd(*head),
                "UpperArmR": rd(-reach, 4, 0), "ForearmR": rd(-reach * 0.8, 0, 0), "HandR": rd(-10, 0, 0),
                "FingersR": rd(-10 + fl, 0, 0), "UpperArmL": rd(2, -2, 0), "FingersL": rd(-10 - fl * 0.5, 0, 0)}

    def pose_with_feet(p):
        C.plant(sk, p)
        return p
    keys = []
    for f, args in ((0, dict(lean=6, head=(10, 0, 0))), (14, dict(lean=12, head=(18, 28, -18), reach=20, fl=-20)),
                    (30, dict(lean=12, head=(20, 34, -24), reach=24, fl=10)),
                    (44, dict(lean=10, head=(14, -10, 10), reach=14, fl=-25)),
                    (62, dict(lean=14, head=(22, -32, 30), reach=22, fl=5)),
                    (76, dict(lean=12, head=(16, -26, 22), reach=18, fl=-15))):
        keys.append((f, pose_with_feet(base(**args))))
    return C.clip(sk, "Investigate", 90, True, keys)


def recoil_clip(sk):
    shield = rd(-20, 0, 0)

    def fn(q):
        pose = {"Hips": (rd(q["hp"], q["shake"] * 0.4, 0), (0, 0.06 * -q["hp"], -0.02 * abs(q["hp"]))),
                "Torso": rd(q["tp"], q["shake"], 0), "Head": rd(q["head"][0], q["head"][1] + q["shake"] * 2, q["head"][2])}
        C.plant(sk, pose)
        W = sk.fk(pose)
        for s, side in (("L", 1), ("R", -1)):
            # forearms cross in front of the shade
            tgt = sk.point(W, "Head", (side * -0.25 + 0.06 * q["shake"], -1.15, 8.05 + side * 0.18))
            C.arm_mix(pose, C.ARM[s], q["w"], lambda P, s=s, side=side, tgt=tgt: C.reach_l(
                sk, P, s, Vector(mx(WRIST, side)) + Vector((0, 0, -0.1)), tgt, shield, (side, 0.3, -1.0)))
            pose["Fingers" + s] = rd(-10 - 40 * q["w"] + q["shake"] * 3, 0, 0)
        return pose
    keys = [(0, dict(hp=0, tp=0, head=(0, 0, 0), w=0.0, shake=0.0), "out"),
            (5, dict(hp=-10, tp=-14, head=(-22, 0, 0), w=1.0), "sine")]
    for i, f in enumerate(range(8, 52, 3)):
        keys.append((f, dict(shake=(2.5 if i % 2 else -2.5), hp=-9, tp=-13), "linear"))
    keys += [(56, dict(shake=0.0, hp=-6, tp=-8, head=(-12, 0, 0)), "sine"),
             (66, dict(w=0.4, hp=-2, tp=-2, head=(-4, 0, 0)), "sine"),
             (75, dict(hp=0, tp=0, head=(0, 0, 0), w=0.0, shake=0.0), "sine")]
    return C.param_clip(sk, "Recoil", 75, False, keys, fn)


def catch_clip(sk):
    def fn(q):
        pose = {"Hips": (rd(q["hp"], 0, 0), q["hl"]), "Torso": rd(q["tp"], 0, 0), "Head": rd(*q["head"])}
        C.plant(sk, pose, {"R": (q["fr"],)})
        for s, side in (("L", 1), ("R", -1)):
            h = Vector(q["hand"])
            h.x *= side
            C.arm_mix(pose, C.ARM[s], q["w"], lambda P, s=s, h=h, side=side: C.reach_l(
                sk, P, s, Vector(mx(WRIST, side)) + Vector((0, 0, -0.2)), h, rd(-15, 0, side * 40), (side, 0.5, -0.4)))
            pose["Fingers" + s] = rd(-8 - q["curl"], side * -0.3 * q["curl"], 0)
        return pose
    keys = [(0, dict(hp=0, hl=(0, 0, 0), tp=0, head=(0, 0, 0), fr=tuple(mx(ANKLE, -1)), hand=(0.9, -1.6, 4.2),
                     w=0.0, curl=0.0), "sine"),
            (8, dict(hp=18, hl=(0, -0.9, -0.5), tp=22, head=(22, 0, 0), fr=(-0.25, -1.3, 0.38), hand=(0.8, -3.0, 3.6),
                     w=1.0, curl=-15), "out"),
            (13, dict(hand=(0.3, -2.9, 3.4), curl=55, head=(30, 8, 0)), "out"),          # fingers close round the victim
            (22, dict(hp=6, hl=(0, -0.6, -0.15), tp=0, hand=(0.28, -2.0, 6.4), head=(34, 10, 0), curl=60), "sine"),
            (40, dict(hand=(0.28, -2.0, 6.5), head=(38, 14, 4), curl=62), "sine"),          # holds it up to the shade
            (50, dict(hp=8, hl=(0, -0.5, -0.2), tp=6, hand=(0.6, -1.6, 4.4), head=(10, 0, 0), curl=10), "sine"),
            (62, dict(hp=0, hl=(0, 0, 0), tp=0, head=(0, 0, 0), fr=tuple(mx(ANKLE, -1)), hand=(0.9, -1.0, 3.6),
                      w=0.0, curl=0.0), "sine")]
    return C.param_clip(sk, "Catch", 62, False, keys, fn)


def dissolve_clip(sk):
    def fn(q):
        sink = q["sink"]
        pose = {"Hips": (rd(q["hp"], q["roll"], 0), (0, 0, -sink)), "Torso": rd(q["tp"], -q["roll"], 0),
                "Head": rd(q["head"][0], q["head"][1], q["head"][2])}
        # knees buckle; feet sink with the body once it starts going under
        fz = 0.38 - max(0.0, sink - 2.2)
        C.plant(sk, pose, {"L": ((0.32, 0.1, fz),), "R": ((-0.32, -0.05, fz),)})
        for s, side in (("L", 1), ("R", -1)):
            pose["UpperArm" + s] = rd(-q["flail"] * (1.0 if s == "L" else 0.8), -side * q["spread"], 0)
            pose["Forearm" + s] = rd(-q["flail"] * 0.5, 0, 0)
            pose["Fingers" + s] = rd(-10 - q["curl"], 0, 0)
        return pose
    keys = [(0, dict(hp=0, tp=0, head=(0, 0, 0), sink=0.0, roll=0, flail=0, spread=0, curl=0), "out"),
            (6, dict(tp=-18, head=(-40, 6, 0), flail=150, spread=30, curl=50, hp=-6), "linear"),   # shriek
            (10, dict(head=(-36, -8, 4), flail=140, spread=40, roll=4), "linear"),
            (14, dict(head=(-42, 8, -4), flail=155, spread=25, roll=-4), "linear"),
            (18, dict(head=(-38, -6, 2), flail=145, spread=35, roll=3), "in"),
            (30, dict(hp=24, tp=30, head=(30, 14, 0), sink=1.8, roll=6, flail=40, spread=50, curl=70), "in"),  # buckles
            (48, dict(hp=34, tp=36, head=(40, 20, 6), sink=6.0, roll=10, flail=20, spread=60, curl=80), "in"),
            (62, dict(sink=10.5, head=(50, 24, 8)), "sine"),
            (66, dict(sink=10.6), "sine")]
    return C.param_clip(sk, "Dissolve", 66, False, keys, fn)


# ======================================================================================

def build():
    sk = C.Skel("LightsOutRig", JOINTS)
    build_model(sk)
    acts = [idle_clip(sk), walk_clip(sk), investigate_clip(sk), chase_clip(sk), recoil_clip(sk), catch_clip(sk),
            dissolve_clip(sk)]
    S = SCALE
    C.rescale(sk, acts, S)
    C.rest_pose(sk.arm)

    def checks():
        for a, v in ((acts[1], 10.0 * S), (acts[3], 19.0 * S)):
            for s, side in (("L", 1), ("R", -1)):
                for nm, pt in (("heel", (0.25 * side * S, 0.16 * S, 0.0)), ("toe", (0.25 * side * S, -0.66 * S, 0.0))):
                    print(f"  [slide] {a.name} Foot{s} {nm}: {C.foot_slide(sk, a, 'Foot' + s, pt, v)}")
        for a in acts[:-1]:
            print(f"  [floor] {a.name}: lowest point {C.lowest_point(sk, a)}")
        import bpy
        arm = sk.arm
        objs = ns._tagged_objects()
        for a in acts:
            C.set_action(arm, a)
            top, at = -1e9, None
            for f in range(a["ns_start"], a["ns_end"] + 1):
                bpy.context.scene.frame_set(f)
                z = max((o.matrix_world @ v.co).z for o in objs for v in o.data.vertices)
                if z > top:
                    top, at = z, f
            print(f"  [height] {a.name}: highest point {top:.2f} (frame {at})")
        C.set_action(arm, acts[-1])
        bpy.context.scene.frame_set(acts[-1]["ns_end"])
        top = max((o.matrix_world @ v.co).z for o in ns._tagged_objects() for v in o.data.vertices)
        print(f"  [dissolve] highest point at the end: {top:.2f} (must be < 0)")
        bpy.context.scene.frame_set(0)

    meta = {
        "root": {"center": [0, round(4.65 * S, 3), round(-0.03 * S, 3)],
                 "size": [round(1.6 * S, 3), round(2.2 * S, 3), round(1.0 * S, 3)]},
        "scale": S,
        "walkSpeed": 10, "investigateSpeed": 13, "chaseSpeed": 19,
        "clipSpeedRef": {"Walk": round(10 * S, 3), "ChaseRun": round(19 * S, 3)},
        "terminal": ["Dissolve"],
        "glow": {"role": "glow", "lit": {"color": "#FFE9A8", "material": "Neon"},
                 "note": "the bulb: light it when a flashlight hits (recoil); dead = default colour"},
        "events": {"Recoil": {"shield": 0.17, "lower": 1.87}, "Catch": {"grab": 0.43, "lift": 0.73},
                   "Dissolve": {"shriek": 0.2, "gone": 2.07}},
    }
    return {"skel": sk, "arm": sk.arm, "actions": acts, "checks": [checks],
            "export": {"rig": sk.arm, "pivot": (0.0, 0.0, 0.0), "meta": meta}}


STRIPS = {
    "IdleSway": dict(frames=[0, 30, 56, 90]),
    "Walk": dict(frames=[0, 5, 10, 15]),
    "Investigate": dict(frames=[0, 14, 44, 62]),
    "ChaseRun": dict(frames=[0, 4, 9, 13]),
    "Recoil": dict(frames=[0, 5, 30, 66], yaw=-40),
    "Catch": dict(frames=[8, 13, 22, 40]),
    "Dissolve": dict(frames=[6, 14, 30, 48]),
}

if __name__ == "__main__":
    C.run(build, "Creature_LightsOut", "LightsOut", strips=STRIPS)
