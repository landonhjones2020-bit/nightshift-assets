"""Character_Regular_jo — Skater Jo (Regular; the Copy may impersonate her).

Photo-board read: purple skate helmet with a big yellow LIGHTNING sticker on the front-left,
dark fringe peeking out, green hoodie (hood down, kangaroo pocket, drawstrings), dark cargo
pants, black-and-white skate shoes.
Tells (runtime roles): tell_sticker (hide = sticker missing). Also eye, eyelid.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
TITLE = "Skater Jo"
SKIN = "#8A5A3C"
HOODIE = "#3E9B4F"
HELMET = "#6B4BB8"
BOLT = "#FFD23F"
H_IN, H_T = 0.1, 0.09      # helmet inner offset over the hair, shell thickness


def helmet_band(phi):
    return C._band_psi(phi, 56, 92, 104)


def build_regular(arm):
    D = C.D2R
    look = {"skin": SKIN, "top": HOODIE, "pants": "#4A4F57", "shoes": "#22252B", "sole": "#F0EEE8",
            "brow": "#211B18", "generic": False, "lid_drop": 0.03, "mouth_curve": 0.026,
            "torso_hidden": True}
    C.build_body(arm, look)
    C.place_accessory(C.strip_roles(C.acc_top_hoodie(color=HOODIE)), arm=arm, bone="Torso")
    # fringe under the helmet
    edge = lambda phi: C.hairline(phi, front=58, side=86, back=110) + 6 * D * C.tri_wave(phi / (14 * D))
    fringe = C.hair_cap(edge, lambda phi, v: 0.06, nu=28, vs=[0.2, 0.45, 0.7, 0.88, 1.0], name="Hair")
    C.part([fringe], "Hair", "#211B18", arm=arm, bone="Head", smooth=55)

    def fo(u, v):
        phi = 2 * math.pi * u
        return C.head_pt(phi, v * helmet_band(phi), H_IN + H_T)

    def fi(u, v):
        phi = 2 * math.pi * u
        return C.head_pt(phi, v * helmet_band(phi), H_IN)
    shell = C.patch(fo, fi, 36, 7, closed_u=True, pole=True, inner="lip", centre=C.HEAD_C,
                    vs=[0.15, 0.32, 0.5, 0.66, 0.8, 0.92, 1.0], name="Helmet")
    C.part([shell], "Helmet", HELMET, arm=arm, bone="Head", smooth=55)

    def ro(u, v):
        phi = 2 * math.pi * u
        return C.head_pt(phi, helmet_band(phi) - 0.08 + 0.095 * v, H_IN + H_T + 0.022)

    def ri(u, v):
        phi = 2 * math.pi * u
        return C.head_pt(phi, helmet_band(phi) - 0.08 + 0.095 * v, H_IN - 0.03)
    rim = C.patch(ro, ri, 30, 2, closed_u=True, pole=False, inner="full", name="Rim")
    vents = [C.head_decal(C.rrect(0.5, 0.12, 0.05, n=2), ph * D, ps * D, 0.32, H_IN + H_T - 0.005, 0.015)
             for ph, ps in ((60, 30), (-60, 30), (180, 28))]
    straps = []
    for s in (1, -1):
        a = C.head_pt(s * 75 * D, helmet_band(s * 75 * D), H_IN)
        straps.append(C.tube([a, C.Vector((s * 0.5, -0.35, 3.95)), C.Vector((s * 0.2, -0.42, 3.74)),
                              C.Vector((0, -0.42, 3.7))], [0.025] * 4, sides=5, res=2))
    C.part([rim] + vents + straps, "HelmetTrim", "#1E1F22", arm=arm, bone="Head", smooth=45)
    bolt = [C.head_decal(piece, 22 * D, 33 * D, 0.62, H_IN + H_T - 0.004, 0.024, name="Sticker")
            for piece in C.BOLT]
    C.part(bolt, "Sticker", BOLT, arm=arm, bone="Head", role="tell_sticker", smooth=30)
    # white side stripes on the skate shoes
    for side, s in C.SIDES:
        st = ns.box((0.02, 0.4, 0.05), loc=(s * (C.SHOE_X + 0.25), -0.12, 0.17), rot=(-8, 0, 0), bevel=0.01, segments=1)
        C.part([st], "Leg" + side + "_Stripe", "#F0EEE8", arm=arm, bone="Leg" + side, smooth=40)


META = {"regular": "jo", "tells": {"tell_sticker": "hide = sticker missing"}, "favorite": "M5"}

if __name__ == "__main__":
    C.run_regular("Character_Regular_jo", build_regular, META)
