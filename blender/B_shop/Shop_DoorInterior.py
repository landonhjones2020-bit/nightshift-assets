"""Shop_DoorInterior — solid wood swing door with a porthole (fits Shop_WallDoorway).

Wood leaf with raised panels, chrome porthole (glass role "glass"), stainless kick plate,
push plate and hinge knuckles, plus a blank name plate on both faces (role sign_panel:
"OFFICE", "RESTROOM", "BASEMENT", "STAFF ONLY" via SurfaceGui). Leaf role "door_leaf" so
the basement door can be recoloured to grey steel.
Pivot = hinge line, bottom (leaf extends toward +X). Place at the doorway's Socket_DoorHinge.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L0, L1 = 0.05, 4.95
T = 0.26
Z0, Z1 = 0.03, 7.95
PX, PZ, PR = 2.5, 5.55, 0.62     # porthole centre / radius
DOOR = "#7A4A30"


def harden_flat_faces(obj, min_area=0.5):
    """Flat-shade the big faces (door faces, panel fronts): mark their edges sharp so the soft bevels no longer
    tilt their corner normals. With the porthole cut-out the door face is a fan of long triangles, and the
    tilted corner normals shaded it as a diagonal 'X' (it read as a bent door). The exporter keeps sharp edges."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for f in bm.faces:
        if f.calc_area() >= min_area:
            for e in f.edges:
                e.smooth = False
    bm.to_mesh(obj.data)
    bm.free()


def build():
    w = L1 - L0
    cx = (L0 + L1) / 2
    leaf = ns.box((w, T, Z1 - Z0), loc=(cx, 0, (Z0 + Z1) / 2), bevel=0.0)
    ns.boolean(leaf, ns.cyl(PR, 2, loc=(PX, 0, PZ), rot=(90, 0, 0), verts=24, bevel=0.0))
    ns.bevel(leaf, width=0.05, segments=2)
    # raised panels (both faces): one under the porthole
    panels = []
    for sy in (-1, 1):
        p = ns.box((3.2, 0.06, 2.3), loc=(cx - 0.25, sy * (T / 2 + 0.02), 2.75), bevel=0.04, segments=2)
        panels.append(p)
    lf = C.part([leaf] + panels, "Leaf", DOOR, "Wood", recolor="door_leaf", can_collide=True, smooth_angle=40)
    harden_flat_faces(lf)

    hw = []
    for sy in (-1, 1):
        f = sy * (T / 2)
        # kick plate
        hw.append(ns.box((w - 0.2, 0.03, 1.2), loc=(cx, f + sy * 0.015, Z0 + 0.62), bevel=0.012, segments=1))
        # push plate on the latch side
        hw.append(ns.box((0.5, 0.03, 1.6), loc=(L1 - 0.55, f + sy * 0.015, 4.0), bevel=0.02, segments=1))
        # porthole ring (chunky chrome torus-like ring)
        r = ns.ring(PR - 0.04, PR + 0.17, 0.08, loc=(0, 0, 0), verts=24)
        r.rotation_euler = (1.5708, 0, 0)
        r.location = (PX, f + sy * 0.04, PZ)
        ns.bevel(r, width=0.025, segments=2)
        hw.append(r)
    # porthole lining through the leaf
    lin = ns.cyl(PR + 0.005, T + 0.02, loc=(PX, 0, PZ), rot=(90, 0, 0), verts=24, bevel=0.0)
    ns.boolean(lin, ns.cyl(PR - 0.05, 2, loc=(PX, 0, PZ), rot=(90, 0, 0), verts=24, bevel=0.0))
    hw.append(lin)
    # hinge knuckles
    for z in (1.0, 4.0, 7.0):
        hw.append(ns.cyl(0.09, 0.55, loc=(0.02, 0, z), verts=10, bevel=0.02, segments=1))
    C.part(hw, "Hardware", C.STAINLESS, "Metal", smooth_angle=45)

    glass = ns.cyl(PR - 0.03, 0.05, loc=(PX, 0, PZ), rot=(90, 0, 0), verts=24, bevel=0.0)
    ns.tag(glass, "Glass", C.GLASS, "Glass", transparency=0.5, recolor="glass", can_collide=True, cast_shadow=False)

    for sy, nm in ((-1, "SignFront"), (1, "SignBack")):
        plate = ns.box((1.7, 0.04, 0.5), loc=(PX, sy * (T / 2 + 0.03), 4.35), bevel=0.02, segments=1)
        ns.tag(plate, nm, "#22283A", recolor="sign_panel")


META = {"leaf": True, "leaf_size": [4.9, 7.92, T], "hinge": "pivot (x=0 edge, bottom, leaf centre plane)",
        "fits": "Shop_WallDoorway Socket_DoorHinge", "open_axis": "pivot Y (yaw)",
        "surfaces": [{"part": "SignFront", "face": "Front"}, {"part": "SignBack", "face": "Back"}],
        "variants": {"Steel": {"door_leaf": "#8E969D"}}}

if __name__ == "__main__":
    C.run(build, "Shop_DoorInterior", pivot=(0, 0, 0), meta=META,
          sockets={"Handle": ((L1 - 0.55, 0, 4.0), 0.0)})
