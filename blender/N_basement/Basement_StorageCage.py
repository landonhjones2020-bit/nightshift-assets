"""Basement_StorageCage — wire-mesh storage-cage wall section with a padlocked gate.

Galvanised square-tube frame (end posts, top rail, bottom rails, a mid rail on both side
panels, gate posts and a header over the gate) filled with a welded grid of thin bars
(verticals in front of the horizontals, 0.5 apart). The gate in the middle (part Gate,
role "gate"; it hinges on its left post, see META) has its own tube frame and grid; a hasp
on its right edge carries a brass padlock (part Padlock, role "padlock") and a faded
KEEP OUT plate hangs on it. Rust creeps up the post feet.
Frame, grid and gate collide. Front faces -Y, pivot = bottom-centre. 8 x 10 x 0.4.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H = 8.0, 10.0
T = 0.18                    # frame tube size
GX = 1.62                   # gate posts (centre x)
GATE_X0, GATE_X1 = -1.47, 1.47
GATE_Z0, GATE_Z1 = 0.22, 6.98
HEAD_Z = 7.2                # header rail over the gate
GT = 0.12                   # gate tube size
WIRE = "#7C8186"
STEP = 0.5
YV, YH = -0.024, 0.024      # verticals in front, horizontals behind (they never share a plane)


def tube(x0, z0, x1, z1, t=T):
    """Square tube spanning exactly x0..x1 (or t thick about x0) and z0..z1 (or t thick about
    z0) in the XZ plane. Joints: verticals stop on the rail centre lines, rails end 0.008
    inside the posts' outer faces, so no two tube faces ever share a plane."""
    sx = abs(x1 - x0) if x0 != x1 else t
    sz = abs(z1 - z0) if z0 != z1 else t
    return ns.box((sx, t, sz), loc=((x0 + x1) / 2, 0.0, (z0 + z1) / 2), bevel=0.0)


def grid(x0, x1, z0, z1, phase_x=0.0):
    """Welded wire grid filling the rectangle (bars run into the surrounding tubes)."""
    bars = []
    x = x0 + ((phase_x - x0) % STEP or STEP)
    while x < x1 - 0.05:
        bars.append(ns.box((0.045, 0.045, z1 - z0), loc=(x, YV, (z0 + z1) / 2), bevel=0.0))
        x += STEP
    z = z0 + STEP
    while z < z1 - 0.05:
        bars.append(ns.box((x1 - x0, 0.045, 0.045), loc=((x0 + x1) / 2, YH, z), bevel=0.0))
        z += STEP
    return bars


def build():
    hw = W / 2 - T / 2
    zt = H - T / 2                                                                 # top rail centre line
    frame = [tube(-hw, 0.05, -hw, zt), tube(hw, 0.05, hw, zt),                     # end posts (on their feet)
             tube(-W / 2 + 0.008, zt, W / 2 - 0.008, zt),                          # top rail
             tube(-GX, 0.05, -GX, zt), tube(GX, 0.05, GX, zt),                     # gate posts
             tube(-GX, HEAD_Z, GX, HEAD_Z)]                                        # header
    for sx in (-1, 1):
        frame.append(tube(sx * hw, T / 2 + 0.06, sx * GX, T / 2 + 0.06))           # bottom rails
        frame.append(tube(sx * hw, 5.0, sx * GX, 5.0))                             # mid rails
    feet = [ns.box((T + 0.06 if abs(x) > 3 else 0.42, 0.42, 0.05), loc=(x - (0.03 if x > 3 else -0.03 if x < -3 else 0), 0,
                                                                         0.025), bevel=0.0) for x in (-hw, -GX, GX, hw)]
    C.part(frame + feet, "Frame", C.STEEL, "Metal", can_collide=True, smooth_angle=40)

    # fixed grids: both side panels (split by the mid rail) and the panel over the gate
    wires = []
    e = T / 2 - 0.01
    for sx in (-1, 1):
        xa, xb = sorted((sx * (hw - e), sx * (GX + e)))
        wires += grid(xa, xb, T + 0.02, 5.0, phase_x=0.25)
        wires += grid(xa, xb, 5.0, H - T + 0.01, phase_x=0.25)
    wires += grid(-GX + e, GX - e, HEAD_Z, H - T + 0.01, phase_x=0.25)
    C.part(wires, "Grid", WIRE, "Metal", can_collide=True, smooth_angle=None)

    # gate: tube frame + grid + hinge knuckles + hasp (own part, role "gate")
    gx0, gx1 = GATE_X0 - GT / 2 + 0.008, GATE_X1 + GT / 2 - 0.008
    g = [tube(GATE_X0, GATE_Z0, GATE_X0, GATE_Z1, GT), tube(GATE_X1, GATE_Z0, GATE_X1, GATE_Z1, GT),
         tube(gx0, GATE_Z0, gx1, GATE_Z0, GT), tube(gx0, GATE_Z1, gx1, GATE_Z1, GT),
         tube(GATE_X0, 3.6, GATE_X1, 3.6, GT)]
    g += grid(GATE_X0 + GT / 2 - 0.01, GATE_X1 - GT / 2 + 0.01, GATE_Z0, 3.6, phase_x=0.25)
    g += grid(GATE_X0 + GT / 2 - 0.01, GATE_X1 - GT / 2 + 0.01, 3.6, GATE_Z1, phase_x=0.25)
    hinge_x = -GX + T / 2 + 0.05
    for z in (0.9, 3.6, 6.3):
        g.append(ns.cyl(0.07, 0.34, loc=(hinge_x, -0.1, z), verts=8, bevel=0.0))
        g.append(ns.box((0.2, 0.04, 0.2), loc=(GATE_X0 + 0.03, -0.075, z), bevel=0.0))
    hasp = ns.box((0.26, 0.05, 0.4), loc=(GATE_X1 + 0.05, -0.085, 3.95), bevel=0.01, segments=1)
    g.append(hasp)
    C.part(g, "Gate", C.STEEL, "Metal", recolor="gate", can_collide=True, smooth_angle=40)
    staple = C.pipe([(GX - 0.06, -0.1, 3.86), (GX - 0.06, -0.2, 3.86), (GX - 0.06, -0.2, 4.04), (GX - 0.06, -0.1, 4.04)],
                    0.025, sides=4)
    C.part([staple], "Staple", C.STEEL, "Metal", smooth_angle=40)
    body, shackle, key = C.padlock((GX - 0.06, -0.2, 3.88), s=1.1)
    C.part([body, shackle], "Padlock", C.BRASS, "Metal", recolor="padlock", smooth_angle=40)
    C.part([key], "LockHole", C.DARK_VOID, smooth_angle=None)

    # KEEP OUT plate wired to the gate grid, rust at the post feet
    plate = ns.box((1.3, 0.03, 0.5), loc=(0.0, -0.075, 5.2), bevel=0.012, segments=1)
    C.part([plate], "Sign", C.BRAND, smooth_angle=40)
    word = C.stencil("KEEP OUT", 0.24, (0.0, -0.09, 5.2), width=1.05)
    C.part([word], "SignInk", C.CREAM, smooth_angle=None)
    rust = []
    for k, x in enumerate((-hw, -GX, GX, hw)):   # rust patches stay inside the 0.18-wide post faces
        b = C.blob(0, 0, 0.075, 0, seed=20 + k)
        for v in b.data.vertices:
            v.co.z *= 2.4
        C.place([b], loc=(x, -T / 2 - 0.008, 0.32))
        rust.append(b)
    C.part(rust, "Rust", C.RUST, smooth_angle=None)

    meta = {"gate_part": "Gate", "padlock_part": "Padlock", "gate_hinge": C.rbx((hinge_x, -0.1, 0.0), (0, 0, 0)),
            "gate_axis": C.rbx_dir((0, 0, 1)), "gate_open_deg": -100, "gate_opening": [round(GATE_X1 - GATE_X0, 2),
                                                                                       round(GATE_Z1, 2)],
            "collide": "frame, grid and gate", "tile": "sections butt end to end (end posts at x = +-3.91)"}
    return {"export": {"meta": meta, "pivot": (0.0, 0.0, 0.0)}}


if __name__ == "__main__":
    C.run(build, "Basement_StorageCage", budget=2000, views=((-28, 12, False), (25, 8, True)))
