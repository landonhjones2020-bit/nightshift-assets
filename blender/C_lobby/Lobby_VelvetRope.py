"""Lobby_VelvetRope — one 6-stud velvet rope section for the VIP lounge.

Two polished brass stanchions (weighted domed base, slim post, ball top with a ring hook)
6 studs apart, with a sagging purple velvet rope (Fabric) between them ending in brass
snap clips. Each stanchion is its own part (StanchionA at Blender -X / Roblox +X,
StanchionB at Blender +X / Roblox -X, role "stanchion") so a run of sections can drop the
duplicate post where two sections meet.

Pivot = bottom-centre (midway between the posts). Front = -Y (either side reads the same).
To chain: offset each next section 6 studs along the model's X and Destroy its
StanchionA (or B) so posts are not doubled. Sockets: PostA / PostB (post bases),
Gap (rope midpoint; put an invisible blocker here when the VIP gate is closed).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SPAN = 6.0
POST_H = 3.0
HOOK_Z = POST_H - 0.1
SAG = 0.65


def stanchion(x, side):
    base = ns.lathe([(0.0, 0.0), (0.55, 0.0), (0.55, 0.08), (0.42, 0.22), (0.14, 0.3), (0.08, 0.36), (0.0, 0.36)],
                    verts=14, loc=(x, 0, 0))
    post = ns.cyl(0.07, POST_H - 0.5, loc=(x, 0, 0.3 + (POST_H - 0.5) / 2), verts=8, bevel=0.0)
    collar = ns.cyl(0.11, 0.1, loc=(x, 0, POST_H - 0.15), verts=8, bevel=0.0)
    ball = ns.sphere(0.17, loc=(x, 0, POST_H + 0.05), segs=10, rings=6)
    ring = ns.torus(0.11, 0.03, major_segs=8, minor_segs=4)
    C.place(ring, (x - side * 0.16, 0, HOOK_Z), pitch=90)
    return [base, post, collar, ball, ring]


def build():
    for name, x, side in (("StanchionA", -SPAN / 2, -1), ("StanchionB", SPAN / 2, 1)):
        ns.tag(C.merge(stanchion(x, side), name), name, C.BRASS, "Metal", recolor="stanchion", smooth_angle=50)
    a = (-SPAN / 2 + 0.3, 0, HOOK_Z - 0.06)
    b = (SPAN / 2 - 0.3, 0, HOOK_Z - 0.06)
    rope = C.pipe(C.catenary(a, b, SAG, n=12), 0.14, sides=8)
    C.part([rope], "Rope", C.VELVET, "Fabric", smooth_angle=60)
    clips = []
    for x, sgn in ((a[0], -1), (b[0], 1)):
        clips.append(C.rod((x - sgn * 0.02, 0, HOOK_Z - 0.06), (x - sgn * 0.24, 0, HOOK_Z - 0.09), 0.17, verts=8,
                           r_top=0.15))
        clips.append(C.rod((x + sgn * 0.0, 0, HOOK_Z - 0.06), (x + sgn * 0.14, 0, HOOK_Z), 0.035, verts=5))
    C.part(clips, "Clips", C.GOLD, "Metal", smooth_angle=50)


SOCKETS = {"PostA": ((-SPAN / 2, 0, 0), 0.0), "PostB": ((SPAN / 2, 0, 0), 0.0),
           "Gap": ((0, 0, HOOK_Z - 0.06 - SAG), 0.0)}
META = {"span": SPAN, "post_height": POST_H, "sag": SAG, "chain_offset": SPAN,
        "chain_hint": "offset next section by span along X; Destroy its StanchionA",
        "roles": {"stanchion": "StanchionA (Roblox +X end), StanchionB (Roblox -X end)"}}

if __name__ == "__main__":
    C.run(build, "Lobby_VelvetRope", sockets=SOCKETS, meta=META)
