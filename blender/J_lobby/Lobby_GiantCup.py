"""Lobby_GiantCup — giant STACKHOUSE soda cup sculpture, plaza decor (~6 wide x ~9.3 tall x 6 deep).

A tapered cream cup with a rolled rim, a red-orange logo band with mustard pinstripes and a STACKHOUSE
sandwich mark on the front, a domed lid, and a bent red-orange / cream striped straw. Decor.

Front = -Y (the logo), pivot = bottom-centre. No sockets.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns

R0, R1, H = 2.15, 2.85, 6.7      # bottom radius, top radius, body height
V = 16


def r_at(z):
    return R0 + (R1 - R0) * z / H


def taper_band(z0, z1, off=0.05):
    """Open frustum band hugging the cup wall between z0 and z1 (no hidden end caps)."""
    import bmesh
    bm = bmesh.new()
    lo = [bm.verts.new(((r_at(z0) + off) * math.cos(2 * math.pi * i / V), (r_at(z0) + off) * math.sin(2 * math.pi * i / V), z0))
          for i in range(V)]
    hi = [bm.verts.new(((r_at(z1) + off) * math.cos(2 * math.pi * i / V), (r_at(z1) + off) * math.sin(2 * math.pi * i / V), z1))
          for i in range(V)]
    for i in range(V):
        j = (i + 1) % V
        bm.faces.new([lo[i], lo[j], hi[j], hi[i]])
    bm.normal_update()
    for f in bm.faces:
        c = f.calc_center_median()
        if f.normal.dot(Vector((c.x, c.y, 0))) < 0:
            f.normal_flip()
    return C.obj_from_bm(bm, "Band")


def build():
    body = ns.lathe([(R0 - 0.1, 0.0), (R0, 0.12), (R1, H), (R1 + 0.1, H + 0.08), (R1 + 0.1, H + 0.2), (0.0, H + 0.2)], verts=V)
    lid = ns.lathe([(R1 + 0.16, H + 0.16), (R1 + 0.2, H + 0.36), (R1 - 0.05, H + 0.55), (2.1, H + 0.82), (0.9, H + 1.02),
                    (0.0, H + 1.06)], verts=V)
    band_z = (2.5, 4.5)
    band = taper_band(*band_z)
    pins = [taper_band(z, z + 0.14) for z in (band_z[0] - 0.3, band_z[1] + 0.16)]
    # logo on the band front, tilted with the cup wall
    zc = sum(band_z) / 2
    taper = math.atan((R1 - R0) / H)
    logo = C.mini_logo((0, 0, 0), r=0.82, depth=0.08, disc=C.CREAM, n=12)
    m = Matrix.Translation((0, -(r_at(zc) + 0.05) + 0.004, zc)) @ Matrix.Rotation(taper, 4, "X")   # wall faces slightly down
    for objs in logo.values():
        for o in objs:
            ns.apply_all(o)
            o.data.transform(m)
            o.data.update()
    # straw: striped, from inside the lid up and bent outward
    path = C.round_path([(0.55, 0.35, H + 0.6), (0.75, 0.45, H + 2.35), (1.45, 0.7, H + 2.75)], 0.45, segs=3)
    pts = [Vector(p) for p in path]
    straw = {C.BRAND: [], C.PAPER: []}
    seg_len = 0.62
    acc, cur, k = 0.0, [pts[0]], 0
    for a, b in zip(pts[:-1], pts[1:]):
        d = (b - a).length
        t0 = 0.0
        while acc + (d - t0) >= seg_len:
            step = seg_len - acc
            t0 += step
            q = a.lerp(b, t0 / d)
            cur.append(q)
            straw[C.BRAND if k % 2 == 0 else C.PAPER].append(C.pipe([tuple(p) for p in cur], 0.3, sides=6))
            cur, acc, k = [q], 0.0, k + 1
        acc += d - t0
        cur.append(b)
    if len(cur) > 1:
        straw[C.BRAND if k % 2 == 0 else C.PAPER].append(C.pipe([tuple(p) for p in cur], 0.3, sides=6))

    C.part([body], "Cup", C.CREAM, can_collide=True, smooth_angle=40)
    C.part([lid] + logo.pop(C.CREAM), "Lid", C.PAPER, smooth_angle=40)
    C.part([band] + straw[C.BRAND], "RedBand", C.BRAND, smooth_angle=40)
    C.part(pins, "Pinstripes", C.MUSTARD, smooth_angle=40)
    C.part(straw[C.PAPER], "StrawCream", C.PAPER, smooth_angle=50)
    names = {C.BUN: "LogoBun", C.LETTUCE: "LogoLettuce"}
    for col, objs in logo.items():
        C.part(objs, names[col], col, smooth_angle=None)


META = {"decor": "plaza cup sculpture next to benches"}

if __name__ == "__main__":
    C.run(build, "Lobby_GiantCup", meta=META, budget=700)
