import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Collection names
COLLECTION_GOLDEN_STANDARDS = "legal_gold_standards"
COLLECTION_PROTOTYPES = "category_prototypes"

class VectorStore:

    def __init__(self, db_path: str = "./chroma_db_gold"):
        self.client = chromadb.PersistentClient(path=db_path)
        
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Load collections
        try:
            self.golden_standards = self.client.get_collection(
                name=COLLECTION_GOLDEN_STANDARDS,
                embedding_function=self.embed_fn
            )
            logger.info(f"✅ Loaded collection: {COLLECTION_GOLDEN_STANDARDS}")
        except Exception as e:
            logger.error(f"❌ Failed to load {COLLECTION_GOLDEN_STANDARDS}: {e}")
            raise
        
        # Get or create prototypes
        try:
            self.prototypes = self.client.get_collection(
                name=COLLECTION_PROTOTYPES,
                embedding_function=self.embed_fn
            )
            logger.info(f"✅ Loaded collection: {COLLECTION_PROTOTYPES}")
        except Exception:
            logger.warning(f"⚠️ Creating {COLLECTION_PROTOTYPES} collection")
            self.prototypes = self._create_prototype_collection()
    
    def _create_prototype_collection(self):
        collection = self.client.create_collection(
            name=COLLECTION_PROTOTYPES,
            embedding_function=self.embed_fn,
            metadata={"description": "Category prototypes"}
        )
        
        prototypes = {
            "Unilateral Termination": """
            Contract termination clauses. Covers ending agreement, notice periods, 
            termination rights, cancellation. Keywords: terminate, cancel, end, notice.
            """,
            "Unlimited Liability": """
            Liability clauses without caps. Covers unlimited exposure, uncapped damages, 
            indemnification without limits. Keywords: unlimited, uncapped, liable for all.
            """,
            "Non-Compete": """
            Post-contract competitive restrictions. Covers non-compete, customer 
            solicitation, restrictive covenants. Keywords: compete, solicit, restrictive.
            """
        }
        
        for category, desc in prototypes.items():
            collection.add(
                documents=[desc],
                metadatas=[{"category": category, "type": "prototype"}],
                ids=[f"prototype_{category.lower().replace(' ', '_')}"]
            )
        
        logger.info(f"✅ Created {len(prototypes)} prototypes")
        return collection
    
    def query_prototypes(self, text: str, k: int = 1) -> List[Dict]:
        results = self.prototypes.query(
            query_texts=[text],
            n_results=k
        )
        
        if not results['documents'][0]:
            return []
        
        formatted = []
        for i in range(len(results['documents'][0])):
            formatted.append({
                "category": results['metadatas'][0][i]['category'],
                "similarity": 1 - results['distances'][0][i]
            })
        
        return formatted
    
    def query_category(
        self,
        text: str,
        category: str,
        risk_level: Optional[str] = None,
        k: int = 3
    ) -> List[Dict]:
        
        where_filter = {"category": {"$eq": category}}
        
        if risk_level:
            where_filter = {
                "$and": [
                    {"category": {"$eq": category}},
                    {"risk_level": {"$eq": risk_level}}
                ]
            }
        
        try:
            results = self.golden_standards.query(
                query_texts=[text],
                n_results=k,
                where=where_filter
            )
            
            if not results['documents'][0]:
                return []
            
            formatted = []
            for i in range(len(results['documents'][0])):
                formatted.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity": 1 - results['distances'][0][i]
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []
    
    def add_verified_clause(self, text: str, category: str, risk_level: str):
        """Add a manually verified or user-corrected clause to the gold standards"""
        import uuid
        try:
            self.golden_standards.add(
                ids=[f"verified_{uuid.uuid4().hex[:8]}"],
                documents=[text],
                metadatas=[{
                    "category": category,
                    "risk_level": risk_level,
                    "source": "user_feedback_sync",
                    "timestamp": "" # Add if helpful
                }]
            )
            logger.info(f"✅ Added safe clause to Chroma: {category}")
            return True
        except Exception as e:
            logger.error(f"Failed to add verified clause: {e}")
            return False

    def get_stats(self) -> Dict:
        try:
            gold_data = self.golden_standards.get()
            
            stats = {
                "total_clauses": len(gold_data['ids']),
                "by_category": {},
                "by_risk_level": {}
            }
            
            for metadata in gold_data['metadatas']:
                cat = metadata.get('category', 'unknown')
                risk = metadata.get('risk_level', 'unknown')
                
                stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
                stats['by_risk_level'][risk] = stats['by_risk_level'].get(risk, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Stats failed: {e}")
            return {}