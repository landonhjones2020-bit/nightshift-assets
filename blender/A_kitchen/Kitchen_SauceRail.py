"""Kitchen_SauceRail — worktop caddy holding the 4 squeeze bottles.

3.2 long stainless caddy: a base with a black rubber drip mat, a collar plate with four
round holders that keep the bottles upright, end cheeks and a red-orange back riser. The
bottles themselves are Kitchen_SauceBottle (separate asset, placed at the sockets).
Front faces -Y; sits on the worktop (bottom at z = 0).

Sockets Bottle1..Bottle4 = bottle base centres on the mat, Bottle1 at -X, yaw 0.
Tab1..Tab4 (roles bottle_tab1..4) are the coloured stickers on the collar front under each
bottle, so the client can tint them to the sauce in that holder.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L, D = 3.2, 0.9
PITCH = 0.76
XS = [(-1.5 + i) * PITCH for i in range(4)]
HOLE_R = 0.29                  # holder inner radius (fits bottles up to ~0.52 across)
BASE_T = 0.12
COLLAR_Z = 0.5                 # collar plate centre height
Y0 = -0.04                     # bottle row centre (riser behind)
RISER_H = 0.8


def build():
    # base and cheeks stop 0.02 inside the riser's back face (their back faces were coplanar with it -> the
    # stainless and the red riser z-fought along the back); front faces unchanged
    base = ns.box((L, D - 0.02, BASE_T), loc=(0, -0.01, BASE_T / 2), bevel=0.045, segments=2)
    cheeks = [ns.box((0.1, D - 0.02, COLLAR_Z + 0.06), loc=(sx * (L / 2 - 0.05), -0.01, (COLLAR_Z + 0.06) / 2), bevel=0.04,
                     segments=1)
              for sx in (-1, 1)]
    collar = ns.box((L, D - 0.12, 0.09), loc=(0, Y0 + 0.02, COLLAR_Z), bevel=0.0)
    for x in XS:
        ns.boolean(collar, ns.cyl(HOLE_R, 0.5, loc=(x, Y0, COLLAR_Z), verts=16, bevel=0.0))
    ns.bevel(collar, width=0.025, segments=1)
    C.part([base, collar] + cheeks, "Caddy", C.STAINLESS, "Metal", smooth_angle=40)

    # back riser in the brand colour with a rolled top
    riser = ns.box((L, 0.1, RISER_H), loc=(0, D / 2 - 0.05, RISER_H / 2), bevel=0.05, segments=2)
    roll = C.rod((-L / 2, D / 2 - 0.05, RISER_H), (L / 2, D / 2 - 0.05, RISER_H), 0.075, verts=10, bevel=0.03)
    C.part([riser, roll], "Riser", C.BRAND, "SmoothPlastic", smooth_angle=45)

    # rubber drip mat with ribs
    mat = [ns.box((L - 0.3, D - 0.25, 0.03), loc=(0, Y0, BASE_T + 0.015), bevel=0.0)]
    mat += [ns.box((L - 0.4, 0.035, 0.025), loc=(0, Y0 - 0.25 + 0.125 * k, BASE_T + 0.04), bevel=0.0) for k in range(5)]
    C.part(mat, "Mat", C.RUBBER, "SmoothPlastic", smooth_angle=None)

    # colour tabs on the collar front, one under each holder
    for i, x in enumerate(XS, start=1):
        tab = ns.box((0.32, 0.03, 0.06), loc=(x, Y0 + 0.02 - (D - 0.12) / 2 - 0.01, COLLAR_Z), bevel=0.012, segments=1)
        C.part(tab, f"Tab{i}", C.MUSTARD, "SmoothPlastic", recolor=f"bottle_tab{i}")

    mat_top = BASE_T + 0.03
    if os.environ.get("NS_DEV") == "1":   # untagged fit-check bottles (never exported)
        for x in XS:
            b = ns.cyl(0.24, 1.0, loc=(x, Y0, mat_top + 0.5), verts=16, bevel=0.06)
            b.data.materials.append(ns.material("#D9C21E"))
    sockets = {f"Bottle{i + 1}": ((x, Y0, mat_top), 0) for i, x in enumerate(XS)}
    meta = {"holder_inner_diameter": round(2 * HOLE_R, 3), "holder_height": COLLAR_Z + 0.045,
            "bottle_pitch": PITCH}
    return {"export": {"sockets": sockets, "meta": meta}}


if __name__ == "__main__":
    C.run(build, "Kitchen_SauceRail")
