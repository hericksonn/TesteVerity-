"""Serviço de LLM com LangChain (ChatOpenAI + prompt estruturado em JSON)."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.prompts.story_prompts import (
    ANALYSIS_SYSTEM,
    ANALYSIS_USER,
    UNDERSTANDING_SYSTEM,
    UNDERSTANDING_USER,
)
from app.utils.config import openai_api_key, openai_model


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    raise ValueError("O modelo não retornou JSON válido.")


def run_understanding_summary(user_story: str) -> str:
    """Uma frase curta para enriquecer a consulta ao RAG."""
    llm = ChatOpenAI(
        api_key=openai_api_key(),
        model=openai_model(),
        temperature=0.0,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", UNDERSTANDING_SYSTEM),
            ("human", UNDERSTANDING_USER),
        ]
    )
    raw = (prompt | llm).invoke({"user_story": user_story})
    content = raw.content if hasattr(raw, "content") else str(raw)
    return content.strip() if isinstance(content, str) else str(content).strip()


def run_structured_analysis(
    *,
    user_story: str,
    rag_context: str,
    memory_summary: str,
) -> dict[str, Any]:
    llm = ChatOpenAI(
        api_key=openai_api_key(),
        model=openai_model(),
        temperature=0.2,
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ANALYSIS_SYSTEM),
            ("human", ANALYSIS_USER),
        ]
    )
    chain = prompt | llm
    raw = chain.invoke(
        {
            "user_story": user_story,
            "rag_context": rag_context,
            "memory_summary": memory_summary,
        }
    )
    content = raw.content if hasattr(raw, "content") else str(raw)
    if not isinstance(content, str):
        content = str(content)
    return _extract_json(content)
