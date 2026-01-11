import re
from typing import List, Optional
import logging

from src.core.models import DocumentMetadata
from src.config.settings import DocumentConfig

logger = logging.getLogger(__name__)

class MetadataExtractor:
    @staticmethod
    def extract(full_text: str, base_metadata: DocumentMetadata) -> DocumentMetadata:
        logger.info("🔍 Extracting metadata...")
        
        # Extract parties
        parties = MetadataExtractor._extract_parties(full_text)
        if parties:
            base_metadata.parties = parties
        
        # Extract effective date
        effective_date = MetadataExtractor._extract_effective_date(full_text)
        if effective_date:
            base_metadata.effective_date = effective_date
        
        # Extract monetary amounts
        amounts = MetadataExtractor._extract_amounts(full_text)
        if amounts:
            base_metadata.mentioned_amounts = amounts[:5]  # Top 5
        
        # Classify contract type if not already set
        if not base_metadata.contract_type:
            base_metadata.contract_type = MetadataExtractor._classify_contract_type(full_text)
        
        logger.info(f"✅ Metadata extracted: {base_metadata.contract_type}, {len(parties or [])} parties")
        return base_metadata
    
    @staticmethod
    def _extract_parties(text: str) -> Optional[List[str]]:
        header = text[:2000]
        
        patterns = [
            r"(?:between|by and between)\s+([A-Z][^,\n]+?)\s+(?:and|&)\s+([A-Z][^,\n]+?)(?:\s*(?:,|\(|dated))",
            r"entered into by\s+([A-Z][^,\n]+?)\s+and\s+([A-Z][^,\n]+?)(?:\s*(?:,|\())",
            r"(?:^|\n)([A-Z][A-Za-z\s&]+(?:Inc|LLC|Corp|Ltd|Corporation))[^\n]{0,50}(?:\n|$)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, header, re.MULTILINE)
            if matches:
                if isinstance(matches[0], tuple):
                    parties = [m.strip() for match in matches[:2] for m in match]
                else:
                    parties = [m.strip() for m in matches[:2]]
                
                parties = [p for p in parties if len(p) > 3 and len(p) < 100]
                if len(parties) >= 2:
                    return parties[:2]
        
        return None
    
    @staticmethod
    def _extract_effective_date(text: str) -> Optional[str]:
        header = text[:2000]
        
        patterns = [
            r"effective\s+(?:date|as of)[:\s]+([^\n]+)",
            r"dated\s+(?:as of\s+)?([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
            r"(?:this|entered into on)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, header, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                date_str = re.sub(r'[^\w\s,]', '', date_str).strip()
                if 3 < len(date_str) < 50:
                    return date_str
        
        return None
    
    @staticmethod
    def _extract_amounts(text: str) -> List[str]:
        pattern = r'\$\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand|USD|dollars))?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        unique_amounts = list(set(matches))
        return unique_amounts
    
    @staticmethod
    def _classify_contract_type(text: str) -> str:
        """Classify contract type from content"""
        text_lower = text[:3000].lower()  
        
        if any(term in text_lower for term in ['non-disclosure', 'nda', 'confidential information']):
            return "NDA"
        elif any(term in text_lower for term in ['service agreement', 'statement of work', 'sow']):
            return "Service Agreement"
        elif any(term in text_lower for term in ['employment agreement', 'offer letter', 'employee']):
            return "Employment Contract"
        elif any(term in text_lower for term in ['master service', 'msa']):
            return "Master Service Agreement"
        elif any(term in text_lower for term in ['purchase order', 'sales agreement']):
            return "Purchase Agreement"
        else:
            return "General Contract"