# How OpenClaw Works + Tokens + Model Changes

## 1. Complete Workflow: From Message to Response

### Step-by-Step (With Details)

#### **User sends a message on Telegram:**
```
You: "Create a Python script that calculates prime numbers"
```

---

#### **Step 1: Gateway receives the message (no cost)**
- Gateway polls Telegram API every few seconds
- Finds your message: `chat_id=7900212479, text="Create a Python script..."`
- Creates or updates session file: 
  ```
  ~/.openclaw/agents/main/sessions/agent:main:telegram:dm:7900212479.jsonl
  ```
- Appends your message as JSONL line:
  ```json
  {"role":"user","content":"Create a Python script that calculates prime numbers","timestamp":"2026-02-05T..."}
  ```

---

#### **Step 2: Agent loads context (no cost)**
Pi Agent reads:
1. **Session history** from JSONL (last 20-50 messages, depending on model)
2. **MEMORY.md** (from `~/.openclaw/workspace/MEMORY.md`)
   - Example content: "User prefers Python over JavaScript, works at Company X"
3. **System prompt** (built dynamically):
   ```
   You are a helpful AI assistant. You have the following tools available:
   - exec: Run shell commands
   - read: Read files
   - write: Write files
   - web_search: Search the web
   - browser: Control browser
   ... (more tools listed)
   
   Your workspace is at: ~/.openclaw/workspace/
   ```
4. **Tool definitions** (schema of all available tools)

---

#### **Step 3: Call LLM API (COSTS TOKENS)**
Agent sends to OpenRouter API:
```
URL: https://openrouter.ai/api/v1/chat/completions
Headers: Authorization: Bearer sk-or-v1-131ebfa...
Body:
{
  "model": "mistralai/mixtral-8x7b-instruct",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant..."},
    {"role": "user", "content": "... last 50 messages from history"},
    {"role": "user", "content": "Create a Python script that calculates prime numbers"}
  ],
  "tools": [...all available tools schema...],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**TOKENS USED:**
- Input tokens: ~500-2000 (depends on conversation length)
- Output tokens: ~200-500 (depends on response length)
- **Total: ~700-2500 tokens per message**

---

#### **Step 4: LLM processes and responds (TOKENS CONSUMED)**
LLM (Mistral 8x7b) analyzes:
- Your request
- Available tools
- Instructions in system prompt
- Past conversation history

Response:
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "I'll create a Python script for you:\n\n```python\ndef is_prime(n):\n    ...\n```"
    }
  }],
  "usage": {
    "prompt_tokens": 1200,
    "completion_tokens": 450,
    "total_tokens": 1650
  }
}
```

---

#### **Step 5: Agent saves response (no cost)**
Appends to JSONL:
```json
{"role":"assistant","content":"I'll create a Python script...\n```python\n...","timestamp":"2026-02-05T..."}
```

---

#### **Step 6: Gateway sends back to Telegram (no cost)**
Messages you on Telegram:
```
Bot: I'll create a Python script for calculating prime numbers...

def is_prime(n):
    if n < 2:
        return False
    ...
```

---

### Summary of the Flow

```
┌────────────────────────────────────────────────────────┐
│ You send message on Telegram                          │
└─────────────────┬──────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│ Gateway polls & receives (NO COST)                    │
│ - Reads JSONL session file                            │
│ - Appends your message                                │
└─────────────────┬──────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│ Agent loads context (NO COST)                         │
│ - Reads last N messages from JSONL                    │
│ - Reads MEMORY.md                                     │
│ - Builds system prompt + tools                        │
└─────────────────┬──────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│ Call LLM API (COSTS TOKENS!)                          │
│ - Input: context + your message                       │
│ - Output: LLM response                                │
│ - Tokens: ~700-2500 per message                       │
└─────────────────┬──────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│ Agent saves & sends response (NO COST)                │
│ - Appends response to JSONL                           │
│ - Sends to Telegram                                   │
└────────────────────────────────────────────────────────┘
```

---

## 2. Token Costs & Models

### What are Tokens?

**Tokens** = units of text that the LLM charges you for. Think of them as "words" (roughly).

```
Example sentence: "Create a Python script for calculating prime numbers"
Tokens: Create | a | Python | script | for | calculating | prime | numbers
~8 tokens (usually 1 token ≈ 0.75 words)
```

### Token Counting

- **Input tokens** (what you send to LLM)
  - Your message + conversation history + system prompt
  - Cost: $X per 1M input tokens
  
- **Output tokens** (what LLM generates)
  - LLM's response
  - Cost: $Y per 1M output tokens (usually 2-5x more expensive than input)

### Example Cost Calculation

**Your setup:** OpenRouter + Mistral 8x7b

OpenRouter pricing (as of Feb 2026):
- Input: $0.14 per 1M tokens
- Output: $0.42 per 1M tokens

**You send one message:**
- Input: 1,500 tokens
- Output: 500 tokens
- **Cost:** 
  - Input: 1,500 × ($0.14 / 1M) = $0.00021
  - Output: 500 × ($0.42 / 1M) = $0.00021
  - **Total: ~$0.0004 per message (~0.04 cents)**

---

### Monthly Cost Estimation

If you send **10 messages per day**:
- Messages/month: 300
- Avg tokens/message: 2,000 (1,500 input + 500 output)
- Total tokens: 600,000
- **Cost: ~$0.13/month** (very cheap!)

If you send **100 messages per day**:
- Messages/month: 3,000
- Avg tokens: 2,000
- Total tokens: 6M
- **Cost: ~$1.30/month**

If you **use Claude Opus-4.5** (30x more expensive):
- Same 10 messages/day
- **Cost: ~$4/month**

---

## 3. What Happens When You Run Out of Tokens?

**You don't "run out" - you pay per-token.**

OpenRouter doesn't have a limit. You can:
- Use $5/month
- Use $50/month
- Use $500/month
- All billed to your account

**If you want limits:**
1. Set up billing alerts on OpenRouter
2. Use OpenAI's `usage_limits` (if using OpenAI)
3. Manually track your usage

---

## 4. Changing Models

### Current Setup
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/mistralai/mixtral-8x7b-instruct"
      }
    }
  },
  "env": {
    "OPENROUTER_API_KEY": "sk-or-v1-..."
  }
}
```

### How to Change

#### **Option A: Edit config file**

Edit `~/.openclaw/openclaw.json`:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/meta-llama/llama-2-70b-chat"
      }
    }
  }
}
```

Then restart gateway:
```bash
systemctl --user restart openclaw-gateway
```

#### **Option B: Use CLI**

```bash
# Not directly supported, so use Option A
```

#### **Option C: In TUI/Chat**

When chatting, you can sometimes change model mid-conversation:
```
/model openrouter/meta-llama/llama-2-70b
```
(If your model supports model switching)

---

### Popular Models on OpenRouter

| Model | Cost | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **Mistral 8x7b** (current) | ✅ Cheap | ⚡ Fast | ✅ Good | General purpose |
| **Llama 2 70b** | 💰 Medium | ⚡ Medium | ✅ Good | General purpose |
| **Claude 3.5 Sonnet** | 💰💰 Expensive | 🐢 Slow | ⭐⭐⭐ Best | Complex reasoning |
| **GPT-4o** | 💰💰 Expensive | 🐢 Slow | ⭐⭐⭐ Best | Coding + analysis |
| **Deepseek v3** | ✅ Cheap | ⚡ Fast | ✅ Good | New, very capable |

### How to Switch to Claude

1. Get Anthropic API key from https://console.anthropic.com/
2. Create auth profile:
   ```bash
   openclaw login --provider anthropic
   ```
   (Paste your API key when prompted)

3. Edit `~/.openclaw/openclaw.json`:
   ```json
   {
     "agents": {
       "defaults": {
         "model": {
           "primary": "anthropic/claude-opus-4-5"
         }
       }
     }
   }
   ```

4. Restart:
   ```bash
   systemctl --user restart openclaw-gateway
   ```

---

## 5. Token Limits & Context Window

Each model has a **context window** (max tokens it can see):

| Model | Context Window | Max Output |
|-------|----------------|-----------|
| Mistral 8x7b | 32k tokens | 4k tokens |
| Llama 2 70b | 4k tokens | 2k tokens |
| Claude 3.5 Sonnet | **200k tokens** 🔥 | 4k tokens |
| GPT-4o | **128k tokens** | 4k tokens |

**Context window** = max conversation length the model sees.

If you have 100 messages in your session JSONL, but the model has a 32k context limit:
- Agent loads last ~15-20 messages that fit in 32k
- Older messages are not sent to LLM
- But JSON history keeps all messages (for your memory)

---

## 6. Fallback Models

If your primary model fails, OpenClaw can fallback to another:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openrouter/mistralai/mixtral-8x7b-instruct",
        "fallbacks": [
          "openrouter/meta-llama/llama-2-70b-chat",
          "anthropic/claude-opus-4-5"
        ]
      }
    }
  }
}
```

If Mistral fails → try Llama 2 → try Claude.

---

## 7. Checking Your Token Usage

### On OpenRouter

1. Log in to https://openrouter.ai/
2. Go to Dashboard → Usage
3. See tokens used, cost, per-model breakdown

### Locally

OpenClaw logs token usage. Check:
```bash
journalctl --user -u openclaw-gateway | grep "tokens"
```

Or check TUI:
When chatting, the bottom shows:
```
tokens 2000/32k (6%)  # Using 2000 out of 32k available
```

---

## Summary Table

| Question | Answer |
|----------|--------|
| **What are tokens?** | Units of text (1 token ≈ 0.75 words) |
| **Do I "run out"?** | No, you pay per-token used |
| **Cost per message?** | $0.0004-0.01 (Mistral) to $0.05+ (Claude) |
| **How to change model?** | Edit `openclaw.json` → `agents.defaults.model.primary` |
| **How to use Claude?** | Get API key → `openclaw login --provider anthropic` → change model |
| **What if model fails?** | Fallback to next model in `fallbacks` list |
| **Check usage?** | OpenRouter dashboard or `journalctl` logs |
| **Context limit?** | 32k (Mistral) to 200k (Claude) tokens |

