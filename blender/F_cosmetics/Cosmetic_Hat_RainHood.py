"""Cosmetic_Hat_RainHood — the Yellow Rain Hood (Mr. Usual's look): a puffy fisherman's
raincoat hood covering the top, back and sides of the head, soft gathers and a rolled hem
around the cinched face opening, a stiff peak over the forehead, three-panel seams over the
crown, and drawstrings with toggles hanging from metal eyelets at the chin.

Worn on HatAttachment (pivot = origin = top centre of the head; head below, front -Y). The hood
is lofted from front-to-back arch sections around the head (inner surface >= 0.05 off the
head). Its sides end at z -1.05, just above the shoulders (UpperTorso top ~ -1.09 in the hat
frame); behind the torso (y > 0.52) it drops a little lower to cover the nape.
Roles: Hood (shell, rolled hem, peak, seams) = cos_body; cords, toggles and eyelets keep fixed
colours.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

from mathutils import Vector  # noqa: E402

ns = C.ns
M = 15                     # points per arch
ZC = -0.45                 # where the arch sides turn vertical
T = 0.045                  # shell thickness
# (y, half width, top z, bottom z)
STATIONS = [(-0.645, 0.45, -0.07, -0.96),
            (-0.56, 0.645, 0.10, -1.035),
            (-0.32, 0.705, 0.15, -1.05),
            (0.00, 0.715, 0.165, -1.05),
            (0.30, 0.69, 0.14, -1.05),
            (0.50, 0.60, 0.08, -1.05),
            (0.585, 0.50, 0.02, -1.15),
            (0.69, 0.31, -0.08, -1.17),
            (0.745, 0.06, -0.18, -1.12)]


def arch(y, A, top, bot, inset=0.0, tilt=0.0):
    """Arch section at depth y: squarish (superellipse) crown, vertical sides down to bot.
    tilt pushes the top of the section forward (face openings lean forward)."""
    A, top = A - inset, top - inset
    pts = []
    for i in range(M):
        t = -1 + 2 * i / (M - 1)
        a = math.radians(125 * t)
        if abs(a) <= math.pi / 2:
            x = math.copysign(A * abs(math.sin(a)) ** 0.62, a)
            z = ZC + (top - ZC) * abs(math.cos(a)) ** 0.62
        else:
            f = (abs(a) - math.pi / 2) / math.radians(35)
            x = math.copysign(A * (1 - 0.05 * f), a)
            z = ZC - (ZC - bot) * f
        pts.append(Vector((x, y - tilt * (z - bot) / (top - bot), z)))
    return pts


def build():
    dc = C.default_colours("Hat_RainHood")
    tilts = [0.07, 0.03] + [0.0] * (len(STATIONS) - 2)
    outer = [arch(*s, tilt=tl) for s, tl in zip(STATIONS, tilts)]
    inner = [arch(*s, inset=T, tilt=tl) for s, tl in zip(STATIONS, tilts)]
    # soft gathers where the drawstring cinches the face opening (fade out going back)
    for k, amp in enumerate((0.032, 0.02, 0.007)):
        for i in range(1, M - 1):
            w = amp * math.sin(i * math.pi / 2)
            for arc in (outer[k], inner[k]):
                p = arc[i]
                n = Vector((p.x, 0, p.z - ZC)) if p.z > ZC else Vector((math.copysign(1, p.x), 0, 0))
                arc[i] = p + n.normalized() * w
    rings = [o + list(reversed(i)) for o, i in zip(outer, inner)]
    # close the back: the last section collapses onto the centre line (outer == inner)
    y_end, _, top_end, bot_end = STATIONS[-1]
    spine = arch(y_end + 0.02, 0.0, top_end - 0.06, bot_end)
    rings.append(spine + list(reversed(spine)))
    shell = C.loft("Shell", [[tuple(p) for p in r] for r in rings], "ngon", None)

    # rolled hem around the face opening
    front_o, front_i = outer[0], inner[0]
    hem_path = [tuple((a + b) / 2 + Vector((0, -0.01, 0))) for a, b in zip(front_o, front_i)]
    hem = C.cord("Hem", hem_path, 0.04, sides=6, per_seg=1)

    # stiff peak over the forehead
    sec = []
    for i in range(2, M - 2):
        p = front_o[i] + Vector((0, 0.02, 0))
        t = -1 + 2 * i / (M - 1)
        taper = max(0.0, math.cos(math.radians(125 * t) * 0.9)) ** 0.9
        radial = Vector((p.x, 0, p.z - ZC)).normalized()
        q = p + Vector((0, -0.27, -0.06)) * taper + radial * 0.07 * taper
        n = Vector((0, 0.25, 1)).normalized()
        sec.append([tuple(p + n * 0.024), tuple(q + n * 0.014), tuple(q - n * 0.014), tuple(p - n * 0.024)])
    peak = C.loft("Peak", sec, "ngon", "ngon")

    # three-panel construction: two welded seams run over the crown, front to back
    seams = []
    for i in (4, M - 5):
        path = []
        for o in outer[2:-1]:
            p = o[i]
            n = Vector((p.x, 0, p.z - ZC)).normalized()
            path.append(tuple(p + n * 0.006))
        seams.append(C.cord("Seam", path, 0.016, sides=3, per_seg=1))
    C.part([shell, hem, peak] + seams, "Hood", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=50)

    # drawstrings from eyelets at the chin, with barrel toggles
    cords, toggles, eyelets = [], [], []
    for s in (-1, 1):
        i = 1 if s < 0 else M - 2
        p = front_o[i] + Vector((0, -0.045, 0.03))
        eyelets.append(C.rivet(tuple(p), normal=(0, -1, 0), r=0.032, h=0.014))
        path = [p + Vector((0, -0.01, 0)), p + Vector((-s * 0.035, -0.045, -0.2)),
                p + Vector((-s * 0.02, -0.04, -0.4)), p + Vector((s * 0.01, -0.03, -0.52))]
        cords.append(C.cord("Cord", [tuple(v) for v in path], 0.017, sides=5, per_seg=2))
        end = path[-1]
        toggles.append(C.rod(tuple(end + Vector((0, 0, 0.02))), tuple(end + Vector((0, 0, -0.08))), 0.038, verts=8))
    C.part(cords, "Drawstrings", C.CREAM, "SmoothPlastic", smooth_angle=60)
    C.part(toggles, "Toggles", C.RUBBER, "SmoothPlastic", smooth_angle=50)
    C.part(eyelets, "Eyelets", "#B9C0C6", "Metal", smooth_angle=60)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Hat_RainHood", "Hat")
