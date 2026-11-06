"""Basement_StorageCagePanel — a plain 4-stud section of the storage cage's wire wall (no gate).

The same galvanised square-tube frame and welded grid as Basement_StorageCage (end posts, top
rail, bottom rail, a mid rail at 5.0, grid bars 0.5 apart with the verticals in front of the
horizontals), half as wide and without the gate, so the cage can close a gap shorter than a full
section. 2026-11-05 (Landon: "fence not all the way around"): it fills the 4 studs between the
cage's east section and the basement's north wall. Rust creeps up the post feet.
Frame and grid collide. Front faces -Y, pivot = bottom-centre. 4 x 10 x 0.4; butts end to end
with the 8-stud section (end posts at x = +-1.91).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import Basement_StorageCage as SC  # noqa: E402  (its tube / grid helpers and frame sizes)

ns = C.ns
W, H, T = 4.0, SC.H, SC.T


def build():
    hw = W / 2 - T / 2
    zt = H - T / 2                                                                 # top rail centre line
    frame = [SC.tube(-hw, 0.05, -hw, zt), SC.tube(hw, 0.05, hw, zt),                 # end posts (on their feet)
             SC.tube(-W / 2 + 0.008, zt, W / 2 - 0.008, zt),                       # top rail
             SC.tube(-hw, T / 2 + 0.06, hw, T / 2 + 0.06),                          # bottom rail
             SC.tube(-hw, 5.0, hw, 5.0)]                                           # mid rail
    feet = [ns.box((T + 0.06, 0.42, 0.05), loc=(x + (0.03 if x < 0 else -0.03), 0, 0.025), bevel=0.0)
            for x in (-hw, hw)]
    C.part(frame + feet, "Frame", C.STEEL, "Metal", can_collide=True, smooth_angle=40)

    # the welded grid, split by the mid rail like the full section's side panels
    e = T / 2 - 0.01
    wires = SC.grid(-hw + e, hw - e, T + 0.02, 5.0, phase_x=0.25)
    wires += SC.grid(-hw + e, hw - e, 5.0, H - T + 0.01, phase_x=0.25)
    C.part(wires, "Grid", SC.WIRE, "Metal", can_collide=True, smooth_angle=None)

    # rust at the post feet (patches stay inside the 0.18-wide post faces)
    rust = []
    for k, x in enumerate((-hw, hw)):
        b = C.blob(0, 0, 0.075, 0, seed=30 + k)
        for v in b.data.vertices:
            v.co.z *= 2.4
        C.place([b], loc=(x, -T / 2 - 0.008, 0.32))
        rust.append(b)
    C.part(rust, "Rust", C.RUST, smooth_angle=None)

    meta = {"collide": "frame and grid",
            "tile": "butts end to end with Basement_StorageCage (end posts at x = +-1.91)"}
    return {"export": {"meta": meta, "pivot": (0.0, 0.0, 0.0)}}


if __name__ == "__main__":
    C.run(build, "Basement_StorageCagePanel", budget=2000, views=((-28, 12, False), (25, 8, True)))
