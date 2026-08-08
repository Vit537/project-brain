"""
JARVIS Background Service - Modular Architecture
Integrates wake word detection + hotkey with modular system
"""
import sys
import os
import time
import threading
import asyncio
from colorama import Fore, Style, init

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.module_manager import ModuleManager
from src.core.intent_router import IntentRouter
from src.core.shared_resources import SharedResources

# Import speech services
try:
    from src.speech.listener_sounddevice import VoiceListener
    VOICE_AVAILABLE = True
except Exception:
    VOICE_AVAILABLE = False

from src.speech.speaker import VoiceSpeaker

# Import wake word service
try:
    from src.services.wake_word_service import WakeWordDetector
    WAKE_WORD_AVAILABLE = True
except Exception:
    WAKE_WORD_AVAILABLE = False

init(autoreset=True)


class JARVISBackgroundModular:
    """
    Background service using modular architecture
    Supports: Wake word, Hotkey, Voice/Text input
    """
    
    def __init__(self, use_voice=True, use_wake_word=True, use_hotkey=True):
        """
        Initialize background service
        
        Args:
            use_voice: Enable voice input/output
            use_wake_word: Listen for "Hi Jarvis"
            use_hotkey: Listen for CTRL+ALT+J
        """
        self.running = False
        self.session_active = False
        self.use_voice = use_voice and VOICE_AVAILABLE
        self.use_wake_word = use_wake_word and WAKE_WORD_AVAILABLE
        self.use_hotkey = use_hotkey
        
        # Initialize modular system
        print(f"{Fore.CYAN}Initializing modular architecture...{Style.RESET_ALL}")
        self.resources = SharedResources()
        self.module_manager = ModuleManager(self.resources)
        self.router = IntentRouter()
        
        # Register all modules
        self._register_modules()
        
        # Initialize voice components
        if self.use_voice:
            self.listener = VoiceListener()
            self.speaker = VoiceSpeaker()
            print(f"{Fore.GREEN}✓ Voice mode enabled{Style.RESET_ALL}")
        else:
            self.listener = None
            self.speaker = VoiceSpeaker()
            print(f"{Fore.YELLOW}⚠ Voice input disabled - text mode only{Style.RESET_ALL}")
        
        # Initialize wake word detector
        if self.use_wake_word:
            self.wake_detector = WakeWordDetector()
            print(f"{Fore.GREEN}✓ Wake word enabled: 'Hi Jarvis'{Style.RESET_ALL}")
        else:
            self.wake_detector = None
        
        # Hotkey thread
        self.hotkey_thread = None
        
        print(f"{Fore.GREEN}✓ JARVIS Background Service initialized{Style.RESET_ALL}")
        print(f"  Modules available: {len(self.module_manager.registry)}")
        print(f"  Wake word: {'ENABLED' if self.use_wake_word else 'DISABLED'}")
        print(f"  Hotkey: {'ENABLED (CTRL+ALT+J)' if self.use_hotkey else 'DISABLED'}")
    
    def _register_modules(self):
        """Register all available modules"""
        from src.modules.file_ops_module import FileOpsModule
        from src.modules.word_module import WordModule
        from src.modules.pdf_module import PDFModule
        
        self.module_manager.register('file_ops', FileOpsModule)
        self.module_manager.register('word', WordModule)
        self.module_manager.register('pdf', PDFModule)
        
        print(f"{Fore.GREEN}✓ 3 modules registered{Style.RESET_ALL}")
    
    def start_hotkey_listener(self):
        """Listen for CTRL+ALT+J in background"""
        try:
            import keyboard
            
            def on_hotkey():
                if not self.session_active:
                    print(f"\n{Fore.GREEN}🔥 HOTKEY PRESSED (CTRL+ALT+J){Style.RESET_ALL}")
                    self._activate_session()
            
            keyboard.add_hotkey('ctrl+alt+j', on_hotkey)
            print(f"{Fore.GREEN}✓ Hotkey registered: CTRL+ALT+J{Style.RESET_ALL}")
            
            # Keep thread alive
            while self.running:
                time.sleep(0.1)
                
        except ImportError:
            print(f"{Fore.YELLOW}⚠ 'keyboard' library missing - run: pip install keyboard{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Hotkey error: {e}{Style.RESET_ALL}")
    
    def _activate_session(self):
        """Start an interactive JARVIS session"""
        if self.session_active:
            return
        
        self.session_active = True
        
        try:
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}  🤖 JARVIS ACTIVATED")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
            
            # Welcome message
            if self.speaker:
                self.speaker.speak("Yes sir, how can I help you?", 'en')
            
            # Session loop
            asyncio.run(self._session_loop())
            
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}  💤 Session ended - Back to listening")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
            
        except Exception as e:
            print(f"{Fore.RED}Session error: {e}{Style.RESET_ALL}")
        finally:
            self.session_active = False
    
    async def _session_loop(self):
        """Interactive session with user"""
        conversation_count = 0
        max_conversations = 5  # Limit per session
        
        while conversation_count < max_conversations:
            try:
                # Get user input
                if self.use_voice and self.listener:
                    print(f"{Fore.YELLOW}🎤 Listening...{Style.RESET_ALL}")
                    
                    user_input = self.listener.listen()
                    
                    if not user_input or user_input.lower() in ['exit', 'goodbye', 'adiós', 'stop']:
                        if self.speaker:
                            self.speaker.speak("Goodbye sir", 'en')
                        break
                else:
                    # Text input mode
                    user_input = input(f"{Fore.YELLOW}You: {Style.RESET_ALL}")
                    
                    if not user_input or user_input.lower() in ['exit', 'quit', 'adiós']:
                        print(f"{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
                        break
                
                print(f"{Fore.GREEN}You: {user_input}{Style.RESET_ALL}")
                
                # Process with modular system
                response = await self._process_command(user_input)
                
                # Output response
                print(f"{Fore.CYAN}JARVIS: {response}{Style.RESET_ALL}")
                
                if self.speaker:
                    self.speaker.speak(response, 'en')
                
                conversation_count += 1
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Session interrupted{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                break
        
        if conversation_count >= max_conversations:
            print(f"{Fore.YELLOW}Max conversations reached for this session{Style.RESET_ALL}")
    
    async def _process_command(self, user_input: str) -> str:
        """
        Process user command through modular system
        
        Args:
            user_input: User's command
            
        Returns:
            Response string
        """
        try:
            # Classify intent (returns dict with type, text, language, confidence)
            intent = await self.router.classify(user_input, language='en')
            
            print(f"{Fore.CYAN}💡 Intent: {intent['type']}{Style.RESET_ALL}")
            
            # Execute through module manager (pass the full intent dict)
            response = await self.module_manager.execute_intent(intent)
            
            return response
            
        except Exception as e:
            print(f"{Fore.RED}Processing error: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return f"I encountered an error: {str(e)}"
    
    def run(self):
        """Main daemon loop"""
        self.running = True
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}  🚀 JARVIS BACKGROUND SERVICE STARTED")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Start hotkey listener in background thread
        if self.use_hotkey:
            self.hotkey_thread = threading.Thread(
                target=self.start_hotkey_listener, 
                daemon=True
            )
            self.hotkey_thread.start()
        
        # Main loop: wake word detection
        if self.use_wake_word and self.wake_detector:
            print(f"{Fore.YELLOW}👂 Listening for wake word: 'Hi Jarvis'{Style.RESET_ALL}")
            
            while self.running:
                try:
                    # Listen for wake word
                    if self.wake_detector.listen_for_wake_word(timeout=3):
                        if not self.session_active:
                            print(f"\n{Fore.GREEN}🎯 WAKE WORD DETECTED!{Style.RESET_ALL}")
                            self._activate_session()
                    
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
                    break
                except Exception as e:
                    print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                    time.sleep(1)
        else:
            # No wake word - just wait for hotkey
            print(f"{Fore.YELLOW}⌨️ Waiting for hotkey (CTRL+ALT+J){Style.RESET_ALL}")
            print(f"{Fore.CYAN}Press Ctrl+C to exit{Style.RESET_ALL}")
            
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
        
        self.stop()
    
    def stop(self):
        """Stop the service"""
        self.running = False
        
        if self.wake_detector:
            self.wake_detector.stop()
        
        print(f"{Fore.CYAN}✓ JARVIS Background Service stopped{Style.RESET_ALL}")


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='JARVIS Background Service (Modular)')
    parser.add_argument('--no-voice', action='store_true', help='Disable voice input')
    parser.add_argument('--no-wake-word', action='store_true', help='Disable wake word')
    parser.add_argument('--no-hotkey', action='store_true', help='Disable hotkey')
    args = parser.parse_args()
    
    # Create and run service
    service = JARVISBackgroundModular(
        use_voice=not args.no_voice,
        use_wake_word=not args.no_wake_word,
        use_hotkey=not args.no_hotkey
    )
    
    try:
        service.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
