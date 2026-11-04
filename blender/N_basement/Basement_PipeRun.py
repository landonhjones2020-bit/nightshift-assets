"""Basement_PipeRun — 8-stud run of the basement's ceiling pipe bundle.

Three parallel pipes along X (front to back: grey, copper, dark grey; the order every
bundle piece shares, see _common.BUNDLE) resting on two galvanised trapeze hangers
(strut channel, threaded rods up to little ceiling plates, a U-bolt over each pipe) at
x = +-2, so hangers stay 4 apart along a tiled run. Half-couplings at both ends: two runs
butted end to end make one full coupling. Details: a flanged joint on the grey pipe, a
copper sweat coupling, a mustard ID band with an arrow on the dark pipe, two rust patches.
PIVOT = TOP-CENTRE (on the ceiling plane, z = 0); everything hangs below. Runs tile every
8 studs along X. No collision. 8 x 0.9 x 1.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L = 8.0
COLLAR = 0.13


def build():
    pipes = {name: [] for _o, _r, _c, name in C.BUNDLE}
    cols = {name: col for _o, _r, col, name in C.BUNDLE}
    for off, r, _col, name in C.BUNDLE:
        z = C.bundle_z(r)
        pipes[name].append(C.pipe([(-L / 2 + 0.02, off, z), (L / 2 - 0.02, off, z)], r, sides=8))
        for sx in (-1, 1):   # half couplings, flush with the run ends
            pipes[name].append(ns.cyl(r + 0.035, COLLAR, loc=(sx * (L / 2 - COLLAR / 2), off, z), rot=(0, 90, 0),
                                      verts=8, bevel=0.0))
    # flanged joint on the grey pipe, sweat coupling on the copper
    og, rg, _c, ng = C.BUNDLE[0]
    zg = C.bundle_z(rg)
    for x in (-0.04, 0.04):
        pipes[ng].append(ns.cyl(rg + 0.065, 0.07, loc=(x, og, zg), rot=(0, 90, 0), verts=8, bevel=0.0))
    oc, rc, _c, nc = C.BUNDLE[1]
    pipes[nc].append(ns.cyl(rc + 0.03, 0.24, loc=(1.2, oc, C.bundle_z(rc)), rot=(0, 90, 0), verts=8, bevel=0.0))
    for name, objs in pipes.items():
        C.part(objs, name, cols[name], "Metal", smooth_angle=50)

    hw = {"strut": [], "rods": [], "clamps": []}
    for x in (-2.0, 2.0):
        for k, v in C.pipe_bracket((x, 0.0), (1, 0)).items():
            hw[k] += v
    C.part(hw["strut"] + hw["rods"] + hw["clamps"], "Hangers", C.STEEL, "Metal", smooth_angle=45)

    # ID band + flow arrow on the dark pipe, rust patches on the greys
    od, rd, _c, _n = C.BUNDLE[2]
    zd = C.bundle_z(rd)
    band = ns.cyl(rd + 0.012, 0.4, loc=(-1.0, od, zd), rot=(0, 90, 0), verts=8, bevel=0.0)
    C.part([band], "IdBand", C.MUSTARD, smooth_angle=50)
    yf = od - (rd + 0.012) - 0.008
    arrow = [C.quad_xz(-1.14, -0.94, zd - 0.025, zd + 0.025, yf),
             C.face_dir(C.poly([(-0.94, yf, zd - 0.06), (-0.84, yf, zd), (-0.94, yf, zd + 0.06)]), "-Y")]
    C.part(arrow, "IdArrow", C.INK, smooth_angle=None)
    rust = [ns.cyl(rg + 0.01, 0.22, loc=(2.75, og, zg), rot=(0, 90, 0), verts=8, bevel=0.0),
            ns.cyl(rd + 0.01, 0.16, loc=(0.45, od, zd), rot=(0, 90, 0), verts=8, bevel=0.0)]
    C.part(rust, "Rust", C.RUST, "Metal", smooth_angle=50)


META = {"pivot": "top-centre, on the ceiling plane (hangs below)", "tile": "every 8 studs along X",
        "bundle": [{"lateral": o, "radius": r, "pipe": n} for o, r, _c, n in C.BUNDLE],
        "hangers_x": [-2.0, 2.0], "collide": "none"}

if __name__ == "__main__":
    C.run(build, "Basement_PipeRun", mount="hang", pivot=(0.0, 0.0, 0.0), budget=2000, meta=META,
          preview_fn=C.hang_preview())
