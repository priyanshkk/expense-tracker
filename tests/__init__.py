"""Test package setup.

Insert ``src/`` into ``sys.path`` so pytest and package-style test imports work
from the repository root without an editable install.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
