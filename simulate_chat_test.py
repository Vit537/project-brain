#!/usr/bin/env python3
"""
Interactive test of chat interface with the fixed Word routing
Types commands directly without waiting for user input
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.shared_resources import SharedResources
from src.core.module_manager import ModuleManager
from src.core.intent_router import IntentRouter
from src.modules.file_ops_module import FileOpsModule
from src.modules.word_module import WordModule
from src.modules.pdf_module import PDFModule


async def simulate_chat():
    """Simulate the chat interface with test commands"""
    print("\n" + "="*70)
    print("  JARVIS Chat - Simulated Interactive Test")
    print("="*70 + "\n")
    
    # Initialize
    shared = SharedResources()
    module_manager = ModuleManager(shared)
    module_manager.register('file_ops', FileOpsModule)
    module_manager.register('word', WordModule)
    module_manager.register('pdf', PDFModule)
    router = IntentRouter()
    
    # Test commands
    commands = [
        ("hola quiero saber que es lo que podes hacer", 'es'),
        ("crees un archivo word en el Desktop dentro de la carpeta new-2026 con el nombre prueba2 y escribe un cuento sobre caperucita roja", 'es'),
        ("status", 'en'),
    ]
    
    for command, lang in commands:
        print(f"\n{'━'*70}")
        print(f"💬 You: {command[:70]}...")
        print(f"{'━'*70}")
        
        # Special handling for "status" command
        if command == "status":
            status = module_manager.status()
            print(f"\n📊 System Status:")
            print(f"   Registered: {status['registered']}")
            print(f"   Loaded: {status['loaded']}")
            print(f"   Active: {status['active']}")
            continue
        
        # Route intent
        print(f"\n🧠 Analyzing intent...")
        intent = await router.classify(command, lang)
        print(f"   Intent Type: {intent['type']}")
        
        # Execute
        response = await module_manager.execute_intent(intent)
        print(f"\n🤖 JARVIS: {response[:200]}...")
    
    print("\n" + "="*70)
    await module_manager.cleanup_all()
    print("✅ Simulated chat test completed!\n")


if __name__ == "__main__":
    asyncio.run(simulate_chat())
