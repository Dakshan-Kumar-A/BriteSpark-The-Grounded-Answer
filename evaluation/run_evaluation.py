import json

from src.config import (
    DATA_PATH,
    EMBEDDING_MODEL,
    MIN_RETRIEVAL_SCORE,
    TOP_K
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

from src.validation.answerability import (
    AnswerabilityChecker
)

from src.agents.contradiction_agent import (
    ContradictionAgent
)


def load_test_cases():
    with open(
        "evaluation/test_cases.json",
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def get_status(
    question,
    retriever,
    checker,
    contradiction_agent
):
    results = retriever.search(
        question,
        TOP_K
    )

    if not checker.can_answer(results):
        return "refused"

    if contradiction_agent.find_known_conflict(
        results
    ):
        return "conflict"

    return "answered"


def main():
    clauses = parse_policy(DATA_PATH)

    bm25 = BM25Retriever(clauses)

    semantic = SemanticRetriever(
        clauses,
        EMBEDDING_MODEL
    )

    retriever = HybridRetriever(
        bm25,
        semantic
    )

    checker = AnswerabilityChecker(
        MIN_RETRIEVAL_SCORE
    )

    contradiction_agent = (
        ContradictionAgent()
    )

    test_cases = load_test_cases()

    passed = 0

    print("\nRunning evaluation...\n")

    for test in test_cases:

        actual_status = get_status(
            test["question"],
            retriever,
            checker,
            contradiction_agent
        )

        expected_status = (
            test["expected_status"]
        )

        success = (
            actual_status == expected_status
        )

        if success:
            passed += 1
            result = "PASS"
        else:
            result = "FAIL"

        print(
            f"Test {test['id']}: {result}"
        )

        print(
            f"Expected: {expected_status}"
        )

        print(
            f"Actual:   {actual_status}\n"
        )

    total = len(test_cases)

    print("-" * 30)

    print(
        f"Passed: {passed}/{total}"
    )

    print(
        f"Failed: {total - passed}/{total}"
    )


if __name__ == "__main__":
    main()