import os
import sys
import json
import pickle
import argparse
import logging
from pathlib import Path
from typing import List, Dict

# Add backend to path to import root modules
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
# Import the new Vertex Embedder
from embeddings.vertex_embedder import VertexEmbedder
import numpy as np
import faiss

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_index():
    logger.info("Starting index build process...")

    # Paths
    artifacts_dir = settings.DATA_DIR / "artifacts"
    interim_dir = settings.DATA_DIR / "interim"
    chunks_file = artifacts_dir / "chunks.jsonl"
    faiss_index_file = artifacts_dir / "faiss.index"
    
    # Ensure artifacts directory exists
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if ingestion has run
    if not interim_dir.exists() or not list(interim_dir.glob("*.txt")):
        logger.error(f"No processed documents found in {interim_dir}. Please run 'python scripts/ingest_docs.py' first.")
        return
    
    # 1. Load Chunks
    # Ideally, we should reload from source texts and re-chunk. 
    # But for now, we assume chunks.jsonl is already populated by ingest_docs.py (or we read from interim).
    # Since ingest_docs creates interim txt files, let's assume we need to generate chunks.jsonl first?
    # Previous implementation of ingest_docs.py does NOT create chunks.jsonl, build_index.py DOES.
    # So we need to read from data/interim/*.txt and chunk them first.
    
    from utils.text_chunker import TextChunker
    chunker = TextChunker(chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)
    
    all_chunks = []
    
    logger.info("Reading processed documents from interim...")
    for txt_file in interim_dir.glob("*.txt"):
        with open(txt_file, "r", encoding="utf-8") as f:
            text = f.read()
            
        meta_file = txt_file.with_suffix(".meta.json")
        meta = {}
        if meta_file.exists():
            with open(meta_file, "r") as f:
                meta = json.load(f)
                
        # Chunking
        doc_chunks = chunker.chunk_text(text, meta)
        all_chunks.extend(doc_chunks)
        
    logger.info(f"Created {len(all_chunks)} chunks.")
    
    # Save chunks.jsonl
    with open(chunks_file, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")
            
    if not all_chunks:
        logger.warning("No chunks to index.")
        return

    # 2. Build Index using Vertex Embeddings
    try:
        logger.info(f"Generating embeddings using {settings.VERTEX_EMBEDDING_MODEL}...")
        embedder = VertexEmbedder()
        
        texts = [c['text'] for c in all_chunks]
        embeddings = embedder.embed_texts(texts)
        
        # Convert to numpy and normalize for Cosine Similarity
        embeddings_np = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings_np)
        
        dimension = embeddings_np.shape[1]
        logger.info(f"Embedding dimension: {dimension}")
        
        # Use IndexFlatIP (Inner Product) which equals Cosine Similarity on normalized vectors
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings_np)
        
        # Save FAISS index
        faiss.write_index(index, str(faiss_index_file))
        logger.info(f"FAISS index saved to {faiss_index_file}")
        
    except Exception as e:
        logger.error(f"Failed to build FAISS index with Vertex Embeddings: {e}")
        # We can implement a fallback or just fail. 
        # Since requirements say "Keep FAISS retrieval if available", we should try to succeed.
        # But if Vertex is down during build, we can't really build a vector index. 
        # We could build TF-IDF as fallback.
        
        logger.info("Falling back to TF-IDF index...")
        from sklearn.feature_extraction.text import TfidfVectorizer
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            with open(artifacts_dir / "tfidf.pkl", "wb") as f:
                pickle.dump((vectorizer, tfidf_matrix), f)
            logger.info("TF-IDF index built as fallback.")
        except Exception as tfidf_e:
            logger.error(f"TF-IDF build also failed: {tfidf_e}")

    logger.info("Index build complete.")

if __name__ == "__main__":
    build_index()
