"""Basement_ChestFreezer — an old dingy-white chest freezer, a hiding spot.

Rounded body built as a hollow tub (outer shell, rim, inner liner, floor: the interior is
real, so it looks right with the lid open or the camera inside), a dark kick plinth, a
faded red-orange stripe wrapping the front and sides, a chrome badge, a key lock, side vent
slots, two hinges at the back, a dark gasket ring on the rim, rust spots and a rust run
under the lock. The closed lid (part Lid, role "lid", with its pull handle) is its own part so the
game can open it: hinge line along the back top edge, rotate about lid_axis by
lid_open_deg (Roblox model space, see META).
Sockets: Hide = interior centre (yaw 0 = facing out, -Y), HideExit = on the floor 2.5 in
front of the front face. Body and lid collide.
Front faces -Y, PIVOT = bottom-centre of the body. 4 x 3 x 2.2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D = 4.0, 2.2
Z_BODY0, Z_RIM = 0.16, 2.6          # body bottom / rim top
WALL = 0.16
Z_FLOOR = 0.42                      # interior floor
LID_T = 0.4                         # gasket + lid shell (top at 3.0)
GASKET = 0.06
RAD = 0.2
WHITE = C.CREAM
LINER = "#D8D2C2"
CHROME = "#B9BEC2"
PLINTH = "#2B2D31"


def ring(w, d, r, z):
    return C.ring3(C.rrect(w, d, r, 3), z)


def build():
    # ---- hollow tub: outer wall (rounded top edge), rim, inner liner, floor ---------------
    tub = C.loft([ring(W, D, RAD, Z_BODY0), ring(W, D, RAD, Z_RIM - 0.06), ring(W - 0.04, D - 0.04, RAD - 0.02, Z_RIM),
                  ring(W - 2 * WALL, D - 2 * WALL, RAD - WALL * 0.6, Z_RIM),
                  ring(W - 2 * WALL, D - 2 * WALL, RAD - WALL * 0.6, Z_FLOOR)], cap0=True, cap1=True)
    C.part([tub], "Body", WHITE, can_collide=True, smooth_angle=40)
    plinth = C.prism(C.rrect(W - 0.24, D - 0.24, RAD - 0.1, 3), "z", 0.0, Z_BODY0 + 0.02)
    C.part([plinth], "Plinth", PLINTH, can_collide=True, smooth_angle=40)

    # dark rubber gasket ring on the rim (stays with the body when the lid opens)
    gasket = C.ring_slab(C.rrect(W - 0.05, D - 0.05, RAD - 0.03, 3), C.rrect(W - 2 * WALL + 0.03, D - 2 * WALL + 0.03,
                                                                            RAD - WALL * 0.6, 3), "z", Z_RIM, Z_RIM + GASKET)
    C.part([gasket], "Gasket", PLINTH, smooth_angle=40)

    # ---- lid (own part, role "lid"): domed-edge shell + chrome-look pull handle ------------
    shell = C.loft([ring(W + 0.04, D + 0.04, RAD + 0.02, Z_RIM + GASKET), ring(W + 0.04, D + 0.04, RAD + 0.02, Z_RIM + LID_T - 0.1),
                    ring(W - 0.06, D - 0.06, RAD - 0.03, Z_RIM + LID_T)], cap0=True, cap1=True)
    hy = -D / 2 - 0.02
    hz = Z_RIM + GASKET + 0.15
    grip = [C.rod((x, hy + 0.01, hz), (x, hy - 0.14, hz), 0.035, verts=6) for x in (-0.45, 0.45)]
    grip.append(C.rod((-0.5, hy - 0.14, hz), (0.5, hy - 0.14, hz), 0.05, verts=8))
    C.part([shell] + grip, "Lid", WHITE, recolor="lid", can_collide=True, smooth_angle=40)

    # ---- stripe, badge, lock, vents, hinges -----------------------------------------------
    outline = C.rrect(W, D, RAD, 3)
    n = len(outline)
    # front and sides only: the back run would sit against the wall
    stripe = C.outline_band(outline, 1.86, 2.08, proud=0.01,
                            skip=lambda i: (outline[i][1] + outline[(i + 1) % n][1]) / 2 > D / 2 - 0.05)
    C.part([stripe], "Stripe", C.BRAND, smooth_angle=None)
    fy = -D / 2
    badge = ns.box((0.6, 0.03, 0.16), loc=(-1.25, fy - 0.006, 2.32), bevel=0.0)
    lock = [ns.cyl(0.09, 0.08, loc=(0.9, fy - 0.03, 2.33), rot=(90, 0, 0), verts=8, bevel=0.0)]
    hinges = [ns.box((0.34, 0.12, 0.26), loc=(x, D / 2 + 0.05, Z_RIM + 0.02), bevel=0.03, segments=1) for x in (-1.2, 1.2)]
    C.part([badge] + lock + hinges, "Chrome", CHROME, "Metal", smooth_angle=40)
    keyhole = C.face_dir(C.quad_xz(0.885, 0.915, 2.29, 2.37, fy - 0.078), "-Y")
    vents = [C.face_dir(C.poly([(W / 2 + 0.008, y, z0), (W / 2 + 0.008, y + 0.9, z0), (W / 2 + 0.008, y + 0.9, z0 + 0.06),
                                (W / 2 + 0.008, y, z0 + 0.06)]), "+X") for y, z0 in ((-0.45, 0.4), (-0.45, 0.55), (-0.45, 0.7))]
    C.part([keyhole] + vents, "Dark", C.DARK_VOID, smooth_angle=None)

    # ---- rust: spots on the front and sides, a run under the lock ---------------------------
    rust = []
    for k, (x, z, r) in enumerate(((-1.5, 0.42, 0.26), (-1.05, 0.3, 0.12), (1.5, 0.5, 0.22), (0.3, 0.32, 0.13),
                                   (-0.6, 1.6, 0.1), (1.6, 1.3, 0.12))):
        b = C.blob(0, 0, r, 0, seed=k)
        C.place([b], loc=(x, fy - 0.008, z))
        rust.append(b)
    for k, (y, z, r) in enumerate(((0.7, 0.42, 0.18), (-0.2, 1.1, 0.1))):
        b = C.blob(0, 0, r, 0, seed=10 + k)
        C.place([b], loc=(W / 2 + 0.008, y, z), yaw=90)
        rust.append(b)
    rust.append(C.streak_flat(0.9, 1.84, 0.5, 0.1, fy, seed=3))     # rust run below the lock, under the stripe
    C.part(rust, "Rust", C.RUST, smooth_angle=None)

    pivot = (0.0, 0.0, 0.0)
    hinge = (0.0, D / 2 + 0.02, Z_RIM)
    sockets = {"Hide": ((0.0, 0.0, (Z_FLOOR + Z_RIM) / 2), 0.0), "HideExit": ((0.0, fy - 2.5, 0.0), 0.0)}
    meta = {"hide_spots": ["Hide"], "hide_exit": "HideExit", "interior_floor": Z_FLOOR,
            "interior_size": [round(W - 2 * WALL, 2), round(Z_RIM - Z_FLOOR, 2), round(D - 2 * WALL, 2)],
            "lid_part": "Lid", "lid_hinge": C.rbx(hinge, pivot), "lid_axis": C.rbx_dir((-1, 0, 0)), "lid_open_deg": 75,
            "collide": "body, plinth and lid (Lid stays its own part)"}
    return {"export": {"sockets": sockets, "meta": meta, "pivot": pivot}}


if __name__ == "__main__":
    C.run(build, "Basement_ChestFreezer", budget=2000, socket_views=((-35, 28), (35, 50)))
