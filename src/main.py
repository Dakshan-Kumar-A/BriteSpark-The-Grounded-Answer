from src.config import (
    POLICY_PATH,
    AMENDMENT_PATH,
    TOP_K,
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

from src.agents.retrieval_agent import (
    RetrievalAgent,
)

from src.agents.evidence_agent import (
    EvidenceAgent,
)

from src.agents.contradiction_agent import (
    ContradictionAgent,
)

from src.agents.answer_agent import (
    AnswerAgent,
)

from src.validation.date_resolver import (
    DateResolver,
)

from src.validation.answerability import (
    Answerability,
)

from src.llm.client import LLMClient


def print_result(result):

    print()

    print(
        f"Status: {result.status}"
    )

    print()

    print(
        "Answer:"
    )

    print(
        result.answer
    )

    if result.reason:

        print()

        print(
            "Reason:"
        )

        print(
            result.reason
        )

    if result.policy_date:

        print()

        print(
            "Policy date: "
            + result.policy_date
        )

    if result.citations:

        print()

        print(
            "Citations:"
        )

        for citation in result.citations:

            print(
                f"- {citation}"
            )

    print()


def build_system():

    clauses = load_corpus(
        POLICY_PATH,
        AMENDMENT_PATH,
    )

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

    return {
        "retrieval": RetrievalAgent(
            hybrid
        ),

        "evidence": EvidenceAgent(),

        "contradiction": ContradictionAgent(
            clauses
        ),

        "date": DateResolver(),

        "answerability": Answerability(),

        "answer": AnswerAgent(
            LLMClient()
        ),
    }
    

def process_query(
    query,
    system,
    memory,
):
    full_query = memory.combine(query)

    # ---------------------------------------------
    # Resolve dates before retrieval/decision logic
    # ---------------------------------------------

    date_info = system["date"].resolve(
        full_query
    )

    # ---------------------------------------------
    # Retrieve relevant clauses
    # ---------------------------------------------

    clauses = system["retrieval"].run(
        full_query
    )

    # ---------------------------------------------
    # Select evidence
    # ---------------------------------------------

    evidence = system["evidence"].run(
        clauses,
        date_info,
    )

    # ---------------------------------------------
    # Detect contradictions
    # ---------------------------------------------

    conflict = system["contradiction"].run(
        full_query,
        evidence,
        date_info,
    )

    # ---------------------------------------------
    # Determine answer status
    # ---------------------------------------------

    status = system["answerability"].check(
        evidence,
        date_info,
        conflict,
        full_query,
    )

    # ---------------------------------------------
    # Generate final answer
    # ---------------------------------------------

    result = system["answer"].run(
        full_query,
        status,
        evidence,
        date_info,
        conflict,
    )

    return result


def main():
    system = build_system()

    print(
        "Calder County Policy Assistant"
    )

    print(
        "Type 'quit' to exit."
    )

    while True:
        query = input(
            "\nYou: "
        ).strip()

        if query.lower() == "quit":
            break

        if not query:
            continue

        result = process_query(
            query,
            system,
        )

        print_result(result)


if __name__ == "__main__":
    main()