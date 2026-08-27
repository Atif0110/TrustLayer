import os
from pathlib import Path
import sys

os.environ.setdefault(
    "TRUSTLAYER_JWT_SECRET",
    "unit-test-secret-with-32-byte-minimum-length",
)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))