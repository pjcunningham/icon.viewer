import sys
from pathlib import Path

# Ensure 'src' is on sys.path for imports in tests
ROOT = Path(__file__).resolve().parents[1]
src_path = ROOT / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
