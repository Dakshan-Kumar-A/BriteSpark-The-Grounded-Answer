import numpy as np

from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL

from src.models.schemas import RetrievedClause


class SemanticRetriever:

    def __init__(
        self,
        clauses,
        model_name=EMBEDDING_MODEL,
    ):
        self.clauses = clauses

        self.model = SentenceTransformer(
            model_name
        )

        texts = [
            clause.text
            for clause in clauses
        ]

        self.embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

    def search(
        self,
        query,
        top_k=5,
    ):
        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )[0]

        scores = np.dot(
            self.embeddings,
            query_embedding
        )

        results = []

        for index, score in enumerate(scores):

            results.append(
                RetrievedClause(
                    clause=self.clauses[index],
                    score=float(score),
                    source="semantic"
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True
        )

        return results[:top_k]