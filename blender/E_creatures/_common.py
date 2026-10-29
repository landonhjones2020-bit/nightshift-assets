"""Shared helpers for the E_creatures batch (creature rigs + keyframed clips).

Import from a generator in this folder with:
    import _common as C          (the folder is on sys.path when the script runs)
    ns = C.ns                     (the shared nslib)

Conventions (same as the gate Nibbler): every bone points +Y with roll 0, so a bone's local
frame equals the world frame at rest and ns.key Euler keys read as world axes:
X = pitch (+ tips the front -Y downward / swings a hanging limb backward),
Y = roll (+ tilts the top toward +X), Z = yaw (+ turns the front toward +X).
Creatures face Blender -Y; their "L" side is Blender +X (as LegFL on the Nibbler).

What lives here (batch-local, on top of nslib):
  * shape builders nslib lacks: rod/capsule between points, superellipse lofts, rounded
    plates, extrusions in any plane, `part` (join + tag) and `attach` (part + bind)
  * `Skel`: the rig's joint table with a Python forward-kinematics mirror of Blender's pose
    evaluation, so clips can be posed by targets (2-bone IK for arms/legs, aim, feet flat)
  * clip builders: `clip` (hand-keyed poses, every bone keyed at both ends) and
    `sampled_clip` (procedural cycles keyed every few frames with linear ease)
  * `biped_cycle`: no-slide walk/run generator (feet move back at exactly `speed` studs/s
    while planted), used for every biped locomotion clip and its clipSpeedRef
  * checks: loop seam, key-to-key rotation jumps / exported Euler jumps (limb flipping),
    foot slide while planted
  * `pose_strip`: like ns.render_pose_strip but framed on the union of all frames, with
    frame labels and optional floor/ceiling/5-stud reference
"""
from __future__ import annotations

import json
import math
import os
import sys

import bpy  # noqa: F401  (must load before bmesh/mathutils in the bpy module build)
import bmesh
from mathutils import Euler, Matrix, Quaternion, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import nslib as ns  # noqa: E402

BATCH = "E_creatures"
GROUP = "Creatures"
FPS = 30
PREV_DIR = os.path.abspath(os.path.join(ns.REPO, "..", "previews", BATCH))
I3 = Matrix.Identity(3)
V0 = Vector((0.0, 0.0, 0.0))

# ---- shared creature palette ----------------------------------------------------------
VOID = "#07070A"            # shadowed hood / eye sockets (reads as a hole)
INK = "#16161B"             # near-black clothing
DRIP = "#7FB4D6"            # rain drops (Glass-ish, semi transparent)
FROST = "#E4F3FA"
ICY_EYES = "#8FF3FF"
PAPER_WHITE = "#F1EDE2"


# ======================================================================================
# Geometry helpers
# ======================================================================================

def _assert_name(name):
    # nslib.render_preview deletes scene objects whose names start with these prefixes
    assert not name.startswith(("PreviewCam", "Key", "Fill", "Rim", "RefCube", "Floor")), name


def part(objs, name, color, mat="SmoothPlastic", **kw):
    """Join (applying modifiers) and tag in one go. objs may be one object or a list."""
    _assert_name(name)
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    if len(objs) == 1:
        o = objs[0]
        ns.apply_all(o)
    else:
        o = ns.join_applied(list(objs), name)
    return ns.tag(o, name, color, mat, **kw)


def attach(objs, name, color, arm, bone, mat="SmoothPlastic", **kw):
    """part() + ns.bind() to a bone."""
    return ns.bind(part(objs, name, color, mat, **kw), arm, bone)


def rod(p0, p1, r, verts=8, bevel=0.0, segments=1, name="Rod", r_top=None):
    """Straight cylinder (or taper with r_top) from point p0 to p1."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    o = ns.cyl(r, d.length, loc=(p0 + p1) / 2, verts=verts, bevel=bevel, segments=segments,
               radius_top=r_top, name=name)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def capsule(p0, p1, r0, r1=None, verts=10, cap_rings=3, name="Capsule"):
    """Tapered capsule (round ends) from p0 (radius r0) to p1 (radius r1)."""
    r1 = r0 if r1 is None else r1
    p0, p1 = Vector(p0), Vector(p1)
    L = (p1 - p0).length
    prof = []
    for i in range(cap_rings + 1):                         # bottom cap (around p0)
        a = -math.pi / 2 + (math.pi / 2) * i / cap_rings
        prof.append((r0 * math.cos(a), r0 * math.sin(a)))
    for i in range(cap_rings + 1):                         # top cap (around p1)
        a = (math.pi / 2) * i / cap_rings
        prof.append((r1 * math.cos(a), L + r1 * math.sin(a)))
    prof = [(max(r, 0.0), z) for r, z in prof]
    o = ns.lathe(prof, verts=verts, name=name)
    ns.apply_all(o)
    q = (p1 - p0).to_track_quat("Z", "Y")
    o.rotation_euler = q.to_euler()
    o.location = p0
    ns.apply_all(o)
    return o


def ell(center, radii, segs=14, rings=8, rot=(0, 0, 0), name="Ell"):
    """Ellipsoid centred at `center` with semi-axes `radii` (applied)."""
    o = ns.sphere(1.0, loc=center, rot=rot, scale=radii, segs=segs, rings=rings, name=name)
    ns.apply_all(o)
    return o


def superellipse(rx, ry, n=2.0, verts=16, cx=0.0, cy=0.0, phase=0.0):
    pts = []
    for i in range(verts):
        a = 2 * math.pi * i / verts + phase
        c, s = math.cos(a), math.sin(a)
        x = math.copysign(abs(c) ** (2.0 / n), c) * rx
        y = math.copysign(abs(s) ** (2.0 / n), s) * ry
        pts.append((cx + x, cy + y))
    return pts


def loft(sections, verts=16, n=2.0, cap_bottom=True, cap_top=True, name="Loft", phase=None):
    """Loft through horizontal superellipse sections.

    sections: [(z, rx, ry, cx, cy), ...] bottom to top (cx, cy optional), or with a 6th
    element = per-section exponent n. Radius 0 collapses to a point (pole).
    """
    bm = bmesh.new()
    rings = []
    ph = (math.pi / verts) if phase is None else phase
    for sec in sections:
        z, rx, ry = sec[0], sec[1], sec[2]
        cx = sec[3] if len(sec) > 3 else 0.0
        cy = sec[4] if len(sec) > 4 else 0.0
        nn = sec[5] if len(sec) > 5 else n
        if rx < 1e-5 and ry < 1e-5:
            rings.append([bm.verts.new((cx, cy, z))])
        else:
            rings.append([bm.verts.new((x, y, z)) for x, y in superellipse(rx, ry, nn, verts, cx, cy, ph)])
    for r0, r1 in zip(rings[:-1], rings[1:]):
        if len(r0) == 1 and len(r1) == 1:
            continue
        if len(r0) == 1:
            for i in range(verts):
                bm.faces.new([r0[0], r1[i], r1[(i + 1) % verts]])
        elif len(r1) == 1:
            for i in range(verts):
                bm.faces.new([r0[i], r0[(i + 1) % verts], r1[0]])
        else:
            for i in range(verts):
                j = (i + 1) % verts
                bm.faces.new([r0[i], r0[j], r1[j], r1[i]])
    if cap_bottom and len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if cap_top and len(rings[-1]) > 1:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name)


def rrect(w, h, r, n=4, cx=0.0, cy=0.0):
    """Closed 2D rounded-rectangle outline (w x h, corner radius r, n segments/corner)."""
    r = min(r, w / 2 - 1e-4, h / 2 - 1e-4)
    pts = []
    corners = ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
               (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270))
    for x, y, a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + x + r * math.cos(a), cy + y + r * math.sin(a)))
    return pts


def extrude(points2d, thickness, plane="XY", offset=0.0, bevel=0.0, segments=2, name="Ext"):
    """Extrude a closed 2D outline.
    plane "XY": outline (x, y), extruded +Z from z = offset.
    plane "XZ": outline (x, z), extruded +Y from y = offset (front-facing plates).
    plane "YZ": outline (y, z), extruded +X from x = offset (side profiles)."""
    bm = bmesh.new()
    if plane == "XY":
        vs = [bm.verts.new((a, b, offset)) for a, b in points2d]
        dvec = (0, 0, thickness)
    elif plane == "XZ":
        vs = [bm.verts.new((a, offset, b)) for a, b in points2d]
        dvec = (0, thickness, 0)
    else:
        vs = [bm.verts.new((offset, a, b)) for a, b in points2d]
        dvec = (thickness, 0, 0)
    face = bm.faces.new(vs)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=dvec)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return ns.from_bmesh(bm, name, (0, 0, 0), (0, 0, 0), bevel, segments)


def stroke(points, width, thickness, plane="XZ", offset=0.0, name="Stroke", round_ends=True):
    """A flat ribbon of `width` following a 2D polyline (crayon line, scar, seam),
    extruded `thickness` in the plane's normal direction."""
    pts = [Vector((p[0], p[1])) for p in points]
    left, right = [], []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        nrm = Vector((-t.y, t.x))
        left.append(p + nrm * width / 2)
        right.append(p - nrm * width / 2)
    outline = left + list(reversed(right))
    if round_ends:
        # round caps: a few points around each end
        def cap(c, d, k=3):
            out = []
            base = math.atan2(d.y, d.x)
            for i in range(1, k):
                ang = base + math.pi / 2 - math.pi * i / k
                out.append(c + Vector((math.cos(ang), math.sin(ang))) * width / 2)
            return out
        d_end = (pts[-1] - pts[-2]).normalized()
        d_start = (pts[0] - pts[1]).normalized()
        outline = left + cap(pts[-1], d_end) + list(reversed(right)) + cap(pts[0], d_start)
    return extrude([(p.x, p.y) for p in outline], thickness, plane=plane, offset=offset, name=name)


def plate(w, h, t, r, loc, plane="XZ", bevel=0.01, n=3, name="Plate"):
    """Rounded-rect plate of thickness t centred at loc. plane XZ = facing -Y (front)."""
    o = extrude(rrect(w, h, r, n), t, plane=plane, offset=-t / 2, bevel=bevel, segments=1, name=name)
    o.location = Vector(loc)
    return o


def drop(loc, r=0.07, name="Drop"):
    """Rain drop: sphere with a pulled-up point."""
    o = ns.sphere(r, loc=(0, 0, 0), segs=8, rings=5, name=name)
    ns.apply_all(o)
    for v in o.data.vertices:
        if v.co.z > 0:
            k = v.co.z / r
            v.co.x *= (1 - 0.75 * k)
            v.co.y *= (1 - 0.75 * k)
            v.co.z *= 1 + 1.3 * k
    o.location = Vector(loc)
    ns.apply_all(o)
    return o


def arc_loft(sections, a0, a1, segs=10, thickness=0.06, n=2.0, name="ArcLoft"):
    """Open partial shell through superellipse sections over the angle range a0..a1 (deg;
    0 = +X, 90 = +Y back, -90 = -Y front), given thickness with a Solidify modifier
    (applied by part()). sections: [(z, rx, ry[, cx, cy]), ...] bottom to top."""
    bm = bmesh.new()
    rows = []
    for sec in sections:
        z, rx, ry = sec[0], sec[1], sec[2]
        cx = sec[3] if len(sec) > 3 else 0.0
        cy = sec[4] if len(sec) > 4 else 0.0
        row = []
        for i in range(segs + 1):
            a = math.radians(a0 + (a1 - a0) * i / segs)
            c, s_ = math.cos(a), math.sin(a)
            x = math.copysign(abs(c) ** (2.0 / n), c) * rx
            y = math.copysign(abs(s_) ** (2.0 / n), s_) * ry
            row.append(bm.verts.new((cx + x, cy + y, z)))
        rows.append(row)
    for r0, r1 in zip(rows[:-1], rows[1:]):
        for i in range(segs):
            bm.faces.new([r0[i], r0[i + 1], r1[i + 1], r1[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = ns.from_bmesh(bm, name)
    # make normals point outward (away from the section centre line)
    me = o.data
    me.update()
    out = 0
    for poly in me.polygons:
        c = poly.center
        out += (poly.normal.x * c.x + poly.normal.y * c.y)
    if out < 0:
        bm2 = bmesh.new()
        bm2.from_mesh(me)
        for f in bm2.faces:
            f.normal_flip()
        bm2.to_mesh(me)
        bm2.free()
    if thickness > 0:
        mod = o.modifiers.new("Solid", "SOLIDIFY")
        mod.thickness = thickness
        mod.offset = -1.0
        mod.use_even_offset = True
    return o


def glove(wrist, side=1, palm=(0.1, 0.17, 0.2), fingers=4, flen=0.45, fr=0.05, curl=12.0,
          thumb=0.3, spread=1.0, rot=None, fverts=6, name="Hand"):
    """Stylised hand hanging from `wrist`: palm (half-sizes x thick, y wide, z long),
    `fingers` capsules pointing down (-Z) and curled toward the palm side, thumb in front.
    side=+1 for an L (+X) hand: palm faces -X (toward the body). rot = optional extra
    rotation (Matrix/Euler deg) about the wrist. Returns a list of objects."""
    pw, pd, ph = palm
    objs = [ell((0, 0, -ph * 0.95), (pw, pd, ph), segs=10, rings=6)]
    for i in range(fingers):
        t = i / max(1, fingers - 1)
        y = (-pd * 0.72 + 1.44 * pd * t) * spread
        z0 = -ph * 1.75
        L = flen * (1.0 - 0.18 * abs(t - 0.4) * 2)
        cr = math.radians(curl * (0.8 + 0.4 * t))
        tip = (-side * math.sin(cr) * L, y * 1.12, z0 - math.cos(cr) * L)
        objs.append(capsule((0, y, z0 + fr), tip, fr, fr * 0.85, verts=fverts, cap_rings=2))
    if thumb > 0:
        b = (-side * pw * 0.3, -pd * 0.75, -ph * 0.55)
        tip = (-side * (pw + 0.07), -pd * 1.25, -ph * 0.55 - thumb)
        objs.append(capsule(b, tip, fr * 1.1, fr * 0.9, verts=fverts, cap_rings=2))
    R = as_mat(rot) if rot is not None else I3
    W = Vector(wrist)
    for o in objs:
        ns.apply_all(o)
        for v in o.data.vertices:
            v.co = W + R @ v.co
        o.data.update()
    return objs


def deform(obj, fn):
    """Apply fn(Vector) -> Vector to every vertex (after applying modifiers/transforms)."""
    ns.apply_all(obj)
    for v in obj.data.vertices:
        v.co = fn(v.co.copy())
    obj.data.update()
    return obj


def noise3(p, seed=0.0):
    """Cheap smooth pseudo-noise in [-1, 1] (sum of sines) for organic lumps."""
    x, y, z = p.x, p.y, p.z
    return (math.sin(1.7 * x + 2.3 * y + 0.7 + seed) * math.sin(2.1 * z - 1.3 * x + 1.9 * seed)
            + 0.5 * math.sin(3.7 * y + 2.9 * z + 0.3 * seed)) / 1.5


# ======================================================================================
# Rig: joint table + Python FK mirror
# ======================================================================================

def rot_deg(rx=0.0, ry=0.0, rz=0.0) -> Matrix:
    return Euler((math.radians(rx), math.radians(ry), math.radians(rz)), "XYZ").to_matrix()


def as_mat(rot) -> Matrix:
    if rot is None:
        return I3.copy()
    if isinstance(rot, Matrix):
        return rot.to_3x3()
    if isinstance(rot, Quaternion):
        return rot.to_matrix()
    return rot_deg(*rot)


def to_deg(R: Matrix):
    e = R.to_euler("XYZ")
    return (math.degrees(e.x), math.degrees(e.y), math.degrees(e.z))


class Skel:
    """Joint table for a rigid-part rig + forward kinematics matching Blender's pose eval.

    joints = [(bone, parent_or_None, head_xyz), ...] parents first.
    A pose is {bone: (rot, loc)} with rot = Euler degrees tuple | Matrix | Quaternion | None
    and loc = local offset (bone frame) or None; bones missing from the pose are at rest.
    """

    def __init__(self, name, joints, bone_len=0.25):
        self.name = name
        self.joints = joints
        self.order = [b for b, _, _ in joints]
        self.parent = {b: p for b, p, _ in joints}
        self.head = {b: Vector(h) for b, _, h in joints}
        for b, p, _ in joints:
            assert p is None or self.order.index(p) < self.order.index(b), (b, p)
        self.arm = ns.make_armature(name, [(b, p, h, (h[0], h[1] + bone_len, h[2])) for b, p, h in joints])
        self.children = {b: [c for c in self.order if self.parent[c] == b] for b in self.order}

    # ---- FK ----------------------------------------------------------------------------
    def fk(self, pose):
        W = {}
        for b in self.order:
            rot, loc = _split(pose.get(b))
            R = as_mat(rot)
            L = Vector(loc) if loc is not None else V0
            p = self.parent[b]
            if p is None:
                W[b] = (R, self.head[b] + L)
            else:
                Rp, hp = W[p]
                W[b] = (Rp @ R, hp + Rp @ (self.head[b] - self.head[p] + L))
        return W

    def point(self, W, bone, p_rest):
        """World position of a rest-pose point carried by `bone`."""
        R, h = W[bone]
        return h + R @ (Vector(p_rest) - self.head[bone])

    def local_rot(self, W, bone, R_world):
        """Local rotation for `bone` so its world rotation becomes R_world (parent posed)."""
        p = self.parent[bone]
        if p is None:
            return R_world
        return W[p][0].inverted() @ R_world

    def bones(self):
        return list(self.order)


def _split(spec):
    if spec is None:
        return None, None
    if isinstance(spec, tuple) and len(spec) == 2 and (spec[1] is None or isinstance(spec[1], (tuple, list, Vector))) \
            and not isinstance(spec[0], (int, float)):
        return spec[0], spec[1]
    return spec, None


def basis(d, f):
    d = Vector(d).normalized()
    f = Vector(f)
    f = (f - d * f.dot(d))
    if f.length < 1e-8:
        f = d.orthogonal()
    f.normalize()
    s = d.cross(f)
    return Matrix((d, f, s)).transposed()


def ik2(S, T, a, b, pole, d0, f0, soft=0.9995):
    """Two-segment IK in world space.

    S root joint, T end target, a/b segment lengths, pole = world direction the middle joint
    should point toward, d0 = rest direction of the chain, f0 = rest flex direction (the
    distal segment bends toward f0). Returns (R_upper_world, R_lower_local_hinge, E, ok).
    """
    S, T, pole, d0, f0 = Vector(S), Vector(T), Vector(pole), Vector(d0).normalized(), Vector(f0).normalized()
    t = T - S
    dist = t.length
    dmin, dmax = abs(a - b) + 1e-3, (a + b) * soft
    ok = dmin - 1e-4 <= dist <= (a + b) * 0.999 + 1e-4
    dist = min(max(dist, dmin), dmax)
    th = t.normalized() if t.length > 1e-8 else d0
    p = pole - th * pole.dot(th)
    if p.length < 1e-6:
        p = th.orthogonal()
    p.normalize()
    cos_a = max(-1.0, min(1.0, (a * a + dist * dist - b * b) / (2 * a * dist)))
    al = math.acos(cos_a)
    u1 = th * math.cos(al) + p * math.sin(al)
    E = S + u1 * a
    Tc = S + th * dist
    l1 = (Tc - E).normalized()
    f1 = l1 - u1 * l1.dot(u1)
    if f1.length < 1e-6:
        f1 = -p
    R_up = basis(u1, f1) @ basis(d0, f0).transposed()
    theta = math.acos(max(-1.0, min(1.0, u1.dot(l1))))
    k = d0.cross(f0).normalized()
    R_lo = Matrix.Rotation(theta, 3, k)
    return R_up, R_lo, E, ok


def aim(d_rest, d_target, up_rest=None, up_target=None):
    """Rotation taking d_rest to d_target (and up_rest toward up_target if given)."""
    d_rest, d_target = Vector(d_rest).normalized(), Vector(d_target).normalized()
    if up_rest is None:
        return d_rest.rotation_difference(d_target).to_matrix()
    return basis(d_target, up_target) @ basis(d_rest, up_rest).transposed()


def solve_limb(sk, pose, upper, lower, end_rest, target, pole, d0=None, f0=None, end=None,
               end_world=None):
    """Pose a 2-bone limb so the rest point `end_rest` (on `lower`) reaches `target`.

    Updates `pose` in place (upper and lower rotations; optional `end` bone set so its world
    rotation is `end_world`). d0 defaults to the rest direction upper->lower joint; f0 must
    be given (flex direction). Returns ok flag."""
    W = sk.fk(pose)
    S = W[upper][1]
    a = (sk.head[lower] - sk.head[upper]).length
    b = (Vector(end_rest) - sk.head[lower]).length
    d0 = Vector(d0) if d0 is not None else (sk.head[lower] - sk.head[upper]).normalized()
    # rest direction of the lower segment may differ from d0: correct with a fixed offset
    dl = (Vector(end_rest) - sk.head[lower]).normalized()
    R_up, R_lo, E, ok = ik2(S, target, a, b, pole, d0, f0)
    # R_lo maps d0 -> lower world dir (in upper frame); lower's own rest dir is dl
    off = d0.rotation_difference(dl).to_matrix() if (d0 - dl).length > 1e-4 else I3
    R_lo = R_lo @ off.inverted()
    keep_up = _split(pose.get(upper))[1]
    keep_lo = _split(pose.get(lower))[1]
    pose[upper] = (sk.local_rot(W, upper, R_up), keep_up)
    pose[lower] = (R_lo, keep_lo)
    if end is not None and end_world is not None:
        W2 = sk.fk(pose)
        pose[end] = (sk.local_rot(W2, end, as_mat(end_world)), _split(pose.get(end))[1])
    return ok


def reach_rel(sk, pose, upper, lower, end, grip_rest, target, end_local, pole, f0, iters=5):
    """IK a limb so the rest point `grip_rest` (carried by `end`) lands on `target` while the
    end bone keeps the LOCAL rotation `end_local` relative to `lower` (a wrist pose, not a
    world orientation: avoids large wrist twists). Iterates because the wrist target
    depends on the solved forearm orientation."""
    Rl = as_mat(end_local)
    target = Vector(target)
    pose[end] = (Rl, _split(pose.get(end))[1])
    ok = True
    for _ in range(iters):
        W = sk.fk(pose)
        Rh = W[lower][0] @ Rl
        wt = target - Rh @ (Vector(grip_rest) - sk.head[end])
        ok = solve_limb(sk, pose, upper, lower, sk.head[end], wt, pole, f0=f0)
    pose[end] = (Rl, _split(pose.get(end))[1])
    return ok


# ======================================================================================
# Clips
# ======================================================================================

def key_pose(sk, frame, pose, ease="SINE", direction="EASE_IN_OUT", bones=None, loc_bones=()):
    """Key every bone in `bones` (default: the pose's bones) at `frame`."""
    arm = sk.arm
    for b in (bones or pose.keys()):
        rot, loc = _split(pose.get(b))
        R = as_mat(rot)
        if loc is None and b in loc_bones:
            loc = (0.0, 0.0, 0.0)
        ns.key(arm, b, frame, rot=to_deg(R), loc=tuple(loc) if loc is not None else None,
               ease=ease, direction=direction)


def clip(sk, name, length, loop, keys, ease="SINE", direction="EASE_IN_OUT", end_pose=None):
    """Hand-keyed clip.

    keys: [(frame, pose_dict) | (frame, pose_dict, ease) | (frame, pose_dict, ease, direction)].
    Every bone is keyed at frame 0 and `length`: bones not given there are at rest. Looping
    clips copy frame 0's pose to `length` (seam = exact). One-shots end on `end_pose`
    (default rest = neutral) unless the keys give the last frame themselves.
    """
    act = ns.new_action(sk.arm, name, 0, length, loop=loop, fps=FPS)
    keys = sorted([tuple(k) for k in keys], key=lambda k: k[0])
    frames = {k[0]: k for k in keys}
    if 0 not in frames:
        keys.insert(0, (0, {}))
    first = dict(keys[0][1])
    if length not in frames:
        if loop:
            keys.append((length, first))
        else:
            keys.append((length, dict(end_pose or {})))
    elif loop:
        keys[-1] = (length, first) + tuple(keys[-1][2:])
    loc_bones = set()
    for k in keys:
        for b, spec in k[1].items():
            if _split(spec)[1] is not None:
                loc_bones.add(b)
    allb = sk.bones()
    for i, k in enumerate(keys):
        f, pose = k[0], k[1]
        e = k[2] if len(k) > 2 else ease
        d = k[3] if len(k) > 3 else direction
        bl = allb if (i == 0 or i == len(keys) - 1) else list(pose.keys())
        key_pose(sk, f, pose, ease=e, direction=d, bones=bl, loc_bones=loc_bones)
    fix_quat_signs(act)
    return act


def sampled_clip(sk, name, length, loop, fn, step=2, ease="LINEAR"):
    """Procedural clip: fn(frame) -> full pose dict; keyed every `step` frames (+ the last)."""
    act = ns.new_action(sk.arm, name, 0, length, loop=loop, fps=FPS)
    frames = list(range(0, length, step)) + [length]
    poses = {f: fn(f) for f in frames}
    if loop:
        poses[length] = poses[0]
    loc_bones = set()
    for p in poses.values():
        for b, spec in p.items():
            if _split(spec)[1] is not None:
                loc_bones.add(b)
    for f in frames:
        key_pose(sk, f, poses[f], ease=ease, bones=sk.bones(), loc_bones=loc_bones)
    fix_quat_signs(act)
    return act


EASES = {
    "linear": lambda t: t,
    "sine": lambda t: 0.5 - 0.5 * math.cos(math.pi * t),
    "in": lambda t: t * t,
    "out": lambda t: 1 - (1 - t) ** 2,
    "in3": lambda t: t ** 3,
    "out3": lambda t: 1 - (1 - t) ** 3,
    "back": lambda t: 1 + 2.70158 * (t - 1) ** 3 + 1.70158 * (t - 1) ** 2,   # overshoot out
    "hold": lambda t: 0.0,
}


def _lerp_val(a, b, t):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a + (b - a) * t
    if isinstance(a, (tuple, list, Vector)) and isinstance(b, (tuple, list, Vector)):
        return tuple(x + (y - x) * t for x, y in zip(a, b))
    return a if t < 1.0 else b


def param_clip(sk, name, length, loop, keys, fn, step=2):
    """Clip from interpolated pose PARAMETERS, re-solved (IK) on every sample.

    keys: [(frame, {param: value}, ease)] - ease (EASES name) shapes the segment that starts
    at this key; params missing from a key carry over from the previous one (the first key
    must define them all). Numbers and tuples interpolate; anything else switches at the
    next key. fn(params) -> pose dict. Samples every `step` frames plus every key frame,
    keyed with linear ease, so planted feet and hand targets hold between keys too.
    """
    keys = sorted([tuple(k) for k in keys], key=lambda k: k[0])
    full = []
    cur = {}
    for k in keys:
        cur = {**cur, **k[1]}
        full.append((k[0], dict(cur), k[2] if len(k) > 2 else "sine"))
    if loop:
        if full[-1][0] != length:
            full.append((length, dict(full[0][1]), "sine"))
        else:
            full[-1] = (length, dict(full[0][1]), full[-1][2])
    assert full[0][0] == 0 and full[-1][0] == length, (name, full[0][0], full[-1][0])

    def params_at(f):
        for (f0, p0, e0), (f1, p1, _) in zip(full[:-1], full[1:]):
            if f0 <= f <= f1:
                t = 0.0 if f1 == f0 else (f - f0) / (f1 - f0)
                te = EASES[e0](t)
                return {k: _lerp_val(p0[k], p1.get(k, p0[k]), te) for k in p0}
        return dict(full[-1][1])

    frames = sorted(set(range(0, length, step)) | {length} | {k[0] for k in full})
    act = ns.new_action(sk.arm, name, 0, length, loop=loop, fps=FPS)
    poses = {f: fn(params_at(f)) for f in frames}
    if loop:
        poses[length] = poses[0]
    loc_bones = set()
    for pz in poses.values():
        for b, spec in pz.items():
            if _split(spec)[1] is not None:
                loc_bones.add(b)
    for f in frames:
        key_pose(sk, f, poses[f], ease="LINEAR", bones=sk.bones(), loc_bones=loc_bones)
    fix_quat_signs(act)
    return act


def blend(pose, bones, w, base=None):
    """Slerp the given bones' rotations from `base` (default rest) toward the pose by w."""
    base = base or {}
    for b in bones:
        rot, loc = _split(pose.get(b))
        R = as_mat(rot).to_quaternion()
        B = as_mat(_split(base.get(b))[0]).to_quaternion()
        pose[b] = (B.slerp(R, max(0.0, min(1.0, w))).to_matrix(), loc)
    return pose


def fix_quat_signs(act):
    """Keep consecutive quaternion keys in the same hemisphere so Blender's per-channel
    interpolation (previews) never takes the long way round. Rotations are unchanged."""
    fcs = ns._action_fcurves(act)
    by_bone = {}
    for fc in fcs:
        if fc.data_path.endswith("rotation_quaternion"):
            by_bone.setdefault(fc.data_path, {})[fc.array_index] = fc
    for path, comps in by_bone.items():
        if len(comps) != 4:
            continue
        n = len(comps[0].keyframe_points)
        prev = None
        for i in range(n):
            q = [comps[c].keyframe_points[i].co.y for c in range(4)]
            if prev is not None and sum(a * b for a, b in zip(prev, q)) < 0:
                for c in range(4):
                    kp = comps[c].keyframe_points[i]
                    kp.co.y = -kp.co.y
                    kp.handle_left.y = -kp.handle_left.y
                    kp.handle_right.y = -kp.handle_right.y
                q = [-x for x in q]
            prev = q
        for c in range(4):
            comps[c].update()


def finalize(sk, acts):
    """Make every clip explicit about translations: any bone translated in ANY clip of the
    rig gets zero-location keys (at its rotation key frames) in clips that don't move it.
    Without this, a clip that never keys a bone's location inherits whatever the previous
    clip left (in Blender), and the exported keys carry no position for that bone."""
    loc_bones = set()
    for act in acts:
        for fc in ns._action_fcurves(act):
            if fc.data_path.endswith(".location"):
                loc_bones.add(fc.data_path.split('"')[1])
    arm = sk.arm
    for act in acts:
        have = {fc.data_path.split('"')[1] for fc in ns._action_fcurves(act) if fc.data_path.endswith(".location")}
        missing = loc_bones - have
        if not missing:
            continue
        set_action(arm, act)
        for b in missing:
            frames = {}
            for fc in ns._action_fcurves(act):
                if fc.data_path == f'pose.bones["{b}"].rotation_quaternion':
                    for kp in fc.keyframe_points:
                        frames[int(round(kp.co.x))] = (kp.interpolation, kp.easing)
            if not frames:
                frames = {act["ns_start"]: ("SINE", "EASE_IN_OUT"), act["ns_end"]: ("SINE", "EASE_IN_OUT")}
            pb = arm.pose.bones[b]
            for f, (ip, ez) in sorted(frames.items()):
                pb.location = (0.0, 0.0, 0.0)
                pb.keyframe_insert("location", frame=f)
            for fc in ns._action_fcurves(act):
                if fc.data_path == f'pose.bones["{b}"].location':
                    for kp in fc.keyframe_points:
                        ip, ez = frames.get(int(round(kp.co.x)), ("SINE", "EASE_IN_OUT"))
                        kp.interpolation = ip
                        kp.easing = ez
    return sorted(loc_bones)


def rescale(sk, acts, S):
    """Uniformly scale a finished rig about the model origin: every part's mesh, the bone
    rest positions and every location key of every clip (rotations are scale-free, so the
    motion is identical, just smaller; no-slide speeds scale by S too)."""
    arm = sk.arm
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    objs = [o for o in ns._tagged_objects() if o.parent == arm]     # only this rig's parts
    bone_of = {}
    for o in objs:
        bone_of[o.name] = o["ns_bone"]
        mw = o.matrix_world.copy()
        o.parent = None
        o.parent_type = "OBJECT"
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(Matrix.Scale(S, 4) @ mw)
        o.data.update()
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for eb in arm.data.edit_bones:
        L = (eb.tail - eb.head).length * S
        h = eb.head * S
        eb.head = h
        eb.tail = h + Vector((0.0, L, 0.0))
        eb.roll = 0.0
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in objs:
        ns.bind(o, arm, bone_of[o.name])
    for act in acts:
        for fc in ns._action_fcurves(act):
            if fc.data_path.endswith(".location"):
                for kp in fc.keyframe_points:
                    kp.co.y *= S
                    kp.handle_left.y *= S
                    kp.handle_right.y *= S
                fc.update()
    sk.head = {b: h * S for b, h in sk.head.items()}
    arm.data.pose_position = "POSE"
    bpy.context.view_layer.update()


def set_action(arm, act):
    arm.animation_data.action = act
    if hasattr(arm.animation_data, "action_slot") and len(getattr(act, "slots", [])) > 0:
        arm.animation_data.action_slot = act.slots[0]


def rest_pose(arm):
    """Leave the armature showing its rest pose (for the standard preview)."""
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()


# ======================================================================================
# Humanoid posing helpers (bone names: Hips, Torso, Head, UpperArm/Forearm/Hand + L/R,
# Thigh/Shin/Foot + L/R, optional Coat/CoatLower + L/R)
# ======================================================================================

ARM = {s: ("UpperArm" + s, "Forearm" + s, "Hand" + s) for s in ("L", "R")}
LEG = {s: ("Thigh" + s, "Shin" + s, "Foot" + s) for s in ("L", "R")}
SIDE = {"L": 1, "R": -1}


def plant(sk, pose, feet=None):
    """IK both legs: each ankle to its target (default: rest) with the foot at a world
    rotation (default flat). feet = {"L": (pos,) or (pos, rot)}."""
    feet = feet or {}
    for s, side in SIDE.items():
        th, sh, ft = LEG[s]
        spec = feet.get(s)
        T = Vector(spec[0]) if spec else sk.head[ft].copy()
        Rf = as_mat(spec[1]) if (spec and len(spec) > 1) else I3
        solve_limb(sk, pose, th, sh, sk.head[ft], T, pole=Vector((0.12 * side, -1, 0)), f0=(0, 1, 0),
                   end=ft, end_world=Rf)


def reach_l(sk, pose, s, grip_rest, target, local, pole):
    """Hand reach with the wrist at a LOCAL rotation (relative to the forearm)."""
    up, fo, ha = ARM[s]
    return reach_rel(sk, pose, up, fo, ha, grip_rest, target, local, Vector(pole), f0=(0, -1, 0))


def reach_w(sk, pose, s, grip_rest, target, world, pole):
    """Hand reach with the hand at a WORLD rotation."""
    up, fo, ha = ARM[s]
    Rh = as_mat(world)
    wr = sk.head[ha]
    wt = Vector(target) - Rh @ (Vector(grip_rest) - wr)
    return solve_limb(sk, pose, up, fo, wr, wt, Vector(pole), f0=(0, -1, 0), end=ha, end_world=Rh)


def arm_mix(pose, bones, w, solve):
    """Solve a limb (IK) and blend it in by weight w from its current (FK/rest) rotation."""
    if w <= 1e-4:
        return
    base = {b: pose.get(b) for b in bones}
    solve(pose)
    blend(pose, bones, w, base)


def palm_world(sk, pose, s):
    """(palm normal, finger direction) of a hand in world space - for checking wrist rolls."""
    W = sk.fk(pose)
    R = W["Hand" + s][0]
    return (tuple(round(c, 2) for c in R @ Vector((-SIDE[s], 0, 0))),
            tuple(round(c, 2) for c in R @ Vector((0, 0, -1))))


def coat_follow(pose, k=0.5, hips_pitch=0.0, lower_k=0.35, cap=10.0):
    """Coat skirt halves follow the thighs (k) and hang plumb against the hips' pitch; the
    lower halves (if the rig has them) counter-swing a little like cloth hanging."""
    for s in ("L", "R"):
        th = _split(pose.get("Thigh" + s))[0]
        p = math.degrees(as_mat(th).to_euler("XYZ").x) if th is not None else 0.0
        up = k * min(p, cap) - 0.85 * hips_pitch
        pose["Coat" + s] = (rot_deg(up, 0, 0), None)
        pose["CoatLower" + s] = (rot_deg(-lower_k * (up + hips_pitch), 0, 0), None)


def merge_keys(keys):
    """Combine (frame, pose, ease, dir) entries; entries sharing a frame merge their pose
    dicts (the first entry's ease wins). Frames listing few bones key only those bones."""
    merged = {}
    for k in keys:
        f = k[0]
        if f in merged:
            merged[f] = (f, {**merged[f][1], **k[1]}) + tuple(merged[f][2:])
        else:
            merged[f] = tuple(k)
    return [merged[f] for f in sorted(merged)]


def set_world(sk, pose, bone, R_world, pos_world):
    """Set a bone's local rotation AND loc so it ends at a world rotation / head position
    (used to carry a torn-off piece in a hand)."""
    W = sk.fk(pose)
    p = sk.parent[bone]
    Rp, hp = W[p] if p else (I3, V0)
    R_loc = Rp.inverted() @ as_mat(R_world)
    rest_off = sk.head[bone] - (sk.head[p] if p else V0)
    if p is None:
        loc = Vector(pos_world) - sk.head[bone]
    else:
        loc = Rp.inverted() @ (Vector(pos_world) - hp) - rest_off
    pose[bone] = (R_loc, tuple(loc))


# ======================================================================================
# Biped locomotion (no foot slide)
# ======================================================================================

def smooth01(s):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, s)))


def biped_cycle(sk, legs, *, speed, period, duty=0.6, lift=0.35, lift_peak=0.5,
                hips="Hips", hip_height=None, bob=0.06, sway=0.0, roll=3.0, twist=6.0,
                lean=0.0, extra=None, toe_off=18.0, heel_strike=-12.0, smooth_passes=3):
    """Return fn(frame)->pose for an in-place biped cycle with planted feet.

    legs: [dict(thigh=, shin=, foot=, ankle=(x,y,z) rest ankle, sole=[rest sole points],
                 phase=0 or 0.5, side=+1 L / -1 R)]
    speed  studs/s the clip is authored for (clipSpeedRef): planted feet move back exactly
           this fast, so playback at that ground speed has zero slide.
    period cycle length (s, two steps). duty = fraction of the cycle each foot is planted.
    bob    hips vertical oscillation amplitude (+ walk vault: high at mid-stance;
           - run: low at mid-stance). Hips are lowered further where needed so the planted
           leg can reach (keeps a little knee bend).
    extra(phase, pose, W) adds upper-body motion (arms, torso, head) to the pose dict.
    """
    n = max(8, int(round(period * FPS)))
    stride = speed * duty * period            # foot travel while planted
    h0 = sk.head[hips].z if hip_height is None else hip_height
    hips_rest = sk.head[hips]

    hs_frac, to_frac = 0.15, 0.75             # heel-roll / toe-roll portions of stance

    def stance_ankle(s, leg):
        """Ankle + foot pitch during stance (s in 0..1). The contact point (heel while the
        foot rolls down, the whole sole when flat, the toe while the heel lifts) moves back
        at exactly `speed`, i.e. it is fixed on the ground."""
        A0 = Vector(leg["ankle"])
        heel, toe = Vector(leg["sole"][0]), Vector(leg["sole"][1])
        yflat = A0.y - stride / 2 + stride * s
        if s < hs_frac:
            pitch = heel_strike * (1 - smooth01(s / hs_frac))
            piv = heel
        elif s > to_frac:
            pitch = toe_off * smooth01((s - to_frac) / (1 - to_frac))
            piv = toe
        else:
            return Vector((A0.x, yflat, A0.z)), 0.0
        pw = Vector((piv.x, yflat + (piv.y - A0.y), piv.z))
        return pw - rot_deg(pitch, 0, 0) @ (piv - A0), pitch

    def hermite(p0, m0, p1, m1, t):
        t2, t3 = t * t, t * t * t
        return (2 * t3 - 3 * t2 + 1) * p0 + (t3 - 2 * t2 + t) * m0 + (-2 * t3 + 3 * t2) * p1 + (t3 - t2) * m1

    def foot_state(u, leg):
        u = (u - leg["phase"]) % 1.0
        if u < duty:
            a, pitch = stance_ankle(u / duty, leg)
            return a, pitch, True
        s = (u - duty) / (1 - duty)
        a0, p0 = stance_ankle(1.0, leg)
        a1, p1 = stance_ankle(0.0, leg)
        # tangent = stance velocity (body frame) so the foot meets the ground at ground speed 0
        m = stride * (1 - duty) / duty
        y = hermite(a0.y, m, a1.y, m, s)
        if s < lift_peak:
            k = math.sin(0.5 * math.pi * s / lift_peak)
        else:
            k = math.cos(0.5 * math.pi * (s - lift_peak) / (1 - lift_peak))
        z = a0.z + (a1.z - a0.z) * s + lift * k
        pitch = p0 + (p1 - p0) * smooth01(s)
        return Vector((a0.x, y, z)), pitch, False

    def sole_lift(leg, pitch):
        R = rot_deg(pitch, 0, 0)
        a = Vector(leg["ankle"])
        lo = min((a + R @ (Vector(p) - a)).z for p in leg["sole"])
        floor = min(Vector(p).z for p in leg["sole"])
        return max(0.0, floor - lo)

    # pass 1: hips height per frame from the reach constraint
    raw = []
    for f in range(n):
        u = f / n
        h = h0 + bob * math.cos(4 * math.pi * (u - duty / 2))
        pose = {hips: (None, (0, 0, h - hips_rest.z))}
        W = sk.fk(pose)
        need = 0.0
        for leg in legs:
            T, pitch, planted = foot_state(u, leg)
            if not planted:
                T.z += sole_lift(leg, pitch)
            S = W[leg["thigh"]][1]
            a = (sk.head[leg["shin"]] - sk.head[leg["thigh"]]).length
            b = (Vector(leg["ankle"]) - sk.head[leg["shin"]]).length
            maxr = (a + b) * 0.975
            horiz = math.hypot(S.x - T.x, S.y - T.y)
            if horiz < maxr:
                zmax = T.z + math.sqrt(maxr * maxr - horiz * horiz)
                need = max(need, S.z - zmax)
        raw.append(h - need)
    hs = raw[:]
    for _ in range(smooth_passes):           # circular smoothing keeps the loop seamless
        hs = [(hs[i - 1] + 2 * hs[i] + hs[(i + 1) % n]) / 4 for i in range(n)]

    def fn(frame):
        f = frame % n
        u = f / n
        h = hs[f]
        lat = sway * math.sin(2 * math.pi * u)               # hips shift over the stance foot
        r_roll = roll * math.sin(2 * math.pi * u)
        r_twist = -twist * math.cos(2 * math.pi * u)         # leading hip forward
        pose = {hips: (rot_deg(lean, -r_roll, r_twist), (lat, 0, h - hips_rest.z))}
        W = sk.fk(pose)
        for leg in legs:
            T, pitch, planted = foot_state(u, leg)
            if not planted:
                T.z += sole_lift(leg, pitch)
            solve_limb(sk, pose, leg["thigh"], leg["shin"], leg["ankle"], T,
                       pole=Vector((0.12 * leg["side"], -1, 0)), f0=(0, 1, 0))
            W = sk.fk(pose)
            pose[leg["foot"]] = (sk.local_rot(W, leg["foot"], rot_deg(pitch, 0, 0)), None)
        if extra:
            extra(u, pose, sk.fk(pose))
        return pose

    fn.frames = n
    fn.heights = hs
    return fn


# ======================================================================================
# Checks
# ======================================================================================

def _eval_bone_mats(arm, act, frame):
    set_action(arm, act)
    bpy.context.scene.frame_set(frame)
    return {pb.name: pb.matrix.copy() for pb in arm.pose.bones}


def _key_frames(act):
    return sorted({int(round(kp.co.x)) for fc in ns._action_fcurves(act) for kp in fc.keyframe_points})


def check_clip(sk, act, *, verbose=True):
    """Seam check (loops), largest key-to-key joint rotation (flip risk), largest jump in the
    exported Roblox Euler angles between consecutive keys, and lowest point vs the floor."""
    arm = sk.arm
    arm.data.pose_position = "POSE"
    frames = _key_frames(act)
    start, end = act["ns_start"], act["ns_end"]
    out = {"clip": act.name}
    prev = None
    max_step = (0.0, None, None)
    max_eu = (0.0, None, None)
    for f in frames:
        mats = _eval_bone_mats(arm, act, f)
        cur = {}
        for b in sk.order:
            pb = arm.pose.bones[b]
            L = pb.matrix_basis.to_3x3()
            R = ns.M_B2R @ L @ ns.M_B2R
            e = R.to_euler("ZYX")
            cur[b] = (L.to_quaternion(), (e.x, e.y, e.z))
        if prev is not None:
            for b in sk.order:
                ang = math.degrees(prev[b][0].rotation_difference(cur[b][0]).angle)
                ang = min(ang, 360.0 - ang)          # q and -q are the same rotation
                if ang > max_step[0]:
                    max_step = (ang, b, f)
                jump = max(abs(x - y) for x, y in zip(prev[b][1], cur[b][1]))
                jump = math.degrees(jump)
                if jump > 180.0:
                    out.setdefault("euler_wraps", []).append((b, f))
                if jump > max_eu[0]:
                    max_eu = (jump, b, f)
        prev = cur
    out["max_key_step_deg"] = (round(max_step[0], 1), max_step[1], max_step[2])
    out["max_euler_jump_deg"] = (round(max_eu[0], 1), max_eu[1], max_eu[2])
    if act["ns_loop"]:
        a = _eval_bone_mats(arm, act, start)
        b = _eval_bone_mats(arm, act, end)
        out["seam_err"] = round(max((a[k].translation - b[k].translation).length +
                                    a[k].to_quaternion().rotation_difference(b[k].to_quaternion()).angle
                                    for k in a), 5)
    bpy.context.scene.frame_set(0)
    if verbose:
        print(f"  [check] {act.name:14s} loop={bool(act['ns_loop'])} len={(end - start) / FPS:.2f}s "
              f"keys={len(frames)} maxStep={out['max_key_step_deg']} eulerJump={out['max_euler_jump_deg']}"
              + (f" seam={out['seam_err']}" if 'seam_err' in out else "")
              + (f" EULER-WRAPS={out['euler_wraps']}" if 'euler_wraps' in out else ""))
    return out


def foot_slide(sk, act, foot_bone, sole_rest, speed, contact_z=0.06, z_floor=0.0, axis=-1):
    """Max slide (studs/s) of a sole point while it is on the floor, with the body moving
    forward (-Y) at `speed`. axis=-1: forward is -Y. Returns (max_slide, contact_frames)."""
    arm = sk.arm
    start, end = act["ns_start"], act["ns_end"]
    pts = []
    for f in range(start, end + 1):
        set_action(arm, act)
        bpy.context.scene.frame_set(f)
        pb = arm.pose.bones[foot_bone]
        M = arm.matrix_world @ pb.matrix @ arm.data.bones[foot_bone].matrix_local.inverted()
        p = M @ Vector(sole_rest)
        t = (f - start) / FPS
        pts.append((f, p.y + axis * speed * t, p.z))
    worst = 0.0
    nc = 0
    for (f0, y0, z0), (f1, y1, z1) in zip(pts[:-1], pts[1:]):
        if abs(z0 - z_floor) < contact_z and abs(z1 - z_floor) < contact_z:
            nc += 1
            worst = max(worst, abs(y1 - y0) * FPS)
    bpy.context.scene.frame_set(0)
    return round(worst, 3), nc


def lowest_point(sk, act, frames=None, skip=("Drip",)):
    """Lowest world z over the clip's frames (default: every 2nd), from actual vertex
    positions (bounding boxes of rotated parts overstate it). Returns (z, part, frame).
    Parts whose name starts with a `skip` prefix (falling drops) are ignored."""
    arm = sk.arm
    arm.data.pose_position = "POSE"
    set_action(arm, act)
    start, end = act["ns_start"], act["ns_end"]
    frames = frames or list(range(start, end + 1, 2))
    objs = [o for o in ns._tagged_objects() if not o.name.startswith(skip)]
    best = (1e9, None, None)
    for f in frames:
        bpy.context.scene.frame_set(f)
        for o in objs:
            mw = o.matrix_world
            z = min((mw @ v.co).z for v in o.data.vertices)
            if z < best[0]:
                best = (round(z, 3), o.name, f)
    bpy.context.scene.frame_set(0)
    return best


# ======================================================================================
# Rendering
# ======================================================================================

def _ref_capsule(loc, height=5.0, name="RefCapsule5"):
    """5-stud reference figure (R15-ish proportions: body capsule + head ball)."""
    x, y, z = loc
    body = capsule((x, y, z + 0.55), (x, y, z + 3.55), 0.55, 0.62, verts=12, name=name + "B")
    head = ns.sphere(0.62, loc=(x, y, z + height - 0.62), segs=14, rings=8, name=name + "H")
    ns.apply_all(head)
    o = ns.join([body, head], name)
    o.data.materials.clear()
    o.data.materials.append(ns.material("#9A9AA6"))
    return o


def _cleanup(extra):
    names = [o.name for o in extra]
    ns._clear_rig()
    for n in names:
        o = bpy.data.objects.get(n)
        if o is not None:
            bpy.data.objects.remove(o, do_unlink=True)


def pose_strip(sk, act, frames, name, res=320, samples=16, yaw=-60.0, pitch=12.0,
               floor=True, ceiling_z=None, ref=False, label=True, fov=30.0):
    """Render the rig at several frames side by side, framed on the union of all frames."""
    from PIL import Image, ImageDraw
    arm = sk.arm
    arm.data.pose_position = "POSE"
    set_action(arm, act)
    os.makedirs(PREV_DIR, exist_ok=True)
    objs = ns._tagged_objects()
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for f in frames:
        bpy.context.scene.frame_set(f)
        l, h = ns.bbox_world(objs)
        lo = Vector(map(min, lo, l))
        hi = Vector(map(max, hi, h))
    extra = []
    if ref:
        r = _ref_capsule((lo.x - 1.2, (lo.y + hi.y) / 2, 0.0), name="RefCube5")
        extra.append(r)
        lo.x -= 2.0
        lo.z = min(lo.z, 0.0)
        hi.z = max(hi.z, 5.0)
    pad = Vector((0.08, 0.08, 0.05)) * max((hi - lo).length, 1)
    flo, fhi = lo - pad, hi + pad
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=max((fhi - flo).length * 5, 6),
                                         location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0))
        fl = bpy.context.active_object
        fl.name = "Floor"
        fl.data.materials.append(ns.material("#3A3B42"))
        extra.append(fl)
    if ceiling_z is not None:
        bpy.ops.mesh.primitive_plane_add(size=max((fhi - flo).length * 3, 6),
                                         location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, ceiling_z + 0.002))
        cl = bpy.context.active_object
        cl.name = "FloorCeil"
        cl.rotation_euler = (math.pi, 0, 0)
        cl.data.materials.append(ns.material("#5A6670"))
        extra.append(cl)
    ns._setup_render(res, samples, transparent=False)
    if ceiling_z is not None:      # keep the camera under the ceiling plane
        c0 = (flo + fhi) / 2
        d0 = max((fhi - flo).length / 2, 0.05) * 1.0 / math.sin(math.radians(fov) / 2)
        lim = (ceiling_z - 0.4 - c0.z) / d0
        if lim < 1.0:
            pitch = min(pitch, math.degrees(math.asin(max(-0.95, lim))))
    cam, ctr, dist = ns._camera_fit(flo, fhi, yaw, pitch, fov_deg=fov, margin=1.0)
    k = math.radians(yaw)
    ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * dist, 60 * dist ** 2 / 9,
              size=dist * 0.6, target=ctr)
    ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3)) * dist, 25 * dist ** 2 / 9,
              size=dist, target=ctr)
    ns._light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.6)) * dist, 30 * dist ** 2 / 9,
              size=dist * 0.4, target=ctr)
    paths = []
    for f in frames:
        bpy.context.scene.frame_set(f)
        p = os.path.join(PREV_DIR, f"_{name}_f{f}.png")
        bpy.context.scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        paths.append((f, p))
    _cleanup(extra)
    ims = []
    for f, p in paths:
        im = Image.open(p).convert("RGB")
        if label:
            d = ImageDraw.Draw(im)
            d.rectangle((0, 0, res, 16), fill=(20, 20, 24))
            d.text((4, 2), f"{act.name}  f{f}  t={(f - act['ns_start']) / FPS:.2f}s", fill=(235, 235, 235))
        ims.append(im)
        os.remove(p)
    combo = Image.new("RGB", (res * len(ims), res))
    for i, im in enumerate(ims):
        combo.paste(im, (i * res, 0))
    out = os.path.join(PREV_DIR, f"{name}_strip.png")
    combo.save(out)
    bpy.context.scene.frame_set(0)
    return out


def quick_view(name, yaw=-35, pitch=15, res=400, samples=12, ref=True, frame=None, act=None, sk=None,
               ceiling_z=None):
    """Fast single-angle look (iteration aid): optional pose frame and 5-stud reference."""
    if sk is not None and act is not None:
        sk.arm.data.pose_position = "POSE"
        set_action(sk.arm, act)
        bpy.context.scene.frame_set(frame or 0)
    from PIL import Image  # noqa: F401
    objs = ns._tagged_objects()
    lo, hi = ns.bbox_world(objs)
    extra = []
    zoom = os.environ.get("NS_ZOOM")          # "zmin,zmax[,yaw]" frames only that height band
    if zoom:
        zz = [float(t) for t in zoom.split(",")]
        lo = Vector((lo.x, lo.y, zz[0]))
        hi = Vector((hi.x, hi.y, zz[1]))
        ref = False
        if len(zz) > 2:
            yaw = zz[2]
    if ref:
        extra.append(_ref_capsule((lo.x - 1.4, (lo.y + hi.y) / 2, 0.0), name="RefCube5"))
        lo = Vector((lo.x - 2.2, lo.y, min(lo.z, 0)))
        hi = Vector((hi.x, hi.y, max(hi.z, 5)))
    bpy.ops.mesh.primitive_plane_add(size=max((hi - lo).length * 5, 6), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0))
    fl = bpy.context.active_object
    fl.name = "Floor"
    fl.data.materials.append(ns.material("#3A3B42"))
    extra.append(fl)
    if ceiling_z is not None:
        bpy.ops.mesh.primitive_plane_add(size=(hi - lo).length * 3, location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, ceiling_z + 0.002))
        cl = bpy.context.active_object
        cl.name = "FloorCeil"
        cl.rotation_euler = (math.pi, 0, 0)
        cl.data.materials.append(ns.material("#5A6670"))
        extra.append(cl)
    ns._setup_render(res, samples, transparent=False)
    cam, ctr, dist = ns._camera_fit(lo, hi, yaw, pitch, margin=1.05)
    k = math.radians(yaw)
    ns._light("Key", "AREA", ctr + Vector((math.sin(k - 0.8), -math.cos(k - 0.8), 0.9)) * dist, 60 * dist ** 2 / 9, size=dist * 0.6, target=ctr)
    ns._light("Fill", "AREA", ctr + Vector((math.sin(k + 1.2), -math.cos(k + 1.2), 0.3)) * dist, 22 * dist ** 2 / 9, size=dist, target=ctr)
    ns._light("Rim", "AREA", ctr + Vector((-math.sin(k), math.cos(k), 0.7)) * dist, 35 * dist ** 2 / 9, size=dist * 0.4, target=ctr)
    os.makedirs(PREV_DIR, exist_ok=True)
    p = os.path.join(PREV_DIR, f"_quick_{name}.png")
    bpy.context.scene.render.filepath = p
    bpy.ops.render.render(write_still=True)
    _cleanup(extra)
    bpy.context.scene.frame_set(0)
    return p


# ======================================================================================
# Main entry
# ======================================================================================

def print_parts(asset):
    dg = bpy.context.evaluated_depsgraph_get()
    tot = 0
    for o in sorted(ns._tagged_objects(), key=lambda o: o.name):
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        n = len(me.loop_triangles)
        tot += n
        print(f"  [{asset}] {o.name:22s} {n:5d} tris  bone={o.get('ns_bone')} role={o.get('ns_role')} "
              f"mat={o.get('ns_material')} tr={o.get('ns_transparency')}")
        o.evaluated_get(dg).to_mesh_clear()
    print(f"  [{asset}] total {tot}")


def run(build, asset, rig_name, strips=None, **export_kw):
    """Build -> preview -> (export) -> checks -> pose strips -> (anim export).

    strips: {clip_name: dict(frames=[...], **pose_strip kwargs)}.
    Env: NS_EXPORT=1 export mesh + anim; NS_STRIPS=none|all|Clip1,Clip2 (default all);
         NS_PREVIEW=0 skips the standard two-angle preview; NS_PARTS=1 lists parts;
         NS_QUICK=1 renders only a quick single view (iteration).
    """
    _build = build

    def build():
        o = _build()
        if o and "skel" in o:
            print("  [finalize] loc bones:", finalize(o["skel"], o["actions"]))
        return o
    if os.environ.get("NS_QUICK") == "1":
        ns.reset()
        out = build()
        print(f"[{asset}] triangles: {ns.tri_count()}")
        if os.environ.get("NS_PARTS") == "1":
            print_parts(asset)
        print(f"[{asset}] quick:", quick_view(asset, ceiling_z=out.get("ceiling_z")))
        return out
    if os.environ.get("NS_PREVIEW") == "0":
        ns.reset()
        out = build() or {}
        print(f"[{asset}] triangles: {ns.tri_count()}")
        if os.environ.get("NS_EXPORT") == "1":
            kw = dict(export_kw)
            kw.update(out.get("export", {}))
            doc = ns.export_asset(asset, BATCH, group=GROUP, **kw)
            print(f"[{asset}] exported: {len(doc['parts'])} parts, {doc['tris']} tris, size {doc['size']}")
    else:
        out = ns.run_main(build, asset, BATCH, GROUP, **export_kw)
    if os.environ.get("NS_PARTS") == "1":
        print_parts(asset)
    sk = out["skel"]
    acts = out["actions"]
    print(f"[{asset}] bones ({len(sk.order)}): {', '.join(sk.order)}")
    for a in acts:
        check_clip(sk, a)
    for fn in out.get("checks", []):
        fn()
    sel = os.environ.get("NS_STRIPS", "all")
    if sel != "none":
        want = None if sel == "all" else set(sel.split(","))
        for a in acts:
            if want is not None and a.name not in want:
                continue
            spec = dict((strips or {}).get(a.name, {}))
            frames = spec.pop("frames", None) or sorted({0, a["ns_end"] // 4, a["ns_end"] // 2, 3 * a["ns_end"] // 4})
            print(f"[{asset}] strip:", pose_strip(sk, a, frames, f"{rig_name}_{a.name}", **spec))
    if os.environ.get("NS_EXPORT") == "1":
        sk.arm.data.pose_position = "POSE"
        print(f"[{asset}] anim:", ns.export_animations(sk.arm, rig_name, acts))
    return out
