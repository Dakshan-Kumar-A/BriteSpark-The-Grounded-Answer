import click

from src.config import (
    DATA_PATH,
    EMBEDDING_MODEL,
    MIN_RETRIEVAL_SCORE,
    TOP_K
)

from src.ingestion.parser import parse_policy

from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.semantic_retriever import SemanticRetriever
from src.retrieval.hybrid_retriever import HybridRetriever

from src.validation.answerability import AnswerabilityChecker
from src.validation.citation_validator import CitationValidator

from src.llm.client import LLMClient

from src.agents.retrieval_agent import RetrievalAgent
from src.agents.evidence_agent import EvidenceAgent
from src.agents.contradiction_agent import ContradictionAgent
from src.agents.answer_agent import AnswerAgent


def build_system():

    print("Loading policy manual...")

    clauses = parse_policy(
        DATA_PATH
    )

    bm25 = BM25Retriever(
        clauses
    )

    semantic = SemanticRetriever(
        clauses,
        EMBEDDING_MODEL
    )

    hybrid = HybridRetriever(
        bm25,
        semantic
    )

    retrieval_agent = RetrievalAgent(
        hybrid
    )

    checker = AnswerabilityChecker(
        MIN_RETRIEVAL_SCORE
    )

    evidence_agent = EvidenceAgent(
        checker
    )

    llm = LLMClient()

    citation_validator = CitationValidator()

    contradiction_agent = ContradictionAgent()

    answer_agent = AnswerAgent(
        llm,
        citation_validator,
        contradiction_agent
    )

    return (
        retrieval_agent,
        evidence_agent,
        answer_agent
    )


def process_question(
    question,
    retrieval_agent,
    evidence_agent,
    answer_agent
):

    results = retrieval_agent.retrieve(
        question,
        TOP_K
    )

    if not results:

        print(
            "\nStatus: NOT_FOUND"
        )

        print(
            "\nAnswer:"
        )

        print(
            "The requested policy section or "
            "information was not found in the "
            "policy manual."
        )

        return

    can_answer, reason = (
        evidence_agent.evaluate(
            results
        )
    )

    if not can_answer:

        print(
            "\nStatus: NEEDS_COUNTY_INSIGHT"
        )

        print(
            "\nAnswer:"
        )

        print(
            "The supplied policy evidence does "
            "not provide enough information to "
            "answer this question authoritatively."
        )

        print(
            "\nCounty Insight:"
        )

        print(
            "The policy manual does not provide "
            "enough information to make an "
            "authoritative determination for "
            "this situation."
        )

        print(
            "Please contact the county directly "
            "for an official determination."
        )

        return

    result = answer_agent.answer(
        question,
        results
    )

    print(
        f"\nStatus: {result.status.upper()}"
    )

    print(
        f"\nAnswer:\n{result.answer}"
    )

    if result.status == "needs_county_insight":

        print(
            "\nCounty Insight:"
        )

        print(
            "The policy manual does not provide "
            "enough information to make an "
            "authoritative determination for "
            "this situation."
        )

        print(
            "Please contact the county directly "
            "for an official determination."
        )

    if result.citations:

        print(
            "\nCitations:"
        )

        for citation in result.citations:
            print(
                f"- §{citation}"
            )


@click.command()
def main():

    (
        retrieval_agent,
        evidence_agent,
        answer_agent
    ) = build_system()

    print(
        "\nPolicy Assistant started!"
    )

    print(
        "Ask a question about the policy manual."
    )

    print(
        "Type 'quit' to exit.\n"
    )

    while True:

        question = input(
            "You: "
        ).strip()

        if question.lower() == "quit":

            print(
                "\nGoodbye!"
            )

            break

        if not question:

            print(
                "Please enter a question.\n"
            )

            continue

        try:

            process_question(
                question,
                retrieval_agent,
                evidence_agent,
                answer_agent
            )

            print()

        except Exception as error:

            print(
                f"\nError: {error}\n"
            )


if __name__ == "__main__":
    main()