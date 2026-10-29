"""Kitchen_PrepStation — the stainless sandwich prep table (2 build slots).

7 wide x 3 deep, worktop at 3.0 (STYLE.md §5). Two recessed stainless trays (2.8 x 1.3)
sit side by side, each with a cream cutting board where the sandwich is built; an open
undershelf below. Front (where the cook stands) faces -Y.

Sockets: Slot1 (left, -X) / Slot2 (right, +X) = top centre of each tray's cutting board,
yaw 0 (sandwich along X). CookCamera = 2.2 above and 2.6 in front of the trays, yaw 180 so
it looks back at them (+Y); meta cook_camera_pitch gives the downward tilt. Prompt = above
the front edge. Slot lamps (roles slot1_lamp / slot2_lamp) let the client show slot state.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D, TOP = 7.0, 3.0, C.TOP
APRON = 0.4
TRAY_W, TRAY_D, TRAY_H = 2.8, 1.3, 0.16
TRAY_X = 1.65                 # tray centres at +-TRAY_X (Slot1 = -X = cook's left)
TRAY_Y = -0.38
RIM_Z = TOP + 0.02            # tray rim sits a hair proud of the worktop
FLOOR_Z = TOP - 0.10          # tray floor top
BOARD_T = 0.07


def build():
    # ---- worktop with two tray wells -------------------------------------------------
    slab = ns.box((W, D, APRON), loc=(0, 0, TOP - APRON / 2), bevel=0.0)
    for sx in (-1, 1):
        ns.boolean(slab, ns.box((TRAY_W + 0.06, TRAY_D + 0.06, 0.32), loc=(sx * TRAY_X, TRAY_Y, TOP), bevel=0.0))
    ns.bevel(slab, width=0.08, segments=2)
    splash = ns.box((W, 0.2, 0.6), loc=(0, D / 2 - 0.1, TOP + 0.27), bevel=0.08, segments=2)
    C.part([slab, splash], "Worktop", C.STAINLESS, "Metal", can_collide=True, smooth_angle=40)

    # ---- trays: shallow stainless pans dropped into the wells -------------------------
    trays = []
    for sx in (-1, 1):
        t = ns.box((TRAY_W, TRAY_D, TRAY_H), loc=(sx * TRAY_X, TRAY_Y, RIM_Z - TRAY_H / 2), bevel=0.0)
        ns.boolean(t, ns.box((TRAY_W - 0.16, TRAY_D - 0.16, 0.3), loc=(sx * TRAY_X, TRAY_Y, FLOOR_Z + 0.15), bevel=0.0))
        ns.bevel(t, width=0.035, segments=1)
        trays.append(t)
    C.part(trays, "Trays", C.STEEL, "Metal", smooth_angle=40)

    # ---- cutting boards inside the trays (where the sandwich is built) ---------------
    boards = []
    for sx in (-1, 1):
        b = C.extrude(C.rrect(TRAY_W - 0.34, TRAY_D - 0.32, 0.12, 2), BOARD_T, plane="XY",
                      bevel=0.025, segments=1, name="Board")
        b.location = (sx * TRAY_X, TRAY_Y, FLOOR_Z)
        boards.append(b)
    C.part(boards, "Boards", C.CREAM, "SmoothPlastic", smooth_angle=40)
    board_top = FLOOR_Z + BOARD_T

    # ---- base: legs, feet, undershelf ------------------------------------------------
    shelf_z = 0.6
    base = C.table_base(W, D, TOP, shelf_z=shelf_z, apron=APRON)
    # a short stack of spare sheet pans on the undershelf (same steel as the frame)
    s0 = shelf_z + 0.06
    pans = [ns.box((1.9, 1.3, 0.08), loc=(-1.7 + 0.03 * i, 0.1 - 0.04 * i, s0 + 0.04 + 0.09 * i), rot=(0, 0, 2 * i - 2),
                   bevel=0.03, segments=1) for i in range(3)]
    C.part(base["legs"] + [base["shelf"]] + pans, "Frame", C.STEEL, "Metal", can_collide=True, smooth_angle=40)
    C.part(base["feet"], "Feet", C.RUBBER, "SmoothPlastic")

    # red sanitizer bucket with a wire handle on the undershelf
    bucket = ns.lathe([(0.0, 0.0), (0.37, 0.0), (0.4, 0.04), (0.47, 0.7), (0.51, 0.74), (0.49, 0.78), (0.43, 0.76),
                       (0.4, 0.1), (0.0, 0.1)], verts=14, name="Bucket")
    bucket.location = (1.9, 0.15, s0)
    handle = C.ns.tube([(1.9 - 0.48, 0.15, s0 + 0.66), (1.9 - 0.34, 0.15, s0 + 1.08), (1.9, 0.15, s0 + 1.22),
                        (1.9 + 0.34, 0.15, s0 + 1.08), (1.9 + 0.48, 0.15, s0 + 0.66)],
                       [0.025] * 5, sides=4, resolution=2, name="Handle")
    C.part(bucket, "Bucket", C.BRAND, "SmoothPlastic", smooth_angle=50)
    C.part(handle, "BucketHandle", C.STEEL_DARK, "Metal", smooth_angle=60)

    # ---- brand stripe on the apron and slot lamps --------------------------------------
    stripe = ns.box((W - 0.5, 0.04, 0.12), loc=(0, -D / 2 - 0.012, TOP - APRON / 2), bevel=0.02, segments=1)
    C.part(stripe, "Stripe", C.BRAND, "SmoothPlastic")
    # slot lamps on the backsplash, centred behind each tray (visible from Cook View)
    for i, sx in enumerate((-1, 1), start=1):
        lamp = C.plate(0.5, 0.16, 0.06, 0.07, n=2, loc=(sx * TRAY_X, D / 2 - 0.22, TOP + 0.3), name="Lamp")
        C.part(lamp, f"Slot{i}Lamp", C.MUSTARD, "SmoothPlastic", recolor=f"slot{i}_lamp")

    # ---- sockets / meta ---------------------------------------------------------------
    cam_back, cam_up = 2.6, 2.2
    sockets = {
        "Slot1": ((-TRAY_X, TRAY_Y, board_top), 0),
        "Slot2": ((TRAY_X, TRAY_Y, board_top), 0),
        "CookCamera": ((0, TRAY_Y - cam_back, board_top + cam_up), 180),
        "Prompt": ((0, -D / 2 + 0.2, TOP + 0.6), 0),
    }
    meta = {
        "worktop_height": TOP,
        "slot_surface_height": round(board_top, 3),
        "tray_size": [TRAY_W, TRAY_D],
        "cook_camera_pitch": round(-math.degrees(math.atan2(cam_up, cam_back)), 2),
        "cook_camera_target": "midpoint of Slot1 and Slot2",
    }
    meta["footprint"] = [W, D]
    # pivot = bottom-centre of the 7 x 3 footprint (not of the bbox), so modules butt cleanly
    return {"export": {"sockets": sockets, "meta": meta, "pivot": (0, 0, 0)}}


if __name__ == "__main__":
    C.run(build, "Kitchen_PrepStation")
