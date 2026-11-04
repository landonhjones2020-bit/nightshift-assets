"""Basement_PipeCorner — the ceiling pipe bundle turning 90 degrees.

The same three pipes as Basement_PipeRun (grey, copper, dark grey; _common.BUNDLE) come in
along the -X arm, sweep round a concentric bend (centre-line radius 0.7) and leave along
the -Y arm. Each arm is 4 long from the corner point and has one trapeze hanger 2 from it,
so with PipeRuns attached the hangers stay 4 apart; half-couplings at both arm ends meet
the runs' half-couplings.
PIVOT = the CORNER POINT on the ceiling plane: where the two bundle centre lines meet,
z = 0 (everything hangs below). Sockets give the pivot CFrame of the PipeRun that
continues each arm (pipe order matched): RunX = (-8, 0, 0) yaw 0, RunY = (0, -8, 0) yaw -90
(Blender coordinates). Rotate the corner in 90-degree steps for the other turns. No
collision. 4.5 x 0.9 x 4.5.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
A = 4.0          # arm length from the corner point
RB = 0.7         # bend radius of the bundle centre line
COLLAR = 0.13


def path(off, z, n=6):
    """Centre line of the pipe at lateral offset `off` (left of travel = outside of this right turn)."""
    pts = [(-A + 0.02, off, z), (-RB, off, z)]
    rr = RB + off
    for i in range(1, n):
        a = math.radians(90.0 - 90.0 * i / n)
        pts.append((-RB + rr * math.cos(a), -RB + rr * math.sin(a), z))
    pts += [(off, -RB, z), (off, -A + 0.02, z)]
    return pts


def build():
    for off, r, col, name in C.BUNDLE:
        z = C.bundle_z(r)
        objs = [C.pipe(path(off, z), r, sides=8)]
        objs.append(ns.cyl(r + 0.035, COLLAR, loc=(-A + COLLAR / 2, off, z), rot=(0, 90, 0), verts=8, bevel=0.0))
        objs.append(ns.cyl(r + 0.035, COLLAR, loc=(off, -A + COLLAR / 2, z), rot=(90, 0, 0), verts=8, bevel=0.0))
        C.part(objs, name, col, "Metal", smooth_angle=50)

    hw = []
    for c, d in (((-2.0, 0.0), (1, 0)), ((0.0, -2.0), (0, -1))):
        for v in C.pipe_bracket(c, d).values():
            hw += v
    C.part(hw, "Hangers", C.STEEL, "Metal", smooth_angle=45)

    # rust weeping from the outside of the bend on the dark pipe
    od, rd, _c, _n = C.BUNDLE[2]
    rr = RB + od
    a = math.radians(45)
    rust = ns.cyl(rd + 0.01, 0.2, loc=(-RB + rr * math.cos(a), -RB + rr * math.sin(a), C.bundle_z(rd)),
                  rot=(90, 0, 45), verts=8, bevel=0.0)   # axis along the bend tangent
    C.part([rust], "Rust", C.RUST, "Metal", smooth_angle=50)


SOCKETS = {"RunX": ((-A - 4.0, 0.0, 0.0), 0.0), "RunY": ((0.0, -A - 4.0, 0.0), -90.0)}
META = {"pivot": "corner point where the bundle centre lines meet, on the ceiling plane (hangs below)",
        "arms": "along -X and -Y, 4 long each", "bend_radius": RB,
        "continue_with": "Basement_PipeRun pivoted at socket RunX / RunY (pipe order matches)", "collide": "none"}

if __name__ == "__main__":
    C.run(build, "Basement_PipeCorner", mount="hang", pivot=(0.0, 0.0, 0.0), sockets=SOCKETS, budget=2000, meta=META,
          preview_fn=C.hang_preview(dirs=((-0.3, -1.0, -0.6), (0.9, -0.5, -0.8))))
