"""World_Guardrail — road W-beam guardrail segment (8 long x 2.4 tall).

Galvanised steel W-beam (two ridges toward the road, -Y) bolted through wooden spacer
blocks to two weathered wooden posts. The beam runs exactly x = -4 .. +4 with flat ends,
so segments chain along X every 8 studs (posts land every 4 studs along a run: x = +/-2).
Exports as 2 MeshParts (Metal beam + bolt heads, Wood posts + blocks), no collision.
Pivot = ground level on the post line, centre of the segment (origin).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
HALF = 4.0
ZC = 1.82                 # beam centre height
BEAM_BACK = -0.62         # beam back plane (road side of the spacer blocks)
T = 0.07                  # sheet thickness
STEEL = "#A7AEB3"
POST = "#5E4B3B"
BOLT = "#4A4F55"


def w_profile():
    """Closed (y, z) cross-section of the W-beam: front surface bottom->top, then back."""
    front = [(0.0, -0.5), (-0.32, -0.36), (-0.32, -0.2), (-0.1, -0.06), (-0.1, 0.06),
             (-0.32, 0.2), (-0.32, 0.36), (0.0, 0.5)]
    back = [(y + T, z) for y, z in reversed(front)]
    return [(BEAM_BACK + y, ZC + z) for y, z in front + back]


def build():
    beam = C.prism(w_profile(), "x", -HALF, HALF)
    bolts = []
    for x in (-2.0, 2.0):
        # bolt heads on the front of the valley (valley front face at y = BEAM_BACK - 0.1)
        bolts.append(C.bipyramid(0.09, 0.06, (x, BEAM_BACK - 0.1, ZC), sides=4))
    C.part([beam] + bolts, "Beam", STEEL, "Metal", smooth_angle=None)

    wood = []
    for x in (-2.0, 2.0):
        wood.append(C.box((0.5, 0.5, 2.4), loc=(x, 0.0, 1.2), bevel=0.04))
        # spacer block: from just inside the valley's back face to just inside the post,
        # kept below the beam lips (|z| < 0.4) so nothing pokes through the sheet
        y0, y1 = BEAM_BACK - 0.1 + T - 0.01, -0.2
        wood.append(C.box((0.4, y1 - y0, 0.8), loc=(x, (y0 + y1) / 2, ZC), bevel=0.0))
    C.part(wood, "Posts", POST, "Wood", smooth_angle=None)


META = {"kind": "guardrail", "chain": "along X every 8 studs (flat beam ends at x = +/-4)",
        "pivot": "ground level, post line, segment centre", "road_side": "front (-Z in Roblox)"}

if __name__ == "__main__":
    C.run(build, "World_Guardrail", meta=META)
