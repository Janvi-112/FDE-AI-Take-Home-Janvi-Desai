"""Configuration loaded from environment."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Path to folder containing PDF documents
DOCUMENTS_PATH = Path(os.getenv("DOCUMENTS_PATH", "data")).resolve()

# ChromaDB persistence directory
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", "chroma_db")).resolve()

# OpenAI API key (required for LLM-generated answers)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Embedding model (sentence-transformers, runs locally)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chunk size and overlap for document splitting
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Number of chunks to retrieve for each query
TOP_K = 6

# Chroma collection name
COLLECTION_NAME = "nexla_documents"
