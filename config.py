import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

class Settings:
    # Project Paths
    BASE_DIR = Path(__file__).parent.resolve()
    DATA_DIR = (BASE_DIR / "data").resolve()
    LOGS_DIR = (BASE_DIR / "logs").resolve()
    
    # Mode Configuration
    MODE = os.getenv("MODE", "vertex")  # vertex | none
    RETRIEVAL_MODE = os.getenv("RETRIEVAL_MODE", "faiss")  # faiss | tfidf | brute
    
    # GCP Configuration
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    # Vertex Models
    VERTEX_GENERATION_MODEL = os.getenv("VERTEX_GENERATION_MODEL", "gemini-2.0-flash-001")
    VERTEX_EMBEDDING_MODEL = os.getenv("VERTEX_EMBEDDING_MODEL", "text-embedding-005")

    # R2D2 / Helix Configuration
    R2D2_VERTEX_BASE_URL = os.getenv("R2D2_VERTEX_BASE_URL")
    R2D2_SOEID_HEADER = os.getenv("R2D2_SOEID_HEADER", "x-r2d2-soeid")
    R2D2_SOEID = os.getenv("R2D2_SOEID")
    HELIX_TOKEN_CMD = os.getenv("HELIX_TOKEN_CMD", "helix auth access-token print -a")
    SSL_CERT_FILE = os.getenv("SSL_CERT_FILE")

    # Embedding Config
    EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "16"))
    EMBED_RETRY = int(os.getenv("EMBED_RETRY", "3"))

    # Ingestion Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

settings = Settings()
