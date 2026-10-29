"""_common — shared helpers for the G_icons batch: sandwich icons (Night Shift at STACKHOUSE).

Renders the Menu sandwiches (Menu_M1..M8, group "menu") and the Secret Sandwiches
(Secret_S01..S30, group "secrets") as the assembled sandwich, built from the finished A_food
ingredient models (their own build() functions, never re-modelled) and shot with nslib's shared
icon rig (ns.render_icon: 512 px, transparent, 3/4 view, three-point light).

Recipes are read at run time from the game bible's tables (Bible §5.6 ingredient catalogue,
§5.7 Menu, §5.8 Secrets) in the git-ignored _local/ folder, so no recipe text is written into
this public repo. Set NS_BIBLE to point at another copy.

Assembly follows STYLE.md §4 and the game's KitchenRenderer (Controllers.Kitchen):
  * bottom bread -> meats -> cheeses -> veggies -> sauces -> top bread; within a category the
    recipe's order; repeated ingredients are repeated layers;
  * each layer's pivot at the running sum of manifest `layer_height`; `layer_count` copies spaced
    `layer_spacing` along X; sauces advance the stack by half their layer height (as in game);
  * toasted recipes use the melted cheese assets; the crust parts (role "toast") are tinted with
    the game's rule  base:Lerp(TOAST_DARK, clamp(d / perfectTo, 0, 1) * 0.75), Burnt = BURNT.
Icon-only staging: the top half is hinged open at the back (like the bread icons); a second sauce
is mirrored across the roll (a criss-cross, so both sauces read); a repeated filling is turned
180 degrees so the double layer reads as more food (not Swiss: its holes must stay open);
Perfect crusts get a thin clear-coat sheen; Burnt gets a faint smoke wisp; the Cursed Secret's
bread cracks glow like embers.

Run a single icon:  bpyenv/bin/python blender/G_icons/Secret_S01.py
                    NS_DRAFT=1 ... -> low-res framing draft into the scratch drafts dir only.
Batch / sheet:      bpyenv/bin/python blender/G_icons/_batch.py [ids...|all] [--draft]
                    bpyenv/bin/python blender/G_icons/_sheet.py
"""
from __future__ import annotations

import contextlib
import glob
import importlib
import importlib.util
import io
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True          # never drop .pyc files into lib/ or A_food/

HERE = os.path.dirname(os.path.abspath(__file__))
A_FOOD = os.path.normpath(os.path.join(HERE, "..", "A_food"))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "lib")))
import nslib as ns  # noqa: E402

import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

# A_food's helper module is also called `_common`: load it under a private name and hand it to the
# A_food scripts as `_common` only while they are being imported (see food_module).
_spec = importlib.util.spec_from_file_location("a_food_common", os.path.join(A_FOOD, "_common.py"))
FC = importlib.util.module_from_spec(_spec)
sys.modules["a_food_common"] = FC
_spec.loader.exec_module(FC)
if A_FOOD not in sys.path:
    sys.path.append(A_FOOD)

REPO = ns.REPO
SCRATCH = os.environ.get("NS_SCRATCH", "/tmp/claude-0/-home-claude/bee54a24-967a-5993-94e6-c9b5acdf45a4/scratchpad/g_icons")
DRAFT_DIR = os.path.join(SCRATCH, "drafts")

# ---- the icon camera (identical for every sandwich icon) ------------------------------------
YAW = -34.0          # slight 3/4 from the front-left (bread icons use -58; fillings read better here)
PITCH = 26.0         # low enough that the open lid shows its crumb face (the bread tell)
FOV = 24.0           # nslib render_icon default
OPEN_DEG = 40.0      # top half hinged open at the back edge (as the bread icons)
FILL = 0.93          # silhouette fills 93% of the frame on its larger axis, centred

# ---- the game's toast tint (Controllers.Kitchen + Config.Economy.toaster) ---------------------
TOAST_DARK = (92, 52, 22)
BURNT = (34, 26, 22)
PERFECT_TO = 1.10
# doneness shown per toast class: the start of the Done band (0.70, the lightest a toasted order
# looks in game) and deep in the Perfect band (0.85-1.10), so the two classes read apart
DONENESS = {"Toasted": 0.70, "Perfect": 1.05}
EMBER = "#FF5A1F"
SMOKE = "#D6D0DC"

CAT_ORDER = ("Meat", "Cheese", "Veggie", "Sauce")
KEEP_ALIGNED = {"swiss"}   # repeats left aligned: turning would plug Swiss's holes with cheese


# --------------------------------------------------------------------------------------
# A_food assets
# --------------------------------------------------------------------------------------

def food_module(name: str):
    """Import an A_food generator script (Food_Ham, ...) so its build() can be reused."""
    if name in sys.modules:
        return sys.modules[name]
    saved = sys.modules.get("_common")
    sys.modules["_common"] = FC
    try:
        return importlib.import_module(name)
    finally:
        if saved is not None:
            sys.modules["_common"] = saved
        else:
            sys.modules.pop("_common", None)


def _load_food_manifest() -> dict:
    with open(os.path.join(REPO, "manifests", "A_food.json")) as f:
        return json.load(f)


MAN = _load_food_manifest()


def _asset_index() -> dict:
    """ingredient id -> {bottom, top, layer, melted} asset names (from manifests/A_food.json, the
    same index the KitchenRenderer builds from ReplicatedStorage.Assets.Food)."""
    idx: dict[str, dict] = {}
    for asset, e in MAN.items():
        ing = (e.get("meta") or {}).get("ingredient")
        if not ing:
            continue
        d = idx.setdefault(ing, {})
        if asset.endswith("_Bottom"):
            d["bottom"] = asset
        elif asset.endswith("_Top"):
            d["top"] = asset
        elif e["meta"].get("melted"):
            d["melted"] = asset
        else:
            d["layer"] = asset
    return idx


ASSETS = _asset_index()


# --------------------------------------------------------------------------------------
# recipes (from the bible, at run time)
# --------------------------------------------------------------------------------------

def bible_path() -> str:
    env = os.environ.get("NS_BIBLE")
    if env:
        return env
    files = glob.glob(os.path.join(REPO, "_local", "Night_Shift_Game_Bible_v*.md"))
    assert files, "game bible not found in _local/ (set NS_BIBLE)"

    def ver(p):
        m = re.search(r"_v(\d+)\.(\d+)", p)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    return max(files, key=ver)


def _table(lines, section: str):
    """Rows (lists of cell strings) of the first table under the heading '## <section> ...'."""
    rows, inside = [], False
    for ln in lines:
        if ln.startswith("## "):
            if inside:
                break
            inside = ln[3:].strip().startswith(section + " ")
            continue
        if inside and ln.startswith("# "):
            break
        if inside and ln.startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            rows.append(cells)
    assert rows, f"bible table {section} not found"
    return rows[1:]   # drop the header row


def _toast_class(cell: str) -> str:
    t = cell.replace("*", "").strip().lower()
    return {"no": "None", "yes": "Toasted", "perfect": "Perfect", "burnt": "Burnt"}[t]


def load_recipes():
    with open(bible_path()) as f:
        lines = f.read().splitlines()
    ing = {}
    for r in _table(lines, "5.6"):
        ing[r[0]] = {"name": r[1], "category": r[2]}
    by_name = {v["name"].lower(): k for k, v in ing.items()}

    def ids(names):
        out = []
        for n in names:
            n = n.strip()
            if not n:
                continue
            assert n.lower() in by_name, f"unknown ingredient '{n}' in the bible tables"
            out.append(by_name[n.lower()])
        return out

    rec = {}
    for r in _table(lines, "5.7"):   # ID | Name | Bread | Fillings | Sauce | Toast | On menu from
        rec[r[0]] = {"id": r[0], "name": r[1], "bread": ids([r[2]])[0],
                     "items": ids(r[3].split(",")) + ids(r[4].split(",")), "toast": _toast_class(r[5]),
                     "rarity": "Menu", "icon": f"Menu_{r[0]}", "group": "menu"}
    for r in _table(lines, "5.8"):   # # | Name | Rarity | Recipe (bread · items) | Toast | Riddle
        bread, items = r[3].split("·")
        rec[r[0]] = {"id": r[0], "name": r[1], "bread": ids([bread])[0], "items": ids(items.split(",")),
                     "toast": _toast_class(r[4]), "rarity": r[2], "icon": f"Secret_{r[0]}", "group": "secrets"}
    for r in rec.values():
        assert ing[r["bread"]]["category"] == "Bread", r
        assert all(ing[i]["category"] in CAT_ORDER for i in r["items"]), r
    return ing, rec


INGREDIENTS, RECIPES = load_recipes()


def stack_of(rid: str):
    """Fillings and sauces bottom -> top: meats, cheeses, veggies, sauces (recipe order within)."""
    items = RECIPES[rid]["items"]
    return sorted(items, key=lambda i: CAT_ORDER.index(INGREDIENTS[i]["category"]))  # stable


# --------------------------------------------------------------------------------------
# colour helpers
# --------------------------------------------------------------------------------------

def _rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(c) -> str:
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(v)))) for v in c)


def toast_color(base_hex: str, toast: str) -> str:
    """The game's crust tint (Controllers.Kitchen `tint`), in sRGB like Color3:Lerp."""
    if toast == "Burnt":
        return _hex(BURNT)
    if toast not in DONENESS:
        return base_hex
    t = max(0.0, min(1.0, DONENESS[toast] / PERFECT_TO)) * 0.75
    b = _rgb(base_hex)
    return _hex(tuple(b[i] + (TOAST_DARK[i] - b[i]) * t for i in range(3)))


def _retint(o, hexcol: str, mat: str | None = None, coat: float = 0.0):
    """Swap a tagged part's colour/material (keeps its tag, role and smoothing)."""
    mat = mat or o["ns_material"]
    m = ns.material(hexcol, mat)
    if coat > 0:
        m = m.copy()
        m.name = m.name + "_Sheen"
        b = m.node_tree.nodes.get("Principled BSDF")
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.22
        b.inputs["Coat IOR"].default_value = 1.45
    o["ns_color"] = hexcol
    o["ns_material"] = mat
    o.data.materials.clear()
    o.data.materials.append(m)


# --------------------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------------------

def _place(asset: str, z: float, prefix: str, pre: Matrix | None = None):
    """Build one A_food asset (layer_count copies along X like the KitchenRenderer), rename its
    parts `<prefix>_<Part>` and move its pivot to (0, 0, z). Returns (objects, layer_height)."""
    mod = food_module(asset)
    meta = MAN[asset]["meta"]
    n = int(meta.get("layer_count", 1) or 1)
    sp = float(meta.get("layer_spacing", 0.0) or 0.0)
    if n < 2 or sp <= 0:
        n = 1
    out = []
    for i in range(n):
        before = set(ns._tagged_objects())
        with contextlib.redirect_stdout(io.StringIO()):
            mod.build()
        bpy.context.view_layer.update()
        new = [o for o in ns._tagged_objects() if o not in before]
        T = Matrix.Translation(((i - (n - 1) / 2) * sp, 0.0, z))
        if pre is not None:
            T = T @ pre
        for o in new:
            nm = f"{prefix}{chr(97 + i) if n > 1 else ''}_{o['ns_part']}"
            o["ns_part"] = nm
            o.name = nm
            o.matrix_world = T @ o.matrix_world
        out += new
    return out, float(meta.get("layer_height", 0.0))


def build_sandwich(rid: str, open_deg: float | None = None, log: bool = True) -> dict:
    """Assemble recipe `rid` in the (already reset) scene. Returns {"fit": [food parts],
    "extra": [staging that is not food, e.g. smoke; framed with the food], "z_top": stack height}."""
    r = RECIPES[rid]
    open_deg = OPEN_DEG if open_deg is None else open_deg
    toast = r["toast"]
    bread = ASSETS[r["bread"]]
    report = []
    objs, h = _place(bread["bottom"], 0.0, "B")
    z = h
    report.append(f"{bread['bottom']:24s} z=0.000")
    seen: dict[str, int] = {}
    sauces = 0
    z_top = z
    for k, ing in enumerate(stack_of(rid)):
        cat = INGREDIENTS[ing]["category"]
        a = ASSETS[ing]
        asset = a["melted"] if (toast != "None" and "melted" in a) else a["layer"]
        rep = seen.get(ing, 0)
        seen[ing] = rep + 1
        pre = None
        if cat == "Sauce":
            if sauces % 2 == 1:                       # second sauce: mirrored across the roll
                pre = Matrix.Scale(-1.0, 4, (0.0, 1.0, 0.0))
            sauces += 1
        elif rep % 2 == 1 and ing not in KEEP_ALIGNED:  # repeated filling: turned end for end
            pre = Matrix.Rotation(math.pi, 4, "Z")
        new, h = _place(asset, z, f"L{k}", pre)
        objs += new
        report.append(f"{asset:24s} z={z:.3f}{'  (mirrored)' if pre is not None and cat == 'Sauce' else ''}"
                      f"{'  (turned)' if pre is not None and cat != 'Sauce' else ''}")
        z_top = max(z_top, z + h)
        z += h * (0.5 if cat == "Sauce" else 1.0)     # game: sauces advance the stack by half
    top, _ = _place(bread["top"], 0.0, "T")
    hinge = Vector((0.0, FC.ROLL_B - 0.03, z_top))
    R = Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-open_deg), 4, "X") @ Matrix.Translation(-hinge)
    for o in top:
        o.matrix_world = R @ Matrix.Translation((0.0, 0.0, z_top)) @ o.matrix_world
    report.append(f"{bread['top']:24s} z={z_top:.3f} (hinged {open_deg:.0f} deg)")
    objs += top
    bpy.context.view_layer.update()

    # toast: the game's crust tint on every part with role "toast"
    extra = []
    for o in objs:
        if o.get("ns_role") == "toast":
            col = toast_color(o["ns_color"], toast)
            _retint(o, col, coat=0.55 if toast == "Perfect" else 0.0)
    if toast == "Burnt":
        extra += smoke_wisps(top)
    if r["rarity"] == "Cursed":
        for o in top:
            if o["ns_part"].endswith("_Cracks"):
                _retint(o, EMBER, "Neon")
    if log:
        print(f"[{r['icon']}] {r['name']} | {r['bread']} | toast {toast}")
        for ln in report:
            print("   ", ln)
    return {"fit": objs, "extra": extra, "z_top": z_top}


def smoke_wisps(top) -> list:
    """Faint curling smoke rising off the crest of the (burnt) top half. Framed with the sandwich
    (the sandwich is wider than tall, so the wisps only re-centre the frame, not rescale it)."""
    tree = FC.bvh_multi([o for o in top if o["ns_part"].endswith("_Crust")])
    specs = [(-0.55, 0.36, 1.0, 0.0), (0.05, 0.44, -1.0, 1.9), (0.62, 0.3, 1.0, 3.4)]
    objs = []
    for k, (x0, H, s, ph) in enumerate(specs):
        # start on the crust: ray-cast down onto the hinged lid near its crest
        loc, _ = FC.hit(tree, x0, 0.3)
        if loc is None:
            continue
        pts, rad = [], []
        n = 8
        for i in range(n):
            t = i / (n - 1)
            pts.append((x0 + s * 0.07 * math.sin(2 * math.pi * 1.2 * t + ph) + 0.06 * t,
                        loc.y + 0.04 * math.cos(2 * math.pi * 0.9 * t + ph),
                        loc.z - 0.01 + H * t))
            rad.append(0.012 + 0.026 * math.sin(math.pi * min(1.0, 0.25 + t)) * (1 - 0.45 * t))
        objs.append(ns.tube(pts, rad, sides=8, resolution=6, name=f"Smoke{k}"))
    sm = ns.join(objs, "Smoke")
    ns.tag(sm, "Smoke", SMOKE, "SmoothPlastic", transparency=0.62, cast_shadow=False, smooth_angle=89)
    return [sm]


# --------------------------------------------------------------------------------------
# framing: same camera for every icon, distance and aim fitted to the sandwich's silhouette
# --------------------------------------------------------------------------------------

def _world_points(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = o.matrix_world
        pts.extend(mw @ v.co for v in me.vertices)
        ev.to_mesh_clear()
    return pts


def fit_frame(objs, yaw=None, pitch=None, fov=None, fill=None):
    """Find the aim point and camera distance (for nslib's yaw/pitch camera) that centre the
    sandwich's projected silhouette and make its larger side `fill` of the frame. Returns the
    `objects` list and `margin` to hand to ns.render_icon: the parts plus a hidden FrameAnchor
    whose bounding box puts nslib's aim point and distance exactly there."""
    yaw = YAW if yaw is None else yaw
    pitch = PITCH if pitch is None else pitch
    fov = FOV if fov is None else fov
    fill = FILL if fill is None else fill
    pts = _world_points(objs)
    y_, p_ = math.radians(yaw), math.radians(pitch)
    d = Vector((math.sin(y_) * math.cos(p_), -math.cos(y_) * math.cos(p_), math.sin(p_)))
    f = -d
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f)
    th = math.tan(math.radians(fov) / 2)
    lo, hi = ns.bbox_world(objs)
    c = (lo + hi) / 2
    D = (hi - lo).length / 2 / math.sin(math.radians(fov) / 2)
    for _ in range(10):
        cam = c + d * D
        xs, ys = [], []
        for p in pts:
            v = p - cam
            dep = v.dot(f)
            xs.append(v.dot(r) / dep / th)
            ys.append(v.dot(u) / dep / th)
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        ext = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
        c = c + r * (cx * D * th) + u * (cy * D * th)
        D *= ext / fill
    H = Vector([max(c[i] - lo[i], hi[i] - c[i]) + 0.01 for i in range(3)])
    me = bpy.data.meshes.new("FrameAnchor")
    me.from_pydata([tuple(c - H), tuple(c + H)], [], [])
    anchor = bpy.data.objects.new("FrameAnchor", me)
    bpy.context.scene.collection.objects.link(anchor)
    anchor.hide_render = True
    margin = D * math.sin(math.radians(fov) / 2) / H.length
    return list(objs) + [anchor], margin


# --------------------------------------------------------------------------------------
# render entry points
# --------------------------------------------------------------------------------------

def _draft_render(path: str, objects, margin: float, res=256, samples=12):
    """Low-sample stand-in for ns.render_icon (same camera, lights and material tweak) that writes
    only to the scratch drafts dir (no .nsz, no manifest)."""
    lo, hi = ns.bbox_world(objects)
    ns._setup_render(res, samples, transparent=True)
    bpy.context.scene.world.node_tree.nodes.get("Background").inputs[1].default_value = 0.45
    for m in bpy.data.materials:
        b = m.node_tree.nodes.get("Principled BSDF") if m.use_nodes else None
        if b:
            b.inputs["Roughness"].default_value = max(0.62, b.inputs["Roughness"].default_value)
            b.inputs["Specular IOR Level"].default_value = 0.25
    cam, ctr, dist = ns._camera_fit(lo, hi, YAW, PITCH, fov_deg=FOV, margin=margin)
    k = math.radians(YAW)
    ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.7), -math.cos(k - 0.7), 1.0)) * dist, 62 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
    ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.3), -math.cos(k + 1.3), 0.2)) * dist, 18 * dist ** 2 / 9, size=dist * 0.9, target=ctr)
    ns._light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.9)) * dist, 50 * dist ** 2 / 9, size=dist * 0.4, target=ctr)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.scene.render.filepath = path
    with contextlib.redirect_stdout(io.StringIO()):
        bpy.ops.render.render(write_still=True)
    ns._clear_rig()
    return path


def render(rid: str, draft: bool = False) -> str:
    r = RECIPES[rid]
    ns.reset()
    built = build_sandwich(rid)
    print(f"[{r['icon']}] triangles: {ns.tri_count(built['fit'])}")
    objects, margin = fit_frame(built["fit"] + built["extra"])
    if draft:
        out = _draft_render(os.path.join(DRAFT_DIR, f"{r['icon']}.png"), objects, margin)
    else:
        out = ns.render_icon(r["icon"], r["group"], yaw=YAW, pitch=PITCH, fov=FOV, margin=margin, objects=objects)
    print(f"[{r['icon']}] {'draft' if draft else 'icon'}: {out}")
    return out


def main(rid: str):
    render(rid, draft=os.environ.get("NS_DRAFT") == "1")


ALL_IDS = [f"M{i}" for i in range(1, 9)] + [f"S{i:02d}" for i in range(1, 31)]


# --------------------------------------------------------------------------------------
# review sheet
# --------------------------------------------------------------------------------------

def icon_sheet(out: str | None = None, src: str | None = None, cols: int = 4, bg=(44, 47, 56)) -> str:
    """All 38 icons at full size (512) with a 64 px copy beside each, labelled.
    src=None: the published icons in icons/<group>/; src=<dir>: drafts named <icon>.png there."""
    from PIL import Image, ImageDraw
    out = out or os.path.join(SCRATCH, "_icons_sheet.png")
    cell_w, cell_h, lab = 512 + 64 + 36, 512 + 34, 30
    rows = (len(ALL_IDS) + cols - 1) // cols
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), bg)
    draw = ImageDraw.Draw(sheet)
    for i, rid in enumerate(ALL_IDS):
        r = RECIPES[rid]
        p = os.path.join(src, f"{r['icon']}.png") if src else os.path.join(REPO, "icons", r["group"], f"{r['icon']}.png")
        x, y = (i % cols) * cell_w, (i // cols) * cell_h
        draw.text((x + 10, y + 8), f"{r['icon']}  {r['name']}  [{r['rarity']}, {r['bread']}, {r['toast']}]",
                  fill=(235, 235, 235))
        if not os.path.exists(p):
            draw.text((x + 10, y + 60), "missing", fill=(255, 90, 90))
            continue
        im = Image.open(p).convert("RGBA")
        if im.size != (512, 512):
            im = im.resize((512, 512), Image.LANCZOS)
        sheet.paste(im, (x + 6, y + lab), im)
        sm = im.resize((64, 64), Image.LANCZOS)
        sheet.paste(sm, (x + 6 + 512 + 14, y + lab + 224), sm)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet.save(out)
    small = os.path.splitext(out)[0] + "_64.png"
    # companion: every icon at 64 px only (the phone-size read test)
    s64 = Image.new("RGB", (8 * 76 + 8, ((len(ALL_IDS) + 7) // 8) * 92 + 8), bg)
    d64 = ImageDraw.Draw(s64)
    for i, rid in enumerate(ALL_IDS):
        r = RECIPES[rid]
        p = os.path.join(src, f"{r['icon']}.png") if src else os.path.join(REPO, "icons", r["group"], f"{r['icon']}.png")
        if not os.path.exists(p):
            continue
        x, y = 8 + (i % 8) * 76, 8 + (i // 8) * 92
        sm = Image.open(p).convert("RGBA").resize((64, 64), Image.LANCZOS)
        s64.paste(sm, (x, y + 14), sm)
        d64.text((x, y), rid, fill=(220, 220, 220))
    s64.save(small)
    return out
