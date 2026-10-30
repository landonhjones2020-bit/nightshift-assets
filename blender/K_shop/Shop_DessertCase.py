"""Shop_DessertCase — counter-top rotating dessert carousel (2.6 x 3 x 2.6).

Chrome turntable base, a chrome centre post with two round shelves, and a tall glass dome
with a chrome rim and knob (Glass part, role glass, transparency 0.7 so the food reads).
Inside: a lattice cherry pie and a strawberry layer cake with one slice cut out (sponge /
jam / sponge layers facing the customer side) on the lower shelf, and a lemon meringue pie
with toasted peaks on the top shelf. Static mesh (the shelves are not a separate part).
Pivot = bottom-centre (sits on a counter top, customer side = front -Y).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402

ns = C.ns
CRUST = "#D99A4E"
CRUST_DARK = "#C8843F"
LATTICE = "#E9B871"
CHERRY = "#C51F33"
FROSTING = "#F58FB5"
SPONGE = "#F4D58C"
JAM = "#D0243B"
CREAM_TOP = "#FFF3E2"
BERRY = "#E3303D"
LEMON = "#F6CF35"
MERINGUE = "#FFF4E4"
TOAST = "#D9A05E"
SHELF1, SHELF2 = 0.36, 1.58      # shelf top heights
DOME_R = 1.22


def sector(r, a0, a1, z0, z1, segs=10, cx=0.0, cy=0.0, top=True, bottom=False, name="Sector"):
    """Pie-slice solid (cake wedge) about a vertical axis; angles in degrees from +X.
    The bottom face is dropped by default (it always sits on something)."""
    bm = bmesh.new()
    c0, c1 = bm.verts.new((cx, cy, z0)), bm.verts.new((cx, cy, z1))
    lo, hi = [], []
    for i in range(segs + 1):
        a = math.radians(a0 + (a1 - a0) * i / segs)
        lo.append(bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z0)))
        hi.append(bm.verts.new((cx + r * math.cos(a), cy + r * math.sin(a), z1)))
    for i in range(segs):
        if bottom:
            bm.faces.new([lo[i + 1], lo[i], c0])
        if top:
            bm.faces.new([hi[i], hi[i + 1], c1])
        bm.faces.new([lo[i], lo[i + 1], hi[i + 1], hi[i]])
    bm.faces.new([c0, lo[0], hi[0], c1])
    bm.faces.new([lo[-1], c0, c1, hi[-1]])
    bm.normal_update()
    zc = (z0 + z1) / 2
    for f in bm.faces:   # outward normals (the wedge is star-shaped about its axis midpoint)
        m = f.calc_center_median()
        ref = (m.x - cx, m.y - cy, m.z - zc)
        d = f.normal.x * ref[0] + f.normal.y * ref[1] + f.normal.z * ref[2]
        if d < 0:
            f.normal_flip()
    return ns.from_bmesh(bm, name)


def pie_shell(cx, cy, z, r=0.56, verts=12):
    """Golden pie crust: dish with a rounded raised rim (lathe), top closed at the centre."""
    return ns.lathe([(0.0, 0.0), (r - 0.1, 0.0), (r + 0.03, 0.17), (r - 0.03, 0.25), (r - 0.1, 0.19), (0.0, 0.16)],
                    verts=verts, loc=(cx, cy, z))


def top_disc(r, z, cx=0.0, cy=0.0, verts=12):
    return C.disc(r, loc=(cx, cy, z), verts=verts)


def cone(r, h, loc, verts=6, r_top=0.0):
    """Cap-less cone / frustum standing on loc (bottom hidden in what it sits on)."""
    return C.lathe_open([(r, 0.0), (r_top, h)], verts=verts, loc=loc)


def build():
    # chrome turntable base, post, shelves, dome rim, knob
    base = ns.lathe([(0.0, 0.0), (1.24, 0.0), (1.28, 0.1), (1.16, 0.26), (0.0, 0.26)], verts=16)
    post = ns.cyl(0.07, SHELF2 + 0.12 - 0.26, loc=(0, 0, 0.26 + (SHELF2 + 0.12 - 0.26) / 2), verts=6, bevel=0.0)
    shelf1 = ns.cyl(1.06, 0.08, loc=(0, 0, SHELF1 - 0.04), verts=16, bevel=0.0)
    shelf2 = ns.cyl(0.8, 0.07, loc=(0, 0, SHELF2 - 0.035), verts=16, bevel=0.0)
    rim = ns.torus(DOME_R + 0.01, 0.055, loc=(0, 0, 0.29), major_segs=16, minor_segs=3)
    knob = ns.sphere(0.13, loc=(0, 0, 2.9), segs=6, rings=4)
    C.part([base, post, shelf1, shelf2, rim, knob], "Chrome", C.CHROME, "Metal", smooth_angle=50)

    # --- lower shelf: lattice cherry pie (left) + strawberry layer cake (right, cut toward the front) ---
    px, py = -0.5, -0.12
    crust = pie_shell(px, py, SHELF1)
    filling = top_disc(0.5, SHELF1 + 0.205, px, py)
    lattice = []
    for k in (-0.17, 0.17):
        ln = 2 * math.sqrt(0.49 ** 2 - k ** 2)
        lattice.append(ns.box((ln, 0.1, 0.035), loc=(px, py + k, SHELF1 + 0.225), bevel=0.0))
        lattice.append(ns.box((0.1, ln, 0.035), loc=(px + k, py, SHELF1 + 0.245), bevel=0.0))
    C.part([crust], "PieCrust", CRUST, smooth_angle=50)
    C.part(lattice, "Lattice", LATTICE, smooth_angle=None)
    C.part([filling], "Cherry", CHERRY, smooth_angle=None)

    cx, cy, cr = 0.47, 0.05, 0.52
    a0, a1 = -55.0, 245.0           # the missing slice faces -Y (the customer side)
    z = SHELF1
    sponge = [sector(cr, a0, a1, z, z + 0.3, cx=cx, cy=cy, top=False),
              sector(cr, a0, a1, z + 0.38, z + 0.7, cx=cx, cy=cy, top=False)]
    jam = [sector(cr, a0, a1, z + 0.3, z + 0.38, cx=cx, cy=cy, top=False)]
    frost = [sector(cr + 0.035, a0, a1, z + 0.7, z + 0.8, cx=cx, cy=cy),
             C.arc_solid(cr - 0.005, cr + 0.035, a0, a1, z, z + 0.7, segs=10, cx=cx, cy=cy)]
    rosettes, berries = [], []
    for k in range(4):
        a = math.radians(a0 + 32 + (a1 - a0 - 64) * k / 3)
        rx, ry = cx + 0.33 * math.cos(a), cy + 0.33 * math.sin(a)
        rosettes.append(cone(0.1, 0.12, (rx, ry, z + 0.79)))
        berries.append(ns.sphere(0.075, loc=(rx, ry, z + 0.95), scale=(1, 1, 1.2), segs=6, rings=3))
    C.part(sponge, "Sponge", SPONGE, smooth_angle=None)
    C.part(jam, "Jam", JAM, smooth_angle=None)
    C.part(frost, "Frosting", FROSTING, smooth_angle=40)
    C.part(rosettes, "Cream", CREAM_TOP, smooth_angle=50)
    C.part(berries, "Berries", BERRY, smooth_angle=60)

    # --- top shelf: lemon meringue pie ---
    lz = SHELF2
    crust2 = pie_shell(0, 0, lz, r=0.62)
    lemon = top_disc(0.56, lz + 0.205)
    mer = ns.lathe([(0.5, 0.0), (0.44, 0.14), (0.3, 0.27), (0.0, 0.34)], verts=10, loc=(0, 0, lz + 0.2))
    ns.jitter(mer, amount=0.03, seed=7)
    peaks, tips = [], []
    for k in range(5):
        a = math.radians(18 + 72 * k)
        x, y = 0.27 * math.cos(a), 0.27 * math.sin(a)
        zz = lz + 0.2 + 0.25
        peaks.append(cone(0.1, 0.13, (x, y, zz - 0.05), r_top=0.03))
        tips.append(cone(0.04, 0.06, (x, y, zz + 0.075)))
    peaks.append(cone(0.11, 0.15, (0, 0, lz + 0.5), r_top=0.03))
    tips.append(cone(0.045, 0.07, (0, 0, lz + 0.645)))
    C.part([crust2], "PieCrust2", CRUST_DARK, smooth_angle=50)
    C.part([lemon], "Lemon", LEMON, smooth_angle=None)
    C.part([mer] + peaks, "Meringue", MERINGUE, smooth_angle=55)
    C.part(tips, "Toast", TOAST, smooth_angle=60)

    # glass dome (single shell, open at the bottom; stands in the chrome rim)
    prof = [(DOME_R, 0.27), (DOME_R, 2.05)]
    for i in range(1, 5):
        a = math.radians(90 * i / 4)
        prof.append((DOME_R * math.cos(a) if i < 4 else 0.0, 2.05 + 0.75 * math.sin(a)))
    dome = C.lathe_open(prof, verts=16)
    ns.tag(dome, "Glass", "#D4ECF2", "Glass", transparency=0.7, recolor="glass", cast_shadow=False, smooth_angle=60)


META = {"mount": "counter top", "pivot": "bottom-centre", "contents": ["cherry pie", "strawberry layer cake", "lemon meringue pie"]}

if __name__ == "__main__":
    C.run(build, "Shop_DessertCase", pivot=(0, 0, 0), meta=META)
