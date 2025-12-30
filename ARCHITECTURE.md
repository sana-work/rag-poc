# System Architecture & Flow Documentation

This document provides a detailed overview of how the RAG (Retrieval Augmented Generation) PoC application works, including the flow of data and the responsibility of each file.

## 1. High-Level Overview

The application is a **Retrieval Augmented Generation** system. It allows users to query a document knowledge base. The system retrieves relevant text chunks from uploaded documents and uses Google's Gemini LLM to generate an answer based *only* on those chunks.

**Tech Stack:**
- **Frontend**: Angular 16+ (UI, Chat Interface, SSE Stream handling)
- **Backend**: FastAPI (Python API, Retrieval Logic, LLM Integration)
- **Database/Storage**: Local file system (FAISS index, TF-IDF pickle, text chunks)
- **AI Model**: Google Vertex AI Gemini (via `google-genai` with R2D2/Helix)

---

## 2. Request/Response Flow

Here is the step-by-step journey of a user's question:

### 1. User Input (Frontend)
- **User** types a question in the chat bar (e.g., *"What is Gemini?"*) and hits Enter.
- **`app.component.ts`** captures the input and calls `ChatService.sendMessageStream()`.

### 2. API Request (Frontend -> Backend)
- **`chat.service.ts`** opens a **Server-Sent Events (SSE)** connection to the backend endpoint:  
  `GET /api/chat/stream?q=What%20is%20Gemini&sessionId=...`
- It listens for three types of events: `meta` (citations), `token` (streaming text), and `done`.

### 3. Request Handling (Backend `routes.py`)
- **FastAPI** routes the request to `chat_stream` in `backend/app/api/routes.py`.
- **Redaction**: First, the query is redacted (PII removal) using `Redactor`.

### 4. Retrieval Phase (`retrieval/`)
- The backend calls `get_retriever().retrieve(query)`.
- **`TfidfRetriever`** (or FAISS) vectorizes the query.
- It calculates **Cosine Similarity** between the query and all stored text chunks (from `chunks.jsonl`).
- The top K (default 3) most similar chunks are returned.

### 5. Prompt Construction
- `routes.py` formats a prompt for the LLM. It combines:
    - System Instructions ("You are a helpful assistant...")
    - The Retrieved Text Chunks ("Context: ...")
    - The User's Question
- This prompts the LLM to answer *only* using the provided context.

### 6. LLM Generation (`llm/vertex_stream.py`)
- The prompt is sent to **Google Gemini** via the `google-generativeai` SDK.
- The `stream=True` parameter is used to get a generator that yields text tokens as they are created.

### 7. Streaming Response (Backend -> Frontend)
- As `vertex_stream.py` yields tokens, `routes.py` packages them into SSE events.
- **Event Sequence**:
    1.  `event: meta`: Sends the JSON list of citations (Chunks used) immediately.
    2.  `event: token`: Sends pieces of the answer text (e.g., "Gemini", " is", " a", " model").
    3.  `event: done`: Sends final latency stats and closes connection.

### 8. Rendering (Frontend)
- **`chat.service.ts`** receives these events.
- **`app.component.ts`** updates the `messages` array in real-time.
- The user sees the answer typing out and the citations appearing below the message.

---

## 3. File Roles & Responsibilities

### Backend (`/backend`)

| File / Directory | Role |
| :--- | :--- |
| **`app/main.py`** | Entry point. Configures FastAPI, CORS, and mounts the API router. |
| **`app/config.py`** | Application settings. Loads env vars (R2D2 URLs, SOEIDs, Helix commands). |
| **`app/api/routes.py`** | Defines API endpoints (`/chat/stream`). Orchestrates Retrieval -> LLM -> Streaming response. |
| **`app/llm/vertex_r2d2_client.py`** | **NEW**. Factory for R2D2-compliant clients. Handles Helix token auth & refresh. |
| **`app/llm/vertex_stream.py`** | Streaming generation logic using the R2D2 client. |
| **`app/embeddings/vertex_embedder.py`** | **NEW**. Generates embeddings via R2D2 (text-embedding-005) with batching. |
| **`app/retrieval/`** | Contains retrieval logic. `factory.py` loads `FaissVertexRetriever`. |
| **`app/utils/text_chunker.py`** | Splits large documents into smaller overlapping text chunks for indexing. |
| **`scripts/ingest_docs.py`** | **Offline Script**. Parses PDF/DOCX/HTML files from `data/source` and saves plain text to `data/interim`. |
| **`scripts/build_index.py`** | **Offline Script**. Reads processed text, chunks it, and builds the Search Index (FAISS/TF-IDF). |
| **`requirements.txt`** | Python dependencies list. |

### Frontend (`/frontend`)

| File / Directory | Role |
| :--- | :--- |
| **`src/app/chat.service.ts`** | Handles HTTP communication. Uses `EventSource` to listen to the backend stream. |
| **`src/app/app.component.ts`** | Main component logic. Manages message history, user input, and UI state. |
| **`src/app/app.component.html`** | The Chat Interface template. Displays the message list and input box. |
| **`src/environments/environment.ts`** | Configures the API URL (`http://localhost:8000/api`). |

### Configuration

| File | Role |
| :--- | :--- |
| **`.env`** | Secrets and Config. Stores API Keys, Project ID, and switching modes (Vertex vs None). |

---

## 4. Workflows

### Adding New Knowledge
1.  Add file to `backend/data/source` (create folder if needed).
2.  Run `python scripts/ingest_docs.py --input data/source` (Converts to text).
3.  Run `python scripts/build_index.py` (Updates the search engine).
4.  Restart Backend (to load new index from disk).

### Switching to "Offline" Mode
1.  Set `MODE=none` in `.env`.
2.  Restart Backend.
3.  The app will now only return chunks (Search results) without generating an AI answer.
