"""Shop_Mirror — fogged restroom mirror (Mr. Usual clue spot: finger-written clue text).

Rounded chrome frame, a pale fogged Glass panel (role "mirror", front face takes the
SurfaceGui clue text), a small chrome shelf with a pink soap pump and two corner clips.
Wall-mounted: pivot = bottom-centre of the back face (+Y, touches the wall); hang the
pivot at about z = 4.6 above a sink.
Socket Clue = centre of the glass face.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H = 3.0, 3.9
SOAP = "#E58FB4"


def build():
    zc = 0.45 + H / 2
    frame = C.prism(C.rrect(W, H, 0.45, 4, 0, zc), "y", -0.14, 0.0)
    ns.boolean(frame, C.prism(C.rrect(W - 0.32, H - 0.32, 0.32, 4, 0, zc), "y", -1, 1))
    ns.bevel(frame, width=0.04, segments=2)
    backing = C.prism(C.rrect(W - 0.2, H - 0.2, 0.36, 4, 0, zc), "y", -0.05, 0.0)
    shelf = ns.box((2.4, 0.42, 0.08), loc=(0, -0.21, 0.32), bevel=0.03, segments=1)
    brackets = [ns.box((0.08, 0.36, 0.3), loc=(sx * 0.95, -0.18, 0.2), bevel=0.02, segments=1) for sx in (-1, 1)]
    pump = ns.cyl(0.035, 0.12, loc=(0.75, -0.21, 0.36 + 0.42 + 0.04), verts=6, bevel=0.0)  # seated on the bottle
    C.part([frame, backing, shelf, pump] + brackets, "Frame", C.CHROME, "Metal", smooth_angle=45)
    glass = C.prism(C.rrect(W - 0.3, H - 0.3, 0.32, 4, 0, zc), "y", -0.09, -0.05)
    ns.tag(glass, "Glass", "#C6D3D8", "Glass", recolor="mirror", cast_shadow=False)
    soap = ns.lathe([(0.0, 0.0), (0.14, 0.0), (0.15, 0.3), (0.1, 0.38), (0.04, 0.42), (0.0, 0.42)], verts=10,
                    loc=(0.75, -0.21, 0.36))
    ns.tag(soap, "Soap", SOAP, smooth_angle=60)


META = {"mount": "wall", "pivot": "bottom-centre of the back face (touches the wall)", "hang_height": 4.6,
        "surfaces": [{"part": "Glass", "face": "Front"}]}

if __name__ == "__main__":
    C.run(build, "Shop_Mirror", pivot=(0, 0, 0), meta=META,
          sockets={"Clue": ((0, -0.09, 0.45 + H / 2), 0.0)})
