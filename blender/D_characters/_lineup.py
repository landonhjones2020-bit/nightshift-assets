"""Review renders for the D_characters batch (not an asset).

  python blender/D_characters/_lineup.py fit     -> previews/D_characters/_fitsheet.png
        every Char_* accessory worn by the base body (proves socket fit)
  python blender/D_characters/_lineup.py lineup  -> previews/D_characters/_lineup.png
        6 dressed customers (base rig + accessory combos + outfit colours) + the 4 Regulars
"""
import importlib
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
bpy = C.bpy
Vector = C.Vector


def dress(look, accs, offset, overrides=None):
    """Base body (no rig) + accessories, moved to `offset`."""
    before = set(bpy.context.scene.objects)
    C.build_body(None, look)
    for name in accs:
        fn, sock = C.ACCESSORIES[name]
        kw = (overrides or {}).get(name, {})
        C.place_accessory(fn(**kw), bone=C.SOCKET_BONE[sock])
    new = [o for o in bpy.context.scene.objects if o not in before]
    for o in new:
        o.location += Vector(offset)
    return new


CUSTOMERS = [
    ("Trucker", {"skin": "#C98B62", "top": "#3F6E46", "pants": "#3F5F8C", "shoes": "#5A3A24", "brow": "#5A3A24"},
     ["Char_Hat_TruckerCap", "Char_Hair_Mullet", "Char_Face_Beard", "Char_Top_Flannel"],
     {"Char_Hat_TruckerCap": {"color": "#B23A33"}, "Char_Hair_Mullet": {"color": "#6B4A2E"},
      "Char_Face_Beard": {"color": "#6B4A2E"}, "Char_Top_Flannel": {"color": "#3F6E46"}}),
    ("Nurse", {"skin": "#9C6644", "top": "#7E6BB0", "pants": "#7E6BB0", "shoes": "#EDEAE2", "brow": "#211B18"},
     ["Char_Hair_Bun", "Char_Face_Bags", "Char_Top_Scrubs"],
     {"Char_Hair_Bun": {"color": "#211B18"}, "Char_Top_Scrubs": {"color": "#7E6BB0", "skin": "#9C6644"}}),
    ("Student", {"skin": "#F2C9A5", "top": "#B8443A", "pants": "#4A4F57", "shoes": "#2B2D31", "brow": "#3D2A1E"},
     ["Char_Hair_Curly", "Char_Face_Glasses", "Char_Top_Hoodie", "Char_Top_Backpack"],
     {"Char_Hair_Curly": {"color": "#3D2A1E"}, "Char_Top_Hoodie": {"color": "#B8443A"},
      "Char_Top_Backpack": {"color": "#B8443A"}}),
    ("Cop", {"skin": "#6E4530", "top": "#26324F", "pants": "#1F2A44", "shoes": "#141518", "brow": "#211B18"},
     ["Char_Hat_CopCap", "Char_Hair_Long", "Char_Top_Badge"],
     {"Char_Hair_Long": {"color": "#211B18"}, "Char_Top_Badge": {"color": "#26324F"}}),
    ("Janitor", {"skin": "#E3AC85", "top": "#5E7A8C", "pants": "#3A3E4A", "shoes": "#2B2D31", "brow": "#8C8880"},
     ["Char_Hat_Beanie", "Char_Hair_Short", "Char_Face_Mustache", "Char_Top_Overalls"],
     {"Char_Hat_Beanie": {"color": "#C8523A"}, "Char_Hair_Short": {"color": "#8C8880"},
      "Char_Face_Mustache": {"color": "#8C8880"}, "Char_Top_Overalls": {"color": "#5E7A8C"}}),
    ("Insomniac", {"skin": "#4B2E22", "top": "#8F6FA8", "pants": "#5B5470", "shoes": "#C9B9D6", "brow": "#211B18"},
     ["Char_Hair_Messy", "Char_Face_Bags", "Char_Top_Robe"],
     {"Char_Hair_Messy": {"color": "#211B18"}, "Char_Top_Robe": {"color": "#8F6FA8"}}),
]
REGULARS = ["Character_Regular_gus", "Character_Regular_mina", "Character_Regular_walt", "Character_Regular_jo"]


def render(path, lo, hi, yaw=-18, pitch=8, w=2000, h=760, samples=20, fov=26):
    sc = bpy.context.scene
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.002))
    fl = bpy.context.active_object
    fl.data.materials.append(ns.material("#2A2F45"))
    ns._setup_render(512, samples)
    sc.render.resolution_x, sc.render.resolution_y = w, h
    ctr = (lo + hi) / 2
    cam_d = bpy.data.cameras.new("Cam")
    cam_d.angle = math.radians(fov)
    cam = bpy.data.objects.new("Cam", cam_d)
    sc.collection.objects.link(cam)
    span = (hi.x - lo.x) * 1.08
    dist = span / 2 / math.tan(cam_d.angle / 2)
    k, p = math.radians(yaw), math.radians(pitch)
    cam.location = ctr + Vector((math.sin(k) * math.cos(p), -math.cos(k) * math.cos(p), math.sin(p))) * dist
    cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    L = dist
    ns._light("Key", "AREA", ctr + Vector((-0.4, -1, 0.8)) * L, 55 * L ** 2 / 9, size=L * 0.5, target=ctr)
    ns._light("Fill", "AREA", ctr + Vector((0.8, -0.7, 0.3)) * L, 22 * L ** 2 / 9, size=L * 0.8, target=ctr)
    ns._light("Rim", "AREA", ctr + Vector((0.2, 1, 0.9)) * L, 30 * L ** 2 / 9, size=L * 0.4, target=ctr)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path


def label(path, names, xs_frac, top=True):
    from PIL import Image, ImageDraw
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    for n, xf in zip(names, xs_frac):
        x = int(xf * im.width)
        d.text((x - 3 * len(n), 10 if top else im.height - 24), n, fill=(240, 240, 240))
    im.save(path)


def fit_sheet():
    """Two rows (hair/hats/faces, then tops), rendered separately and stacked."""
    from PIL import Image
    names = list(C.ACCESSORIES)
    rows = [names[:11], names[11:]]
    gap = 2.5
    paths = []
    for r, row in enumerate(rows):
        ns.reset()
        C.reset_caches()
        for i, name in enumerate(row):
            dress({}, [name], ((i - 5) * gap, 0, 0))
        lo, hi = Vector((-5 * gap - 1.2, -0.8, 0)), Vector((5 * gap + 1.2, 0.8, 5.5))
        p = os.path.join(C.PREV, f"_fit_row{r}.png")
        yaw = -14 if r == 0 else 22
        render(p, lo, hi, yaw=yaw, pitch=8, w=2200, h=620, fov=24, samples=10)
        label(p, [n.replace("Char_", "") for n in row], [0.5 + (i - 5) * gap / ((hi.x - lo.x) * 1.08) for i in range(len(row))])
        paths.append(p)
    ims = [Image.open(p) for p in paths]
    sheet = Image.new("RGB", (ims[0].width, sum(i.height for i in ims)))
    y = 0
    for im in ims:
        sheet.paste(im, (0, y))
        y += im.height
    out = os.path.join(C.PREV, "_fitsheet.png")
    sheet.save(out)
    for p in paths:
        os.remove(p)
    return out


def lineup():
    ns.reset()
    gap = 2.7
    n = len(CUSTOMERS) + len(REGULARS)
    xs = [(i - (n - 1) / 2) * gap for i in range(n)]
    labels = []
    for i, (nm, look, accs, ov) in enumerate(CUSTOMERS):
        dress(look, accs, (xs[i], 0, 0), ov)
        labels.append(nm)
    for j, mod in enumerate(REGULARS):
        try:
            m = importlib.import_module(mod)
        except ModuleNotFoundError:
            continue
        before = set(bpy.context.scene.objects)
        m.build_regular(None)
        for o in [o for o in bpy.context.scene.objects if o not in before]:
            o.location += Vector((xs[len(CUSTOMERS) + j], 0, 0))
        labels.append(m.TITLE)
    lo, hi = Vector((xs[0] - 1.3, -0.8, 0)), Vector((xs[-1] + 1.3, 0.8, 5.6))
    p = os.path.join(C.PREV, "_lineup.png")
    render(p, lo, hi, yaw=0, pitch=6, w=2400, h=760, fov=24)
    span = (hi.x - lo.x) * 1.08
    label(p, labels, [0.5 + x / span for x in xs])
    return p


if __name__ == "__main__":
    mode = sys.argv[-1]
    os.makedirs(C.PREV, exist_ok=True)
    print("[lineup]", fit_sheet() if mode == "fit" else lineup())
