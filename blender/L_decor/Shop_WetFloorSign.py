"""Shop_WetFloorSign — yellow A-frame "CAUTION / WET FLOOR" floor sign.

Two tapered caution-yellow panels meeting at the top, with carry-handle slots that line up
through both panels. Front face: a black header band with yellow "CAUTION" letters, a
slipping-figure pictogram (modelled strokes) over a puddle, and "WET FLOOR" in black. The
back face repeats the band + CAUTION + figure (WET FLOOR only on the front: 400-tri budget).
Front faces -Y. Pivot = bottom-centre. ~1.2 x 2.2 x 1.0.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
H = 2.2                  # overall height
SPREAD = 0.47            # panel mid-plane bottom edge at y = +/- SPREAD
T = 0.06                 # panel thickness
TOP_GAP = T / 2          # mid-plane top edge at y = +/- TOP_GAP (inner faces meet at the top)
W0, W1 = 1.2, 0.9        # panel width at the bottom / top
THETA = math.degrees(math.atan2(SPREAD - TOP_GAP, H - 0.07))
LEN = (H - 0.07) / math.cos(math.radians(THETA))
INK = "#1B1C1F"


def panel_set(wet_floor=True):
    """One panel in its local frame: lying in the XZ plane, bottom edge on the origin,
    front face on y = -T/2 (facing -Y). Returns (yellow, ink, letters)."""
    yellow, ink, letters = [], [], []
    # 6-point outline (chamfered top corners) and a 6-point handle slot, paired point by point
    outer = C.fillet([(-W0 / 2, 0.0), (W0 / 2, 0.0), (W1 / 2, LEN), (-W1 / 2, LEN)], [0, 0, 0.2, 0.2], 1)
    sz = LEN - 0.25
    slot = [(-0.16, sz - 0.075), (0.16, sz - 0.075), (0.24, sz), (0.16, sz + 0.075), (-0.16, sz + 0.075), (-0.24, sz)]
    pnl = C.ring_slab(outer, slot, "y", -T / 2, T / 2)
    yellow.append(pnl)
    fy = -T / 2
    # header band + CAUTION (yellow letters on the black band)
    bz0, bz1 = LEN - 0.73, LEN - 0.44
    wb = W0 - (W0 - W1) * ((bz0 + bz1) / 2) / LEN - 0.1
    ink.append(C.quad_xz(-wb / 2, wb / 2, bz0, bz1, fy - 0.008))
    letters.append(C.text("CAUTION", 0.19, 0.01, (0, fy - 0.016 + 0.005, (bz0 + bz1) / 2), width=wb * 0.84, res=1,
                          spacing=1.06, flat=True))
    # slipping figure: falling backwards, one foot kicked up, arms flung out
    y = fy - 0.008
    s = 1.45
    b0 = (0.0, 0.8)
    P = lambda u, v: (b0[0] + u * s, b0[1] + v * s)  # noqa: E731
    head = C.disc(0.056 * s, loc=(0, 0, 0), verts=6)
    head.rotation_euler = (math.radians(90), 0, 0)
    hx, hz = P(-0.15, 0.36)
    head.location = (hx, y, hz)
    ns.apply_all(head)
    ink.append(C.face_dir(head, "-Y"))
    strokes = [((-0.1, 0.28), (0.02, 0.13), 0.072),     # torso (leaning back)
               ((0.02, 0.13), (0.13, 0.2), 0.058),      # kicked thigh
               ((0.13, 0.2), (0.24, 0.16), 0.052),      # kicked shin
               ((0.02, 0.13), (0.07, 0.06), 0.058),     # standing thigh
               ((0.07, 0.06), (0.15, 0.015), 0.052),    # standing shin
               ((-0.1, 0.27), (-0.24, 0.2), 0.045),     # arm back
               ((-0.08, 0.28), (0.05, 0.36), 0.045)]    # arm up
    for a, b, w in strokes:
        ink.append(C.strip_xz(P(*a), P(*b), w * s * 1.12, y))
    # puddle under the feet
    pts = [P(-0.24, -0.04), P(0.27, -0.04), P(0.31, 0.0), P(-0.29, 0.0)]
    ink.append(C.face_dir(C.poly([(u, y, v) for u, v in pts]), "-Y"))
    # WET FLOOR (two lines)
    if wet_floor:
        for txt, z, wfrac in (("WET", 0.6, 0.42), ("FLOOR", 0.36, 0.7)):
            ink.append(C.text(txt, 0.2, 0.01, (0, fy - 0.008 + 0.005, z), width=W0 * wfrac, res=1, spacing=1.06,
                              flat=True))
    return yellow, ink, letters


def build():
    yellow, ink, letters = [], [], []
    for side in (-1, 1):
        y_, i_, l_ = panel_set(wet_floor=side < 0)   # budget: WET FLOOR on the front face only
        grp = y_ + i_ + l_
        # front panel: tilt the top back (+Y); back panel: same tilt, turned 180 degrees
        C.place(grp, loc=(0, side * SPREAD, 0), pitch=-THETA, yaw=0 if side < 0 else 180)
        yellow += y_
        ink += i_
        letters += l_
    C.part(yellow + letters, "Panels", C.SAFETY_YELLOW, smooth_angle=35)
    C.part(ink, "Ink", INK, smooth_angle=None)


META = {"text": "front: CAUTION + slipping figure + WET FLOOR; back: CAUTION + slipping figure"}

if __name__ == "__main__":
    C.run(build, "Shop_WetFloorSign", budget=400, meta=META)
