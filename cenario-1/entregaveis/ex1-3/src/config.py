from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    docs_dir: Path
    chroma_dir: Path
    collection_name: str
    chunk_threshold_chars: int
    chunk_size: int
    chunk_overlap: int
    default_top_k: int
    prompt_template_path: Path


ROOT_DIR = Path(__file__).resolve().parents[3]

SETTINGS = Settings(
    docs_dir=ROOT_DIR / "anexo-a-documentos-individuais",
    chroma_dir=ROOT_DIR / "entregaveis" / "ex1-3" / "chroma_db",
    collection_name="novatech_knowledge_base",
    chunk_threshold_chars=1000,
    chunk_size=700,
    chunk_overlap=100,
    default_top_k=8,
    prompt_template_path=ROOT_DIR / "entregaveis" / "ex1-2" / "prompt-v3.md",
)
