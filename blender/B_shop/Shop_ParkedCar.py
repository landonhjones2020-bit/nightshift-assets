"""Shop_ParkedCar — chunky stylized 1980s four-door sedan (~16 long) for the parking lot.

Boxy three-box body in faded maroon (role "car_paint" for variety), dark glass greenhouse
with body-colour roof and pillars, chrome bumpers/grille surround/side trim, black rubber
mouldings, quad square headlights (Headlights, role "headlight": switch Material to Neon to
turn them on), red taillights (role "taillight"), wheels with chrome hubcaps, and a blank
rear plate (role sign_panel).
Front of the car = -Y. Pivot = bottom-centre. Sockets: DriverDoor (outside the driver's
door, facing the car), HeadlightL / HeadlightR (attach SpotLights facing -Y).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402

ns = C.ns
PAINT = "#6E343A"
GLASS_DARK = "#1E262E"
WB = (-5.0, 5.1)          # axle y positions
WR = 1.25                 # wheel radius
HW = 3.15                 # half width of the body


def greenhouse(y0, y1, y2, y3, z0, z1, w0, w1):
    """Tapered cabin: bottom y0..y3 at z0 (width w0), roof y1..y2 at z1 (width w1)."""
    bm = bmesh.new()
    b = [bm.verts.new((sx * w0 / 2, y, z0)) for sx, y in ((-1, y0), (1, y0), (1, y3), (-1, y3))]
    t = [bm.verts.new((sx * w1 / 2, y, z1)) for sx, y in ((-1, y1), (1, y1), (1, y2), (-1, y2))]
    bm.faces.new(b)
    bm.faces.new(list(reversed(t)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([b[i], t[i], t[j], b[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, "Cabin", bevel=0.1, segments=1)


def build():
    side = [(-8.0, 1.0), (-8.0, 2.55), (-7.85, 3.0), (-3.3, 3.35), (4.3, 3.35), (7.8, 3.25), (8.0, 2.85),
            (8.0, 1.0), (7.7, 0.7), (-7.7, 0.7)]
    side = C.fillet(side, [0.1, 0.12, 0.25, 0.1, 0.1, 0.2, 0.12, 0.1, 0.1, 0.1], 2)
    body = C.prism(side, "x", -HW, HW)
    for y in WB:
        ns.boolean(body, ns.cyl(WR + 0.25, 2 * HW + 1, loc=(0, y, WR), rot=(0, 90, 0), verts=18, bevel=0.0))
    ns.bevel(body, width=0.09, segments=1)
    cab_y = (-3.0, -1.2, 2.7, 4.1)
    roof = greenhouse(cab_y[1] - 0.05, cab_y[1] + 0.12, cab_y[2] - 0.1, cab_y[2] + 0.05, 5.2, 5.5, 5.35, 5.25)
    pillars = []
    for sx in (-1, 1):   # B pillar + window frame stripes on each side
        pillars.append(ns.box((0.14, 0.5, 2.02), loc=(sx * 2.8, 0.7, 4.27), rot=(0, -sx * 11.6, 0), bevel=0.03,
                              segments=1))
    ns.tag(C.merge([body, roof] + pillars, "Body"), "Body", PAINT, recolor="car_paint", can_collide=True,
           smooth_angle=35)
    cab = greenhouse(*cab_y, 3.3, 5.25, 5.9, 5.1)
    ns.tag(cab, "Windows", GLASS_DARK, "Glass", smooth_angle=30)

    chrome = []
    for y, d in ((-8.15, 1), (8.15, -1)):     # bumpers
        chrome.append(ns.box((2 * HW + 0.3, 0.45, 0.6), loc=(0, y, 1.45), bevel=0.15, segments=1))
    chrome.append(C.ring_slab(C.rrect(3.0, 0.95, 0.1, 1, 0, 2.3), C.rrect(2.7, 0.7, 0.05, 1, 0, 2.3), "y", -8.08, -7.98))
    def strip_runs(half_chord, y0=-7.6, y1=7.6):
        """y ranges of a side strip broken at the wheel arches (it used to run across the openings)."""
        cuts = sorted((y - half_chord, y + half_chord) for y in WB)
        runs, a = [], y0
        for c0, c1 in cuts:
            runs.append((a, c0))
            a = c1
        runs.append((a, y1))
        return [(a, b) for a, b in runs if b - a > 0.2]

    for sx in (-1, 1):
        for a, b in strip_runs(1.19):        # arch half-chord at z 2.3..2.4 is 1.07, + 0.12 for the bevel
            chrome.append(ns.box((0.06, b - a, 0.1), loc=(sx * (HW + 0.03), (a + b) / 2, 2.35), bevel=0.02, segments=1))
        chrome.append(ns.box((0.25, 0.4, 0.3), loc=(sx * (HW + 0.15), -2.7, 3.7), bevel=0.06, segments=1))  # mirrors
        # mirror arm from the door top (beltline 3.35) to the mirror (it floated 0.2 above the body)
        chrome.append(C.pipe([(sx * (HW - 0.15), -2.68, 3.25), (sx * (HW + 0.12), -2.7, 3.62)], 0.05, sides=6))
    hubs = []
    tires = []
    for y in WB:
        for sx in (-1, 1):
            x = sx * (HW - 0.55)
            tires.append(ns.cyl(WR, 1.0, loc=(x, y, WR), rot=(0, 90, 0), verts=16, bevel=0.2, segments=1))
            hubs.append(ns.cyl(0.72, 0.1, loc=(x + sx * 0.5, y, WR), rot=(0, 90, 0), verts=10, radius_top=0.5,
                               bevel=0.0))
    C.part(chrome + hubs, "Chrome", C.CHROME, "Metal", smooth_angle=45)
    grille = ns.box((2.7, 0.08, 0.7), loc=(0, -8.0, 2.3), bevel=0.0)
    rubber = [grille]
    for sx in (-1, 1):
        for a, b in strip_runs(1.55):        # arch half-chord at z 1.71 is 1.43, + 0.12
            rubber.append(ns.box((0.08, b - a, 0.28), loc=(sx * (HW + 0.03), (a + b) / 2, 1.85), bevel=0.03, segments=1))
    C.part(tires + rubber, "Rubber", C.RUBBER, smooth_angle=45)

    heads = []
    for sx in (-1, 1):
        for k in range(2):
            x = sx * (1.85 + k * 0.62)
            heads.append(ns.box((0.52, 0.1, 0.52), loc=(x, -8.02, 2.3), bevel=0.04, segments=1))
    ns.tag(C.merge(heads, "Headlights"), "Headlights", "#F4EDCC", recolor="headlight", cast_shadow=False)
    tails = [ns.box((1.5, 0.1, 0.5), loc=(sx * 2.15, 8.02, 2.4), bevel=0.04, segments=1) for sx in (-1, 1)]
    ns.tag(C.merge(tails, "Taillights"), "Taillights", "#B3221E", recolor="taillight", cast_shadow=False)
    plate = ns.box((1.4, 0.05, 0.7), loc=(0, 8.03, 1.95), bevel=0.0)
    ns.tag(plate, "Plate", C.PAPER, recolor="sign_panel")


META = {"size": [6.6, 5.5, 16.6], "front": "-Y (LookVector)", "paint_variants": ["#6E343A", "#3C6670", "#B9AE8F", "#2F3A55"],
        "surfaces": [{"part": "Plate", "face": "Back"}],
        "light_hint": {"type": "SpotLight", "color": "#FFF1C4", "range": 30, "angle": 60}}

if __name__ == "__main__":
    C.run(build, "Shop_ParkedCar", meta=META,
          sockets={"DriverDoor": ((-HW - 1.6, -0.6, 0), 90.0), "HeadlightL": ((-2.16, -8.1, 2.3), 0.0),
                   "HeadlightR": ((2.16, -8.1, 2.3), 0.0)})
