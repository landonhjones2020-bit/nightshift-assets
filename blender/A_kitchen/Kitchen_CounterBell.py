"""Kitchen_CounterBell — chrome service bell on a red-orange base ("ding!", noise 30).

Stylised a little oversized (0.8 across) so it reads on the counter at phone size. The
plunger (rod + cap) is a separate part (role bell_plunger); the client pushes it down by
meta plunger_travel along plunger_dir (Roblox model space) when the bell is rung. Round,
so any yaw works. Bottom-centre pivot.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
CHROME = "#D3D9DE"


def build():
    base = ns.lathe([(0.0, 0.0), (0.38, 0.0), (0.41, 0.03), (0.41, 0.09), (0.37, 0.14), (0.0, 0.14)], verts=20, name="Base")
    C.part(base, "Base", C.BRAND, "SmoothPlastic", smooth_angle=50)
    ring = ns.lathe([(0.0, 0.135), (0.31, 0.135), (0.33, 0.155), (0.0, 0.155)], verts=20, name="Ring")
    C.part(ring, "Seat", C.RUBBER, "SmoothPlastic", smooth_angle=50)
    dome = ns.lathe([(0.32, 0.15), (0.32, 0.19), (0.3, 0.27), (0.25, 0.35), (0.17, 0.41), (0.08, 0.44), (0.0, 0.445)],
                    verts=20, name="Dome")
    C.part(dome, "Dome", CHROME, "Metal", smooth_angle=55)
    plunger = ns.lathe([(0.0, 0.42), (0.035, 0.42), (0.035, 0.54), (0.075, 0.55), (0.085, 0.58), (0.06, 0.61), (0.0, 0.615)],
                       verts=10, name="Plunger")
    C.part(plunger, "Plunger", CHROME, "Metal", recolor="bell_plunger", smooth_angle=55)
    meta = {"plunger_travel": 0.07, "plunger_dir": [0, -1, 0]}
    return {"export": {"meta": meta}}


if __name__ == "__main__":
    C.run(build, "Kitchen_CounterBell")
