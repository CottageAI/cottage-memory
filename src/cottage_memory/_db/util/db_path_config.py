# util/db_path_config.py  (or util/paths.py)

import json
from pathlib import Path
from platformdirs import user_config_dir

_APP = "Cottage_Memory"
_FILE = "db_path.json"

def config_file_path() -> Path:
    d = Path(user_config_dir(_APP))
    d.mkdir(parents=True, exist_ok=True)
    return d / _FILE

def write_db_path(db_path: str) -> None:
    p = Path(db_path).expanduser().resolve()
    config_file_path().write_text(json.dumps({"db_path": str(p)}), encoding="utf-8")

def read_db_path() -> Path | None:
    f = config_file_path()
    if not f.exists():
        return None
    data = json.loads(f.read_text(encoding="utf-8"))
    raw = data.get("db_path")
    return Path(raw).expanduser().resolve() if raw else None
