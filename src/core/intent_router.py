"""
Intent Router - OpenClaw Pattern
Classifies user input and routes to appropriate module
"""
import re
from typing import Dict, Any


class IntentRouter:
    """
    Central place to decide which module should handle a command
    Keeps modules independent (OpenClaw pattern)
    """
    
    def __init__(self):
        # IMPORTANT: Order matters! Check more specific patterns first
        # Check Word/PDF BEFORE File (more specific)
        # Check File/Folder BEFORE general operators
        self.patterns = {
            # Document operations (check FIRST - most specific)
            'apa': ['apa report', 'apa template', 'crear reporte apa', 'plantilla apa'],
            'pdf': ['pdf', 'read pdf', 'open pdf', 'leer pdf', 'archivo pdf'],
            'word': [
                'word', 'docx', 'archivo word', 'word file',
                'summary', 'summarize', 'resumen', 'resumir'
            ],
            
            # File operations (check BEFORE calculator to avoid '-' match)
            'file': ['create file', 'delete file', 'write to', 'read file', 'crear archivo', 'eliminar archivo', 'search file', 'buscar archivo', 'find file'],
            'folder': ['create folder', 'delete folder', 'crear carpeta', 'eliminar carpeta'],
            
            # Other specific operations
            'note': ['note', 'remember', 'write down', 'anota', 'recuerda'],
            'app': ['open', 'launch', 'start', 'abrir', 'ejecutar'],
            'time': ['time', 'hora', 'what time'],
            'date': ['date', 'fecha', 'what date'],
            'system': ['system', 'sistema', 'memory', 'memoria', 'cpu'],
            
            # Calculator (check LAST - avoid matching '-' in dates/numbers)
            # REMOVED: single characters '+', '-', '*', '/' to avoid false matches
            'calculator': ['calculate', 'calcular', 'plus', 'minus', 'times', 'divided', 'multiply', 'divide'],
        }
    
    async def classify(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Classify user input into an intent
        
        Args:
            text: User's input text
            language: Language ('en' or 'es')
            
        Returns:
            dict: Intent with type, text, action, etc.
        """
        text_lower = text.lower()

        # Conversation-first guard: capability/general questions should not execute tools
        if self._is_capability_question(text_lower):
            return {
                'type': 'conversation',
                'text': text,
                'language': language,
                'confidence': 0.9
            }

        # Hard routing for clear document types
        if any(keyword in text_lower for keyword in ['apa report', 'apa template', 'crear reporte apa', 'plantilla apa']):
            return {
                'type': 'apa',
                'text': text,
                'language': language,
                'confidence': 1.0
            }
        if 'pdf' in text_lower:
            return {
                'type': 'pdf',
                'text': text,
                'language': language,
                'confidence': 1.0
            }
        if any(token in text_lower for token in [' word ', 'docx', 'archivo word', 'word file']):
            return {
                'type': 'word',
                'text': text,
                'language': language,
                'confidence': 1.0
            }
        
        # Check patterns in order (specific to general)
        # IMPORTANT: Dictionary now has ordered patterns
        for intent_type, keywords in self.patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return {
                    'type': intent_type,
                    'text': text,
                    'language': language,
                    'confidence': 1.0
                }
        
        # Default to conversation
        return {
            'type': 'conversation',
            'text': text,
            'language': language,
            'confidence': 0.5
        }

    def _is_capability_question(self, text_lower: str) -> bool:
        """Detect questions asking if the agent can do something (should stay conversational)."""
        question_starters = [
            'can you', 'could you', 'do you', 'are you able', 'tell me if', 'hi',
            'puedes', 'podrias', 'me puedes decir', 'dime si', 'eres capaz'
        ]
        action_words = ['read', 'create', 'summarize', 'edit', 'open', 'leer', 'crear', 'resumir', 'editar', 'abrir']
        object_words = ['pdf', 'word', 'docx', 'document', 'apa', 'report', 'template', 'plantilla']

        starts_like_question = any(text_lower.strip().startswith(s) for s in question_starters) or '?' in text_lower
        has_action = any(a in text_lower for a in action_words)
        has_object = any(o in text_lower for o in object_words)
        has_execution_detail = any(k in text_lower for k in ['"', "'", 'path', 'ruta', 'called', 'named', 'con el nombre'])

        return starts_like_question and has_action and has_object and not has_execution_detail
    
    async def classify_with_ai(self, text: str, ai_brain, language: str = 'en') -> Dict[str, Any]:
        """
        Use AI to classify complex intents (OpenClaw-style)
        
        Args:
            text: User's input
            ai_brain: AI Brain instance
            language: Language
            
        Returns:
            dict: Intent with details
        """
        # For now, use simple classification
        # Later: Use AI for complex intent detection
        return await self.classify(text, language)
