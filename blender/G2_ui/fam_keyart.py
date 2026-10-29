"""fam_keyart — loading / teleport screen key art (group "art"): Art_KeyArt, 1024 x 576.

The STACKHOUSE diner at night seen from its parking lot, assembled from this project's own
generators (no new architecture): the facade is B_shop's wall modules turned exterior-out with
the ExteriorNight back preset (Shop_BrickWall, Shop_WallWindow, Shop_WallDoorway +
Shop_DoorFront), the STACKHOUSE neon sign, the hanging OPEN sign and a parked car and street
lamp in the lot; booths, pendant lamps and the counter's register glow behind the windows
(B_shop / A_kitchen); Mr. Usual (E_creatures) stands in the rain by the door, and Paperface's
bag face shows in a window. Rain streaks, a wet asphalt lot with puddles that pick up the neon.
The left third is kept dark and calm (receding brick wall, unlit lot) for UI text.
"""
from __future__ import annotations

import contextlib
import io
import math
import os
import random

import _common as G
from _common import ns, bpy, Vector, Matrix

WALL_Y = 0.0                 # facade centre line (exterior face at y = -0.5)
EXT = {"wall_back": "#C9BCA2", "wall_back_base": "#2A2C30", "wall_back_band": "#B8432A"}   # B_shop ExteriorNight
INT = {"wall_upper": "#EFE6D2", "wall_tile": "#6E9E97", "wall_grout": "#DCD0B8", "wall_base": "#2B2D33", "wall_stripe": "#E8502A"}
RES = (1024, 576)


def recolor(objs, table):
    for o in objs:
        r = o.get("ns_role")
        if r in table:
            o["ns_color"] = table[r]
            o.data.materials.clear()
            o.data.materials.append(ns.material(table[r], o["ns_material"]))


def place(objs, x=0.0, y=0.0, z=0.0, rz=0.0, s=1.0):
    G.xform(objs, G.Tm(x, y, z) @ G.R(rz=rz) @ G.S(s))
    return objs


def module(name, x, rz=180.0, batch="B_shop"):
    _, objs = G.build_foreign(batch, name)
    recolor(objs, EXT)
    recolor(objs, INT)
    place(objs, x, WALL_Y, 0.0, rz)
    return objs


def glass_window(objs):
    """Window glass -> clear (we look into the lit room through it)."""
    for o in objs:
        if o.get("ns_role") == "glass":
            G.glass_mat(o, tint="#FFE9C8", centre=0.04, edge=0.35)


# --------------------------------------------------------------------------------------------
# scene
# --------------------------------------------------------------------------------------------

def facade():
    layout = [("Shop_BrickWall", -36.0, 0.0), ("Shop_BrickWall", -28.0, 0.0), ("Shop_BrickWall", -20.0, 0.0),
              ("Shop_BrickWall", -12.0, 0.0), ("Shop_WallWindow", -4.0, 180.0), ("Shop_WallDoorway", 4.0, 180.0),
              ("Shop_WallWindow", 12.0, 180.0), ("Shop_BrickWall", 20.0, 0.0)]
    out = {}
    for name, x, rz in layout:
        objs = module(name, x, rz)
        glass_window(objs)
        out.setdefault(name, []).append((x, objs))
    # door leaf in the doorway (hinge on the left jamb), slightly ajar
    _, door = G.build_foreign("B_shop", "Shop_DoorFront")
    glass_window(door)
    place(door, 4.0 - 2.5, WALL_Y, 0.0, rz=-12)
    # cornice / parapet cap along the roofline, and the dark roof mass behind it
    G.T(G.box((64.0, 1.6, 0.7), loc=(-6.0, WALL_Y - 0.1, 12.3), bevel=0.06), "#2A2C30", name="Cornice")
    G.T(G.box((64.0, 0.3, 0.18), loc=(-6.0, WALL_Y - 0.92, 11.86), bevel=0.04), "#B8432A", name="CorniceBand")
    return out


def interior():
    # floor (black / white checker), ceiling, back wall (cream kitchen preset), booths, lamps
    floor = G.box((48.0, 13.0, 0.2), loc=(0.0, 6.9, -0.1), bevel=0.0)
    m = bpy.data.materials.new("G2_Checker")
    m.use_nodes = True
    nt = m.node_tree
    pb = nt.nodes.get("Principled BSDF")
    ck = nt.nodes.new("ShaderNodeTexChecker")
    ck.inputs["Scale"].default_value = 1.0
    ck.inputs["Color1"].default_value = (0.75, 0.72, 0.66, 1)
    ck.inputs["Color2"].default_value = (0.02, 0.02, 0.025, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.5, 0.5, 0.5)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs[0], ck.inputs["Vector"])
    nt.links.new(ck.outputs["Color"], pb.inputs["Base Color"])
    pb.inputs["Roughness"].default_value = 0.35
    m["g2_custom"] = True
    G.T(floor, "#808080", name="Floor_")
    floor.data.materials.clear()
    floor.data.materials.append(m)
    G.T(G.box((48.0, 13.0, 0.2), loc=(0.0, 6.9, 12.1), bevel=0.0), "#E9E0CC", name="Ceiling")
    for x in (-4.0, 4.0, 12.0):
        objs = module("Shop_Wall", x, rz=0.0)
        place(objs, 0.0, 12.5, 0.0)
    # booths in the two left windows and the OPEN window
    for x in (-4.0, 12.0):
        _, b = G.build_foreign("B_shop", "Shop_Booth")
        place(b, x, 3.35, 0.0, rz=180)
    # pendant lamps over the booths
    for x in (-4.0, 12.0, 4.0):
        _, lamp = G.build_foreign("B_shop", "Shop_PendantLamp")
        place(lamp, x, 3.4 if x != 4.0 else 6.0, 12.0)
        for o in lamp:
            if o.get("ns_role") == "lamp":
                G.neon(o, "#FFD9A0", 8.0, name="Bulb")
        pl = bpy.data.lights.new(f"Lamp{x}", "POINT")
        pl.energy = 260
        pl.color = (1.0, 0.78, 0.5)
        pl.shadow_soft_size = 0.4
        po = bpy.data.objects.new(f"Lamp{x}", pl)
        bpy.context.scene.collection.objects.link(po)
        po.location = (x, 3.4 if x != 4.0 else 6.0, 8.4)
    # the counter + register seen through the open door
    _, counter = G.build_foreign("B_shop", "Shop_Counter")
    place(counter, 6.0, 8.5, 0.0, rz=180)
    _, reg = G.build_foreign("A_kitchen", "Kitchen_Register")
    place(reg, 5.0, 8.4, 3.0, rz=200)


def signs():
    _, neon = G.build_foreign("B_shop", "Shop_NeonSign")
    place(neon, 4.0, WALL_Y - 0.5, 9.25, s=0.92)
    for o in neon:
        if o.get("ns_role") == "neon":
            G.neon(o, o["ns_color"], 7.0, name="NeonTube")
    _, op = G.build_foreign("B_shop", "Shop_OpenSign")
    place(op, 12.0, WALL_Y + 0.6, 5.6, rz=0)
    for o in op:
        if o.get("ns_role") == "neon":
            G.neon(o, o["ns_color"], 8.0, name="OpenTube")


def lot():
    # sidewalk + curb (wet concrete), asphalt lot (wet, glossy), parking stripes, puddles
    G.T(G.box((80.0, 5.0, 0.3), loc=(-6.0, -3.0, 0.15), bevel=0.04), "#4E5056", name="Sidewalk", gloss=0.35)
    G.T(G.box((80.0, 0.4, 0.34), loc=(-6.0, -5.55, 0.17), bevel=0.06), "#6A6C70", name="Curb", gloss=0.35)
    G.T(G.box((160.0, 120.0, 0.2), loc=(-6.0, -65.0, -0.1), bevel=0.0), "#17191F", name="Asphalt", gloss=0.16)
    stripes = [G.box((0.3, 9.0, 0.02), loc=(x, -11.5, 0.01), bevel=0.0) for x in (-26.0, -14.0, -2.0, 10.0, 22.0)]
    G.T(stripes, "#8C7A3A", name="Stripe", gloss=0.3)
    rnd = random.Random(7)
    pud = []
    for x, y, rx, ry in ((6.0, -9.5, 3.2, 1.4), (14.0, -13.0, 2.4, 1.0), (-2.0, -15.0, 3.8, 1.5), (1.0, -7.4, 1.6, 0.6), (18.0, -8.2, 2.0, 0.8)):
        pts = [(x + rx * math.cos(a) * (1 + 0.12 * math.sin(3 * a + x)), y + ry * math.sin(a) * (1 + 0.1 * math.cos(2 * a)))
               for a in [2 * math.pi * k / 40 for k in range(40)]]
        pud.append(G.slab_xy(pts, 0.012, z=0.0))
    G.T(pud, "#0C0E14", name="Puddle", gloss=0.02)
    # a parked car in the dark left of the lot, a street lamp on the right
    _, car = G.build_foreign("B_shop", "Shop_ParkedCar")
    place(car, -31.0, -11.0, 0.0, rz=74)
    recolor(car, {"car_paint": "#3A2A33"})
    _, lamp = G.build_foreign("B_shop", "Shop_StreetLamp")
    place(lamp, 24.0, -12.0, 0.0, rz=200)
    for o in lamp:
        if o.get("ns_role") == "lamp":
            G.neon(o, "#FFB25C", 5.0, name="Sodium")
    return lamp


def creatures():
    C = G.batch_common("E_creatures")
    mu = G.batch_module("E_creatures", "Creature_MrUsual")
    with contextlib.redirect_stdout(io.StringIO()):
        sk = C.Skel("MrUsualRig", mu.JOINTS)
        before = set(G.tagged())
        mu.build_model(sk)
        C.rest_pose(sk.arm)
    usual = [o for o in G.tagged() if o not in before]
    bpy.context.view_layer.update()
    G.xform([sk.arm], G.Tm(9.6, -2.6, 0.3) @ G.R(rz=-28))
    pf = G.batch_module("E_creatures", "Creature_Paperface")
    with contextlib.redirect_stdout(io.StringIO()):
        sk2 = C.Skel("PaperfaceRig", pf.JOINTS)
        pf.build_model(sk2)
        C.rest_pose(sk2.arm)
    bpy.context.view_layer.update()
    G.xform([sk2.arm], G.Tm(-2.3, 1.45, 0.0) @ G.R(rz=26))
    return sk.arm, sk2.arm


def rain(n=3400, seed=3):
    """Thin falling streaks between the camera and the building (one mesh), lit by the scene."""
    import bmesh
    rnd = random.Random(seed)
    bm = bmesh.new()
    for i in range(n):
        y = rnd.uniform(-34.0, -1.0)
        x = rnd.uniform(-40.0, 30.0)
        z = rnd.uniform(0.0, 22.0)
        L = rnd.uniform(0.7, 1.4)
        w = 0.022
        d = Vector((0.12, 0.0, -1.0)).normalized() * L
        a = Vector((x, y, z))
        b = a + d
        side = Vector((w, 0, 0))
        vs = [bm.verts.new(a - side), bm.verts.new(a + side), bm.verts.new(b + side), bm.verts.new(b - side)]
        bm.faces.new(vs)
    o = ns.from_bmesh(bm, "Rain")
    G.T(o, "#DCE8FF", name="Rain", gloss=0.2, alpha=0.5, shadow=False)
    return o


def light_rig():
    sc = bpy.context.scene
    world = sc.world or bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes.get("Background")
    bg.inputs[1].default_value = 1.0
    # night sky: faint warm-grey town glow at the horizon fading to deep navy overhead
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.035, 0.035, 0.05, 1)
    cr.elements[1].position = 0.45
    cr.elements[1].color = (0.006, 0.009, 0.022, 1)
    e = cr.elements.new(0.08)
    e.color = (0.03, 0.032, 0.055, 1)
    nt.links.new(ramp.outputs["Color"], bg.inputs[0])

    def area(name, loc, target, energy, size, color, shape="RECTANGLE", size_y=None):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy
        ld.size = size
        ld.shape = shape
        if size_y:
            ld.size_y = size_y
        ld.color = color
        ob = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(ob)
        ob.location = Vector(loc)
        ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()
        return ob

    def spot(name, loc, target, energy, angle, color, blend=0.8, soft=0.5):
        ld = bpy.data.lights.new(name, "SPOT")
        ld.energy = energy
        ld.spot_size = math.radians(angle)
        ld.spot_blend = blend
        ld.shadow_soft_size = soft
        ld.color = color
        ob = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(ob)
        ob.location = Vector(loc)
        ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()
        return ob

    warm = (1.0, 0.72, 0.42)
    # interior fill (ceiling panels) so the windows glow warm
    for x in (-4.0, 4.0, 12.0):
        area(f"Ceil{x}", (x, 5.5, 11.6), (x, 5.5, 0.0), 380, 6.0, warm, size_y=8.0)
    # window spill onto the sidewalk + door spill (inside the glass, facing out)
    for x in (-4.0, 12.0):
        area(f"Spill{x}", (x, 1.2, 6.0), (x, -6.0, 0.0), 320, 6.0, warm, size_y=5.0)
    area("DoorSpill", (4.0, 1.5, 4.5), (4.0, -8.0, 0.0), 500, 4.5, warm, size_y=7.5)
    # neon colour washes from the sign (pink) and the OPEN sign (red-pink / cyan)
    area("NeonPink", (4.0, -2.0, 10.6), (4.0, -9.0, 0.0), 2600, 12.0, (1.0, 0.28, 0.62), size_y=1.5)
    area("NeonCyan", (4.0, -1.6, 9.0), (6.0, -6.0, 3.0), 700, 12.0, (0.25, 0.85, 1.0), size_y=0.5)
    area("OpenGlow", (12.0, -1.0, 6.4), (11.0, -6.0, 2.0), 260, 2.5, (1.0, 0.3, 0.45))
    # porch downlight over the door: catches Mr. Usual's raincoat
    spot("Porch", (8.6, -1.6, 10.8), (9.6, -2.6, 4.0), 5200, 60, warm, blend=0.6, soft=0.6)
    # sodium street lamp on the right, rim light from behind-right on Mr. Usual
    spot("Sodium", (21.0, -10.0, 18.0), (16.0, -8.0, 0.0), 26000, 70, (1.0, 0.6, 0.25), blend=0.9, soft=1.0)
    area("UsualRim", (13.5, 1.5, 9.0), (9.6, -2.6, 5.0), 1400, 2.0, (0.55, 0.75, 1.0))
    # a lamp inside, just catching Paperface's paper bag through the glass
    spot("BagLight", (0.5, -0.2, 7.6), (-2.3, 1.45, 5.2), 380, 40, (1.0, 0.85, 0.65), blend=0.9, soft=0.4)
    # cold moonlight from the upper left, very low
    sun = bpy.data.lights.new("Moon", "SUN")
    sun.energy = 0.06
    sun.color = (0.55, 0.65, 1.0)
    so = bpy.data.objects.new("Moon", sun)
    sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(55), 0, math.radians(-35))


CAMERA = dict(loc=(17.5, -33.0, 4.6), target=(-1.5, 0.0, 6.6), lens=30.0)


def camera():
    cd = bpy.data.cameras.new("ArtCam")
    cd.lens = CAMERA["lens"]
    cd.sensor_width = 36.0
    cd.clip_start = 0.1
    cd.clip_end = 400.0
    cam = bpy.data.objects.new("ArtCam", cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector(CAMERA["loc"])
    cam.rotation_euler = (Vector(CAMERA["target"]) - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def render_art(name, draft):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24 if draft else 160
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.transparent_max_bounces = 16
    k = 0.25 if draft else 1.0
    sc.render.resolution_x = int(RES[0] * k)
    sc.render.resolution_y = int(RES[1] * k)
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.render.image_settings.color_mode = "RGBA"
    G._icon_materials()
    out = os.path.join(G.DRAFT_DIR if draft else os.path.join(G.REPO, "icons", "art"), f"{name}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sc.render.filepath = out
    with contextlib.redirect_stdout(io.StringIO()):
        bpy.ops.render.render(write_still=True)
    return out


@G.icon("Art_KeyArt", "art", "art", kind="art")
def keyart():
    facade()
    interior()
    signs()
    lot()
    creatures()
    rain()
    light_rig()
    camera()
    return {"render": lambda draft: render_art("Art_KeyArt", draft)}
