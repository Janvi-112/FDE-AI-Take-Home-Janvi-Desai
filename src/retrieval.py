"""
Retrieval + LLM answer generation
"""

from typing import Dict, Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline as hf_pipeline
from groq import Groq

from .config import (
    GROQ_API_KEY,
    CHROMA_PERSIST_DIR,
    LLM_MODEL,
    EMBEDDING_MODEL,
    TOP_K,
    COLLECTION_NAME
)

_client = Groq(api_key=GROQ_API_KEY)

def load_vectorstore():

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectordb = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    return vectordb


def retrieve(question: str):
    vectordb = load_vectorstore()
    retriever = vectordb.as_retriever(search_kwargs={"k": TOP_K})
    
    docs = retriever.invoke(question) # this returns a list of Document objects containing the relevant chunks
    return docs


def format_context(docs: list[Document]):

    context = []

    sources = []

    for d in docs:

        text = d.page_content
        meta = d.metadata

        doc_name = meta.get("document", "unknown")
        page = meta.get("page", "unknown")

        context.append(
            f"[Source: {doc_name}, page {page}]\n{text}"
        )

        sources.append({
            "document": doc_name,
            "page": page
        })

    return "\n\n---\n\n".join(context), sources


def generate_answer(question: str, context: str):
    prompt = f"""
        You are a document analysis assistant.

        Answer the question using ONLY the provided document excerpts.

        Always cite the document name and page number.

        Context:
        {context}

        Question:
        {question}
    """

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
    )
    return response.choices[0].message.content


def query_documents(question: str) -> Dict[str, Any]:

    docs = retrieve(question)

    if not docs:
        return {
            "answer": "No relevant documents found.",
            "sources": []
        }

    context, sources = format_context(docs)

    answer = generate_answer(question, context)

    return {
        "answer": answer,
        "sources": sources
    }