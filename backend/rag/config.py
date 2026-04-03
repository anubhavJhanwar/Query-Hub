# Central configuration for the RAG system
import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────
# Switch via .env: LLM_PROVIDER=groq  or  LLM_PROVIDER=gemini
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL    = "llama-3.1-8b-instant"    # fast, free tier

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "models/gemini-1.5-flash" # final submission model

# ── CHUNKING ─────────────────────────────────────────
# Config A → 300  |  Config B → 700
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 300))
CHUNK_OVERLAP = 50

# ── VECTOR DB ────────────────────────────────────────
# Config A → faiss  |  Config B → chroma
VECTOR_DB = os.getenv("VECTOR_DB", "faiss")

# ── RETRIEVAL ────────────────────────────────────────
TOP_K = 3

# ── PATHS ────────────────────────────────────────────
_BASE = os.path.dirname(__file__)
DATA_DIR         = os.path.join(_BASE, "..", "data", "sample_docs")
FAISS_INDEX_PATH = os.path.join(_BASE, "..", "data", "faiss_index")
CHROMA_DB_PATH   = os.path.join(_BASE, "..", "data", "chroma_db")

# ── EMBEDDINGS ───────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
