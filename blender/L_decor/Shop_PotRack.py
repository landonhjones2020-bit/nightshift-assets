"""Shop_PotRack — ceiling-hung steel pot rack over the kitchen prep area.

Two round ceiling plates, each sending a V of two chains (alternating flat / edge-on links)
down to the corners of a dark steel rounded-rectangle frame with two crossbars. Six things
hang from S-hooks at different heights: a cast-iron skillet, a copper saucepan, a small
copper skillet, a red-orange enamel saucepan, a stainless ladle and a slotted spatula.
Pans hang by their handles with the cooking side facing front (-Y).
PIVOT = TOP of the chains (the ceiling plates' top face, z = 0); everything hangs below.
~5 x 3.5 x 1.6.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
FZ = -1.25                    # frame rail height
FX, FY = 2.3, 0.68            # frame half extents (rail centre lines)
MOUNT_X = 1.6
STEEL = "#4E5459"
COPPER = "#C27A4B"
IRON = "#2E3035"


def chain(p0, p1, n, name="Chain"):
    """n links from p0 to p1, alternating a flat ring link and an edge-on bar link."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0)
    L = d.length / n
    out = []
    for k in range(n):
        c = p0 + d * ((k + 0.5) / n)
        if k % 2 == 0:
            o = C.ring_slab([(-0.07, -L * 0.62), (0.07, -L * 0.62), (0.07, L * 0.62), (-0.07, L * 0.62)],
                            [(-0.03, -L * 0.45), (0.03, -L * 0.45), (0.03, L * 0.45), (-0.03, L * 0.45)], "y", -0.017, 0.017)
        else:
            o = ns.box((0.034, 0.14, L * 1.24), loc=(0, 0, 0), bevel=0.0)
        # turn the link (built along Z) to follow the chain direction, keep its face roughly front
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        o.location = c
        ns.apply_all(o)
        out.append(o)
    return out


def pan(depth, radius, wall, handle_len, z_hang, x, y):
    """Pan hanging by its handle: built with its opening up (+Z), turned so the cooking side
    faces -Y, its handle running from the top of the rim up to the hang point (x, y, z_hang).
    Returns (body, handle).
    2026-11-05 (Landon: "pans ... have no handles"): ns.box only sets an object's location, and
    this function used to overwrite that location with the pan's, so every handle sat flat
    behind its own pan. The handle is now placed on its own, in world space."""
    r0 = radius * 0.8
    zc = z_hang - handle_len - radius + 0.06          # pan centre (the handle meets the rim)
    body = ns.lathe([(0.0, 0.0), (r0, 0.0), (radius, depth), (radius - wall, depth + 0.01), (r0 - wall, wall),
                     (0.0, wall)], verts=10)
    body.rotation_euler = (math.radians(90), 0, 0)
    body.location = (x, y + depth * 0.5, zc)
    ns.apply_all(body)
    hnd = ns.box((0.1, 0.06, handle_len), loc=(x, y, zc + radius + handle_len / 2 - 0.04), bevel=0.0)
    ns.apply_all(hnd)
    return body, hnd


def s_hook(x, y, z, drop):
    """S-hook over a rail at (x, y, z), its lower curl at z - drop."""
    return C.pipe([(x, y + 0.07, z + 0.02), (x, y - 0.02, z + 0.1), (x, y - 0.06, z - 0.04), (x, y - 0.05, z - drop),
                   (x, y + 0.03, z - drop - 0.06)], 0.022, sides=4)


def build():
    steel = []
    # ceiling plates + chains (V to the frame corners)
    for sx in (-1, 1):
        steel.append(ns.cyl(0.2, 0.06, loc=(sx * MOUNT_X, 0, -0.03), verts=8, bevel=0.0))
        steel.append(ns.cyl(0.05, 0.12, loc=(sx * MOUNT_X, 0, -0.1), verts=6, bevel=0.0))
        for sy in (-1, 1):
            steel += chain((sx * MOUNT_X, 0, -0.16), (sx * (FX - 0.05), sy * (FY - 0.02), FZ + 0.05), 4)
    # frame: rounded rectangle tube + two crossbars
    rect = [(-FX, -FY, FZ), (FX, -FY, FZ), (FX, FY, FZ), (-FX, FY, FZ)]
    pts = []
    for i in range(4):
        p0, p1, p2 = Vector(rect[i - 1]), Vector(rect[i]), Vector(rect[(i + 1) % 4])
        a = p1 + (p0 - p1).normalized() * 0.2
        b = p1 + (p2 - p1).normalized() * 0.2
        for k in range(3):
            t = k / 2
            q = (1 - t) ** 2 * a + 2 * (1 - t) * t * p1 + t * t * b
            pts.append(tuple(q))
    steel.append(C.pipe(pts, 0.06, sides=6, closed=True))
    for x in (-0.85, 0.85):
        steel.append(C.pipe([(x, -FY, FZ), (x, FY, FZ)], 0.045, sides=6))

    iron, copper, enamel, chrome, black, slots = [], [], [], [], [], []
    hooks = []
    # front rail (y = -FY): skillet, saucepan, ladle, spatula
    b, h = pan(0.16, 0.56, 0.035, 0.9, FZ - 0.16, -1.55, -FY)
    iron += [b, h]
    hooks.append(s_hook(-1.55, -FY, FZ, 0.14))
    b, h = pan(0.4, 0.4, 0.03, 0.62, FZ - 0.3, -0.25, -FY)
    copper.append(b)
    chrome.append(h)
    hooks.append(s_hook(-0.25, -FY, FZ, 0.28))
    # ladle: a deep bowl hung with its inside to the front, like the pans, and a long handle from
    # the top of its rim up to a ring on the S-hook (2026-11-05: the handle used to run straight
    # down into the middle of an upturned dish, which read as a pole with a lid, not a ladle)
    lx = 0.75
    br, bd, bw = 0.26, 0.2, 0.025                 # bowl radius, depth, wall
    zb = FZ - 1.98                                # bowl centre
    bowl = ns.lathe([(0.0, 0.0), (br * 0.72, 0.03), (br, bd * 0.62), (br + 0.006, bd), (br - bw, bd + 0.004),
                     (br - bw, bd * 0.62), (br * 0.72 - bw, 0.03 + bw), (0.0, 0.03 + bw)], verts=8)
    bowl.rotation_euler = (math.radians(90), 0, 0)
    bowl.location = (lx, -FY + bd / 2, zb)
    ns.apply_all(bowl)
    ring_c = (lx, -FY - 0.01, FZ - 0.19)          # round the hook's lower curl (it passes through)
    lh = C.rod((lx, -FY - bd / 2, zb + br - 0.02), (lx, -FY - 0.01, ring_c[2] - 0.05), 0.034, verts=6)
    ring = ns.torus(0.05, 0.014, loc=ring_c, rot=(90, 0, 0), major_segs=8, minor_segs=3)
    chrome += [bowl, lh, ring]
    hooks.append(s_hook(lx, -FY, FZ, 0.16))
    # slotted spatula: blade + slots + black handle
    sx_ = 1.6
    blade = ns.box((0.42, 0.03, 0.5), loc=(sx_, -FY - 0.04, FZ - 1.48), bevel=0.02, segments=1)
    neck = ns.box((0.06, 0.03, 0.34), loc=(sx_, -FY - 0.04, FZ - 1.08), bevel=0.0)
    chrome += [blade, neck]
    black.append(ns.box((0.1, 0.06, 0.62), loc=(sx_, -FY - 0.04, FZ - 0.6), bevel=0.02, segments=1))
    for k in range(3):
        slots.append(C.quad_xz(sx_ - 0.12 + 0.12 * k - 0.025, sx_ - 0.12 + 0.12 * k + 0.025, FZ - 1.66, FZ - 1.32,
                               -FY - 0.04 - 0.017))
    hooks.append(s_hook(sx_, -FY, FZ, 0.18))
    # back rail (y = +FY): small copper skillet, red-orange enamel saucepan
    b, h = pan(0.13, 0.42, 0.03, 0.6, FZ - 0.4, -0.95, FY)
    copper += [b]
    chrome.append(h)
    hooks.append(s_hook(-0.95, FY, FZ, 0.38))
    b, h = pan(0.36, 0.35, 0.03, 0.55, FZ - 0.22, 1.05, FY)
    enamel.append(b)
    black.append(h)
    hooks.append(s_hook(1.05, FY, FZ, 0.2))

    C.part(steel, "Rack", STEEL, "Metal", smooth_angle=50)
    C.part(hooks, "Hooks", C.CHROME, "Metal", smooth_angle=60)
    C.part(iron, "CastIron", IRON, "Metal", smooth_angle=45)
    C.part(copper, "Copper", COPPER, "Metal", smooth_angle=45)
    C.part(enamel, "Enamel", C.BRAND, smooth_angle=45)
    C.part(chrome, "Utensils", C.CHROME, "Metal", smooth_angle=45)
    C.part(black, "Handles", "#1E1F22", smooth_angle=40)
    C.part(slots, "Slots", "#16171A", smooth_angle=None)


META = {"pivot": "top of the chains (ceiling plates' top face): hang from y = ceiling",
        "drop": 3.5}

if __name__ == "__main__":
    C.run(build, "Shop_PotRack", mount="hang", pivot=(0, 0, 0), budget=1500, meta=META)   # between the ceiling plates
