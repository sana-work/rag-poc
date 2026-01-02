import json
import logging
import re
from typing import List, Dict, Any, Set
from pathlib import Path
from config import settings
from llm.retrieval.base import BaseRetriever

logger = logging.getLogger(__name__)

class BruteRetriever(BaseRetriever):
    def __init__(self):
        try:
            chunks_path = settings.DATA_DIR / "artifacts" / "chunks.jsonl"
            self.chunks = []
            if chunks_path.exists():
                with open(chunks_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        self.chunks.append(json.loads(line))
            
            logger.info(f"BruteRetriever initialized with {len(self.chunks)} chunks.")
        except Exception as e:
            logger.error(f"Failed to initialize BruteRetriever: {e}")
            raise e

    def _tokenize(self, text: str) -> Set[str]:
        return set(re.findall(r'\w+', text.lower()))

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []
            
        scored_chunks = []
        for chunk in self.chunks:
            chunk_tokens = self._tokenize(chunk['text'])
            intersection = query_tokens.intersection(chunk_tokens)
            score = len(intersection) / len(query_tokens) # partial Jaccard-ish
            
            if score > 0:
                chunk_copy = chunk.copy()
                chunk_copy['score'] = score
                scored_chunks.append(chunk_copy)
                
        # Sort by score desc
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        return scored_chunks[:top_k]
