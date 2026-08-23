class AnswerabilityChecker:

    def __init__(self, min_score):
        self.min_score = min_score

    def can_answer(self, results):
        if not results:
            return False

        best_result = results[0]

        return (
            best_result.score
            >= self.min_score
        )

    def get_reason(self, results):
        if not results:
            return "No relevant policy clause was found."

        best_score = results[0].score

        if best_score < self.min_score:
            return (
                "The retrieved policy evidence "
                "is not strong enough."
            )

        return ""