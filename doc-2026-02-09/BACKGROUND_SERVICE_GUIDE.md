# JARVIS Background Service - User Guide

## 🚀 What's New?

Your JARVIS assistant can now run in the background and respond to:
- **Wake Words**: "Hi Jarvis", "Hey Jarvis"
- **Hotkey**: CTRL+ALT+J
- **System Tray**: Right-click icon in taskbar

## ✨ New File Operations

JARVIS can now:
- ✅ **Create files with content**: "Jarvis, create a file called todo.txt with my tasks"
- ✅ **Write to files**: "Jarvis, write 'buy milk' to my shopping list"
- ✅ **Read files**: "Jarvis, what's in my notes?"
- ✅ **Take notes**: "Jarvis, take a note: meeting at 3pm"
- ✅ **List notes**: "Jarvis, list my notes"
- ✅ **Create folders**: "Jarvis, create a folder called Projects on desktop"

All notes are automatically saved to: `Documents/JARVIS_Notes/`

## 🎯 Running JARVIS

### Option 1: System Tray (Recommended)
```bash
python src/background/system_tray.py
```
- Shows icon in system tray
- Right-click for menu options
- Use hotkey CTRL+ALT+J or wake word
- Runs silently in background

### Option 2: Background Console
```bash
python src/background/jarvis_daemon.py
```
- Runs in console window
- Listens for wake word + hotkey
- Shows status messages

### Option 3: Normal Mode (Original)
```bash
python src/main.py
```
- Interactive mode
- Always listening
- Best for testing

### Option 4: Easy Launcher
```bash
start_jarvis_background.bat
```
- Menu-driven launcher
- Choose your preferred mode

## 🎤 Using Voice Commands

### File Operations Examples

**Create files:**
- "Jarvis, create a file called recipe.txt on desktop"
- "Jarvis, create todo.txt in documents"

**Write to files:**
- "Jarvis, write 'hello world' to test.txt on desktop"
- "Jarvis, append 'new line' to my notes"

**Read files:**
- "Jarvis, read myfile.txt from desktop"
- "Jarvis, what's in notes.txt?"

**Take notes:**
- "Jarvis, take a note: dentist appointment tomorrow"
- "Jarvis, note titled Shopping: buy eggs and milk"
- "Jarvis, list my notes"
- "Jarvis, read my latest note"

**Folders:**
- "Jarvis, create folder Projects on desktop"
- "Jarvis, create folder Work in documents"

**Quick locations:**
- Use "desktop", "documents", "downloads", or "notes"
- "Jarvis, create file test.txt on desktop"

## ⌨️ Hotkey

Press **CTRL+ALT+J** anywhere in Windows to activate JARVIS!

## 🗣️ Wake Words

Say any of these:
- "Hi Jarvis"
- "Hey Jarvis"
- "Hello Jarvis"
- "OK Jarvis"

## 🔧 Auto-Start on Windows Boot

### Method 1: Task Scheduler (Easy)
1. Open Task Scheduler
2. Create Basic Task
3. Name: "JARVIS Background"
4. Trigger: "At startup"
5. Action: Start program
   - Program: `C:\Python313\python.exe`
   - Arguments: `C:\Users\HP\Desktop\app-2026-agent\backend\src\background\system_tray.py`
6. ✅ Done! JARVIS will start on boot

### Method 2: Startup Folder (Quick)
1. Press `Win+R`, type `shell:startup`, press Enter
2. Create shortcut to `start_jarvis_background.bat`
3. ✅ Done!

### Method 3: Windows Service (Advanced)
Use NSSM (Non-Sucking Service Manager) for true service:
```bash
# Download NSSM from https://nssm.cc/
nssm install JarvisService "C:\Python313\python.exe" "C:\Users\HP\Desktop\app-2026-agent\backend\src\background\system_tray.py"
nssm start JarvisService
```

## 📊 System Requirements

- **CPU (idle)**: ~5-10% (wake word mode)
- **CPU (hotkey only)**: <1%
- **Memory**: ~150MB
- **Microphone**: Required for wake word
- **Windows 10/11**: Recommended

## 🐛 Troubleshooting

### Wake word not working
- Check microphone permissions
- Test with: `python src/services/wake_word_service.py`
- Try speaking louder/clearer
- Reduce background noise

### Hotkey not working
- Make sure `keyboard` library is installed: `pip install keyboard`
- May need admin rights on some systems
- Try different key combination

### System tray icon missing
- Check if `pystray` and `pillow` are installed
- Fallback to console mode if needed

### High CPU usage
- Use hotkey-only mode: `--no-wake-word`
- Reduce listening frequency
- Close other programs

## 📁 File Structure

```
backend/
├── src/
│   ├── background/
│   │   ├── jarvis_daemon.py        # Background service
│   │   ├── system_tray.py          # System tray app
│   │   └── __init__.py
│   ├── services/
│   │   └── wake_word_service.py    # Wake word detection
│   └── system/
│       └── file_ops.py             # Enhanced file operations
├── start_jarvis_background.bat     # Easy launcher
└── BACKGROUND_SERVICE_GUIDE.md     # This file
```

## 🎯 Example Session

1. **Start**: Double-click `start_jarvis_background.bat`
2. **Choose**: Option 1 (System Tray)
3. **Icon appears** in system tray
4. **Say**: "Hi Jarvis"
5. **JARVIS**: "Yes sir, I'm here"
6. **You**: "Take a note: finish the project report"
7. **JARVIS**: "Note saved successfully"
8. **You**: "Goodbye"
9. **JARVIS** returns to listening mode

## ⚡ Performance Tips

1. **Use hotkey only** if you don't need voice activation
2. **System tray mode** is most efficient
3. **Disable wake word** if battery is low
4. **Close unused programs** for better performance

## 🔮 Future Enhancements

Potential upgrades:
- [ ] Better wake word engine (Porcupine)
- [ ] GUI configuration panel
- [ ] Custom hotkey selection
- [ ] Voice profiles
- [ ] Remote activation

## ❓ FAQ

**Q: Can I use both wake word and hotkey?**  
A: Yes! Both work simultaneously.

**Q: How do I stop JARVIS?**  
A: Right-click tray icon → Quit, or close console window

**Q: Does it work when PC is locked?**  
A: No, Windows blocks microphone when locked

**Q: Can I change the hotkey?**  
A: Yes, edit `jarvis_daemon.py` line with `keyboard.add_hotkey()`

**Q: What if I don't have a microphone?**  
A: Use hotkey-only mode with `--no-wake-word`

## 📝 Notes Location

All voice notes are saved to:
```
C:\Users\HP\Documents\JARVIS_Notes\
```

Format: `note_YYYY-MM-DD_HH-MM-SS.txt`

## 🎉 You're All Set!

JARVIS is now ready to assist you in the background. Just say "Hi Jarvis" or press CTRL+ALT+J!
