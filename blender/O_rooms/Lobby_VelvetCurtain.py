"""Lobby_VelvetCurtain — heavy draped red-velvet wall curtain (8 W x 16 H x 1 D), wall-mounted.

A moulded gold cornice board (the pelmet) with a scalloped red-velvet swag valance under it,
edged with a gold cord and four gold tassels. Below, two heavy pleated velvet panels part in
the middle and are gathered by gold rope tie-backs (each with a tassel and a gold holdback rosette
on the wall), flaring out again to the floor; behind them a straight pleated backdrop in darker
velvet. The panels are double-sided (Roblox draws one side only), so oblique views stay solid.

Wall-mounted: back face on the wall plane (Blender y = 0), front -Y; pivot = bottom-centre of the
back face (the hems touch the floor at pivot height). No collision. No sockets.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
W, H, D = 8.0, 16.0, 1.0
TOP_Z = 15.36                 # panels / backdrop top (under the pelmet)
TIE_Z = 6.0
X_OUT = W / 2 - 0.06
PANEL_Y = -0.5                # front panels' mid plane
ROWS = (0.0, 1.6, 3.2, 4.6, 5.5, 6.0, 6.6, 8.2, 10.2, 12.6, TOP_Z)
COLS, FOLDS = 10, 4
SWAG_Z = (14.5, 14.95)        # scallop dip / junction height


def x_in(z):
    """Inner (parting) edge of the right panel at height z."""
    if z >= TIE_Z:
        s = (z - TIE_Z) / (TOP_Z - TIE_Z)
        return 2.72 - 2.68 * s ** 1.25
    s = (TIE_Z - z) / TIE_Z
    return 2.72 - 0.95 * s ** 0.75


def panel(side):
    """One tied-back pleated panel as a closed double sheet (front faces -Y)."""
    bm = C.bmesh.new()
    front, back = [], []
    for z in ROWS:
        xi = x_in(z)
        width = X_OUT - xi
        amp = 0.05 + 0.24 * max(0.0, min(1.0, 1.0 - width / (X_OUT - 0.04)))
        bunch = 0.12 * math.exp(-((z - TIE_Z) / 1.3) ** 2)
        rf, rb = [], []
        for k in range(COLS + 1):
            u = k / COLS
            x = xi + width * u
            y = PANEL_Y + amp * math.sin(2 * math.pi * FOLDS * u + 0.6) - bunch * (1.0 - u) ** 0.5
            rf.append(bm.verts.new((side * x, y, z)))
            rb.append(bm.verts.new((side * x, y + 0.05, z)))
        front.append(rf)
        back.append(rb)
    faces_f, faces_b = [], []
    for r in range(len(ROWS) - 1):
        for k in range(COLS):
            faces_f.append(bm.faces.new([front[r][k], front[r][k + 1], front[r + 1][k + 1], front[r + 1][k]]))
            faces_b.append(bm.faces.new([back[r][k], back[r + 1][k], back[r + 1][k + 1], back[r][k + 1]]))
    # close the parting edge and the hem
    for r in range(len(ROWS) - 1):
        bm.faces.new([front[r][0], front[r + 1][0], back[r + 1][0], back[r][0]])
    for k in range(COLS):
        bm.faces.new([front[0][k], back[0][k], back[0][k + 1], front[0][k + 1]])
    C.bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])   # consistent winding over the double sheet
    bm.normal_update()
    if sum(f.normal.y for f in faces_f) > 0:      # make sure the front sheet faces -Y (the room)
        for f in bm.faces:
            f.normal_flip()
    return ns.from_bmesh(bm, "Panel")


def backdrop():
    """Straight pleated backdrop (single sheet, front faces -Y; its back is against the wall)."""
    bm = C.bmesh.new()
    n = 32
    lo = [bm.verts.new((-X_OUT + 2 * X_OUT * k / n, -0.1 - 0.04 * math.sin(math.pi * k / 2), 0.0)) for k in range(n + 1)]
    hi = [bm.verts.new((v.co.x, v.co.y, TOP_Z)) for v in lo]
    for k in range(n):
        f = bm.faces.new([lo[k], lo[k + 1], hi[k + 1], hi[k]])
    bm.normal_update()
    if sum(f.normal.y for f in bm.faces) > 0:
        for f in bm.faces:
            f.normal_flip()
    return ns.from_bmesh(bm, "Backdrop")


def scallop_outline():
    """Swag valance front outline (x, z): flat top, three scallops along the bottom."""
    pts = [(-W / 2, 15.38), (W / 2, 15.38), (W / 2, SWAG_Z[1])]
    xs = (W / 2, W / 6, -W / 6, -W / 2)
    for a, b in zip(xs[:-1], xs[1:]):
        for k in range(1, 7):
            t = k / 6
            x = a + (b - a) * t
            pts.append((x, SWAG_Z[1] - (SWAG_Z[1] - SWAG_Z[0]) * math.sin(math.pi * t)))
    return pts


def tassel(top, length=0.55, r=0.13):
    """Gold tassel hanging from `top`: knob + flared skirt."""
    x, y, z = top
    knob = C.spheres([(x, y, z - 0.08)], 0.09, segs=5, rings=3)
    skirt = ns.cyl(r * 0.45, length, loc=(x, y, z - 0.16 - length / 2), verts=6, radius_top=r * 0.25, bevel=0.0)
    ns.apply_all(skirt)
    for v in skirt.data.vertices:     # flare the bottom
        if v.co.z < z - 0.16 - length / 2:
            v.co.x = x + (v.co.x - x) * 2.2
            v.co.y = y + (v.co.y - y) * 2.2
    return [knob, skirt]


def build():
    velvet = [panel(1), panel(-1)]
    swag = C.prism(scallop_outline(), "y", -0.92, -0.08)
    ns.bevel(swag, width=0.05, segments=1)
    velvet.append(swag)
    C.part(velvet, "Velvet", C.VELVET, "Fabric", smooth_angle=55)
    C.part([backdrop()], "Backdrop", C.VELVET_DARK, "Fabric", smooth_angle=55)

    gold = []
    corn = C.fillet([(0.0, 15.32), (-0.97, 15.32), (-1.0, 15.42), (-1.0, 15.72), (-0.9, 15.8), (-1.0, 15.88), (-1.0, 16.0),
                     (0.0, 16.0)], [0, 0.02, 0.02, 0.04, 0.04, 0.02, 0.02, 0], 1)
    cornice = C.prism(corn, "x", -W / 2, W / 2)
    ns.bevel(cornice, width=0.025, segments=1)
    gold.append(cornice)
    gold.append(C.pipe([(x * 0.985, -0.93, z) for x, z in scallop_outline()[2:]], 0.06, sides=4))
    for x in (W / 2 - 0.17, W / 6, -W / 6, -W / 2 + 0.17):
        gold += tassel((x, -0.86, SWAG_Z[1] - 0.02))
    # tie-backs: rope loop round each gathered panel, a tassel at the parting side, a rosette holdback
    for side in (1, -1):
        xi = x_in(TIE_Z)
        loop = []
        for k in range(14):
            a = 2 * math.pi * k / 14
            x = (xi + X_OUT) / 2 + (X_OUT - xi) / 2 * 0.97 * math.cos(a)
            y = PANEL_Y - 0.1 + 0.36 * math.sin(a)
            loop.append((side * x, min(y, -0.08), TIE_Z + 0.06 * math.sin(2 * a)))
        gold.append(C.pipe(loop, 0.07, sides=4, closed=True))
        gold += tassel((side * (xi + 0.02), PANEL_Y - 0.36, TIE_Z - 0.05), length=0.7, r=0.16)
        ros = ns.cyl(0.24, 0.1, verts=8, bevel=0.0)
        C.place(ros, (side * (X_OUT - 0.2), -0.06, TIE_Z + 0.42), pitch=90)
        gold.append(ros)
    C.part(gold, "Gold", C.GOLD, "Metal", smooth_angle=50)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (on the wall plane); hems at pivot height",
        "wall_back_z": 0.0, "collide": False}

if __name__ == "__main__":
    C.run(build, "Lobby_VelvetCurtain", mount="wall", budget=2000, pivot=(0, 0, 0), meta=META, backdrop="#3A2440",
          views=((-28, 10, False), (40, 6, True)))
