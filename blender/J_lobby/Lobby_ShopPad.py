"""Lobby_ShopPad — the glowing circle in front of each shop on the lobby's shop row (9.6 across).

2026-11-04 (Landon, on 99 Nights in the Forest: shops "right next to each other with glowing
circles that if you step on them automatically opens up the menu"). Lies flat on the paving:

  * Base: a dark stone kerb ring (r 4.3-4.8) that frames the glow on the light paving.
  * Ring: a thick neon ring (r 3.85-4.3), role "ring" — the map tints it per shop.
  * Dash: 20 short neon dashes on an inner circle (r 3.2-3.55), role "dash" — the client turns
    them slowly so the circle reads as alive.
  * Disc: a thin translucent neon disc filling the centre (r 3.05), role "disc" — the client
    pulses it and brightens it while you stand on it.

Everything is non-colliding (you walk onto it). Pivot = centre on the ground. Socket: Center.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402

ns = C.ns

R_BASE = (4.3, 4.8)
R_RING = (3.85, 4.3)
R_DASH = (3.2, 3.55)
R_DISC = 3.05
N_DASH = 20


def sector(r0, r1, a0, a1, z0, z1, segs=3):
    return C.arc_solid(r0, r1, a0, a1, z0, z1, segs=segs)


def build():
    base = ns.ring(R_BASE[0], R_BASE[1], 0.1, loc=(0, 0, 0.05), verts=40)
    ring = ns.ring(R_RING[0], R_RING[1], 0.12, loc=(0, 0, 0.08), verts=40)
    dashes = []
    step = 360.0 / N_DASH
    for i in range(N_DASH):
        a0 = i * step
        dashes.append(sector(R_DASH[0], R_DASH[1], a0, a0 + step * 0.55, 0.03, 0.1))
    disc = C.disc(R_DISC, loc=(0, 0, 0.035), verts=32)
    C.part([base], "Base", "#2B2D33", "Concrete", smooth_angle=None)
    ns.tag(C.merge([ring], "Ring"), "Ring", "#FFFFFF", "Neon", recolor="ring", cast_shadow=False, smooth_angle=None)
    ns.tag(C.merge(dashes, "Dash"), "Dash", "#FFFFFF", "Neon", recolor="dash", cast_shadow=False, smooth_angle=None)
    ns.tag(C.merge([disc], "Disc"), "Disc", "#FFFFFF", "Neon", transparency=0.7, recolor="disc", cast_shadow=False,
           smooth_angle=None)


def sockets():
    return {"Center": ((0.0, 0.0, 0.05), 0.0)}


META = {
    "radius": R_BASE[1],
    "inner_radius": R_DISC,
    "roles": {"ring": "Ring (neon, tinted per shop)", "dash": "Dash (neon dashes, turned by the client)",
              "disc": "Disc (translucent neon, pulsed by the client)"},
}

if __name__ == "__main__":
    C.run(build, "Lobby_ShopPad", sockets=sockets(), meta=META, budget=1500)
