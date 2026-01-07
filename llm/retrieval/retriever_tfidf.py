import json
import pickle
import logging
from typing import List, Dict, Any
from config import settings
from llm.retrieval.base import BaseRetriever
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class TfidfRetriever(BaseRetriever):
    def __init__(self, pkl_path: Any = None, chunks_path: Any = None):
        try:
            artifacts_dir = settings.DATA_DIR / "artifacts"
            
            # Default paths if not provided
            if not pkl_path:
                pkl_path = artifacts_dir / "tfidf.pkl"
            if not chunks_path:
                chunks_path = artifacts_dir / "chunks.jsonl"
            
            with open(pkl_path, "rb") as f:
                self.vectorizer, self.tfidf_matrix = pickle.load(f)
                
            self.chunks = []
            with open(chunks_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self.chunks.append(json.loads(line))
                    
            logger.info(f"TfidfRetriever initialized from {pkl_path}")
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
