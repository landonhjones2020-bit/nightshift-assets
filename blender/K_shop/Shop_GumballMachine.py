"""Shop_GumballMachine — classic red gumball machine on a chrome stand (1.5 x 4.2 x 1.5).

Weighted chrome foot, slim chrome column with collar rings, a round red cast body with a
chrome coin plate + turn handle and a chrome chute flap on the front (-Y), a glass globe
(Glass part, role glass) packed with colourful gumballs (low-poly balls over a heap whose
facets carry the same colours, so it reads packed), and a red cap with a chrome finial.
Pivot = bottom-centre (floor prop). Socket Prompt = in front of the coin handle.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
RED = "#D42A30"
RED_DARK = "#A61F27"
BALLS = {"#F2C230": "Yellow", "#2F7FE0": "Blue", "#3FBF5A": "Green", "#F05AA0": "Pink", "#FF8A2A": "Orange",
         "#F4F1E8": "White", "#E23434": "Red", "#8E5BD9": "Purple"}
BODY_Z0, BODY_Z1 = 2.35, 2.95
GR = 0.6                         # globe radius
GZ = BODY_Z1 + GR - 0.08         # globe centre


def build():
    # chrome stand
    foot = ns.lathe([(0.0, 0.0), (0.72, 0.0), (0.72, 0.07), (0.5, 0.18), (0.13, 0.3), (0.0, 0.3)], verts=10)
    column = ns.cyl(0.085, BODY_Z0 - 0.3, loc=(0, 0, 0.3 + (BODY_Z0 - 0.3) / 2), verts=6, bevel=0.0)
    rings = [ns.torus(0.12, 0.045, loc=(0, 0, 1.3), major_segs=8, minor_segs=3)]
    collar = ns.lathe([(0.1, BODY_Z0 - 0.4), (0.18, BODY_Z0 - 0.26), (0.34, BODY_Z0 - 0.04), (0.0, BODY_Z0 - 0.04)],
                      verts=10)
    finial = ns.sphere(0.08, loc=(0, 0, GZ + GR + 0.17), segs=5, rings=3)

    # red cast body (round, flared) + cap
    body = ns.lathe([(0.0, BODY_Z0 - 0.06), (0.46, BODY_Z0 - 0.06), (0.52, BODY_Z0 + 0.06), (0.52, BODY_Z1 - 0.16),
                     (0.4, BODY_Z1 - 0.02), (0.0, BODY_Z1 - 0.02)], verts=10)
    cap = ns.lathe([(0.3, GZ + GR - 0.1), (0.29, GZ + GR + 0.02), (0.18, GZ + GR + 0.1), (0.0, GZ + GR + 0.12)],
                   verts=10)
    C.part([body], "Body", RED, smooth_angle=45)
    C.part([cap], "Cap", RED_DARK, smooth_angle=45)

    # coin plate, handle and chute on the front
    yf = -0.52
    pz = BODY_Z1 - 0.27              # coin plate / handle centre height
    plate = C.prism(C.rrect(0.5, 0.36, 0.08, 2, 0, pz), "y", yf - 0.06, yf + 0.12)
    hub = ns.cyl(0.09, 0.14, verts=8, bevel=0.0)
    C.place(hub, (0, yf - 0.13, pz), pitch=90)
    grip = ns.box((0.34, 0.07, 0.08), loc=(0, yf - 0.22, pz), bevel=0.0)
    chute = C.prism(C.fillet([(-0.17, BODY_Z0 + 0.03), (0.17, BODY_Z0 + 0.03), (0.17, BODY_Z0 + 0.2),
                              (-0.17, BODY_Z0 + 0.2)], [0.03, 0.03, 0.07, 0.07], 2), "y", yf - 0.08, yf + 0.12)
    C.part([foot, column, collar, finial, plate, hub, grip, chute] + rings, "Chrome", C.CHROME, "Metal",
           smooth_angle=45)
    slot = ns.box((0.05, 0.02, 0.14), loc=(0.15, yf - 0.065, pz + 0.04), bevel=0.0)
    flap = ns.box((0.24, 0.02, 0.09), loc=(0, yf - 0.085, BODY_Z0 + 0.115), bevel=0.0)
    C.part([slot, flap], "Slots", C.DARK_VOID, smooth_angle=None)

    # gumball fill (dark, lumpy) + balls packed against the glass
    fill = ns.sphere(GR - 0.1, loc=(0, 0, GZ - 0.02), scale=(1, 1, 0.9), segs=8, rings=5)
    ns.apply_all(fill)
    for v in fill.data.vertices:             # flatten the top into a heap at ~75 %
        if v.co.z > GZ + 0.2:
            v.co.z = GZ + 0.2 + (v.co.z - GZ - 0.2) * 0.25
    rnd = random.Random(11)
    groups = {c: [] for c in BALLS}
    # the heap's faces are split into the gumball colours: a packed, multicoloured mosaic behind the balls
    import bmesh
    cols = list(BALLS)
    pick = [cols[(i * 3 + rnd.randrange(len(cols))) % len(cols)] for i in range(len(fill.data.polygons))]
    for col in cols:
        if col not in pick:
            continue
        piece = fill.copy()
        piece.data = fill.data.copy()
        C.bpy.context.scene.collection.objects.link(piece)
        bm = bmesh.new()
        bm.from_mesh(piece.data)
        bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if pick[f.index] != col], context="FACES")
        bm.to_mesh(piece.data)
        bm.free()
        groups[col].append(piece)
    C.bpy.data.objects.remove(fill, do_unlink=True)
    pts = []
    for ring_z, n, rr in ((-0.32, 5, 0.28), (-0.1, 7, 0.42), (0.11, 7, 0.4), (0.27, 3, 0.18)):
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * (ring_z > 0)) / max(n, 1) + rnd.uniform(-0.15, 0.15)
            p = Vector((rr * math.cos(a), rr * math.sin(a), GZ + ring_z + rnd.uniform(-0.02, 0.02)))
            pts.append(p)
    for i, p in enumerate(pts):
        col = list(BALLS)[(i * 5 + 3) % len(BALLS)]
        groups[col].append(ns.sphere(0.145, loc=p, segs=5, rings=3))
    for col, objs in groups.items():
        if objs:
            C.part(objs, "Gum" + BALLS[col], col, smooth_angle=55)

    globe = ns.sphere(GR, loc=(0, 0, GZ), segs=12, rings=8)
    ns.tag(globe, "Glass", "#D4ECF2", "Glass", transparency=0.65, recolor="glass", cast_shadow=False, smooth_angle=60)


SOCKETS = {"Prompt": ((0, -1.4, BODY_Z1 - 0.27), 0.0)}
META = {"pivot": "bottom-centre", "mount": "floor"}

if __name__ == "__main__":
    C.run(build, "Shop_GumballMachine", sockets=SOCKETS, pivot=(0, 0, 0), meta=META)
