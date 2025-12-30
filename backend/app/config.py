import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

class Settings:
    # Project Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Mode Configuration
    MODE = os.getenv("MODE", "vertex")  # vertex | none
    RETRIEVAL_MODE = os.getenv("RETRIEVAL_MODE", "faiss")  # faiss | tfidf | brute
    
    # GCP Configuration
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    VERTEX_MODEL = os.getenv("VERTEX_MODEL", "gemini-pro")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Ingestion Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

settings = Settings()
