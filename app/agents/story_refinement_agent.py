"""Orquestração multi-step: entendimento → MCP (RAG/memória) → LLM → MCP (persistência)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from app.services.llm_service import run_structured_analysis, run_understanding_summary

if TYPE_CHECKING:
    from mcp import ClientSession


def _tool_text(result: Any) -> str:
    parts: list[str] = []
    for block in getattr(result, "content", []) or []:
        t = getattr(block, "text", None)
        if t:
            parts.append(t)
    return "\n".join(parts).strip() if parts else str(result)


def _tool_failed(result: Any, text: str) -> bool:
    """Detecta falhas explícitas do MCP ou mensagens de erro das ferramentas."""
    if getattr(result, "isError", False):
        return True
    lower = text.lower()
    if lower.startswith("erro ao"):
        return True
    if "json inválido" in lower:
        return True
    if lower.startswith("payload vazio"):
        return True
    return False


async def refine_user_story(session: ClientSession, user_story: str) -> dict[str, Any]:
    story = user_story.strip()
    if not story:
        raise ValueError("História vazia.")

    print("Passo 1: entendimento da história (LLM)...")
    summary = run_understanding_summary(story)
    print(f"  Resumo para busca: {summary}")

    print("Passo 2: recuperando contexto com RAG via MCP...")
    print("Using MCP tool: search_knowledge_base")
    rag = await session.call_tool(
        "search_knowledge_base",
        {"query": f"{summary}\n\n{story}"},
    )
    rag_text = _tool_text(rag)
    if _tool_failed(rag, rag_text):
        snippet = rag_text[:400].replace("\n", " ")
        print(f"  Atenção: problema na busca na base. {snippet}…", flush=True)
        rag_text = (
            "(Contexto RAG indisponível nesta execução; a análise segue com menor ancoragem documental.)"
        )
    else:
        print("  Contexto RAG recuperado.", flush=True)

    print("Passo 3: consultando memória (análises anteriores) via MCP...")
    print("Using MCP tool: list_previous_analyses")
    mem = await session.call_tool("list_previous_analyses", {"limit": 5})
    mem_text = _tool_text(mem)
    if _tool_failed(mem, mem_text):
        snippet = mem_text[:400].replace("\n", " ")
        print(f"  Atenção: problema ao ler memória. {snippet}…", flush=True)
        mem_text = "(Sem histórico anterior utilizável.)"

    print("Passo 4: avaliação e geração estruturada (LangChain + LLM)...")
    analysis = run_structured_analysis(
        user_story=story,
        rag_context=rag_text,
        memory_summary=mem_text,
    )

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
    }

    print("Passo 5: persistindo análise na memória local via MCP...")
    print("Using MCP tool: save_story_analysis")
    save_res = await session.call_tool(
        "save_story_analysis",
        {"payload": json.dumps(payload, ensure_ascii=False)},
    )
    save_text = _tool_text(save_res)
    if _tool_failed(save_res, save_text) or ("sucesso" not in save_text.lower()):
        print(f"  Atenção: não foi possível confirmar o salvamento: {save_text}", flush=True)
    else:
        print("  Memória atualizada (memory/history.json).", flush=True)

    return analysis


def format_analysis_markdown(analysis: dict[str, Any]) -> str:
    """Saída legível para o PO/SM no terminal."""
    lines: list[str] = ["## Resultado da análise", ""]
    lines.append(f"**Diagnóstico:** {analysis.get('diagnosis', '')}")
    lines.append("")
    issues = analysis.get("issues") or []
    if issues:
        lines.append("### Problemas / lacunas")
        for i in issues:
            lines.append(f"- {i}")
        lines.append("")
    qs = analysis.get("refinement_questions") or []
    if qs:
        lines.append("### Perguntas para o refinamento")
        for q in qs:
            lines.append(f"- {q}")
        lines.append("")
    ac = analysis.get("acceptance_criteria") or []
    if ac:
        lines.append("### Critérios de aceite sugeridos")
        for a in ac:
            lines.append(f"- {a}")
        lines.append("")
    risks = analysis.get("risks") or []
    if risks:
        lines.append("### Riscos")
        for r in risks:
            lines.append(f"- {r}")
        lines.append("")
    deps = analysis.get("dependencies") or []
    if deps:
        lines.append("### Dependências")
        for d in deps:
            lines.append(f"- {d}")
        lines.append("")
    lines.append("### História refinada")
    lines.append(analysis.get("refined_user_story", "").strip() or "(n/d)")
    lines.append("")
    notes = analysis.get("confidence_notes", "").strip()
    if notes:
        lines.append("### Notas de confiança / incertezas")
        lines.append(notes)
    return "\n".join(lines).strip()
