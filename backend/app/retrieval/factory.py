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
    
    if mode == "faiss":
        try:
            return FaissRetriever()
        except:
            logger.warning("FAISS init failed, falling back to TF-IDF")
            mode = "tfidf"
            
    if mode == "tfidf":
        try:
            return TfidfRetriever()
        except:
            logger.warning("TF-IDF init failed, falling back to Brute")
            mode = "brute"
            
    return BruteRetriever()
