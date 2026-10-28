"""Creature_Nibbler — chubby rat with glowing eyes (pipeline-gate asset #3, rig + clips).

Rigid-part rig. Bones: Body (root), Head, Tail, LegFL, LegFR, LegBL, LegBR.
Every bone points +Y with zero roll, so bone-local Euler keys read as world axes:
X = pitch, Y = roll, Z = yaw. The creature faces Blender -Y (Roblox LookVector).
Clips: Idle (loop 2.0 s), Scurry (loop 0.6 s, authored for 8 studs/s).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import nslib as ns  # noqa: E402

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

    return {"arm": arm, "actions": [idle, scurry],
            "export": {"rig": arm, "pivot": PIVOT,
                       "meta": {"root": {"center": [0, 0.36, 0.0], "size": [0.6, 0.5, 0.84]},
                                "walkSpeed": 8, "clipSpeedRef": {"Scurry": 8}}}}


if __name__ == "__main__":
    out = ns.run_main(build, "Creature_Nibbler", "gate", "Creatures")
    prev_dir = os.path.join(ns.REPO, "..", "previews", "gate")
    for act, frames in ((out["actions"][1], [0, 4, 9, 13]), (out["actions"][0], [0, 12, 36, 48])):
        print("[Creature_Nibbler] strip:", ns.render_pose_strip(out["arm"], act, frames, f"Nibbler_{act.name}", prev_dir))
    if os.environ.get("NS_EXPORT") == "1":
        print("[Creature_Nibbler] anim:", ns.export_animations(out["arm"], "Nibbler", out["actions"]))
