"""Kitchen_MeatHook — ceiling meat rail with a hook and a wrapped meat bundle (freezer).

A short overhead rail (two ceiling hangers with flanges), a trolley, an S-hook and a big
paper-wrapped meat bundle tied with twine, torn open at the bottom so a little dark-red
meat shows. Lumpy on purpose. Decor with a creepy sway: the hook and everything on it are
separate parts with swing_* roles (listed in meta swing_parts) so the client can rotate
them together about meta swing_pivot (the trolley pin, Roblox model space).

Pivot = bottom-centre (the bundle's bottom); meta mount_top = height from the pivot to the
ceiling flanges, so the map places the pivot at ceiling_height - mount_top.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
PAPER_W = "#E9E2D3"
TWINE = "#B08A5A"
MEAT = "#9E3B43"
RAIL_Z = 3.9                     # rail centre height above the bundle bottom
TOP = RAIL_Z + 0.75              # ceiling flange top


def lump(obj, lean=0.12):
    """Coherent low-frequency lumps + a lopsided bulge + a slight lean, applied the same way
    to every bundle part so the twine keeps hugging the paper."""
    ns.apply_all(obj)
    for v in obj.data.vertices:
        r = math.hypot(v.co.x, v.co.y)
        z = v.co.z
        th = math.atan2(v.co.y, v.co.x)
        if r > 1e-4:
            k = 1.0 + 0.05 * math.sin(3 * th + 2.1 * z) + 0.03 * math.sin(5 * th - 3.3 * z + 1.0)
            k *= 1.0 + 0.1 * math.cos(th - 0.6) * max(0.0, 1.0 - abs(z - 0.9))   # one fat side low down
            v.co.x *= k
            v.co.y *= k * 0.86
        v.co.x += lean * max(0.0, 1.2 - z) ** 2 * 0.4                               # bottom swings out a bit
    return obj


def build():
    # ---- rail, hangers, trolley -------------------------------------------------------
    rail = [C.rod((-1.6, 0, RAIL_Z), (1.6, 0, RAIL_Z), 0.1, verts=10, bevel=0.03)]
    for x in (-1.2, 1.2):
        rail.append(C.rod((x, 0, RAIL_Z), (x, 0, TOP - 0.05), 0.06, verts=8))
        rail.append(ns.cyl(0.22, 0.06, loc=(x, 0, TOP - 0.03), verts=10, bevel=0.0))
    caps = [ns.cyl(0.13, 0.08, loc=(sx * 1.62, 0, RAIL_Z), rot=(0, 90, 0), verts=10, bevel=0.025, segments=1) for sx in (-1, 1)]
    C.part(rail + caps, "Rail", C.STEEL_DARK, "Metal", smooth_angle=50)
    trolley = [ns.box((0.36, 0.08, 0.32), loc=(0, sy * 0.15, RAIL_Z - 0.05), bevel=0.03, segments=1) for sy in (-1, 1)]
    trolley += [ns.cyl(0.11, 0.06, loc=(0, sy * 0.15, RAIL_Z + 0.06), rot=(90, 0, 0), verts=10, bevel=0.0) for sy in (-1, 1)]
    pin = C.rod((0, -0.22, RAIL_Z - 0.15), (0, 0.22, RAIL_Z - 0.15), 0.035, verts=6)
    C.part(trolley + [pin], "Trolley", C.GUNMETAL, "Metal", smooth_angle=50)

    # ---- S-hook --------------------------------------------------------------------
    hz = RAIL_Z - 0.15
    hook = ns.tube([(0, 0.0, hz + 0.12), (0, -0.14, hz - 0.02), (0, 0.0, hz - 0.18), (0, 0.0, hz - 0.55),
                    (0, 0.0, hz - 0.85), (0, 0.18, hz - 1.0), (0, 0.24, hz - 0.85)],
                   [0.05] * 7, sides=8, resolution=3, name="Hook")
    C.part(hook, "Hook", C.STEEL, "Metal", recolor="swing_hook", smooth_angle=60)

    # ---- wrapped bundle: lumpy paper body, gathered neck, twine bands -----------------
    neck_z = hz - 0.95
    prof = [(0.68, 0.5), (0.75, 0.8), (0.74, 1.12), (0.64, 1.48), (0.5, 1.8), (0.34, 2.1),
            (0.22, 2.38), (0.15, neck_z - 0.14), (0.13, neck_z), (0.08, neck_z + 0.08), (0.0, neck_z + 0.1)]
    body = ns.lathe(prof, verts=16, name="Bundle")
    ns.apply_all(body)
    for v in body.data.vertices:          # torn bottom edge: every other bottom vertex drops
        if abs(v.co.z - 0.5) < 1e-4:
            i = round((math.degrees(math.atan2(v.co.y, v.co.x)) % 360) / (360 / 16))
            v.co.z += -0.14 if i % 2 else 0.05
    lump(body)
    C.part(body, "Bundle", PAPER_W, "SmoothPlastic", recolor="swing_bundle", smooth_angle=80)
    meat = ns.lathe([(0.0, 0.0), (0.3, 0.04), (0.5, 0.17), (0.61, 0.38), (0.66, 0.62), (0.0, 0.66)], verts=16, name="Meat")
    lump(meat)
    C.part(meat, "Meat", MEAT, "SmoothPlastic", recolor="swing_meat", smooth_angle=80)
    bands = []
    for z, r in ((0.82, 0.76), (1.38, 0.7), (1.92, 0.48)):
        bands.append(ns.torus(r, 0.04, loc=(0, 0, z), major_segs=14, minor_segs=4))
    bands.append(ns.torus(0.13, 0.045, loc=(0, 0, neck_z - 0.05), major_segs=10, minor_segs=4))
    for o in bands:
        lump(o)
    C.part(bands, "Twine", TWINE, "SmoothPlastic", recolor="swing_twine", smooth_angle=80)

    pivot = (0.0, 0.0, 0.0)
    meta = {
        "mount": "ceiling", "mount_top": TOP,
        "swing_pivot": C.rbx((0, 0, hz), pivot), "swing_axis": C.rbx_dir((1, 0, 0)),
        "swing_parts": ["Hook", "Bundle", "Meat", "Twine"], "decor": True,
    }
    return {"export": {"meta": meta}}


if __name__ == "__main__":
    C.run(build, "Kitchen_MeatHook")
