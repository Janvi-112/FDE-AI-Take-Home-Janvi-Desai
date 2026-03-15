import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTS_PATH = Path(os.getenv("DOCUMENTS_PATH", BASE_DIR / "data"))
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", BASE_DIR / "chroma_db"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

TOP_K = 6
COLLECTION_NAME = "nexla_docs"