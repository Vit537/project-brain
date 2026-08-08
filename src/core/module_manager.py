"""
Module Manager - OpenClaw Pattern
Manages all JARVIS modules with lazy loading
Only loads modules when they're actually used
"""
from typing import Dict, Type, Optional, Set
from .base_module import BaseModule
from .shared_resources import SharedResources


class ModuleManager:
    """
    Manages all JARVIS modules - lazy loading (OpenClaw pattern)
    
    Flow:
    1. Register modules (doesn't instantiate yet)
    2. User sends command
    3. Load module only when needed
    4. Execute with shared resources
    """
    
    def __init__(self, shared: SharedResources):
        self.shared = shared
        self.registry: Dict[str, Type[BaseModule]] = {}
        self.loaded_modules: Dict[str, BaseModule] = {}
        self._initialized: Set[str] = set()
        
        print("✓ Module Manager created")
    
    def register(self, name: str, module_class: Type[BaseModule]):
        """
        Register a module class (doesn't load it yet)
        
        Args:
            name: Module name
            module_class: Module class (not instance!)
        """
        self.registry[name] = module_class
        print(f"  ↳ Registered module: {name}")
    
    async def get(self, name: str) -> Optional[BaseModule]:
        """
        Get module instance - loads on first access (lazy loading)
        
        Args:
            name: Module name
            
        Returns:
            BaseModule: Module instance or None
        """
        if name not in self.registry:
            return None
        
        # Load module if not already loaded
        if name not in self.loaded_modules:
            module_class = self.registry[name]
            module = module_class(name)
            
            # Initialize module
            await module.initialize()
            
            self.loaded_modules[name] = module
            self._initialized.add(name)
            print(f"  ↳ Lazy-loaded module: {name}")
        
        return self.loaded_modules[name]
    
    async def execute_intent(self, intent: Dict) -> str:
        """
        Execute intent by finding the right module
        
        Args:
            intent: Intent dictionary from IntentRouter
            
        Returns:
            str: Response message
        """
        # Route summary requests to last-read document type when possible
        text = intent.get('text', '').lower()
        if any(word in text for word in ['summary', 'summarize', 'resumen', 'resumir', 'resume']):
            last_type = self.shared.session_state.get('last_read_type')
            if last_type in ['word', 'pdf'] and intent.get('type') in ['conversation', 'word']:
                intent['type'] = last_type

        # Optional writing mode: append conversational lines to last Word document
        if intent.get('type') == 'conversation' and self.shared.session_state.get('stream_to_word'):
            text_raw = intent.get('text', '').strip()
            if text_raw and text_raw.lower() not in ['status', 'exit', 'quit'] and '?' not in text_raw:
                word_module = await self.get('word')
                if word_module and word_module.enabled:
                    response = await word_module.append_to_last_word(text_raw, intent.get('language', 'en'))
                    self.shared.save_session_state()
                    return response

        # Check each registered module
        for name in self.registry.keys():
            module = await self.get(name)
            
            if module and module.enabled and await module.can_handle(intent):
                print(f"  ↳ Module '{name}' handling request")
                response = await module.execute(intent, self.shared)
                self.shared.save_session_state()
                return response
        
        # Fallback to AI conversation
        print("  ↳ No module matched - using AI conversation")
        response = await self._handle_conversation(intent)
        self.shared.save_session_state()
        return response
    
    async def _handle_conversation(self, intent: Dict) -> str:
        """Fallback AI conversation handler"""
        import time
        from src.ai.response_generator import ResponseGenerator
        
        text = intent.get('text', '')
        language = intent.get('language', 'en')
        
        # Use shared AI brain
        ai = self.shared.ai
        memory = self.shared.memory
        
        # Get context from memory
        context_blocks = []
        embedding = None
        if memory and memory.enabled:
            rows, embedding = memory.get_context(text, k=5)
            for row in rows:
                snippet = f"User: {row['user_input']}\nAssistant: {row['ai_response']}"
                context_blocks.append(snippet)
        
        system_prompt = "You are JARVIS, a helpful AI assistant. Answer briefly and naturally."
        if language == 'es':
            system_prompt = "Eres JARVIS, un asistente de IA útil. Responde de manera breve y natural."
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context_blocks:
            context_text = "\n\n".join(context_blocks)
            messages.append({"role": "system", "content": f"Relevant context:\n{context_text}"})
        
        messages.append({"role": "user", "content": text})
        
        start_time = time.time()
        response = ai.client.chat.completions.create(
            model=ai.model,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        latency_ms = int((time.time() - start_time) * 1000)
        
        result = response.choices[0].message.content.strip()
        
        # Store in memory with all required parameters
        if memory and memory.enabled and embedding:
            memory.store_interaction(
                user_input=text,
                ai_response=result,
                embedding=embedding,
                intent="conversation",
                action_taken=None,
                success=True,
                latency_ms=latency_ms,
                language=language
            )
        
        return result
    
    async def cleanup_all(self):
        """Cleanup all loaded modules"""
        for module in self.loaded_modules.values():
            await module.cleanup()
        print("✓ All modules cleaned up")
    
    def status(self):
        """Get manager status"""
        return {
            'registered': len(self.registry),
            'loaded': len(self.loaded_modules),
            'modules': list(self.registry.keys()),
            'active': list(self.loaded_modules.keys())
        }
