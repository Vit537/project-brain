# How OpenClaw's AI Agent Works: Complete Flow Explanation

## The Question You Asked

> "I wanna know about what is the AI or agent that control my computer, because the models are interpret the language that is sent by the user, and after the models depend of what are you using, receive that and after send the command that got it open and open Claude into my computer execute that i say right?"

**Short answer:** YES, you're exactly right! Let me explain how it actually works.

---

## The Complete Flow (Step by Step)

### **Diagram**

```
┌──────────────────────────────────────────────────────────────────┐
│ USER                                                             │
│ "Create a Python script to calculate prime numbers"             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ CHANNEL (Telegram, WhatsApp, Discord, Web, etc.)               │
│ Message arrives → Gateway polls for new messages               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ GATEWAY (Control Plane)                                         │
│ • Receives message from channel                                 │
│ • Loads session history (JSONL file)                            │
│ • Routes to Agent                                               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ Pi AGENT (AI Engine)                                            │
│                                                                 │
│ 1. Loads context:                                              │
│    - Your message: "Create a Python script..."                 │
│    - Last 30 messages from JSONL                               │
│    - MEMORY.md (personal facts)                                │
│    - System prompt (tools available)                           │
│    - Tool definitions (exec, read, write, etc.)                │
│                                                                 │
│ 2. Prepares request for LLM:                                   │
│    {                                                            │
│      "model": "mistralai/mixtral-8x7b",                        │
│      "messages": [                                             │
│        {"role": "system", "content": "You are..."},            │
│        {"role": "user", "content": "... history ..."},         │
│        {"role": "user", "content": "Create Python script"}     │
│      ],                                                         │
│      "tools": [                                                │
│        {"name": "exec", "description": "Run commands"},        │
│        {"name": "write", "description": "Write files"},        │
│        ...                                                      │
│      ]                                                          │
│    }                                                            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ LLM API (OpenRouter / Anthropic / OpenAI / etc.)               │
│                                                                 │
│ The "AI Model" (Mistral, Claude, GPT, etc.)                    │
│ • Reads your request + context                                 │
│ • Understands what you're asking                               │
│ • Decides: "I should use 'write' tool to create a file"        │
│ • Returns:                                                      │
│   {                                                             │
│     "role": "assistant",                                        │
│     "content": "I'll create the script...",                    │
│     "tool_calls": [                                            │
│       {                                                         │
│         "name": "write",                                        │
│         "arguments": {                                          │
│           "path": "~/.openclaw/workspace/primes.py",           │
│           "content": "def is_prime(n):\n    ..."               │
│         }                                                       │
│       }                                                         │
│     ]                                                           │
│   }                                                             │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ AGENT (Tool Executor)                                           │
│ • Sees: "write tool was called"                                │
│ • Executes: write file to ~/.openclaw/workspace/primes.py      │
│ • Result: File created ✅                                       │
│                                                                 │
│ More examples of tool calls:                                    │
│ • "exec" → runs shell: python ~/.openclaw/workspace/primes.py  │
│ • "read" → reads a file                                        │
│ • "web_search" → searches Google                               │
│ • "browser" → opens/clicks browser                             │
│ • "message" → sends message back to Telegram                   │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ RESPONSE                                                         │
│ "I've created the prime numbers script at:                      │
│ ~/.openclaw/workspace/primes.py                                 │
│                                                                 │
│ def is_prime(n):                                                │
│     if n < 2:                                                   │
│         return False                                            │
│     ..."                                                        │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ CHANNEL (Send back to user)                                     │
│ Telegram message: "I've created the prime numbers script..."    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Detailed Explanation of Each Step

### **Step 1: You send a message**

```
You (on Telegram): "Create a Python script to calculate prime numbers"
```

---

### **Step 2: Gateway receives it**

```javascript
// Gateway polls Telegram API every few seconds
const updates = await telegram.getUpdates();

// Finds your message
const message = {
  chat_id: 7900212479,
  text: "Create a Python script to calculate prime numbers",
  date: 1707158400
};

// Stores in JSONL session file
fs.appendFile(
  "~/.openclaw/agents/main/sessions/agent:main:telegram:dm:7900212479.jsonl",
  JSON.stringify({
    role: "user",
    content: "Create a Python script to calculate prime numbers"
  }) + "\n"
);
```

---

### **Step 3: Agent loads context**

The Pi Agent reads:

```typescript
// 1. Conversation history from JSONL
const history = [
  { role: "user", content: "Hello" },
  { role: "assistant", content: "Hi! How can I help?" },
  { role: "user", content: "Create a Python script..." }
];

// 2. Personal memory
const memory = fs.readFileSync("~/.openclaw/workspace/MEMORY.md", "utf8");
// Content: "User prefers Python. Works in engineering..."

// 3. Available tools
const tools = [
  {
    name: "exec",
    description: "Run shell commands",
    parameters: { command: "string", timeout: "number" }
  },
  {
    name: "write",
    description: "Write or create a file",
    parameters: { path: "string", content: "string" }
  },
  {
    name: "read",
    description: "Read file contents",
    parameters: { path: "string" }
  },
  // ... more tools
];

// 4. System prompt (instructions)
const systemPrompt = `
You are a helpful AI assistant. You have access to the following tools:
- exec: Run shell commands
- write: Create/modify files
- read: Read files
- web_search: Search the web
- browser: Control a browser

Your workspace: ~/.openclaw/workspace

User's personal context:
${memory}

When the user asks you to do something:
1. Understand what they want
2. Use the appropriate tools
3. Provide a clear response

Be concise and helpful.
`;
```

---

### **Step 4: Prepare LLM request**

Agent builds the request that goes to the LLM:

```json
{
  "model": "mistralai/mixtral-8x7b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful AI assistant. You have access to the following tools: exec, write, read, web_search, browser. Your workspace is ~/.openclaw/workspace ..."
    },
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help?"
    },
    {
      "role": "user",
      "content": "Create a Python script to calculate prime numbers"
    }
  ],
  "tools": [
    {
      "name": "exec",
      "description": "Run shell commands in the workspace",
      "parameters": {
        "type": "object",
        "properties": {
          "command": {"type": "string"},
          "timeout": {"type": "number"}
        }
      }
    },
    {
      "name": "write",
      "description": "Write or create a file",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {"type": "string"},
          "content": {"type": "string"}
        }
      }
    }
    // ... more tools ...
  ]
}
```

---

### **Step 5: LLM processes the request**

**The LLM (Mistral 8x7b) receives your request.**

LLM's "thinking":
```
The user wants: "Create a Python script to calculate prime numbers"

Available tools:
- exec: Run commands
- write: Create files
- read: Read files
- ...

My plan:
1. Use 'write' to create a Python file with the prime number script
2. Optionally use 'exec' to run it
3. Return the result

Let me construct the response:
```

**LLM's response:**

```json
{
  "role": "assistant",
  "content": "I'll create a Python script that calculates prime numbers. Let me write that for you.",
  "tool_calls": [
    {
      "id": "call_123",
      "name": "write",
      "arguments": {
        "path": "~/.openclaw/workspace/primes.py",
        "content": "def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprimes = [n for n in range(2, 100) if is_prime(n)]\nprint(primes)"
      }
    }
  ]
}
```

---

### **Step 6: Agent executes the tools**

The Agent sees: "The LLM called the 'write' tool"

```typescript
// Execute the write tool
const path = "~/.openclaw/workspace/primes.py";
const content = "def is_prime(n):\n    ...";

fs.writeFileSync(path, content);

// Tool result
const result = {
  status: "success",
  message: "File created at ~/.openclaw/workspace/primes.py"
};
```

The Agent now has:
- ✅ File created at `~/.openclaw/workspace/primes.py`
- ✅ Tool execution result

---

### **Step 7: Agent sends back to LLM (optional)**

If there are more tool calls to process or if the Agent wants to check the result:

```json
{
  "role": "user",
  "content": "Tool: write executed successfully. File created."
}
```

LLM might then say:
```
"Great! The file has been created at ~/.openclaw/workspace/primes.py. 
The script contains a function to check if a number is prime and 
prints all primes between 2 and 100."
```

---

### **Step 8: Final response to user**

Agent collects everything and sends back:

```
Your response on Telegram:

"I've created a Python script for calculating prime numbers!

The script is saved at: ~/.openclaw/workspace/primes.py

Here's what it does:
- Defines an is_prime() function
- Calculates all prime numbers from 2 to 100
- Prints them out

You can run it with: python ~/.openclaw/workspace/primes.py

Output will be: [2, 3, 5, 7, 11, 13, ...]"
```

---

## The "Control" Part You Asked About

> "send the command that got it open and open Claude into my computer execute that i say right"

**YES! Here's how it works:**

### **Example 1: Run a Python script**

```
USER: "Run the prime numbers script you created"

LLM thinks: "User wants to run ~/openclaw/workspace/primes.py"

LLM calls: exec tool with command "python ~/.openclaw/workspace/primes.py"

Agent executes: shell command runs

Output returned:
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, ...]

Sent back to Telegram: "Here are the prime numbers: [2, 3, 5, ...]"
```

---

### **Example 2: Open a web browser**

```
USER: "Search for Python documentation and show me"

LLM thinks: "I should use web_search and browser tools"

LLM calls:
1. web_search tool: "python documentation"
2. browser tool: navigate to https://docs.python.org

Agent:
1. Searches and gets results
2. Opens browser to documentation
3. Takes screenshot

Response: "I've opened Python docs for you. Here's what I see: [screenshot]"
```

---

### **Example 3: Execute shell command**

```
USER: "Create a directory called 'my_projects' on my desktop and list files there"

LLM calls:
1. exec: mkdir /mnt/c/Users/HP/Desktop/my_projects
2. exec: ls /mnt/c/Users/HP/Desktop/my_projects

Agent executes both commands

Response: "Directory created! It's currently empty."
```

---

## The Model's Role vs The Agent's Role

### **LLM Model's Job:**
- ✅ Understand what you're asking
- ✅ Decide which tools to use
- ✅ Generate the tool calls
- ✅ Provide a human-readable explanation

### **Agent's Job:**
- ✅ Execute the tools the LLM specified
- ✅ Capture the results
- ✅ Send results back to LLM (if needed)
- ✅ Return the final response to you

### **Key Point:**
**The LLM doesn't directly execute commands.** It just says "execute this tool with these parameters." The Agent is what actually:
- Runs the command
- Writes the file
- Reads the file
- Searches the web
- Controls the browser

---

## Real Example: "Open VS Code"

```
YOU: "Open VS Code for me with the openclaw project"

AGENT FLOW:
1. Receives message on Telegram
2. Loads context
3. Calls LLM with: "Open VS Code with openclaw project"

LLM thinks:
- User wants to open VS Code
- Should navigate to ~/openclaw directory
- Should open it with 'code .' command
- This is an exec command

LLM responds:
{
  "content": "I'll open VS Code with the OpenClaw project for you.",
  "tool_calls": [
    {
      "name": "exec",
      "arguments": {
        "command": "cd ~/openclaw && code ."
      }
    }
  ]
}

AGENT executes:
- Shell runs: cd ~/openclaw && code .
- VS Code opens on your screen

RESPONSE TO YOU ON TELEGRAM:
"Done! I've opened VS Code with the OpenClaw project. 
The directory ~/openclaw should now be open in your editor."
```

---

## Summary: How "Control" Happens

```
1. You request something on Telegram
   ↓
2. Gateway receives it
   ↓
3. Agent loads context (history + MEMORY + tools)
   ↓
4. LLM (Mistral, Claude, GPT) "understands" what you want
   ↓
5. LLM decides which TOOLS to use (exec, write, read, web_search, browser, etc.)
   ↓
6. Agent EXECUTES those tools on YOUR computer
   ↓
7. Results sent back to you on Telegram
```

**The LLM is the "brain" (decides what to do).**
**The Agent is the "hands" (actually does it).**

---

## Available Tools (What the Agent Can "Control")

| Tool | What it does | Example |
|------|-------------|---------|
| **exec** | Run shell commands | `python script.py`, `mkdir folder`, `npm install` |
| **write** | Create/modify files | Create Python scripts, edit config files |
| **read** | Read file contents | Read MEMORY.md, read code files |
| **web_search** | Search the web | Find documentation, news, information |
| **web_fetch** | Download web content | Extract text from websites |
| **browser** | Control a browser | Open URL, click buttons, fill forms, screenshot |
| **message** | Send messages | Post to Telegram, Discord, Slack |
| **image** | Analyze images | Describe an image, read text from image |
| **canvas** | Render UI | Show custom interfaces, dashboards |
| **nodes** | Control devices | Access Mac/iOS/Android phones paired to it |
| **sessions** | Multi-agent | Spawn sub-agents, run parallel tasks |

---

## Summary

**You were RIGHT!** The model interprets your language, decides which tools to use, and the agent executes those tools on your computer. The LLM tells the agent WHAT to do, and the agent actually DOES it.

