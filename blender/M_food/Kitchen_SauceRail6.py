"""Kitchen_SauceRail6 — worktop caddy holding 6 squeeze bottles (M_food batch, group "Kitchen").

Kitchen_SauceRail (A_kitchen) widened to six holders: 4.6 long x 0.9 deep stainless caddy with a
black ribbed rubber drip mat, a collar plate with six round holders that keep the bottles upright,
end cheeks and a red-orange back riser with a rolled top. The bottles are Kitchen_SauceBottle
(separate asset, placed at the sockets). Front faces -Y; sits on the worktop (bottom at z = 0).

Same conventions as the 4-holder rail: pivot = bounding-box bottom-centre, holder pitch 0.76, the
bottle row 0.04 in front of the caddy's centre line, collar at 0.5.
Sockets Bottle1..Bottle6 = bottle base centres on the mat (yaw 0), Bottle1 at Blender -X, which is
Roblox +X (as Bottle1 on Kitchen_SauceRail), Bottle6 at the other end.
Tab1..Tab6 (roles bottle_tab1..6) are the coloured stickers on the collar front under each holder,
so the client can tint them to the sauce in that holder.
Run:  bpyenv/bin/python blender/M_food/Kitchen_SauceRail6.py   (NS_EXPORT=1 export)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
K = C.kitchen()
N_HOLDERS = 6
L, D = 4.6, 0.9
PITCH = 0.76
XS = [(i - (N_HOLDERS - 1) / 2) * PITCH for i in range(N_HOLDERS)]   # -1.9 .. 1.9
HOLE_R = 0.29                  # holder inner radius (fits bottles up to ~0.52 across)
BASE_T = 0.12
COLLAR_Z = 0.5                 # collar plate centre height
Y0 = -0.04                     # bottle row centre (riser behind)
RISER_H = 0.8


def build():
    # base and cheeks stop 0.02 inside the riser's back face (no coplanar z-fighting with the riser)
    base = ns.box((L, D - 0.02, BASE_T), loc=(0, -0.01, BASE_T / 2), bevel=0.045, segments=2)
    cheeks = [ns.box((0.1, D - 0.02, COLLAR_Z + 0.06), loc=(sx * (L / 2 - 0.05), -0.01, (COLLAR_Z + 0.06) / 2),
                     bevel=0.04, segments=1)
              for sx in (-1, 1)]
    collar = ns.box((L, D - 0.12, 0.09), loc=(0, Y0 + 0.02, COLLAR_Z), bevel=0.0)
    for x in XS:
        ns.boolean(collar, ns.cyl(HOLE_R, 0.5, loc=(x, Y0, COLLAR_Z), verts=16, bevel=0.0))
    ns.bevel(collar, width=0.025, segments=1)
    K.part([base, collar] + cheeks, "Caddy", K.STAINLESS, "Metal", smooth_angle=40)

    # back riser in the brand colour with a rolled top
    riser = ns.box((L, 0.1, RISER_H), loc=(0, D / 2 - 0.05, RISER_H / 2), bevel=0.05, segments=2)
    roll = K.rod((-L / 2, D / 2 - 0.05, RISER_H), (L / 2, D / 2 - 0.05, RISER_H), 0.075, verts=10, bevel=0.03)
    K.part([riser, roll], "Riser", K.BRAND, "SmoothPlastic", smooth_angle=45)

    # rubber drip mat with ribs
    mat = [ns.box((L - 0.3, D - 0.25, 0.03), loc=(0, Y0, BASE_T + 0.015), bevel=0.0)]
    mat += [ns.box((L - 0.4, 0.035, 0.025), loc=(0, Y0 - 0.25 + 0.125 * k, BASE_T + 0.04), bevel=0.0) for k in range(5)]
    K.part(mat, "Mat", K.RUBBER, "SmoothPlastic", smooth_angle=None)

    # colour tabs on the collar front, one under each holder
    for i, x in enumerate(XS, start=1):
        tab = ns.box((0.32, 0.03, 0.06), loc=(x, Y0 + 0.02 - (D - 0.12) / 2 - 0.01, COLLAR_Z), bevel=0.012, segments=1)
        K.part(tab, f"Tab{i}", K.MUSTARD, "SmoothPlastic", recolor=f"bottle_tab{i}")

    mat_top = BASE_T + 0.03
    if os.environ.get("NS_DEV") == "1":   # untagged fit-check bottles (never exported)
        for x in XS:
            b = ns.cyl(0.24, 1.0, loc=(x, Y0, mat_top + 0.5), verts=16, bevel=0.06)
            b.data.materials.append(ns.material("#D9C21E"))
    sockets = {f"Bottle{i + 1}": ((x, Y0, mat_top), 0) for i, x in enumerate(XS)}
    meta = {"holder_inner_diameter": round(2 * HOLE_R, 3), "holder_height": COLLAR_Z + 0.045,
            "bottle_pitch": PITCH, "bottle_count": N_HOLDERS}
    return {"export": {"sockets": sockets, "meta": meta}}


if __name__ == "__main__":
    C.run(build, "Kitchen_SauceRail6", meta_=None, pivot=None, group="Kitchen")
