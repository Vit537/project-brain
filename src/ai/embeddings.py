from typing import List, Optional
from sentence_transformers import SentenceTransformer


class EmbeddingClient:
    """Wrapper around sentence-transformers for local offline embeddings (384-dim)."""

    def __init__(self, model: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model
        self.enabled = False
        self.model = None
        try:
            print(f"[EmbeddingClient] Loading model: {model}...")
            self.model = SentenceTransformer(model)
            self.enabled = True
            print(f"[EmbeddingClient] Ready (local embeddings, 384-dim)")
        except Exception as exc:
            print(f"[EmbeddingClient] Failed to load model: {exc}")
            self.enabled = False

    def embed(self, text: str) -> Optional[List[float]]:
        if not self.enabled or not self.model:
            return None
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as exc:
            print(f"[EmbeddingClient] Failed to embed text: {exc}")
            return None
