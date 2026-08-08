"""
Response Generator Module
Generates natural, fluent responses with personality and variation
"""
import random
from colorama import Fore, Style, init

init(autoreset=True)


class ResponseGenerator:
    """Generates natural conversational responses"""
    
    # Success responses
    SUCCESS_RESPONSES = {
        'en': {
            'create_folder': [
                "Folder created successfully, sir",
                "Done. I've created that folder for you",
                "The folder is ready to go",
                "Created successfully, sir",
            ],
            'delete_folder': [
                "Folder deleted, sir",
                "Done. I've removed that folder",
                "Folder is gone",
                "Deleted successfully",
            ],
            'create_file': [
                "File created, sir",
                "Your file is ready",
                "File has been created",
                "Done creating that file",
            ],
            'delete_file': [
                "File deleted, sir",
                "I've removed that file",
                "File is gone",
                "Deleted successfully",
            ],
            'move': [
                "Move complete, sir",
                "I've moved it for you",
                "Item relocated successfully",
                "Done moving that",
            ],
            'copy': [
                "Copy complete, sir",
                "I've copied that for you",
                "Copied successfully",
                "Done copying",
            ],
            'search': [
                "Here's what I found, sir",
                "I found these matches",
                "Search results ready",
                "These are the items I found",
            ],
            'launch': [
                "Opening now, sir",
                "I'm launching that for you",
                "Starting up",
                "On it, sir",
            ],
        },
        'es': {
            'create_folder': [
                "Carpeta creada exitosamente, señor",
                "Listo. He creado la carpeta",
                "La carpeta está lista",
                "Creado exitosamente",
            ],
            'delete_folder': [
                "Carpeta eliminada, señor",
                "Listo. He removido la carpeta",
                "La carpeta se ha ido",
                "Eliminado exitosamente",
            ],
            'create_file': [
                "Archivo creado, señor",
                "Tu archivo está listo",
                "El archivo ha sido creado",
                "Listo creando ese archivo",
            ],
            'delete_file': [
                "Archivo eliminado, señor",
                "He removido ese archivo",
                "El archivo se ha ido",
                "Eliminado exitosamente",
            ],
            'move': [
                "Movimiento completado, señor",
                "He movido esto por ti",
                "Elemento reubicado exitosamente",
                "Listo moviendo eso",
            ],
            'copy': [
                "Copia completada, señor",
                "He copiado eso por ti",
                "Copiado exitosamente",
                "Listo copiando",
            ],
            'search': [
                "Aquí está lo que encontré, señor",
                "Encontré estos resultados",
                "Resultados listos",
                "Estos son los elementos que encontré",
            ],
            'launch': [
                "Abriendo ahora, señor",
                "Estoy lanzando eso por ti",
                "Iniciando",
                "En ello, señor",
            ],
        }
    }
    
    # Error responses
    ERROR_RESPONSES = {
        'en': {
            'not_found': [
                "I couldn't find that, sir",
                "That doesn't seem to exist",
                "I can't locate that",
                "Not found, sir",
            ],
            'permission': [
                "I don't have permission to do that",
                "Access denied, sir",
                "I can't access that location",
                "Permission issue, sir",
            ],
            'needs_info': [
                "I need more information, sir. Could you specify both the name and location?",
                "I'm missing some details. Tell me what and where",
                "I need to know both the item and where it is",
                "Could you give me more details, sir?",
            ],
            'unknown_command': [
                "I'm not quite sure what you're asking, sir",
                "Could you rephrase that?",
                "I didn't catch that, sir. Try being more specific",
                "Sorry, I didn't understand that command",
            ],
        },
        'es': {
            'not_found': [
                "No pude encontrar eso, señor",
                "Eso no parece existir",
                "No puedo ubicar eso",
                "No encontrado, señor",
            ],
            'permission': [
                "No tengo permiso para hacer eso",
                "Acceso denegado, señor",
                "No puedo acceder a esa ubicación",
                "Problema de permiso, señor",
            ],
            'needs_info': [
                "Necesito más información, señor. ¿Podrías especificar el nombre y la ubicación?",
                "Me faltan detalles. Dime qué y dónde",
                "Necesito saber tanto el elemento como dónde está",
                "¿Podrías darme más detalles, señor?",
            ],
            'unknown_command': [
                "No estoy seguro de qué pides, señor",
                "¿Podrías reformular eso?",
                "No capté eso, señor. Sé más específico",
                "Disculpa, no entendí ese comando",
            ],
        }
    }
    
    @staticmethod
    def get_success_response(action, language='en'):
        """Get a random success response"""
        responses = ResponseGenerator.SUCCESS_RESPONSES.get(language, {}).get(action, ["Done"])
        return random.choice(responses)
    
    @staticmethod
    def get_error_response(error_type, language='en'):
        """Get a random error response"""
        responses = ResponseGenerator.ERROR_RESPONSES.get(language, {}).get(error_type, ["Something went wrong"])
        return random.choice(responses)
