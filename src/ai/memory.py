from typing import List, Optional, Tuple
from src.ai.embeddings import EmbeddingClient
from src.db.chroma_store import ChromaVectorStore


class MemoryManager:
    """Coordinates embeddings and vector storage for conversation memory (local, free)."""

    def __init__(self, embedder: EmbeddingClient, store: ChromaVectorStore) -> None:
        self.embedder = embedder
        self.store = store
        self.enabled = bool(embedder and embedder.enabled and store and store.enabled)
        if self.enabled:
            print(f"[MemoryManager] Active ({store.get_total_conversations()} past conversations)")
        else:
            print("[MemoryManager] Disabled (embedder or store not ready)")

    def get_context(self, user_input: str, k: int = 5) -> Tuple[List[dict], Optional[List[float]]]:
        """Embed input and fetch top-k similar past conversations."""
        if not self.enabled:
            return [], None
        embedding = self.embedder.embed(user_input)
        if not embedding:
            return [], None
        rows = self.store.similar_conversations(embedding, limit=k)
        return rows, embedding

    def store_interaction(
        self,
        user_input: str,
        ai_response: str,
        embedding: Optional[List[float]],
        intent: Optional[str],
        action_taken: Optional[str],
        success: bool,
        latency_ms: Optional[int],
        language: str,
    ) -> None:
        if not self.enabled or not embedding:
            return
        self.store.add_conversation(
            user_input=user_input,
            ai_response=ai_response,
            embedding=embedding,
            intent=intent,
            action_taken=action_taken,
            success=success,
            latency_ms=latency_ms,
            language=language,
        )
