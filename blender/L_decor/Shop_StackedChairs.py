"""Shop_StackedChairs — a stack of four diner chairs (Shop_Chair's look, low-poly copies).

Each chair: bent chrome side tubes (front leg -> seat rail -> rear leg), chrome back
uprights, a red vinyl seat pad (dark piping band under it) and back pad (part Vinyl, role "chair_vinyl" like
Shop_Chair, so a room's chair colour preset applies to the stack too). Every chair sits
0.3 higher and 0.18 further forward than the one below, so each back pad rests just in
front of the one beneath it, the way stacked chairs fan out.
Front faces -Y, pivot = bottom-centre. ~1.7 x 4.2 x 2.3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SZ = 1.6                 # seat top of the bottom chair (Shop_Chair)
HW, HD = 0.8, 0.75       # frame half width (legs just outside the 1.56 seat) / half depth
N = 4
DZ, DY = 0.3, -0.18      # per-chair stacking offset


def chair(k):
    """One low-poly chair raised by k stacking steps. Returns (tubes, pads, piping)."""
    oz, oy = k * DZ, k * DY
    tubes, pads = [], []
    for sx in (-1, 1):
        x = sx * HW
        tubes.append(C.pipe([(x, -HD + oy, 0.05 + oz), (x, -HD + 0.08 + oy, SZ - 0.3 + oz), (x, HD - 0.05 + oy, SZ - 0.3 + oz),
                             (x, HD + 0.05 + oy, 0.05 + oz)], 0.06, sides=5))
        tubes.append(C.pipe([(x * 0.84, HD - 0.12 + oy, SZ - 0.3 + oz), (x * 0.84, HD + 0.1 + oy, 3.2 + oz)], 0.05, sides=5))
    pads.append(ns.box((2 * HW - 0.04, 2 * HD + 0.02, 0.26), loc=(0, -0.02 + oy, SZ - 0.13 + oz), bevel=0.08, segments=1))
    pads.append(ns.box((2 * HW * 0.84, 0.16, 1.02), loc=(0, HD + 0.08 + oy, 2.72 + oz), rot=(-8, 0, 0), bevel=0.07,
                       segments=1))
    piping = ns.box((2 * HW - 0.02, 2 * HD + 0.05, 0.07), loc=(0, -0.02 + oy, SZ - 0.235 + oz), bevel=0.0)
    return tubes, pads, piping


def build():
    tubes, pads, piping = [], [], []
    for k in range(N):
        t, p, pp = chair(k)
        tubes += t
        pads += p
        piping.append(pp)
    C.part(tubes, "Frame", C.CHROME, "Metal", smooth_angle=60)
    C.part(piping, "Piping", C.BASE_DARK, smooth_angle=50)
    C.part(pads, "Vinyl", C.VINYL_RED, recolor="chair_vinyl", smooth_angle=50)


META = {"count": N, "matches": "Shop_Chair (role chair_vinyl on the pads)", "stack_step": [0, DZ, DY]}

if __name__ == "__main__":
    C.run(build, "Shop_StackedChairs", budget=900, meta=META)
