"""Shop_BoxStack — stack of five cardboard boxes in the pantry / back hall.

Two big boxes side by side at the bottom, a wide "BUNS" box across them (stencilled black
letters + "this side up" arrows), an open box on top with its flaps splayed out, and a
small taped box on the free corner. Tape strips run over the top seams and down the
front faces. Boxes collide. Front faces -Y, pivot = bottom-centre. ~3.4 x 4.0 x 2.6.
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

    # bottom row (same height so the BUNS box sits level)
    add(CB_MID, C.carton(1.8, 2.4, 1.5, loc=(-0.8, 0.05, 0), yaw=-2))
    add(CB_DARK, C.carton(1.5, 2.2, 1.5, loc=(0.92, -0.02, 0), yaw=3))
    # middle: the BUNS box spanning both
    zc = 1.5
    add(CB_LIGHT, C.carton(2.25, 2.0, 1.3, loc=(-0.25, 0.1, zc), yaw=4, tape=True))
    # top: open box, flaps splayed
    add(CB_MID, C.carton(1.35, 1.3, 0.95, loc=(-0.45, 0.25, zc + 1.3), yaw=-9, open_top=True, flap_angle=112))
    # small box on the free corner of the right bottom box
    add(CB_DARK, C.carton(0.7, 0.85, 0.55, loc=(1.28, -0.55, 1.5), yaw=-6))

    for col, objs in groups.items():
        C.part(objs, {CB_LIGHT: "BoxesLight", CB_MID: "Boxes", CB_DARK: "BoxesDark"}[col], col, can_collide=True,
               smooth_angle=30)
    C.part(tape, "Tape", C.TAPE, smooth_angle=30)
    C.part(inside, "Inside", INSIDE, "Fabric", smooth_angle=None)   # matte: no sky glint inside

    # BUNS stencil + "this side up" arrows on the middle box front, built in the box's local
    # frame (front face y = -1.0) and moved with the same transform as the box
    fy = -1.0 - 0.009
    stencil = [C.text("BUNS", 0.5, 0.01, (0, fy + 0.005, 0.6), width=1.3, res=1, spacing=1.12, flat=True)]
    for ax in (-0.86, 0.86):
        stencil.append(C.strip_xz((ax, 0.42), (ax, 0.66), 0.07, fy))
        stencil.append(C.face_dir(C.poly([(ax - 0.12, fy, 0.64), (ax + 0.12, fy, 0.64), (ax, fy, 0.82)]), "-Y"))
    C.place(stencil, loc=(-0.25, 0.1, zc), yaw=4)
    C.part(stencil, "Stencil", STENCIL, smooth_angle=None)
    # white shipping label with printed lines on the bottom-left box front (local frame, yaw -2)
    ly = -1.2 - 0.009
    label = [C.quad_xz(0.12, 0.74, 0.62, 1.08, ly)]
    lines = [C.quad_xz(0.2, 0.2 + w, z, z + 0.045, ly - 0.006) for z, w in ((0.94, 0.46), (0.84, 0.32), (0.74, 0.4))]
    C.place(label + lines, loc=(-0.8, 0.05, 0), yaw=-2)
    C.part(label, "Label", C.PAPER, smooth_angle=None)
    C.part(lines, "LabelInk", STENCIL, smooth_angle=None)


META = {"collide": "box bodies collide; tape/stencil do not"}

if __name__ == "__main__":
    C.run(build, "Shop_BoxStack", budget=600, meta=META)
