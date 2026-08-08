"""
JARVIS Background Service Launcher
Easy launcher with multiple modes
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from colorama import Fore, Style, init
init(autoreset=True)


def main():
    """Launch JARVIS in background mode"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}  🤖 JARVIS Background Service Launcher")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    print("Choose launch mode:\n")
    print(f"{Fore.GREEN}1.{Style.RESET_ALL} System Tray Mode (⭐ Recommended)")
    print("   → Icon in taskbar")
    print("   → CTRL+ALT+J to activate")
    print("   → Wake word: 'Hi Jarvis'")
    print()
    print(f"{Fore.GREEN}2.{Style.RESET_ALL} Console Mode (Full features)")
    print("   → Visible console window")
    print("   → Wake word + Hotkey")
    print("   → Best for debugging")
    print()
    print(f"{Fore.GREEN}3.{Style.RESET_ALL} Hotkey Only (Silent)")
    print("   → No wake word detection")
    print("   → Just CTRL+ALT+J")
    print("   → Minimal resource usage")
    print()
    print(f"{Fore.GREEN}4.{Style.RESET_ALL} Text Mode (No voice)")
    print("   → Keyboard input only")
    print("   → For testing without mic")
    print()
    print(f"{Fore.YELLOW}0.{Style.RESET_ALL} Exit")
    
    choice = input(f"\n{Fore.CYAN}Enter choice (0-4): {Style.RESET_ALL}")
    
    if choice == "1":
        print(f"\n{Fore.GREEN}🚀 Launching System Tray Mode...{Style.RESET_ALL}")
        from src.background.system_tray_modular import main
        main()
    
    elif choice == "2":
        print(f"\n{Fore.GREEN}🚀 Launching Console Mode...{Style.RESET_ALL}")
        from src.background.jarvis_background_modular import main
        main()
    
    elif choice == "3":
        print(f"\n{Fore.GREEN}🚀 Launching Hotkey Mode...{Style.RESET_ALL}")
        from src.background.jarvis_background_modular import JARVISBackgroundModular
        service = JARVISBackgroundModular(
            use_voice=True,
            use_wake_word=False,
            use_hotkey=True
        )
        service.run()
    
    elif choice == "4":
        print(f"\n{Fore.GREEN}🚀 Launching Text Mode...{Style.RESET_ALL}")
        from src.background.jarvis_background_modular import JARVISBackgroundModular
        service = JARVISBackgroundModular(
            use_voice=False,
            use_wake_word=False,
            use_hotkey=True
        )
        service.run()
    
    elif choice == "0":
        print(f"{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    
    else:
        print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Launcher interrupted{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
