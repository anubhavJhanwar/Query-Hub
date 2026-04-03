import axios from "axios";

const BASE_URL = "http://localhost:8000";

export async function sendQuery(query, vectorDb, chunkSize) {
  const response = await axios.post(`${BASE_URL}/query`, {
    query,
    vector_db: vectorDb,
    chunk_size: chunkSize,
  });
  return response.data;
  // Returns: { answer, response_time_ms, config_used, llm_used, sources, confidences, followups }
}

export async function ingestDocuments(vectorDb, chunkSize) {
  const response = await axios.post(`${BASE_URL}/ingest`, {
    vector_db: vectorDb,
    chunk_size: chunkSize,
  });
  return response.data;
}
