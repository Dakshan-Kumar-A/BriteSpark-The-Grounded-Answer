from rank_bm25 import BM25Okapi

from src.models.schemas import RetrievedClause


class BM25Retriever:

    def __init__(self, clauses):
        self.clauses = clauses

        self.corpus = [
            self.tokenize(clause.text)
            for clause in clauses
        ]

        self.bm25 = BM25Okapi(self.corpus)

    def tokenize(self, text):
        return text.lower().split()

    def search(self, query, top_k=5):
        tokens = self.tokenize(query)

        scores = self.bm25.get_scores(tokens)

        results = []

        for index, score in enumerate(scores):
            results.append(
                RetrievedClause(
                    clause=self.clauses[index],
                    score=float(score),
                    source="bm25"
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True
        )

        return results[:top_k]