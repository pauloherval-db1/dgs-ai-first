from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from langchain_chroma import Chroma

from .config import SETTINGS
from .embedding import get_embedding_model


@dataclass
class RetrievedChunk:
    text: str
    metadata: Dict[str, Any]
    score: float


def _vectorstore() -> Chroma:
    return Chroma(
        collection_name=SETTINGS.collection_name,
        embedding_function=get_embedding_model(),
        persist_directory=str(SETTINGS.chroma_dir),
    )


def _priority_filter(query: str) -> Optional[Dict[str, Any]]:
    query_l = query.lower()
    norm_keywords = [
        "politica",
        "sla",
        "contrato",
        "norma",
        "devolucao",
    ]
    if any(k in query_l for k in norm_keywords):
        return {"priority_level": {"$ne": 6}}
    return None


def _sort_by_authority(items: List[RetrievedChunk]) -> List[RetrievedChunk]:
    return sorted(
        items,
        key=lambda x: (
            x.metadata.get("priority_level", 99),
            x.score,
        ),
    )


def retrieve_chunks(query: str, top_k: int = SETTINGS.default_top_k) -> List[RetrievedChunk]:
    vs = _vectorstore()
    where_filter = _priority_filter(query)
    docs_with_scores = vs.similarity_search_with_score(query=query, k=top_k, filter=where_filter)

    results = [
        RetrievedChunk(text=doc.page_content, metadata=doc.metadata, score=score)
        for doc, score in docs_with_scores
    ]

    return _sort_by_authority(results)


if __name__ == "__main__":
    question = "Qual o prazo de devolucao para carga perigosa?"
    retrieved = retrieve_chunks(question, top_k=6)
    for idx, item in enumerate(retrieved, start=1):
        print(f"[{idx}] score={item.score:.4f} source={item.metadata.get('source')} section={item.metadata.get('section_heading')}")
