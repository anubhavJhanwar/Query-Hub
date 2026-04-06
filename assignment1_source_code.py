"""
Assignment 1 — Query Hub: RAG-Powered Customer Support Chatbot
Topic-wise ML Source Code
"""

# ============================================================
# TOPIC 1: CONFIGURATION
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER   = os.getenv("LLM_PROVIDER", "groq")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL     = "llama-3.1-8b-instant"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = "models/gemini-1.5-flash"

CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 300))
CHUNK_OVERLAP = 50
VECTOR_DB     = os.getenv("VECTOR_DB", "faiss")
TOP_K         = 3

_BASE            = os.path.dirname(__file__)
DATA_DIR         = os.path.join(_BASE, "backend", "data", "sample_docs")
FAISS_INDEX_PATH = os.path.join(_BASE, "backend", "data", "faiss_index")
CHROMA_DB_PATH   = os.path.join(_BASE, "backend", "data", "chroma_db")
EMBEDDING_MODEL  = "sentence-transformers/all-MiniLM-L6-v2"


# ============================================================
# TOPIC 2: DOCUMENT INGESTION
# ============================================================

def load_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """Load all .txt and .pdf files from data_dir."""
    docs = []
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        return docs

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read().strip()
            if text:
                docs.append({"source": filename, "content": text})
        elif filename.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(filepath)
                text = "\n".join(p.extract_text() or "" for p in reader.pages).strip()
                if text:
                    docs.append({"source": filename, "content": text})
            except ImportError:
                print("pypdf not installed — skipping:", filename)

    print(f"[Ingestion] Loaded {len(docs)} document(s)")
    return docs


# ============================================================
# TOPIC 3: TEXT CHUNKING
# ============================================================
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document


def chunk_documents(docs: list[dict], chunk_size: int = CHUNK_SIZE) -> list[Document]:
    """Split documents into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = []
    for doc in docs:
        splits = splitter.create_documents(
            texts=[doc["content"]],
            metadatas=[{"source": doc["source"]}],
        )
        chunks.extend(splits)
    print(f"[Chunking] {len(chunks)} chunk(s) | size={chunk_size}")
    return chunks


# ============================================================
# TOPIC 4: EMBEDDINGS  (sentence-transformers, CPU)
# ============================================================
os.environ["USE_TF"]    = "0"
os.environ["USE_TORCH"] = "1"

from langchain_huggingface import HuggingFaceEmbeddings

_embeddings_cache = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return a cached all-MiniLM-L6-v2 embeddings instance (384-dim, CPU)."""
    global _embeddings_cache
    if _embeddings_cache is None:
        print(f"[Embeddings] Loading: {EMBEDDING_MODEL}")
        _embeddings_cache = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )
    return _embeddings_cache


# ============================================================
# TOPIC 5: VECTOR STORE  (FAISS / ChromaDB)
# ============================================================

_stores: dict = {}


def build_vectorstore(chunks: list[Document], vector_db: str = VECTOR_DB):
    """Embed chunks and persist to FAISS or ChromaDB."""
    embeddings = get_embeddings()
    if vector_db == "faiss":
        from langchain_community.vectorstores import FAISS
        store = FAISS.from_documents(chunks, embeddings)
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        store.save_local(FAISS_INDEX_PATH)
    elif vector_db == "chroma":
        from langchain_community.vectorstores import Chroma
        store = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DB_PATH)
    else:
        raise ValueError(f"Unknown vector_db: {vector_db}")
    _stores[vector_db] = store
    return store


def load_vectorstore(vector_db: str = VECTOR_DB):
    """Load a persisted vector store from disk (cached after first load)."""
    if vector_db in _stores:
        return _stores[vector_db]
    embeddings = get_embeddings()
    if vector_db == "faiss":
        from langchain_community.vectorstores import FAISS
        if os.path.exists(FAISS_INDEX_PATH):
            store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
            _stores[vector_db] = store
            return store
    elif vector_db == "chroma":
        from langchain_community.vectorstores import Chroma
        if os.path.exists(CHROMA_DB_PATH):
            store = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
            _stores[vector_db] = store
            return store
    print(f"[VectorStore] No index for '{vector_db}'. Run ingest first.")
    return None


# ============================================================
# TOPIC 6: RETRIEVAL WITH CONFIDENCE SCORES
# ============================================================

def retrieve_with_scores(query: str, vector_db: str = VECTOR_DB) -> tuple[list[str], list[float]]:
    """
    Retrieve top-K chunks and normalize raw distances to 0-100% confidence.
    Formula: confidence = max(0, min(100, 100 - score * 50))
    Works for both FAISS (L2) and ChromaDB (cosine) — lower distance = better.
    """
    vs = load_vectorstore(vector_db)
    if vs is None:
        return [], []
    results = vs.similarity_search_with_score(query, k=TOP_K)
    chunks, confidences = [], []
    for doc, score in results:
        chunks.append(doc.page_content)
        confidences.append(round(max(0.0, min(100.0, 100.0 - float(score) * 50)), 1))
    return chunks, confidences


# ============================================================
# TOPIC 7: LLM ANSWER & FOLLOW-UP GENERATION
# ============================================================

PROMPT_TEMPLATE = """You are a customer support assistant.

RULES:
- Answer ONLY from the provided context below.
- Do NOT assume or add information not present in the context.
- If the answer is not found in the context, say exactly: "I don't know."

Context:
{context}

Question: {question}

Answer:"""

FOLLOWUP_PROMPT = """Suggest exactly 3 short follow-up questions based on the question and answer below.
Return ONLY a JSON array of 3 strings. No explanation.

Question: {question}
Answer: {answer}

JSON array:"""


def _call_llm(prompt: str) -> str:
    if LLM_PROVIDER == "groq":
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    else:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return resp.text.strip()


def generate_answer(question: str, context_chunks: list[str]) -> str:
    if not context_chunks:
        return "I don't know. No relevant documents were found."
    context = "\n\n".join(context_chunks)
    return _call_llm(PROMPT_TEMPLATE.format(context=context, question=question))


def generate_followups(question: str, answer: str) -> list[str]:
    import json
    try:
        raw = _call_llm(FOLLOWUP_PROMPT.format(question=question, answer=answer))
        start, end = raw.find("["), raw.rfind("]") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except Exception:
        pass
    return []


# ============================================================
# TOPIC 8: END-TO-END PIPELINE DEMO
# ============================================================

def run_pipeline_demo():
    """Full RAG pipeline: load → chunk → embed → index → retrieve → generate."""
    print("\n=== Query Hub — RAG Pipeline Demo ===\n")

    docs = load_documents()
    if not docs:
        print("No documents found in", DATA_DIR)
        return

    chunks = chunk_documents(docs)
    build_vectorstore(chunks, VECTOR_DB)

    question = "What is the refund policy?"
    print(f"Question: {question}\n")

    sources, confidences = retrieve_with_scores(question, VECTOR_DB)
    for i, (src, conf) in enumerate(zip(sources, confidences), 1):
        print(f"  Source {i} ({conf}% confidence): {src[:120]}...\n")

    answer = generate_answer(question, sources)
    print(f"Answer:\n{answer}\n")

    followups = generate_followups(question, answer)
    print("Follow-ups:")
    for q in followups:
        print(f"  • {q}")


if __name__ == "__main__":
    run_pipeline_demo()
