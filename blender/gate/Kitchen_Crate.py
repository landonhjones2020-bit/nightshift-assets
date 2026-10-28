"""Kitchen_Crate — stackable plastic supply crate (pipeline-gate asset #2).

One mesh serves all five crate types (Meat, Cheese, Veg, Bread, Sauce): the Body and
Trim parts carry runtime roles so StockService recolours them per type, and the Label
plate gets a SurfaceGui with the type name in Studio.
Front (the label side) faces Blender -Y => Roblox LookVector.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import nslib as ns  # noqa: E402

W, D, H = 2.0, 1.4, 1.0     # outer size (x, y, z) in studs
T = 0.1                     # wall thickness
BODY = "#4FA04A"            # Veg green (default); recoloured per crate type
TRIM = "#3B7D37"
LABEL = "#F3EEE2"


def build():
    body = ns.box((W, D, H), loc=(0, 0, H / 2), bevel=0.0, name="Body")
    # hollow it out (open top, 0.1 floor)
    ns.boolean(body, ns.box((W - 2 * T, D - 2 * T, H), loc=(0, 0, H / 2 + T), bevel=0.0))
    # handle slots through both short ends
    ns.boolean(body, ns.box((W + 0.4, 0.55, 0.2), loc=(0, 0, H - 0.25), bevel=0.0))
    # vent slots on both long sides (below the label)
    for x in (-0.5, 0.0, 0.5):
        ns.boolean(body, ns.box((0.16, D + 0.4, 0.3), loc=(x, 0, 0.32), bevel=0.0))
    ns.bevel(body, width=0.025, segments=2)
    ns.tag(body, "Body", BODY, "SmoothPlastic", smooth_angle=40, recolor="crate_body")

    # rolled top rim, slightly proud of the walls
    rim_outer = ns.box((W + 0.06, D + 0.06, 0.12), loc=(0, 0, H - 0.03), bevel=0.0)
    ns.boolean(rim_outer, ns.box((W - 2 * T - 0.03, D - 2 * T - 0.03, 0.4), loc=(0, 0, H - 0.03), bevel=0.0))
    # stacking feet at the four corners
    feet = [ns.box((0.22, 0.22, 0.06), loc=(sx * (W / 2 - 0.16), sy * (D / 2 - 0.16), 0.03), bevel=0.0)
            for sx in (-1, 1) for sy in (-1, 1)]
    trim = ns.join_applied([rim_outer] + feet, "Trim")
    ns.bevel(trim, width=0.02, segments=2)
    ns.tag(trim, "Trim", TRIM, "SmoothPlastic", smooth_angle=40, recolor="crate_trim")

    label = ns.box((0.95, 0.03, 0.26), loc=(0, -D / 2 - 0.012, 0.7), bevel=0.01, segments=1)
    ns.tag(label, "Label", LABEL, "SmoothPlastic", recolor="crate_label")


if __name__ == "__main__":
    ns.run_main(build, "Kitchen_Crate", "gate", "Kitchen",
                meta={"surface_label": {"part": "Label", "face": "Front"}, "carry_offset": [0, 0.9, -1.3]})
