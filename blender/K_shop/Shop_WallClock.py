"""Shop_WallClock — big diner wall clock (4 studs across, 0.5 deep).

Chrome bezel round a cream face with 12 bold tick marks (long bars at 12/3/6/9), a
red-orange STACKHOUSE wordmark, a pink neon ring inside the bezel (role neon), black hour /
minute hands, a red second hand with a counterweight and a chrome centre cap.
Hands are separate parts, all modelled pointing straight up (12 o'clock) on their own
layer in front of the face, so they can turn freely:
  HourHand (role clock_hour), MinuteHand (role clock_minute), SecondHand (role clock_second).
Socket Center = face centre (yaw 0 = facing front). Turn a hand about the socket's Z axis
(the face normal): hand.CFrame = center * CFrame.Angles(0, 0, a) * center:ToObjectSpace(rest),
where center = model:GetPivot() * Socket_Center; positive a = clockwise seen from the front.
Wall-mounted: pivot = bottom-centre of the back face (+Y, flat on the wall).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
R = 2.0                  # outer radius
RF = 1.66                # face radius
ZC = R                   # clock centre height (pivot at the bottom of the bezel)
FACE_Y = -0.24           # face plane (front)
INK = "#1A1C22"


def lathe_ring(profile, verts=20, name="LatheRing"):
    """Revolve a CLOSED (r, z) profile about Z with no end caps (a torus-like solid)."""
    import bmesh
    bm = bmesh.new()
    rings = []
    for i in range(verts):
        a = 2 * math.pi * i / verts
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
    n = len(profile)
    for i in range(verts):
        r0, r1 = rings[i], rings[(i + 1) % verts]
        for j in range(n):
            jj = (j + 1) % n
            bm.faces.new([r0[j], r1[j], r1[jj], r0[jj]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def axis_y(ob):
    """Lathe objects are built around Z: turn them to face -Y and move to the clock centre."""
    C.place(ob, (0, 0, ZC), pitch=90)
    return ob


def hand(length, w_base, w_tip, tail, y0, y1, tip_round=True):
    """Flat tapered hand pointing up (+Z) from the clock centre, with a short tail."""
    pts = [(-w_base / 2, -tail), (w_base / 2, -tail), (w_tip / 2, length - w_tip * 0.6), (0, length),
           (-w_tip / 2, length - w_tip * 0.6)]
    pts = [(x, ZC + z) for x, z in pts]
    ob = C.prism(C.fillet(pts, [0.02, 0.02, 0.02, 0.03 if tip_round else 0, 0.02], 1), "y", y0, y1)
    return ob


def build():
    # chrome bezel: rolled rim with a back flange (lathe about the clock axis)
    # (r, z) with z toward the front (axis_y turns +Z into -Y)
    bez = lathe_ring([(RF - 0.03, 0.47), (R - 0.12, 0.5), (R, 0.36), (R, 0.08), (R - 0.14, 0.0), (RF - 0.03, 0.0)],
                     verts=20)
    axis_y(bez)
    C.part([bez], "Bezel", C.CHROME, "Metal", smooth_angle=50)
    # cream face (a shallow disc set into the bezel)
    face = C.disc(RF + 0.02, verts=20)
    C.place(face, (0, FACE_Y, ZC), pitch=90)
    C.part([face], "Face", C.CREAM, smooth_angle=None)
    # pink neon ring just inside the bezel lip
    ring = ns.torus(RF - 0.08, 0.05, major_segs=20, minor_segs=4)
    C.place(ring, (0, FACE_Y - 0.06, ZC), pitch=90)
    ns.tag(ring, "NeonRing", C.PINK, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # 12 bold tick marks (single-sided quads 0.015 proud of the face; long bars at 12/3/6/9)
    import bmesh
    bm = bmesh.new()
    for i in range(12):
        big = i % 3 == 0
        w, l0, l1 = (0.22, 1.02, 1.48) if big else (0.12, 1.18, 1.48)
        a = math.radians(30 * i)
        ux, uz = math.sin(a), math.cos(a)          # radial direction
        px, pz = math.cos(a), -math.sin(a)         # perpendicular
        quad = [(ux * l0 - px * w / 2, uz * l0 - pz * w / 2), (ux * l0 + px * w / 2, uz * l0 + pz * w / 2),
                (ux * l1 + px * w / 2, uz * l1 + pz * w / 2), (ux * l1 - px * w / 2, uz * l1 - pz * w / 2)]
        vs = [bm.verts.new((x, FACE_Y - 0.015, ZC + z)) for x, z in quad]
        f = bm.faces.new(vs)
        f.normal_update()
        if f.normal.y > 0:
            f.normal_flip()
    ticks = [ns.from_bmesh(bm, "Ticks")]
    word = C.text("STACKHOUSE", 0.2, 0.03, (0, FACE_Y, ZC - 0.62), width=1.25, res=1, flat=True)
    C.part(ticks, "Ticks", INK, smooth_angle=None)
    C.part([word], "Wordmark", C.BRAND, smooth_angle=None)

    # hands (separate parts, 12 o'clock), each on its own layer in front of the face
    hh = hand(0.98, 0.17, 0.12, 0.22, FACE_Y - 0.12, FACE_Y - 0.07)
    ns.tag(hh, "HourHand", INK, recolor="clock_hour", smooth_angle=None)
    mh = hand(1.42, 0.13, 0.08, 0.28, FACE_Y - 0.18, FACE_Y - 0.13)
    ns.tag(mh, "MinuteHand", INK, recolor="clock_minute", smooth_angle=None)
    sh = C.prism([(-0.025, ZC - 0.42), (0.025, ZC - 0.42), (0.018, ZC + 1.45), (-0.018, ZC + 1.45)], "y",
                 FACE_Y - 0.23, FACE_Y - 0.2)
    cw = ns.cyl(0.09, 0.05, verts=8, bevel=0.0)           # 0.01 proud of the bar on both sides (no coplanar faces)
    C.place(cw, (0, FACE_Y - 0.215, ZC - 0.36), pitch=90)
    ns.tag(C.merge([sh, cw], "SecondHand"), "SecondHand", C.VINYL_RED, recolor="clock_second", smooth_angle=None)
    cap = ns.cyl(0.12, 0.1, verts=10, bevel=0.02, segments=1)
    C.place(cap, (0, FACE_Y - 0.29, ZC), pitch=90)
    C.part([cap], "Cap", C.CHROME, "Metal", smooth_angle=50)


def preview(asset, out_dir, res, spp):
    """Preview with the hands swung to 10:09:35 about the Center axis (restored afterwards, so
    the export keeps them at 12 o'clock) - also proves they turn about the right point."""
    from mathutils import Matrix
    c = Matrix.Translation((0, FACE_Y, ZC))
    saved = {}
    for name, deg in (("HourHand", 10 * 30 + 9 * 0.5), ("MinuteHand", 9 * 6 + 35 * 0.1), ("SecondHand", 35 * 6)):
        o = C.bpy.data.objects[name]
        saved[name] = o.matrix_world.copy()
        # clockwise seen from the front (-Y) = negative rotation about Blender -Y ... i.e. about +Y
        o.matrix_world = c @ Matrix.Rotation(math.radians(deg), 4, "Y") @ c.inverted() @ o.matrix_world
    out = C.front_preview(asset, out_dir, res, spp, backdrop=C.NAVY)
    for name, m in saved.items():
        C.bpy.data.objects[name].matrix_world = m
    return out


SOCKETS = {"Center": ((0, FACE_Y, ZC), 0.0)}
META = {"mount": "wall", "pivot": "bottom-centre of the back face (flat on the wall)", "diameter": 2 * R,
        "hands": {"HourHand": "clock_hour", "MinuteHand": "clock_minute", "SecondHand": "clock_second"},
        "hand_rest": "12 o'clock (pointing up)",
        "rotate": "about Socket_Center's Z axis (face normal): center * CFrame.Angles(0, 0, a) * "
                  "center:ToObjectSpace(restCFrame); positive a = clockwise seen from the front",
        "hang_height": 14.0}

if __name__ == "__main__":
    C.run(build, "Shop_WallClock", sockets=SOCKETS, pivot=(0, 0, 0), meta=META, preview=preview)
