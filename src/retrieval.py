"""Retrieval and answer generation with source attribution."""
from typing import Any

from chromadb import PersistentClient
from chromadb.config import Settings
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from .config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    TOP_K,
)


def get_collection():
    """Return the ChromaDB collection (must exist from prior ingestion)."""
    client = PersistentClient(path=str(CHROMA_PERSIST_DIR), settings=Settings(anonymized_telemetry=False))
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception:
        return None


def retrieve(question: str, top_k: int = TOP_K) -> list[dict[str, Any]]:
    """
    Embed the question, search ChromaDB for relevant chunks, return list of
    { content, document, page }.
    """
    collection = get_collection()
    if collection is None or collection.count() == 0:
        return []
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_embedding = model.encode([question]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas"],
    )
    out: list[dict[str, Any]] = []
    if results["documents"] and results["documents"][0]:
        for doc, meta in zip(results["documents"][0], results["metadatas"][0] or []):
            out.append({
                "content": doc,
                "document": meta.get("document", "unknown"),
                "page": meta.get("page", 0),
            })
    return out


def answer_with_sources(question: str, chunks: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Use OpenAI to generate a grounded answer from the retrieved chunks.
    Returns { answer, sources } where sources is list of { document, page }.
    """
    if not OPENAI_API_KEY:
        # Fallback: concatenate top chunk and say no LLM
        if chunks:
            c = chunks[0]
            return {
                "answer": (
                    f"No OPENAI_API_KEY set. Here is the most relevant excerpt:\n\n{c['content'][:1500]}..."
                ),
                "sources": [{"document": c["document"], "page": c["page"]}],
            }
        return {"answer": "No relevant passages found and no LLM configured.", "sources": []}

    context_parts = []
    seen: set[tuple[str, int]] = set()
    for c in chunks:
        key = (c["document"], c["page"])
        if key in seen:
            continue
        seen.add(key)
        context_parts.append(
            f"[Source: {c['document']}, page {c['page']}]\n{c['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise assistant that answers questions using ONLY the provided document excerpts. "
                    "Always cite the document name and page number (e.g. 'According to document X, page Y'). "
                    "If the excerpts do not contain enough information, say so and do not invent details. "
                    "Keep answers concise and grounded in the source text."
                ),
            },
            {
                "role": "user",
                "content": f"Relevant excerpts:\n\n{context}\n\n---\n\nQuestion: {question}\n\nProvide a grounded answer with source attribution (document name and page).",
            },
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    answer_text = (response.choices[0].message.content or "").strip()

    # Build unique sources list from chunks we used
    sources = [{"document": c["document"], "page": c["page"]} for c in chunks]

    return {"answer": answer_text, "sources": sources}


def query_documents(question: str, top_k: int = TOP_K) -> dict[str, Any]:
    """
    Full pipeline: retrieve relevant chunks, then generate answer with sources.
    """
    chunks = retrieve(question, top_k=top_k)
    if not chunks:
        return {
            "answer": "No relevant passages were found in the indexed documents for this question.",
            "sources": [],
        }
    return answer_with_sources(question, chunks)
