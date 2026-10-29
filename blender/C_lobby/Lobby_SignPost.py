"""Lobby_SignPost — wayfinding signpost with four colour-coded arrow boards.

A navy square post on a concrete footing with a mustard ball finial carries four arrow
boards, each with modelled lettering on BOTH faces (the back copy is mirrored so it reads
correctly from behind):
  TEST KITCHEN  red-orange board, cream letters, points -X (Blender) = Roblox +X
  LOCKERS       navy board, cream letters,       points +X (Blender) = Roblox -X
  SHOP          mustard board, navy letters,     points -X (Blender) = Roblox +X
  VANS          cream board, red-orange letters, points +X (Blender) = Roblox -X
Boards face front/back (-Y / +Y); orient the post so its front faces the spawn and the
arrows point toward the right spaces (meta arrows gives each direction in model space).

Pivot = bottom-centre of the footing.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
POST_H = 9.2
BL, BH, BT = 5.0, 0.85, 0.16   # board body length (incl. tip), height, thickness
TIP = 0.55
BOARDS = [("TEST KITCHEN", 8.15, -1, C.BRAND, C.CREAM),
          ("LOCKERS", 7.05, 1, C.NAVY, C.CREAM),
          ("SHOP", 5.95, -1, C.MUSTARD, C.NAVY),
          ("VANS", 4.85, 1, C.CREAM, C.BRAND)]


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
        boards.setdefault(bcol, []).append(b)
        w = min(len(txt) * 0.36, BL - TIP - 0.35 - 0.3 - 0.45)   # between the post clamp and the tip
        tx = d * (0.3 + (BL - TIP - 0.35)) / 2
        f = C.text(txt, 0.5, 0.04, (tx, -BT / 2 - 0.0, z), width=w, res=1, spacing=1.06, flat=True)
        bk = C.text(txt, 0.5, 0.04, (tx, BT / 2 + 0.0, z), width=w, res=1, spacing=1.06, facing="+Y", flat=True)
        letters.setdefault(tcol, []).extend([f, bk])
    names = {C.BRAND: "Red", C.NAVY: "Navy", C.MUSTARD: "Mustard", C.CREAM: "Cream"}
    for col, objs in boards.items():
        C.part(objs, "Board" + names[col], col, smooth_angle=40)
    for col, objs in letters.items():
        C.part(objs, "Text" + names[col], col, smooth_angle=None)
    clamps = [ns.box((0.5, 0.5, 0.18), loc=(0, 0, z), bevel=0.03, segments=1) for _, z, _, _, _ in BOARDS]
    C.part(fin[:1], "Finial", C.MUSTARD, smooth_angle=60)
    C.part(clamps + fin[1:], "Clamps", C.CHROME, "Metal", smooth_angle=40)


META = {"arrows": {t: ("Roblox +X" if d < 0 else "Roblox -X") for t, _, d, _, _ in BOARDS},
        "boards": [t for t, *_ in BOARDS], "height": POST_H + 0.55}

if __name__ == "__main__":
    C.run(build, "Lobby_SignPost", meta=META)
