# Document ingestion: loads TXT and PDF files from the data directory
import os
from rag.config import DATA_DIR


def load_documents() -> list[dict]:
    """Load all TXT and PDF files from the data directory."""
    docs = []

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        return docs

    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)

        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read().strip()
            if text:
                docs.append({"source": filename, "content": text})

        elif filename.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(filepath)
                text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
                if text:
                    docs.append({"source": filename, "content": text})
            except ImportError:
                print("pypdf not installed, skipping PDF:", filename)

    print(f"[Ingestion] Loaded {len(docs)} document(s) from {DATA_DIR}")
    return docs
