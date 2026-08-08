"""
Shared Resources - OpenClaw Pattern
Single instances of heavy objects shared across all modules
Prevents memory bloat from duplicate AI clients, databases, etc.
"""
import os
import json
from typing import Optional


class SharedResources:
    """
    Shared across all modules to save memory (OpenClaw pattern)
    
    Before: Each module creates its own AI client, memory, DB
             8 modules × 80 MB = 640 MB ❌
    
    After: Single shared instances
           1 shared resource = 80 MB ✅
    
    Savings: 560 MB!
    """
    
    def __init__(self):
        # Lazy-loaded (only created when first accessed)
        self._ai = None
        self._memory = None
        self._db = None
        self._config = None
        self._logger = None
        self._conversation_store = None
        self._knowledge_base = None
        self._telegram = None
        self._session_state = {}
        self._session_state_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'jarvis_session_state.json')
        )
        self._load_session_state()
        
        print("✓ Shared resources container created (lazy initialization)")
    
    @property
    def ai(self):
        """Groq AI Brain - loaded once, shared by all modules"""
        if self._ai is None:
            from src.ai.brain import AIBrain
            self._ai = AIBrain()
            print("  ↳ AI Brain loaded (shared instance)")
        return self._ai
    
    @property
    def memory(self):
        """Memory Manager (ChromaDB + Embeddings) - loaded once, shared"""
        if self._memory is None:
            from src.ai.memory import MemoryManager
            from src.ai.embeddings import EmbeddingClient
            from src.db.chroma_store import ChromaVectorStore
            
            embedder = EmbeddingClient()
            chroma_store = ChromaVectorStore()
            self._memory = MemoryManager(embedder, chroma_store)
            print("  ↳ Memory system loaded (shared instance)")
        return self._memory
    
    @property
    def db(self):
        """Database - loaded once, shared (if needed later)"""
        if self._db is None:
            # For now, we use ChromaDB through memory
            # Add SQLite here if needed for structured data
            print("  ↳ Database loaded (shared instance)")
            self._db = None  # Placeholder
        return self._db

    @property
    def conversation_store(self):
        """Conversation transcript store - JSONL append-only log"""
        if self._conversation_store is None:
            from src.core.conversation_store import ConversationStore
            self._conversation_store = ConversationStore()
            print("  ↳ Conversation Store loaded (shared instance)")
        return self._conversation_store

    @property
    def knowledge_base(self):
        """Knowledge base - hybrid .md files + ChromaDB vector search"""
        if self._knowledge_base is None:
            from src.core.knowledge_base import KnowledgeBase
            # Reuse the same embedder and chroma client from memory
            embedder = None
            chroma = None
            mem = self.memory
            if mem and mem.enabled:
                embedder = mem.embedder
                chroma = mem.store
            self._knowledge_base = KnowledgeBase(
                embedder=embedder,
                chroma_store=chroma,
            )
            print("  ↳ Knowledge Base loaded (shared instance)")
        return self._knowledge_base

    @property
    def telegram(self):
        """Telegram channel for notifications and remote commands"""
        if self._telegram is None:
            from src.channels.telegram_bot import TelegramChannel
            self._telegram = TelegramChannel()
            print("  ↳ Telegram Channel loaded (shared instance)")
        return self._telegram
    
    @property
    def config(self):
        """Configuration - always loaded"""
        if self._config is None:
            self._config = {
                'model': 'llama-3.3-70b-versatile',
                'temperature': 0.7,
                'max_tokens': 500,
                'language': 'en'
            }
        return self._config
    
    @property
    def logger(self):
        """Logger - always loaded"""
        if self._logger is None:
            import logging
            self._logger = logging.getLogger('JARVIS')
            self._logger.setLevel(logging.INFO)
        return self._logger

    @property
    def session_state(self):
        """Lightweight in-memory state for recent actions"""
        return self._session_state

    def _load_session_state(self):
        """Load persisted session state from disk if available."""
        try:
            if os.path.exists(self._session_state_file):
                with open(self._session_state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._session_state = data
                        print("  ↳ Session state loaded")
        except Exception:
            self._session_state = {}

    def save_session_state(self):
        """Persist session state to disk."""
        try:
            with open(self._session_state_file, 'w', encoding='utf-8') as f:
                json.dump(self._session_state, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def status(self):
        """Get status of loaded resources"""
        return {
            'ai_loaded': self._ai is not None,
            'memory_loaded': self._memory is not None,
            'db_loaded': self._db is not None,
            'conversation_store_loaded': self._conversation_store is not None,
            'knowledge_base_loaded': self._knowledge_base is not None,
            'telegram_loaded': self._telegram is not None,
        }
