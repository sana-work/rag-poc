import os
import sys
import json
import pickle
import argparse
import logging
from pathlib import Path
from typing import List, Dict

# Add backend to path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings
from app.utils.text_chunker import TextChunker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_processed_docs(interim_dir: Path) -> List[Dict]:
    docs = []
    for txt_file in interim_dir.glob("*.txt"):
        meta_file = interim_dir / f"{txt_file.stem}.meta.json"
        
        if meta_file.exists():
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            with open(txt_file, 'r', encoding='utf-8') as f:
                text = f.read()
                
            docs.append({"text": text, "meta": meta})
    return docs

def build_indices(input_dir: str, output_dir: str):
    interim_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Chunking
    logger.info("Chunking documents...")
    chunker = TextChunker(chunk_size=settings.CHUNK_SIZE, overlap=settings.CHUNK_OVERLAP)
    docs = load_processed_docs(interim_path)
    
    all_chunks = []
    for doc in docs:
        chunks = chunker.chunk_text(doc["text"], doc["meta"])
        all_chunks.extend(chunks)
        
    logger.info(f"Created {len(all_chunks)} chunks.")
    
    # Save chunks registry
    chunks_file = output_path / "chunks.jsonl"
    with open(chunks_file, 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + "\n")
            
    texts = [c["text"] for c in all_chunks]
    ids = [c["chunkId"] for c in all_chunks]
    
    # 2. Build FAISS Index
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
        
        logger.info("Building FAISS index...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(texts)
        
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        
        faiss.write_index(index, str(output_path / "faiss.index"))
        logger.info("FAISS index built.")
    except ImportError:
        logger.warning("FAISS or sentence-transformers not found. Skipping FAISS build.")
    except Exception as e:
        logger.error(f"Error building FAISS index: {e}")

    # 3. Build TF-IDF Index
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        logger.info("Building TF-IDF index...")
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        with open(output_path / "tfidf.pkl", "wb") as f:
            pickle.dump((vectorizer, tfidf_matrix), f)
        logger.info("TF-IDF index built.")
    except ImportError:
        logger.warning("scikit-learn not found. Skipping TF-IDF build.")

    logger.info("Index build complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Search Index")
    parser.add_argument("--input", default="data/interim", help="Input directory processed text")
    parser.add_argument("--output", default="data/artifacts", help="Output directory for indices")
    args = parser.parse_args()
    
    build_indices(args.input, args.output)
