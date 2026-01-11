from typing import Tuple, Optional
import logging

from src.core.models import SemanticChunk, CategoryDetection
from src.config.settings import RAGThresholds
from src.rag.vector_store import VectorStore
from langfuse import observe

logger = logging.getLogger(__name__)

class CategoryDetector:
    
    def __init__(self):
        self.vector_store = VectorStore()
        logger.info("✅ CategoryDetector initialized")
    
    @observe(name="Stage 2: Category Detection")
    def detect_category(self, chunk: SemanticChunk) -> CategoryDetection:
        results = self.vector_store.query_prototypes(chunk.text, k=1)
        
        if not results:
            return CategoryDetection(
                category="Unknown",
                confidence=0.0,
                similarity_to_prototype=0.0,
                zone="noise",
                needs_agent_review=False,
                retrieved_safe_examples=[],
                retrieved_risky_examples=[],
                decision_reasoning="No category match"
            )
        
        result = results[0]
        category = result['category']
        similarity = result['similarity']
        
        zone, needs_review, reasoning = self._apply_zone_logic(
            similarity, category, chunk.text
        )
        
        safe_examples = []
        risky_examples = []
        
        if needs_review:
            safe_examples = self._retrieve_examples(chunk.text, category, "safe")
            risky_examples = self._retrieve_examples(chunk.text, category, "risky")
        
        return CategoryDetection(
            category=category,
            confidence=similarity,
            similarity_to_prototype=similarity,
            zone=zone,
            needs_agent_review=needs_review,
            retrieved_safe_examples=safe_examples,
            retrieved_risky_examples=risky_examples,
            decision_reasoning=reasoning
        )
    
    def _apply_zone_logic(
        self, 
        similarity: float, 
        category: str,
        text: str
    ) -> Tuple[str, bool, str]:

        if similarity < RAGThresholds.NOISE_THRESHOLD:
            return (
                "noise",
                False,
                f"Similarity {similarity:.2%} below noise threshold. "
                f"Not related to target categories."
            )
        
        if similarity >= RAGThresholds.SAFE_THRESHOLD:
            safe_matches = self.vector_store.query_category(
                text, category, risk_level="safe", k=1
            )
            
            if safe_matches and safe_matches[0]['similarity'] > 0.90:
                return (
                    "safe",
                    False,
                    f"High similarity to {category} prototype ({similarity:.2%}) "
                    f"and matches safe standard ({safe_matches[0]['similarity']:.2%})."
                )
            else:
                return (
                    "courtroom",
                    True,
                    f"High category similarity ({similarity:.2%}) but deviates "
                    f"from safe standards. Requires agent review."
                )
        
        return (
            "courtroom",
            True,
            f"Moderate similarity to {category} ({similarity:.2%}). "
            f"Falls in grey zone - requires agent analysis."
        )
    
    def _retrieve_examples(
        self, 
        text: str, 
        category: str, 
        risk_level: str
    ) -> list[str]:
        results = self.vector_store.query_category(
            text, category, risk_level=risk_level, k=3
        )
        return [r['text'] for r in results]