import json
import os
import chromadb
from chromadb.utils import embedding_functions

# --- CONFIGURATION ---
INPUT_FILE = "./data/verified_golden_rules.json"
RISKY_INPUT = "./data/extracted_clauses.json"  
DB_PATH = "./chroma_db_gold"
COLLECTION_NAME = "legal_gold_standards"

def build_database():
    print("🗃️  INITIALIZING GOLDEN STANDARD DATABASE...")
    print(f"    Safe clauses: {INPUT_FILE}")
    print(f"    Risky clauses: {RISKY_INPUT}")
    print(f"    Output: {DB_PATH}")

    # 1. Load Safe Clauses
    if not os.path.exists(INPUT_FILE):
        print("❌ Error: verified_golden_rules.json not found!")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        safe_clauses = json.load(f)
    
    print(f"    Loaded {len(safe_clauses)} safe clauses.")

    # 2. Load Risky Clauses
    risky_clauses = []
    if os.path.exists(RISKY_INPUT):
        with open(RISKY_INPUT, 'r', encoding='utf-8') as f:
            risky_clauses = json.load(f)
        print(f"    Loaded {len(risky_clauses)} risky clauses.")
    else:
        print("    ⚠️ No risky clauses file found. Will only index safe clauses.")

    # 3. Initialize ChromaDB
    client = chromadb.PersistentClient(path=DB_PATH)
    
    print("    Loading Embedding Model (all-MiniLM-L6-v2)...")
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # 4. Delete old collection
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("    (Deleted old collection)")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"description": "Safe and Risky Legal Clauses for RAG"}
    )

    # 5. Prepare Data
    ids = []
    documents = []
    metadatas = []

    # Add SAFE clauses
    print("    Indexing SAFE clauses...")
    for i, item in enumerate(safe_clauses):
        ids.append(f"safe_{i}")
        documents.append(item['safe_fix'])
        metadatas.append({
            "category": item['category'],
            "risk_level": "safe",  
            "style": item.get('style', 'Standard'),
            "source": "generated"
        })

    # Add RISKY clauses
    print("    Indexing RISKY clauses...")
    for i, item in enumerate(risky_clauses):
        ids.append(f"risky_{i}")
        documents.append(item['risky_text'])
        metadatas.append({
            "category": item['category'],
            "risk_level": "risky", 
            "source": "CUAD"
        })

    # 6. Add to ChromaDB
    print(f"    Indexing {len(documents)} total documents...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"✅ SUCCESS! Vector DB created:")
    print(f"   • Safe clauses: {len(safe_clauses)}")
    print(f"   • Risky clauses: {len(risky_clauses)}")
    print(f"   • Total: {len(documents)}")

if __name__ == "__main__":
    build_database()