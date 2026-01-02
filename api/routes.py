import asyncio
import json
import uuid
import time
from typing import Optional
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
    topK: int = Query(3, description="Number of chunks to retrieve")
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
        system_instruction = "You are a friendly AI assistant. Greet the user warmly and ask how you can help them today. Do NOT use search results."
    elif intent == Intent.CLOSURE:
        system_instruction = "The user is finishing the conversation or saying thanks. Respond politely and wish them a great day!"
    elif intent == Intent.OFF_TOPIC:
        system_instruction = "You are a helpful AI assistant. The user has asked something outside your specialized knowledge of the uploaded documents. Politely inform them that you are focused on the documentation and ask if they have questions about that."
    else:
        # RAG_QUERY: Proceed with retrieval
        retriever = get_retriever()
        chunks = retriever.retrieve(q, top_k=topK)

    # 3. Prepare Log Data
    log_data = {
        "sessionId": sessionId,
        "query": redacted_q,
        "intent": intent,
        "retrieval_mode": settings.RETRIEVAL_MODE,
        "mode": settings.MODE,
        "retrieved_chunks": [c['chunkId'] for c in chunks],
        "retrieved_scores": [c.get('score', 0) for c in chunks]
    }
    
    async def event_generator():
        try:
            citations = [{"id": c.get('chunkId', 'unknown'), "title": c.get('meta', {}).get('docTitle', 'Untitled'), "score": float(c.get('score', 0))} for c in chunks]
            yield f"event: meta\ndata: {json.dumps({'citations': citations, 'retrievalMode': settings.RETRIEVAL_MODE, 'intent': intent})}\n\n"
            
            full_response = ""
            if intent in [Intent.GREETING, Intent.CLOSURE, Intent.OFF_TOPIC]:
                if settings.MODE == "none":
                    static_responses = {Intent.GREETING: "Hello! How can I help you today?", Intent.CLOSURE: "You're welcome! Have a great day!", Intent.OFF_TOPIC: "I'm focused on the technical documentation provided."}
                    full_response = static_responses.get(intent, "Hello!")
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
                    full_response = "I couldn't find specific info in the docs. Please rephrase."
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
    body = await request.json()
    q = body.get("q")
    sessionId = body.get("sessionId", str(uuid.uuid4()))
    topK = body.get("topK", 3)
    
    if not q:
        return JSONResponse({"error": "Missing query"}, status_code=400)

    start_time = time.time()
    redacted_q = Redactor.redact(q)
    
    # Intent Detection
    intent = await intent_router.predict_intent(q)
    
    chunks = []
    system_instruction = None

    if intent == Intent.GREETING:
        system_instruction = "You are a friendly AI assistant. Greet the user warmly."
    elif intent == Intent.CLOSURE:
        system_instruction = "The user is saying goodbye or thank you. Wish them well."
    elif intent == Intent.OFF_TOPIC:
        system_instruction = "Helpful AI assistant, but politely decline off-topic questions."
    else:
        retriever = get_retriever()
        chunks = retriever.retrieve(q, top_k=topK)

    # Generate
    full_response = ""
    
    # Handle direct resolution intents (GREETING, CLOSURE, OFF_TOPIC)
    if intent in [Intent.GREETING, Intent.CLOSURE, Intent.OFF_TOPIC]:
        if settings.MODE == "none":
            if intent == Intent.GREETING:
                full_response = "Hello! I am your local AI assistant. How can I help you explore the OpsUI Application today?"
            elif intent == Intent.CLOSURE:
                full_response = "You're very welcome! Have a great day!"
            else:
                full_response = "I'm optimized for technical documentation queries. Please ask about the software!"
        else:
            try:
                generator = await get_llm_response(settings.MODE, q, chunks, system_instruction)
                async for token in generator:
                    full_response += token
            except Exception:
                # Fallback to static if LLM fails
                static_map = {
                    Intent.GREETING: "Hello! I am your AI assistant. How can I help you today?",
                    Intent.CLOSURE: "You're welcome! Let me know if you need anything else.",
                    Intent.OFF_TOPIC: "I'm focused on the technical documentation provided."
                }
                full_response = static_map.get(intent, "Hello!")
    
    # Handle RAG_QUERY
    elif intent == Intent.RAG_QUERY:
        if not chunks and settings.MODE == "none":
            full_response = "I'm sorry, I couldn't find any specific information about that in the documents."
        else:
            try:
                generator = await get_llm_response(settings.MODE, q, chunks, system_instruction)
                async for token in generator:
                    full_response += token
            except Exception as e:
                full_response = f"[Error: {str(e)}]"
        
    latency = time.time() - start_time
    
    # Log
    log_data = {
        "sessionId": sessionId,
        "query": redacted_q,
        "intent": intent,
        "retrieval_mode": settings.RETRIEVAL_MODE,
        "mode": settings.MODE,
        "retrieved_chunks": [c['chunkId'] for c in chunks],
        "latency": latency
    }
    logger.info("Chat POST Request Completed", extra={"structured_data": log_data})
    
    return JSONResponse({
        "answer": full_response,
        "intent": intent,
        "citations": [
            {"id": c['chunkId'], "title": c['meta'].get('docTitle'), "score": c.get('score')} 
            for c in chunks
        ],
        "latency": latency
    })
