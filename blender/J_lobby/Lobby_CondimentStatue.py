"""Lobby_CondimentStatue — giant ketchup and mustard squeeze bottles (~6 wide x ~10 tall x 3 deep).

Two chubby cartoon squeeze bottles leaning toward each other on a small cream base: ketchup (red,
cream label with a tomato, cream cap, a drip on the nozzle) on the left and mustard (yellow, cream
label with a star, red cap, a drip on the nozzle) on the right, as seen from the front. Decor.

Front = -Y, pivot = bottom-centre. No sockets.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ns = C.ns

BASE_H = 0.6
BODY = [(0.0, 0.0), (1.05, 0.0), (1.27, 0.3), (1.3, 1.0), (1.2, 2.1), (1.2, 4.1), (1.25, 5.0), (1.1, 5.85),
        (0.62, 6.35), (0.0, 6.4)]
VERTS = 10
SCALE = 1.08


def bottle(x, lean, body_col, cap_col, label_icon):
    """Returns {colour: [objs]} for one bottle standing at (x, 0) on the base, leaning `lean` deg."""
    out = {}
    body = ns.lathe(BODY, verts=VERTS)
    out.setdefault(body_col, []).append(body)
    label = C.band(1.235, 1.7, loc=(0, 0, 3.1), verts=VERTS)
    out.setdefault(C.CREAM, []).append(label)
    cap = ns.cyl(0.66, 0.75, loc=(0, 0, 6.6), verts=VERTS, bevel=0.0)
    out.setdefault(cap_col, []).append(cap)
    nozzle = C.rod((0, 0, 6.9), (0, 0, 8.2), 0.42, verts=6, r_top=0.09)
    drip = ns.sphere(0.15, loc=(0.05, -0.07, 8.18), scale=(1, 1, 1.35), segs=5, rings=3)
    out[body_col] += [nozzle, drip]
    # label icon, flat on the front of the label
    fy = -1.235 - 0.03
    if label_icon == "tomato":
        out.setdefault(C.KETCHUP, []).append(C.prism(C.circle_pts(0.36, 10, 0, 3.05), "y", fy - 0.03, fy + 0.04))
        out.setdefault(C.LETTUCE, []).append(C.prism(C.star_pts(0.2, 0.08, 0, 3.42), "y", fy - 0.06, fy + 0.03))
    else:
        out.setdefault(C.MUSTARD, []).append(C.prism(C.star_pts(0.42, 0.19, 0, 3.1), "y", fy - 0.03, fy + 0.04))
    # stripe under the label
    out.setdefault(C.BRAND, []).append(C.band(1.24, 0.14, loc=(0, 0, 2.15), verts=VERTS))
    rot = Matrix.Translation((x, 0, BASE_H - 0.02)) @ Matrix.Rotation(math.radians(lean), 4, "Y") @ Matrix.Scale(SCALE, 4)
    for objs in out.values():
        for o in objs:
            ns.apply_all(o)
            o.data.transform(rot)
            o.data.update()
    return out


def build():
    base = C.prism(C.rrect(6.0, 3.0, 0.7, 2), "z", 0.0, BASE_H)
    ns.bevel(base, width=0.08, segments=1)
    groups = {C.CREAM: [base]}
    for x, lean, bc, cc, icon in ((-1.5, 5.0, C.KETCHUP, C.CREAM, "tomato"), (1.5, -5.0, C.MUSTARD_SAUCE, C.KETCHUP, "star")):
        C.merge_into(groups, bottle(x, lean, bc, cc, icon))
    names = {C.CREAM: "Cream", C.KETCHUP: "Ketchup", C.MUSTARD_SAUCE: "Mustard", C.LETTUCE: "Leaf", C.MUSTARD: "Star",
             C.BRAND: "Stripes"}
    for col, objs in groups.items():
        C.part(objs, names[col], col, can_collide=(col == C.CREAM), smooth_angle=50)


META = {"left": "ketchup (Roblox +X side = left as seen from the front)", "right": "mustard"}

if __name__ == "__main__":
    C.run(build, "Lobby_CondimentStatue", meta=META, budget=800)
