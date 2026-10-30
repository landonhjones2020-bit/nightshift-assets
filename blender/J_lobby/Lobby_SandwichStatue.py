"""Lobby_SandwichStatue — plaza centrepiece fountain with a GIANT sandwich on top (~16 x 18 x 16).

A round two-step cast-stone plinth carries a brick fountain basin with a stone coping; the basin
holds a shallow pool (Water: flat Glass, cyan tint, role "water") ringed by a cyan neon tube round
the rim (RimNeon, role "neon"). A stone column with a red-orange band rises from the pool, four
water jets arc from it into the basin (Jets, role "water"), and on its brass top plate sits a giant
chunky sandwich sculpture, tilted a few degrees: bottom bun, ruffled deli meat, a cheese slice with
corner drips, tomato discs peeking out, wavy lettuce and a domed sesame top bun. On the front of the
basin wall, a curved navy plaque with brass modelled text "STACKHOUSE · EST. 1987".

Front = -Y (the plaque), pivot = bottom-centre. No sockets needed (decor); meta lists the roles.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns

R1, R2 = 8.0, 7.25            # step radii
S1, S2 = 0.6, 1.2             # step tops
WALL = (5.85, 6.6, 3.0)       # basin wall inner / outer radius, top
COPE = (5.72, 6.82, 3.26)
POOL_FLOOR, WATER_Z = 1.8, 2.72
COL_TOP = 8.55
PLATE_TOP = 8.98
SAND_SCALE = 1.12
TILT = (6.0, -3.5)            # sandwich tilt about X (leans to the front) and Y, degrees
SAND_SINK = 0.36
MEAT = "#C9604F"
SEED = "#F6E7C4"
POOL = "#2C5A6A"
PLAQUE_A = 52.0               # plaque half-angle (degrees either side of the front)


def ruffle_disc(r, h, z0, waves, amp_r, amp_z, verts=40, phase=0.0, name="Ruffle"):
    """Thick disc whose rim undulates in / out (amp_r) and up / down (amp_z): lettuce, deli meat."""
    bm = bmesh.new()
    bot, top = [], []
    for i in range(verts):
        a = 2 * math.pi * i / verts
        rr = r + amp_r * math.sin(waves * a + phase)
        dz = amp_z * math.cos(waves * a + phase)
        bot.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z0 + dz)))
        top.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z0 + h + dz)))
    cb = bm.verts.new((0, 0, z0))
    ct = bm.verts.new((0, 0, z0 + h))
    for i in range(verts):
        j = (i + 1) % verts
        bm.faces.new([bot[i], bot[j], top[j], top[i]])
        bm.faces.new([cb, bot[j], bot[i]])
        bm.faces.new([ct, top[i], top[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return C.obj_from_bm(bm, name)


def lathe(profile, verts, z0=0.0):
    o = ns.lathe([(r, z + z0) for r, z in profile], verts=verts)
    return o


def sandwich():
    """Built at the origin (bottom of the bun on z = 0). Returns {colour: [objs]}."""
    out = {C.BUN: [], MEAT: [], C.CHEESE: [], C.TOMATO: [], C.LETTUCE: [], SEED: []}
    out[C.BUN].append(lathe([(0.0, 0.0), (4.2, 0.0), (4.58, 0.38), (4.64, 1.12), (4.36, 1.62), (0.0, 1.74)], 18))
    out[MEAT].append(ruffle_disc(4.78, 1.0, 1.66, 9, 0.32, 0.16, verts=36))
    # cheese slice turned 45 degrees so its corners poke out, with a drip at each corner
    sq = [(x * math.cos(math.pi / 4) - y * math.sin(math.pi / 4), x * math.sin(math.pi / 4) + y * math.cos(math.pi / 4))
          for x, y in C.rrect(8.0, 8.0, 0.55, 2)]
    out[C.CHEESE].append(C.prism(sq, "z", 2.72, 3.08))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        rr = 8.0 / 2 * math.sqrt(2) - 0.55 * (math.sqrt(2) - 1) - 0.35
        drop = [(-0.38, 3.0), (0.38, 3.0), (0.36, 2.35), (0.26, 1.9), (0.0, 1.72), (-0.26, 1.9), (-0.36, 2.35)]
        d = C.prism(drop, "y", -0.13, 0.13)
        C.place(d, (rr * math.cos(a), rr * math.sin(a), 0.0), yaw=math.degrees(a) + 90)
        out[C.CHEESE].append(d)
    # tomato discs: one in the middle, five round the edge poking out
    out[C.TOMATO].append(ns.cyl(2.1, 0.55, loc=(0, 0, 3.32), verts=12, bevel=0.0))
    for k in range(5):   # outer slices sit 0.03 / 0.06 higher than the centre one (no coplanar tops)
        a = math.radians(18 + 72 * k)
        out[C.TOMATO].append(ns.cyl(1.62, 0.55, loc=(3.3 * math.cos(a), 3.3 * math.sin(a), 3.35 + 0.03 * (k % 2)), verts=12,
                                    bevel=0.0))
    out[C.LETTUCE].append(ruffle_disc(5.05, 0.38, 3.56, 11, 0.42, 0.26, verts=44, phase=0.4))
    top = lathe([(4.5, 0.0), (4.72, 0.3), (4.68, 0.9), (4.3, 1.75), (3.5, 2.55), (2.3, 3.15), (0.95, 3.48), (0.0, 3.55)], 18,
                z0=3.98)
    out[C.BUN].append(top)
    # sesame seeds on the dome (along the surface normal)
    pts, nrm = [], []
    prof = [(4.68, 0.9), (4.3, 1.75), (3.5, 2.55), (2.3, 3.15), (0.95, 3.48)]
    rng = [(0.18, 1.2), (0.38, 2.0), (0.6, 2.75), (0.82, 3.3)]
    import random
    rnd = random.Random(7)
    for (t, _), n in zip(rng, (6, 5, 4, 2)):
        for i in range(n):
            a = 2 * math.pi * (i + rnd.uniform(-0.25, 0.25) + (0.5 if n % 2 else 0)) / n + t
            # point on the dome at parameter t (piecewise along the profile)
            seg = min(int(t * (len(prof) - 1)), len(prof) - 2)
            u = t * (len(prof) - 1) - seg
            (ra, za), (rb, zb) = prof[seg], prof[seg + 1]
            r = ra + (rb - ra) * u
            z = 3.98 + za + (zb - za) * u
            tang = Vector((rb - ra, 0, zb - za)).normalized()
            nr = Vector((tang.z, 0, -tang.x))           # outward normal in the (r, z) plane
            r -= 0.05 * nr.x                             # seat the seed into the faceted dome
            z -= 0.05 * nr.z
            pts.append((r * math.cos(a), r * math.sin(a), z))
            nrm.append((nr.x * math.cos(a), nr.x * math.sin(a), nr.z))
    out[SEED].append(C.domes(pts, 0.2, axis=nrm, segs=5, rings=2, squash=0.55))
    return out


def bend(obj, radius):
    """Wrap a mesh built facing -Y round a vertical cylinder: x -> angle on the circle, the front
    plane y = -radius stays on the circle."""
    for v in obj.data.vertices:
        x, y, z = v.co
        rr = radius - (y + radius)          # depth behind the front plane reduces the radius
        phi = x / radius
        v.co = Vector((rr * math.sin(phi), -rr * math.cos(phi), z))
    return obj


def build():
    stone, brick, steel, gold = [], [], [], []
    for r, z0, z1 in ((R1, 0.0, S1), (R2, S1 - 0.01, S2)):
        step = C.prism(C.circle_pts(r, 24), "z", z0, z1)
        ns.bevel(step, width=0.06, segments=1)
        stone.append(step)
    brick.append(C.ring_slab(C.circle_pts(WALL[1], 24), C.circle_pts(WALL[0], 24), "z", S2 - 0.02, WALL[2]))
    stone.append(C.ring_slab(C.circle_pts(COPE[1], 24), C.circle_pts(COPE[0], 24), "z", WALL[2], COPE[2]))
    pool = C.prism(C.circle_pts(WALL[0] + 0.02, 24), "z", S2, POOL_FLOOR)
    C.part([pool], "PoolFloor", POOL, "Slate", smooth_angle=None)
    water = C.prism(C.circle_pts(WALL[0] + 0.03, 24), "z", WATER_Z - 0.08, WATER_Z)
    ns.tag(water, "Water", C.WATER, "Glass", transparency=0.3, recolor="water", cast_shadow=False, smooth_angle=None)
    rim = C.pipe([(6.9 * math.cos(2 * math.pi * i / 24), 6.9 * math.sin(2 * math.pi * i / 24), WALL[2] + 0.1)
                  for i in range(24)], 0.1, sides=4, closed=True)
    ns.tag(rim, "BasinNeon", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # column + brass top plate
    col = ns.lathe([(2.55, POOL_FLOOR - 0.05), (2.55, 2.95), (2.25, 3.35), (2.1, 3.6), (2.1, COL_TOP - 0.55),
                    (2.35, COL_TOP - 0.3), (2.35, COL_TOP)], verts=16)
    stone.append(col)
    band = C.band(2.13, 0.5, loc=(0, 0, COL_TOP - 1.25), verts=16)
    plate = ns.cyl(2.95, PLATE_TOP - COL_TOP, loc=(0, 0, (COL_TOP + PLATE_TOP) / 2), verts=16, bevel=0.08, segments=1)
    gold.append(plate)

    # water jets from the column into the basin (diagonals, so the plaque view stays clear)
    jets = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        pts = []
        for i in range(7):
            t = i / 6
            r = 2.2 + (4.75 - 2.2) * t
            z = 5.6 + 4.47 * t - 7.45 * t * t          # apex ~6.3 at t 0.3, lands just under the water
            pts.append((r * math.cos(a), r * math.sin(a), z))
        jets.append(C.pipe(pts, 0.14, sides=4))
    ns.tag(C.merge(jets, "Jets"), "Jets", "#9BE9F7", "Glass", transparency=0.35, recolor="water", cast_shadow=False,
           smooth_angle=60)

    # the giant sandwich, tilted a few degrees
    sw = sandwich()
    rot = Matrix.Rotation(math.radians(TILT[1]), 4, "Y") @ Matrix.Rotation(math.radians(TILT[0]), 4, "X")
    for col_, objs in sw.items():
        for o in objs:
            ns.apply_all(o)
            o.data.transform(Matrix.Scale(SAND_SCALE, 4))
            o.data.transform(rot)
            o.data.transform(Matrix.Translation((0, 0, PLATE_TOP - SAND_SINK)))
            o.data.update()

    # curved plaque on the basin wall front + bent brass text
    a0, a1 = -90 - PLAQUE_A, -90 + PLAQUE_A
    plq = C.arc_solid(WALL[1] - 0.05, WALL[1] + 0.16, a0, a1, 1.42, 2.82, segs=14)
    trim = [C.arc_solid(WALL[1] + 0.1, WALL[1] + 0.2, a0 - 1.2, a1 + 1.2, z0, z1, segs=12) for z0, z1 in ((1.36, 1.48),
                                                                                                         (2.76, 2.88))]
    R = WALL[1] + 0.16
    w = C.Word("STACKHOUSE · EST. 1987", 0.0, cap=0.6, spacing=1.08, base=2.12 - 0.3, res=2)
    txt = w.solid(-R - 0.03, 0.03, front_only=True, name="PlaqueText")   # single-sided letters 0.03 proud
    bend(txt, R)
    gold += trim
    C.part([plq], "Plaque", C.NAVY, smooth_angle=40)

    C.part(stone, "Stone", C.STONE, "Concrete", can_collide=True, smooth_angle=40)
    C.part(brick, "BasinWall", C.BRICK, "Brick", can_collide=True, smooth_angle=40)
    C.part([band], "ColumnBand", C.BRAND, smooth_angle=60)
    C.part(gold + [txt], "Brass", C.BRASS, "Metal", smooth_angle=40)
    names = {C.BUN: "Bun", MEAT: "Meat", C.CHEESE: "Cheese", C.TOMATO: "Tomato", C.LETTUCE: "Lettuce", SEED: "Sesame"}
    for col_, objs in sw.items():
        C.part(objs, names[col_], col_, smooth_angle=50 if col_ != C.CHEESE else 35)


META = {
    "roles": {"water": "Water (pool surface), Jets (four arcing jets)", "neon": "BasinNeon (cyan ring round the basin rim)"},
    "plaque": "STACKHOUSE · EST. 1987 (front, on the basin wall)",
    "basin_rim_height": COPE[2], "water_height": WATER_Z, "sandwich_tilt_deg": list(TILT),
    "light_hint": {"type": "PointLight", "at": "over the pool, ~1 stud above the water", "color": C.CYAN, "range": 14,
                   "brightness": 1, "sandwich": "warm SpotLight from the front at the sandwich (~12 high)"},
}

if __name__ == "__main__":
    C.run(build, "Lobby_SandwichStatue", meta=META, budget=4000, far=True, far_kw={"dist": 40.0})
