import re
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

from src.core.models import SemanticChunk
from src.config.settings import ChunkingConfig

logger = logging.getLogger(__name__)

class SemanticChunker:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info(f"✅ Loaded embedding model: all-MiniLM-L6-v2")
    
    def chunk_text(self, full_text: str) -> List[SemanticChunk]:

        logger.info("🔪 Starting semantic chunking...")
        
        # Step 1: Split into sentences
        sentences = self._split_sentences(full_text)
        logger.debug(f"   Split into {len(sentences)} sentences")
        
        if len(sentences) < 2:
            return [self._create_chunk(full_text, 0, len(full_text), "chunk_001")]
        
        # Step 2: Embed sentences
        embeddings = self.model.encode(sentences, show_progress_bar=False)
        logger.debug(f"   Generated embeddings: {embeddings.shape}")
        
        # Step 3: Find semantic breakpoints
        breakpoints = self._find_breakpoints(embeddings, sentences)
        logger.debug(f"   Found {len(breakpoints)} breakpoints")
        
        # Step 4: Create chunks from breakpoints
        chunks = self._create_chunks_from_breakpoints(
            full_text, sentences, breakpoints
        )
        
        logger.info(f"✅ Created {len(chunks)} semantic chunks")
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:

        text = re.sub(r'\b([A-Z][a-z]?)\.\s', r'\1<PERIOD> ', text) 
        text = re.sub(r'\b(Inc|LLC|Corp|Ltd)\.\s', r'\1<PERIOD> ', text)
        
        sentences = re.split(r'[.!?]+\s+', text)
        
        sentences = [s.replace('<PERIOD>', '.') for s in sentences]
        
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        return sentences
    
    def _find_breakpoints(
        self, 
        embeddings: np.ndarray, 
        sentences: List[str]
    ) -> List[int]:

        similarities = []
        
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity(
                embeddings[i].reshape(1, -1),
                embeddings[i+1].reshape(1, -1)
            )[0][0]
            similarities.append(sim)
        
        if not similarities:
            return []
        
        threshold = np.percentile(similarities, ChunkingConfig.SIMILARITY_THRESHOLD * 100)
        
        breakpoints = [0] 
        for i, sim in enumerate(similarities):
            if sim < threshold:
                breakpoints.append(i + 1)
        
        if breakpoints[-1] != len(sentences):
            breakpoints.append(len(sentences))
        
        return breakpoints
    
    def _create_chunks_from_breakpoints(
        self,
        full_text: str,
        sentences: List[str],
        breakpoints: List[int]
    ) -> List[SemanticChunk]:

        chunks = []
        
        for i in range(len(breakpoints) - 1):
            start_idx = breakpoints[i]
            end_idx = breakpoints[i + 1]
            
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_text = ' '.join(chunk_sentences)
            
            if len(chunk_text) < ChunkingConfig.MIN_CHUNK_LENGTH:
                continue
            
            if len(chunk_text) > ChunkingConfig.MAX_CHUNK_LENGTH:
                chunk_text = chunk_text[:ChunkingConfig.MAX_CHUNK_LENGTH]
            
            start_char = full_text.find(chunk_sentences[0])
            if start_char == -1:
                start_char = 0
            end_char = start_char + len(chunk_text)
            
            preceding = full_text[max(0, start_char-50):start_char].strip()
            following = full_text[end_char:end_char+50].strip()
            
            chunk = SemanticChunk(
                id=f"chunk_{i+1:03d}",
                text=chunk_text.strip(),
                start_char=start_char,
                end_char=end_char,
                word_count=len(chunk_text.split()),
                preceding_text=preceding if preceding else None,
                following_text=following if following else None
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(
        self, 
        text: str, 
        start: int, 
        end: int, 
        chunk_id: str
    ) -> SemanticChunk:
        return SemanticChunk(
            id=chunk_id,
            text=text[start:end].strip(),
            start_char=start,
            end_char=end,
            word_count=len(text[start:end].split())
        )