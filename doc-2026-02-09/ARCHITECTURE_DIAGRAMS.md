# 🏗️ JARVIS Architecture - Visual Diagrams

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   JARVIS CORE (Single Process)              │
│                     Python Background Service               │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┴─────────────────────┐
        │                                           │
    ┌───▼──────────────┐             ┌──────────────▼────┐
    │  VOICE ENGINE    │             │  MODULE ROUTER    │
    │                  │             │                   │
    │ • Wake word      │◄────────────┤ • Routes commands │
    │ • Listening      │             │ • Manages tasks   │
    │ • Hotkey (CTRL+  │             │ • Coordinates    │
    │   ALT+J)         │             │   modules         │
    └──────────────────┘             └───────────────────┘
                                            ↓
                ┌───────────────────────────┼───────────────────────────┐
                │                           │                           │
         ┌──────▼──────┐  ┌────────▼─────┐ ┌──────────▼──────┐  ┌──────▼──────┐
         │NOTIFICATION │  │  WHATSAPP    │ │  CLASSROOM     │  │  PROJECT    │
         │  MODULE     │  │  MODULE      │ │  MODULE        │  │  MANAGER    │
         └─────────────┘  └──────────────┘ └────────────────┘  └─────────────┘
                │                │                 │                  │
         ┌──────▼──────┐  ┌────────▼─────┐ ┌──────────▼──────┐  ┌──────▼──────┐
         │VS CODE      │  │  DOCUMENT    │ │  CONTEXT      │  │  DAILY      │
         │BRIDGE       │  │  MANAGER     │ │  ENGINE       │  │  PLANNER    │
         └─────────────┘  └──────────────┘ └────────────────┘  └─────────────┘
                                                  │
                ┌─────────────────────────────────┼─────────────────────────────┐
                │                                 │                             │
         ┌──────▼──────┐              ┌──────────▼──────┐            ┌─────────▼─────┐
         │  AI CLIENT  │              │  MEMORY SYSTEM  │            │  DATABASE     │
         │  (Groq)     │              │  (ChromaDB)     │            │  (SQLite)     │
         └─────────────┘              └─────────────────┘            └───────────────┘
```

---

## 2. Data Flow: Command Processing

```
User speaks: "Jarvis, take a note about my assignment"
                        │
                        ▼
        ┌───────────────────────────────┐
        │  VOICE ENGINE                 │
        │  • Listens continuously       │
        │  • Detects wake word          │
        │  • Records audio              │
        │  • Converts to text           │
        └──────────────┬────────────────┘
                       │ (Text: "take a note about...")
                       ▼
        ┌───────────────────────────────┐
        │  COMMAND ROUTER               │
        │  • Identifies command type    │
        │  • Routes to correct module   │
        │  • Manages execution          │
        └──────────────┬────────────────┘
                       │ (Route to: CONTEXT ENGINE)
                       ▼
        ┌───────────────────────────────┐
        │  CONTEXT ENGINE MODULE        │
        │  • Understands assignment     │
        │  • Calls AI for context       │
        │  • Stores in memory           │
        └──────────────┬────────────────┘
                       │ (Execute: take_note)
                       ▼
        ┌───────────────────────────────┐
        │  FILE OPERATIONS              │
        │  • Create note file           │
        │  • Timestamp                  │
        │  • Save to Documents folder   │
        └──────────────┬────────────────┘
                       │ (Response)
                       ▼
        ┌───────────────────────────────┐
        │  VOICE OUTPUT                 │
        │  "Note saved successfully"    │
        └───────────────────────────────┘
```

---

## 3. Module Interaction Pattern

```
┌─────────────────────────────────────────────────────────┐
│                  JARVIS CORE LOOP                       │
│  while True:                                            │
│      if voice_detected():                              │
│          command = speech_to_text()                    │
│          module = identify_module(command)             │
│          result = module.execute(command)              │
│          speak(result)                                 │
│      else:                                              │
│          # Background tasks (async, non-blocking)      │
│          check_notifications()                         │
│          check_whatsapp()                              │
│          process_learning()                            │
│          check_deadlines()                             │
└─────────────────────────────────────────────────────────┘
           │                                    │
           │ (Blocking)                         │ (Async)
           ▼                                    ▼
    Voice commands                    Background tasks
    run immediately                   run in parallel
```

---

## 4. Resource Architecture

```
SYSTEM MEMORY: 2-4 GB (typical student PC)
JARVIS ALLOCATION: 250-350 MB

┌────────────────────────────────┐
│    JARVIS MEMORY USAGE         │
├────────────────────────────────┤
│ Core JARVIS        │███ │ ~80MB  │
│ Voice Buffers      │ ██ │ ~30MB  │
│ ChromaDB           │████ │ ~60MB  │
│ SQLite DB          │ █  │ ~20MB  │
│ Modules (shared)   │ ██ │ ~40MB  │
│ AI Models (local)  │ █  │ ~20MB  │
│ Free Buffer        │ █  │ ~20MB  │
├────────────────────────────────┤
│ TOTAL              │────│~270MB  │
└────────────────────────────────┘
```

---

## 5. CPU Usage Timeline

```
CPU Usage (%) over time during typical day:

     25% ┤
        ├─────────────────────────────────────────
     20% ├─   ___________
        │  /             \      ____     ____
     15% ├_/               \____/    \___/    \___
        │
     10% ├────────────────────────────────────────
        │   ___ (Idle with modules)
      5% ├__/                                    \__
        │
      0% └────────────────────────────────────────
        06:00   09:00   12:00   15:00   18:00   21:00

Legend:
  5-10%:  Idle (voice listening + background tasks)
 10-15%:  Normal operation (features active)
 15-20%:  Recording lecture (heavy audio processing)
 20-25%:  Peak (multiple features active)
```

---

## 6. Module Communication

```
Scenario: User in classroom, gets a WhatsApp message

┌──────────────────────────────────┐
│ Classroom Module: RECORDING      │
│ (High quality, high CPU)         │
└─────────────┬──────────────────┘
              │
              │ "Still in classroom"
              ▼
    ┌─────────────────────┐
    │ Context Engine      │
    │ (Detects: IN CLASS) │
    └─────────┬───────────┘
              │ "Suppress notifications"
              ▼
    ┌─────────────────────┐
    │ WhatsApp Module     │
    │ (QUEUE MESSAGE)     │
    │ (Silent, low CPU)   │
    └────────┬────────────┘
             │ "After class"
             ▼
    ┌─────────────────────┐
    │ After class ends    │
    │ (Context Engine)    │
    └─────────┬───────────┘
              │ "Now announce messages"
              ▼
    ┌─────────────────────┐
    │ WhatsApp Module     │
    │ VOICE ALERT:        │
    │ "You have message   │
    │  from Sarah"        │
    └─────────────────────┘
```

---

## 7. Daily Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   TYPICAL DAY                           │
└─────────────────────────────────────────────────────────┘

06:00 AM
┌─────────────────────────────────────────────────────────┐
│ PC boots → JARVIS auto-starts                          │
│ Loads modules from config                              │
│ JARVIS: "Good morning! You have 3 deadlines this week" │
└─────────────────────────────────────────────────────────┘

08:30 AM
┌─────────────────────────────────────────────────────────┐
│ User in class                                          │
│ Classroom Module: START RECORDING                      │
│ Notification Module: SILENT MODE                       │
│ WhatsApp Module: QUEUE MESSAGES                        │
└─────────────────────────────────────────────────────────┘

10:00 AM
┌─────────────────────────────────────────────────────────┐
│ Class ends                                             │
│ Classroom Module: PROCESSING                           │
│  - Transcribing lecture                                │
│  - Creating summary                                    │
│ Context Engine: ANALYZE LEARNING PATTERNS             │
└─────────────────────────────────────────────────────────┘

10:30 AM
┌─────────────────────────────────────────────────────────┐
│ JARVIS: "Physics lecture done. 3 messages while away." │
│ "Most important: Sarah asked for lab notes"            │
│ Do you want me to reply?                              │
└─────────────────────────────────────────────────────────┘

12:00 PM
┌─────────────────────────────────────────────────────────┐
│ User: "Jarvis, show my schedule"                       │
│ Project Manager Module: DISPLAYS TODAY'S TASKS         │
│  - WebApp: 4 hours work (due Friday)                   │
│  - Study: 2 hours (Math test Wednesday)               │
│  - Documentation: 1 hour                              │
└─────────────────────────────────────────────────────────┘

13:00 - 17:00 (Afternoon)
┌─────────────────────────────────────────────────────────┐
│ User coding in VS Code                                │
│ VS Code Module: ACTIVE                                │
│ Notification Module: IMPORTANT ONLY                    │
│ User: "Jarvis, explain this function"                │
│ JARVIS: [Analyzes code, explains]                     │
└─────────────────────────────────────────────────────────┘

17:00
┌─────────────────────────────────────────────────────────┐
│ User: "Jarvis, daily summary"                         │
│ JARVIS: "You completed 3 tasks today.                 │
│          WebApp is on schedule.                        │
│          Tomorrow: Study for Math test.               │
│          3 messages waiting from classmates"           │
└─────────────────────────────────────────────────────────┘

20:00
┌─────────────────────────────────────────────────────────┐
│ User: "Jarvis, sleep mode"                            │
│ All modules: LOW POWER MODE                            │
│ Notification Module: CRITICAL ONLY                     │
│ Memory usage: ~150MB                                  │
│ CPU: <2%                                             │
└─────────────────────────────────────────────────────────┘
```

---

## 8. Architecture Evolution Path

```
NOW (Semester 1)         FUTURE (Semester 2+)      POTENTIAL (Commercial)

┌──────────────────┐    ┌──────────────────┐      ┌────────────────────┐
│ Modular Monolith │    │ Modular Monolith │      │ Distributed System │
│ (Single PC)      │    │ (Single PC)      │      │ (Multiple PCs)     │
│                  │    │                  │      │                    │
│ 1 Process        │───→│ 1 Process        │─────→│ Service Grid       │
│ Python Only      │    │ Python + Node    │      │ Microservices      │
│ SQLite           │    │ SQLite + Network │      │ PostgreSQL         │
│ Local Only       │    │ Shared Database  │      │ Message Queue      │
│                  │    │ Multi-user       │      │ Load Balancing     │
└──────────────────┘    └──────────────────┘      └────────────────────┘
   Development              Production            Enterprise Scale
   Phase                    Ready Phase           Phase
```

---

## 9. Feature Integration

```
Voice Command Processing Pipeline:

Input: "Jarvis, create Word document for project report"
                         │
         ┌───────────────┴───────────────┐
         │                               │
    Voice Recognition              AI Understanding
    ("word", "document"...)    (Intent: create_document,
                                Type: Word,
                                Subject: project_report)
         │                               │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼──────────────────┐
         │ Module Router                    │
         │ Identify: Document Manager       │
         └───────────────┬──────────────────┘
                         │
         ┌───────────────▼──────────────────┐
         │ Document Manager Module          │
         │ • Check template available       │
         │ • Create from template           │
         │ • Set metadata                   │
         │ • Return file path               │
         └───────────────┬──────────────────┘
                         │
         ┌───────────────▼──────────────────┐
         │ Context Engine                   │
         │ • Learn user preference          │
         │ • Store in vector memory         │
         └───────────────┬──────────────────┘
                         │
         ┌───────────────▼──────────────────┐
         │ Voice Output                     │
         │ "Document created at            │
         │  Documents\project_report.docx" │
         └────────────────────────────────┘
```

---

## 10. Scalability Path

```
CURRENT (3-4 months):
Single Student PC
└─ 1 JARVIS Instance
   └─ 1 User
   └─ 1 Database

FUTURE (Semester 2):
Single Database, Multiple PCs
└─ JARVIS Instance 1 (Student 1)
└─ JARVIS Instance 2 (Student 2)
└─ JARVIS Instance N (Student N)
   └─ Shared Database (with user isolation)

FUTURE+ (Commercial):
Distributed Architecture
├─ AI Service (Centralized)
├─ Database Service (Centralized)
├─ JARVIS Core (Client instances)
│  ├─ User 1
│  ├─ User 2
│  └─ User N
└─ Admin Dashboard
```

---

## Summary

**This architecture ensures:**
- ✅ Lightweight background operation (single process)
- ✅ All features accessible (modular design)
- ✅ Voice not blocked (async tasks)
- ✅ Easy to add features (plugin system)
- ✅ Scales to production (database-backed)
- ✅ Professional code quality (clean architecture)

---

**Ready to implement this architecture!** 🚀
