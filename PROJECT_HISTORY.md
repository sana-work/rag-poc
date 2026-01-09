# 📜 Project History: GenAI RAG PoC

This document tracks the evolution of the application from its initial foundation to the current Phase 2 release.

---

## 🔮 Phase 3: Strategic Roadmap (Proposed: Hybrid RAG + Agentic AI)
**Goal**: Evolve from a passive retrieval system to an active Agentic AI solution capable of executing tasks.

### 🌟 Key Architectural Shifts
*   **Hybrid Architecture**: Combines **RAG** (for knowledge) with **Agentic AI** (for action).
*   **SmartRouter (Orchestrator)**: A central brain that directs queries to either the RAG pipeline or the Agentic toolset.
*   **MCP Integration**: Adopts the **Model Context Protocol (MCP)** to standardize connections between the AI and external systems.

### 🧩 New Components
*   **Agentic AI Orchestrator**:
    *   Authentication via **COIN Auth Server**.
    *   Determines intent (Informational vs. Directional vs. Executional).
*   **MCP Server Tools**:
    *   Exposes functionality of downstream applications as standardized tools.
    *   Connects to **Backend API Services** for real-time data and actions.
*   **Enhanced Security**:
    *   Active token maintenance via **HashiCorp Vault**.
    *   Syncs with **R2D2** for secure gateway access.

### 📋 Use Case Expansion
*   **Informational**: "How do I...?" (Solved via RAG)
*   **Directional**: "Get me the list of..." (Solved via MCP Server Call)
*   **Executional**: "Generate a report for..." (Solved via MCP Server Call)

---

## 🚀 Phase 2: Data Fidelity & UX Enhancements (Current)
**Goal**: Enhance the precision, verifiable accuracy, and usability of the system.

### 🌟 Major Features
*   **Multi-Corpus Support**:
    *   **User Mode**: Friendly persona, queries `user` index.
    *   **Developer Mode**: Technical persona, queries `developer` index.
    *   **UI Toggle**: Real-time switching between modes via the web frontend.
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
    *   **Frontend**: Native Web Standards (HTML5/JS).
    *   **Streaming**: Server-Sent Events (SSE) for real-time response delivery.
*   **Security & Governance**:
    *   **Intent Router**: Classifies "Greeting" vs "Search" to save API costs.
    *   **Redaction**: Automatic masking of PII and credentials in logs.
    *   **R2D2/Helix**: Enterprise-grade authentication headers.

---

## 📊 Summary of Artifacts Created
*   `SAMPLE_DEVELOPER_RAG_QUESTIONS.txt`: Validated test questions for Developer usage.
*   `SAMPLE_USER_RAG_QUESTIONS.txt`: Validated test questions for User usage.
*   `PROJECT_HISTORY.md`: This file.
