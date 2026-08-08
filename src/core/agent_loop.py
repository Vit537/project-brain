"""
Agent Loop - Multi-Step Autonomous Execution
The brain of JARVIS: receives user input, decides which tool(s) to call,
executes them, feeds results back to the LLM, and repeats until done.

Replaces the old single-shot intent_router → module_manager flow.
"""
import json
import os
import re
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from colorama import Fore, Style

from src.core.tool_registry import ToolRegistry


# Maximum tool-call iterations per user turn to prevent runaway loops
MAX_ITERATIONS = 6

# Path to report project config
_REPORT_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'report_project.json')
)

# System prompt that teaches the LLM to be JARVIS with tool use
SYSTEM_PROMPT_EN = """You are JARVIS, an intelligent AI assistant for Windows.
You help the user manage Word documents, PDF files, APA reports, folders, and more.

RULES:
1. If the user asks you to DO something (create, read, edit, summarize, delete, search),
   pick the right tool and call it. You may call multiple tools in sequence.
2. If the user just asks a question or wants a conversation, reply directly WITHOUT any tool call.
3. Always respond in the same language the user used (English or Spanish).
4. After a tool call returns its result, summarize what happened briefly.
5. If a tool fails, explain the error and suggest a fix.
6. NEVER pretend you called a tool. If you want to use a tool, actually call it.
7. Keep responses concise. Do not repeat yourself.
"""

SYSTEM_PROMPT_ES = """Eres JARVIS, un asistente de IA inteligente para Windows.
Ayudas al usuario a gestionar documentos Word, archivos PDF, reportes APA, carpetas y más.

REGLAS:
1. Si el usuario te pide HACER algo (crear, leer, editar, resumir, eliminar, buscar),
   selecciona la herramienta correcta y llámala. Puedes llamar varias herramientas en secuencia.
2. Si el usuario solo hace una pregunta o quiere conversar, responde directamente SIN llamar herramientas.
3. Siempre responde en el mismo idioma que usó el usuario (inglés o español).
4. Después de que una herramienta devuelva su resultado, resume brevemente lo que pasó.
5. Si una herramienta falla, explica el error y sugiere una solución.
6. NUNCA finjas que llamaste una herramienta. Si quieres usar una herramienta, LLÁMALA de verdad.
7. Mantén las respuestas concisas. No te repitas.
"""

# ── Report specialist prompt (injected when project is configured) ──
REPORT_SPECIALIST_PROMPT = """
## SW DEVELOPMENT REPORT SPECIALIST

You also specialize in engineering SW development project reports for Latin American university faculties.
You know SCRUM (roles, events, artifacts, Fibonacci story points, HU format) and PUDS (phases, UML >= 2.5).

### KEY RULES:
1. ALWAYS use the report tools to modify the Word document. NEVER just describe what you would write — actually call the tool.
2. When asked to write a section, call write_report_section with the actual content text.
3. When asked to fill multiple sections, call the tool once per section sequentially.
4. Default language is SPANISH. Academic formal tone.
5. Be consistent: use the same team names, dates, tech stack from project config.
6. For UML diagrams, describe what the diagram should contain (the actual image must be created separately).

### WORKFLOW:
1. setup_report_project → 2. create_report_template → 3. write_report_section (per section) → 4. add_sprint_section + user stories + backlogs → 5. analyze_report_progress

### HU FORMAT:
ID (HU01...), Name, Priority (Alta/Media/Baja), Story Points, Status, Como [rol] Quiero [acción] Para que [beneficio], Acceptance criteria, Developer.
"""


class AgentLoop:
    """
    Multi-step agent loop using Groq function calling.

    Flow per user turn:
    1. Build messages (system + memory context + conversation history + user input)
    2. Call Groq with tool definitions
    3. If LLM returns tool_calls → execute each → append results → go to step 2
    4. If LLM returns text → return to user (done)
    """

    def __init__(self, shared, tool_registry: ToolRegistry):
        self.shared = shared
        self.registry = tool_registry
        self._conversation_history: List[Dict[str, str]] = []
        self._max_history = 20  # Keep last N messages for context window
        print("✓ Agent Loop created")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def run(self, user_input: str, language: str = "en") -> str:
        """
        Process one user turn through the full agent loop.

        Returns the final text response from JARVIS.
        """
        start_time = time.time()

        # 1) Build initial messages
        messages = self._build_messages(user_input, language)

        # 2) Get tools in Groq format — filtered by context to reduce noise
        report_cfg = self._load_report_config()
        report_active = bool(report_cfg and report_cfg.get("configured"))
        tools = self.registry.get_tools_for_context(user_input, report_active=report_active)

        # 3) Agent loop: call LLM, check for tool calls, repeat
        final_text = ""
        iterations = 0
        tools_used = []

        while iterations < MAX_ITERATIONS:
            iterations += 1
            if iterations == 1:
                print(f"{Fore.YELLOW}🧠 Agent thinking (step {iterations}, {len(tools)} tools)...{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}🧠 Agent thinking (step {iterations})...{Style.RESET_ALL}")

            response_msg, tool_calls = await self._call_llm(messages, tools)

            if tool_calls:
                # LLM wants to call tool(s) — execute and feed results back
                messages.append(response_msg)

                for tc in tool_calls:
                    tool_name = tc["function"]["name"]
                    try:
                        tool_args = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        tool_args = {}

                    print(f"{Fore.CYAN}  🔧 Calling tool: {tool_name}({json.dumps(tool_args, ensure_ascii=False)[:120]}){Style.RESET_ALL}")

                    result = await self.registry.execute(tool_name, tool_args, self.shared)
                    tools_used.append(tool_name)

                    # Truncate very large results to stay within context window
                    if len(result) > 4000:
                        result = result[:4000] + "\n...[truncated]"

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": tool_name,
                        "content": result,
                    })

                    print(f"{Fore.GREEN}  ✓ Tool result ({len(result)} chars){Style.RESET_ALL}")

                # Continue loop — LLM will see tool results and decide next step
            else:
                # LLM returned text — we're done
                final_text = response_msg.get("content", "") if isinstance(response_msg, dict) else str(response_msg)
                break

        if not final_text:
            final_text = "I completed the requested actions." if language == "en" else "Completé las acciones solicitadas."

        # 4) Update conversation history
        self._conversation_history.append({"role": "user", "content": user_input})
        self._conversation_history.append({"role": "assistant", "content": final_text})
        self._trim_history()

        # 5) Store interaction in memory + conversation store
        latency_ms = int((time.time() - start_time) * 1000)
        await self._store_memory(user_input, final_text, language, latency_ms)

        # Persist to JSONL transcript
        try:
            store = self.shared.conversation_store
            store.store_turn(
                user_input=user_input,
                assistant_response=final_text,
                language=language,
                tools_called=tools_used if tools_used else None,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            print(f"{Fore.RED}  ⚠ Transcript store failed: {exc}{Style.RESET_ALL}")

        return final_text

    # ------------------------------------------------------------------
    # Internal: LLM call
    # ------------------------------------------------------------------
    async def _call_llm(
        self,
        messages: List[Dict],
        tools: List[Dict],
    ) -> Tuple[Dict, Optional[List[Dict]]]:
        """
        Call Groq chat completions with tools.
        Returns (assistant_message_dict, tool_calls_list_or_None).

        Handles the 'tool_use_failed' error that Groq returns when the LLM
        generates a malformed function call (common with many tools or
        Windows backslash paths).  Recovery strategy:
          1. Parse the failed_generation XML to extract the intended tool call
          2. If parsing succeeds, return it as a normal tool_call
          3. If parsing fails, retry the request without tools (text-only)
        """
        ai = self.shared.ai

        try:
            kwargs = dict(
                model=ai.model,
                messages=messages,
                temperature=0.4,
                max_tokens=2048,
            )
            # Only pass tools when we actually have them
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
                kwargs["parallel_tool_calls"] = False  # reduces malformed calls

            response = ai.client.chat.completions.create(**kwargs)
            msg = response.choices[0].message

            # Build a plain dict representation so we can append to messages
            msg_dict = {"role": "assistant", "content": msg.content or ""}

            tool_calls = None
            if msg.tool_calls:
                tool_calls = []
                msg_dict["tool_calls"] = []
                for tc in msg.tool_calls:
                    tc_dict = {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    tool_calls.append(tc_dict)
                    msg_dict["tool_calls"].append(tc_dict)

            return msg_dict, tool_calls

        except Exception as exc:
            exc_str = str(exc)

            # ── Handle Groq's tool_use_failed error ──────────────────
            if "tool_use_failed" in exc_str and "failed_generation" in exc_str:
                print(f"{Fore.YELLOW}  ⚠ Groq tool_use_failed — attempting recovery...{Style.RESET_ALL}")

                # Strategy 1: parse the failed_generation to recover the call
                recovered = self._parse_failed_generation(exc_str)
                if recovered:
                    fn_name, fn_args_str = recovered
                    print(f"{Fore.YELLOW}  ↳ Recovered tool call: {fn_name}({fn_args_str[:80]}...){Style.RESET_ALL}")
                    call_id = f"call_{uuid.uuid4().hex[:24]}"
                    tc_dict = {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": fn_name,
                            "arguments": fn_args_str,
                        },
                    }
                    msg_dict = {
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [tc_dict],
                    }
                    return msg_dict, [tc_dict]

                # Strategy 2: retry without tools, lower max_tokens to prevent repetition
                print(f"{Fore.YELLOW}  ↳ Could not parse — retrying without tools...{Style.RESET_ALL}")
                try:
                    fallback_kwargs = dict(
                        model=ai.model,
                        messages=messages,
                        temperature=0.4,
                        max_tokens=1024,
                    )
                    response = ai.client.chat.completions.create(**fallback_kwargs)
                    msg = response.choices[0].message
                    content = msg.content or ""
                    # Warn user that tools weren't used
                    notice = (
                        "\n\n⚠️ *Nota: no pude ejecutar herramientas en esta respuesta. "
                        "Por favor repite tu solicitud y seré más preciso.*"
                    )
                    return {"role": "assistant", "content": content + notice}, None
                except Exception as retry_exc:
                    print(f"{Fore.RED}  ✗ Retry also failed: {retry_exc}{Style.RESET_ALL}")

            print(f"{Fore.RED}  ✗ LLM error: {exc}{Style.RESET_ALL}")
            return {"role": "assistant", "content": f"Sorry, I encountered an error: {exc}"}, None

    # ------------------------------------------------------------------
    # Internal: Parse failed_generation from Groq error
    # ------------------------------------------------------------------
    def _parse_failed_generation(self, error_text: str) -> Optional[Tuple[str, str]]:
        """
        Extract function name and JSON arguments from Groq's failed_generation.

        Groq returns errors like:
          <function=read_word_document({"filename": "test", "location": "C:\\..."})</function>

        The error text passes through Python repr, so backslashes can be
        2x, 4x, or 8x escaped depending on nesting.  We try multiple
        rounds of un-escaping until JSON parses.

        Returns (function_name, json_args_string) or None.
        """
        # Use GREEDY match for the JSON block — the closing is })</ or })>
        match = re.search(
            r'<function=(\w+)\((\{.+\})\)(?:</function>|>)',
            error_text,
            re.DOTALL,
        )
        if not match:
            # Also try without the closing tag (some errors truncate it)
            match = re.search(
                r'<function=(\w+)\((\{.+\})\)',
                error_text,
                re.DOTALL,
            )
        if not match:
            return None

        fn_name = match.group(1)
        raw_args = match.group(2)

        # Try to parse as-is first, then progressively un-escape backslashes
        # Groq errors nest escaping:  C:\\\\Users  or  C:\\Users  →  C:\Users
        candidates = [raw_args]
        # Build un-escaped variants
        v = raw_args
        for _ in range(4):  # max 4 rounds of halving backslashes
            v = v.replace('\\\\', '\\\\'[0:2])
            if v != candidates[-1]:
                candidates.append(v)
            else:
                break

        for attempt in candidates:
            try:
                json.loads(attempt)
                return fn_name, attempt
            except json.JSONDecodeError:
                continue

        # Last resort: try to fix common JSON issues
        cleaned = raw_args.replace("\\'", "'").replace('\\"', '"')
        # Re-wrap in proper JSON escaping
        try:
            json.loads(cleaned)
            return fn_name, cleaned
        except json.JSONDecodeError:
            pass

        return None

    # ------------------------------------------------------------------
    # Internal: Message building
    # ------------------------------------------------------------------
    def _build_messages(self, user_input: str, language: str) -> List[Dict]:
        """Build the full message list for the LLM."""
        system = SYSTEM_PROMPT_ES if language == "es" else SYSTEM_PROMPT_EN

        # ── Inject report specialist prompt when project is configured ──
        report_cfg = self._load_report_config()
        if report_cfg and report_cfg.get("configured"):
            system += REPORT_SPECIALIST_PROMPT
            # Inject project context so the LLM knows team, university, etc.
            project_summary = self._build_project_context(report_cfg)
            if project_summary:
                system += f"\n\n### CURRENT PROJECT CONTEXT\n{project_summary}"

        messages = [{"role": "system", "content": system}]

        # Add memory context (similar past conversations)
        memory = self.shared.memory
        if memory and memory.enabled:
            rows, _ = memory.get_context(user_input, k=3)
            if rows:
                context_lines = []
                for r in rows:
                    context_lines.append(f"User: {r['user_input']}\nJARVIS: {r['ai_response']}")
                context_block = "\n---\n".join(context_lines)
                messages.append({
                    "role": "system",
                    "content": f"Relevant past interactions:\n{context_block}",
                })

        # Add knowledge base context (MEMORY.md + daily logs + vector search)
        try:
            kb = self.shared.knowledge_base
            kb_context = kb.get_context(user_input, k=3)
            if kb_context:
                messages.append({
                    "role": "system",
                    "content": kb_context,
                })
        except Exception:
            pass  # Knowledge base is optional

        # Add session state hints
        session = self.shared.session_state
        hints = []
        if session.get("last_word_path"):
            hints.append(f"Last Word file: {session['last_word_path']}")
        if session.get("last_pdf_path"):
            hints.append(f"Last PDF file: {session['last_pdf_path']}")
        if session.get("stream_to_word"):
            hints.append("Writing mode is currently ACTIVE.")
        if hints:
            messages.append({
                "role": "system",
                "content": "Current session state:\n" + "\n".join(hints),
            })

        # Add recent conversation history
        for msg in self._conversation_history:
            messages.append(msg)

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        return messages

    # ------------------------------------------------------------------
    # Internal: Report config helpers
    # ------------------------------------------------------------------
    def _load_report_config(self) -> Optional[Dict]:
        """Load report project config from disk (cached per session)."""
        if not hasattr(self, '_report_config_cache'):
            self._report_config_cache = None
            self._report_config_mtime = 0.0

        try:
            if not os.path.exists(_REPORT_CONFIG_PATH):
                return None
            mtime = os.path.getmtime(_REPORT_CONFIG_PATH)
            if mtime != self._report_config_mtime:
                with open(_REPORT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    self._report_config_cache = json.load(f)
                self._report_config_mtime = mtime
            return self._report_config_cache
        except Exception:
            return None

    def _build_project_context(self, cfg: Dict) -> str:
        """Build a concise text summary of the project config for the system prompt."""
        lines = []
        if cfg.get("project_name"):
            lines.append(f"Project: {cfg['project_name']}")
        if cfg.get("university"):
            lines.append(f"University: {cfg['university']}")
        if cfg.get("faculty"):
            lines.append(f"Faculty: {cfg['faculty']}")
        if cfg.get("subject"):
            lines.append(f"Subject: {cfg['subject']}")
        if cfg.get("professor"):
            lines.append(f"Professor: {cfg['professor']}")
        if cfg.get("group_number"):
            lines.append(f"Group: {cfg['group_number']}")
        team = cfg.get("team_members", [])
        if team:
            members = []
            for m in team:
                name = m.get("name", "")
                role = m.get("role", "")
                sid = m.get("student_id", "")
                members.append(f"{name} ({role}) [{sid}]" if role else f"{name} [{sid}]")
            lines.append(f"Team ({len(team)} members): {', '.join(members)}")
        methods = cfg.get("methodologies", [])
        if methods:
            lines.append(f"Methodologies: {', '.join(methods)}")
        tech = cfg.get("tech_stack", {})
        if isinstance(tech, dict):
            parts = [f"{k}: {v}" for k, v in tech.items() if v]
            if parts:
                lines.append(f"Tech stack: {', '.join(parts)}")
        if cfg.get("uml_version"):
            lines.append(f"UML version: {cfg['uml_version']}")
        if cfg.get("year"):
            lines.append(f"Year: {cfg['year']}")
        if cfg.get("story_point_scale"):
            lines.append(f"Story point scale: {cfg['story_point_scale']}")
        return "\n".join(lines)

    def _trim_history(self):
        """Keep conversation history within bounds."""
        if len(self._conversation_history) > self._max_history:
            self._conversation_history = self._conversation_history[-self._max_history:]

    # ------------------------------------------------------------------
    # Internal: Memory storage
    # ------------------------------------------------------------------
    async def _store_memory(self, user_input: str, response: str, language: str, latency_ms: int):
        """Store the interaction in vector memory."""
        memory = self.shared.memory
        if not memory or not memory.enabled:
            return
        try:
            embedding = memory.embedder.embed(user_input)
            if embedding:
                memory.store_interaction(
                    user_input=user_input,
                    ai_response=response,
                    embedding=embedding,
                    intent="agent_loop",
                    action_taken=None,
                    success=True,
                    latency_ms=latency_ms,
                    language=language,
                )
        except Exception as exc:
            print(f"{Fore.RED}  ⚠ Memory store failed: {exc}{Style.RESET_ALL}")

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------
    @property
    def history_length(self) -> int:
        return len(self._conversation_history)

    def clear_history(self):
        self._conversation_history.clear()

    def status(self) -> Dict[str, Any]:
        return {
            "history_messages": len(self._conversation_history),
            "max_history": self._max_history,
            "tools_available": self.registry.list_names(),
        }
