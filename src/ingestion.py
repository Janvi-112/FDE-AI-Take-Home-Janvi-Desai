"""PDF document ingestion: parse, chunk, and index into ChromaDB."""
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF
from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .config import (
    CHROMA_PERSIST_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DOCUMENTS_PATH,
    EMBEDDING_MODEL,
)


def extract_text_from_pdf(pdf_path: Path) -> list[tuple[int, str]]:
    """Extract text from each page of a PDF. Returns list of (page_num, text)."""
    pages: list[tuple[int, str]] = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()
        if text:
            pages.append((page_num + 1, text))  # 1-based page numbers
    doc.close()
    return pages


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks by character count."""
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Prefer breaking at sentence boundary (last . or newline)
        if end < len(text):
            last_break = max(chunk.rfind(". "), chunk.rfind("\n"))
            if last_break > chunk_size // 2:
                chunk = chunk[: last_break + 1]
                end = start + last_break + 1
        chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def ingest_pdfs(documents_path: Path | None = None) -> dict[str, Any]:
    """
    Find all PDFs in documents_path, extract text, chunk, embed, and store in ChromaDB.
    Returns summary: num_docs, num_chunks, doc_names.
    """
    base_path = documents_path or DOCUMENTS_PATH
    if not base_path.exists():
        raise FileNotFoundError(f"Documents path does not exist: {base_path}")

    pdf_files = sorted(base_path.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {base_path}")

    # Load embedding model once
    model = SentenceTransformer(EMBEDDING_MODEL)

    # ChromaDB client with persistence
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    client = PersistentClient(path=str(CHROMA_PERSIST_DIR), settings=Settings(anonymized_telemetry=False))

    # Use a single collection; we'll replace it on full re-index
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Document chunks for Q&A"},
    )

    all_ids: list[str] = []
    all_documents: list[str] = []
    all_metadatas: list[dict[str, str | int]] = []
    doc_names: list[str] = []

    for pdf_path in pdf_files:
        doc_name = pdf_path.name
        doc_names.append(doc_name)
        pages = extract_text_from_pdf(pdf_path)
        chunk_index = 0
        for page_num, page_text in pages:
            chunks = chunk_text(page_text)
            for chunk in chunks:
                if not chunk:
                    continue
                chunk_id = f"{doc_name}::p{page_num}::c{chunk_index}"
                all_ids.append(chunk_id)
                all_documents.append(chunk)
                all_metadatas.append({
                    "document": doc_name,
                    "page": page_num,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1

    if not all_documents:
        raise ValueError("No text extracted from any PDF. Check that the files are valid.")

    # Embed in batches for efficiency
    embeddings = model.encode(all_documents, show_progress_bar=len(all_documents) > 20).tolist()
    collection.add(ids=all_ids, documents=all_documents, metadatas=all_metadatas, embeddings=embeddings)

    return {
        "num_documents": len(pdf_files),
        "num_chunks": len(all_ids),
        "doc_names": doc_names,
    }


if __name__ == "__main__":
    """CLI: run from project root to index PDFs in data/ (e.g. python -m src.ingestion)."""
    import sys
    path = DOCUMENTS_PATH
    if len(sys.argv) > 1:
        path = Path(sys.argv[1]).resolve()
    try:
        summary = ingest_pdfs(path)
        print(
            f"Indexed {summary['num_documents']} document(s), "
            f"{summary['num_chunks']} chunks. Documents: {', '.join(summary['doc_names'])}."
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
