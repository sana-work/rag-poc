import json
import pickle
import logging
from typing import List, Dict, Any
from pathlib import Path
from config import settings
from retrieval.base import BaseRetriever
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class TfidfRetriever(BaseRetriever):
    def __init__(self):
        try:
            artifacts_dir = settings.DATA_DIR / "artifacts"
            
            with open(artifacts_dir / "tfidf.pkl", "rb") as f:
                self.vectorizer, self.tfidf_matrix = pickle.load(f)
                
            chunks_path = artifacts_dir / "chunks.jsonl"
            self.chunks = []
            with open(chunks_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self.chunks.append(json.loads(line))
                    
            logger.info(f"TfidfRetriever initialized with {len(self.chunks)} chunks.")
        except Exception as e:
            logger.error(f"Failed to initialize TfidfRetriever: {e}")
            raise e

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Get top K indices
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                chunk = self.chunks[idx].copy()
                chunk['score'] = float(similarities[idx])
                results.append(chunk)
                
        return results
