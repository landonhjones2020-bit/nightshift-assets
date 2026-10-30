"""Shop_WaitSign — "PLEASE WAIT TO BE SEATED" host sign on a chrome post (1.6 x 5 x 1.2).

Weighted chrome base, slim chrome post with a collar, a chrome clamp and a chrome-framed
navy sign: red-orange "PLEASE" band (cream letters), cream "WAIT TO BE", big mustard
"SEATED" with a pink underline. The back of the sign carries a small cream STACKHOUSE.
Floor prop: pivot = bottom-centre, front (-Y) = the reading side.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SW, SH = 1.6, 1.32               # sign outer size
SZ = 4.28                        # sign centre height
PT = 0.07                        # panel half-thickness


def build():
    base = ns.lathe([(0.0, 0.0), (0.6, 0.0), (0.62, 0.05), (0.5, 0.14), (0.13, 0.2), (0.08, 0.27), (0.0, 0.27)], verts=12)
    post = ns.cyl(0.05, SZ - SH / 2 - 0.25, loc=(0, 0, 0.25 + (SZ - SH / 2 - 0.25) / 2), verts=6, bevel=0.0)
    collar = ns.torus(0.075, 0.03, loc=(0, 0, 1.0), major_segs=8, minor_segs=3)
    clamp = ns.box((0.22, 0.2, 0.16), loc=(0, 0, SZ - SH / 2 - 0.02), bevel=0.03, segments=1)
    frame = C.ring_slab(C.rrect(SW, SH, 0.12, 2, 0, SZ), C.rrect(SW - 0.18, SH - 0.18, 0.06, 2, 0, SZ), "y",
                        -PT - 0.03, PT + 0.03)
    ns.bevel(frame, width=0.025, segments=1, angle=50)
    C.part([base, post, collar, clamp, frame], "Chrome", C.CHROME, "Metal", smooth_angle=45)

    pw, ph = SW - 0.16, SH - 0.16
    panel = ns.box((pw, 2 * PT, ph), loc=(0, 0, SZ), bevel=0.0)
    C.part([panel], "Panel", C.NAVY, smooth_angle=None)
    top = SZ + ph / 2
    band = ns.box((pw, 0.012, 0.34), loc=(0, -PT - 0.006, top - 0.17), bevel=0.0)
    C.part([band], "Band", C.BRAND, smooth_angle=None)
    fy = -PT
    t1 = C.text("PLEASE", 0.22, 0.03, (0, fy - 0.012, top - 0.17), width=0.95, res=1, spacing=1.15, flat=True)
    t2 = C.text("WAIT TO BE", 0.2, 0.03, (0, fy, SZ + 0.05), width=1.2, res=1, spacing=1.05, flat=True)
    back = C.text("STACKHOUSE", 0.16, 0.03, (0, PT, SZ), width=1.0, res=1, flat=True, facing="+Y")
    C.part([t1, t2, back], "Letters", C.CREAM, smooth_angle=None)
    t3 = C.text("SEATED", 0.3, 0.03, (0, fy, SZ - 0.3), width=1.16, res=1, spacing=1.08, flat=True)
    C.part([t3], "Seated", C.MUSTARD, smooth_angle=None)
    ul = ns.box((0.9, 0.012, 0.045), loc=(0, fy - 0.006, SZ - 0.5), bevel=0.0)
    C.part([ul], "Underline", C.PINK, smooth_angle=None)


META = {"pivot": "bottom-centre", "mount": "floor", "sign_size": [SW, SH]}

if __name__ == "__main__":
    C.run(build, "Shop_WaitSign", pivot=(0, 0, 0), meta=META)
