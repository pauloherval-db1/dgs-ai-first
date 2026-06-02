from __future__ import annotations

from .prompt_builder import build_prompt
from .retrieve import retrieve_chunks


def run(question: str, top_k: int = 8) -> str:
    chunks = retrieve_chunks(query=question, top_k=top_k)
    return build_prompt(question=question, chunks=chunks)


if __name__ == "__main__":
    q = "Posso devolver carga perigosa?"
    prompt = run(question=q, top_k=8)
    print(prompt)
