import json
import uuid
import time
from typing import Any
from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse

from config import settings
from utils.logger import logger
from utils.redaction import Redactor
from llm.retrieval.factory import get_retriever

# Import LLM handlers
from llm import vertex_stream, none_extractive, intent_router
from llm.intent_router import Intent

router = APIRouter()

async def get_llm_response(mode: str, query: str, chunks: list, system_instruction: str = None):
    if mode == "vertex":
        return vertex_stream.generate_response_stream(query, chunks, system_instruction)
    else:
        return none_extractive.generate_response_stream(query, chunks, system_instruction)

@router.get("/chat/stream")
async def chat_stream(
    request: Request,
    q: str = Query(..., description="User question"),
    sessionId: str = Query(default_factory=lambda: str(uuid.uuid4())),
    topK: int = Query(5, description="Number of chunks to retrieve"),
    corpus: str = Query("user", description="Corpus to search: 'user' or 'developer'")
):
    start_time = time.time()
    redacted_q = Redactor.redact(q)
    
    # 1. Intent Detection
    intent = await intent_router.predict_intent(q)
    logger.info(f"Detected intent for {sessionId}: {intent}")

    # 2. Decision Logic based on Intent
    chunks = []
    system_instruction = None

    if intent == Intent.GREETING:
        if corpus == "developer":
            system_instruction = "You are a precise technical assistant. Acknowledge the developer briefly and await their command."
        else:
            system_instruction = "You are a friendly AI assistant. Greet the user warmly and ask how you can help them today. Do NOT use search results."
            
    elif intent == Intent.CLOSURE:
        system_instruction = "The user is finishing the conversation. Respond polite and concisely."
        
    elif intent == Intent.OFF_TOPIC:
        system_instruction = f"You are a specialized assistant for the {corpus} corpus. The user's question is off-topic. Politely redirect them to the relevant documentation."
        
    else:
        # RAG_QUERY: Proceed with retrieval
        retriever = get_retriever(corpus=corpus)
        chunks = retriever.retrieve(q, top_k=topK)
        
        # Define Corpus-Specific System Prompts
        if corpus == "developer":
            system_instruction = (
                "You are an expert technical documentation assistant for developers.\n"
                "Your goal is to provide precise, technical, and concise answers based strictly on the provided context.\n"
                "### Instructions:\n"
                "1. **Structure**: Start with a direct answer. Use `##` headers to organize sections (e.g., 'Implementation', 'Configuration').\n"
                "2. **Be Technical**: Use correct terminology. Focus on implementation details, APIs, and configurations.\n"
                "3. **Strict Grounding**: Answer ONLY using the provided context chunks. If information is missing, state 'Not specified in current context'.\n"
                "4. **Format Code**: Use triple backticks with language tags (e.g., ```python) for all code blocks.\n"
                "5. **Citations**: Append source filenames like `[Source: filename]`."
            )
        else:
            # User Mode (Default)
            system_instruction = (
                "You are a friendly and helpful AI assistant for general users.\n"
                "Your goal is to explain concepts simply and provide step-by-step guidance based on the context.\n"
                "### Instructions:\n"
                "1. **Structure**: Begin with a warm, clear summary. Use `##` headers to break up long explanations.\n"
                "2. **Be Conversational**: Use a natural tone. Explain complex terms simply (e.g., 'Authentication' -> 'proving who you are').\n"
                "3. **Helpful Guidance**: If providing steps, use numbered lists. Bold key actions or buttons.\n"
                "4. **Grounding**: Base your answer on the context, but smooth out the language to be readable.\n"
                "5. **Citations**: Reference which document helped, e.g., `(see 'User Guide')`."
            )

    # 3. Prepare Log Data
    log_data = {
        "sessionId": sessionId,
        "query": redacted_q,
        "intent": intent,
        "retrieval_mode": settings.RETRIEVAL_MODE,
        "mode": settings.MODE,
        "corpus": corpus,
        "retrieved_chunks": [c['chunkId'] for c in chunks],
        "retrieved_scores": [c.get('score', 0) for c in chunks]
    }
    
    async def event_generator():
        try:
            # Prepare unique citations list
            unique_citations = {}
            for c in chunks:
                title = c.get('meta', {}).get('docTitle', 'Untitled')
                if title not in unique_citations:
                    unique_citations[title] = {
                        "id": c.get('chunkId', 'unknown'),
                        "title": title,
                        "score": float(c.get('score', 0))
                    }
            citations = list(unique_citations.values())
            yield f"event: meta\ndata: {json.dumps({'citations': citations, 'retrievalMode': settings.RETRIEVAL_MODE, 'intent': intent, 'corpus': corpus})}\n\n"
            
            full_response = ""
            if intent in [Intent.GREETING, Intent.CLOSURE, Intent.OFF_TOPIC]:
                if settings.MODE == "none":
                    if intent == Intent.GREETING:
                        full_response = "Hello! I am ready to help you search your documents (Local Mode)."
                    elif intent == Intent.CLOSURE:
                        full_response = "Goodbye! Have a great day."
                    else:
                        full_response = "I am in Local Mode. Please ask a specific question about your documents."
                else:
                    try:
                        generator = await get_llm_response(settings.MODE, q, chunks, system_instruction)
                        async for token in generator:
                            full_response += token
                            yield f"event: token\ndata: {json.dumps(token)}\n\n"
                    except Exception:
                        full_response = "Hello! How can I help you today?"
                
                if full_response and settings.MODE == "none":
                    yield f"event: token\ndata: {json.dumps(full_response)}\n\n"
            
            elif intent == Intent.RAG_QUERY:
                if not chunks and settings.MODE == "none":
                    full_response = f"I could not find information in the {corpus} docs."
                    yield f"event: token\ndata: {json.dumps(full_response)}\n\n"
                else:
                    try:
                        generator = await get_llm_response(settings.MODE, q, chunks, system_instruction)
                        async for token in generator:
                            full_response += token
                            yield f"event: token\ndata: {json.dumps(token)}\n\n"
                    except Exception as e:
                        if any(err in str(e) for err in ["401", "403"]):
                            from llm.vertex_r2d2_client import VertexR2D2Client
                            VertexR2D2Client.refresh_on_error()
                            yield f"event: token\ndata: {json.dumps('[Auth Error: Token refreshed, please retry]')}\n\n"
                        else:
                            yield f"event: token\ndata: {json.dumps(f'[Error: {str(e)}]')}\n\n"
            
            latency = time.time() - start_time
            logger.info("Chat Completed", extra={"structured_data": {**log_data, "latency": latency, "length": len(full_response)}})
            yield f"event: done\ndata: {json.dumps({'latency': latency})}\n\n"
        except Exception as e:
            logger.error(f"SSE Error: {e}")
            yield f"event: done\ndata: {{}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/chat")
async def chat_post(
    request: Request,
):
    # Simplified POST handler primarily for testing - standardizing on corpus='user' default for now
    body = await request.json()
    q = body.get("q")
    sessionId = body.get("sessionId", str(uuid.uuid4()))
    topK = body.get("topK", 3)
    corpus = body.get("corpus", "user")
    
    if not q:
        return JSONResponse({"error": "Missing query"}, status_code=400)

    start_time = time.time()
    redacted_q = Redactor.redact(q)
    
    # Intent Detection
    intent = await intent_router.predict_intent(q)
    
    chunks = []
    
    # Simple logic for POST - expand if needed
    retriever = get_retriever(corpus=corpus)
    chunks = retriever.retrieve(q, top_k=topK)
    
    # ... (Omitted full generation logic for POST to save space, keeping it minimal as primary is stream)
    full_response = "Static POST response for testing."

    latency = time.time() - start_time
    
    # Log
    log_data = {
        "sessionId": sessionId,
        "query": redacted_q,
        "intent": intent,
        "retrieval_mode": settings.RETRIEVAL_MODE,
        "mode": settings.MODE,
        "corpus": corpus,
        "retrieved_chunks": [c['chunkId'] for c in chunks],
        "latency": latency
    }
    
    return JSONResponse({
        "answer": full_response,
        "intent": intent,
        "citations": list({
            c['meta'].get('docTitle', 'Untitled'): {
                "id": c['chunkId'], 
                "title": c['meta'].get('docTitle', 'Untitled'), 
                "score": c.get('score')
            } for c in chunks
        }.values()),
        "latency": latency
    })
