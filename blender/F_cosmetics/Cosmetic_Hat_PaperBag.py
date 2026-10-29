"""Cosmetic_Hat_PaperBag — Paper Bag Head: a crinkled kraft grocery bag worn over the whole
head, with folded-in side gussets, the bag's folded bottom on top, a turned-up serrated rim,
two scissor-cut eye holes and a friendly red crayon smile (a nod to Paperface, but nice).

Worn on HatAttachment (pivot = origin = top centre of the head; head below, front -Y). The bag
is 1.35 x 1.35 and rises 0.15 above the head. Its front and back panels hang to z -1.30, in
front of / behind the torso; the side panels are notched up to z -1.03 so they rest just
above the shoulders (UpperTorso top is ~ -1.09 in the hat frame) instead of cutting into them.
Roles: Bag (bag + rim + top fold) = cos_body; eye holes, smile and cheeks keep fixed colours.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

from mathutils import Vector  # noqa: E402

N = 40
HALF = 0.675
TOP = 0.15
FRONT_BOT = -1.30
SIDE_BOT = -1.03
GUSSET = 0.07
EYE_Z = -0.47


def outline():
    """Rounded-square plan, resampled to N points of equal spacing (CCW from +X)."""
    dense = C.rrect(2 * HALF, 2 * HALF, 0.12, n=6)
    seg = [math.dist(dense[i], dense[(i + 1) % len(dense)]) for i in range(len(dense))]
    L = sum(seg)
    out, acc, k = [], 0.0, 0
    # start on the +X side centre so the side gusset folds sit on vertices
    start = min(range(len(dense)), key=lambda i: abs(dense[i][1]) + (0 if dense[i][0] > 0 else 9))
    pts = dense[start:] + dense[:start]
    seg = seg[start:] + seg[:start]
    for i in range(N):
        target = L * i / N
        while acc + seg[k] < target:
            acc += seg[k]
            k += 1
        t = (target - acc) / seg[k]
        a, b = pts[k], pts[(k + 1) % len(pts)]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def gusset(x, y):
    """Side panels fold inward along their vertical centre line (paper-bag gusset)."""
    if abs(x) > HALF - 0.02 and abs(y) < 0.5:
        return x - math.copysign(GUSSET * (1 - abs(y) / 0.5), x)
    return x


def bottom_z(x, y):
    """Front/back panels hang low; side panels are notched up to clear the shoulders."""
    side = C.smooth((0.62 - abs(y)) / 0.14)              # 1 well inside the side panels
    sideness = C.smooth((abs(x) - 0.45) / 0.2)           # only on the side faces
    return FRONT_BOT + (SIDE_BOT - FRONT_BOT) * side * sideness


def face_zone(x, y, z):
    """0 inside the front face area that carries the face (keep it smooth), else 1."""
    if y < -HALF + 0.05 and abs(x) < 0.5 and -1.0 < z < -0.25:
        return 0.15
    return 1.0


def build():
    dc = C.default_colours("Hat_PaperBag")
    rnd = random.Random(5)
    plan = outline()
    levels = [0.0, 0.17, 0.42, 0.62, 0.80, 0.93, 1.0]      # 0 = bottom edge .. 1 = top
    rings = []
    # inner lip (paper thickness at the open end)
    rings.append([(gusset(x, y) * 0.965, y * 0.965, bottom_z(x, y) + 0.004) for x, y in plan])
    for lv in levels:
        ring = []
        for x, y in plan:
            zb = bottom_z(x, y)
            z = zb + (TOP - zb) * lv
            gx = gusset(x, y) if lv < 0.97 else x - math.copysign(GUSSET * 0.5 * (1 - abs(y) / 0.5), x) * (abs(x) > HALF - 0.02 and abs(y) < 0.5)
            if lv == 1.0:
                gx, yy = gx * 0.985, y * 0.985
            else:
                yy = y
            # crinkle: push along the outward plan direction
            nrm = Vector((x, y, 0)).normalized()
            amp = 0.02 * face_zone(x, y, z) * (0.3 if lv in (0.0, 1.0) else 1.0)
            d = rnd.uniform(-amp, amp)
            ring.append((gx + nrm.x * d, yy + nrm.y * d, z + rnd.uniform(-0.012, 0.012) * (0 < lv < 1)))
        rings.append(ring)
    bag = C.loft("Bag", rings, None, "ngon")

    # turned-up rim: a band on the outside of the bottom edge with a serrated top
    cuff = []
    for k, (dz, out) in enumerate(((0.0, 0.0), (0.0, 0.026), (0.15, 0.026), (0.15, 0.0))):
        ring = []
        for i, (x, y) in enumerate(plan):
            zb = bottom_z(x, y)
            zig = (0.028 if i % 2 else -0.012) if k >= 2 else 0.0
            nrm = Vector((x, y, 0)).normalized()
            gx = gusset(x, y)
            ring.append((gx + nrm.x * (out + 0.004), y + nrm.y * (out + 0.004), zb - 0.006 + dz + zig))
        cuff.append(ring)
    cuff.append(cuff[0])
    rim = C.loft("Rim", cuff, None, None)

    # the bag's folded bottom, seen on top: a flap and a fold line
    flap = C.extrude(C.rrect(1.02, 0.46, 0.04, n=1, cy=0.12), 0.022, plane="XY", offset=TOP - 0.004)
    C.part([bag, rim, flap], "Bag", dc["body"], "SmoothPlastic", recolor="cos_body", smooth_angle=38)

    # face (fixed colours) on the front panel
    def front(x, z):
        return -HALF

    eyes = []
    for sx in (-1, 1):
        pts = []
        for i in range(12):
            a = 2 * math.pi * i / 12
            jag = 1 + (0.12 if i % 2 else -0.06) * rnd.uniform(0.5, 1)
            pts.append((sx * 0.22 + 0.085 * math.cos(a) * jag, EYE_Z + 0.105 * math.sin(a) * jag))
        eyes.append(pts)
    holes = C.flat_patches("Eyes", eyes, surf=front, lift=0.024)
    C.part(holes, "EyeHoles", "#1A1410", "SmoothPlastic", smooth_angle=None)

    smile_col = []
    for i in range(11):
        t = -1 + 2 * i / 10
        x = 0.26 * t
        z = -0.86 + 0.11 * t * t + 0.008 * math.sin(i * 2.1)
        w = 0.022 * (1 - 0.35 * t * t)
        smile_col.append((x, z, w))
    verts, faces = [], []
    for i, (x, z, w) in enumerate(smile_col):
        verts += [(x, -HALF - 0.026, z + w), (x, -HALF - 0.026, z - w)]
        if i:
            b = 2 * i
            faces.append((b - 2, b, b + 1, b - 1))
    smile = C.mesh_obj("Smile", verts, faces, recalc=False, dedupe=0)
    # make sure the strip faces front (-Y)
    smile.data.update()
    if smile.data.polygons[0].normal.y > 0:
        for p in smile.data.polygons:
            p.flip()
    C.part(smile, "Smile", "#D9302B", "SmoothPlastic", smooth_angle=None)
    cheeks = C.flat_patches("Cheeks", [C.circle2(0.07, N=8, cx=sx * 0.40, cy=-0.70, sy=0.6) for sx in (-1, 1)],
                            surf=front, lift=0.022)
    C.part(cheeks, "Cheeks", "#F28CA0", "SmoothPlastic", smooth_angle=None)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Hat_PaperBag", "Hat")
