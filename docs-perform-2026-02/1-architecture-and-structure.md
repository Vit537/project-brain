# OpenClaw Architecture & Structure

## Overview

OpenClaw is a **personal AI assistant** built with a **two-layer architecture**: Gateway (control plane) + Agent (AI engine).

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (You)                               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Telegram    │  │   WhatsApp   │  │   Discord    │  ...    │
│  │    Bot       │  │    Web       │  │    Bot       │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GATEWAY (Port 18789)                         │
│                 (Control Plane / Message Router)                │
│                                                                 │
│  • Polls channels for new messages                             │
│  • Routes messages to agent                                    │
│  • Stores session history (JSONL files)                        │
│  • Manages authentication                                      │
│  • Schedules cron jobs                                         │
│  • Manages browser sessions                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PI AGENT (AI Engine)                           │
│                  (Runs in same process)                         │
│                                                                 │
│  • Reads your message                                          │
│  • Loads conversation history (JSONL)                          │
│  • Reads MEMORY.md (your personal context)                     │
│  • Calls LLM (OpenRouter, Anthropic, OpenAI, etc.)            │
│  • Executes tools (exec, read, write, web_search, etc.)       │
│  • Saves response to JSONL                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              LLM PROVIDER (Cloud API)                           │
│                                                                 │
│  • OpenRouter (Mistral, Llama, etc.)                          │
│  • Anthropic (Claude)                                          │
│  • OpenAI (GPT models)                                         │
│  • Google (Gemini)                                             │
│  • And many more...                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
~/.openclaw/                          # Main state directory
├── openclaw.json                     # Configuration (channels, models, auth)
├── credentials/
│   └── openrouter.json              # API key storage
├── agents/
│   └── main/
│       ├── agent/
│       │   └── auth-profiles.json    # Per-agent API keys
│       └── sessions/
│           ├── agent:main:telegram:dm:7900212479.jsonl
│           └── agent:main:whatsapp:dm:+1234567890.jsonl
└── workspace/                        # Your custom content
    ├── MEMORY.md                     # Personal context (you edit)
    ├── skills/                       # Custom skill scripts
    └── ... your files
```

---

## Core Components

### 1. **Gateway** (TypeScript, Node.js)
- **Location:** `src/gateway/` in source code
- **Runtime:** Runs as systemd service (Ubuntu) or launchd (macOS)
- **Port:** 18789 (WebSocket + HTTP)
- **Responsibilities:**
  - WebSocket server for real-time communication
  - Channel polling (Telegram, Discord, WhatsApp, etc.)
  - Message routing to agents
  - Session management
  - Authentication & token validation
  - Browser/Node management

### 2. **Pi Agent** (TypeScript, embedded)
- **Location:** `src/agents/` in source code
- **Core Dependency:** `@mariozechner/pi-agent-core` (external SDK)
- **Responsibilities:**
  - Receives messages from Gateway
  - Loads session history
  - Calls LLM API
  - Executes tools (read files, exec commands, search web, etc.)
  - Manages conversation context
  - Saves responses to JSONL

### 3. **Channels** (Plugin architecture)
- **Location:** `src/channels/` (built-in) + `extensions/*/` (plugins)
- **Built-in:**
  - Telegram (`src/channels/telegram/`)
  - Discord (`src/channels/discord/`)
  - WhatsApp (`src/channels/whatsapp/`)
  - Slack (`src/channels/slack/`)
  - Signal, iMessage, Google Chat, etc.
- **Plugins:** Matrix, Zalo, BlueBubbles, Voice Call, etc.

### 4. **Tools** (Agent Capabilities)
- **Core Tools:**
  - `exec` - Run shell commands
  - `read`/`write`/`edit` - File operations
  - `web_search`/`web_fetch` - Web browsing
  - `browser` - Automated browser control
  - `canvas` - UI rendering
  - `nodes` - Target macOS/iOS devices
  - `message` - Send messages across channels
  - `sessions_spawn` - Sub-agent workflows
  - And more...

### 5. **Workspace & Memory**
- **Workspace:** `~/.openclaw/workspace/`
  - Custom skills and scripts you write
  - Persistent files for your agent
- **Memory:** `MEMORY.md`
  - You edit this markdown file
  - Agent reads it at the start of each conversation
  - Stores facts about you, preferences, habits

---

## Data Flow (Step-by-Step)

### When you send a message:

```
1. You send message on Telegram
   ↓
2. Gateway polls Telegram API
   ↓
3. Gateway retrieves your session file:
   ~/.openclaw/agents/main/sessions/agent:main:telegram:dm:7900212479.jsonl
   ↓
4. Gateway appends your message to JSONL
   ↓
5. Gateway calls Pi Agent with:
   - Your message
   - Last N messages from JSONL
   - Content from MEMORY.md
   - System prompt with available tools
   ↓
6. Pi Agent:
   - Loads LLM model (e.g., Mistral 8x7b)
   - Sends context to LLM API
   - LLM processes and responds
   - Agent may call tools (exec, web_search, etc.)
   - Agent collects response
   ↓
7. Agent appends response to JSONL
   ↓
8. Gateway sends response back to Telegram
   ↓
9. Done! ✅
```

---

## Configuration Hierarchy

```
1. openclaw.json                     (Your config)
   ├── agents.defaults               (Default for all agents)
   │   ├── model                     (Which LLM to use)
   │   ├── workspace                 (Where files live)
   │   └── tools                     (Which tools are allowed)
   │
   ├── channels                      (Telegram, Discord, WhatsApp, etc.)
   │   ├── telegram
   │   │   ├── botToken              (Telegram bot API key)
   │   │   └── dmPolicy              (pairing, open, requireAuth)
   │   └── ...
   │
   ├── env                          (Environment variables)
   │   └── OPENROUTER_API_KEY        (Your API key for the model provider)
   │
   └── gateway                      (Gateway settings)
       ├── mode: "local"             (local or remote)
       ├── port: 18789               (WebSocket port)
       └── auth.token                (Authentication token)

2. auth-profiles.json               (Per-agent credentials)
   └── Created by 'openclaw login' or manually

3. MEMORY.md                        (Personal context)
   └── Written by you, read by agent on every turn
```

---

## Key Concepts

### **Session**
A conversation thread with a user. Example:
- Session ID: `agent:main:telegram:dm:7900212479`
- Storage: JSONL file at `~/.openclaw/agents/main/sessions/agent:main:telegram:dm:7900212479.jsonl`
- Each user/channel = separate session file

### **Agent**
The AI assistant. OpenClaw supports multiple agents (e.g., "main", "support", "coding").
- Default: `main` agent
- Per-agent config: `agents.list[].id`
- Each agent can have different workspace, model, tools

### **Model**
The LLM (language model) used for responses.
- Examples: `openrouter/mistralai/mixtral-8x7b-instruct`, `anthropic/claude-opus-4-5`, `openai/gpt-4o`
- Set in: `agents.defaults.model.primary`
- Changed via: `openclaw config set` or edit `openclaw.json`

### **Tool**
Capability the agent can use. Examples:
- `exec` - Run commands
- `read` - Read files
- `web_search` - Search the web
- `browser` - Control browser
- Controlled via: `agents.defaults.tools`

### **Workspace**
Directory where your files live. Default: `~/.openclaw/workspace/`
- Contains: `MEMORY.md`, custom skills, your scripts
- Per-agent: can have different workspace per agent

---

## Runtime Flow

```
User Device (Ubuntu WSL on Windows)
    ↓
Node.js Process
    ↓
┌──────────────────────────────────────┐
│  OpenClaw Gateway                    │
├──────────────────────────────────────┤
│  WebSocket Server (port 18789)       │
│  Channel Polling Loop                │
│  Session Manager                     │
│  Browser Manager                     │
│  Node Manager                        │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│  Pi Agent (in-process)               │
├──────────────────────────────────────┤
│  AgentSession                        │
│  Tool Executor                       │
│  LLM Call Interface                  │
│  Context Manager                     │
└──────────────────────────────────────┘
    ↓
┌──────────────────────────────────────┐
│  LLM Provider (Cloud API)            │
├──────────────────────────────────────┤
│  OpenRouter API (HTTPS)              │
│  Sends: message + context            │
│  Returns: AI response                │
└──────────────────────────────────────┘
```

---

## Summary

| Component | What | Where | Purpose |
|-----------|------|-------|---------|
| **Gateway** | Control plane | `src/gateway/` | Message routing, channel polling, session mgmt |
| **Pi Agent** | AI engine | `src/agents/` | LLM calls, tool execution, context mgmt |
| **Channels** | Message interfaces | `src/channels/` + `extensions/` | Telegram, Discord, WhatsApp, etc. |
| **Tools** | Agent capabilities | `src/agents/tools/` | exec, read, write, web_search, browser, etc. |
| **Workspace** | Your files | `~/.openclaw/workspace/` | MEMORY.md, skills, custom scripts |
| **Sessions** | Conversations | `~/.openclaw/agents/main/sessions/*.jsonl` | Per-user/channel chat history |

