from src.models.schemas import RetrievedClause


class HybridRetriever:

    def __init__(
        self,
        bm25_retriever,
        semantic_retriever,
        semantic_weight=0.7,
        bm25_weight=0.3
    ):
        self.bm25 = bm25_retriever
        self.semantic = semantic_retriever

        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight


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
            item.score
            for item in results
        )

        if maximum <= 0:
            return {
                item.clause.citation: 0.0
                for item in results
            }

        return {
            item.clause.citation:
            item.score / maximum
            for item in results
        }


    def search(
        self,
        query,
        top_k=5,
        candidate_k=20
    ):
        bm25_results = self.bm25.search(
            query,
            candidate_k
        )

        semantic_results = self.semantic.search(
            query,
            candidate_k
        )

        bm25_scores = self.normalize_scores(
            bm25_results
        )

        semantic_scores = {
            item.clause.citation: item.score
            for item in semantic_results
        }

        clauses = {}

        for item in bm25_results + semantic_results:
            citation = item.clause.citation

            clauses[citation] = item.clause

        results = []

        for citation, clause in clauses.items():

            bm25_score = bm25_scores.get(
                citation,
                0.0
            )

            semantic_score = semantic_scores.get(
                citation,
                0.0
            )

            final_score = (
                semantic_score * self.semantic_weight
                + bm25_score * self.bm25_weight
            )

            results.append(
                RetrievedClause(
                    clause=clause,
                    score=float(final_score),
                    source="hybrid"
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True
        )

        return results[:top_k]