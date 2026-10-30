"""World_Billboard — roadside billboard (~30 wide x 24 tall x 3 deep).

A 29 x 13 sheet-steel cabinet on two steel I-beam legs (concrete footings, X-brace
between them), a light frame round one flat dark glossy face (Screen, Glass, role
"screen": the game draws "STACKHOUSE · OPEN 24 HOURS · NEXT EXIT" on it), a grated
catwalk with a railing under the face on knee braces, and three gooseneck lamps reaching
over the top edge with lit lenses aimed at the face (LampLenses, Neon, role "lamp").
Back side: plain grey panel with two horizontal stringers.

Front = -Y. Pivot = ground level under the centre of the cabinet (origin).
Sockets: Panel = centre of the screen face, facing -Y (yaw 0); Lamp1..3 = lens centres
(left to right seen from the front) for SpotLights aimed at the face.
Exports as 4 MeshParts (Metal structure, Concrete footings, Screen, LampLenses), no
collision.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
CAB_X = 14.6                 # cabinet half width
CAB_Y = 0.4                  # cabinet half depth
CAB_Z = (10.0, 23.0)
SCR_W, SCR_H = 27.9, 11.9    # visible screen (frame opening)
SCR_ZC = 16.5
SCR_Y = -0.52                # screen face plane
LEG_X = 8.0
LEG_Y = 0.75
DECK_Z = 8.8
LAMP_X = (-9.5, 0.0, 9.5)
STEEL = "#4A4F55"
BRACE = "#565C62"
PANEL = "#7D838A"
FRAME = "#CFCAC0"
DECK = "#3F444A"
LENS = "#FFF1D6"


def lamp_geometry(x):
    """Gooseneck pipe points, head centre and the unit vector the head aims along."""
    pts = [(x, -0.15, CAB_Z[1] - 0.3), (x, -0.15, CAB_Z[1] + 0.55), (x, -0.85, CAB_Z[1] + 1.05),
           (x, -1.7, CAB_Z[1] + 1.05), (x, -2.05, CAB_Z[1] + 0.72)]
    head = Vector((x, -2.2, CAB_Z[1] + 0.48))
    aim = (Vector((x * 0.85, SCR_Y, SCR_ZC + 1.0)) - head).normalized()
    return pts, head, aim


def build():
    steel, concrete = [], []
    # legs + footings
    for sx in (-1, 1):
        steel.append(C.ibeam(sx * LEG_X, LEG_Y, 0.45, CAB_Z[1] - 0.05, w=0.9, d=0.8, tf=0.15, tw=0.14))
        concrete.append(C.box((1.7, 1.5, 0.55), loc=(sx * LEG_X, LEG_Y, 0.25), bevel=0.06))
    # X-brace between the legs (through the webs) + a low tie
    steel.append(C.beam((-LEG_X, LEG_Y, 1.6), (LEG_X, LEG_Y, DECK_Z - 0.4), 0.32, 0.1))
    steel.append(C.beam((LEG_X, LEG_Y, 1.6), (-LEG_X, LEG_Y, DECK_Z - 0.4), 0.32, 0.1))
    # cabinet (plain grey back / sides) + light frame round the face
    cab = C.box((2 * CAB_X, 2 * CAB_Y, CAB_Z[1] - CAB_Z[0]), loc=(0, 0, sum(CAB_Z) / 2), bevel=0.06)
    frame = C.ring_slab(C.rrect(SCR_W + 1.5, SCR_H + 1.5, 0.3, 1, 0, SCR_ZC), C.rrect(SCR_W, SCR_H, 0.12, 1, 0, SCR_ZC),
                        "y", SCR_Y - 0.12, -CAB_Y + 0.04)
    # back stringers (pass through the legs)
    stringers = [C.box((2 * CAB_X - 0.4, 0.4, 0.5), loc=(0, CAB_Y + 0.18, z), bevel=0.0) for z in (12.4, 20.6)]
    # catwalk: deck, front stiffener, knee braces, railing
    deck = C.box((2 * CAB_X - 0.6, 2.1, 0.15), loc=(0, -0.65, DECK_Z + 0.075), bevel=0.0)
    stiff = C.box((2 * CAB_X - 0.6, 0.2, 0.25), loc=(0, -1.6, DECK_Z - 0.12), bevel=0.0)
    knees = [C.beam((sx * LEG_X, LEG_Y - 0.35, DECK_Z - 2.6), (sx * LEG_X, -1.55, DECK_Z - 0.05), 0.25, 0.12)
             for sx in (-1, 1)]
    rail = []
    n_posts = 6
    for k in range(n_posts):
        x = -CAB_X + 0.45 + (2 * CAB_X - 0.9) * k / (n_posts - 1)
        rail.append(C.rod((x, -1.62, DECK_Z + 0.1), (x, -1.62, DECK_Z + 1.12), 0.06, verts=4))
    for z in (DECK_Z + 0.6, DECK_Z + 1.1):
        rail.append(C.rod((-CAB_X + 0.4, -1.62, z), (CAB_X - 0.4, -1.62, z), 0.06, verts=4))
    # gooseneck lamps
    arms, lenses = [], []
    for x in LAMP_X:
        pts, head, aim = lamp_geometry(x)
        arms.append(C.pipe(pts, 0.1, sides=4, corner=0.35, corner_segs=2))
        arms.append(C.rod(head - aim * 0.35, head + aim * 0.25, 0.42, verts=6, r_top=0.36))
        lens = C.disc(0.33, verts=6)
        lens.rotation_euler = aim.to_track_quat("Z", "Y").to_euler()
        lens.location = head + aim * 0.27
        lenses.append(lens)

    C.part(steel + stringers + knees + [stiff] + arms, "Steel", STEEL, "Metal", smooth_angle=None)
    C.part(rail, "Railing", BRACE, "Metal", smooth_angle=None)
    C.part([deck], "Deck", DECK, "Metal", smooth_angle=None)
    C.part([cab], "Cabinet", PANEL, "Metal", smooth_angle=None)
    C.part([frame], "Frame", FRAME, "Metal", smooth_angle=None)
    C.part(concrete, "Footings", C.CONCRETE, "Concrete", smooth_angle=None)

    scr = C.box((SCR_W + 0.3, 0.24, SCR_H + 0.3), loc=(0, SCR_Y + 0.12, SCR_ZC), bevel=0.0)
    ns.tag(scr, "Screen", C.SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=None)
    ns.tag(C.merge(lenses, "LampLenses"), "LampLenses", LENS, "Neon", recolor="lamp", cast_shadow=False,
           smooth_angle=None)


def sockets():
    out = {"Panel": ((0.0, SCR_Y, SCR_ZC), 0.0)}
    for i, x in enumerate(LAMP_X):
        _, head, aim = lamp_geometry(x)
        p = head + aim * 0.27
        out[f"Lamp{i + 1}"] = ((p.x, p.y, p.z), 180.0)   # the lamps look back at the face (+Y)
    return out


META = {"kind": "billboard", "pivot": "ground level under the cabinet centre",
        "screen_size": [SCR_W, SCR_H], "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H)],
        "roles": {"screen": "Screen", "lamp": "LampLenses"},
        "light_hint": {"type": "SpotLight", "at": "Socket_Lamp1..3", "aim": "down and back at the face",
                       "color": LENS, "range": 18, "angle": 70, "brightness": 2}}

if __name__ == "__main__":
    C.run(build, "World_Billboard", sockets=sockets(), meta=META)
