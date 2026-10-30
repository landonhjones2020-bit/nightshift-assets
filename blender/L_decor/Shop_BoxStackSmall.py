"""Shop_BoxStackSmall — small stack of cardboard boxes (variant of Shop_BoxStack).

A wide taped "CUPS" box with "this side up" arrows, an open box on top with its flaps
splayed out, and a flat taped box leaning against the side. Boxes collide. Front faces
-Y, pivot = bottom-centre. ~2.5 x 2.0 x 2.0.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
CB_LIGHT = "#C49B69"
CB_MID = C.CARDBOARD
CB_DARK = "#A47A4E"
INSIDE = "#33271C"
STENCIL = "#2A2622"


def build():
    groups = {CB_LIGHT: [], CB_MID: [], CB_DARK: []}
    tape, inside = [], []

    def add(col, d):
        groups[col] += d["body"] + d["flaps"]
        tape.extend(d["tape"])
        inside.extend(d["inside"])

    add(CB_LIGHT, C.carton(1.95, 1.75, 1.2, loc=(-0.12, 0.05, 0), yaw=2))
    add(CB_DARK, C.carton(1.15, 1.05, 0.72, loc=(-0.25, 0.15, 1.2), yaw=-11, open_top=True, flap_angle=108))
    # flat box leaning on the big box's right side: it stands on its wall-side bottom edge
    # (x = 0 locally), top tipped toward -X until its inner top corner meets the box face
    phi = C.math.radians(14)
    fb = ns.box((0.36, 1.25, 1.05), loc=(0.18, 0, 0.525), bevel=0.03, segments=1)
    ns.apply_all(fb)
    fb.rotation_euler = (0, -phi, 0)
    x_face = -0.12 + 1.95 / 2 + 0.035          # big box right face (+ its 2 degree turn)
    fb.location = (x_face + 1.05 * C.math.sin(phi), -0.05, 0.0)
    ns.apply_all(fb)
    groups[CB_MID].append(fb)

    for col, objs in groups.items():
        if objs:
            C.part(objs, {CB_LIGHT: "BoxesLight", CB_MID: "Boxes", CB_DARK: "BoxesDark"}[col], col, can_collide=True,
                   smooth_angle=30)
    C.part(tape, "Tape", C.TAPE, smooth_angle=30)
    C.part(inside, "Inside", INSIDE, "Fabric", smooth_angle=None)

    # CUPS stencil + arrows on the big box front (local frame, front face y = -0.875)
    fy = -0.875 - 0.009
    stencil = [C.text("CUPS", 0.38, 0.01, (0, fy + 0.005, 0.52), width=1.0, res=1, spacing=1.12, flat=True)]
    for ax in (-0.72, 0.72):
        stencil.append(C.strip_xz((ax, 0.36), (ax, 0.56), 0.06, fy))
        stencil.append(C.face_dir(C.poly([(ax - 0.1, fy, 0.55), (ax + 0.1, fy, 0.55), (ax, fy, 0.7)]), "-Y"))
    C.place(stencil, loc=(-0.12, 0.05, 0), yaw=2)
    C.part(stencil, "Stencil", STENCIL, smooth_angle=None)


META = {"collide": "box bodies collide; tape/stencil do not", "variant_of": "Shop_BoxStack"}

if __name__ == "__main__":
    C.run(build, "Shop_BoxStackSmall", budget=600, meta=META)
