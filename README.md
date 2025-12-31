# Informational RAG PoC (Python + JS)

A simplified, enterprise-ready RAG (Retrieval Augmented Generation) system. This version uses a lightweight JS frontend served directly by a FastAPI backend.

## Project Structure

```text
rag-poc/
├── app/                  # Application source code
│   ├── api/              # API endpoints (Streaming, Health)
│   ├── embeddings/       # Vertex AI Embedding logic
│   ├── llm/              # Vertex AI Generation & R2D2/Helix Auth
│   ├── retrieval/        # FAISS & TF-IDF search logic
│   ├── config.py         # App configuration & Env loading
│   └── main.py           # FastAPI entry point & UI Server
├── scripts/              # Utility scripts
│   ├── ingest_docs.py    # Document parsing (PDF/HTML/DOCX)
│   └── build_index.py    # Vector index creation
├── ui/                   # Frontend UI (Vanilla JS/HTML/CSS)
│   └── index.html        # Main Chat Interface
├── data/                 # Local data storage (Git ignored)
│   ├── source/           # Drop your PDFs/HTML here
│   ├── interim/          # Extracted text
│   └── artifacts/        # Search indices
├── .env                  # Your local secrets (R2D2, GCP Project)
├── requirements.txt      # Python dependencies
├── ARCHITECTURE.md       # Technical design overview
└── README.md             # This file
```

---

## Prerequisites

- **Python 3.10+** (Recommended) or 3.9
- **Helix & R2D2 Access**:
    - `helix` CLI installed and authenticated.
    - Active session via `helix auth login`.
    - Access to a Vertex AI project via R2D2.

---

## Setup & Running

### 1. Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .\.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy example environment file
cp .env.example .env
```
Fill in the following values in `.env`:
- `R2D2_VERTEX_BASE_URL`
- `R2D2_SOEID`
- `GOOGLE_CLOUD_PROJECT`
- `SSL_CERT_FILE` (if on corporate network)

### 3. Prepare Data
```bash
# 1. Place your raw files in data/source/
# 2. Ingest documents (converts to text)
python scripts/ingest_docs.py --input "data/source"

# 3. Build the search index
python scripts/build_index.py
```

### 4. Run the Application
```bash
python -m uvicorn app.main:app --reload
```
Open your browser at: **[http://localhost:8000/](http://localhost:8000/)**

---

## Key Features
- **Streaming UI**: Dynamic responses via Server-Sent Events (SSE).
- **Advanced Intent Detection**: 
    - **`GREETING`**: Warm welcomes.
    - **`CLOSURE`**: Detects goodbyes and thanks (e.g., "Bye", "Thanks").
    - **`OFF_TOPIC`**: Keeps the conversation focused on docs.
    - **`RAG_QUERY`**: Specialized search across your PDFs.
- **Hybrid Security**: Integrated Helix token refresh and R2D2 gateway routing.
- **Operating Modes**:
    - **Vertex AI (LLM)**: Full capability with generative reasoning.
    - **Local Extractive (None)**: Fast, offline-first search fallback.
- **Citations**: Interactive sourcing with relevance scoring.

## Troubleshooting
- **401/403 Error**: Run `helix auth login` to refresh your session.
- **SSL Error**: Ensure `SSL_CERT_FILE` points to  `.pem` bundle in `.env`.
- **Dimension Mismatch**: Re-run `python scripts/build_index.py` if you change embedding models.
