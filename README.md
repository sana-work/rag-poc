# Phase-1 Informational RAG PoC

A complete, enterprise-friendly RAG (Retrieval Augmented Generation) system with an Angular frontend and FastAPI backend.

## Features

- **Angular 16+ Chat UI**: Real-time streaming responses, citations display.
- **FastAPI Backend**: 
  - **Modes**: `vertex` (Cloud LLM) and `none` (No-LLM fallback).
  - **Retrieval**: Auto-fallback strategy (FAISS -> TF-IDF -> Brute Force).
  - **Streaming**: Server-Sent Events (SSE) for low latency.
  - **Logging**: Structured JSON logs with PII redaction.
- **Ingestion**: Scripts to parse PDF, DOCX, and HTML.

---

## Prerequisites

- **Python 3.10+** (Recommended), or Python 3.9 with `importlib-metadata`
- **Node.js 16+** (includes **NPM**) - [Download here](https://nodejs.org/)
- **Helix & R2D2 Access**:
    - `helix` CLI installed and configured.
    - An active session with `helix auth login`.
    - `SSL_CERT_FILE` pointing to your corporate CA bundle (if required).
    - Access to the target Vertex project via R2D2.

---

## Setup Instructions (Windows Friendly)

### 1. Backend Setup

Open a terminal (PowerShell or Command Prompt) in the `rag-poc/backend` directory.

1.  **Create Virtual Environment**:
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

2.  **Install Dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**:
    - Copy `.env.example` to `.env`.
    - **R2D2 Config**: Set `R2D2_VERTEX_BASE_URL` and `R2D2_SOEID`.
    - **Enterprise TLS**: Set `SSL_CERT_FILE` path in `.env`.
    - **Helix**: Ensure `HELIX_TOKEN_CMD` is correct for your OS.
    - **Project**: Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`.
    ```powershell
    copy .env.example .env
    ```

5.  **Ingest Documents (Demo Data)**:
    - Create a sample HTML/PDF/DOCX file in a folder (e.g., `data/source`).
    - For example, create `data/source/gemini.html` with some content.
    - Run ingestion:
    ```powershell
    python scripts/ingest_docs.py --input "data/source"
    ```

6.  **Build Index**:
    ```powershell
    python scripts/build_index.py
    ```

6.  **Run Server**:
    ```powershell
    uvicorn app.main:app --reload
    ```
    The backend runs at `http://localhost:8000`.

### 2. Frontend Setup

Open a new terminal in the `rag-poc/frontend` directory.

1.  **Install Dependencies**:
    ```powershell
    npm install
    ```

2.  **Run Application**:
    ```powershell
    ng serve
    ```
    The frontend runs at `http://localhost:4200`.

---

## Usage Scenarios

### Mode 1: Cloud LLM (Vertex AI)

- Ensure `MODE=vertex` in `.env`.
- Ensure you have run `gcloud auth application-default login`.
- Start both servers.
- Ask questions in the UI.

### Mode 2: No-LLM Fallback (Strictly Restricted Env)

- Set `MODE=none` in `.env`.
- Restart Backend.
- The system will return the best matching text chunks directly.

### Search Fallbacks

You can control retrieval strategy via `.env`:
- `RETRIEVAL_MODE=faiss` (Requires `faiss-cpu` and `sentence-transformers`)
- `RETRIEVAL_MODE=tfidf` (Requires `scikit-learn`)
- `RETRIEVAL_MODE=brute` (Works with standard Python only)

If a library is missing, the system automatically falls back to the next available method.

---

## Troubleshooting

- **FAISS Import Error**: Using Windows? Ensure you installed `faiss-cpu`. If problems persist, set `RETRIEVAL_MODE=tfidf` in `.env`.
- **Authentication Error (401/403)**:
    - The app automatically tries to refresh the token.
    - If it persists, run `helix auth login` in your terminal manually.
    - Check if `HELIX_TOKEN_CMD` in `.env` works by running it in your shell.
- **SSL / Certificate Verify Failed**:
    - Ensure `SSL_CERT_FILE` in `.env` points to the correct `.pem` file.
    - Ensure the path has no trailing spaces.
- **'npm' is not recognized**:
    - This means Node.js is not installed or not in your system's PATH.
    - Download and install Node.js from [nodejs.org](https://nodejs.org/).
    - Restart your terminal/IDE after installation.
- **ModuleNotFoundError: google.generativeai**: Ensure you installed `google-generativeai` (not `google-genai`).
- **ImportError: importlib.metadata**: If using Python < 3.10, install `importlib-metadata`.
- **Frontend Connection Error**: Ensure backend is running on port 8000 and CORS is enabled (default is allow all).

