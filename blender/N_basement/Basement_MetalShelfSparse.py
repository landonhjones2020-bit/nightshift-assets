"""Basement_MetalShelfSparse — the same slotted-angle steel shelving, almost cleared out.

Frame from blender/N_basement/_common.shelf_frame (identical to Basement_MetalShelf).
Left on it: an open carton with splayed flaps and a tin lying on its side on the bottom
deck, a jar and two tins on the second, one dusty carton pushed to the back of the third,
a flattened box on the top deck, and a cobweb (pale, Transparency 0.3, no shadow) slung
across the top-left corner of the third bay. Back (+Y) against the wall. Steel frame
collides; the rest does not. Front faces -Y, pivot = bottom-centre. 6 x 8 x 2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
Z0, Z1, Z2, Z3 = C.SHELF_TOPS
HX, HY = C.SHELF_W / 2, C.SHELF_D / 2


def build():
    fr = C.shelf_frame()
    C.part(fr["steel"], "Steel", C.STEEL, "Metal", can_collide=True, smooth_angle=35)
    C.part(fr["slots"], "Slots", C.DARK_VOID, smooth_angle=None)
    C.part(fr["feet"], "Feet", C.CONCRETE_DARK, "Metal", smooth_angle=35)

    boxes, dark_boxes, inside, dust = [], [], [], []
    metal, lab_red, lab_green, jar_lbl = [], [], [], []

    # bottom deck: open carton (flaps splayed) + a tin lying on its side
    c = C.carton(1.35, 1.15, 0.9, loc=(-1.7, -0.02, Z0), yaw=6, open_top=True, flap_angle=40)   # flaps stay inside the frame
    boxes += c["body"] + c["flaps"]
    inside += c["inside"]
    m = ns.cyl(0.25, 0.6, loc=(1.15, -0.25, Z0 + 0.25), rot=(0, 90, 18), verts=7, bevel=0.0)
    lb = ns.cyl(0.265, 0.42, loc=(1.15, -0.25, Z0 + 0.25), rot=(0, 90, 18), verts=7, bevel=0.0)
    metal.append(m)
    lab_red.append(lb)

    # second deck: a jar at the left, two tins at the right
    body, lid, lab = C.jar(-2.25, -0.35, Z1, r=0.19, h=0.52, verts=6)
    for x, col in ((1.95, lab_green), (2.35, lab_red)):
        mm, ll = C.can(x, -0.4, Z1, verts=6)
        metal.append(mm)
        col.append(ll)

    # third deck: one dusty carton pushed back
    d = C.carton(1.3, 1.1, 0.9, loc=(0.55, 0.35, Z2), yaw=-4, tape=False)
    dark_boxes += d["body"]
    dust.append(C.dust_cap(1.2, 1.0, Z2 + 0.9, loc=(0.55, 0.35), yaw=-4))

    # top deck: a flattened box lying askew
    boxes.append(ns.box((1.5, 1.3, 0.07), loc=(-0.9, 0.0, Z3 + 0.035), rot=(0, 0, 7), bevel=0.0))

    C.part(boxes, "Boxes", C.CARDBOARD, smooth_angle=30)
    C.part(dark_boxes, "BoxesDark", C.CARDBOARD_DARK, smooth_angle=30)
    C.part(inside, "Inside", "#33271C", "Fabric", smooth_angle=None)
    C.part(dust, "Dust", C.DUST, smooth_angle=None)
    C.part(metal, "TinMetal", C.STEEL, "Metal", smooth_angle=65)
    C.part(lab_red, "LabelRed", C.BRAND, smooth_angle=65)
    C.part(lab_green, "LabelGreen", "#5E6E45", smooth_angle=65)
    C.part([body], "Jar", "#6E7A3C", smooth_angle=60)
    C.part([lid], "JarLid", C.RUST, "Metal", smooth_angle=60)
    C.part([lab], "JarLabel", C.CREAM, smooth_angle=65)

    # cobweb across the top-left corner of the third bay, in front of the lip, anchored where the
    # left upright's front flange meets the underside of the top deck's lip
    ax = -HX + C.UP_A + 0.005
    web = C.web_fan((ax, -HY + 0.015, Z3 - 0.2), (1, 0, -0.04), (0.02, 0, -1), 1.35, spokes=6, rings=4,
                    bulge=(0.0, -0.06, -0.08), sag=0.16, r_strand=0.014, seed=4, wisps=2)
    C.part(web, "Cobweb", C.WEB, transparency=0.3, cast_shadow=False, smooth_angle=70)


META = {"size": [C.SHELF_W, C.SHELF_H, C.SHELF_D], "back": "+Y against the wall",
        "shelf_tops": list(C.SHELF_TOPS), "collide": "steel frame only",
        "cobweb": "part Cobweb, Transparency 0.3, no shadow"}

if __name__ == "__main__":
    C.run(build, "Basement_MetalShelfSparse", budget=2000, meta=META)
