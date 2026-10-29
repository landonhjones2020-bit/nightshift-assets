"""Food_WrapPaper — a sheet of deli wrap paper lying on the wrap station (A_food batch).

2.6 x 1.7 sheet, slight paper ripple, the far edge (+Y, the end that came off the roll) curling
up; two thin STACKHOUSE-red brand stripes along the near edge. Parts: Paper, Stripes.
Run:  bpyenv/bin/python blender/A_food/Food_WrapPaper.py   (NS_EXPORT=1 export)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
PAPER, RED = "#F4EFE2", "#E8502A"
LX, LY, T = 2.6, 1.7, 0.016
CURL_START, CURL_R = 0.5, 0.2


def surface(u, v):
    """Paper midsurface: u in [-1, 1] across X, v in [-1, 1] across Y -> (x, y, z)."""
    x = u * LX / 2
    y = v * LY / 2
    z = 0.006 * math.sin(2.2 * x + 0.5) * math.cos(1.7 * y) + 0.008
    d = y - CURL_START
    if d > 0:
        a = d / CURL_R                      # wrap around a cylinder of radius CURL_R
        a = min(a, math.radians(160))
        y = CURL_START + CURL_R * math.sin(a)
        z += CURL_R * (1 - math.cos(a))
    near = -LY / 2 + 0.1
    if y < near:
        z += 0.012 * ((near - y) / 0.1) ** 2   # near edge lifts a hair
    return (x, y, z)


def sheet(nu=6, nv=14, vs=None):
    vs = vs or [-1 + 2 * j / (nv - 1) for j in range(nv)]
    us = [-1 + 2 * i / (nu - 1) for i in range(nu)]
    top, bot = {}, {}
    verts = []
    for i, u in enumerate(us):
        for j, v in enumerate(vs):
            x, y, z = surface(u, v)
            top[(i, j)] = len(verts)
            verts.append((x, y, z + T / 2))
            bot[(i, j)] = len(verts)
            verts.append((x, y, z - T / 2))
    faces = []
    nu, nv = len(us), len(vs)
    for i in range(nu - 1):
        for j in range(nv - 1):
            faces.append((top[(i, j)], top[(i + 1, j)], top[(i + 1, j + 1)], top[(i, j + 1)]))
            faces.append((bot[(i, j)], bot[(i, j + 1)], bot[(i + 1, j + 1)], bot[(i + 1, j)]))
    loop = [(i, 0) for i in range(nu - 1)] + [(nu - 1, j) for j in range(nv - 1)] + \
           [(i, nv - 1) for i in range(nu - 1, 0, -1)] + [(0, j) for j in range(nv - 1, 0, -1)]
    for k in range(len(loop)):
        a, b = loop[k], loop[(k + 1) % len(loop)]
        faces.append((top[a], bot[a], bot[b], top[b]))
    return C.mesh_obj("Paper", verts, faces, recalc=True)


# rows: sparse on the flat part, dense through the curl (v is the flat-sheet coordinate)
V_ROWS = [-1.0, -0.88, -0.5, -0.1, 0.3, 0.52, 0.59, 0.66, 0.73, 0.8, 0.87, 0.94, 1.0]


def build():
    p = sheet(nu=6, vs=V_ROWS)
    ns.tag(p, "Paper", PAPER, "SmoothPlastic", smooth_angle=50)
    tree = C.bvh(p)
    stripes = []
    for k, yv in enumerate((-LY / 2 + 0.2, -LY / 2 + 0.29)):
        pts = [(-LX / 2 + 0.06 + (LX - 0.12) * t, yv) for t in [i / 5 for i in range(6)]]
        stripes.append(C.surface_ribbon(f"St{k}", tree, pts, [0.05 if k == 0 else 0.025] * 6, lift=0.003,
                                        depth=0.004))
    s = ns.join(stripes, "Stripes")
    ns.tag(s, "Stripes", RED, "SmoothPlastic", smooth_angle=50)


if __name__ == "__main__":
    C.run(build, "Food_WrapPaper", meta_=None, pivot=None)
