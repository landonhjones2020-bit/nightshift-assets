"""Basement_SupportColumn — steel I-beam column holding up the diner floor.

A grey wide-flange I-beam (flanges face front and back) on a bevelled concrete footing
and a bolted steel base plate (four hex nuts), a top plate on the 11-stud ceiling, and a
hazard band at head height: the beam is mustard there with black diagonal stripes on the
flange faces and the web. Rust weeps down from the base plate bolts and the top plate.
Collides. Front faces -Y, pivot = bottom-centre. 1.2 x 11 x 1.2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
TOP = C.CEILING
FW, FT, WT = 1.0, 0.1, 0.09         # flange width, flange thickness, web thickness
DEPTH = 1.0                         # beam depth (flange outer face to outer face, along Y)
FOOT_H = 0.22
PLATE_T = 0.06
Z0 = FOOT_H + PLATE_T               # beam bottom
Z1 = TOP - PLATE_T                  # beam top
BAND = (3.1, 4.1)                   # hazard band
BEAM = C.CONCRETE                  # lighter grey: a darker Metal reads black in the basement


def h_profile():
    hy, hx = DEPTH / 2, FW / 2
    iy = hy - FT
    w = WT / 2
    return [(-hx, -hy), (hx, -hy), (hx, -iy), (w, -iy), (w, iy), (hx, iy), (hx, hy), (-hx, hy), (-hx, iy), (-w, iy),
            (-w, -iy), (-hx, -iy)]


def clip(poly, x0, x1, z0, z1):
    """Clip a convex 2D polygon to the rectangle [x0, x1] x [z0, z1] (Sutherland-Hodgman)."""
    def cut(pts, inside, inter):
        out = []
        for i in range(len(pts)):
            p, q = pts[i - 1], pts[i]
            if inside(q):
                if not inside(p):
                    out.append(inter(p, q))
                out.append(q)
            elif inside(p):
                out.append(inter(p, q))
        return out

    def ix(p, q, x):
        t = (x - p[0]) / (q[0] - p[0])
        return (x, p[1] + t * (q[1] - p[1]))

    def iz(p, q, z):
        t = (z - p[1]) / (q[1] - p[1])
        return (p[0] + t * (q[0] - p[0]), z)
    pts = poly
    for inside, inter in ((lambda p: p[0] >= x0, lambda p, q: ix(p, q, x0)), (lambda p: p[0] <= x1, lambda p, q: ix(p, q, x1)),
                          (lambda p: p[1] >= z0, lambda p, q: iz(p, q, z0)), (lambda p: p[1] <= z1, lambda p, q: iz(p, q, z1))):
        if not pts:
            break
        pts = cut(pts, inside, inter)
    return pts


def stripes_on(u0, u1, to3, facing):
    """Black 45-degree hazard stripes over the band, on a face spanning u0..u1 (u = the face's
    horizontal coordinate); to3(u, z) gives the 3D point on the decal plane."""
    out = []
    z0, z1 = BAND
    sw, step = 0.17, 0.36
    k = -6
    while k < 12:
        c = u0 + k * step
        par = [(c, z0), (c + sw, z0), (c + sw + (z1 - z0), z1), (c + (z1 - z0), z1)]
        pts = clip(par, u0, u1, z0, z1)
        if len(pts) >= 3:
            out.append(C.face_dir(C.poly([to3(u, z) for u, z in pts]), facing))
        k += 1
    return out


def build():
    foot = ns.box((1.2, 1.2, FOOT_H), loc=(0, 0, FOOT_H / 2), bevel=0.06, segments=1)
    C.part([foot], "Footing", C.CONCRETE, "Concrete", can_collide=True, smooth_angle=35)
    plates = [ns.box((1.06, 1.06, PLATE_T), loc=(0, 0, FOOT_H + PLATE_T / 2), bevel=0.0),
              ns.box((1.06, 1.06, PLATE_T), loc=(0, 0, TOP - PLATE_T / 2), bevel=0.0)]
    nuts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            # anchor nuts in the pockets beside the web, clear of the flanges
            nuts.append(ns.cyl(0.07, 0.08, loc=(sx * 0.32, sy * 0.26, Z0 + 0.04), verts=6, bevel=0.0))
    prof = h_profile()
    lower = C.prism(prof, "z", Z0, BAND[0])
    upper = C.prism(prof, "z", BAND[1], Z1)
    C.part([lower, upper] + plates + nuts, "Beam", BEAM, can_collide=True, smooth_angle=30)     # painted steel
    band = C.prism(prof, "z", BAND[0], BAND[1])
    C.part([band], "HazardBand", C.MUSTARD, can_collide=True, smooth_angle=30)

    hy = DEPTH / 2
    iy = hy - FT
    blk = []
    blk += stripes_on(-FW / 2, FW / 2, lambda u, z: (u, -hy - 0.008, z), "-Y")      # front flange
    blk += stripes_on(-FW / 2, FW / 2, lambda u, z: (-u, hy + 0.008, z), "+Y")      # back flange
    for sx in (-1, 1):                                                              # both web faces
        blk += stripes_on(-iy, iy, lambda u, z, s=sx: (s * (WT / 2 + 0.008), s * u, z), "+X" if sx > 0 else "-X")
    C.part(blk, "HazardStripes", C.INK, smooth_angle=None)

    rust = []
    for k, (x, ln) in enumerate(((-0.3, 0.9), (0.18, 0.55), (0.38, 1.2))):
        rust.append(C.streak_flat(x, Z1 - 0.02, ln, 0.12, -hy, seed=k))
    for k, (x, z) in enumerate(((-0.32, Z0 + 0.12), (0.3, Z0 + 0.18))):
        b = C.blob(0, 0, 0.12, 0, seed=30 + k)
        C.place([b], loc=(x, -hy - 0.008, z))
        rust.append(b)
    C.part(rust, "Rust", C.RUST, smooth_angle=None)


META = {"collide": "footing, beam, plates", "hazard_band": list(BAND), "top": "top plate on the 11-stud ceiling"}

if __name__ == "__main__":
    C.run(build, "Basement_SupportColumn", budget=2000, meta=META, views=((-35, 15, False), (55, 10, True)))
