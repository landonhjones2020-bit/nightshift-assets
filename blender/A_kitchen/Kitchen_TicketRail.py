"""Kitchen_TicketRail — wall-mounted order rail: 4 ticket clips + the pinned creature slot.

A 4.5-long stainless channel rail on two wall standoffs with rubber end caps. Four black
spring clips hang on the rail for normal tickets; the pinned 5th slot (right end, +X) is set
apart by a divider and has a bigger red-orange clip with a pushpin (role pinned_clip), so it
reads differently at a glance. Tickets are spawned by the client (none are modelled).
Modelled with its back on the wall plane (Blender y = 0), front -Y.

Sockets Ticket1..Ticket4 (Ticket1 at -X) and Pinned = top centre of a hanging ticket,
just under the clip jaws, yaw 0 (ticket faces -Y). Meta ticket_size = suggested ticket
width x height; mount height is the map's call (suggested_bottom).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
L = 4.5
RAIL_Y = -0.28                   # rail centre (standoffs bridge to the wall)
RAIL_Z = 0.7                     # rail centre height above the asset bottom
RAIL_H = 0.34                    # flat-faced bar: 0.34 tall x 0.16 deep
TICKET_W, TICKET_H = 0.8, 1.15
XS = [-1.86, -0.96, -0.06, 0.84]
PIN_X = 1.8


def clip(x, big=False):
    """Spring clip hanging under the rail. Returns (body objs, lever objs)."""
    s = 1.2 if big else 1.0
    w, h = 0.38 * s, 0.26 * s
    jaw_z = RAIL_Z - RAIL_H / 2 - 0.06 - h / 2
    hook = ns.box((0.14 * s, 0.12, 0.16), loc=(x, RAIL_Y, RAIL_Z - RAIL_H / 2 - 0.02), bevel=0.03, segments=1)
    jaw = ns.box((w, 0.15, h), loc=(x, RAIL_Y - 0.01, jaw_z), bevel=0.05, segments=1)
    lever = ns.box((w * 0.72, 0.04, h * 0.8), loc=(x, RAIL_Y - 0.1, jaw_z + 0.05), rot=(-14, 0, 0), bevel=0.015, segments=1)
    return [hook, jaw], [lever], jaw_z - h / 2


def build():
    # ---- rail: rounded channel + standoffs + end caps --------------------------------
    rail = ns.box((L, 0.16, RAIL_H), loc=(0, RAIL_Y, RAIL_Z), bevel=0.06, segments=2)
    groove = ns.box((L - 0.05, 0.05, 0.03), loc=(0, RAIL_Y, RAIL_Z - RAIL_H / 2 - 0.005), bevel=0.0)
    # brand stripe stops at the divider so the pinned zone reads as its own thing
    sx0, sx1 = -L / 2 + 0.15, 1.2
    stripe = ns.box((sx1 - sx0, 0.02, 0.07), loc=((sx0 + sx1) / 2, RAIL_Y - 0.085, RAIL_Z + 0.06), bevel=0.0)
    standoffs = []
    for x in (-L / 2 + 0.55, L / 2 - 0.55):
        standoffs.append(C.rod((x, RAIL_Y, RAIL_Z), (x, 0.0, RAIL_Z), 0.07, verts=8))
        standoffs.append(ns.cyl(0.17, 0.05, loc=(x, -0.025, RAIL_Z), rot=(90, 0, 0), verts=12, bevel=0.015, segments=1))
    C.part([rail] + standoffs, "Rail", C.STAINLESS, "Metal", smooth_angle=40)
    caps = [ns.box((0.08, 0.2, RAIL_H + 0.06), loc=(sx * (L / 2 + 0.03), RAIL_Y, RAIL_Z), bevel=0.04, segments=1) for sx in (-1, 1)]
    C.part(stripe, "Stripe", C.BRAND, "SmoothPlastic")
    C.part(caps + [groove], "EndCaps", C.RUBBER, "SmoothPlastic", smooth_angle=40)

    # ---- divider before the pinned slot + its red tag ----------------------------------
    div = ns.box((0.06, 0.06, 0.6), loc=(1.33, RAIL_Y - 0.06, RAIL_Z - 0.3), bevel=0.02, segments=1)
    C.part(div, "Divider", C.STEEL_DARK, "Metal", smooth_angle=40)

    # ---- clips --------------------------------------------------------------------
    bodies, levers, tops = [], [], []
    for x in XS:
        b, lv, tz = clip(x)
        bodies += b
        levers += lv
        tops.append(tz)
    C.part(bodies, "Clips", C.BLACK, "SmoothPlastic", smooth_angle=40)
    C.part(levers, "ClipLevers", C.STEEL, "Metal", smooth_angle=40)
    pb, plv, ptz = clip(PIN_X, big=True)
    pin_head = ns.sphere(0.085, loc=(PIN_X + 0.32, RAIL_Y - 0.17, RAIL_Z + 0.02), segs=10, rings=6)
    pin_shaft = C.rod((PIN_X + 0.32, RAIL_Y - 0.17, RAIL_Z + 0.02), (PIN_X + 0.32, RAIL_Y - 0.06, RAIL_Z + 0.02), 0.02, verts=6)
    C.part(pb + plv + [pin_head], "PinnedClip", C.BRAND, "SmoothPlastic", recolor="pinned_clip", smooth_angle=45)
    C.part(pin_shaft, "PinShaft", C.STEEL, "Metal")
    tag = ns.box((0.5, 0.03, 0.2), loc=(PIN_X - 0.05, RAIL_Y - 0.09, RAIL_Z + 0.02), bevel=0.015, segments=1)
    C.part(tag, "PinnedTag", C.MUSTARD, "SmoothPlastic", recolor="pinned_tag")

    if os.environ.get("NS_DEV") == "1":   # untagged ticket placeholders (never exported)
        for x, tz in list(zip(XS, tops)) + [(PIN_X, ptz)]:
            t = ns.box((TICKET_W, 0.015, TICKET_H), loc=(x, RAIL_Y - 0.03, tz + 0.06 - TICKET_H / 2), bevel=0.0)
            t.data.materials.append(ns.material("#F6F1E6"))

    sockets = {f"Ticket{i + 1}": ((x, RAIL_Y - 0.03, tz + 0.06), 0) for i, (x, tz) in enumerate(zip(XS, tops))}
    sockets["Pinned"] = ((PIN_X, RAIL_Y - 0.03, ptz + 0.06), 0)
    meta = C.wall_meta(None, ticket_size=[TICKET_W, TICKET_H], suggested_bottom=5.2)
    return {"export": {"sockets": sockets, "meta": meta}}


if __name__ == "__main__":
    C.run(build, "Kitchen_TicketRail")
