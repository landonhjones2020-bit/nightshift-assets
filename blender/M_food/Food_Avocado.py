"""Food_Avocado — fanned avocado slices (M_food batch).

Six crescent slices laid across the roll, all curving the same way and fanned along X: each one
leans its skin edge on the previous slice's pit side, so every dark skin edge stays in view. The
flesh fades from green at the skin to pale yellow-green toward the pit side (three bands).
Parts: Skin (thin dark edge + skin wall), FleshOuter, FleshMid, FleshInner (also the pit-side wall).
Run:  bpyenv/bin/python blender/M_food/Food_Avocado.py   (NS_EXPORT=1 export, NS_ICON=1 icon)
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns
SKIN, OUTER, MID, INNER = "#2C4A1C", "#9BCF5A", "#B9DB72", "#D7E68A"
BANDS = (0.0, 0.38, 0.7, 0.92, 1.0)        # across the slice: 0 = pit edge .. 1 = skin edge
BAND_PART = ("FleshInner", "FleshMid", "FleshOuter", "Skin")
L, T0, BOW, H = 0.86, 0.32, 0.2, 0.07


def crescent(rnd, L=L, T0=T0, bow=BOW, h=H, nV=9):
    """One slice in local coords: long axis along Y, bowing toward -X (the skin side), pointed tips,
    flat bottom at z 0. Returns {part name: object}."""
    V, faces = [], {p: [] for p in BAND_PART}
    top, pit_b, skin_b, centre = {}, [], [], []
    wob = rnd.uniform(0, 6.28)
    for iv in range(nV):
        v = -1 + 2 * iv / (nV - 1)
        y = L / 2 * v * (1 + 0.02 * math.sin(3 * v + wob))
        xc = -bow * (1 - v * v)
        k = max(0.0, 1 - v * v)
        T = T0 * k ** 0.55
        taper = k ** 0.35
        centre.append(Vector((xc, y, h * 0.5)))
        tip = iv in (0, nV - 1)
        for ic, s in enumerate(BANDS):
            if tip and ic > 0:
                top[(iv, ic)] = top[(iv, 0)]
                continue
            x = xc + T / 2 - T * s
            edge = 0.8 if s in (0.0, 1.0) else 1.0 - 0.05 * abs(s - 0.6)
            V.append((x, y, h * (0.4 + 0.6 * taper) * edge))
            top[(iv, ic)] = len(V) - 1
        if tip:
            V.append((xc, y, 0.0))
            pit_b.append(len(V) - 1)
            skin_b.append(len(V) - 1)
        else:
            V.append((xc + T / 2, y, 0.0))
            pit_b.append(len(V) - 1)
            V.append((xc - T / 2, y, 0.0))
            skin_b.append(len(V) - 1)
    nb = len(BANDS) - 1
    up, down = (0, 0, 1), (0, 0, -1)
    dirs = {p: [] for p in BAND_PART}

    def side(iv, idx):
        """Outward (horizontal) direction of a wall quad from the centre-line at that station."""
        c = 0.5 * (V[idx[0]][0] + V[idx[1]][0])
        cl = 0.5 * (centre[iv].x + centre[iv + 1].x)
        return (1.0 if c >= cl else -1.0, 0.0, 0.0)
    for iv in range(nV - 1):
        for ic in range(nb):
            faces[BAND_PART[ic]].append((top[(iv, ic)], top[(iv + 1, ic)], top[(iv + 1, ic + 1)], top[(iv, ic + 1)]))
            dirs[BAND_PART[ic]].append(up)
        q = (pit_b[iv], pit_b[iv + 1], top[(iv + 1, 0)], top[(iv, 0)])
        faces["FleshInner"].append(q)
        dirs["FleshInner"].append(side(iv, (top[(iv + 1, 0)], top[(iv, 0)])))
        q = (skin_b[iv], skin_b[iv + 1], top[(iv + 1, nb)], top[(iv, nb)])
        faces["Skin"].append(q)
        dirs["Skin"].append(side(iv, (top[(iv + 1, nb)], top[(iv, nb)])))
        faces["FleshInner"].append((pit_b[iv], skin_b[iv], skin_b[iv + 1], pit_b[iv + 1]))
        dirs["FleshInner"].append(down)
    return {p: C.faces_obj(p + "_tmp", V, fl, dirs[p]) for p, fl in faces.items()}


def fan(n=6, pitch=0.28, yaw=-10.0, lean=10.0, seed=5, scale=1.0, x0=None, y_jit=0.02, flip=False):
    """n slices fanned along +X: each leans its skin edge (-X) on the previous slice's pit side."""
    rnd = random.Random(seed)
    groups = {p: [] for p in BAND_PART}
    start = -(n - 1) * pitch / 2 + BOW * 0.5 * scale if x0 is None else x0
    for k in range(n):
        sl = crescent(rnd, L=L * scale * rnd.uniform(0.96, 1.03), T0=T0 * scale * rnd.uniform(0.95, 1.05),
                      bow=BOW * scale, h=H)
        x = start + k * pitch
        y = rnd.uniform(-y_jit, y_jit)
        lift = 0.004            # the lean pivots about the tips line: pit side stays down, skin side rises
        M = (Matrix.Translation((x, y, lift)) @ Matrix.Rotation(math.radians(yaw + rnd.uniform(-3, 3)), 4, "Z")
             @ Matrix.Rotation(math.radians(lean), 4, "Y"))
        if flip:
            M = Matrix.Scale(-1, 4, (0, 1, 0)) @ M
        for p, o in sl.items():
            o.matrix_world = M
            ns.apply_all(o)
            if flip:
                o.data.flip_normals()
            groups[p].append(o)
    parts = []
    cols = {"Skin": SKIN, "FleshOuter": OUTER, "FleshMid": MID, "FleshInner": INNER}
    for p in BAND_PART:
        o = ns.join(groups[p], p)
        ns.tag(o, p, cols[p], "SmoothPlastic", smooth_angle=72)
        parts.append(o)
    return parts


def build():
    parts = fan()
    lo, hi = ns.bbox_world(parts)
    for o in parts:                       # centre the fan on the roll (the slices bow toward -X)
        o.data.transform(Matrix.Translation((-(lo.x + hi.x) / 2, 0.0, 0.0)))
        o.data.update()
    C.check_bounds("Food_Avocado", parts)


def icon():
    fan(n=3, pitch=0.28, yaw=-16, lean=12, seed=8, x0=-0.18, y_jit=0.0)


if __name__ == "__main__":
    C.run(build, "Food_Avocado", C.meta("avocado", 0.10),
          icon=("Ingredient_avocado", icon, {"pitch": 45.0}))
