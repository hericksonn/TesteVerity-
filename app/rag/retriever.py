"""RAG leve: fragmentação, embeddings OpenAI e similaridade por cosseno."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from openai import OpenAI

from app.rag.document_loader import load_markdown_files
from app.utils.config import embedding_model, openai_api_key


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


@dataclass
class RetrievedChunk:
    source: str
    text: str
    score: float


class KnowledgeRetriever:
    """Indexa documentos locais e recupera trechos relevantes à consulta."""

    def __init__(self, data_dir: Path, client: OpenAI | None = None) -> None:
        self._data_dir = data_dir
        self._client = client or OpenAI(api_key=openai_api_key())
        self._emb_model = embedding_model()
        self._chunks: list[str] = []
        self._sources: list[str] = []
        self._vectors: np.ndarray | None = None

    def _split(self, text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
        text = text.strip()
        if not text:
            return []
        parts: list[str] = []
        i = 0
        while i < len(text):
            parts.append(text[i : i + chunk_size])
            i += chunk_size - overlap
        return parts

    def build_index(self) -> int:
        """Carrega arquivos, fragmenta e calcula embeddings. Retorna nº de chunks."""
        self._chunks.clear()
        self._sources.clear()
        for name, content in load_markdown_files(self._data_dir):
            for chunk in self._split(content):
                self._chunks.append(chunk)
                self._sources.append(name)
        if not self._chunks:
            self._vectors = None
            return 0
        resp = self._client.embeddings.create(model=self._emb_model, input=self._chunks)
        rows = [np.array(d.embedding, dtype=np.float32) for d in resp.data]
        self._vectors = np.vstack(rows)
        return len(self._chunks)

    def retrieve(self, query: str, top_k: int = 4) -> list[RetrievedChunk]:
        if not self._chunks or self._vectors is None:
            self.build_index()
        if not self._chunks or self._vectors is None:
            return []
        q = self._client.embeddings.create(model=self._emb_model, input=[query])
        qv = np.array(q.data[0].embedding, dtype=np.float32)
        scores: list[tuple[int, float]] = []
        for idx, row in enumerate(self._vectors):
            scores.append((idx, _cosine(qv, row)))
        scores.sort(key=lambda x: x[1], reverse=True)
        out: list[RetrievedChunk] = []
        for idx, sc in scores[:top_k]:
            out.append(
                RetrievedChunk(source=self._sources[idx], text=self._chunks[idx], score=sc)
            )
        return out

    def format_context(self, query: str, top_k: int = 4) -> str:
        chunks = self.retrieve(query, top_k=top_k)
        if not chunks:
            return "(Nenhum documento indexado em data/.)"
        lines: list[str] = []
        for c in chunks:
            lines.append(f"### Fonte: {c.source} (relevância ~{c.score:.3f})\n{c.text}\n")
        return "\n".join(lines).strip()
