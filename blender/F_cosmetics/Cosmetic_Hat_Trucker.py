"""Cosmetic_Hat_Trucker — a trucker cap: tall foam front panel (cos_trim) carrying a round
STACKHOUSE-style bun badge, mesh back panels (cos_body) with rows of dark perforations, a curved
visor, top button and a snapback strap over the rear opening.

Worn on HatAttachment (pivot = origin = top centre of the head; head below, front -Y). The
crown band hugs the head at z -0.31 (r 0.622 vs head r 0.58) and the crown clears the head
top by 0.12+; the visor leaves the front of the band and curves down at the sides.
Roles: Crown back, visor, button, badge disc = cos_body; Front panel, strap = cos_trim.
Badge artwork (bun, patty), the mesh perforations and the dark rear opening keep fixed colours.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

from mathutils import Vector  # noqa: E402

ns = C.ns
V = 24
BACK = [(0.622, -0.31), (0.628, -0.17), (0.618, -0.03), (0.57, 0.095), (0.47, 0.195), (0.31, 0.262),
        (0.13, 0.292)]
TOP_Z = 0.298
FRONT_HALF = 60.0          # front panel spans +-60 deg around -Y


def front_k(phi):
    """0 at the back .. 1 at the very front (-Y)."""
    return max(0.0, -math.sin(phi)) ** 2


def crown_pt(phi, k, push=0.0):
    r, z = BACK[k]
    f = front_k(phi)
    base = BACK[0][1]
    z = base + (z - base) * (1 + 0.22 * f)           # taller, more upright front panel
    if 0 < k < len(BACK) - 1:
        r += 0.03 * f * math.sin(math.pi * k / (len(BACK) - 1))
    r += push
    return (r * math.cos(phi), r * math.sin(phi), z)


def crown():
    """Outer crown + inner sweatband lip; returns (back_obj, front_obj)."""
    phis = [2 * math.pi * i / V for i in range(V)]
    verts, back_f, front_f = [], [], []
    rings = []
    for k in range(len(BACK)):
        rings.append([len(verts) + i for i in range(V)])
        verts += [crown_pt(p, k) for p in phis]
    inner = []
    for dz in (0.0, 0.10):
        inner.append([len(verts) + i for i in range(V)])
        verts += [(0.60 * math.cos(p), 0.60 * math.sin(p), BACK[0][1] + dz) for p in phis]
    apex = len(verts)
    verts.append((0, 0, TOP_Z))

    def is_front(i):
        mid = (phis[i] + math.pi / V)
        ang = math.degrees(math.atan2(math.sin(mid), math.cos(mid)))
        return abs(ang + 90) < FRONT_HALF

    for k in range(len(BACK) - 1):
        for i in range(V):
            j = (i + 1) % V
            q = (rings[k][i], rings[k][j], rings[k + 1][j], rings[k + 1][i])
            (front_f if is_front(i) else back_f).append(q)
    for i in range(V):
        j = (i + 1) % V
        (front_f if is_front(i) else back_f).append((rings[-1][i], rings[-1][j], apex))
        back_f.append((inner[0][i], inner[0][j], rings[0][j], rings[0][i]))      # bottom edge
        back_f.append((inner[1][i], inner[1][j], inner[0][j], inner[0][i]))      # sweatband
    back, front = C.split_mesh(["CrownBack", "CrownFront"], verts, [back_f, front_f])
    return back, front


def visor(nu=12, nv=4, T=0.035):
    """Curved bill: crescent leaving the front of the band, drooping at the sides."""
    top, bot = [], []
    for v in range(nv):
        tv = v / (nv - 1)
        rt, rb = [], []
        for u in range(nu):
            uu = -1 + 2 * u / (nu - 1)
            a = math.radians(72 * uu)
            L = 0.60 * (1 - uu * uu) ** 0.55 + 0.03
            r = 0.615 + L * tv
            x, y = r * math.sin(a), -r * math.cos(a)
            z = -0.295 - 0.12 * uu * uu * tv - 0.05 * tv
            rt.append((x, y, z))
            rb.append((x, y, z - T * (1 - 0.35 * tv)))
        top.append(rt)
        bot.append(rb)
    verts, faces = [], []

    def idx(grid, v, u, base):
        return base + v * nu + u

    bt = 0
    verts += [p for row in top for p in row]
    bb = len(verts)
    verts += [p for row in bot for p in row]
    for v in range(nv - 1):
        for u in range(nu - 1):
            faces.append((idx(top, v, u, bt), idx(top, v, u + 1, bt), idx(top, v + 1, u + 1, bt), idx(top, v + 1, u, bt)))
            faces.append((idx(bot, v, u, bb), idx(bot, v + 1, u, bb), idx(bot, v + 1, u + 1, bb), idx(bot, v, u + 1, bb)))
    # outer rim, side ends, inner edge
    for u in range(nu - 1):
        v = nv - 1
        faces.append((idx(top, v, u, bt), idx(top, v, u + 1, bt), idx(bot, v, u + 1, bb), idx(bot, v, u, bb)))
        faces.append((idx(top, 0, u, bt), idx(bot, 0, u, bb), idx(bot, 0, u + 1, bb), idx(top, 0, u + 1, bt)))
    for v in range(nv - 1):
        for u in (0, nu - 1):
            faces.append((idx(top, v, u, bt), idx(top, v + 1, u, bt), idx(bot, v + 1, u, bb), idx(bot, v, u, bb)))
    return C.mesh_obj("Visor", verts, faces)


def surf_pt(phi, k, push=0.0):
    """Crown surface point at fractional station k (the crown is planar between stations)."""
    k0 = min(int(k), len(BACK) - 2)
    return Vector(crown_pt(phi, k0, push)).lerp(Vector(crown_pt(phi, k0 + 1, push)), k - k0)


def perforations(size=0.036):
    """Mesh-back look: staggered rows of small dark diamond holes over the back panels."""
    a0, a1 = -90 + FRONT_HALF + 9, 270 - FRONT_HALF - 9
    verts, faces = [], []
    for row, k in enumerate((0.6, 1.45, 2.3, 3.15)):
        step = 12.5 if row < 3 else 15.0
        off = (step / 2) * (row % 2)
        ang = a0 + off
        while ang <= a1 + 1e-6:
            phi = math.radians(ang)
            c = surf_pt(phi, k, 0.005)
            up = (surf_pt(phi, k + 0.1) - surf_pt(phi, k - 0.1)).normalized()
            side = Vector((-math.sin(phi), math.cos(phi), 0))
            h = size / 2 * (0.85 if k > 3 else 1.0)
            b0 = len(verts)
            verts += [tuple(c + up * h), tuple(c + side * h * 0.8), tuple(c - up * h), tuple(c - side * h * 0.8)]
            radial = Vector((math.cos(phi), math.sin(phi), 0))
            n = Vector(verts[b0 + 1]) - Vector(verts[b0])
            m = Vector(verts[b0 + 2]) - Vector(verts[b0 + 1])
            faces.append((b0, b0 + 1, b0 + 2, b0 + 3) if n.cross(m).dot(radial) > 0 else (b0 + 3, b0 + 2, b0 + 1, b0))
            ang += step
    return C.mesh_obj("Perforations", verts, faces, recalc=False, dedupe=0)


def badge(dc):
    """Round patch on the front panel with a bun-stack icon. Returns (disc, bun, patty)."""
    phi = -math.pi / 2
    k = 2.2
    k0 = int(k)
    p = Vector(crown_pt(phi, k0)).lerp(Vector(crown_pt(phi, k0 + 1)), k - k0)
    n = Vector(crown_pt(phi, k0 + 1)) - Vector(crown_pt(phi, k0))
    n = Vector((0, -n.z, n.y)).normalized()                     # surface normal in the YZ plane
    if n.y > 0:
        n = -n
    # local frame: x along X, up along the panel, out = n
    up = Vector((0, 0, 1))
    up = (up - n * up.dot(n)).normalized()
    R = C.facing_matrix(n, up)

    def place(obj, depth):
        ns.apply_all(obj)                      # modelled facing -Y around the origin
        obj.matrix_world = R
        obj.location = p + n * depth
        ns.apply_all(obj)
        return obj

    disc = place(ns.cyl(0.165, 0.035, rot=(90, 0, 0), verts=16, bevel=0.0), 0.0)
    rim = ns.ring(0.14, 0.168, 0.014, verts=16)
    rim.rotation_euler = (math.radians(90), 0, 0)
    ring = place(rim, 0.019)
    # bun stack, front-facing extrusions in the badge plane (x across, z up)
    top_bun = [(0.10 * math.cos(math.radians(a)), 0.012 + 0.075 * math.sin(math.radians(a))) for a in range(0, 181, 30)]
    bun = [place(C.extrude(C.ccw(top_bun), 0.016, plane="XZ", offset=-0.008), 0.026),
           place(C.extrude(C.rrect(0.20, 0.04, 0.018, n=2, cy=-0.07), 0.016, plane="XZ", offset=-0.008), 0.026)]
    patty = [place(C.extrude(C.rrect(0.215, 0.042, 0.02, n=2, cy=-0.026), 0.016, plane="XZ", offset=-0.008), 0.028)]
    return [disc], ring, bun, patty


def snapback():
    """Dark rear opening (fixed) and the strap across it (trim)."""
    r = 0.632
    arch = [(0.0, -0.31)]
    for i in range(9):
        a = math.radians(180 * i / 8)
        arch.append((0.135 * math.cos(a), -0.31 + 0.15 * math.sin(a)))
    verts = [(x, math.sqrt(r * r - x * x), z) for x, z in arch]
    faces = [tuple(range(len(verts)))]
    hole = C.mesh_obj("Opening", verts, faces)
    strap_pts = []
    for x in (-0.19, -0.1, 0.0, 0.1, 0.19):
        strap_pts.append((x, math.sqrt((r + 0.012) ** 2 - x * x), -0.27))
    strap = C.strap("Strap", strap_pts, [(0, 1, 0)] * 5, 0.05, 0.02, per_seg=1)
    studs = [C.rivet((x, math.sqrt((r + 0.03) ** 2 - x * x), -0.27), normal=(x, 1, 0), r=0.017, h=0.012)
             for x in (-0.06, 0.06)]
    return hole, strap, studs


def build():
    dc = C.default_colours("Hat_Trucker")
    back, front = crown()
    button = ns.sphere(0.05, loc=(0, 0, TOP_Z), scale=(1, 1, 0.5), segs=8, rings=4, name="Button")
    disc, ring, bun, patty = badge(dc)
    C.part([back, visor(), button] + disc, "Crown", dc["body"], "SmoothPlastic", recolor="cos_body",
           smooth_angle=45)
    hole, strap, studs = snapback()
    C.part([front, ring, strap], "FrontPanel", dc["trim"], "SmoothPlastic", recolor="cos_trim", smooth_angle=45)
    C.part(bun, "BadgeBun", C.MUSTARD, "SmoothPlastic", smooth_angle=50)
    C.part(patty, "BadgePatty", "#5A2E1C", "SmoothPlastic", smooth_angle=50)
    C.part([hole, perforations()], "Holes", "#1E1F22", "SmoothPlastic", smooth_angle=None)
    C.part(studs, "Snaps", "#9AA2AA", "Metal", smooth_angle=60)


if __name__ == "__main__":
    C.run(build, "Cosmetic_Hat_Trucker", "Hat")
