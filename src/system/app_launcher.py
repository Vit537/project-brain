"""
App Launch Module
Opens applications on Windows
"""
import subprocess
import os
from colorama import Fore, Style, init

init(autoreset=True)


class AppLauncher:
    # Common app mappings
    APPS = {
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'paint': 'mspaint.exe',
        'word': 'winword.exe',
        'excel': 'excel.exe',
        'chrome': 'chrome.exe',
        'edge': 'msedge.exe',
        'firefox': 'firefox.exe',
        'vscode': 'code.exe',
        'vs code': 'code.exe',
        'visual studio': 'devenv.exe',
        'cmd': 'cmd.exe',
        'powershell': 'powershell.exe',
        'explorer': 'explorer.exe',
        'file explorer': 'explorer.exe',
    }
    
    def __init__(self):
        print(f"{Fore.GREEN}✓ App launcher ready{Style.RESET_ALL}")
    
    def launch_app(self, app_name):
        """
        Launch an application
        
        Args:
            app_name (str): Application name
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            app_lower = app_name.lower().strip()
            
            # Check if in known apps
            if app_lower in self.APPS:
                executable = self.APPS[app_lower]
                subprocess.Popen(executable)
                print(f"{Fore.GREEN}✓ Launched: {app_name}{Style.RESET_ALL}")
                return True, f"Opening {app_name}"
            
            # Try direct executable name
            try:
                subprocess.Popen(app_lower)
                print(f"{Fore.GREEN}✓ Launched: {app_name}{Style.RESET_ALL}")
                return True, f"Opening {app_name}"
            except:
                return False, f"I don't know how to launch '{app_name}'. Try: notepad, calculator, chrome, edge, vscode, explorer"
                
        except Exception as e:
            return False, f"Error launching app: {str(e)}"
