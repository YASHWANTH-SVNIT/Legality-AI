from pydantic import BaseModel, Field

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str
    filename: str

class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: str
    filename: str
    progress: int = Field(ge=0, le=100)

class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str
    message: str