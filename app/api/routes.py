import asyncio
import json
import uuid
import time
from typing import Optional
from fastapi import APIRouter, Request, Query
from fastapi.responses import StreamingResponse, JSONResponse

from app.config import settings
from app.utils.logger import logger
from app.utils.redaction import Redactor
from app.retrieval.factory import get_retriever

# Import LLM handlers
from app.llm import vertex_stream, none_extractive

router = APIRouter()

async def get_llm_response(mode: str, query: str, chunks: list):
    if mode == "vertex":
        return vertex_stream.generate_response_stream(query, chunks)
    else:
        return none_extractive.generate_response_stream(query, chunks)

@router.get("/chat/stream")
async def chat_stream(
    request: Request,
    q: str = Query(..., description="User question"),
    sessionId: str = Query(default_factory=lambda: str(uuid.uuid4())),
    topK: int = Query(3, description="Number of chunks to retrieve")
):
    start_time = time.time()
    redacted_q = Redactor.redact(q)
    
    # 1. Retrieve
    retriever = get_retriever()
    chunks = retriever.retrieve(q, top_k=topK)
    
    # 2. Prepare Log Data
    log_data = {
        "sessionId": sessionId,
        "query": redacted_q,
        "retrieval_mode": settings.RETRIEVAL_MODE,
        "mode": settings.MODE,
        "retrieved_chunks": [c['chunkId'] for c in chunks],
        "retrieved_scores": [c.get('score', 0) for c in chunks]
    }
    
    async def event_generator():
        try:
            # 1. Send 'meta' event with citations
            citations = [
                {
                    "id": c.get('chunkId', 'unknown'), 
                    "title": c.get('meta', {}).get('docTitle', 'Untitled'), 
                    "score": float(c.get('score', 0))
                } 
                for c in chunks
            ]
            yield f"event: meta\ndata: {json.dumps({'citations': citations, 'retrievalMode': settings.RETRIEVAL_MODE})}\n\n"
            
            # 2. Get LLM generator (which now yields raw strings)
            full_response = ""
            try:
                generator = await get_llm_response(settings.MODE, q, chunks)
                async for token in generator:
                    full_response += token
                    # Yield raw token string back to UI
                    yield f"event: token\ndata: {json.dumps(token)}\n\n"
            except Exception as llm_e:
                # Handle auth refresh
                err_str = str(llm_e)
                if "401" in err_str or "403" in err_str:
                    logger.warning("Auth error during stream. Refreshing.")
                    from app.llm.vertex_r2d2_client import VertexR2D2Client
                    VertexR2D2Client.refresh_on_error()
                    yield f"event: token\ndata: {json.dumps('[Auth Error: Token refreshed, please retry request]')}\n\n"
                else:
                    yield f"event: token\ndata: {json.dumps(f'[Error: {err_str}]')}\n\n"
                
            # 3. Log completion and send 'done'
            latency = time.time() - start_time
            log_data['latency'] = latency
            log_data['response_length'] = len(full_response)
            logger.info("Chat Request Completed", extra={"structured_data": log_data})
            
            yield f"event: done\ndata: {json.dumps({'latency': latency})}\n\n"
            
        except Exception as e:
            logger.error(f"Event generator crash: {e}")
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
    
    # 1. Retrieve
    retriever = get_retriever()
    chunks = retriever.retrieve(q, top_k=topK)
    
    # 2. Generate (collect stream)
    generator = await get_llm_response(settings.MODE, q, chunks)
    full_response = ""
    async for token in generator:
        full_response += token
        
    latency = time.time() - start_time
    
    # Log
    log_data = {
        "sessionId": sessionId,
        "query": redacted_q,
        "retrieval_mode": settings.RETRIEVAL_MODE,
        "mode": settings.MODE,
        "retrieved_chunks": [c['chunkId'] for c in chunks],
        "latency": latency
    }
    logger.info("Chat POST Request Completed", extra={"structured_data": log_data})
    
    return JSONResponse({
        "answer": full_response,
        "citations": [
            {"id": c['chunkId'], "title": c['meta'].get('docTitle'), "score": c.get('score')} 
            for c in chunks
        ],
        "latency": latency
    })
