"""Kitchen_BinRail — refrigerated ingredient rail (the shared row of 6 bins on the line).

A floor-standing stainless cold cabinet (three doors, vent grille, temperature readout)
whose top holds six insert pans (1.1 x 0.9 x 0.45 deep) in one long well, rims at 3.0
(STYLE.md §5), under an overhead glass sneeze-guard. 7.2 long. Front faces -Y.

Sockets Bin1..Bin6 = pan inner-floor centres, Bin1 at -X (cook's left), yaw 0.
The cream label tags under each pan are one part (role bin_labels) for a SurfaceGui.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L, D, TOP = 7.2, 2.0, C.TOP
PAN_W, PAN_D, PAN_H = 1.1, 0.9, 0.45
PAN_Y = 0.1                       # pan row centre (front ledge in front of it)
DECK_T = 0.03                     # pan lip thickness resting on the deck
BODY_TOP = TOP - DECK_T           # top of the stainless deck
PAN_XS = [(-2.5 + i) * PAN_W for i in range(6)]


def build():
    # ---- cabinet body + deck, one long well cut for the pans --------------------------
    body = ns.box((L, D, BODY_TOP - 0.3), loc=(0, 0, 0.3 + (BODY_TOP - 0.3) / 2), bevel=0.0)
    ns.boolean(body, ns.box((6 * PAN_W - 0.1, PAN_D - 0.1, 1.0), loc=(0, PAN_Y, BODY_TOP), bevel=0.0))
    ns.bevel(body, width=0.08, segments=2)
    C.part(body, "Body", C.STAINLESS, "Metal", can_collide=True, smooth_angle=40)

    # ---- the six insert pans ----------------------------------------------------------
    pans = [C.open_pan(PAN_W - 0.01, PAN_D, PAN_H, lip=0.07, lip_t=DECK_T + 0.01, taper=0.05, r=0.08, n=2,
                       loc=(x, PAN_Y, TOP)) for x in PAN_XS]
    C.part(pans, "Pans", C.STEEL, "Metal", smooth_angle=40)

    # ---- doors: three raised panels with chunky bar handles ---------------------------
    door_w, door_h, door_z = 2.25, 1.95, 0.42
    doors, handles, gaskets = [], [], []
    for i, x in enumerate((-2.38, 0.0, 2.38)):
        doors.append(ns.box((door_w, 0.1, door_h), loc=(x, -D / 2 - 0.03, door_z + door_h / 2), bevel=0.07, segments=1))
        gaskets.append(ns.box((door_w + 0.06, 0.05, door_h + 0.06), loc=(x, -D / 2 + 0.0, door_z + door_h / 2),
                              bevel=0.0))
        hx = x + (door_w / 2 - 0.25) * (1 if i != 2 else -1)
        handles.append(C.rod((hx, -D / 2 - 0.2, door_z + 0.42), (hx, -D / 2 - 0.2, door_z + door_h - 0.42), 0.065, verts=8))
        for z in (door_z + 0.5, door_z + door_h - 0.5):
            handles.append(C.rod((hx, -D / 2 - 0.06, z), (hx, -D / 2 - 0.22, z), 0.04, verts=6))
    C.part(doors, "Doors", C.STAINLESS, "Metal", smooth_angle=40)
    C.part(handles, "Handles", C.STEEL_DARK, "Metal", smooth_angle=50)
    C.part(gaskets, "Gaskets", C.RUBBER, "SmoothPlastic", smooth_angle=40)

    # ---- kick plate with a louvred compressor vent and feet ---------------------------
    kick = [ns.box((L - 0.3, 0.12, 0.3), loc=(0, -D / 2 + 0.08, 0.27), bevel=0.03, segments=1)]
    louvres = [ns.box((1.6, 0.06, 0.035), loc=(-2.3, -D / 2 + 0.0, 0.17 + 0.065 * k), rot=(-25, 0, 0), bevel=0.0)
               for k in range(4)]
    feet = [ns.cyl(0.13, 0.14, loc=(sx * (L / 2 - 0.3), sy * (D / 2 - 0.3), 0.07), verts=8, bevel=0.0, radius_top=0.1)
            for sx in (-1, 1) for sy in (-1, 1)]
    vent_bg = ns.box((1.7, 0.04, 0.3), loc=(-2.3, -D / 2 + 0.03, 0.27), bevel=0.01, segments=1)
    C.part(kick + feet, "Kick", C.STEEL_DARK, "Metal", smooth_angle=40)
    C.part([vent_bg] + louvres, "Vent", C.GUNMETAL, "SmoothPlastic", smooth_angle=None)

    # ---- front ledge details: brand stripe, bin label tags, temperature readout -------
    stripe = ns.box((L - 0.5, 0.04, 0.12), loc=(0, -D / 2 - 0.012, BODY_TOP - 0.24), bevel=0.02, segments=1)
    C.part(stripe, "Stripe", C.BRAND, "SmoothPlastic")
    tags = [ns.box((0.78, 0.2, 0.025), loc=(x, PAN_Y - PAN_D / 2 - 0.2, BODY_TOP + 0.012), bevel=0.0) for x in PAN_XS]
    C.part(tags, "Labels", C.CREAM, "SmoothPlastic", recolor="bin_labels")
    disp_box = ns.box((0.62, 0.06, 0.3), loc=(2.9, -D / 2 - 0.03, BODY_TOP - 0.24), bevel=0.03, segments=1)
    C.part(disp_box, "DisplayFrame", C.RUBBER, "SmoothPlastic")
    disp = ns.box((0.46, 0.03, 0.17), loc=(2.9, -D / 2 - 0.06, BODY_TOP - 0.24), bevel=0.0)
    C.part(disp, "Display", C.ICY, "Neon", recolor="temp_display")

    # ---- sneeze-guard: three posts from the back edge, sloped glass canopy -----------
    gy0, gz0 = D / 2 - 0.2, TOP + 1.65          # back top corner of the glass
    gy1, gz1 = PAN_Y - 0.35, TOP + 1.35         # front low edge of the glass
    posts = []
    for x in (-L / 2 + 0.3, 0.0, L / 2 - 0.3):
        posts.append(C.rod((x, gy0, BODY_TOP - 0.02), (x, gy0, gz0 + 0.04), 0.07, verts=8))
        posts.append(ns.cyl(0.14, 0.07, loc=(x, gy0, BODY_TOP + 0.035), verts=8, bevel=0.0, radius_top=0.1))
    # tube frame around the glass
    frame_pts = [(-L / 2 + 0.3, gy0, gz0), (-L / 2 + 0.3, gy1, gz1), (L / 2 - 0.3, gy1, gz1), (L / 2 - 0.3, gy0, gz0)]
    for a, b in zip(frame_pts, frame_pts[1:] + frame_pts[:1]):
        posts.append(C.rod(a, b, 0.05, verts=6))
    C.part(posts, "GuardFrame", C.STAINLESS, "Metal", smooth_angle=50)
    import math
    from mathutils import Vector
    mid = (Vector(frame_pts[0]) + Vector(frame_pts[2])) / 2
    slope = math.degrees(math.atan2(gz0 - gz1, gy0 - gy1))
    glass = ns.box((L - 0.65, ((gy0 - gy1) ** 2 + (gz0 - gz1) ** 2) ** 0.5 - 0.06, 0.04), loc=mid,
                   rot=(slope, 0, 0), bevel=0.0)
    C.part(glass, "Glass", "#CFEAF5", "Glass", transparency=0.55, cast_shadow=False)

    sockets = {f"Bin{i + 1}": ((x, PAN_Y, TOP - PAN_H), 0) for i, x in enumerate(PAN_XS)}
    meta = {
        "rail_top": TOP,
        "pan_size": [PAN_W, PAN_D, PAN_H],
        "surface_label": {"part": "Labels", "face": "Top", "slots": 6},
    }
    meta["footprint"] = [L, D]
    return {"export": {"sockets": sockets, "meta": meta, "pivot": (0, 0, 0)}}


if __name__ == "__main__":
    C.run(build, "Kitchen_BinRail")
