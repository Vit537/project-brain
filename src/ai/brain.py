"""
AI Brain Module - Groq Integration
Understands natural language commands and extracts actions
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv
from colorama import Fore, Style, init

init(autoreset=True)
load_dotenv()


class AIBrain:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Updated model (Jan 2026)
        
        print(f"{Fore.GREEN}✓ AI Brain connected (Groq){Style.RESET_ALL}")
    
    def understand_command(self, user_input, language='en'):
        """
        Parse natural language command into structured action (bilingual)
        
        Args:
            user_input (str): User's voice command
            language (str): 'en' or 'es'
            
        Returns:
            dict: Parsed command with action, target, location
        """
        if language == 'es':
            system_prompt = """Eres JARVIS, un asistente de IA que entiende comandos del sistema de archivos y del sistema.
Analiza el comando del usuario y devuelve SOLO un objeto JSON con estos campos:
- action: uno de [create_folder, delete_folder, create_file, delete_file, move, copy, search, open, unknown]
- target: el nombre del archivo/carpeta/aplicación
- location: la ruta donde crear/eliminar/buscar (usa rutas completas de Windows como C:\\Users\\HP\\Documents)
- source: ruta de origen para mover/copiar (ej: C:\\Users\\HP\\Desktop)
- destination: ruta de destino para mover/copiar (ej: C:\\Users\\HP\\Documents)
- content: contenido de texto opcional cuando el usuario pide escribir dentro de un archivo/documento

Ejemplos:
Usuario: "crear una carpeta llamada Proyectos en Documentos"
{"action": "create_folder", "target": "Proyectos", "location": "C:\\\\Users\\\\HP\\\\Documents", "source": null, "destination": null}

Usuario: "mueve la carpeta Reportes desde Descargas a Documentos"
{"action": "move", "target": "Reportes", "location": null, "source": "C:\\\\Users\\\\HP\\\\Downloads", "destination": "C:\\\\Users\\\\HP\\\\Documents"}

Usuario: "abre el navegador"
{"action": "open", "target": "chrome", "location": null, "source": null, "destination": null}

Usuario: "abre vscode"
{"action": "open", "target": "vscode", "location": null, "source": null, "destination": null}

Usuario: "busca la carpeta proyectos en Documentos"
{"action": "search", "target": "proyectos", "location": "C:\\\\Users\\\\HP\\\\Documents", "source": null, "destination": null}

Devuelve SOLO el objeto JSON, sin otro texto."""
        else:
            system_prompt = """You are JARVIS, an AI assistant that understands file system and application commands.
Parse the user's command and return ONLY a JSON object with these fields:
- action: one of [create_folder, delete_folder, create_file, delete_file, move, copy, search, open, unknown]
- target: the name of the file/folder/application
- location: the path where to create/delete/search (use full Windows paths like C:\\Users\\HP\\Documents)
- source: source path for move/copy (e.g., C:\\Users\\HP\\Desktop)
- destination: destination path for move/copy (e.g., C:\\Users\\HP\\Documents)
- content: optional text content when user asks to write inside a file/document

Examples:
User: "create a folder called Projects in Documents"
{"action": "create_folder", "target": "Projects", "location": "C:\\\\Users\\\\HP\\\\Documents", "source": null, "destination": null}

User: "move the folder Reports from Downloads to Documents"
{"action": "move", "target": "Reports", "location": null, "source": "C:\\\\Users\\\\HP\\\\Downloads", "destination": "C:\\\\Users\\\\HP\\\\Documents"}

User: "open chrome"
{"action": "open", "target": "chrome", "location": null, "source": null, "destination": null}

User: "launch vscode"
{"action": "open", "target": "vscode", "location": null, "source": null, "destination": null}

User: "search for projects in Documents"
{"action": "search", "target": "projects", "location": "C:\\\\Users\\\\HP\\\\Documents", "source": null, "destination": null}

Return ONLY the JSON object, no other text."""

        try:
            print(f"{Fore.YELLOW}🧠 Thinking...{Style.RESET_ALL}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            command = json.loads(result)
            
            print(f"{Fore.GREEN}Understood: {command}{Style.RESET_ALL}")
            return command
            
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse AI response: {e}{Style.RESET_ALL}")
            return {
                "action": "unknown",
                "target": None,
                "location": None,
                "source": None,
                "destination": None,
                "content": ""
            }
            
        except Exception as e:
            print(f"{Fore.RED}AI error: {e}{Style.RESET_ALL}")
            return {
                "action": "unknown",
                "target": None,
                "location": None,
                "source": None,
                "destination": None,
                "content": ""
            }
