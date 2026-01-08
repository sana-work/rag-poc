import re
from typing import AsyncGenerator, List, Dict, Any

async def generate_response_stream(
    query: str, 
    context_chunks: List[Dict[str, Any]],
    system_instruction: str = None
) -> AsyncGenerator[str, None]:
    
    if not context_chunks:
        yield "### No Results Found\n\n"
        yield "I'm sorry, I couldn't find any relevant information in the uploaded documents to answer your question. Please try rephrasing or asking something else."
        return

    yield "### Extractive Source Insights (Local Mode)\n\n"
    yield "*I have analyzed your documentation and identified the following excerpts that directly address your query:*\n\n---\n\n"
    
    unique_sources = []
    
    for i, chunk in enumerate(context_chunks, 1):
        title = chunk['meta'].get('docTitle', 'Unknown Document')
        text = chunk['text']
        
        # Extract page/slide info from markers if present
        page_label = ""
        # Look for the FIRST marker in the chunk to attribute it
        match = re.search(r'--- \[(Page|Slide) (\d+)\] ---', text)
        if match:
            type_label = match.group(1)
            num = match.group(2)
            page_label = f"({type_label} {num})"
        
        # Clean markers from display text
        display_text = re.sub(r'--- \[(Page|Slide) \d+\] ---\n?', '', text).strip()
        
        # Determine Source ID (Unique Mapping)
        full_citation = f"{title} {page_label}".strip()
        if full_citation not in unique_sources:
            unique_sources.append(full_citation)
        
        source_idx = unique_sources.index(full_citation) + 1
        
        yield f"#### [Source {source_idx}, {page_label or 'Doc'}]\n\n"
        yield f"> {display_text}\n\n"
        
        if i < len(context_chunks):
            yield "\n---\n\n"
            
    yield "\n\n### References\n"
    # Comma separated unique sources
    refs = [f"Source{i} : {s}" for i, s in enumerate(unique_sources, 1)]
    yield ", ".join(refs)
