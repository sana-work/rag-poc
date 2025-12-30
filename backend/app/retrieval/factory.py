import logging
import os
from app.config import settings
from app.retrieval.base import BaseRetriever
from app.retrieval.retriever_tfidf import TfidfRetriever
from app.retrieval.retriever_brute import BruteRetriever

logger = logging.getLogger(__name__)

def get_retriever() -> BaseRetriever:
    """
    Returns the configured retriever based on settings.
    Default fallback order: FAISS (Vertex) -> TF-IDF -> Brute Force.
    """
    mode = settings.RETRIEVAL_MODE.lower()
    
    if mode == "faiss":
        try:
            from app.retrieval.retriever_faiss_vertex import FaissVertexRetriever
            index_path = settings.DATA_DIR / "artifacts" / "faiss.index"
            chunks_path = settings.DATA_DIR / "artifacts" / "chunks.jsonl"
            
            if index_path.exists() and chunks_path.exists():
                logger.info("Initializing FAISS Vertex Retriever")
                return FaissVertexRetriever(index_path=index_path, chunks_path=chunks_path)
            else:
                logger.warning("FAISS index files not found. Falling back to TF-IDF.")
                mode = "tfidf"
        except Exception as e:
            logger.error(f"Failed to initialize FAISS Vertex Retriever: {e}")
            mode = "tfidf"

    if mode == "tfidf":
        try:
            return TfidfRetriever()
        except Exception as e:
            logger.error(f"Failed to initialize TF-IDF Retriever: {e}")
            mode = "brute"
            
    return BruteRetriever()
