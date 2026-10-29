"""Shared helpers for the D_characters batch (human rig, accessories, Regulars, clips).

Import from a generator in this folder with:
    import _common as C          (the folder is on sys.path when the script runs)
    ns = C.ns                     (the shared nslib)

Contents
  * skeleton  : the shared rigid-part human rig (9 bones, all +Y, roll 0) and its sockets
  * geometry  : superellipse lofts, thick parametric patches (hair, hats, garments, beards)
                that are generated ON the base head / torso surfaces so accessories fit
  * body      : build_body(arm, look) -> the chunky base human, parts bound to bones
  * accessory : ACCESSORIES table, place_accessory(), run_accessory()
  * animation : build_actions(arm) -> the 9 "Human" clips (see ANIM section)
  * review    : foot-slide / penetration metrics, pose strips, quick renders

Coordinates are Blender world = rest pose of the rig: 1 unit = 1 stud, Z up, the character
faces -Y, its LEFT side is +X. Every accessory is modelled in this space against the real
head/torso and then shifted so its socket point becomes the asset pivot.
"""
from __future__ import annotations

import math
import os
import random
import sys

import bpy  # noqa: F401  (must load before bmesh/mathutils in the bpy module build)
import bmesh
from mathutils import Euler, Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import nslib as ns  # noqa: E402

BATCH = "D_characters"
GROUP = "Characters"
PREV = os.path.join(ns.REPO, "..", "previews", BATCH)
RIG_NAME = "Human"

# --------------------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------------------
SKIN = "#E3AC85"          # default (runtime recolours role "skin")
SKIN_TONES = ["#F2C9A5", "#E3AC85", "#C98B62", "#9C6644", "#6E4530", "#4B2E22"]
TOP = "#4F7C9E"           # default outfit top (role "top")
PANTS = "#3A3E4A"         # role "pants"
SHOES = "#6B4430"         # role "shoes"
SOLE = "#EDE6D8"          # sneaker soles + laces (fixed)
EYE_WHITE = "#F7F4EE"
PUPIL = "#2A211D"
BROW = "#4A3326"
MOUTH = "#7A3B33"
HAIR = {"black": "#211B18", "dark": "#3D2A1E", "brown": "#6B4A2E", "auburn": "#8C4A2A",
        "blonde": "#D8B46A", "grey": "#B9B5AE", "white": "#E4E1DA", "ginger": "#B5652E"}
GOLD = "#E2B64A"
CHROME = "#C9CED3"
BLACK = "#1E1F22"
WHITE = "#F4F1EA"
BRAND = "#E8502A"
MUSTARD = "#F2B33D"

# --------------------------------------------------------------------------------------
# Skeleton (rest pose). Bones point +Y with zero roll, so bone-local Euler keys read as
# world axes: X = pitch (+ tips the top of an upright bone FORWARD / swings a hanging limb
# BACK), Y = roll about the forward axis, Z = yaw (+ turns the face toward +X = its left).
# --------------------------------------------------------------------------------------
HIPS_J = Vector((0.0, 0.0, 2.05))
WAIST_J = Vector((0.0, 0.0, 2.38))
NECK_J = Vector((0.0, 0.0, 3.62))
LEG_X, LEG_Z = 0.34, 1.95
SH_X, SH_Z = 0.90, 3.32
ARM_SPLAY = 6.0           # rest arms hang 6 deg out from vertical (A-pose, clears the hips)
ARM_LEN = 1.32            # shoulder joint -> wrist joint
HAND_LEN = 0.44
SIDES = (("L", 1.0), ("R", -1.0))


def arm_dir(s: float) -> Vector:
    a = math.radians(ARM_SPLAY)
    return Vector((s * math.sin(a), 0.0, -math.cos(a)))


def shoulder(s: float) -> Vector:
    return Vector((s * SH_X, 0.0, SH_Z))


def wrist(s: float) -> Vector:
    return shoulder(s) + arm_dir(s) * ARM_LEN


def hip(s: float) -> Vector:
    return Vector((s * LEG_X, 0.0, LEG_Z))


JOINTS = {"Hips": HIPS_J, "Torso": WAIST_J, "Head": NECK_J,
          "ArmL": shoulder(1), "HandL": wrist(1), "ArmR": shoulder(-1), "HandR": wrist(-1),
          "LegL": hip(1), "LegR": hip(-1)}
PARENT = {"Hips": None, "Torso": "Hips", "Head": "Torso", "ArmL": "Torso", "HandL": "ArmL",
          "ArmR": "Torso", "HandR": "ArmR", "LegL": "Hips", "LegR": "Hips"}
BONES = ["Hips", "Torso", "Head", "ArmL", "HandL", "ArmR", "HandR", "LegL", "LegR"]


def make_rig(name: str = "HumanRig"):
    spec = [(b, PARENT[b], tuple(JOINTS[b]), tuple(JOINTS[b] + Vector((0, 0.1, 0)))) for b in BONES]
    return ns.make_armature(name, spec)


# Head + torso reference shapes (shared by body, hair, hats, faces, garments)
HEAD_C = Vector((0.0, -0.03, 4.39))
HEAD_R = Vector((0.63, 0.59, 0.66))
HEAD_TOP = HEAD_C.z + HEAD_R.z          # 5.01

# torso rings (z, half-width a, half-depth b, superellipse n, y-centre) bottom (hem) -> neck
TORSO = [(2.20, 0.665, 0.445, 2.4, 0.0), (2.26, 0.67, 0.447, 2.4, 0.0), (2.45, 0.68, 0.452, 2.5, 0.0),
         (2.75, 0.74, 0.468, 2.6, -0.01), (3.05, 0.80, 0.472, 2.7, -0.02), (3.28, 0.83, 0.452, 2.8, -0.01),
         (3.44, 0.76, 0.405, 2.7, 0.0), (3.55, 0.56, 0.33, 2.3, 0.0), (3.62, 0.30, 0.24, 2.0, 0.0)]

# Sockets (rest pose, Blender world). Accessories are modelled so their pivot = the socket.
SOCKETS = {
    "HatSocket": Vector((0.0, HEAD_C.y, HEAD_TOP + 0.08)),   # top of head + short-hair allowance
    "HairSocket": Vector((0.0, HEAD_C.y, HEAD_TOP)),          # skull apex (head centre, top)
    "FaceSocket": Vector((0.0, -0.615, 4.42)),                # nose bridge, eye level
    "TorsoSocket": Vector((0.0, -0.49, 3.00)),                # chest centre, on the shirt front
}
SOCKET_BONE = {"HatSocket": "Head", "HairSocket": "Head", "FaceSocket": "Head", "TorsoSocket": "Torso"}

ROOT_META = {"center": [0, 2.95, 0], "size": [2.0, 2.0, 1.0]}   # HRP: bottom at the hip joints
WALK_SPEED = 9.0
CHASE_SPEED = 20.0
SEAT_H = 1.6


def base_meta(extra: dict | None = None) -> dict:
    m = {"root": dict(ROOT_META), "walkSpeed": WALK_SPEED,
         "clipSpeedRef": {"Walk": WALK_SPEED, "ChaseRun": CHASE_SPEED},
         "animRig": RIG_NAME,
         "socketBones": dict(SOCKET_BONE),
         "sit": {"seatHeight": SEAT_H, "pivotFromSeatSocket": [0, -SEAT_H, 0],
                 "note": "Sit/Eat: put the model pivot on the floor right under the seat socket, facing the socket yaw"},
         "eyelids": "role eyelid parts export Transparency 1 (eyes open); set 0 for ~0.12 s to blink",
         "events": {"EatStand": {"bite": EATSTAND_BITE / 30.0}}}
    if extra:
        m.update(extra)
    return m


def socket_spec() -> dict:
    return {k: tuple(v) for k, v in SOCKETS.items()}


# --------------------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------------------

def _sgnpow(v: float, e: float) -> float:
    return math.copysign(abs(v) ** e, v)


def se_point(phi: float, a: float, b: float, n: float, cx: float = 0.0, cy: float = 0.0):
    """Superellipse point. phi 0 = front (-Y), +90 deg = +X (character's left)."""
    s, c = math.sin(phi), math.cos(phi)
    return cx + a * _sgnpow(s, 2.0 / n), cy - b * _sgnpow(c, 2.0 / n)


def xform(obj, M: Matrix):
    obj.data.transform(M)
    obj.data.update()
    return obj


def loft_z(rings, segs=24, cap0=True, cap1=True, name="Loft"):
    """Closed loft of superellipse rings along Z. rings: (z, a, b, n[, cx, cy]) bottom->top."""
    bm = bmesh.new()
    vr = []
    for r in rings:
        z, a, b, n = r[:4]
        cx, cy = (r[4], r[5]) if len(r) >= 6 else (0.0, r[4] if len(r) == 5 else 0.0)
        row = []
        for i in range(segs):
            x, y = se_point(2 * math.pi * i / segs, a, b, n, cx, cy)
            row.append(bm.verts.new((x, y, z)))
        vr.append(row)
    for r0, r1 in zip(vr, vr[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    for row, flag in ((vr[0], cap0), (vr[-1], cap1)):
        if flag:
            c = sum((v.co for v in row), Vector()) / len(row)
            cv = bm.verts.new(c)
            for i in range(segs):
                bm.faces.new((cv, row[i], row[(i + 1) % segs]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def ellipsoid(c, r, segs=16, rings=10, rot=(0, 0, 0), name="Ell"):
    o = ns.sphere(1.0, loc=tuple(c), rot=rot, scale=tuple(r), segs=segs, rings=rings, name=name)
    return o


def _orient_out(bm, centre: Vector):
    """Flip all faces if, on average, they point toward `centre` (open shells)."""
    tot = 0.0
    for f in bm.faces:
        tot += f.normal.dot(f.calc_center_median() - centre) * f.calc_area()
    if tot < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])


def patch(f_out, f_in, nu, nv, *, closed_u=True, pole=False, inner="full", centre=None,
          name="Patch", vs=None):
    """Thick shell between two parametric surfaces sampled on the same (u, v) grid.

    f_out/f_in(u, v) -> Vector, u,v in [0, 1]. closed_u wraps u. pole=True collapses v=0 to
    one point (caps). inner = "full": whole inner skin (closed solid); "lip": inner skin only
    one cell deep along every open edge (shells hidden against the body — the visible edge
    still has thickness); "none": single outer skin (surface bands like plaid stripes).
    """
    us = [i / nu for i in range(nu)] if closed_u else [i / (nu - 1) for i in range(nu)]
    if vs is None:
        vs = [j / nv for j in range(1, nv + 1)] if pole else [j / (nv - 1) for j in range(nv)]
    nU, nV = len(us), len(vs)
    bm = bmesh.new()
    O = [[bm.verts.new(f_out(u, v)) for u in us] for v in vs]

    def wanted(j, i):
        if inner == "full":
            return True
        if inner == "none":
            return False
        edge_rows = {nV - 2, nV - 1} | (set() if pole else {0, 1})
        edge_cols = set() if closed_u else {0, 1, nU - 2, nU - 1}
        return j in edge_rows or i in edge_cols
    I = {}
    for j in range(nV):
        for i in range(nU):
            if wanted(j, i):
                I[(j, i)] = bm.verts.new(f_in(us[i], vs[j]))
    span = range(nU if closed_u else nU - 1)

    def quad(a, b, c, d, flip=False):
        try:
            bm.faces.new((d, c, b, a) if flip else (a, b, c, d))
        except ValueError:
            pass

    for j in range(nV - 1):
        for i in span:
            k = (i + 1) % nU
            quad(O[j][i], O[j][k], O[j + 1][k], O[j + 1][i])
            ks = [(j, i), (j, k), (j + 1, k), (j + 1, i)]
            if all(x in I for x in ks):
                quad(*[I[x] for x in ks], flip=True)
    if pole:
        po = bm.verts.new(f_out(0.0, 0.0))
        for i in span:
            bm.faces.new((po, O[0][(i + 1) % nU], O[0][i]))
        if inner == "full":
            pi = bm.verts.new(f_in(0.0, 0.0))
            for i in span:
                bm.faces.new((pi, I[(0, i)], I[(0, (i + 1) % nU)]))
    if inner != "none":
        last = nV - 1
        for i in span:  # rim at v = 1
            k = (i + 1) % nU
            quad(O[last][i], I[(last, i)], I[(last, k)], O[last][k])
        if not pole:
            for i in span:
                k = (i + 1) % nU
                quad(O[0][k], I[(0, k)], I[(0, i)], O[0][i])
        if not closed_u:
            for j in range(nV - 1):
                quad(O[j][0], O[j + 1][0], I[(j + 1, 0)], I[(j, 0)])
                quad(O[j][-1], I[(j, nU - 1)], I[(j + 1, nU - 1)], O[j + 1][-1])
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if inner != "full":
        _orient_out(bm, centre if centre is not None else Vector((0, 0, 0)))
    return ns.from_bmesh(bm, name)


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def tube(points, radii, sides=8, res=4, name="Tube"):
    return ns.tube([tuple(p) for p in points], radii, sides=sides, resolution=res, name=name)


def rbox(size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.04, seg=2, name="Box"):
    return ns.box(size, loc=loc, rot=rot, bevel=bevel, segments=seg, name=name)


def part(objs, name, color, mat="SmoothPlastic", *, arm=None, bone=None, role=None, smooth=60.0,
         transparency=0.0, shadow=True):
    """Join objs into ONE tagged part (and bind it to `bone` when a rig is given)."""
    objs = [o for o in objs if o is not None]
    if len(objs) > 1:
        o = ns.join_applied(objs, name)
    else:
        o = objs[0]
        ns.apply_all(o)
    ns.tag(o, name, color, mat, recolor=role, smooth_angle=smooth, transparency=transparency,
           cast_shadow=shadow)
    if arm is not None and bone:
        ns.bind(o, arm, bone)
    elif bone:
        o["ns_bone"] = bone
    return o


def bvh_of(objs):
    """World-space BVH of the evaluated meshes of objs."""
    dg = bpy.context.evaluated_depsgraph_get()
    verts, polys = [], []
    for o in objs:
        me = o.evaluated_get(dg).to_mesh()
        off = len(verts)
        mw = o.matrix_world
        verts.extend(mw @ v.co for v in me.vertices)
        polys.extend([off + i for i in p.vertices] for p in me.polygons)
        o.evaluated_get(dg).to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)


def surf_y(bvh, x, z, y0=-3.0):
    """Front surface y of a body at (x, z) by ray-casting from the front (-Y)."""
    hit = bvh.ray_cast(Vector((x, y0, z)), Vector((0, 1, 0)))
    return hit[0].y if hit[0] is not None else None


def surf_x(bvh, y, z, side=1.0):
    hit = bvh.ray_cast(Vector((3.0 * side, y, z)), Vector((-side, 0, 0)))
    return hit[0].x if hit[0] is not None else None


# --------------------------------------------------------------------------------------
# Head surface (used by the head mesh AND by hair/hats/beards so they fit exactly)
# --------------------------------------------------------------------------------------

def head_dir(phi: float, psi: float) -> Vector:
    """Unit direction. phi 0 = front (-Y), +pi/2 = +X; psi 0 = top, pi = bottom."""
    sp = math.sin(psi)
    return Vector((sp * math.sin(phi), -sp * math.cos(phi), math.cos(psi)))


def _gauss(dphi, dpsi, sphi, spsi):
    return math.exp(-(dphi / sphi) ** 2 - (dpsi / spsi) ** 2)


def head_bump(phi: float, psi: float) -> float:
    """Small radial offsets that give the ellipsoid cheeks and a softer brow."""
    phi = (phi + math.pi) % (2 * math.pi) - math.pi
    b = 0.0
    for sgn in (1, -1):
        b += 0.035 * _gauss(phi - sgn * 0.75, psi - 1.95, 0.35, 0.3)   # cheeks
    b += 0.02 * _gauss(phi, psi - 1.15, 0.6, 0.2)                     # brow ridge
    return b


def head_pt(phi: float, psi: float, infl: float = 0.0) -> Vector:
    d = head_dir(phi, psi)
    p = Vector((HEAD_R.x * d.x, HEAD_R.y * d.y, HEAD_R.z * d.z))
    n = Vector((d.x / HEAD_R.x, d.y / HEAD_R.y, d.z / HEAD_R.z)).normalized()
    p = p + n * (infl + head_bump(phi, psi))
    w = d.z
    if w < 0:                                    # jaw: narrower toward the chin, chin forward
        k = 1.0 - 0.2 * (-w) ** 1.6
        p.x *= k
        if p.y < 0:
            p.y *= 1.0 + 0.05 * (-w)
    return HEAD_C + p


# --------------------------------------------------------------------------------------
# Torso surface (garments)
# --------------------------------------------------------------------------------------

def torso_frame(t: float, rings=TORSO):
    t = max(0.0, min(len(rings) - 1.0, t))
    i = min(int(t), len(rings) - 2)
    f = t - i
    r0, r1 = rings[i], rings[i + 1]
    return tuple(r0[k] + (r1[k] - r0[k]) * f for k in range(5))


def torso_pt(phi: float, t: float, infl: float = 0.0, rings=TORSO) -> Vector:
    """Point on the torso (t = ring index, fractional) inflated along the profile normal."""
    z, a, b, n, cy = torso_frame(t, rings)
    dt = 0.05
    z0, a0, b0, _, _ = torso_frame(t - dt, rings)
    z1, a1, b1, _, _ = torso_frame(t + dt, rings)
    dr = ((a1 + b1) - (a0 + b0)) / 2
    dz = z1 - z0
    L = math.hypot(dr, dz) or 1.0
    nr, nz = dz / L, -dr / L
    x, y = se_point(phi, a + infl * nr, b + infl * nr, n, 0.0, cy)
    return Vector((x, y, z + infl * nz))


def t_at_z(z: float, rings=TORSO) -> float:
    for i in range(len(rings) - 1):
        z0, z1 = rings[i][0], rings[i + 1][0]
        if z0 <= z <= z1:
            return i + (z - z0) / (z1 - z0)
    return 0.0 if z < rings[0][0] else len(rings) - 1.0


# --------------------------------------------------------------------------------------
# Body
# --------------------------------------------------------------------------------------
DEFAULT_LOOK = {
    "skin": SKIN, "top": TOP, "pants": PANTS, "shoes": SHOES, "sole": SOLE,
    "eye": EYE_WHITE, "pupil": PUPIL, "brow": BROW, "mouth": MOUTH,
    "generic": True,          # True: runtime roles skin/top/pants/shoes/brow on body parts
    "torso": TORSO,           # torso ring table (a Regular can pass a belly)
    "sleeve": "long",         # "long" (sleeve to wrist) | "short" (skin forearm)
    "brow_tilt": 9.0,         # deg, inner ends up = tired/worried
    "brow_size": (0.19, 0.05, 0.055),
    "lid_drop": 0.045,        # how far the tired upper lid covers the eye (0 = wide awake)
    "skip": (),               # part keys to skip (a Regular builds its own)
    "mouth_curve": 0.018,     # smile depth
    "roles": {},              # per-part role overrides, e.g. {"Torso": "tell_flannel"}
    "arm_color": None,        # sleeve colour if it differs from the top (Walt's cardigan)
    "arm_mat": "SmoothPlastic",
    "extra": {},              # extra objects joined into a body part: {"Torso": [objs]}
}


def _arm_matrix(s: float) -> Matrix:
    """Local arm space (joint at origin, hanging along -Z) -> world rest pose."""
    return Matrix.Translation(shoulder(s)) @ Matrix.Rotation(math.radians(-s * ARM_SPLAY), 4, "Y")


def _hand_matrix(s: float) -> Matrix:
    return Matrix.Translation(wrist(s)) @ Matrix.Rotation(math.radians(-s * ARM_SPLAY), 4, "Y")


def head_mesh(name="Head"):
    """Head + neck + ears + nose as separate objects (caller joins)."""
    nphi, npsi = 20, 12
    bm = bmesh.new()
    top = bm.verts.new(head_pt(0, 0))
    rows = []
    for j in range(1, npsi):
        psi = math.pi * j / npsi
        rows.append([bm.verts.new(head_pt(2 * math.pi * i / nphi, psi)) for i in range(nphi)])
    bot = bm.verts.new(head_pt(0, math.pi))
    for i in range(nphi):
        k = (i + 1) % nphi
        bm.faces.new((top, rows[0][k], rows[0][i]))
        bm.faces.new((bot, rows[-1][i], rows[-1][k]))
    for r0, r1 in zip(rows, rows[1:]):
        for i in range(nphi):
            k = (i + 1) % nphi
            bm.faces.new((r0[i], r0[k], r1[k], r1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    skull = ns.from_bmesh(bm, name)
    neck = ns.cyl(0.215, 0.62, loc=(0, -0.01, 3.72), verts=12, bevel=0.0, name="Neck")
    ears = []
    for s in (1, -1):
        e = ellipsoid((s * 0.615, 0.04, 4.33), (0.075, 0.125, 0.165), segs=8, rings=6,
                      rot=(0, 0, -s * 12), name="Ear")
        ears.append(e)
    nose = ellipsoid((0, -0.63, 4.23), (0.105, 0.09, 0.11), segs=10, rings=6, name="Nose")
    return [skull, neck, nose] + ears


def build_body(arm, look: dict | None = None) -> dict:
    """Build the base human on `arm`. Returns {key: object}. See DEFAULT_LOOK."""
    L = dict(DEFAULT_LOOK)
    L.update(look or {})
    gen = L["generic"]
    skip = set(L["skip"])
    over = L["roles"]
    ext = L["extra"]
    out = {}

    def R(r, key=None):
        if key in over:
            return over[key]
        return r if gen else None

    # ---------------- Hips (pelvis / seat of the trousers)
    if "Hips" not in skip:
        pel = loft_z([(1.66, 0.34, 0.27, 2.2, 0.02), (1.70, 0.50, 0.36, 2.3, 0.02),
                      (1.80, 0.585, 0.415, 2.4, 0.025), (1.98, 0.63, 0.435, 2.4, 0.015),
                      (2.20, 0.635, 0.435, 2.4, 0.0), (2.40, 0.61, 0.42, 2.4, 0.0),
                      (2.46, 0.5, 0.34, 2.2, 0.0)], segs=20, name="Pelvis")
        out["Hips"] = part([pel] + ext.get("Hips", []), "Hips", L["pants"], arm=arm, bone="Hips",
                           role=R("pants", "Hips"), smooth=70)

    # ---------------- Torso (shirt) + crew collar
    if "Torso" not in skip:
        rings = list(L["torso"])
        if L.get("torso_hidden"):     # fully covered by a Regular's garment: cheap stand-in
            low = [rings[0], rings[3], rings[5], rings[6], rings[7], rings[8]]
            parts_t = [loft_z([r[:4] + (0.0, r[4]) for r in low], segs=12, name="Shirt")]
        else:
            body = loft_z([r[:4] + (0.0, r[4]) for r in rings], segs=20, name="Shirt")
            hem = loft_z([(2.17, rings[0][1] + 0.012, rings[0][2] + 0.012, 2.4),
                          (2.27, rings[0][1] + 0.016, rings[0][2] + 0.016, 2.4)], segs=20, cap1=False, name="Hem")
            collar = ns.torus(0.255, 0.05, loc=(0, -0.005, 3.6), major_segs=14, minor_segs=5, name="Collar")
            collar.scale = (1.0, 0.88, 1.0)
            parts_t = [body, hem, collar]
        out["Torso"] = part(parts_t + ext.get("Torso", []), "Torso", L["top"], arm=arm, bone="Torso",
                            role=R("top", "Torso"), smooth=65)

    # ---------------- Head (skin, with neck/ears/nose/tired upper lids) and face features
    head = ns.join_applied(head_mesh(), "Head")
    bvh = bvh_of([head])
    out["_head_bvh"] = bvh
    ez, ex = 4.42, 0.225
    face_dark, glints, lids, brows = [], [], [], []
    for side, s in SIDES:
        y = surf_y(bvh, s * ex, ez)
        yaw = -s * 14.0
        fwd = Matrix.Rotation(math.radians(yaw), 3, "Z") @ Vector((0, -1, 0))
        c = Vector((s * ex, y + 0.022, ez))
        eye = ellipsoid(c, (0.11, 0.06, 0.135), segs=12, rings=7, rot=(0, 0, yaw))
        out["Eye" + side] = part([eye], "Eye" + side, L["eye"], arm=arm, bone="Head", role="eye", smooth=80)
        pc = c + fwd * 0.045 + Vector((s * -0.012, 0, -0.008))
        face_dark.append(ellipsoid(pc, (0.066, 0.03, 0.082), segs=8, rings=6, rot=(0, 0, yaw)))
        glints.append(ns.sphere(0.021, loc=tuple(pc + fwd * 0.026 + Vector((s * 0.022, 0, 0.032))),
                                segs=6, rings=4))
        if L["lid_drop"] > 0:     # tired upper lid: skin cap over the top of the eye, droopy outside
            lid = ellipsoid(c + fwd * 0.004, (0.122, 0.07, 0.147), segs=12, rings=8, rot=(0, 0, yaw))
            _bisect_keep(lid, c + Vector((0, 0, 0.147 - L["lid_drop"] * 2.0)), Vector((s * 0.18, 0, 1)))
            lids.append(lid)
        bl = ellipsoid(c + fwd * 0.006, (0.125, 0.072, 0.151), segs=10, rings=7, rot=(0, 0, yaw))
        _bisect_keep(bl, c - fwd * 0.005, fwd)
        out["Eyelid" + side] = part([bl], "Eyelid" + side, L["skin"], arm=arm, bone="Head", role="eyelid",
                                    smooth=80, transparency=1.0, shadow=False)
        bw, bh, bd = L["brow_size"]
        bz = 4.615
        by = surf_y(bvh, s * ex, bz)
        brows.append(rbox((bw, bd, bh), loc=(s * ex, by + 0.005, bz), rot=(0, s * L["brow_tilt"], -s * 14),
                          bevel=0.022, seg=1))
    out["Head"] = part([head] + lids + ext.get("Head", []), "Head", L["skin"], arm=arm, bone="Head",
                       role=R("skin", "Head"), smooth=70)
    out["Brows"] = part(brows, "Brows", L["brow"], arm=arm, bone="Head", role=R("brow", "Brows"), smooth=50)
    pts = []
    for k in range(5):               # mouth: a small soft smile on the face surface
        x = -0.1 + 0.05 * k
        z = 4.045 - L["mouth_curve"] * (1 - (x / 0.1) ** 2)
        pts.append((x, surf_y(bvh, x, z) + 0.004, z))
    face_dark.append(tube(pts, [0.016, 0.021, 0.022, 0.021, 0.016], sides=6, res=3))
    out["Face"] = part(face_dark, "Face", L["pupil"], arm=arm, bone="Head", smooth=70)
    out["Glint"] = part(glints, "Glint", "#FFFFFF", arm=arm, bone="Head", smooth=80)

    # ---------------- Arms + hands
    for side, s in SIDES:
        if "Arm" + side not in skip:
            out["Arm" + side] = build_arm(arm, side, s, L, role=R("top", "Arm" + side), extra=ext.get("Arm" + side, []))
        if "Hand" + side not in skip:
            hd = hand_mesh(s)
            out["Hand" + side] = part([hd] + ext.get("Hand" + side, []), "Hand" + side, L["skin"], arm=arm,
                                      bone="Hand" + side, role=R("skin", "Hand" + side), smooth=70)

    # ---------------- Legs + shoes
    for side, s in SIDES:
        if "Leg" + side not in skip:
            out["Leg" + side] = part([leg_mesh(s)] + ext.get("Leg" + side, []), "Leg" + side, L["pants"], arm=arm,
                                     bone="Leg" + side, role=R("pants", "Leg" + side), smooth=65)
        if "Shoe" + side not in skip:
            up, sole, laces = shoe_meshes(s)
            out["Shoe" + side] = part([up], "Leg" + side + "_Shoe", L["shoes"], arm=arm, bone="Leg" + side,
                                      role=R("shoes", "Shoe" + side), smooth=60)
            out["Sole" + side] = part([sole] + laces, "Leg" + side + "_Sole", L["sole"], arm=arm,
                                      bone="Leg" + side, smooth=45)
    return out


def _bisect_keep(obj, co: Vector, no: Vector):
    """Cut obj with a plane and keep the side the normal points to; fill the cut."""
    ns.apply_all(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=-no, clear_outer=True)
    edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    if edges:
        try:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        except Exception:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def arm_rings(short=False):
    return [(0.205, 0.05, 0.05, 2.0), (0.175, 0.165, 0.16, 2.0), (0.1, 0.24, 0.232, 2.0),
            (-0.04, 0.262, 0.252, 2.1), (-0.35, 0.25, 0.24, 2.1), (-0.7, 0.232, 0.224, 2.1),
            (-1.16, 0.214, 0.206, 2.1)]


def build_arm(arm, side, s, L, color=None, role="top", extra=()):
    """Sleeved arm (long: cuffed to the wrist; short: sleeve to mid-upper-arm + skin forearm).
    `role` is already resolved by the caller (None = no runtime role)."""
    gen = True
    M = _arm_matrix(s)
    color = color or L.get("arm_color") or L["top"]
    amat = L.get("arm_mat", "SmoothPlastic")
    if L.get("sleeve", "long") == "long":
        rings = arm_rings() + [(-1.17, 0.232, 0.224, 2.2), (-1.31, 0.236, 0.228, 2.2), (-1.33, 0.18, 0.175, 2.2)]
        sl = loft_z(rings, segs=14, name="Sleeve")
        xform(sl, M)
        return part([sl] + list(extra), "Arm" + side, color, amat, arm=arm, bone="Arm" + side,
                    role=(role if gen else None), smooth=65)
    rings = arm_rings()[:4] + [(-0.32, 0.262, 0.252, 2.2), (-0.5, 0.268, 0.258, 2.2), (-0.52, 0.2, 0.19, 2.0)]
    sl = loft_z(rings, segs=16, name="Sleeve")
    xform(sl, M)
    fa = loft_z([(-0.45, 0.19, 0.185, 2.0), (-0.75, 0.185, 0.18, 2.0), (-1.1, 0.165, 0.158, 2.0),
                 (-1.3, 0.13, 0.125, 2.0), (-1.36, 0.06, 0.06, 2.0)], segs=14, name="Forearm")
    xform(fa, M)
    sleeve = part([sl] + list(extra), "Arm" + side, color, amat, arm=arm, bone="Arm" + side,
                  role=(role if gen else None), smooth=65)
    part([fa], "Arm" + side + "_Skin", L["skin"], arm=arm, bone="Arm" + side,
         role=("skin" if L["generic"] else None), smooth=70)
    return sleeve


def hand_mesh(s: float):
    """Chunky mitten hand + thumb, palm facing the body, hanging from the wrist."""
    palm = ellipsoid((0, 0, -0.23), (0.125, 0.185, 0.235), segs=10, rings=8)
    ns.apply_all(palm)
    for v in palm.data.vertices:          # curl the finger end toward the palm (-X local)
        if v.co.z < -0.25:
            t = (-0.25 - v.co.z) / 0.215
            v.co.x -= 0.11 * t * t
            v.co.y *= 1.0 - 0.1 * t
    thumb = ellipsoid((-0.035, -0.165, -0.15), (0.068, 0.072, 0.13), segs=8, rings=5, rot=(28, 0, 0))
    wrist_c = ns.cyl(0.13, 0.16, loc=(0, 0, 0.0), verts=10, bevel=0.0)
    h = ns.join_applied([palm, thumb, wrist_c], "Hand")
    if s < 0:
        xform(h, Matrix.Scale(-1, 4, (1, 0, 0)))
        bm = bmesh.new()
        bm.from_mesh(h.data)
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
        bm.to_mesh(h.data)
        bm.free()
    else:
        pass
    # palm faces the body: for the left hand (+X side) the palm is -X; mirror handles the right
    xform(h, _hand_matrix(s))
    return h


def leg_mesh(s: float):
    rings = [(0.3, 0.2, 0.2, 2.0), (0.33, 0.285, 0.29, 2.1), (0.48, 0.29, 0.295, 2.1),
             (0.51, 0.275, 0.28, 2.1), (0.95, 0.285, 0.29, 2.1), (1.45, 0.315, 0.318, 2.1),
             (1.85, 0.325, 0.325, 2.1), (2.18, 0.30, 0.30, 2.1), (2.24, 0.19, 0.19, 2.0)]
    lg = loft_z([(z, a, b, n, s * LEG_X, 0.0) for z, a, b, n in rings], segs=14, name="Leg")
    return lg


SHOE_X = 0.37


def shoe_meshes(s: float):
    """Chunky sneaker: upper, sole (with toe spring) and three lace bars."""
    x0 = s * SHOE_X
    up_rings = [(0.33, 0.11, 0.21, 0.10), (0.29, 0.21, 0.23, 0.155), (0.16, 0.25, 0.245, 0.165),
                (-0.06, 0.255, 0.212, 0.14), (-0.29, 0.243, 0.172, 0.10), (-0.48, 0.21, 0.152, 0.08),
                (-0.59, 0.12, 0.146, 0.058)]
    bm = bmesh.new()
    segs = 12
    vr = []
    for (y, a, zc, c) in up_rings:
        row = []
        for i in range(segs):
            ang = 2 * math.pi * i / segs
            x = x0 + a * _sgnpow(math.sin(ang), 2 / 2.5)
            z = zc + c * _sgnpow(math.cos(ang), 2 / 2.5)
            row.append(bm.verts.new((x, y, z)))
        vr.append(row)
    for r0, r1 in zip(vr, vr[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    for row in (vr[0], vr[-1]):
        c = sum((v.co for v in row), Vector()) / segs
        cv = bm.verts.new(c)
        for i in range(segs):
            bm.faces.new((cv, row[i], row[(i + 1) % segs]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    upper = ns.from_bmesh(bm, "Upper")
    # sole: boxy loft along Y with toe spring
    so_rings = [(0.355, 0.13, 0.03, 0.10), (0.315, 0.235, 0.005, 0.105), (-0.33, 0.27, 0.0, 0.10),
                (-0.52, 0.235, 0.024, 0.11), (-0.63, 0.13, 0.06, 0.118)]
    bm = bmesh.new()
    vr = []
    for (y, a, z0, z1) in so_rings:
        row = []
        for i in range(segs):
            ang = 2 * math.pi * i / segs
            x = x0 + a * _sgnpow(math.sin(ang), 2 / 4.0)
            z = (z0 + z1) / 2 + (z1 - z0) / 2 * _sgnpow(math.cos(ang), 2 / 4.0)
            row.append(bm.verts.new((x, y, z)))
        vr.append(row)
    for r0, r1 in zip(vr, vr[1:]):
        for i in range(segs):
            j = (i + 1) % segs
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    for row in (vr[0], vr[-1]):
        c = sum((v.co for v in row), Vector()) / segs
        cv = bm.verts.new(c)
        for i in range(segs):
            bm.faces.new((cv, row[i], row[(i + 1) % segs]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    sole = ns.from_bmesh(bm, "Sole")
    laces = []
    for k, (y, z) in enumerate(((-0.06, 0.348), (-0.19, 0.306), (-0.32, 0.266))):
        laces.append(rbox((0.22, 0.05, 0.035), loc=(x0, y, z), rot=(-18 - 6 * k, 0, 0), bevel=0.0, seg=1))
    return upper, sole, laces


# --------------------------------------------------------------------------------------
# Review renders
# --------------------------------------------------------------------------------------

def quick_render(path, views=((-30, 12), (0, 5), (90, 5), (180, 10)), res=420, samples=10,
                 objects=None, fov=30.0, margin=1.08, floor=True, focus=None):
    """Low-sample Cycles turnaround for iteration: one tile per (yaw, pitch)."""
    from PIL import Image
    objs = objects or ns._tagged_objects()
    lo, hi = ns.bbox_world(objs) if focus is None else focus
    fl = None
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, min(lo.z, 0.0) - 0.002))
        fl = bpy.context.active_object
        fl.name = "Floor"
        fl.data.materials.append(ns.material("#3A3B42"))
    ns._setup_render(res, samples)
    tiles = []
    for i, (yaw, pitch) in enumerate(views):
        ns._clear_rig() if False else None
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cam, ctr, dist = ns._camera_fit(lo, hi, yaw, pitch, fov_deg=fov, margin=margin)
        k = math.radians(yaw)
        ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * dist, 60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3)) * dist, 22 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        ns._light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.8)) * dist, 35 * dist ** 2 / 9, size=dist * 0.4, target=ctr)
        p = f"{path}_{i}.png"
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        tiles.append(p)
    for o in list(bpy.context.scene.objects):
        if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim", "Floor")):
            bpy.data.objects.remove(o, do_unlink=True)
    ims = [Image.open(p).convert("RGB") for p in tiles]
    combo = Image.new("RGB", (res * len(ims), res))
    for i, im in enumerate(ims):
        combo.paste(im, (i * res, 0))
    combo.save(path + ".png")
    for p in tiles:
        os.remove(p)
    return path + ".png"


# --------------------------------------------------------------------------------------
# ANIMATION — the nine "Human" clips
# --------------------------------------------------------------------------------------
# Keys are bone-local Euler XYZ degrees (see the skeleton note) + optional location (studs).
# Locomotion is authored on analytic gait curves: during stance the leg angle follows
# asin(linear) so the foot moves back at exactly clipSpeedRef; hip height is then solved
# per key so the planted shoe's lowest point sits on the floor. Every bone is keyed in
# every clip (start and end at least).

def _q(rot) -> Quaternion:
    return Euler(tuple(math.radians(a) for a in rot), "XYZ").to_quaternion()


def _deg(q: Quaternion):
    return tuple(math.degrees(a) for a in q.to_euler("XYZ"))


def _basis(a: Vector, b: Vector) -> Matrix:
    a = a.normalized()
    b = (b - a * b.dot(a)).normalized()
    return Matrix((a, b, a.cross(b))).transposed()


LOC_BONES = {"Hips", "LegL", "LegR"}


class Clip:
    def __init__(self, arm, name, end, loop=True, fps=30):
        self.arm, self.name, self.end, self.fps, self.loop = arm, name, end, fps, loop
        self.act = ns.new_action(arm, name, 0, end, loop=loop, fps=fps)
        self.keys = {b: {} for b in BONES}
        self.done = set()

    # authoring
    def k(self, bone, f, rot=(0, 0, 0), loc=None, ease="SINE", d="EASE_IN_OUT"):
        self.keys[bone][int(f)] = (tuple(rot), None if loc is None else tuple(loc), ease, d)

    def get(self, bone, f):
        return self.keys[bone].get(int(f), ((0, 0, 0), None, "SINE", "EASE_IN_OUT"))

    def commit(self, bones=None):
        for b in (bones or BONES):
            if b in self.done:
                continue
            ks = self.keys[b]
            if 0 not in ks:
                ks[0] = ((0, 0, 0), None, "SINE", "EASE_IN_OUT")
            if self.end not in ks:
                ks[self.end] = ks[0] if self.loop else ((0, 0, 0), None, "SINE", "EASE_IN_OUT")
            has_loc = b in LOC_BONES or any(v[1] is not None for v in ks.values())
            for f in sorted(ks):
                rot, loc, ease, d = ks[f]
                if has_loc and loc is None:
                    loc = (0, 0, 0)
                ns.key(self.arm, b, f, rot=rot, loc=loc, ease=ease, direction=d)
            self.done.add(b)

    def finish(self):
        self.commit()
        fix_quat_continuity(self.arm, self.act)
        bpy.context.scene.frame_set(0)
        return self.act

    # evaluation / IK
    def pose_at(self, f):
        bpy.context.scene.frame_set(int(f))
        return self.arm.pose.bones

    def world_q(self, bone, f) -> Quaternion:
        return self.pose_at(f)[bone].matrix.to_quaternion()

    def aim(self, bone, f, target_dir, rest_dir, twist=0.0):
        pq = self.world_q(PARENT[bone], f)
        lt = pq.inverted() @ Vector(target_dir).normalized()
        q = Vector(rest_dir).rotation_difference(lt)
        if twist:
            q = q @ Quaternion(Vector(rest_dir).normalized(), math.radians(twist))
        return _deg(q)

    def aim_arm(self, side, f, point=None, direction=None, twist=0.0):
        s = 1.0 if side == "L" else -1.0
        if direction is None:
            direction = Vector(point) - self.pose_at(f)["Arm" + side].head
        return self.aim("Arm" + side, f, direction, arm_dir(s), twist)

    def orient_hand(self, side, f, long_dir, palm_dir):
        s = 1.0 if side == "L" else -1.0
        pq = self.world_q("Arm" + side, f)
        rest = _basis(arm_dir(s), Vector((-s, 0, 0)))
        want = _basis(Vector(long_dir), Vector(palm_dir))
        return _deg(pq.inverted() @ (want @ rest.inverted()).to_quaternion())


def fix_quat_continuity(arm, act):
    """Keep consecutive quaternion keys in one hemisphere (no long-way interpolation)."""
    fcs = ns._action_fcurves(act)
    for b in BONES:
        path = f'pose.bones["{b}"].rotation_quaternion'
        comp = sorted([fc for fc in fcs if fc.data_path == path], key=lambda fc: fc.array_index)
        if len(comp) != 4:
            continue
        n = len(comp[0].keyframe_points)
        prev = None
        for i in range(n):
            q = [comp[c].keyframe_points[i].co.y for c in range(4)]
            if prev is not None and sum(a * b for a, b in zip(q, prev)) < 0:
                for c in range(4):
                    kp = comp[c].keyframe_points[i]
                    kp.co.y = -kp.co.y
                    kp.handle_left.y = -kp.handle_left.y
                    kp.handle_right.y = -kp.handle_right.y
                q = [-x for x in q]
            prev = q
        for c in comp:
            c.update()


# ---- feet / contact helpers ------------------------------------------------------------

def rest_points(arm, bone_filter, name_filter=None):
    """{bone: (N,3) numpy array} of rest-pose world vertices of parts bound to those bones."""
    import numpy as np
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    for o in ns._tagged_objects():
        b = o.get("ns_bone")
        if b not in bone_filter:
            continue
        if name_filter and not any(k in o["ns_part"] for k in name_filter):
            continue
        me = o.evaluated_get(dg).to_mesh()
        M = arm.matrix_world.inverted() @ o.matrix_world      # armature space
        pts = np.array([tuple(M @ v.co) for v in me.vertices])
        o.evaluated_get(dg).to_mesh_clear()
        out[b] = pts if b not in out else np.vstack([out[b], pts])
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()
    return out


def posed(arm, bone, pts):
    import numpy as np
    pb = arm.pose.bones[bone]
    M = arm.matrix_world @ pb.matrix @ arm.data.bones[bone].matrix_local.inverted()
    A = np.array(M)
    return pts @ A[:3, :3].T + A[:3, 3]


def gait_leg(tau, theta, stance, lift, abd, over=0.0):
    """Leg pitch (deg, - = forward), lift (studs) and abduction (deg) at gait phase tau.

    tau 0 = heel contact with the leg forward. Stance: the foot sweeps back linearly in
    space (asin), so it stays planted while the body moves at the reference speed."""
    st = math.sin(math.radians(theta))
    if tau < stance:
        s = tau / stance
        return math.degrees(math.asin((2 * s - 1) * st)), 0.0, 0.0
    s = (tau - stance) / (1 - stance)
    if over > 0 and s > 0.8:
        u = (s - 0.8) / 0.2
        pitch = -theta - over + over * (1 - math.cos(math.pi * u)) / 2
    else:
        u = s / 0.8 if over > 0 else s
        e = (1 - math.cos(math.pi * u)) / 2
        pitch = theta - (2 * theta + over) * e
    return pitch, lift * math.sin(math.pi * s) ** 0.8, abd * math.sin(math.pi * s)


def solve_hip_height(clip, feet, frames, base=None, flight=None):
    """Re-key Hips so the lowest point of either foot touches the floor at each frame.
    base: {f: (rot, (x, y, z))} current Hips keys; flight: {f: extra lift} for airborne keys."""
    arm = clip.arm
    out = {}
    for f in frames:
        clip.pose_at(f)
        mz = min(posed(arm, b, feet[b])[:, 2].min() for b in ("LegL", "LegR"))
        rot, loc, ease, d = clip.get("Hips", f)
        loc = loc or (0, 0, 0)
        out[f] = loc[2] - mz
    if flight:
        for f, extra in flight.items():
            out[f] = out[f] + extra
    for f in frames:
        rot, loc, ease, d = clip.get("Hips", f)
        loc = loc or (0, 0, 0)
        ns.key(arm, "Hips", f, rot=rot, loc=(loc[0], loc[1], out[f]), ease=ease, direction=d)
        clip.keys["Hips"][f] = (rot, (loc[0], loc[1], out[f]), ease, d)
    return out


def gait_report(arm, act, feet, speed, contact_eps=0.03):
    """Measure foot behaviour of a locomotion clip at its reference speed.
    Returns dict: penetration (most negative foot z), slide per step (studs the planted
    contact vertex travels on the floor), hover (max contact gap while supporting)."""
    import numpy as np
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and len(act.slots):
        arm.animation_data.action_slot = act.slots[0]
    fps, end = act["ns_fps"], act["ns_end"]
    res = {"minZ": 9.0, "slide": {"LegL": 0.0, "LegR": 0.0}, "maxSlideSpeed": 0.0, "supportGap": 0.0}
    prev = {}
    for f in range(0, end + 1):
        bpy.context.scene.frame_set(f)
        t = f / fps
        cur = {}
        lows = []
        for b in ("LegL", "LegR"):
            P = posed(arm, b, feet[b])
            P[:, 1] -= speed * t
            cur[b] = P
            lows.append(P[:, 2].min())
        res["minZ"] = min(res["minZ"], min(lows))
        res["supportGap"] = max(res["supportGap"], min(lows))
        for b in ("LegL", "LegR"):
            if b in prev:
                P0, P1 = prev[b], cur[b]
                i = int(np.argmin(P0[:, 2]))
                if P0[i, 2] < contact_eps and P1[i, 2] < contact_eps:
                    d = float(np.hypot(P1[i, 0] - P0[i, 0], P1[i, 1] - P0[i, 1]))
                    res["slide"][b] += d
                    res["maxSlideSpeed"] = max(res["maxSlideSpeed"], d * fps)
        prev = cur
    bpy.context.scene.frame_set(0)
    return res


OVERLAP_PAIRS = [("HandL", "Head"), ("HandR", "Head"), ("HandL", "Torso"), ("HandR", "Torso"),
                 ("HandL", "HandR"), ("ArmL", "Head"), ("ArmR", "Head"), ("HandL", "Hips"),
                 ("HandR", "Hips"), ("HandL", "LegL"), ("HandR", "LegR"), ("ArmL", "LegL"),
                 ("ArmR", "LegR"), ("LegL", "LegR"), ("ArmL", "ArmR"), ("HandL", "ArmR"),
                 ("HandR", "ArmL"), ("ArmL", "Hips"), ("ArmR", "Hips"), ("Head", "Torso_far")]


def overlap_report(arm, act, frames, pairs=OVERLAP_PAIRS):
    """Triangle-intersection counts between non-adjacent body parts at given frames."""
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and len(act.slots):
        arm.animation_data.action_slot = act.slots[0]
    by_bone = {}
    for o in ns._tagged_objects():
        if o.get("ns_role") == "eyelid":
            continue
        by_bone.setdefault(o.get("ns_bone"), []).append(o)
    hits = {}
    for f in frames:
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        trees = {}
        for a, b in pairs:
            if a not in by_bone or b not in by_bone:
                continue
            for x in (a, b):
                if x not in trees:
                    trees[x] = bvh_of(by_bone[x])
            n = len(trees[a].overlap(trees[b]))
            if n:
                hits.setdefault(f, []).append(f"{a}x{b}:{n}")
    bpy.context.scene.frame_set(0)
    return hits


def _static(c, bones, frames=None):
    for b in bones:
        for f in (frames or (0, c.end)):
            c.k(b, f)


def _rot_yz(P, deg):
    a = math.radians(deg)
    c, sn = math.cos(a), math.sin(a)
    return P[:, 0] * c - P[:, 1] * sn, P[:, 0] * sn + P[:, 1] * c


def stance_profile(P, theta1, dys):
    """Leg pitch per frame through stance so the CURRENT contact vertex stays planted.
    P: (N, 2) foot vertices (y, z) relative to the hip joint; dys: backward travel per frame."""
    import numpy as np
    p = -theta1
    out = [p]
    for dy in dys:
        Y, Z = _rot_yz(P, p)
        i = int(np.argmin(Z))
        y, z = P[i]
        target = Y[i] + dy
        lo, hi = 0.0, 20.0
        for _ in range(40):
            mid = (lo + hi) / 2
            a = math.radians(p + mid)
            if y * math.cos(a) - z * math.sin(a) < target:
                lo = mid
            else:
                hi = mid
        p += (lo + hi) / 2
        out.append(p)
    return out


def _zmin(P, deg):
    return _rot_yz(P, deg)[1].min()


def solve_gait(feet, n_stance, dys, equal_ends=True, theta1=None):
    """Pick the landing angle so heel-strike and toe-off are at the same height (walk), or
    use a fixed landing angle (run). Returns the stance pitch list."""
    import numpy as np
    P = feet["LegL"][:, 1:3] - np.array([hip(1).y, hip(1).z])
    if not equal_ends:
        return stance_profile(P, theta1, dys)
    lo, hi = 8.0, 40.0
    for _ in range(40):
        mid = (lo + hi) / 2
        prof = stance_profile(P, mid, dys)
        if _zmin(P, prof[0]) > _zmin(P, prof[-1]):     # heel too high -> land less forward
            hi = mid
        else:
            lo = mid
    return stance_profile(P, (lo + hi) / 2, dys)


def _lift(s, h, rise=0.22):
    if s < 0.5:
        return h * smoothstep(0, rise, s)
    return h * smoothstep(0, rise, 1 - s)


def clip_walk(arm, feet):
    """Brisk 9 studs/s customer walk (0.467 s cycle, 60 fps keys)."""
    T, fps, v = 28, 60, WALK_SPEED
    H = T // 2

    def yaw(f):
        return -5 * math.cos(2 * math.pi * f / T)

    def hip_y(f, s):
        return s * LEG_X * math.sin(math.radians(yaw(f)))

    dys = [v / fps - (hip_y(k + 1, 1) - hip_y(k, 1)) for k in range(H)]
    prof = solve_gait(feet, H, dys)
    th1, th2 = -prof[0], prof[-1]
    c = Clip(arm, "Walk", T, loop=True, fps=fps)
    frames = list(range(0, T + 1))

    def leg_pitch(f, off):
        k = (f - off) % T
        if k <= H:
            return prof[k], 0.0, 0.0
        sw = (k - H) / (T - H)
        e = (1 - math.cos(math.pi * sw)) / 2
        return th2 - (th1 + th2) * e, _lift(sw, 0.16), 4.0 * math.sin(math.pi * sw)

    for f in frames:
        ph = 2 * math.pi * f / T
        hy, hr, hx = yaw(f), 3 * math.sin(ph), 0.035 * math.sin(ph)
        c.k("Hips", f, (0, hr, hy), (hx, 0, 0), ease="LINEAR")
        for side, s, off in (("L", 1, 0), ("R", -1, H)):
            p, lift, ab = leg_pitch(f, off)
            c.k("Leg" + side, f, (p, -s * ab - hr, -hy), (0, 0, lift), ease="LINEAR")
        if f % 2 == 0:
            c.k("Torso", f, (5 + 1.2 * math.cos(2 * ph), -0.6 * hr, 9 * math.cos(ph)), ease="LINEAR")
            c.k("Head", f, (-4 - 1.2 * math.cos(2 * ph - 0.4), -0.3 * hr, -4 * math.cos(ph)), ease="LINEAR")
            for side, s in SIDES:
                c.k("Arm" + side, f, (s * 21 * math.cos(ph - 0.35), -s * 2.5, 0), ease="LINEAR")
                c.k("Hand" + side, f, (s * 9 * math.cos(ph - 0.9) - 6, 0, 0), ease="LINEAR")
    c.commit()
    solve_hip_height(c, feet, frames)
    c.info = {"land": th1, "toeoff": th2}
    return c.finish()


CHASE_TWITCH = [0, 0, 0, 10, 10, -5, -5, 0, 0, 0, 14, 14, 14, 0, -8, -8, 0, 0, 6, 6, 0]


def clip_chase(arm, feet):
    """The Copy's 20 studs/s chase: pitched forward, head cocked and twitching, arms
    reaching like it's grabbing — wrong on purpose (0.333 s cycle, flight phases)."""
    T, fps, v, NS = 20, 60, CHASE_SPEED, 7
    H = T // 2

    def yaw(f):
        return -8 * math.cos(2 * math.pi * f / T)

    def hip_y(f, s):
        return s * LEG_X * math.sin(math.radians(yaw(f)))

    dys = [v / fps - (hip_y(k + 1, 1) - hip_y(k, 1)) for k in range(NS)]
    prof = solve_gait(feet, NS, dys, equal_ends=False, theta1=24.0)
    th1, th2 = -prof[0], prof[-1]
    over = 12.0
    c = Clip(arm, "ChaseRun", T, loop=True, fps=fps)
    frames = list(range(0, T + 1))

    def leg_pitch(f, off):
        k = (f - off) % T
        if k <= NS:
            return prof[k], 0.0, 0.0
        sw = (k - NS) / (T - NS)
        if sw < 0.75:
            e = (1 - math.cos(math.pi * sw / 0.75)) / 2
            p = th2 - (th1 + th2 + over) * e
        else:
            u = (sw - 0.75) / 0.25
            p = -th1 - over + over * (1 - math.cos(math.pi * u)) / 2
        return p, _lift(sw, 0.3, 0.18), 7.0 * math.sin(math.pi * sw)

    for f in frames:
        ph = 2 * math.pi * f / T
        hy, hr, hx = yaw(f), 6 * math.sin(ph), 0.05 * math.sin(ph)
        c.k("Hips", f, (0, hr, hy), (hx, 0, 0), ease="LINEAR")
        for side, s, off in (("L", 1, 0), ("R", -1, H)):
            p, lift, ab = leg_pitch(f, off)
            c.k("Leg" + side, f, (p, -s * ab - hr, -hy), (0, 0, lift), ease="LINEAR")
        tr = 9 * math.sin(ph + 0.6) + 5
        c.k("Torso", f, (25 + 3 * math.cos(2 * ph), tr - hr, 14 * math.cos(ph)), ease="LINEAR")
        tw = CHASE_TWITCH[f]
        c.k("Head", f, (-24 - 3 * math.cos(2 * ph) + 0.4 * tw, 24 - tr + tw, -6 * math.cos(ph) - 0.6 * tw),
            ease="LINEAR")
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for f in frames:
        ph = 2 * math.pi * f / T
        dl = Vector((0.34, -0.86 - 0.14 * math.cos(ph), -0.18 + 0.2 * math.sin(ph)))
        dr = Vector((-0.4, -0.8 + 0.14 * math.cos(ph), 0.06 - 0.2 * math.sin(ph)))
        c.k("ArmL", f, c.aim_arm("L", f, direction=dl, twist=-65), ease="LINEAR")
        c.k("ArmR", f, c.aim_arm("R", f, direction=dr, twist=70), ease="LINEAR")
    c.commit(["ArmL", "ArmR"])
    for f in frames:
        j = CHASE_TWITCH[(f + 7) % T]
        c.k("HandL", f, (-38 + j, 8, -j), ease="LINEAR")
        c.k("HandR", f, (-34 - j, -8, j * 0.5), ease="LINEAR")
    c.commit()
    fl = {}
    for a in (NS, H + NS):          # airborne between toe-off and the other foot's contact
        for k in range(a + 1, a + (H - NS)):
            u = (k - a) / (H - NS)
            fl[k] = 0.09 * math.sin(math.pi * u)
    solve_hip_height(c, feet, frames, flight=fl)
    c.info = {"land": th1, "toeoff": th2}
    return c.finish()


def clip_idle(arm):
    c = Clip(arm, "Idle", 120, loop=True, fps=30)
    _static(c, ["Hips", "LegL", "LegR"])
    for f, p, r in ((0, 0, 0), (30, -1.6, 0.8), (60, 0, 1.2), (90, -1.6, -0.6), (120, 0, 0)):
        c.k("Torso", f, (p, r, 0))
    for f, rot in ((0, (0, 0, 0)), (18, (-2, 0, 13)), (40, (0, 0, 10)), (52, (2, 0, 0)), (64, (7, 3, 0)),
                   (78, (4, 2, -3)), (90, (0, 0, -11)), (108, (-1, 0, -2)), (120, (0, 0, 0))):
        c.k("Head", f, rot)
    for side, s in SIDES:
        for f, p, r in ((0, 0, 0), (30, 1.5, 1.5), (60, 0, 0), (90, 1.5, 1.5), (120, 0, 0)):
            c.k("Arm" + side, f, (p, -s * r, 0))
        for f, p in ((0, -4), (45, -8), (75, -6), (120, -4)):
            c.k("Hand" + side, f, (p, 0, 0))
    return c.finish()


def clip_wave(arm):
    c = Clip(arm, "Wave", 46, loop=False, fps=30)
    _static(c, ["Hips", "LegL", "LegR"])
    for f, t, h in ((0, (0, 0, 0), (0, 0, 0)), (9, (0, 3, -5), (-3, 6, 5)), (38, (0, 3, -5), (-3, 6, 5)),
                    (46, (0, 0, 0), (0, 0, 0))):
        c.k("Torso", f, t)
        c.k("Head", f, h)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    seq = [(9, (-0.5, -0.3, 0.81)), (13, (-0.66, -0.26, 0.7)), (17, (-0.36, -0.3, 0.88)),
           (21, (-0.66, -0.26, 0.7)), (25, (-0.36, -0.3, 0.88)), (29, (-0.66, -0.26, 0.7)),
           (33, (-0.4, -0.3, 0.86)), (38, (-0.5, -0.3, 0.8))]
    c.k("ArmR", 0)
    for f, d in seq:
        c.k("ArmR", f, c.aim_arm("R", f, direction=Vector(d)), ease="BACK" if f == 9 else "SINE",
            d="EASE_OUT" if f == 9 else "EASE_IN_OUT")
    c.k("ArmR", 46)
    for f, rot in ((0, (0, 0, 0)), (9, (-3, 2, 0)), (38, (-3, 2, 0)), (46, (0, 0, 0))):
        c.k("ArmL", f, rot)
    c.commit(["ArmR", "ArmL"])
    c.k("HandR", 0)
    for i, (f, d) in enumerate(seq):
        tilt = 0 if f in (9, 38) else (1 if i % 2 else -1)
        long = Vector(d).normalized()
        palm = Vector((0.22 * tilt, -1, 0))
        long = (long + Vector((-0.45 * tilt, 0, 0))).normalized()
        c.k("HandR", f, c.orient_hand("R", f, long, palm))
    c.k("HandR", 46)
    _static(c, ["HandL"])
    return c.finish()


def clip_happy(arm):
    c = Clip(arm, "Happy", 40, loop=False, fps=30)
    hips = {0: 0, 5: 0, 11: 0.34, 17: 0, 22: 0.13, 27: 0, 40: 0}
    eases = {0: ("SINE", "EASE_IN_OUT"), 5: ("QUAD", "EASE_OUT"), 11: ("QUAD", "EASE_IN"),
             17: ("QUAD", "EASE_OUT"), 22: ("QUAD", "EASE_IN"), 27: ("SINE", "EASE_IN_OUT"),
             40: ("SINE", "EASE_IN_OUT")}
    for f, z in hips.items():
        c.k("Hips", f, (0, 0, 0), (0, 0, z), *eases[f])
    for side, s in SIDES:
        for f, rot in ((0, (0, 0, 0)), (5, (0, 0, 0)), (11, (10, -s * 4, 0)), (17, (0, 0, 0)),
                       (22, (5, -s * 2, 0)), (27, (0, 0, 0)), (40, (0, 0, 0))):
            c.k("Leg" + side, f, rot, None, *eases[f])
    for f, t, h in ((0, (0, 0, 0), (0, 0, 0)), (5, (8, 0, 0), (6, 0, 0)), (11, (-6, 0, 0), (-12, 0, 0)),
                    (17, (4, 0, 0), (0, 0, 0)), (22, (-3, 0, 0), (-6, 8, 0)), (27, (2, 0, 0), (2, 5, 0)),
                    (40, (0, 0, 0), (0, 0, 0))):
        c.k("Torso", f, t, None, *eases[f])
        c.k("Head", f, h, None, *eases[f])
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    arms = {5: None, 11: (0.6, -0.22, 0.77), 17: (0.74, -0.28, 0.6), 22: (0.55, -0.22, 0.8),
            27: (0.42, -0.5, -0.6)}
    for side, s in SIDES:
        c.k("Arm" + side, 0)
        c.k("Arm" + side, 5, (25, -s * 4, 0), None, *eases[5])
        for f in (11, 17, 22, 27):
            d = Vector(arms[f])
            d.x *= s
            c.k("Arm" + side, f, c.aim_arm(side, f, direction=d), None, *eases[f])
        c.k("Arm" + side, 40)
    c.commit(["ArmL", "ArmR"])
    for side, s in SIDES:
        c.k("Hand" + side, 0)
        c.k("Hand" + side, 5, (10, 0, 0))
        for f in (11, 17, 22):
            d = Vector(arms[f])
            d.x *= s
            c.k("Hand" + side, f, c.orient_hand(side, f, d, Vector((0, -1, 0.2))), None, *eases[f])
        c.k("Hand" + side, 27, (-10, 0, 0))
        c.k("Hand" + side, 40)
    return c.finish()


def clip_upset(arm):
    c = Clip(arm, "Upset", 54, loop=False, fps=30)
    _static(c, ["Hips", "LegL", "LegR"])
    torso = {0: (0, 0, 0), 7: (-5, 0, 0), 12: (12, 0, 0), 42: (12, 0, 0), 48: (8, 0, 0), 54: (0, 0, 0)}
    head = {0: (0, 0, 0), 7: (-10, 0, 0), 12: (18, 0, 0), 18: (16, 0, -18), 24: (16, 0, 18), 30: (15, 0, -14),
            36: (14, 0, 9), 42: (12, 0, 0), 48: (8, 0, 0), 54: (0, 0, 0)}
    for f, r in torso.items():
        c.k("Torso", f, r, None, "EXPO" if f == 7 else "SINE", "EASE_IN" if f == 7 else "EASE_IN_OUT")
    for f, r in head.items():
        c.k("Head", f, r)
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    for side, s in SIDES:
        c.k("Arm" + side, 0)
        c.k("Arm" + side, 7, c.aim_arm(side, 7, direction=Vector((s * 0.62, -0.32, -0.72))), None, "EXPO", "EASE_IN")
        for f in (12, 42):
            c.k("Arm" + side, f, (-5, s * 1.5, 0))
        c.k("Arm" + side, 48, (-3, 0, 0))
        c.k("Arm" + side, 54)
    c.commit(["ArmL", "ArmR"])
    for side, s in SIDES:
        c.k("Hand" + side, 0)
        c.k("Hand" + side, 7, c.orient_hand(side, 7, Vector((s * 0.62, -0.32, -0.72)), Vector((s * 0.3, -1, 0.4))),
            None, "EXPO", "EASE_IN")
        c.k("Hand" + side, 12, (-6, 0, 0))
        c.k("Hand" + side, 42, (-8, 0, 0))
        c.k("Hand" + side, 54)
    return c.finish()


def clip_shriek(arm):
    """The Copy's reveal: freeze, snap into a too-far head tilt with arms flung out and a
    buzzing tremble, then a jerk into a forward lunge (ends ready for ChaseRun)."""
    c = Clip(arm, "Shriek", 50, loop=False, fps=30)
    trem = [0, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1]
    for side, s in SIDES:
        for f, rot in ((0, (0, 0, 0)), (4, (0, 0, 0)), (6, (0, 0, 0)), (30, (0, 0, 0)), (32, (0, 0, 0)),
                       (50, (0, 0, 0))):
            c.k("Leg" + side, f, rot, None, "EXPO" if f == 4 else "LINEAR", "EASE_IN")
    hz = {0: 0, 4: 0, 6: 0, 30: 0, 32: 0, 50: 0}
    for f, z in hz.items():
        c.k("Hips", f, (0, 0, 0), (0, 0, z), "EXPO" if f == 4 else "LINEAR", "EASE_IN")
    c.k("Torso", 0)
    c.k("Torso", 4, (0, 0, 0), None, "EXPO", "EASE_IN")
    c.k("Head", 0)
    c.k("Head", 4, (0, 8, 0), None, "EXPO", "EASE_IN")
    for i, f in enumerate(range(6, 31, 2)):
        tt = trem[i % len(trem)]
        c.k("Torso", f, (-14 + 1.5 * tt, -6 + tt, 0), None, "LINEAR")
        c.k("Head", f, (-28 + 3 * tt, 52 - 4 * tt, 2 * tt), None, "CONSTANT" if f == 30 else "LINEAR")
    c.k("Torso", 30, (-14, -6, 0), None, "CONSTANT")
    c.k("Torso", 32, (10, 4, 6), None, "QUAD", "EASE_OUT")
    c.k("Head", 32, (12, -38, 22), None, "QUAD", "EASE_OUT")
    c.k("Torso", 40, (22, 3, 0))
    c.k("Head", 40, (-18, -30, 0))
    c.k("Torso", 50, (20, 4, 2))
    c.k("Head", 50, (-20, -34, 4))
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    outd = {"L": Vector((0.93, -0.1, 0.36)), "R": Vector((-0.9, -0.16, 0.4))}
    fwd1 = {"L": Vector((0.35, -0.85, 0.3)), "R": Vector((-0.3, -0.85, 0.36))}
    fwd2 = {"L": Vector((0.3, -0.95, 0.1)), "R": Vector((-0.3, -0.95, 0.16))}
    for side, s in SIDES:
        c.k("Arm" + side, 0)
        c.k("Arm" + side, 4, (0, 0, 0), None, "EXPO", "EASE_IN")
        for i, f in enumerate(range(6, 31, 2)):
            tt = trem[(i + 1) % len(trem)] * s
            d = outd[side] + Vector((0, 0.05 * tt, 0.06 * tt))
            c.k("Arm" + side, f, c.aim_arm(side, f, direction=d), None, "CONSTANT" if f == 30 else "LINEAR")
        c.k("Arm" + side, 32, c.aim_arm(side, 32, direction=fwd1[side]), None, "QUAD", "EASE_OUT")
        c.k("Arm" + side, 40, c.aim_arm(side, 40, direction=fwd2[side]))
        c.k("Arm" + side, 50, c.aim_arm(side, 50, direction=fwd2[side] + Vector((0, 0, 0.08))))
    c.commit(["ArmL", "ArmR"])
    for side, s in SIDES:
        c.k("Hand" + side, 0)
        c.k("Hand" + side, 4, (0, 0, 0), None, "EXPO", "EASE_IN")
        for i, f in enumerate(range(6, 31, 2)):
            tt = trem[i % len(trem)]
            c.k("Hand" + side, f, (-35 + 8 * tt, s * 20, -s * 25 + 6 * tt), None,
                "CONSTANT" if f == 30 else "LINEAR")
        c.k("Hand" + side, 32, (-40, s * 10, 0), None, "QUAD", "EASE_OUT")
        c.k("Hand" + side, 40, (-45, s * 6, 0))
        c.k("Hand" + side, 50, (-42, s * 8, 0))
    return c.finish()


SIT_LEG = -84.0


def _seat_hips(c, frames, rot_hips=(0, 0, 0)):
    """Key Hips/legs into the seated pose and drop the pelvis so it rests at SEAT_H."""
    for f in frames:
        c.k("Hips", f, rot_hips, (0, 0, 0))
        for side, s in SIDES:
            c.k("Leg" + side, f, (SIT_LEG, -s * 5, s * 7))
    c.commit(["Hips", "LegL", "LegR"])
    pts = rest_points(c.arm, ("Hips", "LegL", "LegR"))
    c.pose_at(frames[0])
    zs = []
    for b, P in pts.items():
        Q = posed(c.arm, b, P)
        near = Q[Q[:, 1] > -0.85]          # what actually rests on the cushion
        zs.append(near[:, 2].min())
    dz = SEAT_H - min(zs)
    for f in frames:
        ns.key(c.arm, "Hips", f, rot=rot_hips, loc=(0, 0, dz))
        c.keys["Hips"][f] = (rot_hips, (0, 0, dz), "SINE", "EASE_IN_OUT")
    return dz


def clip_sit(arm):
    c = Clip(arm, "Sit", 120, loop=True, fps=30)
    dz = _seat_hips(c, [0, 60, 120])
    for f, p, r in ((0, -6, 0), (30, -7.5, 0.6), (60, -6, 0.8), (90, -7.5, -0.4), (120, -6, 0)):
        c.k("Torso", f, (p, r, 0))
    for f, rot in ((0, (2, 0, 0)), (24, (0, 0, 14)), (48, (1, 0, 10)), (62, (6, 3, 0)), (84, (2, 0, -12)),
                   (104, (0, 0, -3)), (120, (2, 0, 0))):
        c.k("Head", f, rot)
    c.commit(["Torso", "Head"])
    for side, s in SIDES:
        for f in (0, 30, 60, 90, 120):
            tgt = Vector((s * 0.43, -0.6, SEAT_H + 0.86 + (0.015 if f in (30, 90) else 0)))
            c.k("Arm" + side, f, c.aim_arm(side, f, point=tgt))
    c.commit(["ArmL", "ArmR"])
    for side, s in SIDES:
        for f in (0, 30, 60, 90, 120):
            c.k("Hand" + side, f, c.orient_hand(side, f, Vector((s * 0.12, -1, -0.32)), Vector((s * 0.15, 0, -1))))
    c.info = {"hipsDrop": dz}
    return c.finish()


def clip_eat(arm):
    c = Clip(arm, "Eat", 90, loop=True, fps=30)
    dz = _seat_hips(c, [0, 45, 90])
    torso = {0: (7, 0, 0), 16: (8, 0, 0), 22: (11, 0, 0), 28: (8, 0, 0), 40: (7, 0, 0), 90: (7, 0, 0)}
    head = {0: (4, 0, 0), 16: (8, 0, 0), 22: (17, 0, 0), 28: (6, 0, 0), 40: (2, 2, 0), 46: (5, 2, 0),
            52: (1, 2, 0), 58: (5, 1, 0), 64: (1, 0, 0), 70: (5, 0, 0), 76: (2, 0, 0), 90: (4, 0, 0)}
    for f, r in torso.items():
        c.k("Torso", f, r)
    for f, r in head.items():
        c.k("Head", f, r)
    c.commit(["Torso", "Head"])
    z0 = SEAT_H - 1.6
    hands = {0: (0.37, -1.08, 3.2), 16: (0.31, -1.3, 3.66), 22: (0.31, -1.28, 3.62), 28: (0.31, -1.26, 3.6),
             40: (0.36, -1.08, 3.22), 90: (0.37, -1.08, 3.2)}
    for side, s in SIDES:
        for f, (x, y, z) in hands.items():
            c.k("Arm" + side, f, c.aim_arm(side, f, point=Vector((s * x, y, z + dz + z0))))
    c.commit(["ArmL", "ArmR"])
    for side, s in SIDES:
        for f in hands:
            c.k("Hand" + side, f, c.orient_hand(side, f, Vector((-s * 0.3, -0.9, 0.3)), Vector((-s, 0.1, 0))))
    c.info = {"hipsDrop": dz}
    return c.finish()


EATSTAND_BITE = 30          # frame of the big bite (30 fps -> 1.0 s); exported as meta.events.EatStand.bite


def clip_eat_stand(arm):
    """The Copy eats its sandwich standing at the counter: both hands bring it up, one big
    bite at 1.0 s, chew with small head bobs, then settle back to Idle's first pose so it
    crossfades cleanly. Feet stay planted (Hips/legs at rest)."""
    c = Clip(arm, "EatStand", 66, loop=False, fps=30)
    _static(c, ["Hips", "LegL", "LegR"])
    B = EATSTAND_BITE
    torso = {0: (0, 0, 0), 12: (3, 0, 0), 24: (5, 0, 0), B: (9, 0, 0), B + 6: (5, 0, 0), 52: (3, 0, 0),
             58: (1, 0, 0), 66: (0, 0, 0)}
    head = {0: (0, 0, 0), 12: (9, 0, 0), 24: (7, 0, 0), B: (17, 0, 0), B + 6: (4, 0, 0), 40: (7, 1.5, 0),
            44: (2, 1.5, 0), 48: (7, -1, 0), 52: (2, -1, 0), 58: (2, 0, 0), 66: (0, 0, 0)}
    for f, r in torso.items():
        c.k("Torso", f, r, None, "QUAD" if f == B else "SINE", "EASE_IN" if f == B else "EASE_IN_OUT")
    for f, r in head.items():
        c.k("Head", f, r, None, "QUAD" if f == B else "SINE", "EASE_IN" if f == B else "EASE_IN_OUT")
    c.commit(["Hips", "LegL", "LegR", "Torso", "Head"])
    hands = {12: (0.37, -1.0, 3.12), 24: (0.31, -1.3, 3.66), B: (0.31, -1.27, 3.6), B + 6: (0.33, -1.22, 3.5),
             44: (0.36, -1.05, 3.2), 52: (0.37, -1.02, 3.16)}
    for side, s in SIDES:
        c.k("Arm" + side, 0)
        for f, (x, y, z) in hands.items():
            c.k("Arm" + side, f, c.aim_arm(side, f, point=Vector((s * x, y, z))))
        c.k("Arm" + side, 66)
    c.commit(["ArmL", "ArmR"])
    for side, s in SIDES:
        c.k("Hand" + side, 0, (-4, 0, 0))                      # = Idle frame 0
        for f in hands:
            c.k("Hand" + side, f, c.orient_hand(side, f, Vector((-s * 0.3, -0.9, 0.3)), Vector((-s, 0.1, 0))))
        c.k("Hand" + side, 66, (-4, 0, 0))
    return c.finish()


def build_actions(arm):
    """Author all nine clips on `arm` (parts must already be bound). Returns [actions]."""
    feet = rest_points(arm, ("LegL", "LegR"), ("Shoe", "Sole"))
    acts = [clip_idle(arm), clip_walk(arm, feet), clip_wave(arm), clip_happy(arm), clip_upset(arm),
            clip_sit(arm), clip_eat(arm), clip_eat_stand(arm), clip_shriek(arm), clip_chase(arm, feet)]
    arm.animation_data.action = None          # leave the rig in its true rest pose (preview/FBX)
    for pb in arm.pose.bones:
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
    return acts


# ---- pose strips -------------------------------------------------------------------------

def booth_proxy():
    """Untagged stand-ins matching Shop_Booth around a Seat socket (sitter at the origin,
    facing -Y): cushion top 1.6, front edge 0.9 ahead, backrest 0.64 behind, table edge
    1.1 ahead with its top at 2.8."""
    def mk(size, loc, col, bev):
        o = ns.box(size, loc=loc, bevel=bev, name="Proxy")
        o.data.materials.append(ns.material(col))
        return o
    return [mk((2.2, 1.87, 0.4), (0, 0.035, SEAT_H - 0.2), "#B23A3A", 0.12),
            mk((2.1, 1.75, SEAT_H - 0.4), (0, 0.1, (SEAT_H - 0.4) / 2), "#2E7F86", 0.04),
            mk((2.2, 0.46, 2.9), (0, 0.87, SEAT_H + 1.45), "#B23A3A", 0.14),
            mk((2.4, 2.5, 0.12), (0, -2.35, 2.74), "#D9D2C3", 0.03)]


def pose_strip(arm, act, frames, name, speed=0.0, views=(-60, 90), props=(), res=300, samples=12,
               out_dir=PREV):
    """Render the rig at several frames (rows = camera yaws). Locomotion clips are rendered
    with root motion at `speed` over a 0.5-stud floor grid, camera fixed, so a planted foot
    must stay on the same grid line from tile to tile."""
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and len(act.slots):
        arm.animation_data.action_slot = act.slots[0]
    fps = act.get("ns_fps", 30)
    objs = ns._tagged_objects()
    lo, hi = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for f in frames:
        bpy.context.scene.frame_set(f)
        arm.location.y = -speed * f / fps
        bpy.context.view_layer.update()
        a, b = ns.bbox_world(objs + list(props))
        lo = Vector(map(min, lo, a))
        hi = Vector(map(max, hi, b))
    lo.z = min(lo.z, 0.0)
    extra = []
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -0.002))
    fl = bpy.context.active_object
    fl.name = "Floor"
    fl.data.materials.append(ns.material("#3A3B42"))
    extra.append(fl)
    if speed > 0:
        y = lo.y - 1.0
        while y < hi.y + 1.0:
            ln = ns.box((3.0, 0.03 if abs(y - round(y)) > 0.01 else 0.05, 0.004), loc=(0, y, 0.0), bevel=0, name="GridLine")
            ln.data.materials.append(ns.material("#8C8F99" if abs(y - round(y)) > 0.01 else "#D9DCE4"))
            extra.append(ln)
            y += 0.5
    ns._setup_render(res, samples)
    rows = []
    for yaw in views:
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cam, ctr, dist = ns._camera_fit(lo, hi, yaw, 12, fov_deg=30, margin=1.02)
        k = math.radians(yaw)
        ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * dist, 60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3)) * dist, 22 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        tiles = []
        for f in frames:
            bpy.context.scene.frame_set(f)
            arm.location.y = -speed * f / fps
            p = os.path.join(out_dir, f"_tmp_{name}_{yaw}_{f}.png")
            bpy.context.scene.render.filepath = p
            bpy.ops.render.render(write_still=True)
            tiles.append(p)
        rows.append(tiles)
    arm.location.y = 0
    for o in list(bpy.context.scene.objects):
        if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")) or o in extra:
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.context.scene.frame_set(0)
    W, H = res * len(frames), res * len(rows) + 30
    sheet = Image.new("RGB", (W, H), (24, 26, 30))
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 8), f"{act.name}  len {(act['ns_end'] - act['ns_start']) / fps:.2f}s  loop={bool(act['ns_loop'])}"
            + (f"  root motion {speed} studs/s" if speed else ""), fill=(235, 235, 235))
    for r, tiles in enumerate(rows):
        for i, p in enumerate(tiles):
            im = Image.open(p).convert("RGB")
            sheet.paste(im, (i * res, 30 + r * res))
            dr.text((i * res + 6, 30 + r * res + 4), f"f{frames[i]} ({frames[i] / fps:.2f}s)", fill=(255, 255, 255))
            os.remove(p)
    out = os.path.join(out_dir, f"Human_{name}_strip.png")
    sheet.save(out)
    return out


# --------------------------------------------------------------------------------------
# ACCESSORIES — modelled in body space on the real head/torso, exported pivot = socket
# --------------------------------------------------------------------------------------
# A builder returns a list of part specs: dict(name, objs, color, mat, role, smooth,
# transparency, shadow). place_accessory() turns them into tagged parts (optionally bound
# to a rig bone); run_accessory() exports one as a standalone asset.

def spec(name, objs, color, mat="SmoothPlastic", role=None, smooth=60.0, transparency=0.0, shadow=True):
    return {"name": name, "objs": [o for o in objs if o is not None], "color": color, "mat": mat,
            "role": role, "smooth": smooth, "transparency": transparency, "shadow": shadow}


_HEAD_BVH = None


def head_bvh():
    """BVH of the base head (built once from the same generator, then discarded)."""
    global _HEAD_BVH
    if _HEAD_BVH is None:
        objs = head_mesh()
        o = ns.join_applied(objs, "HeadProbe")
        _HEAD_BVH = bvh_of([o])
        bpy.data.objects.remove(o, do_unlink=True)
    return _HEAD_BVH


def reset_caches():
    global _HEAD_BVH
    _HEAD_BVH = None


D2R = math.pi / 180.0


def hairline(phi, front=50.0, side=85.0, back=115.0, ear_notch=11.0):
    """Hairline polar angle (radians) around the head; phi radians (0 = front)."""
    A1 = (front - back) / 2.0
    A0A2 = (front + back) / 2.0          # A0 + A2
    A0 = (A0A2 + side) / 2.0
    A2 = A0A2 - A0
    d = A0 + A1 * math.cos(phi) + A2 * math.cos(2 * phi)
    pw = (phi + math.pi) % (2 * math.pi) - math.pi
    for sgn in (1, -1):
        d -= ear_notch * math.exp(-((pw - sgn * math.pi / 2) / 0.32) ** 2)
    return d * D2R


def tri_wave(x):
    """Triangle wave in [0, 1] with period 1."""
    x = x % 1.0
    return 1 - abs(2 * x - 1)


def hair_cap(edge, thick, infl=0.012, nu=40, vs=None, disp=None, name="HairCap"):
    """Thick hair shell from the crown to the hairline `edge(phi)` (radians).
    thick(phi, v) and disp(phi, v) add outward volume (v 0 = crown, 1 = hairline)."""
    vs = vs or [0.12, 0.28, 0.45, 0.6, 0.73, 0.84, 0.93, 1.0]

    def fo(u, v):
        phi = 2 * math.pi * u
        return head_pt(phi, v * edge(phi), infl + thick(phi, v) + (disp(phi, v) if disp else 0.0))

    def fi(u, v):
        phi = 2 * math.pi * u
        return head_pt(phi, v * edge(phi), infl)

    return patch(fo, fi, nu, len(vs), closed_u=True, pole=True, inner="lip", centre=HEAD_C, vs=vs, name=name)


def tuft_field(n, seed, h=(0.04, 0.09), w=(0.25, 0.45), psi_max=1.6, sharp=1.0):
    rnd = random.Random(seed)
    tufts = []
    for _ in range(n):
        phi = rnd.uniform(-math.pi, math.pi)
        psi = math.acos(rnd.uniform(math.cos(psi_max), 1.0))
        tufts.append((head_dir(phi, psi), rnd.uniform(*h), rnd.uniform(*w)))

    def f(phi, psi):
        d = head_dir(phi, psi)
        tot = 0.0
        for td, th, tw in tufts:
            ang = math.acos(max(-1.0, min(1.0, d.dot(td))))
            tot += th * math.exp(-(ang / tw) ** (2 if sharp == 1.0 else sharp))
        return tot
    return f


def curtain(phi0, phi1, top_psi, z_bot, thick=0.06, bulge=0.05, out=0.03, nu=16, nv=6, jag=0.0,
            name="Curtain"):
    """Hanging hair sheet (open in phi) from the head surface down to z_bot(phi)."""
    def base(phi, v, extra):
        t = head_pt(phi, top_psi, 0.02 + extra)
        r = Vector((t.x - HEAD_C.x, t.y - HEAD_C.y, 0.0))
        rl = r.length or 1.0
        rn = r / rl
        zb = z_bot(phi) - jag * tri_wave(5.0 * (phi - phi0) / (phi1 - phi0))
        b = Vector((t.x + rn.x * out, t.y + rn.y * out, zb))
        p = t.lerp(b, v)
        p += rn * (bulge * math.sin(math.pi * min(1.0, v * 1.3)) + extra * 0.0)
        return p, rn

    def fo(u, v):
        phi = phi0 + (phi1 - phi0) * u
        p, rn = base(phi, v, 0.0)
        return p + rn * thick * (1.0 - 0.45 * v)

    def fi(u, v):
        phi = phi0 + (phi1 - phi0) * u
        p, rn = base(phi, v, 0.0)
        return p

    return patch(fo, fi, nu, nv, closed_u=False, pole=False, inner="full", name=name)


# ---------------- hair ----------------------------------------------------------------

def acc_hair_short(color=HAIR["brown"]):
    edge = lambda phi: hairline(phi) + 4 * D2R * tri_wave(phi / (16 * D2R)) * math.exp(-(phi / 0.9) ** 2 if abs(phi) < math.pi else 0)
    def edge2(phi):
        pw = (phi + math.pi) % (2 * math.pi) - math.pi
        j = 5 * D2R * tri_wave(pw / (15 * D2R) + 0.5) * math.exp(-(pw / 0.85) ** 2)
        return hairline(phi) + j
    crown = tuft_field(1, 3, h=(0.02, 0.02), w=(0.7, 0.7), psi_max=0.3)
    quiff = lambda phi, psi: 0.03 * _gauss(((phi + math.pi) % (2 * math.pi) - math.pi), psi - 0.55, 0.6, 0.35)
    thick = lambda phi, v: 0.062 * (1 - 0.45 * smoothstep(0.7, 1.0, v))
    disp = lambda phi, v: crown(phi, v * edge2(phi)) * (1 - v) + quiff(phi, v * edge2(phi))
    cap = hair_cap(edge2, thick, nu=44, disp=disp, name="Hair")
    return [spec("Hair", [cap], color, role="hair", smooth=55)]


def acc_hair_messy(color=HAIR["dark"]):
    tf = tuft_field(16, 11, h=(0.05, 0.13), w=(0.18, 0.32), psi_max=1.75, sharp=1.3)

    def edge(phi):
        pw = (phi + math.pi) % (2 * math.pi) - math.pi
        return hairline(phi, front=54, side=88, back=112) + 9 * D2R * tri_wave(pw / (22 * D2R))
    thick = lambda phi, v: 0.085 * (1 - 0.5 * smoothstep(0.75, 1.0, v))
    disp = lambda phi, v: tf(phi, v * edge(phi)) * (1 - 0.6 * v)
    cap = hair_cap(edge, thick, nu=48, vs=[0.1, 0.22, 0.36, 0.5, 0.63, 0.75, 0.86, 0.94, 1.0], disp=disp,
                   name="Hair")
    return [spec("Hair", [cap], color, role="hair", smooth=45)]


def acc_hair_mullet(color=HAIR["auburn"]):
    def edge(phi):
        pw = (phi + math.pi) % (2 * math.pi) - math.pi
        return hairline(phi, front=52, side=84, back=108) + 4 * D2R * tri_wave(pw / (14 * D2R)) * math.exp(-(pw / 0.8) ** 2)
    thick = lambda phi, v: 0.07 * (1 - 0.4 * smoothstep(0.75, 1.0, v))
    cap = hair_cap(edge, thick, nu=40, name="Hair")
    back = curtain(132 * D2R, 228 * D2R, 98 * D2R, lambda phi: 3.74 + 0.05 * math.cos(phi - math.pi),
                   thick=0.075, bulge=0.035, out=0.02, nu=18, nv=6, jag=0.09, name="Mullet")
    return [spec("Hair", [cap, back], color, role="hair", smooth=50)]


def _sphere_on_head(phi, psi, off, r, scale=(1, 1, 1), segs=10, rings=6):
    c = head_pt(phi, psi, off)
    return ns.sphere(r, loc=tuple(c), scale=scale, segs=segs, rings=rings)


def acc_hair_bun(color=HAIR["black"], tie="#3B3F59"):
    edge = lambda phi: hairline(phi, front=48, side=84, back=114)
    thick = lambda phi, v: 0.05 * (1 - 0.3 * smoothstep(0.8, 1.0, v))
    cap = hair_cap(edge, thick, nu=34, vs=[0.15, 0.35, 0.55, 0.72, 0.86, 0.95, 1.0], name="Hair")
    bun = _sphere_on_head(math.pi, 42 * D2R, 0.2, 0.255, scale=(1.0, 0.95, 0.9), segs=12, rings=8)
    swirl = ns.torus(0.17, 0.07, loc=tuple(head_pt(math.pi, 40 * D2R, 0.33)), rot=(-48, 0, 0),
                     major_segs=12, minor_segs=5)
    band = ns.torus(0.2, 0.045, loc=tuple(head_pt(math.pi, 44 * D2R, 0.07)), rot=(-48, 0, 0),
                    major_segs=12, minor_segs=4)
    return [spec("Hair", [cap, bun, swirl], color, role="hair", smooth=55),
            spec("Tie", [band], tie, smooth=60)]


def acc_hair_ponytail(color=HAIR["brown"], tie="#C2405A", high=False):
    edge = lambda phi: hairline(phi, front=49, side=84, back=112)
    thick = lambda phi, v: 0.05 * (1 - 0.3 * smoothstep(0.8, 1.0, v))
    cap = hair_cap(edge, thick, nu=34, vs=[0.15, 0.35, 0.55, 0.72, 0.86, 0.95, 1.0], name="Hair")
    tpsi = (58 if high else 80) * D2R
    t0 = head_pt(math.pi, tpsi, 0.06)
    if high:
        pts = [t0, t0 + Vector((0, 0.2, 0.12)), t0 + Vector((0, 0.42, -0.08)), t0 + Vector((0, 0.5, -0.45)),
               t0 + Vector((0, 0.44, -0.8))]
        radii = [0.12, 0.155, 0.16, 0.12, 0.035]
    else:
        pts = [t0, t0 + Vector((0, 0.18, -0.06)), t0 + Vector((0, 0.26, -0.32)), t0 + Vector((0, 0.22, -0.62)),
               t0 + Vector((0, 0.16, -0.84))]
        radii = [0.12, 0.15, 0.145, 0.1, 0.03]
    tail = tube(pts, radii, sides=8, res=3, name="Tail")
    band = ns.torus(0.11, 0.045, loc=tuple(t0 + (pts[1] - t0) * 0.35), major_segs=12, minor_segs=5)
    d = (pts[1] - t0).normalized()
    band.rotation_euler = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    return [spec("Hair", [cap, tail], color, role="hair", smooth=55),
            spec("Tie", [band], tie, smooth=60)]


def acc_hair_curly(color=HAIR["black"]):
    """Tight curly volume: a thick cap studded with small curls."""
    edge = lambda phi: hairline(phi, front=56, side=86, back=110)
    thick = lambda phi, v: 0.13 * (1 - 0.35 * smoothstep(0.75, 1.0, v))
    cap = hair_cap(edge, thick, nu=24, vs=[0.2, 0.45, 0.7, 0.88, 1.0], name="Hair")
    rnd = random.Random(7)
    curls = []
    n = 24
    for i in range(n):                       # golden-angle spread over the cap
        ph = (i * 137.5) % 360 - 180
        f = (i + 0.5) / n
        e = hairline(ph * D2R, front=56, side=86, back=110) / D2R
        ps = (e - 7) * math.sqrt(f)
        r = rnd.uniform(0.095, 0.125)
        curls.append(_sphere_on_head(ph * D2R, ps * D2R, 0.105 + r * 0.3, r, segs=6, rings=4))
    return [spec("Hair", [cap] + curls, color, role="hair", smooth=70)]


def acc_hair_long(color=HAIR["blonde"]):
    def edge(phi):
        pw = (phi + math.pi) % (2 * math.pi) - math.pi
        # side-swept fringe: hairline drops lower on the character's right (-X)
        sweep = 9 * D2R * math.exp(-((pw + 0.35) / 0.55) ** 2)
        return hairline(phi, front=50, side=90, back=100, ear_notch=0.0) + sweep
    thick = lambda phi, v: 0.075 * (1 - 0.35 * smoothstep(0.8, 1.0, v))
    cap = hair_cap(edge, thick, nu=34, vs=[0.15, 0.35, 0.55, 0.72, 0.86, 0.95, 1.0], name="Hair")
    zb = lambda phi: 3.66 + 0.1 * max(0.0, math.cos(phi - math.pi) * -1 + 0.2)
    sheet = curtain(62 * D2R, 298 * D2R, 92 * D2R, zb, thick=0.08, bulge=0.06, out=0.1, nu=22, nv=5, jag=0.06,
                    name="Long")
    return [spec("Hair", [cap, sheet], color, role="hair", smooth=50)]


# ---------------- hats -----------------------------------------------------------------

def _band_psi(phi, front, side, back):
    A1 = (front - back) / 2.0
    A0 = ((front + back) / 2.0 + side) / 2.0
    A2 = (front + back) / 2.0 - A0
    return (A0 + A1 * math.cos(phi) + A2 * math.cos(2 * phi)) * D2R


def acc_hat_trucker(color="#2F4A7A", mesh="#EDEBE4", patch_col=MUSTARD, backwards=False, single=None):
    infl = 0.11
    # worn backwards the strap side faces the forehead, so it must sit high (hairline)
    bf, bs, bb = (66, 76, 60) if backwards else (62, 79, 94)
    band = lambda phi: _band_psi(phi, bf, bs, bb)
    front_bulge = lambda phi, v: 0.08 * math.exp(-(((phi + math.pi) % (2 * math.pi) - math.pi) / 0.95) ** 2) \
        * math.sin(math.pi * min(1.0, v * 1.15)) ** 0.7

    def mk(phi0, phi1, nu, name):
        def fo(u, v):
            phi = phi0 + (phi1 - phi0) * u
            return head_pt(phi, max(v, 0.04) * band(phi), infl + 0.05 + front_bulge(phi, v))

        def fi(u, v):
            phi = phi0 + (phi1 - phi0) * u
            return head_pt(phi, max(v, 0.04) * band(phi), infl)
        return patch(fo, fi, nu, 6, closed_u=False, pole=False, inner="lip", centre=HEAD_C,
                     vs=[0.0, 0.25, 0.5, 0.72, 0.9, 1.0], name=name)
    fr = mk(-72 * D2R, 72 * D2R, 12, "CapFront")
    bk = mk(72 * D2R, 288 * D2R, 13, "CapBack")
    top = head_pt(0, 0, infl + 0.05)
    button = ns.sphere(0.05, loc=(top.x, top.y, top.z + 0.012), scale=(1, 1, 0.55), segs=8, rings=4)
    # brim: D-shaped slab from the front band, curved down at the sides
    def brim_pt(u, v, off):
        phi = (-54 + 108 * u) * D2R
        b = head_pt(phi, band(phi), infl + 0.03)
        r = Vector((b.x - HEAD_C.x, b.y - HEAD_C.y, 0)).normalized()
        r = (r + Vector((0, -0.6, 0))).normalized()          # bill points forward, not splayed
        k = 2 * u - 1
        L = 0.05 + 0.55 * math.sqrt(max(0.0, 1 - k * k)) ** 0.8
        p = b + r * (L * v) + Vector((0, 0, -0.08 * v - 0.16 * k * k * v + off))
        return p
    brim = patch(lambda u, v: brim_pt(u, v, 0.0), lambda u, v: brim_pt(u, v, -0.04), 13, 4, closed_u=False,
                 pole=False, inner="full", name="Brim")
    # snapback opening at the back: strap + raised arch (same part, it's what faces you when reversed)
    arch = [head_pt(a * D2R, band(a * D2R) - (0.3 * math.sin(math.pi * (a - 156) / 48)), infl + 0.06)
            for a in range(156, 205, 6)]
    strap = [head_pt(a * D2R, band(a * D2R) - 0.04, infl + 0.065) for a in range(150, 211, 10)]
    snap = [tube(arch, [0.026] * len(arch), sides=6, res=2), tube(strap, [0.03] * len(strap), sides=6, res=2)]
    pc = head_pt(0, 0.62 * band(0), infl + 0.05 + front_bulge(0, 0.62))
    pt = rbox((0.3, 0.03, 0.17), loc=(pc.x, pc.y + 0.004, pc.z), rot=(-28, 0, 0), bevel=0.02, seg=1)
    if backwards:
        R = Matrix.Translation(SOCKETS["HatSocket"]) @ Matrix.Rotation(math.pi, 4, "Z") @ \
            Matrix.Translation(-SOCKETS["HatSocket"])
        for o in [fr, bk, button, brim, pt] + snap:
            ns.apply_all(o)
            xform(o, R)
    if single:
        return [spec(single[0], [fr, bk, button, brim, pt] + snap, single[1], role=single[2], smooth=50)]
    return [spec("Crown", [fr, button, brim], color, role="hat", smooth=50),
            spec("Mesh", [bk] + snap, mesh, "Fabric", smooth=50),
            spec("Patch", [pt], patch_col, smooth=40)]


def acc_hat_beanie(color="#C8523A", tag="#6B4430"):
    """Snug cuffed knit beanie: soft slightly-peaked crown, ribbed fold-up cuff."""
    band = lambda phi: _band_psi(phi, 67, 80, 96)
    infl = 0.1

    def fo(u, v):
        phi = 2 * math.pi * u
        p = head_pt(phi, v * band(phi), infl + 0.05)
        return p + Vector((0, 0, 0.035 * (1 - v) ** 1.5))

    def fi(u, v):
        phi = 2 * math.pi * u
        return head_pt(phi, v * band(phi), infl)
    crown = patch(fo, fi, 30, 6, closed_u=True, pole=True, inner="lip", centre=HEAD_C,
                  vs=[0.18, 0.4, 0.6, 0.78, 0.92, 1.0], name="Crown")
    nu = 40

    def co(u, v):
        phi = 2 * math.pi * u
        rib = 0.014 if (round(u * nu) % 2 == 0) else 0.0
        return head_pt(phi, band(phi) - (21 - 21 * v) * D2R, infl + 0.09 + rib)

    def ci(u, v):
        phi = 2 * math.pi * u
        return head_pt(phi, band(phi) - (21 - 21 * v) * D2R, infl + 0.005)
    cuff = patch(co, ci, nu, 3, closed_u=True, pole=False, inner="full", name="Cuff")
    tp = head_pt(-0.55, band(-0.55) - 9 * D2R, infl + 0.095)
    tg = rbox((0.13, 0.025, 0.1), loc=tuple(tp), rot=(0, 0, -0.55 / D2R), bevel=0.01, seg=1)
    return [spec("Beanie", [crown, cuff], color, "Fabric", role="hat", smooth=55),
            spec("Tag", [tg], tag, smooth=40)]


def acc_hat_cop(navy="#1F2A44", black="#141518", gold=GOLD):
    infl = 0.1
    band = lambda phi: _band_psi(phi, 64, 76, 86)
    top_z = lambda phi: HEAD_TOP + 0.2 + 0.07 * math.cos(phi)       # crown tilts up at the front
    nb = 0.22                                                       # band height (along psi)

    def ring_pt(phi, frac, off):
        # frac 0 = band bottom ... 1 = top rim; the crown flares out above the band
        b0 = head_pt(phi, band(phi), infl + off)
        if frac <= 0.4:
            return head_pt(phi, band(phi) - (frac / 0.4) * nb, infl + off)
        b1 = head_pt(phi, band(phi) - nb, infl + off)
        r = Vector((b1.x - HEAD_C.x, b1.y - HEAD_C.y, 0)).normalized()
        u = (frac - 0.4) / 0.6
        flare = 0.2 * math.sin(math.pi * 0.5 * u) ** 0.8
        z = b1.z + (top_z(phi) - b1.z) * u
        return Vector((b1.x + r.x * (flare + off * 0.0), b1.y + r.y * flare, z))

    def fo(u, v):
        phi = 2 * math.pi * u
        if v <= 0.35:     # flat top disc (v 0 = centre)
            rim = ring_pt(phi, 1.0, 0.05)
            c = Vector((0, HEAD_C.y + 0.02, top_z(0) * 0 + (top_z(phi) + HEAD_TOP + 0.24) / 2))
            t = v / 0.35
            p = c.lerp(rim, t)
            p.z = top_z(phi) + 0.035 * (1 - t * t)
            return p
        return ring_pt(phi, 1.0 - (v - 0.35) / 0.65, 0.05)

    def fi(u, v):
        p = fo(u, v)
        return p
    vs = [0.15, 0.35, 0.47, 0.62, 0.78, 0.9, 1.0]
    crown_o = patch(fo, lambda u, v: _inset(fo, u, v), 26, len(vs), closed_u=True, pole=True, inner="lip",
                    centre=Vector((0, HEAD_C.y, HEAD_TOP)), vs=vs, name="Crown")
    # black band over the lower crown + visor
    def bo(u, v):
        phi = 2 * math.pi * u
        return head_pt(phi, band(phi) - v * (nb * 0.9), infl + 0.075)

    def bi(u, v):
        phi = 2 * math.pi * u
        return head_pt(phi, band(phi) - v * (nb * 0.9), infl + 0.035)
    bandm = patch(bo, bi, 26, 2, closed_u=True, pole=False, inner="full", name="Band")

    def vis(u, v, off):
        phi = (-62 + 124 * u) * D2R
        b = head_pt(phi, band(phi), infl + 0.06)
        r = Vector((b.x - HEAD_C.x, b.y - HEAD_C.y, 0)).normalized()
        k = 2 * u - 1
        L = 0.04 + 0.36 * math.sqrt(max(0.0, 1 - k * k))
        return b + r * (L * v) + Vector((0, 0, -0.2 * v - 0.05 * k * k * v + off))
    visor = patch(lambda u, v: vis(u, v, 0.0), lambda u, v: vis(u, v, -0.03), 12, 4, closed_u=False, pole=False,
                  inner="full", name="Visor")
    bp = ring_pt(0.0, 0.62, 0.075)
    badge = _shield(0.17, 0.2, 0.03)
    badge.location = bp
    badge.rotation_euler = (math.radians(-18), 0, 0)
    cord = tube([head_pt(-58 * D2R, band(-58 * D2R) - 0.02, infl + 0.09), head_pt(0, band(0) - 0.035, infl + 0.095),
                 head_pt(58 * D2R, band(58 * D2R) - 0.02, infl + 0.09)], [0.022, 0.022, 0.022], sides=6, res=6)
    btn = [ns.sphere(0.03, loc=tuple(head_pt(s * 60 * D2R, band(s * 60 * D2R) - 0.02, infl + 0.1)), segs=8, rings=4)
           for s in (1, -1)]
    return [spec("Crown", [crown_o], navy, "Fabric", smooth=55),
            spec("Band", [bandm, visor], black, smooth=45),
            spec("Badge", [badge, cord] + btn, gold, "Metal", smooth=40)]


def _inset(f, u, v, d=0.04):
    """Point offset inward (toward the head centre axis) for simple shells."""
    p = f(u, v)
    c = Vector((0, HEAD_C.y, p.z - 0.6))
    return p - (p - c).normalized() * d


def _shield(w, h, t):
    pts = [(-w / 2, h / 2), (w / 2, h / 2), (w / 2, -h * 0.05), (0, -h / 2), (-w / 2, -h * 0.05)]
    pts = [(x, 0) for x in []] or pts
    o = ns.profile_slab(pts, t, bevel=0.01, segments=1, name="Shield")
    ns.apply_all(o)
    xform(o, Matrix.Rotation(math.pi / 2, 4, "X") @ Matrix.Translation((0, 0, -t / 2)))
    return o


# ---------------- face -----------------------------------------------------------------

def _face_y(x, z, off=0.0):
    hit = head_bvh().ray_cast(Vector((x, -3.0, z)), Vector((0, 1, 0)))
    return (hit[0].y if hit[0] is not None else -0.6) - off


def acc_face_beard(color=HAIR["dark"]):
    def top(phi):
        a = abs(((phi + math.pi) % (2 * math.pi)) - math.pi) / D2R
        return (124 - 44 * smoothstep(28, 96, a)) * D2R

    vs = [0.0, 0.18, 0.38, 0.58, 0.78, 1.0]

    def psi_of(phi, v):
        return top(phi) + (172 * D2R - top(phi)) * v

    def thick(phi, v):
        pw = (phi + math.pi) % (2 * math.pi) - math.pi
        chin = 0.09 * math.exp(-(pw / 0.7) ** 2) * math.sin(math.pi * min(1, v * 1.4)) ** 0.6
        edge = smoothstep(0.0, 0.25, v) * (1 - 0.3 * smoothstep(0.85, 1, v))
        return (0.05 + chin) * (0.35 + 0.65 * edge)
    fo = lambda u, v: head_pt((-104 + 208 * u) * D2R, psi_of((-104 + 208 * u) * D2R, v), 0.012 + thick((-104 + 208 * u) * D2R, v))
    fi = lambda u, v: head_pt((-104 + 208 * u) * D2R, psi_of((-104 + 208 * u) * D2R, v), 0.008)
    b = patch(fo, fi, 28, len(vs), closed_u=False, pole=False, inner="lip", centre=HEAD_C, vs=vs, name="Beard")
    return [spec("Beard", [b], color, role="hair", smooth=55)]


def acc_face_mustache(color=HAIR["dark"], big=False, role="hair", name="Mustache"):
    k = 1.25 if big else 1.0
    pts, radii = [], []
    for s in (-1, 1):
        side = []
        for x, z, r in ((0.0, 4.115, 0.05), (0.09, 4.112, 0.062), (0.17, 4.085, 0.058), (0.235, 4.03, 0.042),
                        (0.27, 3.96 if big else 3.99, 0.022)):
            xx = s * x * k
            zz = 4.11 + (z - 4.11) * k
            side.append((Vector((xx, _face_y(xx, zz) - r * 0.55, zz)), r * k))
        pts.append(side)
    left = tube([p for p, r in pts[1]], [r for p, r in pts[1]], sides=10, res=4)
    right = tube([p for p, r in pts[0]], [r for p, r in pts[0]], sides=10, res=4)
    return [spec(name, [left, right], color, role=role, smooth=60)]


def _loop_tube(points, r, sides=8, name="Loop"):
    """Closed tube along a closed polyline (list of Vector)."""
    bm = bmesh.new()
    n = len(points)
    rings = []
    for i, p in enumerate(points):
        t = (points[(i + 1) % n] - points[i - 1]).normalized()
        a = t.orthogonal().normalized()
        b = t.cross(a).normalized()
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * k / sides) + b * math.sin(2 * math.pi * k / sides)) * r)
                      for k in range(sides)])
    for i in range(n):
        r0, r1 = rings[i], rings[(i + 1) % n]
        # align ring twist: pick the offset that minimises distance
        best = min(range(sides), key=lambda o: (r0[0].co - r1[o].co).length)
        for k in range(sides):
            bm.faces.new((r0[k], r0[(k + 1) % sides], r1[(k + 1 + best) % sides], r1[(k + best) % sides]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def _rim_shape(w, h, rr, n=20, round_=False):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        if round_:
            pts.append((w / 2 * math.cos(a), h / 2 * math.sin(a)))
        else:
            c, s = math.cos(a), math.sin(a)
            pts.append((w / 2 * _sgnpow(c, 2 / 4.0), h / 2 * _sgnpow(s, 2 / 4.0)))
    return pts


def acc_face_glasses(frame="#24211F", lens="#BFE3F2", round_=False, role=None, w=0.34, h=0.25):
    ez, ex = 4.42, 0.235
    parts_f, parts_l = [], []
    inner_pts = {}
    for s in (1, -1):
        cy = _face_y(s * ex, ez) - (0.115 if not round_ else 0.12)
        yaw = -s * 9 * D2R
        M = Matrix.Translation((s * ex, cy, ez)) @ Matrix.Rotation(yaw, 4, "Z")
        shape = _rim_shape(w, h, 0.06, n=16, round_=round_)
        loop = [M @ Vector((x, 0, y)) for x, y in shape]
        parts_f.append(_loop_tube(loop, 0.028 if not round_ else 0.026, sides=5))
        ln = ns.profile_slab([(x * 0.97, y * 0.97) for x, y in shape], 0.016, bevel=0.0, name="Lens")
        ns.apply_all(ln)
        xform(ln, M @ Matrix.Rotation(math.pi / 2, 4, "X") @ Matrix.Translation((0, 0, -0.008)))
        parts_l.append(ln)
        inner_pts[s] = M @ Vector((-s * w / 2, 0, h * 0.12))
        # temple arm back to the ear
        a = M @ Vector((s * w / 2, 0, h * 0.18))
        p1 = Vector((s * 0.6, -0.42, ez + 0.05))
        p1.x = s * (abs(surf_x(head_bvh(), p1.y, p1.z, s)) + 0.035)
        p2 = Vector((s * 0.6, -0.05, ez + 0.06))
        p2.x = s * (abs(surf_x(head_bvh(), p2.y, p2.z, s)) + 0.04)
        p3 = Vector((s * 0.6, 0.12, ez - 0.06))
        p3.x = s * (abs(surf_x(head_bvh(), p3.y, p3.z, s)) + 0.02)
        parts_f.append(tube([a, p1, p2, p3], [0.022, 0.02, 0.02, 0.018], sides=5, res=2))
    br = tube([inner_pts[1], Vector((0, inner_pts[1].y - 0.03, ez + 0.06)), inner_pts[-1]], [0.022, 0.022, 0.022],
              sides=6, res=4)
    parts_f.append(br)
    return [spec("Frame", parts_f, frame, role=role, smooth=60),
            spec("Lens", parts_l, lens, "Glass", role=role, smooth=30, transparency=0.6, shadow=False)]


def acc_face_bags(color="#4E3359"):
    objs = []
    for s in (1, -1):
        pts, radii = [], []
        for k in range(5):
            dx = -0.12 + 0.06 * k
            x = s * (0.225 + dx)
            z = 4.29 + 0.035 * (dx / 0.12) ** 2
            pts.append((x, _face_y(x, z) + 0.006, z))
            radii.append([0.014, 0.03, 0.034, 0.03, 0.014][k])
        objs.append(tube(pts, radii, sides=6, res=2))
        pts2 = []
        for k in range(4):
            dx = -0.08 + 0.055 * k
            x = s * (0.23 + dx)
            z = 4.235 + 0.03 * (dx / 0.09) ** 2
            pts2.append((x, _face_y(x, z) + 0.004, z))
        objs.append(tube(pts2, [0.008, 0.014, 0.014, 0.008], sides=5, res=2))
    return [spec("Bags", objs, color, smooth=70, transparency=0.25, shadow=False)]


# ---------------- tops (torso overlays, weld to Torso at TorsoSocket) -------------------
# Garment rings extend the torso table below the shirt hem (around the pelvis) so jackets,
# robes and overalls can hang over the hips. Skirts flare enough for the walk's leg swing.
GARM_LOW = [(2.02, 0.675, 0.455, 2.4, 0.0), (2.12, 0.67, 0.45, 2.4, 0.0)]
GARMENT = GARM_LOW + TORSO
ROBE = [(1.58, 0.84, 0.74, 2.3, 0.03), (1.75, 0.79, 0.66, 2.3, 0.02), (1.95, 0.72, 0.52, 2.4, 0.0),
        (2.12, 0.68, 0.46, 2.4, 0.0)] + TORSO


def garment(t0, t1, infl, thick, rings=GARMENT, open_front=None, nu=32, nv=10, inner="lip", disp=None,
            phi_range=None, name="Garment"):
    """Shell over the torso (t = index into `rings`, fractional). open_front(t) -> half-angle
    (radians) of a front opening; phi_range=(a, b) makes a partial panel instead."""
    def phi_of(u, t):
        if phi_range:
            return phi_range[0] + (phi_range[1] - phi_range[0]) * u
        if open_front:
            a = open_front(t)
            return a + u * (2 * math.pi - 2 * a)
        return 2 * math.pi * u

    def fo(u, v):
        t = t0 + (t1 - t0) * v
        phi = phi_of(u, t)
        return torso_pt(phi, t, infl + thick + (disp(phi, v) if disp else 0.0), rings)

    def fi(u, v):
        t = t0 + (t1 - t0) * v
        return torso_pt(phi_of(u, t), t, infl, rings)
    closed = not (open_front or phi_range)
    return patch(fo, fi, nu, nv, closed_u=closed, pole=False, inner=inner,
                 centre=Vector((0, 0, 2.8)), name=name)


def gt(z, rings=GARMENT):
    return t_at_z(z, rings)


def _neck_collar(phi0, phi1, z_in, r_in, z_out, r_out, thick, nu=20, name="Collar", lift=0.06):
    """Folded collar band lying on the shoulders around the neck (open between phi0/phi1)."""
    def pt(u, v, off):
        phi = phi0 + (phi1 - phi0) * u
        r = r_in + (r_out - r_in) * v
        z = z_in + (z_out - z_in) * v + lift * math.sin(math.pi * v) + off
        return Vector((r * math.sin(phi), -r * 0.85 * math.cos(phi), z))
    return patch(lambda u, v: pt(u, v, thick), lambda u, v: pt(u, v, 0.0), nu, 4, closed_u=False, pole=False,
                 inner="full", name=name)


def acc_top_flannel(color="#B23A33", plaid="#2A2422", tee="#EDEAE2"):
    of = lambda t: 15 * D2R
    t0, t1 = gt(2.08), gt(3.585)
    body = garment(t0, t1, 0.03, 0.035, open_front=of, nu=24, nv=8, name="Panels")
    col = _neck_collar(24 * D2R, 336 * D2R, 3.6, 0.3, 3.5, 0.5, 0.03, nu=14)
    flaps = []
    for s in (1, -1):
        p = torso_pt(s * 26 * D2R, gt(3.12), 0.075)
        flaps.append(rbox((0.24, 0.035, 0.11), loc=tuple(p), rot=(8, 0, s * 24), bevel=0.015, seg=1))
    tee_strip = garment(t0 + 0.2, gt(3.6), 0.012, 0.012, phi_range=(-17 * D2R, 17 * D2R), nu=4, nv=6, name="Tee")
    bands = []
    for z in (2.3, 2.72, 3.14):
        bands.append(garment(gt(z - 0.045), gt(z + 0.045), 0.062, 0.012, open_front=of, nu=24, nv=2, inner="none",
                             name="BandH"))
    for a in (40, 95, 145, 180, 215, 265, 320):
        bands.append(garment(t0 + 0.05, gt(3.48), 0.063, 0.011, phi_range=((a - 4.5) * D2R, (a + 4.5) * D2R),
                             nu=2, nv=6, inner="none", name="BandV"))
    return [spec("Flannel", [body, col] + flaps, color, "Fabric", role="top", smooth=50),
            spec("Plaid", bands, plaid, "Fabric", smooth=40),
            spec("Tee", [tee_strip], tee, "Fabric", smooth=50)]


def acc_top_vest(color="#3E6B4E", zip_col="#2B2D31"):
    t0, t1 = gt(2.06), gt(3.53)
    disp = lambda phi, v: 0.028 * abs(math.sin(math.pi * 5 * v)) ** 0.7
    body = garment(t0, t1, 0.035, 0.05, nu=22, nv=13, disp=disp, name="Vest")
    collar = loft_z([(3.5, 0.4, 0.33, 2.2), (3.62, 0.36, 0.3, 2.2), (3.76, 0.35, 0.29, 2.2), (3.79, 0.31, 0.25, 2.2)],
                    segs=16, cap0=False, cap1=False, name="Collar")
    zp = []
    for k in range(10):
        z = 2.12 + k * 0.165
        p = torso_pt(0, gt(min(z, 3.5)), 0.1)
        zp.append(p)
    zp.append(Vector((0, -0.39, 3.77)))
    zipper = tube(zp, [0.016] * len(zp), sides=6, res=1)
    pull = rbox((0.05, 0.02, 0.1), loc=(0, -0.4, 3.68), bevel=0.01, seg=1)
    return [spec("Vest", [body, collar], color, "Fabric", role="top", smooth=45),
            spec("Zip", [zipper, pull], zip_col, "Metal", smooth=40)]


def acc_top_scrubs(color="#5B9BD5", skin=SKIN, pen="#EDEAE2"):
    def of(t):
        z = torso_frame(t, GARMENT)[0]
        return (2 + 24 * smoothstep(3.22, 3.6, z)) * D2R if z > 3.22 else 0.0
    t0, t1 = gt(1.98), gt(3.585)
    body = garment(t0, t1, 0.03, 0.035, open_front=lambda t: max(of(t), 0.5 * D2R), nu=28, nv=9, name="Tunic")
    vee = garment(gt(3.15), gt(3.6), 0.012, 0.012, phi_range=(-28 * D2R, 28 * D2R), nu=8, nv=5, name="Vee")
    pk = torso_pt(28 * D2R, gt(2.98), 0.07)
    pocket = rbox((0.27, 0.035, 0.26), loc=tuple(pk), rot=(4, 0, 26), bevel=0.02, seg=1)
    trim = []
    for s in (1, -1):    # V-neck piping along the opening
        pts = [torso_pt(s * (of(gt(z)) + 0.02), gt(z), 0.07) for z in (3.22, 3.36, 3.48, 3.57)]
        trim.append(tube(pts, [0.025] * 4, sides=6, res=2))
    penb = ns.cyl(0.022, 0.24, loc=(pk.x - 0.06, pk.y - 0.012, pk.z + 0.1), rot=(0, 0, 0), verts=8, bevel=0.0)
    penc = ns.cyl(0.026, 0.06, loc=(pk.x - 0.06, pk.y - 0.012, pk.z + 0.22), verts=8, bevel=0.0)
    return [spec("Scrubs", [body, pocket] + trim, color, "Fabric", role="top", smooth=45),
            spec("Neck", [vee], skin, role="skin", smooth=50),
            spec("Pen", [penb, penc], pen, smooth=40)]


def acc_top_hoodie(color="#6B6F7A", strings="#EEEAE0"):
    t0, t1 = gt(2.1), gt(3.585)
    body = garment(t0, t1, 0.035, 0.05, nu=22, nv=7, name="Hoodie")
    hem = garment(gt(1.99), gt(2.13), 0.03, 0.06, nu=22, nv=2, name="Hem")
    pocket = garment(gt(2.18), gt(2.62), 0.085, 0.035, phi_range=(-38 * D2R, 38 * D2R), nu=8, nv=3, name="Pocket")
    # hood lying down at the back of the neck: a fat folded roll + back flap
    hood_pts = [Vector((s * x, y, z)) for s, x, y, z in ((1, 0.36, -0.12, 3.62), (1, 0.42, 0.12, 3.68),
                                                          (1, 0.3, 0.34, 3.72), (1, 0.0, 0.42, 3.74),
                                                          (-1, 0.3, 0.34, 3.72), (-1, 0.42, 0.12, 3.68),
                                                          (-1, 0.36, -0.12, 3.62))]
    roll = tube(hood_pts, [0.09, 0.13, 0.15, 0.16, 0.15, 0.13, 0.09], sides=7, res=2, name="HoodRoll")
    flap = garment(gt(3.0), gt(3.5), 0.085, 0.045, phi_range=(140 * D2R, 220 * D2R), nu=6, nv=3, name="HoodFlap")
    st = []
    for s in (1, -1):
        a = Vector((s * 0.13, -0.32, 3.58))
        st.append(tube([a, a + Vector((s * 0.01, -0.06, -0.2)), a + Vector((s * 0.02, -0.12, -0.42))],
                       [0.018, 0.016, 0.016], sides=6, res=3))
        st.append(ns.cyl(0.026, 0.07, loc=tuple(a + Vector((s * 0.02, -0.12, -0.45))), verts=8, bevel=0.0))
    return [spec("Hoodie", [body, hem, pocket, roll, flap], color, "Fabric", role="top", smooth=50),
            spec("Strings", st, strings, smooth=50)]


def acc_top_backpack(color="#C8523A", strap="#2B2D31", pocket="#3A3D42"):
    body = rbox((0.98, 0.44, 1.08), loc=(0, 0.7, 2.98), bevel=0.17, seg=3)
    ns.apply_all(body)
    for v in body.data.vertices:     # rounded top, slight taper
        if v.co.z > 3.2:
            k = (v.co.z - 3.2) / 0.32
            v.co.x *= 1 - 0.1 * k
            v.co.y = 0.7 + (v.co.y - 0.7) * (1 - 0.15 * k)
    pk = rbox((0.72, 0.18, 0.5), loc=(0, 0.95, 2.72), bevel=0.08, seg=2)
    straps, bits = [], []
    for s in (1, -1):
        pts = [Vector((s * 0.3, 0.52, 3.42)), Vector((s * 0.4, 0.2, 3.6)), torso_pt(s * 140 * D2R, gt(3.5), 0.06),
               torso_pt(s * 42 * D2R, gt(3.4), 0.07), torso_pt(s * 30 * D2R, gt(3.05), 0.075),
               torso_pt(s * 30 * D2R, gt(2.72), 0.075)]
        pts[1] = torso_pt(s * 90 * D2R, gt(3.56), 0.08)
        straps.append(tube(pts, [0.06] * len(pts), sides=6, res=3))
        bits.append(rbox((0.13, 0.05, 0.1), loc=tuple(torso_pt(s * 30 * D2R, gt(2.95), 0.105)), rot=(0, 0, s * 30),
                         bevel=0.015, seg=1))
    handle = tube([Vector((-0.16, 0.62, 3.5)), Vector((0, 0.66, 3.6)), Vector((0.16, 0.62, 3.5))], [0.03] * 3,
                  sides=6, res=3)
    zips = [ns.box((0.06, 0.03, 0.12), loc=(sx, 1.05, 2.9), bevel=0.01, segments=1) for sx in (-0.2, 0.2)]
    return [spec("Backpack", [body], color, "Fabric", role="top", smooth=50),
            spec("Pocket", [pk], pocket, "Fabric", smooth=50),
            spec("Straps", straps + [handle] + bits + zips, strap, smooth=50)]


def acc_top_badge(color=TOP, gold=GOLD, bar="#1E1F22"):
    pc = torso_pt(27 * D2R, gt(3.0), 0.04)
    pocket = rbox((0.3, 0.04, 0.32), loc=tuple(pc), rot=(4, 0, 27), bevel=0.025, seg=1)
    flap = rbox((0.32, 0.05, 0.1), loc=tuple(pc + Vector((0, -0.012, 0.13))), rot=(10, 0, 27), bevel=0.02, seg=1)
    btn = ns.sphere(0.025, loc=tuple(pc + Vector((-0.02, -0.04, 0.1))), segs=8, rings=4)
    bc = torso_pt(27 * D2R, gt(3.0), 0.09)
    shield = _shield(0.25, 0.31, 0.04)
    ns.apply_all(shield)
    xform(shield, Matrix.Translation(bc + Vector((0, -0.01, 0.0))) @ Matrix.Rotation(27 * D2R, 4, "Z"))
    star = ns.cyl(0.07, 0.02, loc=(0, 0, 0), rot=(90, 0, 0), verts=5, bevel=0.0)
    ns.apply_all(star)
    xform(star, Matrix.Translation(bc + Vector((0, -0.035, 0.02))) @ Matrix.Rotation(27 * D2R, 4, "Z"))
    nb = torso_pt(-27 * D2R, gt(3.1), 0.06)
    name_bar = rbox((0.26, 0.03, 0.065), loc=tuple(nb), rot=(4, 0, -27), bevel=0.01, seg=1)
    return [spec("Pocket", [pocket, flap, btn], color, "Fabric", role="top", smooth=45),
            spec("Badge", [shield, star], gold, "Metal", smooth=35),
            spec("NameBar", [name_bar], bar, smooth=35)]


def acc_top_overalls(color="#41618C", metal=GOLD):
    bib = garment(gt(2.15), gt(3.18), 0.04, 0.04, phi_range=(-46 * D2R, 46 * D2R), nu=10, nv=6, name="Bib")
    back = garment(gt(2.15), gt(2.92), 0.04, 0.04, phi_range=(132 * D2R, 228 * D2R), nu=8, nv=4, name="Back")
    waist = garment(gt(2.03), gt(2.3), 0.035, 0.045, nu=24, nv=2, name="Waist")
    pocket = garment(gt(2.62), gt(2.98), 0.082, 0.025, phi_range=(-20 * D2R, 20 * D2R), nu=6, nv=3, name="BibPocket")
    straps, metals = [], []
    for s in (1, -1):
        pts = [torso_pt(s * 38 * D2R, gt(3.12), 0.09), torso_pt(s * 40 * D2R, gt(3.38), 0.085),
               torso_pt(s * 62 * D2R, gt(3.53), 0.08), torso_pt(s * 120 * D2R, gt(3.5), 0.075),
               torso_pt(s * 155 * D2R, gt(3.2), 0.08), torso_pt(s * 168 * D2R, gt(2.9), 0.085)]
        straps.append(tube(pts, [0.055] * len(pts), sides=6, res=2))
        bp = torso_pt(s * 36 * D2R, gt(3.08), 0.1)
        metals.append(rbox((0.12, 0.04, 0.1), loc=tuple(bp), rot=(5, 0, s * 36), bevel=0.012, seg=1))
        sp = torso_pt(s * 84 * D2R, gt(2.2), 0.09)
        metals.append(ns.cyl(0.04, 0.03, loc=tuple(sp), rot=(0, 90, 0), verts=10, bevel=0.0))
    return [spec("Overalls", [bib, back, waist, pocket] + straps, color, "Fabric", role="top", smooth=45),
            spec("Buckles", metals, metal, "Metal", smooth=35)]


def acc_top_robe(color="#8F6FA8", pj="#D9D4C8"):
    R = ROBE

    def of(t):
        z = torso_frame(t, R)[0]
        return (3 + 28 * smoothstep(2.5, 3.6, z)) * D2R
    t0, t1 = 0.0, t_at_z(3.585, R)
    body = garment(t0, t1, 0.035, 0.05, rings=R, open_front=of, nu=20, nv=8, name="Robe")
    shawl = []
    for s in (1, -1):
        pts = [torso_pt(s * (of(t_at_z(z, R)) + 0.07), t_at_z(z, R), 0.1, R) for z in (2.3, 2.7, 3.1, 3.42)]
        pts.append(Vector((s * 0.36, -0.2, 3.66)))
        pts.append(Vector((s * 0.3, 0.2, 3.72)))
        pts.append(Vector((0.0, 0.33, 3.74)))
        shawl.append(tube(pts, [0.07, 0.085, 0.095, 0.1, 0.1, 0.1, 0.1], sides=6, res=2))
    belt = garment(t_at_z(2.3, R), t_at_z(2.42, R), 0.09, 0.035, rings=R, nu=20, nv=2, name="Belt")
    kp = torso_pt(-20 * D2R, t_at_z(2.36, R), 0.15, R)
    knot = ns.sphere(0.075, loc=tuple(kp), segs=7, rings=4)
    ends = [tube([kp, kp + Vector((-0.05, -0.04, -0.2)), kp + Vector((-0.03, -0.06, -0.45))], [0.05, 0.045, 0.04],
                 sides=6, res=2),
            tube([kp, kp + Vector((0.06, -0.05, -0.18)), kp + Vector((0.1, -0.08, -0.38))], [0.05, 0.045, 0.04],
                 sides=6, res=2)]
    pjs = garment(t_at_z(2.5, R), t_at_z(3.6, R), 0.012, 0.012, rings=R, phi_range=(-33 * D2R, 33 * D2R), nu=5,
                  nv=5, name="Pajama")
    return [spec("Robe", [body, belt, knot] + shawl + ends, color, "Fabric", role="top", smooth=50),
            spec("Pajama", [pjs], pj, "Fabric", smooth=50)]


# ---------------- table + placement -------------------------------------------------------
ACCESSORIES = {
    "Char_Hat_TruckerCap": (acc_hat_trucker, "HatSocket"),
    "Char_Hat_Beanie": (acc_hat_beanie, "HatSocket"),
    "Char_Hat_CopCap": (acc_hat_cop, "HatSocket"),
    "Char_Hair_Short": (acc_hair_short, "HairSocket"),
    "Char_Hair_Mullet": (acc_hair_mullet, "HairSocket"),
    "Char_Hair_Bun": (acc_hair_bun, "HairSocket"),
    "Char_Hair_Ponytail": (acc_hair_ponytail, "HairSocket"),
    "Char_Hair_Messy": (acc_hair_messy, "HairSocket"),
    "Char_Hair_Curly": (acc_hair_curly, "HairSocket"),
    "Char_Hair_Long": (acc_hair_long, "HairSocket"),
    "Char_Face_Beard": (acc_face_beard, "FaceSocket"),
    "Char_Face_Mustache": (acc_face_mustache, "FaceSocket"),
    "Char_Face_Glasses": (acc_face_glasses, "FaceSocket"),
    "Char_Face_Bags": (acc_face_bags, "FaceSocket"),
    "Char_Top_Flannel": (acc_top_flannel, "TorsoSocket"),
    "Char_Top_Vest": (acc_top_vest, "TorsoSocket"),
    "Char_Top_Scrubs": (acc_top_scrubs, "TorsoSocket"),
    "Char_Top_Hoodie": (acc_top_hoodie, "TorsoSocket"),
    "Char_Top_Backpack": (acc_top_backpack, "TorsoSocket"),
    "Char_Top_Badge": (acc_top_badge, "TorsoSocket"),
    "Char_Top_Overalls": (acc_top_overalls, "TorsoSocket"),
    "Char_Top_Robe": (acc_top_robe, "TorsoSocket"),
}


def place_accessory(specs, arm=None, bone=None, prefix="", offset=None, overrides=None):
    """Tag (and bind) accessory specs. overrides: {part name: colour}."""
    out = []
    for sp in specs:
        objs = sp["objs"]
        if offset is not None:
            for o in objs:
                ns.apply_all(o)
                xform(o, Matrix.Translation(offset))
        col = (overrides or {}).get(sp["name"], sp["color"])
        out.append(part(objs, prefix + sp["name"], col, sp["mat"], arm=arm, bone=bone, role=sp["role"],
                        smooth=sp["smooth"], transparency=sp["transparency"], shadow=sp["shadow"]))
    return out


def run_accessory(asset: str, **kw):
    """Standalone accessory generator: build in body space, move the socket to the origin,
    preview, export with pivot = attach point."""
    fn, sock = ACCESSORIES[asset]

    def build():
        reset_caches()
        specs = fn(**kw)
        place_accessory(specs, offset=-SOCKETS[sock])
        meta = {"socket": sock, "bone": SOCKET_BONE[sock], "attach": "pivot = socket; weld to the bone part"}
        meta.update(ACC_META.get(asset, {}))
        return {"export": {"pivot": (0.0, 0.0, 0.0), "meta": meta}}
    return ns.run_main(build, asset, BATCH, GROUP)


# Hat x hair compatibility from a triangle-intersection test of every pair (0 = no clipping).
_HAT_FITS = {"Char_Hat_TruckerCap": ["Short", "Mullet"], "Char_Hat_Beanie": ["Short", "Mullet"],
             "Char_Hat_CopCap": ["Short", "Mullet", "Long"]}
ACC_META = {h: {"fitsHair": v, "hairNote": "other hair styles clip through this hat — hide hair or pick a listed one"}
            for h, v in _HAT_FITS.items()}
for _hair in ("Short", "Mullet", "Bun", "Ponytail", "Messy", "Curly", "Long"):
    ACC_META["Char_Hair_" + _hair] = {"fitsHats": [h.replace("Char_Hat_", "") for h, v in _HAT_FITS.items() if _hair in v]}
ACC_META["Char_Face_Glasses"] = {"lensTransparency": 0.6}
ACC_META["Char_Face_Bags"] = {"transparency": 0.35, "note": "semi-transparent so it darkens any skin tone"}
ACC_META["Char_Top_Scrubs"] = {"skinRole": "the V-neck insert has role skin"}
ACC_META["Char_Top_Robe"] = {"note": "hip-length; flares over the hips so the walk's leg swing stays inside"}


# --------------------------------------------------------------------------------------
# REGULARS — helpers shared by Character_Regular_*.py
# --------------------------------------------------------------------------------------
# lightning bolt as two convex pieces (upper slab + lower spike) — robust to triangulate
BOLT = [[(0.06, 0.5), (-0.24, -0.02), (0.06, -0.02), (0.26, 0.5)],
        [(-0.06, 0.1), (0.26, 0.1), (-0.14, -0.52)]]


def head_decal(poly, phi_c, psi_c, size, infl, thick, name="Decal"):
    """Flat outline (x right, y up, about unit size) wrapped onto the head-shaped surface
    at `infl` (e.g. a helmet's outer skin), `thick` deep."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, 0.0)) for x, y in poly]
    f = bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=[f], ngon_method="EAR_CLIP")
    ext = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    for v in ext["geom"]:
        if isinstance(v, bmesh.types.BMVert):
            v.co.z = 1.0
    R = 0.62 + infl
    for v in bm.verts:
        x, y, z = v.co
        phi = phi_c + x * size / (R * math.sin(psi_c))
        psi = psi_c - y * size / R
        v.co = head_pt(phi, psi, infl + z * thick)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def rrect(w, h, r, n=4):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                       (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def arm_bands(s, zs, height=0.08, grow=0.012, segs=16):
    """Plaid rings around a sleeve (arm-local z positions), returned in world rest pose."""
    out = []
    rings = arm_rings()
    for z in zs:
        def r_at(zz):
            for (z0, a0, b0, n0), (z1, a1, b1, n1) in zip(rings, rings[1:]):
                if z1 <= zz <= z0:
                    t = (zz - z0) / (z1 - z0)
                    return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t
            return rings[-1][1], rings[-1][2]
        a0, b0 = r_at(z + height / 2)
        a1, b1 = r_at(z - height / 2)
        o = loft_z([(z - height / 2, a1 + grow, b1 + grow, 2.1), (z + height / 2, a0 + grow, b0 + grow, 2.1)],
                   segs=segs, cap0=False, cap1=False, name="ArmBand")
        xform(o, _arm_matrix(s))
        out.append(o)
    return out


def arm_stripes(s, angles, z0=-1.12, z1=0.05, width=0.07, grow=0.011, nv=6):
    """Lengthwise plaid stripes on a sleeve at angles (deg, 0 = front)."""
    out = []
    rings = arm_rings()

    def r_at(zz):
        for (za, a0, b0, n0), (zb, a1, b1, n1) in zip(rings, rings[1:]):
            if zb <= zz <= za:
                t = (zz - za) / (zb - za)
                return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t
        return rings[-1][1], rings[-1][2]
    for ang in angles:
        def pt(u, v, off):
            z = z0 + (z1 - z0) * v
            a, b = r_at(z)
            phi = math.radians(ang) + (u - 0.5) * width / max(a, 0.15)
            x, y = se_point(phi, a + grow + off, b + grow + off, 2.1)
            return Vector((x, y, z))
        o = patch(lambda u, v: pt(u, v, 0.011), lambda u, v: pt(u, v, 0.0), 2, nv, closed_u=False, pole=False,
                  inner="none", centre=Vector((0, 0, (z0 + z1) / 2)), name="ArmStripe")
        xform(o, _arm_matrix(s))
        out.append(o)
    return out


def strip_roles(specs, keep=()):
    for sp in specs:
        if sp["role"] not in keep:
            sp["role"] = None
    return specs


def pose_tiles(arm, items, name, res=340, samples=12, out_dir=PREV):
    """One tile per (action, frame, yaw, seated) — each with its own camera fit."""
    from PIL import Image, ImageDraw
    paths = []
    ns._setup_render(res, samples)
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -0.002))
    fl = bpy.context.active_object
    fl.name = "Floor"
    fl.data.materials.append(ns.material("#3A3B42"))
    for i, (act, f, yaw, seated) in enumerate(items):
        props = booth_proxy() if seated else []
        arm.animation_data.action = act
        if hasattr(arm.animation_data, "action_slot") and len(act.slots):
            arm.animation_data.action_slot = act.slots[0]
        bpy.context.scene.frame_set(f)
        lo, hi = ns.bbox_world(ns._tagged_objects() + props)
        lo.z = min(lo.z, 0.0)
        for o in list(bpy.context.scene.objects):
            if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim")):
                bpy.data.objects.remove(o, do_unlink=True)
        cam, ctr, dist = ns._camera_fit(lo, hi, yaw, 10, fov_deg=30, margin=1.02)
        k = math.radians(yaw)
        ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * dist, 60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
        ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3)) * dist, 22 * dist ** 2 / 9, size=dist * 0.8, target=ctr)
        p = os.path.join(out_dir, f"_tmp_{name}_{i}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append((p, f"{act.name} f{f}"))
        for o in props:
            bpy.data.objects.remove(o, do_unlink=True)
    for o in list(bpy.context.scene.objects):
        if o.name.startswith(("PreviewCam", "Key", "Fill", "Rim", "Floor")):
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.context.scene.frame_set(0)
    sheet = Image.new("RGB", (res * len(paths), res), (24, 26, 30))
    d = ImageDraw.Draw(sheet)
    for i, (p, lab) in enumerate(paths):
        sheet.paste(Image.open(p).convert("RGB"), (i * res, 0))
        d.text((i * res + 6, 6), lab, fill=(255, 255, 255))
        os.remove(p)
    out = os.path.join(out_dir, f"{name}_poses.png")
    sheet.save(out)
    return out


def run_regular(asset, build_regular, extra_meta=None):
    """Regular generator: same rig/bones/sockets as Character_Human, clips from anim/Human.lua."""
    def build():
        reset_caches()
        arm = make_rig()
        build_regular(arm)
        return {"arm": arm, "export": {"rig": arm, "pivot": (0.0, 0.0, 0.0), "meta": base_meta(extra_meta),
                                       "sockets": socket_spec()}}
    out = ns.run_main(build, asset, BATCH, GROUP)
    if os.environ.get("NS_POSES", "1") == "1":
        arm = out["arm"]
        acts = {a.name: a for a in build_actions(arm)}
        print(f"[{asset}] poses:", pose_tiles(arm, [(acts["Idle"], 0, -25, False), (acts["Walk"], 7, -70, False),
                                                    (acts["Wave"], 13, -15, False), (acts["Eat"], 22, -55, True),
                                                    (acts["ChaseRun"], 5, -70, False)], asset))
    return out
