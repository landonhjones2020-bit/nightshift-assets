"""Character_Regular_walt — Old Walt (Regular; the Copy may impersonate him).

Photo-board read: white horseshoe hair, bushy white brows, big ROUND glasses, mustard
knit cardigan over a pale-blue collared shirt, grey slacks, a wooden crook cane in his
LEFT hand (the right hand is free to wave).
Tells (runtime roles): tell_glasses (frame + lenses; hide both = glasses missing).
Also eye, eyelid, and cane (the cane part, so code can hide it while seated if wanted).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
TITLE = "Old Walt"
SKIN = "#EBC2A2"
CARDI = "#B07A3A"
SHIRT = "#BFD3E6"
WHITE_HAIR = "#E8E5DE"


def build_regular(arm):
    D = C.D2R
    look = {"skin": SKIN, "top": SHIRT, "pants": "#6E6A64", "shoes": "#5A3A24", "sole": "#2B2520",
            "brow": WHITE_HAIR, "brow_size": (0.24, 0.07, 0.085), "brow_tilt": 12.0, "generic": False,
            "lid_drop": 0.06, "mouth_curve": 0.012, "arm_color": CARDI, "arm_mat": "Fabric"}
    C.build_body(arm, look)
    def of(t):
        z = C.torso_frame(t, C.GARMENT)[0]
        return (4 + 22 * C.smoothstep(2.7, 3.5, z)) * D
    t0, t1 = C.gt(2.0), C.gt(3.585)
    cardigan = C.garment(t0, t1, 0.03, 0.05, open_front=of, nu=28, nv=9, name="Cardigan")
    hem = C.garment(C.gt(1.98), C.gt(2.1), 0.035, 0.06, open_front=of, nu=28, nv=2, name="CardiHem")
    pockets = [C.garment(C.gt(2.15), C.gt(2.5), 0.08, 0.025, phi_range=((s * 40 - 16) * D, (s * 40 + 16) * D), nu=4,
                         nv=3, name="Pocket") for s in (1, -1)]
    C.part([cardigan, hem] + pockets, "Cardigan", CARDI, "Fabric", arm=arm, bone="Torso", smooth=45)
    buttons = [ns.sphere(0.035, loc=tuple(C.torso_pt(-(of(C.gt(z)) + 0.05), C.gt(z), 0.09)), segs=8, rings=4)
               for z in (2.2, 2.42, 2.64)]
    C.part(buttons, "Buttons", "#5A3A24", arm=arm, bone="Torso", smooth=50)
    collar = []
    for s in (1, -1):
        pts = [(0.0, 0.0), (s * 0.19, 0.02), (s * 0.05, -0.22)]
        o = ns.profile_slab(pts, 0.03, bevel=0.01, segments=1)
        ns.apply_all(o)
        C.xform(o, C.Matrix.Translation((s * 0.05, -0.3, 3.63)) @ C.Matrix.Rotation(math.radians(60), 4, "X"))
        collar.append(o)
    C.part(collar, "ShirtCollar", SHIRT, arm=arm, bone="Torso", smooth=40)
    # white horseshoe hair: sides + back only, fluffy
    tf = C.tuft_field(10, 4, h=(0.03, 0.06), w=(0.25, 0.4), psi_max=2.0)

    def edge(phi):
        return C.hairline(phi, front=60, side=88, back=112)

    def fo(u, v):
        phi = (58 + 244 * u) * D
        top = 64 * D + 10 * D * math.cos(phi - math.pi)
        psi = top + (edge(phi) - top) * v
        return C.head_pt(phi, psi, 0.012 + 0.065 * math.sin(math.pi * min(1.0, 0.15 + v)) + tf(phi, psi))

    def fi(u, v):
        phi = (58 + 244 * u) * D
        top = 64 * D + 10 * D * math.cos(phi - math.pi)
        return C.head_pt(phi, top + (edge(phi) - top) * v, 0.01)
    hair = C.patch(fo, fi, 30, 5, closed_u=False, pole=False, inner="full", name="Hair")
    C.part([hair], "Hair", WHITE_HAIR, arm=arm, bone="Head", smooth=55)
    C.place_accessory(C.acc_face_glasses(frame="#A8823A", lens="#CFE6F2", round_=True, role="tell_glasses",
                                         w=0.33, h=0.31), arm=arm, bone="Head")
    # crook cane in the left hand (hand hangs at the wrist; grip ~0.27 below it)
    g = C.wrist(1) + C.arm_dir(1) * 0.27
    hook_c = C.Vector((g.x, g.y - 0.11, g.z + 0.17))
    hook = []
    for k in range(9):
        a = math.radians(180 - 180 * k / 8)
        hook.append(C.Vector((g.x, hook_c.y + 0.12 * math.cos(a), hook_c.z + 0.12 * math.sin(a) * 0.95)))
    shaft = [hook[-1], C.Vector((g.x + 0.02, g.y - 0.0, g.z - 0.6)), C.Vector((g.x + 0.04, g.y + 0.02, 0.16))]
    cane = C.tube(hook + shaft[1:], [0.055] * (len(hook) + 2), sides=8, res=2, name="Cane")
    tip = ns.cyl(0.065, 0.14, loc=(g.x + 0.04, g.y + 0.02, 0.07), verts=10, bevel=0.015)
    C.part([cane], "Cane", "#7A4E2C", "Wood", arm=arm, bone="HandL", role="cane", smooth=50)
    C.part([tip], "CaneTip", "#1E1F22", arm=arm, bone="HandL", smooth=50)


META = {"regular": "walt", "tells": {"tell_glasses": "hide frame + lenses = glasses missing"},
        "cane": {"role": "cane", "bone": "HandL", "hideWhileSeated": True,
                 "note": "rides the left hand; hide it during Sit/Eat (it would swing over the table)"},
        "favorite": "M1"}

if __name__ == "__main__":
    C.run_regular("Character_Regular_walt", build_regular, META)
