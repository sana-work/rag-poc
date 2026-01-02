import os
import sys
import time
import subprocess
import logging
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

from google.genai import Client
from google.oauth2.credentials import Credentials
from google.genai.types import HttpOptions, EmbedContentConfig

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load env from the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

def get_helix_token():
    """Executes helix command to get a fresh access token."""
    cmd = os.getenv("HELIX_TOKEN_CMD")
    if not cmd:
        raise ValueError("HELIX_TOKEN_CMD is not set in .env")
        
    try:
        logger.info("Executing Helix command to fetch access token...")
        result = subprocess.run(
            cmd, 
            shell=True,
            check=True, 
            stdout=subprocess.PIPE, 
            text=True
        )
        token = result.stdout.strip()
        if not token:
            raise ValueError("Helix command returned empty token")
        return token
    except subprocess.CalledProcessError as e:
        logger.error(f"Helix command failed: {e}")
        raise RuntimeError("Failed to obtain Helix token") from e

def check_connection_and_search():
    logger.info("Starting Standalone Connectivity and FAISS Verification...")

    # 1. Config Check
    r2d2_url = os.getenv("R2D2_VERTEX_BASE_URL")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    
    # SSL Cert handling from reference
    ssl_cert = os.getenv("SSL_CERT_FILE")
    if ssl_cert:
        os.environ["SSL_CERT_FILE"] = ssl_cert
        logger.info(f"Set SSL_CERT_FILE to: {ssl_cert}")

    if not r2d2_url or not project_id or not location:
        logger.error("Missing required env vars: R2D2_VERTEX_BASE_URL, GOOGLE_CLOUD_PROJECT, or GOOGLE_CLOUD_LOCATION")
        return
    
    if "<" in r2d2_url or ">" in r2d2_url:
        logger.error(f"R2D2_VERTEX_BASE_URL contains placeholders: {r2d2_url}")
        logger.error("Please update .env with the actual R2D2 host.")
        return

    # 2. R2D2 Embedding Check
    logger.info("--- Phase 1: Checking R2D2 Connection (Direct) ---")
    try:
        # Get Token
        token = get_helix_token()
        creds = Credentials(token)
        
        # Prepare Headers
        headers = {}
        soe_header = os.getenv("R2D2_SOEID_HEADER")
        soe_id = os.getenv("R2D2_SOEID")
        if soe_header and soe_id:
            headers[soe_header] = soe_id

        # Initialize Client
        logger.info(f"Initializing Vertex Client for project {project_id}...")
        client = Client(
            vertexai=True,
            project=project_id,
            location=location,
            credentials=creds,
            http_options=HttpOptions(
                base_url=r2d2_url,
                headers=headers
            )
        )
        logger.info("Vertex Client initialized. Attempting to verify connection with embedding generation...")
        
        # Generate Embedding
        test_text = "This is a standalone connection test."
        model_name = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-004")
        
        logger.info(f"Attempting to embed with model '{model_name}': '{test_text}'")
        
        response = client.models.embed_content(
            model=model_name,
            contents=[test_text],
            config=EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        
        # Extract vector
        embeddings = [e.values for e in response.embeddings]
        
        if not embeddings or len(embeddings) == 0:
            logger.error("Embedding returned empty result.")
            return
            
        vector = np.array(embeddings[0]).astype('float32')
        dimension = vector.shape[0]
        logger.info(f"Success! Generated embedding with dimension: {dimension}")
        
    except Exception as e:
        logger.error(f"R2D2 Connection Failed: {e}")
        logger.error("Verify your VPN, Proxy, R2D2_VERTEX_BASE_URL, and Helix authentication.")
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
