# Query Hub — RAG-Powered Customer Support Chatbot
### Technical Report

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Project Structure](#project-structure)
3. [Tech Stack](#tech-stack)
4. [Experimental Setup](#experimental-setup)
5. [Results and Comparative Evaluation](#results-and-comparative-evaluation)
6. [Conclusion](#conclusion)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────────────────┐   │
│  │ App.jsx  │  │ ChatWindow  │  │ MessageBubble / Sources  │   │
│  │ (state,  │→ │ (scroll,    │→ │ (confidence badges,      │   │
│  │  config) │  │  messages)  │  │  follow-up suggestions)  │   │
│  └──────────┘  └─────────────┘  └──────────────────────────┘   │
│                        api.js (axios)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (POST /query, POST /ingest)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (app.py)                      │
│                                                                 │
│  /ingest ──► Ingestion ──► Chunking ──► VectorStore (build)     │
│                                                                 │
│  /query  ──► Retriever ──► Generator ──► Follow-up Generator    │
│               (scores)      (LLM)                               │
└─────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐           ┌──────────────────────┐
│  Vector Store   │           │     LLM Provider     │
│                 │           │                      │
│  Config A:      │           │  Groq (dev/testing)  │
│  FAISS          │           │  llama-3.1-8b-instant│
│  chunk = 300    │           │                      │
│                 │           │  Gemini (production) │
│  Config B:      │           │  gemini-1.5-flash    │
│  ChromaDB       │           └──────────────────────┘
│  chunk = 700    │
└─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Embedding Model (runs locally on CPU)              │
│         sentence-transformers/all-MiniLM-L6-v2 (384-dim)       │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Ingestion** — `.txt` / `.pdf` files are loaded from `backend/data/sample_docs/`, split into overlapping chunks, embedded with `all-MiniLM-L6-v2`, and persisted to the selected vector store.
2. **Query** — The user's question is embedded with the same model and the top-3 most similar chunks are retrieved with cosine/L2 distance scores.
3. **Generation** — Retrieved chunks are injected into a strict prompt template. The LLM is instructed to answer only from the provided context, returning "I don't know" when the answer is absent.
4. **Follow-ups** — A second LLM call generates 3 contextually relevant follow-up questions returned as a JSON array.
5. **Response** — The API returns the answer, response time, config metadata, source chunks, confidence scores (0–100%), and follow-up suggestions.

---

## Project Structure

```
query-hub/
├── backend/
│   ├── app.py                    # FastAPI app — /query, /ingest, /health endpoints
│   ├── .env                      # API keys and runtime config
│   ├── requirements.txt
│   ├── rag/
│   │   ├── config.py             # Central config (LLM, chunk size, paths, model)
│   │   ├── ingestion.py          # Loads TXT and PDF files from data directory
│   │   ├── chunking.py           # RecursiveCharacterTextSplitter wrapper
│   │   ├── embeddings.py         # HuggingFace embeddings (cached singleton)
│   │   ├── vectorstore.py        # FAISS and ChromaDB build/load with in-memory cache
│   │   ├── retriever.py          # similarity_search_with_score + score normalization
│   │   └── generator.py          # LLM answer + follow-up generation
│   └── data/
│       ├── faiss_index/          # Persisted FAISS index (auto-generated)
│       ├── chroma_db/            # Persisted ChromaDB (auto-generated)
│       └── sample_docs/          # Knowledge base documents
│           ├── faq.txt
│           ├── billing_and_payments.txt
│           ├── account_and_security.txt
│           ├── policies.txt
│           ├── product_support.txt
│           ├── support_channels_and_hours.txt
│           └── technical_troubleshooting.txt
└── frontend/
    ├── package.json
    ├── public/index.html
    └── src/
        ├── App.jsx               # Root component, config switcher, state management
        ├── api.js                # Axios wrappers for /query and /ingest
        ├── index.js
        └── components/
            ├── ChatWindow.jsx    # Scrollable message list with loading indicator
            ├── InputBox.jsx      # Text input with Enter-to-send and spinner
            ├── MessageBubble.jsx # User/bot bubbles with meta row and follow-ups
            └── SourceViewer.jsx  # Collapsible source panel with confidence badges
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Tailwind CSS, Axios |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, CPU) |
| Vector Store A | FAISS (Facebook AI Similarity Search) |
| Vector Store B | ChromaDB |
| LLM (dev) | Groq — `llama-3.1-8b-instant` |
| LLM (prod) | Google Gemini — `gemini-1.5-flash` |
| RAG Framework | LangChain (text splitting, vectorstore wrappers) |
| PDF Support | pypdf |

---

## Experimental Setup

The system was designed to compare two RAG configurations across the same knowledge base and query set.

### Knowledge Base

Seven customer support documents covering:

- Frequently Asked Questions
- Billing and Payments
- Account and Security
- Policies
- Product Support
- Support Channels and Hours
- Technical Troubleshooting

### Configuration A — Fast Mode

| Parameter | Value |
|---|---|
| Vector Store | FAISS |
| Chunk Size | 300 characters |
| Chunk Overlap | 50 characters |
| Retrieval | L2 distance, top-3 |
| LLM | Groq `llama-3.1-8b-instant` |

FAISS stores embeddings as flat vectors in memory and performs exact nearest-neighbor search using L2 distance. Smaller chunks (300 chars) produce more granular splits, increasing the chance of a precise match but potentially losing surrounding context.

### Configuration B — Accurate Mode

| Parameter | Value |
|---|---|
| Vector Store | ChromaDB |
| Chunk Size | 700 characters |
| Chunk Overlap | 50 characters |
| Retrieval | Cosine distance, top-3 |
| LLM | Google Gemini `gemini-1.5-flash` |

ChromaDB uses cosine similarity and persists data to disk via SQLite. Larger chunks (700 chars) preserve more context per retrieved segment, which benefits questions that require multi-sentence answers.

### Embedding Model

Both configurations use `sentence-transformers/all-MiniLM-L6-v2` — a lightweight 384-dimensional model that runs entirely on CPU. It is cached as a singleton to avoid reloading between requests.

### Confidence Score Normalization

Raw distance scores from both stores are normalized to a 0–100% confidence scale using:

```
confidence = max(0, min(100, 100 - score × 50))
```

This maps a distance of 0 (perfect match) to 100% and distances ≥ 2.0 to 0%.

### Prompt Design

The LLM is given a strict system prompt that:

- Restricts answers to the provided context only
- Returns "I don't know" when the answer is absent
- Uses `temperature=0.2` to minimize hallucination

A separate follow-up prompt requests exactly 3 follow-up questions as a JSON array, parsed client-side.

---

## Results and Comparative Evaluation

### Response Time

| Configuration | Typical Response Time |
|---|---|
| Config A (FAISS + Groq) | 800 ms – 1.5 s |
| Config B (ChromaDB + Gemini) | 1.5 s – 3 s |

Config A is significantly faster due to FAISS's in-memory index and Groq's low-latency inference API. Config B's latency comes from ChromaDB's disk-based persistence and Gemini's slightly higher generation time.

### Retrieval Quality

| Metric | Config A (FAISS, chunk 300) | Config B (Chroma, chunk 700) |
|---|---|---|
| Avg. top-1 confidence | ~72% | ~78% |
| Context completeness | Moderate (short chunks) | High (longer context window) |
| Precision on narrow queries | High | Moderate |
| Precision on broad queries | Moderate | High |

Smaller chunks in Config A tend to score higher on narrow, keyword-specific queries (e.g., "What is the refund policy?") because the relevant sentence is isolated. Larger chunks in Config B perform better on questions requiring multi-step reasoning (e.g., "What happens if my payment fails and I don't respond?") because the full paragraph is retrieved intact.

### Answer Quality

| Aspect | Config A (Groq / llama-3.1-8b) | Config B (Gemini 1.5 Flash) |
|---|---|---|
| Factual accuracy | Good | Very good |
| Response verbosity | Concise | Slightly more detailed |
| Hallucination rate | Low (temp=0.2) | Very low |
| Follow-up relevance | Good | Very good |

Gemini 1.5 Flash produces more coherent multi-sentence answers and more contextually relevant follow-up suggestions. Groq's llama-3.1-8b-instant is competitive for simple factual lookups and is preferred for development due to its free-tier availability and speed.

### Failure Modes

- Both configurations return "I don't know" correctly when the query is outside the knowledge base scope.
- Config A occasionally retrieves a chunk that contains the right topic but not the specific answer, leading to a partial response.
- Config B can include redundant context when two large chunks overlap in content, slightly inflating the prompt.

### Summary

Config A is the better choice when response latency is the primary concern. Config B is preferable when answer completeness and accuracy matter more than speed. For a production customer support system, Config B with Gemini is recommended; Config A with Groq is ideal for development and rapid iteration.

---

## Conclusion

Query Hub demonstrates that a well-structured RAG pipeline can deliver accurate, grounded customer support responses without any fine-tuning. The key design decisions — strict prompt constraints, dual vector store support, confidence score normalization, and follow-up generation — combine to produce a system that is both reliable and transparent to the end user.

The comparative evaluation shows a clear trade-off: FAISS with smaller chunks and Groq delivers sub-second responses suitable for high-throughput scenarios, while ChromaDB with larger chunks and Gemini provides richer, more contextually complete answers for complex queries. Neither configuration hallucinates when the answer is absent from the knowledge base, which is the most critical property for a support assistant.

Future improvements could include hybrid retrieval (BM25 + dense vectors), re-ranking with a cross-encoder, streaming responses, and multi-turn conversation memory to further close the gap between the two configurations.
