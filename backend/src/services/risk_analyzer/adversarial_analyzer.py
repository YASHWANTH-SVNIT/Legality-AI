from typing import Dict, Any
import logging

from src.core.models import (
    SemanticChunk, 
    CategoryDetection, 
    RiskAnalysis,
    PessimistAnalysis,
    OptimistAnalysis,
    ArbiterVerdict
)
from src.core.llm_client import LLMClient
from src.services.risk_analyzer.parameter_extractor import ParameterExtractor
from src.services.risk_analyzer.prompts import *
from src.utils.text_utils import truncate_for_context
from langfuse import observe

logger = logging.getLogger(__name__)

class AdversarialAnalyzer:

    def __init__(self):
        self.llm = LLMClient()
        self.param_extractor = ParameterExtractor()
    
    @observe(name="Stage 3: Adversarial Analysis")
    def analyze_risk(
        self, 
        chunk: SemanticChunk, 
        detection: CategoryDetection
    ) -> RiskAnalysis:
        logger.info(f"🏛️ Analyzing {chunk.id} - {detection.category}")
        
        params = self.param_extractor.extract(chunk.text)
        
        # AGENT 1: Pessimist (Gatekeeper + Risk Finder)
        pessimist = self._run_pessimist(
            chunk.text, 
            detection.category,
            detection.retrieved_risky_examples,
            params
        )
        
        if not pessimist.is_relevant:
            logger.info(f"   ✋ Dismissed as not relevant to {detection.category}")
            return RiskAnalysis(
                chunk_id=chunk.id,
                category=detection.category,
                is_relevant=False,
                final_risk_score=0,
                final_risk_level="Low"
            )
        
        # AGENT 2: Optimist (Defense)
        optimist = self._run_optimist(
            chunk.text,
            pessimist.risk_argument,
            detection.retrieved_safe_examples,
            params
        )
        
        # AGENT 3: Arbiter (Judge)
        verdict = self._run_arbiter(
            chunk.text,
            detection.category,
            pessimist,
            optimist,
            detection.retrieved_safe_examples,
            detection.retrieved_risky_examples,
            params
        )
        
        risk_level = self._score_to_level(verdict.risk_score)
        
        logger.info(f"   ⚖️ Verdict: {verdict.risk_score}/100 ({risk_level})")
        
        return RiskAnalysis(
            chunk_id=chunk.id,
            category=detection.category,
            is_relevant=True,
            pessimist_analysis=pessimist,
            optimist_analysis=optimist,
            arbiter_verdict=verdict,
            extracted_parameters=params,
            safe_precedents_used=detection.retrieved_safe_examples[:3],
            risky_precedents_used=detection.retrieved_risky_examples[:3],
            final_risk_score=verdict.risk_score,
            final_risk_level=risk_level
        )
    
    def _run_pessimist(
        self, 
        text: str, 
        category: str,
        risky_precedents: list,
        params
    ) -> PessimistAnalysis:
        """Run pessimist agent"""
        
        precedent_text = "\n".join([
            f"- {p[:150]}..." for p in risky_precedents[:3]
        ]) if risky_precedents else "None available"
        
        param_summary = self._format_parameters(params)
        
        prompt = PESSIMIST_GATEKEEPER_PROMPT.format(
            category=category,
            clause_text=truncate_for_context(text, 400),
            risky_precedents=precedent_text,
            parameters=param_summary
        )
        
        try:
            result = self.llm.get_structured_completion(
                messages=[
                    {"role": "system", "content": PESSIMIST_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_model=PessimistAnalysis,
                model_type="smart"
            )
            return result
        except Exception as e:
            logger.error(f"Pessimist failed: {e}")
            return PessimistAnalysis(
                is_relevant=True,
                relevance_reasoning="Error in analysis",
                risk_argument="Manual review required"
            )
    
    def _run_optimist(
        self,
        text: str,
        pessimist_argument: str,
        safe_precedents: list,
        params
    ) -> OptimistAnalysis:
        
        precedent_text = "\n".join([
            f"- {p[:150]}..." for p in safe_precedents[:3]
        ]) if safe_precedents else "None available"
        
        param_summary = self._format_parameters(params)
        
        prompt = OPTIMIST_DEFENSE_PROMPT.format(
            clause_text=truncate_for_context(text, 400),
            pessimist_argument=truncate_for_context(pessimist_argument, 300),
            safe_precedents=precedent_text,
            parameters=param_summary
        )
        
        try:
            result = self.llm.get_structured_completion(
                messages=[
                    {"role": "system", "content": OPTIMIST_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_model=OptimistAnalysis,
                model_type="smart"
            )
            return result
        except Exception as e:
            logger.error(f"Optimist failed: {e}")
            return OptimistAnalysis(
                defense_argument="Standard practice in industry",
                industry_context="Common in similar agreements"
            )
    
    def _run_arbiter(
        self,
        text: str,
        category: str,
        pessimist: PessimistAnalysis,
        optimist: OptimistAnalysis,
        safe_precedents: list,
        risky_precedents: list,
        params
    ) -> ArbiterVerdict:
        
        # Summarize precedents
        safe_summary = f"Standard protection: {len(safe_precedents)} examples show mutual rights, notice periods"
        risky_summary = f"Risk patterns: {len(risky_precedents)} examples show unilateral control, no protections"
        
        prompt = ARBITER_VERDICT_PROMPT.format(
            category=category,
            clause_text=truncate_for_context(text, 400),
            pessimist_argument=truncate_for_context(pessimist.risk_argument, 300),
            pessimist_concerns=", ".join(pessimist.key_concerns[:3]) if pessimist.key_concerns else "None",
            optimist_argument=truncate_for_context(optimist.defense_argument, 300),
            optimist_factors=", ".join(optimist.mitigating_factors[:3]) if optimist.mitigating_factors else "None",
            safe_summary=safe_summary,
            risky_summary=risky_summary,
            parameters=self._format_parameters(params)
        )
        
        try:
            result = self.llm.get_structured_completion(
                messages=[
                    {"role": "system", "content": ARBITER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_model=ArbiterVerdict,
                model_type="smart"
            )
            
            result.risk_level = self._score_to_level(result.risk_score)
            
            return result
        except Exception as e:
            logger.error(f"Arbiter failed: {e}")
            return ArbiterVerdict(
                risk_score=50,
                risk_level="Medium",
                reasoning="Manual review required due to analysis error"
            )
    
    @staticmethod
    def _format_parameters(params) -> str:
        lines = []
        if params.days_mentioned:
            lines.append(f"- Notice period: {params.days_mentioned} days")
        if params.amounts_mentioned:
            lines.append(f"- Amounts: {', '.join(params.amounts_mentioned)}")
        if params.is_mutual:
            lines.append("- Mutual (either party)")
        else:
            lines.append("- Unilateral (one party only)")
        if params.has_written_notice:
            lines.append("- Written notice required")
        if params.requires_cause:
            lines.append("- Requires cause")
        if params.has_cap:
            lines.append("- Has liability cap")
        
        return "\n".join(lines) if lines else "No specific parameters extracted"
    
    @staticmethod
    def _score_to_level(score: int) -> str:
        if score >= 76:
            return "Critical"
        elif score >= 51:
            return "High"
        elif score >= 26:
            return "Medium"
        else:
            return "Low"