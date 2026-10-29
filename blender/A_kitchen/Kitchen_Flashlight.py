"""Kitchen_Flashlight — the chunky work flashlight every player carries (F / Y / touch).

Held tool: pivot = grip point (middle of the body) at the origin; the beam points along
Blender -Y (Roblox -Z = LookVector). Mustard body with black rubber grip rings and tail cap,
a flared head with a chrome bezel, a rubber thumb switch on top and a Neon lens (role
lens: the client dims it with the battery / turns it off). Body carries role
flashlight_body so cosmetic skins can recolour it.

Sockets: Beam = lens centre, yaw 0 (attach the SpotLight here). Meta grip as on the spatula.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
LENS_COL = "#FFF1C4"
# profile along the beam axis: z grows toward the head (rot X +90 sends +Z to -Y)
Z_TAIL, Z_HEAD = -0.62, 0.68


def lay(obj):
    obj.rotation_euler = (1.5708, 0, 0)
    return obj


def build():
    body = lay(ns.lathe([(0.0, -0.5), (0.135, -0.5), (0.135, 0.2), (0.15, 0.27), (0.21, 0.42), (0.225, 0.47),
                         (0.225, 0.6), (0.0, 0.6)], verts=14, name="Body"))
    C.part(body, "Body", C.MUSTARD, "SmoothPlastic", recolor="flashlight_body", smooth_angle=50)

    rubber = [lay(ns.lathe([(0.0, Z_TAIL), (0.13, Z_TAIL), (0.15, Z_TAIL + 0.03), (0.15, -0.49), (0.0, -0.49)], verts=14, name="Tail"))]
    for z in (-0.32, -0.16, 0.0):
        rubber.append(lay(ns.lathe([(0.134, z - 0.045), (0.152, z - 0.03), (0.152, z + 0.03), (0.134, z + 0.045)], verts=14, name="Ring")))
    # thumb switch on top of the body, just behind the head
    rubber.append(ns.box((0.13, 0.18, 0.08), loc=(0, -0.12, 0.155), bevel=0.035, segments=1))
    # lanyard loop on the tail
    rubber.append(ns.torus(0.07, 0.018, loc=(0, -Z_TAIL + 0.06, 0), rot=(0, 90, 0), major_segs=10, minor_segs=4))
    C.part(rubber, "Rubber", C.RUBBER, "SmoothPlastic", smooth_angle=50)

    bezel = lay(ns.lathe([(0.19, 0.58), (0.24, 0.58), (0.245, 0.62), (0.235, Z_HEAD), (0.19, Z_HEAD), (0.19, 0.64)],
                         verts=14, name="Bezel"))
    C.part(bezel, "Bezel", C.STAINLESS, "Metal", smooth_angle=50)
    lens = lay(ns.lathe([(0.0, 0.6), (0.195, 0.6), (0.195, 0.655), (0.0, 0.665)], verts=14, name="Lens"))
    C.part(lens, "Lens", LENS_COL, "Neon", recolor="lens", cast_shadow=False, smooth_angle=50)

    meta = {"grip": {"point": [0, 0, 0], "forward": [0, 0, -1], "up": [0, 1, 0]}, "tool": True}
    sockets = {"Beam": ((0, -0.665, 0), 0)}
    return {"export": {"meta": meta, "sockets": sockets, "pivot": (0, 0, 0)}}


if __name__ == "__main__":
    C.run(build, "Kitchen_Flashlight")
