"""Kitchen_WrapStation — 3-wide worktop with a big deli-paper roll and cutter bar.

Matches the prep station (same stainless top at 3.0, apron, backsplash and open base) so the
line reads as one run. A big paper roll with brand-red edge bands sits in two stainless
cheeks at the back; the paper feeds under a serrated cutter bar and lies flat on the
worktop as the wrap sheet (role wrap_sheet, so the client can hide/fold it). Spare rolls
and a stack of kraft bags on the undershelf. Front faces -Y.

Sockets: Wrap = top centre of the wrap sheet (sandwich bottom, yaw 0 = along X); Prompt.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D, TOP = 3.0, 3.0, C.TOP
APRON = 0.4
ROLL_R, ROLL_L = 0.46, 2.3
ROLL_Y, ROLL_Z = 0.78, TOP + 0.62
KRAFT = "#B39573"


def build():
    # ---- worktop + base (same family as the prep station) -----------------------------
    top = C.worktop_slab(W, D, TOP, apron=APRON, backsplash=0.55, splash_t=0.2)
    C.part(top, "Worktop", C.STAINLESS, "Metal", can_collide=True, smooth_angle=40)
    base = C.table_base(W, D, TOP, shelf_z=0.6, apron=APRON)
    C.part(base["legs"] + [base["shelf"]], "Frame", C.STEEL, "Metal", can_collide=True, smooth_angle=40)
    C.part(base["feet"], "Feet", C.RUBBER, "SmoothPlastic")
    stripe = ns.box((W - 0.5, 0.04, 0.12), loc=(0, -D / 2 - 0.012, TOP - APRON / 2), bevel=0.02, segments=1)

    # ---- dispenser cheeks + axle ------------------------------------------------------
    cheeks = []
    for sx in (-1, 1):
        c = C.extrude(C.rrect(0.95, 1.0, 0.3, 2), 0.12, plane="YZ", offset=-0.06, bevel=0.03, segments=1, name="Cheek")
        c.location = (sx * (ROLL_L / 2 + 0.12), ROLL_Y, TOP + 0.5)
        cheeks.append(c)
    axle = C.rod((-ROLL_L / 2 - 0.25, ROLL_Y, ROLL_Z), (ROLL_L / 2 + 0.25, ROLL_Y, ROLL_Z), 0.07, verts=8)
    caps = [ns.cyl(0.12, 0.08, loc=(sx * (ROLL_L / 2 + 0.24), ROLL_Y, ROLL_Z), rot=(0, 90, 0), verts=10, bevel=0.03, segments=1)
            for sx in (-1, 1)]
    # serrated cutter bar in front of the roll
    teeth = []
    n_teeth = 16
    for k in range(n_teeth + 1):
        x = -ROLL_L / 2 + ROLL_L * k / n_teeth
        teeth.append((x, 0.0))
        if k < n_teeth:
            teeth.append((x + ROLL_L / n_teeth / 2, -0.07))
    blade_outline = [(ROLL_L / 2, 0.12), (-ROLL_L / 2, 0.12)] + teeth
    blade = C.extrude(blade_outline, 0.04, plane="XZ", offset=-0.02, name="Blade")
    blade.location = (0, ROLL_Y - ROLL_R - 0.14, TOP + 0.16)
    blade.rotation_euler = (0.35, 0, 0)
    bar = C.rod((-ROLL_L / 2 - 0.12, ROLL_Y - ROLL_R - 0.12, TOP + 0.3), (ROLL_L / 2 + 0.12, ROLL_Y - ROLL_R - 0.12, TOP + 0.3), 0.07, verts=10)
    C.part(cheeks + caps, "Dispenser", C.STAINLESS, "Metal", smooth_angle=40)
    C.part([axle, blade, bar], "Cutter", C.STEEL_DARK, "Metal", smooth_angle=40)

    # ---- the roll: paper body, brand edge bands, cardboard core ------------------------
    roll = ns.cyl(ROLL_R, ROLL_L - 0.04, loc=(0, ROLL_Y, ROLL_Z), rot=(0, 90, 0), verts=16, bevel=0.04, segments=1)
    # paper tongue: from the bottom-front of the roll, down under the cutter, onto the worktop
    sheet_y0, sheet_y1 = ROLL_Y - ROLL_R - 0.14, -1.15
    tongue = ns.box((ROLL_L - 0.2, 0.36, 0.02), loc=(0, ROLL_Y - ROLL_R + 0.02, TOP + 0.13), rot=(-62, 0, 0), bevel=0.0)
    C.part([roll, tongue], "PaperRoll", C.PAPER, "SmoothPlastic", smooth_angle=40)
    bands = [ns.cyl(ROLL_R + 0.012, 0.14, loc=(sx * (ROLL_L / 2 - 0.22), ROLL_Y, ROLL_Z), rot=(0, 90, 0), verts=16, bevel=0.0)
             for sx in (-1, 1)]
    C.part(bands + [stripe], "Bands", C.BRAND, "SmoothPlastic", smooth_angle=40)
    core = ns.cyl(0.16, ROLL_L + 0.02, loc=(0, ROLL_Y, ROLL_Z), rot=(0, 90, 0), verts=12, bevel=0.0)
    C.part(core, "Core", KRAFT, "SmoothPlastic", smooth_angle=40)

    # ---- the wrap sheet lying on the worktop ------------------------------------------
    sheet = C.extrude(C.rrect(ROLL_L - 0.2, sheet_y0 - sheet_y1, 0.03, 1), 0.02, plane="XY", name="Sheet")
    sheet.location = (0, (sheet_y0 + sheet_y1) / 2, TOP + 0.002)
    C.part(sheet, "Sheet", C.PAPER, "SmoothPlastic", recolor="wrap_sheet", smooth_angle=None)

    # ---- undershelf: two spare rolls + a stack of kraft bags --------------------------
    s0 = 0.66
    spares = [ns.cyl(0.3, 1.1, loc=(-0.55, y, s0 + 0.3), rot=(0, 90, 0), verts=12, bevel=0.0) for y in (-0.35, 0.3)]
    C.part(spares, "SpareRolls", C.PAPER, "SmoothPlastic", smooth_angle=40)
    bags = [ns.box((0.9, 1.2, 0.07), loc=(0.75, 0.0, s0 + 0.035 + 0.075 * k), rot=(0, 0, 3 * k - 4), bevel=0.02, segments=1)
            for k in range(3)]
    C.part(bags, "Bags", KRAFT, "SmoothPlastic", smooth_angle=40)

    sheet_top = TOP + 0.022
    sockets = {
        "Wrap": ((0, (sheet_y0 + sheet_y1) / 2, sheet_top), 0),
        "Prompt": ((0, -D / 2 + 0.2, TOP + 0.6), 0),
    }
    meta = {"worktop_height": TOP, "wrap_surface_height": round(sheet_top, 3)}
    meta["footprint"] = [W, D]
    return {"export": {"sockets": sockets, "meta": meta, "pivot": (0, 0, 0)}}


if __name__ == "__main__":
    C.run(build, "Kitchen_WrapStation")
