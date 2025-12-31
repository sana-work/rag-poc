# Project Workflow & File Directory Guide

This document explains exactly how the code is organized and how data flows through the system.

---

## 1. Directory & File Map

### 📂 `app/` (The Core Engine)
This directory contains the logic that runs while the server is active.

*   **`main.py`**: The entry point. It starts the FastAPI server, configures security (CORS), and tells the server where to find the UI files (`ui/index.html`).
*   **`config.py`**: The "Settings" hub. It reads the `.env` file and shares configurations (like model names, SOEIDs, and folder paths) with the rest of the app.
*   **`api/routes.py`**: The "Traffic Controller". It handles the URL endpoints (like `/chat/stream`). When a user asks a question, this file coordinates the retrieval and the LLM generation.
*   **`llm/`**:
    *   **`vertex_r2d2_client.py`**: The "Bouncer". It manages authentication with Helix, fetches the access token, and sets up the secure R2D2 connection to Google.
    *   **`vertex_stream.py`**: The "Speaker". It sends the prompt to Gemini and gets back the streaming text.
    *   **`none_extractive.py`**: The "Fallback". If LLM mode is off, this file simply shows the search results directly.
*   **`retrieval/`**:
    *   **`factory.py`**: The "Selector". It decides whether to use FAISS (Vector search) or TF-IDF based on what's available.
    *   **`retriever_faiss_vertex.py`**: The "Search Engine". It searches the vector database to find the most relevant documents.
*   **`embeddings/vertex_embedder.py`**: The "Translator". It turns human words into the mathematical "Vectors" used for search.

### 📂 `scripts/` (The Tools)
These are run manually to prepare your data.
*   **`ingest_docs.py`**: Reads your raw PDFs/HTML and breaks them into small, readable "chunks" of text.
*   **`build_index.py`**: Takes those chunks, generates math vectors for them, and saves the **FAISS** index to your disk.

### 📂 `ui/` (The Face)
*   **`index.html`**: A single, self-contained file with all the HTML, CSS, and Javascript. It handles the chat bubbles and the live streaming connection to the server.

---

## 2. The Data Flow (Step-by-Step)

### Phase A: Preparing your Knowledge (Indexing)
1.  **Drop Files**: You put a PDF in `data/source/`.
2.  **Parse**: You run `ingest_docs.py`. It reads the PDF and saves clean text chunks in `data/interim/`.
3.  **Embed**: You run `build_index.py`. 
    *   It sends each text chunk to `vertex_embedder.py`.
    *   It gets back a "Vector" (List of numbers).
4.  **Save**: It saves all those vectors into an "Index" file (`data/artifacts/faiss.index`).

### Phase B: Asking a Question (The Chat Flow)
1.  **UI**: User types "What is Gemini?" in `ui/index.html`.
2.  **Route**: The request hits `api/routes.py`.
3.  **Search**:
    *   `routes.py` sends the question to `retriever_faiss_vertex.py`.
    *   The question is turned into a Vector.
    *   The retriever finds the **top 3 most similar** text chunks in your saved FAISS index.
4.  **Generate**:
    *   `routes.py` takes those 3 chunks and the user's question.
    *   It sends them to `vertex_stream.py`.
    *   `vertex_stream.py` connects via `vertex_r2d2_client.py` to Gemini.
5.  **Stream**: 
    *   As Gemini creates each word, it flows through `routes.py`.
    *   `routes.py` sends it as an **SSE** event to the browser.
    *   The browser updates the screen instantly.

---

## 3. Summary of Roles

| Component | Responsibility | Relevant Files |
| :--- | :--- | :--- |
| **Ingestion** | Extracting text from files | `ingest_docs.py` |
| **Vectorization** | Turning text into math | `vertex_embedder.py`, `build_index.py` |
| **Retrieval** | Searching for context | `factory.py`, `retriever_faiss_vertex.py` |
| **Auth** | Helix/R2D2 Security | `vertex_r2d2_client.py` |
| **Generation** | Creating the final answer | `vertex_stream.py` |
| **Interface** | Showing the chat UI | `index.html`, `main.py` |
