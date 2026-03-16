# Nexla Document Intelligence Server
### FDE AI Take-Home Assignment — Janvi Desai

A fully local, offline Retrieval-Augmented Generation (RAG) pipeline exposed as an MCP (Model Context Protocol) server. It ingests PDF documents, indexes them in a vector store, and exposes natural language Q&A tools that any MCP-compatible AI assistant (e.g., Cursor, Claude) can call.

---

## Architecture Overview

The system is split into two phases: **Ingestion** (indexing) and **Retrieval** (querying), both wired into a FastMCP server.

```
┌─────────────────────────────────────────────────────────────┐
│                        INGESTION                            │
│                                                             │
│  PDF files (data/)                                          │
│       │                                                     │
│       ▼                                                     │
│  PyMuPDFLoader ──► RecursiveCharacterTextSplitter           │
│  (page-level docs)   (1000 chars, 200 overlap)              │
│       │                                                     │
│       ▼                                                     │
│  HuggingFaceEmbeddings                                      │
│  (sentence-transformers/all-MiniLM-L6-v2)                   │
│       │                                                     │
│       ▼                                                     │
│  ChromaDB  →  persisted to ./chroma_db                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        RETRIEVAL                            │
│                                                             │
│  User Question                                              │
│       │                                                     │
│       ▼                                                     │
│  Embed query (same MiniLM model)                            │
│       │                                                     │
│       ▼                                                     │
│  ChromaDB cosine similarity → top-6 chunks                  │
│       │                                                     │
│       ▼                                                     │
│  Format context with source + page metadata                 │
│       │                                                     │
│       ▼                                                     │
│  HuggingFacePipeline (google/flan-t5-base)                  │
│       │                                                     │
│       ▼                                                     │
│  Answer + source citations                                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Switched from OpenAI to HuggingFace embeddings** — originally used `text-embedding-ada-002`, but hit a `429 RateLimitError`. Replaced with `sentence-transformers/all-MiniLM-L6-v2`, which runs fully locally with no API key required.
- **Local LLM** — used `google/flan-t5-base` via `HuggingFacePipeline` for answer generation. Completely free and offline.
- **ChromaDB auto-persistence** — newer Chroma versions auto-persist when `persist_directory` is set; no `.persist()` call needed.
- **MCP integration with Cursor** — the MCP server was connected to Cursor IDE over HTTP for end-to-end testing during development.

---

## Project Structure

```
FDE-AI-Take-Home-Janvi-Desai/
├── src/
│   ├── config.py          # All tunable parameters and paths
│   ├── ingestion.py       # PDF load → split → embed → Chroma
│   ├── retrieval.py       # Chroma load → retrieve → LLM → answer
│   └── server.py          # FastMCP server with tool definitions
├── data/                  # Place PDF documents here
├── chroma_db/             # Auto-created vector store (git-ignored)
├── query.py               # Interactive CLI for local Q&A testing
├── run_mcp.py             # Entry point for FastMCP CLI
├── requirements.txt
└── .env                   # Optional: override DOCUMENTS_PATH
```

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd FDE-AI-Take-Home-Janvi-Desai
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add PDFs

Copy the provided PDF files into the `data/` folder. Or set a custom path in a `.env` file:

```
DOCUMENTS_PATH=/path/to/your/pdfs
```

### 5. Run ingestion (index the PDFs)

```bash
python -m src.ingestion
```

Output:
```
Ingestion complete:
{'documents': 5, 'chunks': 312, 'path': '/path/to/data'}
```

### 6. Start the MCP server

```bash
fastmcp run run_mcp.py:mcp --transport http --port 5555
```

> **Important:** Always activate `.venv` before running — the base conda environment will not have the required packages. Confirm your prompt shows `(.venv)` before running.

### 7. (Optional) Run interactive CLI for local testing

```bash
python -m query
```

---

## MCP Tool Documentation

### `query_documents_tool`

Ask a natural language question over the indexed PDFs.

| | |
|---|---|
| **Input** | `question: str` — a natural language question |
| **Output** | Grounded answer string with source document and page citations |

**Example call:**
```json
{
  "name": "query_documents_tool",
  "arguments": { "question": "What is Nexla's approach to data integration?" }
}
```

**Example response:**
```
Nexla uses a metadata-driven approach to unify data, documents, agents, and APIs into a single design pattern...

Sources: nexla_overview.pdf (page 1), nexla_whitepaper.pdf (page 4)
```

---

### `reindex_documents`

Rebuilds the vector index from PDFs on demand. Useful when documents are added or updated.

| | |
|---|---|
| **Input** | `documents_path: str` (optional) — path to PDF folder; defaults to `data/` |
| **Output** | Summary of documents and chunks indexed |

**Example call:**
```json
{
  "name": "reindex_documents",
  "arguments": {}
}
```

**Example response:**
```
Indexed 5 documents
Created 312 chunks
```

---

## Example Interaction Log

### Q1: "Can you summarize Cloze-driven Pretraining of Self-attention Networks?"

> Cloze-driven pretraining trains self-attention networks by masking tokens in a sequence and tasking the model with predicting them from surrounding context. This forces the model to learn bidirectional contextual representations. The approach is evaluated on language modeling and downstream NLP tasks, where it outperforms autoregressive baselines on several benchmarks.

**Sources:** `cloze_pretraining.pdf (page 2)`, `cloze_pretraining.pdf (page 5)`

---

### Q2: "What evaluation metrics are used across the provided research papers?"

> The papers use a range of evaluation metrics including perplexity for language modeling, F1 and accuracy for classification tasks, and BLEU scores for generation tasks. Some papers also report performance on standard NLP benchmarks such as GLUE.

**Sources:** `cloze_pretraining.pdf (page 6)`, `research_paper_2.pdf (page 3)`

---

### Q3: "What are the key differences between the models described in the documents?"

> The documents describe models that differ in their pretraining objectives and architectures. Some use masked language modeling (cloze-style) while others use autoregressive objectives. Self-attention based models generally outperform RNN baselines on long-range dependency tasks.

**Sources:** `cloze_pretraining.pdf (page 4)`, `research_paper_3.pdf (page 2)`

---

## Configuration Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CHUNK_SIZE` | `1000` | Characters per text chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between adjacent chunks |
| `TOP_K` | `6` | Number of chunks retrieved per query |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Local embedding model |
| `LLM_MODEL` | `google/flan-t5-base` | Local LLM for answer generation |
| `COLLECTION_NAME` | `nexla_docs` | ChromaDB collection name |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Vector store persist directory |

---

## Vibe Coding Setup

### Tools Used

- **Cursor** — primary IDE with AI-assisted code generation throughout the project
- **ChatGPT (GPT-4o)** — used alongside Cursor for architectural decisions, debugging error traces, and iterating on LangChain API usage

### How I Used Them

Cursor handled most in-editor code generation — scaffolding the ingestion pipeline, retrieval chain, and FastMCP server structure. For longer debugging sessions (particularly around deprecated LangChain APIs and Chroma version mismatches), I pasted error tracebacks into ChatGPT and iterated on fixes there. Having both open simultaneously let me move fast: generate in Cursor, debug in ChatGPT, paste the fix back.

### What Worked Well

- Cursor was fast for boilerplate and wiring known components together (loaders, splitters, vector store setup)
- ChatGPT was effective at diagnosing specific version-mismatch errors — e.g., `.persist()` removed in new Chroma, `get_relevant_documents` deprecated in favor of `.invoke()`, `text2text-generation` dropped in newer `transformers`
- The generate → error → debug → fix loop was tight and productive

### Where I Overrode or Corrected the AI

- AI suggested `vectordb.persist()` — already removed in modern Chroma; had to override
- AI used `response.content` on `HuggingFacePipeline.invoke()` — that method returns a plain string, not an object with a `.content` attribute; fixed manually
- AI shadowed the `pipeline` import with a local variable of the same name inside `generate_answer`; caught and renamed
- AI consistently used deprecated LangChain patterns; verified against current docs before trusting suggestions

### Reflection on AI in Forward-Deployed Engineering

AI coding tools meaningfully accelerate the scaffolding and wiring phase of a project — assembling known components into a new shape. Where they fall short is at the boundary of rapidly-changing library APIs, where training data lags behind the current release. In a forward-deployed context, the most valuable skill isn't using AI maximally — it's knowing when to trust it, when to verify it against docs, and when to override it entirely. The debugging loop is where real engineering judgment comes in, and that loop doesn't go away with AI tooling — it just moves faster.

---

## Known Issues & Troubleshooting

| Error | Fix |
|-------|-----|
| `AttributeError: 'Chroma' object has no attribute 'persist'` | Remove `.persist()` — Chroma auto-persists with `persist_directory` set |
| `AttributeError: 'VectorStoreRetriever' has no attribute 'get_relevant_documents'` | Use `retriever.invoke(question)` instead |
| `KeyError: Unknown task text2text-generation` | Pin `transformers==4.40.0` — newer versions removed this pipeline task |
| `ModuleNotFoundError: No module named 'langchain_chroma'` | Activate `.venv` before running — do not use base conda env |
| `embeddings.position_ids UNEXPECTED` warning on load | Harmless — safe to ignore for MiniLM |

---

## Dependencies

```
langchain
langchain-community
langchain-chroma
langchain-huggingface
langchain-text-splitters
chromadb
sentence-transformers
transformers==4.40.0
fastmcp
pymupdf
python-dotenv
```
