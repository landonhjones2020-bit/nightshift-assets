"""Shop_CCTVMonitor — chunky 2 x 2 bank of CRT security monitors with a control console.

Four tapered CRT casings in a black steel rack; each screen is its own flat part
(Screen1 = top-left, Screen2 = top-right, Screen3 = bottom-left, Screen4 = bottom-right,
role "screen", front face) for the camera-feed SurfaceGui / static overlay. Each CRT has
knobs and a power LED (role "led"). In front: a sloped console with a red-topped joystick
and button rows. Cables trail off the back.
Pivot = bottom-centre of the rack (the console sticks out 1.45 in front); it sits on
Shop_OfficeDesk Socket_Monitor. Socket Prompt = console centre (the "Sit / View cameras"
prompt).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402

ns = C.ns
CW, CH = 1.8, 1.4          # CRT front width / height
RD = 1.5                   # rack depth (y -0.75 .. 0.75)
CASE = "#A79F8B"
BEZEL = "#2C2E33"
RACK = "#1E2024"


def frustum(w0, h0, w1, h1, depth, loc):
    """Box tapering from a w0 x h0 front (at -Y) to a w1 x h1 back, centred at loc."""
    bm = bmesh.new()
    x, y, z = loc
    f = [bm.verts.new((x + sx * w0 / 2, y - depth / 2, z + sz * h0 / 2)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    b = [bm.verts.new((x + sx * w1 / 2, y + depth / 2, z + sz * h1 / 2)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    bm.faces.new(f)
    bm.faces.new(list(reversed(b)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new([f[i], b[i], b[j], f[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, "Frustum", bevel=0.08, segments=1)


def build():
    cases, bezels, knobs, leds = [], [], [], []
    slots = {1: (-1, 1), 2: (1, 1), 3: (-1, 0), 4: (1, 0)}
    for idx, (sx, row) in slots.items():
        cx = sx * (CW / 2 + 0.05)
        cz = 0.1 + CH / 2 + row * (CH + 0.1)
        cases.append(frustum(CW, CH, CW * 0.62, CH * 0.62, RD - 0.1, (cx, 0.0, cz)))
        fy = -(RD - 0.1) / 2
        bz = C.ring_slab(C.rrect(CW - 0.28, CH - 0.4, 0.2, 2, cx, cz + 0.16),
                         C.rrect(CW - 0.5, CH - 0.62, 0.14, 2, cx, cz + 0.16), "y", fy - 0.07, fy + 0.02)
        bezels.append(bz)
        scr = C.prism(C.rrect(CW - 0.5, CH - 0.62, 0.14, 1, cx, cz + 0.16), "y", fy - 0.02, fy + 0.03)
        ns.tag(scr, f"Screen{idx}", C.SCREEN_OFF, "Glass", recolor="screen", cast_shadow=False)
        for kx in (0.45, 0.65):
            knobs.append(ns.cyl(0.06, 0.08, loc=(cx + kx, fy - 0.08, cz - CH / 2 + 0.17), rot=(90, 0, 0), verts=8,
                                bevel=0.0))
        led = ns.sphere(0.035, loc=(cx - CW / 2 + 0.3, fy - 0.07, cz - CH / 2 + 0.17), segs=6, rings=4)
        ns.tag(led, f"Led{idx}", "#45FF6A", "Neon", recolor="led", cast_shadow=False)
    C.part(cases, "Cases", CASE, smooth_angle=40)
    C.part(bezels, "Bezels", BEZEL, smooth_angle=40)

    # rack: corner posts, shelves, top
    rack = []
    rw = 2 * CW + 0.3
    for sx in (-1, 1):
        for sy in (-1, 1):
            rack.append(ns.box((0.08, 0.08, 2 * CH + 0.36), loc=(sx * rw / 2, sy * (RD / 2 - 0.04), CH + 0.18),
                               bevel=0.015, segments=1))
    for z in (0.05, CH + 0.15, 2 * CH + 0.3):
        rack.append(ns.box((rw + 0.08, RD, 0.08), loc=(0, 0, z), bevel=0.02, segments=1))
    # console (sloped) in front of the rack
    prof = C.fillet([(-1.45, 0.0), (-0.85, 0.0), (-0.85, 0.42), (-1.45, 0.22)], [0.03, 0.03, 0.06, 0.06], 1)
    console = C.prism(prof, "x", -1.6, 1.6)
    rack.append(console)
    C.part(rack, "Rack", RACK, "Metal", smooth_angle=40)
    # joystick, buttons, cables
    stick = [ns.cyl(0.04, 0.35, loc=(0.95, -1.15, 0.45), rot=(-14, 0, 0), verts=6, bevel=0.0),
             ns.cyl(0.14, 0.05, loc=(0.95, -1.15, 0.31), verts=10, bevel=0.0)]
    knobs += stick
    C.part(knobs, "Knobs", "#202226", smooth_angle=60)
    ns.tag(ns.sphere(0.09, loc=(0.95, -1.19, 0.63), segs=8, rings=6), "StickTop", "#D93B3B", smooth_angle=60)
    btns = {"#E8502A": [], "#F2B33D": [], "#3FBF5A": []}
    cols = list(btns)
    for i in range(6):
        for j in range(2):
            x = -1.25 + i * 0.3
            y = -1.27 + j * 0.25
            z = 0.25 + (y + 1.45) / 0.6 * 0.2 + 0.03
            btns[cols[(i + j) % 3]].append(ns.box((0.16, 0.14, 0.06), loc=(x, y, z), rot=(-18, 0, 0), bevel=0.0))
    for k, (col, objs) in enumerate(btns.items()):
        C.part(objs, f"Buttons{k + 1}", col, smooth_angle=50)
    cables = [C.pipe([(-0.6, 0.6, 2.2), (-0.7, 0.95, 1.6), (-0.55, 1.0, 0.35), (-0.2, 1.25, 0.05)], 0.05, sides=6,
                     corner=0.3, corner_segs=2),
              C.pipe([(0.7, 0.6, 0.8), (0.8, 0.95, 0.45), (1.2, 1.2, 0.05)], 0.05, sides=6, corner=0.25, corner_segs=2)]
    C.part(cables, "Cables", "#141518", smooth_angle=60)


META = {"screens": ["Screen1", "Screen2", "Screen3", "Screen4"], "screen_layout": "1 TL, 2 TR, 3 BL, 4 BR",
        "camera_feeds": {"Screen1": "parking lot", "Screen2": "freezer", "Screen3": "basement", "Screen4": "dining room"},
        "surfaces": [{"part": f"Screen{i}", "face": "Front"} for i in range(1, 5)],
        "pivot": "bottom-centre of the rack (console extends 1.45 in front)", "sits_on": "Shop_OfficeDesk Socket_Monitor"}

if __name__ == "__main__":
    C.run(build, "Shop_CCTVMonitor", pivot=(0, 0, 0), meta=META,
          sockets={"Prompt": ((0, -1.15, 0.4), 0.0)})
