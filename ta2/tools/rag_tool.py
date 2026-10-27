"""Chroma-backed RAG tool using nomic-embed-text embeddings.

Implements U3-3:
- Chroma with persist_directory
- nomic-embed-text embeddings
- At least 8 chunks from academic study guidelines
- Grounded prompt that responds 'I don't know' when answer is absent
- Support for k=1 vs k=3 comparison and unanswerable question checks
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import ChatOllama, OllamaEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_PATH = BASE_DIR / "corpus" / "exam_guidelines.md"
CHROMA_PERSIST_DIR = BASE_DIR / "database" / "chroma_db"


def load_corpus_chunks(corpus_path: Path = CORPUS_PATH) -> List[Document]:
    """Parse the guidelines markdown into structured section chunks (8+ chunks)."""
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus file not found: {corpus_path}")

    text = corpus_path.read_text(encoding="utf-8")
    raw_sections = text.split("## Section ")
    documents: List[Document] = []

    # First chunk is the header intro
    header_intro = raw_sections[0].strip()
    if header_intro:
        documents.append(
            Document(
                page_content=header_intro,
                metadata={"section_id": "intro", "title": "Overview"},
            )
        )

    for section in raw_sections[1:]:
        lines = section.strip().split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        content = f"Section {title}\n{body}"
        documents.append(
            Document(
                page_content=content,
                metadata={"section_id": title.split(":")[0].strip(), "title": title},
            )
        )

    return documents


class StudyGuidelinesRAG:
    """Manages Chroma vector store, indexing, and grounded retrieval."""

    def __init__(
        self,
        persist_dir: Path | str = CHROMA_PERSIST_DIR,
        embedding_model: str = "nomic-embed-text",
        llm_model: str = "qwen2.5:3b",
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.llm = ChatOllama(model=llm_model, temperature=0)
        self.vector_store = self._init_or_load_store()

    def _init_or_load_store(self) -> Chroma:
        """Initialize Chroma store, indexing corpus chunks if newly created."""
        store = Chroma(
            collection_name="exam_guidelines",
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_dir),
        )
        # Check if documents already exist in the collection
        existing = store.get()
        if not existing or len(existing.get("ids", [])) < 8:
            docs = load_corpus_chunks()
            store.add_documents(docs)
        return store

    def retrieve(self, query: str, k: int = 3) -> List[Document]:
        """Fetch the top-k most relevant guideline documents."""
        return self.vector_store.similarity_search(query, k=k)

    def retrieve_with_scores(self, query: str, k: int = 3) -> List[tuple[Document, float]]:
        """Fetch documents with distance scores."""
        return self.vector_store.similarity_search_with_score(query, k=k)

    def answer_query(self, query: str, k: int = 3) -> Dict[str, Any]:
        """Grounded QA ensuring refusal on out-of-scope or unanswerable queries."""
        docs = self.retrieve(query, k=k)
        context = "\n\n---\n\n".join(
            [f"[{doc.metadata.get('title', 'Policy')}]:\n{doc.page_content}" for doc in docs]
        )

        prompt = (
            "You are an academic exam policy assistant. Answer the user's question STRICTLY using "
            "only the provided context documents. If the question cannot be answered directly and "
            "completely from the context, or if the information is absent, you MUST reply: "
            "'I don't know based on the provided documents.' Do not extrapolate or invent policies.\n\n"
            f"Context Documents:\n{context}\n\n"
            f"User Question: {query}\n\n"
            "Answer:"
        )

        response = self.llm.invoke(prompt)
        answer_text = str(response.content).strip()

        return {
            "query": query,
            "k": k,
            "retrieved_chunks": [
                {"title": d.metadata.get("title", ""), "content": d.page_content}
                for d in docs
            ],
            "answer": answer_text,
        }


def run_rag_demo() -> Dict[str, Any]:
    """Execute U3-3 evidence demo: k=1 vs k=3 comparison and unanswerable question."""
    rag = StudyGuidelinesRAG()

    test_q1 = "What is the maximum allowed daily study hours before burnout oversight is required?"
    res_k1 = rag.answer_query(test_q1, k=1)
    res_k3 = rag.answer_query(test_q1, k=3)

    unanswerable_q = "What is the cafeteria lunch menu or student parking fee for exam week?"
    res_unanswerable = rag.answer_query(unanswerable_q, k=3)

    return {
        "k1_test": res_k1,
        "k3_test": res_k3,
        "unanswerable_test": res_unanswerable,
    }


if __name__ == "__main__":
    print("=== Chroma RAG Verification (U3-3) ===")
    demo = run_rag_demo()
    print("\n--- Query 1 with k=1 ---")
    print(f"Question: {demo['k1_test']['query']}")
    print(f"Retrieved Chunks: {len(demo['k1_test']['retrieved_chunks'])}")
    print(f"Answer: {demo['k1_test']['answer']}")

    print("\n--- Query 1 with k=3 ---")
    print(f"Question: {demo['k3_test']['query']}")
    print(f"Retrieved Chunks: {len(demo['k3_test']['retrieved_chunks'])}")
    print(f"Answer: {demo['k3_test']['answer']}")

    print("\n--- Unanswerable Query (Grounding Check) ---")
    print(f"Question: {demo['unanswerable_test']['query']}")
    print(f"Answer: {demo['unanswerable_test']['answer']}")
