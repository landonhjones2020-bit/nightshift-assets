"""fam_shop — currencies, Robux products and gamepasses (group "shop"), shown at 120-200 px on
dark rarity-gradient shop cards.

Family look: the "shop" camera (yaw -30, pitch 24), chunky toy-like props in the game palette:
Coins are amber diner coins with an embossed "S", Tokens are pink arcade tokens with a notched
edge and a star. Pack tiers grow the same pile idea from 3 pieces to a register drawer / jar.
"""
from __future__ import annotations

import math
import random

import bmesh

import _common as G
from _common import ns, Vector, Matrix

FAM = "shop"

COIN_R, COIN_T = 1.0, 0.22
TOKEN_R, TOKEN_T = 1.0, 0.2


def shop(name, **opts):
    return G.icon(name, "shop", FAM, **opts)


# ---------------------------------------------------------------------------------------------
# currency pieces (built lying flat, centred at the origin, face up +Z)
# ---------------------------------------------------------------------------------------------

def coin(emboss="S", detail=True, scale=1.0):
    R, T_ = COIN_R, COIN_T
    prof = [(0.0, -T_ / 2), (R - 0.05, -T_ / 2), (R, -T_ / 2 + 0.05), (R, T_ / 2 - 0.05), (R - 0.05, T_ / 2),
            (R - 0.16, T_ / 2), (R - 0.2, T_ / 2 - 0.035), (0.0, T_ / 2 - 0.035)]
    if detail:
        prof = prof[:-1] + [(R - 0.2, T_ / 2 - 0.035), (0.0, T_ / 2 - 0.035)]
    body = G.lathe(prof, verts=48 if detail else 32)
    G.T(body, G.AMBER, name="Coin", smooth=50)
    parts = [body]
    if detail:
        # matching rim on the underside so a flipped coin also reads
        groove = G.torus(R + 0.002, 0.018, segs=48, rsegs=6)
        G.T(groove, G.AMBER_D, name="CoinGroove")
        parts.append(groove)
        if emboss:
            if emboss == "arrow":
                e = G.puffy(G.fillet([(0.0, 0.62), (0.48, 0.1), (0.2, 0.1), (0.2, -0.56), (-0.2, -0.56), (-0.2, 0.1), (-0.48, 0.1)], 0.05, 2),
                            0.12, puff=0.35)
                col = G.GREEN
            else:
                e = G.text(emboss, 1.15, 0.1)
                col = "#FFE08A"
            G.xform(e, G.Tm(0, 0, T_ / 2 - 0.035) @ G.R(rx=-90))
            G.T(e, col, name="CoinMark")
            parts.append(e)
    if scale != 1.0:
        G.xform(parts, G.S(scale))
    return parts


def token(detail=True, scale=1.0):
    R = TOKEN_R
    n = 14
    pts = []
    for i in range(n):
        a0 = 2 * math.pi * i / n
        w = 2 * math.pi / n
        for f, r in ((0.0, R), (0.62, R), (0.7, R - 0.09), (0.92, R - 0.09)):
            pts.append((r * math.cos(a0 + f * w), r * math.sin(a0 + f * w)))
    body = G.slab_xy(G.fillet(pts, 0.02, 1), TOKEN_T, bevel=0.035, segs=2, z=-TOKEN_T / 2)
    G.T(body, G.PINK, name="Token", smooth=40)
    parts = [body]
    if detail:
        ring = G.torus(R - 0.28, 0.035, loc=(0, 0, TOKEN_T / 2), segs=40, rsegs=6, scale=(1, 1, 0.6))
        G.T(ring, G.PINK_D, name="TokenRing")
        st = G.puffy(G.fillet(G.star(5, 0.5, 0.22), 0.03, 2), 0.1, puff=0.35)
        G.xform(st, G.Tm(0, 0, TOKEN_T / 2) @ G.R(rx=-90))
        G.T(st, G.PINK_L, name="TokenStar")
        parts += [ring, st]
    if scale != 1.0:
        G.xform(parts, G.S(scale))
    return parts


def piece(kind, **kw):
    return coin(**kw) if kind == "coin" else token(**kw)


def put(parts, loc=(0, 0, 0), rx=0.0, ry=0.0, rz=0.0):
    G.xform(parts, G.Tm(*loc) @ G.R(rz=rz) @ G.R(ry=ry) @ G.R(rx=rx))
    return parts


def stand(kind, loc, face_yaw=-24.0, lean=0.0, scale=1.0):
    """A piece standing on its edge, its face turned toward the camera."""
    p = piece(kind, scale=scale)
    r = (COIN_R if kind == "coin" else TOKEN_R) * scale
    put(p, (0, 0, 0), rx=90)        # face -> -Y
    G.xform(p, G.Tm(loc[0], loc[1], loc[2] + r) @ G.R(rz=face_yaw) @ G.R(rx=-lean))
    return p


def stack(kind, n, loc=(0, 0, 0), seed=1, scale=1.0, top_detail=True):
    rnd = random.Random(seed)
    t = (COIN_T if kind == "coin" else TOKEN_T) * scale
    out = []
    for i in range(n):
        top = i == n - 1
        p = piece(kind, detail=top and top_detail, scale=scale)
        put(p, (loc[0] + rnd.uniform(-0.04, 0.04) * scale, loc[1] + rnd.uniform(-0.04, 0.04) * scale, loc[2] + t / 2 + i * t * 0.98),
            rz=rnd.uniform(0, 360))
        out += p
    return out


def heap(kind, n, centre=(0, 0, 0), radius=1.6, height=0.9, seed=3, scale=0.7, tilt=30.0, detail_every=1):
    """A mound of loose pieces (cone-ish), deterministic."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        u = math.sqrt(rnd.random())
        a = rnd.uniform(0, 2 * math.pi)
        x, y = u * radius * math.cos(a), u * radius * math.sin(a) * 0.8
        z = height * (1 - u) ** 1.2 + rnd.uniform(-0.04, 0.06)
        p = piece(kind, detail=(i % detail_every == 0), scale=scale)
        put(p, (centre[0] + x, centre[1] + y, centre[2] + z), rx=rnd.uniform(-tilt, tilt), ry=rnd.uniform(-tilt, tilt), rz=rnd.uniform(0, 360))
        out += p
    return out


# ---------------------------------------------------------------------------------------------
# currencies
# ---------------------------------------------------------------------------------------------

@shop("Currency_Coins")
def currency_coins():
    p = coin()
    put(p, rx=72, rz=-26)


@shop("Currency_Tokens")
def currency_tokens():
    p = token()
    put(p, rx=72, rz=-26)


# ---------------------------------------------------------------------------------------------
# coin / token pack tiers (same composition per tier, coins vs tokens)
# ---------------------------------------------------------------------------------------------

def tier1(kind):
    stand(kind, (0.35, -0.3, 0.0), face_yaw=-30, lean=10)
    p = piece(kind)
    put(p, (-0.95, 0.25, 0.11), rx=0, rz=20)
    p = piece(kind)
    put(p, (-0.75, -0.6, 0.33), rx=-14, ry=8, rz=40)


def tier2(kind):
    stack(kind, 6, (-0.35, 0.3, 0.0), seed=4)
    stand(kind, (0.75, -0.55, 0.0), face_yaw=-30, lean=14)
    p = piece(kind)
    put(p, (-0.6, -0.95, 0.11), rz=10)


def tier3(kind):
    stack(kind, 9, (-0.6, 0.55, 0.0), seed=5)
    stack(kind, 5, (0.75, 0.75, 0.0), seed=6)
    heap(kind, 11, centre=(0.1, -0.55, 0.0), radius=1.2, height=0.55, seed=7, scale=0.72)
    stand(kind, (1.25, -0.6, 0.0), face_yaw=-28, lean=12, scale=0.8)


def pouch():
    prof = [(0.0, 0.0), (0.7, 0.02), (1.08, 0.25), (1.2, 0.62), (1.12, 1.05), (0.82, 1.38), (0.46, 1.58), (0.4, 1.66),
            (0.5, 1.78), (0.62, 1.96), (0.6, 2.06), (0.38, 2.02), (0.0, 1.98)]
    bag = G.lathe(prof, verts=40)
    # gentle cloth folds
    for v in bag.data.vertices:
        a = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.035 * math.sin(7 * a) * min(1.0, v.co.z / 1.2)
        v.co.x *= k
        v.co.y *= k
    G.T(bag, "#9A5B34", name="Pouch", smooth=70)
    cord = G.torus(0.45, 0.06, loc=(0, 0, 1.64), segs=32, rsegs=8)
    tails = [G.tube([(0.3, -0.35, 1.64), (0.45, -0.55, 1.4), (0.42, -0.6, 1.1)], 0.05, sides=8),
             G.tube([(0.2, -0.38, 1.64), (0.15, -0.6, 1.35), (0.22, -0.66, 1.05)], 0.05, sides=8)]
    knobs = [G.sphere(0.09, loc=(0.42, -0.6, 1.06)), G.sphere(0.09, loc=(0.22, -0.66, 1.0))]
    G.T([cord] + tails + knobs, G.AMBER, name="Cord")
    badge = coin(scale=0.42)
    put(badge, (0, -1.27, 0.72), rx=90)
    G.xform(badge, G.R(rx=-12, about=(0, -1.27, 0.72)))


def tier4(kind):
    if kind == "coin":
        pouch()
        heap(kind, 9, centre=(0.4, -1.15, 0.0), radius=1.0, height=0.35, seed=8, scale=0.6)
        stand(kind, (-1.5, -0.8, 0.0), face_yaw=-25, lean=10, scale=0.62)
    else:
        token_cup()


def sack():
    prof = [(0.0, 0.0), (1.0, 0.0), (1.42, 0.3), (1.6, 0.9), (1.55, 1.6), (1.36, 2.05), (1.42, 2.2), (1.62, 2.32),
            (1.66, 2.42), (1.5, 2.46), (1.28, 2.3), (1.18, 2.1), (0.0, 2.1)]
    bag = G.lathe(prof, verts=48)
    for v in bag.data.vertices:
        a = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.04 * math.sin(6 * a + 0.5) * min(1.0, v.co.z / 1.5) + 0.03 * math.sin(11 * a)
        v.co.x *= k
        v.co.y *= k
    G.T(bag, "#C9A46A", name="Sack", smooth=70)
    G.T(G.cyl(1.2, 0.05, loc=(0, 0, 2.08), verts=40, bevel=0), "#3A2A1A", name="SackInside")
    band = G.lathe([(1.37, 1.6), (1.43, 1.62), (1.46, 1.78), (1.4, 1.82)], verts=48)
    G.T(band, "#8E6A44", name="Stitch")
    mark = G.text("S", 0.95, 0.1)
    G.xform(mark, G.Tm(0, -1.6, 1.05) @ G.R(rx=4))
    G.T(mark, "#7A5233", name="SackMark")


def tier5(kind):
    if kind == "coin":
        sack()
        heap("coin", 22, centre=(0, 0, 2.05), radius=1.15, height=0.65, seed=9, scale=0.55, tilt=25)
        heap("coin", 12, centre=(0.3, -1.6, 0.0), radius=1.3, height=0.32, seed=10, scale=0.58)
        stand("coin", (-1.65, -0.9, 0.0), face_yaw=-25, lean=10, scale=0.6)
    else:
        token_jar()


def register_drawer():
    mod_res, objs = G.build_foreign("A_kitchen", "Kitchen_Register")
    drawer = [o for o in objs if o.get("ns_role") == "drawer"]
    G.xform(drawer, G.Tm(0, -0.85, 0))
    # coins overflowing every compartment of the open drawer and spilling over its front
    dy = -0.85 - 1.7 / 2 + (1.7 - 0.3) / 2 + 0.02 + 0.1
    for i, x in enumerate((-0.6, -0.2, 0.2, 0.6)):
        heap("coin", 6, centre=(x, dy - 0.05, 0.42), radius=0.26, height=0.3, seed=20 + i, scale=0.17, tilt=35)
    heap("coin", 12, centre=(0.0, dy - 0.35, 0.5), radius=0.7, height=0.18, seed=30, scale=0.17, tilt=40)
    heap("coin", 16, centre=(0.1, -2.0, 0.0), radius=0.95, height=0.14, seed=31, scale=0.18, tilt=20)
    for loc, yaw in (((-0.75, -1.95, 0.0), -30), ((0.95, -1.75, 0.0), -20)):
        stand("coin", loc, face_yaw=yaw, lean=10, scale=0.2)
    return objs


def tier6(kind):
    register_drawer()


def token_cup():
    prof = [(0.0, 0.0), (0.72, 0.0), (0.76, 0.06), (1.0, 1.9), (1.06, 1.98), (1.04, 2.04), (0.95, 2.02), (0.92, 1.94),
            (0.66, 0.12), (0.0, 0.12)]
    cup = G.lathe(prof, verts=48)
    G.T(cup, G.PAPER, name="Cup", smooth=40)
    # six pink stripes: a thin band just proud of the cup wall, keeping only the stripe wedges
    st = G.lathe([(0.771, 0.1), (0.781, 0.1), (1.005, 1.86), (0.995, 1.86)], verts=96)
    bm = bmesh.new()
    bm.from_mesh(st.data)
    kill = [f for f in bm.faces if (math.degrees(math.atan2(f.calc_center_median().y, f.calc_center_median().x)) + 360) % 60 > 24]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(st.data)
    bm.free()
    G.T(st, G.PINK, name="CupStripe", smooth=40)
    heap("token", 16, centre=(0, 0, 1.95), radius=0.95, height=0.55, seed=12, scale=0.42, tilt=28)
    heap("token", 7, centre=(0.5, -1.25, 0.0), radius=0.85, height=0.22, seed=13, scale=0.45)
    stand("token", (-1.2, -0.8, 0.0), face_yaw=-25, lean=10, scale=0.48)


def token_jar():
    R_, H_ = 1.05, 2.3
    glass = G.lathe([(0.0, 0.0), (R_ - 0.12, 0.0), (R_, 0.12), (R_, H_ - 0.35), (R_ - 0.2, H_ - 0.15), (R_ - 0.2, H_)], verts=48)
    G.glass_mat(glass)
    lip = G.torus(R_ - 0.18, 0.06, loc=(0, 0, H_), segs=48, rsegs=8)
    G.glass_mat(lip, centre=0.4, edge=0.9)
    # tokens filling the jar (a packed, tumbled column) and heaped over the mouth
    rnd = random.Random(14)
    for i in range(52):
        z = 0.15 + (H_ - 0.35) * i / 52
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.05, 0.5)
        p = token(detail=(i % 2 == 0), scale=0.4)
        put(p, (rr * math.cos(a), rr * math.sin(a), z), rx=rnd.uniform(-60, 60), ry=rnd.uniform(-60, 60), rz=rnd.uniform(0, 360))
    heap("token", 10, centre=(0, 0, H_ - 0.05), radius=0.72, height=0.45, seed=15, scale=0.4, tilt=28)
    label = G.lathe([(R_ + 0.005, 0.7), (R_ + 0.02, 0.7), (R_ + 0.02, 1.3), (R_ + 0.005, 1.3)], verts=48)
    G.T(label, G.PAPER, name="Label")
    star = G.puffy(G.fillet(G.star(5, 0.26, 0.11), 0.02, 1), 0.06)
    G.xform(star, G.Tm(0, -R_ - 0.03, 1.0))
    G.T(star, G.PINK, name="LabelStar")
    lid = G.cyl(R_ - 0.08, 0.26, loc=(1.2, -0.75, 0.13), verts=48, bevel=0.06)
    G.T(lid, G.PINK_D, name="Lid")
    G.xform(lid, G.R(rx=-10, ry=8, about=(1.2, -0.75, 0.13)))
    heap("token", 6, centre=(-0.6, -1.3, 0.0), radius=0.7, height=0.2, seed=16, scale=0.42)


for i, fn in enumerate((tier1, tier2, tier3, tier4, tier5, tier6), start=1):
    shop(f"Product_DP_COINS_{i}")((lambda f: (lambda: f("coin")))(fn))
for i, fn in enumerate((tier1, tier2, tier3, tier4, tier5), start=1):
    shop(f"Product_DP_TOKENS_{i}")((lambda f: (lambda: f("token")))(fn))


# ---------------------------------------------------------------------------------------------
# revives (heart family shared with HUD_Revive)
# ---------------------------------------------------------------------------------------------
HEART = "#FF2E4D"


def heart_plus(size=1.0, depth=0.62, loc=(0, 0, 0)):
    h = G.puffy(G.heart(1.05 * size, 72), depth * size, puff=0.45)
    G.T(h, HEART, name="Heart")
    yf = -depth * size / 2
    plus = [G.puffy(G.rrect(0.26 * size, 0.86 * size, 0.1 * size, cz=0.1 * size), 0.16 * size, y=yf),
            G.puffy(G.rrect(0.86 * size, 0.26 * size, 0.1 * size, cz=0.1 * size), 0.16 * size, y=yf)]
    G.T(plus, G.PAPER, name="Plus")
    objs = [h] + plus
    G.xform(objs, G.Tm(*loc))
    return objs


def paddle(side):
    """Defibrillator paddle in profile (glyph style), pad pressed on the heart's side."""
    s = side
    pad = G.puffy(G.rrect(0.2, 1.0, 0.08), 0.62, puff=0.35)
    G.T(pad, G.STEEL, "Metal", name="Pad", gloss=0.35)
    body = G.puffy(G.fillet([(0.08, -0.42), (0.5, -0.3), (0.5, 0.3), (0.08, 0.42)], 0.08, 3), 0.52, puff=0.4)
    G.T(body, G.INK_SOFT, name="PaddleBody")
    grip = G.puffy_holes(G.fillet([(0.44, -0.36), (0.98, -0.3), (0.98, 0.3), (0.44, 0.36)], 0.16, 4),
                         [G.fillet([(0.58, -0.17), (0.82, -0.14), (0.82, 0.14), (0.58, 0.17)], 0.06, 3)], 0.34, puff=0.4)
    G.T(grip, G.AMBER, name="Grip")
    btn = G.puffy(G.rrect(0.1, 0.16, 0.04, cx=0.9, cz=0.36), 0.16, puff=0.4)
    G.T(btn, G.RED, name="Trigger")
    objs = [pad, body, grip, btn]
    if s < 0:
        G.xform(objs, G.S((-1, 1, 1)))
    G.xform(objs, G.Tm(s * 1.02, 0.0, 0.02) @ G.R(ry=-s * 14))
    lead = G.tube([(s * 1.9, 0.05, -0.05), (s * 2.1, 0.08, -0.55), (s * 1.75, 0.1, -0.95), (s * 1.2, 0.1, -1.1)], 0.055, sides=8)
    G.T(lead, G.INK_SOFT, name="Lead")
    return objs + [lead]


def zap(x, z, s=1.0, rot=0.0):
    bolt = [(0.04, 0.5), (0.3, 0.5), (0.1, 0.12), (0.3, 0.12), (-0.16, -0.5), (-0.04, -0.08), (-0.26, -0.08)]
    o = G.puffy(G.fillet([(px * s, pz * s) for px, pz in bolt], 0.03, 2), 0.12 * s, puff=0.4, y=-0.35)
    G.xform(o, G.Tm(x, 0, z) @ G.R(ry=rot))
    G.T(o, G.CYAN, name="Zap")
    return o


def revive_set():
    heart_plus()
    paddle(1)
    paddle(-1)
    zap(-0.62, 1.05, 0.7, -18)
    zap(0.66, 1.02, 0.65, 22)


def badge(text_, col=G.AMBER, loc=(0.95, -0.5, 0.95), r=0.42, txt_col=G.INK_SOFT, size=0.55):
    disc = G.puffy(G.circle(r, 40), 0.22, puff=0.42)
    G.T(disc, col, name="Badge")
    ring = G.puffy_holes(G.circle(r + 0.06, 40), [G.circle(r - 0.02, 40)], 0.18, puff=0.4)
    G.T(ring, G.PAPER, name="BadgeRing")
    t = G.text(text_, size, 0.08, loc=(0, -0.11, -0.02))
    G.T(t, txt_col, name="BadgeText")
    objs = [disc, ring, t]
    G.xform(objs, G.Tm(*loc))
    return objs


@shop("Product_DP_REVIVE")
def revive():
    revive_set()
    G.face_cam(family=FAM, reveal=16, tilt=6)


@shop("Product_DP_REVIVE_AGAIN")
def revive_again():
    revive_set()
    badge("2", loc=(0.88, -0.6, 0.98), r=0.44, size=0.62)
    G.face_cam(family=FAM, reveal=16, tilt=6)


def hand(skin, sleeve, cuff, front=True):
    """One arm of a handshake in the XZ plane: forearm from the lower left, the hand gripping
    toward +X at the centre. front=True: its fingers wrap over the other hand (in front)."""
    yb = 0.1 if front else 0.25
    arm = G.puffy(G.stroke([(-1.55, -0.95), (-0.72, -0.2)], 0.6), 0.56, puff=0.42, y=yb)
    G.T(arm, sleeve, name="Sleeve")
    cf = G.puffy(G.stroke([(-0.84, -0.31), (-0.68, -0.17)], 0.66), 0.62, puff=0.42, y=yb)
    G.T(cf, cuff, name="SleeveCuff")
    palm = G.puffy(G.rrect(0.84, 0.66, 0.28, cx=-0.2, cz=0.02), 0.5, puff=0.45, y=yb - 0.04)
    G.xform(palm, G.R(ry=-22, about=(-0.2, 0, 0.02)))
    G.T(palm, skin, name="Palm")
    fy = -0.3 if front else 0.48
    fingers = []
    for k in range(4):
        z = 0.32 - 0.18 * k
        fingers.append(G.puffy(G.stroke([(0.0, z), (0.36, z + 0.02), (0.5, z - 0.12)], 0.18), 0.2, puff=0.45, y=fy))
    G.T(fingers, skin, name="Finger")
    thumb = G.puffy(G.stroke([(-0.36, 0.3), (-0.04, 0.5), (0.16, 0.44)], 0.2), 0.22, puff=0.45, y=-0.36 if front else -0.1)
    G.T(thumb, skin, name="Thumb")
    return [arm, cf, palm, thumb] + fingers


@shop("Product_DP_REVIVE_FRIEND")
def revive_friend():
    hand("#F2C9A5", G.CYAN, G.PAPER, front=True)
    b = hand("#B9784F", G.PINK, G.PAPER, front=False)
    G.xform(b, G.S((-1, 1, 1)))
    h = G.puffy(G.heart(0.36, 48), 0.24, puff=0.45)
    G.xform(h, G.Tm(0.0, -0.2, 1.0))
    G.T(h, HEART, name="Heart")
    sp = [G.puffy(G.fillet(G.star(4, r, r * 0.3, cx=x, cz=z), 0.01, 1), 0.06, y=-0.2) for x, z, r in ((-0.6, 0.95, 0.16), (0.62, 1.15, 0.12))]
    G.T(sp, G.AMBER, name="Sparkle")
    G.face_cam(family=FAM, reveal=14, tilt=4)


@shop("Product_DP_REVIVE_CREW")
def revive_crew():
    ring = G.torus(1.05, 0.12, rot=(90, 0, 0), segs=64, rsegs=12)
    G.T(ring, G.AMBER, name="Ring")
    for k in range(4):
        a = 90 + 90 * k
        h = G.puffy(G.heart(0.5, 56), 0.4, puff=0.45)
        G.xform(h, G.Tm(1.05 * math.cos(math.radians(a)), -0.02, 1.05 * math.sin(math.radians(a))) @ G.R(ry=-(a - 270)))
        G.T(h, HEART, name="Heart")
        hl = G.puffy(G.stroke(G.arc(0.2, 110, 170, 6, -0.2, 0.12), 0.07), 0.04, y=-0.2)
        G.xform(hl, G.Tm(1.05 * math.cos(math.radians(a)), -0.02, 1.05 * math.sin(math.radians(a))) @ G.R(ry=-(a - 270)))
        G.T(hl, "#FF9AA9", name="Shine")
    plus = [G.puffy(G.rrect(0.2, 0.62, 0.08), 0.22), G.puffy(G.rrect(0.62, 0.2, 0.08), 0.22)]
    G.T(plus, G.PAPER, name="Plus")
    G.face_cam(family=FAM, reveal=16, tilt=6)


# ---------------------------------------------------------------------------------------------
# starter + boost
# ---------------------------------------------------------------------------------------------

def folded_apron(col=G.BRAND, trim=G.MUSTARD):
    body = G.box((1.3, 0.95, 0.22), bevel=0.1, segs=4)
    G.T(body, col, name="ApronFold")
    folds = [G.box((1.32, 0.06, 0.24), loc=(0, y, 0.0), bevel=0.03, segs=2) for y in (-0.15, 0.2)]
    G.T(folds, "#C9411F", name="ApronFoldLine")
    pocket = G.box((0.7, 0.04, 0.16), loc=(0.0, -0.49, 0.0), bevel=0.02, segs=1)
    straps = [G.tube([(-0.5, -0.3, 0.11), (-0.3, -0.6, 0.12), (0.1, -0.62, 0.12), (0.45, -0.52, 0.11)], 0.045, sides=8),
              G.tube([(0.5, 0.3, 0.12), (0.62, -0.1, 0.13), (0.72, -0.45, 0.1)], 0.045, sides=8)]
    G.T([pocket] + straps, trim, name="ApronStrap")
    return [body, pocket] + folds + straps


@shop("Product_DP_STARTER")
def starter():
    W, D, H = 2.1, 1.5, 1.1
    box_ = G.box((W, D, H), loc=(0, 0, H / 2), bevel=0.0)
    G.boolean(box_, G.box((W - 0.12, D - 0.12, H), loc=(0, 0, H / 2 + 0.08), bevel=0.0))
    G._bevel(box_, 0.025, 2)
    G.T(box_, G.KRAFT, name="Box")
    flaps = []
    for sy in (-1, 1):
        f = G.box((W - 0.04, 0.05, 0.55), bevel=0.02, segs=1)
        G.xform(f, G.Tm(0, sy * D / 2, H) @ G.R(rx=sy * -125) @ G.Tm(0, 0, 0.275))
        flaps.append(f)
    for sx in (-1, 1):
        f = G.box((0.05, D - 0.04, 0.5), bevel=0.02, segs=1)
        G.xform(f, G.Tm(sx * W / 2, 0, H) @ G.R(ry=sx * 125) @ G.Tm(0, 0, 0.25))
        flaps.append(f)
    G.T(flaps, G.KRAFT_D, name="Flap")
    band = G.box((W + 0.02, 0.02, 0.34), loc=(0, -D / 2 - 0.005, 0.48), bevel=0.0)
    G.T(band, G.BRAND, name="Band")
    star = G.puffy(G.fillet(G.star(5, 0.3, 0.13), 0.02, 1), 0.06)
    G.xform(star, G.Tm(-0.7, -D / 2 - 0.03, 0.48))
    G.T(star, G.MUSTARD, name="BandStar")
    new = G.text("STARTER", 0.24, 0.04, loc=(0.2, -D / 2 - 0.03, 0.48))
    G.fit_width(new, 1.1)
    G.T(new, G.PAPER, name="BandText")
    # folded "First Night" apron standing at the back, coins and tokens heaped in front of it
    import fam_hud
    ap = G.puffy(fam_hud.apron_outline(), 0.2, puff=0.4)
    G.T(ap, G.BRAND, name="Apron")
    pocket = G.puffy(G.rrect(0.96, 0.4, 0.08, cz=-0.4), 0.06, y=-0.1)
    G.T(pocket, G.MUSTARD, name="ApronPocket")
    strap = G.tube([(-0.3, 0.0, 0.84), (-0.24, 0.0, 1.14), (0.0, -0.02, 1.28), (0.24, 0.0, 1.14), (0.3, 0.0, 0.84)], 0.05, sides=10)
    G.T(strap, G.MUSTARD, name="ApronStrap")
    G.xform([ap, pocket, strap], G.Tm(-0.05, 0.35, H + 0.15) @ G.R(rx=-14) @ G.S(0.72))
    heap("coin", 14, centre=(-0.45, -0.15, H - 0.3), radius=0.65, height=0.55, seed=40, scale=0.36, tilt=30)
    heap("token", 10, centre=(0.5, -0.12, H - 0.3), radius=0.6, height=0.5, seed=41, scale=0.34, tilt=30)
    stand("coin", (-0.75, -1.05, 0.0), face_yaw=-25, lean=8, scale=0.42)
    stand("token", (0.85, -1.1, 0.0), face_yaw=-30, lean=8, scale=0.4)
    G.xform(G.tagged(), G.R(rz=8))


@shop("Product_DP_BOOST_3")
def boost3():
    p = coin(emboss="arrow")
    put(p, rx=78, rz=-22)
    pill = G.puffy(G.rrect(1.0, 0.56, 0.28), 0.3, puff=0.42)
    G.T(pill, G.GREEN, name="Pill")
    t = G.text("×3", 0.5, 0.08, loc=(0, -0.16, 0.0))
    G.T(t, G.INK_SOFT, name="PillText")
    G.xform([pill, t], G.Tm(0.82, -0.55, -0.7) @ G.R(rz=-26))
    pips = [G.puffy(G.fillet([(-0.18, -0.06), (0.0, 0.12), (0.18, -0.06), (0.18, -0.16), (0.0, 0.02), (-0.18, -0.16)], 0.02, 1), 0.12)
            for _ in range(3)]
    for k, o in enumerate(pips):
        G.xform(o, G.Tm(-1.0, -0.4, 0.15 + 0.28 * k) @ G.R(rz=-26))
    G.T(pips, G.GREEN, name="Pip")


# ---------------------------------------------------------------------------------------------
# gamepasses
# ---------------------------------------------------------------------------------------------

def crown(loc=(0, 0, 0), s=1.0):
    pts = [(-0.6, 0.0), (0.6, 0.0), (0.66, 0.62), (0.32, 0.3), (0.0, 0.72), (-0.32, 0.3), (-0.66, 0.62)]
    c = G.puffy(G.fillet([(x * s, z * s) for x, z in pts], 0.04 * s, 2), 0.3 * s, puff=0.4)
    G.T(c, G.GOLD, name="Crown")
    gems = [G.sphere(0.09 * s, loc=(x * s, -0.12 * s, z * s)) for x, z in ((-0.66, 0.66), (0.0, 0.78), (0.66, 0.66))]
    G.T(gems, G.PINK, name="Gem")
    band = G.puffy(G.rrect(1.24 * s, 0.18 * s, 0.06 * s, cz=0.08 * s), 0.34 * s, puff=0.4)
    G.T(band, "#E59A0E", name="CrownBand")
    objs = [c, band] + gems
    G.xform(objs, G.Tm(*loc))
    return objs


@shop("Pass_GP_VIP")
def vip():
    plate = G.puffy(G.rrect(2.1, 1.25, 0.3), 0.36, puff=0.38)
    G.T(plate, G.GOLD, "Metal", name="Plate", gloss=0.32)
    inset = G.puffy(G.rrect(1.8, 0.95, 0.2), 0.08, y=-0.18)
    G.T(inset, "#2A1F3D", name="Inset")
    t = G.text("VIP", 0.72, 0.1, loc=(0, -0.24, -0.02))
    G.fit_width(t, 1.4)
    G.T(t, G.GOLD, "Metal", name="VIP", gloss=0.3)
    crown(loc=(0, 0.0, 0.62), s=0.62)
    rib = []
    for s in (1, -1):
        rib.append(G.puffy([(s * 0.25, -0.6), (s * 0.62, -0.62), (s * 0.66, -1.25), (s * 0.45, -1.08), (s * 0.25, -1.25)][::s], 0.06, y=0.1))
    G.T(rib, G.VIOLET, name="Ribbon")
    sp = [G.puffy(G.fillet(G.star(4, r, r * 0.28, cx=x, cz=z), 0.01, 1), 0.06, y=-0.2) for x, z, r in ((-1.15, 0.7, 0.2), (1.18, -0.55, 0.16))]
    G.T(sp, G.PAPER, name="Sparkle")
    G.face_cam(family=FAM, reveal=16, tilt=6)


@shop("Pass_GP_2X_COINS")
def two_x():
    a = coin()
    put(a, (0.6, 0.55, 0.45), rx=80, rz=-14)
    b = coin()
    put(b, (-0.3, -0.05, 0.0), rx=76, rz=-34)
    t = G.text("2×", 1.25, 0.36, loc=(0, 0, 0), bevel=0.05)
    G.T(t, G.GREEN, name="TwoX")
    back = G.puffy(G.rrect(1.55, 0.95, 0.42), 0.26, puff=0.42, y=0.2)
    G.T(back, G.INK_SOFT, name="TwoXBack")
    G.xform([t, back], G.Tm(0.55, -1.1, -0.55) @ G.R(rz=-28) @ G.R(rx=-8))


@shop("Pass_GP_SECOND_SHIFT")
def second_shift():
    body = G.cyl(1.0, 0.55, rot=(90, 0, 0), verts=64, bevel=0.14, segs=4)
    G.T(body, G.VINYL_RED, name="ClockBody")
    face = G.cyl(0.84, 0.06, loc=(0, -0.28, 0), rot=(90, 0, 0), verts=64, bevel=0.02)
    G.T(face, G.PAPER, name="Face")
    bezel = G.torus(0.86, 0.06, loc=(0, -0.28, 0), rot=(90, 0, 0), segs=64, rsegs=8)
    G.T(bezel, G.CHROME, "Metal", name="Bezel", gloss=0.3)
    ticks = []
    for k in range(12):
        a = math.radians(90 - 30 * k)
        L = 0.14 if k % 3 == 0 else 0.07
        ticks.append(G.rod((0.7 * math.cos(a), -0.31, 0.7 * math.sin(a)), ((0.7 - L) * math.cos(a), -0.31, (0.7 - L) * math.sin(a)), 0.03, verts=8))
    G.T(ticks, G.INK_SOFT, name="Tick")
    h = G.puffy(G.heart(0.3, 48, cz=-0.32), 0.14, y=-0.32)
    G.T(h, HEART, name="FaceHeart")
    hands = [G.puffy(G.stroke([(0, 0), (0.0, 0.52)], 0.07), 0.05, y=-0.35), G.puffy(G.stroke([(0, 0), (0.36, 0.18)], 0.08), 0.05, y=-0.37)]
    hub = G.cyl(0.07, 0.06, loc=(0, -0.38, 0), rot=(90, 0, 0), verts=16, bevel=0.02)
    G.T(hands + [hub], G.INK_SOFT, name="Hand")
    bells = []
    for s in (1, -1):
        b = G.sphere(0.36, scale=(1, 1, 0.75), segs=24, rings=12)
        G.xform(b, G.Tm(s * 0.66, 0, 0.95) @ G.R(ry=s * 35))
        bells.append(b)
    hammer = G.rod((0, 0, 0.98), (0, 0, 1.2), 0.04, verts=8)
    knob = G.sphere(0.08, loc=(0, 0, 1.22))
    legs = [G.rod((s * 0.55, 0.0, -0.75), (s * 0.82, 0.0, -1.15), 0.08, verts=10) for s in (1, -1)]
    G.T(bells + [hammer, knob] + legs, G.CHROME, "Metal", name="Bells", gloss=0.3)
    plus = badge("+", col=G.GREEN, loc=(0.92, -0.45, -0.78), r=0.34, size=0.6)
    G.face_cam(family=FAM, reveal=14, tilt=6)


def ghost(col="#EEF5FF"):
    import fam_hud
    g = G.puffy(fam_hud.ghost_outline(), 0.6, puff=0.46)
    G.T(g, col, name="Ghost")
    return g


@shop("Pass_GP_POLTERGEIST")
def poltergeist():
    ghost()
    # mischievous face: half-closed eyes, raised brow, sly grin
    lids = [G.puffy(G.arc(0.15, 200, 340, 10, x, 0.42) + [(x, 0.36)], 0.1, y=-0.3) for x in (-0.3, 0.3)]
    eyes = [G.puffy(G.circle(0.12, 20, x, 0.32, rz=0.1), 0.1, y=-0.29) for x in (-0.3, 0.3)]
    brow = [G.puffy(G.stroke([(-0.45, 0.6), (-0.18, 0.66)], 0.07), 0.06, y=-0.3),
            G.puffy(G.stroke([(0.17, 0.72), (0.44, 0.62)], 0.07), 0.06, y=-0.3)]
    grin = G.puffy(G.fillet(G.arc(0.32, 200, 340, 12, 0.04, 0.06) + G.arc(0.2, 330, 210, 10, 0.04, 0.0)[::1], 0.02, 1), 0.08, y=-0.3)
    G.T(eyes + brow + [grin], G.INK_SOFT, name="Face")
    G.T(lids, "#D5E2F2", name="Lid")
    # rattling frying pan in its raised arm
    pan = G.lathe([(0.0, 0.0), (0.55, 0.0), (0.66, 0.2), (0.6, 0.2), (0.5, 0.05), (0.0, 0.05)], verts=40)
    G.T(pan, "#3B3F47", name="Pan", smooth=40)
    inside = G.cyl(0.5, 0.02, loc=(0, 0, 0.055), verts=40, bevel=0)
    G.T(inside, GUN := "#4A4F56", name="PanInside")
    handle = G.rod((0.62, 0, 0.14), (1.4, 0, 0.32), 0.07, verts=12)
    grip = G.rod((1.05, 0, 0.25), (1.45, 0, 0.33), 0.1, verts=12)
    G.T(handle, "#2B2D33", name="PanHandle")
    G.T(grip, "#7A5233", name="PanGrip")
    pan_objs = [pan, inside, handle, grip]
    # held by its handle in the ghost's right arm nub, pan raised and tipped toward the camera
    G.xform(pan_objs, G.Tm(1.1, -0.12, -0.14) @ G.R(ry=120) @ G.R(rx=70) @ G.S(1.15) @ G.Tm(-1.45, 0, -0.33))
    arcs = []
    for rr in (0.92, 1.15):
        arcs.append(G.puffy(G.stroke(G.arc(rr, -35, 55, 12, 1.9, 1.3), 0.09), 0.08))
    for rr in (0.45,):
        arcs.append(G.puffy(G.stroke(G.arc(rr, 150, 230, 10, -1.2, 0.0), 0.09), 0.08))
    G.T(arcs, G.CYAN, name="Rattle")
    G.xform(G.tagged(), G.R(ry=-6))
    G.face_cam(family=FAM, reveal=14, tilt=6)


def tactical_light():
    prof = [(0.0, -1.3), (0.2, -1.3), (0.24, -1.24), (0.24, -1.05), (0.21, -1.0), (0.21, 0.3), (0.26, 0.45), (0.4, 0.75),
            (0.44, 0.8), (0.44, 1.02), (0.0, 1.02)]
    body = G.lathe(prof, verts=32)
    G.T(body, "#59606A", "Metal", name="TacBody", gloss=0.42, smooth=40)
    rings = [G.torus(0.215, 0.03, loc=(0, 0, z), segs=28, rsegs=6) for z in (-0.8, -0.65, -0.5, -0.35, -0.2, -0.05)]
    G.T(rings, "#24272C", name="Knurl")
    bands = [G.torus(0.25, 0.035, loc=(0, 0, 0.36), segs=28, rsegs=6), G.torus(0.225, 0.03, loc=(0, 0, -1.02), segs=28, rsegs=6)]
    G.T(bands, G.AMBER, name="TacBand")
    crenel = G.lathe([(0.4, 1.0), (0.47, 1.0), (0.47, 1.12), (0.4, 1.12)], verts=32)
    teeth = [G.box((0.12, 0.1, 0.1), loc=(0.44 * math.cos(a), 0.44 * math.sin(a), 1.16), rot=(0, 0, math.degrees(a)), bevel=0.02, segs=1)
             for a in [2 * math.pi * k / 8 for k in range(8)]]
    G.T([crenel] + teeth, G.STEEL, "Metal", name="Bezel", gloss=0.3)
    lens = G.cyl(0.4, 0.04, loc=(0, 0, 1.06), verts=32, bevel=0.0)
    G.neon(lens, "#FFF6D0", 7.0, name="Lens")
    sw = G.box((0.16, 0.12, 0.2), loc=(0.0, -0.23, 0.05), bevel=0.04, segs=2)
    G.T(sw, G.AMBER, name="Switch")
    clip = G.box((0.06, 0.12, 0.7), loc=(0.0, 0.25, -0.5), bevel=0.02, segs=1)
    G.T(clip, G.STEEL, "Metal", name="Clip", gloss=0.3)
    beam = G.cyl(0.42, 1.9, loc=(0, 0, 1.08 + 0.95), verts=48, bevel=0, r_top=1.25)
    G.glow_mat(beam, "#FFF0B0", 1.5, 0.4, falloff=1.4)
    beam["g2_noframe"] = True
    return beam


@shop("Pass_GP_FLASHLIGHT_PRO")
def flashlight_pro():
    beam = tactical_light()
    objs = G.tagged()
    q = Vector((0, 0, 1)).rotation_difference(Vector((0.8, -0.42, 0.45)).normalized())
    G.xform(objs, q.to_matrix().to_4x4())
    beam["g2_noframe"] = False
    return {}


def apron_parts(col, pocket_col, trim_col, strap_col, depth=0.24):
    import fam_hud
    a = G.puffy(fam_hud.apron_outline(), depth, puff=0.4)
    G.T(a, col, name="Apron")
    strap = G.tube([(-0.3, 0.0, 0.84), (-0.24, 0.0, 1.14), (0.0, -0.02, 1.28), (0.24, 0.0, 1.14), (0.3, 0.0, 0.84)], 0.05, sides=10)
    ties = [G.tube([(s * 0.64, 0.0, 0.16), (s * 0.8, -0.02, 0.0), (s * 0.78, -0.03, -0.3), (s * 0.88, -0.03, -0.55)], 0.045, sides=10)
            for s in (1, -1)]
    G.T([strap] + ties, strap_col, name="Strap")
    trim = G.puffy(G.rrect(0.62, 0.09, 0.04, cz=0.74), 0.05, y=-depth / 2)
    G.T(trim, trim_col, name="Trim")
    return a


@shop("Pass_GP_BIG_POCKETS")
def big_pockets():
    apron_parts(G.BRAND, None, G.MUSTARD, G.MUSTARD)
    for s in (1, -1):
        cx = s * 0.33
        pk = G.sphere(0.36, loc=(cx, -0.1, -0.42), scale=(1.0, 0.62, 0.9), segs=28, rings=16)
        G.T(pk, "#F06A3F", name="Pocket", smooth=70)
        hem = G.tube([(cx - 0.34, -0.2, -0.18), (cx, -0.38, -0.12), (cx + 0.34, -0.2, -0.18)], 0.04, sides=8)
        G.T(hem, G.MUSTARD, name="PocketHem")
    # stuff bulging out: a wrapped sub corner and coins
    sub = G.box((0.34, 0.26, 0.5), loc=(-0.38, -0.22, -0.1), rot=(10, 0, 14), bevel=0.1, segs=3)
    G.T(sub, G.PAPER, name="Wrap")
    stk = G.cyl(0.08, 0.02, loc=(-0.36, -0.36, -0.02), rot=(80, 0, 14), verts=16, bevel=0.005)
    G.T(stk, G.BRAND, name="WrapSticker")
    for k, (x, z, rx) in enumerate(((0.26, -0.08, 70), (0.42, -0.04, 60), (0.34, 0.04, 80))):
        c = coin(scale=0.16)
        put(c, (x, -0.24, z), rx=rx, rz=-20 + 15 * k)
    G.face_cam(family=FAM, reveal=14, tilt=6)


@shop("Pass_GP_MANAGER_KEYS")
def manager_keys():
    import fam_hud
    fam_hud.keyring(((G.GOLD, None, -36), (G.STEEL, None, -10), ("#E8B23A", G.VINYL_RED, 14), (G.STEEL, G.BLUE, 38)), ring_r=0.5)
    tag = G.puffy_holes(G.rrect(1.3, 0.5, 0.25), [G.circle(0.08, 16, -0.5, 0.0)], 0.12, puff=0.4)
    G.T(tag, G.VINYL_RED, name="Fob")
    t = G.text("MANAGER", 0.2, 0.04, loc=(0.08, -0.07, -0.01))
    G.fit_width(t, 0.92)
    G.T(t, G.PAPER, name="FobText")
    link = G.torus(0.12, 0.025, loc=(-0.5, 0, 0.0), rot=(0, 90, 0), segs=16, rsegs=6)
    G.T(link, G.CHROME, "Metal", name="FobLink", gloss=0.3)
    G.xform([tag, t, link], G.Tm(-0.55, -0.12, 0.3) @ G.R(ry=58) @ G.Tm(0.5, 0, 0))
    G.face_cam(family=FAM, reveal=16, tilt=6)


def cap(col, brim_col, loc=(0, 0, 0), rot=(0, 0, 0)):
    dome = G.sphere(0.55, scale=(1.0, 1.05, 0.78), segs=32, rings=16)
    G.boolean(dome, G.box((2, 2, 1), loc=(0, 0, -0.5), bevel=0.0))
    G.T(dome, col, name="CapDome", smooth=60)
    brim = G.slab_xy(G.fillet([(-0.5, -0.2), (0.5, -0.2), (0.45, -0.75), (0.0, -0.9), (-0.45, -0.75)], 0.12, 4), 0.06, bevel=0.025)
    G.T(brim, brim_col, name="CapBrim")
    button = G.sphere(0.07, loc=(0, 0, 0.43))
    G.T(button, brim_col, name="CapButton")
    objs = [dome, brim, button]
    G.xform(objs, G.Tm(*loc) @ G.R(*rot))
    return objs


def spatula(handle_col, blade_col=G.STEEL, handle="wood", glow=False):
    blade = G.slab_holes(G.rrect(0.62, 0.7, 0.08), [G.rrect(0.07, 0.4, 0.03, cx=x, cz=0.04) for x in (-0.16, 0.0, 0.16)], 0.05, bevel=0.015)
    G.T(blade, blade_col, "Metal", name="Blade", gloss=0.32)
    shank = G.rod((0, 0, -0.35), (0, 0.06, -0.75), 0.04, verts=10)
    G.T(shank, blade_col, "Metal", name="Shank", gloss=0.32)
    if handle == "bone":
        hd = G.rod((0, 0.06, -0.75), (0, 0.06, -1.55), 0.07, verts=14)
        knobs = [G.sphere(0.1, loc=(dx, 0.06, -1.6)) for dx in (-0.07, 0.07)] + [G.sphere(0.09, loc=(dx, 0.06, -0.78)) for dx in (-0.06, 0.06)]
        G.T([hd] + knobs, "#EFE6D2", name="Bone")
        parts = [hd] + knobs
    else:
        hd = G.rod((0, 0.06, -0.75), (0, 0.06, -1.55), 0.085, verts=14)
        if glow:
            G.neon(hd, handle_col, 4.0, name="NeonHandle")
        else:
            G.T(hd, handle_col, name="Handle")
        parts = [hd]
    return [blade, shank] + parts


@shop("Pass_GP_PACK_NEON")
def pack_neon():
    apron_parts("#1E2233", None, G.CYAN, G.PINK)
    import fam_hud
    edge = G.tube([(x, -0.0, z) for x, z in fam_hud.apron_outline()] + [tuple((fam_hud.apron_outline()[0][0], 0.0, fam_hud.apron_outline()[0][1]))],
                  0.04, sides=8, res=1)
    G.xform(edge, G.Tm(0, -0.12, 0))
    G.neon(edge, G.PINK, 4.0, name="NeonEdge")
    pk = G.tube([(x, -0.14, z) for x, z in G.rrect(0.9, 0.36, 0.08, cz=-0.42)] + [(G.rrect(0.9, 0.36, 0.08, cz=-0.42)[0][0], -0.14, G.rrect(0.9, 0.36, 0.08, cz=-0.42)[0][1])],
                0.035, sides=8, res=1)
    G.neon(pk, G.CYAN, 4.0, name="NeonPocket")
    c = cap("#1E2233", G.CYAN, loc=(-0.95, -0.55, -1.0), rot=(0, 0, 30))
    for o in c:
        if "CapBrim" in o.name:
            G.neon(o, G.CYAN, 3.0, name="NeonBrim")
    sp = spatula(G.PINK, glow=True)
    G.xform(sp, G.Tm(0.85, -0.5, -0.3) @ G.R(ry=-35) @ G.R(rx=10))
    G.face_cam(family=FAM, reveal=14, tilt=6)


def lantern(loc=(0, 0, 0), s=1.0):
    base = G.cyl(0.42, 0.14, loc=(0, 0, 0.07), verts=8, bevel=0.03)
    top = G.cyl(0.42, 0.12, loc=(0, 0, 1.02), verts=8, bevel=0.03, r_top=0.2)
    cap_ = G.cyl(0.2, 0.18, loc=(0, 0, 1.17), verts=8, bevel=0.03, r_top=0.12)
    bars = [G.rod((0.38 * math.cos(a), 0.38 * math.sin(a), 0.12), (0.38 * math.cos(a), 0.38 * math.sin(a), 0.98), 0.035, verts=6)
            for a in [2 * math.pi * k / 4 + math.pi / 4 for k in range(4)]]
    ring = G.torus(0.26, 0.04, loc=(0, 0, 1.38), rot=(90, 0, 0), segs=24, rsegs=6)
    G.T([base, top, cap_, ring] + bars, "#2B2D33", "Metal", name="Iron", gloss=0.5)
    glass = G.cyl(0.36, 0.86, loc=(0, 0, 0.56), verts=8, bevel=0.0)
    G.T(glass, "#FFB45A", "Neon", name="LanternGlass", emit=2.2, alpha=0.75)
    flame = G.sphere(0.13, loc=(0, 0, 0.52), scale=(1, 1, 1.8))
    G.neon(flame, "#FFF1B0", 6.0, name="Flame")
    objs = [base, top, cap_, ring, glass, flame] + bars
    G.xform(objs, G.Tm(*loc) @ G.S(s))
    return objs


@shop("Pass_GP_PACK_GRAVEYARD")
def pack_graveyard():
    apron_parts("#4A5240", None, "#8C8F7A", "#8C8F7A")
    patches = [G.puffy(G.rrect(0.32, 0.28, 0.05, cx=0.28, cz=-0.62), 0.04, y=-0.12), G.puffy(G.rrect(0.26, 0.22, 0.05, cx=-0.3, cz=0.45), 0.04, y=-0.12)]
    G.T(patches, "#6E5A43", name="Patch")
    stitches = [G.puffy(G.stroke([(x - 0.05, z - 0.05), (x + 0.05, z + 0.05)], 0.025), 0.02, y=-0.15)
                for x, z in ((0.16, -0.5), (0.26, -0.5), (0.36, -0.5), (-0.4, 0.55), (-0.3, 0.55), (-0.2, 0.55))]
    G.T(stitches, G.PAPER_D, name="Stitch")
    rip = G.text("R.I.P.", 0.2, 0.04, loc=(0.0, -0.14, 0.05))
    G.T(rip, G.PAPER_D, name="RIP")
    lantern(loc=(-1.05, -0.45, -1.15), s=0.95)
    sp = spatula(None, handle="bone")
    G.xform(sp, G.Tm(0.85, -0.5, -0.3) @ G.R(ry=-35) @ G.R(rx=10))
    G.face_cam(family=FAM, reveal=14, tilt=6)
