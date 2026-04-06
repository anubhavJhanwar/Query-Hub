# Query Hub

A full-stack RAG-powered customer support chatbot built with React, FastAPI, FAISS/ChromaDB, and Groq/Gemini.

## Architecture

```
React Frontend  →  FastAPI Backend  →  Vector Store (FAISS / ChromaDB)
                                    →  LLM (Groq / Gemini)
                                    →  Embeddings (all-MiniLM-L6-v2, local CPU)
```

Full architecture diagram and comparative evaluation in [`report.md`](./report.md).

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # fill in your API keys
python -m uvicorn app:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

App runs at `http://localhost:3000`.
Click the upload icon in the header to ingest the knowledge base before querying.

## Configuration

Two configs are supported — switch via `backend/.env`:

| | Config A — Fast | Config B — Accurate |
|---|---|---|
| Vector Store | FAISS | ChromaDB |
| Chunk Size | 300 chars | 700 chars |
| LLM | Groq `llama-3.1-8b-instant` | Gemini `gemini-1.5-flash` |
| Response Time | ~800ms–1.5s | ~1.5s–3s |

```env
# Config A (default)
VECTOR_DB=faiss
CHUNK_SIZE=300
LLM_PROVIDER=groq

# Config B
VECTOR_DB=chroma
CHUNK_SIZE=700
LLM_PROVIDER=gemini
```

Re-ingest the knowledge base after switching configs.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/query` | Ask a question, get answer + sources + follow-ups |
| POST | `/ingest` | Load and index documents from `data/sample_docs/` |
| GET | `/health` | Check current runtime config |

## Project Structure

```
query-hub/
├── backend/
│   ├── app.py                  # FastAPI endpoints
│   ├── .env.example            # Environment variable template
│   ├── requirements.txt
│   └── rag/
│       ├── config.py           # Central config
│       ├── ingestion.py        # Load TXT / PDF files
│       ├── chunking.py         # RecursiveCharacterTextSplitter
│       ├── embeddings.py       # sentence-transformers (local CPU)
│       ├── vectorstore.py      # FAISS + ChromaDB build/load
│       ├── retriever.py        # similarity search + score normalization
│       └── generator.py        # LLM answer + follow-up generation
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       └── components/
│           ├── ChatWindow.jsx
│           ├── InputBox.jsx
│           ├── MessageBubble.jsx
│           └── SourceViewer.jsx
├── report.md                   # System architecture + evaluation
└── assignment1_source_code.py  # Topic-wise ML source code
```

## Knowledge Base

Seven customer support documents in `backend/data/sample_docs/`:
- FAQ
- Billing and Payments
- Account and Security
- Policies
- Product Support
- Support Channels and Hours
- Technical Troubleshooting
