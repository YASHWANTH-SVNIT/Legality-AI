from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


class DocumentMetadata(BaseModel):
    filename: str
    file_size: int  
    page_count: int
    extraction_date: datetime = Field(default_factory=datetime.now)
    
    contract_type: Optional[str] = None
    parties: Optional[List[str]] = None
    effective_date: Optional[str] = None
    mentioned_amounts: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "vendor_nda.pdf",
                "file_size": 245760,
                "page_count": 12,
                "contract_type": "NDA",
                "parties": ["Acme Corp", "Vendor Inc"],
                "effective_date": "January 1, 2024"
            }
        }

class Definition(BaseModel):
    term: str
    definition: str
    section: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "term": "Confidential Information",
                "definition": "all non-public information disclosed by either party",
                "section": "1.1"
            }
        }

class SemanticChunk(BaseModel):
    id: str
    text: str
    start_char: int
    end_char: int
    word_count: int
    
    embedding: Optional[List[float]] = None
    semantic_score: Optional[float] = None  
    
    preceding_text: Optional[str] = None  
    following_text: Optional[str] = None  
    
    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Chunk text cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "chunk_001",
                "text": "Either party may terminate this Agreement...",
                "start_char": 1523,
                "end_char": 1789,
                "word_count": 45
            }
        }

class ProcessedDocument(BaseModel):
    metadata: DocumentMetadata
    full_text: str
    definitions: List[Definition]
    chunks: List[SemanticChunk]
    
    total_chunks: int
    avg_chunk_length: float
    processing_time_seconds: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {"filename": "contract.pdf"},
                "full_text": "This Agreement is made...",
                "definitions": [],
                "chunks": [],
                "total_chunks": 45,
                "avg_chunk_length": 250.5,
                "processing_time_seconds": 3.2
            }
        }

class CategoryDetection(BaseModel):
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    similarity_to_prototype: float
    zone: Literal["noise", "courtroom", "safe"]
    needs_agent_review: bool
    
    retrieved_prototypes: Optional[List[str]] = None
    decision_reasoning: str

class ExtractedParameters(BaseModel):
    days: Optional[int] = None
    months: Optional[int] = None
    years: Optional[int] = None
    amount: Optional[str] = None
    percentage: Optional[float] = None
    
    written_notice_required: bool = False
    party_symmetry: bool = False
    for_cause_only: bool = False
    
    raw_matches: Dict[str, Any] = Field(default_factory=dict)

class AgentArgument(BaseModel):
    agent_name: Literal["Pessimist", "Optimist", "Arbiter"]
    argument: str
    confidence: Optional[float] = None
    retrieved_precedents: Optional[List[str]] = None

class RiskAnalysis(BaseModel):
    is_relevant: bool
    category: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: Literal["Low", "Medium", "High"]
    
    reasoning: str
    debate_transcript: List[AgentArgument]
    
    extracted_parameters: Optional[ExtractedParameters] = None
    parameter_deviations: Optional[Dict[str, Any]] = None
    
    retrieved_safe_examples: List[str] = Field(default_factory=list)
    retrieved_risky_examples: List[str] = Field(default_factory=list)

class GeneratedFix(BaseModel):
    suggested_replacement: str
    edit_comment: str
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Precedents used
    template_sources: List[str] = Field(default_factory=list)
    why_this_fix: str  # Explanation of changes

class FlaggedClause(BaseModel):
    """Complete analysis of one risky clause"""
    chunk_id: str
    original_text: str
    category: str
    
    risk_analysis: RiskAnalysis
    
    suggested_fix: Optional[GeneratedFix] = None
    
    langfuse_trace_id: Optional[str] = None
    analysis_timestamp: datetime = Field(default_factory=datetime.now)

class CompoundRisk(BaseModel):
    risk_type: str  # e.g., "Termination + Liability"
    description: str
    severity: Literal["Low", "Medium", "High", "Critical"]
    affected_clause_ids: List[str]
    mitigation_advice: str

class ContractAnalysisResult(BaseModel):
    document_metadata: DocumentMetadata
    
    flagged_clauses: List[FlaggedClause]
    total_clauses_analyzed: int
    total_risks_found: int
    
    compound_risks: List[CompoundRisk]
    executive_summary: str
    overall_risk_score: int = Field(ge=0, le=100)
    
    processing_time_seconds: float
    llm_calls_made: int
    cost_estimate_usd: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_metadata": {"filename": "contract.pdf"},
                "flagged_clauses": [],
                "total_clauses_analyzed": 45,
                "total_risks_found": 8,
                "compound_risks": [],
                "executive_summary": "Found 8 high-risk clauses...",
                "overall_risk_score": 72,
                "processing_time_seconds": 15.3,
                "llm_calls_made": 24,
                "cost_estimate_usd": 0.02
            }
        }

class CategoryDetection(BaseModel):
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    similarity_to_prototype: float
    zone: Literal["noise", "courtroom", "safe"]
    needs_agent_review: bool
    
    retrieved_prototypes: Optional[List[str]] = None
    retrieved_safe_examples: Optional[List[str]] = Field(default_factory=list)
    retrieved_risky_examples: Optional[List[str]] = Field(default_factory=list)
    decision_reasoning: str

class PessimistAnalysis(BaseModel):
    """Pessimist's initial analysis"""
    is_relevant: bool = Field(..., description="Is clause actually about target category?")
    relevance_reasoning: str = Field(..., description="Why relevant/irrelevant")
    risk_argument: str = Field(..., description="Worst-case risk analysis (if relevant)")
    key_concerns: List[str] = Field(default_factory=list, description="Specific risk points")

class OptimistAnalysis(BaseModel):
    defense_argument: str = Field(..., description="Why clause might be acceptable")
    industry_context: str = Field(..., description="Market standard context")
    mitigating_factors: List[str] = Field(default_factory=list, description="Points in favor")

class ArbiterVerdict(BaseModel):
    risk_score: int = Field(..., ge=0, le=100, description="0=safe, 100=critical")
    risk_level: Literal["Low", "Medium", "High", "Critical"]
    reasoning: str = Field(..., description="Synthesis of both arguments")
    key_factors: List[str] = Field(default_factory=list, description="Decision factors")

class ExtractedParameters(BaseModel):
    days_mentioned: Optional[int] = None
    months_mentioned: Optional[int] = None
    years_mentioned: Optional[int] = None
    amounts_mentioned: List[str] = Field(default_factory=list)
    
    has_written_notice: bool = False
    is_mutual: bool = False  
    requires_cause: bool = False
    has_cap: bool = False
    has_cure_period: bool = False
    
    raw_text_markers: Dict[str, bool] = Field(default_factory=dict)

class RiskAnalysis(BaseModel):
    chunk_id: str
    category: str
    
    is_relevant: bool
    
    pessimist_analysis: Optional[PessimistAnalysis] = None
    optimist_analysis: Optional[OptimistAnalysis] = None
    arbiter_verdict: Optional[ArbiterVerdict] = None
    
    extracted_parameters: Optional[ExtractedParameters] = None
    
    safe_precedents_used: List[str] = Field(default_factory=list)
    risky_precedents_used: List[str] = Field(default_factory=list)
    
    final_risk_score: int = Field(default=0, ge=0, le=100)
    final_risk_level: str = "Low"

class GeneratedFix(BaseModel):
    suggested_replacement: str = Field(..., description="Complete safe clause text")
    edit_comment: str = Field(..., description="Explanation of changes")
    key_changes: List[str] = Field(default_factory=list, description="Specific improvements")
    precedent_citations: List[str] = Field(default_factory=list, description="Templates used")


class CompoundRisk(BaseModel):
    risk_type: str = Field(..., description="Type of compound risk")
    severity: Literal["Low", "Medium", "High", "Critical"]
    description: str = Field(..., description="What makes this combination dangerous")
    affected_clause_ids: List[str] = Field(..., description="Which clauses create this risk")
    mitigation_advice: str = Field(..., description="How to address this risk")
    combined_risk_score: int = Field(..., ge=0, le=100, description="Aggregate risk level")