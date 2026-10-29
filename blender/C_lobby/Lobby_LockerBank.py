"""Lobby_LockerBank — row of 4 staff lockers (6 wide x 7 tall x 2 deep).

Darker STACKHOUSE-red carcass on a black plinth with a sloped top cap; four red-orange
doors (Doors, role "locker_door"; hinged on the right, latch on the left) with louvre vents
top and bottom, chrome lift latches and brass oval number tags with modelled navy digits
1-4 (numbered left to right as seen from the front). Door 3 stands ajar (30 deg) on its
hinge, showing a dark interior with a shelf, a folded STACKHOUSE cap and a mustard apron
on a hook.

Front = -Y, pivot = bottom-centre. Collides (carcass + doors). Socket Prompt = in front of
the bank at chest height (open the Locker / Uniforms screen); Locker1..Locker4 = centre
of each closed door face (yaw 0).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D = 6.0, 2.0
Z0, Z1 = 0.4, 6.75            # carcass body (above the plinth)
LW = W / 4                    # locker pitch
DOOR_Z = (0.55, 6.6)
FY = -D / 2                   # carcass front plane
AJAR = 3                      # which locker is open
AJAR_DEG = 30
CARCASS = "#9E3524"
INTERIOR = "#2A2C30"
DOOR_RED = "#D9472B"


def door_geo(i):
    """Door i (1..4) parts in its CLOSED position: slab, vents, latch, tag, digit."""
    x0 = -W / 2 + (i - 1) * LW
    xc = x0 + LW / 2
    dw, dz0, dz1 = LW - 0.08, DOOR_Z[0], DOOR_Z[1]
    zc = (dz0 + dz1) / 2
    slab = ns.box((dw, 0.09, dz1 - dz0), loc=(xc, FY - 0.05, zc), bevel=0.03, segments=1)
    vents = []
    for zb in (dz1 - 0.55, dz0 + 0.35):
        for k in range(4):
            vents.append(ns.box((dw - 0.5, 0.03, 0.07), loc=(xc, FY - 0.105, zb - k * 0.14), bevel=0.0))
    latch = [ns.box((0.14, 0.08, 0.55), loc=(xc - dw / 2 + 0.22, FY - 0.13, 3.35), bevel=0.03, segments=1),
             ns.box((0.1, 0.12, 0.2), loc=(xc - dw / 2 + 0.22, FY - 0.2, 3.25), bevel=0.02, segments=1)]
    tag = C.prism(C.ellipse_pts(0.44, 0.31, 12, xc, dz1 - 1.15), "y", FY - 0.14, FY - 0.08)
    digit = C.text(str(i), 0.46, 0.05, (xc, FY - 0.15, dz1 - 1.15), res=1, back=False)
    return {"slab": [slab], "vent": vents, "chrome": latch, "brass": [tag], "digit": [digit], "hinge_x": x0 + LW - 0.04}


def build():
    plinth = ns.box((W - 0.1, D - 0.2, Z0), loc=(0, 0.05, Z0 / 2), bevel=0.04, segments=1)
    carcass = ns.box((W, D, Z1 - Z0), loc=(0, 0, (Z0 + Z1) / 2), bevel=0.05, segments=1)
    # cavity behind the ajar door
    ax0 = -W / 2 + (AJAR - 1) * LW
    ns.boolean(carcass, ns.box((LW - 0.14, D - 0.12, DOOR_Z[1] - DOOR_Z[0] - 0.1),
                               loc=(ax0 + LW / 2, FY + (D - 0.12) / 2 - 0.01, (DOOR_Z[0] + DOOR_Z[1]) / 2), bevel=0.0))
    cap = C.prism(C.fillet([(FY - 0.05, Z1), (-FY + 0.02, Z1), (-FY + 0.02, Z1 + 0.5), (FY + 0.3, Z1 + 0.5), (FY - 0.05, Z1 + 0.15)],
                           [0, 0, 0.05, 0.05, 0.04], 1), "x", -W / 2, W / 2)
    C.part([carcass, cap], "Carcass", CARCASS, can_collide=True, smooth_angle=40)
    C.part([plinth], "Plinth", C.BLACK, can_collide=True, smooth_angle=40)

    slabs, vents, chrome, brass, digits = [], [], [], [], []
    for i in range(1, 5):
        g = door_geo(i)
        objs = g["slab"] + g["vent"] + g["chrome"] + g["brass"] + g["digit"]
        if i == AJAR:
            hx = g["hinge_x"]
            for o in objs:
                ns.apply_all(o)
            C.place(objs, (0, 0, 0))
            for o in objs:   # rotate about the hinge line (x = hx, y = FY - 0.05)
                for v in o.data.vertices:
                    v.co = C.yaw_point(tuple(v.co), AJAR_DEG, about=(hx, FY - 0.05, 0))
            # hinge knuckles
            for z in (1.3, 3.6, 5.9):
                chrome.append(ns.cyl(0.05, 0.4, loc=(hx + 0.03, FY - 0.06, z), verts=6, bevel=0.0))
        slabs += g["slab"]
        vents += g["vent"]
        chrome += g["chrome"]
        brass += g["brass"]
        digits += g["digit"]
    C.part(slabs, "Doors", DOOR_RED, recolor="locker_door", can_collide=True, smooth_angle=40)
    C.part(vents, "Vents", "#2B1A17", smooth_angle=None)
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    C.part(brass, "Tags", C.BRASS, "Metal", smooth_angle=40)
    C.part(digits, "Digits", C.NAVY, smooth_angle=None)

    # interior of the ajar locker: dark lining, shelf, hook + apron, folded cap
    xc = ax0 + LW / 2
    lining = ns.box((LW - 0.18, 0.04, DOOR_Z[1] - DOOR_Z[0] - 0.14), loc=(xc, 0.845, (DOOR_Z[0] + DOOR_Z[1]) / 2),
                    bevel=0.0)
    shelf = ns.box((LW - 0.16, D - 0.2, 0.06), loc=(xc, 0.02, 5.5), bevel=0.0)
    C.part([lining, shelf], "Interior", INTERIOR, smooth_angle=None)
    hook = C.pipe([(xc, 0.88, 4.9), (xc, 0.6, 4.9), (xc, 0.5, 4.75), (xc, 0.56, 4.62)], 0.035, sides=5)
    chrome_hook = [hook]
    C.part(chrome_hook, "Hook", C.CHROME, "Metal", smooth_angle=60)
    apron = C.prism([(xc - 0.3, 4.75), (xc + 0.3, 4.75), (xc + 0.45, 4.25), (xc + 0.5, 2.3), (xc - 0.5, 2.3), (xc - 0.45, 4.25)],
                    "y", 0.42, 0.5)
    strap = C.pipe([(xc - 0.22, 0.47, 4.74), (xc, 0.48, 4.98), (xc + 0.22, 0.47, 4.74)], 0.03, sides=4)
    pocket = ns.box((0.6, 0.03, 0.35), loc=(xc, 0.405, 3.2), bevel=0.0)
    C.part([apron, strap], "Apron", C.MUSTARD, "Fabric", smooth_angle=40)
    C.part([pocket], "ApronPocket", C.BRAND, "Fabric", smooth_angle=None)
    capd = ns.sphere(0.4, loc=(xc, 0.15, 5.53), scale=(1, 1, 0.55), segs=10, rings=5)
    ns.boolean(capd, ns.box((1, 1, 0.5), loc=(xc, 0.15, 5.28), bevel=0.0))
    brim = ns.box((0.55, 0.4, 0.04), loc=(xc, -0.32, 5.55), bevel=0.02, segments=1)
    C.part([capd, brim], "Cap", C.BRAND, "Fabric", smooth_angle=50)


def sockets():
    s = {"Prompt": ((0, FY - 1.6, 3.5), 0.0)}
    for i in range(1, 5):
        xc = -W / 2 + (i - 0.5) * LW
        s[f"Locker{i}"] = ((xc, FY - 0.1, sum(DOOR_Z) / 2), 0.0)
    return s


META = {"lockers": 4, "numbering": "1..4 left to right (front view)", "ajar": AJAR, "ajar_deg": abs(AJAR_DEG),
        "roles": {"locker_door": "Doors (all four, incl. the ajar one)"},
        "light_hint": {"type": "PointLight", "inside": "Locker3", "color": "#FFE2B0", "range": 4, "brightness": 0.5}}

if __name__ == "__main__":
    C.run(build, "Lobby_LockerBank", sockets=sockets(), meta=META)
