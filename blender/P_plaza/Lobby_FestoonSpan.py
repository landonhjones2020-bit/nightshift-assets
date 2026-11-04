"""Lobby_FestoonSpan — a sagging string of round festoon bulbs, 24 studs from hook to hook.

A dark cable hanging in a catenary (3.0 sag at mid-span) with sixteen warm globe bulbs (Bulbs,
Neon, role "lamp") on black sockets and short drops, and a small chrome eye at each end.
No collision.

PIVOT = the START hook (cable end at the pivot). The span runs along the model's +X (Roblox
RightVector): the end hook is at (24, 0, 0) in Roblox axes (Blender x = -24). To hang it: put
the pivot on pole A's Socket_Hook and point the model's +X at pole B's hook. For other
distances scale the MeshParts along X by distance / 24 (meta span).
Sockets: Start (0, 0, 0), End (24, 0, 0), Light (among the lowest bulbs, mid-span).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

SPAN = 24.0
SAG = 3.0
NB = 16
BULB_R = 0.26


def build():
    a, b = (0.0, 0.0, 0.0), (C.along_x(SPAN), 0.0, 0.0)
    pts = C.catenary(a, b, SAG, n=24)
    cable = C.pipe(pts, 0.045, sides=5)
    socks, centres = C.hang_bulbs(pts, NB, r=BULB_R, drop=0.08, sock_r=0.09, sock_h=0.2, end_pad=0.8,
                                  fine=C.catenary(a, b, SAG, n=240))
    bulbs = C.spheres(centres, BULB_R, segs=7, rings=5, scale=(1, 1, 1.08))
    eyes = []
    for x in (a[0], b[0]):
        e = ns.torus(0.12, 0.035, major_segs=8, minor_segs=4)
        C.place(e, (x, 0, 0.0), pitch=90)
        eyes.append(e)
    C.part([cable] + socks, "Cable", C.CABLE, smooth_angle=60)
    C.part(eyes, "Eyes", C.CHROME, "Metal", smooth_angle=60)
    ns.tag(bulbs, "Bulbs", C.BULB, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=80)
    return {}


SOCKETS = {"Start": ((0.0, 0.0, 0.0), 0.0), "End": ((C.along_x(SPAN), 0.0, 0.0), 0.0),
           "Light": ((C.along_x(SPAN / 2), 0.0, -SAG - 0.5), 0.0)}
META = {"span": SPAN, "sag": SAG, "bulbs": NB, "pivot": "start hook (cable end); runs along Roblox +X to End",
        "roles": {"lamp": "Bulbs"},
        "light_hint": {"type": "PointLight", "at": "Socket_Light", "color": C.BULB, "range": 14, "brightness": 0.7}}

if __name__ == "__main__":
    C.run(build, "Lobby_FestoonSpan", sockets=SOCKETS, meta=META, budget=2000, pivot=(0.0, 0.0, 0.0),
          socket_views=((-20, 15),), far=True, far_kw={"dist": 30.0})
