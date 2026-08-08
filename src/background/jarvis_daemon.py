"""
JARVIS Background Daemon
Runs continuously in background with:
- System tray icon
- Hotkey activation (CTRL+ALT+J)
- Wake word detection ("Hi Jarvis")
"""
import sys
import os
import time
import threading
from colorama import Fore, Style, init

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.wake_word_service import WakeWordDetector

init(autoreset=True)


class JARVISDaemon:
    """Main background service for JARVIS"""
    
    def __init__(self, use_wake_word=True, use_hotkey=True):
        self.running = False
        self.session_active = False
        self.use_wake_word = use_wake_word
        self.use_hotkey = use_hotkey
        
        # Initialize wake word detector
        if self.use_wake_word:
            self.wake_detector = WakeWordDetector()
        else:
            self.wake_detector = None
        
        # Hotkey thread
        self.hotkey_thread = None
        
        print(f"{Fore.GREEN}✓ JARVIS Daemon initialized{Style.RESET_ALL}")
        print(f"  Wake word: {'ENABLED' if use_wake_word else 'DISABLED'}")
        print(f"  Hotkey: {'ENABLED (CTRL+ALT+J)' if use_hotkey else 'DISABLED'}")
    
    def start_hotkey_listener(self):
        """Start listening for hotkey in background thread"""
        try:
            import keyboard
            
            def on_hotkey():
                if not self.session_active:
                    print(f"\n{Fore.GREEN}✓ HOTKEY PRESSED (CTRL+ALT+J){Style.RESET_ALL}")
                    self.activate_jarvis_session()
            
            # Register hotkey
            keyboard.add_hotkey('ctrl+alt+j', on_hotkey)
            print(f"{Fore.GREEN}✓ Hotkey registered: CTRL+ALT+J{Style.RESET_ALL}")
            
            # Keep thread alive
            while self.running:
                time.sleep(0.1)
                
        except ImportError:
            print(f"{Fore.YELLOW}⚠ 'keyboard' library not installed - hotkey disabled{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  Install with: pip install keyboard{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Hotkey error: {e}{Style.RESET_ALL}")
    
    def activate_jarvis_session(self):
        """Activate full JARVIS session"""
        if self.session_active:
            return
        
        self.session_active = True
        
        try:
            # Import and run JARVIS
            from src.main import JARVIS
            
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}  JARVIS SESSION ACTIVATED")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
            
            # Create and run JARVIS instance
            jarvis = JARVIS()
            jarvis.run()
            
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}  JARVIS SESSION ENDED - Back to listening mode")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
            
        except Exception as e:
            print(f"{Fore.RED}Session error: {e}{Style.RESET_ALL}")
        finally:
            self.session_active = False
    
    def run(self):
        """Main daemon loop"""
        self.running = True
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}  JARVIS BACKGROUND SERVICE STARTED")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Start hotkey listener in background thread if enabled
        if self.use_hotkey:
            self.hotkey_thread = threading.Thread(target=self.start_hotkey_listener, daemon=True)
            self.hotkey_thread.start()
        
        # Main loop: wake word detection
        if self.use_wake_word and self.wake_detector:
            print(f"{Fore.YELLOW}Listening for wake word...{Style.RESET_ALL}")
            
            while self.running:
                try:
                    # Listen for wake word (non-blocking with timeout)
                    if self.wake_detector.listen_for_wake_word(timeout=3):
                        if not self.session_active:
                            self.activate_jarvis_session()
                    
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
                    break
                    
                except Exception as e:
                    print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                    time.sleep(1)
        else:
            # No wake word - just wait for hotkey
            print(f"{Fore.YELLOW}Waiting for hotkey (CTRL+ALT+J)...{Style.RESET_ALL}")
            
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Shutting down...{Style.RESET_ALL}")
        
        self.stop()
    
    def stop(self):
        """Stop the daemon"""
        self.running = False
        
        if self.wake_detector:
            self.wake_detector.stop()
        
        print(f"{Fore.CYAN}JARVIS Background Service stopped{Style.RESET_ALL}")


def main():
    """Entry point for background service"""
    import argparse
    
    parser = argparse.ArgumentParser(description='JARVIS Background Service')
    parser.add_argument('--no-wake-word', action='store_true', help='Disable wake word detection')
    parser.add_argument('--no-hotkey', action='store_true', help='Disable hotkey')
    args = parser.parse_args()
    
    # Create and run daemon
    daemon = JARVISDaemon(
        use_wake_word=not args.no_wake_word,
        use_hotkey=not args.no_hotkey
    )
    
    try:
        daemon.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
