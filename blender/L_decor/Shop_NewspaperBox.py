"""Shop_NewspaperBox — two coin-op newspaper boxes side by side on the sidewalk (outdoors).

Left box blue ("DAILY"), right box yellow ("NEWS"). Each: a box body on a dark steel
pedestal and base plate, a top cap with a rounded front edge, a coin unit on top (coin
slot + return button), a door with a darker frame and a glass window (part Glass, role
"glass", both windows) showing the front page (headline bar, photo, columns), a chrome
pull handle, and the paper's name across the lower front. Colours a step greyer for the
night street. Front faces -Y, pivot = bottom-centre. ~3.4 x 3.6 x 1.6.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
BW, BD = 1.6, 1.5            # one box: width, depth
BOXES = ((-0.86, "#2D5C9A", "#22487A", "DAILY", "#F4F1E8"), (0.86, "#E2B232", "#B98F22", "NEWS", "#24262B"))
Z_BODY = (0.62, 3.18)
Z_TOP = 3.42
FY = -BD / 2


def build():
    steel, glass, paper, ink, grey, chrome = [], [], [], [], [], []
    for x, col, frame_col, name, name_col in BOXES:
        z0, z1 = Z_BODY
        body = [ns.box((BW, BD, z1 - z0), loc=(x, 0, (z0 + z1) / 2), bevel=0.06, segments=1)]
        prof = C.fillet([(FY, z1 - 0.02), (BD / 2, z1 - 0.02), (BD / 2, Z_TOP), (FY, Z_TOP)], [0, 0, 0.1, 0.24], 2)
        top = C.prism(prof, "x", x - BW / 2 - 0.03, x + BW / 2 + 0.03)
        body.append(top)
        C.part(body, f"Box{name.title()}", col, smooth_angle=40)
        # door frame (ring) + window glass + front page
        wx0, wx1, wz0, wz1 = x - 0.62, x + 0.62, 1.78, 3.0
        outer = [(wx0 - 0.08, wz0 - 0.08), (wx1 + 0.08, wz0 - 0.08), (wx1 + 0.08, wz1 + 0.08), (wx0 - 0.08, wz1 + 0.08)]
        inner = [(wx0, wz0), (wx1, wz0), (wx1, wz1), (wx0, wz1)]
        frame = C.ring_slab(outer, inner, "y", FY - 0.08, FY + 0.01)
        C.part([frame], f"Frame{name.title()}", frame_col, smooth_angle=40)
        glass.append(ns.box((wx1 - wx0 + 0.04, 0.02, wz1 - wz0 + 0.04), loc=(x, FY - 0.06, (wz0 + wz1) / 2), bevel=0.0))
        py = FY - 0.01                       # the front page lies just in front of the body face, behind the glass
        paper.append(C.quad_xz(wx0 + 0.08, wx1 - 0.08, wz0 + 0.04, wz1 - 0.02, py))
        ink.append(C.quad_xz(wx0 + 0.14, wx1 - 0.14, wz1 - 0.24, wz1 - 0.1, py - 0.006))           # masthead
        ink.append(C.quad_xz(wx0 + 0.14, wx1 - 0.14, wz1 - 0.36, wz1 - 0.3, py - 0.006))           # headline
        grey.append(C.quad_xz(wx0 + 0.14, x - 0.02, wz0 + 0.3, wz1 - 0.46, py - 0.006))            # photo
        for k in range(4):
            zz = wz1 - 0.5 - k * 0.14
            grey.append(C.quad_xz(x + 0.06, wx1 - 0.14, zz - 0.035, zz, py - 0.006))               # columns
        # pull handle under the window
        chrome.append(C.pipe([(x - 0.3, FY - 0.02, wz0 - 0.2), (x - 0.3, FY - 0.13, wz0 - 0.24), (x + 0.3, FY - 0.13, wz0 - 0.24),
                              (x + 0.3, FY - 0.02, wz0 - 0.2)], 0.035, sides=5))
        # coin unit on top (front right) + slot + return button
        cx = x + 0.38
        steel.append(ns.box((0.5, 0.42, 0.3), loc=(cx, FY + 0.3, Z_TOP + 0.13), bevel=0.04, segments=1))
        ink.append(C.quad_xz(cx - 0.1, cx + 0.1, Z_TOP + 0.17, Z_TOP + 0.21, FY + 0.09 - 0.004))
        chrome.append(ns.cyl(0.05, 0.05, loc=(cx + 0.14, FY + 0.07, Z_TOP + 0.09), rot=(90, 0, 0), verts=6, bevel=0.0))
        # pedestal + base plate
        steel.append(ns.box((0.46, 0.46, z0 + 0.02), loc=(x, 0.05, (z0 + 0.02) / 2), bevel=0.0))
        steel.append(ns.box((1.0, 1.0, 0.06), loc=(x, 0.05, 0.03), bevel=0.0))
        # paper's name across the lower front
        nm = C.text(name, 0.3, 0.01, (x, FY - 0.008 + 0.005, 0.98), width=1.1, res=1, spacing=1.1, flat=True)
        C.part([nm], f"Name{name.title()}", name_col, smooth_angle=None)
    C.part(steel, "Steel", "#3A3D42", "Metal", smooth_angle=40)
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=50)
    C.part(paper, "Paper", "#E8E2D2", smooth_angle=None)
    C.part(ink, "Ink", C.INK, smooth_angle=None)
    C.part(grey, "Print", "#8D9097", smooth_angle=None)
    C.part(glass, "Glass", "#9DBFCB", "Glass", transparency=0.75, recolor="glass", cast_shadow=False, smooth_angle=None)


META = {"boxes": "left blue DAILY, right yellow NEWS", "glass": "part Glass (role glass) = both windows"}

if __name__ == "__main__":
    C.run(build, "Shop_NewspaperBox", budget=800, meta=META)
