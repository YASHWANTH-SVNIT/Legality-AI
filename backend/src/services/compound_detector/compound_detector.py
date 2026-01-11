from typing import List
import logging
from pydantic import BaseModel, Field

from src.core.models import RiskAnalysis, CompoundRisk
from src.core.llm_client import LLMClient
from langfuse import observe

logger = logging.getLogger(__name__)


class CompoundRiskDetector:

    DANGEROUS_PATTERNS = [
        {
            "categories": ["Unilateral Termination", "Unlimited Liability"],
            "risk_type": "Termination + Unlimited Liability",
            "description": "Vendor can terminate at will while maintaining unlimited liability claims"
        },
        {
            "categories": ["Unilateral Termination", "Non-Compete"],
            "risk_type": "Termination + Non-Compete Lock-in",
            "description": "Vendor can terminate while non-compete prevents working elsewhere"
        },
        {
            "categories": ["Unlimited Liability", "Non-Compete"],
            "risk_type": "Unlimited Liability + Restricted Exit",
            "description": "Unlimited exposure with no ability to work for competitors"
        }
    ]
    
    def __init__(self):
        self.llm = LLMClient()
    
    @observe(name="Stage 5: Compound Risk Detection")
    def detect_compound_risks(
        self,
        risk_analyses: List[RiskAnalysis],
        document_text: str = ""
    ) -> List[CompoundRisk]:

        if len(risk_analyses) < 2:
            logger.info("Only 1 risky clause - no compound risks possible")
            return []
        
        logger.info(f"🔍 Checking {len(risk_analyses)} clauses for compound risks")
        
        compound_risks = []
        
        # Step 1: Pattern-based detection
        pattern_risks = self._detect_pattern_risks(risk_analyses)
        compound_risks.extend(pattern_risks)
        
        # Step 2: Severity escalation (multiple high risks in same category)
        severity_risks = self._detect_severity_escalation(risk_analyses)
        compound_risks.extend(severity_risks)
        
        # Step 3: LLM synthesis (catch non-obvious combinations)
        if len(risk_analyses) >= 2:
            llm_risks = self._llm_compound_analysis(risk_analyses)
            compound_risks.extend(llm_risks)
        
        unique_risks = self._deduplicate_risks(compound_risks)
        
        logger.info(f"✅ Found {len(unique_risks)} compound risks")
        return unique_risks
    
    def _detect_pattern_risks(
        self,
        analyses: List[RiskAnalysis]
    ) -> List[CompoundRisk]:

        risks = []
        categories_present = {a.category for a in analyses if a.is_relevant}
        
        for pattern in self.DANGEROUS_PATTERNS:
            pattern_categories = set(pattern["categories"])
            
            if pattern_categories.issubset(categories_present):
                affected = [
                    a.chunk_id for a in analyses 
                    if a.category in pattern_categories and a.is_relevant
                ]
                
                involved_scores = [
                    a.final_risk_score for a in analyses 
                    if a.chunk_id in affected
                ]
                combined_score = int(sum(involved_scores) / len(involved_scores)) if involved_scores else 50
                
                combined_score = min(100, combined_score + 15)
                
                risk = CompoundRisk(
                    risk_type=pattern["risk_type"],
                    severity=self._score_to_severity(combined_score),
                    description=pattern["description"] + ". This creates a power imbalance where one party controls both contract duration and financial exposure.",
                    affected_clause_ids=affected,
                    mitigation_advice=f"Negotiate to make both clauses mutual and balanced. If one party can terminate unilaterally, ensure liability is capped and reasonable.",
                    combined_risk_score=combined_score
                )
                
                risks.append(risk)
                logger.info(f"   🚨 Pattern detected: {pattern['risk_type']}")
        
        return risks
    
    def _detect_severity_escalation(
        self,
        analyses: List[RiskAnalysis]
    ) -> List[CompoundRisk]:
        risks = []
        
        by_category = {}
        for a in analyses:
            if a.is_relevant and a.final_risk_score >= 70:
                if a.category not in by_category:
                    by_category[a.category] = []
                by_category[a.category].append(a)
        
        for category, clause_list in by_category.items():
            if len(clause_list) >= 2:
                avg_score = int(sum(c.final_risk_score for c in clause_list) / len(clause_list))
                
                risk = CompoundRisk(
                    risk_type=f"Multiple {category} Risks",
                    severity=self._score_to_severity(min(100, avg_score + 10)),
                    description=f"Contract contains {len(clause_list)} separate high-risk {category} clauses, creating systemic vulnerability.",
                    affected_clause_ids=[c.chunk_id for c in clause_list],
                    mitigation_advice=f"Address all {category} clauses holistically to ensure consistent protections throughout the contract.",
                    combined_risk_score=min(100, avg_score + 10)
                )
                
                risks.append(risk)
                logger.info(f"   ⚠️ Severity escalation: {len(clause_list)}x {category}")
        
        return risks
    
    def _llm_compound_analysis(
        self,
        analyses: List[RiskAnalysis]
    ) -> List[CompoundRisk]:

        clause_summaries = []
        for i, analysis in enumerate(analyses, 1):
            if analysis.is_relevant and analysis.final_risk_score >= 50:
                clause_summaries.append(
                    f"{i}. [{analysis.category}] Risk: {analysis.final_risk_score}/100\n"
                    f"   Issue: {analysis.arbiter_verdict.reasoning[:150] if analysis.arbiter_verdict else 'See analysis'}..."
                )
        
        if len(clause_summaries) < 2:
            return []
        
        prompt = f"""
                    FLAGGED CLAUSES:
                    {chr(10).join(clause_summaries)}

                    TASK: Identify COMPOUND RISKS where these clauses combine to create bigger problems.

                    CRITICAL: Respond with valid JSON matching this EXACT structure:
                    {{
                    "risks": [
                        {{
                        "risk_type": "Brief name of compound risk",
                        "severity": "Critical",
                        "description": "Why this combination is dangerous",
                        "affected_clause_ids": ["chunk_005", "chunk_006"],
                        "mitigation_advice": "How to fix it",
                        "combined_risk_score": 90
                        }}
                    ]
                    }}

                    If no compound risks exist, return: {{"risks": []}}

                    Only report GENUINE compound risks (0-2 maximum).
                    """
        
        try:
            class CompoundRiskList(BaseModel):
                risks: List[CompoundRisk] = Field(default_factory=list)
            
            result = self.llm.get_structured_completion(
                messages=[
                    {"role": "system", "content": "You are a senior contract attorney identifying systemic risks."},
                    {"role": "user", "content": prompt}
                ],
                response_model=CompoundRiskList,
                model_type="smart"
            )
            
            return result.risks
            
        except Exception as e:
            logger.warning(f"LLM compound analysis failed: {e}")
            return []
    
    def _deduplicate_risks(
        self,
        risks: List[CompoundRisk]
    ) -> List[CompoundRisk]:
        seen = set()
        unique = []
        
        for risk in risks:
            key = (risk.risk_type, tuple(sorted(risk.affected_clause_ids)))
            if key not in seen:
                seen.add(key)
                unique.append(risk)
        
        return unique
    
    @staticmethod
    def _score_to_severity(score: int) -> str:
        """Convert score to severity level"""
        if score >= 85:
            return "Critical"
        elif score >= 70:
            return "High"
        elif score >= 50:
            return "Medium"
        else:
            return "Low"