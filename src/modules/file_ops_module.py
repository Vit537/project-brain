"""
File Operations Module - OpenClaw Pattern
Handles file and folder operations
"""
from typing import Dict, Any
from src.core.base_module import BaseModule
from src.system.file_ops import FileOperations


class FileOpsModule(BaseModule):
    """Module for file and folder operations"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.description = "Handles file and folder operations"
        self.file_ops = None
    
    async def initialize(self):
        """Load file operations on first use"""
        self.file_ops = FileOperations()
        await super().initialize()
    
    async def can_handle(self, intent: Dict[str, Any]) -> bool:
        """Check if this module handles files/folders"""
        intent_type = intent.get('type', '')
        return intent_type in ['file', 'folder', 'note']
    
    async def execute(self, intent: Dict[str, Any], shared) -> str:
        """Execute file operation"""
        text = intent.get('text', '')
        language = intent.get('language', 'en')
        
        # Use AI to parse command
        command = shared.ai.understand_command(text, language)
        action = command.get('action')
        target = command.get('target')
        location = command.get('location')
        
        # Execute action
        if action == 'create_folder':
            if not target or not location:
                return "I need the folder name and location" if language == 'en' else "Necesito el nombre y ubicación"
            
            success, message = self.file_ops.create_folder(target, location)
            if success:
                return f"Folder '{target}' created" if language == 'en' else f"Carpeta '{target}' creada"
            return message
        
        elif action == 'create_file':
            if not target or not location:
                return "I need the file name and location" if language == 'en' else "Necesito el nombre y ubicación"
            
            success, message = self.file_ops.create_file(target, location)
            if success:
                return f"File '{target}' created" if language == 'en' else f"Archivo '{target}' creado"
            return message
        
        elif action == 'delete_folder':
            success, message = self.file_ops.delete_folder(target, location)
            return message
        
        elif action == 'delete_file':
            success, message = self.file_ops.delete_file(target, location)
            return message
        
        elif action == 'write':
            content = command.get('content', '')
            append = command.get('append', False)
            location = self.file_ops.get_quick_location(location)
            
            success, message = self.file_ops.write_to_file(target, location, content, append)
            if success:
                return f"Content written to {target}" if language == 'en' else f"Contenido escrito en {target}"
            return message
        
        elif action == 'read':
            location = self.file_ops.get_quick_location(location)
            success, content = self.file_ops.read_file(target, location)
            if success:
                preview = content[:200] + "..." if len(content) > 200 else content
                return f"File content:\n{preview}"
            return content
        
        elif intent.get('type') == 'note':
            # Extract note content
            note_content = text.lower()
            for trigger in ['take a note', 'take note', 'note', 'anota', 'recuerda']:
                note_content = note_content.replace(trigger, '')
            note_content = note_content.strip().strip(':').strip()
            
            if not note_content:
                return "What would you like me to note?" if language == 'en' else "¿Qué quieres que anote?"
            
            success, message = self.file_ops.take_note(note_content)
            if success:
                return "Note saved" if language == 'en' else "Nota guardada"
            return message
        
        return "I couldn't complete that action" if language == 'en' else "No pude completar esa acción"
