"""Food_WrappedSandwich — the carried item: a finished sub wrapped in deli paper (A_food batch).

Paper roll-wrap along X with a crisp folded end at +X (side flaps tucked, top flap folded down),
an open, slightly flared end at -X where the sub peeks out (crust, lettuce, tomato, cheese), a
long overlap seam, and a STACKHOUSE-red sticker with a mustard ring on the front (-Y) top.
Parts: Paper, Seam (overlap seam + folded flap), Sticker, StickerRing, Crust (recolor "toast", so a
toasted order shows darker bread at the open end), Crumb, Lettuce, Tomato, Cheese.
Run:  bpyenv/bin/python blender/A_food/Food_WrappedSandwich.py   (NS_EXPORT=1 export)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
PAPER, SEAM, RED, MUSTARD = "#F4EFE2", "#E6DECB", "#E8502A", "#F2B33D"
W, H = 0.98, 0.86          # wrapped cross-section
X0, X1 = -1.12, 1.0        # open end .. folded end tip
N = 14


def section(x, w, h, z0=0.0, flare=0.0, crinkle=0.0, phase=0.0):
    """Cross-section ring (rounded rectangle, flat-ish bottom) at x."""
    pts = []
    for i in range(N):
        t = 2 * math.pi * i / N + math.pi / N
        c, s = math.cos(t), math.sin(t)
        yy = (w / 2 + flare) * C.spow(c, 2 / 3.4)
        zz = (h / 2 + flare) * C.spow(s, 2 / 3.0)
        r = 1 + crinkle * math.sin(5 * t + phase)
        pts.append((x, yy * r, z0 + h / 2 + zz * r))
    return pts


def paper():
    rings = [section(X0, W, H, flare=0.05, crinkle=0.04), section(X0 + 0.06, W, H, flare=0.02, crinkle=0.015),
             section(-0.45, W, H), section(0.45, W - 0.01, H - 0.01), section(0.8, W - 0.04, H - 0.04),
             section(0.92, W - 0.2, H - 0.2, z0=0.05)]
    tip = (X1, 0.0, 0.42)
    body = C.loft("Paper", rings, cap_start=None, cap_end="fan", end_center=tip)
    # inside of the wrap at the open end: the tube is a single outward-facing skin, so from the open end its
    # inner side was back-face culled (the sub looked unwrapped, the sticker floated). An inward-facing
    # sleeve one paper-thickness inside runs from the rim back past the sub's end, closed by a bulkhead.
    t_ = 0.012
    sleeve = C.loft("Sleeve", [section(X0, W, H, flare=0.05, crinkle=0.04),
                               section(X0 + 0.06, W - 2 * t_, H - 2 * t_, z0=t_, flare=0.02, crinkle=0.015),
                               section(-0.45, W - 2 * t_, H - 2 * t_, z0=t_)],
                    cap_start=None, cap_end="fan", end_center=(-0.45, 0.0, H / 2))
    for poly in sleeve.data.polygons:
        c, n_ = poly.center, poly.normal
        if c.x > -0.46 and abs(n_.x) > 0.9:          # bulkhead: face the opening (-X)
            want_flip = n_.x > 0
        else:                                         # sleeve wall: face the tube axis
            want_flip = n_.y * (0.0 - c.y) + n_.z * (H / 2 - c.z) < 0
        if want_flip:
            poly.flip()
    sleeve.data.update()
    p = ns.join([body, sleeve], "Paper")
    ns.tag(p, "Paper", PAPER, "SmoothPlastic", smooth_angle=32)
    # folded end: the top flap is a shell over the upper part of the end cap, creased at its edge
    last = rings[-1]
    upper = [i for i in range(N) if last[i][2] > 0.42]
    verts, faces = [], []
    tipv = Vector(tip)
    for i in upper:
        j = (i + 1) % N
        if j not in upper:
            continue
        a_, b_ = Vector(last[i]), Vector(last[j])
        nrm = (b_ - a_).cross(tipv - a_).normalized()
        if nrm.x < 0:
            nrm = -nrm
        k = len(verts)
        for v in (a_, b_, tipv + Vector((0, 0, -0.03))):
            verts.append(tuple(v + nrm * 0.012))
        faces.append((k, k + 1, k + 2))
    flap = C.mesh_obj("Flap", verts, faces, recalc=False)
    for poly in flap.data.polygons:
        if poly.normal.x < 0:
            poly.flip()
    # long overlap seam along the back-top
    tree = C.bvh(p)
    pts = [(X0 + 0.12 + (0.78 - X0 - 0.12) * t, 0.21) for t in [i / 4 for i in range(5)]]
    seam = C.surface_ribbon("Seam", tree, pts, [0.035] * 5, lift=0.012, depth=0.01)
    s = ns.join([flap, seam], "Seam")
    ns.tag(s, "Seam", SEAM, "SmoothPlastic", smooth_angle=30)
    return p, tree


def sticker(tree):
    loc, nor = C.hit(tree, -0.05, -0.3)
    disc = ns.cyl(0.19, 0.016, verts=16, bevel=0)
    ring = C.flat_ring("SR", 0.125, 0.155, 0.0, N=16)
    for o, lift in ((disc, 0.006), (ring, 0.0155)):
        ns.apply_all(o)
        q = Vector((0, 0, 1)).rotation_difference(nor)
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = q
        o.location = loc + nor * lift
        ns.apply_all(o)
    ns.tag(disc, "Sticker", RED, "SmoothPlastic", smooth_angle=40)
    ns.tag(ring, "StickerRing", MUSTARD, "SmoothPlastic", smooth_angle=40)


def roll_end(name, w, h, z0, ex, tipx, n=12, back=None):
    """Rounded end of the sub (a half capsule pointing to -X)."""
    back = back if back is not None else X0 + 0.3

    def ring(x, sc):
        out = []
        for i in range(n):
            t = 2 * math.pi * i / n + math.pi / n
            out.append((x, sc * w / 2 * C.spow(math.cos(t), 2 / ex), z0 + h / 2 + sc * h / 2 * C.spow(math.sin(t), 2 / ex)))
        return out
    rings = [ring(back, 1.0), ring(tipx + 0.09, 1.0), ring(tipx + 0.025, 0.72)]
    return C.loft(name, rings, cap_start="ngon", cap_end="fan", end_center=(tipx, 0, z0 + h / 2))


def peek():
    """The sub's end showing at the open end (-X): crusts, crumb lines and fillings."""
    tip = X0 - 0.12
    cb = roll_end("CrustB", W - 0.15, 0.26, 0.035, 2.6, tip)
    ct = roll_end("CrustT", W - 0.15, 0.36, 0.45, 2.0, tip + 0.02)
    crust = ns.join([cb, ct], "Crust")
    ns.tag(crust, "Crust", C.BREADS["white_sub"]["crust"], "SmoothPlastic", smooth_angle=60, recolor="toast")
    mb = roll_end("CrumbB", W - 0.2, 0.05, 0.255, 4.0, tip + 0.035, n=8)
    mt = roll_end("CrumbT", W - 0.2, 0.05, 0.43, 4.0, tip + 0.045, n=8)
    crumb = ns.join([mb, mt], "Crumb")
    ns.tag(crumb, "Crumb", C.BREADS["white_sub"]["crumb"], "SmoothPlastic", smooth_angle=60)
    let = C.frilly_leaf("Lettuce", 0.2, W / 2 - 0.04, N=16, frills=6, amp_z=0.025, amp_xy=0.1, thick=0.03,
                        inner=(0.6,), cup=0.0, seed=3)
    let.location = (X0 + 0.07, 0, 0.29)
    ns.apply_all(let)
    ns.tag(let, "Lettuce", "#4FB33C", "SmoothPlastic", smooth_angle=70)
    tom = roll_end("Tomato", W - 0.22, 0.06, 0.33, 4.0, tip - 0.01, n=10)
    ns.tag(tom, "Tomato", "#D92E24", "SmoothPlastic", smooth_angle=60)
    ch = roll_end("Cheese", W - 0.1, 0.035, 0.395, 6.0, tip - 0.03, n=8)
    ns.tag(ch, "Cheese", "#F7A01C", "SmoothPlastic", smooth_angle=60)


def build():
    p, tree = paper()
    sticker(tree)
    peek()
    print(C.part_tris())


if __name__ == "__main__":
    C.run(build, "Food_WrappedSandwich", meta_=None, pivot=None)
