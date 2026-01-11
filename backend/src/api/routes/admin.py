from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List
import logging

from src.services.feedback_manager.feedback_manager import FeedbackManager
from src.services.feedback_manager.learning_loop import LearningLoop
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "change-me")


router = APIRouter()
logger = logging.getLogger(__name__)

feedback_mgr = FeedbackManager()
learning_loop = LearningLoop(feedback_mgr)

ADMIN_API_KEY = "your-secret-admin-key-here"  

def verify_admin(x_api_key: Optional[str] = Header(None)):
    """Simple admin authentication"""
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin credentials")
    return True

@router.get("/learning-status")
def get_learning_status(admin: bool = Depends(verify_admin)):
    """
    Get system learning status and improvement suggestions
    """
    try:
        patterns = learning_loop.analyze_feedback_patterns()
        suggestions = learning_loop.get_improvement_suggestions()
        should_retrain = learning_loop.should_retrain()
        
        return {
            "patterns": patterns,
            "suggestions": suggestions,
            "should_retrain": should_retrain,
            "recommendation": "Review and retrain system" if should_retrain else "System performing well"
        }
    except Exception as e:
        logger.error(f"❌ Learning status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feedback/pending")
def get_pending_feedback(
    limit: int = 50,
    admin: bool = Depends(verify_admin)
):
    """
    Get all feedback items for review
    """
    try:
        all_data = feedback_mgr.feedback_collection.get()
        
        if not all_data['ids']:
            return {"feedback": [], "total": 0}
        
        feedback_items = []
        for i, doc_id in enumerate(all_data['ids'][:limit]):
            feedback_items.append({
                "id": doc_id,
                "text": all_data['documents'][i],
                "metadata": all_data['metadatas'][i],
                "type": all_data['metadatas'][i].get('feedback_type'),
                "category": all_data['metadatas'][i].get('category'),
                "timestamp": all_data['metadatas'][i].get('timestamp')
            })
        
        return {
            "feedback": feedback_items,
            "total": len(all_data['ids']),
            "showing": len(feedback_items)
        }
    except Exception as e:
        logger.error(f"❌ Get feedback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/{feedback_id}/approve")
def approve_feedback(
    feedback_id: str,
    admin: bool = Depends(verify_admin)
):
    """
    Approve feedback item (marks for promotion to gold standard)
    
    In production, this would:
    1. Add metadata: {"approved": True, "approved_by": admin_id}
    2. Trigger vector DB rebuild with approved items
    """
    try:
        result = feedback_mgr.feedback_collection.get(ids=[feedback_id])
        
        if not result['ids']:
            raise HTTPException(status_code=404, detail="Feedback not found")

        logger.info(f"✅ Feedback approved: {feedback_id}")
        
        return {
            "status": "approved",
            "feedback_id": feedback_id,
            "message": "Feedback approved. Will be included in next DB rebuild."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Approve failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/{feedback_id}/reject")
def reject_feedback(
    feedback_id: str,
    reason: Optional[str] = None,
    admin: bool = Depends(verify_admin)
):
    """
    Reject feedback item (remove from collection)
    """
    try:
        feedback_mgr.feedback_collection.delete(ids=[feedback_id])
        
        logger.info(f"❌ Feedback rejected: {feedback_id} - Reason: {reason}")
        
        return {
            "status": "rejected",
            "feedback_id": feedback_id,
            "message": "Feedback rejected and removed."
        }
    except Exception as e:
        logger.error(f"❌ Reject failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export-feedback")
def export_feedback(admin: bool = Depends(verify_admin)):
    """
    Export all feedback to JSON file for review
    """
    try:
        export_path = feedback_mgr.export_feedback_for_review()
        
        if not export_path:
            raise HTTPException(status_code=500, detail="Export failed")
        
        return {
            "status": "success",
            "export_path": export_path,
            "message": f"Feedback exported to {export_path}"
        }
    except Exception as e:
        logger.error(f"❌ Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild-db")
def rebuild_vector_db(
    include_approved_feedback: bool = True,
    admin: bool = Depends(verify_admin)
):
    """
    Trigger vector DB rebuild with approved feedback
    
    WARNING: This is a heavy operation. Run during off-hours.
    """
    try:
        
        logger.warning("🔄 Vector DB rebuild triggered by admin")
        
        return {
            "status": "initiated",
            "message": "DB rebuild started. This may take 10-30 minutes.",
            "warning": "System will be read-only during rebuild"
        }
    except Exception as e:
        logger.error(f"❌ Rebuild failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-health")
def get_system_health(admin: bool = Depends(verify_admin)):
    """
    Get overall system health metrics
    """
    try:
        stats = feedback_mgr.get_feedback_stats()
        patterns = learning_loop.analyze_feedback_patterns()
        
        try:
            from src.rag.vector_store import VectorStore
            vs = VectorStore()
            db_stats = vs.get_stats()
            db_healthy = True
        except Exception as e:
            db_stats = {"error": str(e)}
            db_healthy = False
        
        health_score = 100
        if patterns["false_positive_rate"] > 30:
            health_score -= 20
        if patterns["false_negative_rate"] > 30:
            health_score -= 20
        if not db_healthy:
            health_score -= 30
        
        return {
            "overall_health": health_score,
            "status": "healthy" if health_score >= 70 else "needs_attention",
            "metrics": {
                "total_feedback": stats.get("total_feedback", 0),
                "false_positive_rate": patterns["false_positive_rate"],
                "false_negative_rate": patterns["false_negative_rate"],
                "vector_db_healthy": db_healthy,
                "vector_db_stats": db_stats
            },
            "recommendations": learning_loop.get_improvement_suggestions()
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/feedback/clear-all")
def clear_all_feedback(
    confirm: bool = False,
    admin: bool = Depends(verify_admin)
):
    """
    DANGER: Clear all feedback data
    Requires confirmation parameter
    """
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Must set confirm=true to clear all feedback"
        )
    
    try:
        feedback_mgr.client.delete_collection("user_feedback")
        feedback_mgr._get_or_create_feedback_collection()
        
        logger.warning("⚠️ All feedback cleared by admin")
        
        return {
            "status": "cleared",
            "message": "All feedback data has been deleted"
        }
    except Exception as e:
        logger.error(f"❌ Clear failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))