# 📜 Project History: GenAI RAG PoC

This document tracks the evolution of the application from its initial foundation to the current Phase 2 release.

---

## 🚀 Phase 2: Data Fidelity & UX Enhancements (Current)
**Goal**: Enhance the precision, verifiable accuracy, and usability of the system.

### 🌟 Major Features
*   **Multi-Corpus Support**:
    *   **User Mode**: Friendly persona, queries `user` index.
    *   **Developer Mode**: Technical persona, queries `developer` index.
    *   **UI Toggle**: Real-time switching between modes via the Angular frontend.
*   **Comprehensive Format Support**:
    *   **PowerPoint (.pptx)**: Added native support for extracting text from slides.
    *   **Page/Slide Precision**: Ingestion now injects `[Page X]` or `[Slide X]` markers into chunks.
*   **Data Fidelity**:
    *   **Link Preservation**: Hyperlinks in PDFs, PPTs, and HTML are extracted and preserved in the LLM context.
    *   **Precision Citations**: Answers now cite specific pages/slides (e.g., `Source 1 : Handbook (Page 12)`).
    *   **Refined UX**: Compact citation headers and a unified comma-separated footer for sources.
*   **Local Mode Upgrade**:
    *   The "Zero-LLM" extractive mode now matches the formatting of the Vertex AI mode, including precision citations and unique source listing.

### 🛠️ Technical Fixes
*   **Metadata Logic**: Fixed "Unknown Document" issue by defaulting missing titles to filenames.
*   **Helix Auth Handling**: Improved error handling for Helix CLI token retrieval.
*   **Fallback Logic**: Ensured TF-IDF fallback works seamlessly when FAISS creation fails.

---

## 🏗️ Phase 1: Foundation (Initial Release)
**Goal**: Establish a working RAG (Retrieval Augmented Generation) pipeline.

### 🌟 Core Capabilities
*   **Hybrid RAG Pipeline**:
    *   **Ingestion**: `tools/ingest_docs.py` for parsing PDF, DOCX, and TXT.
    *   **Indexing**: FAISS (Vector Search) + TF-IDF (Keyword Search) priority chain.
    *   **Generation**: Google Vertex AI (Gemini Pro) integration.
*   **Application Stack**:
    *   **Backend**: FastAPI (Python 3.10+) with async endpoints.
    *   **Frontend**: Angular 16+ chat interface.
    *   **Streaming**: Server-Sent Events (SSE) for real-time response delivery.
*   **Security & Governance**:
    *   **Intent Router**: Classifies "Greeting" vs "Search" to save API costs.
    *   **Redaction**: Automatic masking of PII and credentials in logs.
    *   **R2D2/Helix**: Enterprise-grade authentication headers.

---

## 📊 Summary of Artifacts Created
*   `TECHNICAL_WALKTHROUGH.md`: Detailed engineering handbook.
*   `DEMO_PRESENTATION.md`: Slide content for stakeholder demos.
*   `SAMPLE_RAG_QUESTIONS.md`: Validated test questions for Developer usage.
*   `PROJECT_HISTORY.md`: This file.
