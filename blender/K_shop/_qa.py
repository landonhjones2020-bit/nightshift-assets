"""QA helper (not an asset): z-fight / coplanar-overlap check for K_shop generators.

Builds an asset from its generator (no render, no export), evaluates every tagged part
(modifiers applied, world space) and reports pairs of triangles that lie in the same plane,
face the same way and overlap with positive area — they z-fight in Roblox. Also reports
the per-part triangle counts and bounding boxes.

    bpyenv/bin/python blender/K_shop/_qa.py Shop_WallTall [Shop_WallWindowTall ...]
"""
import importlib
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bpy  # noqa: E402

ns = C.ns


def _tris_world():
    dg = bpy.context.evaluated_depsgraph_get()
    out = []
    for o in ns._tagged_objects():
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        mw = o.matrix_world
        vs = [mw @ v.co for v in me.vertices]
        for lt in me.loop_triangles:
            a, b, c = (vs[i] for i in lt.vertices)
            n = (b - a).cross(c - a)
            area2 = n.length
            if area2 < 1e-9:
                continue
            n = n / area2
            out.append((o["ns_part"], (a.copy(), b.copy(), c.copy()), n.copy(), area2 / 2))
        ev.to_mesh_clear()
    return out


def _clip(poly, a, b):
    """Sutherland-Hodgman: keep the part of poly left of edge a->b (2D)."""
    def side(p):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        sp, sq = side(p), side(q)
        if sp >= 0:
            out.append(p)
        if (sp >= 0) != (sq >= 0):
            t = sp / (sp - sq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def _area(poly):
    s = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        s += x0 * y1 - x1 * y0
    return s / 2


def _proj(n):
    ax = max(range(3), key=lambda i: abs(n[i]))
    return ax, [(1, 2), (0, 2), (0, 1)][ax]


def _overlap_poly(t1, t2, n):
    ax, (u, v) = _proj(n)
    p1 = [(p[u], p[v]) for p in t1]
    p2 = [(p[u], p[v]) for p in t2]
    if _area(p1) < 0:
        p1 = p1[::-1]
    if _area(p2) < 0:
        p2 = p2[::-1]
    poly = p2
    for i in range(3):
        poly = _clip(poly, p1[i], p1[(i + 1) % 3])
        if len(poly) < 3:
            return None, 0.0
    return poly, abs(_area(poly)) / max(abs(n[ax]), 1e-6)


def _inside(pt, tri2):
    (x, y) = pt
    s = []
    for i in range(3):
        (x0, y0), (x1, y1) = tri2[i], tri2[(i + 1) % 3]
        s.append((x1 - x0) * (y - y0) - (y1 - y0) * (x - x0))
    return all(c >= -1e-7 for c in s) or all(c <= 1e-7 for c in s)


def check(min_area=2e-4, plane_eps=0.004):
    """Same-plane, same-facing, positively overlapping triangle pairs, minus the ones whose
    overlap is covered by an opposite-facing coincident face (a face pressed against another
    surface, pointing into it: never visible)."""
    tris = _tris_world()
    buckets = defaultdict(list)
    for i, (pn, t, n, a) in enumerate(tris):
        d = n.dot(t[0])
        key = (round(n.x, 2), round(n.y, 2), round(n.z, 2))
        buckets[key].append((d, i))
    for lst in buckets.values():
        lst.sort()

    def covered(poly, n, d):
        """Is the overlap's centroid covered by an opposite-facing triangle in the same plane?"""
        key = (round(-n.x, 2), round(-n.y, 2), round(-n.z, 2))
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        ax, (u, v) = _proj(n)
        for d2, i2 in buckets.get(key, []):
            if abs(-d2 - d) < plane_eps:
                t2 = tris[i2][1]
                if _inside((cx, cy), [(p[u], p[v]) for p in t2]):
                    return True
        return False

    hits = defaultdict(float)
    for key, lst in buckets.items():
        for j in range(len(lst)):
            dj, ij = lst[j]
            k = j + 1
            while k < len(lst) and lst[k][0] - dj < plane_eps:
                ik = lst[k][1]
                pa, ta, na, _ = tris[ij]
                pb, tb, nb, _ = tris[ik]
                if na.dot(nb) > 0.999:
                    shared = sum(1 for p in ta for q in tb if (p - q).length < 1e-5)
                    if shared < 3:
                        poly, ov = _overlap_poly(ta, tb, na)
                        if ov > min_area and not covered(poly, na, dj):
                            hits[tuple(sorted((pa, pb)))] += ov
                k += 1
    return hits


def _load_bshop(name):
    """B_shop generator with ITS _common (for calibration against the existing modules)."""
    import importlib.util
    saved = sys.modules.get("_common")
    sys.modules["_common"] = C.S
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "B_shop", name + ".py")
        spec = importlib.util.spec_from_file_location("bshop_" + name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.modules["_common"] = saved
    return mod


def main(names):
    for name in names:
        mod = _load_bshop(name[2:]) if name.startswith("B:") else importlib.import_module(name)
        ns.reset()
        build = getattr(mod, "build")
        build()
        tot = ns.tri_count()
        hits = check()
        print(f"== {name}: {tot} tris, {len(ns._tagged_objects())} parts")
        if not hits:
            print("   no coplanar same-facing overlaps")
        for (pa, pb), area in sorted(hits.items(), key=lambda kv: -kv[1]):
            print(f"   OVERLAP {pa} <-> {pb}: {area:.4f} sq studs")


if __name__ == "__main__":
    main(sys.argv[1:])
