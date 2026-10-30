"""Shop_PosterB — framed vintage photo print: "STACKHOUSE — SINCE 1987" (3 x 4 x 0.15).

Dark walnut frame round a cream mat. On the mat: "STACKHOUSE" above and "SINCE 1987" (with
rule dashes) below a sepia "photograph" held by dark photo corners: a streamline diner
silhouette with a rounded end, a roof sign band and a row of lit windows, a glowing door,
an "EAT" pole sign, a low sun and the ground line, all in three or four sepia tones.
Wall-mounted: pivot = bottom-centre of the back face (+Y, flat on the wall).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 3.0, 4.0, 0.15
SKY = "#D8BE90"
SUN = "#E9D3A3"
GROUND = "#A8855A"
BUILDING = "#6B4F33"
LIT = "#F0DCAE"
INK = "#5B4330"
CORNER = "#3A2A1E"
PH_W, PH_H = 2.2, 2.3            # photo size


def build():
    fr, pa, pf, (cx, cz), (pw, ph) = C.poster_frame(W, H, D, border=0.2, radius=0.06, paper_inset=0.1)
    C.part([fr], "Frame", C.WOOD_DARK, "Wood", smooth_angle=45)
    C.part([pa], "Mat", C.CREAM, smooth_angle=None)

    pz = cz + 0.02                     # photo centre
    py = pf - 0.012                    # photo front face
    photo = ns.box((PH_W, 0.012, PH_H), loc=(0, pf - 0.006, pz), bevel=0.0)
    C.part([photo], "PhotoSky", SKY, smooth_angle=None)
    x0, x1, z0, z1 = -PH_W / 2, PH_W / 2, pz - PH_H / 2, pz + PH_H / 2
    gz = z0 + 0.42                     # ground line
    ground = ns.box((PH_W, 0.006, gz - z0), loc=(0, py - 0.003, (z0 + gz) / 2), bevel=0.0)
    C.part([ground], "PhotoGround", GROUND, smooth_angle=None)
    sun = C.disc(0.42, verts=16)
    C.place(sun, (0.48, py - 0.008, gz + 0.95), pitch=90)
    C.part([sun], "PhotoSun", SUN, smooth_angle=None)

    # diner silhouette (dark), its lit windows / door / sign band (light)
    by = py - 0.018                    # silhouette front
    body = C.prism(C.fillet([(-0.86, gz), (0.92, gz), (0.92, gz + 0.62), (-0.86, gz + 0.62)], [0, 0.3, 0.3, 0], 4),
                   "y", by, py - 0.002)
    roof = C.prism(C.fillet([(-0.9, gz + 0.62), (0.96, gz + 0.62), (0.96, gz + 0.7), (-0.9, gz + 0.7)],
                            [0, 0.04, 0.04, 0], 1), "y", by - 0.004, py - 0.002)
    tower = C.prism(C.fillet([(-0.35, gz + 0.7), (0.35, gz + 0.7), (0.35, gz + 0.98), (-0.35, gz + 0.98)],
                             [0, 0, 0.06, 0.06], 1), "y", by, py - 0.002)
    pole = ns.box((0.05, 0.01, 1.05), loc=(-0.98, by + 0.005, gz + 0.52), bevel=0.0)
    sign = C.prism(C.rrect(0.46, 0.3, 0.07, 2, -0.98, gz + 1.15), "y", by, py - 0.002)
    C.part([body, roof, tower, pole, sign], "PhotoDiner", BUILDING, smooth_angle=None)
    lit = []
    for k in range(6):
        x = -0.72 + k * 0.24
        if abs(x - 0.0) < 0.05:
            continue
        lit.append(ns.box((0.17, 0.006, 0.2), loc=(x, by - 0.008, gz + 0.36), bevel=0.0))
    lit.append(ns.box((0.16, 0.006, 0.36), loc=(0.0, by - 0.008, gz + 0.18), bevel=0.0))     # door
    lit.append(ns.box((0.6, 0.006, 0.12), loc=(0.0, by - 0.008, gz + 0.84), bevel=0.0))      # sign band
    eat = C.text("EAT", 0.14, 0.016, (-0.98, by, gz + 1.15), width=0.32, res=1, flat=True)
    lit.append(eat)
    C.part(lit, "PhotoLit", LIT, smooth_angle=None)

    # photo corners
    corners = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            cxp, czp = sx * PH_W / 2, pz + sz * PH_H / 2
            tri = [(cxp + sx * 0.04, czp + sz * 0.04), (cxp - sx * 0.3, czp + sz * 0.04), (cxp + sx * 0.04, czp - sz * 0.3)]
            corners.append(C.prism(tri, "y", py - 0.026, pf + 0.001))
    C.part(corners, "PhotoCorners", CORNER, smooth_angle=None)

    # mat lettering
    t1 = C.text("STACKHOUSE", 0.34, 0.02, (0, pf - 0.01, z1 + 0.32), width=2.25, res=1, spacing=1.08, flat=True)
    t2 = C.text("SINCE 1987", 0.24, 0.02, (0, pf - 0.01, z0 - 0.3), width=1.35, res=1, spacing=1.1, flat=True,
                font=C.FONT_BOLD_ITALIC)
    dashes = [ns.box((0.32, 0.01, 0.035), loc=(sx * 0.95, pf - 0.005, z0 - 0.3), bevel=0.0) for sx in (-1, 1)]
    C.part([t1, t2] + dashes, "MatText", INK, smooth_angle=None)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (flat on the wall)", "hang_height": 4.5}

if __name__ == "__main__":
    C.run(build, "Shop_PosterB", pivot=(0, 0, 0), meta=META,
          preview=lambda *a: C.front_preview(*a, backdrop=C.NAVY))
