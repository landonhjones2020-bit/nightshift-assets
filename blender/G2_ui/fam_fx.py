"""fam_fx — the tutorial guide's world FX (group "fx"): the arrow line and the target marker.

FX_GuideArrow  one tile of the guide line (Controllers.Tutorial draws it as camera-facing
               Beams, Config.Tutorial.guide). 512 x 256, one chevron pointing +U (right), so
               the beam's TextureLength = one arrow. Fill is pure white and tinted in game by
               Beam.Color (guide.color); the ink outline stays dark under any tint, which is
               what keeps the line readable on the bright Lobby and the dark Shop alike.
               Rendered face-on and orthographic: a beam tile must have no perspective.
FX_GuideMarker the bouncing arrow over the target (and, rotated, the UI pointer): a chunky
               down arrow in the guide yellow with an ink outline, in the HUD glyph look.
"""
from __future__ import annotations

import contextlib
import io
import math
import os

import bpy

import _common as G
from _common import ns, Vector

FAM = "fx"
GUIDE_YELLOW = "#FFD23F"
G.FAMILY.setdefault(FAM, dict(G.FAMILY["hud"], fill=0.9))

CHEVRON = [(-0.34, 0.62), (0.3, 0.0), (-0.34, -0.62)]


def offset(pts, d):
    """Mitred outward offset of a simple polygon [(x, z)...] by d."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1.0 if area < 0 else -1.0   # outward normal side for this winding
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0 = Vector((-e0.y, e0.x)) * sgn
        n1 = Vector((-e1.y, e1.x)) * sgn
        b = (n0 + n1).normalized()
        out.append(tuple(p1 + b * d / max(0.3, b.dot(n0))))
    return out


def fx(name, **opts):
    return G.icon(name, "fx", FAM, **opts)


def _tile_render(name, draft):
    """Orthographic, face-on render of x in [-1, 1], z in [-0.5, 0.5] at 2:1."""
    w, h = (256, 128) if draft else (512, 256)
    ns._setup_render(w, 12 if draft else 64, transparent=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.world.node_tree.nodes.get("Background").inputs[1].default_value = 0.55
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.exposure = 0.0
    G._icon_materials()
    cd = bpy.data.cameras.new("PreviewCam")
    cd.type = "ORTHO"
    cd.ortho_scale = 2.0
    cd.clip_start, cd.clip_end = 0.1, 40.0
    cam = bpy.data.objects.new("PreviewCam", cd)
    sc.collection.objects.link(cam)
    cam.location = Vector((0, -10, 0))
    cam.rotation_euler = (math.radians(90), 0, 0)
    sc.camera = cam
    # soft key from upper left, broad fill: the chevron reads as a soft-plastic pillow
    ns._light("Key", "AREA", (-3.0, -6.0, 4.0), 900, size=5.0, target=(0, 0, 0))
    ns._light("Fill", "AREA", (3.5, -6.0, -1.0), 380, size=7.0, target=(0, 0, 0))
    out = os.path.join(G.DRAFT_DIR if draft else os.path.join(G.REPO, "icons", "fx"), f"{name}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out
    with contextlib.redirect_stdout(io.StringIO()):
        bpy.ops.render.render(write_still=True)
    ns._clear_rig()
    return out


@fx("FX_GuideArrow", kind="tile")
def guide_arrow():
    fill = G.puffy(G.fillet(G.stroke(CHEVRON, 0.36, cap_round=True), 0.03, 2), 0.3)
    G.T(fill, "#FFFFFF", name="Chevron")
    rim = G.slab(G.stroke(CHEVRON, 0.36 + 0.13, cap_round=True), 0.12, y=0.12)
    G.T(rim, G.INK, name="Rim")
    return {"render": lambda draft: _tile_render("FX_GuideArrow", draft)}


@fx("FX_GuideMarker", cam=dict(exposure=1.0, kick=0.6))
def guide_marker():
    # down arrow: a short shaft and a wide head, pillowed
    arrow = [(-0.3, 0.95), (0.3, 0.95), (0.3, 0.12), (0.72, 0.12), (0.0, -0.9), (-0.72, 0.12), (-0.3, 0.12)]
    body = G.fillet(arrow, 0.12, 3)
    G.T(G.puffy(body, 0.46), GUIDE_YELLOW, name="Arrow")
    # outline: the same arrow grown outward, thinner and set behind
    G.T(G.slab(G.fillet(offset(arrow, 0.11), 0.16, 3), 0.2, y=0.2), G.INK, name="Rim")
    G.face_cam(family="hud", reveal=10, tilt=4)
