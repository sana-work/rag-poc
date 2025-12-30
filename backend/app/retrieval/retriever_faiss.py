import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from app.config import settings
from app.retrieval.base import BaseRetriever

logger = logging.getLogger(__name__)

class FaissRetriever(BaseRetriever):
    def __init__(self):
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            index_path = settings.DATA_DIR / "artifacts" / "faiss.index"
            self.index = faiss.read_index(str(index_path))
            
            chunks_path = settings.DATA_DIR / "artifacts" / "chunks.jsonl"
            self.chunks = []
            with open(chunks_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self.chunks.append(json.loads(line))
                    
            logger.info(f"FaissRetriever initialized with {len(self.chunks)} chunks.")
        except Exception as e:
            logger.error(f"Failed to initialize FaissRetriever: {e}")
            raise e

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_vector = self.model.encode([query])
        
        # Search
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks) and idx >= 0:
                chunk = self.chunks[idx].copy()
                chunk['score'] = float(distances[0][i])
                results.append(chunk)
                
        return results
