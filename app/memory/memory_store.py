"""Histórico local de análises (JSON) — memória simples do MVP."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def default_history_path(root: Path) -> Path:
    return root / "memory" / "history.json"


class MemoryStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _read_all(self) -> list[dict[str, Any]]:
        if not self._path.is_file():
            return []
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        return []

    def append_analysis(self, record: dict[str, Any]) -> None:
        items = self._read_all()
        record = {**record, "saved_at": datetime.now(timezone.utc).isoformat()}
        items.append(record)
        self._path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    def list_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        items = self._read_all()
        return items[-limit:][::-1]

    def format_recent_for_prompt(self, limit: int = 5) -> str:
        rows = self.list_recent(limit=limit)
        if not rows:
            return "(Sem análises anteriores salvas.)"
        lines: list[str] = []
        for r in rows:
            ts = r.get("saved_at", "?")
            story = (r.get("story") or "")[:200].replace("\n", " ")
            diag = (r.get("diagnosis") or "")[:180].replace("\n", " ")
            lines.append(f"- [{ts}] História: {story}… | Diagnóstico: {diag}…")
        return "\n".join(lines)
