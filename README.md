# Nexla Document Q&A – MCP Server

An MCP (Model Context Protocol) server that exposes a **Q&A tool** over a collection of PDF documents. AI agents (e.g. Claude, ChatGPT, or any MCP-compatible client) can ask natural language questions and receive **grounded answers** with **source attribution** (document name and page).

## Setup Instructions

### 1. Clone and enter the repository

```bash
git clone <your-repo-url>
cd FDE-AI-Take-Home-Janvi-Desai
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add the PDF documents

- Download the 4–5 PDFs from the [assignment data folder](https://drive.google.com/drive/folders/1yxhF1lFF2gKeTNc8Wh0EyBdMT3M4pDYr).
- Place them in the `data/` directory (create it if needed).

### 4. Configure environment (optional)

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-... for LLM-generated answers.
# Without it, the server still runs but returns only the top retrieved excerpt.
```

### 5. Run the MCP server

From the **project root**:

**Option A – stdio (for Claude Desktop, Cursor, etc.):**

```bash
python -m src.server
```

**Option B – FastMCP CLI:**

```bash
fastmcp run run_mcp.py:mcp
```

The server uses **stdio** by default. Configure your MCP client to start the server with one of the commands above (e.g. in Cursor MCP settings or Claude Desktop config).

### 6. First-time indexing

- On the **first tool call** (e.g. `query_documents`), the server will automatically index all PDFs in `data/` if the index is missing or empty.
- **Optional:** Pre-index from the command line:  
  `python -m src.ingestion`  
  (or `python -m src.ingestion /path/to/pdfs` to use a custom folder.)
- To force a full re-index after adding or replacing PDFs, call the `reindex_documents` tool.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Client (Claude, Cursor, etc.)             │
└───────────────────────────────┬─────────────────────────────────┘
                                │ MCP protocol (stdio)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastMCP Server (src/server.py)              │
│  Tools: query_documents, reindex_documents                       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  ingestion.py │     │  retrieval.py   │     │    config.py     │
│  - PDF parse  │     │  - Vector search│     │  - Paths, keys   │
│  - Chunking   │     │  - LLM answer   │     │  - Model names   │
│  - Embed &    │     │  - Source       │     └─────────────────┘
│    index      │     │    attribution  │
└───────┬───────┘     └────────┬────────┘
        │                      │
        ▼                      ▼
┌───────────────┐     ┌─────────────────┐
│  PyMuPDF      │     │  ChromaDB        │
│  (fitz)       │     │  (persistent)   │
└───────────────┘     └────────┬────────┘
                               │
                    ┌──────────┴──────────┐
                    │  sentence-transformers  │  (embeddings)
                    │  OpenAI API             │  (answer generation)
                    └───────────────────────┘
```

- **Document ingestion**: PDFs in `data/` are parsed with **PyMuPDF**, split into overlapping **chunks**, embedded with **sentence-transformers** (`all-MiniLM-L6-v2`), and stored in **ChromaDB** with metadata (document name, page).
- **Query flow**: A natural language question is embedded, the top‑k chunks are retrieved from ChromaDB, and an **OpenAI** model (e.g. `gpt-4o-mini`) generates a short answer with explicit **source attribution** (document + page). If `OPENAI_API_KEY` is not set, the server returns the top retrieved excerpt with source only.
- **Multi-document**: Retrieval is over the whole collection, so answers can combine context from multiple PDFs when relevant.

---

## Tool Documentation

### `query_documents`

Ask a natural language question over the indexed PDFs. Returns a grounded answer and source references.

| Input   | Type  | Description                                |
|---------|-------|--------------------------------------------|
| `question` | string | Natural language question (e.g. “What is the main finding?”). |

**Returns:** Plain text: the answer followed by a “Sources:” line listing document names and page numbers.

**Example:**

- *“What are the key recommendations in the report?”*
- *“Which companies are mentioned as partners?”*
- *“Summarize the section on data integration.”*

---

### `reindex_documents`

Re-scan the documents folder, parse all PDFs, and rebuild the search index. Use after adding or replacing files in `data/`.

| Input            | Type  | Description                                      |
|------------------|-------|--------------------------------------------------|
| `documents_path` | string | (Optional) Path to folder with PDFs. Default: `./data`. |

**Returns:** A short summary: number of documents and chunks indexed, and list of document names.

---

## Example Interaction Log

See **[EXAMPLE_INTERACTIONS.md](EXAMPLE_INTERACTIONS.md)** for at least three sample questions and the answers returned by the system, including source attribution.

---

## Vibe Coding / AI-Assisted Development

*(To be filled by you before submission.)*

- **Which AI coding tool(s) you used and how** (e.g. Cursor, GitHub Copilot, Claude Code).
- **How you prompted or directed the AI** — what worked and what did not.
- **Where you leaned on the AI vs. where you overrode or corrected it.**
- **Your view on how AI tooling fits into a forward-deployed engineering workflow.**

There are no “wrong” answers; we care about self-awareness and intentionality with these tools.

---

## License

MIT (or as required by the assignment).
