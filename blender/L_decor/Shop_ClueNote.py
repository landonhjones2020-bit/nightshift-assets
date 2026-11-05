"""Shop_ClueNote — Mr. Usual's clue: a sticky note stuck on a wall (WALL PROP).

Landon, 2026-11-05: "for mr usual make actually sticky notes where we can see on the map on
the wall somewhere that way your not just searching for a button prompt". ClueService sticks
one on a wall at each of tonight's clue spots; the note's Read prompt sits on it.

A canary-yellow square note (1.1 x 1.1, a hair brighter than the decor stickies on the fridge
and the cork board, so the clue reads as different), flat on the wall along its sticky top and
curling away from it lower down, the bottom-right corner most. On its face:
  * Mr. Usual's mark - his hat, a fedora drawn in red marker - so every clue looks like his;
  * three lines of dark scribbled handwriting;
  * a green check mark over it all, its own part (role "check"): the game hides it until
    someone has read the note, so a read note shows it's done.

Wall prop (L_decor/_common.py): back face on y = 0 touching the wall, the face looks at
Blender -Y = Roblox LookVector. The PIVOT is the centre of the back face (not the wall-prop
bottom-centre), so the game centres the note on the point it picks on the wall:
note:PivotTo(CFrame.lookAt(point, point + wallNormal)).
"""
import os
import random
import sys

import bpy  # noqa: F401  (must load before bmesh in the bpy module build)
import bmesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import Prop_Notepad as NP  # noqa: E402  (ribbon handwriting)

ns = C.ns

W, H, T = 1.1, 1.1, 0.014      # note size and paper thickness
NX, NZ = 6, 8                  # sheet grid (the curl bends along it)
CURL = 0.11                    # bottom edge's lift off the wall (studs), mid-width
CURL_FROM = 0.62               # the note lies flat above this fraction of its height
CURL_TWIST = 0.5               # the right corner lifts (1 + this/2) x, the left (1 - this/2) x

PAPER = "#FFE14A"              # canary (decor stickies are C.STICKY #F4D85A)
INK = "#2A2C33"                # handwriting
MARKER = "#C42B2B"             # Mr. Usual's hat
CHECK = "#2E8B4E"              # read: green check
INK_Y = -T - 0.003             # ink layer just in front of the paper face
CHECK_Y = -T - 0.006


def sheet():
    """Closed paper sheet, back face on y = 0, front on y = -T, z from 0 to H, gridded so it
    can curl."""
    bm = bmesh.new()
    grid = {}
    for side, y in (("b", 0.0), ("f", -T)):
        for i in range(NX + 1):
            for k in range(NZ + 1):
                grid[side, i, k] = bm.verts.new((-W / 2 + W * i / NX, y, H * k / NZ))
    for i in range(NX):
        for k in range(NZ):
            bm.faces.new([grid["f", i, k], grid["f", i + 1, k], grid["f", i + 1, k + 1], grid["f", i, k + 1]])
            bm.faces.new([grid["b", i, k + 1], grid["b", i + 1, k + 1], grid["b", i + 1, k], grid["b", i, k]])
    for i in range(NX):           # bottom and top edges
        for k in (0, NZ):
            bm.faces.new([grid["f", i, k], grid["f", i + 1, k], grid["b", i + 1, k], grid["b", i, k]])
    for k in range(NZ):           # left and right edges
        for i in (0, NX):
            bm.faces.new([grid["f", i, k], grid["f", i, k + 1], grid["b", i, k + 1], grid["b", i, k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, "Sheet")


def scribble_line(x0, x1, z, rnd, h=0.055, w=0.022):
    """One line of quick marker handwriting between x0 and x1 on baseline z: words of up/down
    strokes with gaps, the odd tall ascender, slanted forward."""
    out = []
    x = x0
    while x < x1 - 0.08:
        pts = []
        for k in range(rnd.randint(5, 9)):
            if k % 2:
                pts.append((x + 0.012, z + h * (1.35 if rnd.random() < 0.2 else rnd.uniform(0.5, 1.0))))
            else:
                pts.append((x, z + rnd.uniform(-0.006, 0.006)))
            x += rnd.uniform(0.026, 0.036)
            if x > x1:
                break
        if len(pts) >= 3:
            out.append(NP.ribbon(pts, w, INK_Y))
        x += rnd.uniform(0.05, 0.075)
    return out


def hat():
    """Mr. Usual's fedora in red marker, centred near the top of the note."""
    cz = 0.80 * H
    brim = [(-0.28, cz + 0.035), (-0.24, cz + 0.016), (-0.17, cz + 0.002), (0.0, cz - 0.008), (0.17, cz + 0.002),
            (0.24, cz + 0.016), (0.28, cz + 0.035)]
    # rounded crown with the pinch on top: up the left side, over two humps, down the right
    crown = [(-0.155, cz + 0.004), (-0.152, cz + 0.07), (-0.142, cz + 0.12), (-0.118, cz + 0.155),
             (-0.08, cz + 0.172), (-0.04, cz + 0.166), (0.0, cz + 0.148), (0.04, cz + 0.166), (0.08, cz + 0.172),
             (0.118, cz + 0.155), (0.142, cz + 0.12), (0.152, cz + 0.07), (0.155, cz + 0.004)]
    band = [(-0.15, cz + 0.038), (0.0, cz + 0.034), (0.15, cz + 0.038)]
    # (the band sits a hair in front of the crown and brim strokes it crosses: no z-fighting)
    return [NP.ribbon(brim, 0.034, INK_Y), NP.ribbon(crown, 0.03, INK_Y), NP.ribbon(band, 0.05, INK_Y - 0.0015)]


def check():
    return [NP.ribbon([(-0.27, 0.47), (-0.07, 0.24), (0.33, 0.72)], 0.075, CHECK_Y)]


def curl(objs):
    """Bend everything below CURL_FROM x H away from the wall (toward -Y), quadratically, the
    right corner a little more than the left."""
    z0 = CURL_FROM * H
    for o in objs:
        ns.apply_all(o)
        for v in o.data.vertices:
            s = max(0.0, min(1.0, (z0 - v.co.z) / z0))
            u = (v.co.x + W / 2) / W
            v.co.y -= CURL * s * s * (1.0 - CURL_TWIST / 2 + CURL_TWIST * u)
        o.data.update()


def build():
    rnd = random.Random(23)
    paper = sheet()
    ink = []
    for z, x1 in ((0.52 * H, W / 2 - 0.12), (0.37 * H, W / 2 - 0.08), (0.22 * H, W / 2 - 0.30)):
        ink += scribble_line(-W / 2 + 0.12, x1, z, rnd)
    red = hat()
    tick = check()
    curl([paper] + ink + red + tick)
    C.part(paper, "Paper", PAPER, smooth_angle=30)
    C.part(ink, "Writing", INK, smooth_angle=None)
    C.part(red, "Hat", MARKER, smooth_angle=None)
    C.part(tick, "Check", CHECK, smooth_angle=None, recolor="check")


META = {"mount": "wall: back face on the wall, pivot = centre of the back face, LookVector = out of the wall",
        "check": "part Check (Role 'check') is hidden by the game until the note has been read"}
VIEWS = ((-30, 12, False), (38, 6, True))

if __name__ == "__main__":
    C.run(build, "Shop_ClueNote", views=VIEWS, mount="wall", budget=600, pivot=(0.0, 0.0, H / 2), meta=META)
