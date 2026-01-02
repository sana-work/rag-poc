import logging
from config import settings
from llm.vertex_r2d2_client import VertexR2D2Client
from google.genai import types

logger = logging.getLogger(__name__)

async def generate_response_stream(query: str, context_chunks: list, system_instruction: str = None):
    """
    Streams raw tokens from Vertex AI Gemini using R2D2 client.
    """
    
    # Construct prompt
    context_text = "\n\n".join([c.get('text', '') for c in context_chunks])
    
    # Default instruction if none provided
    if not system_instruction:
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

    try:
        client = VertexR2D2Client.get_client()
        
        # Configure generation config
        config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1024,
            system_instruction=system_instruction
        )

        response_stream = client.models.generate_content_stream(
            model=settings.VERTEX_GENERATION_MODEL,
            contents=prompt,
            config=config
        )

        # Stream raw tokens
        for chunk in response_stream:
            text_chunk = chunk.text
            if text_chunk:
                yield text_chunk

    except Exception as e:
        logger.error(f"Vertex AI generation error: {e}")
        # Re-raise to let the API layer handle or report the error
        raise e
