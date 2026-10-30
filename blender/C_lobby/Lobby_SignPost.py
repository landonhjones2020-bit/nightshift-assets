"""Lobby_SignPost — wayfinding fingerpost with four colour-coded arrow boards.

A navy square post on a concrete footing with a mustard ball finial carries four arrow
boards, each with modelled lettering on BOTH faces (the back copy is mirrored so it reads
correctly from behind). Each arm is turned about the post to point at its place in the
Lobby (2026-10-29: the arms used to lie in one plane, so from the spawn TEST KITCHEN and
SHOP pointed right and VANS sideways). Yaws are for the post standing unrotated at the
plaza spot LobbyMap uses, (-5, 0, 9) in Roblox space; Roblox (x, z) = Blender (-x, y):
  TEST KITCHEN  red-orange board, cream letters → the Test Kitchen bay (0, 30)
  LOCKERS       navy board, cream letters       → the Locker Room bay (32, 30)
  SHOP          mustard board, navy letters     → the Shop kiosk (-20, 7)
  VANS          cream board, red-orange letters → the van lot (z -30)
meta arrows gives each arm's direction in Roblox model space.

Pivot = bottom-centre of the footing.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Matrix  # noqa: E402  (after bpy is loaded)

ns = C.ns
POST_H = 9.2
BL, BH, BT = 5.0, 0.85, 0.16   # board body length (incl. tip), height, thickness
TIP = 0.55
POST_AT = (-5.0, 9.0)   # Roblox (x, z) of the post in LobbyMap
TARGETS = {"TEST KITCHEN": (0.0, 30.0), "LOCKERS": (32.0, 30.0), "SHOP": (-20.0, 7.0), "VANS": (-5.0, -30.0)}
# boards raised 0.55 (2026-10-29) so the lowest arm clears a tall avatar's head when it
# reaches over the plaza
BOARDS = [("TEST KITCHEN", 8.7, 1, C.BRAND, C.CREAM),
          ("LOCKERS", 7.6, 1, C.NAVY, C.CREAM),
          ("SHOP", 6.5, 1, C.MUSTARD, C.NAVY),
          ("VANS", 5.4, 1, C.CREAM, C.BRAND)]


def yaw_of(txt):
    """Blender angle (from +X toward +Y) of the arm pointing at its Roblox target."""
    tx, tz = TARGETS[txt]
    rx, rz = tx - POST_AT[0], tz - POST_AT[1]
    return math.atan2(rz, -rx)


def turn(objs, theta):
    """Rotate meshes about the post's axis (world Z through the origin)."""
    m = Matrix.Rotation(theta, 4, "Z")
    for o in objs:
        o.data.transform(o.matrix_world)
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(m)
        o.data.update()


def arrow(direction, z):
    """Arrow outline (x, z): tail just past the post, tip `direction` (+1 = +X)."""
    t0 = -0.35 * direction            # tail (behind the post)
    t1 = t0 + direction * (BL - TIP)
    tip = t0 + direction * BL
    pts = [(t0, z - BH / 2), (t1, z - BH / 2), (tip, z), (t1, z + BH / 2), (t0, z + BH / 2)]
    if direction < 0:
        pts = list(reversed(pts))
    return C.fillet(pts, [0.08, 0.02, 0.06, 0.02, 0.08], 1), (t0 + t1) / 2


def build():
    foot = ns.box((1.1, 1.1, 0.45), loc=(0, 0, 0.225), bevel=0.06, segments=1)
    C.part([foot], "Footing", C.CONCRETE, "Concrete", can_collide=True, smooth_angle=40)
    post = ns.box((0.36, 0.36, POST_H - 0.45), loc=(0, 0, 0.45 + (POST_H - 0.45) / 2), bevel=0.05, segments=1)
    C.part([post], "Post", C.NAVY, "Metal", can_collide=True, smooth_angle=40)
    fin = [ns.sphere(0.3, loc=(0, 0, POST_H + 0.25), segs=10, rings=6),
           ns.box((0.48, 0.48, 0.1), loc=(0, 0, POST_H + 0.02), bevel=0.03, segments=1)]
    boards, letters = {}, {}
    for txt, z, d, bcol, tcol in BOARDS:
        outline, _ = arrow(d, z)
        b = C.prism(outline, "y", -BT / 2, BT / 2)
        ns.bevel(b, width=0.04, segments=1, angle=50)
        w = min(len(txt) * 0.36, BL - TIP - 0.35 - 0.3 - 0.45)   # between the post clamp and the tip
        tx = d * (0.3 + (BL - TIP - 0.35)) / 2
        f = C.text(txt, 0.5, 0.04, (tx, -BT / 2 - 0.0, z), width=w, res=1, spacing=1.06, flat=True)
        bk = C.text(txt, 0.5, 0.04, (tx, BT / 2 + 0.0, z), width=w, res=1, spacing=1.06, facing="+Y", flat=True)
        turn([b, f, bk], yaw_of(txt))
        boards.setdefault(bcol, []).append(b)
        letters.setdefault(tcol, []).extend([f, bk])
    names = {C.BRAND: "Red", C.NAVY: "Navy", C.MUSTARD: "Mustard", C.CREAM: "Cream"}
    for col, objs in boards.items():
        C.part(objs, "Board" + names[col], col, smooth_angle=40)
    for col, objs in letters.items():
        C.part(objs, "Text" + names[col], col, smooth_angle=None)
    clamps = [ns.box((0.5, 0.5, 0.18), loc=(0, 0, z), bevel=0.03, segments=1) for _, z, _, _, _ in BOARDS]
    C.part(fin[:1], "Finial", C.MUSTARD, smooth_angle=60)
    C.part(clamps + fin[1:], "Clamps", C.CHROME, "Metal", smooth_angle=40)


META = {"arrows": {t: [round(-math.cos(yaw_of(t)), 3), round(math.sin(yaw_of(t)), 3)] for t, *_ in BOARDS},
        "arrows_frame": "Roblox model space (x, z), post unrotated at plaza (-5, 9)",
        "boards": [t for t, *_ in BOARDS], "height": POST_H + 0.55}

if __name__ == "__main__":
    C.run(build, "Lobby_SignPost", meta=META)
