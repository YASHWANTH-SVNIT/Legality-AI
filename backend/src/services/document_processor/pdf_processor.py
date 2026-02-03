import fitz  
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from pathlib import Path
from typing import Tuple
import logging
import os
import io

from src.core.models import DocumentMetadata

logger = logging.getLogger(__name__)

# Configure Tesseract path from env or default
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
POPPLER_PATH = os.getenv("POPPLER_PATH", r"C:\Program Files\poppler-25.12.0\Library\bin")

# Set the tesseract command
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

class PDFProcessor:
    
    @staticmethod
    def extract_text(pdf_path: Path) -> Tuple[str, DocumentMetadata]:

        logger.info(f"📄 Processing: {pdf_path.name}")
        
        try:
            # Step 1: Try Text Extraction
            full_text = PDFProcessor._hybrid_extract(pdf_path)
            
            # Step 2: Quality Check (If extracted text is too short, assume scanned)
            if len(full_text.strip()) < 100:  
                logger.info("🔍 Detect scanned document (text < 100 chars). Switching to OCR...")
                full_text = PDFProcessor._ocr_extract(pdf_path)
                
            metadata = PDFProcessor._extract_metadata(pdf_path)
            return full_text, metadata
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return PDFProcessor._fallback_extract(pdf_path)
    
    @staticmethod
    def _hybrid_extract(pdf_path: Path) -> str:

        full_text = ""
        
        pymupdf_doc = fitz.open(pdf_path)
        pdfplumber_doc = pdfplumber.open(pdf_path)
        
        try:
            for page_num in range(len(pymupdf_doc)):
                pymupdf_text = pymupdf_doc[page_num].get_text()
                
                # Check if page exists in plumber
                if page_num < len(pdfplumber_doc.pages):
                    pdfplumber_page = pdfplumber_doc.pages[page_num]
                    pdfplumber_text = pdfplumber_page.extract_text()
                else:
                    pdfplumber_text = ""
                
                # Use plumber if it got more text (better at tables), else fitz
                if pdfplumber_text and len(pdfplumber_text) > len(pymupdf_text) * 0.9:
                    page_text = pdfplumber_text
                else:
                    page_text = pymupdf_text
                
                full_text += page_text + "\n\n"
                
        finally:
            pymupdf_doc.close()
            pdfplumber_doc.close()
        
        logger.debug(f"✅ Text extraction result: {len(full_text)} chars")
        return full_text

    @staticmethod
    def _ocr_extract(pdf_path: Path) -> str:
        """extract text from scanned PDF using OCR"""
        full_text = ""
        
        try:
            # Check poppler path explicitly
            poppler_bin = POPPLER_PATH
            if not os.path.exists(poppler_bin):
                 logger.warning(f"⚠️ Poppler not found at {poppler_bin}. OCR might fail.")

            # Convert PDF pages to images
            images = convert_from_path(pdf_path, poppler_path=poppler_bin)
            
            total_pages = len(images)
            logger.info(f"📷 OCR Processing {total_pages} pages...")
            
            for i, image in enumerate(images):
                # Basic preprocessing can be added here (e.g., contrast)
                text = pytesseract.image_to_string(image)
                full_text += text + "\n\n"
                logger.debug(f"   - Page {i+1}/{total_pages} OCR complete")
                
            return full_text
            
        except Exception as e:
            logger.error(f"❌ OCR Extraction Native Failed: {e}")
            return "OCR FAILED: Could not extract text from this document."

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