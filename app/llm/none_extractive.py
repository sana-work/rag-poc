from typing import AsyncGenerator, List, Dict, Any
import json

async def generate_response_stream(
    query: str, 
    context_chunks: List[Dict[str, Any]]
) -> AsyncGenerator[str, None]:
    
    yield "### Extractive Answer (No LLM Mode)\n\n"
    
    if not context_chunks:
        yield "No relevant information found."
        return

    yield "I found the following relevant information:\n\n"
    
    for i, chunk in enumerate(context_chunks, 1):
        title = chunk['meta'].get('docTitle', 'Unknown')
        score = chunk.get('score', 0.0)
        text = chunk['text']
        
        yield f"**Source {i}: {title}** (Score: {score:.4f})\n"
        yield f"> {text}\n\n"
        
    yield "\n*Note: This response was generated without an LLM by extracting top matching chunks.*"
