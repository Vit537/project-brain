"""
Confirmation Module
Handles user confirmations for destructive operations
"""
import time
from colorama import Fore, Style, init

init(autoreset=True)


class ConfirmationHandler:
    """Manages confirmations for risky operations"""
    
    @staticmethod
    def ask_confirmation(action, target, language='en'):
        """
        Ask user to confirm an action
        
        Args:
            action (str): Action type (delete, move, etc)
            target (str): Item being acted upon
            language (str): Language ('en' or 'es')
            
        Returns:
            bool: True if confirmed, False if cancelled
        """
        if language == 'es':
            messages = {
                'delete': f"¿Estás seguro de que quieres eliminar '{target}'? (di 'si' o 'no')",
                'move': f"¿Quieres mover '{target}'? (di 'si' o 'no')",
            }
            wait_msg = "Esperando confirmación..."
        else:
            messages = {
                'delete': f"Are you sure you want to delete '{target}'? (say 'yes' or 'no')",
                'move': f"Do you want to move '{target}'? (say 'yes' or 'no')",
            }
            wait_msg = "Waiting for confirmation..."
        
        msg = messages.get(action, f"Confirm this action for '{target}'?")
        
        print(f"{Fore.YELLOW}{msg}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{wait_msg}{Style.RESET_ALL}")
        
        # For now: always return True for voice (too complex to parse yes/no in real-time)
        # In future: add voice yes/no parsing
        return True
