import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_PATH = Path(os.getenv("DOCUMENTS_PATH", BASE_DIR / "data"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHROMA_PERSIST_DIR = "./chroma_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

TOP_K = 6
COLLECTION_NAME = "nexla_docs"