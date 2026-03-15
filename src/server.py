"""
MCP server exposing document Q&A tools.
"""

from pathlib import Path

from fastmcp import FastMCP

from .ingestion import ingest_pdfs
from .retrieval import query_documents
from .config import DOCUMENTS_PATH

mcp = FastMCP("Nexla Document Intelligence Server")


@mcp.tool()
def query_documents_tool(question: str) -> str:
    """
    Ask questions about the indexed documents.

    Returns grounded answers with document and page references.
    """

    result = query_documents(question)

    answer = result["answer"]

    sources = result["sources"]

    if sources:
        source_text = ", ".join(
            f"{s['document']} (page {s['page']})"
            for s in sources
        )

        return f"{answer}\n\nSources: {source_text}"

    return answer


@mcp.tool()
def reindex_documents(documents_path: str = "") -> str:
    """
    Rebuild the vector index from PDFs.
    """

    path = Path(documents_path) if documents_path else DOCUMENTS_PATH

    summary = ingest_pdfs(path)

    return f"""
Indexed {summary['documents']} documents
Created {summary['chunks']} chunks
"""


def main():

    ingest_pdfs()

    mcp.run()


if __name__ == "__main__":
    main()