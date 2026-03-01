import os
import tempfile
from pathlib import Path

DATA_ROOT = Path(tempfile.mkdtemp(prefix="littup-tests-"))
os.environ.setdefault("LITTUP_DATA_DIR", str(DATA_ROOT))
os.environ.setdefault("LITTUP_DB_PATH", str(DATA_ROOT / "littup.db"))
os.environ.setdefault("LITTUP_PROJECTS_DIR", str(DATA_ROOT / "projects"))
os.environ.setdefault("LITTUP_ENV", "development")
