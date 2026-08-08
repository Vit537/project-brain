# Programming Language & Technology Stack

## Overview

OpenClaw is written entirely in **TypeScript** and runs on **Node.js**. Here's the complete tech stack breakdown.

---

## Programming Languages Used

### **TypeScript (95% of codebase)**

**What it is:** JavaScript with type checking. Compiles to plain JavaScript.

**Why TypeScript?**
- ✅ Type safety (catch bugs before runtime)
- ✅ Better IDE support (autocomplete, refactoring)
- ✅ Scalability (easier to maintain large projects)
- ✅ Modern JavaScript features

**Example:**
```typescript
// TypeScript (with types)
interface User {
  id: string;
  name: string;
  telegram_id?: number;
}

function sendMessage(user: User, message: string): Promise<void> {
  // Type checking ensures user.id exists and is string
  // Type checking ensures message is string
  return api.send(user.id, message);
}
```

Compiles to:
```javascript
// JavaScript (no types, no comments)
function sendMessage(user, message) {
  return api.send(user.id, message);
}
```

---

### **JSON/JSON5 (Configuration)**

**Used for:** Config files (`openclaw.json`)

Example:
```json5
{
  // Comments allowed in JSON5!
  agents: {
    defaults: {
      model: { primary: "openrouter/mistralai/mixtral-8x7b-instruct" },
      workspace: "~/.openclaw/workspace"
    }
  },
  channels: {
    telegram: {
      botToken: "8471847127:AAG..." // Your bot token
    }
  }
}
```

---

### **Shell Scripts (Bash)**

**Used for:** Installation, setup, maintenance

Files:
- `install.sh` - Installation script
- `docker-setup.sh` - Docker setup
- Various helper scripts in `scripts/`

Example:
```bash
#!/bin/bash
# Check if Node.js is installed
if ! command -v node &> /dev/null; then
  echo "Node.js not found. Installing..."
  curl -fsSL https://fnm.io/install | bash
fi
```

---

### **Swift (iOS/macOS apps)**

**Used for:** Native mobile apps

Directories:
- `apps/ios/` - iPhone/iPad app
- `apps/macos/` - Mac desktop app

```swift
// Example Swift code (from iOS app)
import SwiftUI

struct ContentView: View {
  @State private var message = ""
  
  var body: some View {
    TextField("Type a message...", text: $message)
      .padding()
  }
}
```

**Note:** You don't need to worry about these for your Ubuntu setup. The Gateway + Agent are pure TypeScript.

---

### **Kotlin (Android app)**

**Used for:** Android app

Directory: `apps/android/`

```kotlin
// Example Kotlin code
class MainActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)
  }
}
```

**Note:** Also not needed for Ubuntu.

---

## Technology Stack Breakdown

### **Runtime & Core**

| Technology | Version | Purpose |
|------------|---------|---------|
| **Node.js** | 22+ | JavaScript runtime |
| **TypeScript** | 5.x | Type-safe JavaScript |
| **pnpm** | 9+ | Package manager (like npm) |
| **Bun** | Optional | Faster TypeScript runner (optional) |

---

### **Core Libraries**

| Package | Version | Purpose |
|---------|---------|---------|
| **@mariozechner/pi-agent-core** | 0.51.0 | AI agent engine (external) |
| **@mariozechner/pi-coding-agent** | 0.51.0 | High-level agent SDK |
| **@mariozechner/pi-ai** | 0.51.0 | LLM abstractions |
| **ws** | Latest | WebSocket server |
| **express** | Optional | HTTP server (some components) |

---

### **Channel Libraries**

| Channel | Library | Version |
|---------|---------|---------|
| **Telegram** | **grammY** | 1.39.3 |
| **Discord** | **discord.js** | Latest |
| **WhatsApp** | **web-whatsapp-api** | Custom |
| **Slack** | **@slack/bolt** | Latest |
| **Signal** | **libsignal** | Custom wrapper |

---

### **Development Tools**

| Tool | Purpose |
|------|---------|
| **vitest** | Testing framework |
| **rolldown** | Build tool (bundles TypeScript) |
| **eslint** | Code linting (style checking) |
| **oxfmt** | Code formatter |
| **TypeScript compiler `tsc`** | Compiles .ts to .js |

---

## Build Process

### How Code Flows from TypeScript to Running

```
1. Source Code (TypeScript)
   📁 src/
   └── agents/pi-embedded-runner.ts
   └── channels/telegram/index.ts
   └── gateway/supervisor.ts
        ↓

2. TypeScript Compiler (pnpm build)
   Using rolldown + tsdown
        ↓

3. JavaScript Output
   📁 dist/
   └── index.js (main entry point)
   └── agents/pi-embedded-runner.js
   └── channels/telegram/index.js
        ↓

4. Node.js Runtime
   node dist/index.js gateway --port 18789
        ↓

5. Running Process
   Open port 18789 (WebSocket)
   Listen for messages
   Execute agent code
```

---

## Build Commands

### Compile TypeScript to JavaScript
```bash
pnpm build
```

**What happens:**
- Reads all `*.ts` files from `src/`
- Runs rolldown (build tool)
- Outputs to `dist/`
- Takes ~18 seconds

---

### Run in Development Mode
```bash
pnpm gateway:watch
```

**What it does:**
- Watches for changes in `src/`
- Auto-rebuilds on every save
- Useful when developing

---

### Run Tests
```bash
pnpm test
```

**What it does:**
- Runs all `*.test.ts` files
- Uses vitest test framework
- Reports pass/fail for each test

---

## Source Code Organization

```
src/
├── index.ts                          # Entry point
├── entry.ts                          # Alternative entry
│
├── gateway/                          # Gateway server
│   ├── supervisor.ts                 # Main loop
│   ├── rpc-handlers/                 # API endpoints
│   │   ├── agent.ts
│   │   ├── channels.ts
│   │   ├── config.ts
│   │   └── ...
│   ├── channels/                     # Channel management
│   │   ├── manager.ts
│   │   └── index.ts
│   └── ...
│
├── channels/                         # Built-in channels
│   ├── telegram/
│   │   ├── index.ts                  # Telegram bot main
│   │   ├── api.ts
│   │   └── handlers.ts
│   ├── discord/
│   │   ├── index.ts
│   │   └── handlers.ts
│   ├── whatsapp/
│   ├── slack/
│   ├── signal/
│   └── ...
│
├── agents/                           # AI agent code (Pi-based)
│   ├── pi-embedded-runner/           # Main agent loop
│   │   ├── run.ts                    # Entry point
│   │   ├── run/
│   │   │   ├── attempt.ts
│   │   │   ├── params.ts
│   │   │   └── ...
│   │   └── ...
│   │
│   ├── pi-tools*/                    # Tool implementations
│   │   ├── exec.ts                   # Run commands
│   │   ├── read.ts                   # Read files
│   │   ├── write.ts                  # Write files
│   │   ├── web-search.ts             # Web search
│   │   ├── browser.ts                # Browser control
│   │   ├── message.ts                # Send messages
│   │   └── ...
│   │
│   ├── system-prompt.ts              # System prompt builder
│   ├── auth-profiles.ts              # Auth management
│   ├── model-selection.ts            # Model choice logic
│   └── ...
│
├── cli/                              # Command-line interface
│   ├── commands/
│   │   ├── gateway.ts                # 'openclaw gateway' command
│   │   ├── agent.ts                  # 'openclaw agent' command
│   │   ├── channels.ts               # 'openclaw channels' command
│   │   ├── config.ts                 # 'openclaw config' command
│   │   └── ...
│   └── index.ts
│
├── infra/                            # Infrastructure/platform code
│   ├── paths.ts                      # File path helpers
│   ├── config.ts                     # Config loading
│   └── ...
│
└── ... (other modules)
```

---

## Key TypeScript Patterns Used

### **Interfaces (Type Definitions)**

```typescript
// Define what a message object looks like
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}
```

### **Classes**

```typescript
// Organize related functions together
class SessionManager {
  constructor(private sessionDir: string) {}
  
  async loadSession(id: string): Promise<Session> {
    // Implementation
  }
  
  async saveSession(id: string, session: Session): Promise<void> {
    // Implementation
  }
}
```

### **Async/Await**

```typescript
// Handle async operations cleanly
async function sendMessage(text: string): Promise<string> {
  const response = await api.call(text);
  return response.text;
}
```

### **Generics (Template Types)**

```typescript
// Works with any type
function cache<T>(key: string, value: T): T {
  store[key] = value;
  return value;
}

cache("user", user);      // T = User
cache("count", 42);       // T = number
```

---

## Compilation Details

### **TypeScript Configuration** (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "ES2020",              // Output JavaScript version
    "module": "ESNext",              // Module format
    "moduleResolution": "node",      // How to find imports
    "strict": true,                  // Strict type checking
    "esModuleInterop": true,         // ES module compatibility
    "declaration": true,             // Generate .d.ts files
    "sourceMap": true,               // For debugging
    "outDir": "./dist"               // Output directory
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## Dependency Management

### **package.json** (Declares dependencies)

```json
{
  "name": "openclaw",
  "version": "2026.2.2",
  "type": "module",  // ESM (import/export)
  "engines": {
    "node": ">=22"    // Requires Node 22+
  },
  "dependencies": {
    "@mariozechner/pi-agent-core": "0.51.0",
    "ws": "^8.0.0",
    "telegram": "latest"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

### **pnpm-lock.yaml** (Locked versions)

Stores exact versions of all dependencies (transitive too).

Ensures everyone uses the same versions (reproducible builds).

---

## Runtime Flow

```
1. You run: pnpm openclaw tui
   ↓

2. pnpm looks up "openclaw" in package.json
   ↓

3. Runs: node dist/index.js tui
   ↓

4. Node.js:
   - Reads dist/index.js (compiled JavaScript)
   - Imports dependencies from node_modules/
   - Executes the TUI command
   ↓

5. JavaScript runs:
   - Imports TypeScript modules (already compiled)
   - Uses libraries (ws, telegram, etc.)
   - Connects to port 18789
   - Opens interactive terminal
   ↓

6. Done! ✅
```

---

## Debugging TypeScript

### **Source Maps** (maps compiled JS back to TS)

When Node.js runs `dist/index.js`, debugger shows:
```
→ src/agents/pi-embedded-runner.ts:42
  const result = await runAgent(...);  // Show TypeScript line, not compiled JS
```

Without source maps, you'd see:
```
→ dist/index.js:1042
  var t=await e(...);  // Compiled JS, hard to read
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Language** | TypeScript (95%), JSON config, Bash scripts, Swift (iOS/macOS), Kotlin (Android) |
| **Runtime** | Node.js 22+ |
| **Package Manager** | pnpm (or npm/Bun) |
| **Build Tool** | rolldown + tsdown |
| **Test Framework** | vitest |
| **Core Framework** | Pi SDK (@mariozechner/pi-agent-core) |
| **Channels** | grammY (Telegram), discord.js, Slack Bolt, etc. |
| **Type Checking** | TypeScript strict mode |
| **Entry Point** | `src/index.ts` → compiled to `dist/index.js` |
| **Config Format** | JSON5 (in `~/.openclaw/openclaw.json`) |

