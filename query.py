# query.py
"""
Interactive query script for your Nexla PDF ingestion.
Loads the Chroma vector store and your LLM for RAG-style Q&A.
"""

from src.retrieval import query_documents

def main():
    print("Welcome to the Nexla PDF Query Assistant!")
    print("Type your question and press Enter (type 'exit' to quit).")

    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not question:
            continue

        result = query_documents(question)

        print("\n--- Answer ---")
        print(result["answer"])
        print("\n--- Sources ---")
        for src in result["sources"]:
            print(f"{src['document']}, page {src['page']}")
        print("\n============================")

if __name__ == "__main__":
    main()