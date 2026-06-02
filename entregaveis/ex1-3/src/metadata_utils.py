from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Any


META_PATTERN = re.compile(r"^\*\*(?P<key>[^*]+):\*\*\s*(?P<value>.+)$")


KEY_MAP = {
    "versao": "version",
    "ultima atualizacao": "last_updated",
    "data de emissao": "issued_at",
    "responsavel": "responsible",
    "classificacao": "classification",
    "status": "status",
}


PRIORITY_BY_TYPE = {
    "normativo": 2,
    "contratual": 2,
    "procedimento": 3,
    "informal": 6,
}


def _normalize(text: str) -> str:
    return text.strip().lower()


def infer_document_type(file_name: str, classification: str) -> str:
    low_name = file_name.lower()
    low_class = classification.lower()

    if "faq" in low_name or "informal" in low_class:
        return "informal"
    if "sla" in low_name or "contratual" in low_class:
        return "contratual"
    if "pol" in low_name or "normativo" in low_class:
        return "normativo"
    if "proc" in low_name:
        return "procedimento"
    return "procedimento"


def extract_document_metadata(file_path: Path, raw_text: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "source": str(file_path.name),
        "doc_id": file_path.stem,
        "classification": "",
        "version": "",
        "last_updated": "",
        "issued_at": "",
        "responsible": "",
        "status": "",
        "authority_label": "",
        "priority_level": 99,
        "is_validated": True,
        "has_transition_rule": False,
        "valid_from": "",
    }

    for line in raw_text.splitlines():
        match = META_PATTERN.match(line.strip())
        if not match:
            continue
        key = _normalize(match.group("key"))
        value = match.group("value").strip()
        mapped_key = KEY_MAP.get(key)
        if mapped_key:
            result[mapped_key] = value

    doc_type = infer_document_type(file_path.name, result.get("classification", ""))
    result["doc_type"] = doc_type
    result["priority_level"] = PRIORITY_BY_TYPE.get(doc_type, 99)
    result["authority_label"] = doc_type

    # FAQ is explicitly informal and non-validated.
    if doc_type == "informal":
        result["is_validated"] = False

    # Explicit business rule from PROC-042-v2 transition section.
    if "proc-042-v2" in file_path.stem.lower():
        result["has_transition_rule"] = True
        result["valid_from"] = "2023-12-01"

    return result
