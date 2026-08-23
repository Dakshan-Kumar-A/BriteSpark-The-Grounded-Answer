class CitationValidator:

    def validate(
        self,
        citations,
        retrieved_clauses
    ):
        available = {
            item.clause.citation
            for item in retrieved_clauses
        }

        valid = []

        for citation in citations:
            if citation in available:
                valid.append(citation)

        return valid

    def all_valid(
        self,
        citations,
        retrieved_clauses
    ):
        valid = self.validate(
            citations,
            retrieved_clauses
        )

        return len(valid) == len(citations)