"""Review renders for the class cast (not an asset).

  python blender/D_characters/_classes_review.py [ids,comma,separated] [frame]
      -> previews/D_characters/_classes_lineup.png (front) and _classes_lineup34.png (3/4)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import _classes as K  # noqa: E402
import _lineup as LU  # noqa: E402

ns = C.ns
bpy = C.bpy
Vector = C.Vector


def lineup(ids, frame=0, gap=3.5, samples=16):
    ns.reset()
    xs = [(i - (len(ids) - 1) / 2) * gap for i in range(len(ids))]
    rigs = []
    for cid, x in zip(ids, xs):
        C.reset_caches()
        arm = C.make_rig("Rig_" + cid)
        act = K.build_class(arm, cid)
        arm.location.x = x
        rigs.append((arm, act))
    for arm, act in rigs:
        arm.animation_data.action = act
        if hasattr(arm.animation_data, "action_slot") and len(act.slots):
            arm.animation_data.action_slot = act.slots[0]
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    lo, hi = Vector((xs[0] - 1.7, -1.2, 0)), Vector((xs[-1] + 1.7, 1.0, 6.4))
    out = []
    for name, yaw, pitch in (("_classes_lineup", 0, 6), ("_classes_lineup34", -24, 10)):
        p = os.path.join(C.PREV, name + ".png")
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("Cam", "Key", "Fill", "Rim", "Plane")):
                bpy.data.objects.remove(o, do_unlink=True)
        LU.render(p, lo, hi, yaw=yaw, pitch=pitch, w=2400, h=860, samples=samples, fov=24)
        span = (hi.x - lo.x) * 1.08
        LU.label(p, [K.TITLES[c] for c in ids], [0.5 + x / span for x in xs])
        out.append(p)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[sys.argv.index("--") + 1:]] if "--" in sys.argv else sys.argv[1:]
    ids = args[0].split(",") if args and args[0] != "all" else K.ORDER
    frame = int(args[1]) if len(args) > 1 else 0
    os.makedirs(C.PREV, exist_ok=True)
    print("[classes]", lineup(ids, frame))
