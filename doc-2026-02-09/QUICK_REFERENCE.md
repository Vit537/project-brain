# 🎤 JARVIS Quick Reference Card

## 🚀 Starting JARVIS

### Quick Start
```bash
start_jarvis_background.bat
```
Then choose your mode!

### Or Start Directly
```bash
# System tray (recommended)
python src/background/system_tray.py

# Console mode
python src/background/jarvis_daemon.py

# Normal interactive
python src/main.py
```

---

## 🎯 Activation Methods

| Method | Command | Works When |
|--------|---------|------------|
| **Wake Word** | Say "Hi Jarvis" | Anytime (app running) |
| **Hotkey** | Press `CTRL+ALT+J` | Anytime (app running) |
| **System Tray** | Right-click icon → Activate | Anytime (tray mode) |

---

## 💬 Voice Commands Cheat Sheet

### 📝 File Operations
```
"Create file todo.txt on desktop"
"Write 'buy milk' to shopping.txt on desktop"  
"Read notes.txt from documents"
"Create folder Projects on desktop"
"Move file report.txt from downloads to documents"
"Search for Python in documents"
```

### 📋 Notes
```
"Take a note: dentist tomorrow at 3pm"
"Note titled Shopping: eggs, milk, bread"
"List my notes"
"Read my latest note"
```

### ⏰ Time & System
```
"What time is it?"
"What's the date today?"
"System status"
"Calculate 25 times 4"
```

### 🚀 Applications
```
"Open Chrome"
"Launch Notepad"
"Start Calculator"
```

### 👋 Exit
```
"Goodbye"
"Exit"
"Quit"
```

---

## 📍 Quick Locations

Use these shortcuts in commands:
- `desktop` → Your Desktop folder
- `documents` → Your Documents folder
- `downloads` → Your Downloads folder
- `notes` → JARVIS_Notes folder

**Example:** "Create file test.txt on desktop"

---

## 🔧 Auto-Start Setup

1. Run: `setup_autostart.bat`
2. Choose **Option 1** (Task Scheduler)
3. ✅ Done! JARVIS starts with Windows

**To disable:**
- Open Task Scheduler
- Find "JARVIS_Assistant"
- Right-click → Disable or Delete

---

## 📁 Important Locations

| Item | Location |
|------|----------|
| **Voice Notes** | `Documents\JARVIS_Notes\` |
| **Config** | `backend\config\` |
| **Logs** | Console output |
| **Test Files** | Desktop (cleanup manually) |

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| Wake word not working | Speak louder, check microphone |
| Hotkey not working | Run as administrator |
| High CPU | Use `--no-wake-word` flag |
| No tray icon | Install: `pip install pystray pillow` |
| Voice errors | Check microphone permissions |

---

## ⚙️ Command Line Options

```bash
# Disable wake word
python src/background/jarvis_daemon.py --no-wake-word

# Disable hotkey
python src/background/jarvis_daemon.py --no-hotkey

# Both disabled (manual activation only)
python src/background/jarvis_daemon.py --no-wake-word --no-hotkey
```

---

## 🎨 Customization

### Change Wake Words
Edit: `src/services/wake_word_service.py`
```python
self.wake_words = [
    "hi jarvis",
    "hey jarvis",
    "your custom phrase"
]
```

### Change Hotkey
Edit: `src/background/jarvis_daemon.py`
```python
keyboard.add_hotkey('ctrl+alt+j', on_hotkey)
# Change to your preferred combination
```

---

## 📊 Performance Stats

| Metric | Value |
|--------|-------|
| CPU (idle) | ~5-10% |
| CPU (hotkey only) | <1% |
| Memory | ~150MB |
| Wake latency | <500ms |
| Response time | 1-2s |

---

## 🎯 Best Practices

✅ **Do:**
- Speak clearly and naturally
- Use quick locations (desktop, documents)
- Say "take a note" for quick thoughts
- Use hotkey for instant access

❌ **Don't:**
- Shout at JARVIS (normal voice works)
- Use complex file paths (use quick locations)
- Expect instant responses (AI takes 1-2s)

---

## 🚨 Emergency Stop

**Kill JARVIS immediately:**
1. Find tray icon → Right-click → Quit
2. Or close console window
3. Or Task Manager → End "python.exe" (JARVIS)

---

## 📞 Quick Help

| Task | Command |
|------|---------|
| Test voice | `python test_wake_word.py` |
| Test files | `python test_file_ops_enhanced.py` |
| Full test | `python test_complete_system.py` |
| Run normal | `python src/main.py` |
| Run background | `start_jarvis_background.bat` |

---

## 🎉 Pro Tips

1. **Battery Saving:** Use hotkey-only mode on laptop
2. **Quick Notes:** Just say "note: your text here"
3. **File Creation:** JARVIS creates parent folders automatically
4. **Multi-Language:** Works in English and Spanish
5. **Confirmation:** Destructive actions ask for confirmation

---

**Made with ❤️ - Your Personal AI Assistant**

---

*Print this card or save it for quick reference!*
