from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a given query.
        Returns a list of dicts with keys: 'chunkId', 'text', 'score', 'meta'.
        """
        pass
