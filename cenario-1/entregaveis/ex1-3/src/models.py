from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ChunkRecord:
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
