# YOUR ACTUAL SETUP: How OpenClaw is Running on Your Machine

## 🎯 The Reality

**Good news!** Your setup is **better** than a typical installation. Here's what you actually have:

```
┌─────────────────────────────────────────────────────────────┐
│ OpenClaw is running from YOUR DEVELOPMENT DIRECTORY!       │
├─────────────────────────────────────────────────────────────┤
│ Service: openclaw-gateway.service                          │
│ Binary: /home/hpdev/openclaw/dist/index.js                │
│ Port: 18789                                                 │
│ Status: ✅ Active (running since 16:29)                    │
│                                                             │
│ This means:                                                 │
│ • You edit files in ~/openclaw/src/                        │
│ • You build: pnpm build                                    │
│ • You restart: systemctl --user restart openclaw-gateway   │
│ • Done! No sudo, no global install needed!                 │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ What's Already Done

Based on what I found:

1. ✅ **Dependencies installed** (`node_modules/` exists)
2. ✅ **Project built** (`dist/` folder exists)
3. ✅ **Service running** (systemctl shows active)
4. ✅ **Running from dev directory** (not global install)

**You're ready to start developing!**

---

## 🚀 Your Simple Workflow

Unlike React/Next where you run `npm run dev`, here's YOUR workflow:

### **Step 1: Edit Code**

Open VS Code:
```bash
code .
```

Edit any file in `src/`, for example:
- `src/gateway/index.ts` - Gateway logic
- `src/channels/telegram/index.ts` - Telegram bot
- `src/agents/pi-embedded-runner/index.ts` - AI agent logic

---

### **Step 2: Build**

Compile TypeScript → JavaScript:
```bash
pnpm build
```

**Output:**
```
✓ Built in 2.5s
```

This updates the `dist/` folder.

---

### **Step 3: Restart**

Apply your changes:
```bash
systemctl --user restart openclaw-gateway
```

**That's it!** Your changes are live.

---

### **Step 4: Check Logs (Optional)**

See what's happening:
```bash
journalctl --user -u openclaw-gateway -f
```

Press `Ctrl+C` to stop viewing logs.

---

## 🔄 Complete Example: Make a Simple Change

Let's try a harmless edit:

### **Edit a file:**
```bash
nano src/gateway/supervisor.ts
```

Find any console.log and add your own:
```typescript
console.log('🎉 Gateway starting - Hello from HP!');
```

Save (`Ctrl+O`, Enter, `Ctrl+X`)

---

### **Build:**
```bash
pnpm build
```

---

### **Restart:**
```bash
systemctl --user restart openclaw-gateway
```

---

### **Check logs:**
```bash
journalctl --user -u openclaw-gateway -n 20
```

**You should see:**
```
Feb 08 17:00:00 node[123]: 🎉 Gateway starting - Hello from HP!
```

✅ **Your change worked!**

---

## 📋 Quick Reference

### **Your Service File:**
```bash
~/.config/systemd/user/openclaw-gateway.service
```

**Contains:**
```ini
[Service]
ExecStart=/usr/bin/node /home/hpdev/openclaw/dist/index.js gateway --port 18789
```

This points to **YOUR development directory**, not a global install.

---

### **Key Locations:**

| What | Where |
|------|-------|
| **Source code** | `/home/hpdev/openclaw/src/` |
| **Built code** | `/home/hpdev/openclaw/dist/` |
| **Dependencies** | `/home/hpdev/openclaw/node_modules/` |
| **Config file** | `~/.openclaw/openclaw.json` |
| **Session logs** | `~/.openclaw/agents/main/sessions/*.jsonl` |
| **Service file** | `~/.config/systemd/user/openclaw-gateway.service` |
| **System logs** | `journalctl --user -u openclaw-gateway` |

---

## 🛠️ Essential Commands

| Task | Command |
|------|---------|
| **Build project** | `pnpm build` |
| **Restart gateway** | `systemctl --user restart openclaw-gateway` |
| **Check status** | `systemctl --user status openclaw-gateway` |
| **View live logs** | `journalctl --user -u openclaw-gateway -f` |
| **View last 50 logs** | `journalctl --user -u openclaw-gateway -n 50` |
| **Stop gateway** | `systemctl --user stop openclaw-gateway` |
| **Start gateway** | `systemctl --user start openclaw-gateway` |
| **Run tests** | `pnpm test` |
| **Open in VS Code** | `code .` |

---

## 🎓 Comparison: This vs React/Next

### **React/Next:**
```bash
npm run dev          # Start dev server
# Edit files
# See changes INSTANTLY
```

### **OpenClaw (Your Setup):**
```bash
pnpm build           # Compile TypeScript
systemctl --user restart openclaw-gateway
# Changes applied
```

**Why the difference?**
- React/Next: dev server with hot reload
- OpenClaw: system service (like nginx, like a database)

---

## 🧰 Development Tips

### **Tip 1: Keep a log window open**

In one terminal:
```bash
journalctl --user -u openclaw-gateway -f
```

In another terminal:
```bash
cd ~/openclaw
code .
```

Now you can see logs in real-time as you make changes!

---

### **Tip 2: Alias for quick restart**

Add to `~/.bashrc`:
```bash
alias ocr='pnpm build && systemctl --user restart openclaw-gateway'
```

Then just run:
```bash
ocr
```

---

### **Tip 3: Check for errors after build**

```bash
pnpm build && echo "Build OK!" || echo "Build FAILED!"
```

---

### **Tip 4: Test before restarting**

```bash
pnpm test
```

If tests pass, then restart.

---

## 🚨 Common Issues

### **"Build failed"**

**Check the error:**
```bash
pnpm build
```

**Common causes:**
- TypeScript type error (fix the code)
- Missing dependency (run `pnpm install`)
- Syntax error (check what you changed)

---

### **"Gateway won't start after restart"**

**Check logs:**
```bash
journalctl --user -u openclaw-gateway -n 100
```

**Look for:**
- `Error:` messages
- `Failed to start` messages
- Stack traces

**Fix and retry:**
```bash
# Fix the issue in code
pnpm build
systemctl --user restart openclaw-gateway
```

---

### **"Changes not applied"**

**Did you:**
1. ✅ Save the file? (Ctrl+S in VS Code)
2. ✅ Build? (`pnpm build`)
3. ✅ Restart? (`systemctl --user restart openclaw-gateway`)

All three required!

---

### **"pnpm command not found"**

**Install pnpm:**
```bash
npm install -g pnpm
```

---

## 📊 What Runs Where

```
┌──────────────────────────────────────────────────────────┐
│ YOUR TERMINAL                                            │
│ • You edit files in src/                                │
│ • You run: pnpm build                                   │
│ • You run: systemctl restart openclaw-gateway           │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│ SYSTEMD SERVICE (Background Process)                    │
│ • Runs: /usr/bin/node /home/hpdev/openclaw/dist/index.js│
│ • Port: 18789                                            │
│ • Polls Telegram, Discord, WhatsApp, etc.              │
│ • Responds to messages                                   │
│ • Runs 24/7 in background                               │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│ YOUR AI MODEL (Cloud API)                               │
│ • OpenRouter (Mistral, Llama, etc.)                     │
│ • Anthropic (Claude)                                     │
│ • OpenAI (GPT)                                           │
│ • Called when someone messages your bot                 │
└──────────────────────────────────────────────────────────┘
```

---

## 🎯 So... Is It Running?

**YES!** ✅

Check for yourself:
```bash
systemctl --user status openclaw-gateway
```

You should see:
```
● openclaw-gateway.service - OpenClaw Gateway (v2026.2.2)
   Active: active (running)
```

✅ **Running!**

Try messaging your Telegram bot right now - it should respond!

---

## 🎉 Next Steps

1. **Explore the code:**
   ```bash
   code .
   ```

2. **Try making a tiny change** (follow the example above)

3. **Read the other docs you created** (they're really good!)

4. **When you want to customize something, just:**
   - Edit the file
   - `pnpm build`
   - `systemctl --user restart openclaw-gateway`
   - Done!

---

## 💡 Final Thoughts

You're in **developer mode** by default, which is great!

Most people install OpenClaw globally and can't easily edit it. You have:
- ✅ Full source code
- ✅ Direct access to edit anything
- ✅ Easy build/restart workflow
- ✅ No sudo needed
- ✅ Fast iteration

**You're ready to explore and modify OpenClaw!** 🚀
