import os
import sys
import numpy as np
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

# Load env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def check_connection_and_search():
    logger.info("Starting Connectivity and FAISS Verification...")

    # 1. Config Check
    url = os.getenv("R2D2_VERTEX_BASE_URL")
    if not url:
        logger.error("R2D2_VERTEX_BASE_URL is not set in .env")
        return
    
    if "<" in url or ">" in url:
        logger.error(f"R2D2_VERTEX_BASE_URL contains placeholders: {url}")
        logger.error("Please update .env with the actual R2D2 host.")
        return

    # 2. R2D2 Embedding Check
    logger.info("--- Phase 1: Checking R2D2 Connection (Embedding Generation) ---")
    try:
        from app.embeddings.vertex_embedder import VertexEmbedder
        embedder = VertexEmbedder()
        
        test_text = "This is a connection test."
        logger.info(f"Attempting to embed: '{test_text}'")
        
        embeddings = embedder.embed_texts([test_text])
        
        if not embeddings or len(embeddings) == 0:
            logger.error("Embedding returned empty result.")
            return
            
        vector = np.array(embeddings[0]).astype('float32')
        dimension = vector.shape[0]
        logger.info(f"Success! Generated embedding with dimension: {dimension}")
        
    except Exception as e:
        logger.error(f"R2D2 Connection Failed: {e}")
        logger.error("Verify your VPN, Proxy, and R2D2_VERTEX_BASE_URL.")
        return

    # 3. FAISS Check
    logger.info("--- Phase 2: Checking FAISS Vector Search ---")
    try:
        import faiss
        
        # Create a simple index
        index = faiss.IndexFlatL2(dimension)
        
        # Add the vector (needs to be 2D array)
        vector_2d = vector.reshape(1, -1)
        index.add(vector_2d)
        logger.info(f"Added vector to FAISS index. Total vectors: {index.ntotal}")
        
        # Search for the same vector
        D, I = index.search(vector_2d, k=1)
        
        logger.info(f"Search result - Distance: {D[0][0]} (Should be close to 0.0), Index: {I[0][0]}")
        
        if I[0][0] == 0:
            logger.info("Success! FAISS is working correctly.")
        else:
            logger.warning("FAISS search returned unexpected index.")
            
    except ImportError:
        logger.error("FAISS is not installed. Run 'pip install faiss-cpu'.")
    except Exception as e:
        logger.error(f"FAISS Check Failed: {e}")

if __name__ == "__main__":
    check_connection_and_search()
