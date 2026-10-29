"""Cosmetic_Apron_Chef — Chef's Whites: a double-breasted chef jacket front worn in the apron
slot. Front panel from the shoulders to below the hips with a lowered neckline, an
overlapping front flap, two rows of cloth-knot buttons (cos_trim), a stand-up mandarin
collar, shoulder yokes over the torso top and a chest pen pocket.

Worn on BodyFrontAttachment (pivot = origin, body behind it along +Y). The collar wraps the
neck at radius 0.60 around the head axis (head r 0.58) and rises above the torso top only
where it is in front of the chest; at the sides it sits on the yokes.
Roles: Jacket (panel, flap, collar, yokes) = cos_body; Trim (edge piping, flap piping, buttons,
pocket welt) = cos_trim. Pens and the STACKHOUSE-red neckerchief keep fixed colours.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns

TOP = 0.97
HEM = -1.25
HW = 0.985
PIPE = 0.04
FLAP_X = 0.44
HEAD_Y = C.BODY_DEPTH / 2


def hw(z):
    if z >= C.TORSO_BOT:
        return HW
    return HW + 0.02 * (C.TORSO_BOT - z) / (C.TORSO_BOT - HEM)


def back_y(x, z):
    y = -C.APRON_GAP
    if z < C.TORSO_BOT:
        y -= 0.06 * ((C.TORSO_BOT - z) / (C.TORSO_BOT - HEM)) ** 1.5
    return y


def front_y(x, z):
    return back_y(x, z) - C.APRON_THICK


def neckline(x):
    """Top edge rises from the neckline (under the collar) to the shoulder line at the sides."""
    return 0.11 * C.smooth(abs(x) / 0.9)


ROWS = [TOP, TOP - PIPE, 0.62, 0.22, -0.20, C.TORSO_BOT, -0.95, HEM + PIPE, HEM]


FLAP_LIFT = 0.032


def flap(lift=FLAP_LIFT):
    """Overlapping front flap: top surface, a visible right edge wall and a bottom wall."""
    xl = -(HW - PIPE) + 0.01
    zs = [TOP - 0.02, 0.62, 0.22, -0.20, C.TORSO_BOT, -0.95, HEM + PIPE + 0.005]
    verts, faces = [], []
    for z in zs:
        verts += [(xl, front_y(xl, z) - lift, z), (FLAP_X, front_y(FLAP_X, z) - lift, z),
                  (FLAP_X, front_y(FLAP_X, z) + 0.004, z), (xl, front_y(xl, z) + 0.004, z)]
    for k in range(len(zs) - 1):
        L0, R0, W0 = 4 * k, 4 * k + 1, 4 * k + 2
        L1, R1, W1 = L0 + 4, R0 + 4, W0 + 4
        faces.append((L1, R1, R0, L0))          # top, facing -Y
        faces.append((R1, W1, W0, R0))          # right edge, facing +X
    n = 4 * (len(zs) - 1)
    faces.append((n + 3, n + 2, n + 1, n))      # bottom edge, facing -Z
    return C.mesh_obj("Flap", verts, faces, recalc=False, dedupe=0)


def collar(r_in=0.60, r_out=0.655, h=0.16, span=104, n=15):
    rings = []
    for i in range(n):
        th = math.radians(-span + 2 * span * i / (n - 1))
        a = abs(math.degrees(th))
        z0 = 0.99 + (1.075 - 0.99) * C.smooth((a - 24) / 16)
        z1 = z0 + h
        rd = (math.sin(th), -math.cos(th))
        prof = [(r_in, z0), (r_out, z0), (r_out, z1 - 0.03), (r_out - 0.025, z1), (r_in, z1)]
        rings.append([(rr * rd[0], HEAD_Y + rr * rd[1], zz) for rr, zz in prof])
    return C.loft("Collar", rings, "ngon", "ngon")


def flap_piping(w=0.032, lift=FLAP_LIFT + 0.006):
    """Trim piping running down the flap's free edge."""
    zs = [TOP - 0.02, 0.62, 0.22, -0.20, C.TORSO_BOT, -0.95, HEM + PIPE + 0.005]
    col = [(FLAP_X - w, FLAP_X + 0.004, z) for z in zs]
    return C.strip_quads("FlapPiping", [col], surf=front_y, lift=lift)


def button(x, z):
    y = front_y(x, z) - FLAP_LIFT
    o = ns.lathe([(0.088, 0.0), (0.086, 0.028), (0.06, 0.056), (0.0, 0.066)], verts=10, name="Button")
    o.rotation_euler = (math.radians(90), 0, 0)      # +Z -> -Y (dome faces front)
    o.location = (x, y + 0.004, z)
    ns.apply_all(o)
    return o


def build():
    dc = C.default_colours("Apron_Chef")
    panel, piping = C.apron_panel(rows=ROWS, hw_fn=hw, back_fn=back_y, top_fn=neckline, bind=PIPE, name="Panel")
    yokes = [ns.box((0.40, 0.84, 0.046), loc=(s * 0.79, 0.31, C.TORSO_TOP + 0.031), bevel=0.02, segments=1)
             for s in (-1, 1)]
    C.part([panel, flap(), collar()] + yokes, "Jacket", dc["body"], "SmoothPlastic", recolor="cos_body",
           smooth_angle=40)

    buttons = [button(sx, z) for sx in (-0.26, 0.26) for z in (0.68, 0.26, -0.16, -0.58)]
    # chest pen pocket welt (wearer's left chest, outside the flap)
    px, pz = 0.70, 0.56
    welt = C.decal("Welt", C.pocket_outline(px, pz, 0.24, 0.055, 0.02), front_y, thick=0.02, embed=0.0)
    C.part([piping, welt, flap_piping()] + buttons, "Trim", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=50)

    pen1 = C.rod((px - 0.05, front_y(px, pz) - 0.012, pz - 0.01), (px - 0.06, front_y(px, pz) - 0.012, pz + 0.2), 0.022,
                 verts=6)
    cap1 = C.rod((px - 0.06, front_y(px, pz) - 0.012, pz + 0.2), (px - 0.062, front_y(px, pz) - 0.012, pz + 0.235),
                 0.022, verts=6, r_top=0.012)
    pen2 = C.rod((px + 0.04, front_y(px, pz) - 0.014, pz - 0.01), (px + 0.055, front_y(px, pz) - 0.014, pz + 0.16),
                 0.02, verts=6)
    clip = ns.box((0.012, 0.012, 0.09), loc=(px - 0.058, front_y(px, pz) - 0.036, pz + 0.15), bevel=0.0)
    C.part([pen1, cap1], "PenBlack", "#2B2D31", "SmoothPlastic", smooth_angle=60)
    C.part(pen2, "PenRed", C.BRAND, "SmoothPlastic", smooth_angle=60)
    C.part(clip, "PenClip", "#C9CCD6", "Metal", smooth_angle=None)

    # STACKHOUSE-red neckerchief knotted at the front of the collar (fixed colour)
    yk = HEAD_Y - 0.66
    knot = ns.box((0.13, 0.07, 0.10), loc=(0.02, yk - 0.025, 1.035), bevel=0.03, segments=1)
    tails = []
    for s, tip in ((-1, (-0.13, 0.80)), (1, (0.14, 0.83))):
        outline = [(0.02 + s * 0.035, 1.03), (0.02 + s * 0.085, 1.0), (tip[0] + s * 0.03, tip[1] + 0.03), tip,
                   (tip[0] - s * 0.05, tip[1] + 0.04), (0.02 + s * 0.01, 0.99)]
        t = C.extrude(C.ccw(outline), 0.024, plane="XZ", offset=front_y(0.0, 0.9) - FLAP_LIFT - 0.03)
        tails.append(t)
    C.part([knot] + tails, "Neckerchief", C.BRAND, "SmoothPlastic", smooth_angle=50)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Apron_Chef", "Apron")
