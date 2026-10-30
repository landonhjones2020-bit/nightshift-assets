"""World_SkylineA — distant town cluster (~110 wide x 60 tall x 30 deep).

Eight boxy blue-grey buildings (#2A3142..#3A4152) in two rows of different heights, two
with setback crowns, dark roof cornices, rooftop water tanks, AC boxes, a bulkhead and
antennas; the tallest carries a lattice-look mast with a red aircraft light
(AircraftLight, Neon, role "lamp"). Facades carry rows of dark unlit windows (punched or
ribbon) and a few sparse warm lit patches (Windows, Neon #FFD99A, role "lamp"), so it
reads as a town at night. Windows hidden behind the front row are not built.
Very low detail; meant for 200-600 studs away. Front = -Y. Pivot = ground level, centre
of the footprint. Exports as 3 MeshParts (buildings, Windows, AircraftLight).
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
WIN_DARK = "#1B2130"

# (x, y, w, d, h, colour index, window kind, front lit patches)
FRONT = [
    (-47.0, -6.5, 14.0, 12.0, 20.0, 3, "punched", [(2, 2, 1, 3), (4, 4, 0, 0)]),
    (-22.0, -6.5, 16.0, 12.0, 27.0, 1, "ribbon", [(3, 3, 0, 2), (5, 5, 3, 4)]),
    (8.0, -6.5, 12.0, 12.0, 32.0, 2, "punched", [(1, 1, 0, 1), (6, 7, 2, 3)]),
    (34.0, -6.5, 14.0, 12.0, 24.0, 3, "ribbon", [(4, 4, 2, 4)]),
    (50.0, -5.5, 10.0, 10.0, 15.0, 0, "punched", [(1, 1, 1, 1)]),
]
BACK = [
    (-35.0, 7.0, 12.0, 14.0, 36.0, 0, "punched", [(6, 6, 1, 2), (8, 8, 2, 3)]),
    (-6.0, 7.0, 14.0, 16.0, 50.0, 0, "punched", [(10, 11, 1, 2), (5, 5, 3, 3)]),
    (22.0, 7.0, 16.0, 14.0, 41.0, 1, "ribbon", [(8, 8, 1, 3), (3, 3, 4, 5)]),
]


def occluded_by_front(x, z, w):
    for fx, fy, fw, fd, fh, *_ in FRONT:
        if fx - fw / 2 - 0.2 <= x - w / 2 and x + w / 2 <= fx + fw / 2 + 0.2 and z < fh + 0.4:
            return True
    return False


class FilteredQuads(C.QuadSet):
    """QuadSet that skips -Y quads hidden behind the front row (for back-row facades)."""

    def add(self, centre, w, h, facing):
        if facing == "-Y" and occluded_by_front(centre[0], centre[2] + h / 2, w):
            return
        super().add(centre, w, h, facing)


def build():
    rnd = random.Random(5)
    walls = {i: [] for i in range(4)}
    roof = []
    dark_q, lit_q = C.QuadSet(), C.QuadSet()
    dark_b, lit_b = FilteredQuads(), FilteredQuads()

    def block(x, y, w, d, h, ci, z0=0.0):
        b = C.box((w, d, h), loc=(x, y, z0 + h / 2))
        if z0 <= 0.0:
            C.no_bottom(b)
        walls[ci].append(b)
        roof.append(C.box((w + 0.5, d + 0.5, 0.5), loc=(x, y, z0 + h + 0.1)))

    for x, y, w, d, h, ci, kind, lit in FRONT:
        block(x, y, w, d, h, ci)
        C.facade(dark_q, lit_q, rnd, x - w / 2, x + w / 2, 2.0, h - 1.0, y - d / 2, "-Y", kind=kind, lit_patches=lit,
                 lit_extra=0.02)
    for x, y, w, d, h, ci, kind, lit in BACK:
        block(x, y, w, d, h, ci)
        C.facade(dark_b, lit_b, rnd, x - w / 2, x + w / 2, 2.0, h - 1.0, y - d / 2, "-Y", kind=kind, lit_patches=lit,
                 lit_extra=0.02)

    # setback crowns
    block(-35.0, 8.0, 8.0, 9.0, 5.0, 1, z0=36.3)
    block(-6.0, 7.5, 9.0, 10.0, 5.0, 1, z0=50.3)
    # side windows: outer ends of the cluster + the tall towers above their neighbours
    C.facade(dark_q, lit_q, rnd, -12.5, -0.5, 2.0, 19.0, -54.0, "-X", lit_patches=[(1, 1, 1, 2)])
    C.facade(dark_q, lit_q, rnd, -10.5, -0.5, 2.0, 14.0, 55.0, "+X", lit_patches=[(0, 0, 0, 1)])
    C.facade(dark_q, lit_q, rnd, 0.0, 14.0, 21.0, 35.0, -41.0, "-X", lit_patches=[(2, 2, 2, 3)])
    C.facade(dark_q, lit_q, rnd, -1.0, 15.0, 33.0, 49.0, -13.0, "-X", lit_patches=[(1, 1, 0, 1)])
    C.facade(dark_q, lit_q, rnd, -1.0, 15.0, 33.0, 49.0, 1.0, "+X", lit_patches=[(3, 3, 3, 4)])
    C.facade(dark_q, lit_q, rnd, 0.0, 14.0, 33.0, 40.0, 30.0, "+X", lit_patches=[(0, 0, 1, 2)])

    # rooftop stuff
    def tank(x, y, z, r=1.5, h=2.4):
        roof.append(C.box((r * 1.7, r * 1.7, 1.2), loc=(x, y, z + 0.6)))
        t = C.lathe([(r, z + 1.2), (r, z + 1.2 + h), (r * 1.08, z + 1.3 + h), (0.0, z + 2.2 + h)], verts=8)
        roof.append(t)

    # everything on a roof stands on roof + 0.3 (the cornice cap's top is roof + 0.35)
    tank(-50.0, -8.0, 20.3)
    tank(10.5, -4.0, 32.3, r=1.3, h=2.0)
    roof.append(C.box((3.0, 2.2, 1.4), loc=(-26.0, -8.0, 27.3 + 0.7)))
    roof.append(C.box((2.4, 2.0, 1.2), loc=(-18.0, -4.5, 27.3 + 0.6)))
    roof.append(C.box((4.0, 3.5, 2.6), loc=(37.0, -4.0, 24.3 + 1.3)))
    roof.append(C.box((5.0, 4.0, 3.0), loc=(18.0, 10.0, 41.3 + 1.5)))
    for x, y, hh in ((26.0, 4.5, 6.0), (27.5, 9.0, 4.0), (5.0, -9.5, 4.5)):
        z0 = 41.3 if x > 20 else 32.3
        roof.append(C.rod((x, y, z0), (x, y, z0 + hh), 0.12, verts=4))
    # mast on the tallest tower (its setback crown's cap top is at 55.65)
    mast_base = 55.6
    roof.append(C.box((2.2, 2.2, 1.0), loc=(-6.0, 7.5, mast_base + 0.5)))
    roof.append(C.rod((-6.0, 7.5, mast_base + 1.0), (-6.0, 7.5, 59.0), 0.45, verts=4, r_top=0.14))
    # oversized beacon so it still registers from 400+ studs
    light = C.bipyramid(0.55, 0.55, (-6.0, 7.5, 59.42), sides=6, axis="z")

    for ci, objs in walls.items():
        if objs:
            C.part(objs, f"Walls{ci}", C.CITY[ci], "SmoothPlastic", smooth_angle=None)
    C.part(roof, "Roofs", C.CITY_ROOF, "SmoothPlastic", smooth_angle=None)
    dq = [o for o in (dark_q.obj("DarkA"), dark_b.obj("DarkB")) if o is not None]
    C.part(dq, "WindowsDark", WIN_DARK, "SmoothPlastic", smooth_angle=None)
    lq = [o for o in (lit_q.obj("LitA"), lit_b.obj("LitB")) if o is not None]
    ns.tag(C.merge(lq, "Windows"), "Windows", C.WARM_BULB, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)
    ns.tag(light, "AircraftLight", C.AIRCRAFT_RED, "Neon", recolor="lamp", cast_shadow=False, smooth_angle=None)


META = {"kind": "skyline", "pivot": "ground level, footprint centre", "view_distance": "200-600 studs",
        "roles": {"lamp": "Windows (warm lit windows), AircraftLight (red, blink it)"}}

if __name__ == "__main__":
    C.run(build, "World_SkylineA", meta=META, sockets={"Beacon": ((-6.0, 7.5, 59.42), 0.0)},
          far_kw={"yaw": -15.0})
