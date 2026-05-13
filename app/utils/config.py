"""Carrega configuração a partir de variáveis de ambiente."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def project_root() -> Path:
    """Raiz do repositório (pasta que contém `app/` e `data/`)."""
    return Path(__file__).resolve().parents[2]


def openai_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "Defina OPENAI_API_KEY no ambiente ou no arquivo .env (veja .env.example)."
        )
    return key


def openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()


def embedding_model() -> str:
    return os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip()
