"""
Quick test of the fixed Word intent routing and execution
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.shared_resources import SharedResources
from src.core.module_manager import ModuleManager
from src.core.intent_router import IntentRouter
from src.modules.file_ops_module import FileOpsModule
from src.modules.word_module import WordModule
from src.modules.pdf_module import PDFModule


async def test_word_creation():
    """Test Word document creation with your exact command"""
    print("\n" + "="*70)
    print("  JARVIS - Word Creation Test (Fixed Intent Routing)")
    print("="*70 + "\n")
    
    # Initialize
    shared = SharedResources()
    module_manager = ModuleManager(shared)
    module_manager.register('file_ops', FileOpsModule)
    module_manager.register('word', WordModule)
    module_manager.register('pdf', PDFModule)
    router = IntentRouter()
    
    # Your exact command (simplified)
    command = "crees un archivo word en el Desktop dentro de la carpeta new-2026 con el nombre prueba2"
    
    print(f"Command: {command}\n")
    print("-" * 70)
    
    # Step 1: Route intent
    intent = await router.classify(command, 'es')
    print(f"\n✅ Step 1: Intent Classification")
    print(f"   Type: {intent['type']} (expected: word)")
    
    # Step 2: Execute through module
    print(f"\n✅ Step 2: Module Execution")
    response = await module_manager.execute_intent(intent)
    print(f"   Response: {response}")
    
    # Step 3: Verify file
    print(f"\n✅ Step 3: File Verification")
    desktop = Path(os.path.expanduser('~')) / 'Desktop'
    test_folder = desktop / 'new-2026'
    test_file = test_folder / 'prueba2.docx'
    
    if test_file.exists():
        file_size = test_file.stat().st_size
        print(f"   ✅ File created successfully!")
        print(f"   Location: {test_file}")
        print(f"   Size: {file_size} bytes")
    else:
        print(f"   ❌ File not found at: {test_file}")
    
    print("\n" + "="*70)
    await module_manager.cleanup_all()
    print("✅ Test completed successfully!\n")


if __name__ == "__main__":
    asyncio.run(test_word_creation())
