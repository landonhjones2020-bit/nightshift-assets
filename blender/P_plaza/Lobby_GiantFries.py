"""Lobby_GiantFries — giant fries carton statue, plaza decor (5 x 9 x 4).

A flared red-orange fries carton (the classic scooped front rim, a taller arched back) with a cream
paper inside and rim, a big mustard STACKHOUSE star with a cream outline on the front and the back,
a mustard pinstripe near the foot, overflowing with chunky golden fries fanning out of the top -
on a small cream plinth. Same family as Lobby_GiantCup and Lobby_CondimentStatue. Carton and
plinth collide.

Front = -Y (the star), pivot = bottom-centre. No sockets.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns

PL_H = 0.6                       # plinth height
B_W, B_D, B_R = 3.0, 1.9, 0.35   # carton bottom
T_W, T_D, T_R = 4.4, 2.8, 0.55   # carton top (rim)
RIM = 6.3                        # rim height at the corners
WALL_T = 0.14
FILL_Z = 5.3                     # fries bed inside the carton
NP = 48                          # rim resolution


def rr_sample(w, d, r, n):
    """n points evenly spaced (by arc length) round a rounded rectangle, CCW seen from above,
    starting at the middle of the front (-Y) edge (so rings of equal n line up)."""
    hx, hy = w / 2 - r, d / 2 - r
    dense = [(0.0, -d / 2)]
    for cx, cy, a0 in ((hx, -hy, -90), (hx, hy, 0), (-hx, hy, 90), (-hx, -hy, 180)):
        for k in range(13):
            a = math.radians(a0 + 90 * k / 12)
            dense.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    dense.append((0.0, -d / 2))
    L = [0.0]
    for a, b in zip(dense[:-1], dense[1:]):
        L.append(L[-1] + math.dist(a, b))
    out, j = [], 0
    for k in range(n):
        t = L[-1] * k / n
        while j < len(L) - 2 and L[j + 1] < t:
            j += 1
        u = (t - L[j]) / max(1e-9, L[j + 1] - L[j])
        a, b = dense[j], dense[j + 1]
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return out


def rim_z(x, y):
    """Rim height: scooped (low in the middle) at the front, arched up at the back."""
    u = max(-1.0, min(1.0, x / (T_W / 2)))
    front = max(0.0, -y / (T_D / 2))
    back = max(0.0, y / (T_D / 2))
    return RIM - 0.75 * (1 - u * u) * front ** 2 + 0.5 * (1 - u * u) * back ** 2


def carton():
    """Outer wall (red), inner wall + rim (cream) as two objects."""
    bot = rr_sample(B_W, B_D, B_R, NP)
    top = rr_sample(T_W, T_D, T_R, NP)
    inn = rr_sample(T_W - 2 * WALL_T, T_D - 2 * WALL_T, T_R - WALL_T, NP)
    bm = bmesh.new()
    vb = [bm.verts.new((x, y, PL_H - 0.02)) for x, y in bot]
    vt = [bm.verts.new((x, y, rim_z(x, y))) for x, y in top]
    for i in range(NP):
        j = (i + 1) % NP
        bm.faces.new([vb[i], vb[j], vt[j], vt[i]])
    bm.faces.new(list(reversed(vb)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    outer = C.obj_from_bm(bm, "Outer")
    bm = bmesh.new()
    vt = [bm.verts.new((x, y, rim_z(x, y))) for x, y in top]
    vi = [bm.verts.new((x, y, rim_z(x, y) - 0.03)) for x, y in inn]
    zd = FILL_Z - 0.3
    td = (zd - PL_H) / (RIM - PL_H)
    deep = rr_sample(B_W + (T_W - B_W) * td - 2 * WALL_T, B_D + (T_D - B_D) * td - 2 * WALL_T,
                     B_R + (T_R - B_R) * td - WALL_T, NP)
    vd = [bm.verts.new((x, y, zd)) for x, y in deep]
    for i in range(NP):
        j = (i + 1) % NP
        bm.faces.new([vt[i], vt[j], vi[j], vi[i]])        # rim strip (faces up)
        bm.faces.new([vi[i], vi[j], vd[j], vd[i]])        # inner wall (faces inward)
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.z < 0.5 and f.normal.dot(Vector((-c.x, -c.y, 0))) < 0:   # inner wall must face the middle
            f.normal_flip()
        elif f.normal.z < -0.5:
            f.normal_flip()
    inner = C.obj_from_bm(bm, "Inner")
    return outer, inner


def wall_frame(z):
    """Point on the front wall centre line at height z and the wall's tilt (deg about X)."""
    y0, y1 = -B_D / 2, -T_D / 2
    z1 = rim_z(0.0, -T_D / 2)
    t = (z - PL_H) / (z1 - PL_H)
    tilt = math.degrees(math.atan2(y0 - y1, z1 - PL_H))
    return Vector((0.0, y0 + (y1 - y0) * t, z)), tilt


def on_front(objs, z, lift=0.0):
    """Move objects built in the XZ plane (back face on y = 0, facing -Y) onto the front wall."""
    p, tilt = wall_frame(z)
    M = Matrix.Translation(p + Vector((0, -lift, 0))) @ Matrix.Rotation(math.radians(-tilt), 4, "X")
    for o in objs:
        ns.apply_all(o)
        o.data.transform(M)
        o.data.update()


def build():
    plinth = C.prism(C.rrect(5.0, 4.0, 0.7, 3), "z", 0.0, PL_H)
    ns.bevel(plinth, width=0.08, segments=1)
    foot = C.prism(C.rrect(4.7, 3.7, 0.6, 3), "z", PL_H - 0.02, PL_H + 0.08)
    outer, inner = carton()
    # star: cream outline + mustard star, flat on the tilted front wall
    zc = 3.3
    rim_star = C.prism(C.star_pts(1.5, 0.72, 0, 0), "y", -0.06, 0.02)
    star = C.prism(C.star_pts(1.22, 0.55, 0, 0), "y", -0.12, -0.04)
    on_front([rim_star, star], zc)
    back = []
    for o in (rim_star, star):                        # the same star on the back wall (turned 180 deg)
        c = o.copy()
        c.data = o.data.copy()
        bpy.context.scene.collection.objects.link(c)
        c.data.transform(Matrix.Rotation(math.pi, 4, "Z"))
        c.data.update()
        back.append(c)
    # pinstripe band near the foot (follows the flare: an open frustum band just outside the wall)
    band_lo, band_hi = 1.2, 1.42
    bm = bmesh.new()
    rings = []
    for z in (band_lo, band_hi):
        t = (z - PL_H) / (RIM - PL_H)
        w = B_W + (T_W - B_W) * t + 0.03
        d = B_D + (T_D - B_D) * t + 0.03
        r = B_R + (T_R - B_R) * t
        rings.append([bm.verts.new((x, y, z)) for x, y in rr_sample(w, d, r, NP)])
    for i in range(NP):
        j = (i + 1) % NP
        bm.faces.new([rings[0][i], rings[0][j], rings[1][j], rings[1][i]])
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.dot(Vector((c.x, c.y, 0))) < 0:
            f.normal_flip()
    pin = C.obj_from_bm(bm, "Pin")

    # fries bed (lumpy golden surface inside the rim) + chunky fries fanning out
    bed = C.grid_box((3.5, 2.0, 0.3), (8, 4, 1), loc=(0, 0, FILL_Z - 0.15), bottom=False)
    C.round_box(bed, (0, 0, FILL_Z - 0.15), (1.75, 1.0, 0.15), 0.14)
    for v in bed.data.vertices:                       # round the corners in plan to follow the carton
        cx, cy = max(-1.3, min(1.3, v.co.x)), max(-0.55, min(0.55, v.co.y))
        dx, dy = v.co.x - cx, v.co.y - cy
        dl = math.hypot(dx, dy)
        if dl > 0.45:
            v.co.x, v.co.y = cx + dx / dl * 0.45, cy + dy / dl * 0.45
    bed.data.update()
    C.noise_displace(bed, amp=0.08, freq=2.2, seed=3)
    rnd = random.Random(5)
    fries = {C.FRY: [], C.FRY_DARK: []}
    spots = []
    for row, (yy, n) in enumerate(((-0.75, 5), (-0.2, 6), (0.35, 6), (0.85, 5))):
        for k in range(n):
            xx = -1.75 + 3.5 * (k + 0.5) / n + rnd.uniform(-0.15, 0.15)
            spots.append((xx, yy + rnd.uniform(-0.1, 0.1), row))
    ZR = 6.0                         # every fry crosses this plane inside the safe rim rect
    for i, (x, y, row) in enumerate(spots):
        cross = Vector((max(-1.72, min(1.72, x)), max(-0.8, min(0.8, y * 1.05)), ZR))
        d = Vector((x * 0.13 + rnd.uniform(-0.08, 0.08), y * 0.22 + rnd.uniform(-0.06, 0.06), 1.0)).normalized()
        base = cross - d * ((ZR - (FILL_Z - 1.0)) / d.z)
        top_target = rnd.uniform(7.5, 8.98) - (0.45 if row == 0 else 0.0) + (0.15 if row >= 2 else 0.0)
        top_target = min(top_target, 8.96)
        length = (top_target - base.z) / d.z
        b = ns.box((0.5, 0.5, length), loc=(0, 0, 0), bevel=0.12, segments=1)
        ns.apply_all(b)
        q = d.to_track_quat("Z", "Y")
        M = Matrix.Translation(base + d * (length / 2)) @ q.to_matrix().to_4x4() @ Matrix.Rotation(rnd.uniform(0, 1.5), 4, "Z")
        b.data.transform(M)
        b.data.update()
        fries[C.FRY_DARK if i % 4 == 1 else C.FRY].append(b)
    # one fry resting over the front rim
    lean = ns.box((0.48, 0.48, 2.3), bevel=0.12, segments=1)
    ns.apply_all(lean)
    M = Matrix.Translation((0.85, -0.95, 6.2)) @ Matrix.Rotation(math.radians(-64), 4, "X") @ Matrix.Rotation(math.radians(16), 4, "Y")
    lean.data.transform(M)
    lean.data.update()
    fries[C.FRY].append(lean)

    C.part([plinth], "Plinth", C.CREAM, can_collide=True, smooth_angle=40)
    C.part([foot], "PlinthFoot", C.CREAM_SHADE, can_collide=True, smooth_angle=40)
    C.part([outer], "Carton", C.BRAND, can_collide=True, smooth_angle=40)
    C.part([inner, rim_star, back[0]], "CartonCream", C.PAPER, smooth_angle=40)
    C.part([star, back[1], pin], "Star", C.MUSTARD, smooth_angle=None)
    C.part([bed] + fries[C.FRY], "Fries", C.FRY, smooth_angle=40)
    C.part(fries[C.FRY_DARK], "FriesToasted", C.FRY_DARK, smooth_angle=40)
    return {}


META = {"decor": "plaza fries statue (family: Lobby_GiantCup, Lobby_CondimentStatue)", "emblem": "STACKHOUSE star, front"}

if __name__ == "__main__":
    C.run(build, "Lobby_GiantFries", meta=META, budget=2000, pivot=(0.0, 0.0, 0.0))
