"""Cosmetic_Spatula_Bone — the Bone Spatula skin (spooky-cute): a cartoon bone handle with
knobbly bone ends, an offset bone neck, and a slotted spatula head shaped like a little skull
whose slots are its eyes, nose and teeth.

Held in the right hand: pivot = grip point (middle of the bone handle) at the origin, the
head points along Blender -Y, blade face up (+Z); the skull's crown is at the tip and its jaw
toward the handle, so it reads upright when the spatula is raised. Reach ~1.9.
Roles: Bone (handle, knobs, neck, skull head) = cos_body (single-colour item).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
Y_END, Y_NECK = 0.40, -0.30
HEAD_Z = -0.15
T = 0.045


def skull_outline():
    """Top-view outline: rounded crown at the tip (-Y), cheekbones, narrower jaw at the neck."""
    pts = []
    cy, r = -1.12, 0.31
    for i in range(13):                                   # crown: from the right cheek round the tip
        a = math.radians(-10 - 160 * i / 12)
        pts.append((r * math.cos(a), cy + r * math.sin(a) * 1.05))
    pts += [(-0.30, -1.06), (-0.27, -0.88), (-0.18, -0.80), (-0.17, -0.70), (-0.12, -0.64), (-0.06, -0.62),
            (0.06, -0.62), (0.12, -0.64), (0.17, -0.70), (0.18, -0.80), (0.27, -0.88), (0.30, -1.06)]
    return C.ccw(pts)


def build():
    dc = C.default_colours("Spatula_Bone")
    parts = []
    # bone shaft: waisted, slightly flattened
    shaft = ns.lathe([(0.0, Y_NECK), (0.06, Y_NECK), (0.072, Y_NECK + 0.06), (0.058, -0.12), (0.055, 0.1),
                      (0.06, Y_END - 0.08), (0.075, Y_END - 0.03), (0.0, Y_END)], verts=10, name="Shaft")
    shaft.scale = (1.0, 0.85, 1.0)
    shaft.rotation_euler = (math.radians(-90), 0, 0)      # +Z -> +Y
    parts.append(shaft)
    for y, r, dx in ((Y_END + 0.02, 0.085, 0.068), (Y_NECK - 0.01, 0.07, 0.056)):
        for s in (-1, 1):
            parts.append(ns.sphere(r, loc=(s * dx, y, 0), scale=(1, 1, 0.82), segs=8, rings=5))
    # offset neck from the bone end down to the skull's jaw
    parts.append(C.cord("Neck", [(0, Y_NECK - 0.05, -0.01), (0, Y_NECK - 0.2, -0.06), (0, -0.62, HEAD_Z + 0.01)],
                        0.05, sides=6, per_seg=2, radii=[0.056, 0.047, 0.05]))
    # skull head with eye, nose and teeth slots
    head = C.extrude(skull_outline(), T, plane="XY", offset=HEAD_Z - T / 2, name="Skull")
    ns.apply_all(head)
    for sx in (-1, 1):
        ns.boolean(head, ns.cyl(0.085, 0.3, loc=(sx * 0.12, -1.05, HEAD_Z), verts=12, bevel=0.0))
    nose = C.extrude(C.ccw([(0.0, -0.955), (0.052, -0.855), (-0.052, -0.855)]), 0.3, plane="XY", offset=HEAD_Z - 0.15)
    ns.boolean(head, nose)
    for x in (-0.085, 0.0, 0.085):
        ns.boolean(head, ns.box((0.032, 0.09, 0.3), loc=(x, -0.72, HEAD_Z), bevel=0.0))
    ns.bevel(head, width=0.012, segments=1, angle=40)
    parts.append(head)
    C.part(parts, "Bone", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=45)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Spatula_Bone", "Spatula")
