# Complete Tools & Capabilities Reference

## Overview

OpenClaw provides a rich set of **tools** that the AI Agent can use to interact with your system and the outside world. These tools are invoked automatically by the LLM based on your request.

---

## Tools Inventory

### **File Operations**

#### **read** - Read file contents
```
Usage: "Read the MEMORY.md file"
What it does: Reads a file and returns its contents

Parameters:
- path: File path (can use ~ for home)
- encoding: (optional) default is "utf8"

Example response:
"Contents of ~/.openclaw/workspace/MEMORY.md:
- User prefers Python
- Works in engineering
- Likes concise responses"
```

#### **write** - Create or overwrite a file
```
Usage: "Create a Python script called hello.py"
What it does: Creates a new file or overwrites existing

Parameters:
- path: File path
- content: File contents

Example:
Creates file at ~/.openclaw/workspace/hello.py
```

#### **edit** - Edit specific lines in a file
```
Usage: "Change line 5 in hello.py to print 'Goodbye'"
What it does: Modifies specific sections without rewriting entire file

Parameters:
- path: File path
- find: Text to find
- replace: Text to replace with
```

#### **delete** - Delete a file
```
Usage: "Remove the test.txt file"
What it does: Deletes a file

Parameters:
- path: File path to delete
```

### **Shell/Command Execution**

#### **exec** - Run shell commands
```
Usage: "Run 'python script.py' and show me the output"
What it does: Executes any shell command

Parameters:
- command: Shell command (bash syntax)
- timeout: (optional) Max seconds to run
- cwd: (optional) Working directory

Examples:
- python ~/.openclaw/workspace/primes.py
- npm install
- git clone https://github.com/...
- ls -la ~/Documents
- grep "error" log.txt
```

### **Web Operations**

#### **web_search** - Search the internet
```
Usage: "Search for Python documentation about async/await"
What it does: Searches Google and returns results

Parameters:
- query: Search query
- count: (optional) Number of results (default 10)

Returns:
- List of search results with titles, snippets, URLs
```

#### **web_fetch** - Download web page content
```
Usage: "Fetch the content from https://docs.python.org"
What it does: Downloads a website and extracts text

Parameters:
- url: Website URL
- format: (optional) "markdown", "text", "json"

Returns:
- Page content in requested format
```

### **Browser Control**

#### **browser** - Automate browser actions
```
Usage: "Open Google, search for 'OpenClaw', and click the first result"
What it does: Controls a real web browser (Chrome/Firefox)

Parameters:
Multiple sub-commands:
- goto(url): Navigate to URL
- click(selector): Click on element
- type(text): Type text in focused element
- screenshot(): Take screenshot
- wait(ms): Wait milliseconds
- waitForNavigation(): Wait for page load

Example workflow:
1. browser.goto("https://google.com")
2. browser.type("OpenClaw")
3. browser.press("Enter")
4. browser.waitForNavigation()
5. browser.click('a:first-child')  // Click first result
6. browser.screenshot()
```

### **Message/Notification**

#### **message:send** - Send messages to users
```
Usage: "Send a message to Telegram saying 'Hello!'"
What it does: Sends a message across channels

Parameters:
- channel: "telegram", "discord", "whatsapp", "slack", etc.
- text: Message text
- to: User ID or channel ID
- format: (optional) "text", "markdown", "html"

Example:
Sends "Processing your request..." to the user who asked
```

### **Image & Vision**

#### **image:analyze** - Analyze images
```
Usage: "What's in this screenshot?"
What it does: Uses vision API to understand images

Parameters:
- image: Image file path or URL
- question: What to ask about the image

Returns:
- Description of what's in the image
```

#### **image:extract_text** - OCR (extract text from image)
```
Usage: "Extract all text from this screenshot"
What it does: Reads text from images

Parameters:
- image: Image file path or URL

Returns:
- All text found in the image
```

### **Device Control** (Mac/iOS/Android only)

#### **nodes** - Control paired devices
```
Usage: "Screenshot my iPhone"
What it does: Runs commands on Mac/iOS/Android via SSH

Parameters:
- nodeName: Device name (e.g., "iphone", "mac-studio")
- command: Command to run

Example devices:
- Your Mac
- iPhone paired via USB
- Android phone paired via adb
```

### **Canvas/UI Rendering**

#### **canvas** - Create custom interfaces
```
Usage: "Show me a dashboard with today's stats"
What it does: Renders HTML/React UI in agent environment

Parameters:
- html: HTML/React component code
- width/height: Dimensions
- interact: Allow user clicks

Example:
Renders a form, chart, or dashboard interface
```

### **Cron/Scheduling**

#### **cron** - Schedule recurring tasks
```
Usage: "Run a task every morning at 8 AM"
What it does: Schedules automation

Parameters:
- schedule: Cron syntax "0 8 * * *"
- task: What to do
- name: Job name

Example cron schedules:
- "0 8 * * *"   = Every day at 8:00 AM
- "*/5 * * * *"  = Every 5 minutes
- "0 12 * * 1"   = Every Monday at noon
```

### **Sessions/Multi-Agent**

#### **sessions_spawn** - Run parallelism or sub-agents
```
Usage: "Process these 5 files in parallel"
What it does: Creates sub-agent sessions for concurrent work

Parameters:
- count: Number of parallel sessions
- task: What each should do

Returns:
- Results from all sessions running in parallel
```

---

## Tool Groups & Profiles

### **Tool Groups** (Organized by category)

```
group:runtime
├── exec
├── cron
└── message:send

group:fs (File System)
├── read
├── write
├── edit
└── delete

group:web
├── web_search
├── web_fetch
├── browser
└── image:*

group:devices
└── nodes

group:ui
├── canvas
└── message:send

group:sessions
└── sessions_spawn

group:memory
├── read (for MEMORY.md)
└── write (for MEMORY.md)
```

### **Tool Profiles** (Pre-configured sets)

#### **minimal** (Safest)
```
Available tools:
- read (only workspace)
- message:send
- web_search

Disabled:
- exec
- write
- browser
- nodes
```

#### **coding** (For developers)
```
Available tools:
- read
- write
- edit
- exec
- web_search
- image:analyze
- browser

Disabled:
- nodes
- canvas (usually)
```

#### **full** (Most powerful)
```
Available tools:
- ALL tools available
```

### **How to Check Which Tools Are Enabled**

In `~/.openclaw/openclaw.json`:
```json
{
  "agents": {
    "defaults": {
      "tools": {
        "group:runtime": true,
        "group:fs": true,
        "group:web": true,
        "exec": true,
        "browser": true,
        "nodes": false  // Disabled
      }
    }
  }
}
```

---

## Safety & Permissions

### **Allow Lists** (What the tool CAN do)

```json
{
  "tools": {
    "exec": {
      "allowed": [
        "python*",
        "npm*",
        "node*"
      ]
    },
    "write": {
      "allowed": [
        "~/.openclaw/workspace/*",
        "~/Documents/*"
      ]
    }
  }
}
```

Only Python, npm, and Node commands can run. Writing only to workspace and Documents.

### **Deny Lists** (What the tool CANNOT do)

```json
{
  "tools": {
    "exec": {
      "denied": [
        "rm -rf /",
        "sudo*",
        "password*"
      ]
    }
  }
}
```

Prevent dangerous operations like deleting root, using sudo, asking for passwords.

---

## Common Use Cases

### **Use Case 1: Data Processing**

```
YOU: "I have a CSV file with user data. Count how many users are active."

AGENT USES:
1. read: Load CSV file
2. exec: Run Python script to count active users
3. message:send: Report the count back to you
```

### **Use Case 2: Web Research**

```
YOU: "Find out the latest news about AI and summarize it"

AGENT USES:
1. web_search: Search for "latest AI news"
2. web_fetch: Get full articles from top results
3. browser: (optional) Visit news sites directly
4. message:send: Send you the summary
```

### **Use Case 3: Automation**

```
YOU: "Every morning at 8 AM, send me a daily summary"

AGENT USES:
1. cron: Schedule task for "0 8 * * *"
2. web_search: Get today's news
3. message:send: Send summary
4. Sessions repeat daily
```

### **Use Case 4: Code Development**

```
YOU: "Create a Python package structure with unit tests"

AGENT USES:
1. write: Create package files and structure
2. write: Create test files
3. exec: Run tests to verify
4. message:send: Report success/failures
```

### **Use Case 5: Image Analysis**

```
YOU: "Analyze this screenshot and tell me what you see"

AGENT USES:
1. image:analyze: Describe screenshot
2. image:extract_text: Get text from screenshot
3. message:send: Send analysis back
```

### **Use Case 6: Device Monitoring**

```
YOU: "Take a screenshot of my iPhone"

AGENT USES:
1. nodes: Connect to iPhone
2. nodes: Execute screenshot command
3. browser/message:send: Show screenshot to you
```

---

## Advanced Examples

### **Example 1: Web Scraping & Data Processing**

```
USER REQUEST: "Find all Python libraries mentioned on Awesome Python page"

AGENT WORKFLOW:
1. web_fetch("https://awesome-python.com")
2. extract library names using image:extract_text or parsing
3. write to ~/.openclaw/workspace/python-libs.txt
4. exec("wc -l python-libs.txt") to count
5. message:send("Found 500 Python libraries: ...")
```

### **Example 2: Code Review & Improvement**

```
USER REQUEST: "Review my Python script and suggest improvements"

AGENT WORKFLOW:
1. read("~/Desktop/my_script.py")
2. LLM analyzes code
3. write("~/Desktop/my_script_improved.py") with improvements
4. exec("python -m py_compile my_script_improved.py") to check syntax
5. message:send("Script improved! Here are the changes: ...")
```

### **Example 3: Parallel Processing**

```
USER REQUEST: "Process 10 CSV files to extract key metrics"

AGENT WORKFLOW:
1. sessions_spawn(count=5) // Create 5 parallel agents
2. Each agent gets 2 files
3. Each exec() processes files in parallel
4. Results collected and merged
5. message:send("Processed all 10 files. Summary: ...")
```

### **Example 4: Scheduled Reporting**

```
USER REQUEST: "Every Monday at 9 AM, send me a code quality report"

AGENT WORKFLOW:
1. cron("0 9 * * 1") // Every Monday 9 AM
2. exec("npm run lint") // Run code linting
3. exec("npm run test") // Run tests
4. exec("npm run coverage") // Get coverage report
5. write("report.txt") // Save report
6. message:send("Code Quality Report: ...")
```

---

## Tool Performance & Limits

| Tool | Timeout | Max Output | Cost |
|------|---------|-----------|------|
| **read** | 5s | 1MB | Free |
| **write** | 5s | 1MB | Free |
| **exec** | 30s | 100MB | Free |
| **web_search** | 10s | 50 results | Free |
| **web_fetch** | 30s | 10MB | Free |
| **browser** | 60s | Screenshots | Free |
| **image:analyze** | 30s | Full response | Costs tokens |
| **message:send** | 5s | Unlimited | Channel dependent |
| **nodes** | 30s | Unlimited | Free |

---

## Tool Fallbacks & Error Handling

If a tool fails, the agent tries alternatives:

```
USER: "Download and analyze this PDF"

1. Try: web_fetch(url, format="pdf")
   ↓ FAILS
2. Try: browser.goto(url) + browser.screenshot()
   ↓ SUCCESS
3. image:analyze(screenshot) to extract content
```

---

## Creating Custom Tools

You can add custom tools to your workspace:

**File:** `~/.openclaw/workspace/custom-tools/my-tool.ts`

```typescript
export const myCustomTool = {
  name: "my_tool",
  description: "What this tool does",
  parameters: {
    param1: "string",
    param2: "number"
  },
  execute: async (params: any) => {
    // Your implementation
    return result;
  }
};
```

Then enable it in `openclaw.json`:
```json
{
  "tools": {
    "my_tool": true
  }
}
```

---

## Summary Table

| Tool | When to Use | Typical Cost |
|------|------------|--------------|
| **read** | Get file contents | No cost |
| **write** | Create/save files | No cost |
| **exec** | Run commands, scripts | No cost |
| **web_search** | Find information | No cost |
| **browser** | Interact with websites | No cost |
| **image** | Analyze/OCR images | Token cost |
| **message** | Send notifications | Channel dependent |
| **nodes** | Control devices | Device dependent |
| **cron** | Schedule tasks | No cost |
| **sessions** | Parallel processing | Token cost (per session) |

