import logging
import json
import time
from app.config import settings
from app.llm.vertex_r2d2_client import VertexR2D2Client
from google.genai.types import GenerateContentConfig

logger = logging.getLogger(__name__)

async def generate_response_stream(query: str, context_chunks: list, session_id:str):
    """
    Streams response from Vertex AI Gemini using R2D2 client.
    """
    
    # Construct prompt
    context_text = "\n\n".join([c.get('text', '') for c in context_chunks])
    
    system_instruction = (
        "You are a helpful AI assistant. "
        "Answer the user's question using ONLY the context provided below. "
        "If the context does not contain the answer, say 'I cannot find the answer in the provided documents'.\n"
    )

    prompt = f"""
    Context:
    {context_text}

    User Question: {query}
    
    Answer:
    """

    start_time = time.time()
    
    try:
        client = VertexR2D2Client.get_client()
        
        # Configure generation config
        config = GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1024,
            system_instruction=system_instruction
        )

        response_stream = client.models.generate_content_stream(
            model=settings.VERTEX_GENERATION_MODEL,
            contents=prompt,
            config=config
        )

        full_response = ""
        
        # Stream chunks
        for chunk in response_stream:
            # Depending on SDK version, text might be accessed differently
            # google-genai v1.0+ usually has chunk.text
            text_chunk = chunk.text
            if text_chunk:
                full_response += text_chunk
                yield f"event: token\ndata: {json.dumps(text_chunk)}\n\n"

        latency = time.time() - start_time
        
        # Best effort logging of request ID if available (SDK dependent)
        # request_id = getattr(response_stream, "request_id", "unknown") 
        # logger.info(f"Stream complete. RequestID: {request_id}, SessionID: {session_id}")

        # Send done event
        done_payload = {
            "latency": latency,
            "tokens": len(full_response.split()) # Approximate
        }
        yield f"event: done\ndata: {json.dumps(done_payload)}\n\n"

    except Exception as e:
        logger.error(f"Vertex AI generation error: {e}")
        
        # Handle auth errors with refresh
        if "401" in str(e) or "403" in str(e):
            logger.warning("Auth error detected, refreshing token...")
            VertexR2D2Client.refresh_on_error()
            yield f"event: token\ndata: {json.dumps('[Auth Error: Token refreshed, please retry request]')}\n\n"
        else:
            yield f"event: token\ndata: {json.dumps(f'[Error generating response: {e}]')}\n\n"
        
        yield f"event: done\ndata: {{}}\n\n"
