"""Shop_Drain — alley floor drain where the Nibblers come from: a 3 x 3 cast-iron frame with a
slightly raised rim, a slotted grate, a black void below the slots and a dark wet stain
around it. Sits ON the alley floor (z = 0 = floor top).
Socket Emerge = centre of the grate, top surface (Nibbler spawn point; glowing-eyes tell).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
S = 3.0
IRON = "#34373B"


def build():
    rim = C.ring_slab(C.rrect(S, S, 0.25, 2), C.rrect(S - 0.5, S - 0.5, 0.1, 2), "z", 0.0, 0.16)
    ns.bevel(rim, width=0.04, segments=1)
    bars = []
    n = 8
    inner = S - 0.5
    for i in range(n):
        x = -inner / 2 + inner * (i + 0.5) / n
        bars.append(ns.box((0.16, inner + 0.02, 0.1), loc=(x, 0, 0.07), bevel=0.02, segments=1))
    bars.append(ns.box((inner, 0.2, 0.08), loc=(0, 0, 0.05), bevel=0.02, segments=1))
    C.part([rim] + bars, "Grate", IRON, "Metal", smooth_angle=40)
    void = ns.box((inner, inner, 0.02), loc=(0, 0, 0.012), bevel=0.0)
    ns.tag(void, "Void", "#050506", cast_shadow=False)
    stain = C.prism(C.fillet([(-2.3, -2.0), (2.1, -2.4), (2.5, 1.8), (-1.9, 2.3)], 0.9, 3), "z", 0.0, 0.01)
    ns.tag(stain, "Stain", "#1E2124", "Slate", cast_shadow=False)


META = {"size": [5.0, 0.16, 4.8], "sits_on": "alley floor top", "spawn": "Socket_Emerge"}

if __name__ == "__main__":
    C.run(build, "Shop_Drain", meta=META, pivot=(0, 0, 0), sockets={"Emerge": ((0, 0, 0.16), 0.0)})
