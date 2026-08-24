from src.models.schemas import (
    AnswerResult,
    Status,
)
from src.validation.citation_validator import (
    make_citation,
)

class AnswerAgent:

    def __init__(self, client):
        self.client = client
    def run(
        self,
        query,
        status,
        evidence,
        date_info,
        conflict,
    ):
        citations = [
            make_citation(
                item.clause
                if hasattr(item, "clause")
                else item
            )
            for item in evidence
        ]
        citations = list(
            dict.fromkeys(citations)
        )
        policy_date = date_info.get(
            "date"
        )

        if policy_date:
            policy_date = (
                policy_date.strftime(
                    "%Y-%m-%d"
                )
            )

        if status == Status.DATE_REQUIRED:
            return AnswerResult(
                status=status,
                answer=(
                    "A date is required to determine "
                    "which version of the policy applies."
                ),
                reason=(
                    "The applicable policy may differ "
                    "before and after 1 March 2026."
                ),
                citations=[],
                policy_date=None,
                follow_up=None,
            )

        if status == Status.CONFLICT:
            conflict_citations = []
            for clause in conflict.get(
                "clauses",
                [],
            ):
                conflict_citations.append(
                    make_citation(
                        clause
                    )
                )
            conflict_citations = list(
                dict.fromkeys(
                    conflict_citations
                )
            )
            return AnswerResult(
                status=status,
                answer=(
                    "The applicable original policy "
                    "contains conflicting reporting rules, "
                    "so the reporting deadline cannot be "
                    "determined unambiguously."
                ),
                reason=(
                    "The change occurred before "
                    "1 March 2026 and both applicable "
                    "reporting clauses are present in "
                    "the original policy."
                ),
                citations=conflict_citations,
                policy_date=policy_date,
                follow_up=None,
            )

        if status == Status.REFUSED:
            return AnswerResult(
                status=status,
                answer=(
                    "The available policy manual does "
                    "not provide sufficient evidence "
                    "to answer this question."
                ),
                reason=(
                    "The system does not make "
                    "unsupported assumptions beyond "
                    "the policy corpus."
                ),
                citations=[],
                policy_date=policy_date,
                follow_up=None,
            )
        context_parts = []
        for item in evidence:
            clause = (
                item.clause
                if hasattr(item, "clause")
                else item
            )
            context_parts.append(
                f"[§{clause.section}]\n"
                f"{clause.text}"
            )
        context = "\n\n".join(
            context_parts
        )

        prompt = f"""
Answer the user's policy question using ONLY
the supplied policy evidence.
Rules:
- Do not use outside knowledge.
- Do not guess.
- Do not invent missing facts.
- Do not invent policy sections.
- Only make claims supported by the evidence.
- Return ONLY the answer.
- Do NOT return a status.
- Do NOT return citations.
- Do NOT return metadata.
User question:
{query}
Policy evidence:
{context}
Give a clear, concise answer.
"""

        answer = self.client.generate(
            prompt
        )
        return AnswerResult(
            status=Status.ANSWERED,
            answer=answer.strip(),
            citations=citations,
            policy_date=policy_date,
            follow_up=None,
        )