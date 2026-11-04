"""Lobby_Bunting — a sagging garland of triangle flags, 12 studs from hook to hook (2.0 sag).

A cream cord in a catenary with pennant flags in the STACKHOUSE colours (red-orange, mustard,
cream, navy, repeating), each folded over the cord in a little sleeve and hanging straight down
with a slight flutter; small chrome eyes at both ends. Fabric, no collision.

PIVOT = the START end (cord end at the pivot). The garland runs along the model's +X (Roblox
RightVector): the end is at (12, 0, 0) in Roblox axes (Blender x = -12). Hang it like
Lobby_FestoonSpan (pivot on a hook, +X toward the next one; scale X by distance / 12).
Sockets: Start (0, 0, 0), End (12, 0, 0).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns

SPAN = 12.0
SAG = 2.0
FLAG_W = 0.82                # along the cord
FLAG_L = 1.05                # hanging length
GAP = 0.2
T = 0.05                     # cloth thickness
COLS = (C.BRAND, C.MUSTARD, C.CREAM, C.NAVY)


def flag(pa, pb, length, flutter):
    """Pennant hanging from the cord segment pa -> pb: top edge along the cord, tip straight
    below the midpoint, a thin slab (both sides visible), turned `flutter` deg about the top edge."""
    pa, pb = Vector(pa), Vector(pb)
    mid = (pa + pb) / 2
    tip = mid - Vector((0, 0, length))
    # slightly bowed sides: one extra point per side
    sa = pa.lerp(tip, 0.5) + (pa - pb).normalized() * 0.03
    sb = pb.lerp(tip, 0.5) + (pb - pa).normalized() * 0.03
    outline = [pa, sa, tip, sb, pb]
    bm = bmesh.new()
    off = Vector((0, T / 2, 0))
    f = [bm.verts.new(p - off) for p in outline]
    k = [bm.verts.new(p + off) for p in outline]
    bm.faces.new(f)
    bm.faces.new(list(reversed(k)))
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([f[j], f[i], k[i], k[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    ob = C.obj_from_bm(bm, "Flag")
    axis = (pb - pa).normalized()
    M = Matrix.Translation(pa) @ Matrix.Rotation(math.radians(flutter), 4, axis) @ Matrix.Translation(-pa)
    ob.data.transform(M)
    ob.data.update()
    sleeve = C.pipe([tuple(pa - axis * 0.02), tuple(pb + axis * 0.02)], 0.06, sides=5)
    return [ob, sleeve]


def build():
    a, b = (0.0, 0.0, 0.0), (C.along_x(SPAN), 0.0, 0.0)
    cord_pts = C.catenary(a, b, SAG, n=20)
    cord = C.pipe(cord_pts, 0.035, sides=4)
    fine = [Vector(p) for p in C.catenary(a, b, SAG, n=400)]
    seg = [(fine[i + 1] - fine[i]).length for i in range(len(fine) - 1)]
    total = sum(seg)
    cum = [0.0]
    for s in seg:
        cum.append(cum[-1] + s)

    def at(t):
        for i in range(len(seg)):
            if cum[i + 1] >= t:
                u = (t - cum[i]) / seg[i] if seg[i] > 1e-9 else 0.0
                return fine[i].lerp(fine[i + 1], u)
        return fine[-1]

    pitch = FLAG_W + GAP
    n = int((total - 0.6) // pitch)
    start = (total - n * pitch + GAP) / 2
    rnd = random.Random(7)
    groups = {c: [] for c in COLS}
    for k in range(n):
        t0 = start + k * pitch
        pa, pb = at(t0), at(t0 + FLAG_W)
        groups[COLS[k % len(COLS)]] += flag(pa, pb, FLAG_L * rnd.uniform(0.94, 1.04), rnd.uniform(-9, 9))
    eyes = []
    for x in (a[0], b[0]):
        e = ns.torus(0.11, 0.03, major_segs=8, minor_segs=4)
        C.place(e, (x, 0, 0.0), pitch=90)
        eyes.append(e)
    C.part([cord], "Cord", C.CREAM_SHADE, "Fabric", smooth_angle=60)
    C.part(eyes, "Eyes", C.CHROME, "Metal", smooth_angle=60)
    names = {C.BRAND: "FlagsRed", C.MUSTARD: "FlagsMustard", C.CREAM: "FlagsCream", C.NAVY: "FlagsNavy"}
    for col, objs in groups.items():
        C.part(objs, names[col], col, "Fabric", smooth_angle=None)
    return {"flags": n}


SOCKETS = {"Start": ((0.0, 0.0, 0.0), 0.0), "End": ((C.along_x(SPAN), 0.0, 0.0), 0.0)}
META = {"span": SPAN, "sag": SAG, "pivot": "start end (cord end); runs along Roblox +X to End",
        "colours": "red-orange, mustard, cream, navy (repeating from the start end)"}

if __name__ == "__main__":
    C.run(build, "Lobby_Bunting", sockets=SOCKETS, meta=META, budget=2000, pivot=(0.0, 0.0, 0.0),
          socket_views=((-20, 15),))
