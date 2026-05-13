from __future__ import annotations

from pathlib import Path

from app.rag.document_loader import load_markdown_files


def test_load_markdown_files_filters_and_sorts(tmp_path):
    (tmp_path / "z.md").write_text("Z content", encoding="utf-8")
    (tmp_path / "a.md").write_text("A content", encoding="utf-8")
    (tmp_path / "skip.txt").write_text("x", encoding="utf-8")
    loaded = load_markdown_files(tmp_path)
    names = [n for n, _ in loaded]
    assert names == ["a.md", "z.md"]
    assert loaded[0][1] == "A content"


def test_load_missing_dir_returns_empty(tmp_path):
    missing = tmp_path / "nope"
    assert load_markdown_files(missing) == []
