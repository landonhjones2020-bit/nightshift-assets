"""Shop_NowServing — wall-mounted digital order-number board (M_food batch, group "Shop").

A 3 x 1.4 black bezel box (0.27 deep) standing 0.13 off the wall on a steel bracket (wall plate +
two arms). Recessed in the bezel: a STACKHOUSE red-orange header strip (part Header, role "header",
Front face: room for a "NOW SERVING" SurfaceGui title) over a dark glossy screen (part Screen,
role "screen", Glass, Front face) where the game draws the order numbers; no baked text. A small
amber status lamp (Neon) sits on the bezel's chin.
Wall-mounted: modelled with the back on Blender y = 0; PIVOT = bottom-centre of the back face
(flat on the wall). Front faces -Y. ~3 x 1.4 x 0.4. No collision.
Sockets Screen / Header = centres of the screen / header strip, just in front of them, facing -Y (yaw 0).
Run:  bpyenv/bin/python blender/M_food/Shop_NowServing.py   (NS_EXPORT=1 export)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

ns = C.ns
S = C.shop()
BEZEL, SCREEN, STEEL, BRAND, AMBER = "#1C1D21", "#10161E", "#4A4F56", "#E8502A", "#FFB23D"
W, H = 3.0, 1.4
Y_BACK, Y_FRONT = -0.13, -0.4      # box back / bezel front (the wall is y = 0)
LIP = 0.035                        # bezel lip proud of the screen
OPEN_W, OPEN_H = 2.68, 1.12       # bezel opening
SCR_W, SCR_H = 2.6, 0.8            # visible screen (SurfaceGui area)
HDR_W, HDR_H = 2.6, 0.2            # header strip (SurfaceGui area)
ZC = H / 2
HDR_Z = ZC + OPEN_H / 2 - 0.04 - HDR_H / 2      # header centre
SCR_Z = HDR_Z - HDR_H / 2 - 0.04 - SCR_H / 2    # screen centre


def build():
    # bezel box: body + a rounded front lip framing the screen opening
    body = S.prism(S.rrect(W, H, 0.14, segs=3), "y", Y_FRONT + LIP, Y_BACK)
    body.location.z = ZC
    ns.bevel(body, width=0.04, segments=2, angle=50)
    lip = S.ring_slab(S.rrect(W, H, 0.14, segs=3), S.rrect(OPEN_W, OPEN_H, 0.05, segs=3), "y",
                      Y_FRONT, Y_FRONT + LIP + 0.01)
    lip.location.z = ZC
    ns.bevel(lip, width=0.02, segments=1, angle=50)
    S.part([body, lip], "Bezel", BEZEL, "SmoothPlastic", smooth_angle=40)

    # recessed header strip and glossy screen
    face = Y_FRONT + LIP
    hdr = S.prism(S.rrect(HDR_W, HDR_H, 0.03, segs=1), "y", face - 0.006, face + 0.02)
    hdr.location.z = HDR_Z
    S.part([hdr], "Header", BRAND, "SmoothPlastic", recolor="header", smooth_angle=30)
    scr = S.prism(S.rrect(SCR_W, SCR_H, 0.04, segs=2), "y", face - 0.004, face + 0.02)
    scr.location.z = SCR_Z
    S.part([scr], "Screen", SCREEN, "Glass", recolor="screen", cast_shadow=False, smooth_angle=30)

    # amber status lamp on the chin
    chin_z = (H - OPEN_H) / 4
    led = ns.cyl(0.035, 0.03, loc=(1.24, Y_FRONT - 0.004, chin_z), rot=(90, 0, 0), verts=8, bevel=0.0)
    S.part([led], "StatusLamp", AMBER, "Neon", cast_shadow=False, smooth_angle=60)

    # wall bracket: wall plate + two arms into the box back
    plate = S.prism(S.rrect(1.5, 0.62, 0.08, segs=2), "y", -0.03, 0.0)
    plate.location.z = ZC
    ns.bevel(plate, width=0.012, segments=1, angle=50)
    arms = [ns.box((0.14, -Y_BACK - 0.02, 0.32), loc=(sx * 0.5, (Y_BACK - 0.03) / 2 - 0.005, ZC), bevel=0.025,
                   segments=1) for sx in (-1, 1)]
    screws = [ns.cyl(0.04, 0.02, loc=(sx * 0.6, -0.035, ZC + sz * 0.2), rot=(90, 0, 0), verts=6, bevel=0.0)
              for sx in (-1, 1) for sz in (-1, 1)]
    S.part([plate] + arms + screws, "Bracket", STEEL, "Metal", smooth_angle=45)

    sockets = {"Screen": ((0.0, face - 0.004 - 0.02, SCR_Z), 0.0),
               "Header": ((0.0, face - 0.006 - 0.02, HDR_Z), 0.0)}
    meta = {"mount": "wall", "pivot": "bottom-centre of the back face (flat on the wall)",
            "screen_size": [SCR_W, SCR_H], "header_size": [HDR_W, HDR_H],
            "surfaces": [C.screen_meta("Screen", SCR_W, SCR_H), C.screen_meta("Header", HDR_W, HDR_H)],
            "roles": {"screen": "Screen", "header": "Header"}}
    return {"export": {"sockets": sockets, "meta": meta}}


def preview(asset, out_dir, res, samples):
    return C.angles_preview(asset, out_dir, res, samples, angles=((-30.0, 8.0), (125.0, 15.0)), margin=1.15)


if __name__ == "__main__":
    C.run(build, "Shop_NowServing", meta_=None, pivot=(0.0, 0.0, 0.0), group="Shop", preview=preview)
