"""
JARVIS System Tray - Modular Architecture
Shows icon in Windows system tray
"""
import sys
import os
import threading
from colorama import Fore, Style

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print(f"{Fore.YELLOW}⚠ System tray not available{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  Install with: pip install pystray pillow{Style.RESET_ALL}")


def create_icon_image():
    """Create JARVIS icon for system tray"""
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), 'black')
    dc = ImageDraw.Draw(image)
    
    # Blue circle
    dc.ellipse([8, 8, 56, 56], fill='#00BFFF', outline='white', width=2)
    
    # "J" text
    dc.text((22, 16), "J", fill='white', font=None)
    
    return image


class JARVISTrayModular:
    """System tray application with modular architecture"""
    
    def __init__(self):
        self.icon = None
        self.service = None
        self.service_thread = None
        
        if not TRAY_AVAILABLE:
            print(f"{Fore.RED}System tray unavailable - fallback to console{Style.RESET_ALL}")
    
    def start_service(self, icon=None, item=None):
        """Start JARVIS service from tray"""
        if self.service and self.service.session_active:
            print(f"{Fore.YELLOW}JARVIS is already active{Style.RESET_ALL}")
            return
        
        print(f"{Fore.GREEN}Activating JARVIS...{Style.RESET_ALL}")
        
        if self.service:
            # Trigger activation
            self.service._activate_session()
    
    def show_status(self, icon=None, item=None):
        """Display status in console"""
        if self.service:
            status = "🟢 Active" if self.service.session_active else "🟡 Listening"
            modules = len(self.service.module_manager.registry)
            loaded = len([m for m in self.service.module_manager.loaded_modules.values() if m])
            
            print(f"\n{Fore.CYAN}{'='*50}")
            print(f"{Fore.CYAN}  JARVIS STATUS")
            print(f"{Fore.CYAN}{'='*50}")
            print(f"{Fore.CYAN}Status: {status}")
            print(f"{Fore.CYAN}Modules: {loaded}/{modules} loaded")
            print(f"{Fore.CYAN}Wake word: {'✓' if self.service.use_wake_word else '✗'}")
            print(f"{Fore.CYAN}Hotkey: {'✓ (CTRL+ALT+J)' if self.service.use_hotkey else '✗'}")
            print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.YELLOW}Service not initialized{Style.RESET_ALL}")
    
    def quit_app(self, icon=None, item=None):
        """Quit application"""
        print(f"{Fore.CYAN}Shutting down JARVIS...{Style.RESET_ALL}")
        
        if self.service:
            self.service.stop()
        
        if self.icon:
            self.icon.stop()
    
    def run(self):
        """Run system tray application"""
        if not TRAY_AVAILABLE:
            # Fallback: run service without tray
            from src.background.jarvis_background_modular import JARVISBackgroundModular
            service = JARVISBackgroundModular()
            service.run()
            return
        
        # Create tray menu
        menu = pystray.Menu(
            pystray.MenuItem("🤖 Activate JARVIS", self.start_service, default=True),
            pystray.MenuItem("📊 Show Status", self.show_status),
            pystray.MenuItem("❌ Quit", self.quit_app)
        )
        
        # Create icon
        image = create_icon_image()
        self.icon = pystray.Icon("JARVIS", image, "JARVIS Assistant", menu)
        
        print(f"{Fore.GREEN}✓ System Tray started{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Right-click tray icon for menu{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Use CTRL+ALT+J to activate JARVIS{Style.RESET_ALL}")
        
        # Start background service
        def run_service():
            from src.background.jarvis_background_modular import JARVISBackgroundModular
            self.service = JARVISBackgroundModular(
                use_voice=True,
                use_wake_word=True,
                use_hotkey=True
            )
            self.service.run()
        
        self.service_thread = threading.Thread(target=run_service, daemon=True)
        self.service_thread.start()
        
        # Run tray (blocking)
        self.icon.run()


def main():
    """Entry point"""
    app = JARVISTrayModular()
    app.run()


if __name__ == "__main__":
    main()
