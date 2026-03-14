# Example Interaction Log

Below are sample questions and the answers returned by the MCP server (with source attribution). Run the server with your PDFs in `data/` and call `query_documents` to reproduce or generate your own examples.

---

## Example 1

**Question:** What is the main topic or purpose of the documents?

**Answer:**  
*(Replace with the actual answer from your run. Example format:)*  
The documents focus on [topic]. Key themes include [X] and [Y].

**Sources:** `document1.pdf` (p. 1), `document2.pdf` (p. 3)

---

## Example 2

**Question:** Which companies or products are mentioned?

**Answer:**  
*(Replace with the actual answer from your run.)*

**Sources:** `document2.pdf` (p. 5), `document4.pdf` (p. 2)

---

## Example 3

**Question:** Summarize the key recommendations or next steps.

**Answer:**  
*(Replace with the actual answer from your run.)*

**Sources:** `document1.pdf` (p. 8), `document3.pdf` (p. 4)

---

## How to generate your own log

1. Put the assignment PDFs in `data/`.
2. Start the server: `python -m src.server` (or use your MCP client to start it).
3. Call the `query_documents` tool with natural language questions.
4. Copy the returned answer and “Sources” line into this file (or add more examples).

This demonstrates that the system works and attributes answers to source documents and pages.
