import re

from src.models.schemas import Status
from src.config import MIN_EVIDENCE_SCORE


STOPWORDS = {
    "what",
    "is",
    "the",
    "a",
    "an",
    "for",
    "on",
    "of",
    "to",
    "and",
    "or",
    "was",
    "are",
    "does",
    "can",
    "be",
    "made",
    "that",
    "would",
    "have",
    "with",
    "how",
    "do",
}


class Answerability:

    def _tokens(self, text):

        words = re.findall(
            r"[a-zA-Z0-9]+",
            text.lower(),
        )

        return {
            word
            for word in words
            if word not in STOPWORDS
            and len(word) > 2
        }

    def _is_relevant(
        self,
        query,
        evidence,
    ):

        query_tokens = self._tokens(
            query
        )

        if not query_tokens:
            return False

        best_overlap = 0

        for item in evidence:

            clause = getattr(
                item,
                "clause",
                item,
            )

            text = getattr(
                clause,
                "text",
                "",
            )

            clause_tokens = self._tokens(
                text
            )

            overlap = len(
                query_tokens
                & clause_tokens
            )

            best_overlap = max(
                best_overlap,
                overlap,
            )

        return best_overlap >= 2

    def check(
        self,
        evidence,
        date_info,
        conflict,
        query=None,
    ):

        # Date is required but absent.
        if date_info.get(
            "needed"
        ):
            return Status.DATE_REQUIRED

        # Explicit contradiction.
        if conflict.get(
            "conflict"
        ):
            return Status.CONFLICT

        # Nothing retrieved.
        if not evidence:
            return Status.REFUSED

        # Retrieval scores.
        scores = []

        for item in evidence:

            score = getattr(
                item,
                "score",
                0.0,
            )

            try:

                scores.append(
                    float(score)
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

        if not scores:
            return Status.REFUSED

        if max(scores) < MIN_EVIDENCE_SCORE:
            return Status.REFUSED

        # Query/evidence lexical sanity check.
        if query:

            if not self._is_relevant(
                query,
                evidence,
            ):
                return Status.REFUSED

        return Status.ANSWERED