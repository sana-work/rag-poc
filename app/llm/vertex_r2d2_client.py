import os
import time
import subprocess
import logging
from typing import Optional
from google.genai import Client
from google.oauth2.credentials import Cedentials
from google.genai.types import HttpOptions
from app.config import settings

logger = logging.getLogger(__name__)

class VertexR2D2Client:
    _instance = None
    _client: Optional[Client] = None
    _token: Optional[str] = None
    _token_expiry: float = 0
    _TOKEN_LIFETIME = 45 * 60  # 45 minutes

    @classmethod
    def get_client(cls) -> Client:
        """
        Returns a configured Google Gen AI Client with R2D2/Helix authentication.
        Handles token caching and refresh.
        """
        # Set Enterprise TLS if provided
        if settings.SSL_CERT_FILE:
            os.environ["SSL_CERT_FILE"] = settings.SSL_CERT_FILE

        if not cls._token or time.time() > cls._token_expiry:
            cls._refresh_token()
            cls._client = None  # Force client recreation with new token

        if not cls._client:
            cls._create_client()

        return cls._client

    @classmethod
    def _refresh_token(cls):
        """Executes helix command to get a fresh access token."""
        try:
            logger.info("Executing Helix command to fetch access token...")
            if not settings.HELIX_TOKEN_CMD:
                raise ValueError("HELIX_TOKEN_CMD not configured")
                
            result = subprocess.run(
                settings.HELIX_TOKEN_CMD, 
                shell=True,
                check=True, 
                stdout=subprocess.PIPE, 
                text=True
            )
            token = result.stdout.strip()
            if not token:
                raise ValueError("Helix command returned empty token")
            
            cls._token = token
            cls._token_expiry = time.time() + cls._TOKEN_LIFETIME
            logger.info("Successfully refreshed Helix token")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Helix command failed: {e}")
            raise RuntimeError("Failed to obtain Helix token") from e
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

    @classmethod
    def _create_client(cls):
        """Constructs the google.genai.Client with R2D2 configuration."""
        if not cls._token:
            raise ValueError("No access token available")
        if not settings.R2D2_VERTEX_BASE_URL:
            raise ValueError("R2D2_VERTEX_BASE_URL not configured")
        if "<" in settings.R2D2_VERTEX_BASE_URL or ">" in settings.R2D2_VERTEX_BASE_URL:
            raise ValueError(f"R2D2_VERTEX_BASE_URL contains placeholder characters: {settings.R2D2_VERTEX_BASE_URL}. Please update your .env file with the actual host.")
            
        if not settings.GOOGLE_CLOUD_PROJECT:
            raise ValueError("GOOGLE_CLOUD_PROJECT not configured")
        if not settings.GOOGLE_CLOUD_LOCATION:
            raise ValueError("GOOGLE_CLOUD_LOCATION not configured")

        logger.info(f"Creating R2D2 Vertex Client for project {settings.GOOGLE_CLOUD_PROJECT}")
        
        # Headers for R2D2
        headers = {}
        if settings.R2D2_SOEID_HEADER and settings.R2D2_SOEID:
            headers[settings.R2D2_SOEID_HEADER] = settings.R2D2_SOEID

        # Use google.oauth2.credentials.Credentials to wrap the raw token
        creds = Credentials(cls._token)

        cls._client = Client(
            vertexai=True,
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION,
            credentials=creds,
            http_options=HttpOptions(
                base_url=settings.R2D2_VERTEX_BASE_URL,
                headers=headers
            )
        )

    @classmethod
    def refresh_on_error(cls):
        """Force a token refresh on the next call. Use when 401/403 is encountered."""
        logger.warning("Invalidating current token due to auth error.")
        cls._token = None
        cls._token_expiry = 0
