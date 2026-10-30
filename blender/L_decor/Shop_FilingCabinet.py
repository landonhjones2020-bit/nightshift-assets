"""Shop_FilingCabinet — 4-drawer steel filing cabinet for the manager's office.

Grey-green painted steel body on a dark recessed plinth, four drawer fronts (a shade
lighter than the body so the gaps read) with chrome U-pulls and chrome label holders with
paper cards. The second drawer from the top is pulled out ~0.7: its side walls show and a
row of manila / coloured hanging folders with staggered tabs stands inside.
Body + drawer fronts collide. Front faces -Y, pivot = bottom-centre. 1.6 x 4.4 x 2.2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, H, D = 1.6, 4.4, 2.2
BODY = "#6E7A74"
FRONT = "#8A968F"
MANILA = "#E3C98F"
PLINTH = 0.16
DRAWERS = [(PLINTH + 0.06 + i * 1.03, PLINTH + 0.06 + i * 1.03 + 0.98) for i in range(4)]   # (z0, z1) bottom up
OPEN = 2              # index of the open drawer (2 = second from the top)
PULL = 0.72


def build():
    fy = -D / 2
    body = ns.box((W, D, H - PLINTH), loc=(0, 0, PLINTH + (H - PLINTH) / 2), bevel=0.05, segments=1)
    plinth = ns.box((W - 0.12, D - 0.12, PLINTH + 0.02), loc=(0, 0.02, (PLINTH + 0.02) / 2), bevel=0.0)
    C.part([body], "Body", BODY, can_collide=True, smooth_angle=35)
    C.part([plinth], "Plinth", C.BASE_DARK, can_collide=True, smooth_angle=35)

    fronts, chrome, cards, sides, folders, tabs = [], [], [], [], [], {}
    for i, (z0, z1) in enumerate(DRAWERS):
        dy = -PULL if i == OPEN else 0.0
        zc = (z0 + z1) / 2
        y0 = fy + dy
        fronts.append(ns.box((W - 0.12, 0.08, z1 - z0), loc=(0, y0 - 0.04, zc), bevel=0.035, segments=1))
        # U-pull below the label holder
        hy = y0 - 0.08
        chrome.append(C.pipe([(-0.3, hy, zc - 0.02), (-0.3, hy - 0.13, zc - 0.06), (0.3, hy - 0.13, zc - 0.06),
                              (0.3, hy, zc - 0.02)], 0.035, sides=6))
        # label holder frame + card
        chrome.append(ns.box((0.5, 0.03, 0.22), loc=(0, hy - 0.005, zc + 0.27), bevel=0.0))
        cards.append(C.quad_xz(-0.21, 0.21, zc + 0.185, zc + 0.355, hy - 0.025))
        if i == OPEN:
            # drawer side walls running back into the body + dark cavity on the body face
            for sx in (-1, 1):
                sides.append(ns.box((0.04, PULL + 0.05, 0.7), loc=(sx * (W / 2 - 0.12), fy - PULL / 2 + 0.02, z0 + 0.38),
                                    bevel=0.0))
            sides.append(ns.box((W - 0.24, PULL + 0.05, 0.04), loc=(0, fy - PULL / 2 + 0.02, z0 + 0.05), bevel=0.0))
            # hanging folders standing across the drawer, staggered tabs
            cols = [MANILA, "#C9584C", MANILA, "#4E7FB8", MANILA, "#6E9E62", MANILA]
            n = len(cols)
            for k in range(n):
                yk = y0 + 0.12 + k * (PULL - 0.12) / (n - 1) * 0.95
                hk = 0.62 + 0.04 * ((k * 37) % 3)
                folders.append(ns.box((W - 0.34, 0.022, hk), loc=(0, yk, z0 + 0.08 + hk / 2), rot=(-6 + 3 * (k % 3), 0, 0),
                                      bevel=0.0))
                tx = (-0.42, 0.05, 0.4, -0.18, 0.25, -0.38, 0.12)[k]
                tabs.setdefault(cols[k], []).append(
                    ns.box((0.3, 0.024, 0.13), loc=(tx, yk, z0 + 0.08 + hk + 0.05), rot=(-6 + 3 * (k % 3), 0, 0), bevel=0.0))
    # dark cavity where the open drawer came out (on the body face, around the drawer box)
    z0, z1 = DRAWERS[OPEN]
    cavity = C.quad_xz(-W / 2 + 0.06, W / 2 - 0.06, z0, z1, fy - 0.004)
    C.part(fronts, "Fronts", FRONT, can_collide=True, smooth_angle=35)
    C.part(chrome, "Chrome", C.CHROME, "Metal", smooth_angle=50)
    C.part(cards, "Cards", C.PAPER, smooth_angle=None)
    C.part(sides, "DrawerBox", BODY, smooth_angle=35)
    C.part([cavity], "Cavity", C.DARK_VOID, smooth_angle=None)
    C.part(folders, "Folders", MANILA, smooth_angle=None)
    for col, objs in tabs.items():
        C.part(objs, "Tabs" + col.lstrip("#"), col, smooth_angle=None)


META = {"open_drawer": "second from the top, pulled 0.72 toward -Y"}

if __name__ == "__main__":
    C.run(build, "Shop_FilingCabinet", budget=700, meta=META)
