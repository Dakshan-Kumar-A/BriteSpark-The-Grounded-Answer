from src.models.schemas import RetrievedClause


class HybridRetriever:

    def __init__(self, bm25_retriever, semantic_retriever):
        self.bm25 = bm25_retriever
        self.semantic = semantic_retriever

    def get_by_citation(self, citation):
        for clause in self.bm25.clauses:
            if clause.citation == citation:
                return RetrievedClause(
                    clause=clause,
                    score=1.0,
                    source="exact"
                )
        return None

    def normalize_scores(self, results):
        if not results:
            return {}

        maximum = max(
            item.score for item in results
        )

        if maximum == 0:
            return {
                item.clause.citation: 0
                for item in results
            }

        return {
            item.clause.citation:
            item.score / maximum
            for item in results
        }

    def search(self, query, top_k=5):
        bm25_results = self.bm25.search(
            query,
            top_k
        )

        semantic_results = self.semantic.search(
            query,
            top_k
        )

        # Keep absolute semantic similarity.
        semantic_scores = {
            item.clause.citation: item.score
            for item in semantic_results
        }

        # BM25 is useful for lexical matching, but its raw scale
        # is not directly comparable to cosine similarity.
        bm25_scores = self.normalize_scores(
            bm25_results
        )

        clauses = {}

        for item in bm25_results + semantic_results:
            clauses[item.clause.citation] = item.clause

        results = []

        for citation, clause in clauses.items():
            semantic_score = semantic_scores.get(
                citation,
                0
            )

            bm25_score = bm25_scores.get(
                citation,
                0
            )

            score = (
                semantic_score * 0.7
                + bm25_score * 0.3
            )

            results.append(
                RetrievedClause(
                    clause=clause,
                    score=score,
                    source="hybrid"
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True
        )

        return results[:top_k]