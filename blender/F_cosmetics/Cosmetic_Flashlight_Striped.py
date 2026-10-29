"""Cosmetic_Flashlight_Striped — Candy Stripe: the flashlight with bold candy-cane spiral bands
wound flush around the whole body (no rubber rings), striped like a peppermint stick.

Held in the left hand: pivot = grip point at the origin, the beam points along Blender -Y,
the thumb switch on top. The body is one twisted lathe surface split by columns, so the
stripes are exact spirals with no extra geometry.
Roles: Body = cos_body; Stripes, Grip (tail cap, switch, lanyard) and Bezel = cos_trim;
Lens = cos_beam (Neon).
Sockets: Beam = lens centre, yaw 0 (pointing -Y).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import Cosmetic_Flashlight as F  # noqa: E402

ns = C.ns
V = 16
TURNS_PER_STUD = 1.15
PROFILE = [(0.135, z / 10) for z in range(-5, 3)] + [(0.15, 0.27), (0.18, 0.345), (0.21, 0.42), (0.225, 0.47),
                                                     (0.225, 0.535), (0.225, 0.6)]


def body_split():
    verts, body_f, stripe_f = [], [], []
    for r, z in PROFILE:
        tw = 2 * math.pi * TURNS_PER_STUD * z
        for i in range(V):
            a = 2 * math.pi * i / V + tw
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for k in range(len(PROFILE) - 1):
        for i in range(V):
            j = (i + 1) % V
            q = (k * V + i, k * V + j, (k + 1) * V + j, (k + 1) * V + i)
            (stripe_f if (i // 2) % 2 == 0 else body_f).append(q)
    body_f.append(tuple(reversed(range(V))))
    last = (len(PROFILE) - 1) * V
    body_f.append(tuple(last + i for i in range(V)))
    body, stripes = C.split_mesh(["Body", "Stripes"], verts, [body_f, stripe_f])
    return F.lay(body), F.lay(stripes)


def build():
    dc = C.default_colours("Flashlight_Striped")
    body, stripes = body_split()
    C.part(body, "Body", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=50)
    C.part(stripes, "Stripes", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=50)
    C.part(F.tail_parts(), "Grip", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=50)
    bezel, lens = F.head_parts()
    C.part(bezel, "Bezel", dc["trim"], "Metal", recolor="cos_trim", smooth_angle=50)
    C.part(lens, "Lens", "#FFF1C4", "Neon", recolor="cos_beam", cast_shadow=False, smooth_angle=50)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Flashlight_Striped", "Flashlight", sockets={"Beam": ((0, -F.LENS_Z, 0), 0)})
