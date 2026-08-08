import os
from typing import List, Optional, Dict
import chromadb


class ChromaVectorStore:
    """Local Chroma-based vector store for conversation memory (no database server needed)."""

    def __init__(self, persist_dir: Optional[str] = None) -> None:
        """
        Initialize Chroma vector store.
        
        Args:
            persist_dir: Directory to store Chroma data. Defaults to ./chroma_data
        """
        self.persist_dir = persist_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", "..", "chroma_data"
        )
        os.makedirs(self.persist_dir, exist_ok=True)
        
        try:
            # Initialize Chroma client with new API
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            
            # Get or create collection for conversations
            self.collection = self.client.get_or_create_collection(
                name="conversations",
                metadata={"hnsw:space": "cosine"}
            )
            
            self.enabled = True
            print(f"[ChromaVectorStore] Connected (data dir: {self.persist_dir})")
            
        except Exception as exc:
            print(f"[ChromaVectorStore] Failed to initialize: {exc}")
            self.enabled = False

    def add_conversation(
        self,
        user_input: str,
        ai_response: str,
        embedding: List[float],
        intent: Optional[str] = None,
        action_taken: Optional[str] = None,
        success: bool = True,
        latency_ms: Optional[int] = None,
        language: str = "en",
    ) -> None:
        """Add a new conversation to the vector store."""
        if not self.enabled or not embedding:
            return
        
        try:
            # Create unique ID
            doc_id = f"conv_{self.collection.count() + 1}"
            
            # Store with metadata
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[user_input],
                metadatas=[{
                    "user_input": user_input,
                    "ai_response": ai_response,
                    "intent": intent or "unknown",
                    "action_taken": action_taken or "none",
                    "success": success,
                    "latency_ms": latency_ms or 0,
                    "language": language,
                }]
            )
        except Exception as exc:
            print(f"[ChromaVectorStore] Error adding conversation: {exc}")

    def similar_conversations(
        self, 
        embedding: List[float], 
        limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve similar past conversations by embedding similarity.
        
        Args:
            embedding: Query embedding vector
            limit: Number of results to return
            
        Returns:
            List of similar conversations with metadata
        """
        if not self.enabled or not embedding:
            return []
        
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=limit
            )
            
            conversations = []
            if results and results["metadatas"] and len(results["metadatas"]) > 0:
                for metadata in results["metadatas"][0]:
                    conversations.append({
                        "user_input": metadata.get("user_input", ""),
                        "ai_response": metadata.get("ai_response", ""),
                        "intent": metadata.get("intent", "unknown"),
                        "action_taken": metadata.get("action_taken", "none"),
                        "success": metadata.get("success", True),
                        "language": metadata.get("language", "en"),
                    })
            
            return conversations
            
        except Exception as exc:
            print(f"[ChromaVectorStore] Error querying conversations: {exc}")
            return []

    def get_total_conversations(self) -> int:
        """Get total number of stored conversations."""
        if not self.enabled:
            return 0
        try:
            return self.collection.count()
        except:
            return 0
