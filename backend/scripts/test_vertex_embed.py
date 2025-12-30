import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.embeddings.vertex_embedder import VertexEmbedder

def test_embed():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Testing Vertex Embeddings via R2D2...")
    
    texts = [
        "What is R2D2?",
        "Google Vertex AI is powerful.",
        "Testing adaptive batching..."
    ]
    
    try:
        embedder = VertexEmbedder()
        logger.info(f"Embedding {len(texts)} texts...")
        
        embeddings = embedder.embed_texts(texts)
        
        logger.info(f"Successfully generated {len(embeddings)} embeddings.")
        if embeddings:
            dim = len(embeddings[0])
            logger.info(f"Embedding Dimension: {dim}")
            print(f"PASS: Generated {len(embeddings)} vectors of dimension {dim}")
        else:
            logger.error("No embeddings returned.")
            
    except Exception as e:
        logger.error(f"Embedding test failed: {e}")
        print("FAIL")

if __name__ == "__main__":
    test_embed()
