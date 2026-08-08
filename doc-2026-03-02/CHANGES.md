# JARVIS Agent — Changes & Documentation
**Date**: 2026-03-02  
**Session scope**: Phase 1–5 implementation + Bug fixes  
**Project path**: `C:\Users\HP\Desktop\app-2026-agent\backend`

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [New Files Created](#new-files-created)
3. [Files Modified](#files-modified)
4. [Bug Fixes](#bug-fixes)
5. [Tool Reference (20 tools)](#tool-reference)
6. [Setup Instructions](#setup-instructions)
7. [How to Test](#how-to-test)

---

## Architecture Overview

### Old flow (before this session)
```
User input → IntentRouter → ModuleManager → Module.execute(text)
                                               └─ regex parse text
                                               └─ AI re-parse on failure
                                               └─ run action
```

### New flow (after this session)
```
User input → AgentLoop → Groq function calling → ToolRegistry handler
                 │                                    └─ calls module._method(structured args) directly
                 │                                    └─ NO re-parsing, NO regex on runtime paths
                 └─ ConversationStore (JSONL log)
                 └─ KnowledgeBase (MEMORY.md + ChromaDB)
```

Key architectural decisions:
- **AgentLoop** drives all conversations — max 6 tool-call iterations per turn
- **ToolRegistry** holds 20 structured tool definitions for Groq function calling
- Tool handlers call internal module methods **directly** with structured kwargs — no text re-parsing
- **SharedResources** provides lazy-initialized singletons (AI client, DB, memory, telegram, etc.)

---

## New Files Created

### `src/core/tool_registry.py`
**Purpose**: Defines all 20 tools as Groq-compatible JSON schemas + async handler functions.

**Key design**:
- `get_tools()` — returns list of 20 tool dicts for Groq `tools=` parameter
- `execute_tool(name, args, shared)` — dispatches to the correct handler
- Each tool group is built by a `_build_*_tools()` private method
- Handlers receive `(args: dict, shared: SharedResources)` — fully typed, no string parsing

**Tools by module**:
| Group | Tool names |
|---|---|
| word | `create_word_document`, `read_word_document`, `edit_word_document`, `summarize_word_document`, `toggle_writing_mode` |
| pdf | `read_pdf_document`, `summarize_pdf_document` |
| apa | `create_apa_report` |
| file_ops | `create_folder`, `create_file`, `delete_file`, `delete_folder`, `search_files` |
| knowledge | `remember_fact`, `recall_memory`, `read_full_memory` |
| web | `web_search`, `fetch_webpage` |
| telegram | `send_telegram_message`, `send_telegram_notification` |

---

### `src/core/agent_loop.py`
**Purpose**: Multi-step autonomous agent, powered by Groq function calling.

**Key behaviour**:
- Max **6 iterations** per user turn (prevents infinite loops)
- On each iteration: sends messages + tools to Groq → if tool call returned → executes tool → appends result → loops
- Conversation history: last **20 messages** (sliding window)
- Integrates `ConversationStore` (logging) and `KnowledgeBase` (memory injection)
- System prompt includes injected memory context from KB on each turn

**Public API**:
```python
loop = AgentLoop(shared)
response = await loop.chat(user_message)
loop.clear_history()
```

---

### `src/core/conversation_store.py`
**Purpose**: Append-only JSONL transcript of all conversations.

**Storage**:
- **Runtime log**: `memory/conversation_log.jsonl` — one JSON object per line
- **Daily exports**: `memory/daily/YYYY-MM-DD.md` — human-readable Markdown
- Loads last **200 entries** on startup for context continuity

**Public API**:
```python
store = ConversationStore()
store.add(role="user", content="...", metadata={})
entries = store.get_recent(n=50)
store.export_daily_log()
```

---

### `src/core/knowledge_base.py`
**Purpose**: Hybrid long-term memory — MEMORY.md (hot) + ChromaDB (cold).

**Tiered retrieval**:
1. **HOT** — reads `memory/MEMORY.md` + today's conversation log directly
2. **COLD** — vector similarity search in ChromaDB `knowledge` collection

**Public API**:
```python
kb = KnowledgeBase(shared)
await kb.remember("fact text", category="personal")
results = await kb.recall("query", n=5)
full = await kb.read_full_memory()
```

**ChromaDB collection**: `knowledge` (separate from the existing 49-conversation `conversations` collection)

---

### `src/modules/web_search_module.py`
**Purpose**: Web search without mandatory API key.

**Strategy**:
1. DuckDuckGo HTML scraping via `httpx` (primary — no key needed)
2. Brave Search API via `httpx` (if `BRAVE_API_KEY` set in `.env`)
3. `urllib` fallback if `httpx` not installed

**Tools exposed**: `web_search(query, n_results)`, `fetch_webpage(url)`

---

### `src/channels/telegram_bot.py`
**Purpose**: Send messages and notifications to Telegram.

**Requirements** (in `.env`):
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

**Tools exposed**: `send_telegram_message(text)`, `send_telegram_notification(title, body, urgency)`

---

### `src/channels/__init__.py`
Empty package marker for the `channels/` directory.

---

## Files Modified

### `src/main_chat.py`
**Changes**:
- Replaced `IntentRouter` / `ModuleManager` startup with `AgentLoop(shared)`
- Main loop now calls `await agent_loop.chat(user_input)`
- Added `clear` command to reset conversation history in-session
- Kept Spanish/English language detection and coloured terminal output

---

### `src/core/shared_resources.py`
**Changes**:
- Added lazy-initialized properties: `telegram`, `conversation_store`, `knowledge_base`
- Added `_telegram`, `_conversation_store`, `_knowledge_base = None` to `__init__`
- Updated `status()` to include all 6 lazy components
- Each property initializes on first access and caches the instance

---

### `src/modules/word_module.py`
**Change: `_resolve_existing_word_path` rewritten (lines ~422–470)**

Old behaviour — exact match only:
```python
candidate = os.path.join(location, filename)
if os.path.exists(candidate):
    return candidate
# ... return fallback path without searching
```

New behaviour — fuzzy partial-name match:
```python
stem_lower = os.path.splitext(filename)[0].lower()   # "fase 1 de hefesto"
filename_with_ext = stem + ".docx"

for d in search_dirs:
    # 1) exact match first
    candidate = os.path.join(d, filename_with_ext)
    if os.path.exists(candidate):
        return candidate
    # 2) fuzzy: any .docx in this folder whose name contains the stem
    if os.path.isdir(d):
        for fname in os.listdir(d):
            if fname.lower().endswith('.docx') and stem_lower in fname.lower():
                return os.path.join(d, fname)
```

This fixes the case where the file on disk is `"📊 FASE 1 DE HEFESTO.docx"` but the user says `"FASE 1 DE HEFESTO"` — the emoji prefix is ignored and the file is found.

---

### `src/modules/pdf_module.py`
**Change: `_resolve_existing_pdf_path` rewritten (lines ~239–283)**

Same fuzzy-match pattern as `word_module.py` above, but for `.pdf` files.

Old: exact `os.path.join(location, filename)` only.  
New: stem extraction + `os.listdir` loop scanning for partial `.pdf` filename match.

---

### `requirements.txt`
**Additions**:
```
httpx          # async HTTP for web search + telegram
chromadb       # vector database for long-term memory
sentence-transformers  # embeddings for ChromaDB
python-telegram-bot    # Telegram bot API (optional)
```

---

## Bug Fixes

### Bug 1 — Double-Parsing (tool_registry.py)
**Symptom**: Slow responses, occasional failures when reading/writing files via tools.

**Root cause**: Tool handlers were building a natural-language text string and passing it back through `module.execute()`, which re-ran regex parsing and AI fallback parsing — work already done by Groq.

**Fix**: All Word and PDF tool handlers in `_build_word_tools()` and `_build_pdf_tools()` now call the internal methods directly:
```python
# Before (bad)
intent = {"type": "word", "text": f"read word file {args['filename']} from {args['location']}"}
return await m.execute(intent, shared)

# After (good)
m = await _get_module(shared)
return await m._read_word_doc(
    filename=args.get("filename", ""),
    location=args.get("location", ""),
    language=args.get("language", "es")
)
```

---

### Bug 2 — Exact Filename Mismatch
**Symptom**: `"📊 FASE 1 DE HEFESTO.docx"` not found when user says `"FASE 1 DE HEFESTO"`.

**Root cause**: `_resolve_existing_word_path` only checked `os.path.join(location, filename + ".docx")` — exact match. Any prefix (emoji, date, etc.) on disk would cause a miss.

**Fix**: Fuzzy `os.listdir()` fallback — see "Files Modified → word_module.py" above.  
Same fix applied to `_resolve_existing_pdf_path` in `pdf_module.py`.

---

### Bug 3 — Wrong Parameter Name in summarize_word
**Symptom**: `TypeError: _summarize_word_doc() got an unexpected keyword argument 'source_name'`

**Root cause**: Old handler used `source_name=args.get("filename")` but the method signature is `def _summarize_word_doc(self, filename, location, output_name, language, shared)`.

**Fix**: Changed to `filename=args.get("filename", "")`.

---

## Tool Reference

### Word Documents
| Tool | Required args | Optional args |
|---|---|---|
| `read_word_document` | `filename`, `location` | `language` |
| `create_word_document` | `filename`, `location`, `content` | `language` |
| `edit_word_document` | `filename`, `location`, `new_content` | `replace` (bool), `language` |
| `summarize_word_document` | `filename`, `location` | `output_name`, `language` |
| `toggle_writing_mode` | `mode` (`on`/`off`) | — |

### PDF Documents
| Tool | Required args | Optional args |
|---|---|---|
| `read_pdf_document` | `filename`, `location` | `language` |
| `summarize_pdf_document` | `filename`, `location` | `output_name`, `language` |

### Knowledge Base
| Tool | Required args | Optional args |
|---|---|---|
| `remember_fact` | `fact`, `category` | — |
| `recall_memory` | `query` | `n_results` |
| `read_full_memory` | — | — |

### Web
| Tool | Required args |
|---|---|
| `web_search` | `query` |
| `fetch_webpage` | `url` |

### Telegram
| Tool | Required args | Optional args |
|---|---|---|
| `send_telegram_message` | `text` | — |
| `send_telegram_notification` | `title`, `body` | `urgency` |

### File Operations
| Tool | Required args |
|---|---|
| `create_folder` | `path` |
| `create_file` | `path`, `content` |
| `delete_file` | `path` |
| `delete_folder` | `path` |
| `search_files` | `query`, `directory` |

---

## Setup Instructions

### 1. Install dependencies
```powershell
cd "C:\Users\HP\Desktop\app-2026-agent\backend"
pip install -r requirements.txt
```

### 2. Configure `.env`
```env
GROQ_API_KEY=your_groq_key

# Optional — only needed for Telegram tools
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Optional — only needed for Brave Search (DuckDuckGo works without this)
BRAVE_API_KEY=your_brave_key
```

### 3. Run JARVIS
```powershell
cd "C:\Users\HP\Desktop\app-2026-agent\backend\src"
python main_chat.py
```

---

## How to Test

### Test file read with fuzzy filename
```
# File on disk: "📊 FASE 1 DE HEFESTO.docx" in C:\Users\HP\Desktop\basura\prove
lee el archivo FASE 1 DE HEFESTO de C:\Users\HP\Desktop\basura\prove
```
Expected: JARVIS reads the file and shows its content despite the emoji prefix mismatch.

### Test memory tools
```
recuerda que mi nombre es HP y uso Windows 11
¿cuál es mi nombre?
```
Expected: First turn stores the fact; second turn retrieves it from KnowledgeBase.

### Test web search
```
busca en internet las últimas noticias sobre inteligencia artificial
```
Expected: DuckDuckGo results returned and summarized.

### Test Telegram (requires .env config)
```
envíame una notificación por telegram que diga "JARVIS está funcionando"
```

### Test multi-step agent
```
busca en internet qué es ChromaDB y guarda un resumen en un archivo Word llamado chromadb_notes en el escritorio
```
Expected: AgentLoop runs 2+ iterations — web_search → create_word_document.

### Test conversation continuity
Start JARVIS, have a conversation, close it, restart. Ask about the previous conversation — KnowledgeBase should recall it.

---

*Documentation generated 2026-03-02 — JARVIS Agent development session.*
