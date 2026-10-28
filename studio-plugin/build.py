"""Inline lib/NSZ.lua into NightShiftImporter.lua (between the BEGIN/END NSZ markers).

Usage:  python3 build.py          rewrite the plugin
        python3 build.py --check  exit 1 if the plugin is out of date (CI / pre-commit)
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PLUGIN = HERE / "NightShiftImporter.lua"
LIB = HERE / "lib" / "NSZ.lua"
BEGIN = "-- BEGIN NSZ"
END = "-- END NSZ"


def library_core() -> str:
    src = LIB.read_text()
    start = src.index("local B64 = {}")
    stop = src.index("local NSZ = {}")
    return src[start:stop].rstrip("\n") + "\n"


def rebuilt() -> str:
    plugin = PLUGIN.read_text()
    head, rest = plugin.split(BEGIN, 1)
    marker_line, rest = rest.split("\n", 1)
    _, tail = rest.split(END, 1)
    return head + BEGIN + marker_line + "\n" + library_core() + END + tail


def main() -> int:
    new = rebuilt()
    if "--check" in sys.argv:
        if new != PLUGIN.read_text():
            print("NightShiftImporter.lua is out of date; run python3 studio-plugin/build.py")
            return 1
        print("plugin up to date")
        return 0
    PLUGIN.write_text(new)
    print("plugin rebuilt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
