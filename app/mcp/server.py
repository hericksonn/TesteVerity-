"""Servidor MCP com ferramentas reais: RAG, persistência e histórico."""

from __future__ import annotations

import json
import sys
import traceback

from mcp.server.fastmcp import FastMCP

from app.memory.memory_store import MemoryStore, default_history_path
from app.rag.retriever import KnowledgeRetriever
from app.utils.config import project_root

mcp = FastMCP("Agile Story Assistant")

_retriever: KnowledgeRetriever | None = None
_memory: MemoryStore | None = None


def _get_retriever() -> KnowledgeRetriever:
    global _retriever
    if _retriever is None:
        print("Carregando base de conhecimento e gerando embeddings...", file=sys.stderr)
        _retriever = KnowledgeRetriever(project_root() / "data")
        n = _retriever.build_index()
        print(f"RAG pronto: {n} chunks indexados.", file=sys.stderr)
    return _retriever


def _get_memory() -> MemoryStore:
    global _memory
    if _memory is None:
        _memory = MemoryStore(default_history_path(project_root()))
    return _memory


@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """Recupera trechos relevantes dos documentos da squad (DoR, DoD, guia de histórias)."""
    q = (query or "").strip()
    if not q:
        return "Informe uma consulta não vazia."
    try:
        return _get_retriever().format_context(q, top_k=4)
    except Exception:
        return f"Erro ao buscar na base: {traceback.format_exc()}"


@mcp.tool()
def save_story_analysis(payload: str) -> str:
    """Salva uma análise no histórico local (JSON em memory/history.json)."""
    raw = (payload or "").strip()
    if not raw:
        return "Payload vazio."
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return "Payload precisa ser um objeto JSON."
        _get_memory().append_analysis(data)
        return "Análise salva com sucesso."
    except json.JSONDecodeError as e:
        return f"JSON inválido: {e}"
    except Exception:
        return f"Erro ao salvar: {traceback.format_exc()}"


@mcp.tool()
def list_previous_analyses(limit: int = 10) -> str:
    """Lista análises recentes para dar contexto ao agente."""
    try:
        lim = max(1, min(int(limit), 50))
    except (TypeError, ValueError):
        lim = 10
    try:
        rows = _get_memory().list_recent(lim)
        if not rows:
            return "(Nenhuma análise anterior.)"
        lines: list[str] = []
        for r in rows:
            ts = r.get("saved_at", "?")
            story = (r.get("story") or "").replace("\n", " ")[:220]
            diag = (r.get("diagnosis") or "").replace("\n", " ")[:200]
            lines.append(f"- [{ts}] {story} | Diagnóstico: {diag}")
        return "\n".join(lines)
    except Exception:
        return f"Erro ao listar: {traceback.format_exc()}"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
