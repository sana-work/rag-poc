import sys
import json
import pickle
import logging
from pathlib import Path

# Add backend to path to import root modules
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
# Import the new Vertex Embedder
from llm.embeddings.vertex_embedder import VertexEmbedder
import numpy as np
import faiss

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_index(corpus_name: str, interim_path: Path, index_path: Path, chunks_path: Path):
    logger.info(f"--- Starting Index Build for Corpus: {corpus_name.upper()} ---")
    
    # Ensure artifacts directory exists
    index_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if ingestion has run
    if not interim_path.exists() or not list(interim_path.glob("*.txt")):
        logger.warning(f"No processed documents found in {interim_path}. Skipping {corpus_name} index build.")
        return

    from utils.text_chunker import TextChunker
    chunker = TextChunker(chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)
    
    all_chunks = []
    
    logger.info(f"Reading processed documents from {interim_path}...")
    for txt_file in interim_path.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()
            
        meta_file = txt_file.with_suffix(".meta.json")
        meta = {}
        if meta_file.exists():
            with open(meta_file, "r") as f:
                meta = json.load(f)
        
        # Default docId and docTitle if missing
        if "docId" not in meta:
            meta["docId"] = txt_file.stem
        if "docTitle" not in meta:
            meta["docTitle"] = txt_file.stem
                
        # Chunking
        doc_chunks = chunker.chunk_text(text, meta)
        all_chunks.extend(doc_chunks)
        
    logger.info(f"Created {len(all_chunks)} chunks for {corpus_name}.")
    
    # Save chunks.jsonl
    with open(chunks_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")
            
    if not all_chunks:
        logger.warning(f"No chunks to index for {corpus_name}.")
        return

    # Build Index using Vertex Embeddings
    try:
        logger.info(f"Generating embeddings using {settings.VERTEX_EMBEDDING_MODEL}...")
        embedder = VertexEmbedder()
        
        texts = [c['text'] for c in all_chunks]
        # Use RETRIEVAL_DOCUMENT for indexing
        embeddings = embedder.embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")
        
        # Convert to numpy and normalize for Cosine Similarity
        embeddings_np = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings_np)
        
        dimension = embeddings_np.shape[1]
        logger.info(f"Embedding dimension: {dimension}")
        
        # Use IndexFlatIP (Inner Product) which equals Cosine Similarity on normalized vectors
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings_np)
        
        # Save FAISS index
        faiss.write_index(index, str(index_path))
        logger.info(f"FAISS index saved to {index_path}")
        
    except Exception as e:
        logger.error(f"Failed to build FAISS index for {corpus_name}: {e}")
        
        logger.info(f"Falling back to TF-IDF index for {corpus_name}...")
        from sklearn.feature_extraction.text import TfidfVectorizer
        import pickle
        
        try:
            vectorizer = TfidfVectorizer()
            texts = [c['text'] for c in all_chunks]
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Save fallback artifacts
            # Note: The factory currently looks for FAISS or TFIDF based on config.
            # If Config is FAISS, it will fail to load if files missing.
            # We should probably save a dummy FAISS index OR rely on the factory falling back.
            # But the factory falls back to TfidfRetriever which needs 'tfidf.pkl'.
            # Let's save a specific tfidf pkl for the corpus.
            
            # Define fallback path
            tfidf_path = index_path.with_name(f"tfidf_{corpus_name}.pkl")
            
            with open(tfidf_path, "wb") as f:
                pickle.dump((vectorizer, tfidf_matrix), f)
            logger.info(f"TF-IDF index built as fallback at {tfidf_path}.")
            
        except Exception as tfidf_e:
            logger.error(f"TF-IDF build also failed: {tfidf_e}")

    logger.info(f"Index build complete for {corpus_name}.")

if __name__ == "__main__":
    # Build User Index
    build_index(
        corpus_name="user",
        interim_path=settings.DATA_DIR / "interim" / "user",
        index_path=settings.INDEX_PATH_USER,
        chunks_path=settings.CHUNKS_PATH_USER
    )

    # Build Developer Index
    build_index(
        corpus_name="developer",
        interim_path=settings.DATA_DIR / "interim" / "developer",
        index_path=settings.INDEX_PATH_DEV,
        chunks_path=settings.CHUNKS_PATH_DEV
    )
