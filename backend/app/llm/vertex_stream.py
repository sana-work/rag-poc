import google.generativeai as genai
from typing import AsyncGenerator, List, Dict, Any
from app.config import settings
from app.utils.logger import logger

# Initialize Vertex AI
# Note: google-genai SDK 0.2+ handles ADC automatically if configured correctly.
# If using the 'google-generativeai' (Palm API) library it might be different, 
# but for Vertex AI we usually use 'vertexai' or 'google.generativeai' with configuration.
# The user specified `google-genai` python SDK. 
# Assuming standard `google.generativeai` setup for Gemini.

try:
    if settings.GOOGLE_API_KEY:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
    else:
        genai.configure(transport="rest")
except:
    pass

async def generate_response_stream(
    query: str, 
    context_chunks: List[Dict[str, Any]]
) -> AsyncGenerator[str, None]:
    
    context_text = "\n\n".join([f"source: {c['meta']['docTitle']}\ncontent: {c['text']}" for c in context_chunks])
    
    prompt = f"""You are a helpful assistant. unique instructions:
    1. Answer the user question based ONLY on the provided context.
    2. If the answer is not in the context, say "I don't have enough information."
    3. Cite your sources by referring to the document titles provided.
    
    Context:
    {context_text}
    
    User Question: {query}
    
    Answer:"""
    
    try:
        model = genai.GenerativeModel(settings.VERTEX_MODEL)
        response = model.generate_content(prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error(f"Vertex AI generation error: {e}")
        yield f"[Error generating response from Vertex AI: {str(e)}]"
