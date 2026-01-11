import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

import chromadb
from chromadb.utils import embedding_functions

from src.config.settings import VectorDBConfig
from src.core.models import RiskAnalysis, GeneratedFix

logger = logging.getLogger(__name__)

class FeedbackEntry(BaseModel):
    feedback_id: str = Field(..., description="Unique feedback ID")
    feedback_type: str = Field(..., description="Type: false_positive, false_negative, fix_approved, etc.")
    
    # Original analysis
    chunk_id: str = Field(..., description="ID of analyzed chunk")
    original_text: str = Field(..., description="Original clause text")
    category: str = Field(..., description="Category detected")
    system_risk_score: int = Field(..., description="System's risk score")
    
    # User correction
    user_risk_score: Optional[int] = Field(None, description="User's corrected risk score")
    user_classification: Optional[str] = Field(None, description="safe/risky")
    user_comment: Optional[str] = Field(None, description="User explanation")
    
    # Context
    user_id: Optional[str] = Field(None, description="User identifier")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # For fix feedback
    suggested_fix: Optional[str] = Field(None, description="Generated fix (if applicable)")
    fix_approved: Optional[bool] = Field(None, description="Did user approve fix?")

class FeedbackManager:

    def __init__(self):
        self.client = chromadb.PersistentClient(path=VectorDBConfig.DB_PATH)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize feedback collection
        self.feedback_collection = self._get_or_create_feedback_collection()
        
        logger.info("✅ Feedback Manager initialized")
    
    def _get_or_create_feedback_collection(self):
        try:
            collection = self.client.get_collection(
                name="user_feedback",
                embedding_function=self.embed_fn
            )
            logger.info("📂 Loaded existing feedback collection")
        except Exception:
            collection = self.client.create_collection(
                name="user_feedback",
                embedding_function=self.embed_fn,
                metadata={"description": "User-verified clauses and corrections"}
            )
            logger.info("📂 Created new feedback collection")
        
        return collection
    
    def add_false_positive_correction(
        self,
        chunk_id: str,
        original_text: str,
        category: str,
        system_risk_score: int,
        user_comment: str = "",
        user_id: Optional[str] = None
    ) -> str:

        feedback_id = f"fp_{chunk_id}_{datetime.utcnow().timestamp()}"
        
        # Store the clause as SAFE in feedback collection
        self.feedback_collection.add(
            ids=[feedback_id],
            documents=[original_text],
            metadatas=[{
                "feedback_type": "false_positive",
                "chunk_id": chunk_id,
                "category": category,
                "risk_level": "safe", 
                "system_score": system_risk_score,
                "user_comment": user_comment,
                "user_id": user_id or "anonymous",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "user_correction"
            }]
        )
        
        logger.info(f"✅ False positive recorded: {chunk_id}")
        return feedback_id
    
    def add_false_negative_correction(
        self,
        chunk_id: str,
        original_text: str,
        category: str,
        user_risk_score: int,
        user_comment: str = "",
        user_id: Optional[str] = None
    ) -> str:

        feedback_id = f"fn_{chunk_id}_{datetime.utcnow().timestamp()}"
        
        # Store the clause as RISKY in feedback collection
        self.feedback_collection.add(
            ids=[feedback_id],
            documents=[original_text],
            metadatas=[{
                "feedback_type": "false_negative",
                "chunk_id": chunk_id,
                "category": category,
                "risk_level": "risky", 
                "user_score": user_risk_score,
                "user_comment": user_comment,
                "user_id": user_id or "anonymous",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "user_correction"
            }]
        )
        
        logger.info(f"✅ False negative recorded: {chunk_id}")
        return feedback_id
    
    def add_fix_approval(
        self,
        chunk_id: str,
        original_risky_text: str,
        generated_fix: str,
        category: str,
        approved: bool,
        user_comment: str = "",
        user_id: Optional[str] = None
    ) -> str:

        feedback_id = f"fix_{chunk_id}_{datetime.utcnow().timestamp()}"
        
        if approved:
            self.feedback_collection.add(
                ids=[feedback_id],
                documents=[generated_fix],
                metadatas=[{
                    "feedback_type": "fix_approved",
                    "chunk_id": chunk_id,
                    "category": category,
                    "risk_level": "safe",
                    "original_risky": original_risky_text[:200], 
                    "user_comment": user_comment,
                    "user_id": user_id or "anonymous",
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "approved_fix"
                }]
            )
            logger.info(f"✅ Fix approved and stored: {chunk_id}")
        else:
            logger.info(f"❌ Fix rejected: {chunk_id} - {user_comment}")
        
        return feedback_id
    
    def add_risk_score_adjustment(
        self,
        chunk_id: str,
        original_text: str,
        category: str,
        system_score: int,
        user_score: int,
        user_comment: str = "",
        user_id: Optional[str] = None
    ) -> str:

        feedback_id = f"score_{chunk_id}_{datetime.utcnow().timestamp()}"
        
        if user_score >= 70:
            risk_level = "risky"
        elif user_score <= 40:
            risk_level = "safe"
        else:
            risk_level = "moderate"
        
        self.feedback_collection.add(
            ids=[feedback_id],
            documents=[original_text],
            metadatas=[{
                "feedback_type": "score_adjustment",
                "chunk_id": chunk_id,
                "category": category,
                "risk_level": risk_level,
                "system_score": system_score,
                "user_score": user_score,
                "score_delta": user_score - system_score,
                "user_comment": user_comment,
                "user_id": user_id or "anonymous",
                "timestamp": datetime.utcnow().isoformat(),
                "source": "user_adjustment"
            }]
        )
        
        logger.info(f"✅ Score adjustment recorded: {chunk_id} ({system_score}→{user_score})")
        return feedback_id
    
    def query_user_feedback(
        self,
        text: str,
        category: str,
        k: int = 3
    ) -> List[Dict]:

        try:
            results = self.feedback_collection.query(
                query_texts=[text],
                n_results=k,
                where={"category": category}
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
            logger.error(f"Feedback query failed: {e}")
            return []
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        try:
            all_data = self.feedback_collection.get()
            
            if not all_data['ids']:
                return {
                    "total_feedback": 0,
                    "by_type": {},
                    "by_category": {}
                }
            
            by_type = {}
            by_category = {}
            
            for metadata in all_data['metadatas']:
                ftype = metadata.get('feedback_type', 'unknown')
                by_type[ftype] = by_type.get(ftype, 0) + 1
                
                category = metadata.get('category', 'unknown')
                by_category[category] = by_category.get(category, 0) + 1
            
            return {
                "total_feedback": len(all_data['ids']),
                "by_type": by_type,
                "by_category": by_category
            }
            
        except Exception as e:
            logger.error(f"Stats retrieval failed: {e}")
            return {"error": str(e)}
    
    def export_feedback_for_review(self, output_file: str = "./data/feedback_export.json"):
        import json
        
        try:
            all_data = self.feedback_collection.get()
            
            export = []
            for i, doc_id in enumerate(all_data['ids']):
                export.append({
                    "id": doc_id,
                    "text": all_data['documents'][i],
                    "metadata": all_data['metadatas'][i]
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Exported {len(export)} feedback entries to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return None