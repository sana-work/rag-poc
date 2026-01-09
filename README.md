# RAG PoC (with Hybrid Agentic Roadmap)

A standard-setting **RAG (Retrieval Augmented Generation)** architecture for informational queries, with a strategic roadmap to evolve into a **Hybrid Agentic AI** solution.

## Project Structure

```text
rag-poc/
├── api/              # API endpoints (Streaming, Health)
├── llm/              # Core Logic (Auth, Generation, Retrieval)
│   ├── embeddings/   # Vertex AI Embedding logic
│   ├── retrieval/    # FAISS & TF-IDF search logic
│   ├── intent_router.py
│   ├── vertex_stream.py
│   ├── vertex_r2d2_client.py
│   └── factory.py    # Retriever instantiation logic
├── utils/            # Shared utilities
├── config.py         # App configuration & Env loading
├── main.py           # FastAPI entry point & UI Server
├── tools/            # Utility & Pipeline tools
│   ├── check_connection.py  # Environment validator
│   ├── ingest_docs.py       # Document parsing (Multi-Corpus)
│   ├── build_index.py       # Vector index creation (Multi-Corpus)
│   └── cleanup.py           # Project reset utility
├── SAMPLE_RAG_QUESTIONS.txt # Test Questions (also .md, .txt)
├── ui/                   # Frontend UI (Vanilla JS/HTML/CSS)
│   └── index.html        # Main Chat Interface (with User/Dev Toggle)
├── data/                 # Local data storage (Git ignored)
│   ├── source/           # Raw documents
│   │   ├── user/         # "User" corpus source files
│   │   └── developer/    # "Developer" corpus source files
│   │   └── Supports: .pdf, .docx, .html, .pptx
│   ├── artifacts/        # Search indices / Chunks
│   └── interim/          # Extracted text (Split by corpus)
├── .env                  # Local secrets (R2D2, GCP Project)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## Prerequisites

- **Python 3.10+** (Recommended) or 3.9
- **Helix & R2D2 Access**:
    - `helix` CLI installed and authenticated.
    - Active session via `helix auth login`.
    - Access to a Vertex AI project via R2D2.

### Verification
Run the standalone connection check to verify your environment before running the app:
```bash
python tools/check_connection.py
```

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
- `SSL_CERT_FILE` 

### 3. Prepare Data
```bash
# 1. Place your raw files in:
#    - data/source/user/ (for general users)
#    - data/source/developer/ (for technical docs)

# 2. Ingest documents (processes both corpora automatically)
python tools/ingest_docs.py

# 3. Build the search indexes (builds both User and Developer indices)
python tools/build_index.py
```

### 4. Run the Application
```bash
python -m uvicorn main:app --reload
```
Open your browser at: **[http://localhost:8000/](http://localhost:8000/)**

### 5. Maintenance (Cleanup)
To reset the project (delete indices, logs, and parsed files) without touching raw data:
```bash
python tools/cleanup.py
```
*This safely removes `data/artifacts`, `data/interim`, and `logs/` content.*

---

## Key Features (Current Phase 1)
- **Streaming UI**: Dynamic responses via Server-Sent Events (SSE).
- **Multi-Corpus Support**:
    - **User Mode**: Friendly, non-technical explanations grounded in user docs.
    - **Developer Mode**: Precise, technical answers from developer documentation.
- **Advanced Intent Detection**: 
    - **`GREETING`**: Warm welcomes.
    - **`CLOSURE`**: Detects goodbyes and thanks.
    - **`OFF_TOPIC`**: Keeps the conversation focused.
    - **`RAG_QUERY`**: Specialized search across your PDFs.
- **Hybrid Security**: Integrated Helix token refresh and R2D2 gateway routing.
- **Operating Modes**:
    - **Vertex AI (LLM)**: Full capability with generative reasoning.
    - **Local Extractive (None)**: Fast, offline-first search fallback.
- **Citations**: Interactive sourcing with relevance scoring.

## 🔮 Future Capabilities (Roadmap)
- **Agentic AI Orchestration**: Intelligent routing to **RAG** (for info) or **MCP Tools** (for action).
- **MCP Integration**: Standardized connection to downstream APIs via Model Context Protocol.

## Troubleshooting
- **401/403 Error**: Run `helix auth login` to refresh your session.
- **SSL Error**: Ensure `SSL_CERT_FILE` points to  `.pem` bundle in `.env`.
- **Dimension Mismatch**: Re-run `python scripts/build_index.py` if you change embedding models.
