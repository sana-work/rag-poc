# Project Workflow & File Directory Guide

This document explains exactly how the code is organized and how data flows through the system.

---

## 1. Directory & File Map

### 📂 Root Directory (The Core Engine)
This directory contains the logic that runs while the server is active.

*   **`main.py`**: The entry point. Starts FastAPI and UI server.
*   **`config.py`**: Central settings hub and `.env` loader.
*   **`api/`**: Functional endpoints (e.g., `/chat/stream`).
*   **`utils/`**: Shared utilities (Logger, Redactor).
*   **`llm/`**:
    *   **`embeddings/`**: The "Translator". Turns words into math Vectors.
    *   **`retrieval/`**: The "Search Engine". Searches FAISS/TF-IDF.
    *   **`intent_router.py`**: The "Traffic Cop". Classifies user intent.
    *   **`vertex_r2d2_client.py`**: The "Bouncer". Manages Helix/R2D2 auth.
    *   **`vertex_stream.py`**: The "Speaker". Streams Gemini response.
    *   **`none_extractive.py`**: The "Fallback". Shows results without LLM.
*   **`utils/`**: Shared utilities like `logger.py` and `redaction.py`.
*   **`utils/`**: Shared utilities like `logger.py` and `redaction.py`.
### 📂 `tools/` (The Pipeline)
These are run manually to manage your data and verify setup.
*   **`ingest_docs.py`**: Reads your raw documents and breaks them into "chunks".
*   **`build_index.py`**: Generates math vectors and saves the **FAISS** index.
*   **`check_connection.py`**: A standalone validator for Vertex AI/R2D2 and FAISS.

### 📂 `ui/` (The Face)
*   **`index.html`**: The chat bubble interface and SSE streaming handler.

---

## 2. The Data Flow (Step-by-Step)

### Phase A: Preparing your Knowledge (Indexing)
1.  **Drop Files**: You put a PDF in `data/source/`.
2.  **Parse**: You run `tools/ingest_docs.py`.
3.  **Embed**: You run `tools/build_index.py`. 
4.  **Save**: It saves vectors into `data/artifacts/faiss.index`.

### Phase B: Asking a Question (The Chat Flow)
1.  **UI**: User types in `ui/index.html`.
2.  **Intent Check**: Analyzed in `llm/intent_router.py`.
3.  **Search**: `llm/retrieval/` finds the best chunks in FAISS.
4.  **Generate**: Results streamed via `llm/vertex_stream.py`.

---

## 3. Summary of Roles

| Component | Responsibility | Relevant Files |
| :--- | :--- | :--- |
| **Ingestion** | Extracting text from files | `tools/ingest_docs.py` |
| **Vectorization** | Turning text into math | `llm/embeddings/`, `tools/build_index.py` |
| **Retrieval** | Searching for context | `llm/retrieval/` |
| **Auth** | Helix/R2D2 Security | `llm/vertex_r2d2_client.py` |
| **Interface** | Showing the chat UI | `ui/index.html`, `main.py` |
