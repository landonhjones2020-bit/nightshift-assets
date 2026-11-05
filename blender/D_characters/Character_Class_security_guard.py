"""Character_Class_security_guard — the class character for the CLASS SHOP (see _classes.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _classes as K  # noqa: E402

if __name__ == "__main__":
    K.run_class("security_guard")
