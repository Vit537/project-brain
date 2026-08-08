# Editing the OpenClaw Repo with VS Code

## Overview

You cloned OpenClaw to Ubuntu (`~/openclaw`). Now you want to edit it with VS Code (running on Windows). 

**Best approach:** Use **VS Code Remote - WSL** to edit Ubuntu files directly from Windows.

---

## Step-by-Step: VS Code + WSL Setup

### **Step 1: Install VS Code on Windows**

Download from: https://code.visualstudio.com/

Or via PowerShell:
```powershell
# Using winget (if you have it)
winget install -e --id Microsoft.VisualStudioCode

# Or download manually from the website above
```

---

### **Step 2: Install VS Code Extension: Remote - WSL**

In VS Code:
1. Click **Extensions** icon (left sidebar, or `Ctrl+Shift+X`)
2. Search: `Remote - WSL`
3. Install the one by **Microsoft** (blue checkmark)

---

### **Step 3: Open Ubuntu Project in VS Code**

#### **Option A: From PowerShell (Easiest)**

```powershell
# Open PowerShell as regular user (NOT admin)
wsl
cd ~/openclaw
code .
```

VS Code will open and connect to WSL. You'll see:
```
[WSL: Ubuntu-24.04] - C:\Users\HP\Desktop\aiBot\codeBase\openclaw
```

**Bottom-left corner will show:** `WSL: Ubuntu-24.04` ✅

---

#### **Option B: From VS Code**

1. Open VS Code on Windows
2. Press `Ctrl+Shift+P` → type `Remote-WSL: Open Folder in WSL`
3. Select `/home/hpdev/openclaw`
4. Done!

---

## Now You Can Edit

### What You See

```
VS Code Window
├── Explorer (left sidebar)
│   ├── 📁 docs/
│   ├── 📁 src/
│   ├── 📁 extensions/
│   ├── 📁 apps/
│   ├── 📄 package.json
│   ├── 📄 openclaw.mjs
│   └── ...
├── Code Editor (center)
│   └── Edit files here
└── Terminal (bottom)
    └── Ubuntu bash shell
```

---

### Integrated Terminal

VS Code has a built-in terminal **connected to Ubuntu**:

1. Open terminal: ``Ctrl+` `` (backtick)
2. Terminal appears at bottom, showing:
   ```bash
   hpdev@DESKTOP-HISNLS9:~/openclaw$
   ```
3. Any command runs in **Ubuntu** (not Windows PowerShell)

**Try it:**
```bash
pwd
# Output: /home/hpdev/openclaw

ls
# Output: AGENTS.md CHANGELOG.md docs extensions ...
```

---

## Working with the Code

### Build & Test

In VS Code terminal:
```bash
# Install dependencies (if needed)
pnpm install

# Build TypeScript
pnpm build

# Run tests
pnpm test

# Start gateway for development
pnpm gateway:watch
```

---

### File Editing Workflow

**Example: Remove WhatsApp channel**

1. Open file: `src/channels/whatsapp/index.ts`
2. Read the code
3. Delete or comment out parts you don't need
4. Save (`Ctrl+S`)
5. Rebuild: `pnpm build`
6. Test: `pnpm test`

---

### Finding Code

Use **Find in Files** (`Ctrl+Shift+F`):

```
Search: "whatsapp"
```

Results show all files mentioning WhatsApp. Click any result to jump there.

---

## Tips & Tricks

### View Structure
Use **Outline** (right sidebar):
- Shows functions, classes, types in current file
- Click any to jump there

### Extension Recommendations
Install these VS Code extensions:

1. **TypeScript Vue Plugin** - Better TypeScript support
2. **ESLint** - Linting (code style checking)
3. **Prettier** - Code formatter
4. **Git Graph** - Visualize git history

---

### Git Integration

VS Code has **built-in git**:

1. Click **Source Control** (left sidebar, 3rd icon)
2. See changed files
3. Stage/unstage/commit changes visually

**Or use terminal:**
```bash
git status
git add .
git commit -m "Remove WhatsApp support"
git push
```

---

### Debugging

Set breakpoints in VS Code:
1. Click left margin of a line → red dot appears
2. Run in debug mode: `F5` or `Ctrl+Shift+D`
3. Execution stops at breakpoint
4. Inspect variables in left sidebar

---

## Project Structure (What You're Editing)

```
~/openclaw/
├── src/
│   ├── gateway/                      # Gateway server code
│   │   ├── rpc-handlers/             # API endpoints
│   │   ├── channels/                 # Channel manager
│   │   └── supervisor.ts             # Main gateway loop
│   │
│   ├── channels/                     # Built-in channels
│   │   ├── telegram/                 # Telegram bot
│   │   ├── discord/                  # Discord bot
│   │   ├── whatsapp/                 # WhatsApp (web)
│   │   ├── slack/                    # Slack bot
│   │   └── ...
│   │
│   ├── agents/                       # AI agent code
│   │   ├── pi-embedded-runner/       # Main agent loop
│   │   ├── pi-tools*/                # Tool definitions
│   │   └── ...
│   │
│   ├── cli/                          # Command-line interface
│   │   ├── commands/                 # CLI commands
│   │   └── ...
│   │
│   └── index.ts                      # Entry point
│
├── extensions/                       # Plugin channels
│   ├── telegram/                     # Telegram plugin (if enabled)
│   ├── discord/                      # Discord plugin (if enabled)
│   ├── msteams/                      # MS Teams plugin
│   └── ...
│
├── apps/                             # Native apps
│   ├── macos/                        # Mac app (Swift)
│   ├── ios/                          # iOS app (Swift)
│   └── android/                      # Android app (Kotlin)
│
├── docs/                             # Documentation (Markdown)
│   ├── gateway/
│   ├── channels/
│   ├── tools/
│   └── ...
│
├── package.json                      # Dependencies
├── pnpm-lock.yaml                    # Locked versions
├── tsconfig.json                     # TypeScript config
├── vitest.config.ts                  # Test config
└── README.md
```

---

## Common Editing Tasks

### **Task 1: Remove a Channel (e.g., WhatsApp)**

1. **Delete channel code:**
   ```bash
   rm -rf src/channels/whatsapp
   ```

2. **Remove from channel manager:**
   Open `src/channels/index.ts`, delete:
   ```typescript
   import { createWhatsAppChannel } from "./whatsapp/index.js";
   ```

3. **Remove from package.json:**
   Open `package.json`, delete:
   ```json
   "whatsapp": "web-whatsapp-api"  // (or similar dependency)
   ```

4. **Rebuild:**
   ```bash
   pnpm install
   pnpm build
   ```

---

### **Task 2: Customize System Prompt**

System prompt is in: `src/agents/system-prompt.ts`

```typescript
export function buildAgentSystemPrompt(): string {
  return `
You are a helpful AI assistant.
You can:
- Read and write files
- Execute commands
- Search the web
- Control a browser

Your workspace is at: ~/.openclaw/workspace/

IMPORTANT: Be concise and helpful.
  `;
}
```

Edit as needed, then rebuild.

---

### **Task 3: Add New Tool**

1. Create file: `src/agents/tools/my-custom-tool.ts`
2. Define tool:
   ```typescript
   export const myCustomTool = {
     name: "my_tool",
     description: "What this tool does",
     parameters: { /*...*/ },
     execute: async (params) => {
       // Implementation
       return result;
     }
   };
   ```

3. Register in `src/agents/pi-tools.ts`:
   ```typescript
   import { myCustomTool } from "./tools/my-custom-tool.js";
   
   export function createOpenClawCodingTools() {
     return [
       myCustomTool,  // Add here
       // ... other tools
     ];
   }
   ```

4. Rebuild:
   ```bash
   pnpm build
   ```

---

## Troubleshooting

### **VS Code says "Cannot access files"**

Check that you're in WSL mode:
- Look at **bottom-left corner**
- Should show: `WSL: Ubuntu-24.04`
- If not, click it → select Ubuntu

---

### **Terminal not working in VS Code**

Close and reopen terminal:
1. `` Ctrl+` `` to close
2. `` Ctrl+` `` to reopen

Or create new terminal:
- Click `+` icon in terminal area

---

### **Changes not reflected after edits**

Rebuild and restart gateway:
```bash
pnpm build
systemctl --user restart openclaw-gateway
```

---

### **Cannot find files**

Make sure you're editing in the **correct path:**
```bash
pwd
# Should output: /home/hpdev/openclaw

ls -la package.json
# Should exist
```

---

## Summary

| Task | Command |
|------|---------|
| **Open repo in VS Code** | `wsl` → `cd ~/openclaw` → `code .` |
| **Build** | `pnpm build` |
| **Run tests** | `pnpm test` |
| **Start dev server** | `pnpm gateway:watch` |
| **Find in files** | `Ctrl+Shift+F` |
| **Open terminal** | `` Ctrl+` `` |
| **Create file** | Right-click → New File |
| **Delete file** | Right-click → Delete |
| **Undo changes** | `Ctrl+Z` (or `git checkout <file>`) |
| **Save all** | `Ctrl+Shift+S` |

