"""Shop_BigNeonSign — the giant STACKHOUSE neon sign over the counter (upper wall, 12 .. 20).

A deep-navy backer box (26 x 6.5) wrapped in a chrome edge, carrying chunky channel letters
"STACKHOUSE" (cream faces, Poppins Bold) traced by hot-pink neon tubes that follow every
letter outline, a cyan neon sandwich icon at the left end (bun dome with sesame dashes,
lettuce wave, filling bar, bottom bun) and small cyan neon "OPEN 24 HOURS" flanked by stars
under the lettering. Every lit part has role "neon" (LetterTubes pink; Icon, OpenText,
Border cyan) so the lighting system can flicker / kill them in blackouts.
Wall-mounted: pivot = bottom-centre of the BACK face (+Y), which sits flush on the wall;
lettering faces the room (LookVector). Socket Glow = a point 2 studs in front of the sign
centre for a PointLight / SurfaceLight.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
W, H = 26.0, 6.5
DEPTH = 0.55                    # backer box: y -DEPTH .. 0 (back face on the wall)
FY = -DEPTH                     # backer front face
LETTER_D = 0.3                  # channel letter depth (front face at FY - LETTER_D)
LFY = FY - LETTER_D
TUBE_R = 0.075
TEXT_X0, TEXT_X1 = -7.35, 12.05  # lettering block
TEXT_ZC = 3.95
STRETCH = 1.22                  # taller, sign-like letter proportions
ICON_X, ICON_Z = -10.0, 3.3
OPEN_Z = 1.25
LIFT = 0.17                     # the chrome edge reaches 0.17 below the backer: lift so its bottom is z = 0


def font_obj(txt, size=4.0, spacing=1.0, extrude=0.0, bevel=0.0, fill="BOTH", res_u=2, bev_res=0, name="Font"):
    """Text curve -> mesh standing in the XZ plane facing -Y (not yet scaled / placed)."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = txt
    cu.font = bpy.data.fonts.load(C.FONT_BOLD, check_existing=True)
    cu.size = size
    cu.space_character = spacing
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.bevel_resolution = bev_res
    cu.resolution_u = res_u
    cu.fill_mode = fill
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.active_object
    ob.rotation_euler = (math.radians(90), 0, 0)
    ns.apply_all(ob)
    return ob


def fit_pair(ref, others, x0, x1, zc, y_front, stretch=1.0):
    """Scale `ref` (and `others` with the same transform) so ref spans x0..x1, centred at zc,
    with ref's FRONT (min y) at y_front."""
    lo, hi = C.bbox_of(ref)
    s = (x1 - x0) / (hi.x - lo.x)
    c = (lo + hi) / 2
    tgt = Vector(((x0 + x1) / 2, 0, zc))
    for o in [ref] + list(others):
        for v in o.data.vertices:
            p = v.co - c
            v.co = Vector((tgt.x + p.x * s, p.y * s, tgt.z + p.z * s * stretch))
    lo, _ = C.bbox_of(ref)
    dy = y_front - lo.y
    for o in [ref] + list(others):
        for v in o.data.vertices:
            v.co.y += dy
    return s


def drop_back_caps(ob):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.normal.y > 0.95], context="FACES")
    bm.to_mesh(ob.data)
    bm.free()


def icon_tubes():
    """Cyan neon sandwich outline (XZ plane, centred on ICON_X / ICON_Z)."""
    y = FY - 0.16
    r = 0.095
    cx, cz = ICON_X, ICON_Z
    out = []
    # bun dome (closed): arc + flat base
    dome = []
    for i in range(13):
        a = math.pi * i / 12
        dome.append((cx + 1.85 * math.cos(a), y, cz + 0.55 + 1.5 * math.sin(a) ** 0.85))
    out.append(C.pipe(dome, r, sides=6, closed=True))
    # sesame dashes on the dome
    for dx, dz, ang in ((-0.85, 1.25, 25), (0.0, 1.62, 0), (0.85, 1.25, -25), (-0.4, 0.95, 10), (0.45, 0.95, -10)):
        a = math.radians(ang)
        hx, hz = 0.18 * math.cos(a), 0.18 * math.sin(a)
        out.append(C.pipe([(cx + dx - hx, y, cz + dz - hz), (cx + dx + hx, y, cz + dz + hz)], 0.075, sides=6))
    # lettuce wave (open)
    wave = [(cx - 2.1 + 4.2 * i / 16, y, cz + 0.2 + 0.16 * math.sin(i * math.pi / 2)) for i in range(17)]
    out.append(C.pipe(wave, r, sides=6))
    # filling bar (closed rounded rect)
    fill = [(x, y, z) for x, z in C.rrect(4.0, 0.42, 0.2, 2, cx, cz - 0.38)]
    out.append(C.pipe(fill, r, sides=6, closed=True))
    # bottom bun
    bot = [(x, y, z) for x, z in C.rrect(3.75, 0.72, 0.34, 2, cx, cz - 1.22)]
    out.append(C.pipe(bot, r, sides=6, closed=True))
    return out


def build():
    # backer box + chrome edge
    backer = C.prism(C.rrect(W, H, 0.85, 4, 0, H / 2), "y", FY, 0.0)
    ns.bevel(backer, width=0.05, segments=1)
    C.part([backer], "Backer", C.NAVY_DEEP, smooth_angle=40)
    edge = C.ring_slab(C.rrect(W + 0.34, H + 0.34, 1.02, 4, 0, H / 2), C.rrect(W - 0.3, H - 0.3, 0.7, 4, 0, H / 2),
                       "y", FY - 0.1, -0.02)
    ns.bevel(edge, width=0.05, segments=1)
    C.part([edge], "ChromeEdge", C.CHROME, "Metal", smooth_angle=40)

    # STACKHOUSE: cream channel letters + pink neon tubes along every outline
    letters = font_obj("STACKHOUSE", extrude=0.5, res_u=2, name="Letters")
    tubes = font_obj("STACKHOUSE", bevel=0.05, fill="NONE", res_u=2, bev_res=0, name="LetterTubes")
    s = fit_pair(letters, [tubes], TEXT_X0, TEXT_X1, TEXT_ZC, LFY, stretch=STRETCH)
    # letters: depth LETTER_D (front at LFY), back caps dropped (they sit on the backer)
    lo, hi = C.bbox_of(letters)
    k = LETTER_D / (hi.y - lo.y)
    for v in letters.data.vertices:
        v.co.y = LFY + (v.co.y - lo.y) * k
    drop_back_caps(letters)
    C.part([letters], "Letters", C.CREAM, smooth_angle=30)
    # tubes: centre plane on the letter faces, radius TUBE_R
    tl, th = C.bbox_of(tubes)
    tc = (tl.y + th.y) / 2
    kt = TUBE_R / (0.05 * s)
    for v in tubes.data.vertices:
        v.co.y = LFY + (v.co.y - tc) * kt
    ns.tag(tubes, "LetterTubes", C.PINK, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # cyan sandwich icon
    ns.tag(C.merge(icon_tubes(), "Icon"), "Icon", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # OPEN 24 HOURS (+ two stars) in small cyan neon letters
    ox = (TEXT_X0 + TEXT_X1) / 2
    op = C.text("OPEN 24 HOURS", 0.7, 0.1, (ox, FY - 0.05, OPEN_Z), width=7.6, res=1, spacing=1.12, back=False)
    stars = []
    for sx in (-1, 1):
        stars.append(C.prism(C.star(0.36, 0.15, ox + sx * 4.55, OPEN_Z), "y", FY - 0.1, FY + 0.01))
    C.part([op] + stars, "OpenText", C.CYAN, "Neon", recolor="neon", cast_shadow=False, smooth_angle=None)
    # thin cyan border tube inset from the chrome edge
    brd = [(x, FY - 0.08, z) for x, z in C.rrect(W - 1.0, H - 0.95, 0.55, 3, 0, H / 2)]
    ns.tag(C.pipe(brd, 0.055, sides=6, closed=True), "Border", C.CYAN, "Neon", recolor="neon", cast_shadow=False,
           smooth_angle=60)
    for o in ns._tagged_objects():
        o.location.z += LIFT


SOCKETS = {"Glow": ((0, -2.0, H / 2 + LIFT), 0.0)}
META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)", "size": [W + 0.34, H + 0.34, 0.93],
        "neon_parts": ["LetterTubes", "Icon", "OpenText", "Border"],
        "hang": "upper wall over the counter: pivot ~12.75 above the floor (sign spans ~12.6 .. 19.4)",
        "light_hint": {"color": C.PINK, "range": 24, "brightness": 2}}

if __name__ == "__main__":
    C.run(build, "Shop_BigNeonSign", sockets=SOCKETS, pivot=(0, 0, 0), meta=META,
          preview=lambda *a: C.front_preview(*a, backdrop=C.NAVY))
