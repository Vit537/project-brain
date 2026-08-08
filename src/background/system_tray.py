"""
JARVIS System Tray Application
Shows icon in Windows system tray with menu options
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
    """Create a simple icon for system tray"""
    # Create a 64x64 image with a blue circle (representing JARVIS)
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), 'black')
    dc = ImageDraw.Draw(image)
    
    # Draw blue circle
    dc.ellipse([8, 8, 56, 56], fill='#00BFFF', outline='white', width=2)
    
    # Draw "J" in center
    dc.text((20, 18), "J", fill='white')
    
    return image


class JARVISTrayApp:
    """System tray application for JARVIS"""
    
    def __init__(self):
        self.icon = None
        self.daemon = None
        self.session_active = False
        
        if not TRAY_AVAILABLE:
            print(f"{Fore.RED}System tray unavailable - using console mode{Style.RESET_ALL}")
            return
    
    def activate_jarvis(self, icon=None, item=None):
        """Activate JARVIS session from tray menu"""
        if self.session_active:
            return
        
        self.session_active = True
        
        def run_session():
            try:
                from src.main import JARVIS
                jarvis = JARVIS()
                jarvis.run()
            except Exception as e:
                print(f"{Fore.RED}Session error: {e}{Style.RESET_ALL}")
            finally:
                self.session_active = False
        
        # Run in separate thread to not block tray
        thread = threading.Thread(target=run_session, daemon=True)
        thread.start()
    
    def quit_app(self, icon=None, item=None):
        """Quit application"""
        print(f"{Fore.CYAN}Shutting down JARVIS...{Style.RESET_ALL}")
        if self.icon:
            self.icon.stop()
    
    def show_status(self, icon=None, item=None):
        """Show status message"""
        status = "Active" if self.session_active else "Listening"
        print(f"{Fore.CYAN}JARVIS Status: {status}{Style.RESET_ALL}")
    
    def run(self):
        """Run the system tray application"""
        if not TRAY_AVAILABLE:
            # Fallback: run daemon without tray
            from src.background.jarvis_daemon import JARVISDaemon
            daemon = JARVISDaemon()
            daemon.run()
            return
        
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Activate JARVIS", self.activate_jarvis, default=True),
            pystray.MenuItem("Status", self.show_status),
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        # Create icon
        image = create_icon_image()
        self.icon = pystray.Icon("JARVIS", image, "JARVIS Assistant", menu)
        
        print(f"{Fore.GREEN}✓ JARVIS System Tray started{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Right-click the tray icon for options{Style.RESET_ALL}")
        
        # Start background daemon in separate thread
        def run_daemon():
            from src.background.jarvis_daemon import JARVISDaemon
            self.daemon = JARVISDaemon(use_wake_word=True, use_hotkey=True)
            self.daemon.run()
        
        daemon_thread = threading.Thread(target=run_daemon, daemon=True)
        daemon_thread.start()
        
        # Run tray icon (blocking)
        self.icon.run()


def main():
    """Entry point"""
    app = JARVISTrayApp()
    app.run()


if __name__ == "__main__":
    main()
