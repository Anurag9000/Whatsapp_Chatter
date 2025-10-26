from __future__ import annotations

from pathlib import Path
from typing import Optional


CONTEXTS_DIR = Path("contexts")


def resolve_context_path(person: str, explicit_filename: Optional[str] = None) -> Path:
    """Resolve the context file path for a given person.

    If `explicit_filename` is provided, use it; otherwise default to `<person>.txt`.
    The file lives under `contexts/`.
    """
    CONTEXTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = explicit_filename or f"{person}.txt"
    return CONTEXTS_DIR / filename


def load_context(person: str, explicit_filename: Optional[str] = None) -> str:
    path = resolve_context_path(person, explicit_filename)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def ensure_context_file(person: str, explicit_filename: Optional[str] = None) -> Path:
    path = resolve_context_path(person, explicit_filename)
    if not path.exists():
        path.write_text(
            "# Write examples of your tone and replies for this contact.\n",
            encoding="utf-8",
        )
    return path

