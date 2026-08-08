import os
import psycopg2
from typing import List, Optional
from pgvector.psycopg2 import register_vector


class VectorStore:
    """Lightweight wrapper around PostgreSQL + pgvector for conversation memory."""

    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.getenv("DATABASE_URL")
        self.enabled = False
        self.conn = None
        if not self.dsn:
            print("[VectorStore] DATABASE_URL not set; memory disabled")
            return
        try:
            self.conn = psycopg2.connect(self.dsn)
            self.conn.autocommit = True
            register_vector(self.conn)
            self._ensure_schema()
            self.enabled = True
            print("[VectorStore] Connected to PostgreSQL + pgvector")
        except Exception as exc:
            print(f"[VectorStore] Disabled (connection failed): {exc}")
            self.enabled = False

    def _ensure_schema(self) -> None:
        """Create extension/table/indexes if they do not exist."""
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    ts TIMESTAMPTZ DEFAULT NOW(),
                    user_input TEXT NOT NULL,
                    ai_response TEXT,
                    embedding vector(1536),
                    intent VARCHAR(100),
                    action_taken TEXT,
                    success BOOLEAN,
                    latency_ms INTEGER,
                    language VARCHAR(10)
                );
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_conversations_embedding
                ON conversations USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_conversations_ts
                ON conversations (ts DESC);
                """
            )

    def add_conversation(
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
        if not self.enabled:
            return
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (
                    user_input, ai_response, embedding, intent,
                    action_taken, success, latency_ms, language
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    user_input,
                    ai_response,
                    embedding,
                    intent,
                    action_taken,
                    success,
                    latency_ms,
                    language,
                ),
            )

    def similar_conversations(
        self, embedding: List[float], limit: int = 5
    ) -> List[dict]:
        if not self.enabled:
            return []
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    user_input,
                    ai_response,
                    intent,
                    action_taken,
                    success,
                    language,
                    ts,
                    (1 - (embedding <=> %s::vector)) AS score
                FROM conversations
                WHERE embedding IS NOT NULL
                ORDER BY embedding <-> %s::vector
                LIMIT %s;
                """,
                (embedding, embedding, limit),
            )
            rows = cur.fetchall()
        return [
            {
                "user_input": r[0],
                "ai_response": r[1],
                "intent": r[2],
                "action_taken": r[3],
                "success": r[4],
                "language": r[5],
                "ts": r[6],
                "score": r[7],
            }
            for r in rows
        ]
