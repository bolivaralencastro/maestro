import hashlib
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
MAESTRO_DIR = ROOT_DIR / ".maestro"
SESSIONS_DIR = MAESTRO_DIR / "sessions"
INDEX_FILE = SESSIONS_DIR / "index.json"
ACTIVE_FILE = SESSIONS_DIR / "active"


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(name: str) -> Tuple[str, bool]:
    base = name.strip().lower()
    base = re.sub(r"[^a-z0-9]+", "-", base)
    base = re.sub(r"-{2,}", "-", base).strip("-")
    if not base:
        return "session", True
    return base, False


def random_base36(length: int = 6) -> str:
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    number = secrets.randbelow(36**length)
    digits: List[str] = []
    for _ in range(length):
        number, rem = divmod(number, 36)
        digits.append(alphabet[rem])
    return "".join(reversed(digits)).rjust(length, "0")


def read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default


def read_active_session_id() -> Tuple[bool, str | None]:
    exists = ACTIVE_FILE.exists()
    if not exists:
        return False, None
    try:
        content = ACTIVE_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return True, None
    return True, content or None


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def ensure_base_structure() -> None:
    (MAESTRO_DIR / "config").mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    (MAESTRO_DIR / "logs").mkdir(parents=True, exist_ok=True)


def format_size(size: Optional[int]) -> str:
    if size is None:
        return "tamanho desconhecido"
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    unit = "B"
    for candidate in units:
        unit = candidate
        if value < 1024 or candidate == units[-1]:
            break
        value /= 1024
    if unit == "B":
        return f"{int(value)} {unit}"
    return f"{value:.1f} {unit}"


def short_digest(digest: Optional[str]) -> str:
    if not digest:
        return "?"
    return f"{digest[:7]}..." if len(digest) > 7 else digest
