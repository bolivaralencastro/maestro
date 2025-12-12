import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from maestro.utils import (
    ACTIVE_FILE,
    INDEX_FILE,
    MAESTRO_DIR,
    ROOT_DIR,
    SESSIONS_DIR,
    ensure_base_structure,
    iso_now,
    random_base36,
    read_active_session_id,
    read_json,
    slugify,
    write_json,
)


def update_index(new_entry: Dict[str, Any], active_id: str) -> None:
    index = read_json(INDEX_FILE, {"sessions": []})
    cleaned_sessions: List[Dict[str, Any]] = []
    for session in index.get("sessions", []):
        session.pop("active", None)
        if session.get("id") == active_id:
            continue
        cleaned_sessions.append(session)

    new_entry = {**new_entry, "active": True}
    cleaned_sessions.append(new_entry)
    write_json(INDEX_FILE, {"sessions": cleaned_sessions})


def create_session_layout(session_id: str) -> Path:
    session_dir = SESSIONS_DIR / session_id
    if session_dir.exists():
        raise FileExistsError(f"Sessão {session_id} já existe")
    session_dir.mkdir(parents=False, exist_ok=False)

    subdirs = [
        session_dir / "context" / "items",
        session_dir / "context" / "blobs",
        session_dir / "runs",
        session_dir / "outputs",
        session_dir / "exports",
    ]

    try:
        for path in subdirs:
            path.mkdir(parents=True, exist_ok=False)
        active_path = session_dir / "context" / "active.json"
        write_json(active_path, {"items": []})
    except Exception:
        shutil.rmtree(session_dir, ignore_errors=True)
        raise

    return session_dir


def start_session(name: str) -> Tuple[str, Path]:
    ensure_base_structure()
    slug, used_fallback_slug = slugify(name)
    if used_fallback_slug:
        raise ValueError("Escolha um nome com caracteres alfanuméricos para a sessão.")
    short_id = random_base36()
    session_id = f"{slug}--{short_id}"
    now = iso_now()

    session_dir = create_session_layout(session_id)
    session_json = {
        "id": session_id,
        "slug": slug,
        "state": "iniciada",
        "tool_active": None,
        "created_at": now,
        "updated_at": now,
        "counters": {"run_seq": 0, "ctx_seq": 0},
        "stats": {"runs_total": 0, "runs_success": 0, "runs_error": 0},
    }
    write_json(session_dir / "session.json", session_json)

    index_entry = {
        "id": session_id,
        "slug": slug,
        "state": "iniciada",
        "created_at": now,
        "updated_at": now,
    }
    update_index(index_entry, session_id)

    ACTIVE_FILE.write_text(session_id, encoding="utf-8")

    return session_id, session_dir


def list_sessions() -> int:
    index = read_json(INDEX_FILE, {"sessions": []})
    sessions = index.get("sessions") or []
    has_active_file, active_id_from_file = read_active_session_id()
    active_id_from_index = next((sess.get("id") for sess in sessions if sess.get("active")), None)
    active_id = active_id_from_file if has_active_file else active_id_from_index
    warnings: List[str] = []

    active_in_index = any(sess.get("id") == active_id for sess in sessions)
    active_label = active_id or "nenhuma"
    if has_active_file and active_id is None:
        active_label = "nenhuma (arquivo de active vazio)"
    elif active_id and not active_in_index:
        active_label = f"{active_id} (não encontrada no índice)"
        warnings.append("Aviso: arquivo de active aponta para uma sessão ausente no índice.")

    print(f"Sessão ativa: {active_label}")
    for warn in warnings:
        print(warn)

    if not sessions:
        print("Nenhuma sessão registrada.")
        return 0

    print("Sessões registradas:")
    for session in sessions:
        session_id = session.get("id", "<sem-id>")
        marker = "*" if session_id == active_id else "-"
        slug = session.get("slug", "<sem-slug>")
        created_at = session.get("created_at", "?")

        session_dir = SESSIONS_DIR / session_id
        session_json_path = session_dir / "session.json"
        session_data = read_json(session_json_path, {}) if session_json_path.exists() else {}
        state = session_data.get("state", session.get("state", "<desconhecido>"))
        updated_at = session_data.get("updated_at", session.get("updated_at", "?"))
        finalized_at = session_data.get("finalized_at", session.get("finalized_at"))
        finalized_part = f" | finalizada: {finalized_at}" if finalized_at else ""
        inconsistent = not session_dir.exists() or not session_json_path.exists()
        inconsistency_tag = " [órfã]" if inconsistent else ""

        print(
            f"{marker} {session_id}{inconsistency_tag} | slug: {slug} | estado: {state} | criada: {created_at} | atualizada: {updated_at}{finalized_part}"
        )

    return 0


def status_session() -> int:
    if not MAESTRO_DIR.exists():
        print("Nenhuma sessão ativa.")
        print("Dica: use maestro session start <nome>.")
        return 0

    index = read_json(INDEX_FILE, {"sessions": []})
    sessions = index.get("sessions") or []
    has_active_file, active_id = read_active_session_id()
    if not has_active_file:
        active_id = next((sess.get("id") for sess in sessions if sess.get("active")), None)

    if not active_id:
        print("Nenhuma sessão ativa.")
        print("Dica: use maestro session start <nome>.")
        return 0

    entry = next((sess for sess in sessions if sess.get("id") == active_id), None)
    if entry is None:
        print(f"Sessão ativa apontada ({active_id}) não existe no índice.")
        return 0

    session_dir = SESSIONS_DIR / active_id
    if not session_dir.exists():
        print(f"Diretório da sessão ativa não encontrado: {session_dir}")
        return 0

    session_json_path = session_dir / "session.json"
    if not session_json_path.exists():
        print(f"Metadados da sessão ativa não encontrados: {session_json_path}")
        return 0

    session_data = read_json(session_json_path, {})
    slug = session_data.get("slug", entry.get("slug", "<desconhecido>"))
    state = session_data.get("state", entry.get("state", "<desconhecido>"))
    tool_active = session_data.get("tool_active")
    created_at = session_data.get("created_at", entry.get("created_at", "?"))
    updated_at = session_data.get("updated_at", entry.get("updated_at", "?"))

    print(f"Sessão ativa: {active_id}")
    print(f"slug: {slug}")
    print(f"state: {state}")
    print(f"tool_active: {tool_active}")
    print(f"created_at: {created_at}")
    print(f"updated_at: {updated_at}")

    counters = session_data.get("counters")
    if isinstance(counters, dict):
        print("counters:")
        if "run_seq" in counters:
            print(f"  run_seq: {counters.get('run_seq')}")
        if "ctx_seq" in counters:
            print(f"  ctx_seq: {counters.get('ctx_seq')}")

    stats = session_data.get("stats")
    if isinstance(stats, dict):
        print("stats:")
        if "runs_total" in stats:
            print(f"  runs_total: {stats.get('runs_total')}")
        if "runs_success" in stats:
            print(f"  runs_success: {stats.get('runs_success')}")
        if "runs_error" in stats:
            print(f"  runs_error: {stats.get('runs_error')}")

    return 0


def require_active_session() -> Tuple[str, Path, Dict[str, Any]]:
    if not MAESTRO_DIR.exists():
        raise RuntimeError("Nenhuma sessão foi criada ainda.")

    has_active, active_id = read_active_session_id()
    if not has_active or not active_id:
        raise RuntimeError("Nenhuma sessão ativa. Use 'maestro session start <nome>'.")

    session_dir = SESSIONS_DIR / active_id
    session_json_path = session_dir / "session.json"
    if not session_dir.exists():
        raise RuntimeError(f"Sessão ativa inválida: {active_id}.")

    try:
        with session_json_path.open("r", encoding="utf-8") as f:
            session_data = json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Metadados da sessão ativa não encontrados: {session_json_path}")
    except json.JSONDecodeError:
        raise RuntimeError(f"Metadados da sessão ativa corrompidos: {session_json_path}")
    except OSError:
        raise RuntimeError(f"Não foi possível ler os metadados da sessão ativa: {session_json_path}")

    if not session_data:
        raise RuntimeError(f"Metadados da sessão ativa ausentes ou corrompidos: {session_json_path}.")

    state = session_data.get("state")
    if state == "finalizada":
        raise RuntimeError("Sessão finalizada não pode ser modificada")

    return active_id, session_dir, session_data
