from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_chroma import Chroma

from .chunking import build_chunks
from .config import SETTINGS
from .embedding import get_embedding_model
from .metadata_utils import extract_document_metadata
from .models import ChunkRecord


def _load_markdown_files(docs_dir: Path) -> List[Path]:
    return sorted(docs_dir.glob("*.md"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_chunks() -> List[ChunkRecord]:
    files = _load_markdown_files(SETTINGS.docs_dir)
    all_chunks: List[ChunkRecord] = []

    for file_path in files:
        raw_text = _read_text(file_path)
        base_metadata = extract_document_metadata(file_path, raw_text)
        chunks = build_chunks(file_path.name, raw_text, base_metadata)
        all_chunks.extend(chunks)

    return all_chunks


def run_ingestion() -> None:
    SETTINGS.chroma_dir.mkdir(parents=True, exist_ok=True)
    chunks = collect_chunks()
    if not chunks:
        raise RuntimeError("No chunks generated. Check source documents path.")

    embedding_model = get_embedding_model()

    vectorstore = Chroma(
        collection_name=SETTINGS.collection_name,
        embedding_function=embedding_model,
        persist_directory=str(SETTINGS.chroma_dir),
    )

    # Recreate content deterministically for a simple MVP execution.
    vectorstore.delete_collection()
    vectorstore = Chroma(
        collection_name=SETTINGS.collection_name,
        embedding_function=embedding_model,
        persist_directory=str(SETTINGS.chroma_dir),
    )

    vectorstore.add_texts(
        texts=[c.text for c in chunks],
        metadatas=[c.metadata for c in chunks],
        ids=[c.chunk_id for c in chunks],
    )

    print(f"Ingestion completed. Indexed chunks: {len(chunks)}")


if __name__ == "__main__":
    run_ingestion()
