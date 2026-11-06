"""UI_Kit — the custom image kit for every screen (group "ui"), drawn procedurally in 2D.

Landon, 2026-11-05: "give everything in the UI its own custom image so that it can compete with
other things in the genre", look "Neon diner + paper" (the Bible's two moods), every screen in
one go. DevTools.UISkin dresses each UIKit element with these (by UIKind), so the art rides on
top of the existing screens and every colour the game sets at runtime still shows through:

UI_Enamel   256 x 128  overlay for the saturated buttons (UIKind Paint): a soft wet gloss band
                       across the top, a rim light, and the darker lip of a pressed-enamel
                       button. Neutral (white/black + alpha): the button's colour shows through.
UI_Tile     256 x 128  overlay for the dark tiles (Tile, Ghost, Close): a quiet sheen, a
                       printed grain and a shade along the bottom.
UI_Gloss    256 x  64  overlay for pills and bar fills: a glassy highlight.
UI_Groove   256 x  64  overlay for bar tracks: the inner shadow of a groove.
UI_Grain    256 x 256  tileable panel surface: fine diner-vinyl stripes and grain (white, low
                       alpha) over the panel's own colour.
UI_Header   512 x 128  a menu's sign band, white (tinted by the panel's accent): bevel light along
                       the top, a shadow along the bottom.
UI_Bulb      64 x  64  one marquee bulb (tiled along the sign band's bottom edge).
UI_Checker   64 x  32  the black-and-cream diner checker (tiled as a trim under the sign).
UI_Close    128 x 128  the close control: a red enamel disc, chrome rim, white X.
UI_Badge     96 x  96  the notification dot: a red enamel disc with a cream rim.
UI_Paper    256 x 256  tileable paper fibre for receipts, tickets and notes (in a shift).
UI_Torn     128 x  32  a torn receipt edge (paper colour, tiled along a receipt's bottom).

Chrome rims are not images: DevTools.UISkin gives each element a UIStroke with a silver
UIGradient, so a rim stays one weight at any size. No Blender scene: numpy + PIL only; the NSZ
payloads and manifests/icons.json entries are written as nslib.export_icon writes them.

    NS_EXPORT=1 python3 blender/G2_ui/UI_Kit.py
"""
from __future__ import annotations

import base64
import hashlib
import json
import math
import os
import struct
import sys
import zlib

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "icons", "ui")
PREVIEW = os.path.join(REPO, "..", "previews", "G2_ui", "kit")
RAW_BASE = "https://raw.githubusercontent.com/landonhjones2020-bit/nightshift-assets/main"
SS = 4

PAPER = (243, 238, 226)  # Bible 13.2 paper
INK = (16, 18, 23)  # ink900


def rgba(arr: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def ramp(n: int, stops) -> np.ndarray:
    """Piecewise-linear ramp over n samples; stops = [(t, value), ...] with t in 0..1."""
    t = np.linspace(0, 1, n)
    ts = [s[0] for s in stops]
    vs = [s[1] for s in stops]
    return np.interp(t, ts, vs)


def noise(w: int, h: int, seed: int, cells: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if cells <= 0:
        return rng.random((h, w)).astype(np.float32)
    g = rng.random((cells, cells)).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8), "L").resize((w, h), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255.0


def tileable_noise(size: int, seed: int, cells: int) -> np.ndarray:
    """Noise that wraps: a cells x cells grid upsampled with wrap-around."""
    rng = np.random.default_rng(seed)
    g = rng.random((cells, cells)).astype(np.float32)
    big = np.tile(g, (3, 3))
    im = Image.fromarray((big * 255).astype(np.uint8), "L").resize((size * 3, size * 3), Image.BICUBIC)
    a = np.asarray(im, np.float32) / 255.0
    return a[size:2 * size, size:2 * size]


def overlay(w: int, h: int, white_alpha: np.ndarray, black_alpha: np.ndarray) -> Image.Image:
    """An overlay built from a white layer and a black layer (alpha 0..1 arrays, h x w)."""
    out = np.zeros((h, w, 4), np.float32)
    wa = np.clip(white_alpha, 0, 1)
    ba = np.clip(black_alpha, 0, 1)
    a = wa + ba * (1 - wa)
    col = np.where(a[..., None] > 1e-6, (255 * wa[..., None]) / np.maximum(a[..., None], 1e-6), 0)
    out[..., 0:3] = col
    out[..., 3] = a * 255
    return rgba(out)


def soft_round_band(w, h, x0, y0, x1, y1, r, blur) -> np.ndarray:
    """A soft rounded-rectangle mask (0..1), drawn at SS and blurred."""
    im = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(im).rounded_rectangle((x0 * SS, y0 * SS, x1 * SS, y1 * SS), r * SS, fill=255)
    im = im.filter(ImageFilter.GaussianBlur(blur * SS)).resize((w, h), Image.LANCZOS)
    return np.asarray(im, np.float32) / 255.0


def ui_enamel() -> Image.Image:
    w, h = 256, 128
    yy = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    band = soft_round_band(w, h, 10, 7, 246, 60, 26, 3.5)
    gloss = band * ramp(h, [(0, 0.46), (0.25, 0.30), (0.5, 0.05), (1, 0)])[:, None]
    rim = np.exp(-((yy - 0.035) / 0.022) ** 2) * 0.30
    lip = ramp(h, [(0, 0), (0.74, 0), (0.86, 0.14), (1, 0.32)])[:, None] * np.ones((1, w))
    # a breath of light along the lower edge, as enamel catches the room
    bounce = np.exp(-((yy - 0.9) / 0.03) ** 2) * 0.07
    return overlay(w, h, gloss + rim + bounce, lip)


def ui_tile() -> Image.Image:
    w, h = 256, 128
    yy = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    sheen = ramp(h, [(0, 0.13), (0.42, 0.03), (0.6, 0)])[:, None] * np.ones((1, w))
    rim = np.exp(-((yy - 0.03) / 0.02) ** 2) * 0.16
    grain = (noise(w, h, 3) - 0.5) * 0.06
    shade = ramp(h, [(0, 0), (0.7, 0), (1, 0.26)])[:, None] * np.ones((1, w))
    return overlay(w, h, sheen + rim + np.maximum(grain, 0), shade + np.maximum(-grain, 0))


def ui_gloss() -> Image.Image:
    w, h = 256, 64
    band = soft_round_band(w, h, 8, 5, 248, 30, 12, 2.0)
    gloss = band * ramp(h, [(0, 0.5), (0.45, 0.12), (0.6, 0)])[:, None]
    shade = ramp(h, [(0, 0), (0.72, 0), (1, 0.24)])[:, None] * np.ones((1, w))
    return overlay(w, h, gloss, shade)


def ui_groove() -> Image.Image:
    w, h = 256, 64
    yy = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    inner = ramp(h, [(0, 0.55), (0.3, 0.12), (0.6, 0)])[:, None] * np.ones((1, w))
    xx = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    sides = (np.exp(-(xx / 0.02) ** 2) + np.exp(-((1 - xx) / 0.02) ** 2)) * 0.25
    low = np.exp(-((yy - 0.94) / 0.05) ** 2) * 0.12
    return overlay(w, h, low, inner + sides)


def ui_grain() -> Image.Image:
    s = 256
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    # diner vinyl: fine diagonal pinstripes (period 16 px, so the tile wraps) and grain
    stripes = (np.sin((xx + yy) * (2 * math.pi / 16)) > 0.86).astype(np.float32) * 0.035
    grain = (tileable_noise(s, 11, 64) - 0.5) * 0.05 + (noise(s, s, 12) - 0.5) * 0.03
    w = stripes + np.maximum(grain, 0)
    b = np.maximum(-grain, 0)
    return overlay(s, s, w, b)


def ui_header() -> Image.Image:
    w, h = 512, 128
    yy = np.linspace(0, 1, h)
    base = np.ones((h, w, 4), np.float32) * 255
    shade = ramp(h, [(0, 1.0), (0.08, 1.0), (0.5, 0.86), (0.88, 0.74), (1, 0.62)])
    light = np.exp(-((yy - 0.06) / 0.035) ** 2) * 0.35
    v = np.clip(shade + light, 0, 1.2)
    base[..., 0:3] = np.clip(v[:, None, None] * 255, 0, 255)
    # a hint of brushed metal in the paint, left to right
    row = np.asarray(Image.fromarray((noise(w, 1, 21, 0) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(2)), np.float32) / 255.0
    streak = (row.repeat(h, 0) - 0.5) * 7
    base[..., 0:3] += streak[..., None]
    return rgba(base)


def ui_bulb() -> Image.Image:
    s = 64
    im = Image.new("RGBA", (s * SS, s * SS), (0, 0, 0, 0))
    glow = Image.new("RGBA", (s * SS, s * SS), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    c = s * SS / 2
    gd.ellipse((c - 24 * SS, c - 24 * SS, c + 24 * SS, c + 24 * SS), fill=(255, 214, 120, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(7 * SS))
    im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    d.ellipse((c - 13 * SS, c - 13 * SS, c + 13 * SS, c + 13 * SS), fill=(52, 38, 30, 255))  # socket
    d.ellipse((c - 10 * SS, c - 10 * SS, c + 10 * SS, c + 10 * SS), fill=(255, 236, 170, 255))
    d.ellipse((c - 6 * SS, c - 7 * SS, c + 3 * SS, c + 1 * SS), fill=(255, 252, 232, 255))  # hot spot
    return im.resize((s, s), Image.LANCZOS)


def ui_checker() -> Image.Image:
    w, h, sq = 64, 32, 16
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for row in range(2):
        for col in range(4):
            dark = (row + col) % 2 == 0
            fill = (24, 24, 30, 255) if dark else (240, 233, 214, 255)
            x0, y0 = col * sq * SS, row * sq * SS
            d.rectangle((x0, y0, x0 + sq * SS - 1, y0 + sq * SS - 1), fill=fill)
            # each square a touch lighter at the top: tiles catch the light
            d.rectangle((x0, y0, x0 + sq * SS - 1, y0 + SS * 2), fill=tuple(min(255, c + 18) for c in fill[:3]) + (255,))
    return im.resize((w, h), Image.LANCZOS)


def disc(size, base, rim_light, rim_dark, glyph=None) -> Image.Image:
    s = size
    S = s * SS
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # drop shadow
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((S * 0.08, S * 0.12, S * 0.94, S * 0.98), fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(S * 0.03)))
    # chrome rim: a vertical silver ramp
    rim = np.zeros((S, S, 4), np.float32)
    ramp_v = ramp(S, [(0, 1.0), (0.45, 0.62), (0.55, 0.82), (1, 0.42)])
    rim[..., 0] = (rim_light[0] * ramp_v)[:, None]
    rim[..., 1] = (rim_light[1] * ramp_v)[:, None]
    rim[..., 2] = (rim_light[2] * ramp_v)[:, None]
    rim[..., 3] = 255
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse((S * 0.04, S * 0.04, S * 0.92, S * 0.92), fill=255)
    rim_im = rgba(rim)
    rim_im.putalpha(mask)
    im.alpha_composite(rim_im)
    # the enamel face
    face = np.zeros((S, S, 4), np.float32)
    fr = ramp(S, [(0, 1.18), (0.5, 1.0), (1, 0.78)])
    for k in range(3):
        face[..., k] = np.clip(base[k] * fr, 0, 255)[:, None]
    face[..., 3] = 255
    fmask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(fmask).ellipse((S * 0.11, S * 0.11, S * 0.85, S * 0.85), fill=255)
    face_im = rgba(face)
    face_im.putalpha(fmask)
    im.alpha_composite(face_im)
    # a dark seam between rim and face
    ImageDraw.Draw(im).ellipse((S * 0.105, S * 0.105, S * 0.855, S * 0.855), outline=rim_dark + (200,), width=int(S * 0.012))
    if glyph:
        glyph(im, S)
    # gloss on the face
    g = Image.new("L", (S, S), 0)
    ImageDraw.Draw(g).ellipse((S * 0.2, S * 0.15, S * 0.76, S * 0.46), fill=110)
    g = g.filter(ImageFilter.GaussianBlur(S * 0.03))
    white = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    white.putalpha(g)
    im.alpha_composite(white)
    return im.resize((s, s), Image.LANCZOS)


def x_glyph(im: Image.Image, S: int):
    d = ImageDraw.Draw(im)
    c = S * 0.48
    r = S * 0.17
    wdt = int(S * 0.085)
    for dx in (1, -1):
        # shadow, then the cream stroke
        d.line((c - r + S * 0.012, c - r * dx + S * 0.02, c + r + S * 0.012, c + r * dx + S * 0.02), fill=(60, 10, 14, 170), width=wdt)
    for dx in (1, -1):
        d.line((c - r, c - r * dx, c + r, c + r * dx), fill=(250, 244, 233, 255), width=wdt)
        for (px, py) in ((c - r, c - r * dx), (c + r, c + r * dx)):
            d.ellipse((px - wdt / 2, py - wdt / 2, px + wdt / 2, py + wdt / 2), fill=(250, 244, 233, 255))


def ui_close() -> Image.Image:
    return disc(128, (214, 66, 78), (236, 238, 242), (40, 20, 22), glyph=x_glyph)


def ui_badge() -> Image.Image:
    return disc(96, (230, 72, 84), (250, 244, 233), (70, 18, 24))


def ui_paper() -> Image.Image:
    s = 256
    fib = tileable_noise(s, 31, 96)
    fine = noise(s, s, 32)
    # fibres: stretched noise along x, wrapped
    streak = tileable_noise(s, 33, 32)
    v = 0.5 + (fib - 0.5) * 0.10 + (fine - 0.5) * 0.06 + (streak - 0.5) * 0.05
    w = np.maximum(v - 0.5, 0) * 0.9
    b = np.maximum(0.5 - v, 0) * 0.9
    return overlay(s, s, w, b)


def ui_torn() -> Image.Image:
    w, h = 128, 32
    S = SS
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(41)
    pts = [(0, 0)]
    teeth = 8
    for i in range(teeth + 1):
        x = i * w / teeth
        pts.append((x * S, (6 + rng.uniform(-1.2, 1.2)) * S))
        if i < teeth:
            pts.append(((x + w / teeth / 2) * S, (22 + rng.uniform(-2.5, 2.5)) * S))
    pts[-1] = (w * S, pts[1][1])  # wrap: the last point matches the first tooth root
    pts.append((w * S, 0))
    d.polygon(pts, fill=PAPER + (255,))
    shadow = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).polygon([(x, y + 2 * S) for x, y in pts], fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.5 * S))
    shadow.alpha_composite(im)
    return shadow.resize((w, h), Image.LANCZOS)


KIT = {
    "UI_Enamel": ui_enamel,
    "UI_Tile": ui_tile,
    "UI_Gloss": ui_gloss,
    "UI_Groove": ui_groove,
    "UI_Grain": ui_grain,
    "UI_Header": ui_header,
    "UI_Bulb": ui_bulb,
    "UI_Checker": ui_checker,
    "UI_Close": ui_close,
    "UI_Badge": ui_badge,
    "UI_Paper": ui_paper,
    "UI_Torn": ui_torn,
}


def write_nsz(png_path: str):
    im = Image.open(png_path).convert("RGBA")
    w, h = im.size
    pixels = im.tobytes()
    raw = b"NSZ1" + struct.pack("<HH", w, h) + zlib.compress(pixels, 9)
    nsz_path = os.path.splitext(png_path)[0] + ".nsz"
    with open(nsz_path, "w") as f:
        f.write(base64.b64encode(raw).decode("ascii"))
    return nsz_path, hashlib.sha1(pixels).hexdigest()[:16], w, h


def export_icon(png_path: str, name: str, group: str) -> dict:
    nsz, digest, w, h = write_nsz(png_path)
    rel = os.path.relpath(nsz, REPO).replace(os.sep, "/")
    entry = {"group": group, "size": [w, h], "hash": digest, "url": f"{RAW_BASE}/{rel}"}
    path = os.path.join(REPO, "manifests", "icons.json")
    man = {}
    if os.path.exists(path):
        with open(path) as f:
            man = json.load(f)
    man[name] = entry
    with open(path, "w") as f:
        json.dump(dict(sorted(man.items())), f, indent=1)
    return entry


def mock(images: dict) -> str:
    """A mock-up of the kit on the game's own colours: a menu, buttons, pills, a bar, a
    receipt. Not a game screen; it shows the pieces together."""
    W, H = 1100, 640
    bg = Image.new("RGBA", (W, H), (30, 26, 40, 255))
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)

    def place(img, box, tile=None, tint=None, radius=0):
        x0, y0, x1, y1 = box
        w, h = x1 - x0, y1 - y0
        if tile:
            t = img
            layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            for yy in range(0, h, t.size[1]):
                for xx in range(0, w, t.size[0]):
                    layer.alpha_composite(t, (xx, yy))
            img2 = layer
        else:
            img2 = img.resize((w, h), Image.LANCZOS)
        if tint:
            arr = np.asarray(img2, np.float32)
            arr[..., 0:3] *= np.array(tint, np.float32)[None, None, :] / 255.0
            img2 = rgba(arr)
        if radius:
            m = Image.new("L", (w, h), 0)
            ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
            a = np.minimum(np.asarray(img2.getchannel("A")), np.asarray(m))
            img2.putalpha(Image.fromarray(a))
        bg.alpha_composite(img2, (x0, y0))

    # the menu panel
    d.rounded_rectangle((60, 60, 640, 580), 18, fill=(23, 26, 32, 255), outline=(200, 205, 214, 255), width=4)
    bg.alpha_composite(panel)
    place(images["UI_Grain"], (62, 62, 638, 578), tile=True, radius=16)
    place(images["UI_Header"], (62, 62, 638, 140), tint=(102, 214, 197), radius=16)
    place(images["UI_Bulb"].resize((24, 24), Image.LANCZOS), (70, 128, 630, 152), tile=True)
    place(images["UI_Checker"].resize((40, 20), Image.LANCZOS), (62, 152, 638, 164), tile=True)
    place(images["UI_Close"], (572, 76, 624, 128))
    # buttons on the panel
    for i, (col, lab) in enumerate((((112, 213, 162), "BUY"), ((239, 106, 152), "GIFT"), ((246, 197, 106), "UPGRADE"))):
        x0 = 100 + i * 180
        ImageDraw.Draw(bg).rounded_rectangle((x0, 470, x0 + 160, 530), 12, fill=col + (255,))
        place(images["UI_Enamel"], (x0, 470, x0 + 160, 530), radius=12)
    for i in range(3):
        x0 = 100 + i * 180
        ImageDraw.Draw(bg).rounded_rectangle((x0, 200, x0 + 160, 420), 14, fill=(35, 39, 47, 255))
        place(images["UI_Tile"], (x0, 200, x0 + 160, 420), radius=14)
    # a pill and a bar
    ImageDraw.Draw(bg).rounded_rectangle((700, 80, 1000, 140), 30, fill=(246, 197, 106, 255), outline=(220, 224, 230, 255), width=3)
    place(images["UI_Gloss"], (700, 80, 1000, 140), radius=30)
    place(images["UI_Badge"], (975, 66, 1015, 106))
    ImageDraw.Draw(bg).rounded_rectangle((700, 170, 1000, 196), 13, fill=(23, 26, 32, 255))
    ImageDraw.Draw(bg).rounded_rectangle((700, 170, 880, 196), 13, fill=(102, 214, 197, 255))
    place(images["UI_Gloss"], (700, 170, 880, 196), radius=13)
    place(images["UI_Groove"], (700, 170, 1000, 196), radius=13)
    # a receipt
    ImageDraw.Draw(bg).rectangle((720, 240, 960, 520), fill=PAPER + (255,))
    place(images["UI_Paper"], (720, 240, 960, 520), tile=True)
    place(images["UI_Torn"], (720, 520, 960, 552), tile=True)
    os.makedirs(PREVIEW, exist_ok=True)
    out = os.path.join(PREVIEW, "UI_Kit_mock.png")
    bg.convert("RGB").save(out)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    images, paths = {}, []
    for name, fn in KIT.items():
        im = fn()
        p = os.path.join(OUT, name + ".png")
        im.save(p, optimize=True)
        images[name] = im
        paths.append((name, p))
        print(f"[{name}] {im.size[0]} x {im.size[1]}")
    print("[mock]", mock(images))
    if os.environ.get("NS_EXPORT") == "1":
        for name, p in paths:
            e = export_icon(p, name, "ui")
            print(f"[{name}] hash {e['hash']}")


if __name__ == "__main__":
    main()
