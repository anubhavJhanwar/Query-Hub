# Retrieves top-k chunks with similarity confidence scores
from rag.config import TOP_K
from rag.vectorstore import load_vectorstore


def retrieve_with_scores(query: str, vector_db: str) -> tuple[list[str], list[float]]:
    """
    Returns (chunks, confidence_scores).
    Scores are normalized 0-100 relevance percentages.
    """
    vs = load_vectorstore(vector_db)
    if vs is None:
        return [], []

    results = vs.similarity_search_with_score(query, k=TOP_K)

    chunks = []
    raw_scores = []
    for doc, score in results:
        chunks.append(doc.page_content)
        raw_scores.append(float(score))

    # Normalize scores to 0-100 confidence
    # FAISS returns L2 distance (lower = better), Chroma returns cosine distance (lower = better)
    # Convert: confidence = max(0, 100 - score * 50) clamped to [0, 100]
    confidences = [round(max(0.0, min(100.0, 100.0 - s * 50)), 1) for s in raw_scores]

    return chunks, confidences


def retrieve(query: str, vector_db: str) -> list[str]:
    """Simple retrieve without scores (backward compat)."""
    chunks, _ = retrieve_with_scores(query, vector_db)
    return chunks
