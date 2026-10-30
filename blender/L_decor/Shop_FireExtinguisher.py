"""Shop_FireExtinguisher — red fire extinguisher on a wall bracket with a FIRE sign above.

Glossy red cylinder with a domed shoulder and a cream label band (printed lines), chrome valve with a black
carry handle and squeeze lever, a pressure gauge, a black hose looping down the right side
to a nozzle clipped to the body. It sits in a dark steel bracket (back plate, strap and a
foot cup). Above: a small red sign with white "FIRE" letters and an arrow pointing down.
Wall-mounted: pivot = bottom-centre of the back face (+Y, touches the wall). 0.8 x 2.6 x 0.7.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
R = 0.19                  # body radius
BY = -0.06 - R            # body axis y (bracket plate 0.06 thick)
BZ = 0.08                 # body bottom
BH = 1.12                 # body height to the shoulder top
BX = -0.08                # body axis x (hose on the +X side)
BLACK = "#1B1C1F"
SIGN_RED = "#C9332B"


def build():
    body = ns.lathe([(0.0, 0.0), (R - 0.03, 0.0), (R, 0.04), (R, BH - 0.16), (R * 0.82, BH - 0.06), (R * 0.45, BH),
                     (0.0, BH)], verts=10, loc=(BX, BY, BZ))
    C.part([body], "Body", C.EXT_RED, smooth_angle=50)
    label = C.band(R + 0.006, 0.36, loc=(BX, BY, BZ + 0.5), verts=10)
    C.part([label], "Label", "#EEE6D2", smooth_angle=50)
    ly = BY - R - 0.012
    lines = [C.quad_xz(BX - 0.1, BX + 0.1, BZ + 0.6, BZ + 0.64, ly), C.quad_xz(BX - 0.1, BX + 0.04, BZ + 0.5, BZ + 0.53, ly),
             C.quad_xz(BX - 0.1, BX + 0.07, BZ + 0.42, BZ + 0.45, ly)]
    C.part(lines, "LabelPrint", C.INK, smooth_angle=None)

    # valve: neck, head, squeeze lever + carry handle, gauge
    vz = BZ + BH
    chrome = [ns.cyl(0.06, 0.1, loc=(BX, BY, vz + 0.04), verts=6, bevel=0.0),
              ns.box((0.13, 0.15, 0.13), loc=(BX, BY - 0.01, vz + 0.14), bevel=0.0)]
    black = [ns.box((0.07, 0.38, 0.05), loc=(BX, BY - 0.12, vz + 0.235), rot=(-12, 0, 0), bevel=0.0),
             ns.box((0.07, 0.36, 0.05), loc=(BX, BY - 0.11, vz + 0.15), rot=(6, 0, 0), bevel=0.0)]
    gauge = ns.cyl(0.055, 0.04, loc=(BX - 0.1, BY - 0.02, vz + 0.15), rot=(0, 90, 0), verts=6, bevel=0.0)
    chrome.append(gauge)
    gface = C.face_dir(C.disc(0.042, verts=8), "+Z")
    gface.rotation_euler = (0, math.radians(-90), 0)
    gface.location = (BX - 0.122, BY - 0.02, vz + 0.15)
    ns.apply_all(gface)
    C.face_dir(gface, "-X")
    C.part([gface], "GaugeFace", "#F4F1E8", smooth_angle=None)
    needle = C.poly([(BX - 0.124, BY - 0.02, vz + 0.15), (BX - 0.124, BY - 0.045, vz + 0.18),
                     (BX - 0.124, BY - 0.035, vz + 0.185)])
    C.part([C.face_dir(needle, "-X")], "GaugeNeedle", "#2E9E4F", smooth_angle=None)
    # safety pin tag (yellow)
    tag = ns.box((0.012, 0.08, 0.1), loc=(BX + 0.075, BY - 0.07, vz + 0.12), bevel=0.0)
    C.part([tag], "PinTag", "#F2C94C", smooth_angle=None)

    # hose from the valve, looping down the right side to a nozzle clipped on the body
    hx = BX + R + 0.05
    hose = C.pipe([(BX + 0.06, BY - 0.02, vz + 0.12), (hx + 0.03, BY - 0.03, vz + 0.02), (hx + 0.05, BY - 0.04, BZ + 0.75),
                   (hx + 0.02, BY - 0.06, BZ + 0.42), (hx - 0.01, BY - 0.1, BZ + 0.3)], 0.032, sides=6)
    nozzle = ns.cyl(0.045, 0.2, loc=(hx - 0.02, BY - 0.12, BZ + 0.2), rot=(14, 0, 0), verts=6, radius_top=0.035, bevel=0.0)
    black += [hose, nozzle]
    C.part(chrome, "Valve", C.CHROME, "Metal", smooth_angle=45)
    C.part(black, "Hose", BLACK, smooth_angle=45)

    # bracket: back plate, strap round the body, foot cup
    brk = [ns.box((0.26, 0.06, 1.02), loc=(BX, -0.03, BZ + 0.5), bevel=0.0),
           C.band(R + 0.02, 0.07, loc=(BX, BY, BZ + 0.86), verts=10),
           ns.cyl(R + 0.03, 0.12, loc=(BX, BY, 0.06), verts=10, bevel=0.0)]
    C.part(brk, "Bracket", C.CHARCOAL, "Metal", smooth_angle=40)

    # FIRE sign above
    sz0, sz1, sw = 1.95, 2.6, 0.64
    sign = ns.box((sw, 0.04, sz1 - sz0), loc=(BX + 0.04, -0.02, (sz0 + sz1) / 2), bevel=0.012, segments=1)
    C.part([sign], "Sign", SIGN_RED, smooth_angle=30)
    fy = -0.04 - 0.008
    white = [C.text("FIRE", 0.2, 0.01, (BX + 0.04, fy + 0.005, sz1 - 0.19), width=0.48, res=1, spacing=1.08, flat=True),
             C.strip_xz((BX + 0.04, sz0 + 0.29), (BX + 0.04, sz0 + 0.14), 0.07, fy),
             C.face_dir(C.poly([(BX - 0.07, fy, sz0 + 0.15), (BX + 0.15, fy, sz0 + 0.15), (BX + 0.04, fy, sz0 + 0.05)]), "-Y")]
    C.part(white, "SignText", "#FBF8F0", smooth_angle=None)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)"}

if __name__ == "__main__":
    C.run(build, "Shop_FireExtinguisher", mount="wall", budget=500, meta=META)
