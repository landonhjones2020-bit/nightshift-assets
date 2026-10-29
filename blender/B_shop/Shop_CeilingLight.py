"""Shop_CeilingLight — flush fluorescent ceiling panel (4 x 1.2 x 0.3) for the kitchen,
counter and dining room.

White enamel housing with rounded corners and end caps, a stainless trim ring and a warm
white prismatic diffuser (part Diffuser, Neon #FFF4DC, role "lamp" — the server swaps it
to SmoothPlastic / dims it in blackouts and flickers it for tells).
PIVOT = TOP centre (z = 0 is the ceiling plane; the fitting hangs below it), so place the
pivot on the 12-stud ceiling. Socket Light = diffuser centre (attach a SurfaceLight /
PointLight facing down).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L, W, H = 4.0, 1.2, 0.3
WARM = "#FFF4DC"


def build():
    housing = C.prism(C.rrect(L, W, 0.14, 2), "z", -H, 0.0)
    ns.bevel(housing, width=0.05, segments=2)
    ns.tag(housing, "Housing", "#E9E6DE", smooth_angle=40)
    trim = C.ring_slab(C.rrect(L - 0.12, W - 0.12, 0.1, 2), C.rrect(L - 0.36, W - 0.36, 0.06, 2), "z", -H - 0.05, -H + 0.01)
    ends = [ns.box((0.14, W - 0.3, 0.06), loc=(sx * (L / 2 - 0.25), 0, -H - 0.06), bevel=0.02, segments=1)
            for sx in (-1, 1)]
    C.part([trim] + ends, "Trim", C.STAINLESS, "Metal", smooth_angle=40)
    # prismatic diffuser: shallow vaulted panel (two soft ridges hint at the tubes inside)
    dif = C.prism(C.fillet([(-(W - 0.38) / 2, -H - 0.01), ((W - 0.38) / 2, -H - 0.01), ((W - 0.38) / 2, -H - 0.06),
                            (0.12, -H - 0.1), (0.0, -H - 0.08), (-0.12, -H - 0.1), (-(W - 0.38) / 2, -H - 0.06)],
                           [0, 0, 0.02, 0.04, 0.03, 0.04, 0.02], 2), "x", -(L - 0.38) / 2, (L - 0.38) / 2)
    ns.tag(dif, "Diffuser", WARM, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=60)


META = {"pivot": "TOP centre (ceiling plane)", "size": [L, H + 0.1, W], "mount_height": 12,
        "light_hint": {"type": "SurfaceLight", "face": "Bottom", "color": WARM, "range": 16, "brightness": 1.6}}

if __name__ == "__main__":
    C.run_hanging(build, "Shop_CeilingLight", pivot=(0, 0, 0), meta=META, sockets={"Light": ((0, 0, -H - 0.1), 0.0)})
