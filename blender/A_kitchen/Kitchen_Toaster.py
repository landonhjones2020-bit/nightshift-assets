"""Kitchen_Toaster — 2-lane conveyor oven that sits on the worktop.

~4.4 wide x 3 deep x 2.2 tall (STYLE.md §5 "~4 x 3 x 2.2"). Two conveyor lanes side by side
run along X through a stainless chamber with a red-orange crown: sandwiches go in on the
left (-X) stub and come out on the right (+X). Lane1 is the front lane (-Y, nearest the
cook), Lane2 the back lane. The tunnel liner and the front viewing window glow orange
(Neon, role heat). The belt slats are one separate part (role belt); the client slides it
along the belt direction by (time * speed) % belt_pitch to make the belt run seamlessly.
Front faces -Y; bottom at z = 0 (place it on a worktop).

Sockets: Lane1In / Lane2In (entry stubs), Lane1Out / Lane2Out (exit stubs) = sandwich
bottom centres on the belt top, yaw 0 (sandwich along X = along the belt). Prompt = front.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402  (after bpy is loaded by _common)

ns = C.ns
HX = 1.3                     # chamber half-length (x)
HY = 1.5                     # chamber half-depth (y)
STUB = 2.2                   # belt ends at +-STUB
Z0, Z1 = 0.32, 2.05          # chamber body bottom/top (crown adds to 2.2)
BELT_TOP = 0.58
T_Y, T_Z0, T_Z1 = 1.3, 0.42, 1.78   # tunnel half-depth and z range
LANES = {1: (-1.25, -0.1), 2: (0.1, 1.25)}   # lane y ranges
PITCH = 0.2
SLAT_W = 0.08


def lane_y(i):
    a, b = LANES[i]
    return (a + b) / 2


def build():
    # ---- chamber body with the through-tunnel and the front window recess ------------
    body = ns.box((2 * HX, 2 * HY, Z1 - Z0), loc=(0, 0, (Z0 + Z1) / 2), bevel=0.0)
    ns.boolean(body, ns.box((2 * HX + 1, 2 * T_Y, T_Z1 - T_Z0), loc=(0, 0, (T_Z0 + T_Z1) / 2), bevel=0.0))
    win_x0, win_x1, win_z0, win_z1 = -1.0, 0.35, 0.72, 1.5
    ns.boolean(body, ns.box((win_x1 - win_x0, 0.24, win_z1 - win_z0), loc=((win_x0 + win_x1) / 2, -HY, (win_z0 + win_z1) / 2), bevel=0.0))
    ns.bevel(body, width=0.07, segments=2)
    C.part(body, "Body", C.STAINLESS, "Metal", smooth_angle=40)

    # ---- crown cap in the brand colour, with exhaust slots -----------------------------
    crown = ns.box((2 * HX + 0.14, 2 * HY + 0.14, 0.2), loc=(0, 0, Z1 + 0.08), bevel=0.08, segments=2)
    C.part(crown, "Crown", C.BRAND, "SmoothPlastic", smooth_angle=40)
    slots = [ns.box((1.5, 0.12, 0.04), loc=(0, -0.6 + 0.4 * k, Z1 + 0.18), bevel=0.0) for k in range(4)]

    # ---- glowing heat: tunnel liner (inward faces) + window panel -------------------
    bm = bmesh.new()
    lx, ly, lz0, lz1 = HX - 0.12, T_Y - 0.02, T_Z0 + 0.02, T_Z1 - 0.02

    def quad(a, b, c, d):
        bm.faces.new([bm.verts.new(a), bm.verts.new(b), bm.verts.new(c), bm.verts.new(d)])
    # ceiling (faces down), front wall (faces +Y), back wall (faces -Y), floor under belt (faces up).
    # Windings set so every quad faces INTO the tunnel (the walls and floor were wound outward, so
    # Roblox culled them and the tunnel showed bare metal instead of the glow).
    quad((-lx, -ly, lz1), (-lx, ly, lz1), (lx, ly, lz1), (lx, -ly, lz1))
    quad((-lx, -ly, lz1), (lx, -ly, lz1), (lx, -ly, lz0), (-lx, -ly, lz0))
    quad((lx, ly, lz1), (-lx, ly, lz1), (-lx, ly, lz0), (lx, ly, lz0))
    quad((lx, -ly, lz0), (lx, ly, lz0), (-lx, ly, lz0), (-lx, -ly, lz0))
    liner = ns.from_bmesh(bm, "Liner")
    # glowing element rods across the tunnel ceiling
    # rods run wall to wall (they stopped 0.05 short of the liner walls, hanging in the air)
    rods = [C.rod((x, -ly - 0.01, lz1 - 0.07), (x, ly + 0.01, lz1 - 0.07), 0.04, verts=6) for x in (-0.75, -0.25, 0.25, 0.75)]
    win = ns.box((win_x1 - win_x0 - 0.04, 0.04, win_z1 - win_z0 - 0.04), loc=((win_x0 + win_x1) / 2, -HY + 0.1, (win_z0 + win_z1) / 2), bevel=0.0)
    C.part([liner, win], "Heat", C.HEAT, "Neon", recolor="heat", cast_shadow=False, smooth_angle=None)

    # window grille bars + element rods + exhaust slots (dark)
    bars = [ns.box((win_x1 - win_x0, 0.05, 0.05), loc=((win_x0 + win_x1) / 2, -HY + 0.02, z), bevel=0.0)
            for z in (0.98, 1.24)]
    C.part(bars + slots, "Grille", C.GUNMETAL, "Metal", smooth_angle=None)
    C.part(rods, "Elements", "#FFB25C", "Neon", recolor="heat_elements", cast_shadow=False)

    # ---- conveyor frame: bed, side guides, lane divider, end rollers, legs ------------
    frame = [ns.box((2 * STUB, 2 * T_Y + 0.1, 0.12), loc=(0, 0, BELT_TOP - 0.11), bevel=0.03, segments=1)]
    for sy in (-1, 1):
        frame.append(ns.box((2 * STUB, 0.1, 0.2), loc=(0, sy * (T_Y + 0.0), BELT_TOP + 0.02), bevel=0.035, segments=1))
    frame.append(ns.box((2 * STUB - 0.1, 0.07, 0.12), loc=(0, 0, BELT_TOP + 0.05), bevel=0.025, segments=1))
    for sx in (-1, 1):
        frame.append(C.rod((sx * STUB, -T_Y - 0.06, BELT_TOP - 0.09), (sx * STUB, T_Y + 0.06, BELT_TOP - 0.09), 0.1, verts=12))
        for sy in (-1, 1):
            # stub legs kept inside x = +-1.8 so they stand on a 4-wide Kitchen_Worktop
            frame.append(ns.box((0.14, 0.14, BELT_TOP - 0.15), loc=(sx * (STUB - 0.45), sy * (T_Y - 0.05), (BELT_TOP - 0.15) / 2),
                                bevel=0.03, segments=1))
            # chunky feet under the chamber body itself
            frame.append(ns.box((0.3, 0.3, Z0 + 0.02), loc=(sx * (HX - 0.25), sy * (HY - 0.25), (Z0 + 0.02) / 2),
                                bevel=0.05, segments=1))
    # exit end-stop lip so sandwiches don't ride off the end
    frame.append(ns.box((0.08, 2 * T_Y, 0.16), loc=(STUB + 0.12, 0, BELT_TOP + 0.02), bevel=0.03, segments=1))
    C.part(frame, "Frame", C.STEEL_DARK, "Metal", smooth_angle=40)

    # ---- the belt: flat slats across each lane, one pitch short of the full run --------
    bm = bmesh.new()
    x = -STUB + 0.05
    count = 0
    while x <= STUB - 0.05 - PITCH + 1e-6:
        for i in (1, 2):
            y0, y1 = LANES[i]
            a, b, z0, z1 = x - SLAT_W / 2, x + SLAT_W / 2, BELT_TOP - 0.04, BELT_TOP
            v = [bm.verts.new(p) for p in ((a, y0, z0), (a, y0, z1), (b, y0, z1), (b, y0, z0),
                                            (a, y1, z0), (a, y1, z1), (b, y1, z1), (b, y1, z0))]
            bm.faces.new([v[1], v[5], v[6], v[2]])   # top
            bm.faces.new([v[0], v[4], v[5], v[1]])   # -X side
            bm.faces.new([v[3], v[2], v[6], v[7]])   # +X side
        x += PITCH
        count += 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    belt = ns.from_bmesh(bm, "Belt")
    C.part(belt, "Belt", "#A9B1B8", "Metal", recolor="belt", smooth_angle=None)

    # ---- controls: two chunky knobs + a ready lamp on the front panel -----------------
    knobs, pointers = [], []
    for z in (1.42, 0.9):
        knobs.append(ns.cyl(0.17, 0.1, loc=(0.82, -HY - 0.05, z), rot=(90, 0, 0), verts=12, bevel=0.035, segments=1))
        pointers.append(ns.box((0.04, 0.04, 0.12), loc=(0.82, -HY - 0.11, z + 0.07), bevel=0.0))
    C.part(knobs, "Knobs", C.CHARCOAL, "SmoothPlastic", smooth_angle=45)
    lamp = ns.cyl(0.07, 0.06, loc=(1.12, -HY - 0.03, 1.68), rot=(90, 0, 0), verts=10, bevel=0.02, segments=1)
    C.part(pointers + [lamp], "Indicators", C.MUSTARD, "SmoothPlastic", recolor="ready_lamp")

    ex = 1.25          # In/Out sandwich centres (sandwich 2.2 long: just inside the stub ends)
    sockets = {
        "Lane1In": ((-ex, lane_y(1), BELT_TOP), 0), "Lane1Out": ((ex, lane_y(1), BELT_TOP), 0),
        "Lane2In": ((-ex, lane_y(2), BELT_TOP), 0), "Lane2Out": ((ex, lane_y(2), BELT_TOP), 0),
        "Prompt": ((0, -HY - 0.3, 1.2), 0),
    }
    meta = {
        "belt_pitch": PITCH,
        "belt_part": "Belt",
        "belt_dir": [-1, 0, 0],        # Roblox model space: Blender +X (in -> out) = Roblox -X
        "belt_top": BELT_TOP,
        "lanes": {"Lane1": "front (-Z side, nearest the cook)", "Lane2": "back"},
        "tunnel_clearance": round(T_Z1 - BELT_TOP, 3),
        "slat_rows": count,
    }
    # pivot = bottom-centre of the chamber, so it centres on Kitchen_Worktop's Top socket
    return {"export": {"sockets": sockets, "meta": meta, "pivot": (0, 0, 0)}}


if __name__ == "__main__":
    C.run(build, "Kitchen_Toaster")
