from __future__ import annotations

import json
from pathlib import Path

from .prompt_builder import build_prompt
from .retrieve import retrieve_chunks

TEST_QUESTIONS = [
    "Qual o prazo de devolução?",
    "Posso devolver carga perigosa?",
    "Qual o SLA do cliente Gold?",
    "Qual o SLA do cliente Platinum?",
    "Qual o multiplicador para o Sudeste?",
]

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "testes"


def run_tests() -> list[dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for idx, question in enumerate(TEST_QUESTIONS, start=1):
        chunks = retrieve_chunks(question, top_k=6)

        retrieval_lines = []
        for rank, c in enumerate(chunks, start=1):
            retrieval_lines.append(
                f"[{rank}] score={c.score:.4f} "
                f"source={c.metadata.get('source')} "
                f"section={c.metadata.get('section_heading')} "
                f"priority={c.metadata.get('priority_level')}"
            )
        retrieval_text = "\n".join(retrieval_lines)

        prompt_text = build_prompt(question, chunks)

        retrieval_path = OUTPUT_DIR / f"teste-{idx:02d}-retrieval.txt"
        prompt_path = OUTPUT_DIR / f"teste-{idx:02d}-prompt.txt"
        retrieval_path.write_text(retrieval_text, encoding="utf-8")
        prompt_path.write_text(prompt_text, encoding="utf-8")

        result = {
            "index": idx,
            "question": question,
            "retrieval": retrieval_lines,
            "retrieval_path": str(retrieval_path),
            "prompt_path": str(prompt_path),
        }
        results.append(result)
        print(f"[teste {idx}/5] '{question}'")
        print(retrieval_text)
        print()

    summary_path = OUTPUT_DIR / "resumo-retrieval.json"
    summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resultados salvos em: {OUTPUT_DIR}")
    return results


if __name__ == "__main__":
    run_tests()
