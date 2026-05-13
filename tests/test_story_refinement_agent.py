from __future__ import annotations

from app.agents.story_refinement_agent import format_analysis_markdown


def test_format_analysis_markdown_contains_sections():
    analysis = {
        "diagnosis": "História incompleta.",
        "issues": ["Falta critério"],
        "refinement_questions": ["Qual escopo?"],
        "acceptance_criteria": ["Dado X quando Y então Z"],
        "risks": ["Escopo creep"],
        "dependencies": ["API de login"],
        "refined_user_story": "Como cliente, quero editar perfil, para manter dados corretos.",
        "confidence_notes": "Nota teste.",
    }
    md = format_analysis_markdown(analysis)
    assert "## Resultado da análise" in md
    assert "Diagnóstico" in md
    assert "Problemas" in md
    assert "Perguntas para o refinamento" in md
    assert "Critérios de aceite" in md
    assert "Riscos" in md
    assert "Dependências" in md
    assert "História refinada" in md
    assert "Notas de confiança" in md
