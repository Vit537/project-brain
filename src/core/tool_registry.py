"""
Tool Registry - Structured Tool Definitions for Agent Loop
Converts JARVIS modules into LLM-callable tools with JSON schemas.
Inspired by OpenAI/Groq function calling format.
"""
from typing import Dict, List, Any, Callable, Optional
import json


class ToolDefinition:
    """A single tool the LLM can call."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
        *,
        module_name: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters  # JSON Schema for function args
        self.handler = handler        # async callable(args_dict, shared) -> str
        self.module_name = module_name

    def to_openai_schema(self) -> Dict[str, Any]:
        """Return Groq/OpenAI-compatible function tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Central registry of all tools available to the agent loop."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        print("✓ Tool Registry created")

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------
    def register(self, tool: ToolDefinition) -> None:
        self._tools[tool.name] = tool
        print(f"  ↳ Registered tool: {tool.name}")

    def register_many(self, tools: List[ToolDefinition]) -> None:
        for t in tools:
            self.register(t)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------
    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_names(self) -> List[str]:
        return list(self._tools.keys())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Return all tools in Groq/OpenAI function-calling format."""
        return [t.to_openai_schema() for t in self._tools.values()]

    def get_tools_for_context(self, user_input: str, report_active: bool = False) -> List[Dict[str, Any]]:
        """Return a filtered subset of tools relevant to the user's request.
        
        This reduces the tool count sent to the LLM, which prevents
        Groq from generating malformed tool calls when overwhelmed.
        """
        text = user_input.lower()
        selected: Dict[str, ToolDefinition] = {}

        # Always include these core tools
        core_tools = {"read_word_document", "create_word_document", "edit_word_document",
                       "search_files", "read_full_memory"}

        # Keyword → tool module mapping
        keyword_groups = {
            "report": {"setup_report_project", "create_report_template", "write_report_section",
                        "create_cover_page", "add_sprint_section", "create_user_story_table",
                        "add_daily_scrum_table", "add_backlog_table", "analyze_report_progress",
                        "add_sprint_retrospective"},
            "word": {"create_word_document", "read_word_document", "edit_word_document",
                     "summarize_word_document", "toggle_writing_mode"},
            "pdf": {"read_pdf_document", "summarize_pdf_document"},
            "apa": {"create_apa_report"},
            "file": {"search_files", "create_folder", "create_file",
                     "delete_file", "delete_folder"},
            "memory": {"remember_fact", "recall_memory", "read_full_memory"},
            "web": {"web_search", "fetch_webpage"},
            "telegram": {"send_telegram_message", "send_telegram_notification"},
        }

        # Detect relevant groups from user input
        trigger_words = {
            "report": ["reporte", "report", "sprint", "scrum", "backlog", "historia de usuario",
                        "user story", "portada", "cover", "retrospect", "daily scrum",
                        "sección", "section", "plantilla", "template", "hu0", "hu1"],
            "word": ["word", "docx", "documento", "document", "leer", "read", "crear", "create",
                     "editar", "edit", "escribir", "write", "archivo", "file"],
            "pdf": ["pdf"],
            "apa": ["apa", "citation", "cita", "referencia"],
            "file": ["carpeta", "folder", "archivos", "files", "lista", "delete", "eliminar",
                     "rename", "renombrar", "md", "markdown"],
            "memory": ["memoria", "memory", "recuerda", "remember"],
            "web": ["busca", "search", "internet", "web", "noticias", "news"],
            "telegram": ["telegram", "mensaje", "enviar", "send"],
        }

        active_groups = set()
        for group, words in trigger_words.items():
            if any(w in text for w in words):
                active_groups.add(group)

        # If report is configured, always include report tools
        if report_active:
            active_groups.add("report")
            active_groups.add("word")

        # If nothing specific detected, include word + file (most common)
        if not active_groups:
            active_groups = {"word", "file"}

        # Collect tools from active groups
        for group in active_groups:
            for tool_name in keyword_groups.get(group, set()):
                if tool_name in self._tools:
                    selected[tool_name] = self._tools[tool_name]

        # Add core tools always
        for name in core_tools:
            if name in self._tools:
                selected[name] = self._tools[name]

        return [t.to_openai_schema() for t in selected.values()]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------
    async def execute(self, name: str, arguments: Dict[str, Any], shared) -> str:
        """Execute a tool by name with given arguments."""
        tool = self._tools.get(name)
        if tool is None:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            result = await tool.handler(arguments, shared)
            return result if isinstance(result, str) else json.dumps(result)
        except Exception as exc:
            return json.dumps({"error": f"Tool '{name}' failed: {exc}"})

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------
    def status(self) -> Dict[str, Any]:
        return {
            "total_tools": len(self._tools),
            "tools": [
                {"name": t.name, "module": t.module_name}
                for t in self._tools.values()
            ],
        }


# ======================================================================
# Built-in tool definitions for existing modules
# ======================================================================

def _build_word_tools():
    """Tool definitions wrapping WordModule capabilities — calls internal methods directly."""
    from src.modules.word_module import WordModule

    _module = None

    async def _get_module(shared) -> WordModule:
        nonlocal _module
        if _module is None:
            _module = WordModule("word")
            await _module.initialize()
        # always sync shared state so the module can update last_word_path
        _module._shared_state = shared.session_state
        return _module

    # --- create_word_document ---
    async def create_word(args: Dict, shared) -> str:
        m = await _get_module(shared)
        return await m._create_word_doc(
            filename=args.get("filename", ""),
            location=args.get("location", "desktop"),
            content=args.get("content", ""),
            language=args.get("language", "en"),
        )

    # --- read_word_document ---
    async def read_word(args: Dict, shared) -> str:
        m = await _get_module(shared)
        return await m._read_word_doc(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            language=args.get("language", "en"),
        )

    # --- edit_word_document ---
    async def edit_word(args: Dict, shared) -> str:
        m = await _get_module(shared)
        if args.get("replace"):
            return await m._replace_word_doc(
                filename=args.get("filename", ""),
                location=args.get("location", ""),
                new_content=args.get("content", ""),
                language=args.get("language", "en"),
            )
        return await m._edit_word_doc(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            new_content=args.get("content", ""),
            language=args.get("language", "en"),
        )

    # --- summarize_word_document ---
    async def summarize_word(args: Dict, shared) -> str:
        m = await _get_module(shared)
        return await m._summarize_word_doc(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            output_name=args.get("output_filename"),
            language=args.get("language", "en"),
            shared=shared,
        )

    # --- toggle_writing_mode ---
    async def toggle_writing_mode(args: Dict, shared) -> str:
        m = await _get_module(shared)
        enable = args.get("enable", True)
        lang = args.get("language", "en")
        action = "start" if enable else "stop"
        intent = {
            "type": "word",
            "text": f"{action} writing mode",
            "language": lang,
        }
        return await m.execute(intent, shared)

    return [
        ToolDefinition(
            name="create_word_document",
            description="Create a new Microsoft Word (.docx) file with optional content.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the Word file (without .docx extension)"},
                    "location": {"type": "string", "description": "Folder path or shortcut like 'desktop', 'documents', 'downloads'"},
                    "content": {"type": "string", "description": "Initial text content to write in the document"},
                    "language": {"type": "string", "enum": ["en", "es"], "description": "Response language"},
                },
                "required": ["filename"],
            },
            handler=create_word,
            module_name="word",
        ),
        ToolDefinition(
            name="read_word_document",
            description="Read and display the content of an existing Word (.docx) file.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the Word file to read"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename"],
            },
            handler=read_word,
            module_name="word",
        ),
        ToolDefinition(
            name="edit_word_document",
            description="Edit (append or replace) content in an existing Word document.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the Word file"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "content": {"type": "string", "description": "Text to add or replace"},
                    "replace": {"type": "boolean", "description": "True to replace all content, False to append"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename", "content"],
            },
            handler=edit_word,
            module_name="word",
        ),
        ToolDefinition(
            name="summarize_word_document",
            description="Generate a chunked AI summary of a large Word document using map-reduce.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the Word file to summarize"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "output_filename": {"type": "string", "description": "Optional name for the summary output file"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename"],
            },
            handler=summarize_word,
            module_name="word",
        ),
        ToolDefinition(
            name="toggle_writing_mode",
            description="Enable or disable continuous writing mode that streams conversation lines to the last Word document.",
            parameters={
                "type": "object",
                "properties": {
                    "enable": {"type": "boolean", "description": "True to start, False to stop writing mode"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["enable"],
            },
            handler=toggle_writing_mode,
            module_name="word",
        ),
    ]


def _build_pdf_tools():
    """Tool definitions wrapping PDFModule capabilities — calls internal methods directly."""
    from src.modules.pdf_module import PDFModule

    _module = None

    async def _get_module(shared) -> PDFModule:
        nonlocal _module
        if _module is None:
            _module = PDFModule("pdf")
            await _module.initialize()
        _module._shared_state = shared.session_state
        return _module

    async def read_pdf(args: Dict, shared) -> str:
        m = await _get_module(shared)
        return await m._read_pdf(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            language=args.get("language", "en"),
        )

    async def summarize_pdf(args: Dict, shared) -> str:
        m = await _get_module(shared)
        return await m._summarize_pdf(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            output_name=args.get("output_filename"),
            language=args.get("language", "en"),
            shared=shared,
        )

    return [
        ToolDefinition(
            name="read_pdf_document",
            description="Read and extract text content from a PDF file.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the PDF file"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename"],
            },
            handler=read_pdf,
            module_name="pdf",
        ),
        ToolDefinition(
            name="summarize_pdf_document",
            description="Generate a chunked AI summary of a large PDF document using map-reduce.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the PDF file to summarize"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "output_filename": {"type": "string", "description": "Optional name for the summary output file"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename"],
            },
            handler=summarize_pdf,
            module_name="pdf",
        ),
    ]


def _build_apa_tools():
    """Tool definitions wrapping APAModule capabilities."""
    from src.modules.apa_module import APAModule

    _module = None

    async def _get_module():
        nonlocal _module
        if _module is None:
            _module = APAModule("apa")
            await _module.initialize()
        return _module

    async def create_apa(args: Dict, shared) -> str:
        m = await _get_module()
        parts = [f"create apa report called {args['filename']}"]
        if args.get("title"):
            parts.append(f"with title {args['title']}")
        if args.get("author"):
            parts.append(f"by {args['author']}")
        if args.get("institution"):
            parts.append(f"from {args['institution']}")
        if args.get("location"):
            parts.append(f"on {args['location']}")
        intent = {
            "type": "apa",
            "text": " ".join(parts),
            "language": args.get("language", "en"),
        }
        return await m.execute(intent, shared)

    return [
        ToolDefinition(
            name="create_apa_report",
            description="Create a new APA-formatted thesis template with title page, table of contents, and section stubs.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name for the APA report file"},
                    "title": {"type": "string", "description": "Report title"},
                    "author": {"type": "string", "description": "Author name"},
                    "institution": {"type": "string", "description": "University or institution name"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename"],
            },
            handler=create_apa,
            module_name="apa",
        ),
    ]


def _build_file_ops_tools():
    """Tool definitions wrapping FileOpsModule capabilities."""
    from src.modules.file_ops_module import FileOpsModule

    _module = None

    async def _get_module():
        nonlocal _module
        if _module is None:
            _module = FileOpsModule("file_ops")
            await _module.initialize()
        return _module

    async def create_folder(args: Dict, shared) -> str:
        m = await _get_module()
        intent = {
            "type": "folder",
            "text": f"create folder {args['name']} in {args['location']}",
            "language": args.get("language", "en"),
        }
        return await m.execute(intent, shared)

    async def create_file(args: Dict, shared) -> str:
        m = await _get_module()
        text = f"create file {args['name']} in {args['location']}"
        if args.get("content"):
            text += f" with content {args['content']}"
        intent = {
            "type": "file",
            "text": text,
            "language": args.get("language", "en"),
        }
        return await m.execute(intent, shared)

    async def delete_file(args: Dict, shared) -> str:
        m = await _get_module()
        intent = {
            "type": "file",
            "text": f"delete file {args['name']} from {args['location']}",
            "language": args.get("language", "en"),
        }
        return await m.execute(intent, shared)

    async def delete_folder(args: Dict, shared) -> str:
        m = await _get_module()
        intent = {
            "type": "folder",
            "text": f"delete folder {args['name']} from {args['location']}",
            "language": args.get("language", "en"),
        }
        return await m.execute(intent, shared)

    async def search_files(args: Dict, shared) -> str:
        m = await _get_module()
        intent = {
            "type": "file",
            "text": f"search file {args['query']} in {args.get('location', 'documents')}",
            "language": args.get("language", "en"),
        }
        return await m.execute(intent, shared)

    return [
        ToolDefinition(
            name="create_folder",
            description="Create a new folder/directory at the specified location.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Folder name"},
                    "location": {"type": "string", "description": "Parent directory path or shortcut"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["name", "location"],
            },
            handler=create_folder,
            module_name="file_ops",
        ),
        ToolDefinition(
            name="create_file",
            description="Create a new file with optional content.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "File name with extension"},
                    "location": {"type": "string", "description": "Directory path or shortcut"},
                    "content": {"type": "string", "description": "Optional initial content"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["name", "location"],
            },
            handler=create_file,
            module_name="file_ops",
        ),
        ToolDefinition(
            name="delete_file",
            description="Delete a file from the specified location.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "File name"},
                    "location": {"type": "string", "description": "Directory path or shortcut"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["name", "location"],
            },
            handler=delete_file,
            module_name="file_ops",
        ),
        ToolDefinition(
            name="delete_folder",
            description="Delete a folder and its contents.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Folder name"},
                    "location": {"type": "string", "description": "Parent directory path or shortcut"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["name", "location"],
            },
            handler=delete_folder,
            module_name="file_ops",
        ),
        ToolDefinition(
            name="search_files",
            description="Search for files by name in a directory.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term or file name pattern"},
                    "location": {"type": "string", "description": "Directory to search in"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["query"],
            },
            handler=search_files,
            module_name="file_ops",
        ),
    ]


def build_all_tools() -> List[ToolDefinition]:
    """Build and return all tool definitions for the agent loop."""
    tools = []
    tools.extend(_build_word_tools())
    tools.extend(_build_pdf_tools())
    tools.extend(_build_apa_tools())
    tools.extend(_build_file_ops_tools())
    tools.extend(_build_memory_tools())
    tools.extend(_build_web_search_tools())
    tools.extend(_build_telegram_tools())
    tools.extend(_build_report_tools())
    return tools


def _build_memory_tools():
    """Tool definitions for knowledge base read/write."""

    async def remember_fact(args: Dict, shared) -> str:
        """Store a fact in long-term memory (MEMORY.md)."""
        kb = shared.knowledge_base
        fact = args.get("fact", "")
        category = args.get("category", "general")
        if not fact:
            return "No fact provided."
        kb.add_memory(fact, category=category)
        return f"Remembered: {fact} (category: {category})"

    async def recall_memory(args: Dict, shared) -> str:
        """Search long-term memory for relevant facts."""
        kb = shared.knowledge_base
        query = args.get("query", "")
        if not query:
            return "No query provided."
        results = kb.search_memory(query)
        if results:
            return "Found in memory:\n" + "\n".join(results[:10])
        # Fallback to vector search
        context = kb.get_context(query, k=5)
        return context if context else "Nothing found in memory."

    async def read_full_memory(args: Dict, shared) -> str:
        """Read the entire MEMORY.md file."""
        kb = shared.knowledge_base
        content = kb.read_memory()
        return content if content else "MEMORY.md is empty."

    return [
        ToolDefinition(
            name="remember_fact",
            description="Store an important fact, preference, or decision in JARVIS long-term memory (MEMORY.md). Use this when the user tells you something worth remembering.",
            parameters={
                "type": "object",
                "properties": {
                    "fact": {"type": "string", "description": "The fact or information to remember"},
                    "category": {
                        "type": "string",
                        "description": "Category: 'user_preferences', 'key_decisions', 'project_context', 'learned_facts', 'general'",
                        "enum": ["user_preferences", "key_decisions", "project_context", "learned_facts", "general"],
                    },
                },
                "required": ["fact"],
            },
            handler=remember_fact,
            module_name="knowledge_base",
        ),
        ToolDefinition(
            name="recall_memory",
            description="Search JARVIS long-term memory for facts related to a query. Use when the user asks 'do you remember...?' or you need context about past decisions.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for in memory"},
                },
                "required": ["query"],
            },
            handler=recall_memory,
            module_name="knowledge_base",
        ),
        ToolDefinition(
            name="read_full_memory",
            description="Read the entire long-term memory file (MEMORY.md). Use when the user asks to see all stored memories or preferences.",
            parameters={
                "type": "object",
                "properties": {},
            },
            handler=read_full_memory,
            module_name="knowledge_base",
        ),
    ]


def _build_web_search_tools():
    """Tool definitions for web search and page fetching."""
    from src.modules.web_search_module import WebSearchModule

    _search = None

    def _get_search():
        nonlocal _search
        if _search is None:
            _search = WebSearchModule()
        return _search

    async def web_search(args: Dict, shared) -> str:
        """Search the web for information."""
        s = _get_search()
        query = args.get("query", "")
        num = args.get("num_results", 5)
        if not query:
            return "No search query provided."
        results = await s.search(query, num_results=num)
        if not results:
            return f"No results found for: {query}"
        lines = [f"Web search results for: {query}\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r['title']}**")
            lines.append(f"   URL: {r['url']}")
            if r.get("snippet"):
                lines.append(f"   {r['snippet']}")
            lines.append("")
        return "\n".join(lines)

    async def fetch_webpage(args: Dict, shared) -> str:
        """Fetch and read a web page."""
        s = _get_search()
        url = args.get("url", "")
        max_chars = args.get("max_chars", 5000)
        if not url:
            return "No URL provided."
        content = await s.fetch_page(url, max_chars=max_chars)
        return content

    return [
        ToolDefinition(
            name="web_search",
            description="Search the internet for information using DuckDuckGo or Brave Search. Use this when the user asks about current events, facts you don't know, or anything requiring web research.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "num_results": {"type": "integer", "description": "Number of results (default 5, max 10)"},
                },
                "required": ["query"],
            },
            handler=web_search,
            module_name="web_search",
        ),
        ToolDefinition(
            name="fetch_webpage",
            description="Fetch and extract text content from a specific web page URL. Use after web_search to read a specific result in detail.",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The full URL to fetch"},
                    "max_chars": {"type": "integer", "description": "Maximum characters to return (default 5000)"},
                },
                "required": ["url"],
            },
            handler=fetch_webpage,
            module_name="web_search",
        ),
    ]


def _build_telegram_tools():
    """Tool definitions for Telegram notifications."""

    async def send_telegram(args: Dict, shared) -> str:
        """Send a message via Telegram."""
        tg = shared.telegram
        if not tg.enabled:
            return "Telegram is not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
        message = args.get("message", "")
        if not message:
            return "No message provided."
        success = await tg.send_message(message)
        return "Message sent via Telegram." if success else "Failed to send Telegram message."

    async def send_telegram_notification(args: Dict, shared) -> str:
        """Send a formatted notification via Telegram."""
        tg = shared.telegram
        if not tg.enabled:
            return "Telegram is not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
        title = args.get("title", "Notification")
        body = args.get("body", "")
        if not body:
            return "No notification body provided."
        success = await tg.send_notification(title, body)
        return "Notification sent via Telegram." if success else "Failed to send notification."

    return [
        ToolDefinition(
            name="send_telegram_message",
            description="Send a text message to the user via Telegram. Use when the user asks you to notify them or send a message to their phone.",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The message text to send"},
                },
                "required": ["message"],
            },
            handler=send_telegram,
            module_name="telegram",
        ),
        ToolDefinition(
            name="send_telegram_notification",
            description="Send a formatted notification with title and body via Telegram.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Notification title"},
                    "body": {"type": "string", "description": "Notification body text"},
                },
                "required": ["title", "body"],
            },
            handler=send_telegram_notification,
            module_name="telegram",
        ),
    ]


def _build_report_tools():
    """Tool definitions for the SW Development Report Specialist module."""
    from src.modules.report_module import ReportModule

    _module = None

    def _get_module() -> ReportModule:
        nonlocal _module
        if _module is None:
            _module = ReportModule()
        return _module

    # ── setup_report_project ──────────────────────────────────────
    async def setup_report_project(args: Dict, shared) -> str:
        m = _get_module()
        # Collect all config fields from args into a data dict
        data = {}
        for key in [
            "university", "faculty", "subject", "professor",
            "group_number", "project_name", "semester", "year",
            "city", "country", "uml_version", "language",
            "sprint_duration_weeks",
        ]:
            if key in args:
                data[key] = args[key]
        if "team_members" in args:
            data["team_members"] = args["team_members"]
        if "methodologies" in args:
            data["methodologies"] = args["methodologies"]
        if "tech_stack" in args:
            data["tech_stack"] = args["tech_stack"]
        return await m.setup_project(data, args.get("language", "es"))

    # ── create_report_template ────────────────────────────────────
    async def create_report_template(args: Dict, shared) -> str:
        m = _get_module()
        return await m.create_report_template(
            filename=args.get("filename", "reporte"),
            location=args.get("location", "desktop"),
            include_sprint_0=args.get("include_sprint_0", True),
            language=args.get("language", "es"),
        )

    # ── write_report_section ──────────────────────────────────────
    async def write_report_section(args: Dict, shared) -> str:
        m = _get_module()
        return await m.write_section(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            section_title=args.get("section_title", ""),
            content=args.get("content", ""),
            language=args.get("language", "es"),
        )

    # ── create_cover_page ─────────────────────────────────────────
    async def create_cover_page(args: Dict, shared) -> str:
        m = _get_module()
        return await m.create_cover_page(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            language=args.get("language", "es"),
        )

    # ── add_sprint_section ────────────────────────────────────────
    async def add_sprint_section(args: Dict, shared) -> str:
        m = _get_module()
        return await m.add_sprint(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            sprint_number=args.get("sprint_number", 1),
            sprint_goal=args.get("sprint_goal", ""),
            language=args.get("language", "es"),
        )

    # ── create_user_story_table ───────────────────────────────────
    async def create_user_story_table(args: Dict, shared) -> str:
        m = _get_module()
        stories = args.get("stories", [])
        return await m.create_user_story_table(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            stories=stories,
            section_title=args.get("section_title", ""),
            language=args.get("language", "es"),
        )

    # ── add_daily_scrum_table ─────────────────────────────────────
    async def add_daily_scrum_table(args: Dict, shared) -> str:
        m = _get_module()
        entries = args.get("entries", [])
        return await m.add_daily_scrum_table(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            sprint_number=args.get("sprint_number", 1),
            entries=entries,
            language=args.get("language", "es"),
        )

    # ── add_backlog_table ─────────────────────────────────────────
    async def add_backlog_table(args: Dict, shared) -> str:
        m = _get_module()
        items = args.get("items", [])
        return await m.add_backlog_table(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            sprint_number=args.get("sprint_number", 0),
            items=items,
            is_product_backlog=args.get("is_product_backlog", False),
            language=args.get("language", "es"),
        )

    # ── analyze_report_progress ───────────────────────────────────
    async def analyze_report_progress(args: Dict, shared) -> str:
        m = _get_module()
        return await m.analyze_report(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            language=args.get("language", "es"),
        )

    # ── add_sprint_retrospective ──────────────────────────────────
    async def add_sprint_retrospective(args: Dict, shared) -> str:
        m = _get_module()
        return await m.add_retrospective(
            filename=args.get("filename", ""),
            location=args.get("location", ""),
            sprint_number=args.get("sprint_number", 1),
            went_well=args.get("went_well", []),
            went_wrong=args.get("went_wrong", []),
            to_improve=args.get("to_improve", []),
            language=args.get("language", "es"),
        )

    return [
        ToolDefinition(
            name="setup_report_project",
            description="Configure the SW development report project metadata (university, team, subject, professor, methodologies, tech stack). Call this first before creating reports. Supports partial updates — only pass fields you want to set.",
            parameters={
                "type": "object",
                "properties": {
                    "university": {"type": "string", "description": "University name"},
                    "faculty": {"type": "string", "description": "Faculty name"},
                    "subject": {"type": "string", "description": "Course/subject name"},
                    "professor": {"type": "string", "description": "Professor name"},
                    "group_number": {"type": "string", "description": "Group number"},
                    "project_name": {"type": "string", "description": "Name of the SW project"},
                    "team_members": {
                        "type": "array",
                        "description": "Team members, each with name, student_id, and role",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "student_id": {"type": "string"},
                                "role": {"type": "string", "description": "SCRUM role: Product Owner, Scrum Master, or Developer"},
                            },
                        },
                    },
                    "semester": {"type": "string", "description": "Academic semester, e.g. 'I/2026'"},
                    "year": {"type": "string", "description": "Academic year"},
                    "city": {"type": "string"},
                    "country": {"type": "string"},
                    "methodologies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Methodologies used, e.g. ['SCRUM', 'PUDS']",
                    },
                    "tech_stack": {
                        "type": "object",
                        "description": "Technology stack: backend, frontend, database, mobile, devops",
                        "properties": {
                            "backend": {"type": "string"},
                            "frontend": {"type": "string"},
                            "database": {"type": "string"},
                            "mobile": {"type": "string"},
                            "devops": {"type": "string"},
                        },
                    },
                    "language": {"type": "string", "enum": ["en", "es"], "description": "Report language (default: es)"},
                },
                "required": ["project_name"],
            },
            handler=setup_report_project,
            module_name="report",
        ),
        ToolDefinition(
            name="create_report_template",
            description="Create a new Word document (.docx) with the full SW development report skeleton: cover page, table of contents, all standard sections (Introduction, Background, Problem, Objectives, Scope, CBIS, Technology, Costs, Benefits, Sprints, Bibliography, Annexes), and optionally Sprint 0.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name for the report file (without .docx)"},
                    "location": {"type": "string", "description": "Folder path or shortcut (desktop, documents, etc.)"},
                    "include_sprint_0": {"type": "boolean", "description": "Whether to include Sprint 0 section (default: true)"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename"],
            },
            handler=create_report_template,
            module_name="report",
        ),
        ToolDefinition(
            name="write_report_section",
            description="Write or overwrite the content of a specific section in the report. Finds the heading by partial match and replaces the body text below it. Supports multi-paragraph content (separate paragraphs with newlines). Lines starting with '## ' or '### ' become sub-headings.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Report filename"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "section_title": {"type": "string", "description": "Heading text to find, e.g. '1. Introducción' or 'Objetivos Específicos'"},
                    "content": {"type": "string", "description": "The text content to write in this section. Use newlines to separate paragraphs."},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename", "section_title", "content"],
            },
            handler=write_report_section,
            module_name="report",
        ),
        ToolDefinition(
            name="create_cover_page",
            description="Create or update the cover page (portada) of an existing report using the project configuration (university, team, date, etc.).",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Report filename"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename"],
            },
            handler=create_cover_page,
            module_name="report",
        ),
        ToolDefinition(
            name="add_sprint_section",
            description="Add a complete Sprint section to the report with all required SCRUM sub-sections: Sprint Planning, Goals, Scrum Team, Story Points, Use Case Diagram, User Stories, UML Designs, Sprint Backlog, Daily Scrum, Sprint Review, Sprint Retrospective. Use sprint_number=0 for Sprint 0 (inception with Product Backlog, tech infra, etc.).",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Report filename"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "sprint_number": {"type": "integer", "description": "Sprint number (0 for Sprint 0 inception, 1+ for regular sprints)"},
                    "sprint_goal": {"type": "string", "description": "Optional: the main goal for this sprint, written under Sprint Goals"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename", "sprint_number"],
            },
            handler=add_sprint_section,
            module_name="report",
        ),
        ToolDefinition(
            name="create_user_story_table",
            description="Insert formatted User Story (HU) cards as tables in the report. Each story includes: ID, name, priority, story points, status, As/I want/So that, acceptance criteria, and developer name.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Report filename"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "section_title": {"type": "string", "description": "Heading under which to insert the stories, e.g. '10.1.5 Historias de Usuario'"},
                    "stories": {
                        "type": "array",
                        "description": "List of user stories",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Story ID, e.g. 'HU01'"},
                                "name": {"type": "string", "description": "Short name"},
                                "priority": {"type": "string", "enum": ["Alta", "Media", "Baja"], "description": "Priority level"},
                                "story_points": {"type": "integer", "description": "Effort estimate (Fibonacci: 1,2,3,5,8,13,21)"},
                                "status": {"type": "string", "description": "Status: Pendiente/En proceso/Terminado"},
                                "as_role": {"type": "string", "description": "As a [role]..."},
                                "i_want": {"type": "string", "description": "I want [action]..."},
                                "so_that": {"type": "string", "description": "So that [benefit]..."},
                                "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "description": "List of acceptance criteria"},
                                "developer": {"type": "string", "description": "Developer assigned"},
                            },
                        },
                    },
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename", "stories"],
            },
            handler=create_user_story_table,
            module_name="report",
        ),
        ToolDefinition(
            name="add_daily_scrum_table",
            description="Insert a Daily Scrum tracking table into a specific sprint section. Each entry has: date, member, what they did yesterday, what they'll do today, and blockers.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Report filename"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "sprint_number": {"type": "integer", "description": "Sprint number"},
                    "entries": {
                        "type": "array",
                        "description": "Daily scrum entries",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date": {"type": "string", "description": "Date (e.g. '2026-03-01')"},
                                "member": {"type": "string", "description": "Team member name"},
                                "did_yesterday": {"type": "string", "description": "What they did yesterday"},
                                "doing_today": {"type": "string", "description": "What they will do today"},
                                "blockers": {"type": "string", "description": "Any impediments"},
                            },
                        },
                    },
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename", "sprint_number", "entries"],
            },
            handler=add_daily_scrum_table,
            module_name="report",
        ),
        ToolDefinition(
            name="add_backlog_table",
            description="Insert a Product Backlog or Sprint Backlog table with ID, description, priority, story points, status, and responsible person.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Report filename"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "sprint_number": {"type": "integer", "description": "Sprint number (0 for Product Backlog in Sprint 0)"},
                    "is_product_backlog": {"type": "boolean", "description": "True for Product Backlog, False for Sprint Backlog"},
                    "items": {
                        "type": "array",
                        "description": "Backlog items",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "description": {"type": "string"},
                                "priority": {"type": "string"},
                                "story_points": {"type": "integer"},
                                "status": {"type": "string"},
                                "responsible": {"type": "string"},
                            },
                        },
                    },
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename", "sprint_number", "items"],
            },
            handler=add_backlog_table,
            module_name="report",
        ),
        ToolDefinition(
            name="analyze_report_progress",
            description="Analyze an existing report document and show which sections are complete (have content), empty (heading only), or missing entirely. Helps identify what to work on next.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Report filename"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename"],
            },
            handler=analyze_report_progress,
            module_name="report",
        ),
        ToolDefinition(
            name="add_sprint_retrospective",
            description="Insert a Sprint Retrospective table with three columns: What went well, What went wrong, What to improve.",
            parameters={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Report filename"},
                    "location": {"type": "string", "description": "Folder path or shortcut"},
                    "sprint_number": {"type": "integer", "description": "Sprint number"},
                    "went_well": {"type": "array", "items": {"type": "string"}, "description": "Things that went well"},
                    "went_wrong": {"type": "array", "items": {"type": "string"}, "description": "Things that went wrong"},
                    "to_improve": {"type": "array", "items": {"type": "string"}, "description": "Things to improve"},
                    "language": {"type": "string", "enum": ["en", "es"]},
                },
                "required": ["filename", "sprint_number", "went_well", "went_wrong", "to_improve"],
            },
            handler=add_sprint_retrospective,
            module_name="report",
        ),
    ]
