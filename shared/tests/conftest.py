"""Put the workspace root on sys.path so `shared.utils` imports resolve."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
