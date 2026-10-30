"""Lobby_TreePlanter — big square brick planter with a stylised round-canopy tree (~6.3 x ~13 x 6.3).

A 6 x 6 brick planter (1.6 tall) with a cast-stone coping and dark soil, a few flowers (pink and
mustard), a tapered bark trunk with two branches, a clustered round canopy in dusk-toned greens, and
a string of six small warm bulbs looped round the canopy (Bulbs, role "lamp") on a dark cable that
lies on the canopy's surface.

Front = -Y, pivot = bottom-centre. Socket Light (centre of the bulb string, for one PointLight).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns

PW, PH = 6.0, 1.6
CANOPY = [((0.0, 0.0, 9.55), 2.6, C.FOLIAGE), ((-1.55, 0.35, 8.7), 1.95, C.FOLIAGE_DARK),
          ((1.45, -0.3, 8.85), 1.95, C.FOLIAGE_DARK), ((0.25, 0.55, 11.05), 1.75, C.FOLIAGE)]
SOIL = "#3B2A20"
PETAL_PINK = "#FF7DB8"


def outside_radius(theta, z, margin=-0.04):
    """Smallest horizontal radius (from the trunk axis) at angle theta / height z that is outside
    every canopy sphere (+ margin)."""
    r = 0.3
    while r < 6.0:
        p = Vector((r * math.cos(theta), r * math.sin(theta), z))
        if all((p - Vector(c)).length >= rad + margin for c, rad, _ in CANOPY):
            return r
        r += 0.03
    return r


def build():
    brick = [ns.box((PW, PW, PH - 0.1), loc=(0, 0, (PH - 0.1) / 2), bevel=0.08, segments=1)]
    stone = [C.ring_slab(C.rrect(PW + 0.36, PW + 0.36, 0.2, 2), C.rrect(PW - 0.8, PW - 0.8, 0.1, 2), "z", PH - 0.16, PH + 0.12)]
    soil = [ns.box((PW - 0.78, PW - 0.78, 0.12), loc=(0, 0, PH - 0.02), bevel=0.0)]
    bark = [C.rod((0, 0, PH - 0.1), (0.1, 0.05, 7.6), 0.46, verts=8, r_top=0.26),
            C.rod((0, 0, PH - 0.05), (0, 0, PH + 0.5), 0.68, verts=8, r_top=0.42),
            C.rod((0.05, 0.0, 6.2), (-1.3, 0.3, 8.0), 0.2, verts=6, r_top=0.11),
            C.rod((0.08, 0.02, 6.6), (1.25, -0.25, 8.2), 0.19, verts=6, r_top=0.1)]
    leaves = {}
    for i, (c, r, col) in enumerate(CANOPY):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=c)   # 80 faces
        o = bpy.context.active_object
        ns.jitter(o, amount=0.1, seed=11 + i)
        leaves.setdefault(col, []).append(o)
    # flowers in the soil
    stems, petals = [], {PETAL_PINK: [], C.MUSTARD: []}
    for k, (x, y, col) in enumerate(((-1.9, -1.8, PETAL_PINK), (1.7, -1.95, C.MUSTARD), (-1.7, 1.6, C.MUSTARD),
                                     (2.0, 1.4, PETAL_PINK))):
        h = PH + 0.55 + 0.12 * (k % 2)
        stems.append(C.rod((x, y, PH), (x, y, h), 0.05, verts=4))
        f = C.prism(C.star_pts(0.46, 0.21, 0, 0, n=5), "z", h - 0.04, h + 0.06)
        f.location = (x, y, 0)
        f.rotation_euler = (0, 0, math.radians(17 * k))
        petals[col].append(f)
        petals[C.MUSTARD if col == PETAL_PINK else PETAL_PINK].append(ns.cyl(0.14, 0.08, loc=(x, y, h + 0.08), verts=6,
                                                                            bevel=0.0))
    # string lights: a cable spiralling down round the canopy, lying on its surface, 6 bulbs
    cable_pts = []
    turns, z0, z1 = 1.15, 10.9, 7.9
    n = 16
    for i in range(n + 1):
        t = i / n
        th = math.radians(-60) + 2 * math.pi * turns * t
        z = z0 + (z1 - z0) * t + 0.35 * math.sin(2 * math.pi * 3 * t)      # gentle swags
        r = outside_radius(th, z)
        cable_pts.append((r * math.cos(th), r * math.sin(th), z))
    cable = C.pipe(cable_pts, 0.04, sides=3)
    bulbs, drops = [], []
    for k in range(6):
        p = Vector(cable_pts[int(round((k + 0.5) / 6 * n))])
        out = Vector((p.x, p.y, 0)).normalized()
        b = p + out * 0.18 + Vector((0, 0, -0.32))
        drops.append(C.rod(p, b + Vector((0, 0, 0.14)), 0.03, verts=3))
        bulbs.append(tuple(b))
    C.part(brick, "Planter", C.BRICK, "Brick", can_collide=True, smooth_angle=40)
    C.part(stone, "Coping", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(soil, "Soil", SOIL, "Pebble", smooth_angle=None)
    C.part(bark, "Trunk", C.BARK, "Wood", can_collide=True, smooth_angle=50)
    for i, (col, objs) in enumerate(leaves.items()):
        C.part(objs, f"Canopy{i + 1}", col, "Plastic", smooth_angle=70)
    C.part(stems, "Stems", C.FOLIAGE_DARK, smooth_angle=60)
    C.part(petals[PETAL_PINK], "PetalsPink", PETAL_PINK, smooth_angle=None)
    C.part(petals[C.MUSTARD], "PetalsGold", C.MUSTARD, smooth_angle=None)
    C.part([cable] + drops, "Cable", "#1E1F23", smooth_angle=60)
    ns.tag(C.spheres(bulbs, 0.15, segs=5, rings=3, scale=(1, 1, 1.15)), "Bulbs", C.LAMP_WARM, "Neon", recolor="lamp",
           cast_shadow=False, smooth_angle=80)
    return {}


SOCKETS = {"Light": ((0.0, 0.0, 9.3), 0.0)}
META = {"planter_height": PH, "roles": {"lamp": "Bulbs (6 on the canopy string)"},
        "light_hint": {"type": "PointLight", "at": "Socket_Light", "color": C.LAMP_WARM, "range": 9, "brightness": 0.6}}

if __name__ == "__main__":
    # pivot = bottom-centre of the planter (the canopy is a little lopsided)
    C.run(build, "Lobby_TreePlanter", sockets=SOCKETS, meta=META, budget=1200, pivot=(0.0, 0.0, 0.0))
