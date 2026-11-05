"""FX_ScareTextures — the jumpscare overlays (group "fx"), drawn procedurally in 2D.

Landon, 2026-11-05: "let's make the jump scares more intense and have a unique one for each
special character". Controllers.Jumpscare layers these over the in-world scare
(Config.Jumpscares); every one is white or neutral so the game tints it (ImageColor3):

FX_ScarePaper   1024 x 1024  Paperface: crumpled paper with a torn hole in the middle (alpha
                0 in the hole). Scaled from 1.3x the screen width (a small hole to peek
                through) to ~12x it bursts open; tinted with the creature's bag colour.
FX_ScareFrost   1024 x 1024  the Shiver: frost creeping in from every edge, clear centre.
FX_ScareCracks  1024 x 1024  the Shiver: the screen cracking like ice, from the middle out.
FX_ScareStatic   512 x  512  Lights-Out (and the Copy): TV static, tileable.

No Blender scene: numpy + PIL only (run it with the bpy venv so nslib can write the NSZ
payloads and register them in manifests/icons.json, like every other icon).

    NS_EXPORT=1 /home/claude/bpyenv/bin/python blender/G2_ui/FX_ScareTextures.py
"""
from __future__ import annotations

import glob
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
try:  # the bpy venv may not ship Pillow: borrow the system interpreter's copy
    import PIL  # noqa: F401
except ImportError:
    _v = f"python{sys.version_info.major}.{sys.version_info.minor}"
    for _sp in glob.glob(f"/usr/local/lib/{_v}/site-packages") + glob.glob(f"/usr/lib/{_v}/site-packages") \
            + glob.glob(f"/usr/lib/python3/dist-packages"):
        if os.path.isdir(os.path.join(_sp, "PIL")) and _sp not in sys.path:
            sys.path.append(_sp)
            break

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "icons", "fx")
PREVIEW = os.path.join(REPO, "..", "previews", "G2_ui", "scare")


def value_noise(size: int, cells: int, rng: np.random.Generator) -> np.ndarray:
    """Smooth 0..1 noise: a cells x cells random grid, bicubic-upsampled (tileable enough)."""
    grid = rng.random((cells, cells)).astype(np.float32)
    im = Image.fromarray((grid * 255).astype(np.uint8), "L").resize((size, size), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32) / 255.0


def fbm(size: int, rng: np.random.Generator, octaves=((4, 0.5), (9, 0.25), (20, 0.15), (48, 0.1))) -> np.ndarray:
    total = np.zeros((size, size), np.float32)
    weight = 0.0
    for cells, w in octaves:
        total += value_noise(size, cells, rng) * w
        weight += w
    return total / weight


# ---------------------------------------------------------------------------------------
# Paper with a torn hole
# ---------------------------------------------------------------------------------------

def paper(size=1024, seed=5) -> Image.Image:
    rng = np.random.default_rng(seed)
    pr = random.Random(seed)
    base = np.array([238, 233, 222], np.float32)
    shade = (fbm(size, rng) - 0.5) * 70.0                      # crumpled lumps
    # creases: lines across the sheet, light on one side and dark on the other
    crease = np.zeros((size, size), np.float32)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    for _ in range(9):
        a = pr.uniform(0, math.pi)
        nx, ny = math.cos(a), math.sin(a)
        c = pr.uniform(-0.45, 0.45) * size
        # a crease that wanders (it follows the crumple noise instead of a ruler)
        d = (xx - size / 2) * nx + (yy - size / 2) * ny - c + (value_noise(size, 5, rng) - 0.5) * size * 0.12
        w = pr.uniform(5.0, 14.0)
        k = pr.uniform(5.0, 11.0)
        crease += np.sign(d) * k * np.exp(-np.abs(d) / w)
    fibre = (rng.random((size, size)).astype(np.float32) - 0.5) * 5.0
    lum = shade + crease + fibre
    rgb = np.clip(base[None, None, :] + lum[:, :, None], 0, 255)

    # the hole: a jagged ring of torn teeth around the middle, plus a few tears running out
    cx = cy = size / 2
    r0 = size * 0.072
    ang = np.arctan2(yy - cy, xx - cx)
    dist = np.hypot(xx - cx, yy - cy)
    n = 360
    radius = np.zeros(n, np.float32)
    wob = [pr.uniform(0, 2 * math.pi) for _ in range(4)]
    for i in range(n):
        t = 2 * math.pi * i / n
        radius[i] = r0 * (1 + 0.22 * math.sin(2 * t + wob[0]) + 0.14 * math.sin(3 * t + wob[1])
                          + 0.07 * math.sin(7 * t + wob[2]) + 0.04 * math.sin(13 * t + wob[3]))
    teeth = 90
    for k in range(teeth):                                       # small torn teeth, ragged
        c = pr.uniform(0, n)
        half = pr.uniform(0.8, 2.6)
        amp = r0 * pr.uniform(0.03, 0.14) * (1 if pr.random() < 0.5 else -1)
        for j in range(int(c - half * 2), int(c + half * 2) + 1):
            f = max(0.0, 1 - abs(j - c) / (half * 2))
            radius[j % n] += amp * f
    idx = ((ang + math.pi) / (2 * math.pi) * n).astype(np.int32) % n
    edge = radius[idx]
    inside = dist - edge                                         # < 0 in the hole
    alpha = np.clip(inside * 0.9, 0, 1)                          # ~1 px anti-aliased edge
    # torn fringe: the paper's lighter inside shows along the tear, with loose fibres
    fringe = np.clip(1 - inside / (size * 0.009), 0, 1) * (inside > 0)
    fibres = rng.random((size, size)).astype(np.float32)
    rgb = rgb + (fringe * 22)[:, :, None]
    alpha = np.where((inside > 0) & (inside < size * 0.006) & (fibres < 0.35), alpha * 0.55, alpha)
    # the paper curls back around the hole: a soft shadow just outside the fringe
    curl = np.clip(1 - np.abs(inside - size * 0.03) / (size * 0.03), 0, 1) * (inside > 0)
    rgb = rgb - (curl * 26)[:, :, None]
    # tears running out from the hole
    tear = Image.new("L", (size, size), 0)
    td = ImageDraw.Draw(tear)
    for _ in range(3):
        a = pr.uniform(0, 2 * math.pi)
        r = r0 * 0.9
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        length = pr.uniform(0.05, 0.1) * size
        steps = 10
        for st in range(steps):                                  # tapering as it runs out
            a += pr.uniform(-0.25, 0.25)
            nx2 = x + math.cos(a) * length / steps
            ny2 = y + math.sin(a) * length / steps
            td.line([(x, y), (nx2, ny2)], fill=255, width=max(1, int(6 * (1 - st / steps))))
            x, y = nx2, ny2
    tear_a = np.asarray(tear.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255.0
    alpha = alpha * (1 - tear_a * 0.92)
    rgb = rgb - (np.clip(np.asarray(tear.filter(ImageFilter.GaussianBlur(4)), np.float32) / 255.0, 0, 1) * 30)[:, :, None]
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


# ---------------------------------------------------------------------------------------
# Frost from the edges
# ---------------------------------------------------------------------------------------

def frost(size=1024, seed=9) -> Image.Image:
    rng = np.random.default_rng(seed)
    pr = random.Random(seed)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = (xx - size / 2) / (size / 2)
    v = (yy - size / 2) / (size / 2)
    # distance to the nearest edge, roughened so the frost line is ragged
    edge = 1 - np.maximum(np.abs(u), np.abs(v))
    rough = fbm(size, rng, ((6, 0.5), (14, 0.3), (40, 0.2)))
    d = edge + (rough - 0.5) * 0.22
    mist = np.clip(1 - d / 0.42, 0, 1) ** 1.6                    # the frosted band
    # crystals: dendrites growing in from the edges
    cr = Image.new("L", (size, size), 0)
    dr = ImageDraw.Draw(cr)

    def branch(x, y, a, length, width, depth):
        if depth > 4 or length < 6:
            return
        steps = max(2, int(length / 7))
        for _ in range(steps):
            nx = x + math.cos(a) * length / steps
            ny = y + math.sin(a) * length / steps
            dr.line([(x, y), (nx, ny)], fill=pr.randint(150, 255), width=max(1, int(width)))
            if pr.random() < 0.28:
                side = pr.choice((-1, 1))
                branch(nx, ny, a + side * math.radians(60), length * 0.45, width * 0.7, depth + 1)
            x, y = nx, ny
            a += pr.uniform(-0.12, 0.12)

    for _ in range(230):
        side = pr.randrange(4)
        t = pr.uniform(0, size)
        x, y, a = {0: (t, 0, math.pi / 2), 1: (t, size, -math.pi / 2), 2: (0, t, 0), 3: (size, t, math.pi)}[side]
        a += pr.uniform(-0.6, 0.6)
        branch(x, y, a, pr.uniform(0.08, 0.3) * size, pr.uniform(1.5, 3.2), 0)
    crystals = np.asarray(cr.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255.0
    crystals *= np.clip(1 - d / 0.55, 0, 1)
    speck = (rng.random((size, size)) < 0.012).astype(np.float32) * np.clip(1 - d / 0.5, 0, 1)
    a = np.clip(mist * 0.78 + crystals * 0.95 + speck * 0.8, 0, 1)
    tint = np.clip(0.75 + crystals * 0.25, 0, 1)
    rgb = np.dstack([215 + 40 * tint, 236 + 19 * tint, 255 * np.ones_like(tint)])
    out = np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


# ---------------------------------------------------------------------------------------
# Cracks from the middle
# ---------------------------------------------------------------------------------------

def cracks(size=1024, seed=17) -> Image.Image:
    pr = random.Random(seed)
    big = 2 * size                                                # drawn at 2x, then down
    line = Image.new("L", (big, big), 0)
    shadow = Image.new("L", (big, big), 0)
    dl = ImageDraw.Draw(line)
    ds = ImageDraw.Draw(shadow)
    cx = cy = big / 2
    spokes = []
    n = 12
    for i in range(n):
        a = 2 * math.pi * i / n + pr.uniform(-0.18, 0.18)
        x, y = cx + pr.uniform(-6, 6), cy + pr.uniform(-6, 6)
        pts = [(x, y)]
        heading = a
        while math.hypot(x - cx, y - cy) < big * 0.75:
            step = pr.uniform(30, 90)
            heading = a + max(-0.22, min(0.22, heading - a + pr.uniform(-0.12, 0.12)))
            x += math.cos(heading) * step
            y += math.sin(heading) * step
            pts.append((x, y))
        spokes.append(pts)
        w = pr.choice((5, 6, 7))
        ds.line([(x + 3, y + 3) for x, y in pts], fill=200, width=w + 4, joint="curve")
        dl.line(pts, fill=255, width=w, joint="curve")
        # side cracks off the spoke
        for k in range(2, len(pts) - 1, 3):
            if pr.random() < 0.55:
                x, y = pts[k]
                b = a + pr.choice((-1, 1)) * pr.uniform(0.5, 1.1)
                sub = [(x, y)]
                sx, sy = x, y
                for _ in range(pr.randint(2, 5)):
                    st = pr.uniform(20, 50)
                    b += pr.uniform(-0.15, 0.15)
                    sx += math.cos(b) * st
                    sy += math.sin(b) * st
                    sub.append((sx, sy))
                dl.line(sub, fill=235, width=max(2, w - 3), joint="curve")
    # the spider web: broken rings between neighbouring spokes
    for ring in (0.06, 0.13, 0.22, 0.34):
        for i in range(n):
            if pr.random() < 0.75:
                p, q = spokes[i], spokes[(i + 1) % n]
                rr = ring * big
                pa = min(p, key=lambda pt: abs(math.hypot(pt[0] - cx, pt[1] - cy) - rr))
                qa = min(q, key=lambda pt: abs(math.hypot(pt[0] - cx, pt[1] - cy) - rr))
                mid = ((pa[0] + qa[0]) / 2 + pr.uniform(-10, 10), (pa[1] + qa[1]) / 2 + pr.uniform(-10, 10))
                dl.line([pa, mid, qa], fill=220, width=pr.choice((3, 4)), joint="curve")
    # the impact: a bright, shattered patch in the middle
    dl.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=170)
    line = line.resize((size, size), Image.LANCZOS)
    shadow = shadow.resize((size, size), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2))
    la = np.asarray(line, np.float32) / 255.0
    sa = np.asarray(shadow, np.float32) / 255.0 * 0.5
    a = np.clip(la + sa * (1 - la), 0, 1)
    lum = np.where(la > 0.05, 255, 30).astype(np.float32)        # white cracks, dark shadow
    rgb = np.dstack([lum, lum, lum])
    out = np.dstack([rgb, a * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


# ---------------------------------------------------------------------------------------
# TV static
# ---------------------------------------------------------------------------------------

def static(size=512, seed=23) -> Image.Image:
    rng = np.random.default_rng(seed)
    noise = rng.random((size, size)).astype(np.float32)
    rows = 0.85 + 0.15 * np.sin(np.arange(size, dtype=np.float32)[:, None] * math.pi / 2)   # scan lines
    lum = np.clip(noise * rows * 255, 0, 255)
    out = np.dstack([lum, lum, lum, np.full_like(lum, 215)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


TEXTURES = {
    "FX_ScarePaper": paper,
    "FX_ScareFrost": frost,
    "FX_ScareCracks": cracks,
    "FX_ScareStatic": static,
}


def contact_sheet(paths):
    tiles = []
    for p in paths:
        im = Image.open(p).convert("RGBA").resize((384, 384), Image.LANCZOS)
        bg = Image.new("RGBA", im.size, (40, 46, 58, 255))   # a dark backdrop shows the alpha
        bg.alpha_composite(im)
        tiles.append(bg.convert("RGB"))
    sheet = Image.new("RGB", (384 * len(tiles), 384), (0, 0, 0))
    for i, t in enumerate(tiles):
        sheet.paste(t, (384 * i, 0))
    os.makedirs(PREVIEW, exist_ok=True)
    out = os.path.join(PREVIEW, "scare_textures.png")
    sheet.save(out)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for name, fn in TEXTURES.items():
        im = fn()
        p = os.path.join(OUT, name + ".png")
        im.save(p, optimize=True)
        paths.append(p)
        print(f"[{name}] {im.size[0]} x {im.size[1]} -> {p}")
    print("[sheet]", contact_sheet(paths))
    if os.environ.get("NS_EXPORT") == "1":
        import nslib as ns
        for name, p in zip(TEXTURES, paths):
            entry = ns.export_icon(p, name, "fx")
            print(f"[{name}] nsz {os.path.getsize(p[:-4] + '.nsz') // 1024} KB hash {entry['hash']}")


if __name__ == "__main__":
    main()
