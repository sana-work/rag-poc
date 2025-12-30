import logging
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings
from app.llm.vertex_r2d2_client import VertexR2D2Client

def test_generate():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Testing Vertex Generation via R2D2...")
    
    try:
        client = VertexR2D2Client.get_client()
        
        prompt = "Hello, explain what is RAG in one sentence."
        logger.info(f"Sending prompt: {prompt}")
        
        response = client.models.generate_content(
            model=settings.VERTEX_GENERATION_MODEL,
            contents=prompt
        )
        
        if response.text:
            logger.info(f"Response received: {response.text}")
            print("PASS: Generation successful")
        else:
            logger.error("Empty response received")
            print("FAIL: Empty response")
            
    except Exception as e:
        logger.error(f"Generation test failed: {e}")
        print("FAIL")

if __name__ == "__main__":
    test_generate()
