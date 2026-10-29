"""Cosmetic_Spatula_Pan — the Frying Pan spatula skin: a chunky cast-iron skillet held by its
long handle, with two pour spouts, a helper lug opposite the handle, a hang hole and a
leather wrap over the grip.

Held in the right hand: pivot = grip point (middle of the wrapped handle) at the origin, the
pan points along Blender -Y with its cooking side up (+Z). Pan 1.0 across, total reach 1.95.
Roles: Pan (skillet, handle, lug) = cos_body (Metal); Wrap (handle sleeve) = cos_trim.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
PAN_Y = -0.92          # pan centre
PAN_R = 0.50
FLOOR = -0.15
RIM = 0.035


def skillet():
    prof = [(0.0, FLOOR), (0.40, FLOOR), (0.455, FLOOR + 0.035), (PAN_R, RIM - 0.005), (PAN_R + 0.004, RIM + 0.01),
            (PAN_R - 0.035, RIM + 0.012), (0.43, FLOOR + 0.05), (0.38, FLOOR + 0.035), (0.0, FLOOR + 0.035)]
    o = ns.lathe(prof, verts=24, name="Skillet")
    ns.apply_all(o)
    # pour spouts on the left and right rim: pull the rim out and down a touch
    for v in o.data.vertices:
        r = math.hypot(v.co.x, v.co.y)
        if r > 0.44 and v.co.z > 0.0:
            a = math.atan2(v.co.y, v.co.x)
            k = max(math.cos(a) ** 2, 0.0) ** 6          # around +-X only
            v.co.x *= 1 + 0.09 * k
            v.co.y *= 1 + 0.09 * k
            v.co.z -= 0.012 * k
    o.location = (0, PAN_Y, 0)
    ns.apply_all(o)
    return o


def build():
    dc = C.default_colours("Spatula_Pan")
    # cast handle: flattened lathe along Y from the pan wall back past the grip
    hp = [(0.0, 0.47), (0.05, 0.47), (0.068, 0.44), (0.066, 0.34), (0.052, 0.0), (0.06, -0.3), (0.085, -0.42),
          (0.0, -0.42)]
    handle = ns.lathe(hp, verts=8, name="Handle")
    handle.scale = (1.0, 0.62, 1.0)
    handle.rotation_euler = (math.radians(90) - 0.06, 0, 0)
    handle.location = (0, 0, 0.0)
    ns.apply_all(handle)
    ns.boolean(handle, ns.cyl(0.028, 0.3, loc=(0, 0.39, 0.02), verts=8, bevel=0.0))
    lug = ns.box((0.22, 0.12, 0.035), loc=(0, PAN_Y - PAN_R - 0.04, RIM - 0.01), bevel=0.015, segments=1)
    ns.boolean(lug, ns.box((0.12, 0.05, 0.2), loc=(0, PAN_Y - PAN_R - 0.055, 0), bevel=0.0))
    C.part([skillet(), handle, lug], "Pan", dc["body"], "Metal", recolor="cos_body", smooth_angle=45)

    wrap = ns.lathe([(0.0, 0.31), (0.06, 0.31), (0.072, 0.29), (0.07, 0.0), (0.075, -0.22), (0.062, -0.24),
                     (0.0, -0.24)], verts=8, name="Wrap")
    wrap.scale = (1.0, 0.7, 1.0)
    wrap.rotation_euler = (math.radians(90) - 0.06, 0, 0)
    ns.apply_all(wrap)
    # stitched seam ridge along the underside of the wrap
    seam = C.rod((0, 0.29, -0.052), (0, -0.22, -0.048), 0.012, verts=4)
    C.part([wrap, seam], "Wrap", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=55)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Spatula_Pan", "Spatula")
