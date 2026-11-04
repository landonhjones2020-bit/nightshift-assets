"""Basement_OldArcade — the broken "STACK ATTACK" arcade cabinet from the diner's heyday.

Classic upright cabinet: faded red-orange side panels (classic profile, mustard side
stripe) around a charcoal body. Marquee: "STACK / ATTACK" in raised mustard letters on a
dead dark panel, the last K hanging loose. A recessed, tilted, cracked dark screen (part
Screen, role "screen", dark Glass; pale crack lines radiate from an impact point). Control
panel: a bent joystick and three buttons with one missing. A steel coin door with two
coin slots, an "OUT OF ORDER" note taped over it, and a dark kick plate.
Body and side panels collide. Front faces -Y, pivot = bottom-centre. 2.4 x 6 x 2.6.
Socket Screen = centre of the screen face (yaw 0, the face looks forward and a little up).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
HW = 1.2                    # half width (outside of the side panels)
SIDE_T = 0.12
BODY = "#2E3036"
SCREEN = "#121823"
CRACK = "#A9B0B4"
# side profile (y, z), front = -Y
PROFILE = [(1.3, 0.0), (-0.95, 0.0), (-0.95, 2.55), (-1.3, 2.7), (-1.3, 2.95), (-0.8, 3.12), (-0.7, 3.25),
           (-0.42, 4.6), (-0.75, 4.75), (-0.75, 5.55), (-0.55, 6.0), (1.3, 6.0)]
S0, S1 = Vector((-0.7, 3.25)), Vector((-0.42, 4.6))          # screen line on the side panels
SN = Vector((-(S1 - S0).y, (S1 - S0).x)).normalized()        # outward (front) normal of the screen line
RECESS = 0.15
TILT = math.degrees(math.atan2((S1 - S0).x, (S1 - S0).y))     # screen leans back this much
CP0, CP1 = Vector((-1.3, 2.95)), Vector((-0.8, 3.12))         # control panel top line
CP_PITCH = math.degrees(math.atan2(CP1.y - CP0.y, CP1.x - CP0.x))


def on_cp(x, t, items):
    """Place objects built upright at the origin onto the control panel top at (x, t along it)."""
    p = CP0.lerp(CP1, t)
    C.place(items, loc=(x, p.x, p.y), pitch=CP_PITCH)
    return items


def build():
    # ---- body core (screen recessed between the side panels) + side panels -----------------
    s0r, s1r = S0 - SN * RECESS, S1 - SN * RECESS
    core_prof = PROFILE[:6] + [tuple(s0r), tuple(s1r)] + PROFILE[8:]
    core = C.prism(core_prof, "x", -HW + SIDE_T - 0.01, HW - SIDE_T + 0.01)
    C.part([core], "Body", BODY, can_collide=True, smooth_angle=30)
    sides = [C.prism(PROFILE, "x", -HW, -HW + SIDE_T), C.prism(PROFILE, "x", HW - SIDE_T, HW)]
    for o in sides:
        ns.bevel(o, width=0.025, segments=1, angle=40)
    C.part(sides, "SidePanels", C.BRAND, can_collide=True, smooth_angle=30)
    stripes = []
    for sx in (-1, 1):   # mustard diagonal side stripe on the outer faces
        x = sx * (HW + 0.008)
        pts = [(0.75, 0.6), (1.15, 0.6), (-0.08, 4.4), (-0.38, 4.4)]      # stays inside the panel outline
        o = C.poly([(x, y, z) for y, z in pts])
        stripes.append(C.face_dir(o, "+X" if sx > 0 else "-X"))
    C.part(stripes, "SideStripe", C.MUSTARD, smooth_angle=None)

    # ---- marquee: dead backing panel + raised STACK / ATTACK, last K hanging loose ---------------
    my = -0.75
    back = ns.box((2 * (HW - SIDE_T) - 0.06, 0.03, 0.72), loc=(0, my - 0.005, 5.15), bevel=0.0)
    C.part([back], "MarqueePanel", "#24262B", smooth_angle=None)
    w1 = C.stencil("STACK", 0.3, (0, my - 0.02, 5.34), width=1.3, depth=0.05, raised=True)
    w2 = C.stencil("ATTACK", 0.3, (0, my - 0.02, 4.96), width=1.56, depth=0.05, raised=True)
    # the last K (its own mesh island, the right-most one) hangs from its top-left screw
    ns.apply_all(w2)
    bm = bmesh.new()
    bm.from_mesh(w2.data)
    bm.verts.ensure_lookup_table()
    seen, islands = set(), []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, isl = [v], []
        seen.add(v.index)
        while stack:
            u = stack.pop()
            isl.append(u)
            for e in u.link_edges:
                w = e.other_vert(u)
                if w.index not in seen:
                    seen.add(w.index)
                    stack.append(w)
        islands.append(isl)
    kis = max(islands, key=lambda isl: sum(u.co.x for u in isl) / len(isl))
    k0 = min(u.co.x for u in kis)
    piv = Vector((k0, my, max(u.co.z for u in kis)))
    a = math.radians(-24)
    for u in kis:
        dx, dz = u.co.x - piv.x, u.co.z - piv.z
        u.co.x, u.co.z = piv.x + dx * math.cos(a) - dz * math.sin(a), piv.z + dx * math.sin(a) + dz * math.cos(a)
    bm.to_mesh(w2.data)
    bm.free()
    C.part([w1, w2], "MarqueeLetters", C.MUSTARD, smooth_angle=30)

    # ---- screen (role "screen") + cracks, in the recessed tilted screen face --------------------
    mid = (s0r + s1r) / 2
    sw, sh = 1.7, 1.12
    glass = ns.box((sw, 0.02, sh), loc=(0, 0, 0), bevel=0.0)
    cracks = []
    hit = Vector((0.32, 0.18))
    for k, (ang, ln) in enumerate(((20, 0.55), (75, 0.42), (140, 0.6), (200, 0.5), (260, 0.38), (320, 0.62))):
        aa = math.radians(ang)
        p1 = hit + Vector((math.cos(aa), math.sin(aa))) * ln
        p1.x = max(-sw / 2 + 0.03, min(sw / 2 - 0.03, p1.x))
        p1.y = max(-sh / 2 + 0.03, min(sh / 2 - 0.03, p1.y))
        kink = hit.lerp(p1, 0.5) + Vector((0.04 * math.sin(k * 2.0), 0.04 * math.cos(k * 1.3)))
        cracks.append(C.strip_xz(tuple(hit), tuple(kink), 0.022, -0.02))
        cracks.append(C.strip_xz(tuple(kink), tuple(p1), 0.016, -0.02))
    ring = [hit + Vector((math.cos(math.radians(a_)), math.sin(math.radians(a_)))) * 0.09 for a_ in range(0, 360, 60)]
    for i in range(6):
        cracks.append(C.strip_xz(tuple(ring[i]), tuple(ring[(i + 1) % 6]), 0.016, -0.028))
    for o in cracks:
        C.face_dir(o, "-Y")
    scr_loc = (0.0, mid.x + SN.x * 0.012, mid.y + SN.y * 0.012)     # SN points out of the cabinet
    C.place([glass] + cracks, loc=scr_loc, pitch=-TILT)
    C.part([glass], "Screen", SCREEN, "Glass", recolor="screen", smooth_angle=None)
    C.part(cracks, "Cracks", CRACK, smooth_angle=None)

    # ---- control panel: bent joystick, three buttons (one missing) -----------------------------
    stick = C.rod((0, 0, -0.02), (0.08, 0, 0.36), 0.035, verts=6)     # bent over to one side
    base = ns.cyl(0.1, 0.05, loc=(0, 0, 0.0), verts=8, bevel=0.0)
    ball = ns.sphere(0.11, loc=(0.085, 0, 0.42), segs=8, rings=6)
    on_cp(-0.5, 0.48, [stick, base, ball])
    C.part([ball], "StickBall", C.BRAND, smooth_angle=60)
    C.part([stick, base], "StickMetal", C.STEEL, "Metal", smooth_angle=50)
    btn_cols = {C.MUSTARD: [], C.CREAM: []}
    holes = []
    for x, col in ((0.15, C.MUSTARD), (0.45, None), (0.75, C.CREAM)):
        if col is None:   # the missing button: just its dark hole
            h = C.disc(0.085, loc=(0, 0, 0.008), verts=8)
            on_cp(x, 0.45, [h])
            holes.append(h)
            continue
        b = ns.cyl(0.085, 0.08, loc=(0, 0, 0.03), verts=8, bevel=0.015, segments=1)
        on_cp(x, 0.45, [b])
        btn_cols[col].append(b)
    for col, objs in btn_cols.items():
        C.part(objs, "Button" + ("Mustard" if col == C.MUSTARD else "Cream"), col, smooth_angle=50)

    # ---- coin door, coin slots, OUT OF ORDER note, kick plate -----------------------------------
    fy = -0.95
    door = ns.box((0.86, 0.04, 0.92), loc=(0, fy - 0.02, 1.45), bevel=0.012, segments=1)
    C.part([door], "CoinDoor", C.STEEL, "Metal", smooth_angle=40)
    slots = [ns.box((0.13, 0.03, 0.22), loc=(x, fy - 0.05, 1.68), bevel=0.0) for x in (-0.18, 0.18)]
    C.part(slots, "CoinSlots", C.BRAND, smooth_angle=None)
    holes += [C.quad_xz(x - 0.015, x + 0.015, 1.6, 1.76, fy - 0.075) for x in (-0.18, 0.18)]
    kick = ns.box((2 * (HW - SIDE_T), 0.03, 0.26), loc=(0, fy - 0.012, 0.13), bevel=0.0)
    C.part(holes + [kick], "Dark", C.DARK_VOID, smooth_angle=None)
    note = [C.quad_xz(-0.48, 0.48, -0.2, 0.2, 0.0)]
    words = [C.stencil("OUT OF", 0.12, (0, 0.0, 0.07), width=0.56),
             C.stencil("ORDER", 0.12, (0, 0.0, -0.09), width=0.56)]
    tape = [C.quad_xz(-0.56, -0.3, 0.13, 0.22, -0.008), C.quad_xz(0.3, 0.56, 0.13, 0.22, -0.008)]
    for o in note + tape:
        C.face_dir(o, "-Y")
    for grp in (note, words, tape):
        C.turn_y(grp, 7, 0.0, 0.0)
        C.place(grp, loc=(0.02, fy - 0.048, 1.32))     # 0.008 in front of the coin door
    C.part(note, "Note", C.CREAM, smooth_angle=None)
    C.part(words, "NoteInk", C.INK, smooth_angle=None)
    C.part(tape, "NoteTape", C.TAPE, smooth_angle=None)

    sockets = {"Screen": ((0.0, mid.x + SN.x * 0.022, mid.y + SN.y * 0.022), 0.0)}
    meta = {"screen": C.D.screen_meta("Screen", sw, sh), "screen_tilt_deg": round(TILT, 1),
            "collide": "body + side panels", "story": "cracked screen, bent joystick, missing button, loose K"}
    return {"export": {"sockets": sockets, "meta": meta}}


if __name__ == "__main__":
    C.run(build, "Basement_OldArcade", budget=2000, views=((-30, 18, False), (35, 12, True)))
