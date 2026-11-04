"""Lobby_UniformRack — rolling staff-uniform rack (6 W x 6 H x 2 D).

A brushed-steel rolling clothes rack: two uprights with ball finials, a top rail, T-feet on
four black swivel casters, a low cross bar and a steel shelf carrying folded uniform stacks.
Eight garments hang closet-style on maple hangers with chrome hooks (each turned a little so
its face shows), alternating polo shirts (contrasting collar) and bib aprons (contrasting
pocket, neck strap over the hanger), in the brand colours: navy, red-orange,
cream and mustard.

Front = -Y, pivot = bottom-centre. Collides (frame, shelf, garments). Socket Prompt = in front
of the rack at chest height (a "Uniforms" prompt).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns
W, H, D = 6.0, 6.0, 2.0
UX = 2.88                    # upright x
RAIL_Z = 5.55
TOP_Z = RAIL_Z - 0.42        # garment local z = 0 (shoulder line)
FOOT_Z = 0.36
SHELF_Z = 0.62
XS = [-2.32 + 4.64 * i / 7 for i in range(8)]
# (kind, body colour, trim colour) left -> right as seen from the front
GARMENTS = [("shirt", C.NAVY, C.MUSTARD), ("apron", C.BRAND, C.MUSTARD), ("shirt", C.CREAM, C.BRAND),
            ("apron", C.MUSTARD, C.NAVY), ("shirt", C.BRAND, C.CREAM), ("apron", C.NAVY, C.CREAM),
            ("shirt", C.MUSTARD, C.NAVY), ("apron", C.CREAM, C.BRAND)]

SHIRT = [(0.17, 0.0), (0.62, -0.12), (0.95, -0.38), (0.8, -0.76), (0.6, -0.66), (0.6, -1.98), (0.45, -2.08),
         (0.0, -2.1), (-0.45, -2.08), (-0.6, -1.98), (-0.6, -0.66), (-0.8, -0.76), (-0.95, -0.38), (-0.62, -0.12),
         (-0.17, 0.0), (0.0, -0.1)]
COLLAR = [(-0.25, 0.03), (0.25, 0.03), (0.32, -0.1), (0.06, -0.34), (0.0, -0.2), (-0.06, -0.34), (-0.32, -0.1)]


def apron_outline(top=-0.35, bib=0.3, hw=0.64, ah=2.05):
    """Bib apron silhouette (x, z) hanging from `top` (Lobby_ApronShop shape, smaller)."""
    pts = []
    r = 0.14
    for k in range(3):
        a = math.pi + (math.pi / 2) * k / 2
        pts.append((-hw + r + r * math.cos(a), top - ah + r + r * math.sin(a)))
    for k in range(3):
        a = 1.5 * math.pi + (math.pi / 2) * k / 2
        pts.append((hw - r + r * math.cos(a), top - ah + r + r * math.sin(a)))
    for k in range(5):
        t = (math.pi / 2) * (4 - k) / 4
        pts.append((hw - (hw - bib) * math.cos(t), top - 0.85 * math.sin(t)))
    for k in range(5):
        t = (math.pi / 2) * k / 4
        pts.append((-hw + (hw - bib) * math.cos(t), top - 0.85 * math.sin(t)))
    return pts


def garment(kind, body, trim, g):
    """Garment + hanger in its LOCAL frame (face plane = XZ, faces -Y, hook over a rail at
    (y 0, z 0.42)). Adds objects to g[colour] / g['maple'] / g['chrome']."""
    if kind == "shirt":
        C.add(g, body, C.prism(SHIRT, "y", -0.08, 0.08))
        C.add(g, trim, C.prism(COLLAR, "y", -0.1, 0.1))
    else:
        out = apron_outline()
        C.add(g, body, C.prism(out, "y", -0.04, 0.04))
        C.add(g, trim, C.prism(C.rrect(0.78, 0.42, 0.08, 1, 0, -1.62), "y", -0.06, 0.06))
        C.add(g, trim, C.pipe([(-0.24, 0, -0.36), (-0.2, 0, 0.0), (0.0, 0, 0.17), (0.2, 0, 0.0), (0.24, 0, -0.36)],
                              0.035, sides=3))
    # maple hanger bar (shoulder arch) + chrome hook over the rail
    g["maple"].append(C.pipe([(-0.66, 0, 0.0), (-0.3, 0, 0.11), (0.0, 0, 0.14), (0.3, 0, 0.11), (0.66, 0, 0.0)], 0.045,
                             sides=3))
    g["chrome"].append(C.pipe([(0.0, 0, 0.15), (0.0, 0, 0.3), (-0.12, 0, 0.42), (0.0, 0, 0.54), (0.12, 0, 0.44),
                               (0.1, 0, 0.36)], 0.022, sides=3))


def build():
    rnd = random.Random(7)
    g = {"maple": [], "chrome": []}
    for x, (kind, body, trim) in zip(XS, GARMENTS):
        local = {"maple": [], "chrome": []}
        garment(kind, body, trim, local)
        yaw = 90.0 + rnd.uniform(-14, 14)
        for col, objs in local.items():
            for o in objs:
                C.place([o], (x, 0.0, TOP_Z), yaw=yaw)
            C.add(g, col, objs)
    # frame: uprights + finials, top rail, T-feet, casters, cross bar, shelf
    steel = []
    for sx in (-1, 1):
        x = sx * UX
        steel.append(C.rod((x, 0, FOOT_Z), (x, 0, 5.82), 0.075, verts=8))
        steel.append(C.rod((x, -1.0, FOOT_Z), (x, 1.0, FOOT_Z), 0.08, verts=8))
    steel.append(C.rod((-UX, 0, RAIL_Z), (UX, 0, RAIL_Z), 0.065, verts=8))
    steel.append(C.rod((-UX, 0, 0.62), (UX, 0, 0.62), 0.05, verts=6))
    for sy in (-1, 1):
        steel.append(C.rod((-UX, sy * 0.66, SHELF_Z - 0.06), (UX, sy * 0.66, SHELF_Z - 0.06), 0.04, verts=6))
    shelf = ns.box((2 * UX - 0.1, 1.5, 0.05), loc=(0, 0, SHELF_Z), bevel=0.0)
    C.part(steel + [shelf], "Frame", C.STEEL, "Metal", can_collide=True, smooth_angle=45)
    fin = C.spheres([(sx * UX, 0, 5.88) for sx in (-1, 1)], 0.12, segs=6, rings=4)
    forks = []
    wheels = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * UX, sy * 0.86
            forks.append(ns.box((0.1, 0.22, 0.12), loc=(x, y, FOOT_Z - 0.12), bevel=0.0))
            wheels.append(ns.cyl(0.15, 0.12, loc=(x, y, 0.15), rot=(0, 90, 0), verts=8, bevel=0.0))
    C.part([fin] + forks + g.pop("chrome"), "Chrome", C.CHROME, "Metal", smooth_angle=45)
    C.part(wheels, "Casters", C.RUBBER, smooth_angle=40)
    C.part(g.pop("maple"), "Hangers", C.MAPLE, "Wood", smooth_angle=50)
    C.parts_by_colour(g, "Garments", "Fabric", can_collide=True, smooth_angle=35)

    # folded uniform stacks on the shelf
    stacks = {}
    for x, cols in ((-1.75, (C.NAVY, C.MUSTARD)), (0.05, (C.BRAND,)), (1.8, (C.CREAM, C.BRAND))):
        z = SHELF_Z + 0.025
        for k, col in enumerate(cols):
            C.add(stacks, col, ns.box((1.0, 0.8, 0.2), loc=(x + rnd.uniform(-0.05, 0.05), rnd.uniform(-0.05, 0.05), z + 0.1),
                                      rot=(0, 0, rnd.uniform(-6, 6)), bevel=0.06, segments=1))
            z += 0.2
    C.parts_by_colour(stacks, "Folded", "Fabric", smooth_angle=45)


SOCKETS = {"Prompt": ((0, -1.6, 3.0), 0.0)}
META = {"garments": "8 on the rail, left->right (front view): navy shirt, red-orange apron, cream shirt, mustard apron, "
                    "red-orange shirt, navy apron, mustard shirt, cream apron",
        "rail_height": RAIL_Z}

if __name__ == "__main__":
    C.run(build, "Lobby_UniformRack", sockets=SOCKETS, budget=2000, meta=META)
