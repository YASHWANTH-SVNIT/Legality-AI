from fastapi import APIRouter
from src.services.feedback_manager.feedback_manager import FeedbackManager

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "healthy"}

@router.get("/stats")
def stats():
    mgr = FeedbackManager()
    return mgr.get_feedback_stats()