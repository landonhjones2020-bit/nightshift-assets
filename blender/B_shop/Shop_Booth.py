"""Shop_Booth — diner booth pair: two red channel-tufted vinyl benches facing each other
across a chrome-edged laminate table, teal vinyl shells, chrome piping, condiment set.

Layout: benches run along Y and face each other across X; the open aisle end is the front
(-Y), the +Y end goes against the (window) wall. 7.9 wide so a booth sits in one 8-stud
window module. Seat height 1.6, table 2.8.
Sockets: Seat1/Seat2 (-X bench, facing +X), Seat3/Seat4 (+X bench, facing -X) at seat-top
height; Table (top centre); Napkin (Mr. Usual "booth napkin" clue spot by the dispenser).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
SEAT_Z, TABLE_Z = 1.6, 2.8
BY = 2.6            # bench half length (outer)
X_IN, X_OUT = 1.45, 3.95
KETCHUP = "#C8261E"


def bench(sx):
    """Returns dict of object lists for the bench on side sx (+1 = +X)."""
    def X(x):
        return sx * x
    out = {"shell": [], "vinyl": [], "trim": [], "base": []}
    sil = [(X_IN, 0.3), (X_OUT, 0.3), (X_OUT, 4.5), (3.32, 4.5), (3.12, 1.3), (X_IN, 1.3)]
    sil = C.fillet(sil, [0.0, 0.0, 0.12, 0.12, 0.05, 0.08], 2)
    pts = [(X(x), z) for x, z in sil]
    for sy in (-1, 1):
        a0, a1 = sorted((sy * (BY - 0.14), sy * BY))
        p = C.prism(pts, "y", a0, a1)
        out["shell"].append(p)
        # chrome piping following the end panel's front + top edge
        y = sy * (BY + 0.01)
        path = [(X(X_IN + 0.02), y, 0.35), (X(X_IN + 0.02), y, 1.28), (X(3.1), y, 1.3), (X(3.3), y, 4.52),
                (X(X_OUT - 0.02), y, 4.52), (X(X_OUT - 0.02), y, 0.35)]
        out["trim"].append(C.pipe(path, 0.05, sides=6, corner=0.1, corner_segs=1))
    out["shell"].append(ns.box((X_OUT - X_IN - 0.1, 2 * BY - 0.2, 0.95), loc=(X((X_IN + X_OUT) / 2 + 0.03), 0, 0.3 + 0.475),
                               bevel=0.05, segments=1))
    back = ns.box((0.5, 2 * BY - 0.2, 3.2), loc=(X(X_OUT - 0.27), 0, 1.25 + 1.6), bevel=0.06, segments=1)
    out["shell"].append(back)
    out["base"].append(ns.box((X_OUT - X_IN - 0.3, 2 * BY - 0.4, 0.3), loc=(X((X_IN + X_OUT) / 2 + 0.05), 0, 0.15),
                              bevel=0.03, segments=1))
    # seat cushion + 4 channel rolls on the back
    out["vinyl"].append(ns.box((3.32 - X_IN + 0.04, 2 * BY - 0.26, 0.4), loc=(X((X_IN + 3.32) / 2), 0, SEAT_Z - 0.2),
                               bevel=0.15, segments=2))
    n = 4
    w = (2 * BY - 0.3) / n
    for k in range(n):
        y = -BY + 0.15 + w * (k + 0.5)
        r = ns.box((0.42, w - 0.04, 2.55), loc=(X(3.2), y, SEAT_Z + 0.05 + 1.3), rot=(0, sx * 6, 0),
                   bevel=0.17, segments=2)
        out["vinyl"].append(r)
    # chrome cap along the top of the backrest
    out["trim"].append(C.pipe([(X(3.62), -BY + 0.12, 4.5), (X(3.62), BY - 0.12, 4.5)], 0.06, sides=8))
    return out


def build():
    for sx, nm in ((-1, "A"), (1, "B")):
        b = bench(sx)
        C.part(b["shell"], "Shell" + nm, C.VINYL_TEAL, recolor="booth_shell", can_collide=True, smooth_angle=40)
        C.part(b["vinyl"], "Vinyl" + nm, C.VINYL_RED, recolor="booth_vinyl", can_collide=True, smooth_angle=50)
        C.part(b["trim"], "Trim" + nm, C.CHROME, "Metal", smooth_angle=60)
        C.part(b["base"], "Base" + nm, C.BASE_DARK)

    # table: laminate top on a chrome band, single chrome pedestal with a round foot
    ty = 0.2
    top = C.prism(C.rrect(2.5, 4.4, 0.3, 3, 0, ty), "z", TABLE_Z - 0.12, TABLE_Z)
    ns.bevel(top, width=0.02, segments=1)
    C.part([top], "TableTop", C.LAMINATE, can_collide=True, smooth_angle=40)
    band = C.prism(C.rrect(2.58, 4.48, 0.33, 3, 0, ty), "z", TABLE_Z - 0.2, TABLE_Z - 0.01)
    post = ns.cyl(0.16, TABLE_Z - 0.3, loc=(0, ty, (TABLE_Z - 0.3) / 2 + 0.1), verts=12, bevel=0.0)
    collar = ns.cyl(0.32, 0.12, loc=(0, ty, TABLE_Z - 0.26), verts=14, bevel=0.03, segments=1)
    foot = ns.cyl(0.85, 0.12, loc=(0, ty, 0.06), verts=16, radius_top=0.7, bevel=0.0)
    C.part([band, post, collar, foot], "TableFrame", C.CHROME, "Metal", smooth_angle=50)

    # condiments by the wall end: ketchup, mustard, napkin dispenser
    cy = ty + 1.75
    bottle = [(0.13, 0.0), (0.14, 0.42), (0.05, 0.56), (0.05, 0.66), (0.0, 0.68)]
    k = ns.lathe(bottle, verts=10, loc=(-0.55, cy, TABLE_Z))
    ns.tag(k, "Ketchup", KETCHUP, smooth_angle=60)
    m = ns.lathe(bottle, verts=10, loc=(-0.2, cy + 0.05, TABLE_Z))
    ns.tag(m, "Mustard", C.MUSTARD, smooth_angle=60)
    disp = ns.box((0.62, 0.36, 0.44), loc=(0.35, cy, TABLE_Z + 0.22), bevel=0.06, segments=1)
    ns.tag(disp, "Dispenser", C.CHROME, "Metal", smooth_angle=40)
    nap = ns.box((0.46, 0.2, 0.14), loc=(0.35, cy, TABLE_Z + 0.48), bevel=0.02, segments=1)
    ns.tag(nap, "Napkins", C.PAPER)


def sockets():
    s = {}
    for i, (x, y, yaw) in enumerate(((-2.35, -1.2, 90), (-2.35, 1.2, 90), (2.35, -1.2, -90), (2.35, 1.2, -90))):
        s[f"Seat{i + 1}"] = ((x, y, SEAT_Z), float(yaw))
    s["Table"] = ((0, 0.2, TABLE_Z), 0.0)
    s["Napkin"] = ((0.35, 0.2 + 1.3, TABLE_Z), 0.0)
    return s


META = {"seat_height": SEAT_Z, "table_height": TABLE_Z, "wall_end": "+Y (back)", "aisle_end": "front (-Y)",
        "fits": "one 8-stud window module", "variants": {"Teal": {"booth_vinyl": C.VINYL_TEAL, "booth_shell": C.VINYL_RED}}}

if __name__ == "__main__":
    C.run(build, "Shop_Booth", meta=META, sockets=sockets())
