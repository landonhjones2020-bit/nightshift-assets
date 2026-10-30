"""World_PoleSign — the diner's tall roadside pole sign (~16 wide x 44 tall).

Two dark-steel poles on a concrete footing carry, from the top down:
  * a big two-sided navy sign box with a chrome rim, a hot-pink neon border tube on each
    face, chunky cream "STACKHOUSE" letters (condensed 1.6x tall) on BOTH faces with a
    cyan neon outline round every letter, and a small mustard "SANDWICHES" tagline.
    The back (+Y) face is the mirrored build, so it reads correctly from behind;
  * a curved red-orange arrow pointing down at the lot with a row of warm marquee bulbs
    (each bulb pokes out of both faces of the arrow);
  * a lower "OPEN 24 HRS" panel (navy, mustard trim, pink neon letters, both faces).
Roles: NeonPink + NeonCyan = "neon" (Neon), Bulbs = "lamp" (Neon, warm).
Front = -Y (both faces are dressed). Pivot = ground level under the poles' centre.
Sockets: Glow = 3 studs in front of the box centre, GlowBack = 3 studs behind it,
ArrowGlow = arrow centre (attach lights there).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
BOX_W, BOX_H = 16.0, 6.6
BOX_ZC = 39.7
FACE = 1.1                  # box faces at y = -FACE / +FACE
POLE_X = 2.8
TXT_W = 13.4
TXT_Z = BOX_ZC + 0.45
TXT_STRETCH = 1.6
TAG_Z = BOX_ZC - 2.05
PANEL_ZC = 26.4
PANEL_W, PANEL_H, PANEL_D = 8.8, 2.5, 1.0
ARROW_T = 0.7
STEEL = "#454A50"
LETTER = "#F3EEE2"
BULB = C.WARM_BULB


def stretch_z(obj, k, zc):
    ns.apply_all(obj)
    for v in obj.data.vertices:
        v.co.z = zc + (v.co.z - zc) * k
    obj.data.update()
    return obj


def bez(p0, p1, p2, t):
    return p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t


def bez_d(p0, p1, p2, t):
    return (p1 - p0) * 2 * (1 - t) + (p2 - p1) * 2 * t


ARROW_P = (Vector((-6.9, 34.6)), Vector((1.6, 34.4)), Vector((4.7, 29.9)))
SHAFT_W = 1.7
HEAD_W, HEAD_L = 4.3, 2.9


def arrow_outline(n=9):
    p0, p1, p2 = ARROW_P
    up, lo = [], []
    for i in range(n + 1):
        t = i / n
        c = bez(p0, p1, p2, t)
        d = bez_d(p0, p1, p2, t).normalized()
        nrm = Vector((-d.y, d.x))
        up.append(c + nrm * SHAFT_W / 2)
        lo.append(c - nrm * SHAFT_W / 2)
    d = bez_d(p0, p1, p2, 1.0).normalized()
    nrm = Vector((-d.y, d.x))
    c = p2
    head = [c + nrm * HEAD_W / 2, c + d * HEAD_L, c - nrm * HEAD_W / 2]
    # fishtail notch at the tail end
    d0 = bez_d(p0, p1, p2, 0.0).normalized()
    notch = p0 + d0 * 0.75
    pts = up + head + list(reversed(lo)) + [notch]
    pts = [(p.x, p.y) for p in pts]
    # counter-clockwise for prism()
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if area > 0 else list(reversed(pts))


def arrow_bulbs(spacing=1.05):
    """Bulb centres on the arrow's centre line at even arc-length spacing (plus two in the
    head), skipping any bulb that would touch a pole (pole r 0.6 + bulb r 0.42)."""
    p0, p1, p2 = ARROW_P
    dense = [bez(p0, p1, p2, i / 400) for i in range(401)]
    acc = [0.0]
    for a_, b_ in zip(dense[:-1], dense[1:]):
        acc.append(acc[-1] + (b_ - a_).length)
    out = []
    s_ = 0.55
    j = 0
    while s_ < acc[-1] - 0.3:
        while acc[j + 1] < s_:
            j += 1
        f = (s_ - acc[j]) / max(acc[j + 1] - acc[j], 1e-9)
        out.append(dense[j].lerp(dense[j + 1], f))
        s_ += spacing
    d = bez_d(p0, p1, p2, 1.0).normalized()
    out += [p2 + d * 0.55, p2 + d * 1.45]
    # skip bulbs where a pole crosses the arrow (their tips would poke out of the pole)
    return [p for p in out if min(abs(p.x - POLE_X), abs(p.x + POLE_X)) > 1.15]


def build():
    # footing + poles
    footing = C.box((7.8, 3.4, 1.3), loc=(0, 0, 0.6), bevel=0.1)
    C.part([footing], "Footing", C.CONCRETE, "Concrete", smooth_angle=None)
    poles = [C.lathe([(0.66, 1.0), (0.6, 1.6), (0.6, BOX_ZC - 1.0)], verts=10, loc=(sx * POLE_X, 0, 0))
             for sx in (-1, 1)]
    collars = [C.lathe([(0.85, 1.15), (0.85, 1.55), (0.62, 1.75)], verts=10, loc=(sx * POLE_X, 0, 0)) for sx in (-1, 1)]
    C.part(poles + collars, "Poles", STEEL, "Metal", smooth_angle=50)

    # sign box + chrome rim
    box = C.prism(C.rrect(BOX_W, BOX_H, 1.0, 3, 0, BOX_ZC), "y", -FACE, FACE)
    rim = C.ring_slab(C.rrect(BOX_W + 0.5, BOX_H + 0.5, 1.25, 3, 0, BOX_ZC), C.rrect(BOX_W - 0.3, BOX_H - 0.3, 0.85, 3, 0, BOX_ZC),
                      "y", -FACE - 0.16, FACE + 0.16)
    C.part([box], "Box", C.NAVY, "SmoothPlastic", smooth_angle=None)

    # letters (both faces), cyan outlines behind them, mustard tagline
    letters, outlines, tags = [], [], []
    for sgn, facing in ((-1, "-Y"), (1, "+Y")):
        lt = C.text("STACKHOUSE", 2.0, 0.34, (0, sgn * (FACE + 0.17 - 0.01), TXT_Z), width=TXT_W, res=1,
                    spacing=1.04, facing=facing, back=False)
        letters.append(stretch_z(lt, TXT_STRETCH, TXT_Z))
        ol = C.text_outline("STACKHOUSE", 2.0, 0.15 / TXT_STRETCH * 1.25, (0, sgn * (FACE + 0.04), TXT_Z), width=TXT_W,
                            res=1, spacing=1.04, facing=facing)
        outlines.append(stretch_z(ol, TXT_STRETCH, TXT_Z))
        tags.append(C.text("SANDWICHES", 0.8, 0.06, (0, sgn * (FACE + 0.03 - 0.03), TAG_Z), width=6.4, res=1,
                           spacing=1.25, facing=facing, flat=True))
    C.part(letters, "Letters", LETTER, "SmoothPlastic", smooth_angle=None)
    C.part(tags, "Tagline", C.MUSTARD, "SmoothPlastic", smooth_angle=None)

    # neon border tubes just inside the rim, both faces
    loop = C.rrect(BOX_W - 1.0, BOX_H - 1.0, 0.6, 2, 0, BOX_ZC)
    tubes = [C.pipe([(x, sgn * (FACE + 0.08), z) for x, z in loop], 0.09, sides=4, closed=True) for sgn in (-1, 1)]

    # arrow + marquee bulbs
    arrow = C.prism(arrow_outline(), "y", -ARROW_T / 2, ARROW_T / 2)
    C.part([arrow], "Arrow", C.BRAND, "SmoothPlastic", smooth_angle=None)
    bulbs = [C.bipyramid(0.42, 0.62, (p.x, 0.0, p.y), sides=6) for p in arrow_bulbs()]
    ns.tag(C.merge(bulbs, "Bulbs"), "Bulbs", BULB, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)

    # OPEN 24 HRS panel
    pz = PANEL_ZC
    panel = C.box((PANEL_W, PANEL_D, PANEL_H), loc=(0, 0, pz), bevel=0.06)
    C.part([panel], "Panel", C.NAVY_DEEP, "SmoothPlastic", smooth_angle=None)
    trim = C.ring_slab(C.rrect(PANEL_W + 0.5, PANEL_H + 0.5, 0.3, 1, 0, pz), C.rrect(PANEL_W - 0.3, PANEL_H - 0.3, 0.15, 1, 0, pz),
                       "y", -PANEL_D / 2 - 0.1, PANEL_D / 2 + 0.1)
    C.part([trim], "PanelTrim", C.MUSTARD, "SmoothPlastic", smooth_angle=None)
    open_txt = [C.text("OPEN 24 HRS", 1.0, 0.06, (0, sgn * (PANEL_D / 2 + 0.03 - 0.03 + 0.04), pz), width=7.2, res=1,
                       spacing=1.06, facing=facing, flat=True) for sgn, facing in ((-1, "-Y"), (1, "+Y"))]

    C.part([rim], "Chrome", C.CHROME, "Metal", smooth_angle=None)
    ns.tag(C.merge(tubes + open_txt, "NeonPink"), "NeonPink", C.PINK, "Neon", recolor="neon", cast_shadow=False,
           smooth_angle=None)
    ns.tag(C.merge(outlines, "NeonCyan"), "NeonCyan", C.CYAN, "Neon", recolor="neon", cast_shadow=False,
           smooth_angle=None)


def sockets():
    bl = arrow_bulbs()
    a = bl[len(bl) // 2]
    return {"Glow": ((0, -FACE - 3.0, BOX_ZC), 0.0), "GlowBack": ((0, FACE + 3.0, BOX_ZC), 180.0),
            "ArrowGlow": ((a.x, 0.0, a.y), 0.0)}


META = {"kind": "pole_sign", "pivot": "ground level under the poles' centre", "two_sided": True,
        "roles": {"neon": "NeonPink (border tubes + OPEN 24 HRS), NeonCyan (letter outlines)", "lamp": "Bulbs"},
        "light_hint": {"type": "PointLight", "at": "Socket_Glow / Socket_GlowBack", "color": C.PINK, "range": 40,
                       "brightness": 1.5}}

if __name__ == "__main__":
    C.run(build, "World_PoleSign", sockets=sockets(), meta=META)
