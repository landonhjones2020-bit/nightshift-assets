"""Lobby_StringLights — festoon strand, 16 studs between its two attachment points.

A dark cable hanging in a gentle catenary (1.0 sag) with ten warm globe bulbs on short
drops (Bulbs, Neon, role "lamp"; black sockets) and a small chrome eye at each end.

PIVOT = midpoint between the two attachment points (EndA at Blender -X / Roblox +X, EndB
at Blender +X / Roblox -X); everything hangs below. To string between two poles: pivot at
the midpoint of the pole tops, model X along the line between them; for other spans the
MeshParts can be scaled along X (meta span).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SPAN = 16.0
SAG = 1.0
NB = 10


def build():
    a, b = (-SPAN / 2, 0, 0), (SPAN / 2, 0, 0)
    pts = C.catenary(a, b, SAG, n=16)
    cable = C.pipe(pts, 0.04, sides=5)
    sockets, bulbs = [], []
    fine = C.catenary(a, b, SAG, n=200)
    for k in range(NB):
        t = (k + 0.5) / NB
        p = fine[int(round(t * 200))]
        drop = 0.12
        sockets.append(ns.cyl(0.085, 0.2, loc=(p[0], p[1], p[2] - drop), verts=6, bevel=0.0))
        bulbs.append(ns.sphere(0.2, loc=(p[0], p[1], p[2] - drop - 0.27), scale=(1, 1, 1.12), segs=8, rings=5))
    C.part([cable] + sockets, "Cable", "#1E1F23", smooth_angle=60)
    ns.tag(C.merge(bulbs, "Bulbs"), "Bulbs", C.LAMP_WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=70)
    eyes = []
    for x in (-SPAN / 2, SPAN / 2):
        e = ns.torus(0.12, 0.035, major_segs=8, minor_segs=4)
        C.place(e, (x, 0, 0.0), pitch=90)
        eyes.append(e)
    C.part(eyes, "Eyes", C.CHROME, "Metal", smooth_angle=60)


SOCKETS = {"EndA": ((-SPAN / 2, 0, 0), 0.0), "EndB": ((SPAN / 2, 0, 0), 0.0)}
META = {"span": SPAN, "sag": SAG, "bulbs": NB, "pivot": "midpoint between the attachment points (top)",
        "roles": {"lamp": "Bulbs"},
        "light_hint": {"type": "PointLight", "per": "a few bulbs", "color": C.LAMP_WARM, "range": 8, "brightness": 0.6}}

if __name__ == "__main__":
    C.run(build, "Lobby_StringLights", sockets=SOCKETS, pivot=(0, 0, 0), meta=META, socket_views=((-20, 15),))
