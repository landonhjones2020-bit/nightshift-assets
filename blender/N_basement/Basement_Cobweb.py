"""Basement_Cobweb — a big dusty cobweb slung across a ceiling corner.

Seven thin spokes fan out from the corner point: the first slopes down along the back
wall, the last down along the side wall, the ones between hang down the corner and out
into the room, so the web is a sloped sheet facing the room below; five sagging cross
threads (the outer one thicker) and two loose wisps. Pale grey strands, Transparency 0.3, no shadow, no collision.
PIVOT = THE CORNER POINT it hangs from (top back corner: ceiling, back wall +Y and the
side wall at +X meet there, z = 0); the web spreads into -X / -Y / -Z. Rotate in 90-degree
steps for the other corners. ~2.4 x 2.1 x 2.4.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
SPAN = 2.9          # spoke length (the wall spokes slope down, so ~2.3 along each wall)


def build():
    d0 = Vector((-1.0, 0.0, -0.75)).normalized()        # down along the back wall
    dm = Vector((-0.42, -0.42, -1.0)).normalized()      # down the corner's diagonal, out into the room
    d1 = Vector((0.0, -1.0, -0.75)).normalized()        # down along the side wall
    dirs = []
    n = 7
    for k in range(n):   # quadratic Bezier d0 -> dm -> d1, normalised
        t = k / (n - 1)
        dirs.append(((1 - t) ** 2 * d0 + 2 * (1 - t) * t * dm * 1.3 + t * t * d1).normalized())
    lens = [1.0, 0.9, 0.85, 0.82, 0.85, 0.9, 1.0]
    web = C.web_fan((-0.03, -0.03, -0.03), d0, d1, SPAN, rings=5, sag=0.16, r_strand=0.019, r_edge=0.026,
                    seed=11, wisps=2, spoke_len=lens, dirs=dirs, wisp_len=(0.07, 0.13))
    C.part(web, "Web", C.WEB, transparency=0.3, cast_shadow=False, smooth_angle=70)


META = {"pivot": "the ceiling corner it hangs from (back wall +Z, side wall -X in Roblox model space)",
        "transparency": 0.3, "collide": "none"}

if __name__ == "__main__":
    C.run(build, "Basement_Cobweb", mount="hang", pivot=(0.0, 0.0, 0.0), budget=2000, meta=META, backdrop="corner",
          views=((-40, -18, False), (-15, -35, True)), backdrop_col="#3F4247")
