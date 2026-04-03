# FastAPI — Query Hub backend
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from rag.ingestion import load_documents
from rag.chunking import chunk_documents
from rag.vectorstore import build_vectorstore
from rag.retriever import retrieve_with_scores
from rag.generator import generate_answer, generate_followups
from rag.config import VECTOR_DB, CHUNK_SIZE, LLM_PROVIDER, GROQ_MODEL, GEMINI_MODEL

app = FastAPI(title="Query Hub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    vector_db: Optional[str] = None   # override .env at runtime
    chunk_size: Optional[int] = None  # informational only


class QueryResponse(BaseModel):
    answer: str
    response_time_ms: float
    config_used: str
    llm_used: str
    sources: list[str]
    confidences: list[float]          # relevance % per source
    followups: list[str]              # suggested follow-up questions


class IngestRequest(BaseModel):
    vector_db: Optional[str] = None
    chunk_size: Optional[int] = None


@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Use request override or fall back to .env config
    vdb = req.vector_db or VECTOR_DB
    cs  = req.chunk_size or CHUNK_SIZE

    start = time.time()
    sources, confidences = retrieve_with_scores(req.query, vdb)
    answer = generate_answer(req.query, sources)
    followups = generate_followups(req.query, answer)
    elapsed_ms = round((time.time() - start) * 1000, 2)

    model_name = GROQ_MODEL if LLM_PROVIDER == "groq" else GEMINI_MODEL.split("/")[-1]

    return QueryResponse(
        answer=answer,
        response_time_ms=elapsed_ms,
        config_used=f"{vdb.upper()} | chunk {cs}",
        llm_used=f"{LLM_PROVIDER} ({model_name})",
        sources=sources,
        confidences=confidences,
        followups=followups,
    )


@app.post("/ingest")
def ingest_endpoint(req: IngestRequest = IngestRequest()):
    vdb = req.vector_db or VECTOR_DB
    cs  = req.chunk_size or CHUNK_SIZE

    docs = load_documents()
    if not docs:
        raise HTTPException(
            status_code=404,
            detail="No documents found in data/sample_docs/. Add .txt or .pdf files.",
        )
    chunks = chunk_documents(docs, chunk_size=cs)
    build_vectorstore(chunks, vdb)
    return {
        "message": f"Ingested {len(docs)} doc(s) into {len(chunks)} chunk(s).",
        "vector_db": vdb,
        "chunk_size": cs,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "default_vector_db": VECTOR_DB,
        "default_chunk_size": CHUNK_SIZE,
        "llm_provider": LLM_PROVIDER,
    }
