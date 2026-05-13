"""Carrega documentos Markdown da pasta `data/` para o RAG."""

from __future__ import annotations

from pathlib import Path


def load_markdown_files(data_dir: Path) -> list[tuple[str, str]]:
    """
    Retorna lista de (nome_arquivo, conteúdo).
    Ignora arquivos que não sejam .md.
    """
    if not data_dir.is_dir():
        return []
    out: list[tuple[str, str]] = []
    for path in sorted(data_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        out.append((path.name, text))
    return out
