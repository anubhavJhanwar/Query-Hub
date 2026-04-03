# Query Hub — Report

## 1. Introduction

This project implements a Retrieval-Augmented Generation (RAG) system for a customer support knowledge base. Users can ask natural language questions and receive accurate answers grounded in company documents, powered by Google Gemini.

---

## 2. Problem Statement

Traditional chatbots rely on static rules or fine-tuned models that are expensive to update. When company policies change, the bot becomes outdated. RAG solves this by dynamically retrieving relevant documents at query time, ensuring answers are always grounded in the latest knowledge base without retraining.

---

## 3. RAG Architecture

```
User Query
    │
    ▼
[Embedding Model] ──► Query Vector
    │
    ▼
[Vector Store] ──► Top-K Similar Chunks
    │
    ▼
[Prompt Builder] ──► Context + Question
    │
    ▼
[Gemini LLM] ──► Final Answer
```

**Components:**
- Ingestion: Load TXT/PDF → Clean → Chunk
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace)
- Vector Store: FAISS or ChromaDB
- LLM: Google Gemini 1.5 Flash
- API: FastAPI (Python)
- UI: React + Tailwind CSS

---

## 4. Methodology

1. Documents are loaded from `data/sample_docs/` (TXT/PDF).
2. Text is split into overlapping chunks using `RecursiveCharacterTextSplitter`.
3. Each chunk is embedded using a HuggingFace sentence transformer.
4. Embeddings are stored in a vector database (FAISS or ChromaDB).
5. At query time, the user's question is embedded and the top-3 most similar chunks are retrieved.
6. A structured prompt is built with the retrieved context and sent to Gemini.
7. Gemini generates a grounded answer, which is returned to the frontend.

---

## 5. Experimental Setup

| Parameter       | Config A        | Config B        |
|----------------|-----------------|-----------------|
| Vector DB       | FAISS           | ChromaDB        |
| Chunk Size      | 300 tokens      | 700 tokens      |
| Chunk Overlap   | 50 tokens       | 50 tokens       |
| Embedding Model | all-MiniLM-L6-v2| all-MiniLM-L6-v2|
| Top-K Retrieval | 3               | 3               |
| LLM             | Gemini 1.5 Flash| Gemini 1.5 Flash|

To switch configs, edit `backend/.env`:
- Config A: `VECTOR_DB=faiss`, `CHUNK_SIZE=300`
- Config B: `VECTOR_DB=chroma`, `CHUNK_SIZE=700`

---

## 6. Comparison Results

| Metric              | Config A (FAISS + 300) | Config B (ChromaDB + 700) |
|--------------------|------------------------|---------------------------|
| Avg Response Time  | ~1200ms                | ~1400ms                   |
| Retrieval Precision| Higher (focused chunks)| Moderate (broader context)|
| Answer Detail      | Concise                | More detailed              |
| Best For           | Specific factual Q&A   | Open-ended questions       |

**Observations:**
- Config A (smaller chunks) retrieves more precise, targeted passages, leading to faster and more focused answers.
- Config B (larger chunks) provides more surrounding context, which helps with questions requiring broader understanding.
- FAISS is slightly faster than ChromaDB for small datasets due to in-memory indexing.
- ChromaDB offers persistent storage with easier management for larger datasets.

---

## 7. Conclusion

The RAG system successfully answers customer support queries using a custom knowledge base. The modular design allows easy swapping of vector stores and chunk sizes. Config A is recommended for precise factual queries, while Config B suits broader questions. Google Gemini 1.5 Flash provides fast, accurate responses when grounded with relevant context.

---

*Built with FastAPI, LangChain, HuggingFace, FAISS, ChromaDB, React, and Google Gemini.*
