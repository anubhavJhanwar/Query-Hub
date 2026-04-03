# Splits documents into chunks using LangChain's text splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from rag.config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_documents(docs: list[dict], chunk_size: int = None) -> list[Document]:
    """Split raw documents into chunks. chunk_size overrides config if provided."""
    size = chunk_size or CHUNK_SIZE
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
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

    print(f"[Chunking] Created {len(chunks)} chunk(s) with size={size}")
    return chunks
