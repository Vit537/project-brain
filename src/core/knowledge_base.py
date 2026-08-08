"""
Knowledge Base - Hybrid Memory Architecture
Combines human-readable .md files with ChromaDB vector search.

Architecture:
- MEMORY.md          → Long-term curated facts (user preferences, key decisions)
- memory/YYYY-MM-DD.md → Daily conversation logs (auto-generated)
- ChromaDB "knowledge" collection → Vector index over all .md content
- Tiered retrieval: hot (today/yesterday) → warm (this week) → cold (search only)

The LLM can both READ from and WRITE to the knowledge base.
"""
import os
import re
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta


class KnowledgeBase:
    """
    Hybrid knowledge base: .md files as source of truth, ChromaDB as search index.
    """

    def __init__(self, memory_dir: Optional[str] = None, embedder=None, chroma_store=None):
        if memory_dir is None:
            memory_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..', 'memory')
            )
        self.memory_dir = memory_dir
        self.memory_file = os.path.join(self.memory_dir, "MEMORY.md")
        os.makedirs(self.memory_dir, exist_ok=True)

        # Optional: vector search over .md files
        self.embedder = embedder      # EmbeddingClient instance
        self.chroma = chroma_store    # ChromaVectorStore instance (or None)

        # Create the knowledge collection in ChromaDB (separate from conversations)
        self._knowledge_collection = None
        if self.chroma and self.chroma.enabled:
            try:
                self._knowledge_collection = self.chroma.client.get_or_create_collection(
                    name="knowledge",
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception as exc:
                print(f"[KnowledgeBase] Could not create knowledge collection: {exc}")

        # Ensure MEMORY.md exists
        if not os.path.exists(self.memory_file):
            self._create_default_memory_file()

        self._indexed_files = set()
        count = self._knowledge_collection.count() if self._knowledge_collection else 0
        print(f"✓ Knowledge Base ready (memory_dir={self.memory_dir}, indexed={count})")

    # ------------------------------------------------------------------
    # MEMORY.md — Long-term curated facts
    # ------------------------------------------------------------------
    def read_memory(self) -> str:
        """Read the full MEMORY.md file."""
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def add_memory(self, fact: str, category: str = "general") -> None:
        """Append a fact to MEMORY.md under the given category heading."""
        content = self.read_memory()

        heading = f"## {category.title()}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"- [{timestamp}] {fact}"

        if heading in content:
            # Insert after the heading
            content = content.replace(heading, f"{heading}\n{entry}", 1)
        else:
            # Add new section
            content += f"\n\n{heading}\n{entry}\n"

        with open(self.memory_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Index the new fact
        self._index_text(fact, source="MEMORY.md", category=category)

    def search_memory(self, query: str) -> List[str]:
        """Simple text search within MEMORY.md."""
        content = self.read_memory()
        query_lower = query.lower()
        return [
            line.strip()
            for line in content.split("\n")
            if query_lower in line.lower() and line.strip()
        ]

    # ------------------------------------------------------------------
    # Daily Logs — memory/YYYY-MM-DD.md
    # ------------------------------------------------------------------
    def get_daily_log(self, date_str: Optional[str] = None) -> str:
        """Read a daily log file."""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(self.memory_dir, f"{date_str}.md")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def list_daily_logs(self, limit: int = 30) -> List[str]:
        """List available daily log files (most recent first)."""
        logs = []
        try:
            for fname in sorted(os.listdir(self.memory_dir), reverse=True):
                if re.match(r"\d{4}-\d{2}-\d{2}\.md$", fname):
                    logs.append(fname.replace(".md", ""))
                    if len(logs) >= limit:
                        break
        except FileNotFoundError:
            pass
        return logs

    # ------------------------------------------------------------------
    # Tiered Retrieval
    # ------------------------------------------------------------------
    def get_context(self, query: str, k: int = 5) -> str:
        """
        Retrieve relevant context using tiered approach:
        1. HOT: Always include today's MEMORY.md sections
        2. WARM: If vector search returns results from this week, include them
        3. COLD: Vector search over all indexed content
        """
        context_parts = []

        # HOT: Key facts from MEMORY.md (always included, trimmed)
        memory_content = self.read_memory()
        if memory_content:
            # Only include first 1500 chars to save tokens
            trimmed = memory_content[:1500]
            if len(memory_content) > 1500:
                trimmed += "\n...[see MEMORY.md for full content]"
            context_parts.append(f"📌 Long-term memory:\n{trimmed}")

        # HOT: Today's daily log
        today_log = self.get_daily_log()
        if today_log:
            trimmed = today_log[:1000]
            if len(today_log) > 1000:
                trimmed += "\n...[more in today's log]"
            context_parts.append(f"📅 Today's activity:\n{trimmed}")

        # WARM/COLD: Vector search
        if self._knowledge_collection and self.embedder and self.embedder.enabled:
            try:
                embedding = self.embedder.embed(query)
                if embedding:
                    results = self._knowledge_collection.query(
                        query_embeddings=[embedding],
                        n_results=k,
                    )
                    if results and results["documents"] and results["documents"][0]:
                        snippets = []
                        for i, doc in enumerate(results["documents"][0]):
                            meta = results["metadatas"][0][i] if results["metadatas"] else {}
                            source = meta.get("source", "unknown")
                            snippets.append(f"[{source}] {doc[:300]}")
                        if snippets:
                            context_parts.append(
                                "🔍 Related knowledge:\n" + "\n---\n".join(snippets)
                            )
            except Exception as exc:
                print(f"[KnowledgeBase] Vector search error: {exc}")

        return "\n\n".join(context_parts) if context_parts else ""

    # ------------------------------------------------------------------
    # Indexing — Build/update vector index over .md files
    # ------------------------------------------------------------------
    def index_all(self) -> int:
        """Index all .md files in memory_dir into the knowledge collection."""
        if not self._knowledge_collection or not self.embedder:
            return 0

        count = 0
        for fname in os.listdir(self.memory_dir):
            if fname.endswith(".md"):
                path = os.path.join(self.memory_dir, fname)
                if path not in self._indexed_files:
                    count += self._index_file(path)
                    self._indexed_files.add(path)
        return count

    def _index_file(self, path: str) -> int:
        """Index a single .md file by chunking and embedding."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return 0

        if not content.strip():
            return 0

        fname = os.path.basename(path)
        chunks = self._chunk_text(content, chunk_size=500)
        count = 0

        for i, chunk in enumerate(chunks):
            chunk_id = f"{fname}::chunk_{i}"
            embedding = self.embedder.embed(chunk)
            if embedding:
                try:
                    self._knowledge_collection.upsert(
                        ids=[chunk_id],
                        documents=[chunk],
                        embeddings=[embedding],
                        metadatas=[{"source": fname, "chunk_index": i}],
                    )
                    count += 1
                except Exception as exc:
                    print(f"[KnowledgeBase] Index error for {chunk_id}: {exc}")

        return count

    def _index_text(self, text: str, source: str = "inline", category: str = "general") -> None:
        """Index a single text snippet."""
        if not self._knowledge_collection or not self.embedder:
            return
        try:
            embedding = self.embedder.embed(text)
            if embedding:
                chunk_id = f"{source}::{category}::{int(time.time())}"
                self._knowledge_collection.upsert(
                    ids=[chunk_id],
                    documents=[text],
                    embeddings=[embedding],
                    metadatas=[{"source": source, "category": category}],
                )
        except Exception as exc:
            print(f"[KnowledgeBase] Inline index error: {exc}")

    # ------------------------------------------------------------------
    # Monthly compaction
    # ------------------------------------------------------------------
    def compact_month(self, year: int, month: int) -> Optional[str]:
        """
        Summarize all daily logs for a given month into a single monthly summary.
        Returns path to the summary file, or None if no logs found.
        """
        prefix = f"{year:04d}-{month:02d}"
        daily_contents = []

        for fname in sorted(os.listdir(self.memory_dir)):
            if fname.startswith(prefix) and fname.endswith(".md") and re.match(r"\d{4}-\d{2}-\d{2}\.md$", fname):
                path = os.path.join(self.memory_dir, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        daily_contents.append(f"## {fname.replace('.md', '')}\n{f.read()}")
                except Exception:
                    continue

        if not daily_contents:
            return None

        summary_path = os.path.join(self.memory_dir, f"{prefix}-summary.md")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"# Monthly Summary — {prefix}\n\n")
            f.write("\n\n---\n\n".join(daily_contents))

        return summary_path

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks by paragraph, respecting chunk_size."""
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""

        for para in paragraphs:
            if len(current) + len(para) + 2 > chunk_size and current:
                chunks.append(current.strip())
                current = para
            else:
                current += "\n\n" + para if current else para

        if current.strip():
            chunks.append(current.strip())

        return chunks if chunks else [text[:chunk_size]]

    def _create_default_memory_file(self) -> None:
        """Create a starter MEMORY.md."""
        content = """# JARVIS Long-Term Memory

## User Preferences
- Language: English/Spanish bilingual

## Key Decisions

## Project Context

## Learned Facts
"""
        with open(self.memory_file, "w", encoding="utf-8") as f:
            f.write(content)

    def status(self) -> Dict:
        count = self._knowledge_collection.count() if self._knowledge_collection else 0
        return {
            "memory_dir": self.memory_dir,
            "memory_file_exists": os.path.exists(self.memory_file),
            "daily_logs": len(self.list_daily_logs()),
            "indexed_chunks": count,
            "indexed_files": len(self._indexed_files),
        }
