import logging
import os
from app.config import settings
from app.retrieval.base import BaseRetriever
from app.retrieval.retriever_faiss import FaissRetriever
from app.retrieval.retriever_tfidf import TfidfRetriever
from app.retrieval.retriever_brute import BruteRetriever

logger = logging.getLogger(__name__)

def get_retriever() -> BaseRetriever:
    mode = settings.RETRIEVAL_MODE.lower()
    
    if settings.RETRIEVAL_MODE == "faiss":
        try:
            from app.retrieval.retriever_faiss_vertex import FaissVertexRetriever
            # Verify files exist
            if (settings.DATA_DIR / "artifacts" / "faiss.index").exists():
                logger.info("Initializing FAISS Vertex Retriever")
                return FaissVertexRetriever(
                    index_path=settings.DATA_DIR / "artifacts" / "faiss.index",
                    chunks_path=settings.DATA_DIR / "artifacts" / "chunks.jsonl"
                )
        except Exception as e:
            logger.error(f"Failed to initialize FAISS Retriever: {e}")
            logger.info("Falling back to TF-IDF")
            mode = "brute"
            
    return BruteRetriever()
