import os
import time
import subprocess
import logging
from typing import Optional
from google.genai import Client
from google.oauth2.credentials import Credentials
from google.genai.types import HttpOptions
from config import settings

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
        try:
            if not settings.HELIX_TOKEN_CMD:
                raise ValueError("HELIX_TOKEN_CMD missing")
            result = subprocess.run(settings.HELIX_TOKEN_CMD, shell=True, check=True, capture_output=True, text=True)
            cls._token = result.stdout.strip()
            cls._token_expiry = time.time() + cls._TOKEN_LIFETIME
            logger.info("Token refreshed via Helix")
        except Exception as e:
            logger.error(f"Helix token failed: {e}")
            raise

    @classmethod
    def _create_client(cls):
        if not cls._token: raise ValueError("No token")
        if not all([settings.R2D2_VERTEX_BASE_URL, settings.GOOGLE_CLOUD_PROJECT, settings.GOOGLE_CLOUD_LOCATION]):
            raise ValueError("Incomplete R2D2 configuration")
        
        soe_id = settings.R2D2_SOEID or os.getenv("USER", "")
        headers = {"x-r2d2-soeid": soe_id} if soe_id else {}
        
        cls._client = Client(
            vertexai=True,
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION,
            credentials=Credentials(cls._token),
            http_options=HttpOptions(base_url=settings.R2D2_VERTEX_BASE_URL, headers=headers)
        )

    @classmethod
    def refresh_on_error(cls):
        """Force a token refresh on the next call. Use when 401/403 is encountered."""
        logger.warning("Invalidating current token due to auth error.")
        cls._token = None
        cls._token_expiry = 0
