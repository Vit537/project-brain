"""
Wake Word Detector - Listens for "Hi Jarvis" trigger
Uses current speech recognition library (free, offline capable)
"""
import sys
import os
from colorama import Fore, Style

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.speech.listener_sounddevice import VoiceListener
    VOICE_AVAILABLE = True
except Exception:
    VOICE_AVAILABLE = False


class WakeWordDetector:
    """Detects wake words like 'Hi Jarvis' or 'Hey Jarvis'"""
    
    def __init__(self):
        self.wake_words = [
            "hi jarvis",
            "hey jarvis", 
            "jarvis",
            "hello jarvis",
            "ok jarvis"
        ]
        self.is_listening = False
        
        if VOICE_AVAILABLE:
            self.listener = VoiceListener()
        else:
            self.listener = None
    
    def listen_for_wake_word(self, timeout=5):
        """
        Listen continuously for wake word in low-power mode
        
        Args:
            timeout (int): Seconds to wait for voice input
            
        Returns:
            bool: True if wake word detected, False otherwise
        """
        if not self.listener:
            return False
        
        try:
            # Listen with short timeout for efficiency
            text, language = self.listener.listen(timeout=timeout)
            
            if text:
                text_lower = text.lower().strip()
                
                # Check if any wake word is in the text
                for wake_word in self.wake_words:
                    if wake_word in text_lower:
                        print(f"\n{Fore.GREEN}✓ WAKE WORD DETECTED: '{text}'{Style.RESET_ALL}")
                        return True
            
            return False
            
        except Exception as e:
            # Timeout or error - just return False and continue
            return False
    
    def continuous_listen(self, on_wake_callback=None):
        """
        Continuously listen for wake word (blocking loop)
        
        Args:
            on_wake_callback: Function to call when wake word detected
        """
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}  JARVIS Background Listening Active")
        print(f"{Fore.CYAN}  Say: 'Hi Jarvis' or 'Hey Jarvis' to activate")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        self.is_listening = True
        
        while self.is_listening:
            try:
                if self.listen_for_wake_word(timeout=3):
                    # Wake word detected
                    if on_wake_callback:
                        on_wake_callback()
                    return True
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Stopping wake word detection...{Style.RESET_ALL}")
                self.is_listening = False
                break
                
            except Exception as e:
                # Continue listening on error
                continue
        
        return False
    
    def stop(self):
        """Stop listening"""
        self.is_listening = False


# Test function
def test_wake_word():
    """Test wake word detection"""
    print("Testing Wake Word Detection")
    print("Say 'Hi Jarvis' or 'Hey Jarvis'...\n")
    
    detector = WakeWordDetector()
    
    def on_wake():
        print(f"{Fore.GREEN}WAKE WORD CONFIRMED!{Style.RESET_ALL}")
    
    detector.continuous_listen(on_wake_callback=on_wake)


if __name__ == "__main__":
    test_wake_word()
