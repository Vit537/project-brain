# PRACTICAL GUIDE: Where Am I & How To Work With OpenClaw

## 🌍 Where You Are Right Now

You're in **TWO environments**:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PRODUCTION OpenClaw (Already Running!)                  │
├─────────────────────────────────────────────────────────────┤
│ Location: /usr/lib/node_modules/openclaw                   │
│ Status: ✅ Active (systemd service)                        │
│ Port: 18789                                                 │
│ Command: systemctl --user status openclaw-gateway          │
│ Config: ~/.openclaw/openclaw.json                          │
│                                                             │
│ This is the PRODUCTION version you're using right now!     │
│ Your Telegram bot is connected to THIS version.            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. DEVELOPMENT OpenClaw (Source Code)                      │
├─────────────────────────────────────────────────────────────┤
│ Location: /home/hpdev/openclaw                             │
│ Status: 📁 Just files (not running)                        │
│ Purpose: Edit code, make changes, test                     │
│                                                             │
│ This is where you EDIT and BUILD the project.              │
│ Changes here don't affect production until you build       │
│ and reinstall.                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 The Difference from React/Next/Django

### **React/Next/Django:**
```bash
npm run dev          # Starts dev server
python manage.py runserver   # Starts dev server

# Changes are reflected IMMEDIATELY
# Easy to see your edits
```

### **OpenClaw:**
```bash
# Step 1: Edit source code
vim src/gateway/index.ts

# Step 2: Build (compile TypeScript → JavaScript)
pnpm build

# Step 3: Reinstall globally
sudo npm install -g .

# Step 4: Restart service
systemctl --user restart openclaw-gateway

# NOW your changes are live!
```

**Why different?**
- OpenClaw runs as a **system service** (like nginx, mysql)
- It's NOT a dev server that auto-reloads
- It needs to be built and installed

---

## ✅ Checking What's Running

### **Is OpenClaw running right now?**
```bash
systemctl --user status openclaw-gateway
```

**What you see:**
```
● openclaw-gateway.service - OpenClaw Gateway (v2026.2.2)
   Active: active (running) since Sun 2026-02-08 16:29:35
```

✅ **YES, it's running!**

---

### **Where is the running version?**
```bash
which openclaw-gateway
# Output: /usr/lib/node_modules/openclaw/dist/cli.js
```

This is the **installed production version**.

---

### **What version is running?**
```bash
openclaw-gateway --version
# Output: 2026.2.2
```

---

## 📂 Working with the Source Code

### **1. Check Dependencies**

First, see if dependencies are installed:
```bash
cd ~/openclaw
ls node_modules
```

If `node_modules/` doesn't exist:
```bash
pnpm install
```

This downloads all the packages OpenClaw needs (like `npm install` in React).

---

### **2. Build the Project**

Compile TypeScript → JavaScript:
```bash
pnpm build
```

**What happens:**
```
src/gateway/index.ts  →  dist/gateway/index.js
src/cli/commands.ts   →  dist/cli/commands.js
... (all TypeScript files compiled)
```

**Output:** `dist/` folder with compiled JavaScript.

---

### **3. Run Tests**

Make sure nothing is broken:
```bash
pnpm test
```

---

### **4. Install Your Changes Globally**

Once you're happy with your edits:
```bash
# From ~/openclaw directory
sudo npm install -g .
```

This copies `dist/*` to `/usr/lib/node_modules/openclaw/`.

---

### **5. Restart the Gateway**

Apply your changes:
```bash
systemctl --user restart openclaw-gateway
```

Check it worked:
```bash
systemctl --user status openclaw-gateway
```

---

## 🛠️ Development Workflow Example

Let's say you want to **remove WhatsApp support**:

### **Step 1: Edit the code**
```bash
cd ~/openclaw
code .   # Opens VS Code
```

In VS Code:
- Delete `src/channels/whatsapp/` folder
- Remove WhatsApp imports from `src/channels/index.ts`

---

### **Step 2: Build**
```bash
pnpm build
```

Check for errors:
```
✓ Build succeeded (no errors)
```

---

### **Step 3: Test locally (optional)**

Before installing, you can test:
```bash
# Run from dist/ folder directly
node dist/cli.js --help
```

---

### **Step 4: Install globally**
```bash
sudo npm install -g .
```

Output:
```
changed 1 package in 2s
```

---

### **Step 5: Restart**
```bash
systemctl --user restart openclaw-gateway
```

---

### **Step 6: Verify**
```bash
# Check logs
journalctl --user -u openclaw-gateway -n 50
```

Look for errors. If none, you're good! ✅

---

## 🚀 Quick Reference Commands

| Task | Command |
|------|---------|
| **Check if running** | `systemctl --user status openclaw-gateway` |
| **Check version** | `openclaw-gateway --version` |
| **Check production location** | `which openclaw-gateway` |
| **Install dependencies** | `pnpm install` |
| **Build project** | `pnpm build` |
| **Run tests** | `pnpm test` |
| **Install changes globally** | `sudo npm install -g .` |
| **Restart gateway** | `systemctl --user restart openclaw-gateway` |
| **View logs** | `journalctl --user -u openclaw-gateway -f` |
| **Stop gateway** | `systemctl --user stop openclaw-gateway` |
| **Start gateway** | `systemctl --user start openclaw-gateway` |

---

## 🧪 Development Server (Alternative)

**Want live reloading like React?**

You can run OpenClaw in development mode:

### **Step 1: Stop production version**
```bash
systemctl --user stop openclaw-gateway
```

### **Step 2: Run dev server**
```bash
cd ~/openclaw
pnpm dev
```

**What happens:**
- Gateway runs from `src/` directly (no build needed)
- Auto-reloads on file changes
- Logs appear in terminal

**Downsides:**
- Your Telegram bot might not work correctly
- Some features may not work in dev mode
- Not suitable for 24/7 use

### **Step 3: When done, restart production**
```bash
pnpm build
sudo npm install -g .
systemctl --user start openclaw-gateway
```

---

## 📊 Summary: React vs OpenClaw

| Aspect | React/Next | OpenClaw |
|--------|-----------|----------|
| **Language** | JavaScript/TypeScript | TypeScript |
| **Dev command** | `npm run dev` | `pnpm dev` (optional) |
| **Build command** | `npm run build` | `pnpm build` |
| **Production** | Deploy to Vercel/server | Install globally + systemd |
| **Auto-reload?** | ✅ Yes (dev server) | ❌ No (system service) |
| **Check status** | Visit localhost:3000 | `systemctl status openclaw-gateway` |
| **View logs** | Terminal output | `journalctl` |
| **Restart** | Ctrl+C, then rerun | `systemctl restart` |

---

## 🎯 Your Current Status

Based on the checks we ran:

✅ **OpenClaw is running** (systemd service active)  
✅ **You're in the source code directory** (`~/openclaw`)  
✅ **You have dependencies installed** (probably - check with `ls node_modules`)  
❓ **You haven't built the project yet** (probably - check with `ls dist`)  

### **Next Steps:**

1. **Try building:**
   ```bash
   pnpm build
   ```

2. **Check if it worked:**
   ```bash
   ls dist/
   ```

3. **Read your code in VS Code:**
   ```bash
   code .
   ```

4. **When ready to make changes, follow the workflow above!**

---

## 🆘 Troubleshooting

### **"pnpm: command not found"**

Install pnpm:
```bash
npm install -g pnpm
```

---

### **"Permission denied" when running npm install**

Use sudo:
```bash
sudo npm install -g .
```

---

### **"Build failed"**

Check the error message. Common issues:
- Missing dependencies: `pnpm install`
- TypeScript errors: Fix the code errors
- Syntax errors: Check what you changed

---

### **"Gateway won't start"**

Check config:
```bash
cat ~/.openclaw/openclaw.json
```

Check logs:
```bash
journalctl --user -u openclaw-gateway -n 100
```

---

### **"Changes not reflected"**

Did you:
1. ✅ Build? (`pnpm build`)
2. ✅ Install? (`sudo npm install -g .`)
3. ✅ Restart? (`systemctl --user restart openclaw-gateway`)

All three steps are required!

---

## 🎓 Final Thoughts

OpenClaw is **different from a typical web app**:

- It's a **system service** (like a database or web server)
- It runs **24/7 in the background**
- Changes require **build → install → restart**
- It's **multi-channel** (Telegram, WhatsApp, Discord, etc.)
- It's **self-hosted** (runs on YOUR machine)

Think of it more like:
- **nginx** (web server that runs 24/7)
- **mysql** (database that runs 24/7)
- **docker** (container runtime that runs 24/7)

Rather than:
- **React** (dev server for building UIs)
- **Next.js** (web framework)
- **Django** (web framework)

---

## 🚀 Ready to Start?

1. **First, explore the code:**
   ```bash
   code .
   ```

2. **Try building:**
   ```bash
   pnpm build
   ```

3. **When you're ready to make changes, come back to this guide!**
