"""Character_Human — the shared rigid-part human rig every customer, Regular and the Copy use.

Chunky, friendly, slightly tired night-shift person (~5.1 studs to the top of the skull).
Bones (all +Y, roll 0): Hips (root, child of the HumanoidRootPart) > Torso > Head, ArmL >
HandL, ArmR > HandR; Hips > LegL, LegR (shoes are parts of the leg bones).
Runtime roles: skin (head, hands), top (shirt + sleeves), pants (hips + legs), shoes,
eye (eye whites, scale them for the Copy's "too wide" tell), eyelid (closed-lid caps,
export Transparency 1; show them to blink), brow (may be tinted to the hair colour).
Sockets (rest pose, CFrame attributes on the Model): HatSocket, HairSocket, FaceSocket
(-> weld to Head) and TorsoSocket (-> weld to Torso); see meta.socketBones.
Clips (anim/Human.lua): Idle, Walk, Wave, Happy, Upset, Sit, Eat, EatStand, Shriek, ChaseRun.
EatStand (the Copy eating at the counter) fires meta.events.EatStand.bite at 1.0 s.

NS_STRIPS=all|none|Walk,Sit,...  selects which pose strips to render (default all).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

VIEWS = {"Wave": (-20, -95), "Shriek": (-25, 90), "EatStand": (-35, 90)}     # default (-60, 90): 3/4 front + left side
STRIPS = {
    "Idle": ([0, 18, 40, 64, 90, 108], 0.0, False),
    "Walk": ([0, 4, 7, 10, 14, 18, 21, 24], C.WALK_SPEED, False),
    "Wave": ([0, 6, 9, 13, 17, 25, 38, 46], 0.0, False),
    "Happy": ([0, 5, 8, 11, 14, 17, 22, 27, 40], 0.0, False),
    "Upset": ([0, 7, 12, 18, 24, 30, 42, 54], 0.0, False),
    "Sit": ([0, 24, 62, 84], 0.0, True),
    "Eat": ([0, 10, 16, 22, 28, 40, 60], 0.0, True),
    "EatStand": ([0, 12, 24, 30, 36, 44, 52, 66], 0.0, False),
    "Shriek": ([0, 4, 6, 12, 20, 30, 32, 40, 50], 0.0, False),
    "ChaseRun": ([0, 3, 5, 7, 9, 10, 13, 15, 17], C.CHASE_SPEED, False),
}


def build():
    arm = C.make_rig()
    C.build_body(arm)
    acts = C.build_actions(arm)
    return {"arm": arm, "actions": acts,
            "export": {"rig": arm, "pivot": (0.0, 0.0, 0.0), "meta": C.base_meta(),
                       "sockets": C.socket_spec()}}


def strips(arm, acts, which):
    paths = []
    for act in acts:
        if which != "all" and act.name not in which:
            continue
        frames, speed, seated = STRIPS[act.name]
        props = C.booth_proxy() if seated else []
        paths.append(C.pose_strip(arm, act, frames, act.name, speed=speed, props=props,
                                  views=VIEWS.get(act.name, (-60, 90))))
        for o in props:
            C.bpy.data.objects.remove(o, do_unlink=True)
    return paths


if __name__ == "__main__":
    out = ns.run_main(build, "Character_Human", C.BATCH, C.GROUP)
    which = os.environ.get("NS_STRIPS", "all")
    if which != "none":
        which = which if which == "all" else which.split(",")
        for p in strips(out["arm"], out["actions"], which):
            print("[Character_Human] strip:", p)
    if os.environ.get("NS_EXPORT") == "1":
        print("[Character_Human] anim:", ns.export_animations(out["arm"], C.RIG_NAME, out["actions"]))
