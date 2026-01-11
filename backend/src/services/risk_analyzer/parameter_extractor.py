import re
import logging

from src.core.models import ExtractedParameters
from src.config.settings import ParameterConfig

logger = logging.getLogger(__name__)

class ParameterExtractor:

    @staticmethod
    def extract(text: str) -> ExtractedParameters:
        text_lower = text.lower()
        
        params = ExtractedParameters()
        
        days_match = re.search(ParameterConfig.PATTERNS["days"], text, re.IGNORECASE)
        if days_match:
            params.days_mentioned = int(days_match.group(1))
        
        months_match = re.search(ParameterConfig.PATTERNS["months"], text, re.IGNORECASE)
        if months_match:
            params.months_mentioned = int(months_match.group(1))
        
        years_match = re.search(ParameterConfig.PATTERNS["years"], text, re.IGNORECASE)
        if years_match:
            params.years_mentioned = int(years_match.group(1))
        
        amounts = re.findall(ParameterConfig.PATTERNS["amount"], text)
        params.amounts_mentioned = amounts
        
        params.has_written_notice = bool(re.search(
            ParameterConfig.PATTERNS["written_notice"], 
            text, 
            re.IGNORECASE
        ))
        
        params.is_mutual = bool(re.search(
            ParameterConfig.PATTERNS["party_symmetry"], 
            text, 
            re.IGNORECASE
        ))
        
        params.requires_cause = bool(re.search(
            ParameterConfig.PATTERNS["for_cause"], 
            text, 
            re.IGNORECASE
        ))
        
        cap_indicators = ["limited to", "shall not exceed", "maximum", "cap"]
        params.has_cap = any(indicator in text_lower for indicator in cap_indicators)
        
        cure_indicators = ["cure", "remedy", "correct the breach"]
        params.has_cure_period = any(indicator in text_lower for indicator in cure_indicators)
        
        params.raw_text_markers = {
            "contains_unilateral": "company may" in text_lower or "vendor may" in text_lower,
            "contains_either_party": "either party" in text_lower,
            "contains_without_cause": "without cause" in text_lower,
            "contains_immediately": "immediately" in text_lower,
            "contains_unlimited": "unlimited" in text_lower or "all claims" in text_lower,
        }
        
        return params