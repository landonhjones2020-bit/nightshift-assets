"""Lobby_BookPodium — wooden lectern holding the giant open Secret Sandwich Book.

Walnut lectern on a dark plinth with gilded trim bands, a lighter inset front panel and a
gold medallion bearing the STACKHOUSE sandwich. Its sloped top (rising away from the
reader) carries a giant open book: burgundy leather boards with gilded corner caps, two
bulging cream page blocks (a sandwich sketch on the left page, ruled "recipe" lines on the
right), a red ribbon bookmark spilling over the front edge, and a faint warm glow along
the page edges (PageGlow, Neon, role "glow": code can pulse it when a Secret is found).

Front (reader side) = -Y. Pivot = bottom-centre of the plinth. Socket Prompt = in front of
the book at reading height; Book = centre of the open pages (normal tilted toward the
reader by meta book_tilt_deg).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

ns = C.ns
TOP_F, TOP_B = (-0.95, 3.15), (0.75, 3.65)      # lectern top slope (y, z) front / back
TILT = math.degrees(math.atan2(TOP_B[1] - TOP_F[1], TOP_B[0] - TOP_F[0]))
LEATHER = "#7A2433"
PAGE = "#F4ECD6"
INK = "#8C7B66"
GLOW = "#F2C66A"
RIBBON = "#D6322A"
BW, BD = 1.85, 2.45            # one cover board (x) / book depth (y)


def ribbon(points, width=0.2, thick=0.035):
    """Flat strip along a polyline, width along X."""
    bm = bmesh.new()
    pts = [Vector(p) for p in points]
    side = Vector((1, 0, 0))
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        n = t.cross(side).normalized()
        rings.append([bm.verts.new(p + side * sx * width / 2 + n * sn * thick / 2)
                      for sx, sn in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(4):
            kk = (k + 1) % 4
            bm.faces.new([r0[k], r0[kk], r1[kk], r1[k]])
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, "Ribbon")


def book():
    """Open book in local space: spine along Y at x = 0, cover bottom at z = 0, front -Y."""
    out = {"leather": [], "page": [], "glow": [], "gold": [], "ink": [], "ribbon": [], "icon": None}
    for sx in (-1, 1):
        # board 0.012 inside the gilded corner caps' outer faces (flush, the caps' side faces z-fought with the
        # leather edges); the caps keep the book's outer size
        board = C.prism(C.rrect(BW - 0.012, BD - 0.024, 0.12, 2, sx * (BW / 2 + 0.014), 0), "z", 0.0, 0.09)
        ns.bevel(board, width=0.025, segments=1)
        out["leather"].append(board)
        prof = [(0.05, 0.09), (0.1, 0.27), (0.3, 0.4), (1.0, 0.41), (BW - 0.18, 0.37), (BW - 0.13, 0.31),
                (BW - 0.13, 0.09)]
        prof = [(sx * x, z) for x, z in prof]
        pg = C.prism(prof, "y", -BD / 2 + 0.12, BD / 2 - 0.12)
        out["page"].append(pg)
        # glow strips: fore-edge + front / back page edges (just proud of the block faces)
        xe = sx * (BW - 0.13)
        a0, a1 = sorted((xe, xe + sx * 0.025))
        out["glow"].append(ns.box((a1 - a0, BD - 0.3, 0.16), loc=((a0 + a1) / 2, 0, 0.2), bevel=0.0))
        for sy in (-1, 1):
            y = sy * (BD / 2 - 0.12)
            b0, b1 = sorted((y, y + sy * 0.025))
            out["glow"].append(ns.box((BW - 0.6, b1 - b0, 0.15), loc=(sx * (BW / 2 + 0.15), (b0 + b1) / 2, 0.24),
                                      bevel=0.0))
            # gilded corner caps on the outer corners of each board
            cx, cy = sx * (BW + 0.02), sy * BD / 2
            tri = [(cx, cy), (cx - sx * 0.42, cy), (cx, cy - sy * 0.42)]
            out["gold"].append(C.prism(tri, "z", -0.015, 0.105))
    # spine roll under the gutter
    sp = ns.cyl(0.13, BD - 0.05, loc=(0, 0, 0.04), rot=(90, 0, 0), verts=8, bevel=0.0)
    out["leather"].append(sp)
    # ruled recipe lines on the right page, a sandwich sketch on the left page
    for k in range(6):
        y = 0.75 - k * 0.3
        w = 1.05 if k % 3 != 2 else 0.7
        out["ink"].append(ns.box((w, 0.05, 0.02), loc=(0.42 + w / 2, y, 0.413), bevel=0.0))
    icon = C.sandwich_icon(s=0.4, depth=0.03)
    C.place(icon, (-0.95, 0.15, 0.41), pitch=-90)
    out["icon"] = icon
    # ribbon: from the spine top across the right page, over the front edge, hanging down
    down = Vector((0, -math.sin(math.radians(TILT)), -math.cos(math.radians(TILT))))
    start = [(0.2, BD / 2 - 0.25, 0.43), (0.33, 0.2, 0.44), (0.38, -BD / 2 + 0.2, 0.44), (0.4, -BD / 2 - 0.02, 0.33)]
    p = Vector(start[-1])
    hang = [tuple(p + down * d + Vector((0.04 * math.sin(d * 3), 0, 0))) for d in (0.35, 0.75, 1.15)]
    out["ribbon"].append(ribbon(start + hang))
    return out


def build():
    # plinth + lectern body
    plinth = ns.box((2.7, 2.2, 0.35), loc=(0, 0, 0.175), bevel=0.08, segments=1)
    C.part([plinth], "Plinth", C.WOOD_DARK, "Wood", can_collide=True, smooth_angle=40)
    prof = C.fillet([(-0.62, 0.35), (0.55, 0.35), TOP_B, TOP_F], [0.0, 0.0, 0.08, 0.08], 1)
    body = C.prism(prof, "x", -1.0, 1.0)
    ns.bevel(body, width=0.06, segments=1)
    C.part([body], "Lectern", C.WOOD, "Wood", can_collide=True, smooth_angle=40)
    # front inset panel (follows the slanted front face)
    fa, fb = (-0.62, 0.35), TOP_F
    d = Vector((0, fb[0] - fa[0], fb[1] - fa[1])).normalized()
    n = Vector((0, -d.z, d.y))           # outward (-Y-ish) normal of the front face
    panel_pts = []
    for t, x in ((0.12, -0.75), (0.12, 0.75), (0.88, 0.75), (0.88, -0.75)):
        p = Vector((x, fa[0], fa[1])) + d * (t * (Vector(fb) - Vector(fa)).length)
        panel_pts.append(p)
    panel = ns.box((1.5, 0.06, 0.82 * (Vector(fb) - Vector(fa)).length), loc=(0, 0, 0), bevel=0.02, segments=1)
    mid = (panel_pts[0] + panel_pts[2]) / 2 + n * 0.0
    panel.rotation_euler = (math.atan2(-d.y, d.z), 0, 0)
    panel.location = mid
    C.part([panel], "Panel", C.WOOD_LIGHT, "Wood", smooth_angle=40)
    # gilded trim: band on the plinth top edge, band under the slope, medallion rim
    gold = [ns.box((2.06, 1.24, 0.08), loc=(0, -0.03, 0.42), bevel=0.02, segments=1)]
    gold.append(C.prism([(TOP_F[0] - 0.04, TOP_F[1] - 0.22), (TOP_B[0] + 0.04, TOP_B[1] - 0.22), (TOP_B[0] + 0.04, TOP_B[1] - 0.12),
                         (TOP_F[0] - 0.04, TOP_F[1] - 0.12)], "x", -1.03, 1.03))
    med_c = mid + n * 0.05 + d * 0.15
    med_rim = ns.cyl(0.42, 0.06, verts=16, bevel=0.0)
    med = ns.cyl(0.34, 0.05, loc=(0, 0, 0.04), verts=16, bevel=0.0)
    mini = C.sandwich_icon(s=0.25, depth=0.05)
    C.place(mini, (0, -0.07, 0.0))
    C.place([med_rim, med], (0, 0, 0), pitch=90)
    tilt_front = math.degrees(math.atan2(-d.y, d.z))
    C.place([med_rim, med], tuple(med_c), pitch=tilt_front)
    C.place(mini, tuple(med_c), pitch=tilt_front)
    gold.append(med_rim)
    # front book lip
    lip = C.prism([(TOP_F[0] - 0.08, TOP_F[1] - 0.06), (TOP_F[0] + 0.08, TOP_F[1] - 0.02), (TOP_F[0] + 0.06, TOP_F[1] + 0.18),
                   (TOP_F[0] - 0.08, TOP_F[1] + 0.14)], "x", -1.05, 1.05)
    ns.bevel(lip, width=0.02, segments=1)

    # the book, laid on the slope
    b = book()
    ctr = ((TOP_F[0] + TOP_B[0]) / 2 + 0.02, (TOP_F[1] + TOP_B[1]) / 2 + 0.01)
    allb = [o for k in ("leather", "page", "glow", "gold", "ink", "ribbon") for o in b[k]]
    C.place(allb, (0, ctr[0], ctr[1]), pitch=TILT)
    C.place(b["icon"], (0, ctr[0], ctr[1]), pitch=TILT)
    C.part(b["leather"], "Leather", LEATHER, smooth_angle=40)
    C.part(b["page"], "Pages", PAGE, smooth_angle=35)
    ns.tag(C.merge(b["glow"], "PageGlow"), "PageGlow", GLOW, "Neon", recolor="glow", cast_shadow=False, smooth_angle=30)
    C.part(gold + b["gold"], "Gilding", C.GOLD, "Metal", smooth_angle=40)
    C.part(b["ink"], "Ink", INK, smooth_angle=None)
    C.part(b["ribbon"], "Ribbon", RIBBON, "Fabric", smooth_angle=50)
    C.part([lip], "Lip", C.WOOD_DARK, "Wood", smooth_angle=40)
    C.part([med], "MedallionNavy", C.NAVY, smooth_angle=40)
    cols = {}
    for dct in (b["icon"], mini):
        for col, objs in dct.items():
            cols.setdefault(col, []).extend(objs)
    for i, (col, objs) in enumerate(cols.items()):
        C.part(objs, f"Icon{i + 1}", col, smooth_angle=40)
    return {"ctr": ctr}


def sockets():
    ctr = ((TOP_F[0] + TOP_B[0]) / 2, (TOP_F[1] + TOP_B[1]) / 2)
    return {"Prompt": ((0, -1.7, 3.2), 0.0),
            "Book": ((0, ctr[0], ctr[1] + 0.42), 0.0)}


META = {"book_tilt_deg": round(TILT, 1), "roles": {"glow": "PageGlow (Neon page-edge accent)"},
        "light_hint": {"type": "PointLight", "color": GLOW, "range": 8, "brightness": 0.8}}

if __name__ == "__main__":
    C.run(build, "Lobby_BookPodium", sockets=sockets(), pivot=(0, 0, 0), meta=META)
