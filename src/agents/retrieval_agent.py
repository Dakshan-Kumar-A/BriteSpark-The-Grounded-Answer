import re


class RetrievalAgent:

    def __init__(self, retriever):
        self.retriever = retriever

    def extract_citations(self, question):
        pattern = (
            r"(?:§\s*|section\s+)"
            r"(\d+(?:\.\d+)+)"
        )

        citations = re.findall(
            pattern,
            question,
            re.IGNORECASE
        )

        return list(
            dict.fromkeys(citations)
        )

    def retrieve(self, question, top_k=5):

        requested = self.extract_citations(
            question
        )

        exact_results = []

        for citation in requested:

            result = self.retriever.get_by_citation(
                citation
            )

            if result:
                exact_results.append(result)

        # Explicit section was requested,
        # but none of the requested sections exist.
        if requested and not exact_results:
            return []

        # If explicit sections were requested,
        # they are mandatory evidence.
        if requested:
            return exact_results + self.retriever.search(
                question,
                top_k
            )

        return self.retriever.search(
            question,
            top_k
        )