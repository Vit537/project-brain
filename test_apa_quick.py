"""
Quick test for APA Module functionality
Tests basic APA template creation
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.shared_resources import SharedResources
from src.core.module_manager import ModuleManager
from src.core.intent_router import IntentRouter
from src.modules.apa_module import APAModule


async def test_apa():
    """Test APA module"""
    print("\n" + "="*60)
    print("  APA Module - Quick Test")
    print("="*60 + "\n")
    
    # Initialize
    print("🔧 Initializing...")
    shared = SharedResources()
    manager = ModuleManager(shared)
    manager.register('apa', APAModule)
    router = IntentRouter()
    
    print("✅ System initialized!\n")
    
    # Test 1: Create APA report template
    print("Test 1: Create APA report template")
    test_input = 'create APA report template for "My Thesis on AI"'
    intent = await router.classify(test_input, 'en')
    print(f"  Input: {test_input}")
    print(f"  Intent: {intent['type']}")
    
    if intent['type'] == 'apa':
        response = await manager.execute_intent(intent)
        print(f"  Response: {response[:100]}...")
    else:
        print(f"  ❌ Wrong intent type! Expected 'apa', got '{intent['type']}'")
    
    print()
    
    # Test 2: Capability question (should be conversation, not APA)
    print("Test 2: Capability question (should stay conversational)")
    test_input = "can you create an APA report?"
    intent = await router.classify(test_input, 'en')
    print(f"  Input: {test_input}")
    print(f"  Intent: {intent['type']}")
    
    if intent['type'] != 'apa':
        print(f"  ✅ Correctly redirected to conversation")
    else:
        print(f"  ❌ Should be conversation, not APA")
    
    print()
    
    # Test 3: Create with Spanish command
    print("Test 3: Spanish APA command")
    test_input = "crear plantilla apa para 'Mi Tesis'"
    intent = await router.classify(test_input, 'es')
    print(f"  Input: {test_input}")
    print(f"  Intent: {intent['type']}")
    
    if intent['type'] == 'apa':
        print(f"  ✅ Spanish APA command recognized")
    else:
        print(f"  ❌ Should recognize Spanish APA command")
    
    print("\n✅ All tests completed!\n")


if __name__ == "__main__":
    asyncio.run(test_apa())
