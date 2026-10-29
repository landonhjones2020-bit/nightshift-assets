"""Kitchen_TicketPrinter — chunky thermal receipt printer for the front counter.

About a 1-stud cube: a charcoal body with a sloped clamshell lid, a dark paper slot with a
tear bar, a curl of receipt paper sticking out, a mustard feed button and a status LED.
Front faces -Y; bottom-centre pivot.

Parts with roles: PaperSlot (paper_slot), Paper (paper — the curl the client can hide/grow
while printing), Led (status_led). Extra socket PaperOut = where paper leaves the slot,
yaw 0 (paper travels up and toward -Y).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
W, D, H = 1.12, 1.15, 0.64      # body
LID_D, LID_H = 0.8, 0.3
SLOT_Y = -0.22                  # paper slot line (between lid front and body front)


def build():
    body = ns.box((W, D, H), loc=(0, 0, H / 2), bevel=0.11, segments=2)
    feet = [ns.box((0.2, 0.2, 0.05), loc=(sx * 0.38, sy * 0.4, 0.02), bevel=0.02, segments=1)
            for sx in (-1, 1) for sy in (-1, 1)]
    C.part(body, "Body", C.CHARCOAL, "SmoothPlastic", smooth_angle=40)

    # clamshell lid, slightly sloped, a step lighter so it reads as a separate lid
    lid = ns.box((W - 0.06, LID_D, LID_H), loc=(0, SLOT_Y + 0.06 + LID_D / 2, H + LID_H / 2 - 0.08), rot=(-6, 0, 0),
                 bevel=0.1, segments=2)
    C.part(lid, "Lid", "#4C5158", "SmoothPlastic", smooth_angle=40)

    # paper slot + metal tear bar
    slot = ns.box((W - 0.2, 0.09, 0.08), loc=(0, SLOT_Y + 0.02, H + 0.0), bevel=0.02, segments=1)
    C.part(slot, "PaperSlot", C.BLACK, "SmoothPlastic", recolor="paper_slot")
    tear = ns.box((W - 0.16, 0.05, 0.05), loc=(0, SLOT_Y - 0.05, H + 0.03), bevel=0.015, segments=1)
    C.part([tear] + feet, "TearBar", C.STEEL, "Metal", smooth_angle=40)

    # receipt curl: up out of the slot, then flopping forward over the front
    pts = [(SLOT_Y + 0.02, H - 0.02), (SLOT_Y + 0.01, H + 0.3), (SLOT_Y - 0.04, H + 0.46), (SLOT_Y - 0.16, H + 0.53),
           (SLOT_Y - 0.29, H + 0.5), (SLOT_Y - 0.37, H + 0.38), (-D / 2 - 0.06, H + 0.16), (-D / 2 - 0.05, H - 0.12)]
    paper = C.strip_yz(pts, 0.018, 0.64, name="Paper")
    C.part(paper, "Paper", C.PAPER, "SmoothPlastic", recolor="paper", smooth_angle=50)

    # feed button + status LED on the front face
    btn = ns.cyl(0.09, 0.06, loc=(0.38, -D / 2 - 0.01, 0.3), rot=(90, 0, 0), verts=12, bevel=0.025, segments=1)
    C.part(btn, "Button", C.MUSTARD, "SmoothPlastic")
    led = ns.cyl(0.04, 0.04, loc=(-0.38, -D / 2 - 0.005, 0.3), rot=(90, 0, 0), verts=8, bevel=0.0)
    C.part(led, "Led", "#6CFF8A", "Neon", recolor="status_led", cast_shadow=False)
    # brand stripe wrapping the lower front
    stripe = ns.box((W - 0.16, 0.02, 0.07), loc=(0, -D / 2 - 0.002, 0.13), bevel=0.0)
    C.part(stripe, "Stripe", C.BRAND, "SmoothPlastic")

    sockets = {"PaperOut": ((0, SLOT_Y + 0.02, H + 0.05), 0)}
    meta = {"paper_part": "Paper", "slot_part": "PaperSlot"}
    return {"export": {"sockets": sockets, "meta": meta}}


if __name__ == "__main__":
    C.run(build, "Kitchen_TicketPrinter")
