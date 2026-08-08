"""
Query Handler
Routes different types of queries (file operations, time, system, etc)
"""
from colorama import Fore, Style, init

init(autoreset=True)


class QueryRouter:
    """Routes queries to appropriate handlers"""
    
    # Keywords that trigger different services
    TIME_KEYWORDS = ['time', 'hour', 'what time', 'hora', 'qué hora', 'me digas la hora']
    DATE_KEYWORDS = ['date', 'today', 'what day', 'día', 'hoy', 'fecha']
    SYSTEM_KEYWORDS = ['cpu', 'memory', 'ram', 'disk', 'battery', 'system', 'status', 'disco', 'batería']
    CALCULATOR_KEYWORDS = ['calculate', 'math', 'plus', 'minus', 'times', 'divided', 'calcular', 'matemática']
    FILE_KEYWORDS = ['create', 'delete', 'move', 'copy', 'search', 'folder', 'file', 'write', 'read', 'crear', 'eliminar', 'buscar', 'escribir', 'leer']
    NOTE_KEYWORDS = ['note', 'take a note', 'write down', 'remember', 'nota', 'anota', 'apunta', 'recuerda']
    APP_KEYWORDS = ['open', 'launch', 'start', 'abre', 'lanza', 'inicia']
    
    @staticmethod
    def identify_query_type(user_input, language='en'):
        """
        Identify what type of query this is
        
        Returns:
            str: Query type ('time', 'date', 'system', 'calculator', 'file', 'app', 'conversation')
        """
        text_lower = user_input.lower()
        
        # Check for specific query types
        if any(keyword in text_lower for keyword in QueryRouter.TIME_KEYWORDS):
            return 'time'
        
        if any(keyword in text_lower for keyword in QueryRouter.DATE_KEYWORDS):
            return 'date'
        
        if any(keyword in text_lower for keyword in QueryRouter.SYSTEM_KEYWORDS):
            return 'system'
        
        if any(keyword in text_lower for keyword in QueryRouter.CALCULATOR_KEYWORDS):
            return 'calculator'
        
        if any(keyword in text_lower for keyword in QueryRouter.NOTE_KEYWORDS):
            return 'note'
        
        if any(keyword in text_lower for keyword in QueryRouter.FILE_KEYWORDS):
            return 'file'
        
        if any(keyword in text_lower for keyword in QueryRouter.APP_KEYWORDS):
            return 'app'
        
        # Default to conversation
        return 'conversation'
