import logging
import json
import faiss
import numpy as np
from typing import List, Dict
from pathlib import Path
from app.embeddings.vertex_embedder import VertexEmbedder
from app.retrieval.base import BaseRetriever

logger = logging.getLogger(__name__)

class FaissVertexRetriever(BaseRetriever):
    def __init__(self, index_path: Path, chunks_path: Path):
        self.index_path = index_path
        self.chunks_path = chunks_path
        self.index = None
        self.chunks = []
        self.embedder = VertexEmbedder()
        self._load_resources()

    def _load_resources(self):
        if not self.index_path.exists() or not self.chunks_path.exists():
            raise FileNotFoundError("FAISS index or chunks file not found.")

        logger.info(f"Loading FAISS index from {self.index_path}")
        self.index = faiss.read_index(str(self.index_path))
        
        logger.info(f"Loading chunks from {self.chunks_path}")
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            for line in f:
                self.chunks.append(json.loads(line))
        
        if self.index.ntotal != len(self.chunks):
            logger.warning(f"Index size ({self.index.ntotal}) does not match chunks size ({len(self.chunks)})")

    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        if not self.index:
            return []
            
        # Embed query using Vertex
        try:
            # We treat query as a singleton list
            query_embedding = self.embedder.embed_query(query)
            
            # Normalize for Cosine Similarity
            q_emb_np = np.array([query_embedding]).astype('float32')
            faiss.normalize_L2(q_emb_np)
            
            # Search
            scores, indices = self.index.search(q_emb_np, k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self.chunks):
                    continue
                
                chunk = self.chunks[idx]
                # Inject score for debugging/ranking display
                chunk['score'] = float(score)
                results.append(chunk)
                
            return results
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []
