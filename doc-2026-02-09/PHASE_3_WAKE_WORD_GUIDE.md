# JARVIS Background Service & Wake Word Implementation Guide

**Objective:** Make JARVIS run in background, listen for "Hi Jarvis" wake word, and respond to commands automatically without manual execution.

---

## **PHASE 3: Wake Word Detection + Background Service**

### **Current Status:**
- ✅ Voice recognition works
- ✅ Memory system (Chroma) active
- ✅ Groq AI integration working
- ❌ No wake word detection yet
- ❌ Manual execution only (you must run `python src/main.py`)

### **Goal:**
```
Boot PC → JARVIS starts automatically → Listens silently in background
         → You say "Hi Jarvis" → JARVIS wakes up and responds
         → Responds to all commands without stopping
         → Stores everything in memory
```

---

## **ARCHITECTURE: How It Will Work**

```
┌─────────────────────────────────────────────────────────────┐
│              WINDOWS SYSTEM BOOT                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Service Manager (Windows Task Scheduler or NSSM)           │
│  Starts: jarvis_background_service.py                       │
│  Status: Always Running                                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Wake Word Detector (Running in LOW-CPU mode)               │
│  Library: Picovoice Porcupine (recommended)                 │
│  Listens for: "Hi Jarvis" or "Hey Jarvis"                   │
│  CPU Usage: ~5%                                              │
│  Memory: ~30 MB                                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
           [Continuous Silent Listening]
                           ↓
      [User says "Hi Jarvis"] ← WAKE WORD DETECTED
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Main JARVIS Session Activated                              │
│  ├─ Start listening for commands                            │
│  ├─ Load memory (Chroma)                                    │
│  ├─ Process voice input                                     │
│  ├─ Query vector memory for context                         │
│  ├─ Call Groq LLM for response                              │
│  └─ Store new conversation in Chroma                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
      [User says "Goodbye"] or [Timeout after 2 min]
                           ↓
         [Return to Silent Wake Word Listening]
```

---

## **IMPLEMENTATION STEPS**

### **Step 1: Choose Wake Word Detection Method**

#### **Option A: Picovoice Porcupine (RECOMMENDED)**
- ✅ Very accurate
- ✅ Custom wake words possible
- ✅ Low CPU usage
- ✅ Works offline
- ❌ Free tier: 30-day trial
- ❌ Paid after: ~$99/year or $9.99/month

**Install:**
```bash
pip install pvporcupine
```

#### **Option B: Local Open Source (FREE)**
- ✅ Completely free
- ✅ No API keys needed
- ✅ Works offline
- ❌ Less accurate
- ❌ Higher CPU usage (~20%)

**Libraries:**
- Snowboy (works, but archived)
- Mycroft Precise (older but free)
- Vosk (requires downloading model)

#### **Recommendation for You:**
Since you don't want to pay more → Use **local open source option** for now, upgrade to Porcupine later if needed.

---

### **Step 2: Architecture Files to Create**

```
src/
├── services/
│   └── wake_word_service.py        ← NEW: Wake word listener
├── background/
│   ├── __init__.py                 ← NEW
│   ├── jarvis_daemon.py            ← NEW: Background service
│   └── system_service.py           ← NEW: Windows service manager
└── main.py                         ← MODIFY: Add background mode
```

---

## **IMPLEMENTATION ROADMAP**

### **Phase 3.1: Local Wake Word Detection (FREE)**

**File: `src/services/wake_word_service.py`**

```python
"""
Wake Word Detector - Listens for "Hi Jarvis" trigger
Uses local offline model (free, no API keys needed)
"""

import numpy as np
from src.speech.listener_sounddevice import VoiceListener

class WakeWordDetector:
    def __init__(self):
        self.listener = VoiceListener()
        self.wake_words = ["hi jarvis", "hey jarvis", "jarvis"]
        self.is_listening = False
    
    def listen_for_wake_word(self):
        """
        Listen continuously for wake word
        Low CPU mode - only processes audio periodically
        """
        print("🎤 JARVIS in background listening mode...")
        print("Say: 'Hi Jarvis' to activate\n")
        
        while True:
            try:
                # Listen (timeout=5 seconds, then return to listening)
                text, language = self.listener.listen(timeout=5)
                
                if text:
                    text_lower = text.lower().strip()
                    
                    # Check if wake word detected
                    for wake_word in self.wake_words:
                        if wake_word in text_lower:
                            print(f"\n✓ WAKE WORD DETECTED: '{text}'")
                            return True  # Signal to activate main JARVIS
                    
                    # If not wake word, go back to listening
                    
            except Exception as e:
                # Timeout or error - continue listening
                continue
        
    def on_wake_word_detected(self):
        """Callback when wake word is detected"""
        from src.speech.speaker import VoiceSpeaker
        speaker = VoiceSpeaker()
        speaker.speak("Yes sir, I'm here", "en")
```

---

### **Phase 3.2: Background Service (Windows)**

**File: `src/background/jarvis_daemon.py`**

```python
"""
JARVIS Background Daemon
Runs continuously, listening for wake word
Spawns main JARVIS session on trigger
"""

import time
from src.services.wake_word_service import WakeWordDetector

class JARVISDaemon:
    def __init__(self):
        self.detector = WakeWordDetector()
        self.running = True
    
    def run(self):
        """Main daemon loop"""
        print("="*60)
        print("JARVIS Background Service Started")
        print("Will auto-start on next boot")
        print("="*60 + "\n")
        
        while self.running:
            try:
                # Listen for wake word (low CPU)
                if self.detector.listen_for_wake_word():
                    # Wake word detected - activate JARVIS
                    self.activate_jarvis_session()
                    
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
    
    def activate_jarvis_session(self):
        """Spawn main JARVIS session"""
        from src.main import JARVIS
        jarvis = JARVIS()
        jarvis.run()  # Run until user says "goodbye"
        # After session ends, return to listening

if __name__ == "__main__":
    daemon = JARVISDaemon()
    daemon.run()
```

---

### **Phase 3.3: Windows Auto-Start Configuration**

#### **Option 1: Task Scheduler (Built-in, No Extra Software)**

**Steps:**
1. Open Windows Task Scheduler
2. Create Basic Task:
   - Name: "JARVIS Background Service"
   - Trigger: "At startup"
   - Action: "Start program"
     - Program: `C:\Python313\python.exe`
     - Arguments: `C:\Users\HP\Desktop\app-2026-agent\backend\src\background\jarvis_daemon.py`
   - Condition: "Wake computer if asleep" ✓

**Configuration file: `tasks/jarvis_scheduler.xml`** (can be imported)

#### **Option 2: NSSM (Non-Sucking Service Manager)**

**Install:**
```bash
Download: https://nssm.cc/download
Extract: C:\nssm\
```

**Create service:**
```powershell
C:\nssm\win64\nssm.exe install JarvisService ^
  "C:\Python313\python.exe" ^
  "C:\Users\HP\Desktop\app-2026-agent\backend\src\background\jarvis_daemon.py"

# Start service
C:\nssm\win64\nssm.exe start JarvisService
```

**This will:**
- Run on boot automatically
- Restart if it crashes
- Run as system service (not visible window)

---

## **PHASE 3.4: Testing Sequence**

### **Step 1: Test Wake Word Detector**
```bash
python src/services/wake_word_service.py

# Say "Hi Jarvis" → Should detect and respond
```

### **Step 2: Test Daemon Mode**
```bash
python src/background/jarvis_daemon.py

# Waits silently... say "Hi Jarvis" → Activates JARVIS
# Use JARVIS normally
# Say "Goodbye" → Returns to listening
```

### **Step 3: Install as Windows Service**
```bash
# Use Task Scheduler or NSSM
# Reboot PC
# Should start automatically
```

---

## **PERFORMANCE TARGETS**

| Metric | Current | Target |
|--------|---------|--------|
| Wake word latency | N/A | < 500ms |
| CPU (idle listening) | N/A | < 5% |
| Memory (idle) | N/A | < 50 MB |
| Response time | 2-3s | 1-2s |
| Accuracy | N/A | > 95% |

---

## **FILES TO CREATE/MODIFY**

```
NEW FILES:
├── src/services/wake_word_service.py (100 lines)
├── src/background/jarvis_daemon.py (80 lines)
├── src/background/__init__.py (empty)
├── config/task_scheduler_config.xml (for auto-start)
└── config/nssm_config.bat (NSSM installation)

MODIFY:
├── src/main.py (add background mode flag)
└── requirements.txt (add wake word libraries)
```

---

## **NEXT STEPS (In Order)**

1. **Install local wake word library**
   ```bash
   pip install vosk  # FREE option
   # OR
   pip install pvporcupine  # PAID but better
   ```

2. **Create `wake_word_service.py`**
   - Test locally with microphone
   - Verify detection accuracy

3. **Create `jarvis_daemon.py`**
   - Test cycle: wake → JARVIS session → back to listening

4. **Set up Windows auto-start**
   - Use Task Scheduler (easier)
   - Or NSSM (more reliable)

5. **Reboot and test**
   - JARVIS should start automatically
   - Say "Hi Jarvis" to activate

---

## **ESTIMATED TIME**

- Phase 3.1 (Wake word): 1-2 hours
- Phase 3.2 (Daemon): 1 hour
- Phase 3.3 (Auto-start): 30 minutes
- Testing: 1 hour

**Total: ~4-5 hours for complete implementation**

---

## **COST**

- Option 1 (Local/Free): $0
- Option 2 (Porcupine): $9.99/month or $99/year

---

## **TROUBLESHOOTING**

| Problem | Solution |
|---------|----------|
| Not detecting "Hi Jarvis" | Lower detection threshold, add synonyms |
| High CPU usage | Switch to local model, increase timeout |
| Service crashes on reboot | Check Python path, add error logging |
| No audio input | Check microphone permissions, test with `sounddevice` |
| Memory leaks | Add session timeout, restart daemon hourly |

---

## **NEXT: Ready to implement?**

When ready, say "YES" and I'll create all the files and integrate them into your system!

Would you like me to:
1. **Implement everything now** (all 4-5 hours work)
2. **Start with just Phase 3.1** (wake word only)
3. **Explain any part in more detail first**

What's your choice?
