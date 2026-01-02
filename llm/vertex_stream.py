import logging
from config import settings
from llm.vertex_r2d2_client import VertexR2D2Client
from google.genai import types

logger = logging.getLogger(__name__)

async def generate_response_stream(query: str, context_chunks: list, system_instruction: str = None):
    """
    Streams raw tokens from Vertex AI Gemini using R2D2 client.
    """
    
    # Construct labeled context
    context_parts = []
    for i, c in enumerate(context_chunks, 1):
        title = c.get('meta', {}).get('docTitle', 'Unknown Document')
        context_parts.append(f"--- SOURCE {i} ({title}) ---\n{c.get('text', '')}")
    
    context_text = "\n\n".join(context_parts)
    
    # Default instruction if none provided
    if not system_instruction:
        system_instruction = (
            "You are a helpful AI assistant specializing in technical documentation.\n\n"
            "Answer the user's question accurately using ONLY the context provided below. "
            "If the context does not contain the answer, say 'I'm sorry, but I couldn't find information about that in the current documents.'\n\n"
            "Formatting Rules:\n\n"
            "1. Use clear Markdown: bold key terms, use bullet points, and ensure high readability.\n"
            "2. If you use information from a specific SOURCE, mention it in your answer (e.g., 'According to Source 1...').\n"
            "3. Keep the tone professional but user-friendly."
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
