"""
Quick Test: Wake Word Detection
Test if wake word detection is working
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colorama import Fore, Style

def test_wake_word():
    """Test wake word detection"""
    print("="*60)
    print("TESTING WAKE WORD DETECTION")
    print("="*60 + "\n")
    
    try:
        from src.services.wake_word_service import WakeWordDetector
        
        detector = WakeWordDetector()
        
        print(f"{Fore.CYAN}Say one of the following:{Style.RESET_ALL}")
        print("  - Hi Jarvis")
        print("  - Hey Jarvis")
        print("  - Hello Jarvis")
        print("\nPress CTRL+C to stop\n")
        
        def on_wake():
            print(f"{Fore.GREEN}✓ WAKE WORD DETECTED! System is working!{Style.RESET_ALL}")
            return True
        
        # Test for 30 seconds
        import time
        start_time = time.time()
        detected = False
        
        while time.time() - start_time < 30 and not detected:
            if detector.listen_for_wake_word(timeout=3):
                detected = True
                on_wake()
                break
        
        if not detected:
            print(f"\n{Fore.YELLOW}No wake word detected in 30 seconds.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Try speaking louder or closer to microphone.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}✅ WAKE WORD TEST PASSED!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Your system is ready for background mode.{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test stopped by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure microphone is working{Style.RESET_ALL}")


if __name__ == "__main__":
    test_wake_word()
