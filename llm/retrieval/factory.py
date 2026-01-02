import logging
from config import settings
from llm.retrieval.base import BaseRetriever
from llm.retrieval.retriever_tfidf import TfidfRetriever
from llm.retrieval.retriever_brute import BruteRetriever

logger = logging.getLogger(__name__)

def get_retriever() -> BaseRetriever:
    """
    Returns the configured retriever based on settings.
    Default fallback order: FAISS (Vertex) -> TF-IDF -> Brute Force.
    """
    mode = settings.RETRIEVAL_MODE.lower()
    
    if mode == "faiss":
        try:
            from llm.retrieval.retriever_faiss_vertex import FaissVertexRetriever
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
