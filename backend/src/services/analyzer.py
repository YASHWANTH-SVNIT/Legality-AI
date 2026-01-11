from pathlib import Path
from typing import Dict, Any
import logging

from src.services.document_processor import DocumentProcessor
from src.rag.category_detector import CategoryDetector
from src.services.risk_analyzer.adversarial_analyzer import AdversarialAnalyzer
from src.services.fix_generator.fix_generator import FixGenerator
from src.services.compound_detector.compound_detector import CompoundRiskDetector

logger = logging.getLogger(__name__)

class ContractAnalyzer:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.detector = CategoryDetector()
        self.risk_analyzer = AdversarialAnalyzer()
        self.fix_generator = FixGenerator()
        self.compound_detector = CompoundRiskDetector()
        
        logger.info("✅ Contract Analyzer initialized")
    
    def analyze_contract(self, file_path: Path) -> Dict[str, Any]:
        logger.info(f"📄 Analyzing: {file_path.name}")
        
        # Stage 1: Extract
        doc = self.processor.process(file_path)
        
        # Stages 2-4: Analyze chunks
        risky_clauses = []
        risk_analyses = []
        
        for chunk in doc.chunks:
            detection = self.detector.detect_category(chunk)
            
            if not detection.needs_agent_review:
                continue
            
            analysis = self.risk_analyzer.analyze_risk(chunk, detection)
            
            if not analysis.is_relevant or analysis.final_risk_score < 50:
                continue
            
            risk_analyses.append(analysis)
            
            fix = self.fix_generator.generate_fix(
                chunk.text,
                detection.category,
                analysis
            )
            
            risky_clauses.append({
                "chunk_id": chunk.id,
                "category": detection.category,
                "original_text": chunk.text,
                "risk_score": analysis.final_risk_score,
                "risk_level": analysis.final_risk_level,
                "pessimist_analysis": analysis.pessimist_analysis.risk_argument if analysis.pessimist_analysis else "",
                "optimist_analysis": analysis.optimist_analysis.defense_argument if analysis.optimist_analysis else "",
                "arbiter_reasoning": analysis.arbiter_verdict.reasoning if analysis.arbiter_verdict else "",
                "suggested_fix": fix.suggested_replacement,
                "fix_comment": fix.edit_comment,
                "key_changes": fix.key_changes
            })
        
        # Stage 5: Compound risks
        compound_risks = self.compound_detector.detect_compound_risks(
            risk_analyses,
            doc.full_text
        )
        
        compound_list = [
            {
                "risk_type": cr.risk_type,
                "severity": cr.severity,
                "description": cr.description,
                "affected_clauses": cr.affected_clause_ids,
                "mitigation": cr.mitigation_advice,
                "risk_score": cr.combined_risk_score
            }
            for cr in compound_risks
        ]
        
        avg_risk = sum(c["risk_score"] for c in risky_clauses) / len(risky_clauses) if risky_clauses else 0
        overall_risk = "Critical" if avg_risk >= 75 else "High" if avg_risk >= 60 else "Medium" if avg_risk >= 40 else "Low"
        
        results = {
            "document": {
                "filename": file_path.name,
                "total_chunks": len(doc.chunks),
                "risky_clauses_found": len(risky_clauses)
            },
            "summary": {
                "overall_risk": overall_risk,
                "average_risk_score": round(avg_risk, 1),
                "compound_risks_found": len(compound_risks),
                "categories_flagged": list(set(c["category"] for c in risky_clauses))
            },
            "risky_clauses": risky_clauses,
            "compound_risks": compound_list
        }
        
        logger.info(f"✅ Analysis complete: {len(risky_clauses)} risky clauses")
        return results