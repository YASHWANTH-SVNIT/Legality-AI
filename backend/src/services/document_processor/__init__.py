import time
from pathlib import Path
from typing import Tuple
import logging

from src.services.document_processor.pdf_processor import PDFProcessor
from src.services.document_processor.metadata_extractor import MetadataExtractor
from src.services.document_processor.definition_extractor import DefinitionExtractor
from src.services.document_processor.semantic_chunker import SemanticChunker
from src.core.models import ProcessedDocument
from src.utils.text_utils import clean_text

logger = logging.getLogger(__name__)

class DocumentProcessor:

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.metadata_extractor = MetadataExtractor()
        self.definition_extractor = DefinitionExtractor()
        self.semantic_chunker = SemanticChunker()
    
    def process(self, pdf_path: Path) -> ProcessedDocument:
        start_time = time.time()
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 STAGE 1: Processing {pdf_path.name}")
        logger.info(f"{'='*60}\n")
        
        # Step 1: Extract text from PDF
        full_text, base_metadata = self.pdf_processor.extract_text(pdf_path)
        full_text = clean_text(full_text)
        logger.info(f"✅ Step 1/4: Extracted {len(full_text)} characters")
        
        # Step 2: Extract metadata
        metadata = self.metadata_extractor.extract(full_text, base_metadata)
        logger.info(f"✅ Step 2/4: Metadata extracted")
        
        # Step 3: Extract definitions
        definitions = self.definition_extractor.extract(full_text)
        logger.info(f"✅ Step 3/4: Found {len(definitions)} definitions")
        
        # Step 4: Semantic chunking
        chunks = self.semantic_chunker.chunk_text(full_text)
        logger.info(f"✅ Step 4/4: Created {len(chunks)} semantic chunks")
        
        # Calculate statistics
        avg_chunk_length = sum(c.word_count for c in chunks) / len(chunks) if chunks else 0
        processing_time = time.time() - start_time
        
        result = ProcessedDocument(
            metadata=metadata,
            full_text=full_text,
            definitions=definitions,
            chunks=chunks,
            total_chunks=len(chunks),
            avg_chunk_length=avg_chunk_length,
            processing_time_seconds=round(processing_time, 2)
        )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ STAGE 1 COMPLETE")
        logger.info(f"   • Chunks: {len(chunks)}")
        logger.info(f"   • Avg length: {avg_chunk_length:.1f} words")
        logger.info(f"   • Time: {processing_time:.2f}s")
        logger.info(f"{'='*60}\n")
        
        return result

def process_document(pdf_path: Path) -> ProcessedDocument:
    """Process a single document through Stage 1"""
    processor = DocumentProcessor()
    return processor.process(pdf_path)