import re

from src.models.schemas import AnswerResult
from src.llm.prompts import build_prompt


class AnswerAgent:

    def __init__(
        self,
        llm_client,
        citation_validator,
        contradiction_agent
    ):
        self.llm = llm_client
        self.citation_validator = citation_validator
        self.contradiction_agent = contradiction_agent

    def answer(self, question, results):

        if self.contradiction_agent.find_known_conflict(
            results
        ):
            return AnswerResult(
                answer=self.contradiction_agent.get_conflict_message(),
                citations=["4.3.2", "9.1.4"],
                status="conflict"
            )

        prompt = build_prompt(
            question,
            results
        )

        response = self.llm.generate(
            prompt
        ).strip()

        status = self.detect_status(
            response
        )

        response = self.remove_status(
            response
        )

        response = self.remove_citation_section(
            response
        )

        if not response:
            response = (
                "The supplied policy evidence does not "
                "provide enough information to answer "
                "this question authoritatively."
            )

            status = "needs_county_insight"

        citations = self.extract_citations(
            response
        )

        valid = self.citation_validator.validate(
            citations,
            results
        )

        valid = list(
            dict.fromkeys(valid)
        )

        return AnswerResult(
            answer=response,
            citations=valid,
            status=status
        )

    def detect_status(self, text):

        match = re.search(
            r"Status:\s*"
            r"(ANSWERED|PARTIALLY_ANSWERED|"
            r"NEEDS_COUNTY_INSIGHT|NOT_FOUND|"
            r"OUT_OF_SCOPE|CONFLICT)",
            text,
            re.IGNORECASE
        )

        if not match:
            return "answered"

        return match.group(1).lower()

    def remove_status(self, text):

        return re.sub(
            r"^\s*Status:\s*"
            r"(ANSWERED|PARTIALLY_ANSWERED|"
            r"NEEDS_COUNTY_INSIGHT|NOT_FOUND|"
            r"OUT_OF_SCOPE|CONFLICT)"
            r"\s*\n?",
            "",
            text,
            count=1,
            flags=re.IGNORECASE
        ).strip()

    def remove_citation_section(self, text):

        text = re.sub(
            r"\n\s*Citations?\s*:.*$",
            "",
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        return text.strip()

    def extract_citations(self, text):

        citations = re.findall(
            r"§\s*(\d+(?:\.\d+)+)",
            text
        )

        return list(
            dict.fromkeys(citations)
        )