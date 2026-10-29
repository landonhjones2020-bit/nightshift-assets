"""Cosmetic_Apron_Patched — the Gravedigger apron: a worn work apron with a torn, frayed hem,
sewn-on patches (cos_trim) held by dark cross-stitches (fixed colour), and loose threads.

Worn on BodyFrontAttachment (pivot = origin, body behind it along +Y). Same cut, straps,
ties, bow and bib pocket as Cosmetic_Apron; no binding along the torn hem, no pencil.
Roles: Apron = cos_body; Trim (patches, binding, straps, ties, bow, pocket) = cos_trim;
Stitches and threads keep fixed colours.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

from mathutils import Vector  # noqa: E402

PATCH_LIFT = 0.02


# hem offset at the panel's hem columns (x: dz). Positive = torn up, negative = tatter down.
TEETH = [(-1.0, -0.03), (-0.945, -0.11), (-0.63, 0.08), (-0.315, -0.15), (0.0, 0.01), (0.315, -0.12),
         (0.63, 0.07), (0.945, -0.13), (1.0, -0.04)]


def torn(x):
    """Ragged hem: piecewise-linear through TEETH (the panel samples exactly these x)."""
    if x <= TEETH[0][0]:
        return TEETH[0][1]
    for (x0, d0), (x1, d1) in zip(TEETH, TEETH[1:]):
        if x <= x1:
            return d0 + (d1 - d0) * (x - x0) / (x1 - x0)
    return TEETH[-1][1]


def patch(cx, cz, w, h, rot, cut=0.0):
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2 - cut), (w / 2 - cut, h / 2), (-w / 2, h / 2)]
    return [(cx + x, cz + z) for x, z in C.rot2(pts, rot)]


def tombstone(cx, cz, w, h, rot):
    r = w / 2
    pts = [(-r, -h / 2), (r, -h / 2), (r, h / 2 - r)]
    for i in range(1, 6):
        a = math.radians(180 * i / 6)
        pts.append((r * math.cos(a), h / 2 - r + r * math.sin(a)))
    pts.append((-r, h / 2 - r))
    return [(cx + x, cz + z) for x, z in C.rot2(pts, rot)]


def inside(pt, poly):
    x, z = pt
    c = False
    n = len(poly)
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        if (z1 > z) != (z2 > z) and x < (x2 - x1) * (z - z1) / (z2 - z1) + x1:
            c = not c
    return c


def stitches(poly, spacing=0.12, a=0.042, w=0.016, skip=()):
    """Cross-stitches straddling each edge of a patch: the half over the patch sits on the
    patch, the other half on the cloth. Returns (verts, faces) in apron space."""
    verts, faces = [], []
    pts = C.ccw(poly)
    n = len(pts)
    for e in range(n):
        if e in skip:
            continue
        p0, p1 = Vector(pts[e]), Vector(pts[(e + 1) % n])
        L = (p1 - p0).length
        t = (p1 - p0).normalized()
        nrm = Vector((t.y, -t.x))            # outward for a CCW outline
        cnt = max(1, int(L / spacing))
        for k in range(cnt):
            c = p0 + t * (L * (k + 0.5) / cnt)
            for a0, a1 in ((c - t * a - nrm * a, c + t * a + nrm * a), (c + t * a - nrm * a, c - t * a + nrm * a)):
                d = (a1 - a0).normalized()
                side = Vector((-d.y, d.x)) * (w / 2)
                quad = [a0 - side, a1 - side, a1 + side, a0 + side]
                b = len(verts)
                for q in quad:
                    lift = PATCH_LIFT + 0.004 if inside((q.x, q.y), pts) else 0.006
                    verts.append((q.x, C.apron_front_y(q.x, q.y) - lift, q.y))
                # CCW in (x, z) seen from the front -> normal -Y
                area = sum(quad[i].x * quad[(i + 1) % 4].y - quad[(i + 1) % 4].x * quad[i].y for i in range(4))
                faces.append((b, b + 1, b + 2, b + 3) if area > 0 else (b + 3, b + 2, b + 1, b))
    return verts, faces


def build():
    patches = [patch(0.40, -0.80, 0.56, 0.44, 8, cut=0.09),
               patch(-0.47, -1.36, 0.48, 0.50, -7),
               patch(-0.22, 0.58, 0.32, 0.27, 12, cut=0.06),
               tombstone(0.36, -1.50, 0.30, 0.38, 4)]
    pobj = C.flat_patches("Patches", patches, lift=PATCH_LIFT, walls=True)
    sv, sf = [], []
    for i, p in enumerate(patches):
        v, f = stitches(p, skip=(1,) if i == 2 else ((0,) if i == 3 else ()))
        off = len(sv)
        sv += v
        sf += [tuple(x + off for x in face) for face in f]
    stitch = C.mesh_obj("Stitches", sv, sf, recalc=False, dedupe=0)
    C.apron_base("Apron_Patched", hem_fn=torn, bind_bottom=False, pencil=False, hips=False, n_inner=5,
                 extra_trim=[pobj])
    C.part(stitch, "Stitches", C.STITCH_DARK, "SmoothPlastic", smooth_angle=None)
    # a few loose threads hanging from the torn hem
    threads = []
    for x, L, lean in ((-0.40, 0.15, 0.03), (0.16, 0.12, -0.02), (0.80, 0.16, 0.04)):
        z0 = C.APRON_HEM + torn(x) + 0.03
        y0 = C.apron_front_y(x, z0) + C.APRON_THICK / 2
        threads.append(C.rod((x, y0, z0), (x + lean, y0 - 0.02, z0 - L), 0.009, verts=4))
    dc = C.default_colours("Apron_Patched")
    C.part(threads, "Threads", dc["body"], "SmoothPlastic", smooth_angle=60, recolor="cos_body")


if __name__ == "__main__":
    C.run(build, "Cosmetic_Apron_Patched", "Apron")
