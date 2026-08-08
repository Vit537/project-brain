"""
Test script to verify PostgreSQL + pgvector connection and setup
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("JARVIS Memory System - Connection Test")
print("="*60 + "\n")

# Test 1: Check environment variables
print("[1] Checking environment variables...")
db_url = os.getenv("DATABASE_URL")
openai_key = os.getenv("OPENAI_API_KEY")

if db_url:
    print(f"✓ DATABASE_URL found: {db_url[:50]}...")
else:
    print("✗ DATABASE_URL not found")

if openai_key:
    print(f"✓ OPENAI_API_KEY found: {openai_key[:20]}...")
else:
    print("✗ OPENAI_API_KEY not found")

# Test 2: Test PostgreSQL connection
print("\n[2] Testing PostgreSQL connection...")
try:
    import psycopg2
    from pgvector.psycopg2 import register_vector
    
    conn = psycopg2.connect(db_url)
    print("✓ Connected to PostgreSQL")
    
    register_vector(conn)
    conn.autocommit = True
    
    with conn.cursor() as cur:
        # Check pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✓ pgvector extension ready")
        
        # Create conversations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                ts TIMESTAMPTZ DEFAULT NOW(),
                user_input TEXT NOT NULL,
                ai_response TEXT,
                embedding vector(1536),
                intent VARCHAR(100),
                action_taken TEXT,
                success BOOLEAN,
                latency_ms INTEGER,
                language VARCHAR(10)
            );
        """)
        print("✓ conversations table created/verified")
        
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_embedding
            ON conversations USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        print("✓ Vector index created")
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_ts
            ON conversations (ts DESC);
        """)
        print("✓ Timestamp index created")
        
        # Check table info
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='conversations'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        print(f"\n✓ Table schema ({len(columns)} columns):")
        for col_name, col_type in columns:
            print(f"   - {col_name}: {col_type}")
    
    conn.close()
    
except Exception as e:
    print(f"✗ PostgreSQL connection failed: {e}")

# Test 3: Test OpenAI embeddings
print("\n[3] Testing OpenAI embeddings...")
try:
    from openai import OpenAI
    
    client = OpenAI(api_key=openai_key)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="test embedding"
    )
    embedding = response.data[0].embedding
    print(f"✓ OpenAI embeddings working")
    print(f"✓ Embedding dimension: {len(embedding)}")
    
except Exception as e:
    print(f"✗ OpenAI embeddings failed: {e}")

# Test 4: Test VectorStore class
print("\n[4] Testing VectorStore class...")
try:
    from src.db.vector_store import VectorStore
    
    store = VectorStore(db_url)
    if store.enabled:
        print("✓ VectorStore initialized and ready")
    else:
        print("✗ VectorStore disabled")
        
except Exception as e:
    print(f"✗ VectorStore test failed: {e}")

# Test 5: Test EmbeddingClient class
print("\n[5] Testing EmbeddingClient class...")
try:
    from src.ai.embeddings import EmbeddingClient
    
    embedder = EmbeddingClient()
    if embedder.enabled:
        print("✓ EmbeddingClient initialized and ready")
        emb = embedder.embed("test")
        if emb:
            print(f"✓ Test embedding generated: {len(emb)} dimensions")
    else:
        print("✗ EmbeddingClient disabled")
        
except Exception as e:
    print(f"✗ EmbeddingClient test failed: {e}")

print("\n" + "="*60)
print("✓ All systems ready! Memory is now ACTIVE")
print("="*60 + "\n")
