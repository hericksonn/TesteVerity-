from __future__ import annotations

import json

from app.memory.memory_store import MemoryStore


def test_memory_store_append_and_list(tmp_path):
    path = tmp_path / "history.json"
    store = MemoryStore(path)
    store.append_analysis({"story": "Como X quero Y", "diagnosis": "ok"})
    store.append_analysis({"story": "História 2", "diagnosis": "revisar"})
    items = store.list_recent(10)
    assert len(items) == 2
    assert items[0]["story"] == "História 2"
    assert "saved_at" in items[0]


def test_memory_store_corrupt_file_recover(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")
    store = MemoryStore(path)
    assert store.list_recent(5) == []
    store.append_analysis({"story": "nova", "diagnosis": "d"})
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) == 1
