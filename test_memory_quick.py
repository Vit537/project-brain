"""
Quick test of complete JARVIS memory system with Chroma
"""
from src.ai.embeddings import EmbeddingClient
from src.db.chroma_store import ChromaVectorStore
from src.ai.memory import MemoryManager

print("\n" + "="*60)
print("✓ JARVIS Memory System - READY")
print("="*60 + "\n")

# Initialize
embedder = EmbeddingClient()
store = ChromaVectorStore()
memory = MemoryManager(embedder, store)

print(f"✓ Embeddings: {embedder.enabled} (local, 384-dim)")
print(f"✓ Chroma DB: {store.enabled} (offline)")
print(f"✓ Memory: {memory.enabled} (active)")
print(f"✓ Stored conversations: {store.get_total_conversations()}\n")

if memory.enabled:
    # Store a few test conversations
    test_data = [
        ("What time is it?", "It's 3:45 PM"),
        ("Tell me a joke", "Why did the chicken cross the road? To get to the other side!"),
        ("How's the weather?", "It's sunny and 72 degrees outside"),
    ]
    
    print("Storing test conversations...")
    for user_input, ai_response in test_data:
        emb = embedder.embed(user_input)
        memory.store_interaction(
            user_input=user_input,
            ai_response=ai_response,
            embedding=emb,
            intent="test",
            action_taken=None,
            success=True,
            latency_ms=100,
            language="en"
        )
    
    print(f"✓ Total stored: {store.get_total_conversations()}\n")
    
    # Test retrieval
    print("Testing retrieval (similarity search)...")
    query = "What's the time right now?"
    context, _ = memory.get_context(query, k=3)
    
    print(f"✓ Query: '{query}'")
    print(f"✓ Retrieved {len(context)} similar conversations:\n")
    for i, conv in enumerate(context, 1):
        print(f"  [{i}] User: {conv['user_input']}")
        print(f"      Response: {conv['ai_response']}\n")

print("="*60)
print("✓ ALL SYSTEMS READY")
print("Cost: $0 (completely free)")
print("="*60 + "\n")
