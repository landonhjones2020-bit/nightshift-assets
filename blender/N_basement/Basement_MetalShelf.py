"""Basement_MetalShelf — slotted-angle steel storage shelving, loaded with old stock.

Four grey angle-iron uprights with slot holes, four steel decks with folded lips, X-braced
sides and back (blender/N_basement/_common.shelf_frame, shared with the sparse shelf).
The decks carry dusty cartons (two STACKHOUSE-branded: faded red-orange band, mustard
stripe, cream wordmark), rows of tin cans, big #10 cans, preserve jars with rusty lids and a
pile of flattened boxes; pale dust lies on several box tops. Back (+Y) goes against the
wall. Steel frame collides; the stock does not. Front faces -Y, pivot = bottom-centre.
6 x 8 x 2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
Z0, Z1, Z2, Z3 = C.SHELF_TOPS
LABEL_COLS = {"LabelRed": C.BRAND, "LabelGreen": "#5E6E45", "LabelMustard": C.MUSTARD, "LabelCream": C.CREAM}
JAR_COLS = ("#9A6A34", "#6E7A3C", "#8A3A2E", "#9A6A34")


def build():
    fr = C.shelf_frame()
    C.part(fr["steel"], "Steel", C.STEEL, "Metal", can_collide=True, smooth_angle=35)
    C.part(fr["slots"], "Slots", C.DARK_VOID, smooth_angle=None)
    C.part(fr["feet"], "Feet", C.CONCRETE_DARK, "Metal", smooth_angle=35)

    boxes = {C.CARDBOARD: [], C.CARDBOARD_DARK: [], C.CARDBOARD_LIGHT: [], C.CREAM: []}
    tape, dust, band, stripe, word = [], [], [], [], []
    metal, labels, jars, lids, jar_lbl = [], {k: [] for k in LABEL_COLS}, [], [], []

    def carton(col, w, d, h, x, y, z, yaw=0.0, tape_on=False, dusty=False, brand=None):
        assert not (tape_on and dusty), "tape and dust share the top plane"
        c = C.carton(w, d, h, loc=(x, y, z), yaw=yaw, tape=tape_on, bevel=0.03)
        boxes[col] += c["body"]
        tape.extend(c["tape"])
        if dusty:
            dust.append(C.dust_cap(w - 0.1, d - 0.1, z + h, loc=(x, y), yaw=yaw))
        if brand:
            # printed panel on the front face, built in the box's local frame (front y = -d / 2)
            fy = -d / 2
            lb = [ns.box((w * 0.84, 0.02, h * 0.3), loc=(0, fy - 0.006, h * 0.6), bevel=0.0)]
            ls = [ns.box((w * 0.84, 0.02, 0.06), loc=(0, fy - 0.006, h * 0.6 - h * 0.15 - 0.07), bevel=0.0)]
            C.place(lb + ls, loc=(x, y, z), yaw=yaw)
            band.extend(lb)
            stripe.extend(ls)
            if brand == "word":
                t = C.stencil("STACKHOUSE", h * 0.15, (0, fy - 0.016, h * 0.6), width=w * 0.72)
                C.place([t], loc=(x, y, z), yaw=yaw)
                word.append(t)

    def tin(x, y, z, key, r=0.17, h=0.42, verts=6):
        m, lab = C.can(x, y, z, r=r, h=h, verts=verts)
        metal.append(m)
        labels[key].append(lab)

    def tin_stack(x, y, z, keys, r=0.17, h=0.42):
        # one metal core for the whole stack, a label sleeve per can
        metal.append(ns.cyl(r * 0.94, h * len(keys), loc=(x, y, z + h * len(keys) / 2), verts=6, bevel=0.0))
        for k, key in enumerate(keys):
            labels[key].append(ns.cyl(r, h * 0.7, loc=(x, y, z + h * (k + 0.5)), verts=6, bevel=0.0))

    def preserve(x, y, z, k):
        b, lid, lab = C.jar(x, y, z, r=0.19, h=0.52, verts=6)
        jars.append((b, JAR_COLS[k % len(JAR_COLS)]))
        lids.append(lid)
        jar_lbl.append(lab)

    # ---- bottom deck: big branded carton, a taped carton, three #10 cans, two jars ----
    carton(C.CREAM, 1.7, 1.5, 1.3, -1.95, 0.05, Z0, yaw=-3, dusty=True, brand="word")
    carton(C.CARDBOARD_DARK, 1.3, 1.4, 1.05, -0.3, 0.12, Z0, yaw=4, tape_on=True)
    tin(0.78, -0.42, Z0, "LabelRed", r=0.27, h=0.64, verts=7)
    tin(1.36, -0.4, Z0, "LabelMustard", r=0.27, h=0.64, verts=7)
    tin(1.08, 0.25, Z0, "LabelRed", r=0.27, h=0.64, verts=7)
    preserve(2.1, -0.38, Z0, 0)
    preserve(2.5, -0.1, Z0, 1)

    # ---- second deck: stacked tins, a closed carton, preserve jars ----
    for i, x in enumerate((-2.45, -2.07, -1.69)):
        tin_stack(x, -0.5, Z1, (("LabelGreen", "LabelCream"), ("LabelGreen", "LabelGreen"), ("LabelCream", "LabelGreen"))[i])
    carton(C.CARDBOARD, 1.45, 1.5, 1.15, -0.45, 0.1, Z1, yaw=-5, dusty=True)
    preserve(0.85, -0.42, Z1, 2)
    preserve(1.27, -0.36, Z1, 3)
    carton(C.CARDBOARD_LIGHT, 1.2, 1.0, 0.85, 1.95, 0.25, Z1, yaw=3)

    # ---- third deck: two branded cartons, two tins, a pile of flattened boxes ----
    carton(C.CREAM, 1.5, 1.4, 1.1, -1.75, 0.05, Z2, yaw=2, brand="band")
    carton(C.CARDBOARD_DARK, 1.1, 1.2, 0.8, -0.35, 0.15, Z2, yaw=-6, dusty=True)
    tin(0.62, -0.45, Z2, "LabelRed")
    tin(0.98, -0.3, Z2, "LabelMustard")
    for k, (yaw, dx) in enumerate(((3, 0.0), (-4, 0.06), (6, -0.04))):
        boxes[C.CARDBOARD].append(ns.box((1.45, 1.4, 0.07), loc=(1.95 + dx, 0.05, Z2 + 0.035 + k * 0.07),
                                         rot=(0, 0, yaw), bevel=0.0))

    # ---- top deck (items stay under 8): flat cartons, two tins ----
    carton(C.CARDBOARD, 1.65, 1.5, 0.9, -1.6, 0.05, Z3, yaw=-2, dusty=True)
    carton(C.CARDBOARD_LIGHT, 1.25, 1.3, 0.62, 0.25, 0.1, Z3, yaw=5, tape_on=True)
    tin(1.75, -0.3, Z3, "LabelGreen")

    names = {C.CARDBOARD: "Boxes", C.CARDBOARD_DARK: "BoxesDark", C.CARDBOARD_LIGHT: "BoxesLight",
             C.CREAM: "BoxesBranded"}
    for col, objs in boxes.items():
        if objs:
            C.part(objs, names[col], col, smooth_angle=30)
    C.part(tape, "Tape", C.TAPE, smooth_angle=30)
    C.part(dust, "Dust", C.DUST, smooth_angle=None)
    C.part(band, "BrandBand", C.BRAND, smooth_angle=None)
    C.part(stripe, "BrandStripe", C.MUSTARD, smooth_angle=None)
    C.part(word, "BrandWord", C.CREAM, smooth_angle=None)
    C.part(metal, "TinMetal", C.STEEL, "Metal", smooth_angle=65)
    for k, objs in labels.items():
        if objs:
            C.part(objs, k, LABEL_COLS[k], smooth_angle=65)
    by_col = {}
    for b, col in jars:
        by_col.setdefault(col, []).append(b)
    for i, (col, objs) in enumerate(by_col.items()):
        C.part(objs, f"Jars{i}", col, smooth_angle=60)
    C.part(lids, "JarLids", C.RUST, "Metal", smooth_angle=60)
    C.part(jar_lbl, "JarLabels", C.CREAM, smooth_angle=65)


META = {"size": [C.SHELF_W, C.SHELF_H, C.SHELF_D], "back": "+Y against the wall",
        "shelf_tops": list(C.SHELF_TOPS), "collide": "steel frame only"}

if __name__ == "__main__":
    C.run(build, "Basement_MetalShelf", budget=2000, meta=META)
