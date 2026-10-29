"""Character_Regular_gus — Gus the trucker (Regular; the Copy may impersonate him).

Photo-board read: trucker cap worn BACKWARDS (brim over the nape), big bushy mustache,
red buffalo-check flannel, jeans, work boots, a comfortable belly.
Tells (runtime roles): tell_cap (single part; the Copy rotates it 180 deg about the
HatSocket vertical axis -> facing forward), tell_mustache (hide = missing),
tell_flannel (torso + both sleeves; recolour = wrong colour; the black check stays).
Also: eye (EyeL/EyeR), eyelid (EyelidL/EyelidR). Same bones/sockets/clips as Character_Human.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
TITLE = "Gus"
SKIN = "#E0A27C"
FLANNEL = "#C7372F"
CHECK = "#241D1D"
CAP = "#2E5AA8"
STACHE = "#6A5646"
BELLY = [(2.20, 0.70, 0.52, 2.4, -0.06), (2.26, 0.71, 0.53, 2.4, -0.065), (2.45, 0.745, 0.575, 2.5, -0.095),
         (2.75, 0.795, 0.585, 2.6, -0.1), (3.05, 0.82, 0.52, 2.7, -0.06), (3.28, 0.84, 0.46, 2.8, -0.02),
         (3.44, 0.77, 0.41, 2.7, 0.0), (3.55, 0.56, 0.33, 2.3, 0.0), (3.62, 0.30, 0.24, 2.0, 0.0)]


def build_regular(arm):
    D = C.D2R
    # shirt details joined into the role parts (collar points, placket) + plaid bands (fixed)
    collar = []
    for s in (1, -1):
        pts = [(0.0, 0.0), (s * 0.2, 0.02), (s * 0.06, -0.24)]
        o = ns.profile_slab([(x, y) for x, y in pts], 0.03, bevel=0.01, segments=1)
        ns.apply_all(o)
        C.xform(o, C.Matrix.Translation((s * 0.06, -0.3, 3.62)) @ C.Matrix.Rotation(math.radians(62), 4, "X"))
        collar.append(o)
    plack = C.garment(C.t_at_z(2.22, BELLY), C.t_at_z(3.5, BELLY), 0.012, 0.02, rings=BELLY,
                      phi_range=(-3.5 * D, 3.5 * D), nu=2, nv=8, name="Placket")
    look = {"skin": SKIN, "top": FLANNEL, "pants": "#3F5F8C", "shoes": "#5A3A24", "sole": "#2B2520",
            "brow": STACHE, "brow_size": (0.23, 0.065, 0.08), "brow_tilt": 4.0, "generic": False,
            "torso": BELLY, "roles": {"Torso": "tell_flannel", "ArmL": "tell_flannel", "ArmR": "tell_flannel"},
            "extra": {"Torso": collar + [plack]}, "mouth_curve": 0.012}
    C.build_body(arm, look)
    # buffalo check: dark horizontal + vertical bands on the shirt and sleeves
    bands = []
    for z in (2.32, 2.7, 3.08):
        bands.append(C.garment(C.t_at_z(z - 0.05, BELLY), C.t_at_z(z + 0.05, BELLY), 0.006, 0.012, rings=BELLY,
                               nu=28, nv=2, inner="none", name="CheckH"))
    for a in (24, 62, 100, 140, 180, 220, 260, 298, 336):
        bands.append(C.garment(C.t_at_z(2.2, BELLY), C.t_at_z(3.42, BELLY), 0.007, 0.011, rings=BELLY,
                               phi_range=((a - 4) * D, (a + 4) * D), nu=2, nv=7, inner="none", name="CheckV"))
    buttons = [ns.sphere(0.028, loc=tuple(C.torso_pt(0, C.t_at_z(z, BELLY), 0.035, BELLY)), segs=8, rings=4)
               for z in (2.45, 2.8, 3.15)]
    C.part(bands, "Torso_Check", CHECK, "Fabric", arm=arm, bone="Torso", smooth=40)
    C.part(buttons, "Torso_Buttons", "#EDE6D8", arm=arm, bone="Torso", smooth=50)
    for side, s in C.SIDES:
        sl = C.arm_bands(s, (-0.42, -0.86)) + C.arm_stripes(s, (60, 180, 300))
        C.part(sl, "Arm" + side + "_Check", CHECK, "Fabric", arm=arm, bone="Arm" + side, smooth=40)
    # short greying hair under the cap (sides/back), mustache, cap
    edge = lambda phi: C.hairline(phi, front=50, side=84, back=112)
    hair = C.hair_cap(edge, lambda phi, v: 0.045, nu=28, vs=[0.2, 0.45, 0.7, 0.88, 1.0], name="Hair")
    C.part([hair], "Hair", "#7A6A5E", arm=arm, bone="Head", smooth=55)
    C.place_accessory(C.acc_face_mustache(color=STACHE, big=True, role="tell_mustache", name="Mustache"),
                      arm=arm, bone="Head")
    C.place_accessory(C.acc_hat_trucker(backwards=True, single=("Cap", CAP, "tell_cap")), arm=arm, bone="Head")


META = {"regular": "gus", "tells": {"tell_cap": "rotate 180 deg about HatSocket's vertical axis = forward cap",
                                     "tell_mustache": "hide = missing", "tell_flannel": "recolour = wrong colour"},
        "favorite": "M4"}

if __name__ == "__main__":
    C.run_regular("Character_Regular_gus", build_regular, META)
