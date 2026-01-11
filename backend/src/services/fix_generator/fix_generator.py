from typing import List, Dict
import logging

from src.core.models import RiskAnalysis, ExtractedParameters
from src.core.llm_client import LLMClient
from src.rag import VectorStore
from pydantic import BaseModel, Field
from langfuse import observe

logger = logging.getLogger(__name__)

class GeneratedFix(BaseModel):
    suggested_replacement: str = Field(..., description="Complete safe clause text")
    edit_comment: str = Field(..., description="Explanation of changes (max 50 words)")
    key_changes: List[str] = Field(default_factory=list, description="Specific improvements made")
    precedent_citations: List[str] = Field(default_factory=list, description="Safe templates used")

class FixGenerator:
    def __init__(self):
        self.llm = LLMClient()
        self.vector_store = VectorStore()
    
    @observe(name="Stage 4: Fix Generation")
    def generate_fix(
        self,
        risky_text: str,
        category: str,
        risk_analysis: RiskAnalysis
    ) -> GeneratedFix:

        logger.info(f"📝 Generating fix for {category}")
        
        # Step 1: Retrieve safe templates
        safe_templates = self._retrieve_safe_templates(
            risky_text, 
            category,
            risk_analysis.extracted_parameters
        )
        
        # Step 2: Generate fix using templates as guidance
        fix = self._generate_with_templates(
            risky_text,
            category,
            risk_analysis,
            safe_templates
        )
        
        fix.precedent_citations = [t['text'][:100] + "..." for t in safe_templates[:2]]
        
        logger.info(f"✅ Fix generated ({len(fix.suggested_replacement)} chars)")
        return fix
    
    def _retrieve_safe_templates(
        self,
        risky_text: str,
        category: str,
        parameters: ExtractedParameters
    ) -> List[Dict]:
 
        templates = self.vector_store.query_category(
            text=risky_text,
            category=category,
            risk_level=None,  
            k=10  
        )
        
        safe_only = [t for t in templates if t['metadata'].get('risk_level') == 'safe']
        
        if parameters and safe_only:
            scored_templates = []
            for template in safe_only:
                score = template['similarity']
                
                template_text = template['text'].lower()
                
                if parameters.days_mentioned and 'days' in template_text:
                    score *= 1.2
                
                if parameters.is_mutual and 'either party' in template_text:
                    score *= 1.3
                
                if parameters.has_cap and ('limited' in template_text or 'cap' in template_text):
                    score *= 1.2
                
                scored_templates.append((score, template))
            
            scored_templates.sort(key=lambda x: x[0], reverse=True)
            safe_only = [t[1] for t in scored_templates]
        
        return safe_only[:5]  
    
    def _generate_with_templates(
        self,
        risky_text: str,
        category: str,
        risk_analysis: RiskAnalysis,
        templates: List[Dict]
    ) -> GeneratedFix:

        template_examples = "\n\n".join([
            f"Example {i+1} (Similarity: {t['similarity']:.0%}):\n{t['text']}"
            for i, t in enumerate(templates[:3])
        ]) if templates else "No templates available - generate from scratch."
        
        risk_summary = f"""
Risk Score: {risk_analysis.final_risk_score}/100 ({risk_analysis.final_risk_level})
Key Issues: {risk_analysis.arbiter_verdict.reasoning[:200] if risk_analysis.arbiter_verdict else 'See analysis'}
"""
        
        prompt = f"""
You are an expert contract attorney drafting safe, balanced legal language.

TASK: Rewrite this risky {category} clause to be fair, mutual, and protective.

RISKY CLAUSE:
"{risky_text}"

IDENTIFIED RISKS:
{risk_summary}

SAFE TEMPLATES FROM DATABASE (use these as guidance):
{template_examples}

REQUIREMENTS:
1. **Fix the specific risks identified** (unilateral → mutual, unlimited → capped, etc.)
2. **Maintain similar length** (~{len(risky_text.split())} words)
3. **Use professional legal language** (formal but clear)
4. **Include specific protections**:
   - For Termination: notice period (30-90 days), written notice, mutual rights
   - For Liability: clear caps (e.g., "fees paid in 12 months"), exceptions only for fraud/gross negligence
   - For Non-Compete: reasonable scope (time/geography), carve-outs for general skills

5. **Edit comment**: Explain changes in 1-2 sentences (max 50 words)
6. **Key changes**: List 2-3 specific improvements (e.g., "Added 60-day notice period")

Generate a complete, copy-pasteable clause that a lawyer can insert directly into the contract.
"""
        
        try:
            fix = self.llm.get_structured_completion(
                messages=[
                    {"role": "system", "content": "You are a senior contract attorney drafting protective legal language."},
                    {"role": "user", "content": prompt}
                ],
                response_model=GeneratedFix,
                model_type="smart",
                temperature=0.3  
            )
            
            return fix
            
        except Exception as e:
            logger.error(f"Fix generation failed: {e}")
            return GeneratedFix(
                suggested_replacement=templates[0]['text'] if templates else risky_text,
                edit_comment="Manual drafting recommended due to generation error.",
                key_changes=["Review and revise manually"]
            )