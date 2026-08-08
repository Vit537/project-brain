"""
JARVIS - Voice-Activated AI Assistant
Main entry point for Sprint 1 MVP
"""
import os
import sys
import time
from colorama import Fore, Style, init

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import voice listener (Python 3.13 compatible version)
try:
    from src.speech.listener_sounddevice import VoiceListener
    VOICE_MODE = True
except Exception as e:
    print(f"Voice mode unavailable: {e}")
    VOICE_MODE = False
    
from src.speech.speaker import VoiceSpeaker
from src.ai.brain import AIBrain
from src.ai.response_generator import ResponseGenerator
from src.ai.embeddings import EmbeddingClient
from src.ai.memory import MemoryManager
from src.db.chroma_store import ChromaVectorStore
from src.system.file_ops import FileOperations
from src.system.app_launcher import AppLauncher
from src.system.confirmation import ConfirmationHandler
from src.services.query_router import QueryRouter
from src.services.time_service import TimeService
from src.services.system_service import SystemService
from src.services.calculator import Calculator


class JARVIS:
    def __init__(self):
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}    JARVIS - Voice Assistant Initializing...")
        print(f"{Fore.CYAN}{'='*50}\n")
        
        # Initialize all modules
        if VOICE_MODE:
            self.listener = VoiceListener()
            self.voice_enabled = True
        else:
            self.listener = None
            self.voice_enabled = False
            print(f"{Fore.YELLOW}⚠ Voice input disabled - using text mode{Style.RESET_ALL}")
            
        self.speaker = VoiceSpeaker()
        self.brain = AIBrain()
        self.embedder = EmbeddingClient()
        self.chroma_store = ChromaVectorStore()
        self.memory = MemoryManager(self.embedder, self.chroma_store)
        self.file_ops = FileOperations()
        self.app_launcher = AppLauncher()
        self.response_gen = ResponseGenerator()
        self.query_router = QueryRouter()
        self.time_service = TimeService()
        self.system_service = SystemService()
        self.calculator = Calculator()
        
        print(f"\n{Fore.GREEN}✓ All systems online!{Style.RESET_ALL}\n")
        mode_msg = "in English and Spanish with voice input" if self.voice_enabled else "in text mode only"
        self.speaker.speak(f"Hello sir, JARVIS is online and ready to assist {mode_msg}", 'en')
    
    def handle_query(self, user_input, language='en'):
        """
        Main query handler - routes to appropriate service
        
        Args:
            user_input (str): User's input
            language (str): Language
            
        Returns:
            str: Response to speak
        """
        # Identify query type
        query_type = self.query_router.identify_query_type(user_input, language)
        
        print(f"{Fore.CYAN}Query type: {query_type}{Style.RESET_ALL}")
        
        # Route to appropriate handler
        if query_type == 'time':
            response, _ = self.time_service.get_current_time(language)
            return response
        
        elif query_type == 'date':
            response, _ = self.time_service.get_current_date(language)
            return response
        
        elif query_type == 'system':
            response, _ = self.system_service.get_system_summary(language)
            return response
        
        elif query_type == 'calculator':
            # Extract numbers and operators from input
            import re
            numbers = re.findall(r'\d+\.?\d*', user_input)
            if numbers:
                success, result = self.calculator.calculate(user_input)
                if success:
                    return self.calculator.format_result(user_input, result, language)
                return result
            if language == 'es':
                return "No entiendo la operación matemática"
            return "I don't understand the math"
        
        elif query_type == 'note':
            # Handle note taking
            return self._handle_note_taking(user_input, language)
        
        elif query_type in ['file', 'app']:
            # Use AI brain to parse
            command = self.brain.understand_command(user_input, language)
            return self.execute_command(command, language)
        
        else:
            # General conversation - use Groq for natural responses
            return self._handle_conversation(user_input, language)
    
    def _handle_conversation(self, user_input, language='en'):
        """Handle general conversation queries using Groq"""
        try:
            print(f"{Fore.YELLOW}🧠 Thinking...{Style.RESET_ALL}")

            start_time = time.time()
            context_blocks = []
            embedding = None

            if self.memory and self.memory.enabled:
                rows, embedding = self.memory.get_context(user_input, k=5)
                for row in rows:
                    snippet = (
                        f"User: {row['user_input']}\n"
                        f"Assistant: {row['ai_response']}"
                    )
                    context_blocks.append(snippet)

            system_prompt = """You are JARVIS, a helpful AI assistant on a Windows computer.
Answer questions briefly and naturally. Keep responses to 1-2 sentences.
Stay helpful and friendly."""

            if language == 'es':
                system_prompt = """Eres JARVIS, un asistente de IA útil en una computadora Windows.
Responde preguntas de manera breve y natural. Mantén respuestas de 1-2 oraciones.
Sé útil y amigable."""

            messages = [{"role": "system", "content": system_prompt}]

            if context_blocks:
                context_text = "\n\n".join(context_blocks)
                messages.append(
                    {
                        "role": "system",
                        "content": f"Relevant past exchanges:\n{context_text}",
                    }
                )

            messages.append({"role": "user", "content": user_input})

            response = self.brain.client.chat.completions.create(
                model=self.brain.model,
                messages=messages,
                temperature=0.7,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            latency_ms = int((time.time() - start_time) * 1000)
            print(f"{Fore.GREEN}Response: {result}{Style.RESET_ALL}")

            if self.memory and self.memory.enabled:
                self.memory.store_interaction(
                    user_input=user_input,
                    ai_response=result,
                    embedding=embedding,
                    intent="conversation",
                    action_taken=None,
                    success=True,
                    latency_ms=latency_ms,
                    language=language,
                )

            return result
            
        except Exception as e:
            print(f"{Fore.RED}Conversation error: {e}{Style.RESET_ALL}")
            if language == 'es':
                return "Disculpa, tuve un problema"
            return "Sorry, I had an issue"
    
    def _handle_note_taking(self, user_input, language='en'):
        """Handle voice note taking"""
        try:
            # Extract note content
            # Remove trigger words to get actual note
            trigger_words = ['take a note', 'take note', 'write down', 'note', 'remember', 
                           'anota', 'apunta', 'recuerda', 'nota']
            
            note_content = user_input.lower()
            for trigger in trigger_words:
                note_content = note_content.replace(trigger, '')
            
            note_content = note_content.strip().strip(':').strip()
            
            if not note_content:
                return "What would you like me to note?" if language == 'en' else "¿Qué quieres que anote?"
            
            # Check if there's a title
            title = None
            if 'titled' in note_content or 'llamada' in note_content or 'llamado' in note_content:
                parts = note_content.split('titled' if 'titled' in note_content else 'llamada' if 'llamada' in note_content else 'llamado')
                if len(parts) > 1:
                    title = parts[1].strip()
                    note_content = parts[0].strip()
            
            # Save note
            success, message = self.file_ops.take_note(note_content, title)
            
            if success:
                return "Note saved successfully" if language == 'en' else "Nota guardada exitosamente"
            return message
            
        except Exception as e:
            print(f"{Fore.RED}Note error: {e}{Style.RESET_ALL}")
            return "Error saving note" if language == 'en' else "Error al guardar nota"
    
    def execute_command(self, command, language='en'):
        """
        Execute a parsed command with natural responses
        
        Args:
            command (dict): Parsed command from AI brain
            language (str): Language for response ('en' or 'es')
            
        Returns:
            str: Response message
        """
        action = command.get('action')
        target = command.get('target')
        location = command.get('location')
        source = command.get('source')
        destination = command.get('destination')
        
        # Determine if action needs confirmation
        needs_confirmation = action in ['delete_folder', 'delete_file', 'move']
        
        if needs_confirmation:
            ConfirmationHandler.ask_confirmation(action, target, language)
        
        if action == 'create_folder':
            if not target or not location:
                return self.response_gen.get_error_response('needs_info', language)
            
            success, message = self.file_ops.create_folder(target, location)
            if success:
                return self.response_gen.get_success_response('create_folder', language)
            return message
        
        elif action == 'delete_folder':
            if not target or not location:
                return self.response_gen.get_error_response('needs_info', language)
            
            success, message = self.file_ops.delete_folder(target, location)
            if success:
                return self.response_gen.get_success_response('delete_folder', language)
            return message
        
        elif action == 'create_file':
            if not target or not location:
                return self.response_gen.get_error_response('needs_info', language)
            
            success, message = self.file_ops.create_file(target, location)
            if success:
                return self.response_gen.get_success_response('create_file', language)
            return message
        
        elif action == 'delete_file':
            if not target or not location:
                return self.response_gen.get_error_response('needs_info', language)
            
            success, message = self.file_ops.delete_file(target, location)
            if success:
                return self.response_gen.get_success_response('delete_file', language)
            return message

        elif action == 'move':
            if not target or not source or not destination:
                return self.response_gen.get_error_response('needs_info', language)

            success, message = self.file_ops.move_item(target, source, destination)
            if success:
                return self.response_gen.get_success_response('move', language)
            return message

        elif action == 'copy':
            if not target or not source or not destination:
                return self.response_gen.get_error_response('needs_info', language)

            success, message = self.file_ops.copy_item(target, source, destination)
            if success:
                return self.response_gen.get_success_response('copy', language)
            return message

        elif action == 'search':
            if not target or not location:
                return self.response_gen.get_error_response('needs_info', language)

            success, message = self.file_ops.search_item(target, location)
            if success:
                return f"{self.response_gen.get_success_response('search', language)}: {message}"
            return message
        
        elif action == 'write':
            # Write to file (create if doesn't exist)
            if not target or not location:
                return self.response_gen.get_error_response('needs_info', language)
            
            content = command.get('content', '')
            append = command.get('append', False)
            
            # Convert quick location names
            location = self.file_ops.get_quick_location(location)
            
            success, message = self.file_ops.write_to_file(target, location, content, append)
            if success:
                action_word = "appended" if append else "written"
                return f"Content {action_word} to {target}" if language == 'en' else f"Contenido escrito en {target}"
            return message
        
        elif action == 'read':
            # Read file content
            if not target or not location:
                return self.response_gen.get_error_response('needs_info', language)
            
            # Convert quick location names
            location = self.file_ops.get_quick_location(location)
            
            success, content = self.file_ops.read_file(target, location)
            if success:
                # Return first 200 characters
                preview = content[:200] + "..." if len(content) > 200 else content
                return f"File content: {preview}" if language == 'en' else f"Contenido del archivo: {preview}"
            return content
        
        elif action == 'list_notes':
            success, message = self.file_ops.list_notes()
            return message
        
        elif action == 'read_latest_note':
            success, message = self.file_ops.read_latest_note()
            return message
        
        elif action == 'open':
            if not target:
                return self.response_gen.get_error_response('needs_info', language)
            
            success, message = self.app_launcher.launch_app(target)
            if success:
                return self.response_gen.get_success_response('launch', language)
            return message
        
        else:
            return self.response_gen.get_error_response('unknown_command', language)
    
    def run(self):
        """
        Main loop - listen for commands and execute (bilingual)
        """
        if self.voice_enabled:
            print(f"{Fore.YELLOW}🎤 Speak your command in English or Spanish{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🎤 Habla en inglés o español{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}💬 Type your command in English or Spanish{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💬 Escribe en inglés o español{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Say/Type 'exit'/'quit' or 'salir'/'terminar' to stop{Style.RESET_ALL}\n")
        
        while True:
            try:
                # Get input (voice or text)
                if self.voice_enabled:
                    text, language = self.listener.listen()
                else:
                    print(f"{Fore.CYAN}💬 You: {Style.RESET_ALL}", end='')
                    text = input().strip().lower()
                    if not text:
                        continue
                    # Simple language detection
                    spanish_words = ['crear', 'eliminar', 'carpeta', 'archivo', 'en', 'del', 'llamada', 'llamado']
                    language = 'es' if any(word in text for word in spanish_words) else 'en'
                
                if text is None:
                    continue
                
                # Check for exit commands (English + Spanish)
                exit_words = ['exit', 'quit', 'goodbye', 'stop', 'salir', 'terminar', 'adiós', 'chao']
                if any(word in text for word in exit_words):
                    goodbye_msg = "Adiós señor, apagándome" if language == 'es' else "Goodbye sir, shutting down"
                    self.speaker.speak(goodbye_msg, language)
                    print(f"\n{Fore.CYAN}JARVIS shutting down...{Style.RESET_ALL}\n")
                    break
                
                # Handle any query type (not just file commands)
                response = self.handle_query(text, language)
                
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
        jarvis = JARVIS()
        jarvis.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
