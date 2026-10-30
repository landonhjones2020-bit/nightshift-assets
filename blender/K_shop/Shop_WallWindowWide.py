"""Shop_WallWindowWide — 16 x 20 wall module: the Patron's picture window (M5+M6).

One 14.4 wide x 13 tall opening (x +-7.2, sill 3.5, head 16.5) with NO centre mullion, only
the chrome transom bar at 12, so the Patron's face fills one clear sheet of glass. Same
frame, sill, wainscot, pinstripes, frieze rail and top crown as Shop_WallWindowTall (built
by its build(hw=8, ox=7.2)); one `Glass` part (role glass, Glass, transparency 0.6, collides).
Pivot on the wall centre line, bottom, at the module's centre (an 8-stud grid node: the
module spans two grid bays). Collision: Core + Glass.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import Shop_WallWindowTall as T  # noqa: E402

HW, OX = 8.0, 7.2


def build():
    T.build(hw=HW, ox=OX)


META = T.meta(hw=HW, ox=OX, grid=16)

if __name__ == "__main__":
    C.run(build, "Shop_WallWindowWide", pivot=(0, 0, 0), meta=META)
