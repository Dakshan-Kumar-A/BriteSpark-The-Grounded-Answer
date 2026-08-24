import re
from src.models.schemas import Status
from src.config import MIN_RETRIEVAL_SCORE

class Answerability:
    STOP_WORDS = {
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
        "does",
        "do",
        "can",
        "be",
        "made",
        "occurred",
        "applies",
        "apply",
        "policy",
    }

    def _tokens(self, text):
        words = re.findall(
            r"[a-z0-9]+",
            text.lower(),
        )
        return {
            word
            for word in words
            if word not in self.STOP_WORDS
            and len(word) > 2
        }

    def _has_lexical_support(
        self,
        query,
        evidence,
    ):
        query_tokens = self._tokens(query)
        if not query_tokens:
            return True
        evidence_text = " ".join(
            (
                item.clause.text
                if hasattr(item, "clause")
                else item.text
            )
            for item in evidence
        )
        evidence_tokens = self._tokens(
            evidence_text
        )
        overlap = (
            query_tokens
            & evidence_tokens
        )
        return bool(overlap)

    def check(
        self,
        evidence,
        date_info,
        conflict,
        query=None,
    ):
        if date_info.get("needed"):
            return Status.DATE_REQUIRED
        if conflict.get("conflict"):
            return Status.CONFLICT
        if not evidence:
            return Status.REFUSED
        relevant = []
        
        for item in evidence:
            score = getattr(
                item,
                "score",
                0.0,
            )
            if score >= MIN_RETRIEVAL_SCORE:
                relevant.append(item)
                
        if not relevant:
            return Status.REFUSED
        if query is not None:
            if not self._has_lexical_support(
                query,
                relevant,
            ):
                return Status.REFUSED
            
        return Status.ANSWERED