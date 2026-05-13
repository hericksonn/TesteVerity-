"""Fluxo local sem OpenAI/MCP: valida carregamento, contexto estático e persistência em JSON."""

from __future__ import annotations

import json
from typing import Any

from app.memory.memory_store import MemoryStore, default_history_path
from app.rag.document_loader import load_markdown_files
from app.utils.config import project_root


def _heuristic_summary(story: str) -> str:
    s = " ".join(story.strip().split())
    if not s:
        return ""
    for sep in ".!?":
        pos = s.find(sep, 0, 320)
        if pos != -1:
            return s[: pos + 1].strip()
    return (s[:220] + "…") if len(s) > 220 else s


def _simulated_rag_context() -> str:
    root = project_root()
    parts: list[str] = []
    for name, content in load_markdown_files(root / "data"):
        excerpt = content.strip()[:950].strip()
        parts.append(
            f"### {name} (trecho estático para dry-run, sem embeddings)\n{excerpt}\n"
        )
    return "\n".join(parts).strip() if parts else "(Nenhum .md em data/.)"


def _mock_analysis(story: str) -> dict[str, Any]:
    """Resposta fixa plausível — apenas para validar pipeline sem API."""
    preview = story.strip().replace("\n", " ")[:120]
    return {
        "diagnosis": (
            f"[DRY-RUN] A história é vaga no escopo e nos critérios observáveis. "
            f"Trecho analisado: “{preview}…”. Em execução real, o LLM usaria RAG + memória."
        ),
        "issues": [
            "Falta detalhar quais dados podem ser alterados e em quais telas.",
            "Não há critérios de aceite testáveis nem tratamento de erros.",
        ],
        "refinement_questions": [
            "Quais campos são editáveis e quais são somente leitura?",
            "Quais validações de negócio e de formato se aplicam?",
            "O que acontece após salvar (feedback, auditoria, reenvio de e-mail)?",
        ],
        "acceptance_criteria": [
            "Dado usuário autenticado, ao salvar dados válidos, o sistema persiste e exibe confirmação.",
            "Dado dados inválidos, o sistema bloqueia o envio e mostra mensagens específicas por campo.",
        ],
        "risks": [
            "Escopo crescer para “qualquer dado” sem regras explícitas.",
            "Impacto em LGPD/compliance se dados sensíveis forem editáveis sem trilha de auditoria.",
        ],
        "dependencies": [
            "Serviço de autenticação e perfil de usuário.",
            "API de cadastro e políticas de validação já existentes.",
        ],
        "refined_user_story": (
            "Como cliente autenticado, quero atualizar campos permitidos do meu cadastro "
            "(ex.: telefone e endereço) no perfil, para que minhas entregas e comunicações usem dados corretos."
        ),
        "confidence_notes": (
            "Saída simulada (--dry-run): não houve chamadas à API OpenAI nem ao servidor MCP."
        ),
    }


def run_dry_run(user_story: str) -> dict[str, Any]:
    story = user_story.strip()
    if not story:
        raise ValueError("História vazia.")

    print("Passo 1: entendimento da história (heurística local, sem LLM)...", flush=True)
    summary = _heuristic_summary(story)
    print(f"  Resumo para busca: {summary}", flush=True)

    print("Passo 2: contexto estático a partir de data/*.md (simula RAG, sem embeddings)...", flush=True)
    print("Using MCP tool: search_knowledge_base (dry-run — não invocado)", flush=True)
    rag_text = _simulated_rag_context()
    print("  Contexto carregado a partir dos arquivos locais.", flush=True)

    print("Passo 3: lendo memória local (sem MCP)...", flush=True)
    print("Using MCP tool: list_previous_analyses (dry-run — não invocado)", flush=True)
    store = MemoryStore(default_history_path(project_root()))
    mem_text = store.format_recent_for_prompt(limit=5)

    print("Passo 4: análise estruturada (resposta simulada, sem LangChain/OpenAI)...", flush=True)
    analysis = _mock_analysis(story)

    payload = {
        "story": story,
        "summary": summary,
        "diagnosis": analysis.get("diagnosis", ""),
        "issues": analysis.get("issues", []),
        "refinement_questions": analysis.get("refinement_questions", []),
        "acceptance_criteria": analysis.get("acceptance_criteria", []),
        "risks": analysis.get("risks", []),
        "dependencies": analysis.get("dependencies", []),
        "refined_user_story": analysis.get("refined_user_story", ""),
        "confidence_notes": analysis.get("confidence_notes", ""),
        "dry_run": True,
    }

    print("Passo 5: persistindo análise em memory/history.json (gravacao direta, sem MCP)...", flush=True)
    print("Using MCP tool: save_story_analysis (dry-run — não invocado)", flush=True)
    try:
        store.append_analysis(payload)
        print("  Memória atualizada (memory/history.json).", flush=True)
    except OSError as e:
        print(f"  Atenção: não foi possível salvar a análise: {e}", flush=True)

    return analysis
