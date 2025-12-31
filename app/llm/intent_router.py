import logging
import json
import re
from google.genai import types
from app.config import settings
from app.llm.vertex_r2d2_client import VertexR2D2Client

logger = logging.getLogger(__name__)

class Intent:
    GREETING = "GREETING"
    CLOSURE = "CLOSURE"
    OFF_TOPIC = "OFF_TOPIC"
    RAG_QUERY = "RAG_QUERY"

def resolve_local_intent(query: str) -> str:
    """
    Very fast, rule-based intent resolver for common patterns.
    """
    q = query.lower().strip()
    
    # Common greetings
    greetings = [
        r"^hi$", r"^hello", r"^hey", r"^good morning", r"^good afternoon", 
        r"^how are you", r"^what's up", r"^yo$", r"^greetings"
    ]
    if any(re.search(pattern, q) for pattern in greetings):
        return Intent.GREETING

    # Common closures
    closures = [
        r"^bye", r"^goodbye", r"^that's all", r"^no more", r"^thanks", r"^thank you",
        r"^see you", r"^ciao", r"^done"
    ]
    if any(re.search(pattern, q) for pattern in closures):
        return Intent.CLOSURE
        
    # Common clear off-topics
    off_topics = [
        r"^tell me a joke", r"^sing a song", r"^what is your favorite color",
        r"^who won the (.*) game", r"^weather in"
    ]
    if any(re.search(pattern, q) for pattern in off_topics):
        return Intent.OFF_TOPIC
        
    return None

async def predict_intent(query: str) -> str:
    """
    Classifies the user query into GREETING, CLOSURE, OFF_TOPIC, or RAG_QUERY.
    """
    # 1. Try local resolution first (Fast & Free)
    local_intent = resolve_local_intent(query)
    if local_intent:
        logger.info(f"Local intent resolved: {local_intent}")
        return local_intent

    # 2. Local fallback if in NONE mode
    if settings.MODE == "none":
        return Intent.RAG_QUERY

    # 3. Use Vertex AI for complex intent detection
    prompt = f"""
    Classify the following user query into one of these categories:
    - GREETING: General greetings like "hello", "hi", "how are you".
    - CLOSURE: Goodbyes, thank yous, or saying "that's all".
    - OFF_TOPIC: Questions not related to tech docs or software.
    - RAG_QUERY: A question or request for info about documentation.

    User Query: "{query}"

    Return ONLY the category name in uppercase.
    Category:"""

    try:
        client = VertexR2D2Client.get_client()
        
        config = types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=10,
        )

        response = client.models.generate_content(
            model=settings.VERTEX_GENERATION_MODEL,
            contents=prompt,
            config=config
        )

        intent = response.text.strip().upper()
        
        valid_intents = [Intent.GREETING, Intent.CLOSURE, Intent.OFF_TOPIC, Intent.RAG_QUERY]
        if intent not in valid_intents:
            return Intent.RAG_QUERY
            
        return intent

    except Exception as e:
        logger.error(f"Intent prediction via LLM failed: {e}")
        # Second chance local check for variations not caught by regex
        q_low = query.lower()
        if any(w in q_low for w in ["bye", "thanks", "thank you"]):
             return Intent.CLOSURE
        if any(w in q_low for w in ["hello", "hi"]):
             return Intent.GREETING
        return Intent.RAG_QUERY
