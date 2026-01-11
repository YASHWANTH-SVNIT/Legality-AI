from fastapi import APIRouter, HTTPException
import logging

from src.api.models.requests import FeedbackRequest
from src.api.models.responses import FeedbackResponse
from src.services.feedback_manager.feedback_manager import FeedbackManager

router = APIRouter()
logger = logging.getLogger(__name__)

feedback_mgr = FeedbackManager()

@router.post("/false-positive", response_model=FeedbackResponse)
def report_false_positive(request: FeedbackRequest):
    try:
        feedback_id = feedback_mgr.add_false_positive_correction(
            chunk_id=request.chunk_id,
            original_text=request.clause_text,
            category=request.category,
            system_risk_score=request.system_risk_score,
            user_comment=request.user_comment or "",
            user_id=request.user_id
        )
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            status="recorded",
            message="Thank you! Correction recorded."
        )
    except Exception as e:
        logger.error(f"❌ Feedback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/false-negative", response_model=FeedbackResponse)
def report_false_negative(request: FeedbackRequest):
    try:
        feedback_id = feedback_mgr.add_false_negative_correction(
            chunk_id=request.chunk_id,
            original_text=request.clause_text,
            category=request.category,
            user_risk_score=request.user_risk_score or 70,
            user_comment=request.user_comment or "",
            user_id=request.user_id
        )
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            status="recorded",
            message="Thank you! We'll improve detection."
        )
    except Exception as e:
        logger.error(f"❌ Feedback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve-fix", response_model=FeedbackResponse)
def approve_fix(request: FeedbackRequest):
    try:
        feedback_id = feedback_mgr.add_fix_approval(
            chunk_id=request.chunk_id,
            original_risky_text=request.clause_text,
            generated_fix=request.suggested_fix or "",
            category=request.category,
            approved=request.approved or False,
            user_comment=request.user_comment or "",
            user_id=request.user_id
        )
        
        message = "Fix approved!" if request.approved else "Thanks for feedback!"
        
        return FeedbackResponse(
            feedback_id=feedback_id,
            status="recorded",
            message=message
        )
    except Exception as e:
        logger.error(f"❌ Feedback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))