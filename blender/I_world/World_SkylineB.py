"""World_SkylineB — second distant town cluster (~80 wide x 45 tall x 25 deep).

A different silhouette from SkylineA: a municipal water tower on four splayed, braced
legs (cone-roofed tank with a catwalk ring), a church with a square clock tower, belfry
openings, a pointed spire and a gabled nave, plus four boxy blue-grey buildings with
dark window rows and sparse warm lit windows. The clock face on the tower's front is lit
(part of Windows). Windows: Neon #FFD99A, role "lamp"; TowerLight (red, role "lamp") on
the water tower's finial. Very low detail; meant for 200-600 studs away.
Front = -Y. Pivot = ground level, centre of the footprint. Exports as 3 MeshParts.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
WIN_DARK = "#1B2130"
TOWER_GREY = "#3D4455"        # water tower (a touch lighter so the legs read)

BLOCKS = [  # (x, y, w, d, h, colour index, window kind, front lit patches)
    (-40.0, -5.0, 9.0, 9.0, 12.0, 3, "punched", [(1, 1, 0, 0)]),
    (-12.0, -5.5, 12.0, 10.0, 18.0, 2, "punched", [(2, 2, 1, 2), (3, 3, 3, 3)]),
    (26.0, 5.0, 14.0, 12.0, 24.0, 0, "ribbon", [(4, 4, 1, 3)]),
    (34.0, -5.0, 10.0, 10.0, 14.0, 1, "punched", [(0, 0, 2, 2), (2, 2, 0, 1)]),
]
WT = (-27.0, 4.0)                # water tower centre
CH = (6.0, -4.0)                 # clock tower centre


def build():
    rnd = random.Random(9)
    walls = {i: [] for i in range(4)}
    roof, tower = [], []
    dark_q, lit_q = C.QuadSet(), C.QuadSet()

    for x, y, w, d, h, ci, kind, lit in BLOCKS:
        b = C.box((w, d, h), loc=(x, y, h / 2))
        C.no_bottom(b)
        walls[ci].append(b)
        roof.append(C.box((w + 0.5, d + 0.5, 0.5), loc=(x, y, h + 0.1)))
        C.facade(dark_q, lit_q, rnd, x - w / 2, x + w / 2, 2.0, h - 1.0, y - d / 2, "-Y", kind=kind, lit_patches=lit,
                 lit_extra=0.02)
    C.facade(dark_q, lit_q, rnd, -9.5, -0.5, 2.0, 11.0, -44.5, "-X", lit_patches=[(1, 1, 1, 1)])
    C.facade(dark_q, lit_q, rnd, -10.0, 0.0, 2.0, 13.0, 39.0, "+X", lit_patches=[(0, 0, 0, 1)])
    C.facade(dark_q, lit_q, rnd, -1.0, 11.0, 15.0, 23.0, 33.0, "+X", lit_patches=[(1, 1, 2, 3)])
    roof.append(C.box((3.0, 2.5, 1.6), loc=(28.0, 7.0, 24.3 + 0.8)))
    roof.append(C.rod((21.5, 3.0, 24.3), (21.5, 3.0, 29.0), 0.12, verts=4))

    # --- water tower: splayed legs, two rings of X-bracing, tank, cone roof, catwalk ring
    wx, wy = WT
    z_tank = 23.0
    legs = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        top = (wx + 2.6 * math.cos(a), wy + 2.6 * math.sin(a), z_tank + 1.0)
        bot = (wx + 4.4 * math.cos(a), wy + 4.4 * math.sin(a), 0.0)
        legs.append((top, bot))
        tower.append(C.rod(bot, top, 0.24, verts=4))
    for zf in (0.3, 0.62):
        pts = []
        for top, bot in legs:
            pts.append(tuple(b + (t - b) * zf for t, b in zip(top, bot)))
        pts2 = []
        for top, bot in legs:
            pts2.append(tuple(b + (t - b) * (zf + 0.27) for t, b in zip(top, bot)))
        for k in range(4):
            j = (k + 1) % 4
            tower.append(C.rod(pts[k], pts2[j], 0.09, verts=3))
            tower.append(C.rod(pts[j], pts2[k], 0.09, verts=3))
    tank = C.lathe([(0.0, z_tank - 1.6), (2.4, z_tank - 0.3), (4.0, z_tank + 0.6), (4.0, z_tank + 6.0),
                    (4.2, z_tank + 6.2), (0.9, z_tank + 8.7), (0.0, z_tank + 9.0)], verts=10, loc=(wx, wy, 0))
    tower.append(tank)
    tower.append(C.ring_slab(C.circle_pts(4.7, 10, wx, wy), C.circle_pts(4.0, 10, wx, wy), "z", z_tank + 0.5,
                             z_tank + 0.75))
    tower.append(C.rod((wx, wy, z_tank + 8.9), (wx, wy, z_tank + 10.2), 0.1, verts=4))
    beacon = C.bipyramid(0.4, 0.42, (wx, wy, z_tank + 10.5), sides=6, axis="z")

    # --- church: clock tower + belfry + spire, gabled nave behind / right of it
    cx, cy = CH
    tw, th = 6.0, 26.0
    t_body = C.box((tw, tw, th), loc=(cx, cy, th / 2))
    C.no_bottom(t_body)
    walls[1].append(t_body)
    roof.append(C.box((tw + 0.7, tw + 0.7, 0.6), loc=(cx, cy, th + 0.2)))           # cornice
    belfry = C.box((tw - 0.8, tw - 0.8, 4.2), loc=(cx, cy, th + 0.5 + 2.1 - 0.05))
    walls[3].append(belfry)
    roof.append(C.box((tw + 0.3, tw + 0.3, 0.5), loc=(cx, cy, th + 4.85)))
    spire = C.lathe([(3.4, th + 5.0), (0.05, 44.0)], verts=4, loc=(cx, cy, 0), phase=45)
    roof.append(spire)
    roof.append(C.rod((cx, cy, 43.6), (cx, cy, 45.0), 0.1, verts=4))
    roof.append(C.box((0.9, 0.12, 0.12), loc=(cx, cy, 44.6)))
    # belfry openings (dark, all four sides) — arched slots as single quads + triangles
    for facing, (fx, fy) in (("-Y", (cx, cy - (tw - 0.8) / 2 - 0.05)), ("+Y", (cx, cy + (tw - 0.8) / 2 + 0.05)),
                             ("-X", (cx - (tw - 0.8) / 2 - 0.05, cy)), ("+X", (cx + (tw - 0.8) / 2 + 0.05, cy))):
        for off in (-1.1, 1.1):
            u = (fx + off, fy) if facing in ("-Y", "+Y") else (fx, fy + off)
            dark_q.add((u[0], u[1], th + 2.4), 1.3, 2.8, facing)
    # clock faces: lit disc on the front, dark disc on the -X side, hands on the lit one
    clock_z = th - 3.2
    face = C.disc(1.8, verts=10)
    face.rotation_euler = (math.radians(90), 0, 0)
    face.location = (cx, cy - tw / 2 - 0.06, clock_z)
    ring = C.ring_slab(C.circle_pts(2.2, 10, cx, clock_z), C.circle_pts(1.75, 10, cx, clock_z), "y",
                       cy - tw / 2 - 0.14, cy - tw / 2 + 0.02)
    roof.append(ring)
    hands = [C.box((0.18, 0.05, 1.3), loc=(cx, cy - tw / 2 - 0.1, clock_z + 0.55)),
             C.box((1.0, 0.05, 0.18), loc=(cx + 0.42, cy - tw / 2 - 0.1, clock_z))]
    roof.extend(hands)
    side_clock = C.disc(1.8, verts=10)
    side_clock.rotation_euler = (0, math.radians(-90), 0)
    side_clock.location = (cx - tw / 2 - 0.06, cy, clock_z)
    # tall arched window slots on the tower front (dark) + door
    dark_q.add((cx, cy - tw / 2 - 0.06, 9.0), 1.4, 6.0, "-Y")
    dark_q.add((cx, cy - tw / 2 - 0.06, 1.8), 2.0, 3.6, "-Y")
    # nave: walls + gabled roof (prism along Y)
    nx0, nx1, ny0, ny1, nh = cx + tw / 2 - 0.2, cx + tw / 2 + 9.8, cy - 1.0, cy + 15.0, 10.0
    nave = C.box((nx1 - nx0, ny1 - ny0, nh), loc=((nx0 + nx1) / 2, (ny0 + ny1) / 2, nh / 2))
    C.no_bottom(nave)
    walls[2].append(nave)
    gable = C.prism([(nx0 - 0.4, nh - 0.1), (nx1 + 0.4, nh - 0.1), ((nx0 + nx1) / 2, nh + 5.5)], "y", ny0 - 0.4,
                    ny1 + 0.4)
    roof.append(gable)
    for k in range(3):   # tall nave windows on the +X side, the first one lit
        q = lit_q if k == 0 else dark_q
        q.add((nx1 + 0.06, ny0 + 3.0 + 4.5 * k, 5.0), 1.2, 4.0, "+X")
    dark_q.add(((nx0 + nx1) / 2, ny0 - 0.06, 6.0), 2.0, 4.6, "-Y")      # rose-window-ish slot on the gable end

    for ci, objs in walls.items():
        if objs:
            C.part(objs, f"Walls{ci}", C.CITY[ci], "SmoothPlastic", smooth_angle=None)
    C.part(roof, "Roofs", C.CITY_ROOF, "SmoothPlastic", smooth_angle=None)
    C.part(tower, "WaterTower", TOWER_GREY, "SmoothPlastic", smooth_angle=None)
    dq = [o for o in (dark_q.obj("DarkA"),) if o is not None] + [side_clock]
    C.part(dq, "WindowsDark", WIN_DARK, "SmoothPlastic", smooth_angle=None)
    lq = [o for o in (lit_q.obj("LitA"),) if o is not None] + [face]
    ns.tag(C.merge(lq, "Windows"), "Windows", C.WARM_BULB, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)
    ns.tag(beacon, "TowerLight", C.AIRCRAFT_RED, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)


META = {"kind": "skyline", "pivot": "ground level, footprint centre", "view_distance": "200-600 studs",
        "roles": {"lamp": "Windows (warm lit windows + clock face), TowerLight (red, on the water tower)"}}

if __name__ == "__main__":
    C.run(build, "World_SkylineB", meta=META, sockets={"Beacon": ((WT[0], WT[1], 23.0 + 10.5), 0.0)},
          far_kw={"yaw": -15.0})
