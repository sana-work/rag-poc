import logging
import time
from typing import List
from config import settings
from llm.vertex_r2d2_client import VertexR2D2Client
from google.genai.types import EmbedContentConfig

logger = logging.getLogger(__name__)

class VertexEmbedder:
    def __init__(self):
        self.model = settings.VERTEX_EMBEDDING_MODEL
        self.retry_count = settings.EMBED_RETRY

    def embed_texts(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
        """
        Embeds a list of texts using Vertex AI via R2D2 using adaptive batching.
        """
        results = []
        batch_size = settings.EMBED_BATCH_SIZE

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                batch_embeddings = self._embed_batch_with_retry(batch, task_type=task_type)
                results.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Batch embedding failed: {e}. Falling back to sequential embedding.")
                # Fallback: Sequential
                for text in batch:
                    try:
                        single_res = self._embed_batch_with_retry([text], task_type=task_type)
                        results.extend(single_res)
                    except Exception as inner_e:
                        logger.error(f"Single embedding failed for text snippet: {inner_e}")
                        # Return zero vector or skip (here we assume downstream handles filtering or crashing is acceptable)
                        # For generated index consistency, we should probably raise or return empty
                        raise inner_e
        return results

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query string."""
        return self.embed_texts([text], task_type="RETRIEVAL_QUERY")[0]

    def _embed_batch_with_retry(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
        """Helpers to call the API with retry logic for 401/429."""
        client = VertexR2D2Client.get_client()
        
        for attempt in range(self.retry_count):
            try:
                response = client.models.embed_content(
                    model=self.model,
                    contents=texts,
                    config=EmbedContentConfig(task_type=task_type) # Optimized based on use-case
                )
                # response.embeddings is a list of ContentEmbedding objects
                return [e.values for e in response.embeddings]
            
            except Exception as e:
                err_str = str(e)
                if "401" in err_str or "403" in err_str:
                    logger.warning("Auth error during embedding. Refreshing token.")
                    VertexR2D2Client.refresh_on_error()
                    client = VertexR2D2Client.get_client() # Get fresh client
                elif "429" in err_str:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited. Waiting {wait_time}s.")
                    time.sleep(wait_time)
                else:
                    # If it's not a transient error we can fix, iterate or re-raise
                    if attempt == self.retry_count - 1:
                        raise e
                    logger.warning(f"Embedding attempt {attempt} failed: {e}")
                    time.sleep(1)
        
        raise RuntimeError("Embedding failed after retries")
