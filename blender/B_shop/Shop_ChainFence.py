"""Shop_ChainFence — 8-stud chain-link fence module for the back-alley yard (~6.6 tall).

Galvanised posts centred on both ends (neighbouring modules share the post position, so a
run looks continuous), domed caps, top rail, bottom tension wire, a crisp diamond lattice
of thin crossed wire rods (0.5 diamond, phase-locked so the lattice continues across
modules) and three strands of barbed wire on post extensions. All geometry is opaque.
Front = -Y. Pivot = bottom-centre. can_collide = False (the map adds invisible collision).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W = 8.0
POST_H = 6.25
RAIL_Z = 5.95
MESH_Z0, MESH_Z1 = 0.2, 5.88
GALV = "#A3AAAF"
WIRE = "#8C9398"
STEP = 0.5


def lattice():
    x0, x1 = -W / 2 + 0.14, W / 2 - 0.14
    z0, z1 = MESH_Z0, MESH_Z1
    rods = []
    # family A: z = x + c ; family B: z = -x + c  (c on a 0.5 grid -> identical in every module)
    k0 = int((z0 - x1) / STEP) - 1
    k1 = int((z1 - x0) / STEP) + 1
    for k in range(k0, k1 + 1):
        c = k * STEP + 0.25
        xa, xb = max(x0, z0 - c), min(x1, z1 - c)
        if xb - xa > 0.05:
            rods.append(C.pipe([(xa, -0.01, xa + c), (xb, -0.01, xb + c)], 0.022, sides=4))
    k0 = int((z0 + x0) / STEP) - 1
    k1 = int((z1 + x1) / STEP) + 1
    for k in range(k0, k1 + 1):
        c = k * STEP + 0.25
        xa, xb = max(x0, c - z1), min(x1, c - z0)
        if xb - xa > 0.05:
            rods.append(C.pipe([(xa, 0.01, c - xa), (xb, 0.01, c - xb)], 0.022, sides=4))
    return rods


def build():
    posts = []
    for sx in (-1, 1):
        x = sx * W / 2
        posts.append(ns.cyl(0.14, POST_H, loc=(x, 0, POST_H / 2), verts=8, bevel=0.0))
        posts.append(ns.sphere(0.17, loc=(x, 0, POST_H), scale=(1, 1, 0.7), segs=8, rings=4))
        posts.append(ns.cyl(0.22, 0.12, loc=(x, 0, 0.06), verts=8, bevel=0.0))
        for z in (1.4, 4.6):                # tension bands
            posts.append(ns.cyl(0.18, 0.08, loc=(x, 0, z), verts=8, bevel=0.0))
        # barbed-wire extension arm
        posts.append(C.pipe([(x, 0, POST_H - 0.1), (x, 0, POST_H + 0.45)], 0.05, sides=6))
    posts.append(C.pipe([(-W / 2, 0, RAIL_Z), (W / 2, 0, RAIL_Z)], 0.09, sides=8))
    C.part(posts, "Posts", GALV, "Metal", smooth_angle=50)
    wires = lattice()
    wires.append(C.pipe([(-W / 2, 0, MESH_Z0), (W / 2, 0, MESH_Z0)], 0.03, sides=4))
    # barbed strands with a few twisted barbs
    for z in (POST_H + 0.05, POST_H + 0.22, POST_H + 0.39):
        wires.append(C.pipe([(-W / 2, 0, z), (0, 0, z - 0.04), (W / 2, 0, z)], 0.018, sides=4))
        for i in range(4):
            bx = -W / 2 + 1.0 + i * 2.0 + (0.5 if z > POST_H + 0.2 else 0.0)
            wires.append(C.pipe([(bx - 0.06, -0.06, z - 0.06), (bx + 0.06, 0.06, z + 0.06)], 0.012, sides=3))
            wires.append(C.pipe([(bx - 0.06, 0.06, z - 0.06), (bx + 0.06, -0.06, z + 0.06)], 0.012, sides=3))
    C.part(wires, "Wire", WIRE, "Metal", smooth_angle=60)


META = {"module": "fence", "grid": 8, "size": [8.3, round(POST_H + 0.5, 2), 0.4], "collision": "none (map adds)",
        "placement": "pivot bottom-centre on the fence line; posts at x = +-4 coincide with neighbours"}

if __name__ == "__main__":
    C.run(build, "Shop_ChainFence", meta=META)
