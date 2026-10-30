"""Shop_PosterA — framed retro ad poster: "TRY THE NIGHT OWL!" (3 x 4 x 0.15).

Chrome frame round a cream paper print: navy header band with cream "TRY THE", big
red-orange "NIGHT OWL!", a mustard starburst behind a modelled stacked sandwich (golden
domed bun with owl eyes, ear tufts and a beak, lettuce wave, tomato, cheese drip) standing
out in relief, and a navy "ONLY AT STACKHOUSE" strap line.
Wall-mounted: pivot = bottom-centre of the back face (+Y, flat on the wall).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 3.0, 4.0, 0.15
OWL_EYE = "#FBF7EC"
PUPIL = "#1A1C22"
BEAK = "#F08A24"


def build():
    fr, pa, pf, (cx, cz), (pw, ph) = C.poster_frame(W, H, D, paper_inset=0.12)   # relief stays inside the frame
    C.part([fr], "Frame", C.CHROME, "Metal", smooth_angle=45)
    C.part([pa], "Paper", C.PAPER, smooth_angle=None)

    top = cz + ph / 2
    band = ns.box((pw, 0.01, 0.62), loc=(0, pf - 0.005, top - 0.31), bevel=0.0)
    C.part([band], "Band", C.NAVY, smooth_angle=None)
    t1 = C.text("TRY THE", 0.36, 0.02, (0, pf - 0.01, top - 0.31), width=1.5, res=1, spacing=1.15, flat=True)
    C.part([t1], "BandText", C.CREAM, smooth_angle=None)
    t2 = C.text("NIGHT OWL!", 0.6, 0.02, (0, pf - 0.005, top - 0.98), width=pw - 0.24, res=1, flat=True)
    C.part([t2], "Title", C.BRAND, smooth_angle=None)
    t3 = C.text("ONLY AT STACKHOUSE", 0.2, 0.02, (0, pf - 0.005, cz - ph / 2 + 0.22), width=2.0, res=1, spacing=1.1,
                flat=True)
    C.part([t3], "Strap", C.NAVY_DEEP, smooth_angle=None)

    # starburst + the owl sandwich in relief
    sz = cz - 0.42
    burst = C.prism(C.burst(1.18, 0.88, 0, sz, n=14, a0=90 + 360 / 28), "y", pf - 0.012, pf + 0.001)
    C.part([burst], "Burst", C.MUSTARD, smooth_angle=None)
    s = 0.78
    icon = C.sandwich_icon(s=s, depth=0.07)
    C.place(icon, (0, pf - 0.012, sz))
    C.part(icon[C.BUN], "Bun", C.BUN, smooth_angle=40)
    C.part(icon[C.LETTUCE], "Lettuce", C.LETTUCE, smooth_angle=40)
    C.part(icon[C.TOMATO], "Tomato", C.TOMATO, smooth_angle=40)
    C.part(icon[C.CHEESE], "Cheese", C.CHEESE, smooth_angle=40)
    # owl face on the top bun: eyes (white + pupils), beak, ear tufts
    fy = pf - 0.012 - 0.07            # bun front face
    ez = sz + 0.68 * s
    eyes, pupils = [], []
    for sx in (-1, 1):
        e = C.disc(0.2, verts=12)
        C.place(e, (sx * 0.27, fy - 0.012, ez), pitch=90)
        eyes.append(e)
        p = C.disc(0.1, verts=8)
        C.place(p, (sx * 0.24, fy - 0.024, ez - 0.02), pitch=90)
        pupils.append(p)
    beak = C.prism([(-0.08, ez - 0.12), (0.08, ez - 0.12), (0.0, ez - 0.27)], "y", fy - 0.022, fy + 0.01)
    tufts = []
    for sx in (-1, 1):
        x0 = sx * 0.45
        tufts.append(C.prism([(x0 - 0.13, sz + 0.86 * s), (x0 + 0.13, sz + 0.86 * s), (x0 + sx * 0.2, sz + 1.2 * s)],
                             "y", pf - 0.075, pf - 0.012))
    C.part(eyes, "OwlEyes", OWL_EYE, smooth_angle=None)
    C.part(pupils, "OwlPupils", PUPIL, smooth_angle=None)
    C.part([beak], "OwlBeak", BEAK, smooth_angle=None)
    C.part(tufts, "OwlTufts", C.BUN_DARK, smooth_angle=None)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (flat on the wall)", "hang_height": 4.5}

if __name__ == "__main__":
    C.run(build, "Shop_PosterA", pivot=(0, 0, 0), meta=META,
          preview=lambda *a: C.front_preview(*a, backdrop=C.NAVY))
