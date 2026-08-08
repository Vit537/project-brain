"""
JARVIS - Text-Based AI Assistant (Python 3.13 Compatible)
Uses text input instead of voice due to PyAudio compatibility issues
"""
import os
import sys
from colorama import Fore, Style, init

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.speech.speaker import VoiceSpeaker
from src.ai.brain import AIBrain
from src.system.file_ops import FileOperations

init(autoreset=True)


class JARVIS_Text:
    def __init__(self):
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}    JARVIS - Text Assistant Initializing...")
        print(f"{Fore.CYAN}{'='*50}\n")
        
        # Initialize all modules
        self.speaker = VoiceSpeaker()
        self.brain = AIBrain()
        self.file_ops = FileOperations()
        
        print(f"\n{Fore.GREEN}✓ All systems online!{Style.RESET_ALL}\n")
        self.speaker.speak("Hello sir, JARVIS is online and ready to assist in English and Spanish", 'en')
    
    def execute_command(self, command, language='en'):
        """
        Execute a parsed command
        
        Args:
            command (dict): Parsed command from AI brain
            language (str): Language for response ('en' or 'es')
            
        Returns:
            str: Response message
        """
        action = command.get('action')
        target = command.get('target')
        location = command.get('location')
        
        # Error messages
        need_info_en = "I need both a folder name and location to proceed"
        need_info_es = "Necesito el nombre y la ubicación para continuar"
        unknown_en = "I'm not sure how to handle that command yet. I can create or delete folders and files."
        unknown_es = "No estoy seguro de cómo manejar ese comando todavía. Puedo crear o eliminar carpetas y archivos."
        
        if action == 'create_folder':
            if not target or not location:
                return need_info_es if language == 'es' else need_info_en
            
            success, message = self.file_ops.create_folder(target, location)
            return message
        
        elif action == 'delete_folder':
            if not target or not location:
                return need_info_es if language == 'es' else need_info_en
            
            success, message = self.file_ops.delete_folder(target, location)
            return message
        
        elif action == 'create_file':
            if not target or not location:
                return need_info_es if language == 'es' else need_info_en
            
            success, message = self.file_ops.create_file(target, location)
            return message
        
        elif action == 'delete_file':
            if not target or not location:
                return need_info_es if language == 'es' else need_info_en
            
            success, message = self.file_ops.delete_file(target, location)
            return message
        
        else:
            return unknown_es if language == 'es' else unknown_en
    
    def run(self):
        """
        Main loop - text input for commands
        """
        print(f"{Fore.YELLOW}Type your command in English or Spanish{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Escribe tu comando en inglés o español{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'exit'/'quit' or 'salir'/'terminar' to stop{Style.RESET_ALL}\n")
        
        while True:
            try:
                # Get text input
                print(f"{Fore.CYAN}💬 You: {Style.RESET_ALL}", end='')
                text = input().strip().lower()
                
                if not text:
                    continue
                
                # Check for exit commands (English + Spanish)
                exit_words = ['exit', 'quit', 'goodbye', 'stop', 'salir', 'terminar', 'adiós', 'chao']
                if any(word in text for word in exit_words):
                    # Detect language for goodbye
                    language = 'es' if any(word in text for word in ['salir', 'terminar', 'adiós', 'chao']) else 'en'
                    goodbye_msg = "Adiós señor, apagándome" if language == 'es' else "Goodbye sir, shutting down"
                    self.speaker.speak(goodbye_msg, language)
                    print(f"\n{Fore.CYAN}JARVIS shutting down...{Style.RESET_ALL}\n")
                    break
                
                # Detect language (simple heuristic)
                spanish_words = ['crear', 'eliminar', 'carpeta', 'archivo', 'en', 'del', 'llamada', 'llamado']
                language = 'es' if any(word in text for word in spanish_words) else 'en'
                
                # Process command with AI
                command = self.brain.understand_command(text, language)
                
                # Execute the command
                response = self.execute_command(command, language)
                
                # Respond with voice in same language
                self.speaker.speak(response, language)
                
                print()  # Blank line for readability
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}JARVIS shutting down...{Style.RESET_ALL}\n")
                self.speaker.speak("Goodbye sir", 'en')
                break
            
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                self.speaker.speak("I encountered an error sir", 'en')


def main():
    """Entry point"""
    try:
        jarvis = JARVIS_Text()
        jarvis.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
