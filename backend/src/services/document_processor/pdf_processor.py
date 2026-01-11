import fitz  
import pdfplumber
from pathlib import Path
from typing import Tuple
import logging

from src.core.models import DocumentMetadata

logger = logging.getLogger(__name__)

class PDFProcessor:
    
    @staticmethod
    def extract_text(pdf_path: Path) -> Tuple[str, DocumentMetadata]:

        logger.info(f"📄 Processing: {pdf_path.name}")
        
        try:
            full_text = PDFProcessor._hybrid_extract(pdf_path)
            metadata = PDFProcessor._extract_metadata(pdf_path)
            return full_text, metadata
            
        except Exception as e:
            logger.error(f"❌ Hybrid extraction failed: {e}")
            return PDFProcessor._fallback_extract(pdf_path)
    
    @staticmethod
    def _hybrid_extract(pdf_path: Path) -> str:

        full_text = ""
        
        pymupdf_doc = fitz.open(pdf_path)
        pdfplumber_doc = pdfplumber.open(pdf_path)
        
        try:
            for page_num in range(len(pymupdf_doc)):
                pymupdf_text = pymupdf_doc[page_num].get_text()
                
                pdfplumber_page = pdfplumber_doc.pages[page_num]
                pdfplumber_text = pdfplumber_page.extract_text()
                
                if pdfplumber_text and len(pdfplumber_text) > len(pymupdf_text) * 0.9:
                    page_text = pdfplumber_text
                else:
                    page_text = pymupdf_text
                
                full_text += page_text + "\n\n"
                
        finally:
            pymupdf_doc.close()
            pdfplumber_doc.close()
        
        logger.debug(f"✅ Hybrid extraction: {len(full_text)} chars")
        return full_text
    
    @staticmethod
    def _fallback_extract(pdf_path: Path) -> Tuple[str, DocumentMetadata]:
        doc = fitz.open(pdf_path)
        full_text = ""
        
        for page in doc:
            full_text += page.get_text() + "\n\n"
        
        metadata = DocumentMetadata(
            filename=pdf_path.name,
            file_size=pdf_path.stat().st_size,
            page_count=len(doc)
        )
        
        doc.close()
        logger.warning("⚠️ Used fallback extraction")
        return full_text, metadata
    
    @staticmethod
    def _extract_metadata(pdf_path: Path) -> DocumentMetadata:
        doc = fitz.open(pdf_path)
        
        metadata = DocumentMetadata(
            filename=pdf_path.name,
            file_size=pdf_path.stat().st_size,
            page_count=len(doc)
        )
        
        pdf_metadata = doc.metadata
        if pdf_metadata.get('title'):
            title_lower = pdf_metadata['title'].lower()
            if 'nda' in title_lower or 'non-disclosure' in title_lower:
                metadata.contract_type = "NDA"
            elif 'service' in title_lower:
                metadata.contract_type = "Service Agreement"
            elif 'employment' in title_lower:
                metadata.contract_type = "Employment Contract"
        
        doc.close()
        return metadata