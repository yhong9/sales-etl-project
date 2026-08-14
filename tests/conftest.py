import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OLIST_SCRIPTS = PROJECT_ROOT / "scripts" / "olist"

sys.path.insert(0, str(OLIST_SCRIPTS))
