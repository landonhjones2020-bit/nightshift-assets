"""Lobby_StoreWallPlain — Lobby_StoreWall without its gooseneck sconce (2026-11-04).

The HQ facade modules behind the three leaderboards use it: their sconces hung in front of
the boards' screens (Landon, 21:45: "fix this issue with the lights"). Same brick, header band,
pinstripes, bolts, parapet and coping as Lobby_StoreWall, so the facade still reads as one wall.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import Lobby_StoreWall as W  # noqa: E402

META = dict(W.META)
META["roles"] = {"brick": "Brick", "header": "Header"}
META.pop("light_hint", None)
META["variant"] = "Lobby_StoreWall without the sconce (behind the leaderboards)"

if __name__ == "__main__":
    C.run(lambda: W.build(sconce=False), "Lobby_StoreWallPlain", sockets={}, pivot=(0, 0, 0), meta=META)
