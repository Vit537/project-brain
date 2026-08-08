"""
Conversation Store - Persistent Transcript Storage
Stores every user/assistant exchange in a JSONL file for full history.
Provides sliding window of recent turns for context injection.

Part of the hybrid memory architecture:
- conversation_log.jsonl → full transcript (append-only)
- ChromaDB → semantic search over past interactions
- This module → recent history retrieval + transcript persistence
"""
import os
import json
import time
from typing import List, Dict, Optional
from datetime import datetime


class ConversationStore:
    """
    Append-only JSONL transcript store.

    Each line is a JSON object:
    {
        "timestamp": "2026-02-28T14:30:00",
        "role": "user" | "assistant",
        "content": "...",
        "language": "en" | "es",
        "tools_called": ["create_word_document"],   # only for assistant
        "latency_ms": 1234                          # only for assistant
    }
    """

    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            log_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..', 'memory')
            )
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        self.log_file = os.path.join(self.log_dir, "conversation_log.jsonl")
        self._cache: List[Dict] = []
        self._load_recent()
        print(f"✓ Conversation Store ready ({len(self._cache)} recent entries)")

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------
    def append(
        self,
        role: str,
        content: str,
        language: str = "en",
        tools_called: Optional[List[str]] = None,
        latency_ms: Optional[int] = None,
    ) -> None:
        """Append one message to the transcript."""
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "role": role,
            "content": content,
            "language": language,
        }
        if tools_called:
            entry["tools_called"] = tools_called
        if latency_ms is not None:
            entry["latency_ms"] = latency_ms

        # Write to disk (append)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as exc:
            print(f"[ConversationStore] Write error: {exc}")

        # Update in-memory cache
        self._cache.append(entry)
        # Keep cache bounded
        if len(self._cache) > 200:
            self._cache = self._cache[-200:]

    def store_turn(
        self,
        user_input: str,
        assistant_response: str,
        language: str = "en",
        tools_called: Optional[List[str]] = None,
        latency_ms: Optional[int] = None,
    ) -> None:
        """Convenience: store a full user+assistant turn."""
        self.append("user", user_input, language)
        self.append(
            "assistant",
            assistant_response,
            language,
            tools_called=tools_called,
            latency_ms=latency_ms,
        )

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------
    def get_recent(self, n: int = 20) -> List[Dict]:
        """Return the last N messages from the cache."""
        return self._cache[-n:]

    def get_recent_as_messages(self, n: int = 20) -> List[Dict[str, str]]:
        """Return recent messages in OpenAI chat format [{role, content}]."""
        return [
            {"role": e["role"], "content": e["content"]}
            for e in self._cache[-n:]
        ]

    def get_today_entries(self) -> List[Dict]:
        """Return all entries from today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return [e for e in self._cache if e.get("timestamp", "").startswith(today)]

    def search_transcripts(self, query: str, limit: int = 20) -> List[Dict]:
        """Simple substring search over cached transcripts."""
        query_lower = query.lower()
        results = []
        for entry in reversed(self._cache):
            if query_lower in entry.get("content", "").lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    # ------------------------------------------------------------------
    # Daily log export (for knowledge base)
    # ------------------------------------------------------------------
    def export_daily_log(self, date_str: Optional[str] = None) -> str:
        """
        Export a day's conversations as a markdown file.
        Returns the file path of the exported .md file.
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        entries = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if entry.get("timestamp", "").startswith(date_str):
                            entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass

        if not entries:
            return ""

        # Build markdown
        md_lines = [f"# JARVIS Conversation Log — {date_str}\n"]
        for e in entries:
            ts = e.get("timestamp", "")
            role = e.get("role", "unknown")
            content = e.get("content", "")
            tools = e.get("tools_called", [])

            time_part = ts.split("T")[1] if "T" in ts else ts
            prefix = "👤 User" if role == "user" else "🤖 JARVIS"
            md_lines.append(f"### [{time_part}] {prefix}")
            md_lines.append(content)
            if tools:
                md_lines.append(f"*Tools: {', '.join(tools)}*")
            md_lines.append("")

        md_path = os.path.join(self.log_dir, f"{date_str}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return md_path

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------
    def total_entries(self) -> int:
        """Count total lines in the log file."""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except FileNotFoundError:
            return 0

    def status(self) -> Dict:
        return {
            "log_file": self.log_file,
            "cached_entries": len(self._cache),
            "total_on_disk": self.total_entries(),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _load_recent(self, max_lines: int = 200) -> None:
        """Load the last N lines from the JSONL file into cache."""
        if not os.path.exists(self.log_file):
            return

        try:
            lines = []
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        lines.append(line)

            # Take last max_lines
            for raw in lines[-max_lines:]:
                try:
                    self._cache.append(json.loads(raw))
                except json.JSONDecodeError:
                    continue
        except Exception as exc:
            print(f"[ConversationStore] Load error: {exc}")
