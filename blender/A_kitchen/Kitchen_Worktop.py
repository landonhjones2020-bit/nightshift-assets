"""Kitchen_Worktop — plain stainless work-counter module (4 wide x 3 deep, top at 3.0).

Same family as the prep and wrap stations (thick rolled-edge top, brand stripe on the
apron, square legs with bullet feet, undershelf) but with closed sides and back: bevelled
stainless side/back panels with raised inset panels, and a shallow utensil drawer in the
apron. No backsplash, so the whole 4 x 3 top is usable: the conveyor toaster (3 deep) and
the ticket printer sit on it. Front faces -Y. Collides.

Socket Top = centre of the worktop surface (z = 3.0), yaw 0.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D, TOP = 4.0, 3.0, C.TOP
APRON = 0.4
SHELF_Z = 0.6


def build():
    top = C.worktop_slab(W, D, TOP, apron=APRON, backsplash=0.0)
    C.part(top, "Worktop", C.STAINLESS, "Metal", can_collide=True, smooth_angle=40)

    base = C.table_base(W, D, TOP, shelf_z=SHELF_Z, apron=APRON)
    inset, leg = 0.2, 0.28
    lx, ly = W / 2 - inset, D / 2 - inset
    pz0, pz1 = SHELF_Z + 0.06, TOP - APRON - 0.02
    pzc, ph = (pz0 + pz1) / 2, pz1 - pz0
    panels = []
    for sx in (-1, 1):       # side panels between the legs
        panels.append(ns.box((0.06, 2 * ly - leg * 0.6, ph), loc=(sx * lx, 0, pzc), bevel=0.025, segments=1))
    panels.append(ns.box((2 * lx - leg * 0.6, 0.06, ph), loc=(0, ly, pzc), bevel=0.025, segments=1))   # back
    C.part(base["legs"] + [base["shelf"]] + panels, "Frame", C.STEEL, "Metal", can_collide=True, smooth_angle=40)
    C.part(base["feet"], "Feet", C.RUBBER, "SmoothPlastic")

    # raised bevelled inset panels on the outside of the sides (the "panel details")
    raised = []
    for sx in (-1, 1):
        raised.append(ns.box((0.05, 2 * ly - 0.75, ph - 0.4), loc=(sx * (lx + 0.045), 0, pzc), bevel=0.04, segments=2))
    # a short stack of sheet pans on the undershelf
    s0 = SHELF_Z + 0.06
    raised += [ns.box((1.7, 1.25, 0.07), loc=(-0.6 + 0.03 * i, -0.05 - 0.03 * i, s0 + 0.035 + 0.08 * i),
                      rot=(0, 0, 3 * i - 2), bevel=0.025, segments=1) for i in range(2)]
    C.part(raised, "Panels", C.STAINLESS, "Metal", smooth_angle=40)

    # apron: shallow utensil drawer + brand stripe either side of it
    drawer = ns.box((1.5, 0.06, 0.26), loc=(0, -D / 2 - 0.02, TOP - APRON / 2), bevel=0.04, segments=2)
    pull = ns.box((0.5, 0.08, 0.06), loc=(0, -D / 2 - 0.08, TOP - APRON / 2 - 0.02), bevel=0.025, segments=1)
    C.part([drawer, pull], "Drawer", C.STEEL, "Metal", smooth_angle=40)
    stripes = [ns.box((0.95, 0.04, 0.12), loc=(sx * 1.38, -D / 2 - 0.012, TOP - APRON / 2), bevel=0.02, segments=1)
               for sx in (-1, 1)]
    C.part(stripes, "Stripe", C.BRAND, "SmoothPlastic")

    sockets = {"Top": ((0, 0, TOP), 0)}
    meta = {"worktop_height": TOP, "footprint": [W, D]}
    return {"export": {"sockets": sockets, "meta": meta, "pivot": (0, 0, 0)}}


if __name__ == "__main__":
    C.run(build, "Kitchen_Worktop")
