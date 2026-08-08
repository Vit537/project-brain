"""
Quick test of Word module to verify it can create documents
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
from src.modules.apa_module import APAModule


async def test_word_operations():
    """Test Word module functionality"""
    print("\n" + "="*60)
    print("  JARVIS - Word Document Test")
    print("="*60 + "\n")
    
    # Initialize
    print("🔧 Initializing...")
    shared = SharedResources()
    module_manager = ModuleManager(shared)
    module_manager.register('file_ops', FileOpsModule)
    module_manager.register('word', WordModule)
    module_manager.register('pdf', PDFModule)
    module_manager.register('apa', APAModule)
    router = IntentRouter()
    
    print("✅ System initialized!\n")
    
    # Test: Create Word file
    print("━" * 60)
    print("TEST: Creating Word Document")
    print("━" * 60 + "\n")
    
    command = "create a word file on desktop in folder test-jarvis called mydocument and write hello world"
    print(f"Command: {command}\n")
    
    intent = await router.classify(command, 'en')
    print(f"Intent detected: {intent['type']}\n")
    
    response = await module_manager.execute_intent(intent)
    print(f"Response: {response}\n")
    
    # Check if file was created
    desktop = Path(os.path.expanduser('~')) / 'Desktop'
    test_folder = desktop / 'test-jarvis'
    test_file = test_folder / 'mydocument.docx'
    
    if test_file.exists():
        print(f"✅ File successfully created at: {test_file}")
        print(f"   File size: {test_file.stat().st_size} bytes\n")
    else:
        print(f"❌ File not found at: {test_file}\n")
    
    # Cleanup
    await module_manager.cleanup_all()
    print("✅ Test completed!")


if __name__ == "__main__":
    asyncio.run(test_word_operations())
