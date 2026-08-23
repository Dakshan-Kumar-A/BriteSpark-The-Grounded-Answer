from src.config import (
    POLICY_PATH,
    AMENDMENT_PATH,
    EMBEDDING_MODEL,
)

from src.ingestion.parser import load_corpus

from src.retrieval.bm25_retriever import (
    BM25Retriever,
)

from src.retrieval.semantic_retriever import (
    SemanticRetriever,
)

from src.retrieval.hybrid_retriever import (
    HybridRetriever,
)


def load_clauses():
    return load_corpus(
        POLICY_PATH,
        AMENDMENT_PATH,
    )


def create_retrievers():

    clauses = load_clauses()

    bm25 = BM25Retriever(
        clauses
    )

    semantic = SemanticRetriever(
        clauses,
        EMBEDDING_MODEL,
    )

    hybrid = HybridRetriever(
        bm25,
        semantic,
    )

    return bm25, semantic, hybrid


def test_bm25_retrieval():

    bm25, _, _ = create_retrievers()

    results = bm25.search(
        "income threshold",
        top_k=3,
    )

    assert results
    assert len(results) <= 3

    for result in results:
        assert result.source == "bm25"
        assert result.clause is not None


def test_semantic_retrieval():

    _, semantic, _ = create_retrievers()

    results = semantic.search(
        "How much income can a household earn?",
        top_k=3,
    )

    assert results
    assert len(results) <= 3

    for result in results:
        assert result.source == "semantic"
        assert result.clause is not None


def test_hybrid_retrieval():

    _, _, hybrid = create_retrievers()

    results = hybrid.search(
        "What is the maximum income allowed?",
        top_k=3,
    )

    assert results
    assert len(results) <= 3

    for result in results:
        assert result.source == "hybrid"
        assert result.clause is not None


def test_bm25_result_has_score():

    bm25, _, _ = create_retrievers()

    results = bm25.search(
        "income",
        top_k=3,
    )

    assert results

    for result in results:
        assert isinstance(
            result.score,
            float,
        )


def test_semantic_result_has_score():

    _, semantic, _ = create_retrievers()

    results = semantic.search(
        "income eligibility",
        top_k=3,
    )

    assert results

    for result in results:
        assert isinstance(
            result.score,
            float,
        )


def test_hybrid_result_has_score():

    _, _, hybrid = create_retrievers()

    results = hybrid.search(
        "income eligibility",
        top_k=3,
    )

    assert results

    for result in results:
        assert isinstance(
            result.score,
            float,
        )