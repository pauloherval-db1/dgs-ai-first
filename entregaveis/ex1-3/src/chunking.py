from __future__ import annotations

from hashlib import md5
from pathlib import Path
from typing import List

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from .config import SETTINGS
from .models import ChunkRecord


def _section_header(section_metadata: dict) -> str:
    h3 = section_metadata.get("h3")
    h2 = section_metadata.get("h2")
    return h3 or h2 or "root"


def _make_chunk_id(file_name: str, section_heading: str, index: int, content: str) -> str:
    raw = f"{file_name}|{section_heading}|{index}|{content[:120]}"
    digest = md5(raw.encode("utf-8")).hexdigest()[:16]
    return f"{Path(file_name).stem}-{digest}"


def build_chunks(file_name: str, text: str, base_metadata: dict) -> List[ChunkRecord]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("##", "h2"), ("###", "h3")],
        strip_headers=False,
    )
    recursive_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=SETTINGS.chunk_size,
        chunk_overlap=SETTINGS.chunk_overlap,
    )

    section_docs = header_splitter.split_text(text)
    if not section_docs:
        section_docs = []

    records: List[ChunkRecord] = []

    for section in section_docs:
        section_text = section.page_content.strip()
        if not section_text:
            continue

        section_heading = _section_header(section.metadata)
        if len(section_text) <= SETTINGS.chunk_threshold_chars:
            metadata = {
                **base_metadata,
                "section_heading": section_heading,
                "chunk_method": "header",
                "chunk_index_in_section": 0,
            }
            chunk_id = _make_chunk_id(file_name, section_heading, 0, section_text)
            records.append(ChunkRecord(chunk_id=chunk_id, text=section_text, metadata=metadata))
            continue

        split_parts = recursive_splitter.split_text(section_text)
        for idx, part in enumerate(split_parts):
            part_clean = part.strip()
            if not part_clean:
                continue
            metadata = {
                **base_metadata,
                "section_heading": section_heading,
                "chunk_method": "recursive_split",
                "chunk_index_in_section": idx,
            }
            chunk_id = _make_chunk_id(file_name, section_heading, idx, part_clean)
            records.append(ChunkRecord(chunk_id=chunk_id, text=part_clean, metadata=metadata))

    # Fallback when no markdown headings exist.
    if not records and text.strip():
        parts = recursive_splitter.split_text(text)
        for idx, part in enumerate(parts):
            part_clean = part.strip()
            if not part_clean:
                continue
            metadata = {
                **base_metadata,
                "section_heading": "root",
                "chunk_method": "recursive_split",
                "chunk_index_in_section": idx,
            }
            chunk_id = _make_chunk_id(file_name, "root", idx, part_clean)
            records.append(ChunkRecord(chunk_id=chunk_id, text=part_clean, metadata=metadata))

    return records
