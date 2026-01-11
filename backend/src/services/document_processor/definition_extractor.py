import re
from typing import List, Dict
import logging

from src.core.models import Definition

logger = logging.getLogger(__name__)

class DefinitionExtractor:

    @staticmethod
    def extract(full_text: str) -> List[Definition]:

        logger.info("📖 Extracting definitions...")
        
        definitions = []
        
        # Pattern 1: "Term" means/shall mean definition
        pattern1 = r'"([^"]{3,50})"\s+(?:means?|shall mean|refers? to|is defined as)\s+([^.;]+[.;])'
        matches1 = re.finditer(pattern1, full_text, re.IGNORECASE)
        
        for match in matches1:
            term = match.group(1).strip()
            definition_text = match.group(2).strip()
            
            context = full_text[max(0, match.start()-100):match.start()]
            section_match = re.search(r'(\d+\.\d+)', context)
            section = section_match.group(1) if section_match else None
            
            definitions.append(Definition(
                term=term,
                definition=definition_text,
                section=section
            ))
        
        # Pattern 2: As used herein, "Term" means...
        pattern2 = r'As used (?:herein|in this Agreement),\s+"([^"]{3,50})"\s+(?:means?|refers? to)\s+([^.;]+[.;])'
        matches2 = re.finditer(pattern2, full_text, re.IGNORECASE)
        
        for match in matches2:
            term = match.group(1).strip()
            definition_text = match.group(2).strip()
            
            definitions.append(Definition(
                term=term,
                definition=definition_text
            ))
        
        seen_terms = set()
        unique_definitions = []
        for defn in definitions:
            if defn.term.lower() not in seen_terms:
                seen_terms.add(defn.term.lower())
                unique_definitions.append(defn)
        
        logger.info(f"✅ Found {len(unique_definitions)} definitions")
        return unique_definitions
    
    @staticmethod
    def get_definition_dict(definitions: List[Definition]) -> Dict[str, str]:
        """Convert to simple dict for quick lookup"""
        return {defn.term.lower(): defn.definition for defn in definitions}