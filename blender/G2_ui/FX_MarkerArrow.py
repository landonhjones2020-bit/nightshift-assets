"""FX_MarkerArrow — the tutorial's pointer arrow (group "fx"), drawn procedurally in 2D.

Landon, 2026-11-05: "the whole tutorial looks very AI — give it its own creative flair", then
"for the arrow make an actual arrow rather than just making it with 3 parts". The tutorial
speaks as the night manager (Config.Tutorial): notes on paper, words run over with a
highlighter, buttons circled in marker. This is the arrow the manager draws at the thing to
press: one bold marker stroke with a gentle swing and a solid head, highlighter yellow with
an ink outline and a soft shadow, so it reads over the bright Lobby and the dark kitchen.

FX_MarkerArrow  256 x 320, pointing DOWN, colours baked in (not tinted).
                Controllers.Tutorial shows it as the UI pointer (Guide.Layer.Pointer, turned
                over under a target near the top of the screen) and under the paper tag over a
                world target (WorldUI.GuideMarker.Arrow).

No Blender scene: numpy + PIL only. The NSZ payload and the manifests/icons.json entry are
written exactly as nslib.export_icon writes them (nslib needs bpy; this doesn't).

    NS_EXPORT=1 python3 blender/G2_ui/FX_MarkerArrow.py
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
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(REPO, "icons", "fx")
PREVIEW = os.path.join(REPO, "..", "previews", "G2_ui", "pointer")
RAW_BASE = "https://raw.githubusercontent.com/landonhjones2020-bit/nightshift-assets/main"

NAME = "FX_MarkerArrow"
W, H = 256, 320
SS = 4  # supersampling: drawn at 4x, then downsampled for clean edges

YELLOW = (255, 210, 63, 255)  # Config.Tutorial guide.color #FFD23F
INK = (26, 18, 6, 255)  # guide.outline #1A1206
SHINE = (255, 246, 201, 150)  # the marker's wet sheen down one side of the stroke

SHAFT_W = 19.0  # half-width of the stroke at the top (px at 1x)
SHAFT_W_END = 23.0  # ... where it meets the head: a marker stroke swells as it lands
INK_T = 9.0  # ink outline width
HEAD_HALF = 58.0  # half the head's base
HEAD_LEN = 74.0  # base to tip
HEAD_BARB = 12.0  # how far the head's corners sweep back past its base


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (
        u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0],
        u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1],
    )


def bezier_tangent(p0, p1, p2, p3, t):
    u = 1 - t
    dx = 3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0])
    dy = 3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1])
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


# The stroke: starts up and to the right, swings out and back, and lands pointing straight
# down with its tip at the middle of the bottom edge (the pointer's anchor is its tip).
P0, P1, P2, P3 = (178.0, 38.0), (216.0, 104.0), (128.0, 128.0), (128.0, 206.0)


def shaft_samples(n=160):
    pts = []
    for i in range(n + 1):
        t = i / n
        x, y = bezier(P0, P1, P2, P3, t)
        w = SHAFT_W + (SHAFT_W_END - SHAFT_W) * (t * t)
        pts.append((x, y, w, t))
    return pts


def head_points(grow=0.0):
    """The head: base centred on the shaft's end, along its end tangent; `grow` widens it
    evenly (the ink outline)."""
    bx, by = P3
    dx, dy = bezier_tangent(P0, P1, P2, P3, 1.0)
    nx, ny = -dy, dx
    tip = (bx + dx * (HEAD_LEN + grow * 1.6), by + dy * (HEAD_LEN + grow * 1.6))
    half = HEAD_HALF + grow * 1.25
    back = HEAD_BARB + grow * 0.6
    left = (bx + nx * half - dx * back, by + ny * half - dy * back)
    right = (bx - nx * half - dx * back, by - ny * half - dy * back)
    # the base dips toward the tip between the corners: the head reads as drawn in one sweep
    mid = (bx + dx * (6 - grow * 0.4), by + dy * (6 - grow * 0.4))
    return [left, tip, right, mid]


def stamp_stroke(draw, samples, extra, color, s=SS):
    for x, y, w, _ in samples:
        r = (w + extra) * s
        draw.ellipse((x * s - r, y * s - r, x * s + r, y * s + r), fill=color)


def fill_head(draw, grow, color, s=SS, round_r=0.0):
    pts = [(x * s, y * s) for x, y in head_points(grow)]
    draw.polygon(pts, fill=color)
    if round_r > 0:  # soft corners: a marker can't draw a needle point
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            draw.line([a, b], fill=color, width=int(round_r * 2 * s))
            r = round_r * s
            draw.ellipse((a[0] - r, a[1] - r, a[0] + r, a[1] + r), fill=color)


def draw_arrow() -> Image.Image:
    big = (W * SS, H * SS)
    samples = shaft_samples()
    # shadow: the ink silhouette, offset and blurred
    shadow = Image.new("RGBA", big, (0, 0, 0, 0))
    d = ImageDraw.Draw(shadow)
    stamp_stroke(d, samples, INK_T, (0, 0, 0, 255))
    fill_head(d, INK_T, (0, 0, 0, 255), round_r=INK_T * 0.6)
    shadow = shadow.filter(ImageFilter.GaussianBlur(6 * SS))
    alpha = shadow.getchannel("A").point(lambda v: int(v * 0.38))
    shadow.putalpha(alpha)
    canvas = Image.new("RGBA", big, (0, 0, 0, 0))
    canvas.alpha_composite(shadow, (5 * SS, 7 * SS))
    # ink outline, then the yellow body
    ink = Image.new("RGBA", big, (0, 0, 0, 0))
    d = ImageDraw.Draw(ink)
    stamp_stroke(d, samples, INK_T, INK)
    fill_head(d, INK_T, INK, round_r=INK_T * 0.6)
    canvas.alpha_composite(ink)
    body = Image.new("RGBA", big, (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    stamp_stroke(d, samples, 0.0, YELLOW)
    fill_head(d, 0.0, YELLOW, round_r=3.0)
    canvas.alpha_composite(body)
    # the wet sheen: a thin lighter streak down the upper side of the stroke
    shine = Image.new("RGBA", big, (0, 0, 0, 0))
    d = ImageDraw.Draw(shine)
    for x, y, w, t in samples:
        if 0.08 < t < 0.78:
            tx, ty = bezier_tangent(P0, P1, P2, P3, t)
            nx, ny = -ty, tx
            ox, oy = x + nx * w * 0.42, y + ny * w * 0.42
            r = w * 0.17 * SS * math.sin(math.pi * (t - 0.08) / 0.7)
            d.ellipse((ox * SS - r, oy * SS - r, ox * SS + r, oy * SS + r), fill=SHINE)
    canvas.alpha_composite(shine.filter(ImageFilter.GaussianBlur(1.2 * SS)))
    return canvas.resize((W, H), Image.LANCZOS)


def write_nsz(png_path: str):
    """nslib.write_nsz: base64("NSZ1" + u16le w + u16le h + zlib(RGBA))."""
    im = Image.open(png_path).convert("RGBA")
    w, h = im.size
    pixels = im.tobytes()
    raw = b"NSZ1" + struct.pack("<HH", w, h) + zlib.compress(pixels, 9)
    nsz_path = os.path.splitext(png_path)[0] + ".nsz"
    with open(nsz_path, "w") as f:
        f.write(base64.b64encode(raw).decode("ascii"))
    return nsz_path, hashlib.sha1(pixels).hexdigest()[:16], w, h


def export_icon(png_path: str, name: str, group: str) -> dict:
    """nslib.export_icon: the NSZ beside the PNG and the manifests/icons.json entry."""
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


def preview(im: Image.Image) -> str:
    """The arrow on the Lobby's dark floor and on paper, at full size and at phone size."""
    tiles = []
    for bg in ((40, 30, 36), (243, 238, 226), (90, 200, 190)):
        t = Image.new("RGBA", (W + 40, H + 40), bg + (255,))
        t.alpha_composite(im, (20, 20))
        small = im.resize((W // 4, H // 4), Image.LANCZOS)
        t.alpha_composite(small, (W - 40, H - 50))
        tiles.append(t.convert("RGB"))
    sheet = Image.new("RGB", ((W + 40) * len(tiles), H + 40))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((W + 40) * i, 0))
    os.makedirs(PREVIEW, exist_ok=True)
    out = os.path.join(PREVIEW, "FX_MarkerArrow_sheet.png")
    sheet.save(out)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    im = draw_arrow()
    p = os.path.join(OUT, NAME + ".png")
    im.save(p, optimize=True)
    print(f"[{NAME}] {W} x {H} -> {p}")
    print("[sheet]", preview(im))
    if os.environ.get("NS_EXPORT") == "1":
        entry = export_icon(p, NAME, "fx")
        print(f"[{NAME}] nsz {os.path.getsize(p[:-4] + '.nsz') // 1024} KB hash {entry['hash']}")


if __name__ == "__main__":
    main()
