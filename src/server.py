"""
Nexla Document Q&A MCP Server.

Exposes a query_documents tool so MCP clients can ask natural language questions
and receive grounded answers with source attribution from the indexed PDFs.
"""
from pathlib import Path

from fastmcp import FastMCP

from .config import DOCUMENTS_PATH
from .ingestion import ingest_pdfs
from .retrieval import query_documents as run_query_documents


mcp = FastMCP(name="Nexla Document Q&A")


def ensure_indexed() -> str | None:
    """Run ingestion if PDFs exist and index is missing or empty. Returns error message or None."""
    try:
        from .config import CHROMA_PERSIST_DIR, COLLECTION_NAME
        from chromadb import PersistentClient
        from chromadb.config import Settings

        if not DOCUMENTS_PATH.exists() or not list(DOCUMENTS_PATH.glob("*.pdf")):
            return "No PDF files found. Place PDFs in the 'data' directory and call reindex_documents first."
        client = PersistentClient(path=str(CHROMA_PERSIST_DIR), settings=Settings(anonymized_telemetry=False))
        try:
            coll = client.get_collection(COLLECTION_NAME)
            if coll.count() == 0:
                ingest_pdfs()
        except Exception:
            ingest_pdfs()
        return None
    except FileNotFoundError as e:
        return str(e)
    except Exception as e:
        return f"Indexing failed: {e}"


@mcp.tool(
    name="query_documents",
    description=(
        "Ask a natural language question over the indexed PDF documents. "
        "Returns a grounded answer with the document name and page number for each source. "
        "Use this when you need to look up information contained in the provided documents."
    ),
)
def query_documents(question: str) -> str:
    """
    Answer a natural language question using the indexed PDFs.

    Args:
        question: Natural language question (e.g. "What is the main finding of the report?").

    Returns:
        A string containing the answer and source attribution (document name and page).
        Format is plain text with sources listed; the answer is grounded in the document content.
    """
    err = ensure_indexed()
    if err:
        return f"Error: {err}"

    result = run_query_documents(question)
    answer = result["answer"]
    sources = result.get("sources", [])
    if sources:
        refs = ", ".join(f"{s['document']} (p.{s['page']})" for s in sources)
        return f"{answer}\n\nSources: {refs}"
    return answer


@mcp.tool(
    name="reindex_documents",
    description=(
        "Re-scan the documents folder, parse all PDFs, and rebuild the search index. "
        "Call this after adding or replacing PDF files in the data directory."
    ),
)
def reindex_documents(documents_path: str = "") -> str:
    """
    Ingest all PDFs from the configured documents path (or default 'data') and rebuild the index.

    Args:
        documents_path: Optional path to folder containing PDFs. Defaults to the configured DOCUMENTS_PATH (e.g. ./data).

    Returns:
        A summary message: number of documents and chunks indexed, and list of document names.
    """
    path = Path(documents_path).resolve() if documents_path else DOCUMENTS_PATH
    try:
        summary = ingest_pdfs(path)
        return (
            f"Indexed {summary['num_documents']} document(s), "
            f"{summary['num_chunks']} chunks. Documents: {', '.join(summary['doc_names'])}."
        )
    except FileNotFoundError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"


def main() -> None:
    """Run the MCP server (e.g. via stdio transport for Claude Desktop / Cursor)."""
    # Optional: index on startup so first query works without calling reindex
    ensure_indexed()
    mcp.run()


if __name__ == "__main__":
    main()
