from __future__ import annotations

from typing import List

from .config import SETTINGS
from .retrieve import RetrievedChunk


FALLBACK_SYSTEM_PROMPT = """# Identidade
Voce e o Assistente de Atendimento da NovaTech.
Responda apenas com base nos chunks recuperados e cite as fontes utilizadas.
"""


def _load_system_prompt() -> str:
    path = SETTINGS.prompt_template_path
    if path.exists():
        return path.read_text(encoding="utf-8")
    return FALLBACK_SYSTEM_PROMPT


def _format_chunk(c: RetrievedChunk) -> str:
    src = c.metadata.get("source", "desconhecido")
    ver = c.metadata.get("version") or c.metadata.get("issued_at") or "n/d"
    auth = c.metadata.get("authority_label", "n/d")
    pri = c.metadata.get("priority_level", "n/d")
    sec = c.metadata.get("section_heading", "n/d")
    return (
        f"[Fonte: {src} | versao: {ver} | autoridade: {auth} | prioridade: {pri} | secao: {sec}]\n"
        f"{c.text}"
    )


def build_prompt(question: str, chunks: List[RetrievedChunk]) -> str:
    system_prompt = _load_system_prompt()
    context = "\n\n".join(_format_chunk(c) for c in chunks)
    return (
        f"# System\n{system_prompt}\n\n"
        f"# Contexto Recuperado\n{context}\n\n"
        f"# Pergunta do Atendente\n{question}\n\n"
        "# Instrucoes de Resposta\n"
        "- Responda em portugues formal e objetivo.\n"
        "- Se houver conflito entre fontes, explique a divergencia e nao consolide arbitrariamente.\n"
        "- Se nao houver respaldo oficial suficiente, diga explicitamente.\n"
    )
