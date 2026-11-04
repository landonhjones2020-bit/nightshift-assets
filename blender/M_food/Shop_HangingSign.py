"""Shop_HangingSign — chunky ceiling-hung station sign (M_food batch, group "Shop").

A 6 x 1.6 x 0.35 navy sign box wrapped in a chunky rounded mustard frame (front, sides and back),
with a thin mustard neon tube (part Neon, role "neon", material Neon) running round the face
inside the frame, hung from two short steel chains on round ceiling plates. The navy face carries
a flush 5.4 x 1.1 label panel (part Screen, role "screen", Front face) where the game draws a
SurfaceGui label (ORDER HERE, PICK UP, BUILD, TOAST); no baked text. Back: plain navy in the frame.
PIVOT = the ceiling mount: top centre, z = 0 (the ceiling plates' top face); the sign bottom hangs
3.2 below it. Front faces -Y. No collision.
Socket Screen = centre of the label panel, just in front of it, facing -Y (yaw 0).
Run:  bpyenv/bin/python blender/M_food/Shop_HangingSign.py   (NS_EXPORT=1 export)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
S = C.shop()
NAVY, MUSTARD, STEEL = "#1E2A44", "#F2B33D", "#6B727A"
W, H, D = 6.0, 1.6, 0.35          # sign box
BOTTOM = -3.2                      # sign bottom below the ceiling mount
ZC = BOTTOM + H / 2                # face centre height (-2.4)
TOP = BOTTOM + H                   # sign top (-1.6)
FRAME = 0.12                       # mustard frame width on the face
RECESS = 0.06                      # navy face sits this far behind the frame front
FACE_Y = -D / 2 + RECESS           # navy face plane (front)
SCR_W, SCR_H = 5.4, 1.1            # label panel (SurfaceGui area)
SCR_T = 0.012
CHAIN_X = 2.2
LINKS = 6


def link(x, z, quarter):
    """One elongated chain link centred at (x, 0, z), ring in the XZ plane (or YZ when quarter)."""
    t = ns.torus(0.085, 0.03, major_segs=6, minor_segs=4)
    t.rotation_euler = (math.radians(90), 0, math.radians(90 if quarter else 0))
    ns.apply_all(t)
    for v in t.data.vertices:
        v.co.z *= 1.5
    t.location = (x, 0, z)
    ns.apply_all(t)
    return t


def build():
    # navy sign box (inside the frame) and the label panel on its face
    body = S.prism(S.rrect(W - 0.1, H - 0.1, 0.16, segs=3), "y", -D / 2 + RECESS, D / 2 - RECESS)
    body.location.z = ZC
    ns.bevel(body, width=0.02, segments=1, angle=50)
    S.part([body], "Body", NAVY, "SmoothPlastic", smooth_angle=40)
    scr = S.prism(S.rrect(SCR_W, SCR_H, 0.06, segs=2), "y", FACE_Y - SCR_T, FACE_Y + 0.004)
    scr.location.z = ZC
    S.part([scr], "Screen", NAVY, "SmoothPlastic", recolor="screen", smooth_angle=30)

    # chunky rounded mustard frame round the whole edge (front lip, sides, back lip)
    frame = S.ring_slab(S.rrect(W, H, 0.2, segs=3), S.rrect(W - 2 * FRAME, H - 2 * FRAME, 0.1, segs=3), "y",
                        -D / 2, D / 2)
    frame.location.z = ZC
    ns.bevel(frame, width=0.035, segments=2, angle=50)
    # eye-bolt stems through the frame top
    stems = [ns.cyl(0.035, 0.12, loc=(sx * CHAIN_X, 0, TOP + 0.05), verts=8, bevel=0.0) for sx in (-1, 1)]
    S.part([frame], "Frame", MUSTARD, "SmoothPlastic", smooth_angle=45)

    # neon tube round the face, inside the frame
    path = [(x, FACE_Y - 0.045, ZC + z) for x, z in S.rrect(5.62, 1.22, 0.14, segs=3)]
    neon = S.pipe(path, 0.032, sides=6, closed=True)
    S.part([neon], "Neon", MUSTARD, "Neon", recolor="neon", cast_shadow=False, smooth_angle=60)

    # ceiling plates, chains and eye bolts
    steel = list(stems)
    z_top, z_bot = -0.24, TOP + 0.27
    for sx in (-1, 1):
        x = sx * CHAIN_X
        steel.append(ns.cyl(0.22, 0.07, loc=(x, 0, -0.035), verts=12, bevel=0.02, segments=1))
        steel.append(ns.cyl(0.05, 0.1, loc=(x, 0, -0.11), verts=6, bevel=0.0))
        for k in range(LINKS):
            steel.append(link(x, z_top + (z_bot - z_top) * k / (LINKS - 1), k % 2 == 1))
        eye = ns.torus(0.08, 0.03, major_segs=6, minor_segs=4)
        eye.rotation_euler = (math.radians(90), 0, math.radians(90 if LINKS % 2 == 1 else 0))
        eye.location = (x, 0, TOP + 0.13)
        steel.append(eye)
    S.part(steel, "Hardware", STEEL, "Metal", smooth_angle=60)

    sockets = {"Screen": ((0.0, FACE_Y - SCR_T - 0.02, ZC), 0.0)}
    meta = {"mount": "ceiling", "pivot": "ceiling mount (top centre, z = 0); the sign hangs below",
            "drop": round(-BOTTOM, 3), "screen_size": [SCR_W, SCR_H],
            "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
            "roles": {"screen": "Screen", "neon": "Neon"},
            "light_hint": {"type": "SurfaceLight", "part": "Neon", "color": MUSTARD, "range": 6}}
    return {"export": {"sockets": sockets, "meta": meta}}


def preview(asset, out_dir, res, samples):
    return C.angles_preview(asset, out_dir, res, samples, angles=((-28.0, -14.0), (32.0, 18.0)))


if __name__ == "__main__":
    C.run(build, "Shop_HangingSign", meta_=None, pivot=(0.0, 0.0, 0.0), group="Shop", preview=preview)
