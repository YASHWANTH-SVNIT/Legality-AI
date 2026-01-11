from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        logger.info(f"✅ Loaded embedding model: {model_name}")
    
    def embed_text(self, text: str) -> np.ndarray:
        return self.model.encode(text, show_progress_bar=False)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts, show_progress_bar=False, batch_size=32)
    
    @staticmethod
    def calculate_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        if emb1.ndim == 1:
            emb1 = emb1.reshape(1, -1)
        if emb2.ndim == 1:
            emb2 = emb2.reshape(1, -1)
        return float(cosine_similarity(emb1, emb2)[0][0])