"""fam_portraits — the four Regulars' photo-board portraits (group "portraits"): Portrait_<id>.

Each is the real Regular from blender/D_characters/Character_Regular_<id>.py (its own
build_regular(): body, outfit, accessories and tells), posed on the first frame of the shared
Human "Idle" clip, shot head-and-shoulders like a staff photo: the camera sits a little to the
Regular's left so they look just past the lens (this also shows Mina's name badge and Jo's
helmet sticker), against a muted dusty blue-grey studio backdrop (#384666) lit by a soft pool
behind the head that falls off into a vignette. Opaque 512 x 512 (they are pinned photos).
"""
from __future__ import annotations

import contextlib
import io
import math
import os

import _common as G
from _common import ns, bpy, Vector

BACKDROP = "#384666"
REGULARS = ("gus", "mina", "walt", "jo")
CAM = dict(yaw=16.0, pitch=3.0, fov=19.0, aim=(0.0, -0.05, 4.08), half=1.5)


def build_regular(rid):
    D = G.batch_common("D_characters")
    mod = G.batch_module("D_characters", f"Character_Regular_{rid}")
    with contextlib.redirect_stdout(io.StringIO()):
        D.reset_caches()
        arm = D.make_rig()
        mod.build_regular(arm)
        D.clip_idle(arm)               # Idle clip, frame 0 (scene frame set by Clip.finish)
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    if rid == "mina":
        # the badge's "MINA" is a SurfaceGui in game; the photo shows the real lettering
        badge = next(o for o in ns._tagged_objects() if o.get("ns_role") == "badge")
        lo, hi = ns.bbox_world([badge])
        c = (lo + hi) / 2
        t = G.text("MINA", 0.13, 0.012, loc=(c.x, lo.y - 0.002, c.z - 0.005))
        G.fit_width(t, (hi.x - lo.x) * 0.78)
        G.T(t, "#1F3D73", name="BadgeText")
    return arm


def studio(draft):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 16 if draft else 96
    sc.cycles.use_denoising = True
    res = 128 if draft else 512
    sc.render.resolution_x = res
    sc.render.resolution_y = res
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    r, g, b = (ns.srgb_to_linear(c) for c in ns.hex_rgb(BACKDROP))
    bg.inputs[0].default_value = (r, g, b, 1)
    bg.inputs[1].default_value = 0.35
    # backdrop wall behind the sitter
    bd = G.box((16.0, 0.1, 12.0), loc=(0, 3.2, 4.0), bevel=0.0)
    G.T(bd, BACKDROP, "Fabric", name="Backdrop")
    bd["g2_backdrop"] = True
    # soft pool of light on the backdrop behind the head -> natural vignette
    spot = bpy.data.lights.new("KeyBack", "SPOT")
    spot.energy = 900
    spot.spot_size = math.radians(55)
    spot.spot_blend = 1.0
    spot.shadow_soft_size = 1.5
    so = bpy.data.objects.new("KeyBack", spot)
    sc.collection.objects.link(so)
    so.location = (0.6, 0.6, 7.2)
    so.rotation_euler = (Vector((0.0, 3.1, 4.3)) - so.location).to_track_quat("-Z", "Y").to_euler()


def portrait_lights(c, D, yaw):
    k = math.radians(yaw)
    # key high on the camera's side, big and soft; low fill opposite; hair/rim lights from behind
    ns._light("Key", "AREA", c + Vector((math.sin(k + 0.55), -math.cos(k + 0.55), 0.75)) * D, 95 * D ** 2 / 9, size=D * 0.7, target=c)
    ns._light("Fill", "AREA", c + Vector((math.sin(k - 1.1), -math.cos(k - 1.1), 0.1)) * D, 28 * D ** 2 / 9, size=D * 0.9, target=c)
    ns._light("Rim", "AREA", c + Vector((-0.55, 0.9, 0.55)) * D * 0.5, 70 * D ** 2 / 36, size=D * 0.25, target=c)
    ns._light("RimR", "AREA", c + Vector((0.6, 0.85, 0.35)) * D * 0.5, 45 * D ** 2 / 36, size=D * 0.25, target=c)


def render_portrait(name, draft):
    f = CAM
    c = Vector(f["aim"])
    D = f["half"] / math.tan(math.radians(f["fov"]) / 2)
    cam = G.make_camera(c, D, f["yaw"], f["pitch"], f["fov"])
    portrait_lights(c, D, f["yaw"])
    out = os.path.join(G.DRAFT_DIR if draft else os.path.join(G.REPO, "icons", "portraits"), f"{name}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sc = bpy.context.scene
    sc.render.filepath = out
    sc.render.image_settings.color_mode = "RGBA"
    # soft, low-specular skin and cloth, same rule as the icon rig
    G._icon_materials()
    with contextlib.redirect_stdout(io.StringIO()):
        bpy.ops.render.render(write_still=True)
    return out


def make(rid):
    name = f"Portrait_{rid}"

    def build():
        build_regular(rid)
        studio(draft=False)
        return {"render": lambda draft: (studio_res(draft), render_portrait(name, draft))[1]}

    G.icon(name, "portraits", "portraits", kind="portrait")(build)


def studio_res(draft):
    sc = bpy.context.scene
    sc.cycles.samples = 16 if draft else 96
    res = 128 if draft else 512
    sc.render.resolution_x = res
    sc.render.resolution_y = res


for _rid in REGULARS:
    make(_rid)
