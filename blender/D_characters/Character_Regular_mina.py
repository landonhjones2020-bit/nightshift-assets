"""Character_Regular_mina — Nurse Mina (Regular; the Copy may impersonate her).

Photo-board read: ceil-blue scrubs (short sleeves, V-neck, pocket + pen), high ponytail,
stethoscope round the neck, white clogs, a big white name badge on her left chest.
Tells (runtime roles): badge (flat white plate, axis-aligned, front = -Z: Studio puts
the "MINA" SurfaceGui text on its Front face; the Copy shows "MNIA"). Also eye, eyelid.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
TITLE = "Nurse Mina"
SKIN = "#B9774F"
SCRUBS = "#4F8FD6"
HAIR = "#2A1E19"
BADGE_C = (0.28, 2.86)        # badge centre (x, z)
BADGE_WH = (0.6, 0.34)


def build_regular(arm):
    look = {"skin": SKIN, "top": SCRUBS, "pants": "#4785CC", "shoes": "#F0EEE8", "sole": "#8FB4D9",
            "brow": HAIR, "generic": False, "sleeve": "short", "lid_drop": 0.05, "torso_hidden": True}
    C.build_body(arm, look)
    C.place_accessory(C.strip_roles(C.acc_top_scrubs(color=SCRUBS, skin=SKIN)), arm=arm, bone="Torso")
    C.place_accessory(C.strip_roles(C.acc_hair_ponytail(color=HAIR, tie="#2BB3B1", high=True)), arm=arm, bone="Head")
    C.place_accessory(C.acc_face_bags(color="#4A2E3A"), arm=arm, bone="Head")
    # name badge: axis-aligned plate on a darker backing card + reel clip
    bx, bz = BADGE_C
    w, h = BADGE_WH
    front = min(C.torso_pt(math.atan2(x, 0.5), C.gt(bz), 0.07).y for x in (bx - w / 2, bx, bx + w / 2))
    y = front - 0.045
    plate = ns.box((w, 0.03, h), loc=(bx, y - 0.012, bz), bevel=0.012, segments=1)
    C.part([plate], "Badge", "#F7F5EF", arm=arm, bone="Torso", role="badge", smooth=30)
    back = ns.box((w + 0.05, 0.025, h + 0.05), loc=(bx, y + 0.012, bz), bevel=0.015, segments=1)
    stripe = ns.box((w + 0.05, 0.02, 0.06), loc=(bx, y + 0.008, bz + h / 2 + 0.0), bevel=0.0)
    C.part([back, stripe], "BadgeCard", "#24508F", arm=arm, bone="Torso", smooth=30)
    reel = ns.cyl(0.05, 0.03, loc=(bx, y + 0.02, bz + h / 2 + 0.12), rot=(90, 0, 0), verts=12, bevel=0.0)
    cord = ns.cyl(0.008, 0.1, loc=(bx, y + 0.01, bz + h / 2 + 0.05), verts=6, bevel=0.0)
    # stethoscope: tube round the back of the neck, down the front over the scrubs, short ends
    D = C.D2R
    P = C.Vector
    front = [C.torso_pt(a * D, C.gt(z), 0.1) for a, z in ((40, 3.2), (36, 3.38), (40, 3.5))]
    path = front + [P((0.36, -0.05, 3.62)), P((0.2, 0.25, 3.66)), P((-0.2, 0.25, 3.66)), P((-0.36, -0.05, 3.62))]
    path += [C.torso_pt(-a * D, C.gt(z), 0.1) for a, z in ((40, 3.5), (36, 3.38), (40, 3.2))]
    tubing = C.tube(path, [0.034] * len(path), sides=6, res=2)
    cp = C.torso_pt(42 * D, C.gt(3.13), 0.14)
    chest = ns.cyl(0.085, 0.04, loc=tuple(cp), rot=(78, 0, 0), verts=14, bevel=0.012)
    tp = C.torso_pt(-42 * D, C.gt(3.14), 0.13)
    tips = [ns.sphere(0.034, loc=(tp.x + dx, tp.y, tp.z), segs=8, rings=4) for dx in (-0.05, 0.05)]
    C.part([tubing], "Stethoscope", "#2B2D31", arm=arm, bone="Torso", smooth=60)
    C.part([chest, reel, cord] + tips, "Steel", C.CHROME, "Metal", arm=arm, bone="Torso", smooth=40)


META = {"regular": "mina", "tells": {"badge": "Studio adds the text MINA on the Front face; the Copy shows MNIA"},
        "badge": {"text": "MINA", "face": "Front", "sizeStuds": [0.5, 0.29]}, "favorite": "M2"}

if __name__ == "__main__":
    C.run_regular("Character_Regular_mina", build_regular, META)
