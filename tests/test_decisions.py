from src.config import (
    DATA_PATH,
    EMBEDDING_MODEL
)

from src.ingestion.parser import parse_policy

from src.retrieval.bm25_retriever import (
    BM25Retriever
)

from src.retrieval.semantic_retriever import (
    SemanticRetriever
)

from src.retrieval.hybrid_retriever import (
    HybridRetriever
)


def test_bm25_search():
    clauses = parse_policy(DATA_PATH)

    retriever = BM25Retriever(
        clauses
    )

    results = retriever.search(
        "report a change"
    )

    assert len(results) > 0


def test_semantic_search():
    clauses = parse_policy(DATA_PATH)

    retriever = SemanticRetriever(
        clauses,
        EMBEDDING_MODEL
    )

    results = retriever.search(
        "How do I tell the department "
        "about changes?"
    )

    assert len(results) > 0


def test_hybrid_search():
    clauses = parse_policy(DATA_PATH)

    bm25 = BM25Retriever(
        clauses
    )

    semantic = SemanticRetriever(
        clauses,
        EMBEDDING_MODEL
    )

    retriever = HybridRetriever(
        bm25,
        semantic
    )

    results = retriever.search(
        "report a change"
    )

    assert len(results) > 0