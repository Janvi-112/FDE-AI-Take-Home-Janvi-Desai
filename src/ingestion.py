"""
Document ingestion pipeline using LangChain.
Parses PDFs, splits text, embeds chunks, and stores them in Chroma.
"""

from pathlib import Path
from typing import Dict, Any

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from .config import (
    CHROMA_PERSIST_DIR,
    DOCUMENTS_PATH,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    COLLECTION_NAME
)


def load_documents(folder: Path):
    documents = []

    for pdf_file in folder.glob("*.pdf"):
        loader = PyMuPDFLoader(str(pdf_file))
        docs = loader.load()

        for d in docs:
            d.metadata["document"] = pdf_file.name

        documents.extend(docs)

    return documents


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return splitter.split_documents(documents)


def build_vector_store(chunks):

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectordb = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=COLLECTION_NAME
    )

    return vectordb


def ingest_pdfs(documents_path: Path | None = None) -> Dict[str, Any]:

    path = documents_path or DOCUMENTS_PATH

    if not path.exists():
        raise FileNotFoundError(f"Documents folder not found: {path}")

    pdfs = list(path.glob("*.pdf"))

    if not pdfs:
        raise ValueError("No PDFs found")

    documents = load_documents(path)

    chunks = split_documents(documents)

    vectordb = build_vector_store(chunks)

    return {
        "documents": len(pdfs),
        "chunks": len(chunks),
        "path": str(path),
    }


if __name__ == "__main__":

    summary = ingest_pdfs()

    print("Ingestion complete:")
    print(summary)