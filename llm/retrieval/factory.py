import logging
from config import settings
from llm.retrieval.base import BaseRetriever
from llm.retrieval.retriever_tfidf import TfidfRetriever
from llm.retrieval.retriever_brute import BruteRetriever

logger = logging.getLogger(__name__)

def get_retriever(corpus: str = "user") -> BaseRetriever:
    """
    Returns the configured retriever based on settings and corpus.
    Default fallback order: FAISS (Vertex) -> TF-IDF -> Brute Force.
    """
    mode = settings.RETRIEVAL_MODE.lower()
    
    if mode == "faiss":
        try:
            from llm.retrieval.retriever_faiss_vertex import FaissVertexRetriever
            
            if corpus == "developer":
                index_path = settings.INDEX_PATH_DEV
                chunks_path = settings.CHUNKS_PATH_DEV
                tfidf_path = settings.ARTIFACTS_DIR / "tfidf_developer.pkl"
            else:
                index_path = settings.INDEX_PATH_USER
                chunks_path = settings.CHUNKS_PATH_USER
                tfidf_path = settings.ARTIFACTS_DIR / "tfidf_user.pkl"
            
            logger.info(f"Requested Corpus: {corpus} | Path: {index_path}")

            if index_path.exists() and chunks_path.exists():
                return FaissVertexRetriever(index_path=index_path, chunks_path=chunks_path)
            else:
                logger.warning(f"FAISS index files not found for {corpus}. Falling back to TF-IDF.")
                mode = "tfidf"
        except Exception as e:
            logger.error(f"Failed to initialize FAISS Vertex Retriever: {e}")
            mode = "tfidf"

    if mode == "tfidf":
        try:
            if corpus == "developer":
                tfidf_path = settings.ARTIFACTS_DIR / "tfidf_developer.pkl"
                chunks_path = settings.CHUNKS_PATH_DEV
            else:
                tfidf_path = settings.ARTIFACTS_DIR / "tfidf_user.pkl"
                chunks_path = settings.CHUNKS_PATH_USER
                
            return TfidfRetriever(pkl_path=tfidf_path, chunks_path=chunks_path)
        except Exception as e:
            logger.error(f"Failed to initialize TF-IDF Retriever: {e}")
            mode = "brute"
            
    chunks_path = settings.CHUNKS_PATH_DEV if corpus == "developer" else settings.CHUNKS_PATH_USER
    return BruteRetriever(chunks_path=chunks_path)
