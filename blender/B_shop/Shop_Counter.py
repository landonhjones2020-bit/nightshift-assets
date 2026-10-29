"""Shop_Counter — front service counter, 16 long x 3 deep, top at 3.0.

Customer side = front (-Y): red panelled front with chrome posts and streamline "speed
lines", black/white checker band under a chrome-edged cream laminate top (rounded front
corners), recessed black toe-kick. Staff side (+Y): stainless cabinets and two open hiding
cubbies (HideA / HideB) with dark interiors and chrome trim.
Collision is split so neither cubby is inside any colliding part's bounding box.
Sockets (top surface z = 3.0):
  Register, TicketPrinter  yaw 180 = the prop's front faces the staff side (+Y)
  Bell                     customer edge
  Plate1..4                where served food lands, in front of each ServeSpot
  ServeSpot1..4            customer stand points 1.8 in front of the counter, facing it
  HideA, HideB             centres of the two cubbies, facing out (+Y, toward the staff side)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L, D, H = 16.0, 3.0, 3.0
FY = -1.2                       # front panel face (top overhangs to -1.5)
SY = 1.38                       # staff-side cabinet face
CUB = ((-5.4, -2.4), (2.4, 5.4))  # cubby x ranges
CZ0, CZ1 = 0.28, 2.5            # cubby floor / ceiling
CY0 = -0.9                      # cubby back
RED = "#B53A2E"
STEEL_DOOR = "#A7AFB6"


def build():
    # --- top: laminate over a chrome edge band, rounded customer corners
    outline = C.fillet([(-8, -1.5), (8, -1.5), (8, 1.5), (-8, 1.5)], [0.4, 0.4, 0.05, 0.05], 4)
    inner = C.fillet([(-7.94, -1.44), (7.94, -1.44), (7.94, 1.5), (-7.94, 1.5)], [0.36, 0.36, 0.0, 0.0], 4)
    band = C.prism(outline, "z", 2.78, 2.985)
    ns.bevel(band, width=0.03, segments=2)
    lam = C.prism(inner, "z", 2.86, 3.0)
    ns.bevel(lam, width=0.02, segments=1)
    C.part([lam], "Top", C.LAMINATE, can_collide=True, smooth_angle=40)

    # --- customer front: red panels, chrome posts/rails/speed lines, checker band, toe-kick
    front = ns.box((L - 0.2, 0.2, 1.84), loc=(0, FY + 0.1, 0.5 + 0.92), bevel=0.0)
    ns.tag(front, "FrontPanel", RED, recolor="counter_front", can_collide=True)
    ends = []
    for sx, nm in ((-1, "EndL"), (1, "EndR")):
        e = ns.box((0.2, SY - FY + 0.02, 2.3), loc=(sx * 7.9, (FY + SY) / 2, 0.5 + 1.15 - 0.1), bevel=0.04)
        ns.tag(e, nm, RED, recolor="counter_front", can_collide=True, smooth_angle=40)
        ends.append(e)

    chrome = [band]
    for x in (-8.0, -4.0, 0.0, 4.0, 8.0):
        chrome.append(ns.box((0.28, 0.12, 2.36), loc=(max(-7.92, min(7.92, x)), FY - 0.02, 0.5 + 1.15), bevel=0.04,
                             segments=1))
    for z in (0.5, 2.28):
        chrome.append(C.prism(C.fillet([(FY + 0.02, z - 0.05), (FY - 0.07, z - 0.05), (FY - 0.07, z + 0.05),
                                        (FY + 0.02, z + 0.05)], [0, 0.03, 0.03, 0], 1), "x", -7.95, 7.95))
    for px in (-6.0, -2.0, 2.0, 6.0):
        for i, z in enumerate((1.12, 1.32, 1.52)):
            ln = 3.1 - i * 0.55
            chrome.append(ns.box((ln, 0.05, 0.08), loc=(px - (3.1 - ln) / 2, FY - 0.02, z), bevel=0.025, segments=1))
    # staff side: cubby trims and cabinet handles
    for x0, x1 in CUB:
        cx = (x0 + x1) / 2
        for xx in (x0, x1):
            chrome.append(ns.box((0.14, 0.1, CZ1 - CZ0 + 0.14), loc=(xx, SY + 0.03, (CZ0 + CZ1) / 2), bevel=0.03,
                                 segments=1))
        for zz in (CZ0, CZ1):
            chrome.append(ns.box((x1 - x0 + 0.14, 0.1, 0.14), loc=(cx, SY + 0.03, zz), bevel=0.03, segments=1))
    C.part(chrome, "Trim", C.CHROME, "Metal", smooth_angle=40)

    dark, light = [], []
    band_cells_d = []
    for r in range(2):
        for i in range(64):
            xa = -8 + i * 0.25
            if (i + r) % 2 == 0:
                band_cells_d.append((xa, xa + 0.25, 2.28 + 0.05 + r * 0.225, 2.28 + 0.05 + (r + 1) * 0.225))
    light.append(ns.box((L - 0.2, 0.08, 0.45), loc=(0, FY - 0.04, 2.555), bevel=0.0))
    dark.append(C.tiles([(max(-7.9, a), min(7.9, b), c, d) for a, b, c, d in band_cells_d], FY - 0.08, 0.015, 0.006))
    C.part(light, "CheckerLight", C.CHECK_LIGHT)
    C.part(dark, "CheckerDark", C.CHECK_DARK)

    kick = ns.box((L - 0.3, SY - FY + 0.1, 0.5), loc=(0, (FY + SY) / 2 + 0.05, 0.25), bevel=0.03)
    ns.tag(kick, "Kick", C.BASE_DARK, can_collide=False, smooth_angle=40)

    # --- staff side: stainless cabinets (split around the cubbies), doors + handles
    segs = ((-7.8, CUB[0][0], "CabL"), (CUB[0][1], CUB[1][0], "CabMid"), (CUB[1][1], 7.8, "CabR"))
    doors, handles = [], []
    for x0, x1, nm in segs:
        cab = ns.box((x1 - x0, SY - FY - 0.2, 2.3), loc=((x0 + x1) / 2, (FY + 0.2 + SY) / 2, 0.5 + 1.15 - 0.15),
                     bevel=0.0)
        ns.tag(cab, nm, C.STAINLESS, "Metal", can_collide=True)
        n = max(1, int(round((x1 - x0) / 2.4)))
        w = (x1 - x0 - 0.2) / n
        for k in range(n):
            dx = x0 + 0.1 + w * (k + 0.5)
            doors.append(ns.box((w - 0.1, 0.06, 1.95), loc=(dx, SY + 0.02, 1.52), bevel=0.04, segments=1))
            hx = dx + (w / 2 - 0.3) * (1 if k % 2 == 0 else -1)
            handles.append(ns.box((0.09, 0.1, 0.55), loc=(hx, SY + 0.09, 1.8), bevel=0.03, segments=1))
    C.part(doors, "CabDoors", STEEL_DOOR, "Metal", smooth_angle=40)
    C.part(handles, "Handles", C.BASE_DARK, smooth_angle=60)

    # --- cubby interiors (dark, inward-facing liners; never colliding)
    for (x0, x1), nm in zip(CUB, ("CubbyA", "CubbyB")):
        cx = (x0 + x1) / 2
        liners = [ns.box((x1 - x0, 0.06, CZ1 - CZ0), loc=(cx, CY0 - 0.03, (CZ0 + CZ1) / 2), bevel=0.0),
                  ns.box((x1 - x0, SY - CY0, 0.06), loc=(cx, (CY0 + SY) / 2, CZ0 - 0.03), bevel=0.0),
                  ns.box((x1 - x0, SY - CY0, 0.06), loc=(cx, (CY0 + SY) / 2, CZ1 + 0.03), bevel=0.0),
                  ns.box((0.06, SY - CY0, CZ1 - CZ0), loc=(x0 - 0.03, (CY0 + SY) / 2, (CZ0 + CZ1) / 2), bevel=0.0),
                  ns.box((0.06, SY - CY0, CZ1 - CZ0), loc=(x1 + 0.03, (CY0 + SY) / 2, (CZ0 + CZ1) / 2), bevel=0.0)]
        C.part(liners, nm, C.DARK_VOID)


def sockets():
    s = {"Register": ((-6.0, 0.55, H), 180.0), "TicketPrinter": ((6.0, 0.7, H), 180.0),
         "Bell": ((-3.6, -0.85, H), 0.0),
         "HideA": (((CUB[0][0] + CUB[0][1]) / 2, (CY0 + SY) / 2, (CZ0 + CZ1) / 2), 180.0),
         "HideB": (((CUB[1][0] + CUB[1][1]) / 2, (CY0 + SY) / 2, (CZ0 + CZ1) / 2), 180.0)}
    for i, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
        s[f"ServeSpot{i + 1}"] = ((x, -1.5 - 1.8, 0.0), 180.0)
        s[f"Plate{i + 1}"] = ((x, -0.75, H), 180.0)
    return s


META = {"top": H, "size": [L, H, D], "customer_side": "front (-Y / LookVector)", "staff_side": "+Y",
        "hide_spots": ["HideA", "HideB"], "socket_yaw": "0 = facing the counter front direction (LookVector)",
        "collider": "Top, FrontPanel, EndL/EndR, CabL/CabMid/CabR (cubbies stay free)"}

if __name__ == "__main__":
    C.run(build, "Shop_Counter", meta=META, sockets=sockets())
