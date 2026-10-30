"""Shop_PottedPlant — tall monstera on a moss pole in a teal diner pot (~2.6 x 6.5 x 2.6).

Glazed teal pot with a cream rolled rim and dark soil, a coir moss pole up the middle, and
eight big split monstera leaves (V-notch fenestrations, slight midrib fold and droop, two
night-desaturated greens) on arching stems at staggered heights. Leaves are double-sided
(a back sheet 0.012 behind the front, flipped), since Roblox draws one side only.
Pivot = bottom-centre (floor prop). The pot collides (can_collide) like big furniture.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns
POT = "#2F8A88"
RIM = "#EFE6D2"
SOIL = "#3B2A20"
POLE = "#5E4630"
LEAF_A = "#4E8A3A"
LEAF_B = "#3E6B35"
STEM = "#5D8F45"
POT_H = 1.6
SOIL_Z = POT_H - 0.12

# (yaw deg, base height, base radius, pitch deg, length, half-width, tone, roll deg, notches, basal)
# leaves 1-7 climb the moss pole on short petioles; 8-9 are basal leaves on long stems from the soil
LEAVES = [
    (10, 5.5, 0.1, 58, 1.2, 0.62, LEAF_A, 0, 2, False),
    (128, 5.1, 0.1, 50, 1.45, 0.74, LEAF_B, 8, 2, False),
    (248, 4.7, 0.1, 44, 1.55, 0.8, LEAF_A, -6, 2, False),
    (58, 4.25, 0.1, 38, 1.6, 0.82, LEAF_B, -10, 2, False),
    (180, 3.8, 0.1, 32, 1.6, 0.82, LEAF_A, 6, 2, False),
    (298, 3.35, 0.1, 26, 1.6, 0.82, LEAF_B, 0, 2, False),
    (92, 2.9, 0.1, 18, 1.5, 0.78, LEAF_A, 10, 2, False),
    (215, 2.35, 0.45, 2, 1.35, 0.7, LEAF_B, -8, 2, True),
    (338, 2.15, 0.45, -6, 1.3, 0.68, LEAF_A, 6, 2, True),
]
POLE_TOP = 5.4
LEAF_SCALE = 0.9                 # keeps the foliage spread near the 2.6-3 stud footprint


def leaf_sheet(L, W, notches, fold=9.0, droop=0.26, n=5, seed=0):
    """Monstera leaf in its local frame: base at the origin, midrib along +X, face up (+Z).
    Returns a list of quads/tris (as tuples of Vectors) for the front sheet."""
    def wfun(t):
        return W * max(0.0, math.sin(math.pi * (0.12 + 0.88 * t))) ** 0.6

    def mid(t):
        return Vector((L * t, 0.0, 0.1 * L * math.sin(math.pi * t * 0.7) - droop * L * t * t))

    fr = math.radians(fold)
    polys = []
    for side in (1, -1):
        cs = [0.3 + 0.48 * k / max(1, notches - 1) for k in range(notches)] if notches > 1 else [0.5]
        cs = [c + (0.04 if side < 0 else 0.0) for c in cs]
        ts = [i / n for i in range(n + 1) if all(abs(i / n - c) > 0.06 for c in cs)]
        pts = [(t, wfun(t)) for t in ts]
        for c in cs:
            pts += [(c - 0.035, wfun(c - 0.035)), (c, wfun(c) * 0.3), (c + 0.035, wfun(c + 0.035))]
        pts.sort()
        prev = None
        for t, w in pts:
            m = mid(t)
            e = m + Vector((0.0, side * w * math.cos(fr), w * math.sin(fr)))
            if prev is not None:
                m0, e0 = prev
                if (e - m).length < 1e-5:
                    polys.append((m0, e0, m) if side > 0 else (m0, m, e0))
                else:
                    polys.append((m0, e0, e, m) if side > 0 else (m0, m, e, e0))
            prev = (m, e)
    return polys


def leaf_obj(L, W, notches, M, name="Leaf"):
    """Front + back sheets of one leaf, transformed by matrix M (local -> world)."""
    bm = bmesh.new()
    polys = leaf_sheet(L, W, notches)
    for poly in polys:
        a, b, c = poly[0], poly[1], poly[2]
        nrm = (b - a).cross(c - a)
        if nrm.z < 0:
            poly = tuple(reversed(poly))
        front = [bm.verts.new(M @ v) for v in poly]
        bm.faces.new(front)
        nloc = ((poly[1] - poly[0]).cross(poly[2] - poly[0])).normalized()
        back = [bm.verts.new(M @ (v - nloc * 0.012)) for v in reversed(poly)]
        bm.faces.new(back)
    return ns.from_bmesh(bm, name)


def build():
    # pot: glazed teal body, cream rolled rim, soil
    # the pot's inner top stays 0.04 under the soil disc (coplanar faces z-fight)
    pot = ns.lathe([(0.0, 0.05), (0.6, 0.0), (0.68, 0.06), (0.86, POT_H - 0.16), (0.8, SOIL_Z - 0.04), (0.0, SOIL_Z - 0.04)],
                   verts=12)
    C.part([pot], "Pot", POT, can_collide=True, smooth_angle=45)
    rim = C.lathe_ring([(0.83, POT_H - 0.22), (0.97, POT_H - 0.18), (0.95, POT_H), (0.8, POT_H - 0.05)], verts=12)
    C.part([rim], "PotRim", RIM, smooth_angle=45)
    soil = C.disc(0.82, loc=(0, 0, SOIL_Z), verts=12)
    C.part([soil], "Soil", SOIL, "Fabric", smooth_angle=None)
    pole = ns.cyl(0.085, POLE_TOP - SOIL_Z, loc=(0, 0, (POLE_TOP + SOIL_Z) / 2 - 0.05), verts=6, bevel=0.0)
    ns.jitter(pole, amount=0.015, seed=3)
    C.part([pole], "MossPole", POLE, "Fabric", smooth_angle=50)

    leaves = {LEAF_A: [], LEAF_B: []}
    stems = []
    for i, (yaw, hz, br, pitch, L, W, tone, roll, notches, basal) in enumerate(LEAVES):
        a = math.radians(yaw)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        base = Vector((d.x * br, d.y * br, hz))
        M = (Matrix.Translation(base) @ Matrix.Rotation(a, 4, "Z") @ Matrix.Rotation(-math.radians(pitch), 4, "Y")
             @ Matrix.Rotation(math.radians(roll), 4, "X"))
        L, W = L * LEAF_SCALE, W * LEAF_SCALE * 1.02
        leaves[tone].append(leaf_obj(L, W, notches, M))
        if basal:   # long stem from the soil, arching out to the leaf
            s0 = Vector((d.x * 0.3, d.y * 0.3, SOIL_Z - 0.02))
            s1 = Vector((d.x * 0.36, d.y * 0.36, hz - 0.35))
            pts = [s0, s1, base - (M.to_3x3() @ Vector((0.12, 0, 0))), base]
        else:       # short petiole from a node on the moss pole
            pts = [Vector((d.x * 0.08, d.y * 0.08, hz - 0.3)), Vector((d.x * 0.12, d.y * 0.12, hz - 0.08)), base]
        stems.append(C.pipe([tuple(p) for p in pts], 0.04, sides=4, cap=False))
    C.part(leaves[LEAF_A], "LeavesLight", LEAF_A, smooth_angle=40)
    C.part(leaves[LEAF_B], "LeavesDark", LEAF_B, smooth_angle=40)
    C.part(stems, "Stems", STEM, smooth_angle=60)


META = {"pivot": "bottom-centre", "mount": "floor", "collider": "Pot"}

if __name__ == "__main__":
    C.run(build, "Shop_PottedPlant", pivot=(0, 0, 0), meta=META)
