"""
Document ingestion pipeline using LangChain.
Parses PDFs, splits text, embeds chunks, and stores them in Chroma.
"""

from pathlib import Path
from typing import Dict, Any

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from .config import (
    DOCUMENTS_PATH,
    CHROMA_PERSIST_DIR,
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

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vectordb = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=str(CHROMA_PERSIST_DIR),
        collection_name=COLLECTION_NAME
    )

    vectordb.persist()

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