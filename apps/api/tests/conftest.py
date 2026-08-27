import os
import sys
from pathlib import Path

os.environ.setdefault(
    "TRUSTLAYER_JWT_SECRET",
    "unit-test-secret-with-32-byte-minimum-length",
)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))