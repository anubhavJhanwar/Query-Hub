# Query Hub

A Retrieval-Augmented Generation (RAG) application: a React frontend and FastAPI backend that answer questions from your knowledge base using embeddings and Google Gemini (or Groq).

---

## Repository layout

```
.
├── backend/          # FastAPI app, RAG pipeline, sample documents
├── frontend/         # React UI
└── README.md
```

---

## Prerequisites

- **Python 3.10+** and `pip`
- **Node.js 18+** and `npm`
- API keys as described below (Gemini and/or Groq, depending on `backend/.env`)

---

## Backend setup and run

From the repository root:

```bash
cd backend
python -m venv .venv
```

**Windows (PowerShell):** `.venv\Scripts\Activate.ps1`  
**macOS / Linux:** `source .venv/bin/activate`

```bash
pip install -r requirements.txt
```

Copy or create `backend/.env` and set your keys (see comments in `backend/rag/config.py`). At minimum, configure the LLM you use, for example:

```env
GEMINI_API_KEY=your_key_here
# or
# LLM_PROVIDER=groq
# GROQ_API_KEY=your_key_here
```

Start the API (serves on **http://localhost:8000**):

```bash
uvicorn app:app --reload
```

---

## Frontend setup and run

In a **second** terminal, from the repository root:

```bash
cd frontend
npm install
npm start
```

Open **http://localhost:3000**. The app calls the backend at **http://localhost:8000** (see `frontend/src/api.js`).

---

## Usage

1. Start the backend (`uvicorn app:app --reload` from `backend/`).
2. Start the frontend (`npm start` from `frontend/`).
3. Click **Load Knowledge Base** to ingest documents from `backend/data/sample_docs/`.
4. Ask questions in the chat UI.

---

## API (summary)

| Method | Endpoint | Description        |
|--------|----------|--------------------|
| POST   | `/query` | Ask a question     |
| POST   | `/ingest`| Index documents    |
| GET    | `/health`| Health check       |

---

## Configuration

Edit `backend/.env` to switch vector store and chunk size, for example:

```env
VECTOR_DB=faiss
CHUNK_SIZE=300
```

Restart the backend and re-ingest after changing these.

---

## License

Add a license file if you publish this repository publicly.
