"""Cosmetic_Flashlight — the flashlight skin mesh (Standard, Chrome Beam, Red Alert, Midnight,
Ghost Glow, Neon): the same chunky design as Kitchen_Flashlight, split into recolour roles.

Held in the left hand: pivot = grip point (middle of the body) at the origin, the beam points
along Blender -Y (Roblox -Z = the grip attachment's LookVector), the thumb switch on top (+Z).
Roles: Body = cos_body; Grip (rubber rings, tail cap, switch, lanyard loop) and Bezel (lens
rim, Metal) = cos_trim; Lens = cos_beam (Neon).
Sockets: Beam = lens centre, yaw 0 (pointing -Y; attach the SpotLight here).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
Z_TAIL, Z_HEAD = -0.62, 0.68     # profile along the beam axis (rot X +90 sends +Z to -Y)
LENS_Z = 0.665


def lay(obj):
    obj.rotation_euler = (1.5708, 0, 0)
    return obj


def head_parts():
    """Bezel and lens shared with the striped skin. Returns (bezel, lens)."""
    bezel = lay(ns.lathe([(0.19, 0.58), (0.24, 0.58), (0.245, 0.62), (0.235, Z_HEAD), (0.19, Z_HEAD), (0.19, 0.64)],
                         verts=14, name="Bezel"))
    lens = lay(ns.lathe([(0.0, 0.6), (0.195, 0.6), (0.195, 0.655), (0.0, LENS_Z)], verts=14, name="Lens"))
    return bezel, lens


def tail_parts():
    """Tail cap, thumb switch and lanyard loop (trim). Returns a list of objects."""
    out = [lay(ns.lathe([(0.0, Z_TAIL), (0.13, Z_TAIL), (0.15, Z_TAIL + 0.03), (0.15, -0.49), (0.0, -0.49)], verts=14,
                        name="Tail"))]
    out.append(ns.box((0.13, 0.18, 0.08), loc=(0, -0.12, 0.155), bevel=0.035, segments=1))
    out.append(ns.torus(0.07, 0.018, loc=(0, -Z_TAIL + 0.06, 0), rot=(0, 90, 0), major_segs=10, minor_segs=4))
    return out


def build():
    dc = C.default_colours("Flashlight")
    body = lay(ns.lathe([(0.0, -0.5), (0.135, -0.5), (0.135, 0.2), (0.15, 0.27), (0.21, 0.42), (0.225, 0.47),
                         (0.225, 0.6), (0.0, 0.6)], verts=14, name="Body"))
    C.part(body, "Body", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=50)
    grip = tail_parts()
    for z in (-0.32, -0.16, 0.0):
        grip.append(lay(ns.lathe([(0.134, z - 0.045), (0.152, z - 0.03), (0.152, z + 0.03), (0.134, z + 0.045)],
                                 verts=14, name="Ring")))
    C.part(grip, "Grip", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=50)
    bezel, lens = head_parts()
    C.part(bezel, "Bezel", dc["trim"], "Metal", recolor="cos_trim", smooth_angle=50)
    C.part(lens, "Lens", "#FFF1C4", "Neon", recolor="cos_beam", cast_shadow=False, smooth_angle=50)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Flashlight", "Flashlight", sockets={"Beam": ((0, -LENS_Z, 0), 0)})
