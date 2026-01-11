from pydantic import BaseModel
from typing import Optional

class FeedbackRequest(BaseModel):
    chunk_id: str
    clause_text: str
    category: str
    system_risk_score: int = 0
    user_risk_score: Optional[int] = None
    user_comment: Optional[str] = None
    user_id: Optional[str] = "anonymous"
    suggested_fix: Optional[str] = None
    approved: Optional[bool] = None