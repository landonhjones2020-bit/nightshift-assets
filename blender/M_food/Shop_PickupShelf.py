"""Shop_PickupShelf — stainless heated pass / pickup shelf that sits ON a counter (M_food batch,
group "Shop").

7 wide x 1.2 deep: a stainless deck (top at 1.0) with a rolled front edge and a low back upstand,
carried by two square-tube end frames on rubber feet; two rear posts carry a stainless heat-lamp
bar (top at 2.6) whose four glowing red-orange elements (part Lamps, role "lamp", Neon) hang one
over each pickup slot. Four cream slot plates lie on the deck, each with a blank mustard number tab
hanging from the deck's front edge below it (parts Tab1..Tab4, roles slot_tab1..4, Front face) so
the game can draw the slot numbers and tint a ready slot; no baked numbers.
PIVOT = bottom-centre (the feet stand on the counter top). Front (customer side) faces -Y.
No collision.
Sockets Plate1..Plate4 = plate top centres (yaw 0: a sandwich lies along X), Plate1 at Blender -X =
Roblox +X (the sauce-rail order). Tag1..Tag4 = number tab centres just in front of them, facing -Y.
Lamp1..Lamp4 = just under each heat element (SpotLight facing down).
Run:  bpyenv/bin/python blender/M_food/Shop_PickupShelf.py   (NS_EXPORT=1 export)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
S = C.shop()
K = C.kitchen()
STAINLESS, RUBBER, PLATE, MUSTARD, HEAT = "#B9C0C6", "#2B2D31", "#EFE6D2", "#F2B33D", "#FF6A2A"
W, D = 7.0, 1.2
DECK_TOP, DECK_T = 1.0, 0.12
LAMP_TOP, LAMP_T = 2.6, 0.2
LAMP_Y, LAMP_D = 0.08, 0.56        # lamp bar centre (y) and depth
POST_X, POST_Y, TUBE = 3.28, 0.36, 0.18
XS = [-2.4, -0.8, 0.8, 2.4]        # slot centres (Plate1 at -X)
PLATE_Y = -0.06
PLATE_W, PLATE_D, PLATE_T = 1.36, 0.8, 0.03
TAB_W, TAB_H = 0.4, 0.22


def build():
    steel = []
    # deck: slab, rolled front edge, low back upstand
    steel.append(ns.box((W, D, DECK_T), loc=(0, 0, DECK_TOP - DECK_T / 2), bevel=0.035, segments=2))
    steel.append(K.rod((-W / 2 + 0.04, -D / 2 + 0.01, DECK_TOP - 0.045), (W / 2 - 0.04, -D / 2 + 0.01, DECK_TOP - 0.045),
                       0.065, verts=8))
    steel.append(ns.box((W, 0.06, 0.1), loc=(0, D / 2 - 0.03, DECK_TOP + 0.04), bevel=0.025, segments=1))
    # end frames: front + back legs, a foot rail and a top rail under the deck (square tube)
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.2)
        for sy in (-1, 1):
            steel.append(ns.box((TUBE, TUBE, DECK_TOP - DECK_T - 0.06), loc=(x, sy * (D / 2 - 0.16),
                                (DECK_TOP - DECK_T + 0.06) / 2), bevel=0.03, segments=1))
        steel.append(ns.box((TUBE, D - 0.32, 0.1), loc=(x, 0, 0.14), bevel=0.025, segments=1))
    # rear posts and the lamp bar housing (with a lip round its underside)
    for sx in (-1, 1):
        steel.append(ns.box((TUBE, TUBE, LAMP_TOP - LAMP_T - DECK_TOP + 0.02),
                            loc=(sx * POST_X, POST_Y, (LAMP_TOP - LAMP_T + DECK_TOP) / 2 + 0.01), bevel=0.03, segments=1))
    steel.append(ns.box((W, LAMP_D, LAMP_T), loc=(0, LAMP_Y, LAMP_TOP - LAMP_T / 2), bevel=0.045, segments=2))
    lip = S.ring_slab(S.rrect(W - 0.02, LAMP_D - 0.02, 0.06, segs=1), S.rrect(W - 0.2, LAMP_D - 0.16, 0.04, segs=1), "z",
                      LAMP_TOP - LAMP_T - 0.05, LAMP_TOP - LAMP_T + 0.01)
    lip.location.y = LAMP_Y
    steel.append(lip)
    C.kitchen().part(steel, "Frame", STAINLESS, "Metal", smooth_angle=40)

    feet = [ns.cyl(0.11, 0.05, loc=(sx * (W / 2 - 0.2), sy * (D / 2 - 0.16), 0.025), verts=8, bevel=0.0,
                   radius_top=0.09) for sx in (-1, 1) for sy in (-1, 1)]
    K.part(feet, "Feet", RUBBER, "SmoothPlastic", smooth_angle=50)

    # four heat elements under the lamp bar, one over each slot
    lamps = []
    lamp_z = LAMP_TOP - LAMP_T - 0.07          # element centre: hangs just below the housing lip
    for x in XS:
        el = S.prism(S.rrect(1.32, 0.28, 0.12, segs=2), "z", lamp_z - 0.035, lamp_z + 0.07)
        el.location = (x, LAMP_Y - 0.02, 0)
        ns.bevel(el, width=0.015, segments=1, angle=50)
        lamps.append(el)
    K.part(lamps, "Lamps", HEAT, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=50)

    # slot plates on the deck and their number tabs on the front edge
    plates = []
    for x in XS:
        p = S.prism(S.rrect(PLATE_W, PLATE_D, 0.12, segs=2), "z", DECK_TOP - 0.005, DECK_TOP + PLATE_T)
        p.location = (x, PLATE_Y, 0)
        ns.bevel(p, width=0.01, segments=1, angle=50)
        plates.append(p)
    K.part(plates, "Plates", PLATE, "SmoothPlastic", smooth_angle=40)
    tab_y = -D / 2 - 0.04
    tab_z = DECK_TOP - DECK_T - TAB_H / 2 + 0.06
    for i, x in enumerate(XS, start=1):
        t = S.prism(S.rrect(TAB_W, TAB_H, 0.05, segs=2), "y", tab_y - 0.03, tab_y + 0.04)
        t.location = (x, 0, tab_z)
        K.part([t], f"Tab{i}", MUSTARD, "SmoothPlastic", recolor=f"slot_tab{i}", smooth_angle=40)

    sockets = {}
    for i, x in enumerate(XS, start=1):
        sockets[f"Plate{i}"] = ((x, PLATE_Y, DECK_TOP + PLATE_T), 0.0)
        sockets[f"Tag{i}"] = ((x, tab_y - 0.03 - 0.02, tab_z), 0.0)
        sockets[f"Lamp{i}"] = ((x, LAMP_Y - 0.02, lamp_z - 0.07), 0.0)
    meta = {"mount": "counter top", "pivot": "bottom-centre (feet on the counter top)",
            "deck_top": DECK_TOP, "slot_count": len(XS), "slot_pitch": round(XS[1] - XS[0], 3),
            "plate_size": [PLATE_W, PLATE_D], "tag_size": [TAB_W, TAB_H],
            "surfaces": [C.screen_meta(f"Tab{i}", TAB_W, TAB_H) for i in range(1, len(XS) + 1)],
            "roles": {"lamp": "Lamps", "slot_tab": "Tab1..Tab4"},
            "light_hint": {"type": "SpotLight", "face": "Bottom", "color": "#FF9A5A", "range": 4, "angle": 70,
                           "sockets": [f"Lamp{i}" for i in range(1, len(XS) + 1)]}}
    return {"export": {"sockets": sockets, "meta": meta}}


def preview(asset, out_dir, res, samples):
    """Front 3/4 from about a player's eye line over the counter (shows the lit elements), then the
    kitchen side from above."""
    return C.angles_preview(asset, out_dir, res, samples, angles=((-26.0, 4.0), (150.0, 24.0)), floor=True)


if __name__ == "__main__":
    C.run(build, "Shop_PickupShelf", meta_=None, pivot=(0.0, 0.0, 0.0), group="Shop", preview=preview)
