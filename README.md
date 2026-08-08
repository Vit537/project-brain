# JARVIS Voice Assistant 🤖

A voice-activated AI assistant powered by Groq AI that runs in the background and responds to wake words or hotkeys!

## 🎯 Current Features

### ✅ Background Service
- **Wake Word Detection**: "Hi Jarvis", "Hey Jarvis", "Hello Jarvis"
- **Hotkey Activation**: Press CTRL+ALT+J anywhere
- **System Tray Icon**: Right-click for menu
- **Auto-Start**: Boot with Windows

### ✅ Voice & AI
- Voice recognition (speech to text)
- Text-to-speech responses (English & Spanish)
- AI-powered command understanding (Groq)
- Vector memory with Chroma (remembers conversations)

### ✅ File Operations
- **Create files** with content
- **Write to files** (create or append)
- **Read files** aloud
- **Create/delete folders**
- **Move/copy files**
- **Search files**
- **Voice notes** (auto-saved to Documents/JARVIS_Notes)
- Quick locations: desktop, documents, downloads, notes

### ✅ System Operations
- Get time/date
- System status (CPU, RAM, disk, battery)
- Calculator
- Launch applications
- Confirmation for destructive operations

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Configure API Key

Your Groq API key is already configured in `.env` file.

### 3. Run JARVIS

**Option A: Background Service (Recommended)**
```powershell
# Easy menu launcher
start_jarvis_background.bat

# Or directly:
python src/background/system_tray.py
```

**Option B: Normal Mode**
```powershell
python src/main.py
```

## 🎤 Voice Commands Examples

### File Operations
- "Jarvis, create a file called todo.txt on desktop"
- "Jarvis, write 'buy milk' to shopping.txt on desktop"
- "Jarvis, read notes.txt from documents"
- "Jarvis, create folder Projects on desktop"
- "Jarvis, search for Python files in documents"

### Voice Notes
- "Jarvis, take a note: meeting tomorrow at 3pm"
- "Jarvis, note titled Shopping: eggs, milk, bread"
- "Jarvis, list my notes"
- "Jarvis, read my latest note"

### System Commands
- "Jarvis, what time is it?"
- "Jarvis, system status"
- "Jarvis, open Chrome"
- "Jarvis, calculate 25 times 4"

### Exit
- "Jarvis, goodbye" or "Jarvis, exit"

## 🔧 Auto-Start Setup

Run the setup script to start JARVIS automatically on Windows boot:

```powershell
setup_autostart.bat
```

Choose from:
1. **Task Scheduler** (recommended - most reliable)
2. **Startup Folder** (quick - simple shortcut)
3. **Manual instructions**

See [BACKGROUND_SERVICE_GUIDE.md](BACKGROUND_SERVICE_GUIDE.md) for detailed instructions.

## 📁 Project Structure

```
backend/
├── src/
│   ├── main.py                      # Main JARVIS application
│   ├── background/
│   │   ├── jarvis_daemon.py         # Background service
│   │   ├── system_tray.py           # System tray app
│   │   └── __init__.py
│   ├── ai/                          # AI & memory modules
│   │   ├── brain.py
│   │   ├── memory.py
│   │   ├── embeddings.py
│   │   └── response_generator.py
│   ├── speech/                      # Voice I/O
│   │   ├── listener_sounddevice.py
│   │   └── speaker.py
│   ├── services/                    # Core services
│   │   ├── wake_word_service.py
│   │   ├── query_router.py
│   │   ├── time_service.py
│   │   └── system_service.py
│   └── system/                      # System operations
│       ├── file_ops.py              # Enhanced file ops
│       ├── app_launcher.py
│       └── confirmation.py
├── config/                          # Configuration files
│   └── task_scheduler_jarvis.xml
├── test_*.py                        # Test files
├── start_jarvis_background.bat      # Easy launcher
├── setup_autostart.bat              # Auto-start setup
├── requirements.txt
├── README.md                        # This file
└── BACKGROUND_SERVICE_GUIDE.md      # Detailed guide
```

## 🧪 Testing

Test individual components:

```powershell
# Test enhanced file operations
python test_file_ops_enhanced.py

# Test wake word detection
python test_wake_word.py

# Test memory system
python test_memory_quick.py
```

## Usage

1. Start JARVIS: `python src/main.py`
2. Wait for "Listening..." prompt
3. Speak your command clearly, for example:
   - "Hey JARVIS, create a folder called TestProject on Desktop"
   - "Create a folder named MyFiles in Documents"
   - "Delete the folder TestProject from Desktop"
4. Say "exit" or "quit" to stop

## Example Commands

```
"Create a folder called Projects in Documents"
"Make a new folder named TestFolder on Desktop"
"Delete the folder TestProject from Desktop"
"Create a file called notes.txt in Documents"
"Move the folder Reports from Downloads to Documents"
"Copy notes.txt from Desktop to Documents"
"Search for Projects in Documents"
```

## Project Structure

```
backend/
├── src/
│   ├── speech/         # Voice I/O
│   │   ├── listener.py # Speech recognition
│   │   └── speaker.py  # Text-to-speech
│   ├── ai/
│   │   └── brain.py    # Groq AI integration
│   ├── system/
│   │   └── file_ops.py # File operations
│   └── main.py         # Main program
├── .env                # API configuration
└── requirements.txt    # Dependencies
```

## ⚙️ Configuration

- **Wake word**: Edit wake words in [wake_word_service.py](src/services/wake_word_service.py)
- **Hotkey**: Change hotkey in [jarvis_daemon.py](src/background/jarvis_daemon.py)
- **Groq API**: Set in `.env` file
- **Voice engine**: Configure in [speaker.py](src/speech/speaker.py)

## 🐛 Troubleshooting

### Microphone not working
- Check Windows microphone permissions
- Test with: `python test_wake_word.py`
- Verify device in Windows Sound settings

### Wake word not detecting
- Speak louder and clearer
- Reduce background noise
- Try different wake words
- Check microphone is not muted

### Hotkey not working
- May need administrator rights
- Check if `keyboard` library is installed
- Try different key combination

### High CPU usage
- Use hotkey-only mode: `--no-wake-word`
- Close other applications
- Reduce listening frequency

### System tray icon missing
- Install dependencies: `pip install pystray pillow`
- Use console mode as fallback

## 📊 Performance

- **CPU (idle, wake word)**: ~5-10%
- **CPU (hotkey only)**: <1%
- **Memory**: ~150MB
- **Wake word latency**: <500ms
- **Response time**: 1-2 seconds

## 🔮 Roadmap

- [x] Phase 1: Enhanced file operations
- [x] Phase 2: Background service
- [x] Phase 3: Wake word detection
- [x] Phase 4: System tray
- [x] Phase 5: Auto-start
- [ ] Phase 6: Better wake word engine (Porcupine)
- [ ] Phase 7: GUI configuration panel
- [ ] Phase 8: Custom commands/macros

## 📝 Notes

All voice notes are automatically saved to:
```
C:\Users\HP\Documents\JARVIS_Notes\
```

Format: `note_YYYY-MM-DD_HH-MM-SS.txt`

## 🤝 Contributing

Feel free to enhance JARVIS! Some ideas:
- Add more file operations
- Improve wake word accuracy
- Add new services (weather, email, etc.)
- Create custom voice profiles
- Add more languages

## 📄 License

Personal project - feel free to use and modify!

## 🎉 Enjoy!

You now have a fully functional background JARVIS assistant!

For detailed usage and setup, see [BACKGROUND_SERVICE_GUIDE.md](BACKGROUND_SERVICE_GUIDE.md)

---

**Made with ❤️ inspired by Iron Man's JARVIS**

- Check Windows microphone permissions
- Ensure microphone is set as default device

**PyAudio installation fails:**
- Use: `pip install pipwin` then `pipwin install pyaudio`
- Or download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

**AI not understanding commands:**
- Speak clearly and include folder/file name and location
- Check Groq API key in .env file

## Next Sprints

- Sprint 2: Move, copy, search files
- Sprint 3: Enhanced AI understanding
- Sprint 4: Open apps, web search, UI
